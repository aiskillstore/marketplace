#!/bin/bash
# 发送邮件脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 使用说明
usage() {
    cat << EOF
使用方法: $0 [选项]

选项:
  -a ACCOUNT    账户名称（默认：SUSTech）
  -t TO         收件人邮箱地址（必需）
  -s SUBJECT    邮件主题（必需）
  -b BODY       邮件正文（必需）
  -f FILE       从文件读取邮件正文
  -c CC         抄送地址（可选）
  -h            显示此帮助信息

示例:
  $0 -t recipient@example.com -s "Test" -b "Hello World"
  $0 -a SUSTech -t recipient@example.com -s "Test" -f message.txt
EOF
    exit 1
}

# 解析参数
ACCOUNT="SUSTech"
TO=""
SUBJECT=""
BODY=""
BODY_FILE=""
CC=""

while getopts "a:t:s:b:f:c:h" opt; do
    case $opt in
        a) ACCOUNT="$OPTARG" ;;
        t) TO="$OPTARG" ;;
        s) SUBJECT="$OPTARG" ;;
        b) BODY="$OPTARG" ;;
        f) BODY_FILE="$OPTARG" ;;
        c) CC="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# 检查必需参数
if [ -z "$TO" ] || [ -z "$SUBJECT" ]; then
    echo "错误：缺少必需参数" >&2
    usage
fi

if [ -z "$BODY" ] && [ -z "$BODY_FILE" ]; then
    echo "错误：必须提供邮件正文（-b 或 -f）" >&2
    usage
fi

# 读取配置
echo "正在加载账户配置：$ACCOUNT"
get_smtp_config "$ACCOUNT" || exit 1

# 准备邮件内容
TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

cat > "$TEMP_FILE" << EOF
From: $SMTP_EMAIL
To: $TO
Subject: $SUBJECT
EOF

if [ -n "$CC" ]; then
    echo "Cc: $CC" >> "$TEMP_FILE"
fi

echo "" >> "$TEMP_FILE"

if [ -n "$BODY_FILE" ]; then
    cat "$BODY_FILE" >> "$TEMP_FILE"
else
    echo "$BODY" >> "$TEMP_FILE"
fi

# 发送邮件
echo "正在发送邮件..."
echo "  从: $SMTP_EMAIL"
echo "  到: $TO"
echo "  主题: $SUBJECT"

curl --url "smtps://${SMTP_HOST}:${SMTP_PORT}" \
    --ssl-reqd \
    --mail-from "$SMTP_EMAIL" \
    --mail-rcpt "$TO" \
    --user "${SMTP_LOGIN}:${SMTP_PASSWORD}" \
    --upload-file "$TEMP_FILE" \
    --silent \
    --show-error

if [ $? -eq 0 ]; then
    echo "✓ 邮件发送成功"
else
    echo "✗ 邮件发送失败" >&2
    exit 1
fi
