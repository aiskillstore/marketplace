#!/usr/bin/env bash
# GitHub Issue Helper Functions
# Bulk operations and utilities for issue management

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

error() {
    echo -e "${RED}Error: $1${NC}" >&2
    exit 1
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_gh_auth() {
    if ! gh auth status >/dev/null 2>&1; then
        error "Not authenticated with GitHub. Run: gh auth login"
    fi
}

triage_batch() {
    local filter="$1"

    check_gh_auth

    info "Finding issues matching: $filter"

    local issues
    issues=$(gh issue list --search "$filter" --json number,title,labels --limit 100)

    local count
    count=$(echo "$issues" | jq 'length')

    if [ "$count" -eq 0 ]; then
        warn "No issues found matching filter"
        return
    fi

    info "Processing $count issues..."

    local processed=0
    echo "$issues" | jq -c '.[]' | while read -r issue; do
        local number
        number=$(echo "$issue" | jq -r '.number')
        local title
        title=$(echo "$issue" | jq -r '.title')

        echo "Processing #$number: $title"

        # Simple classification based on title keywords
        local labels=""

        if echo "$title" | grep -iq "bug\|error\|fail\|broken\|crash"; then
            labels="bug"
        elif echo "$title" | grep -iq "feature\|add\|implement\|new"; then
            labels="feature"
        elif echo "$title" | grep -iq "doc\|readme\|guide"; then
            labels="docs"
        fi

        if [ -n "$labels" ]; then
            gh issue edit "$number" --add-label "$labels" 2>/dev/null && \
                echo "  → Added label: $labels"
        fi

        ((processed++)) || true
    done

    success "Processed $processed issues"
}

find_stale() {
    local days="${1:-90}"

    check_gh_auth

    info "Finding issues inactive for $days+ days..."

    local cutoff_date
    cutoff_date=$(date -d "$days days ago" +%Y-%m-%d 2>/dev/null || date -v-${days}d +%Y-%m-%d)

    gh issue list \
        --search "is:open updated:<$cutoff_date" \
        --json number,title,updatedAt \
        --limit 100 | \
    jq -r '.[] | "#\(.number): \(.title) (updated: \(.updatedAt[:10]))"'
}

close_duplicate() {
    local duplicate="$1"
    local original="$2"

    check_gh_auth

    info "Closing #$duplicate as duplicate of #$original"

    gh issue close "$duplicate" \
        --reason "not planned" \
        --comment "Duplicate of #$original"

    gh issue comment "$original" \
        --body "Duplicate report: #$duplicate"

    success "Closed #$duplicate as duplicate"
}

bulk_label() {
    local filter="$1"
    local label="$2"

    check_gh_auth

    info "Applying '$label' to issues matching: $filter"

    local issues
    issues=$(gh issue list --search "$filter" --json number --limit 100)

    local count
    count=$(echo "$issues" | jq 'length')

    if [ "$count" -eq 0 ]; then
        warn "No issues found"
        return
    fi

    info "Adding label to $count issues..."

    echo "$issues" | jq -r '.[].number' | while read -r number; do
        gh issue edit "$number" --add-label "$label" 2>/dev/null && \
            echo -n "."
    done

    echo ""
    success "Added '$label' to $count issues"
}

add_to_project() {
    local filter="$1"
    local project_number="$2"
    local owner="${3:-}"

    check_gh_auth

    if [ -z "$owner" ]; then
        owner=$(gh repo view --json owner -q '.owner.login')
    fi

    info "Adding issues to project #$project_number"

    gh issue list --search "$filter" --json url --limit 100 | \
    jq -r '.[].url' | while read -r url; do
        gh project item-add "$project_number" --owner "$owner" --url "$url" 2>/dev/null && \
            echo -n "."
    done

    echo ""
    success "Added issues to project"
}

generate_report() {
    check_gh_auth

    echo ""
    echo "========================================"
    echo "Issue Triage Report"
    echo "========================================"
    echo ""

    local total_open
    total_open=$(gh issue list --state open --json number --limit 5000 | jq 'length')

    local needs_triage
    needs_triage=$(gh issue list --label "needs-triage" --json number --limit 5000 | jq 'length')

    local high_priority
    high_priority=$(gh issue list --label "priority:high" --json number --limit 5000 | jq 'length')

    local bugs
    bugs=$(gh issue list --label "bug" --state open --json number --limit 5000 | jq 'length')

    local features
    features=$(gh issue list --label "feature" --state open --json number --limit 5000 | jq 'length')

    echo "Total open issues: $total_open"
    echo "Needs triage: $needs_triage"
    echo "High priority: $high_priority"
    echo "Bugs: $bugs"
    echo "Features: $features"
    echo ""
}

main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        triage-batch)
            triage_batch "$@"
            ;;
        find-stale)
            find_stale "$@"
            ;;
        close-duplicate)
            close_duplicate "$@"
            ;;
        bulk-label)
            bulk_label "$@"
            ;;
        add-to-project)
            add_to_project "$@"
            ;;
        report)
            generate_report
            ;;
        help|*)
            cat <<EOF
GitHub Issue Helper Script

Usage: $0 <command> [options]

Commands:
  triage-batch <filter>
      Batch triage issues matching filter
      Example: triage-batch "is:open no:label"

  find-stale [days]
      Find issues inactive for N days (default: 90)

  close-duplicate <duplicate-number> <original-number>
      Close issue as duplicate

  bulk-label <filter> <label>
      Add label to all matching issues
      Example: bulk-label "is:bug" "needs-triage"

  add-to-project <filter> <project-number> [owner]
      Add matching issues to project board

  report
      Generate triage status report

Examples:
  $0 triage-batch "is:open no:label"
  $0 find-stale 90
  $0 close-duplicate 42 38
  $0 bulk-label "is:bug is:open" "needs-triage"
  $0 report

EOF
            ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
