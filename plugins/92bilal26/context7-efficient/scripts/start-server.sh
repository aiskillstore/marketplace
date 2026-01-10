#!/bin/bash
# Start Context7 MCP server for context7-efficient skill
# Usage: ./start-server.sh [port]

PORT=${1:-8809}
PID_FILE="/tmp/context7-mcp-${PORT}.pid"

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "Context7 MCP already running on port $PORT (PID: $(cat $PID_FILE))"
    exit 0
fi

# Start server
npx -y @upstash/context7-mcp --port "$PORT" &
echo $! > "$PID_FILE"

sleep 2

if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
    echo "Context7 MCP started on port $PORT (PID: $(cat $PID_FILE))"
else
    echo "Failed to start Context7 MCP"
    rm -f "$PID_FILE"
    exit 1
fi
