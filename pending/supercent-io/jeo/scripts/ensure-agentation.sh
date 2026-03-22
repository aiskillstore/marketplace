#!/usr/bin/env bash
# JEO helper — ensures agentation npm package is installed and <Agentation> is mounted
# in the project's React entry point before VERIFY_UI runs.
#
# Usage: bash ensure-agentation.sh [--project-dir <path>] [--endpoint <url>] [--quiet] [--dry-run]
# Exit codes:
#   0  — agentation ready (already installed, or just installed+injected)
#   1  — could not install or inject (non-fatal: VERIFY_UI should graceful-skip)
#   2  — package.json not found (not a Node.js project — skip silently)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── defaults ──────────────────────────────────────────────────────────────────
PROJECT_DIR="${PWD}"
ENDPOINT="http://localhost:4747"
QUIET=false
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --project-dir=*) PROJECT_DIR="${arg#*=}" ;;
    --endpoint=*)    ENDPOINT="${arg#*=}" ;;
    --quiet)         QUIET=true ;;
    --dry-run)       DRY_RUN=true ;;
    -h|--help)
      echo "Usage: bash ensure-agentation.sh [--project-dir <path>] [--endpoint <url>] [--quiet] [--dry-run]"
      echo "Ensures agentation npm package is installed and <Agentation> is mounted in the React entry point."
      exit 0
      ;;
  esac
done

log() { $QUIET || echo "[JEO][ANNOTATE] $*"; }
warn() { echo "[JEO][ANNOTATE] ⚠️  $*" >&2; }

# ── locate package.json ───────────────────────────────────────────────────────
find_package_json() {
  local dir="$1"
  # Check project dir and common sub-dirs
  for candidate in "$dir" "$dir/src" "$dir/app" "$dir/frontend" "$dir/client" "$dir/web"; do
    if [[ -f "$candidate/package.json" ]]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

PKG_DIR=""
if ! PKG_DIR=$(find_package_json "$PROJECT_DIR"); then
  log "No package.json found — not a Node.js project, skipping agentation setup."
  exit 2
fi

log "Found package.json at: $PKG_DIR"

# ── check if agentation already in dependencies ───────────────────────────────
is_package_installed() {
  python3 - "$PKG_DIR/package.json" <<'EOF'
import sys, json
try:
    d = json.load(open(sys.argv[1]))
    deps = {**d.get('dependencies', {}), **d.get('devDependencies', {})}
    sys.exit(0 if 'agentation' in deps else 1)
except Exception:
    sys.exit(1)
EOF
}

# ── detect package manager ────────────────────────────────────────────────────
detect_package_manager() {
  if [[ -f "$PKG_DIR/bun.lockb" ]] || [[ -f "$PKG_DIR/bun.lock" ]]; then
    echo "bun"
  elif [[ -f "$PKG_DIR/pnpm-lock.yaml" ]]; then
    echo "pnpm"
  elif [[ -f "$PKG_DIR/yarn.lock" ]]; then
    echo "yarn"
  else
    echo "npm"
  fi
}

# ── install agentation package ────────────────────────────────────────────────
install_agentation() {
  local pm="$1"
  log "Installing agentation with $pm..."
  if $DRY_RUN; then
    log "[dry-run] would run: cd $PKG_DIR && $pm add agentation -D (or equivalent)"
    return 0
  fi

  case "$pm" in
    bun)  (cd "$PKG_DIR" && bun add agentation -D) ;;
    pnpm) (cd "$PKG_DIR" && pnpm add agentation -D) ;;
    yarn) (cd "$PKG_DIR" && yarn add agentation --dev) ;;
    npm)  (cd "$PKG_DIR" && npm install agentation --save-dev --legacy-peer-deps) ;;
  esac
}

# ── find React entry point ────────────────────────────────────────────────────
find_entry_point() {
  local dir="$PROJECT_DIR"
  local candidates=(
    # Vite / CRA
    "$dir/src/main.tsx"
    "$dir/src/main.jsx"
    "$dir/main.tsx"
    "$dir/main.jsx"
    # Next.js App Router
    "$dir/app/layout.tsx"
    "$dir/app/layout.jsx"
    "$dir/src/app/layout.tsx"
    "$dir/src/app/layout.jsx"
    # Next.js Pages Router
    "$dir/pages/_app.tsx"
    "$dir/pages/_app.jsx"
    "$dir/src/pages/_app.tsx"
    "$dir/src/pages/_app.jsx"
  )
  for f in "${candidates[@]}"; do
    if [[ -f "$f" ]]; then
      echo "$f"
      return 0
    fi
  done
  return 1
}

