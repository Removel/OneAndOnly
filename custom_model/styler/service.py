"""
文本风格化服务模块

提供基于 T5 模型的文本风格化功能，支持懒加载模型、内容保护等功能
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os
import time

import torch
from transformers import BertTokenizer, AutoModelForSeq2SeqLM
from optimum.onnxruntime import ORTModelForSeq2SeqLM, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器，负责加载和管理风格化模型"""
    
    def __init__(
        self,
        model_path: str = "./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
        use_onnx: bool = True,
        use_quantization: bool = False,
        quantization_mode: str = "dynamic"
    ):
        """
        初始化模型管理器
        
        参数:
            model_path: 微调后模型的存放路径
            use_onnx: 是否使用ONNX Runtime进行推理
            use_quantization: 是否使用量化
            quantization_mode: 量化模式 (dynamic, static)
        """
        self.model_path = Path(model_path)
        self.use_onnx = use_onnx
        self.use_quantization = use_quantization
        self.quantization_mode = quantization_mode
        self._tokenizer = None
        self._model = None
        self._device = None
        self._is_loaded = False
        
        # 如果使用ONNX，检查ONNX模型是否存在
        if self.use_onnx:
            onnx_path = self._get_onnx_path()
            if not onnx_path.exists():
                logger.warning(f"ONNX模型不存在: {onnx_path}")
                logger.info("将回退到PyTorch模型")
                self.use_onnx = False
        
    def _get_onnx_path(self) -> Path:
        """
        获取ONNX模型路径
        
        返回:
            Path: ONNX模型路径
        """
        # 检查模型路径是否已经是ONNX路径
        if self.model_path.name == "onnx":
            return self.model_path
        
        # 构建ONNX路径
        onnx_path = self.model_path.parent / "onnx"
        return onnx_path
    
    def load_model(self) -> Tuple[BertTokenizer, Any, str]:
        """
        加载模型（懒加载模式）
        
        返回:
            Tuple[BertTokenizer, Any, str]: 分词器、模型和设备
        """
        if self._is_loaded:
            return self._tokenizer, self._model, self._device
            
        try:
            # 确定设备
            self._device = self._get_device()
            
            # 根据配置选择加载方式
            if self.use_onnx:
                self._load_onnx_model()
            else:
                self._load_pytorch_model()
            
            self._is_loaded = True
            logger.info(f"✓ 模型加载成功，设备: {self._device}, ONNX: {self.use_onnx}")
            
            return self._tokenizer, self._model, self._device
            
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise RuntimeError(f"模型加载失败: {str(e)}")
    
    def _load_pytorch_model(self):
        """加载PyTorch模型"""
        try:
            # 检查模型路径是否存在
            if not self.model_path.exists():
                raise FileNotFoundError(f"模型路径不存在: {self.model_path}")
            
            # 检查必要的模型文件
            required_files = ["config.json", "tokenizer_config.json"]
            model_files = ["model.safetensors", "pytorch_model.bin"]
            missing_files = [f for f in required_files if not (self.model_path / f).exists()]
            
            has_model_file = any((self.model_path / f).exists() for f in model_files)
            if not has_model_file:
                missing_files.extend(model_files)
            
            if missing_files:
                raise FileNotFoundError(
                    f"模型文件不完整，缺失文件: {', '.join(missing_files)}"
                )
            
            # 加载模型
            logger.info(f"正在加载PyTorch模型: {self.model_path}")
            self._tokenizer = BertTokenizer.from_pretrained(str(self.model_path))
            self._model = AutoModelForSeq2SeqLM.from_pretrained(str(self.model_path))
            self._model.to(self._device)
            self._model.eval()
            
        except Exception as e:
            logger.error(f"PyTorch模型加载失败: {str(e)}")
            raise
    
    def _load_onnx_model(self):
        """加载ONNX模型"""
        try:
            onnx_path = self._get_onnx_path()
            
            if not onnx_path.exists():
                raise FileNotFoundError(f"ONNX模型路径不存在: {onnx_path}")
            
            # 检查必要的ONNX模型文件
            required_onnx_files = [
                "encoder_model.onnx",
                "decoder_model.onnx",
                "decoder_with_past_model.onnx"
            ]
            missing_files = [f for f in required_onnx_files if not (onnx_path / f).exists()]
            
            if missing_files:
                raise FileNotFoundError(
                    f"ONNX模型文件不完整，缺失文件: {', '.join(missing_files)}"
                )
            
            # 加载ONNX模型
            logger.info(f"正在加载ONNX模型: {onnx_path}")
            self._tokenizer = BertTokenizer.from_pretrained(str(onnx_path))
            
            # 根据是否量化选择加载方式
            if self.use_quantization:
                logger.info(f"使用量化模式: {self.quantization_mode}")
                self._model = ORTModelForSeq2SeqLM.from_pretrained(
                    str(onnx_path),
                    provider=self._get_onnx_provider(),
                    use_cache=True
                )
            else:
                self._model = ORTModelForSeq2SeqLM.from_pretrained(
                    str(onnx_path),
                    provider=self._get_onnx_provider(),
                    use_cache=True
                )
            
        except Exception as e:
            logger.error(f"ONNX模型加载失败: {str(e)}")
            logger.info("回退到PyTorch模型")
            self.use_onnx = False
            self._load_pytorch_model()
    
    def _get_onnx_provider(self) -> str:
        """
        获取ONNX Runtime提供者
        
        返回:
            str: 提供者名称
        """
        if self._device == "cuda":
            return "CUDAExecutionProvider"
        else:
            return "CPUExecutionProvider"
    
    def _get_device(self) -> str:
        """
        获取最佳设备
        
        返回:
            str: 设备名称 (cuda/cpu)
        """
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"使用 GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("使用 CPU")
        return device
    
    def unload_model(self):
        """卸载模型，释放内存"""
        if self._is_loaded:
            del self._model
            del self._tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            self._model = None
            self._tokenizer = None
            self._is_loaded = False
            logger.info("模型已卸载")


