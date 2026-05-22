"""
性能对比测试脚本

对比PyTorch和ONNX Runtime的推理性能
"""

import time
import logging
from pathlib import Path
from typing import List, Dict

from transformers import BertTokenizer, AutoModelForSeq2SeqLM
from optimum.onnxruntime import ORTModelForSeq2SeqLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """性能基准测试类"""
    
    def __init__(self, pytorch_model_path: str, onnx_model_path: str):
        """
        初始化性能基准测试
        
        参数:
            pytorch_model_path: PyTorch模型路径
            onnx_model_path: ONNX模型路径
        """
        self.pytorch_model_path = pytorch_model_path
        self.onnx_model_path = onnx_model_path
        self.device = self._get_device()
        
    def _get_device(self) -> str:
        """获取最佳设备"""
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"使用 GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            logger.info("使用 CPU")
        return device
    
    def load_pytorch_model(self):
        """加载PyTorch模型"""
        logger.info("加载PyTorch模型...")
        tokenizer = BertTokenizer.from_pretrained(self.pytorch_model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(self.pytorch_model_path)
        model.to(self.device)
        model.eval()
        return tokenizer, model
    
    def load_onnx_model(self):
        """加载ONNX模型"""
        logger.info("加载ONNX模型...")
        tokenizer = BertTokenizer.from_pretrained(self.onnx_model_path)
        
        provider = "CUDAExecutionProvider" if self.device == "cuda" else "CPUExecutionProvider"
        model = ORTModelForSeq2SeqLM.from_pretrained(
            self.onnx_model_path,
            provider=provider,
            use_cache=True
        )
        
        return tokenizer, model
    
    def benchmark_pytorch(
        self,
        texts: List[str],
        max_new_tokens: int = 512,
        warmup_runs: int = 3
    ) -> Dict[str, float]:
        """
        测试PyTorch模型性能
        
        参数:
            texts: 测试文本列表
            max_new_tokens: 最大生成token数
            warmup_runs: 预热运行次数
            
        返回:
            Dict[str, float]: 性能指标
        """
        tokenizer, model = self.load_pytorch_model()
        
        # 预热
        logger.info("PyTorch模型预热...")
        for i in range(warmup_runs):
            test_text = texts[i % len(texts)]
            inputs = tokenizer(test_text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
            with torch.no_grad():
                _ = model.generate(**inputs, max_new_tokens=50)
        
        # 正式测试
        logger.info("PyTorch模型性能测试...")
        total_time = 0
        total_tokens = 0
        
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
            
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
            end_time = time.time()
            
            total_time += (end_time - start_time)
            total_tokens += outputs.shape[1]
        
        # 清理内存
        del model
        del tokenizer
        if self.device == "cuda":
            import torch
            torch.cuda.empty_cache()
        
        return {
            "total_time": total_time,
            "avg_time": total_time / len(texts),
            "total_tokens": total_tokens,
            "tokens_per_second": total_tokens / total_time
        }
    
    def benchmark_onnx(
        self,
        texts: List[str],
        max_new_tokens: int = 512,
        warmup_runs: int = 3
    ) -> Dict[str, float]:
        """
        测试ONNX模型性能
        
        参数:
            texts: 测试文本列表
            max_new_tokens: 最大生成token数
            warmup_runs: 预热运行次数
            
        返回:
            Dict[str, float]: 性能指标
        """
        tokenizer, model = self.load_onnx_model()
        
        # 预热
        logger.info("ONNX模型预热...")
        for i in range(warmup_runs):
            test_text = texts[i % len(texts)]
            inputs = tokenizer(test_text, return_tensors="pt", truncation=True, max_length=512)
            _ = model.generate(**inputs, max_new_tokens=50)
        
        # 正式测试
        logger.info("ONNX模型性能测试...")
        total_time = 0
        total_tokens = 0
        
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            
            start_time = time.time()
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)
            end_time = time.time()
            
            total_time += (end_time - start_time)
            total_tokens += outputs.shape[1]
        
        # 清理内存
        del model
        del tokenizer
        
        return {
            "total_time": total_time,
            "avg_time": total_time / len(texts),
            "total_tokens": total_tokens,
            "tokens_per_second": total_tokens / total_time
        }
    
    def compare(self, texts: List[str], max_new_tokens: int = 512) -> Dict[str, Dict[str, float]]:
        """
        对比PyTorch和ONNX性能
        
        参数:
            texts: 测试文本列表
            max_new_tokens: 最大生成token数
            
        返回:
            Dict[str, Dict[str, float]]: 性能对比结果
        """
        logger.info("=" * 60)
        logger.info("开始性能对比测试")
        logger.info("=" * 60)
        
        # 测试PyTorch
        pytorch_results = self.benchmark_pytorch(texts, max_new_tokens)
        
        # 测试ONNX
        onnx_results = self.benchmark_onnx(texts, max_new_tokens)
        
        # 计算性能提升
        speedup = pytorch_results["avg_time"] / onnx_results["avg_time"]
        token_speedup = onnx_results["tokens_per_second"] / pytorch_results["tokens_per_second"]
        
        # 打印结果
        logger.info("=" * 60)
        logger.info("性能对比结果")
        logger.info("=" * 60)
        logger.info(f"测试样本数: {len(texts)}")
        logger.info(f"最大生成tokens: {max_new_tokens}")
        logger.info("")
        logger.info("PyTorch:")
        logger.info(f"  总时间: {pytorch_results['total_time']:.3f}s")
        logger.info(f"  平均时间: {pytorch_results['avg_time']:.3f}s")
        logger.info(f"  Tokens/s: {pytorch_results['tokens_per_second']:.2f}")
        logger.info("")
        logger.info("ONNX Runtime:")
        logger.info(f"  总时间: {onnx_results['total_time']:.3f}s")
        logger.info(f"  平均时间: {onnx_results['avg_time']:.3f}s")
        logger.info(f"  Tokens/s: {onnx_results['tokens_per_second']:.2f}")
        logger.info("")
        logger.info("性能提升:")
        logger.info(f"  速度提升: {speedup:.2f}x")
        logger.info(f"  Token生成速度提升: {token_speedup:.2f}x")
        logger.info("=" * 60)
        
        return {
            "pytorch": pytorch_results,
            "onnx": onnx_results,
            "speedup": speedup,
            "token_speedup": token_speedup
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="性能对比测试")
    parser.add_argument(
        "--pytorch_model_path",
        type=str,
        default="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
        help="PyTorch模型路径"
    )
    parser.add_argument(
        "--onnx_model_path",
        type=str,
        default="./custom_model/styler/styled_models/my_t5_style_model/onnx",
        help="ONNX模型路径"
    )
    parser.add_argument(
        "--max_new_tokens",
        type=int,
        default=512,
        help="最大生成token数"
    )
    parser.add_argument(
        "--num_tests",
        type=int,
        default=5,
        help="测试次数"
    )
    
    args = parser.parse_args()
    
    # 准备测试文本
    test_texts = [
        "你好，今天天气很好。",
        "这是一个测试文本，用于评估模型性能。",
        "人工智能技术正在快速发展，为各行各业带来了巨大的变革。",
        "机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的一种方法，它使用神经网络来模拟人脑的学习过程。"
    ] * args.num_tests
    
    # 运行性能对比
    benchmark = PerformanceBenchmark(
        args.pytorch_model_path,
        args.onnx_model_path
    )
    
    results = benchmark.compare(test_texts, args.max_new_tokens)


if __name__ == "__main__":
    main()