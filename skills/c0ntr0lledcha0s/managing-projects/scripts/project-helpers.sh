#!/usr/bin/env bash
# GitHub Projects v2 Helper Functions
# Provides wrapper functions for common project operations

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Error handling
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

# Execute command with retry logic
execute_with_retry() {
    local max_attempts="${MAX_RETRIES:-3}"
    local attempt=1
    local delay=2
    local command="$@"

    while [ $attempt -le $max_attempts ]; do
        if eval "$command"; then
            return 0
        fi

        if [ $attempt -lt $max_attempts ]; then
            warn "Attempt $attempt/$max_attempts failed, retrying in ${delay}s..."
            sleep $delay
            ((attempt++))
            delay=$((delay * 2))  # Exponential backoff
        else
            error "Command failed after $max_attempts attempts"
            return 1
        fi
    done
}

# Validate prerequisites with helpful messages
validate_prerequisites() {
    local errors=()

    # Check gh CLI
    if ! command -v gh >/dev/null 2>&1; then
        errors+=("GitHub CLI (gh) not installed. Install from: https://github.com/cli/cli#installation")
    elif ! gh auth status >/dev/null 2>&1; then
        errors+=("GitHub CLI not authenticated. Run: gh auth login")
    fi

    # Check jq if available
    if ! command -v jq >/dev/null 2>&1; then
        warn "jq not installed. Some features may not work. Install from: https://stedolan.github.io/jq/download/"
    fi

    # Report errors
    if [ ${#errors[@]} -gt 0 ]; then
        error "Prerequisites check failed:"
        for err in "${errors[@]}"; do
            echo "  - $err" >&2
        done
        return 1
    fi

    return 0
}

# Check prerequisites and ensure gh CLI is installed
ensure_gh_cli() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../../.. && pwd)"
    local ensure_gh_script="$script_dir/scripts/ensure-gh-cli.sh"
    local ensure_deps_script="$script_dir/scripts/ensure-dependencies.sh"

    # First, ensure dependencies (jq, python3, etc.)
    if [ -f "$ensure_deps_script" ]; then
        if ! bash "$ensure_deps_script" true false >/dev/null 2>&1; then
            warn "Some dependencies may be missing (jq, python3)"
        fi
    fi

    # Then, ensure gh CLI
    if [ -f "$ensure_gh_script" ]; then
        # Try to ensure gh is installed and authenticated
        if bash "$ensure_gh_script" true false; then
            return 0
        else
            error "GitHub CLI setup failed"
            return 1
        fi
    else
        # Fallback to simple check
        if ! command -v gh >/dev/null 2>&1; then
            error "GitHub CLI (gh) is not installed"
            echo "Install it from: https://github.com/cli/cli#installation" >&2
            return 1
        fi

        if ! gh auth status >/dev/null 2>&1; then
            error "Not authenticated with GitHub. Run: gh auth login"
            return 1
        fi
    fi
}

# Get organization from current repository
get_org() {
    gh repo view --json owner -q '.owner.login' 2>/dev/null || echo ""
}

# Create project with template
create_project() {
    local title="$1"
    local template="${2:-}"
    local owner="${3:-$(get_org)}"

    ensure_gh_cli || return 1

    if [[ -z "$owner" ]]; then
        error "Could not determine organization. Specify with --owner"
    fi

    echo "Creating project '$title' for $owner..."

    local project_id
    project_id=$(gh project create \
        --owner "$owner" \
        --title "$title" \
        --format json | jq -r '.id')

    if [[ -z "$project_id" ]]; then
        error "Failed to create project"
    fi

    success "Project created: $project_id"

    # Apply template if specified
    if [[ -n "$template" ]]; then
        apply_template "$project_id" "$template" "$owner"
    fi

    echo "$project_id"
}

