#!/usr/bin/env bash
# Codex Vision Bridge 代理启动脚本（macOS / Linux）
set -e
here="$(cd "$(dirname "$0")" && pwd)"

node="${CVB_NODE_EXE:-node}"
command -v "$node" >/dev/null 2>&1 || { echo "[ERROR] 未找到 Node.js: $node" >&2; exit 1; }

export NODE_PATH="${NODE_PATH:-$here/node_modules}"
proxy_js="$here/ocr-proxy.js"
[ -f "$proxy_js" ] || { echo "[ERROR] 未找到 $proxy_js" >&2; exit 1; }

port="${OCR_PROXY_PORT:-57323}"
if lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "[OK] 代理已在运行，端口 $port"
    exit 0
fi

echo "[OK] 启动代理（后台），端口 $port"
echo "    日志: $here/outputs/proxy.log"
nohup "$node" "$proxy_js" >>"$here/outputs/proxy.log" 2>&1 &
