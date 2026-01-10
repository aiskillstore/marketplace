# GitHub Projects v2 GraphQL Operations - gh api Workarounds

This guide provides direct `gh api` command examples for common GitHub Projects v2 operations when you need an alternative to the `graphql-queries.sh` helper script.

## Prerequisites

```bash
# Ensure gh CLI is authenticated
gh auth status

# Install jq for JSON processing
# Ubuntu/Debian: sudo apt-get install jq
# macOS: brew install jq
# Or use online tools like jq.play for one-off queries
```

## Getting Project Information

### Get Project Node ID

You need the project node ID for most GraphQL operations:

```bash
# Get project ID from organization and project number
OWNER="your-org"
PROJECT_NUMBER=1

gh api graphql -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      id
      title
    }
  }
}' -f owner="$OWNER" -F number=$PROJECT_NUMBER --jq '.data.organization.projectV2.id'
```

**Example output:** `PVT_kwDOABcDEF4AABCD`

### Get Project Fields and Options

To update fields, you need field IDs and option IDs:

```bash
# List all fields with their IDs and options
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
            dataType
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -F number=$PROJECT_NUMBER
```

**Tip:** Save field IDs and option IDs for reuse in your workflow.

## Adding Issues/PRs to Projects

### Get Issue/PR Node ID

First, get the node ID of the issue or PR:

```bash
# For an issue
OWNER="your-org"
REPO="your-repo"
ISSUE_NUMBER=42

gh api repos/$OWNER/$REPO/issues/$ISSUE_NUMBER --jq '.node_id'

# For a pull request
PR_NUMBER=123
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER --jq '.node_id'
```

**Example output:** `I_kwDOABcDEF5ABCDE`

### Add Item to Project

```bash
PROJECT_ID="PVT_kwDOABcDEF4AABCD"  # From step 1
CONTENT_ID="I_kwDOABcDEF5ABCDE"    # From previous step

gh api graphql -f query='
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {
    projectId: $projectId
    contentId: $contentId
  }) {
    item {
      id
    }
  }
}' -f projectId="$PROJECT_ID" -f contentId="$CONTENT_ID" --jq '.data.addProjectV2ItemById.item.id'
```

**Example output:** `PVTI_kwDOABcDEF4AABCDEF`

**Note:** Save this item ID for updating fields.

## Updating Project Fields

### Update Single Select Field (Status, Priority, etc.)

```bash
PROJECT_ID="PVT_kwDOABcDEF4AABCD"
ITEM_ID="PVTI_kwDOABcDEF4AABCDEF"
FIELD_ID="PVTSSF_lADOABcDEF4AABCD"     # From field list query
OPTION_ID="abc123"                      # From field options query

gh api graphql -f query='
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
}' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID"
```

### Update Text Field

```bash
TEXT_VALUE="Sprint 2024-Q1"

gh api graphql -f query='
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
}' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f text="$TEXT_VALUE"
```

### Update Number Field (Story Points, Estimate, etc.)

```bash
NUMBER_VALUE=5

gh api graphql -f query='
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
}' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -F number=$NUMBER_VALUE
```

### Update Date Field

```bash
DATE_VALUE="2024-12-31"

gh api graphql -f query='
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $date: Date!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: {
      date: $date
    }
  }) {
    projectV2Item {
      id
    }
  }
}' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f date="$DATE_VALUE"
```

## Bulk Operations

### Add Multiple Issues to Project

```bash
#!/bin/bash
# Add all issues with a specific label to project

PROJECT_ID="PVT_kwDOABcDEF4AABCD"
OWNER="your-org"
REPO="your-repo"
LABEL="feature"

# Get all issues with label
gh issue list --repo "$OWNER/$REPO" --label "$LABEL" --json number --jq '.[].number' | \
while read -r issue_number; do
    # Get issue node ID
    content_id=$(gh api repos/$OWNER/$REPO/issues/$issue_number --jq '.node_id')

    # Add to project
    gh api graphql -f query='
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }' -f projectId="$PROJECT_ID" -f contentId="$content_id"

    echo "Added issue #$issue_number"
done
```

### Bulk Update Field for Multiple Items

```bash
#!/bin/bash
# Update status for all items

PROJECT_ID="PVT_kwDOABcDEF4AABCD"
FIELD_ID="PVTSSF_lADOABcDEF4AABCD"
OPTION_ID="abc123"  # "In Progress" option

# Array of item IDs
ITEM_IDS=(
    "PVTI_kwDOABcDEF4AABCDEF"
    "PVTI_kwDOABcDEF4AABCDEG"
    "PVTI_kwDOABcDEF4AABCDEH"
)

for item_id in "${ITEM_IDS[@]}"; do
    gh api graphql -f query='
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item { id }
      }
    }' -f projectId="$PROJECT_ID" -f itemId="$item_id" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID"

    echo "Updated item $item_id"
done
```

## Querying Project Items

### Get All Items in Project

```bash
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              state
            }
            ... on PullRequest {
              number
              title
              state
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}' -f owner="$OWNER" -F number=$PROJECT_NUMBER
```

