#!/bin/bash
# Coverage Parser Script
# Extracts coverage metrics from common coverage report formats

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo "======================================="
    echo "$1"
    echo "======================================="
}

# Parse Jest coverage-summary.json
parse_jest_coverage() {
    local coverage_file="$1"

    if [[ ! -f "$coverage_file" ]]; then
        echo "Coverage file not found: $coverage_file"
        return 1
    fi

    print_header "Jest Coverage Summary"

    # Extract overall coverage
    echo "Overall Coverage:"
    jq -r '.total | to_entries[] | "\(.key): \(.value.pct)%"' "$coverage_file"

    echo ""
    echo "Files with low coverage (<80%):"
    jq -r 'to_entries[] | select(.key != "total") | select(.value.lines.pct < 80) | "\(.key): \(.value.lines.pct)%"' "$coverage_file" | sort -t: -k2 -n
}

# Parse lcov.info
parse_lcov() {
    local lcov_file="$1"

    if [[ ! -f "$lcov_file" ]]; then
        echo "LCOV file not found: $lcov_file"
        return 1
    fi

    print_header "LCOV Coverage Report"

    # Use lcov tools if available
    if command -v lcov &> /dev/null; then
        lcov --summary "$lcov_file" 2>&1 | grep -E "(lines|functions|branches)"
    else
        # Manual parsing
        echo "Total lines found:"
        grep -c "^DA:" "$lcov_file" || echo "0"

        echo "Total lines hit:"
        grep "^DA:" "$lcov_file" | grep -v ",0$" | wc -l || echo "0"
    fi
}

# Parse Python coverage report
parse_python_coverage() {
    if command -v coverage &> /dev/null; then
        print_header "Python Coverage Report"
        coverage report --show-missing
    else
        echo "coverage tool not found. Install with: pip install coverage"
        return 1
    fi
}

# Parse Go coverage
parse_go_coverage() {
    local coverage_file="${1:-coverage.out}"

    if [[ ! -f "$coverage_file" ]]; then
        echo "Go coverage file not found: $coverage_file"
        return 1
    fi

    print_header "Go Coverage Report"

    if command -v go &> /dev/null; then
        go tool cover -func="$coverage_file" | tail -n 1
        echo ""
        echo "Functions with low coverage:"
        go tool cover -func="$coverage_file" | awk '$NF < 80.0 && NR > 1 { print $0 }' | sort -k3 -n
    fi
}

# Detect and parse coverage format
detect_and_parse() {
    if [[ -f "coverage/coverage-summary.json" ]]; then
        parse_jest_coverage "coverage/coverage-summary.json"
    elif [[ -f "coverage/lcov.info" ]]; then
        parse_lcov "coverage/lcov.info"
    elif [[ -f ".coverage" ]]; then
        parse_python_coverage
    elif [[ -f "coverage.out" ]]; then
        parse_go_coverage "coverage.out"
    else
        echo "No coverage report found."
        echo "Searched for:"
        echo "  - coverage/coverage-summary.json (Jest)"
        echo "  - coverage/lcov.info (LCOV)"
        echo "  - .coverage (Python)"
        echo "  - coverage.out (Go)"
        return 1
    fi
}

# Main execution
main() {
    if [[ $# -eq 0 ]]; then
        # Auto-detect
        detect_and_parse
    else
        # Parse specific file
        local file="$1"
        case "$file" in
            *.json)
                parse_jest_coverage "$file"
                ;;
            lcov.info)
                parse_lcov "$file"
                ;;
            .coverage)
                parse_python_coverage
                ;;
            coverage.out)
                parse_go_coverage "$file"
                ;;
            *)
                echo "Unknown coverage format: $file"
                return 1
                ;;
        esac
    fi
}

main "$@"
