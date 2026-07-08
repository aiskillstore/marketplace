#!/usr/bin/env bash
# Quality Gates for PRs
# Run automated quality checks

set -euo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_ci() {
    local pr="$1"

    echo -e "${BLUE}Gate 1: CI/CD Status${NC}"

    local checks
    checks=$(gh pr checks "$pr" --json name,status,conclusion)

    local total
    total=$(echo "$checks" | jq 'length')
    local passed
    passed=$(echo "$checks" | jq '[.[] | select(.conclusion == "SUCCESS")] | length')

    if [ "$passed" -eq "$total" ]; then
        echo -e "${GREEN}✅ PASS${NC} - All checks passed ($passed/$total)"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - Some checks failed ($passed/$total)"
        echo "$checks" | jq -r '.[] | select(.conclusion != "SUCCESS") | "  - \(.name): \(.conclusion)"'
        return 1
    fi
}

check_coverage() {
    local pr="$1"

    echo -e "${BLUE}Gate 2: Test Coverage${NC}"

    # This would integrate with coverage tools
    # For now, check if tests exist in PR

    local files
    files=$(gh pr view "$pr" --json files -q '.files[].path')

    local has_tests=0
    while read -r file; do
        if [[ "$file" == *"test"* ]] || [[ "$file" == *"spec"* ]]; then
            has_tests=1
            break
        fi
    done <<< "$files"

    if [ "$has_tests" -eq 1 ]; then
        echo -e "${GREEN}✅ PASS${NC} - Tests included"
        return 0
    else
        echo -e "${YELLOW}⚠️  WARNING${NC} - No test files detected"
        return 1
    fi
}

check_security() {
    local pr="$1"

    echo -e "${BLUE}Gate 4: Security Scan${NC}"

    # Check for common security issues
    local files
    files=$(gh pr diff "$pr")

    local issues=0

    # Check for secrets
    if echo "$files" | grep -iqE '(password|secret|api[_-]?key|token).*(=|:)'; then
        echo -e "${RED}⚠️  Potential secret detected${NC}"
        ((issues++)) || true
    fi

    # Check for SQL injection patterns
    if echo "$files" | grep -iq 'execute.*+.*request\|query.*+.*params'; then
        echo -e "${YELLOW}⚠️  Potential SQL injection pattern${NC}"
        ((issues++)) || true
    fi

    if [ "$issues" -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} - No obvious security issues"
        return 0
    else
        echo -e "${YELLOW}⚠️  WARNING${NC} - $issues potential security issues"
        return 1
    fi
}

check_size() {
    local pr="$1"

    echo -e "${BLUE}Gate 6: PR Size${NC}"

    local additions
    additions=$(gh pr view "$pr" --json additions -q '.additions')
    local deletions
    deletions=$(gh pr view "$pr" --json deletions -q '.deletions')
    local total=$((additions + deletions))

    echo "  Changes: +$additions, -$deletions (total: $total LOC)"

    if [ "$total" -lt 400 ]; then
        echo -e "${GREEN}✅ PASS${NC} - Good size (< 400 LOC)"
        return 0
    elif [ "$total" -lt 800 ]; then
        echo -e "${YELLOW}⚠️  WARNING${NC} - Large PR (consider splitting)"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - Very large PR (>= 800 LOC, definitely split)"
        return 1
    fi
}

check_all() {
    local pr="$1"

    echo ""
    echo "========================================"
    echo "Quality Gates for PR #$pr"
    echo "========================================"
    echo ""

    local gates_passed=0
    local gates_total=4

    check_ci "$pr" && ((gates_passed++)) || true
    echo ""

    check_coverage "$pr" && ((gates_passed++)) || true
    echo ""

    check_security "$pr" && ((gates_passed++)) || true
    echo ""

    check_size "$pr" && ((gates_passed++)) || true
    echo ""

    echo "========================================"
    echo "Result: $gates_passed/$gates_total gates passed"
    echo "========================================"

    if [ "$gates_passed" -eq "$gates_total" ]; then
        echo -e "${GREEN}✅ ALL GATES PASSED${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  SOME GATES FAILED${NC}"
        return 1
    fi
}

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        check-all)
            check_all "$@"
            ;;
        check-ci)
            check_ci "$@"
            ;;
        check-coverage)
            check_coverage "$@"
            ;;
        check-security)
            check_security "$@"
            ;;
        check-size)
            check_size "$@"
            ;;
        *)
            cat <<EOF
Quality Gates Script

Usage: $0 <command> --pr <pr-number>

Commands:
  check-all --pr <number>
      Run all quality gates

  check-ci --pr <number>
      Check CI/CD status

  check-coverage --pr <number>
      Check test coverage

  check-security --pr <number>
      Run security scan

  check-size --pr <number>
      Check PR size

Examples:
  $0 check-all --pr 123
  $0 check-ci --pr 123

EOF
            ;;
    esac
}

main "$@"
