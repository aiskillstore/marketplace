#!/bin/bash
# 读取邮件内容脚本（改进版）

set -e
set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 允许测试/调试时替换 curl 实现（例如使用 mock curl）
CURL_BIN="${CURL_BIN:-curl}"

# 使用说明
usage() {
    cat << EOF
使用方法: $0 [选项] EMAIL_ID

选项:
  -a ACCOUNT    账户名称（默认：SUSTech）
  -m MAILBOX    邮箱文件夹（默认：INBOX）
  -f FORMAT     输出格式（默认：summary，可选：summary, full, headers, body）
  -h            显示此帮助信息

参数:
  EMAIL_ID      邮件 ID（必需）

输出格式说明:
  summary   - 显示邮件摘要（发件人、主题、日期和正文预览）
  full      - 显示完整邮件（头部 + 正文）
  headers   - 仅显示邮件头部
  body      - 仅显示邮件正文

示例:
  $0 1                    # 显示第 1 封邮件的摘要
  $0 -f full 1            # 显示第 1 封邮件的完整内容
  $0 -f headers 5         # 仅显示第 5 封邮件的头部
  $0 -a SUSTech -m Sent 3 # 读取已发送文件夹中的第 3 封邮件
EOF
    exit 1
}

# MIME 解码函数（从标准输入读取）
decode_mime_header() {
    # RFC 2047 encoded-word 解码（支持任意 charset + B/Q，避免双重编码导致乱码）
    perl -MEncode -MMIME::Base64 -CS -pe '
        BEGIN {
            binmode(STDIN, ":raw");
            binmode(STDOUT, ":utf8");
        }

        s{=\?([^?]+)\?([BbQq])\?([^?]+)\?=}{
            my ($charset, $encoding, $encoded) = (lc($1), uc($2), $3);
            my $decoded;

            if ($encoding eq "B") {
                $decoded = decode_base64($encoded);
            } else {
                $encoded =~ s/_/ /g;
                $encoded =~ s/=([0-9A-Fa-f]{2})/chr(hex($1))/eg;
                $decoded = $encoded;
            }

            my $out;
            eval { $out = Encode::decode($charset, $decoded); 1 } or $out = $decoded;
            $out;
        }egi;
    ' 2>/dev/null
}

# 从 IMAP server stream 中提取 FETCH literal（基于 {N}\\r?\\n 后的 N 字节）
# 注意：某些 IMAP 服务器在 curl 非 verbose 模式下不会输出 literal；此函数配合 imap_server_stream() 使用。
extract_imap_literal() {
    perl -0777 -ne '
        binmode(STDIN);
        binmode(STDOUT);
        my $data = $_;

        my @literals;
        while ($data =~ /\{(\d+)\+?\}(?:\r\n|\n|\r)/sg) {
            my $len = $1;
            my $start = pos($data);
            my $chunk = substr($data, $start, $len);

            # 正常情况下 $chunk 长度应等于 $len；若不足则回退为剩余内容并做尾部清理
            if (length($chunk) < $len) {
                $chunk = substr($data, $start);
                $chunk =~ s/\r?\n\)\r?\n[A-Za-z0-9]+ (?:OK|NO|BAD).*?\r?\n?\z//s;
                $chunk =~ s/\r?\n[A-Za-z0-9]+ (?:OK|NO|BAD).*?\r?\n?\z//s;
            }

            push @literals, $chunk;
            pos($data) = $start + $len;
        }

        if (@literals) {
            print $literals[-1];
        } else {
            print $data;
        }
    ' 2>/dev/null
}

# 发送 IMAP 请求并输出 server stream（从 curl --verbose stderr 中提取以 "< " 开头的服务器响应行）
imap_server_stream() {
    local request="$1"

    local log_file
    log_file="$(mktemp)"

    set +e
    "$CURL_BIN" --url "imaps://${IMAP_HOST}:${IMAP_PORT}/${MAILBOX}" \
        --user "${IMAP_LOGIN}:${IMAP_PASSWORD}" \
        --request "$request" \
        --verbose \
        --output /dev/null \
        --silent \
        --show-error 2>"$log_file" >/dev/null
    local curl_exit_code=$?
    set -e

    if [ $curl_exit_code -ne 0 ]; then
        echo "✗ IMAP 请求失败（curl 退出码: $curl_exit_code）" >&2
        # 仅输出 IMAP 状态行，避免把 literal（邮件内容）打印到 stderr
        perl -ne '
            next unless s/^< //;
            next unless /^\* / || /^[A-Za-z0-9]+ (?:OK|NO|BAD|BYE)/;
            print;
        ' "$log_file" | tail -20 >&2 || true
        rm -f "$log_file"
        return $curl_exit_code
    fi

    # 输出服务器响应（去掉 "< " 前缀），供后续提取 literal
    perl -ne 'next unless s/^< //; print' "$log_file"
    rm -f "$log_file"
}

