"""
ONNX Runtime集成测试脚本

测试ONNX Runtime集成是否正常工作
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """测试必要的依赖是否可以导入"""
    logger.info("测试依赖导入...")
    
    try:
        import torch
        logger.info("✓ torch 导入成功")
    except ImportError as e:
        logger.error(f"✗ torch 导入失败: {e}")
        return False
    
    try:
        from transformers import BertTokenizer, AutoModelForSeq2SeqLM
        logger.info("✓ transformers 导入成功")
    except ImportError as e:
        logger.error(f"✗ transformers 导入失败: {e}")
        return False
    
    try:
        from optimum.onnxruntime import ORTModelForSeq2SeqLM
        logger.info("✓ optimum.onnxruntime 导入成功")
    except ImportError as e:
        logger.error(f"✗ optimum.onnxruntime 导入失败: {e}")
        return False
    
    return True


def test_service_module():
    """测试service模块是否可以正常导入"""
    logger.info("\n测试service模块...")
    
    try:
        from custom_model.styler.service import (
            ModelManager,
            ContentProtector,
            stylize,
            batch_stylize
        )
        logger.info("✓ service模块导入成功")
        return True
    except ImportError as e:
        logger.error(f"✗ service模块导入失败: {e}")
        return False


def test_model_manager_creation():
    """测试ModelManager是否可以正常创建"""
    logger.info("\n测试ModelManager创建...")
    
    try:
        from custom_model.styler.service import ModelManager
        
        # 测试PyTorch模式
        manager_pytorch = ModelManager(
            model_path="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
            use_onnx=False
        )
        logger.info("✓ PyTorch模式ModelManager创建成功")
        
        # 测试ONNX模式
        manager_onnx = ModelManager(
            model_path="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
            use_onnx=True
        )
        logger.info("✓ ONNX模式ModelManager创建成功")
        
        return True
    except Exception as e:
        logger.error(f"✗ ModelManager创建失败: {e}")
        return False


def test_content_protector():
    """测试ContentProtector是否正常工作"""
    logger.info("\n测试ContentProtector...")
    
    try:
        from custom_model.styler.service import ContentProtector
        
        protector = ContentProtector()
        test_text = "这是一个测试 https://example.com 代码：```python\nprint('hello')\n``` 数字：123"
        
        protected_text, placeholders = protector.protect_content(test_text)
        logger.info(f"✓ 内容保护成功")
        logger.info(f"  原始文本: {test_text}")
        logger.info(f"  保护后: {protected_text}")
        logger.info(f"  占位符: {placeholders}")
        
        restored_text = protector.restore_content(protected_text, placeholders)
        logger.info(f"✓ 内容恢复成功")
        logger.info(f"  恢复后: {restored_text}")
        
        if restored_text == test_text:
            logger.info("✓ 内容保护/恢复验证成功")
            return True
        else:
            logger.error("✗ 内容保护/恢复验证失败")
            return False
            
    except Exception as e:
        logger.error(f"✗ ContentProtector测试失败: {e}")
        return False


def test_model_files():
    """测试模型文件是否存在"""
    logger.info("\n测试模型文件...")
    
    pytorch_path = Path("./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6")
    onnx_path = Path("./custom_model/styler/styled_models/my_t5_style_model/onnx")
    
    # 检查PyTorch模型
    if pytorch_path.exists():
        logger.info(f"✓ PyTorch模型路径存在: {pytorch_path}")
        required_files = ["config.json", "tokenizer_config.json", "model.safetensors"]
        for file in required_files:
            if (pytorch_path / file).exists():
                logger.info(f"  ✓ {file} 存在")
            else:
                logger.warning(f"  ✗ {file} 不存在")
    else:
        logger.warning(f"✗ PyTorch模型路径不存在: {pytorch_path}")
    
    # 检查ONNX模型
    if onnx_path.exists():
        logger.info(f"✓ ONNX模型路径存在: {onnx_path}")
        required_files = ["encoder_model.onnx", "decoder_model.onnx", "decoder_with_past_model.onnx"]
        for file in required_files:
            if (onnx_path / file).exists():
                logger.info(f"  ✓ {file} 存在")
            else:
                logger.warning(f"  ✗ {file} 不存在")
    else:
        logger.info(f"ℹ ONNX模型路径不存在（需要转换）: {onnx_path}")
    
    return True


def test_stylize_function_signature():
    """测试stylize函数签名是否正确"""
    logger.info("\n测试stylize函数签名...")
    
    try:
        from custom_model.styler.service import stylize
        import inspect
        
        sig = inspect.signature(stylize)
        params = list(sig.parameters.keys())
        
        expected_params = [
            'raw_text', 'model_path', 'max_new_tokens', 'do_sample',
            'num_beams', 'temperature', 'top_p', 'use_onnx',
            'use_quantization', 'quantization_mode'
        ]
        
        if all(param in params for param in expected_params):
            logger.info("✓ stylize函数签名正确")
            logger.info(f"  参数: {params}")
            return True
        else:
            logger.error("✗ stylize函数签名不完整")
            logger.error(f"  期望参数: {expected_params}")
            logger.error(f"  实际参数: {params}")
            return False
            
    except Exception as e:
        logger.error(f"✗ stylize函数签名测试失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("ONNX Runtime集成测试")
    logger.info("=" * 60)
    
    tests = [
        ("依赖导入", test_imports),
        ("service模块", test_service_module),
        ("ModelManager创建", test_model_manager_creation),
        ("ContentProtector", test_content_protector),
        ("模型文件", test_model_files),
        ("stylize函数签名", test_stylize_function_signature),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 发生异常: {e}")
            results.append((test_name, False))
    
    # 打印测试结果摘要
    logger.info("\n" + "=" * 60)
    logger.info("测试结果摘要")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
    
    logger.info("=" * 60)
    logger.info(f"总计: {passed}/{total} 测试通过")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("✓ 所有测试通过！")
        return 0
    else:
        logger.warning("✗ 部分测试失败，请检查上述错误信息")
        return 1


if __name__ == "__main__":
    exit(main())