"""
综合优化的风格化模型训练模块

结合了两个训练脚本的优点，提供基于预训练 T5 模型的 LoRA 微调功能，用于文本风格转换任务
"""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    BertTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveStyleModelTrainer:
    """综合优化的风格化模型训练器"""
    
    def __init__(
        self,
        pretrained_model_path: str = "./origin_models/uer-t5-base-chinese-cluecorpussmall",
        output_dir: str = "./styled_models/comprehensive_my_t5_style_model",
        train_data_path: str = "./data/train.jsonl",
        eval_data_path: str = "./data/eval.jsonl",
        lora_r: int = 32,
        lora_alpha: int = 64,
        lora_dropout: float = 0.05,
        lora_target_modules: str = "SelfAttention.q,SelfAttention.k,SelfAttention.v,EncDecAttention.q,EncDecAttention.k,EncDecAttention.v"
    ):
        """
        初始化训练器
        
        参数:
            pretrained_model_path: 预训练模型路径
            output_dir: 输出目录
            train_data_path: 训练数据路径
            eval_data_path: 评估数据路径
            lora_r: LoRA rank
            lora_alpha: LoRA scaling factor
            lora_dropout: LoRA dropout rate
            lora_target_modules: LoRA目标模块列表，逗号分隔
        """
        # 存储训练配置路径
        self.pretrained_model_path = Path(pretrained_model_path)  # 预训练模型路径
        self.output_dir = Path(output_dir)                        # 模型输出路径
        self.train_data_path = Path(train_data_path)              # 训练数据路径
        self.eval_data_path = Path(eval_data_path)                # 评估数据路径
        
        # LoRA配置参数
        self.lora_r = lora_r
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.lora_target_modules = [module.strip() for module in lora_target_modules.split(",")]
        
        # 初始化模型组件（将在训练过程中加载）
        self.tokenizer = None    # 分词器实例
        self.model = None        # 模型实例  
        self.trainer = None      # 训练器实例
        
    def load_data(self, file_path: Path) -> Dataset:
        """
        加载 JSONL 格式的训练数据
        
        参数:
            file_path: 数据文件路径
            
        返回:
            Dataset: HuggingFace Dataset 对象
        """
        # 验证数据文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        # 初始化数据容器，用于存储源文本和目标文本
        data = {"source": [], "target": []}
        
        try:
            # 逐行读取JSONL文件
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        # 解析每一行的JSON数据
                        item = json.loads(line.strip())
                        if "source" in item and "target" in item:
                            # 添加有效的源文本和目标文本到数据容器
                            data["source"].append(item["source"])
                            data["target"].append(item["target"])
                        else:
                            # 记录缺少必要字段的行
                            logger.warning(f"第 {line_num} 行缺少必要字段，已跳过")
                    except json.JSONDecodeError as e:
                        # 记录解析错误的行
                        logger.warning(f"第 {line_num} 行 JSON 解析失败: {e}")
            
            # 检查是否成功加载了数据
            if not data["source"]:
                raise ValueError(f"数据文件为空或格式错误: {file_path}")
            
            # 将字典数据转换为HuggingFace Dataset对象
            dataset = Dataset.from_dict(data)
            logger.info(f"成功加载数据集: {len(dataset)} 条记录")
            return dataset
            
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            raise
    
    def load_model_and_tokenizer(self):
        """加载预训练模型和分词器，并配置LoRA"""
        try:
            # 检查预训练模型路径
            if not self.pretrained_model_path.exists():
                raise FileNotFoundError(f"预训练模型路径不存在: {self.pretrained_model_path}")
            
            logger.info(f"正在加载预训练模型: {self.pretrained_model_path}")
            
            # UER T5 需使用 BertTokenizer
            self.tokenizer = BertTokenizer.from_pretrained(str(self.pretrained_model_path))
            
            # 修复tokenizer配置：添加缺失的EOS token
            if self.tokenizer.eos_token is None:
                # 使用[SEP]作为EOS token，这是BERT tokenizer中常见的做法
                self.tokenizer.eos_token = "[SEP]"
                self.tokenizer.eos_token_id = self.tokenizer.convert_tokens_to_ids("[SEP]")
                logger.info(f"设置EOS token: {self.tokenizer.eos_token} (ID: {self.tokenizer.eos_token_id})")
            
            # 设置pad token与eos token相同（T5模型的常见做法）
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
                logger.info(f"设置PAD token: {self.tokenizer.pad_token} (ID: {self.tokenizer.pad_token_id})")
            
            self.model = AutoModelForSeq2SeqLM.from_pretrained(str(self.pretrained_model_path))
            
            # 确保模型的配置与tokenizer一致
            if self.model.config.eos_token_id is None:
                self.model.config.eos_token_id = self.tokenizer.eos_token_id
            if self.model.config.pad_token_id is None:
                self.model.config.pad_token_id = self.tokenizer.pad_token_id
            
            logger.info(f"模型EOS token ID: {self.model.config.eos_token_id}")
            logger.info(f"模型PAD token ID: {self.model.config.pad_token_id}")
            
            # 配置LoRA
            logger.info("正在配置LoRA...")
            peft_config = LoraConfig(
                task_type=TaskType.SEQ_2_SEQ_LM,
                inference_mode=False,
                r=self.lora_r,
                target_modules=self.lora_target_modules,
                lora_alpha=self.lora_alpha,
                lora_dropout=self.lora_dropout
            )
            
            # 应用LoRA配置到模型
            self.model = get_peft_model(self.model, peft_config)
            
            # 打印模型参数信息
            self.model.print_trainable_parameters()
            
            logger.info("✓ 模型、分词器和LoRA配置加载成功")
            
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            raise
    
    def preprocess_function(self, examples: Dict) -> Dict:
        """
        数据预处理函数
        
        参数:
            examples: 数据样本
            
        返回:
            Dict: 处理后的数据
        """
        # 处理输入文本 - 使用更短的序列长度以提高训练效率和效果
        inputs = self.tokenizer(
            examples["source"],
            max_length=256,  # 减少最大长度，提高训练效率
            truncation=True,
            padding="max_length",
            add_special_tokens=True,  # 添加特殊token
            return_tensors=None  # 不返回tensor，由DataCollator处理
        )
        
        # 处理目标文本（作为标签）- 使用更短的序列长度
        targets = self.tokenizer(
            examples["target"],
            max_length=256,  # 减少最大长度，提高训练效率
            truncation=True,
            padding="max_length",
            add_special_tokens=True,  # 添加特殊token
            return_tensors=None  # 不返回tensor，由DataCollator处理
        )
        
        # 将目标序列的pad token设置为-100，这样在计算损失时会被忽略
        inputs["labels"] = targets["input_ids"]
        
        # 确保labels中pad token的位置为-100
        labels = inputs["labels"]
        labels = [(label if label != self.tokenizer.pad_token_id else -100) for label in labels]
        inputs["labels"] = labels
        
        return inputs
    
    def prepare_datasets(self) -> Tuple[Dataset, Dataset]:
        """
        准备训练和评估数据集
        
        返回:
            Tuple[Dataset, Dataset]: 训练数据集和评估数据集
        """
        # 加载原始训练和评估数据
        train_dataset = self.load_data(self.train_data_path)
        eval_dataset = self.load_data(self.eval_data_path)
        
        # 对数据进行分词和编码预处理
        logger.info("正在预处理训练数据...")
        tokenized_train = train_dataset.map(
            self.preprocess_function,      # 应用预处理函数
            batched=True,                  # 批量处理以提高效率
            remove_columns=train_dataset.column_names  # 移除原始列，保留处理后的数据
        )
        
        logger.info("正在预处理评估数据...")
        tokenized_eval = eval_dataset.map(
            self.preprocess_function,      # 应用预处理函数
            batched=True,                  # 批量处理以提高效率
            remove_columns=eval_dataset.column_names  # 移除原始列，保留处理后的数据
        )
        
        return tokenized_train, tokenized_eval
    
    def setup_trainer(
        self,
        tokenized_train: Dataset,
        tokenized_eval: Dataset,
        learning_rate: float = 5e-4,
        per_device_train_batch_size: int = 2,
        per_device_eval_batch_size: int = 2,
        num_train_epochs: int = 10,
        weight_decay: float = 0.01,
        fp16: bool = True,
        logging_steps: int = 20,
        save_steps: int = 100,
        eval_steps: int = 100,
        save_total_limit: int = 3,
        warmup_steps: int = 100,
        gradient_accumulation_steps: int = 2
    ):
        """
        设置训练器
        
        参数:
            tokenized_train: 训练数据集
            tokenized_eval: 评估数据集
            learning_rate: 学习率
            per_device_train_batch_size: 每设备训练批次大小
            per_device_eval_batch_size: 每设备评估批次大小
            num_train_epochs: 训练轮数
            weight_decay: 权重衰减
            fp16: 是否使用混合精度训练
            logging_steps: 日志记录步数
            save_steps: 保存步数
            eval_steps: 评估步数
            save_total_limit: 保存的模型数量限制
            warmup_steps: 预热步数
            gradient_accumulation_steps: 梯度累积步数
        """
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置训练参数，定义训练过程的行为
        training_args = Seq2SeqTrainingArguments(
            output_dir=str(self.output_dir),    # 模型输出目录
            eval_strategy="steps",              # 每固定步数进行评估
            eval_steps=eval_steps,              # 评估间隔
            save_strategy="steps",              # 每固定步数保存检查点
            save_steps=save_steps,              # 保存间隔
            learning_rate=learning_rate,        # 优化器学习率
            per_device_train_batch_size=per_device_train_batch_size,  # 训练批次大小
            per_device_eval_batch_size=per_device_eval_batch_size,    # 评估批次大小
            weight_decay=weight_decay,          # 权重衰减系数
            num_train_epochs=num_train_epochs,  # 训练轮数
            predict_with_generate=True,         # 生成预测时使用generate方法
            fp16=fp16,                        # 启用混合精度训练以节省显存
            logging_steps=logging_steps,       # 日志记录频率
            save_total_limit=save_total_limit,  # 保留检查点数量上限
            report_to="none",                 # 不向外部报告
            load_best_model_at_end=True,      # 训练结束时加载最佳模型
            metric_for_best_model="eval_loss", # 以评估损失作为最佳模型判断标准
            greater_is_better=False,          # 损失越小越好
            # 激进的训练参数优化
            warmup_steps=warmup_steps,        # 增加预热步数，稳定训练
            dataloader_pin_memory=True,       # 加速数据加载
            gradient_accumulation_steps=gradient_accumulation_steps,  # 梯度累积
            dataloader_num_workers=0,         # 数据加载进程数
            # 正则化和优化
            label_smoothing_factor=0.1,       # 标签平滑，减少过拟合
            adafactor=True,                   # 使用Adafactor优化器，可能更有效
            # 学习率调度
            lr_scheduler_type="cosine",       # 余弦退火学习率调度
            # 其他优化
            group_by_length=False,            # 按长度分组，这里关闭以避免复杂性
            dataloader_drop_last=True,        # 丢弃最后一个不完整的批次
        )
        
        # 数据整理器，用于动态填充批次数据
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,         # 使用当前分词器
            model=self.model.base_model.model if hasattr(self.model, 'base_model') else self.model  # 指定基础模型以获取pad token id
        )
        
        # 创建序列到序列训练器实例
        self.trainer = Seq2SeqTrainer(
            model=self.model,                 # 要训练的模型（含LoRA适配器）
            args=training_args,               # 训练参数
            train_dataset=tokenized_train,    # 训练数据集
            eval_dataset=tokenized_eval,      # 评估数据集
            data_collator=data_collator,      # 数据整理器
            tokenizer=self.tokenizer          # 分词器
        )
        
        logger.info("✓ 训练器设置完成")
    
    def train(self):
        """开始训练"""
        # 检查训练器是否已正确初始化
        if self.trainer is None:
            raise RuntimeError("训练器未初始化，请先调用 setup_trainer()")
        
        try:
            logger.info("开始训练...")
            # 执行实际的模型训练过程
            self.trainer.train()
            logger.info("✓ 训练完成")
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            raise
    
    def save_model(self):
        """保存最终模型（仅保存LoRA适配器权重）"""
        try:
            logger.info(f"正在保存LoRA适配器到: {self.output_dir}")
            
            # 仅保存LoRA适配器权重，而不是整个模型
            self.model.save_pretrained(str(self.output_dir))
            
            # 保存分词器
            self.tokenizer.save_pretrained(str(self.output_dir))
            
            logger.info("✓ LoRA适配器和分词器保存完成")
            logger.info(f"  适配器保存在: {self.output_dir}")
            logger.info(f"  使用时需同时加载基础模型和此适配器")
            
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            raise
    
    def run_training(
        self,
        learning_rate: float = 5e-4,
        per_device_train_batch_size: int = 2,
        per_device_eval_batch_size: int = 2,
        num_train_epochs: int = 10,
        weight_decay: float = 0.01,
        fp16: bool = True,
        logging_steps: int = 20,
        save_steps: int = 100,
        eval_steps: int = 100,
        save_total_limit: int = 3,
        warmup_steps: int = 100,
        gradient_accumulation_steps: int = 2
    ):
        """
        完整的LoRA微调流程
        
        参数:
            learning_rate: 学习率
            per_device_train_batch_size: 每设备训练批次大小
            per_device_eval_batch_size: 每设备评估批次大小
            num_train_epochs: 训练轮数
            weight_decay: 权重衰减
            fp16: 是否使用混合精度训练
            logging_steps: 日志记录步数
            save_steps: 保存步数
            eval_steps: 评估步数
            save_total_limit: 保存的模型数量限制
            warmup_steps: 预热步数
            gradient_accumulation_steps: 梯度累积步数
        """
        try:
            # 步骤1: 加载预训练模型和分词器
            self.load_model_and_tokenizer()
            
            # 步骤2: 加载并预处理训练和评估数据集
            tokenized_train, tokenized_eval = self.prepare_datasets()
            
            # 步骤3: 配置训练参数并创建训练器
            self.setup_trainer(
                tokenized_train,
                tokenized_eval,
                learning_rate=learning_rate,
                per_device_train_batch_size=per_device_train_batch_size,
                per_device_eval_batch_size=per_device_eval_batch_size,
                num_train_epochs=num_train_epochs,
                weight_decay=weight_decay,
                fp16=fp16,
                logging_steps=logging_steps,
                save_steps=save_steps,
                eval_steps=eval_steps,
                save_total_limit=save_total_limit,
                warmup_steps=warmup_steps,
                gradient_accumulation_steps=gradient_accumulation_steps
            )
            
            # 步骤4: 执行模型训练
            self.train()
            
            # 步骤5: 保存训练完成的模型
            self.save_model()
            
            logger.info(f"✓ 训练流程完成，模型已保存至: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"训练流程失败: {str(e)}")
            raise


def create_sample_data(output_dir: str = "./data"):
    """
    创建示例训练数据
    
    参数:
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 训练数据示例
    train_data = [
        {"source": "你好，今天天气很好。", "target": "亲爱的朋友，今日阳光明媚，心情愉悦。"},
        {"source": "这个产品很不错。", "target": "该产品品质卓越，值得信赖。"},
        {"source": "我需要帮助。", "target": "恳请阁下给予协助，不胜感激。"},
        {"source": "谢谢你的帮助。", "target": "承蒙阁下相助，深表谢意。"},
        {"source": "明天见。", "target": "期待明日与阁下再会。"},
    ]
    
    # 评估数据示例
    eval_data = [
        {"source": "这个问题很难。", "target": "此问题颇具挑战性，需要深思熟虑。"},
        {"source": "我很高兴。", "target": "内心充满喜悦，倍感欣慰。"},
    ]
    
    # 写入训练数据
    train_file = output_path / "train.jsonl"
    with open(train_file, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # 写入评估数据
    eval_file = output_path / "eval.jsonl"
    with open(eval_file, 'w', encoding='utf-8') as f:
        for item in eval_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    logger.info(f"✓ 示例数据已创建:")
    logger.info(f"  训练数据: {train_file}")
    logger.info(f"  评估数据: {eval_file}")


if __name__ == "__main__":
    try:
        # 创建示例数据
        # 如果已经有了就不要再创建了
        if not (Path("./data") / "train.jsonl").exists():
            create_sample_data()
        
        # 初始化综合优化的训练器
        trainer = ComprehensiveStyleModelTrainer(
            pretrained_model_path="./origin_models/uer-t5-base-chinese-cluecorpussmall",
            output_dir="./styled_models/comprehensive_my_t5_style_model",
            train_data_path="./data/train.jsonl",
            eval_data_path="./data/eval.jsonl",
            lora_r=32,                    # 增加LoRA秩以提高表达能力
            lora_alpha=64,                # 增加缩放因子
            lora_dropout=0.05,            # 降低dropout以减少信息丢失
            lora_target_modules="SelfAttention.q,SelfAttention.k,SelfAttention.v,EncDecAttention.q,EncDecAttention.k,EncDecAttention.v"  # 确保正确的模块名称
        )
        
        # 运行综合优化的训练
        trainer.run_training(
            learning_rate=5e-4,           # 适中的学习率
            per_device_train_batch_size=2, # 适合4060的批次大小
            per_device_eval_batch_size=2,
            num_train_epochs=10,           # 增加训练轮数
            weight_decay=0.01,
            fp16=True,
            logging_steps=20,              # 增加日志频率
            save_steps=100,
            eval_steps=100,
            save_total_limit=3,            # 保留更多检查点
            warmup_steps=100,
            gradient_accumulation_steps=2
        )
        
    except Exception as e:
        logger.error(f"综合优化训练失败: {e}")
        raise