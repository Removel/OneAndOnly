# ONNX Runtime 推理优化使用指南

本指南介绍如何使用ONNX Runtime对风格化文本模型进行推理优化。

## 概述

ONNX Runtime是一个高性能的推理引擎，可以显著提升模型推理速度并降低内存占用。本项目已集成ONNX Runtime支持，并提供以下功能：

- 模型转换：将PyTorch模型转换为ONNX格式
- 模型量化：进一步优化模型大小和推理速度
- 性能对比：对比PyTorch和ONNX Runtime的性能差异
- 自动回退：ONNX模型不可用时自动回退到PyTorch

## 安装依赖

首先确保安装了必要的依赖：

```bash
pip install onnxruntime onnx optimum accelerate
```

或更新requirements.txt后运行：

```bash
pip install -r requirements.txt
```

## 使用步骤

### 1. 转换模型为ONNX格式

使用`convert_to_onnx.py`脚本将PyTorch模型转换为ONNX格式：

```bash
python custom_model/styler/convert_to_onnx.py \
    --model_path ./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6 \
    --output_path ./custom_model/styler/styled_models/my_t5_style_model/onnx \
    --verify
```

参数说明：
- `--model_path`: 原始PyTorch模型路径
- `--output_path`: ONNX模型输出路径
- `--verify`: 转换后验证模型（可选）

### 2. （可选）量化模型

如果需要进一步优化性能，可以对ONNX模型进行量化：

```bash
python custom_model/styler/quantize_model.py \
    --model_path ./custom_model/styler/styled_models/my_t5_style_model/onnx \
    --output_path ./custom_model/styler/styled_models/my_t5_style_model/onnx_quantized \
    --mode dynamic \
    --verify
```

参数说明：
- `--model_path`: ONNX模型路径
- `--output_path`: 量化模型输出路径
- `--mode`: 量化模式（dynamic/static）
- `--per_channel`: 使用per-channel量化（可选）
- `--reduce_range`: 减少量化范围（可选）
- `--verify`: 量化后验证模型（可选）

### 3. 使用ONNX模型进行推理

在代码中使用ONNX模型进行推理：

```python
from custom_model.styler.service import stylize

# 使用ONNX模型
result = stylize(
    raw_text="你好，今天天气很好。",
    model_path="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
    use_onnx=True,  # 启用ONNX Runtime
    use_quantization=False,  # 是否使用量化
    quantization_mode="dynamic"  # 量化模式
)

# 使用PyTorch模型（回退）
result = stylize(
    raw_text="你好，今天天气很好。",
    model_path="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
    use_onnx=False  # 使用PyTorch
)
```

### 4. 性能对比测试

使用`benchmark.py`脚本对比PyTorch和ONNX Runtime的性能：

```bash
python custom_model/styler/benchmark.py \
    --pytorch_model_path ./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6 \
    --onnx_model_path ./custom_model/styler/styled_models/my_t5_style_model/onnx \
    --max_new_tokens 512 \
    --num_tests 5
```

参数说明：
- `--pytorch_model_path`: PyTorch模型路径
- `--onnx_model_path`: ONNX模型路径
- `--max_new_tokens`: 最大生成token数
- `--num_tests`: 测试次数

## 配置选项

### ModelManager参数

- `model_path`: 模型路径
- `use_onnx`: 是否使用ONNX Runtime（默认：True）
- `use_quantization`: 是否使用量化（默认：False）
- `quantization_mode`: 量化模式（默认："dynamic"）

### stylize函数参数

- `raw_text`: 输入文本
- `model_path`: 模型路径
- `max_new_tokens`: 最大生成token数
- `do_sample`: 是否使用采样生成
- `num_beams`: beam search数量
- `temperature`: 采样温度
- `top_p`: nucleus sampling的p值
- `use_onnx`: 是否使用ONNX Runtime
- `use_quantization`: 是否使用量化
- `quantization_mode`: 量化模式

## 性能优化建议

### 1. 使用ONNX Runtime

ONNX Runtime通常比PyTorch快2-3倍，特别是在CPU上。

### 2. 使用量化

量化可以进一步减少模型大小和提升推理速度：
- 动态量化：简单快速，通常能获得1.5-2x的速度提升
- 静态量化：需要校准数据集，但性能更好

### 3. 批处理

对于批量处理，使用`batch_stylize`函数：

```python
from custom_model.styler.service import batch_stylize

texts = ["文本1", "文本2", "文本3"]
results = batch_stylize(
    texts=texts,
    model_path="./custom_model/styler/styled_models/my_t5_style_model/checkpoint-6",
    use_onnx=True
)
```

### 4. GPU加速

如果有GPU，ONNX Runtime会自动使用CUDAExecutionProvider：

```python
# 自动检测并使用GPU
result = stylize(
    raw_text="你好，今天天气很好。",
    use_onnx=True
)
```

## 故障排除

### ONNX模型加载失败

如果ONNX模型加载失败，系统会自动回退到PyTorch模型。检查日志中的错误信息：

```
WARNING: ONNX模型不存在: ...
INFO: 将回退到PyTorch模型
```

### 量化模型性能下降

如果量化后性能下降，尝试：
- 使用动态量化而不是静态量化
- 调整`per_channel`和`reduce_range`参数
- 检查量化后的模型验证输出

### 内存不足

如果遇到内存不足问题：
- 减小`max_new_tokens`参数
- 使用量化模型
- 使用较小的批处理大小

## 文件结构

```
custom_model/styler/
├── service.py              # 主服务模块（已更新支持ONNX）
├── convert_to_onnx.py      # 模型转换脚本
├── quantize_model.py       # 模型量化脚本
├── benchmark.py            # 性能对比脚本
└── styled_models/
    └── my_t5_style_model/
        ├── checkpoint-6/   # PyTorch模型
        └── onnx/           # ONNX模型（转换后生成）
```

## 性能预期

基于T5-base模型的典型性能提升：

| 配置 | 推理速度 | 内存占用 | 模型大小 |
|------|---------|---------|---------|
| PyTorch | 1.0x | 100% | 100% |
| ONNX Runtime | 2.5x | 80% | 100% |
| ONNX + 动态量化 | 3.5x | 60% | 50% |
| ONNX + 静态量化 | 4.0x | 50% | 50% |

*实际性能取决于硬件和具体使用场景*

## 技术支持

如遇问题，请检查：
1. 依赖版本是否正确
2. 模型文件是否完整
3. 日志中的详细错误信息
4. 硬件资源是否充足

## 更新日志

- 添加ONNX Runtime支持
- 添加模型转换功能
- 添加模型量化功能
- 添加性能对比测试
- 添加自动回退机制
- 添加性能监控日志