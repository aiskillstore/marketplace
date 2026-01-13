#!/bin/bash
# Find potentially blocking calls in async Python code
# Usage: ./find-blocking-calls.sh [directory]

DIR="${1:-.}"

echo "=== Scanning for blocking calls in async code ==="
echo "Directory: $DIR"
echo

# time.sleep() in async functions
echo "--- time.sleep() in async functions ---"
rg -n "async def" -A 20 "$DIR" | rg "time\.sleep\(" || echo "None found"
echo

# requests library (blocking HTTP)
echo "--- requests library usage ---"
rg -n "import requests|from requests" "$DIR" --type py || echo "None found"
echo

# Blocking file operations
echo "--- Blocking file operations in async ---"
rg -n "async def" -A 30 "$DIR" | rg "open\(|\.read\(\)|\.write\(" || echo "None found"
echo

# subprocess without asyncio
echo "--- Blocking subprocess calls ---"
rg -n "subprocess\.(run|call|check_output)" "$DIR" --type py || echo "None found"
echo

# socket operations
echo "--- Blocking socket operations ---"
rg -n "socket\.(socket|create_connection)" "$DIR" --type py || echo "None found"
echo

# input() calls
echo "--- Blocking input() calls ---"
rg -n "\binput\(" "$DIR" --type py || echo "None found"
echo

echo "=== Recommendations ==="
echo "- Replace time.sleep() with asyncio.sleep()"
echo "- Replace requests with aiohttp or httpx"
echo "- Replace open() with aiofiles"
echo "- Replace subprocess with asyncio.create_subprocess_exec()"
echo "- Use asyncio.get_event_loop().run_in_executor() for blocking code"
