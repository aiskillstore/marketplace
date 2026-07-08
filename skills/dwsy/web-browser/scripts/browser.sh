#!/bin/bash

# Web Browser Automation Script
# 基于 agent-browser 的封装脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
AGENT_BROWSER_CMD="${AGENT_BROWSER_CMD:-agent-browser}"
VERBOSE=0

log() {
  echo "[web-browser] $*"
}

verbose() {
  [ "$VERBOSE" -eq 1 ] && log "$*"
}

check_agent_browser() {
  if ! command -v $AGENT_BROWSER_CMD &> /dev/null; then
    if command -v npx &> /dev/null; then
      AGENT_BROWSER_CMD="npx agent-browser"
      verbose "Using npx: $AGENT_BROWSER_CMD"
    else
      log "错误: agent-browser 未安装"
      log "安装方式: npm install -g agent-browser"
      log "或使用: npx agent-browser"
      exit 1
    fi
  fi
}

show_help() {
  cat << 'EOF'
Web Browser Automation Script

使用方式:
  ./browser.sh <command> [args...]

常用命令:
  open <url>           打开网页
  snapshot             获取页面快照
  click <ref>          点击元素
  fill <ref> <text>    填写表单
  screenshot [path]    截图
  close                关闭浏览器
  help                 显示帮助信息

CDP 模式:
  --cdp <port>         连接到指定端口 (默认 9222)

示例:
  ./browser.sh open https://example.com
  ./browser.sh snapshot -i
  ./browser.sh click @e1
  ./browser.sh --cdp 9222 snapshot

完整帮助:
  ./browser.sh agent-browser-help
EOF
}

agent_browser_help() {
  check_agent_browser
  $AGENT_BROWSER_CMD --help
}

main() {
  check_agent_browser

  if [ $# -eq 0 ]; then
    show_help
    exit 0
  fi

  case "$1" in
    help|--help|-h)
      show_help
      ;;

    agent-browser-help)
      agent_browser_help
      ;;

    *)
      verbose "执行: $AGENT_BROWSER_CMD $*"
      $AGENT_BROWSER_CMD "$@"
      ;;
  esac
}

main "$@"
