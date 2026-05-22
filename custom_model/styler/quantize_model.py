"""
ONNX模型量化脚本

对ONNX模型进行量化以进一步优化推理性能和减少内存占用
"""

import logging
from pathlib import Path

from optimum.onnxruntime import ORTModelForSeq2SeqLM, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def quantize_model(
    model_path: str,
    output_path: str,
    quantization_mode: str = "dynamic",
    per_channel: bool = False,
    reduce_range: bool = False
):
    """
    量化ONNX模型
    
    参数:
        model_path: ONNX模型路径
        output_path: 量化模型输出路径
        quantization_mode: 量化模式 (dynamic, static)
        per_channel: 是否使用per-channel量化
        reduce_range: 是否减少量化范围
    """
    try:
        logger.info(f"开始量化模型: {model_path}")
        logger.info(f"量化模式: {quantization_mode}")
        
        # 加载tokenizer
        logger.info("加载tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # 加载ONNX模型
        logger.info("加载ONNX模型...")
        model = ORTModelForSeq2SeqLM.from_pretrained(model_path)
        
        # 配置量化
        if quantization_mode == "dynamic":
            logger.info("使用动态量化")
            qconfig = AutoQuantizationConfig.avx512_vnni(
                is_static=False,
                per_channel=per_channel,
                reduce_range=reduce_range
            )
        elif quantization_mode == "static":
            logger.info("使用静态量化")
            qconfig = AutoQuantizationConfig.avx512_vnni(
                is_static=True,
                per_channel=per_channel,
                reduce_range=reduce_range
            )
        else:
            raise ValueError(f"不支持的量化模式: {quantization_mode}")
        
        # 创建量化器
        quantizer = ORTQuantizer.from_pretrained(model)
        
        # 量化模型
        logger.info("正在量化模型...")
        quantized_model_path = quantizer.quantize(
            save_dir=output_path,
            quantization_config=qconfig
        )
        
        # 保存tokenizer
        tokenizer.save_pretrained(output_path)
        
        logger.info(f"✓ 模型量化完成，保存至: {output_path}")
        logger.info(f"  量化模式: {quantization_mode}")
        logger.info(f"  Per-channel: {per_channel}")
        logger.info(f"  Reduce range: {reduce_range}")
        
    except Exception as e:
        logger.error(f"模型量化失败: {str(e)}")
        raise


def verify_quantized_model(
    model_path: str,
    test_text: str = "你好，今天天气很好。"
):
    """
    验证量化后的模型是否正常工作
    
    参数:
        model_path: 量化模型路径
        test_text: 测试文本
    """
    try:
        logger.info("验证量化模型...")
        
        # 加载量化模型
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = ORTModelForSeq2SeqLM.from_pretrained(model_path)
        
        # 推理测试
        inputs = tokenizer(test_text, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=50)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"✓ 量化模型验证成功")
        logger.info(f"  输入: {test_text}")
        logger.info(f"  输出: {result}")
        
    except Exception as e:
        logger.error(f"量化模型验证失败: {str(e)}")
        raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="量化ONNX模型")
    parser.add_argument(
        "--model_path",
        type=str,
        default="./custom_model/styler/styled_models/my_t5_style_model/onnx",
        help="ONNX模型路径"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="./custom_model/styler/styled_models/my_t5_style_model/onnx_quantized",
        help="量化模型输出路径"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="dynamic",
        choices=["dynamic", "static"],
        help="量化模式"
    )
    parser.add_argument(
        "--per_channel",
        action="store_true",
        help="使用per-channel量化"
    )
    parser.add_argument(
        "--reduce_range",
        action="store_true",
        help="减少量化范围"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="量化后验证模型"
    )
    
    args = parser.parse_args()
    
    # 量化模型
    quantize_model(
        args.model_path,
        args.output_path,
        args.mode,
        args.per_channel,
        args.reduce_range
    )
    
    # 验证模型
    if args.verify:
        verify_quantized_model(args.output_path)


if __name__ == "__main__":
    main()