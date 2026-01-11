#!/bin/bash
# 磁盘健康检查器 - 检查磁盘空间、inode使用和健康状态

set -e

DISK_PATH="${1:-/}"
THRESHOLD="${2:-80}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 帮助信息
usage() {
    echo "💾 磁盘健康检查器"
    echo ""
    echo "使用: $0 [路径] [阈值]"
    echo ""
    echo "参数:"
    echo "  路径       要检查的磁盘路径 (默认: /)"
    echo "  阈值       空间使用警报阈值百分比 (默认: 80%)"
    echo ""
    echo "示例:"
    echo "  $0                    # 检查根目录，阈值80%"
    echo "  $0 /home 85           # 检查/home目录，阈值85%"
    echo "  $0 /var/log 90        # 检查日志目录，阈值90%"
    echo ""
}

# 检查参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    usage
    exit 0
fi

# 检查路径是否存在
if [ ! -d "$DISK_PATH" ]; then
    echo "❌ 错误: 路径不存在: $DISK_PATH"
    exit 1
fi

# 数字验证
if ! [[ "$THRESHOLD" =~ ^[0-9]+$ ]] || [ "$THRESHOLD" -lt 1 ] || [ "$THRESHOLD" -gt 100 ]; then
    echo "❌ 错误: 阈值必须是1-100之间的数字"
    exit 1
fi

echo "💾 磁盘健康检查器"
echo "=========================================="
echo "检查路径: ${BLUE}$DISK_PATH${NC}"
echo "警报阈值: ${THRESHOLD}%"
echo "=========================================="
echo ""

# 获取磁盘使用情况
DISK_INFO=$(df -h "$DISK_PATH" | tail -1)
DISK_DEVICE=$(echo "$DISK_INFO" | awk '{print $1}')
DISK_SIZE=$(echo "$DISK_INFO" | awk '{print $2}')
DISK_USED=$(echo "$DISK_INFO" | awk '{print $3}')
DISK_AVAIL=$(echo "$DISK_INFO" | awk '{print $4}')
DISK_USAGE_PERCENT=$(echo "$DISK_INFO" | awk '{print $5}' | sed 's/%//')

echo "📊 磁盘使用概况:"
echo "=========================================="
echo -e "设备: ${CYAN}$DISK_DEVICE${NC}"
echo -e "总容量: ${BLUE}$DISK_SIZE${NC}"
echo -e "已使用: ${YELLOW}$DISK_USED${NC}"
echo -e "可用: ${GREEN}$DISK_AVAIL${NC}"

# 使用百分比颜色标记
if [ "$DISK_USAGE_PERCENT" -gt 90 ]; then
    USAGE_COLOR="$RED"
    STATUS="🔴 严重"
elif [ "$DISK_USAGE_PERCENT" -gt "$THRESHOLD" ]; then
    USAGE_COLOR="$YELLOW"
    STATUS="🟡 警告"
else
    USAGE_COLOR="$GREEN"
    STATUS="🟢 正常"
fi

echo -e "使用率: ${USAGE_COLOR}${DISK_USAGE_PERCENT}%${NC} $STATUS"
echo ""

# inode检查
echo "=========================================="
echo "📂 Inode使用概况:"
echo "=========================================="

INODE_INFO=$(df -i "$DISK_PATH" | tail -1)
INODE_USED_PERCENT=$(echo "$INODE_INFO" | awk '{print $5}' | sed 's/%//')
INODE_TOTAL=$(echo "$INODE_INFO" | awk '{print $2}')
INODE_USED=$(echo "$INODE_INFO" | awk '{print $3}')
INODE_AVAIL=$(echo "$INODE_INFO" | awk '{print $4}')

echo -e "总数: ${BLUE}$INODE_TOTAL${NC}"
echo -e "已使用: ${YELLOW}$INODE_USED${NC}"
echo -e "可用: ${GREEN}$INODE_AVAIL${NC}"

# Inode百分比颜色
if [ "$INODE_USED_PERCENT" -gt 90 ]; then
    INODE_COLOR="$RED"
    INODE_STATUS="🔴 严重"
elif [ "$INODE_USED_PERCENT" -gt "$THRESHOLD" ]; then
    INODE_COLOR="$YELLOW"
    INODE_STATUS="🟡 警告"
else
    INODE_COLOR="$GREEN"
    INODE_STATUS="🟢 正常"
fi

echo -e "使用率: ${INODE_COLOR}${INODE_USED_PERCENT}%${NC} $INODE_STATUS"
echo ""

