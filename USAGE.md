# Usage Guide

## 本地开发（macOS）

### 1. 安装依赖（仅用于脚本开发，不需要GPU）

```bash
# 创建虚拟环境（可选）
python3 -m venv .venv
source .venv/bin/activate

# 安装基础依赖（不包括vLLM，因为macOS不支持）
pip install pyyaml
```

### 2. 测试脚本功能

```bash
# 运行本地测试（测试 generate_rag_prompts.py）
python scripts/test_generate_prompts.py
```

测试会验证：
- 文件格式（JSONL）
- 必需字段完整性
- Prompt数量正确性
- Prompt结构格式
- 上下文长度近似值
- Sample ID正确性

### 3. 生成测试数据

```bash
# 生成RAG prompts（可以在本地运行）
python scripts/generate_rag_prompts.py \
    --context-lengths 2048 4096 8192 \
    --num-samples 5 \
    --output data/rag_prompts.jsonl
```

## Lambda Lab 云端运行

### 1. 同步项目到云端

```bash
# 从本地同步到Lambda Lab实例
rsync -av --exclude .venv --exclude results --exclude data/*.jsonl \
    ./ user@<lambda-host>:/path/to/project/
```

### 2. 云端环境设置（一次性）

参考 `CLOUD_SETUP.md` 或 `Git_procedure.md` 进行环境配置。

### 3. 运行完整Workflow

```bash
# SSH到Lambda Lab实例
ssh user@<lambda-host>

# 进入项目目录
cd /path/to/project

# 激活虚拟环境
source .venv/bin/activate

# 运行完整workflow（Phase 1: Baseline）
python scripts/workflow.py --config configs/baseline.yaml --phase 1

# 或者分步运行：
# 1. 生成prompts
python scripts/generate_rag_prompts.py --output data/rag_prompts.jsonl

# 2. 运行基准测试
python scripts/run_baseline.py \
    --config configs/baseline.yaml \
    --prompts data/rag_prompts.jsonl \
    --output results/baseline_results.jsonl
```

### 4. 下载结果

```bash
# 从云端下载结果到本地
rsync -av user@<lambda-host>:/path/to/project/results/ ./results/
```

## 配置文件说明

编辑 `configs/baseline.yaml` 来调整实验参数：

- `context_lengths`: 要测试的RAG上下文长度（tokens）
- `num_samples`: 每个上下文长度的样本数
- `decode_length`: 解码输出长度
- `gpu_memory_utilization`: GPU内存使用率

## 结果格式

结果保存为JSONL格式，每行一个JSON对象，包含：

- `context_length`: 上下文长度
- `sample_id`: 样本ID
- `prompt_tokens`: 实际prompt token数
- `output_tokens`: 输出token数
- `ttft`: Time to First Token (秒)
- `total_latency`: 总延迟 (秒)
- `decode_throughput`: 解码吞吐量 (tokens/秒)
- `peak_gpu_memory_gb`: 峰值GPU内存 (GB)

