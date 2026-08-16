#!/bin/bash
# ----------------------------------------------------------------------------
# pricewin-flight-search — registers the hosted `pricewin` MCP server with every
# agent found on this machine. Idempotent: re-running changes nothing once the
# entry is present and pointing at the same URL.
#
# Why this exists: the skill is guidance for driving MCP tools, so without the
# server registered it is inert — the agent reads "call search_flights_live" and
# has no such tool. `npx skills add` only copies files (the CLI has no install
# hook), so this step cannot happen automatically at add-time.
#
# The server is public Streamable HTTP and takes no credentials, so there is
# nothing secret to write anywhere.
#
# Usage:  bash install.sh [--dry-run] [--url <mcp-url>]
# ----------------------------------------------------------------------------
set -euo pipefail

MCP_NAME="pricewin"
MCP_URL="${PRICEWIN_MCP_URL:-https://mcp.price.win/mcp}"
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --url) MCP_URL="$2"; shift 2 ;;
    -h|--help) sed -n '2,17p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

command -v node >/dev/null 2>&1 || {
  echo "[pricewin-flight-search] node is required (it merges JSON config safely). Install Node 18+ and re-run." >&2
  exit 1
}

say(){ echo "[pricewin-flight-search] $*"; }

# Merge one server entry into an agent's JSON config without disturbing anything
# else in the file. Done in node rather than sed/jq: these files hold the user's
# whole agent config, jq is not always installed, and a regex edit that half-works
# is worse than no installer at all. Writes a .bak the first time it touches a file.
#
# $3 is the entry shape, which is NOT the same across agents — Gemini expects the
# URL under `httpUrl`, Windsurf under `serverUrl`, the rest under `url`. Writing
# one shape everywhere would leave a parseable but dead entry in half of them.
merge_json(){
  local file="$1" wrapper_key="$2" shape="${3:-type-url}"
  MCP_FILE="$file" MCP_WRAPPER="$wrapper_key" MCP_SHAPE="$shape" MCP_NAME="$MCP_NAME" MCP_URL="$MCP_URL" MCP_DRY="$DRY_RUN" node - <<'NODE'
const fs = require('fs');
const path = require('path');
const file = process.env.MCP_FILE;
const wrapper = process.env.MCP_WRAPPER;
const name = process.env.MCP_NAME;
const url = process.env.MCP_URL;
const dry = process.env.MCP_DRY === '1';

let config = {};
let existed = false;
if (fs.existsSync(file)) {
  existed = true;
  const raw = fs.readFileSync(file, 'utf8').trim();
  if (raw) {
    try {
      config = JSON.parse(raw);
    } catch {
      // Refuse to touch a file we cannot parse — rewriting it would destroy
      // whatever the user actually has in there.
      console.log(`SKIP ${file} (not valid JSON — register ${name} manually)`);
      process.exit(0);
    }
  }
}

const shapes = {
  'type-url': { type: 'http', url },
  'url': { url },
  'httpUrl': { httpUrl: url },
  'serverUrl': { serverUrl: url },
};
const entry = shapes[process.env.MCP_SHAPE] || shapes['type-url'];
const urlKey = Object.keys(entry).find((k) => entry[k] === url);

const servers = config[wrapper] && typeof config[wrapper] === 'object' ? config[wrapper] : {};
const current = servers[name];
if (current && current[urlKey] === url) {
  console.log(`OK ${file} (already registered)`);
  process.exit(0);
}

servers[name] = entry;
config[wrapper] = servers;

if (dry) {
  console.log(`WOULD ${current ? 'update' : 'add'} ${name} in ${file}`);
  process.exit(0);
}

fs.mkdirSync(path.dirname(file), { recursive: true });
if (existed && !fs.existsSync(`${file}.bak`)) fs.copyFileSync(file, `${file}.bak`);
fs.writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`);
console.log(`${current ? 'UPDATED' : 'ADDED'} ${name} in ${file}`);
NODE
}

# Codex keeps TOML, which has no safe merge without a parser we can rely on, so we
# only ever append a block and only when it is absent.
merge_codex(){
  local file="$HOME/.codex/config.toml"
  [ -d "$HOME/.codex" ] || return 1
  if [ -f "$file" ] && grep -q "^\[mcp_servers\.${MCP_NAME}\]" "$file"; then
    say "OK $file (already registered)"
    return 0
  fi
  if [ "$DRY_RUN" = "1" ]; then
    say "WOULD append [mcp_servers.$MCP_NAME] to $file"
    return 0
  fi
  [ -f "$file" ] && [ ! -f "$file.bak" ] && cp "$file" "$file.bak"
  mkdir -p "$HOME/.codex"
  {
    echo
    echo "[mcp_servers.${MCP_NAME}]"
    echo "url = \"${MCP_URL}\""
  } >> "$file"
  say "ADDED $MCP_NAME in $file"
}

say "Registering MCP server '$MCP_NAME' -> $MCP_URL"
[ "$DRY_RUN" = "1" ] && say "(dry run — nothing will be written)"

found=0

# Claude Code — user scope lives in ~/.claude.json. Prefer the CLI when present so
# we go through whatever the installed version considers correct.
if command -v claude >/dev/null 2>&1; then
  found=1
  if [ "$DRY_RUN" = "1" ]; then
    say "WOULD run: claude mcp add --transport http $MCP_NAME $MCP_URL --scope user"
  elif claude mcp list 2>/dev/null | grep -q "^${MCP_NAME}\b"; then
    say "OK claude CLI (already registered)"
  elif claude mcp add --transport http "$MCP_NAME" "$MCP_URL" --scope user >/dev/null 2>&1; then
    say "ADDED $MCP_NAME via claude CLI (user scope)"
  else
    say "claude CLI rejected the add — falling back to ~/.claude.json"
    merge_json "$HOME/.claude.json" mcpServers
  fi
elif [ -f "$HOME/.claude.json" ] || [ -d "$HOME/.claude" ]; then
  found=1
  merge_json "$HOME/.claude.json" mcpServers
fi

# Agents keyed under "mcpServers" but each with its own entry shape.
while IFS='|' read -r cfg shape; do
  [ -n "$cfg" ] || continue
  if [ -f "$cfg" ] || [ -d "$(dirname "$cfg")" ]; then
    found=1
    merge_json "$cfg" mcpServers "$shape"
  fi
done <<EOF
$HOME/.cursor/mcp.json|url
$HOME/.codeium/windsurf/mcp_config.json|serverUrl
$HOME/.gemini/settings.json|httpUrl
EOF

# VS Code / Copilot uses the same file with a "servers" key instead.
for vscode_dir in "$HOME/.vscode" "$HOME/Library/Application Support/Code/User" "$HOME/.config/Code/User"; do
  if [ -d "$vscode_dir" ]; then
    found=1
    merge_json "$vscode_dir/mcp.json" servers
  fi
done

merge_codex && found=1 || true

if [ "$found" = "0" ]; then
  say "No agent config directory found on this machine."
  echo
  echo "Register the server manually with whichever agent you use:"
  echo "  claude mcp add --transport http $MCP_NAME $MCP_URL --scope user"
  echo
  echo "or add this to your agent's MCP config:"
  echo "  \"$MCP_NAME\": { \"type\": \"http\", \"url\": \"$MCP_URL\" }"
  exit 0
fi

echo
say "Done. Restart your agent so it picks up the new server."
say "Verify with: curl -s -X POST $MCP_URL -H 'content-type: application/json' \\"
say "  -H 'accept: application/json, text/event-stream' \\"
say "  -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}'"
