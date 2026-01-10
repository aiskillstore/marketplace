#!/bin/bash
# 获取邮件列表脚本（改进版：支持MIME解码和友好输出）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 使用说明
usage() {
    cat << EOF
使用方法: $0 [选项]

选项:
  -a ACCOUNT    账户名称（默认：SUSTech）
  -m MAILBOX    邮箱文件夹（默认：INBOX）
  -n COUNT      获取邮件数量（默认：10）
  -h            显示此帮助信息

示例:
  $0                           # 获取收件箱最新 10 封邮件
  $0 -a SUSTech -n 20          # 获取最新 20 封邮件
  $0 -m "Sent"                 # 获取已发送邮件
EOF
    exit 1
}

# 解析参数
ACCOUNT="SUSTech"
MAILBOX="INBOX"
COUNT=10

while getopts "a:m:n:h" opt; do
    case $opt in
        a) ACCOUNT="$OPTARG" ;;
        m) MAILBOX="$OPTARG" ;;
        n) COUNT="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# 读取配置
get_imap_config "$ACCOUNT" || exit 1

# 获取邮件列表
echo "📬 正在获取邮件列表..."
echo "   账户: $IMAP_EMAIL"
echo "   文件夹: $MAILBOX"
echo ""

# 使用 IMAP FETCH 命令获取邮件头信息
# 使用 verbose 模式以获取完整的 IMAP 响应
# 临时禁用 set -e 以便捕获错误
set +e
response=$(curl --url "imaps://${IMAP_HOST}:${IMAP_PORT}/${MAILBOX}" \
    --user "${IMAP_LOGIN}:${IMAP_PASSWORD}" \
    --request "FETCH 1:${COUNT} (FLAGS BODY[HEADER.FIELDS (FROM SUBJECT DATE)])" \
    --verbose 2>&1)
curl_exit_code=$?
set -e

# 检查是否成功
if [ $curl_exit_code -ne 0 ]; then
    echo "✗ 邮件列表获取失败（curl 退出码: $curl_exit_code）" >&2
    echo "错误信息：" >&2
    echo "$response" | tail -20 >&2
    exit 1
fi

# 提取收件箱状态信息
# 临时禁用 set -e 以防止 grep 没有匹配时退出
set +e
total_emails=$(echo "$response" | grep -E "^< \* [0-9]+ EXISTS" | sed 's/^< \* \([0-9]*\) EXISTS/\1/' | tr -d '[:space:]')
unseen_emails=$(echo "$response" | grep -E "^< \* OK \[UNSEEN [0-9]+\]" | sed 's/^< \* OK \[UNSEEN \([0-9]*\)\]/\1/' | tr -d '[:space:]')
set -e

# 清理 COUNT 变量，确保它是纯数字
COUNT=$(echo "$COUNT" | tr -d '[:space:]')

if [ -n "$total_emails" ]; then
    echo "📊 收件箱状态："
    echo "   总邮件数: $total_emails 封"
    if [ -n "$unseen_emails" ]; then
        echo "   未读邮件: $unseen_emails 封"
    fi
    echo ""

    # 计算最新邮件的范围
    if [ "$total_emails" -gt "$COUNT" ] 2>/dev/null; then
        start_id=$((total_emails - COUNT + 1))
        end_id=$total_emails
        echo "📧 获取最新 $COUNT 封邮件 (#$start_id - #$end_id)..."
        echo ""

        # 重新获取最新的邮件
        response=$(curl --url "imaps://${IMAP_HOST}:${IMAP_PORT}/${MAILBOX}" \
            --user "${IMAP_LOGIN}:${IMAP_PASSWORD}" \
            --request "FETCH ${start_id}:${end_id} (FLAGS BODY[HEADER.FIELDS (FROM SUBJECT DATE)])" \
            --verbose 2>&1)
    else
        echo "📧 获取全部 $total_emails 封邮件..."
        echo ""
    fi
fi

