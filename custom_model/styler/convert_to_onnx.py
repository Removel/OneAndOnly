"""
将T5风格化模型转换为ONNX格式以优化推理性能

使用ONNX Runtime可以获得更好的推理性能和更低的内存占用
"""

import logging
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from optimum.onnxruntime import ORTModelForSeq2SeqLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_to_onnx(
    model_path: str,
    output_path: str,
    task: str = "text2text-generation"
):
    """
    将PyTorch模型转换为ONNX格式
    
    参数:
        model_path: 原始模型路径
        output_path: ONNX模型输出路径
        task: 任务类型
    """
    try:
        logger.info(f"开始转换模型: {model_path}")
        
        # 加载tokenizer
        logger.info("加载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # 转换模型为ONNX格式
        logger.info("转换模型为ONNX格式...")
        model = ORTModelForSeq2SeqLM.from_pretrained(
            model_path,
            export=True,
            task=task
        )
        
        # 保存ONNX模型
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        logger.info(f"✓ ONNX模型转换完成，保存至: {output_path}")
        logger.info(f"  - 编码器: {output_dir / 'encoder_model.onnx'}")
        logger.info(f"  - 解码器: {output_dir / 'decoder_model.onnx'}")
        logger.info(f"  - 解码器带past: {output_dir / 'decoder_with_past_model.onnx'}")
        
    except Exception as e:
        logger.error(f"模型转换失败: {str(e)}")
        raise


def verify_onnx_model(
    model_path: str,
    test_text: str = "你好，今天天气很好。"
):
    """
    验证ONNX模型是否正常工作
    
    参数:
        model_path: ONNX模型路径
        test_text: 测试文本
    """
    try:
        logger.info("验证ONNX模型...")
        
        # 加载ONNX模型
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = ORTModelForSeq2SeqLM.from_pretrained(model_path)
        
        # 推理测试
        inputs = tokenizer(test_text, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=50)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"✓ ONNX模型验证成功")
        logger.info(f"  输入: {test_text}")
        logger.info(f"  输出: {result}")
        
    except Exception as e:
        logger.error(f"ONNX模型验证失败: {str(e)}")
        raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="转换T5模型为ONNX格式")
    parser.add_argument(
        "--model_path",
        type=str,
        default="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
        help="原始模型路径"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="./custom_model/styler/styled_models/my_t5_style_model/onnx",
        help="ONNX模型输出路径"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="转换后验证模型"
    )
    
    args = parser.parse_args()
    
    # 转换模型
    convert_to_onnx(args.model_path, args.output_path)
    
    # 验证模型
    if args.verify:
        verify_onnx_model(args.output_path)


if __name__ == "__main__":
    main()