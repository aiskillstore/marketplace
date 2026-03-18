#!/usr/bin/env bash
# validate_skill.sh — Validates a SKILL.md against the Agent Skills specification
# Usage:
#   validate_skill.sh <skill-directory>       # validate one skill
#   validate_skill.sh --all <skills-dir>      # validate all skills in directory
#   validate_skill.sh --help                  # show usage

set -euo pipefail

ERRORS=0
WARNINGS=0
TOTAL_ERRORS=0
TOTAL_WARNINGS=0

usage() {
  cat <<EOF
Usage: validate_skill.sh [--all] <path>

  validate_skill.sh my-skill/            Validate a single skill directory
  validate_skill.sh --all .agent-skills/ Validate all skill directories

Checks performed:
  - Required frontmatter fields: name, description
  - name format: lowercase, no consecutive hyphens, matches directory name
  - description length: 1-1024 characters
  - description phrasing: warns if missing imperative trigger language
  - allowed-tools format: space-delimited (not YAML list)
  - Recommended sections: When to use, Instructions, Examples, Best practices, References
  - File length: warns if over 500 lines

Exit codes:
  0 = no errors (warnings may exist)
  1 = one or more errors found
EOF
}

check() {
  local status="$1" msg="$2"
  if [[ "$status" == "ok" ]]; then
    echo "  ✓ $msg"
  elif [[ "$status" == "warn" ]]; then
    echo "  ⚠ $msg"
    ((WARNINGS++)) || true
  else
    echo "  ✗ $msg"
    ((ERRORS++)) || true
  fi
}

extract_fm_field() {
  local content="$1" field="$2"
  # Handle both single-line and block scalar (>) values
  # Use || true to prevent set -e from triggering when grep finds no match
  echo "$content" | grep -E "^${field}:" | head -1 | sed "s/^${field}: *//" | tr -d '"' | sed 's/^>//' || true
}

