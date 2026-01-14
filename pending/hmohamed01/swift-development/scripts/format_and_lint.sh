#!/bin/bash
# Format and lint Swift code
# Usage: format_and_lint.sh [path] [--fix] [--check]
#   --fix     Auto-fix issues (default)
#   --check   Check only, don't modify files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${GREEN}==>${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

echo_error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

PATH_TO_CHECK="${1:-.}"
MODE="fix"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --fix) MODE="fix" ;;
        --check) MODE="check" ;;
    esac
done

# Shift path argument if it's not a flag
[[ "$1" != --* ]] && shift

# Validate path exists
if [[ ! -e "$PATH_TO_CHECK" ]]; then
    echo_error "Path '$PATH_TO_CHECK' does not exist."
    exit 1
fi

HAS_ERRORS=0
TOOLS_FOUND=0

# SwiftFormat
if command -v swiftformat &> /dev/null; then
    TOOLS_FOUND=1
    echo_step "Running SwiftFormat..."
    if [[ "$MODE" == "check" ]]; then
        if ! swiftformat --lint "$PATH_TO_CHECK" 2>&1; then
            HAS_ERRORS=1
        fi
    else
        if ! swiftformat "$PATH_TO_CHECK" 2>&1; then
            echo_warning "SwiftFormat encountered errors"
            HAS_ERRORS=1
        fi
    fi
else
    echo_warning "SwiftFormat not found. Install with: brew install swiftformat"
fi

echo ""

# SwiftLint
if command -v swiftlint &> /dev/null; then
    TOOLS_FOUND=1
    echo_step "Running SwiftLint..."
    if [[ "$MODE" == "check" ]]; then
        if ! swiftlint lint --path "$PATH_TO_CHECK" --strict 2>&1; then
            HAS_ERRORS=1
        fi
    else
        if ! swiftlint --fix --path "$PATH_TO_CHECK" 2>&1; then
            echo_warning "SwiftLint auto-fix encountered errors"
        fi
        # Run lint after fix to show remaining issues
        if ! swiftlint lint --path "$PATH_TO_CHECK" 2>&1; then
            HAS_ERRORS=1
        fi
    fi
else
    echo_warning "SwiftLint not found. Install with: brew install swiftlint"
fi

echo ""

# Apple's swift-format (if available)
if command -v swift-format &> /dev/null; then
    TOOLS_FOUND=1
    echo_step "Running swift-format..."
    if [[ "$MODE" == "check" ]]; then
        if ! swift-format lint -r "$PATH_TO_CHECK" 2>&1; then
            HAS_ERRORS=1
        fi
    else
        if ! swift-format -i -r "$PATH_TO_CHECK" 2>&1; then
            echo_warning "swift-format encountered errors"
            HAS_ERRORS=1
        fi
    fi
fi

# Check if at least one tool was found
if [[ $TOOLS_FOUND -eq 0 ]]; then
    echo_error "No formatting/linting tools found."
    echo "         Install at least one:" >&2
    echo "           brew install swiftformat" >&2
    echo "           brew install swiftlint" >&2
    exit 1
fi

if [[ $HAS_ERRORS -eq 1 ]]; then
    echo ""
    if [[ "$MODE" == "check" ]]; then
        echo_error "Some issues were found. Run without --check to auto-correct."
    else
        echo_error "Some issues remain after auto-fix. Please review manually."
    fi
    exit 1
else
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  All checks passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
fi
