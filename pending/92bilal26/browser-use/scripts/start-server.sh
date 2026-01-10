#!/bin/bash
# Start Playwright MCP server for browser-use skill
# Usage: ./start-server.sh [port]

PORT=${1:-8808}
PID_FILE="/tmp/playwright-mcp-${PORT}.pid"

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "Playwright MCP already running on port $PORT (PID: $(cat $PID_FILE))"
    exit 0
fi

# Start server
npx @playwright/mcp@latest --port "$PORT" --shared-browser-context &
echo $! > "$PID_FILE"

sleep 2

if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "Playwright MCP started on port $PORT (PID: $(cat $PID_FILE))"
else
    echo "Failed to start Playwright MCP"
    rm -f "$PID_FILE"
    exit 1
fi
