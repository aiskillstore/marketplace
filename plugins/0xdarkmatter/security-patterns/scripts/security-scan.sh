#!/bin/bash
# Quick security scan using grep patterns
# Usage: ./security-scan.sh [directory]

set -e

DIR="${1:-.}"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== Security Scan: $DIR ==="
echo ""

ISSUES=0

check_pattern() {
    local name="$1"
    local pattern="$2"
    local type="$3"

    echo -n "Checking: $name... "

    if rg -l "$pattern" "$DIR" --type "$type" 2>/dev/null | head -5 | grep -q .; then
        echo -e "${RED}FOUND${NC}"
        rg -n "$pattern" "$DIR" --type "$type" 2>/dev/null | head -10
        echo ""
        ISSUES=$((ISSUES + 1))
    else
        echo -e "${GREEN}OK${NC}"
    fi
}

# Python checks
echo "--- Python Security Checks ---"
check_pattern "Hardcoded secrets" "(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}['\"]" "py"
check_pattern "SQL injection (f-strings)" "execute\(f['\"]" "py"
check_pattern "SQL injection (format)" "execute\(.*\.format\(" "py"
check_pattern "eval() usage" "\beval\s*\(" "py"
check_pattern "exec() usage" "\bexec\s*\(" "py"
check_pattern "pickle.loads" "pickle\.loads?\(" "py"
check_pattern "os.system" "os\.system\(" "py"
check_pattern "shell=True" "subprocess.*shell\s*=\s*True" "py"
check_pattern "MD5 hashing" "hashlib\.md5\(" "py"
check_pattern "SHA1 hashing" "hashlib\.sha1\(" "py"

echo ""

# JavaScript checks
echo "--- JavaScript Security Checks ---"
check_pattern "innerHTML" "\.innerHTML\s*=" "js"
check_pattern "eval() usage" "\beval\s*\(" "js"
check_pattern "document.write" "document\.write\(" "js"

echo ""

# General checks
echo "--- General Security Checks ---"

echo -n "Checking: .env files in git... "
if git ls-files | grep -E "\.env$|\.env\." | grep -q .; then
    echo -e "${RED}FOUND${NC}"
    git ls-files | grep -E "\.env$|\.env\."
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}OK${NC}"
fi

echo -n "Checking: TODO/FIXME security items... "
if rg -i "TODO.*security|FIXME.*security|HACK.*security" "$DIR" 2>/dev/null | head -5 | grep -q .; then
    echo -e "${YELLOW}FOUND${NC}"
    rg -i "TODO.*security|FIXME.*security|HACK.*security" "$DIR" 2>/dev/null | head -10
    ISSUES=$((ISSUES + 1))
else
    echo -e "${GREEN}OK${NC}"
fi

echo ""
echo "=== Summary ==="
if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}No issues found!${NC}"
    exit 0
else
    echo -e "${RED}Found $ISSUES potential security issues${NC}"
    echo "Review the findings above and address any real vulnerabilities."
    exit 1
fi
