#!/usr/bin/env bash
# GraphQL Operations for GitHub Projects v2
# Provides query builder and executor functions for advanced project operations

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_gh_auth() {
    if ! gh auth status >/dev/null 2>&1; then
        error "Not authenticated with GitHub. Run: gh auth login"
    fi
}

# Retry logic with exponential backoff
retry_graphql() {
    local max_attempts="${RETRY_MAX_ATTEMPTS:-3}"
    local initial_delay="${RETRY_INITIAL_DELAY:-2}"
    local max_delay="${RETRY_MAX_DELAY:-30}"
    local attempt=1
    local delay="$initial_delay"

    while [ "$attempt" -le "$max_attempts" ]; do
        # Execute the command (passed as arguments)
        if "$@" 2>/dev/null; then
            return 0
        fi

        local exit_code=$?

        if [ "$attempt" -eq "$max_attempts" ]; then
            error "GraphQL operation failed after $max_attempts attempts"
            return "$exit_code"
        fi

        warn "Attempt $attempt/$max_attempts failed. Retrying in ${delay}s..."
        sleep "$delay"

        # Exponential backoff with cap
        delay=$((delay * 2))
        if [ "$delay" -gt "$max_delay" ]; then
            delay="$max_delay"
        fi

        attempt=$((attempt + 1))
    done

    return 1
}

# Execute GraphQL query with retry
execute_graphql_query() {
    local query="$1"
    shift
    local variables=("$@")

    retry_graphql gh api graphql -f query="$query" "${variables[@]}"
}

# Build project query
build_project_query() {
    local org="$1"
    local project_number="$2"

    cat <<'EOF'
query($org: String!, $number: Int!) {
  organization(login: $org) {
    projectV2(number: $number) {
      id
      title
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations {
                id
                title
              }
            }
          }
        }
      }
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              id
              number
              title
              state
            }
            ... on PullRequest {
              id
              number
              title
              state
            }
          }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                field {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                  }
                }
                name
              }
            }
          }
        }
      }
    }
  }
}
EOF
}

# Execute GraphQL query
execute_query() {
    local query="$1"
    local variables="$2"

    check_gh_auth

    gh api graphql -f query="$query" -f variables="$variables"
}

# Get project details
get_project() {
    local owner="$1"
    local project_number="$2"

    check_gh_auth

    local query
    query=$(build_project_query "$owner" "$project_number")

    local variables
    variables=$(jq -n \
        --arg org "$owner" \
        --arg number "$project_number" \
        '{org: $org, number: ($number | tonumber)}')

    gh api graphql -f query="$query" -F variables="$variables" 2>/dev/null || {
        error "Failed to get project. Check owner and project number."
    }
}

# Get project node ID from organization and project number
get_project_node_id() {
    local owner="$1"
    local project_number="$2"

    local result
    result=$(get_project "$owner" "$project_number")

    echo "$result" | jq -r '.data.organization.projectV2.id'
}

# Get issue/PR node ID
get_content_node_id() {
    local owner="$1"
    local repo="$2"
    local type="$3"  # "issue" or "pr"
    local number="$4"

    check_gh_auth

    if [[ "$type" == "issue" ]]; then
        gh api "repos/$owner/$repo/issues/$number" --jq '.node_id'
    elif [[ "$type" == "pr" ]]; then
        gh api "repos/$owner/$repo/pulls/$number" --jq '.node_id'
    else
        error "Invalid type: $type (use 'issue' or 'pr')"
    fi
}

# Add item to project (mutation)
add_project_item() {
    local project_id="$1"
    local content_id="$2"

    check_gh_auth

    local mutation
    mutation=$(cat <<'EOF'
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {
    projectId: $projectId
    contentId: $contentId
  }) {
    item {
      id
    }
  }
}
EOF
)

    local result
    result=$(gh api graphql -f query="$mutation" \
        -f projectId="$project_id" \
        -f contentId="$content_id" 2>&1) || {
        warn "Failed to add item to project"
        echo "$result" >&2
        return 1
    }

    local item_id
    item_id=$(echo "$result" | jq -r '.data.addProjectV2ItemById.item.id')

    if [[ -n "$item_id" && "$item_id" != "null" ]]; then
        success "Added item to project: $item_id"
        echo "$item_id"
    else
        warn "Item may already be in project or operation failed"
        return 1
    fi
}

