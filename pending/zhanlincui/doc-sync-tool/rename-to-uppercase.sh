#!/bin/bash

# 重命名所有已生成的文件为大写
# Agents.md -> AGENTS.md
# Gemini.md -> GEMINI.md

echo "🔄 开始重命名文件..."
echo ""

count=0

# 重命名 Agents.md
while IFS= read -r -d '' file; do
  dir=$(dirname "$file")
  mv "$file" "$dir/AGENTS.md"
  echo "✓ $file -> $dir/AGENTS.md"
  ((count++))
done < <(find . -type f -name "Agents.md" -print0 2>/dev/null)

# 重命名 Gemini.md
while IFS= read -r -d '' file; do
  dir=$(dirname "$file")
  mv "$file" "$dir/GEMINI.md"
  echo "✓ $file -> $dir/GEMINI.md"
  ((count++))
done < <(find . -type f -name "Gemini.md" -print0 2>/dev/null)

echo ""
echo "✅ 完成！共重命名 $count 个文件"
