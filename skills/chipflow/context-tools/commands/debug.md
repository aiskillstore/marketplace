---
description: Debug context-tools plugin status
---

# Debug Plugin Status

Run this to diagnose plugin issues:

```bash
echo "=== Context Tools Debug ==="
echo ""

# Check .claude directory
CLAUDE_DIR="${PWD}/.claude"
echo "Project .claude dir: ${CLAUDE_DIR}"
if [[ -d "${CLAUDE_DIR}" ]]; then
    echo "  EXISTS"
    ls -la "${CLAUDE_DIR}/" 2>/dev/null || echo "  (empty)"
else
    echo "  DOES NOT EXIST"
fi
echo ""

# Check repo map
REPO_MAP="${CLAUDE_DIR}/repo-map.md"
if [[ -f "${REPO_MAP}" ]]; then
    SYMBOL_COUNT=$(grep -c "^\*\*" "${REPO_MAP}" 2>/dev/null || echo "0")
    echo "Repo map: EXISTS (${SYMBOL_COUNT} symbols)"
    echo "  Modified: $(stat -f '%Sm' "${REPO_MAP}" 2>/dev/null || stat -c '%y' "${REPO_MAP}" 2>/dev/null || echo 'unknown')"
else
    echo "Repo map: DOES NOT EXIST"
fi
echo ""

# Check progress file
PROGRESS="${CLAUDE_DIR}/repo-map-progress.json"
if [[ -f "${PROGRESS}" ]]; then
    echo "Progress file: EXISTS"
    cat "${PROGRESS}" | python3 -m json.tool 2>/dev/null || cat "${PROGRESS}"
else
    echo "Progress file: DOES NOT EXIST"
fi
echo ""

# Check lock file
LOCK="${CLAUDE_DIR}/repo-map-cache.lock"
if [[ -f "${LOCK}" ]]; then
    echo "Lock file: EXISTS (indexing in progress)"
    cat "${LOCK}"
else
    echo "Lock file: does not exist (not currently indexing)"
fi
echo ""

# Check cache
CACHE="${CLAUDE_DIR}/repo-map-cache.json"
if [[ -f "${CACHE}" ]]; then
    FILE_COUNT=$(python3 -c "import json; print(len(json.load(open('${CACHE}')).get('files', {})))" 2>/dev/null || echo "?")
    echo "Cache: EXISTS (${FILE_COUNT} files cached)"
else
    echo "Cache: DOES NOT EXIST"
fi
echo ""

# Check manifest
MANIFEST="${CLAUDE_DIR}/project-manifest.json"
if [[ -f "${MANIFEST}" ]]; then
    echo "Manifest: EXISTS"
    python3 -c "import json; m=json.load(open('${MANIFEST}')); print(f\"  Project: {m.get('project_name', '?')}\")" 2>/dev/null || true
else
    echo "Manifest: DOES NOT EXIST"
fi
echo ""

echo "=== Debug Complete ==="
```

This will show all the plugin state files and their contents.
