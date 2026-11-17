#!/bin/sh

set -eu

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/anyviz-install-test.XXXXXX")"
TEST_HOME="$TEST_ROOT/home"

cleanup() {
  rm -rf "$TEST_ROOT"
}

trap cleanup EXIT HUP INT TERM

mkdir -p \
  "$TEST_HOME/.claude/skills/anyviz" \
  "$TEST_HOME/.hermes" \
  "$TEST_HOME/.gemini" \
  "$TEST_HOME/.config/goose"
printf '%s\n' 'keep me' > "$TEST_HOME/.claude/skills/anyviz/custom.txt"

run_installer() {
  ANYVIZ_HOME="$TEST_HOME" \
  ANYVIZ_SOURCE_DIR="$PROJECT_ROOT" \
  ANYVIZ_DETECT_COMMANDS=0 \
    sh "$PROJECT_ROOT/install.sh" >/dev/null
}

assert_installed() {
  TARGET="$1"
  [ -f "$TARGET/SKILL.md" ]
  [ -f "$TARGET/guides/chart-selection.md" ]
  [ -f "$TARGET/templates/charts/bar-chart.md" ]
  [ -f "$TARGET/.anyviz-source" ]
}

run_installer

assert_installed "$TEST_HOME/.agents/skills/anyviz"
assert_installed "$TEST_HOME/.claude/skills/anyviz"
assert_installed "$TEST_HOME/.hermes/skills/anyviz"
assert_installed "$TEST_HOME/.gemini/skills/anyviz"
assert_installed "$TEST_HOME/.config/goose/skills/anyviz"
[ -f "$(find "$TEST_HOME/.claude/skills" -path '*/anyviz.backup-*/custom.txt' -print -quit)" ]

printf 'stale\n' > "$TEST_HOME/.agents/skills/anyviz/stale.txt"
run_installer

[ ! -e "$TEST_HOME/.agents/skills/anyviz/stale.txt" ]
[ -z "$(find "$TEST_HOME" -name '.anyviz-install-*' -o -name '.anyviz-backup-*')" ]

printf '%s\n' 'anyviz installer verified'
