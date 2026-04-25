#!/bin/bash
# 美团打印机 Web 管理界面 - macOS 启动脚本
# 双击运行，或在终端执行: bash start.command

cd "$(dirname "$0")"

# 检测 Python
PYTHON=""
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ 未找到 Python，请先安装 Python 3"
    echo "   https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

echo "🔍 使用 Python: $PYTHON"
$PYTHON --version

# 检查依赖
echo "📦 检查依赖..."
$PYTHON -c "import flask" 2>/dev/null || {
    echo "📥 正在安装 flask..."
    $PYTHON -m pip install flask
}
$PYTHON -c "import apscheduler" 2>/dev/null || {
    echo "📥 正在安装 apscheduler..."
    $PYTHON -m pip install apscheduler
}

# 启动服务
echo ""
echo "======================================"
echo "  🖨️  美团打印机 Web 管理界面"
echo "  访问地址: http://localhost:5000"
echo "  （如果 5000 被占用则自动使用 5001）"
echo "  按 Ctrl+C 停止服务"
echo "======================================"
echo ""

$PYTHON web_admin.py

echo ""
echo "服务已停止。"
read -p "按回车键退出..."
