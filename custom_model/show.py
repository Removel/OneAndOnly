import torch
if __name__ == "__main__":
    print(f"CUDA可用: {torch.cuda.is_available()}")
    print(f"GPU数量: {torch.cuda.device_count()}")
    if torch.cuda.is_available():
        print(f"当前GPU: {torch.cuda.current_device()}")
        print(f"GPU名称: {torch.cuda.get_device_name()}")
