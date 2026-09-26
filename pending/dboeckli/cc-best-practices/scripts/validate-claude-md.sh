#!/usr/bin/env bash
# Validate CLAUDE.md: required sections present and skill table in sync with skill folders.
#
# Exit codes: 0 = all ok, 1 = errors found

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
SKILLS_DIR="$REPO_ROOT/.claude/skills"
errors=0

if [[ ! -f "$CLAUDE_MD" ]]; then
	echo "FAIL  CLAUDE.md not found at repo root"
	exit 1
fi

REQUIRED_SECTIONS=(
	"## Repository Purpose"
	"## Skill Structure"
	"## Included Skills"
	"## Conventions When Adding a New Skill"
)

for section in "${REQUIRED_SECTIONS[@]}"; do
	if grep -qF "$section" "$CLAUDE_MD"; then
		echo "OK    section: $section"
	else
		echo "FAIL  missing section: $section"
		errors=$((errors + 1))
	fi
done

echo ""

# Collect skill folder names
mapfile -t folder_skills < <(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d -exec basename {} \; | sort)

# Collect skill names from the ## Included Skills table (backtick-quoted entries in first column)
mapfile -t table_skills < <(awk '/^## Included Skills/{found=1; next} found && /^##/{exit} found{print}' "$CLAUDE_MD" |
	grep -oP '(?<=`)[a-z][a-z0-9-]+(?=`)' | sort)

for skill in "${folder_skills[@]}"; do
	if printf '%s\n' "${table_skills[@]}" | grep -qx "$skill"; then
		echo "OK    skill in table: $skill"
	else
		echo "FAIL  skill folder '$skill' missing from CLAUDE.md Included Skills table"
		errors=$((errors + 1))
	fi
done

for skill in "${table_skills[@]}"; do
	if printf '%s\n' "${folder_skills[@]}" | grep -qx "$skill"; then
		: # already checked above
	else
		echo "FAIL  table entry '$skill' has no matching skill folder"
		errors=$((errors + 1))
	fi
done

echo ""
[[ $errors -eq 0 ]] && echo "CLAUDE.md: all checks passed" || echo "CLAUDE.md: $errors error(s) found"

exit $((errors > 0))