# 详细信息检测
echo "=========================================="
echo "🔍 详细信息:"
echo "=========================================="

# 文件系统类型
FS_TYPE=$(df -T "$DISK_PATH" | tail -1 | awk '{print $2}')
echo -e "文件系统类型: ${CYAN}$FS_TYPE${NC}"

# 挂载点
MOUNT_POINT=$(df "$DISK_PATH" | tail -1 | awk '{print $NF}')
echo -e "挂载点: ${BLUE}$MOUNT_POINT${NC}"

# 可读写性检测
if [ -w "$DISK_PATH" ]; then
    RW_STATUS="${GREEN}可读写${NC}"
else
    RW_STATUS="${RED}只读${NC}"
fi
echo -e "访问权限: $RW_STATUS"

echo ""

# 警报检查
echo "=========================================="
echo "🚨 警报检查:"
echo "=========================================="

ALERT_COUNT=0

if [ "$DISK_USAGE_PERCENT" -gt 90 ]; then
    echo -e "⚠️  磁盘使用率过高: ${RED}${DISK_USAGE_PERCENT}%${NC}"
    ((ALERT_COUNT++))
fi

if [ "$DISK_USAGE_PERCENT" -gt "$THRESHOLD" ]; then
    echo -e "⚠️  磁盘使用率超过阈值": "${DISK_USAGE_PERCENT}% > ${THRESHOLD}%"
fi

if [ "$INODE_USED_PERCENT" -gt 90 ]; then
    echo -e "⚠️  Inode使用率过高: ${RED}${INODE_USED_PERCENT}%${NC}"
    ((ALERT_COUNT++))
fi

if [ "$INODE_USED_PERCENT" -gt "$THRESHOLD" ]; then
    echo -e "⚠️  Inode使用率超过阈值": "${INODE_USED_PERCENT}% > ${THRESHOLD}%"
fi

if [ ! -w "$DISK_PATH" ]; then
    echo -e "⚠️  ${YELLOW}磁盘为只读状态${NC}"
    ((ALERT_COUNT++))
fi

echo ""
echo "=========================================="
echo "📈 性能指标:"
echo "=========================================="

# 检查磁盘是被大量小文件填满还是少数大文件
echo "按大小排序的顶级目录:"
du -h "$DISK_PATH" 2>/dev/null | sort -hr | head -5 | while read -r size path; do
    echo -e "  ${YELLOW}$size${NC}\t$path"
done

echo ""
echo "按数量排序的顶级目录:"
find "$DISK_PATH" -maxdepth 2 -type d 2>/dev/null | head -10 | while read -r dir; do
    count=$(find "$dir" -maxdepth 1 -type f 2>/dev/null | wc -l)
    if [ "$count" -gt 100 ]; then
        echo -e "  ${YELLOW}$count${NC}个文件\t$dir"
    fi
done

echo ""
echo "=========================================="
echo "💡 建议:"
echo "=========================================="

if [ "$ALERT_COUNT" -gt 0 ]; then
    echo "🚨 发现 $ALERT_COUNT 个问题需要处理:"
    echo ""

    if [ "$DISK_USAGE_PERCENT" -gt 90 ]; then
        echo "  磁盘使用率超过90%:"
        echo "  - 建议立即清理日志文件（/var/log）"
        echo "  - 检查临时文件（/tmp）"
        echo "  - 考虑扩容或迁移数据"
        echo ""
    fi

    if [ "$INODE_USED_PERCENT" -gt 90 ]; then
        echo "  Inode使用率高:"
        echo "  - 通常由大量小文件导致"
        echo "  - 检查并清理临时文件"
        echo "  - 查找并删除空文件"
        echo "  - 可能是邮件队列或缓存文件过多"
        echo ""
    fi

    if [ ! -w "$DISK_PATH" ]; then
        echo "  磁盘只读:"
        echo "  - 检查文件系统错误（fsck）"
        echo "  - 可能是磁盘故障或挂载问题"
        echo "  - 需要root权限检查和修复"
        echo ""
    fi
else
    echo "✅ 磁盘健康状况良好"
    echo ""

    if [ "$DISK_USAGE_PERCENT" -lt 70 ]; then
        echo "  - 使用率充足，暂无扩容需求"
    fi

    if [ "$INODE_USED_PERCENT" -lt 70 ]; then
        echo "  - Inode充足，无小文件问题"
    fi

    echo ""
    echo "  💡 建议定期运行此工具监控磁盘状态"
fi

echo ""
echo "=========================================="
echo "磁盘检查完成"
echo "=========================================="

exit 0