# Update item field value (single select)
update_item_field_single_select() {
    local project_id="$1"
    local item_id="$2"
    local field_id="$3"
    local option_id="$4"

    check_gh_auth

    local mutation
    mutation=$(cat <<'EOF'
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: {
      singleSelectOptionId: $optionId
    }
  }) {
    projectV2Item {
      id
    }
  }
}
EOF
)

    gh api graphql -f query="$mutation" \
        -f projectId="$project_id" \
        -f itemId="$item_id" \
        -f fieldId="$field_id" \
        -f optionId="$option_id" >/dev/null && \
    success "Updated field value"
}

# Update item field value (text)
update_item_field_text() {
    local project_id="$1"
    local item_id="$2"
    local field_id="$3"
    local text_value="$4"

    check_gh_auth

    local mutation
    mutation=$(cat <<'EOF'
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $text: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: {
      text: $text
    }
  }) {
    projectV2Item {
      id
    }
  }
}
EOF
)

    gh api graphql -f query="$mutation" \
        -f projectId="$project_id" \
        -f itemId="$item_id" \
        -f fieldId="$field_id" \
        -f text="$text_value" >/dev/null && \
    success "Updated text field"
}

# Update item field value (number)
update_item_field_number() {
    local project_id="$1"
    local item_id="$2"
    local field_id="$3"
    local number_value="$4"

    check_gh_auth

    local mutation
    mutation=$(cat <<'EOF'
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $number: Float!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: {
      number: $number
    }
  }) {
    projectV2Item {
      id
    }
  }
}
EOF
)

    gh api graphql -f query="$mutation" \
        -f projectId="$project_id" \
        -f itemId="$item_id" \
        -f fieldId="$field_id" \
        -F number="$number_value" >/dev/null && \
    success "Updated number field"
}

# Bulk update items
bulk_update_items() {
    local project_id="$1"
    local field_id="$2"
    local option_id="$3"
    shift 3
    local item_ids=("$@")

    check_gh_auth

    info "Updating ${#item_ids[@]} items..."

    local success_count=0
    local fail_count=0

    for item_id in "${item_ids[@]}"; do
        if update_item_field_single_select "$project_id" "$item_id" "$field_id" "$option_id" 2>/dev/null; then
            ((success_count++))
        else
            ((fail_count++))
        fi
    done

    echo ""
    success "Updated $success_count items"
    [[ $fail_count -gt 0 ]] && warn "Failed to update $fail_count items"
}

# List project fields
list_project_fields() {
    local owner="$1"
    local project_number="$2"

    local result
    result=$(get_project "$owner" "$project_number")

    echo "$result" | jq -r '
        .data.organization.projectV2.fields.nodes[] |
        "\(.id)\t\(.name)\t\(.__typename)"
    ' | column -t -s $'\t'
}

# List project items
list_project_items() {
    local owner="$1"
    local project_number="$2"

    local result
    result=$(get_project "$owner" "$project_number")

    echo "$result" | jq -r '
        .data.organization.projectV2.items.nodes[] |
        "\(.id)\t\(.content.number // "N/A")\t\(.content.title // "No title")\t\(.content.state // "unknown")"
    ' | column -t -s $'\t'
}

# Get field options (for single select fields)
get_field_options() {
    local owner="$1"
    local project_number="$2"
    local field_name="$3"

    local result
    result=$(get_project "$owner" "$project_number")

    echo "$result" | jq -r --arg field "$field_name" '
        .data.organization.projectV2.fields.nodes[] |
        select(.name == $field) |
        .options[]? |
        "\(.id)\t\(.name)"
    ' | column -t -s $'\t'
}