# 从 .eml 中提取头部（到第一个空行之前）
extract_eml_headers() {
    local eml_file="$1"
    perl -0777 -ne '
        binmode(STDIN, ":raw");
        binmode(STDOUT, ":raw");
        my $data = $_;
        if ($data =~ /\A(.*?)\r?\n\r?\n/s) {
            print $1;
        } else {
            print $data;
        }
    ' "$eml_file" 2>/dev/null
}

# 从 .eml 提取“可读正文文本”（优先 text/plain，回退 text/html，再回退 raw body）
extract_body_text() {
    local eml_file="$1"
    perl -MMIME::Parser -MHTML::Entities -MEncode -MFile::Temp -CS -e '
        use strict;
        use warnings;
        use utf8;

        binmode(STDOUT, ":utf8");

        my $file = shift @ARGV;
        exit 1 if !defined($file) || $file eq "";

        sub normalize_newlines {
            my ($s) = @_;
            $s //= "";
            $s =~ s/\r\n/\n/g;
            $s =~ s/\r/\n/g;
            return $s;
        }

        sub read_raw_body_fallback {
            my ($path) = @_;
            open my $fh, "<:raw", $path or return "";
            local $/;
            my $raw = <$fh>;
            close $fh;
            $raw = normalize_newlines($raw);
            $raw =~ s/\A.*?\n\n//s;
            return $raw;
        }

        sub read_entity_body_bytes {
            my ($ent) = @_;
            my $bh = $ent->bodyhandle or return "";
            my $io = $bh->open("r") or return "";
            local $/;
            my $bytes = <$io>;
            $io->close;
            return $bytes // "";
        }

        sub decode_charset {
            my ($bytes, $charset) = @_;
            $bytes //= "";
            $charset //= "";
            $charset =~ s/^\"|\"$//g;
            $charset = lc($charset);
            $charset = "utf-8" if $charset eq "" || $charset eq "us-ascii";

            my $text;
            eval { $text = Encode::decode($charset, $bytes); 1 } or $text = $bytes;
            return $text;
        }

        sub html_to_text {
            my ($html) = @_;
            $html = normalize_newlines($html);
            $html =~ s/<(script|style)[^>]*>.*?<\/\1>//sig;
            $html =~ s/<br\s*\/?>/\n/ig;
            $html =~ s/<\/p\s*>/\n\n/ig;
            $html =~ s/<[^>]+>//g;
            $html = HTML::Entities::decode_entities($html);
            $html =~ s/\r//g;
            $html =~ s/[ \t]+/ /g;
            $html =~ s/\n{3,}/\n\n/g;
            $html =~ s/^\s+|\s+$//g;
            return $html;
        }

        sub collect_text_parts {
            my ($ent, $want) = @_;
            my @parts = $ent->parts;
            if (!@parts) {
                my $type = lc($ent->head->mime_type || "");
                return () if $type ne $want;

                my $bytes = read_entity_body_bytes($ent);
                my $charset = $ent->head->mime_attr("content-type.charset");
                my $text = decode_charset($bytes, $charset);
                $text = normalize_newlines($text);
                $text =~ s/^\s+|\s+$//g;
                return $text ne "" ? ($text) : ();
            }

            my @out;
            for my $p (@parts) {
                push @out, collect_text_parts($p, $want);
            }
            return @out;
        }

        my $tmpdir = File::Temp::tempdir(CLEANUP => 1);
        my $parser = MIME::Parser->new;
        $parser->output_dir($tmpdir);
        $parser->decode_bodies(1);
        $parser->ignore_errors(1);

        my $entity = eval { $parser->parse_open($file) };
        if (!$entity) {
            print read_raw_body_fallback($file);
            exit 0;
        }

        my @plain = collect_text_parts($entity, "text/plain");
        my $text = $plain[0] // "";

        if ($text eq "") {
            my @html = collect_text_parts($entity, "text/html");
            if (defined($html[0]) && $html[0] ne "") {
                $text = html_to_text($html[0]);
            }
        }

        $text = read_raw_body_fallback($file) if $text eq "";
        print $text;
    ' "$eml_file" 2>/dev/null
}

