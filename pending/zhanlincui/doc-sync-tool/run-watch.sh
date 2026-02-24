#!/bin/bash

# 文档同步工具 - 监听服务脚本
# 用法: ./run-watch.sh [目录路径]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$(pwd)}"

echo "🚀 启动文档监听服务..."
echo "📂 目标目录: $TARGET_DIR"
echo "💡 按 Ctrl+C 停止服务"
echo ""

cd "$TARGET_DIR" && node "$SCRIPT_DIR/watch.js"
