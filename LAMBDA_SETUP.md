# Lambda Labs 实例设置指南

## 实例信息
- **Type**: gpu_1x_a10 (A10 GPU)
- **Region**: us-east-1
- **IP Address**: 150.136.52.154
- **SSH Login**: ubuntu@150.136.52.154
- **SSH Key**: MacBookPro.pem

## ✅ 已完成的设置

1. ✓ SSH连接测试成功
2. ✓ 系统依赖安装（python3-venv, git）
3. ✓ 项目代码同步完成
4. ✓ 虚拟环境创建完成
5. ✓ Python依赖安装完成（vLLM, pyyaml, huggingface_hub）
6. ✓ GPU设备检测到（A10）

## ⚠️ 待解决的问题

### NVIDIA驱动未完全加载

GPU设备已检测到，但NVIDIA驱动可能需要：
1. **等待实例完全初始化**（通常需要几分钟）
2. **重启实例**（在Lambda Labs控制台）
3. **手动安装驱动**（如果需要）

### 检查驱动状态

```bash
# SSH到实例
ssh -i ~/.ssh/MacBookPro.pem ubuntu@150.136.52.154

# 检查GPU
nvidia-smi

# 如果nvidia-smi不可用，检查驱动
dpkg -l | grep nvidia
lsmod | grep nvidia
```

### 如果驱动未安装

```bash
# 在实例上运行
sudo apt update
sudo apt install -y nvidia-driver-535 nvidia-utils-535
sudo reboot  # 重启后驱动才会生效
```

## 快速连接

```bash
# 使用快速连接脚本
./quick_connect.sh ubuntu 150.136.52.154

# 或手动连接
ssh -i ~/.ssh/MacBookPro.pem ubuntu@150.136.52.154
```

## 下一步操作

### 1. 验证GPU驱动（重要）

```bash
# SSH到实例后
nvidia-smi
```

如果显示GPU信息，说明驱动正常。如果报错，需要安装或重启。

### 2. 登录Hugging Face

```bash
cd ~/projects/vllm_playground
source .venv/bin/activate
huggingface-cli login
# 输入你的HF token（从 https://huggingface.co/settings/tokens 获取）
```

### 3. 运行第一个测试

```bash
# 生成小规模测试数据
python scripts/generate_rag_prompts.py \
    --context-lengths 2048 4096 \
    --num-samples 2 \
    --output data/test_prompts.jsonl

# 验证生成的文件
head -1 data/test_prompts.jsonl | python -m json.tool
```

### 4. 运行完整基准测试（需要GPU驱动正常）

```bash
# 确保GPU驱动正常后
python scripts/workflow.py --phase 1 --config configs/baseline.yaml
```

## 项目目录结构

在实例上的项目位置：
```
~/projects/vllm_playground/
├── scripts/
├── configs/
├── data/
├── results/
└── .venv/
```

## 同步本地代码到云端

如果本地有更新，可以使用rsync：

```bash
# 在本地项目目录
rsync -av --exclude .venv --exclude __pycache__ --exclude logs --exclude results --exclude .git \
    -e "ssh -i ~/.ssh/MacBookPro.pem" \
    ./ ubuntu@150.136.52.154:~/projects/vllm_playground/
```

## 下载结果到本地

```bash
# 从云端下载结果
rsync -av -e "ssh -i ~/.ssh/MacBookPro.pem" \
    ubuntu@150.136.52.154:~/projects/vllm_playground/results/ ./results/

# 下载日志
rsync -av -e "ssh -i ~/.ssh/MacBookPro.pem" \
    ubuntu@150.136.52.154:~/projects/vllm_playground/logs/ ./logs/
```

## 常见问题

### nvidia-smi命令未找到
- 等待实例完全初始化（5-10分钟）
- 或重启实例
- 或手动安装驱动（见上方）

### CUDA不可用
- 确保GPU驱动已安装并加载
- 检查 `nvidia-smi` 输出
- 重启实例后重试

### Hugging Face登录失败
- 确保有LLaMA-3的访问权限
- Token可以从 https://huggingface.co/settings/tokens 获取
- 使用 `huggingface-cli login` 登录

### vLLM导入失败
- 确保虚拟环境已激活：`source .venv/bin/activate`
- 检查vLLM安装：`pip list | grep vllm`
- 确保GPU驱动正常

## 联系信息

如果遇到问题，可以：
1. 检查Lambda Labs控制台的实例日志
2. 查看项目日志：`~/projects/vllm_playground/logs/`
3. 检查系统日志：`journalctl -u nvidia-persistenced`
