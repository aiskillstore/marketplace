# Notion Database Query Filters and Sorts

This document provides comprehensive documentation for filtering and sorting database queries in the Notion API.

## Filter Structure

Filters are sent in the request body of database query requests:

```bash
curl -s -X POST "https://api.notion.com/v1/databases/{database_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": { /* filter object */ },
    "sorts": [ /* sort array */ ],
    "page_size": 100
  }'
```

## Single Property Filters

Each filter object requires:
- `property`: The property name or ID
- A type-specific condition object

### Text Filters (Rich Text, Title, URL, Email, Phone Number)

```json
{
  "property": "Name",
  "rich_text": {
    "equals": "exact match"
  }
}
```

Text conditions:
- `equals` - Exact match (case-sensitive)
- `does_not_equal` - Not exact match
- `contains` - Contains substring
- `does_not_contain` - Does not contain substring
- `starts_with` - Starts with string
- `ends_with` - Ends with string
- `is_empty` - Value is empty (boolean: true)
- `is_not_empty` - Value is not empty (boolean: true)

Examples:

```json
{"property": "Title", "title": {"contains": "Project"}}
{"property": "Website", "url": {"starts_with": "https://"}}
{"property": "Email", "email": {"is_not_empty": true}}
{"property": "Phone", "phone_number": {"contains": "+1"}}
```

### Number Filters

```json
{
  "property": "Price",
  "number": {
    "greater_than": 100
  }
}
```

Number conditions:
- `equals` - Equal to number
- `does_not_equal` - Not equal to number
- `greater_than` - Greater than number
- `less_than` - Less than number
- `greater_than_or_equal_to` - Greater than or equal
- `less_than_or_equal_to` - Less than or equal
- `is_empty` - Value is empty (boolean: true)
- `is_not_empty` - Value is not empty (boolean: true)

### Checkbox Filters

```json
{
  "property": "Complete",
  "checkbox": {
    "equals": true
  }
}
```

Checkbox conditions:
- `equals` - Equal to boolean (true/false)
- `does_not_equal` - Not equal to boolean

### Select Filters

```json
{
  "property": "Status",
  "select": {
    "equals": "Done"
  }
}
```

Select conditions:
- `equals` - Matches option name
- `does_not_equal` - Does not match option name
- `is_empty` - No selection (boolean: true)
- `is_not_empty` - Has selection (boolean: true)

### Multi-Select Filters

```json
{
  "property": "Tags",
  "multi_select": {
    "contains": "Urgent"
  }
}
```

Multi-select conditions:
- `contains` - Contains option name
- `does_not_contain` - Does not contain option name
- `is_empty` - No selections (boolean: true)
- `is_not_empty` - Has selections (boolean: true)

### Status Filters

```json
{
  "property": "Project Status",
  "status": {
    "equals": "In progress"
  }
}
```

Status conditions (same as select):
- `equals`, `does_not_equal`, `is_empty`, `is_not_empty`

### Date Filters

```json
{
  "property": "Due Date",
  "date": {
    "after": "2024-01-01"
  }
}
```

Date conditions with date values:
- `equals` - Exact date match
- `before` - Before date
- `after` - After date
- `on_or_before` - On or before date
- `on_or_after` - On or after date

Date conditions without values (boolean: true):
- `is_empty` - No date set
- `is_not_empty` - Date is set
- `past_week` - Within the past week
- `past_month` - Within the past month
- `past_year` - Within the past year
- `this_week` - Within current week
- `next_week` - Within next week
- `next_month` - Within next month
- `next_year` - Within next year

