#!/bin/bash

# 文档同步工具测试脚本
# 用于验证工具的各项功能

set -e  # 遇到错误立即退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="/tmp/doc-sync-test-$(date +%s)"

echo "🧪 开始测试文档同步工具..."
echo ""

# 创建测试目录
echo "📁 创建测试目录: $TEST_DIR"
mkdir -p "$TEST_DIR/project1"
mkdir -p "$TEST_DIR/project2/subdir"
mkdir -p "$TEST_DIR/project3"

# 测试 1: 单个文件创建
echo ""
echo "✅ 测试 1: 从单个文件创建其他文件"
echo "# Project 1 Config" > "$TEST_DIR/project1/claude.md"
echo "这是 claude.md 的内容" >> "$TEST_DIR/project1/claude.md"

cd "$TEST_DIR" && node "$SCRIPT_DIR/sync.js" > /dev/null

if [ -f "$TEST_DIR/project1/Agents.md" ] && [ -f "$TEST_DIR/project1/gemini.md" ]; then
    echo "   ✓ 成功创建 Agents.md 和 gemini.md"
else
    echo "   ✗ 失败: 文件未创建"
    exit 1
fi

# 验证内容一致
if diff -q "$TEST_DIR/project1/claude.md" "$TEST_DIR/project1/Agents.md" > /dev/null; then
    echo "   ✓ 文件内容一致"
else
    echo "   ✗ 失败: 文件内容不一致"
    exit 1
fi

# 测试 2: 嵌套目录
echo ""
echo "✅ 测试 2: 嵌套目录文件同步"
echo "# Subdir Config" > "$TEST_DIR/project2/subdir/gemini.md"

cd "$TEST_DIR" && node "$SCRIPT_DIR/sync.js" > /dev/null

if [ -f "$TEST_DIR/project2/subdir/Agents.md" ] && [ -f "$TEST_DIR/project2/subdir/claude.md" ]; then
    echo "   ✓ 嵌套目录同步成功"
else
    echo "   ✗ 失败: 嵌套目录同步失败"
    exit 1
fi

# 测试 3: 多个文件选择最新
echo ""
echo "✅ 测试 3: 多个文件时选择最新内容"
echo "# Old Content" > "$TEST_DIR/project3/Agents.md"
sleep 1  # 确保时间戳不同
echo "# New Content" > "$TEST_DIR/project3/claude.md"

cd "$TEST_DIR" && node "$SCRIPT_DIR/sync.js" > /dev/null

if grep -q "# New Content" "$TEST_DIR/project3/Agents.md"; then
    echo "   ✓ 成功选择最新文件内容"
else
    echo "   ✗ 失败: 未选择最新文件"
    exit 1
fi

# 测试 4: 内容相同时跳过
echo ""
echo "✅ 测试 4: 内容相同时跳过更新"
BEFORE_MTIME=$(stat -f "%m" "$TEST_DIR/project1/Agents.md")
cd "$TEST_DIR" && node "$SCRIPT_DIR/sync.js" > /dev/null
AFTER_MTIME=$(stat -f "%m" "$TEST_DIR/project1/Agents.md")

if [ "$BEFORE_MTIME" == "$AFTER_MTIME" ]; then
    echo "   ✓ 成功跳过相同内容"
else
    echo "   ✗ 失败: 不必要的文件更新"
    exit 1
fi

# 清理
echo ""
echo "🧹 清理测试目录..."
rm -rf "$TEST_DIR"

echo ""
echo "============================================================"
echo "🎉 所有测试通过！"
echo "============================================================"
echo ""
echo "📋 测试摘要:"
echo "   ✓ 单个文件创建"
echo "   ✓ 嵌套目录同步"
echo "   ✓ 最新文件选择"
echo "   ✓ 相同内容跳过"
echo ""
echo "✅ 文档同步工具运行正常，可以安全使用！"