### Filter Items by Field Value

```bash
# Get items with specific status
gh api graphql -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue { number title }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField { name }
                }
              }
            }
          }
        }
      }
    }
  }
}' -f owner="$OWNER" -F number=$PROJECT_NUMBER | \
jq '.data.organization.projectV2.items.nodes[] |
    select(.fieldValues.nodes[] | select(.field.name == "Status" and .name == "In Progress"))'
```

## Common Workflows

### Workflow 1: Add Issue and Set Initial Fields

```bash
#!/bin/bash
# Complete workflow: Add issue to project and set status

OWNER="your-org"
REPO="your-repo"
ISSUE_NUMBER=42
PROJECT_NUMBER=1

# Step 1: Get IDs
PROJECT_ID=$(gh api graphql -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) { id }
  }
}' -f owner="$OWNER" -F number=$PROJECT_NUMBER --jq '.data.organization.projectV2.id')

CONTENT_ID=$(gh api repos/$OWNER/$REPO/issues/$ISSUE_NUMBER --jq '.node_id')

# Step 2: Add to project
ITEM_ID=$(gh api graphql -f query='
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item { id }
  }
}' -f projectId="$PROJECT_ID" -f contentId="$CONTENT_ID" --jq '.data.addProjectV2ItemById.item.id')

echo "Added issue #$ISSUE_NUMBER to project (item ID: $ITEM_ID)"

# Step 3: Set status to "Todo"
# Note: You'll need to get FIELD_ID and OPTION_ID from your project
FIELD_ID="your-status-field-id"
OPTION_ID="your-todo-option-id"

gh api graphql -f query='
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: { singleSelectOptionId: $optionId }
  }) {
    projectV2Item { id }
  }
}' -f projectId="$PROJECT_ID" -f itemId="$ITEM_ID" -f fieldId="$FIELD_ID" -f optionId="$OPTION_ID"

echo "Set status to Todo"
```

### Workflow 2: Sync Issues to Project by Label

```bash
#!/bin/bash
# Sync all "priority:high" issues to sprint board

OWNER="your-org"
REPO="your-repo"
PROJECT_NUMBER=1
LABEL="priority:high"

PROJECT_ID=$(gh api graphql -f query='
query($owner: String!, $number: Int!) {
  organization(login: $owner) {
    projectV2(number: $number) { id }
  }
}' -f owner="$OWNER" -F number=$PROJECT_NUMBER --jq '.data.organization.projectV2.id')

gh issue list --repo "$OWNER/$REPO" --label "$LABEL" --state open --json number --jq '.[].number' | \
while read -r issue_number; do
    content_id=$(gh api repos/$OWNER/$REPO/issues/$issue_number --jq '.node_id')

    item_id=$(gh api graphql -f query='
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }' -f projectId="$PROJECT_ID" -f contentId="$content_id" --jq '.data.addProjectV2ItemById.item.id' 2>/dev/null)

    if [[ -n "$item_id" && "$item_id" != "null" ]]; then
        echo "✓ Added issue #$issue_number"
    else
        echo "⚠ Issue #$issue_number already in project or failed"
    fi
done
```

## Troubleshooting

### Error: "Resource protected by organization SAML enforcement"

**Solution:** Authenticate with SSO:
```bash
gh auth refresh -h github.com -s project
```

### Error: "Could not resolve to a node"

**Problem:** Invalid node ID

**Solution:** Verify IDs are correct and haven't expired. Node IDs are stable but double-check:
```bash
# Re-fetch the ID
gh api repos/OWNER/REPO/issues/NUMBER --jq '.node_id'
```

### Error: "Field does not exist on this project"

**Problem:** Wrong field ID or field deleted

**Solution:** Re-fetch field IDs:
```bash
gh api graphql -f query='query($owner: String!, $number: Int!) { ... }' ...
```

### Rate Limiting

GraphQL operations count against your rate limit. Check status:
```bash
gh api rate_limit
```

**Tip:** Use pagination and batch operations to minimize API calls.

## Additional Resources

- [GitHub GraphQL API Explorer](https://docs.github.com/en/graphql/overview/explorer)
- [Projects v2 GraphQL API docs](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
- [gh CLI manual](https://cli.github.com/manual/)

## Quick Reference: ID Lookup

Keep these commands handy for quick ID lookups:

```bash
# Project ID
gh api graphql -f query='query($o: String!, $n: Int!) {organization(login: $o) {projectV2(number: $n) {id}}}' -f o=OWNER -F n=NUM --jq '.data.organization.projectV2.id'

# Issue/PR ID
gh api repos/OWNER/REPO/issues/NUM --jq '.node_id'

# Field IDs
gh api graphql -f query='query($o: String!, $n: Int!) {organization(login: $o) {projectV2(number: $n) {fields(first: 20) {nodes {id name}}}}}' -f o=OWNER -F n=NUM --jq '.data.organization.projectV2.fields.nodes[] | "\(.name): \(.id)"'
```

---

**Remember:** The `graphql-queries.sh` helper script wraps these commands for convenience, but these raw `gh api` commands provide full flexibility and transparency.
