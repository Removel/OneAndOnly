"""
下载预训练模型模块

提供从 Hugging Face Hub 下载预训练 T5 模型的功能
"""

import os
from pathlib import Path
from typing import Optional
from huggingface_hub import snapshot_download, HfApi
from tqdm import tqdm


def download_pretrained_model(
    repo_id: str = "uer/t5-base-chinese-cluecorpussmall",
    local_dir: Optional[str] = None,
    resume_download: bool = True,
    force_download: bool = False
) -> str:
    """
    从 Hugging Face Hub 下载预训练模型
    
    参数:
        repo_id: Hugging Face 模型仓库 ID
        local_dir: 本地保存路径，默认为 ./origin_models/{repo_id}
        resume_download: 是否支持断点续传
        force_download: 是否强制重新下载
        
    返回:
        str: 模型保存的本地路径
        
    异常:
        RuntimeError: 下载失败时抛出
    """
    if local_dir is None:
        local_dir = f"./origin_models/{repo_id.replace('/', '-')}"
    
    local_dir = Path(local_dir)
    
    # 检查模型是否已存在
    if local_dir.exists() and not force_download:
        required_files = ["config.json", "pytorch_model.bin", "tokenizer_config.json"]
        if all((local_dir / f).exists() for f in required_files):
            print(f"✓ 模型已存在于 {local_dir}")
            return str(local_dir)
    
    try:
        print(f"开始下载模型: {repo_id}")
        print(f"保存路径: {local_dir}")
        
        # 创建目录
        local_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载模型
        model_path = snapshot_download(
            repo_id=repo_id,
            local_dir=str(local_dir),
            resume_download=resume_download,
            force_download=force_download
        )
        
        print(f"✓ 模型下载完成: {model_path}")
        return model_path
        
    except Exception as e:
        raise RuntimeError(f"模型下载失败: {str(e)}")


def check_model_exists(repo_id: str, local_dir: Optional[str] = None) -> bool:
    """
    检查本地是否存在完整的模型文件
    
    参数:
        repo_id: Hugging Face 模型仓库 ID
        local_dir: 本地模型路径
        
    返回:
        bool: 模型是否存在且完整
    """
    if local_dir is None:
        local_dir = f"./origin_models/{repo_id.replace('/', '-')}"
    
    local_dir = Path(local_dir)
    
    if not local_dir.exists():
        return False
    
    required_files = ["config.json", "pytorch_model.bin", "tokenizer_config.json"]
    return all((local_dir / f).exists() for f in required_files)


def get_model_info(repo_id: str) -> dict:
    """
    获取模型信息
    
    参数:
        repo_id: Hugging Face 模型仓库 ID
        
    返回:
        dict: 模型信息
    """
    try:
        api = HfApi()
        model_info = api.model_info(repo_id)
        return {
            "model_id": model_info.modelId,
            "downloads": model_info.downloads,
            "likes": model_info.likes,
            "created_at": str(model_info.created_at),
            "tags": model_info.tags
        }
    except Exception as e:
        print(f"获取模型信息失败: {e}")
        return {}


if __name__ == "__main__":
    # 示例用法
    try:
        model_path = download_pretrained_model()
        print(f"模型下载成功: {model_path}")
        
        model_info = get_model_info("uer/t5-base-chinese-cluecorpussmall")
        print(f"模型信息: {model_info}")
        
    except Exception as e:
        print(f"错误: {e}")