#!/bin/bash
# cleanup-duplicates.sh - 清理重复的中英文文档
# 用法: ./cleanup-duplicates.sh [--dry-run]
#
# 此脚本会:
# 1. 删除中文版本文档 (保留英文版作为主版本)
# 2. 删除冗余的 usage-guide (SKILL.md 已包含快速入门)

SKILL_DIR="$(dirname "$0")/.."
DRY_RUN=false

if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN 模式 - 仅显示将要删除的文件"
    echo ""
fi

echo "🧹 清理重复文档"
echo "==============="
echo ""

# 要删除的文件列表
FILES_TO_DELETE=(
    # 中文重复版本 (保留英文版)
    "$SKILL_DIR/references/guides/usage-guide-zh.md"
    "$SKILL_DIR/references/guides/design-zh.md"
    "$SKILL_DIR/references/guides/extending-zh.md"
    # 冗余的 usage-guide (SKILL.md 已包含核心内容)
    "$SKILL_DIR/references/guides/usage-guide.md"
)

total_lines=0
deleted_count=0

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file" | tr -d ' ')
        total_lines=$((total_lines + lines))
        deleted_count=$((deleted_count + 1))
        name=$(basename "$file")

        if [ "$DRY_RUN" = true ]; then
            echo "  [将删除] $name ($lines 行)"
        else
            rm "$file"
            echo "  ✅ 已删除 $name ($lines 行)"
        fi
    fi
done

echo ""
echo "----------------------------------------"
if [ "$DRY_RUN" = true ]; then
    echo "📊 将删除 $deleted_count 个文件, 共 $total_lines 行"
    echo ""
    echo "确认删除请运行: ./cleanup-duplicates.sh"
else
    echo "📊 已删除 $deleted_count 个文件, 共 $total_lines 行"
fi
