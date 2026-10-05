#!/bin/sh
# 加载时先找可用的 Python 3；缺少时只提醒一次，继续原任务。
script_dir=${0%/*}
if [ -n "$OIL_NO_UPDATE_CHECK" ] || [ -e "$script_dir/../.git" ]; then
    exit 0
fi
state_base=${XDG_STATE_HOME:-${LOCALAPPDATA:-$HOME/.local/state}}
marker="$state_base/oil/update-python-missing"
for interpreter in python3 python; do
    if command -v "$interpreter" >/dev/null 2>&1 && "$interpreter" -c 'import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)' >/dev/null 2>&1; then
        rmdir "$marker" 2>/dev/null
        exec "$interpreter" "$script_dir/check_update.py"
    fi
done
# mkdir 的独占创建同时防止连续加载与并发加载重复提醒。
missing_python_notice() {
    case ${LC_ALL:-${LC_MESSAGES:-$LANG}} in
        en*|EN*) printf '%s\n' 'Automatic updates need Python 3. This update check did not run.' ;;
        *) printf '%s\n' '自动更新需要 Python 3，本次没有检查更新。' ;;
    esac
}
mkdir -p "$state_base/oil" 2>/dev/null
if mkdir "$marker" 2>/dev/null; then
    missing_python_notice
elif [ -d "$marker" ]; then
    printf '%s\n' 'OIL_UPDATE_CHECK_SKIPPED: missing_python'
else
    # 状态目录不可写时，由宿主记住这次提醒。
    missing_python_notice
fi
exit 0