Date format: ISO 8601 (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS.sssZ`)

**Note**: If no timezone is provided, defaults to UTC.

### People Filters

```json
{
  "property": "Assignee",
  "people": {
    "contains": "user-uuid"
  }
}
```

People conditions:
- `contains` - Contains user ID
- `does_not_contain` - Does not contain user ID
- `is_empty` - No people assigned (boolean: true)
- `is_not_empty` - Has people assigned (boolean: true)

### Files Filters

```json
{
  "property": "Attachments",
  "files": {
    "is_not_empty": true
  }
}
```

Files conditions:
- `is_empty` - No files (boolean: true)
- `is_not_empty` - Has files (boolean: true)

### Relation Filters

```json
{
  "property": "Related Projects",
  "relation": {
    "contains": "page-uuid"
  }
}
```

Relation conditions:
- `contains` - Contains related page ID
- `does_not_contain` - Does not contain related page ID
- `is_empty` - No relations (boolean: true)
- `is_not_empty` - Has relations (boolean: true)

### Rollup Filters

Rollup filters depend on the rollup type:

For aggregated rollups (count, sum, etc.):

```json
{
  "property": "Task Count",
  "rollup": {
    "number": {
      "greater_than": 5
    }
  }
}
```

For "show original" rollups, use `any`, `every`, or `none`:

```json
{
  "property": "Task Statuses",
  "rollup": {
    "any": {
      "select": {
        "equals": "Done"
      }
    }
  }
}
```

Rollup conditions:
- `any` - At least one item matches
- `every` - All items match
- `none` - No items match

### Formula Filters

Formula filters depend on the formula result type:

```json
{
  "property": "Days Until Due",
  "formula": {
    "number": {
      "less_than": 7
    }
  }
}
```

```json
{
  "property": "Is Overdue",
  "formula": {
    "checkbox": {
      "equals": true
    }
  }
}
```

### Timestamp Filters

Filter by creation or edit time without specifying a property:

```json
{
  "timestamp": "created_time",
  "created_time": {
    "after": "2024-01-01"
  }
}
```

```json
{
  "timestamp": "last_edited_time",
  "last_edited_time": {
    "past_week": {}
  }
}
```

### Unique ID Filters

```json
{
  "property": "ID",
  "unique_id": {
    "equals": 42
  }
}
```

Unique ID conditions:
- `equals` - Exact number match
- `does_not_equal` - Not equal to number
- `greater_than`, `less_than`, `greater_than_or_equal_to`, `less_than_or_equal_to`

---

## Compound Filters

Combine multiple filters using `and` or `or`:

### AND Filter (All conditions must match)

```json
{
  "and": [
    {"property": "Status", "select": {"equals": "In Progress"}},
    {"property": "Priority", "select": {"equals": "High"}}
  ]
}
```

### OR Filter (Any condition must match)

```json
{
  "or": [
    {"property": "Status", "select": {"equals": "Done"}},
    {"property": "Status", "select": {"equals": "Archived"}}
  ]
}
```

### Nested Compound Filters

**Note**: Nesting is supported up to **two levels deep**.

```json
{
  "and": [
    {"property": "Type", "select": {"equals": "Task"}},
    {
      "or": [
        {"property": "Priority", "select": {"equals": "High"}},
        {
          "and": [
            {"property": "Priority", "select": {"equals": "Medium"}},
            {"property": "Due Date", "date": {"before": "2024-02-01"}}
          ]
        }
      ]
    }
  ]
}
```

---

## Sort Structure

Sorts are provided as an array. Earlier sorts take precedence over later ones.

### Property Value Sort

```json
{
  "sorts": [
    {
      "property": "Due Date",
      "direction": "ascending"
    }
  ]
}
```

### Timestamp Sort

```json
{
  "sorts": [
    {
      "timestamp": "created_time",
      "direction": "descending"
    }
  ]
}
```

### Multiple Sorts

```json
{
  "sorts": [
    {"property": "Priority", "direction": "descending"},
    {"property": "Due Date", "direction": "ascending"},
    {"timestamp": "created_time", "direction": "descending"}
  ]
}
```

Sort directions:
- `ascending` - A to Z, 0 to 9, oldest to newest
- `descending` - Z to A, 9 to 0, newest to oldest

---

## Complete Query Examples

### Tasks due this week, high priority first

```json
{
  "filter": {
    "and": [
      {"property": "Due Date", "date": {"this_week": {}}},
      {"property": "Status", "status": {"does_not_equal": "Done"}}
    ]
  },
  "sorts": [
    {"property": "Priority", "direction": "descending"},
    {"property": "Due Date", "direction": "ascending"}
  ],
  "page_size": 50
}
```

### Recent items created by specific user

```json
{
  "filter": {
    "and": [
      {"timestamp": "created_time", "created_time": {"past_month": {}}},
      {"property": "Created By", "people": {"contains": "user-uuid"}}
    ]
  },
  "sorts": [
    {"timestamp": "created_time", "direction": "descending"}
  ]
}
```

### Items with specific tag OR high priority

```json
{
  "filter": {
    "or": [
      {"property": "Tags", "multi_select": {"contains": "Urgent"}},
      {"property": "Priority", "select": {"equals": "High"}}
    ]
  }
}
```

### Uncompleted tasks assigned to anyone

```json
{
  "filter": {
    "and": [
      {"property": "Assignee", "people": {"is_not_empty": true}},
      {"property": "Complete", "checkbox": {"equals": false}}
    ]
  }
}
```

---

## Filter Properties Parameter

Limit which properties are returned in the response:

```bash
curl -s -X POST "https://api.notion.com/v1/databases/{database_id}/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter_properties": ["Name", "Status", "Due Date"]
  }'
```

Or using property IDs:

```json
{
  "filter_properties": ["title", "abc123", "xyz789"]
}
```

---

## Limitations

1. **Nesting Depth**: Compound filters support up to 2 levels of nesting
2. **Relation Rollups**: Formulas depending on relations with >25 references only evaluate 25 items
3. **Multi-layer Rollups**: Rollups of rollups may produce incorrect results
4. **Case Sensitivity**: Text comparisons are case-sensitive
5. **Date Precision**: Date comparisons use millisecond precision when times are included
