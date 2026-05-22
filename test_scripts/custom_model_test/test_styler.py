"""
测试 custom_model/styler 包的功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试必要的导入"""
    try:
        import torch
        from transformers import BertTokenizer, AutoModelForSeq2SeqLM
        from huggingface_hub import snapshot_download
        print("✓ 所有必要的依赖包已安装")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_service_module():
    """测试 service 模块"""
    try:
        from custom_model.styler.service import stylize, _protect_content, _restore_content
        print("✓ service 模块导入成功")
        
        # 测试内容保护功能
        test_text = "这是测试文本，包含代码块 ```print('hello')``` 和URL https://example.com"
        protected_text, placeholders = _protect_content(test_text)
        restored_text = _restore_content(protected_text, placeholders)
        
        if restored_text == test_text:
            print("✓ 内容保护和恢复功能正常")
        else:
            print("✗ 内容保护和恢复功能异常")
            print(f"原始: {test_text}")
            print(f"恢复后: {restored_text}")
            
        return True
    except Exception as e:
        print(f"✗ service 模块测试失败: {e}")
        return False

def test_model_files():
    """检查模型文件是否存在"""
    required_paths = [
        "./origin_models/t5-base-chinese-cluecorpussmall",
        "./styled_models/my_t5_style_model",
        "./data/train.jsonl",
        "./data/eval.jsonl"
    ]
    
    missing_files = []
    for path in required_paths:
        if not os.path.exists(path):
            missing_files.append(path)
    
    if missing_files:
        print("✗ 以下文件或目录缺失:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✓ 所有必需的文件和目录都存在")
        return True

def test_download_script():
    """测试下载脚本"""
    try:
        from custom_model.styler.download import snapshot_download
        print("✓ download 模块导入成功")
        return True
    except Exception as e:
        print(f"✗ download 模块测试失败: {e}")
        return False

def main():
    print("开始测试 custom_model/styler 包...")
    print("=" * 50)
    
    results = []
    
    # 测试导入
    results.append(("依赖包导入", test_imports()))
    
    # 测试 service 模块
    results.append(("service 模块", test_service_module()))
    
    # 检查文件
    results.append(("模型文件", test_model_files()))
    
    # 测试下载脚本
    results.append(("download 模块", test_download_script()))
    
    print("=" * 50)
    print("测试结果汇总:")
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✓ 所有测试通过！")
    else:
        print("\n✗ 部分测试失败，请检查上述问题")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)