# 解析并格式化输出
echo "$response" | perl -MMIME::Base64 -MMIME::QuotedPrint -MEncode -CS -e '
    use strict;
    use warnings;
    use utf8;

    # 设置输出编码为UTF-8
    binmode(STDOUT, ":utf8");
    binmode(STDERR, ":utf8");

    my $email_num = 0;
    my $in_headers = 0;
    my ($from, $subject, $date, $flags);
    my $current_field = "";

    while (<>) {
        # 只处理以 "< " 开头的行（curl verbose模式的服务器响应）
        # 跳过不带前缀的行，避免重复处理
        next unless /^< /;

        # 移除 curl verbose 输出的前缀
        s/^< //;
        # 规范化行尾（IMAP 通常使用 CRLF；去掉末尾的 \r 以便更稳定地搜索/匹配）
        s/\r$//;

        # 检测新邮件开始
        if (/^\* (\d+) FETCH/) {
            # 输出上一封邮件的信息
            if ($email_num > 0) {
                # 解码并输出上一封邮件
                if ($from) {
                    $from =~ s/\s+$//;
                    $from = decode_mime($from);
                }
                if ($subject) {
                    $subject =~ s/\s+$//;
                    $subject = decode_mime($subject);
                }
                print_email($email_num, $from, $subject, $date, $flags);
            }

            $email_num = $1;
            $in_headers = 1;
            $from = $subject = $date = $flags = "";
            $current_field = "";

            # 提取 FLAGS
            if (/FLAGS \(([^)]*)\)/) {
                $flags = $1;
            }
            next;
        }

        # 解析邮件头部字段
        if ($in_headers) {
            # 检查是否为续行（以空格或制表符开头）
            if (/^\s+(.+)/ && $current_field) {
                my $continuation = $1;
                $continuation =~ s/\s+$//;
                if ($current_field eq "from") {
                    $from .= " " if length($from);
                    $from .= $continuation;
                } elsif ($current_field eq "subject") {
                    $subject .= " " if length($subject);
                    $subject .= $continuation;
                }
                next;
            }

            # 新的字段行
            $current_field = "";

            if (/^Date:\s*(.+)/) {
                $date = $1;
                $date =~ s/\s+$//;
            }
            elsif (/^From:\s*(.+)/) {
                $from = $1;
                $from =~ s/\s+$//;
                $current_field = "from";
            }
            elsif (/^Subject:\s*(.+)/) {
                $subject = $1;
                $subject =~ s/\s+$//;
                $current_field = "subject";
            }
            elsif (/^\)$/) {
                $in_headers = 0;
                $current_field = "";
            }
        }
    }

    # 输出最后一封邮件
    if ($email_num > 0) {
        # 解码并输出最后一封邮件
        if ($from) {
            $from =~ s/\s+$//;
            $from = decode_mime($from);
        }
        if ($subject) {
            $subject =~ s/\s+$//;
            $subject = decode_mime($subject);
        }
        print_email($email_num, $from, $subject, $date, $flags);
    }

    # 解码 MIME encoded-words
    sub decode_mime {
        my $text = shift;
        $text =~ s{=\?([^?]+)\?([BQ])\?([^?]+)\?=}{
            my ($charset, $encoding, $encoded) = (lc($1), uc($2), $3);
            my $decoded;
            if ($encoding eq "B") {
                $decoded = decode_base64($encoded);
            } else {
                $encoded =~ s/_/ /g;
                $encoded =~ s/=([0-9A-F]{2})/chr(hex($1))/eg;
                $decoded = $encoded;
            }
            eval { Encode::decode($charset, $decoded) } || $decoded;
        }egi;
        return $text;
    }

    # 格式化输出邮件信息
    sub print_email {
        my ($num, $from, $subject, $date, $flags) = @_;

        # 判断是否已读
        my $status = ($flags =~ /\\Seen/) ? "✓" : "●";

        print "[$status] 邮件 #$num\n";
        print "    发件人: $from\n" if $from;
        print "    主题: $subject\n" if $subject;
        print "    日期: $date\n" if $date;
        print "\n";
    }
'

echo "✓ 邮件列表获取成功"