# Usage/help
show_usage() {
    cat <<EOF
Usage: $0 <command> [arguments]

Commands:
  get_project <owner> <project_number>
      Get full project details including fields and items

  get_project_id <owner> <project_number>
      Get project node ID

  get_content_id <owner> <repo> <issue|pr> <number>
      Get issue or PR node ID

  add_item <project_id> <content_id>
      Add an issue or PR to a project

  update_field_select <project_id> <item_id> <field_id> <option_id>
      Update a single select field

  update_field_text <project_id> <item_id> <field_id> <text_value>
      Update a text field

  update_field_number <project_id> <item_id> <field_id> <number_value>
      Update a number field

  bulk_update <project_id> <field_id> <option_id> <item_id1> [item_id2...]
      Bulk update field for multiple items

  list_fields <owner> <project_number>
      List all fields in a project

  list_items <owner> <project_number>
      List all items in a project

  get_options <owner> <project_number> <field_name>
      Get options for a single select field

Examples:
  # Get project ID
  $0 get_project_id myorg 1

  # Add issue to project
  CONTENT_ID=\$($0 get_content_id myorg myrepo issue 42)
  PROJECT_ID=\$($0 get_project_id myorg 1)
  $0 add_item "\$PROJECT_ID" "\$CONTENT_ID"

  # Update status field
  $0 update_field_select "\$PROJECT_ID" "\$ITEM_ID" "\$FIELD_ID" "\$OPTION_ID"

  # List fields to find IDs
  $0 list_fields myorg 1

  # Get status field options
  $0 get_options myorg 1 "Status"

Note: Requires 'gh' CLI with authentication and 'jq' for JSON processing.
EOF
}

# Main entry point
main() {
    # Check for jq
    if ! command -v jq &>/dev/null; then
        error "jq is required but not installed. Install with: apt-get install jq (Ubuntu) or brew install jq (macOS)"
    fi

    # Check for gh CLI
    if ! command -v gh &>/dev/null; then
        error "GitHub CLI (gh) is required but not installed. See: https://cli.github.com/"
    fi

    case "${1:-help}" in
        get_project)
            [[ $# -lt 3 ]] && error "Usage: $0 get_project <owner> <project_number>"
            get_project "$2" "$3"
            ;;
        get_project_id)
            [[ $# -lt 3 ]] && error "Usage: $0 get_project_id <owner> <project_number>"
            get_project_node_id "$2" "$3"
            ;;
        get_content_id)
            [[ $# -lt 5 ]] && error "Usage: $0 get_content_id <owner> <repo> <issue|pr> <number>"
            get_content_node_id "$2" "$3" "$4" "$5"
            ;;
        add_item)
            [[ $# -lt 3 ]] && error "Usage: $0 add_item <project_id> <content_id>"
            add_project_item "$2" "$3"
            ;;
        update_field_select)
            [[ $# -lt 5 ]] && error "Usage: $0 update_field_select <project_id> <item_id> <field_id> <option_id>"
            update_item_field_single_select "$2" "$3" "$4" "$5"
            ;;
        update_field_text)
            [[ $# -lt 5 ]] && error "Usage: $0 update_field_text <project_id> <item_id> <field_id> <text_value>"
            update_item_field_text "$2" "$3" "$4" "$5"
            ;;
        update_field_number)
            [[ $# -lt 5 ]] && error "Usage: $0 update_field_number <project_id> <item_id> <field_id> <number_value>"
            update_item_field_number "$2" "$3" "$4" "$5"
            ;;
        bulk_update)
            [[ $# -lt 5 ]] && error "Usage: $0 bulk_update <project_id> <field_id> <option_id> <item_id1> [item_id2...]"
            bulk_update_items "$2" "$3" "$4" "${@:5}"
            ;;
        list_fields)
            [[ $# -lt 3 ]] && error "Usage: $0 list_fields <owner> <project_number>"
            list_project_fields "$2" "$3"
            ;;
        list_items)
            [[ $# -lt 3 ]] && error "Usage: $0 list_items <owner> <project_number>"
            list_project_items "$2" "$3"
            ;;
        get_options)
            [[ $# -lt 4 ]] && error "Usage: $0 get_options <owner> <project_number> <field_name>"
            get_field_options "$2" "$3" "$4"
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            error "Unknown command: $1\n\nRun '$0 help' for usage information."
            ;;
    esac
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
