#!/bin/bash
# Start Next.js DevTools MCP server
set -euo pipefail

PORT="${1:-8809}"

echo "Starting Next.js DevTools MCP server on port $PORT..."
npx next-devtools-mcp@latest --port "$PORT" &

echo "Server started. Use mcp-client.py with -u http://localhost:$PORT"
