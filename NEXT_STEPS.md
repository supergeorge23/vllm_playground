# 后续步骤总结

## ✅ 已完成的工作

### 1. 项目基础设施
- ✅ 项目结构和workflow框架
- ✅ 统一的logger系统（带单元测试）
- ✅ 结果分析脚本
- ✅ 完整的文档和配置

### 2. Lambda Labs云端环境
- ✅ 实例创建和SSH连接配置
- ✅ 系统依赖安装（python3-venv, git）
- ✅ vLLM和Python依赖安装
- ✅ GPU驱动验证（A10正常工作）
- ✅ Hugging Face登录和LLaMA-3权限配置

### 3. 基准测试运行
- ✅ 配置文件优化（解决max_model_len和OOM问题）
- ✅ Phase 1基准测试成功运行
- ✅ 结果文件生成

## 📋 下次启动实例后的操作流程

### 步骤1: 启动新实例并连接

```bash
# 在Lambda Labs控制台启动新实例（A10或A100）
# 获取IP地址和SSH信息

# 快速连接
./quick_connect.sh ubuntu <NEW_IP_ADDRESS>
```

### 步骤2: 快速环境检查

```bash
# SSH到实例后
cd ~/projects/vllm_playground
source .venv/bin/activate

# 检查GPU
nvidia-smi

# 检查环境
python -c "import vllm; print('vLLM OK')"
```

### 步骤3: 运行实验

```bash
# 运行完整workflow
python scripts/workflow.py --phase 1 --config configs/baseline.yaml

# 或分步运行
# 1. 生成prompts
python scripts/generate_rag_prompts.py \
    --context-lengths 2048 4096 8192 \
    --num-samples 10 \
    --output data/rag_prompts.jsonl

# 2. 运行基准测试
python scripts/run_baseline.py \
    --config configs/baseline.yaml \
    --prompts data/rag_prompts.jsonl
```

### 步骤4: 下载结果

```bash
# 在本地机器上运行
cd /Users/supergeorge/Desktop/KernelBoard/Playground

# 下载结果文件
rsync -av -e "ssh -i ~/.ssh/MacBookPro.pem" \
    ubuntu@<IP_ADDRESS>:~/projects/vllm_playground/results/ ./results/

# 下载日志文件
rsync -av -e "ssh -i ~/.ssh/MacBookPro.pem" \
    ubuntu@<IP_ADDRESS>:~/projects/vllm_playground/logs/ ./logs/
```

### 步骤5: 分析结果（本地）

```bash
# 分析结果
python scripts/analyze_results.py results/baseline_results.jsonl

# 导出为CSV
python scripts/analyze_results.py results/baseline_results.jsonl \
    --output results/summary.csv
```

## 🔧 配置优化建议

### 内存优化（如果遇到OOM）

如果A10（24GB）仍然内存不足，可以进一步调整 `configs/baseline.yaml`：

```yaml
inference:
  gpu_memory_utilization: 0.8  # 进一步降低
  max_num_seqs: 16  # 或更低
```

### 测试不同配置

可以创建多个配置文件测试不同参数：

```bash
# 创建小规模测试配置
cp configs/baseline.yaml configs/baseline_small.yaml
# 修改 num_samples: 5, context_lengths: [2048, 4096]

# 创建大规模配置（如果使用A100）
cp configs/baseline.yaml configs/baseline_large.yaml
# 修改 max_model_len: 16384, context_lengths: [2048, 4096, 8192, 16384]
```

## 📊 实验计划

### Phase 1: Baseline（已完成）
- [x] 运行基准测试
- [x] 收集TTFT、吞吐量、延迟数据
- [ ] 分析结果并生成报告

### Phase 2: Prefill/Decode Profiling（下一步）
- [ ] 分离prefill和decode执行时间
- [ ] 分析KV cache分配
- [ ] 测量attention行为

### Phase 3: System Optimization（未来）
- [ ] Prefill-decode解耦实验
- [ ] Context KV cache复用
- [ ] 延迟-内存权衡分析

## 📁 重要文件位置

### 云端（实例上）
```
~/projects/vllm_playground/
├── results/          # 结果文件（JSONL）
├── logs/             # 日志文件
├── data/             # 输入数据（prompts）
└── configs/          # 配置文件
```

### 本地
```
/Users/supergeorge/Desktop/KernelBoard/Playground/
├── results/          # 下载的结果
├── logs/             # 下载的日志
├── scripts/          # 脚本（包括分析工具）
└── configs/          # 配置文件
```

## 🚀 快速命令参考

### 连接和检查
```bash
# 连接实例
./quick_connect.sh ubuntu <IP>

# 检查GPU
nvidia-smi

# 检查环境
cd ~/projects/vllm_playground && source .venv/bin/activate
```

### 运行实验
```bash
# 完整workflow
python scripts/workflow.py --phase 1

# 单独运行
python scripts/run_baseline.py --config configs/baseline.yaml --prompts data/rag_prompts.jsonl
```

### 下载和分析
```bash
# 下载结果
rsync -av -e "ssh -i ~/.ssh/MacBookPro.pem" \
    ubuntu@<IP>:~/projects/vllm_playground/results/ ./results/

# 分析结果
python scripts/analyze_results.py results/baseline_results.jsonl
```

## ⚠️ 注意事项

1. **实例成本**: Lambda Labs按小时计费，用完记得terminate
2. **结果备份**: 及时下载结果文件，避免丢失
3. **配置版本**: 修改配置后记得同步到云端
4. **日志查看**: 如果实验失败，查看 `logs/` 目录的详细日志

## 📝 待办事项

- [ ] 分析已收集的baseline结果
- [ ] 规划Phase 2的实验设计
- [ ] 考虑是否需要更大的GPU（A100）进行更长上下文测试
- [ ] 优化prompt生成策略（更真实的RAG场景）
- [ ] 添加更多性能指标收集

## 🔗 相关文档

- `LAMBDA_SETUP.md` - Lambda Labs设置指南
- `USAGE.md` - 详细使用说明
- `README.md` - 项目概述
- `FIX_HF_ACCESS.md` - Hugging Face访问问题解决
- `PR_GUIDE.md` - Pull Request创建指南