class ContentProtector:
    """内容保护器，保护代码块、URL等精确内容"""
    
    # 保护模式
    CODE_PATTERN = r'```.*?```'
    URL_PATTERN = r'https?://\S+'
    NUMBER_PATTERN = r'\d+'
    
    def __init__(self):
        self.placeholder_counter = {
            'code': 0,
            'url': 0,
            'number': 0
        }
    
    def protect_content(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        保护文本中的精确内容
        
        参数:
            text: 原始文本
            
        返回:
            Tuple[str, Dict[str, str]]: 保护后的文本和占位符映射
        """
        placeholders = {}
        
        # 重置计数器
        for key in self.placeholder_counter:
            self.placeholder_counter[key] = 0
        
        # 收集所有需要替换的位置和内容
        replacements = []
        
        # 收集代码块 ```...```
        for match in re.finditer(self.CODE_PATTERN, text, re.DOTALL):
            placeholder = f"__CODE_BLOCK_{self.placeholder_counter['code']}__"
            replacements.append((match.start(), match.end(), placeholder, match.group(0)))
            self.placeholder_counter['code'] += 1
        
        # 收集 URL
        for match in re.finditer(self.URL_PATTERN, text):
            placeholder = f"__URL_LINK_{self.placeholder_counter['url']}__"
            replacements.append((match.start(), match.end(), placeholder, match.group(0)))
            self.placeholder_counter['url'] += 1
        
        # 收集数字
        for match in re.finditer(self.NUMBER_PATTERN, text):
            placeholder = f"__NUM_VALUE_{self.placeholder_counter['number']}__"
            replacements.append((match.start(), match.end(), placeholder, match.group(0)))
            self.placeholder_counter['number'] += 1
        
        # 按位置排序，从后往前替换，避免位置偏移
        replacements.sort(key=lambda x: x[0], reverse=True)
        
        # 执行替换
        text_list = list(text)
        for start, end, placeholder, original in replacements:
            text_list[start:end] = list(placeholder)
            placeholders[placeholder] = original
        
        protected_text = ''.join(text_list)
        
        return protected_text, placeholders
    
    def restore_content(self, text: str, placeholders: Dict[str, str]) -> str:
        """
        恢复被保护的内容
        
        参数:
            text: 保护后的文本
            placeholders: 占位符映射
            
        返回:
            str: 恢复后的文本
        """
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        return text


# 全局模型管理器实例
_global_model_manager = None
_global_content_protector = None


def get_model_manager(
    model_path: str = "./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
    use_onnx: bool = True,
    use_quantization: bool = False,
    quantization_mode: str = "dynamic"
) -> ModelManager:
    """
    获取全局模型管理器实例
    
    参数:
        model_path: 模型路径
        use_onnx: 是否使用ONNX Runtime进行推理
        use_quantization: 是否使用量化
        quantization_mode: 量化模式
        
    返回:
        ModelManager: 模型管理器实例
    """
    global _global_model_manager
    if _global_model_manager is None:
        _global_model_manager = ModelManager(
            model_path=model_path,
            use_onnx=use_onnx,
            use_quantization=use_quantization,
            quantization_mode=quantization_mode
        )
    return _global_model_manager


def get_content_protector() -> ContentProtector:
    """
    获取全局内容保护器实例
    
    返回:
        ContentProtector: 内容保护器实例
    """
    global _global_content_protector
    if _global_content_protector is None:
        _global_content_protector = ContentProtector()
    return _global_content_protector


def stylize(
    raw_text: str,
    model_path: str = "./styled_models/my_t5_style_model",
    max_new_tokens: int = 4096,
    do_sample: bool = False,
    num_beams: int = 1,
    temperature: float = 1.0,
    top_p: float = 1.0,
    use_onnx: bool = True,
    use_quantization: bool = False,
    quantization_mode: str = "dynamic"
) -> str:
    """
    对外暴露的接口：输入原始文本，输出风格化后的文本
    
    参数:
        raw_text: Execute 节点输出的原始回答
        model_path: 微调后模型的存放路径
        max_new_tokens: 生成的最大 token 数
        do_sample: 是否使用采样生成
        num_beams: beam search 的数量
        temperature: 采样温度
        top_p: nucleus sampling 的 p 值
        use_onnx: 是否使用ONNX Runtime进行推理
        use_quantization: 是否使用量化
        quantization_mode: 量化模式
        
    返回:
        str: 风格化后的文本
        
    异常:
        RuntimeError: 模型加载或推理失败时抛出
    """
    if not raw_text or not raw_text.strip():
        logger.warning("输入文本为空")
        return raw_text
    
    start_time = time.time()
    
    try:
        # 1. 获取模型管理器并加载模型
        model_manager = get_model_manager(
            model_path=model_path,
            use_onnx=use_onnx,
            use_quantization=use_quantization,
            quantization_mode=quantization_mode
        )
        tokenizer, model, device = model_manager.load_model()
        
        # 2. 保护精确内容
        content_protector = get_content_protector()
        protected_text, placeholders = content_protector.protect_content(raw_text)
        
        # 3. 风格化转换
        inputs = tokenizer(
            protected_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            return_token_type_ids=False
        )
        
        # 根据模型类型调整输入
        if model_manager.use_onnx:
            # ONNX Runtime不需要将输入移动到设备
            pass
        else:
            # PyTorch模型需要将输入移动到设备
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        inference_start = time.time()
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                num_beams=num_beams,
                temperature=temperature,
                top_p=top_p
            )
        
        inference_time = time.time() - inference_start
        
        styled_protected = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 4. 恢复精确内容
        final_text = content_protector.restore_content(styled_protected, placeholders)
        
        total_time = time.time() - start_time
        
        logger.info(f"文本风格化完成")
        logger.info(f"  原始长度: {len(raw_text)}, 风格化后长度: {len(final_text)}")
        logger.info(f"  推理引擎: {'ONNX Runtime' if model_manager.use_onnx else 'PyTorch'}")
        logger.info(f"  量化: {'是' if model_manager.use_quantization else '否'}")
        logger.info(f"  推理时间: {inference_time:.3f}s, 总时间: {total_time:.3f}s")
        
        return final_text
        
    except Exception as e:
        logger.error(f"文本风格化失败: {str(e)}")
        raise RuntimeError(f"文本风格化失败: {str(e)}")


def batch_stylize(
    texts: list,
    model_path: str = "./styled_models/my_t5_style_model",
    max_new_tokens: int = 4096,
    batch_size: int = 4,
    use_onnx: bool = True,
    use_quantization: bool = False,
    quantization_mode: str = "dynamic"
) -> list:
    """
    批量文本风格化
    
    参数:
        texts: 文本列表
        model_path: 模型路径
        max_new_tokens: 最大生成 token 数
        batch_size: 批处理大小
        use_onnx: 是否使用ONNX Runtime进行推理
        use_quantization: 是否使用量化
        quantization_mode: 量化模式
        
    返回:
        list: 风格化后的文本列表
    """
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_results = []
        
        for text in batch:
            try:
                styled_text = stylize(
                    text,
                    model_path,
                    max_new_tokens,
                    use_onnx=use_onnx,
                    use_quantization=use_quantization,
                    quantization_mode=quantization_mode
                )
                batch_results.append(styled_text)
            except Exception as e:
                logger.error(f"文本风格化失败: {str(e)}")
                batch_results.append(text)
        
        results.extend(batch_results)
    
    return results


if __name__ == "__main__":
    # 示例用法
    test_text = """
    你好，今天天气很好。
    这是代码示例：
    ```python
    def hello():
        print("Hello, World!")
    ```
    访问 https://example.com 了解更多信息。
    """
    
    try:
        styled_text = stylize(test_text)
        print("原始文本:")
        print(test_text)
        print("\n风格化文本:")
        print(styled_text)
    except Exception as e:
        print(f"错误: {e}")