# Apply board template
apply_template() {
    local project_id="$1"
    local template="$2"
    local owner="$3"

    case "$template" in
        sprint)
            echo "Applying sprint template..."
            create_sprint_fields "$project_id" "$owner"
            ;;
        kanban)
            echo "Applying kanban template..."
            create_kanban_fields "$project_id" "$owner"
            ;;
        roadmap)
            echo "Applying roadmap template..."
            create_roadmap_fields "$project_id" "$owner"
            ;;
        *)
            warn "Unknown template: $template"
            ;;
    esac
}

# Create sprint board fields
create_sprint_fields() {
    local project_id="$1"
    local owner="$2"

    echo "Creating custom fields..."

    # Status field (SingleSelect)
    create_single_select_field "$project_id" "$owner" "Status" \
        "Backlog,Sprint,In Progress,Review,Done"

    # Priority field
    create_single_select_field "$project_id" "$owner" "Priority" \
        "High,Medium,Low"

    # Story Points field
    create_single_select_field "$project_id" "$owner" "Story Points" \
        "1,2,3,5,8,13"

    success "Sprint fields created"
}

# Create kanban board fields
create_kanban_fields() {
    local project_id="$1"
    local owner="$2"

    # Status field
    create_single_select_field "$project_id" "$owner" "Status" \
        "Todo,In Progress,Review,Done"

    # Priority field
    create_single_select_field "$project_id" "$owner" "Priority" \
        "High,Medium,Low"

    # Size field
    create_single_select_field "$project_id" "$owner" "Size" \
        "XS,S,M,L,XL"

    success "Kanban fields created"
}

# Create roadmap board fields
create_roadmap_fields() {
    local project_id="$1"
    local owner="$2"

    # Status field
    create_single_select_field "$project_id" "$owner" "Status" \
        "Planning,In Progress,Completed,On Hold"

    # Quarter field
    create_single_select_field "$project_id" "$owner" "Quarter" \
        "Q1 2024,Q2 2024,Q3 2024,Q4 2024"

    success "Roadmap fields created"
}

# Helper to create SingleSelect field via GraphQL
create_single_select_field() {
    local project_id="$1"
    local owner="$2"
    local field_name="$3"
    local options="$4"

    echo "Creating field: $field_name"

    # Convert comma-separated options to JSON array for GraphQL
    local options_json
    options_json=$(echo "$options" | jq -R 'split(",") | map({name: ., color: "GRAY"})')

    local mutation
    mutation=$(cat <<'EOF'
mutation($projectId: ID!, $fieldName: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
  createProjectV2Field(input: {
    projectId: $projectId
    dataType: SINGLE_SELECT
    name: $fieldName
    singleSelectOptions: $options
  }) {
    projectV2Field {
      ... on ProjectV2SingleSelectField {
        id
        name
      }
    }
  }
}
EOF
)

    local result
    result=$(gh api graphql -f query="$mutation" \
        -f projectId="$project_id" \
        -f fieldName="$field_name" \
        --input - <<< "{\"options\": $options_json}" 2>&1)

    if echo "$result" | jq -e '.data.createProjectV2Field.projectV2Field.id' >/dev/null 2>&1; then
        success "Created field: $field_name"
        return 0
    else
        warn "Failed to create field $field_name: $(echo "$result" | jq -r '.errors[0].message // "unknown error"')"
        return 1
    fi
}

# Bulk add items to project
bulk_add_items() {
    local project_number="$1"
    local filter="$2"
    local owner="${3:-$(get_org)}"

    ensure_gh_cli || return 1

    echo "Searching for items: $filter"

    # Search for issues matching filter
    local issues
    issues=$(gh issue list --search "$filter" --json number,url --limit 1000)

    local count=0
    echo "$issues" | jq -r '.[] | .url' | while read -r url; do
        if gh project item-add "$project_number" --owner "$owner" --url "$url" >/dev/null 2>&1; then
            ((count++)) || true
            echo -n "."
        fi
    done
    echo ""

    success "Added items to project"
}

