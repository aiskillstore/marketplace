#!/bin/bash
# doc-stats.sh - 文档统计脚本
# 用法: ./doc-stats.sh

SKILL_DIR="$(dirname "$0")/.."
echo "📊 Picture Book Wizard 文档统计"
echo "================================"
echo ""

# 总体统计
total_files=$(find "$SKILL_DIR" -name "*.md" -type f | wc -l | tr -d ' ')
total_lines=$(find "$SKILL_DIR" -name "*.md" -type f | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

echo "📁 总文件数: $total_files"
echo "📝 总行数: $total_lines"
echo ""

# 按目录统计
echo "📂 按目录统计:"
echo "----------------------------------------"
printf "%-40s %8s %8s\n" "目录" "文件数" "行数"
echo "----------------------------------------"

for dir in "$SKILL_DIR" "$SKILL_DIR/references/config/core" "$SKILL_DIR/references/config/cclp" "$SKILL_DIR/references/config/animals" "$SKILL_DIR/references/config/advanced" "$SKILL_DIR/references/guides" "$SKILL_DIR/references/examples" "$SKILL_DIR/assets/templates"; do
    if [ -d "$dir" ]; then
        name=$(basename "$dir")
        if [ "$dir" = "$SKILL_DIR" ]; then
            name="(root)"
            files=$(find "$dir" -maxdepth 1 -name "*.md" -type f | wc -l | tr -d ' ')
            lines=$(find "$dir" -maxdepth 1 -name "*.md" -type f | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        else
            files=$(find "$dir" -name "*.md" -type f | wc -l | tr -d ' ')
            lines=$(find "$dir" -name "*.md" -type f | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        fi
        [ -z "$lines" ] && lines=0
        printf "%-40s %8s %8s\n" "$name" "$files" "$lines"
    fi
done

echo ""
echo "📈 最大的 10 个文件:"
echo "----------------------------------------"
find "$SKILL_DIR" -name "*.md" -type f | xargs wc -l 2>/dev/null | sort -rn | head -11 | tail -10 | while read lines file; do
    name=$(basename "$file")
    printf "%6d 行  %s\n" "$lines" "$name"
done

echo ""
echo "🔍 中英文重复文件检测:"
echo "----------------------------------------"
for file in "$SKILL_DIR"/references/guides/*.md; do
    name=$(basename "$file")
    if [[ "$name" == *"-zh.md" ]]; then
        en_name="${name/-zh.md/.md}"
        en_file="$SKILL_DIR/references/guides/$en_name"
        if [ -f "$en_file" ]; then
            zh_lines=$(wc -l < "$file" | tr -d ' ')
            en_lines=$(wc -l < "$en_file" | tr -d ' ')
            echo "⚠️  $en_name ($en_lines行) + $name ($zh_lines行) = $((en_lines + zh_lines))行"
        fi
    fi
done
