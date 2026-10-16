#!/bin/bash

# GRAVITAS Verification Script
# Runs the full verification chain for the current project
# Output: VERDICT: PASS or VERDICT: FAIL
#
# Usage: bash skills/gravitas/scripts/verify.sh
#        bash skills/gravitas/scripts/verify.sh --lang typescript
#        bash skills/gravitas/scripts/verify.sh --coverage

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
FAILURES=""

log_pass() { echo -e "${GREEN}✓${NC} $1"; PASS=$((PASS + 1)); }
log_fail() { echo -e "${RED}✗${NC} $1"; FAIL=$((FAIL + 1)); FAILURES="$FAILURES\n  - $1"; }
log_info() { echo -e "${BLUE}→${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# ============================================================
# Language Detection
# ============================================================

detect_language() {
  if [ -f "tsconfig.json" ] || [ -f "package.json" ]; then
    if grep -q "vitest\|jest\|mocha" package.json 2>/dev/null; then
      echo "typescript"
      return
    fi
  fi
  if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    echo "python"
    return
  fi
  if [ -f "Cargo.toml" ]; then
    echo "rust"
    return
  fi
  if [ -f "go.mod" ]; then
    echo "go"
    return
  fi
  if [ -f "pom.xml" ] || [ -f "build.gradle" ]; then
    echo "java"
    return
  fi
  if [ -f "*.csproj" ] || [ -f "*.sln" ]; then
    echo "csharp"
    return
  fi
  if [ -f "Gemfile" ]; then
    echo "ruby"
    return
  fi
  echo "unknown"
}

LANG="${1:-}"
if [ -z "$LANG" ]; then
  LANG=$(detect_language)
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         GRAVITAS VERIFICATION ENGINE          ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
log_info "Language: $LANG"
echo ""

# ============================================================
# TypeScript
# ============================================================

verify_typescript() {
  log_info "Running TypeScript verification chain..."
  echo ""

  # Type check
  log_info "Step 1/3: Type check (tsc --noEmit)"
  if output=$(tsc --noEmit 2>&1); then
    log_pass "Type check: clean"
  else
    log_fail "Type check FAILED"
    echo "$output" | head -20
  fi

  # Lint
  log_info "Step 2/3: Lint (eslint)"
  if [ -f ".eslintrc*" ] || [ -f "eslint.config*" ]; then
    if output=$(npx eslint . --max-warnings 0 2>&1); then
      log_pass "Lint: clean (0 warnings)"
    else
      log_fail "Lint FAILED"
      echo "$output" | head -20
    fi
  else
    log_warn "No ESLint config found — skipping lint"
  fi

  # Tests
  log_info "Step 3/3: Tests"
  if command -v vitest &>/dev/null || npx vitest --version &>/dev/null 2>&1; then
    if output=$(npx vitest run --reporter=verbose 2>&1); then
      # Extract test counts
      passed=$(echo "$output" | grep -E "Tests:.*passed" | tail -1)
      log_pass "Tests: $passed"
      echo "$output" | tail -10
    else
      log_fail "Tests FAILED"
      echo "$output" | tail -30
    fi
  elif [ -f "package.json" ] && grep -q '"jest"' package.json; then
    if output=$(npx jest --verbose 2>&1); then
      log_pass "Tests: $(echo "$output" | grep -E 'Tests:' | tail -1)"
    else
      log_fail "Tests FAILED"
      echo "$output" | tail -30
    fi
  else
    log_warn "No test runner found — skipping tests"
  fi
}

# ============================================================
# Python
# ============================================================

verify_python() {
  log_info "Running Python verification chain..."
  echo ""

  # Type check
  log_info "Step 1/3: Type check (mypy)"
  if command -v mypy &>/dev/null; then
    if output=$(mypy . 2>&1); then
      log_pass "Type check: clean"
    else
      log_fail "Type check FAILED"
      echo "$output" | head -20
    fi
  else
    log_warn "mypy not found — skipping type check"
  fi

  # Lint
  log_info "Step 2/3: Lint (ruff)"
  if command -v ruff &>/dev/null; then
    if output=$(ruff check . 2>&1); then
      log_pass "Lint: clean"
    else
      log_fail "Lint FAILED"
      echo "$output" | head -20
    fi
  elif command -v flake8 &>/dev/null; then
    if output=$(flake8 . 2>&1); then
      log_pass "Lint: clean"
    else
      log_fail "Lint FAILED"
      echo "$output" | head -20
    fi
  else
    log_warn "No linter found — skipping lint"
  fi

  # Tests
  log_info "Step 3/3: Tests (pytest)"
  if command -v pytest &>/dev/null; then
    if output=$(pytest -v --tb=short 2>&1); then
      passed=$(echo "$output" | grep -E "passed" | tail -1)
      log_pass "Tests: $passed"
    else
      log_fail "Tests FAILED"
      echo "$output" | tail -30
    fi
  else
    log_warn "pytest not found — skipping tests"
  fi
}

# ============================================================
# Rust
# ============================================================

verify_rust() {
  log_info "Running Rust verification chain..."
  echo ""

  log_info "Step 1/3: Type check (cargo check)"
  if output=$(cargo check 2>&1); then
    log_pass "Type check: clean"
  else
    log_fail "Type check FAILED"
    echo "$output" | head -20
  fi

  log_info "Step 2/3: Lint (cargo clippy)"
  if output=$(cargo clippy -- -D warnings 2>&1); then
    log_pass "Lint: clean"
  else
    log_fail "Lint FAILED"
    echo "$output" | head -20
  fi

  log_info "Step 3/3: Tests (cargo test)"
  if output=$(cargo test 2>&1); then
    passed=$(echo "$output" | grep -E "test result" | tail -1)
    log_pass "Tests: $passed"
  else
    log_fail "Tests FAILED"
    echo "$output" | tail -30
  fi
}

# ============================================================
# Go
# ============================================================

verify_go() {
  log_info "Running Go verification chain..."
  echo ""

  log_info "Step 1/3: Vet (go vet)"
  if output=$(go vet ./... 2>&1); then
    log_pass "Vet: clean"
  else
    log_fail "Vet FAILED"
    echo "$output" | head -20
  fi

  log_info "Step 2/3: Lint (staticcheck)"
  if command -v staticcheck &>/dev/null; then
    if output=$(staticcheck ./... 2>&1); then
      log_pass "Lint: clean"
    else
      log_fail "Lint FAILED"
      echo "$output" | head -20
    fi
  else
    log_warn "staticcheck not found — skipping (install: go install honnef.co/go/tools/cmd/staticcheck@latest)"
  fi

  log_info "Step 3/3: Tests (go test)"
  if output=$(go test ./... -v 2>&1); then
    passed=$(echo "$output" | grep -c "^--- PASS")
    failed=$(echo "$output" | grep -c "^--- FAIL")
    if [ "$failed" -eq 0 ]; then
      log_pass "Tests: $passed passed, $failed failed"
    else
      log_fail "Tests FAILED: $failed failures"
      echo "$output" | grep "^--- FAIL" | head -10
    fi
  else
    log_fail "Tests FAILED"
    echo "$output" | tail -20
  fi
}

# ============================================================
# Run detection
# ============================================================

case "$LANG" in
  typescript|ts) verify_typescript ;;
  python|py) verify_python ;;
  rust|rs) verify_rust ;;
  go) verify_go ;;
  *)
    log_warn "Language '$LANG' not auto-detected or supported yet."
    log_info "Supported: typescript, python, rust, go"
    log_info "Usage: bash verify.sh typescript"
    echo ""
    echo "VERDICT: UNKNOWN — language not identified"
    exit 1
    ;;
esac

# ============================================================
# Final Verdict
# ============================================================

echo ""
echo "════════════════════════════════════════════════"
echo ""
echo "Results: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}"
echo ""

if [ "$FAIL" -eq 0 ]; then
  echo -e "${GREEN}VERDICT: PASS${NC}"
  echo ""
  exit 0
else
  echo -e "${RED}VERDICT: FAIL${NC}"
  echo ""
  echo "Failed checks:"
  printf "%b\n" "$FAILURES"
  echo ""
  exit 1
fi