# Update item status
update_item_status() {
    local project_id="$1"
    local item_id="$2"
    local status="$3"
    local owner="${4:-$(get_org)}"

    echo "Updating item $item_id to status: $status"

    # Get graphql-queries.sh location
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local graphql_script="$script_dir/graphql-queries.sh"

    if [[ ! -f "$graphql_script" ]]; then
        error "graphql-queries.sh not found at $graphql_script"
    fi

    # First, get the Status field ID and option ID
    local project_number
    project_number=$(gh project list --owner "$owner" --format json | \
        jq -r --arg id "$project_id" '.projects[] | select(.id == $id) | .number')

    if [[ -z "$project_number" ]]; then
        error "Could not find project number for ID: $project_id"
    fi

    # Get field options
    local field_info
    field_info=$(bash "$graphql_script" get_options "$owner" "$project_number" "Status" 2>/dev/null)

    local option_id
    option_id=$(echo "$field_info" | grep -i "$status" | awk '{print $1}')

    if [[ -z "$option_id" ]]; then
        error "Could not find option ID for status: $status"
    fi

    # Get Status field ID
    local field_id
    field_id=$(bash "$graphql_script" list_fields "$owner" "$project_number" 2>/dev/null | \
        grep -i "Status" | awk '{print $1}')

    if [[ -z "$field_id" ]]; then
        error "Could not find Status field ID"
    fi

    # Update the field
    if bash "$graphql_script" update_field_select "$project_id" "$item_id" "$field_id" "$option_id"; then
        success "Updated item status to: $status"
    else
        error "Failed to update item status"
    fi
}

# Archive completed items
archive_done_items() {
    local project_number="$1"
    local owner="${2:-$(get_org)}"
    local days_old="${3:-14}"

    echo "Archiving items older than $days_old days in Done status..."

    ensure_gh_cli || return 1

    # Get graphql-queries.sh location
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local graphql_script="$script_dir/graphql-queries.sh"

    # Get project ID
    local project_id
    project_id=$(bash "$graphql_script" get_project_id "$owner" "$project_number" 2>/dev/null)

    if [[ -z "$project_id" || "$project_id" == "null" ]]; then
        error "Could not get project ID for project #$project_number"
    fi

    # Query for done items with their updated dates
    local query
    query=$(cat <<'EOF'
query($projectId: ID!) {
  node(id: $projectId) {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          updatedAt
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2SingleSelectField { name } }
              }
            }
          }
        }
      }
    }
  }
}
EOF
)

    local result
    result=$(gh api graphql -f query="$query" -f projectId="$project_id" 2>/dev/null)

    # Filter for Done items older than N days
    local cutoff_date
    cutoff_date=$(date -d "-$days_old days" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || \
                  date -v-${days_old}d +%Y-%m-%dT%H:%M:%SZ)

    local items_to_archive
    items_to_archive=$(echo "$result" | jq -r --arg cutoff "$cutoff_date" '
        .data.node.items.nodes[] |
        select(
            .updatedAt < $cutoff and
            (.fieldValues.nodes[] | select(.field.name == "Status" and .name == "Done"))
        ) | .id
    ')

    if [[ -z "$items_to_archive" ]]; then
        echo "No items to archive"
        return 0
    fi

    local archive_count=0
    while IFS= read -r item_id; do
        [[ -z "$item_id" ]] && continue

        local archive_mutation
        archive_mutation=$(cat <<'EOF'
mutation($projectId: ID!, $itemId: ID!) {
  archiveProjectV2Item(input: {
    projectId: $projectId
    itemId: $itemId
  }) {
    item { id }
  }
}
EOF
)

        if gh api graphql -f query="$archive_mutation" \
            -f projectId="$project_id" \
            -f itemId="$item_id" >/dev/null 2>&1; then
            ((archive_count++))
            echo -n "."
        fi
    done <<< "$items_to_archive"

    echo ""
    success "Archived $archive_count items"
}

