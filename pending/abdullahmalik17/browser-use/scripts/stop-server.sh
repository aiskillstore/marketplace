#!/bin/bash
# Stop Playwright MCP server
# Usage: ./stop-server.sh [port]

PORT=${1:-8808}
PID_FILE="/tmp/playwright-mcp-${PORT}.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        # First close the browser gracefully
        python3 "$(dirname "$0")/mcp-client.py" call -u "http://localhost:${PORT}" -t browser_close -p '{}' 2>/dev/null || true

        # Then kill the server
        kill "$PID" 2>/dev/null
        sleep 1

        # Force kill if still running
        kill -9 "$PID" 2>/dev/null || true

        echo "Playwright MCP stopped (was PID: $PID)"
    else
        echo "Playwright MCP not running (stale PID file)"
    fi
    rm -f "$PID_FILE"
else
    # Try to find and kill by process name
    pkill -f "@playwright/mcp.*--port.*${PORT}" 2>/dev/null && echo "Playwright MCP stopped" || echo "Playwright MCP not running"
fi
