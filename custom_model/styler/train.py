"""
风格化模型训练模块

提供基于预训练 T5 模型的微调功能，用于文本风格转换任务
"""

import json
import logging
from pathlib import Path
from typing import Dict, Tuple

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    BertTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StyleModelTrainer:
    """风格化模型训练器"""
    
    def __init__(
        self,
        pretrained_model_path: str = "./origin_models/uer-t5-base-chinese-cluecorpussmall",
        output_dir: str = "./styled_models/my_t5_style_model",
        train_data_path: str = "./data/train.jsonl",
        eval_data_path: str = "./data/eval.jsonl"
    ):
        """
        初始化训练器
        
        参数:
            pretrained_model_path: 预训练模型路径
            output_dir: 输出目录
            train_data_path: 训练数据路径
            eval_data_path: 评估数据路径
        """
        self.pretrained_model_path = Path(pretrained_model_path)
        self.output_dir = Path(output_dir)
        self.train_data_path = Path(train_data_path)
        self.eval_data_path = Path(eval_data_path)
        
        self.tokenizer = None
        self.model = None
        self.trainer = None
        
    def load_data(self, file_path: Path) -> Dataset:
        """
        加载 JSONL 格式的训练数据
        
        参数:
            file_path: 数据文件路径
            
        返回:
            Dataset: HuggingFace Dataset 对象
        """
        if not file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        data = {"source": [], "target": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        item = json.loads(line.strip())
                        if "source" in item and "target" in item:
                            data["source"].append(item["source"])
                            data["target"].append(item["target"])
                        else:
                            logger.warning(f"第 {line_num} 行缺少必要字段，已跳过")
                    except json.JSONDecodeError as e:
                        logger.warning(f"第 {line_num} 行 JSON 解析失败: {e}")
            
            if not data["source"]:
                raise ValueError(f"数据文件为空或格式错误: {file_path}")
            
            dataset = Dataset.from_dict(data)
            logger.info(f"成功加载数据集: {len(dataset)} 条记录")
            return dataset
            
        except Exception as e:
            logger.error(f"加载数据失败: {str(e)}")
            raise
    
    def load_model_and_tokenizer(self):
        """加载预训练模型和分词器"""
        try:
            # 检查预训练模型路径
            if not self.pretrained_model_path.exists():
                raise FileNotFoundError(f"预训练模型路径不存在: {self.pretrained_model_path}")
            
            logger.info(f"正在加载预训练模型: {self.pretrained_model_path}")
            
            # UER T5 需使用 BertTokenizer
            self.tokenizer = BertTokenizer.from_pretrained(str(self.pretrained_model_path))
            self.model = AutoModelForSeq2SeqLM.from_pretrained(str(self.pretrained_model_path))
            
            logger.info("✓ 模型和分词器加载成功")
            
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
        # 处理输入文本
        inputs = self.tokenizer(
            examples["source"],
            max_length=512,
            truncation=True,
            padding="max_length"
        )
        
        # 处理目标文本
        labels = self.tokenizer(
            examples["target"],
            max_length=512,
            truncation=True,
            padding="max_length"
        )
        
        inputs["labels"] = labels["input_ids"]
        return inputs
    
    def prepare_datasets(self) -> Tuple[Dataset, Dataset]:
        """
        准备训练和评估数据集
        
        返回:
            Tuple[Dataset, Dataset]: 训练数据集和评估数据集
        """
        # 加载原始数据
        train_dataset = self.load_data(self.train_data_path)
        eval_dataset = self.load_data(self.eval_data_path)
        
        # 预处理数据
        logger.info("正在预处理训练数据...")
        tokenized_train = train_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=train_dataset.column_names
        )
        
        logger.info("正在预处理评估数据...")
        tokenized_eval = eval_dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=eval_dataset.column_names
        )
        
        return tokenized_train, tokenized_eval
    
    def setup_trainer(
        self,
        tokenized_train: Dataset,
        tokenized_eval: Dataset,
        learning_rate: float = 2e-5,
        per_device_train_batch_size: int = 4,
        per_device_eval_batch_size: int = 4,
        num_train_epochs: int = 3,
        weight_decay: float = 0.01,
        fp16: bool = True,
        logging_steps: int = 100,
        save_total_limit: int = 2
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
            save_total_limit: 保存的模型数量限制
        """
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 训练参数
        training_args = Seq2SeqTrainingArguments(
            output_dir=str(self.output_dir),
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=learning_rate,
            per_device_train_batch_size=per_device_train_batch_size,
            per_device_eval_batch_size=per_device_eval_batch_size,
            weight_decay=weight_decay,
            num_train_epochs=num_train_epochs,
            predict_with_generate=True,
            fp16=fp16,
            logging_steps=logging_steps,
            save_total_limit=save_total_limit,
            report_to="none",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False
        )
        
        # 数据整理器
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model
        )
        
        # 创建训练器
        self.trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_eval,
            data_collator=data_collator,
            processing_class=self.tokenizer
        )
        
        logger.info("✓ 训练器设置完成")
    
    def train(self):
        """开始训练"""
        if self.trainer is None:
            raise RuntimeError("训练器未初始化，请先调用 setup_trainer()")
        
        try:
            logger.info("开始训练...")
            self.trainer.train()
            logger.info("✓ 训练完成")
            
        except Exception as e:
            logger.error(f"训练失败: {str(e)}")
            raise
    
    def save_model(self):
        """保存最终模型"""
        try:
            logger.info(f"正在保存模型到: {self.output_dir}")
            self.trainer.save_model(str(self.output_dir))
            self.tokenizer.save_pretrained(str(self.output_dir))
            logger.info("✓ 模型保存完成")
            
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            raise
    
    def run_training(
        self,
        learning_rate: float = 2e-5,
        per_device_train_batch_size: int = 4,
        per_device_eval_batch_size: int = 4,
        num_train_epochs: int = 3,
        weight_decay: float = 0.01,
        fp16: bool = True,
        logging_steps: int = 100,
        save_total_limit: int = 2
    ):
        """
        完整的训练流程
        
        参数:
            learning_rate: 学习率
            per_device_train_batch_size: 每设备训练批次大小
            per_device_eval_batch_size: 每设备评估批次大小
            num_train_epochs: 训练轮数
            weight_decay: 权重衰减
            fp16: 是否使用混合精度训练
            logging_steps: 日志记录步数
            save_total_limit: 保存的模型数量限制
        """
        try:
            # 1. 加载模型和分词器
            self.load_model_and_tokenizer()
            
            # 2. 准备数据集
            tokenized_train, tokenized_eval = self.prepare_datasets()
            
            # 3. 设置训练器
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
                save_total_limit=save_total_limit
            )
            
            # 4. 开始训练
            self.train()
            
            # 5. 保存模型
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
    # 示例用法
    try:
        # 创建示例数据
        # 如果已经有了就不要再创建了
        if not (Path("./data") / "train.jsonl").exists():
            create_sample_data()
        
        # 初始化训练器
        trainer = StyleModelTrainer()
        
        # 运行训练
        trainer.run_training(
            learning_rate=2e-5,
            per_device_train_batch_size=4,
            num_train_epochs=3
        )
        
    except Exception as e:
        logger.error(f"训练失败: {e}")
        raise