"""
文本风格化服务模块

提供基于 T5 模型的文本风格化功能，支持懒加载模型、内容保护等功能
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os
import time

import torch
from transformers import BertTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器，负责加载和管理风格化模型"""
    
    def __init__(
        self,
        model_path: str = "./custom_model/styler/styled_models/my_t5_style_model/checkpoint-300"
    ):
        """
        初始化模型管理器
        
        参数:
            model_path: 微调后模型的存放路径
        """
        # 存储模型路径
        self.model_path = Path(model_path)
        # 初始化模型组件（懒加载）
        self._tokenizer = None      # 分词器实例
        self._model = None          # 模型实例
        self._device = None         # 推理设备
        self._is_loaded = False     # 加载状态标记
        

    
    def load_model(self) -> Tuple[BertTokenizer, Any, str]:
        """
        加载模型（懒加载模式）
        
        返回:
            Tuple[BertTokenizer, Any, str]: 分词器、模型和设备
        """
        # 检查模型是否已经加载，如果是则直接返回现有实例（懒加载机制）
        if self._is_loaded:
            return self._tokenizer, self._model, self._device
            
        try:
            # 自动确定最优的推理设备（GPU 或 CPU）
            self._device = self._get_device()
            
            # 执行实际的模型加载过程
            self._load_pytorch_model()
            
            # 更新加载状态
            self._is_loaded = True
            logger.info(f"✓ 模型加载成功，设备: {self._device}")
            
            return self._tokenizer, self._model, self._device
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise RuntimeError(f"模型加载失败: {str(e)}")
    
    def _load_pytorch_model(self):
        """加载PyTorch模型（支持基础模型或LoRA适配器）"""
        try:
            # 第一步：验证模型路径是否存在
            if not self.model_path.exists():
                raise FileNotFoundError(f"模型路径不存在: {self.model_path}")
            
            # 第二步：检查是否是指向具体checkpoint的路径，否则尝试查找子目录中的checkpoint
            model_path = self.model_path
            if self._is_checkpoint_directory(model_path):
                # 如果当前路径已经是指向checkpoint的路径，直接使用
                actual_model_path = model_path
            else:
                # 否则尝试查找子目录中的checkpoint
                checkpoint_dirs = [d for d in self.model_path.iterdir() 
                                 if d.is_dir() and d.name.startswith('checkpoint-')]
                if checkpoint_dirs:
                    # 选择最新的checkpoint目录
                    actual_model_path = sorted(checkpoint_dirs, 
                                             key=lambda x: int(x.name.split('-')[1]))[-1]
                    logger.info(f"找到checkpoint目录: {actual_model_path}")
                else:
                    # 如果没有找到checkpoint子目录，使用原路径
                    actual_model_path = model_path
            
            # 第三步：检查是否为LoRA适配器路径（包含adapter_config.json）
            adapter_config_path = actual_model_path / "adapter_config.json"
            if adapter_config_path.exists():
                # 这是一个LoRA适配器，需要先加载基础模型，然后应用适配器
                logger.info(f"检测到LoRA适配器: {actual_model_path}")
                
                # 查找基础模型路径（通过adapter_config.json中的信息）
                import json
                with open(adapter_config_path, 'r', encoding='utf-8') as f:
                    adapter_config = json.load(f)
                
                # 从适配器配置中获取基础模型路径（如果有的话）
                # 否则需要用户提供基础模型路径
                base_model_path = adapter_config.get("base_model_name_or_path", "./origin_models/uer-t5-base-chinese-cluecorpussmall")
                
                logger.info(f"正在加载基础模型: {base_model_path}")
                self._tokenizer = BertTokenizer.from_pretrained(base_model_path)
                
                # 修复tokenizer配置：添加缺失的EOS token
                if self._tokenizer.eos_token is None:
                    # 使用[SEP]作为EOS token
                    self._tokenizer.eos_token = "[SEP]"
                    self._tokenizer.eos_token_id = self._tokenizer.convert_tokens_to_ids("[SEP]")
                    logger.info(f"设置EOS token: {self._tokenizer.eos_token} (ID: {self._tokenizer.eos_token_id})")
                
                base_model = AutoModelForSeq2SeqLM.from_pretrained(base_model_path)
                
                # 确保模型的配置与tokenizer一致
                if base_model.config.eos_token_id is None:
                    base_model.config.eos_token_id = self._tokenizer.eos_token_id
                    logger.info(f"设置模型EOS token ID: {base_model.config.eos_token_id}")
                
                logger.info(f"正在应用LoRA适配器: {actual_model_path}")
                self._model = PeftModel.from_pretrained(base_model, str(actual_model_path))
                
            else:
                # 这是一个完整的模型（非LoRA），按原方式加载
                # 检查模型文件完整性，确保必要的文件都存在
                required_files = ["config.json", "tokenizer_config.json"]  # 必需的配置文件
                model_files = ["model.safetensors", "pytorch_model.bin"]   # 模型权重文件
                missing_files = [f for f in required_files if not (actual_model_path / f).exists()]
                
                # 检查是否有模型权重文件存在
                has_model_file = any((actual_model_path / f).exists() for f in model_files)
                if not has_model_file:
                    missing_files.extend(model_files)
                
                # 如果有任何必需文件缺失，则抛出异常
                if missing_files:
                    raise FileNotFoundError(
                        f"模型文件不完整，缺失文件: {', '.join(missing_files)}"
                    )
                
                # 加载完整的预训练模型
                logger.info(f"正在加载完整模型: {actual_model_path}")
                self._tokenizer = BertTokenizer.from_pretrained(str(actual_model_path))
                self._model = AutoModelForSeq2SeqLM.from_pretrained(str(actual_model_path))
            
            # 将模型移动到指定设备（GPU或CPU）以进行推理
            self._model.to(self._device)
            # 设置模型为评估模式
            self._model.eval()
            # 不融合LoRA权重，直接使用LoRA适配器以确保正确性
            # 如果融合权重出现问题，会导致生成异常
            logger.info("使用LoRA适配器进行推理...")
            
        except Exception as e:
            logger.error(f"PyTorch模型加载失败: {str(e)}")
            raise
    
    def _is_checkpoint_directory(self, path: Path) -> bool:
        """
        检查路径是否为有效的checkpoint目录
        通过检查必需的模型文件是否存在来判断
        
        参数:
            path: 要检查的路径
            
        返回:
            bool: 如果是有效的checkpoint目录则返回True
        """
        required_files = ["config.json", "tokenizer_config.json"]
        model_files = ["model.safetensors", "pytorch_model.bin"]
        
        has_required_files = all((path / f).exists() for f in required_files)
        has_model_files = any((path / f).exists() for f in model_files)
        
        return has_required_files and has_model_files
    
    def _get_device(self) -> str:
        """
        获取最佳设备
        
        返回:
            str: 设备名称 (cuda/cpu)
        """
        # 检查 CUDA 是否可用，以决定使用 GPU 还是 CPU
        if torch.cuda.is_available():
            device = "cuda"
            # 记录使用的 GPU 设备信息
            logger.info(f"使用 GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            # 当 CUDA 不可用时，使用 CPU
            logger.info("使用 CPU")
        return device
    
    def unload_model(self):
        """
        卸载模型，释放内存
        用于清理不再需要的模型实例以节省系统资源
        """
        if self._is_loaded:
            # 删除模型和分词器实例，释放内存
            del self._model
            del self._tokenizer
            # 如果使用GPU，清理GPU缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            # 重置内部状态
            self._model = None
            self._tokenizer = None
            self._is_loaded = False
            logger.info("模型已卸载")


# 全局模型管理器实例
_global_model_manager = None


def get_model_manager(
    model_path: str = "./custom_model/styler/styled_models/my_t5_style_model"
) -> ModelManager:
    """
    获取全局模型管理器实例
    
    参数:
        model_path: 模型路径
        
    返回:
        ModelManager: 模型管理器实例
    """
    global _global_model_manager
    if _global_model_manager is None:
        _global_model_manager = ModelManager(
            model_path=model_path
        )
    return _global_model_manager


def stylize(
    raw_text: str,
    model_path: str = "./styled_models/my_t5_style_model",
    max_new_tokens: int = 256,
    do_sample: bool = True,
    num_beams: int = 4,
    temperature: float = 0.7,
    top_p: float = 0.9
) -> str:
    """
    对外暴露的接口：输入原始文本，输出风格化后的文本
    
    参数:
        raw_text: Execute 节点输出的原始回答
        model_path: 微调后模型的存放路径（相对于当前工作目录）
        max_new_tokens: 生成的最大 token 数
        do_sample: 是否使用采样生成
        num_beams: beam search 的数量
        temperature: 采样温度
        top_p: nucleus sampling 的 p 值
        
    返回:
        str: 风格化后的文本
        
    异常:
        RuntimeError: 模型加载或推理失败时抛出
    """
    # 输入验证：检查原始文本是否为空
    if not raw_text or not raw_text.strip():
        logger.warning("输入文本为空")
        return raw_text
    
    # 记录总处理时间
    start_time = time.time()
    
    try:
        # 步骤1：获取模型管理器并加载模型（使用懒加载机制，如果模型已加载则直接返回）
        model_manager = get_model_manager(
            model_path=model_path
        )
        tokenizer, model, device = model_manager.load_model()
        
        # 步骤2：对输入文本进行分词处理，准备模型输入
        inputs = tokenizer(
            raw_text,                    # 原始输入文本
            return_tensors="pt",         # 返回 PyTorch 张量格式
            truncation=True,             # 启用截断，防止过长输入
            max_length=512,              # 最大序列长度限制
            return_token_type_ids=False  # T5 模型不需要 token type ids
        )
        
        # 步骤3：将输入张量移动到指定设备（GPU 或 CPU）进行推理
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 记录推理时间
        inference_start = time.time()
        
        # 步骤4：执行模型推理，生成风格化文本
        with torch.no_grad():  # 禁用梯度计算以节省内存和加速推理
            outputs = model.generate(
                **inputs,                   # 模型输入
                min_length=max(len(inputs['input_ids'][0]), 20),  # 设置最小长度，至少与输入一样长，最少20个token
                max_new_tokens=min(max_new_tokens, 256),  # 限制生成的最大 token 数，避免过度生成
                do_sample=do_sample,        # 是否使用采样策略
                num_beams=max(num_beams, 6), # 增加beam数量到6，提高输出质量
                temperature=max(0.4, min(temperature, 1.0)),  # 稍微提高温度，增加探索性
                top_p=top_p,                # nucleus sampling 参数
                repetition_penalty=1.0,     # 降低重复惩罚，避免过度限制
                length_penalty=1.2,         # 增加长度惩罚，鼓励生成更长内容
                early_stopping=False,       # 禁用提前停止，让模型生成到min_length
                pad_token_id=tokenizer.pad_token_id,  # 确保使用正确的pad token
                eos_token_id=tokenizer.eos_token_id,  # 确保使用正确的结束token
                no_repeat_ngram_size=3      # 防止3-gram重复
            )
        
        # 计算推理耗时
        inference_time = time.time() - inference_start
        
        # 步骤5：将模型输出的 token 序列解码为可读文本
        # 由于设置了EOS token，不跳过特殊token以确保正确处理EOS
        final_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
        
        # 后处理：检查并修复明显的错误输出
        if not final_text.strip() or "extra0" in final_text or final_text.strip() == "[SEP]":
            # 如果输出包含错误的特殊token，尝试清理
            import re
            # 移除特殊token标记
            final_text = re.sub(r'\[extra_id_\d+\]', '', final_text)
            final_text = re.sub(r'extra\d+', '', final_text)
            final_text = final_text.replace('[SEP]', '').strip()
            
            if not final_text.strip():
                # 如果清理后仍然为空，使用原始文本
                final_text = raw_text
                logger.warning("检测到无效输出，使用原始文本作为替代")
            else:
                logger.warning("检测到特殊token，已清理输出")
        
        # 计算总处理时间
        total_time = time.time() - start_time
        
        # 记录处理结果和性能指标
        logger.info(f"文本风格化完成")
        logger.info(f"  原始长度: {len(raw_text)}, 风格化后长度: {len(final_text)}")
        logger.info(f"  推理引擎: PyTorch")
        logger.info(f"  推理时间: {inference_time:.3f}s, 总时间: {total_time:.3f}s")
        
        return final_text
        
    except Exception as e:
        logger.error(f"文本风格化失败: {str(e)}")
        raise RuntimeError(f"文本风格化失败: {str(e)}")




if __name__ == "__main__":
    # 示例用法
    test_text_1 = """
    你好，今天天气很好。
    """
    test_text_2=  """
    这是代码示例：
    ```python
    def hello():
        print("Hello, World!")
    ```
    """
    test_text_3 = """
    访问 https://example.com 了解更多信息。
    """
    
    try:
        styled_text_1 = stylize(test_text_1)
        print("原始文本:")
        print(test_text_1)
        print("\n风格化文本:")
        print(styled_text_1)

        styled_text_2 = stylize(test_text_2)
        print("原始文本:")
        print(test_text_2)
        print("\n风格化文本:")
        print(styled_text_2)

        styled_text_3 = stylize(test_text_3)
        print("原始文本:")
        print(test_text_3)
        print("\n风格化文本:")
        print(styled_text_3)
    except Exception as e:
        print(f"错误: {e}")