# ── inject <Agentation> into entry point ─────────────────────────────────────
inject_agentation() {
  local entry="$1"
  local endpoint="$2"

  # Already injected?
  if grep -q 'from.*agentation' "$entry" 2>/dev/null; then
    log "<Agentation> already imported in $entry"
    return 0
  fi

  log "Injecting <Agentation endpoint=\"$endpoint\" /> into $entry"

  if $DRY_RUN; then
    log "[dry-run] would inject into $entry"
    return 0
  fi

  # Detect framework pattern from filename
  local filename
  filename="$(basename "$entry")"
  local framework="vite"
  [[ "$filename" == "layout.tsx" || "$filename" == "layout.jsx" ]] && framework="next-app"
  [[ "$filename" == "_app.tsx" || "$filename" == "_app.jsx" ]] && framework="next-pages"

  python3 - "$entry" "$endpoint" "$framework" <<'PYEOF'
import sys, re

entry_path = sys.argv[1]
endpoint = sys.argv[2]
framework = sys.argv[3]

with open(entry_path, 'r', encoding='utf-8') as f:
    content = f.read()

IMPORT_LINE = "import { Agentation } from 'agentation';"
COMPONENT_DEV = f"{{process.env.NODE_ENV === 'development' && <Agentation endpoint=\"{endpoint}\" />}}"

# Already injected guard (double-check)
if 'agentation' in content.lower():
    print(f"[JEO][ANNOTATE] agentation already present in {entry_path}", file=sys.stderr)
    sys.exit(0)

# --- Add import line ---
# Insert after the last existing import statement
import_match = list(re.finditer(r'^import\s.+;?\s*$', content, re.MULTILINE))
if import_match:
    last_import = import_match[-1]
    insert_pos = last_import.end()
    content = content[:insert_pos] + '\n' + IMPORT_LINE + content[insert_pos:]
else:
    # No imports found; prepend
    content = IMPORT_LINE + '\n' + content

# --- Inject component ---
if framework == 'next-app':
    # Next.js App Router layout.tsx: inject before closing </body> or </html>, or before return closing
    if '</body>' in content:
        content = content.replace('</body>', f'      {COMPONENT_DEV}\n      </body>', 1)
    elif 'return (' in content:
        # Inject before last closing paren of return block
        last_paren = content.rfind('\n)')
        if last_paren >= 0:
            content = content[:last_paren] + f'\n      {COMPONENT_DEV}' + content[last_paren:]
elif framework == 'next-pages':
    # Next.js Pages _app: inject inside Component rendering
    if '<Component' in content:
        content = re.sub(
            r'(<Component\s[^/]*/?>)',
            r'\1\n      ' + COMPONENT_DEV,
            content,
            count=1
        )
    elif 'return (' in content:
        last_paren = content.rfind('\n  )')
        if last_paren >= 0:
            content = content[:last_paren] + f'\n      {COMPONENT_DEV}' + content[last_paren:]
else:
    # Vite / CRA: inject inside the root render call
    # Strategy 1: inject before ReactDOM.createRoot closing render call's last closing tag
    # Look for </StrictMode>, </React.StrictMode>, or the outermost JSX closing tag
    strict_match = re.search(r'(</(?:React\.)?StrictMode>)', content)
    if strict_match:
        pos = strict_match.start()
        content = content[:pos] + f'  {COMPONENT_DEV}\n  ' + content[pos:]
    else:
        # Strategy 2: find render(<...>) and inject inside
        render_match = re.search(r'(\.render\s*\(\s*<)([^)]+?)(\s*>\s*\))', content, re.DOTALL)
        if render_match:
            inner = render_match.group(2)
            new_inner = inner + f'\n  {COMPONENT_DEV}'
            content = content[:render_match.start(2)] + new_inner + content[render_match.end(2):]

with open(entry_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[JEO][ANNOTATE] ✅ Injected <Agentation endpoint=\"{endpoint}\" /> into {entry_path}")
PYEOF
}

# ── main ──────────────────────────────────────────────────────────────────────
main() {
  local pm
  pm=$(detect_package_manager)
  log "Detected package manager: $pm"

  # 1. Install package if needed
  if is_package_installed; then
    log "agentation package already in $PKG_DIR/package.json"
  else
    log "agentation package not found — installing..."
    if ! install_agentation "$pm"; then
      warn "Failed to install agentation package. Run manually: cd $PKG_DIR && $pm add agentation -D"
      exit 1
    fi
    log "agentation package installed successfully."
  fi

  # 2. Find entry point and inject component
  local entry=""
  if ! entry=$(find_entry_point); then
    warn "Could not find React entry point (main.jsx, app/layout.tsx, pages/_app.tsx). Mount <Agentation endpoint=\"$ENDPOINT\" /> manually."
    exit 1
  fi

  inject_agentation "$entry" "$ENDPOINT"
  log "Entry point: $entry — injection complete."
  exit 0
}

main
