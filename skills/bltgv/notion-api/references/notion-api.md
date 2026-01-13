# Notion API Reference

Quick reference for Notion API endpoints and data structures.

## Base URL

```
https://api.notion.com/v1
```

## Authentication

All requests require:
- `Authorization: Bearer {integration_token}`
- `Notion-Version: 2022-06-28`
- `Content-Type: application/json`

## Endpoints

### Search

**POST** `/search`

Search pages and databases across the workspace.

Request body:
```json
{
  "query": "search term",
  "filter": {
    "value": "page",  // or "database"
    "property": "object"
  },
  "sort": {
    "direction": "ascending",  // or "descending"
    "timestamp": "last_edited_time"
  },
  "page_size": 100,
  "start_cursor": "cursor_from_previous_response"
}
```

### Pages

**GET** `/pages/{page_id}`

Retrieve a page by ID.

**POST** `/pages`

Create a new page.

Request body:
```json
{
  "parent": {
    "page_id": "parent_page_id"
    // OR
    "database_id": "parent_database_id"
  },
  "properties": {
    "title": {
      "title": [{"text": {"content": "Page Title"}}]
    }
  },
  "icon": {
    "type": "emoji",
    "emoji": "📝"
  },
  "children": []  // optional initial blocks
}
```

**PATCH** `/pages/{page_id}`

Update a page.

Request body:
```json
{
  "properties": {
    "title": {
      "title": [{"text": {"content": "New Title"}}]
    }
  },
  "icon": {"type": "emoji", "emoji": "🎉"},
  "archived": false
}
```

### Databases

**GET** `/databases/{database_id}`

Retrieve database schema.

**POST** `/databases/{database_id}/query`

Query database entries.

Request body:
```json
{
  "filter": {
    "property": "Status",
    "select": {"equals": "Done"}
  },
  "sorts": [
    {
      "property": "Created",
      "direction": "descending"
    }
  ],
  "page_size": 100,
  "start_cursor": "cursor"
}
```

### Blocks

**GET** `/blocks/{block_id}/children`

Get child blocks of a page or block.

Query parameters:
- `page_size`: Max 100
- `start_cursor`: For pagination

**GET** `/blocks/{block_id}`

Get a specific block.

## Filter Types

### Text filters (rich_text, title, url, email, phone_number)
```json
{"property": "Name", "rich_text": {"equals": "exact match"}}
{"property": "Name", "rich_text": {"does_not_equal": "value"}}
{"property": "Name", "rich_text": {"contains": "partial"}}
{"property": "Name", "rich_text": {"does_not_contain": "value"}}
{"property": "Name", "rich_text": {"starts_with": "prefix"}}
{"property": "Name", "rich_text": {"ends_with": "suffix"}}
{"property": "Name", "rich_text": {"is_empty": true}}
{"property": "Name", "rich_text": {"is_not_empty": true}}
```

### Number filters
```json
{"property": "Score", "number": {"equals": 100}}
{"property": "Score", "number": {"does_not_equal": 0}}
{"property": "Score", "number": {"greater_than": 50}}
{"property": "Score", "number": {"less_than": 50}}
{"property": "Score", "number": {"greater_than_or_equal_to": 50}}
{"property": "Score", "number": {"less_than_or_equal_to": 50}}
{"property": "Score", "number": {"is_empty": true}}
{"property": "Score", "number": {"is_not_empty": true}}
```

### Checkbox filters
```json
{"property": "Done", "checkbox": {"equals": true}}
{"property": "Done", "checkbox": {"does_not_equal": true}}
```

### Select filters
```json
{"property": "Status", "select": {"equals": "Done"}}
{"property": "Status", "select": {"does_not_equal": "Done"}}
{"property": "Status", "select": {"is_empty": true}}
{"property": "Status", "select": {"is_not_empty": true}}
```

### Multi-select filters
```json
{"property": "Tags", "multi_select": {"contains": "Important"}}
{"property": "Tags", "multi_select": {"does_not_contain": "Archived"}}
{"property": "Tags", "multi_select": {"is_empty": true}}
{"property": "Tags", "multi_select": {"is_not_empty": true}}
```

### Date filters
```json
{"property": "Due", "date": {"equals": "2024-01-15"}}
{"property": "Due", "date": {"before": "2024-01-15"}}
{"property": "Due", "date": {"after": "2024-01-15"}}
{"property": "Due", "date": {"on_or_before": "2024-01-15"}}
{"property": "Due", "date": {"on_or_after": "2024-01-15"}}
{"property": "Due", "date": {"past_week": {}}}
{"property": "Due", "date": {"past_month": {}}}
{"property": "Due", "date": {"past_year": {}}}
{"property": "Due", "date": {"next_week": {}}}
{"property": "Due", "date": {"next_month": {}}}
{"property": "Due", "date": {"next_year": {}}}
{"property": "Due", "date": {"is_empty": true}}
{"property": "Due", "date": {"is_not_empty": true}}
```

### Compound filters
```json
{
  "and": [
    {"property": "Status", "select": {"equals": "Done"}},
    {"property": "Priority", "select": {"equals": "High"}}
  ]
}

{
  "or": [
    {"property": "Status", "select": {"equals": "Done"}},
    {"property": "Status", "select": {"equals": "Archived"}}
  ]
}
```

## Sort Options

### By property
```json
{"property": "Name", "direction": "ascending"}
{"property": "Created", "direction": "descending"}
```

### By timestamp
```json
{"timestamp": "created_time", "direction": "ascending"}
{"timestamp": "last_edited_time", "direction": "descending"}
```

## Property Types

Database properties can be:
- `title` - Page title
- `rich_text` - Text content
- `number` - Numeric value
- `select` - Single select
- `multi_select` - Multiple selections
- `date` - Date/datetime
- `people` - User references
- `files` - File attachments
- `checkbox` - Boolean
- `url` - URL
- `email` - Email address
- `phone_number` - Phone number
- `formula` - Calculated value (read-only)
- `relation` - Links to other pages
- `rollup` - Aggregated from relations (read-only)
- `created_time` - Creation timestamp (read-only)
- `created_by` - Creator (read-only)
- `last_edited_time` - Last edit timestamp (read-only)
- `last_edited_by` - Last editor (read-only)
- `status` - Status with groups

## Block Types

Common block types:
- `paragraph` - Text paragraph
- `heading_1`, `heading_2`, `heading_3` - Headings
- `bulleted_list_item` - Bullet point
- `numbered_list_item` - Numbered item
- `to_do` - Checkbox item
- `toggle` - Collapsible section
- `code` - Code block with language
- `quote` - Quote block
- `callout` - Callout with icon
- `divider` - Horizontal line
- `table` - Table
- `image` - Image
- `bookmark` - URL bookmark
- `embed` - Embedded content
- `file` - File attachment
- `pdf` - PDF embed

## Rate Limits

- Average: 3 requests per second
- Burst: Higher for short periods
- HTTP 429 response when exceeded
- Check `Retry-After` header for wait time

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Invalid request (validation error) |
| 401 | Unauthorized (bad token) |
| 403 | Forbidden (no access) |
| 404 | Not found (or not shared with integration) |
| 409 | Conflict (concurrent edit) |
| 429 | Rate limited |
| 500 | Internal server error |

## Pagination

All list endpoints support pagination:
- Request: `page_size` (max 100), `start_cursor`
- Response: `has_more`, `next_cursor`

Loop until `has_more` is false to get all results.
