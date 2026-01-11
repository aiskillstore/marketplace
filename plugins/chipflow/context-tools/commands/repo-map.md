# Regenerate Repository Map

Regenerate the repo map for this project to understand the code structure, find similar classes/functions, and identify documentation gaps.

Run this command to regenerate:

```bash
# Kill ALL repo-map processes for this project
PROJECT_PATH="${PWD}"
echo "Checking for existing repo-map processes..."
PIDS=$(pgrep -f "generate-repo-map.py.*${PROJECT_PATH}" 2>/dev/null || true)
if [[ -n "${PIDS}" ]]; then
    echo "Stopping existing processes: ${PIDS}"
    echo "${PIDS}" | xargs kill 2>/dev/null || true
    sleep 1
    # Force kill any remaining
    PIDS=$(pgrep -f "generate-repo-map.py.*${PROJECT_PATH}" 2>/dev/null || true)
    if [[ -n "${PIDS}" ]]; then
        echo "${PIDS}" | xargs kill -9 2>/dev/null || true
    fi
fi

# Run any cache format migrations (clears cache if incompatible version)
python3 -c "
import json
from pathlib import Path

CURRENT_VERSION = 2  # Must match CACHE_VERSION in generate-repo-map.py

cache_path = Path('.claude/repo-map-cache.json')
if cache_path.exists():
    try:
        data = json.loads(cache_path.read_text())
        version = data.get('version', 0)
        if version != CURRENT_VERSION:
            print(f'Cache version {version} != {CURRENT_VERSION}, clearing...')
            cache_path.unlink()
    except (json.JSONDecodeError, KeyError):
        print('Corrupt cache, clearing...')
        cache_path.unlink()
" 2>/dev/null

# Run in foreground with live output
echo "Regenerating repo map..."
uv run ${CLAUDE_PLUGIN_ROOT}/scripts/generate-repo-map.py 2>&1

# Show summary with clash count
if [[ -f .claude/repo-map.md ]]; then
    CLASH_COUNT=$(grep -c "^- \*\*" .claude/repo-map.md 2>/dev/null | head -1 || echo "0")
    if [[ "${CLASH_COUNT}" -gt 0 ]]; then
        echo ""
        echo "${CLASH_COUNT} potential naming clash(es) detected."
        echo "Run /clash-summary for overview or /resolve-clashes to review interactively."
    fi
fi
```

After running, review the output for:
- **Similar classes**: May indicate overlapping responsibilities or duplicate implementations (same-language only)
- **Similar functions**: May be candidates for consolidation (same-language only)
- **Undocumented code**: Opportunities to improve codebase understanding

Note: Cross-language similarities (e.g., Python and Rust) are not flagged as they're typically intentional (bindings, ports).

If clashes are detected, use `/clash-summary` for an overview or `/resolve-clashes` to review and resolve them interactively.
