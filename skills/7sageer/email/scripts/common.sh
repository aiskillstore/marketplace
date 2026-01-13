#!/bin/bash
# 通用函数库：读取配置和密码

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../references/accounts.yaml"

# 从 Keychain 读取密码
get_password() {
    local account=$1
    local service=$2
    local login=$3

    local password=$(security find-generic-password \
        -a "$login" \
        -s "$service" \
        -w 2>/dev/null)

    if [ -z "$password" ]; then
        echo "错误：未找到 Keychain 中的密码" >&2
        echo "请先设置密码：" >&2
        echo "  security add-generic-password -a \"$login\" -s \"$service\" -w \"your-password\" -U" >&2
        return 1
    fi

    echo "$password"
}

# 解析 YAML 配置（简化版，只支持我们需要的字段）
get_config() {
    local account=${1:-SUSTech}
    local field=$2

    # 使用 grep 和 awk 简单解析 YAML
    # 排除注释行（以 # 开头的行）
    grep -A 20 "^  $account:" "$CONFIG_FILE" | grep "$field:" | grep -v "^[[:space:]]*#" | awk '{print $2}'
}

# 获取账户的 IMAP 配置
get_imap_config() {
    local account=${1:-SUSTech}
    local account_lower=$(echo "$account" | tr '[:upper:]' '[:lower:]')

    export IMAP_HOST=$(get_config "$account" "host" | head -1)
    export IMAP_PORT=$(get_config "$account" "port" | head -1)
    export IMAP_LOGIN=$(get_config "$account" "login" | head -1)
    export IMAP_EMAIL=$(get_config "$account" "email")

    IMAP_PASSWORD=$(get_password "$account" "email-imap-${account_lower}" "$IMAP_LOGIN")
    if [ $? -ne 0 ]; then
        return 1
    fi
    export IMAP_PASSWORD
}

# 获取账户的 SMTP 配置
get_smtp_config() {
    local account=${1:-SUSTech}
    local account_lower=$(echo "$account" | tr '[:upper:]' '[:lower:]')

    export SMTP_HOST=$(get_config "$account" "host" | tail -1)
    export SMTP_PORT=$(get_config "$account" "port" | tail -1)
    export SMTP_LOGIN=$(get_config "$account" "login" | tail -1)
    export SMTP_EMAIL=$(get_config "$account" "email")

    SMTP_PASSWORD=$(get_password "$account" "email-smtp-${account_lower}" "$SMTP_LOGIN")
    if [ $? -ne 0 ]; then
        return 1
    fi
    export SMTP_PASSWORD
}
