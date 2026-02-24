#!/bin/bash

# 文档同步工具 - 手动同步脚本
# 用法: ./run-sync.sh [目录路径]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${1:-$(pwd)}"

echo "🚀 启动文档同步工具..."
echo "📂 目标目录: $TARGET_DIR"
echo ""

cd "$TARGET_DIR" && node "$SCRIPT_DIR/sync.js"
