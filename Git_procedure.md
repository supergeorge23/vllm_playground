# Step 1：云端环境一次性 setup

# Ubuntu 22.04
sudo apt update
sudo apt install -y python3-venv git

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip

# vLLM（推荐最新）
pip install vllm

# 登录 HF 获取 LLaMA-3 权重（需许可）
pip install huggingface_hub
huggingface-cli login