# 提取邮件头部字段
get_header_field() {
    local header_content="$1"
    local field_name="$2"

    # 提取指定字段（支持 folded headers），并展开为单行
    printf '%s' "$header_content" | perl -0777 -s -ne '
        my $field = $field // "";
        exit 0 if $field eq "";
        s/\r\n/\n/g;
        if (m/^\Q$field\E:\s*(.*(?:\n[ \t].*)*)/im) {
            my $v = $1;
            $v =~ s/\n[ \t]+/ /g;
            $v =~ s/^\s+|\s+$//g;
            print $v;
        }
    ' -- -field="$field_name" | decode_mime_header
}

# 解析参数
ACCOUNT="SUSTech"
MAILBOX="INBOX"
FORMAT="summary"

while getopts "a:m:f:h" opt; do
    case $opt in
        a) ACCOUNT="$OPTARG" ;;
        m) MAILBOX="$OPTARG" ;;
        f) FORMAT="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

shift $((OPTIND - 1))

# 检查必需参数
if [ -z "${1:-}" ]; then
    echo "错误：缺少邮件 ID" >&2
    usage
fi

EMAIL_ID="$1"

# 验证格式参数
if [[ ! "$FORMAT" =~ ^(summary|full|headers|body)$ ]]; then
    echo "错误：无效的格式 '$FORMAT'" >&2
    usage
fi

# 读取配置（允许在测试时通过环境变量预先提供）
if [ -z "${IMAP_HOST:-}" ] || [ -z "${IMAP_PORT:-}" ] || [ -z "${IMAP_LOGIN:-}" ] || [ -z "${IMAP_PASSWORD:-}" ]; then
    get_imap_config "$ACCOUNT" > /dev/null || exit 1
fi

EML_FILE="$(mktemp)"
BODY_FILE="$(mktemp)"
cleanup() {
    rm -f "$EML_FILE" "$BODY_FILE"
}
trap cleanup EXIT

# 一次性获取 RFC822（含头部+正文），避免 curl 非 verbose 模式下拿不到 literal 的问题
imap_server_stream "FETCH ${EMAIL_ID} (BODY.PEEK[])" | extract_imap_literal >"$EML_FILE"

if [ ! -s "$EML_FILE" ]; then
    echo "✗ 未获取到邮件内容（可能是邮件 ID 无效或服务器未返回 literal）" >&2
    exit 1
fi

HEADERS_CONTENT=""
FROM=""
TO=""
CC=""
SUBJECT=""
DATE=""

if [ "$FORMAT" != "body" ]; then
    HEADERS_CONTENT="$(extract_eml_headers "$EML_FILE")"
    FROM="$(get_header_field "$HEADERS_CONTENT" "From")"
    TO="$(get_header_field "$HEADERS_CONTENT" "To")"
    CC="$(get_header_field "$HEADERS_CONTENT" "Cc")"
    SUBJECT="$(get_header_field "$HEADERS_CONTENT" "Subject")"
    DATE="$(get_header_field "$HEADERS_CONTENT" "Date")"
fi

if [ "$FORMAT" != "headers" ]; then
    extract_body_text "$EML_FILE" >"$BODY_FILE"
fi

# 根据格式输出
case "$FORMAT" in
    summary)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📧 邮件 #${EMAIL_ID}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📤 发件人: $FROM"
        echo "📅 日期:   $DATE"
        echo "📌 主题:   $SUBJECT"

        if [ -n "$CC" ]; then
            echo "📋 抄送:   $CC"
        fi

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📝 正文预览："
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        PREVIEW="$(head -30 "$BODY_FILE" 2>/dev/null || true)"
        printf '%s\n' "$PREVIEW"

        LINE_COUNT="$(printf '%s\n' "$PREVIEW" | wc -l | tr -d ' ')"
        if [ "$LINE_COUNT" -ge 30 ]; then
            echo ""
            echo "... (使用 -f full 查看完整内容)"
        fi

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ;;

    headers)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📧 邮件头部 #${EMAIL_ID}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "From:    $FROM"
        echo "To:      $TO"
        [ -n "$CC" ] && echo "Cc:      $CC"
        echo "Subject: $SUBJECT"
        echo "Date:    $DATE"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ;;

    body)
        cat "$BODY_FILE"
        ;;

    full)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📧 完整邮件 #${EMAIL_ID}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "From:    $FROM"
        echo "To:      $TO"
        [ -n "$CC" ] && echo "Cc:      $CC"
        echo "Subject: $SUBJECT"
        echo "Date:    $DATE"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📝 正文内容："
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        cat "$BODY_FILE"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ;;
esac
