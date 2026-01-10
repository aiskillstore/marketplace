#!/bin/bash
# Stop Context7 MCP server
# Usage: ./stop-server.sh [port]

PORT=${1:-8809}
PID_FILE="/tmp/context7-mcp-${PORT}.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        # Kill the server
        kill "$PID" 2>/dev/null
        sleep 1

        # Force kill if still running
        kill -9 "$PID" 2>/dev/null || true

        echo "Context7 MCP stopped (was PID: $PID)"
    else
        echo "Context7 MCP not running (stale PID file)"
    fi
    rm -f "$PID_FILE"
else
    # Try to find and kill by process name
    pkill -f "context7-mcp.*--port.*${PORT}" 2>/dev/null && echo "Context7 MCP stopped" || echo "Context7 MCP not running"
fi
