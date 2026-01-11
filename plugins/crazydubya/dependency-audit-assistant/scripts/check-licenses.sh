#!/bin/bash
# License Checker Script
# Extracts and categorizes licenses from project dependencies

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo "======================================="
    echo "$1"
    echo "======================================="
}

categorize_license() {
    local license="$1"

    case "$license" in
        MIT|ISC|BSD*|Apache-2.0|Unlicense|0BSD)
            echo "permissive"
            ;;
        LGPL*|MPL*|EPL*)
            echo "weak-copyleft"
            ;;
        GPL*|AGPL*)
            echo "strong-copyleft"
            ;;
        UNLICENSED|UNKNOWN|"")
            echo "unknown"
            ;;
        *)
            echo "other"
            ;;
    esac
}

check_npm_licenses() {
    print_header "NPM License Report"

    if ! command -v npx &> /dev/null; then
        echo "npx not found. Install Node.js first."
        return 1
    fi

    # Check if license-checker is available
    if ! npx license-checker --version &> /dev/null 2>&1; then
        echo "Installing license-checker..."
        npm install -g license-checker
    fi

    # Run license checker
    npx license-checker --json > /tmp/licenses.json

    echo ""
    echo "License Summary:"
    echo "----------------"

    # Count by license type
    jq -r 'to_entries[] | .value.licenses' /tmp/licenses.json | sort | uniq -c | sort -rn

    echo ""
    echo "${YELLOW}Packages with GPL/AGPL licenses:${NC}"
    jq -r 'to_entries[] | select(.value.licenses | contains("GPL")) | "\(.key): \(.value.licenses)"' /tmp/licenses.json

    echo ""
    echo "${RED}Packages with unknown licenses:${NC}"
    jq -r 'to_entries[] | select(.value.licenses == "UNKNOWN" or .value.licenses == "") | .key' /tmp/licenses.json

    rm /tmp/licenses.json
}

check_python_licenses() {
    print_header "Python License Report"

    if ! command -v pip &> /dev/null; then
        echo "pip not found. Install Python first."
        return 1
    fi

    # Install pip-licenses if not available
    if ! command -v pip-licenses &> /dev/null; then
        echo "Installing pip-licenses..."
        pip install pip-licenses
    fi

    pip-licenses --format=markdown --order=license

    echo ""
    echo "${YELLOW}GPL/AGPL Licenses:${NC}"
    pip-licenses --format=plain | grep -i "gpl" || echo "None found"

    echo ""
    echo "${RED}Unknown Licenses:${NC}"
    pip-licenses --format=plain | grep -i "unknown\|UNKNOWN" || echo "None found"
}

check_ruby_licenses() {
    print_header "Ruby License Report"

    if ! command -v bundle &> /dev/null; then
        echo "bundle not found. Install Bundler first."
        return 1
    fi

    # Use license_finder if available
    if command -v license_finder &> /dev/null; then
        license_finder report
    else
        echo "Consider installing license_finder: gem install license_finder"

        # Basic check using bundle
        bundle list | while read -r line; do
            gem_name=$(echo "$line" | awk '{print $2}')
            if [[ -n "$gem_name" ]]; then
                gem specification "$gem_name" license 2>/dev/null || echo "$gem_name: Unknown"
            fi
        done
    fi
}

check_go_licenses() {
    print_header "Go License Report"

    if ! command -v go &> /dev/null; then
        echo "go not found. Install Go first."
        return 1
    fi

    # Install go-licenses if not available
    if ! command -v go-licenses &> /dev/null; then
        echo "Installing go-licenses..."
        go install github.com/google/go-licenses@latest
    fi

    go-licenses report ./... 2>/dev/null | column -t

    echo ""
    echo "${YELLOW}GPL/AGPL Licenses:${NC}"
    go-licenses report ./... 2>/dev/null | grep -i "gpl" || echo "None found"
}

# Detect project type and run appropriate check
detect_and_check() {
    if [[ -f "package.json" ]]; then
        check_npm_licenses
    elif [[ -f "requirements.txt" ]] || [[ -f "setup.py" ]] || [[ -f "pyproject.toml" ]]; then
        check_python_licenses
    elif [[ -f "Gemfile" ]]; then
        check_ruby_licenses
    elif [[ -f "go.mod" ]]; then
        check_go_licenses
    else
        echo "No recognized package manager found."
        echo "Supported: npm, pip, bundler, go modules"
        return 1
    fi
}

main() {
    if [[ $# -eq 0 ]]; then
        detect_and_check
    else
        case "$1" in
            npm|node)
                check_npm_licenses
                ;;
            python|pip)
                check_python_licenses
                ;;
            ruby|bundle)
                check_ruby_licenses
                ;;
            go)
                check_go_licenses
                ;;
            *)
                echo "Unknown package manager: $1"
                echo "Supported: npm, python, ruby, go"
                return 1
                ;;
        esac
    fi
}

main "$@"
