# GitHub CLI Project Commands Reference

## Project Commands

### List Projects
```bash
# List user projects
gh project list --owner @me

# List org projects
gh project list --owner ORG_NAME

# List with format
gh project list --owner @me --format json
```

### View Project
```bash
# View by number
gh project view PROJECT_NUMBER --owner @me

# View with web
gh project view PROJECT_NUMBER --owner @me --web
```

### Create Project
```bash
# Create project
gh project create --owner @me --title "Project Name"

# Create with template (if supported)
gh project create --owner @me --title "Sprint Board"
```

### Delete Project
```bash
gh project delete PROJECT_NUMBER --owner @me
```

## Item Management

### Add Items
```bash
# Add issue to project
gh project item-add PROJECT_NUMBER --owner @me --url ISSUE_URL

# Add PR to project
gh project item-add PROJECT_NUMBER --owner @me --url PR_URL
```

### List Items
```bash
# List all items
gh project item-list PROJECT_NUMBER --owner @me

# List with format
gh project item-list PROJECT_NUMBER --owner @me --format json
```

### Delete Items
```bash
gh project item-delete PROJECT_NUMBER --owner @me --id ITEM_ID
```

## Field Management

### List Fields
```bash
gh project field-list PROJECT_NUMBER --owner @me
```

### Create Field
```bash
# Text field
gh project field-create PROJECT_NUMBER --owner @me \
  --name "Field Name" --data-type TEXT

# Single select
gh project field-create PROJECT_NUMBER --owner @me \
  --name "Priority" --data-type SINGLE_SELECT \
  --single-select-options "High,Medium,Low"

# Number field
gh project field-create PROJECT_NUMBER --owner @me \
  --name "Story Points" --data-type NUMBER

# Date field
gh project field-create PROJECT_NUMBER --owner @me \
  --name "Due Date" --data-type DATE
```

### Delete Field
```bash
gh project field-delete PROJECT_NUMBER --owner @me --id FIELD_ID
```

## Edit Item Fields

```bash
# Update text field
gh project item-edit --project-id PROJECT_ID --id ITEM_ID \
  --field-id FIELD_ID --text "value"

# Update single select
gh project item-edit --project-id PROJECT_ID --id ITEM_ID \
  --field-id FIELD_ID --single-select-option-id OPTION_ID

# Update number
gh project item-edit --project-id PROJECT_ID --id ITEM_ID \
  --field-id FIELD_ID --number 5

# Update date
gh project item-edit --project-id PROJECT_ID --id ITEM_ID \
  --field-id FIELD_ID --date "2024-03-15"
```

## Advanced: GraphQL via gh api

### Get Project ID
```bash
gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        title
      }
    }
  }
' -f owner="USERNAME" -F number=1
```

### Get Field Options
```bash
gh api graphql -f query='
  query($projectId: ID!) {
    node(id: $projectId) {
      ... on ProjectV2 {
        fields(first: 20) {
          nodes {
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
  }
' -f projectId="PROJECT_ID"
```

### Add Item via GraphQL
```bash
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
  }
' -f projectId="PROJECT_ID" -f contentId="ISSUE_NODE_ID"
```

### Update Field Value
```bash
gh api graphql -f query='
  mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
    updateProjectV2ItemFieldValue(input: {
      projectId: $projectId
      itemId: $itemId
      fieldId: $fieldId
      value: { singleSelectOptionId: $optionId }
    }) {
      projectV2Item {
        id
      }
    }
  }
' -f projectId="PROJECT_ID" -f itemId="ITEM_ID" -f fieldId="FIELD_ID" -f optionId="OPTION_ID"
```

## Common Workflows

### Bulk Add Issues
```bash
# Add all open issues to project
gh issue list --state open --json url -q '.[].url' | \
  xargs -I {} gh project item-add PROJECT_NUMBER --owner @me --url {}
```

### Export Project Data
```bash
# Export items as JSON
gh project item-list PROJECT_NUMBER --owner @me --format json > project-export.json
```

### Copy Project Structure
```bash
# Get fields from source
SOURCE_FIELDS=$(gh project field-list SOURCE_NUM --owner @me --format json)

# Create fields in target (manual iteration required)
```

## Environment Variables

```bash
# Set default owner
export GH_PROJECT_OWNER="@me"

# Use in commands
gh project list --owner $GH_PROJECT_OWNER
```

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| "Project not found" | Wrong number/owner | Verify with `gh project list` |
| "Field not found" | Invalid field ID | Get IDs with `gh project field-list` |
| "Permission denied" | Not project admin | Check project settings |
| "Rate limit exceeded" | Too many API calls | Wait and retry |