# Generate project report
generate_report() {
    local project_number="$1"
    local owner="${2:-$(get_org)}"

    echo "Generating report for project #$project_number..."

    ensure_gh_cli || return 1

    # Get graphql-queries.sh location
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local graphql_script="$script_dir/graphql-queries.sh"

    # Get full project data via GraphQL
    local result
    result=$(bash "$graphql_script" get_project "$owner" "$project_number" 2>/dev/null)

    if [[ -z "$result" ]]; then
        error "Could not fetch project data"
    fi

    local title
    title=$(echo "$result" | jq -r '.data.organization.projectV2.title // "Unknown"')

    echo ""
    echo "========================================="
    echo "Project Report: $title"
    echo "========================================="
    echo ""

    # Calculate statistics
    local total_items
    total_items=$(echo "$result" | jq '.data.organization.projectV2.items.nodes | length')

    echo "Total items: $total_items"
    echo ""

    # Count by status
    echo "By Status:"
    echo "$result" | jq -r '
        .data.organization.projectV2.items.nodes |
        map(
            .fieldValues.nodes[] |
            select(.field.name == "Status") |
            .name // "No Status"
        ) |
        group_by(.) |
        map({status: .[0], count: length}) |
        sort_by(-.count) |
        .[] |
        "  \(.status): \(.count)"
    '

    echo ""

    # Calculate completion rate
    local done_count
    done_count=$(echo "$result" | jq '[
        .data.organization.projectV2.items.nodes[] |
        select(.fieldValues.nodes[] | select(.field.name == "Status" and .name == "Done"))
    ] | length')

    if [[ "$total_items" -gt 0 ]]; then
        local completion_pct
        completion_pct=$(echo "scale=1; $done_count * 100 / $total_items" | bc)
        echo "Completion: $done_count/$total_items ($completion_pct%)"
    else
        echo "Completion: 0/0 (0%)"
    fi

    # Show open vs closed issues
    echo ""
    echo "Item States:"
    echo "$result" | jq -r '
        .data.organization.projectV2.items.nodes |
        group_by(.content.state // "unknown") |
        map({state: .[0].content.state // "unknown", count: length}) |
        .[] |
        "  \(.state): \(.count)"
    '

    echo ""
}

# List user's projects
list_projects() {
    local owner="${1:-$(get_org)}"

    ensure_gh_cli || return 1

    if [[ -z "$owner" ]]; then
        error "Could not determine organization"
    fi

    echo "Projects for $owner:"
    echo ""

    gh project list --owner "$owner" --format json | jq -r '.projects[] | "  #\(.number): \(.title)"'
}

# Main command router
main() {
    local command="${1:-help}"
    shift || true

    case "$command" in
        create_project)
            create_project "$@"
            ;;
        bulk_add_items)
            bulk_add_items "$@"
            ;;
        update_status)
            update_item_status "$@"
            ;;
        archive_done_items)
            archive_done_items "$@"
            ;;
        generate_report)
            generate_report "$@"
            ;;
        list_projects)
            list_projects "$@"
            ;;
        help|*)
            cat <<EOF
GitHub Projects Helper Script

Usage: $0 <command> [options]

Commands:
  create_project <title> [template] [owner]
      Create a new project with optional template
      Templates: sprint, kanban, roadmap

  bulk_add_items <project_number> <filter> [owner]
      Add items matching filter to project
      Example: bulk_add_items 1 "is:issue is:open label:feature"

  update_status <project_id> <item_id> <status> [owner]
      Update item status (requires GraphQL)

  archive_done_items <project_number> [owner] [days_old]
      Archive completed items older than N days

  generate_report <project_number> [owner]
      Generate project progress report

  list_projects [owner]
      List all projects for owner

Examples:
  $0 create_project "Sprint 5" sprint
  $0 bulk_add_items 1 "is:issue label:feature"
  $0 generate_report 1
  $0 list_projects myorg

EOF
            ;;
    esac
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
