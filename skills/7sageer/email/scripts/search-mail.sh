#!/bin/bash
# 搜索体测相关邮件

cd "$(dirname "$0")"

echo "正在搜索体测相关邮件..."

for i in $(seq 600 855); do
  subject=$(./read-email.sh -a SUSTech -f headers $i 2>/dev/null | grep "^Subject:" || true)
  if echo "$subject" | grep -qiE "体测|体质|体能"; then
    echo "找到邮件 #$i: $subject"
    ./read-email.sh -a SUSTech $i
    echo ""
  fi
done
