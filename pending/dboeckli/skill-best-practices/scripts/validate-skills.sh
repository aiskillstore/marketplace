#!/usr/bin/env bash
# Validate SKILL.md frontmatter for npx skills CLI compatibility.
#
# Usage:
#   bash validate-skills.sh           # local YAML check only
#   bash validate-skills.sh --remote  # local check + npx skills add --list
#
# Exit codes: 0 = all ok, 1 = errors found

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SKILLS_DIR="$REPO_ROOT/.claude/skills"
REMOTE=false
errors=0

[[ "${1:-}" == "--remote" ]] && REMOTE=true

frontmatter() { awk '/^---$/{n++; if(n==2)exit; next} n==1{print}' "$1"; }

for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
	[[ -f "$skill_md" ]] || continue
	skill="$(basename "$(dirname "$skill_md")")"
	fm="$(frontmatter "$skill_md")"
	fail=false

	output="$(printf '%s' "$fm" | python3 -c '
import sys, yaml
content = sys.stdin.read()
try:
    data = yaml.safe_load(content) or {}
except yaml.YAMLError as e:
    print(str(e).replace(chr(10), " "))
    sys.exit(1)
name = data.get("name", "")
desc = str(data.get("description", ""))
if not name:
    print("missing required field: name")
    sys.exit(1)
if not desc:
    print("missing required field: description")
    sys.exit(1)
if len(desc) > 1024:
    print("WARN description is " + str(len(desc)) + " chars (limit: 1024)")
' 2>&1)" || {
		echo "FAIL  $skill — $output"
		fail=true
		errors=$((errors + 1))
	}

	if ! $fail; then
		while IFS= read -r line; do
			[[ "$line" == WARN* ]] && echo "WARN  $skill — ${line#WARN }"
		done <<<"$output"
		echo "OK    $skill"
	fi
done

echo ""
[[ $errors -eq 0 ]] && echo "Local: all skills valid" || echo "Local: $errors error(s) found"

if $REMOTE; then
	REPO_URL="$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || true)"
	[[ -z "$REPO_URL" ]] && {
		echo "error: no git remote 'origin' found" >&2
		exit 1
	}
	echo ""
	echo "Remote: npx skills add --list $REPO_URL"
	echo ""
	_tmp="$(mktemp -d)"
	trap 'rm -rf "$_tmp"' EXIT
	TMPDIR="$_tmp" npm_config_cache="$_tmp/cache" \
		npx --yes --package=skills skills add --list "$REPO_URL" 2>&1 |
		sed 's/\x1b\[[0-9;]*[mGJhls?]//g; s/\r//g' |
		grep -E "(Skipped|Found [0-9]|Available Skills|  [a-z])" || true
fi

exit $((errors > 0))
