#!/bin/bash
# 快速连接Lambda Labs实例的脚本

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

ssh -i "$KEY_FILE" "$USERNAME@$IP_ADDRESS"
