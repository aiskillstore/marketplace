---
description: Check repo map indexing progress
---

# Check Indexing Status

Check the current status of repo map generation.

## Status Information

```bash
PROJECT_ROOT="${PWD}"
CLAUDE_DIR="${PROJECT_ROOT}/.claude"
REPO_MAP="${CLAUDE_DIR}/repo-map.md"
PROGRESS_FILE="${CLAUDE_DIR}/repo-map-progress.json"

# Check if repo-map process is running (use pgrep, not lock file)
is_running() {
    pgrep -f "generate-repo-map.py.*${PROJECT_ROOT}" >/dev/null 2>&1
}

echo "=== Repo Map Status ==="

if [[ -f "${REPO_MAP}" ]]; then
    SYMBOL_COUNT=$(grep -c "^\*\*" "${REPO_MAP}" 2>/dev/null || echo "0")
    echo "Status: Complete"
    echo "Symbols: ${SYMBOL_COUNT}"

    if [[ -f "${PROGRESS_FILE}" ]]; then
        python3 -c "
import json
import time
with open('${PROGRESS_FILE}') as f:
    p = json.load(f)
ts = p.get('timestamp', 0)
if ts > 0:
    age = time.time() - ts
    if age < 60:
        print(f'Last updated: {int(age)}s ago')
    elif age < 3600:
        print(f'Last updated: {int(age/60)}m ago')
    else:
        print(f'Last updated: {int(age/3600)}h ago')
print(f'Files: {p.get(\"files_total\", \"?\")} ({p.get(\"files_cached\", 0)} cached)')
" 2>/dev/null || true
    fi

    if is_running; then
        echo ""
        echo "⏳ Update in progress..."
    fi
elif is_running; then
    echo "Status: Building..."

    if [[ -f "${PROGRESS_FILE}" ]]; then
        python3 -c "
import json
with open('${PROGRESS_FILE}') as f:
    p = json.load(f)
status = p.get('status', 'unknown')
parsed = p.get('files_parsed', 0)
to_parse = p.get('files_to_parse', 0)
total = p.get('files_total', 0)
cached = p.get('files_cached', 0)
symbols = p.get('symbols_found', 0)

print(f'Total files: {total}')
print(f'Cached: {cached}')
if to_parse > 0:
    pct = int(parsed / to_parse * 100)
    print(f'Parsing: {parsed}/{to_parse} ({pct}%)')
if symbols > 0:
    print(f'Symbols found: {symbols}')
" 2>/dev/null || echo "Progress data not available yet"
    else
        echo "Starting up..."
    fi

    echo ""
    echo "The repo map is building in the background."
    echo "It will be available once indexing completes."
else
    echo "Status: Not started"
    echo ""
    echo "Run /context-tools:repo-map to generate the repo map"
fi

echo "======================="
```

The repo map indexes all Python, C++, and Rust code in your project to help Claude understand the codebase structure and detect potential duplicates.
