#!/bin/bash
#
# AI Partner Chat 2.0 - 安全安装到 Claude Code Skill 目录
# 特性：保护 data/ 目录，避免历史数据丢失
#

set -e

echo "🚀 安装 AI Partner Chat 2.0 到 Claude Code..."

# 目录配置
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.claude/skills/ai-partner-chat"
DATA_DIR="$TARGET_DIR/data"
BACKUP_DIR="/tmp/ai-partner-data-backup-$$"

# ========================================
# 1. 备份现有 data 目录（如果存在）
# ========================================
if [ -d "$DATA_DIR" ]; then
    echo "💾 检测到现有数据目录，正在备份..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$DATA_DIR" "$BACKUP_DIR/"
    echo "   备份位置: $BACKUP_DIR/data"
fi

# ========================================
# 2. 安全删除旧版本（保留 data/）
# ========================================
if [ -d "$TARGET_DIR" ]; then
    echo "🗑️  清理旧版本文件..."
    # 只删除代码文件，不删除 data/
    rm -rf "$TARGET_DIR/scripts" 2>/dev/null || true
    rm -rf "$TARGET_DIR/assets" 2>/dev/null || true
    rm -rf "$TARGET_DIR/notes" 2>/dev/null || true
    rm -f "$TARGET_DIR/SKILL.md" 2>/dev/null || true
    rm -f "$TARGET_DIR/README.md" 2>/dev/null || true
    rm -f "$TARGET_DIR/QUICKSTART.md" 2>/dev/null || true
    rm -f "$TARGET_DIR/CHANGELOG.md" 2>/dev/null || true
    rm -f "$TARGET_DIR/HOW_TO_USE.md" 2>/dev/null || true

    # 删除旧的运行时目录（已迁移到 data/）
    rm -rf "$TARGET_DIR/vector_db" 2>/dev/null || true
    rm -rf "$TARGET_DIR/conversations" 2>/dev/null || true
    rm -rf "$TARGET_DIR/indexes" 2>/dev/null || true
    rm -rf "$TARGET_DIR/analysis" 2>/dev/null || true
fi

# ========================================
# 3. 创建目标目录结构
# ========================================
echo "📦 复制项目文件..."
mkdir -p "$TARGET_DIR"

# 复制核心文件
cp -r "$PROJECT_ROOT/scripts" "$TARGET_DIR/"
cp -r "$PROJECT_ROOT/assets" "$TARGET_DIR/"

# 复制 SKILL.md（唯一必须的文档）
cp "$PROJECT_ROOT/SKILL.md" "$TARGET_DIR/"

# 复制示例 notes（如果存在）
if [ -d "$PROJECT_ROOT/notes" ]; then
    echo "📝 复制笔记示例..."
    cp -r "$PROJECT_ROOT/notes" "$TARGET_DIR/notes-examples"
    echo "   💡 提示: 在你的项目中创建 notes/ 目录来记录学习笔记"
    echo "   系统会自动检测并学习这些笔记"
fi

# ========================================
# 4. 恢复 data 目录（如果有备份）
# ========================================
if [ -d "$BACKUP_DIR/data" ]; then
    echo "♻️  恢复历史数据..."
    cp -r "$BACKUP_DIR/data" "$TARGET_DIR/"
    rm -rf "$BACKUP_DIR"
    echo "   ✅ 历史数据已恢复"
else
    # 首次安装：创建空的 data 目录结构
    echo "📁 初始化 data 目录..."
    mkdir -p "$TARGET_DIR/data/vector_db"
    mkdir -p "$TARGET_DIR/data/conversations/raw"
    mkdir -p "$TARGET_DIR/data/conversations/summary"
    mkdir -p "$TARGET_DIR/data/indexes"
    mkdir -p "$TARGET_DIR/data/analysis"
fi

# ========================================
# 5. 统计信息
# ========================================
TOTAL_CHUNKS=0
if [ -d "$TARGET_DIR/data/vector_db" ]; then
    # 粗略统计向量数据库大小
    TOTAL_CHUNKS=$(find "$TARGET_DIR/data/vector_db" -type f 2>/dev/null | wc -l | tr -d ' ')
fi

TOTAL_CONVS=0
if [ -d "$TARGET_DIR/data/conversations/raw" ]; then
    TOTAL_CONVS=$(find "$TARGET_DIR/data/conversations/raw" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "📍 安装位置: $TARGET_DIR"
echo "📊 数据统计:"
echo "   - 向量库文件: $TOTAL_CHUNKS"
echo "   - 对话记录: $TOTAL_CONVS 个文件"
echo ""
echo "🔧 后续步骤:"
echo ""
echo "1️⃣  创建 Python 虚拟环境（在你的项目目录）:"
echo "   cd /path/to/your/project"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate  # macOS/Linux"
echo "   # 或 venv\\Scripts\\activate  # Windows"
echo ""
echo "2️⃣  安装依赖:"
echo "   pip install -r $TARGET_DIR/scripts/requirements.txt"
echo ""
echo "3️⃣  配置画像（首次使用）:"
echo "   mkdir -p config"
echo "   cp $TARGET_DIR/assets/user-persona-template.md config/user-persona.md"
echo "   cp $TARGET_DIR/assets/ai-persona-template.md config/ai-persona.md"
echo "   # 然后编辑 config/*.md 填写你的画像信息"
echo ""
echo "💡 测试安装:"
echo "   python3 -c 'import sys; from pathlib import Path; sys.path.insert(0, str(Path.home() / \".claude/skills/ai-partner-chat/scripts\")); from orchestrator import AIPartnerOrchestrator; orch = AIPartnerOrchestrator(); print(orch.get_system_stats())'"
echo ""
