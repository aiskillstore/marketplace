#!/usr/bin/env bash
# Issue Relationship Mapper
# Map dependencies and relationships between issues

set -euo pipefail

BLUE='\033[0;34m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

map_issue() {
    local issue_number="$1"

    echo -e "${BLUE}Mapping relationships for issue #$issue_number${NC}"
    echo ""

    # Get issue details
    local issue_data
    issue_data=$(gh issue view "$issue_number" --json title,body,labels)

    local title
    title=$(echo "$issue_data" | jq -r '.title')

    echo "Issue #$issue_number: $title"
    echo ""

    # Find mentioned issues in body
    local body
    body=$(echo "$issue_data" | jq -r '.body // ""')

    echo -e "${YELLOW}Related Issues:${NC}"
    echo "$body" | grep -oE '#[0-9]+' | sort -u | while read -r ref; do
        local ref_num
        ref_num=$(echo "$ref" | tr -d '#')
        if [ "$ref_num" != "$issue_number" ]; then
            local ref_title
            ref_title=$(gh issue view "$ref_num" --json title 2>/dev/null | jq -r '.title' || echo "Unknown")
            echo "  $ref: $ref_title"
        fi
    done

    echo ""

    # Check labels for relationships
    echo -e "${YELLOW}Labels:${NC}"
    echo "$issue_data" | jq -r '.labels[].name' | while read -r label; do
        echo "  - $label"
    done

    echo ""

    # Find blockers (issues this depends on)
    echo -e "${YELLOW}Potential Blockers:${NC}"
    if echo "$body" | grep -iq "depends on\|blocked by\|requires"; then
        echo "$body" | grep -iE "depends on|blocked by|requires" | head -5
    else
        echo "  None detected"
    fi

    echo ""

    # Find blocked issues (issues that depend on this)
    echo -e "${YELLOW}Issues Blocked by This:${NC}"
    gh issue list --search "is:open #$issue_number" --json number,title --limit 10 | \
        jq -r '.[] | "  #\(.number): \(.title)"'
}

find_blockers() {
    echo -e "${BLUE}Finding blocking issues...${NC}"
    echo ""

    # Search for issues with blocking keywords
    gh issue list \
        --search 'is:open "blocked by" OR "depends on" OR "requires"' \
        --json number,title,body \
        --limit 50 | \
    jq -r '.[] | "#\(.number): \(.title)"'
}

generate_graph() {
    local format="${1:-text}"

    echo -e "${BLUE}Generating dependency graph...${NC}"
    echo ""

    if [ "$format" = "dot" ]; then
        echo "digraph issues {"
        echo "  rankdir=LR;"

        # Get all open issues
        gh issue list --state open --json number,title,body --limit 100 | \
        jq -c '.[]' | while read -r issue; do
            local num
            num=$(echo "$issue" | jq -r '.number')
            local title
            title=$(echo "$issue" | jq -r '.title' | cut -c1-30)

            echo "  issue_$num [label=\"#$num: $title\"];"

            # Find dependencies
            local body
            body=$(echo "$issue" | jq -r '.body // ""')

            echo "$body" | grep -oE '#[0-9]+' | sort -u | while read -r ref; do
                local ref_num
                ref_num=$(echo "$ref" | tr -d '#')
                if [ "$ref_num" != "$num" ]; then
                    echo "  issue_$ref_num -> issue_$num;"
                fi
            done
        done

        echo "}"
    else
        # Text format
        gh issue list --state open --json number,title,body --limit 20 | \
        jq -r '.[] | "#\(.number): \(.title)"'
    fi
}

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        map-issue)
            map_issue "$@"
            ;;
        find-blockers)
            find_blockers
            ;;
        generate-graph)
            generate_graph "$@"
            ;;
        *)
            cat <<EOF
Issue Relationship Mapper

Usage: $0 <command> [options]

Commands:
  map-issue <issue-number>
      Map all relationships for an issue

  find-blockers
      Find all blocking issues

  generate-graph [format]
      Generate dependency graph (format: text|dot)

Examples:
  $0 map-issue 42
  $0 find-blockers
  $0 generate-graph dot > deps.dot

EOF
            ;;
    esac
}

main "$@"
