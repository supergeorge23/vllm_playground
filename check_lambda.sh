#!/bin/bash
# Lambda Labs 连接检查脚本

echo "=== Lambda Labs 实例连接检查 ==="
echo ""

# 检查SSH key文件
KEY_PATHS=(
    "$HOME/.ssh/MacBookPro.pem"
    "$HOME/MacBookPro.pem"
    "$HOME/Downloads/MacBookPro.pem"
)

KEY_FILE=""
for path in "${KEY_PATHS[@]}"; do
    if [ -f "$path" ]; then
        KEY_FILE="$path"
        echo "✓ 找到SSH key: $KEY_FILE"
        break
    fi
done

if [ -z "$KEY_FILE" ]; then
    echo "✗ 未找到SSH key文件 MacBookPro.pem"
    echo "  请确认文件位置，或手动指定路径"
    exit 1
fi

# 检查权限
if [ "$(stat -f "%OLp" "$KEY_FILE" 2>/dev/null || stat -c "%a" "$KEY_FILE" 2>/dev/null)" != "400" ]; then
    echo "⚠ 设置SSH key权限为400..."
    chmod 400 "$KEY_FILE"
    echo "✓ 权限已设置"
fi

echo ""
echo "=== 下一步 ==="
echo "1. 在Lambda Labs控制台等待实例状态变为 'Running'"
echo "2. 获取IP地址和SSH用户名（通常是 'ubuntu'）"
echo "3. 使用以下命令连接："
echo ""
echo "   ssh -i $KEY_FILE <USERNAME>@<IP_ADDRESS>"
echo ""
echo "   例如："
echo "   ssh -i $KEY_FILE ubuntu@123.45.67.89"
echo ""
