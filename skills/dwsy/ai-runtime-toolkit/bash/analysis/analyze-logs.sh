#!/bin/bash
# 日志分析器 - 从日志文件中提取和分析信息

set -e

LOG_FILE="${1:-}"
PATTERN="${2:-}"
LEVEL="${3:-INFO}"
DATE_RANGE="${4:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 帮助信息
usage() {
    echo "📝 日志分析器"
    echo ""
    echo "使用: $0 <日志文件> [模式] [级别] [日期范围]"
    echo ""
    echo "参数:"
    echo "  日志文件    日志文件路径 (必需)"
    echo "  模式        要搜索的正则表达式 (可选)"
    echo "  级别        日志级别: ERROR/WARN/INFO/DEBUG (默认: INFO)"
    echo "  日期范围    日期范围, 如: 2025-11-01~2025-11-14 (可选)"
    echo ""
    echo "示例:"
    echo "  $0 /var/log/app.log"
    echo "  $0 /var/log/app.log 'timeout|error' ERROR"
    echo "  $0 /var/log/app.log 'database' WARN 2025-11-01~2025-11-07"
    echo ""
}

# 检查参数
if [ -z "$LOG_FILE" ]; then
    echo "❌ 错误: 请提供日志文件路径"
    usage
    exit 1
fi

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ 错误: 文件不存在: $LOG_FILE"
    exit 1
fi

echo "📝 日志分析器"
echo "=========================================="
echo "文件: ${BLUE}$LOG_FILE${NC}"
echo "大小: $(du -h "$LOG_FILE" | cut -f1)"
echo "行数: $(wc -l < "$LOG_FILE")"
echo "=========================================="

# 按级别过滤
echo ""
echo "📊 按级别统计:"
echo "=========================================="

ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
WARN_COUNT=$(grep -c "WARN" "$LOG_FILE" 2>/dev/null || echo "0")
INFO_COUNT=$(grep -c "INFO" "$LOG_FILE" 2>/dev/null || echo "0")
DEBUG_COUNT=$(grep -c "DEBUG" "$LOG_FILE" 2>/dev/null || echo "0")

echo -e "  ${RED}ERROR${NC}: $ERROR_COUNT"
echo -e "  ${YELLOW}WARN${NC}:  $WARN_COUNT"
echo -e "  ${GREEN}INFO${NC}:  $INFO_COUNT"
echo -e "  ${BLUE}DEBUG${NC}: $DEBUG_COUNT"

# 展示特定级别的日志
echo ""
echo "=========================================="
echo "📋 ${LEVEL} 级别日志 (前10条):"
echo "=========================================="
grep "$LEVEL" "$LOG_FILE" | head -10

# 模式匹配
if [ -n "$PATTERN" ]; then
    echo ""
    echo "=========================================="
    echo "🔍 匹配模式 '${PATTERN}':"
    echo "=========================================="
    MATCH_COUNT=$(grep -c "$PATTERN" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "匹配数量: $MATCH_COUNT"
    echo ""
    echo "示例:"
    grep "$PATTERN" "$LOG_FILE" | head -5
fi

# 时间范围
check_date_range() {
    if [ -n "$DATE_RANGE" ]; then
        START_DATE=$(echo "$DATE_RANGE" | cut -d'~' -f1)
        END_DATE=$(echo "$DATE_RANGE" | cut -d'~' -f2)

        echo ""
        echo "=========================================="
        echo "📅 时间范围 $START_DATE ~ $END_DATE:"
        echo "=========================================="

        # 简单的日期过滤（假设日志包含日期)
        awk -v start="$START_DATE" -v end="$END_DATE" '
        $0 >= start && $0 <= end {
            print $0
        }' "$LOG_FILE" | head -10
    fi
}

check_date_range

# 常见错误模式分析
echo ""
echo "=========================================="
echo "⚠️  常见错误模式分析:"
echo "=========================================="

# 超时错误
TIMEOUT_COUNT=$(grep -c "timeout\|Timeout\|TIMEOUT" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$TIMEOUT_COUNT" -gt 0 ]; then
    echo -e "⏱️  超时错误: ${RED}$TIMEOUT_COUNT${NC}次"
fi

# 连接错误
CONN_ERROR_COUNT=$(grep -c "connection refused\|Connection refused\|ECONNREFUSED" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$CONN_ERROR_COUNT" -gt 0 ]; then
    echo -e "🔗 连接错误: ${RED}$CONN_ERROR_COUNT${NC}次"
fi

# 内存错误
MEMORY_ERROR_COUNT=$(grep -c "OutOfMemory\|memory\|Memory" "$LOG_FILE" 2>/dev/null || echo "0")
if [ "$MEMORY_ERROR_COUNT" -gt 0 ]; then
    echo -e "🧠 内存问题: ${RED}$MEMORY_ERROR_COUNT${NC}次"
fi

# 总结
echo ""
echo "=========================================="
echo "📊 统计总结:"
echo "=========================================="
echo "总错误数: $((ERROR_COUNT + WARN_COUNT))"
echo "关键错误数: $ERROR_COUNT"

if [ -n "$PATTERN" ]; then
    echo "模式'$PATTERN'匹配: $MATCH_COUNT 次"
fi

echo ""
echo "=========================================="
echo "💡 建议:"
echo "=========================================="
if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "  - ⚠️  ERROR数量较多，建议立即调查"
fi

if [ "$TIMEOUT_COUNT" -gt 5 ]; then
    echo "  - ⚠️  频繁超时，检查网络或服务响应"
fi

if [ "$CONN_ERROR_COUNT" -gt 3 ]; then
    echo "  - ⚠️  连接问题，验证服务状态和配置"
fi

if [ "$ERROR_COUNT" -le 5 ] && [ "$WARN_COUNT" -le 10 ]; then
    echo "  - ✅  日志健康状况良好"
fi

echo ""
echo "=========================================="
echo "日志分析完成"
echo "=========================================="
