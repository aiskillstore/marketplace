#!/usr/bin/env bash
# Duplicate Issue Detection
# Find duplicate issues using similarity scoring

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

find_duplicates() {
    local issue_number="$1"

    echo -e "${YELLOW}Finding duplicates for issue #$issue_number...${NC}"

    # Get target issue
    local target
    target=$(gh issue view "$issue_number" --json title,body)
    local title
    title=$(echo "$target" | jq -r '.title')
    local body
    body=$(echo "$target" | jq -r '.body // ""')

    echo "Target: $title"
    echo ""

    # Extract keywords
    local keywords
    keywords=$(echo "$title $body" | tr '[:upper:]' '[:lower:]' | grep -oE '\w{4,}' | sort -u | head -20)

    # Search for similar issues
    local search_terms
    search_terms=$(echo "$keywords" | head -5 | tr '\n' ' ')

    echo "Searching for: $search_terms"
    echo ""

    gh issue list \
        --search "is:issue $search_terms -#$issue_number" \
        --json number,title,state,createdAt \
        --limit 10 | \
    jq -r '.[] | "  #\(.number): \(.title) (\(.state), \(.createdAt[:10]))"'
}

scan_all() {
    echo -e "${YELLOW}Scanning for duplicates...${NC}"

    # Get all open issues
    local issues
    issues=$(gh issue list --state open --json number,title --limit 200)

    local count
    count=$(echo "$issues" | jq 'length')

    echo "Scanning $count issues..."
    echo ""

    # Simple duplicate detection based on title similarity
    echo "$issues" | jq -r '.[] | [.number, .title] | @tsv' | \
    while IFS=$'\t' read -r num title; do
        # Search for similar titles
        local similar
        similar=$(gh issue list --search "is:open \"$title\"" --json number --limit 5 | jq 'length')

        if [ "$similar" -gt 1 ]; then
            echo -e "${YELLOW}Potential duplicates for #$num:${NC}"
            gh issue list --search "is:open \"$title\"" --json number,title --limit 5 | \
                jq -r '.[] | "  #\(.number): \(.title)"'
            echo ""
        fi
    done
}

compare() {
    local issue1="$1"
    local issue2="$2"

    echo -e "${YELLOW}Comparing issues #$issue1 and #$issue2${NC}"
    echo ""

    local data1
    data1=$(gh issue view "$issue1" --json title,body)
    local data2
    data2=$(gh issue view "$issue2" --json title,body)

    echo "Issue #$issue1:"
    echo "$data1" | jq -r '.title'
    echo ""

    echo "Issue #$issue2:"
    echo "$data2" | jq -r '.title'
    echo ""

    # Simple comparison
    local title1
    title1=$(echo "$data1" | jq -r '.title' | tr '[:upper:]' '[:lower:]')
    local title2
    title2=$(echo "$data2" | jq -r '.title' | tr '[:upper:]' '[:lower:]')

    if [ "$title1" = "$title2" ]; then
        echo -e "${RED}⚠️  Titles are identical - likely duplicate${NC}"
    else
        echo -e "${GREEN}Titles differ - likely not duplicate${NC}"
    fi
}

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        find-duplicates)
            find_duplicates "$@"
            ;;
        scan-all)
            scan_all
            ;;
        compare)
            compare "$@"
            ;;
        *)
            cat <<EOF
Duplicate Detection Script

Usage: $0 <command> [options]

Commands:
  find-duplicates <issue-number>
      Find potential duplicates for an issue

  scan-all
      Scan all open issues for duplicates

  compare <issue1> <issue2>
      Compare two issues for similarity

Examples:
  $0 find-duplicates 42
  $0 scan-all
  $0 compare 42 38

EOF
            ;;
    esac
}

main "$@"