validate_skill() {
  local skill_dir="$1"
  local skill_md="${skill_dir%/}/SKILL.md"
  ERRORS=0
  WARNINGS=0

  if [[ ! -f "$skill_md" ]]; then
    echo "✗ No SKILL.md found in $skill_dir"
    TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    return
  fi

  echo "Validating: $skill_md"

  # Extract frontmatter block
  local in_fm=0 fm_content="" body_started=0 line_count=0
  while IFS= read -r line; do
    ((line_count++)) || true
    if [[ "$line" == "---" && $in_fm -eq 0 && $body_started -eq 0 ]]; then
      in_fm=1
    elif [[ "$line" == "---" && $in_fm -eq 1 ]]; then
      in_fm=0
      body_started=1
    elif [[ $in_fm -eq 1 ]]; then
      fm_content+="$line"$'\n'
    fi
  done < "$skill_md"

  if [[ -z "$fm_content" ]]; then
    check "error" "No YAML frontmatter found (expected --- ... --- block)"
    echo ""
    echo "  Issues: ${ERRORS} errors, ${WARNINGS} warnings"
    TOTAL_ERRORS=$((TOTAL_ERRORS + ERRORS))
    TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNINGS))
    return
  fi

  # --- Check: name field ---
  local name
  name=$(extract_fm_field "$fm_content" "name") || true
  if [[ -n "$name" ]]; then
    check "ok" "Required field: name = '$name'"
    # Format check: lowercase, alphanumeric + hyphens
    if echo "$name" | grep -qE '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'; then
      if echo "$name" | grep -q -- '--'; then
        check "error" "Name contains consecutive hyphens: '$name'"
      else
        check "ok" "Name format: valid (lowercase alphanumeric + hyphens)"
      fi
    else
      check "error" "Name format: invalid characters or leading/trailing hyphen: '$name'"
    fi
    # Length check
    if [[ ${#name} -gt 64 ]]; then
      check "error" "Name length: ${#name} chars (max 64)"
    fi
    # Directory name match
    local dir_name
    dir_name=$(basename "${skill_dir%/}")
    if [[ "$name" == "$dir_name" ]]; then
      check "ok" "Name matches directory: '$name'"
    else
      check "warn" "Name/directory mismatch: name='$name' vs dir='$dir_name'"
    fi
  else
    check "error" "Required field 'name' is missing"
  fi

  # --- Check: description field ---
  local desc
  desc=$(extract_fm_field "$fm_content" "description") || true
  # For block scalars, also collect continuation lines
  if [[ -z "$desc" ]] || [[ "$desc" == ">" ]] || [[ "$desc" == "|" ]]; then
    # Try to get multi-line description
    desc=$(awk '/^description:/{found=1; next} found && /^  /{printf "%s ", $0; next} found{exit}' "$skill_md" | xargs)
  fi

  if [[ -n "$desc" ]]; then
    check "ok" "Required field: description present"
    local desc_len=${#desc}
    if [[ $desc_len -gt 1024 ]]; then
      check "error" "Description length: ${desc_len} chars (max 1024)"
    elif [[ $desc_len -lt 20 ]]; then
      check "warn" "Description seems too short (${desc_len} chars): '$desc'"
    else
      check "ok" "Description length: ${desc_len} chars (OK)"
    fi
    # Phrasing check
    if echo "$desc" | grep -qiE "(use when|use this skill when|triggers on|use for)"; then
      check "ok" "Description has imperative trigger phrasing"
    else
      check "warn" "Description may lack imperative phrasing — consider adding 'Use when...' or 'Triggers on:'"
    fi
  else
    check "error" "Required field 'description' is missing or empty"
  fi

  # --- Check: allowed-tools format ---
  local tools_line
  tools_line=$(echo "$fm_content" | grep -E "^allowed-tools:" | head -1 || true)
  if [[ -n "$tools_line" ]]; then
    local tools_val
    tools_val=$(echo "$tools_line" | sed 's/^allowed-tools: *//')
    if echo "$tools_val" | grep -qE '^\['; then
      check "warn" "allowed-tools uses YAML list syntax — spec requires space-delimited string"
    else
      check "ok" "allowed-tools format: space-delimited (OK)"
    fi
  fi

  # --- Check: compatibility field length ---
  local compat
  compat=$(extract_fm_field "$fm_content" "compatibility") || true
  if [[ -n "$compat" && ${#compat} -gt 500 ]]; then
    check "warn" "compatibility field: ${#compat} chars (max 500)"
  fi

  # --- Check: recommended sections ---
  for section in "When to use this skill" "Instructions" "Examples" "Best practices" "References"; do
    if grep -q "^## ${section}" "$skill_md"; then
      check "ok" "Recommended section: $section"
    else
      check "warn" "Missing recommended section: ## ${section}"
    fi
  done

  # --- Check: file length ---
  if [[ $line_count -gt 500 ]]; then
    check "warn" "File length: ${line_count} lines (recommended max: 500 — move details to references/)"
  else
    check "ok" "File length: ${line_count} lines (OK)"
  fi

  echo ""
  echo "  Issues: ${ERRORS} errors, ${WARNINGS} warnings"
  echo ""

  TOTAL_ERRORS=$((TOTAL_ERRORS + ERRORS))
  TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNINGS))
}

main() {
  if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    usage
    exit 0
  fi

  if [[ "${1:-}" == "--all" ]]; then
    local skills_dir="${2:-.}"
    local found=0
    for dir in "${skills_dir%/}"/*/; do
      if [[ -f "${dir}SKILL.md" ]]; then
        found=1
        validate_skill "$dir"
      fi
    done
    if [[ $found -eq 0 ]]; then
      echo "No skill directories (containing SKILL.md) found in: $skills_dir"
      exit 1
    fi
    echo "========================================"
    echo "Total: ${TOTAL_ERRORS} errors, ${TOTAL_WARNINGS} warnings"
    [[ $TOTAL_ERRORS -eq 0 ]] && exit 0 || exit 1
  else
    local skill_dir="${1:-.}"
    validate_skill "$skill_dir"
    [[ $TOTAL_ERRORS -eq 0 ]] && exit 0 || exit 1
  fi
}

main "$@"
