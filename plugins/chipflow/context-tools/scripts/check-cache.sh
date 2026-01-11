#!/usr/bin/env bash
# Cache staleness check for PreToolUse hook
# Detects when repo map needs rebuilding: new files, modified files, or version mismatch

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PWD}"
CLAUDE_DIR="${PROJECT_ROOT}/.claude"
CACHE_FILE="${CLAUDE_DIR}/repo-map-cache.json"
REPO_MAP="${CLAUDE_DIR}/repo-map.md"
LAST_CHECK="${CLAUDE_DIR}/.last-cache-check"

# Throttle: only check every 30 seconds to avoid slowdown on large codebases
CHECK_INTERVAL=30

# Skip if already indexing (check running processes)
if pgrep -f "generate-repo-map.py.*${PROJECT_ROOT}" >/dev/null 2>&1; then
    exit 0
fi

# Skip if no .claude directory yet (first run handled by SessionStart)
if [[ ! -d "${CLAUDE_DIR}" ]]; then
    exit 0
fi

# Skip if we checked recently (within CHECK_INTERVAL seconds)
if [[ -f "${LAST_CHECK}" ]]; then
    LAST_CHECK_TIME=$(stat -f %m "${LAST_CHECK}" 2>/dev/null || stat -c %Y "${LAST_CHECK}" 2>/dev/null || echo "0")
    NOW=$(date +%s)
    if (( NOW - LAST_CHECK_TIME < CHECK_INTERVAL )); then
        exit 0
    fi
fi

NEEDS_REINDEX=false
REASON=""

# Expected cache version - must match CACHE_VERSION in generate-repo-map.py
EXPECTED_CACHE_VERSION=3

# Check 1: Cache version mismatch
if [[ -f "${CACHE_FILE}" ]]; then
    CACHE_VERSION=$(python3 -c "import json; print(json.load(open('${CACHE_FILE}')).get('version', 0))" 2>/dev/null || echo "0")
    if [[ "${CACHE_VERSION}" != "${EXPECTED_CACHE_VERSION}" ]]; then
        NEEDS_REINDEX=true
        REASON="cache version mismatch (${CACHE_VERSION} != ${EXPECTED_CACHE_VERSION})"
    fi
fi

# Check 2: File count changed (quick check)
if [[ "${NEEDS_REINDEX}" == "false" && -f "${CACHE_FILE}" ]]; then
    # Count cached files
    CACHED_COUNT=$(python3 -c "import json; print(len(json.load(open('${CACHE_FILE}')).get('files', {})))" 2>/dev/null || echo "0")

    # Count current source files (excluding common non-source dirs)
    # This is fast because find exits early and we just count
    CURRENT_COUNT=$(find "${PROJECT_ROOT}" \
        -type f \( -name "*.py" -o -name "*.rs" -o -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" -o -name "*.hpp" -o -name "*.h" -o -name "*.hxx" \) \
        ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" \
        ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/target/*" \
        ! -path "*/build/*" ! -path "*/dist/*" ! -path "*/.cache/*" \
        2>/dev/null | wc -l | tr -d ' ')

    if [[ "${CURRENT_COUNT}" != "${CACHED_COUNT}" ]]; then
        NEEDS_REINDEX=true
        REASON="file count changed (${CACHED_COUNT} cached, ${CURRENT_COUNT} found)"
    fi
fi

# Check 3: Any source file newer than repo map (sample check for speed)
if [[ "${NEEDS_REINDEX}" == "false" && -f "${REPO_MAP}" ]]; then
    # Find any source file newer than repo map (limit to first match for speed)
    NEWER_FILE=$(find "${PROJECT_ROOT}" \
        -type f \( -name "*.py" -o -name "*.rs" -o -name "*.cpp" -o -name "*.cc" -o -name "*.h" \) \
        -newer "${REPO_MAP}" \
        ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" \
        ! -path "*/venv/*" ! -path "*/.venv/*" ! -path "*/target/*" \
        ! -path "*/build/*" ! -path "*/dist/*" ! -path "*/.cache/*" \
        2>/dev/null | head -1)

    if [[ -n "${NEWER_FILE}" ]]; then
        NEEDS_REINDEX=true
        REASON="files modified since last index"
    fi
fi

# Update last check timestamp
touch "${LAST_CHECK}"

# Trigger reindex if needed
if [[ "${NEEDS_REINDEX}" == "true" ]]; then
    # Delete stale cache/map
    rm -f "${CACHE_FILE}" "${REPO_MAP}"

    # Start background reindex
    (
        nohup uv run "${SCRIPT_DIR}/generate-repo-map.py" "${PROJECT_ROOT}" \
            > "${CLAUDE_DIR}/repo-map-build.log" 2>&1 &
    ) &
fi

exit 0
