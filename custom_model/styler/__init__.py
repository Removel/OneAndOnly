"""
Styler 模块 - 文本风格化服务

该模块提供文本风格化功能，基于预训练的 T5 模型进行微调，
支持将原始文本转换为特定风格的文本。
"""

from .service import stylize, ModelManager
from .download import download_pretrained_model
from .train import StyleModelTrainer

__version__ = "1.0.0"
__all__ = ["stylize", "ModelManager", "download_pretrained_model", "StyleModelTrainer"]