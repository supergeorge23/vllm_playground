#!/bin/bash
# Lambda Labs 实例自动化设置脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Lambda Labs 实例设置脚本"
echo "=========================================="
echo ""

# 检查参数
if [ $# -lt 2 ]; then
    echo "用法: $0 <USERNAME> <IP_ADDRESS>"
    echo ""
    echo "例如:"
    echo "  $0 ubuntu 123.45.67.89"
    echo ""
    exit 1
fi

USERNAME=$1
IP_ADDRESS=$2
KEY_FILE="$HOME/.ssh/MacBookPro.pem"
PROJECT_DIR="~/projects/vllm_playground"

echo "配置信息:"
echo "  Username: $USERNAME"
echo "  IP Address: $IP_ADDRESS"
echo "  SSH Key: $KEY_FILE"
echo "  Project Dir: $PROJECT_DIR"
echo ""

# 检查SSH key
if [ ! -f "$KEY_FILE" ]; then
    echo "错误: 找不到SSH key文件 $KEY_FILE"
    exit 1
fi

# 测试SSH连接
echo "步骤 1: 测试SSH连接..."
if ssh -i "$KEY_FILE" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USERNAME@$IP_ADDRESS" "echo 'Connection successful'" 2>/dev/null; then
    echo "✓ SSH连接成功"
else
    echo "✗ SSH连接失败，请检查："
    echo "  - 实例状态是否为 'Running'"
    echo "  - IP地址是否正确"
    echo "  - 用户名是否正确（通常是 'ubuntu'）"
    exit 1
fi

echo ""
echo "步骤 2: 安装系统依赖..."
ssh -i "$KEY_FILE" "$USERNAME@$IP_ADDRESS" << 'ENDSSH'
    sudo apt update
    sudo apt install -y python3-venv git
    echo "✓ 系统依赖安装完成"
ENDSSH

echo ""
echo "步骤 3: 创建项目目录并克隆仓库..."
ssh -i "$KEY_FILE" "$USERNAME@$IP_ADDRESS" << 'ENDSSH'
    mkdir -p ~/projects
    cd ~/projects
    if [ -d "vllm_playground" ]; then
        echo "项目目录已存在，跳过克隆"
    else
        git clone git@github.com:supergeorge23/vllm_playground.git || {
            echo "Git clone失败，可能需要配置SSH key或使用HTTPS"
            exit 1
        }
    fi
    echo "✓ 项目目录准备完成"
ENDSSH

echo ""
echo "步骤 4: 创建虚拟环境..."
ssh -i "$KEY_FILE" "$USERNAME@$IP_ADDRESS" << 'ENDSSH'
    cd ~/projects/vllm_playground
    if [ -d ".venv" ]; then
        echo "虚拟环境已存在，跳过创建"
    else
        python3 -m venv .venv
        echo "✓ 虚拟环境创建完成"
    fi
ENDSSH

echo ""
echo "步骤 5: 安装Python依赖..."
echo "  这可能需要几分钟，请耐心等待..."
ssh -i "$KEY_FILE" "$USERNAME@$IP_ADDRESS" << 'ENDSSH'
    cd ~/projects/vllm_playground
    source .venv/bin/activate
    pip install -U pip
    pip install vllm pyyaml huggingface_hub
    echo "✓ Python依赖安装完成"
ENDSSH

echo ""
echo "步骤 6: 验证环境..."
ssh -i "$KEY_FILE" "$USERNAME@$IP_ADDRESS" << 'ENDSSH'
    echo "--- GPU信息 ---"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || echo "nvidia-smi未找到"
    
    echo ""
    echo "--- Python环境 ---"
    cd ~/projects/vllm_playground
    source .venv/bin/activate
    python --version
    python -c "import vllm; print('✓ vLLM导入成功')" || echo "✗ vLLM导入失败"
    python -c "import torch; print(f'✓ PyTorch CUDA可用: {torch.cuda.is_available()}')" || echo "✗ PyTorch检查失败"
ENDSSH

echo ""
echo "=========================================="
echo "设置完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. SSH到实例："
echo "   ssh -i $KEY_FILE $USERNAME@$IP_ADDRESS"
echo ""
echo "2. 登录Hugging Face："
echo "   cd ~/projects/vllm_playground"
echo "   source .venv/bin/activate"
echo "   huggingface-cli login"
echo ""
echo "3. 运行测试："
echo "   python scripts/generate_rag_prompts.py --num-samples 2"
echo ""
