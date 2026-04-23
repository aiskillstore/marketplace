# Notion Property Types Reference

This document covers database property schemas and page property values in the Notion API.

## Property Schema Objects (Database Columns)

Property schemas define the structure of database columns. Every database requires exactly one `title` property.

### Title

```json
{
  "Name": {
    "id": "title",
    "type": "title",
    "title": {}
  }
}
```

Required. One per database. Controls the title displayed at the top of pages.

### Rich Text

```json
{
  "Description": {
    "type": "rich_text",
    "rich_text": {}
  }
}
```

### Number

```json
{
  "Price": {
    "type": "number",
    "number": {
      "format": "dollar"
    }
  }
}
```

Format options:
- Numbers: `number`, `number_with_commas`, `percent`
- Currencies: `dollar`, `euro`, `pound`, `yen`, `ruble`, `rupee`, `won`, `yuan`, `real`, `lira`, `canadian_dollar`, `australian_dollar`, `singapore_dollar`, `hong_kong_dollar`, `new_zealand_dollar`, `krona`, `norwegian_krone`, `mexican_peso`, `rand`, `new_taiwan_dollar`, `danish_krone`, `zloty`, `baht`, `forint`, `koruna`, `shekel`, `chilean_peso`, `philippine_peso`, `dirham`, `colombian_peso`, `riyal`, `ringgit`, `leu`, `argentine_peso`, `uruguayan_peso`, `peruvian_sol`

### Select

```json
{
  "Status": {
    "type": "select",
    "select": {
      "options": [
        {"id": "uuid", "name": "To Do", "color": "red"},
        {"id": "uuid", "name": "In Progress", "color": "yellow"},
        {"id": "uuid", "name": "Done", "color": "green"}
      ]
    }
  }
}
```

Color options: `default`, `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`

### Multi-Select

```json
{
  "Tags": {
    "type": "multi_select",
    "multi_select": {
      "options": [
        {"id": "uuid", "name": "Tag1", "color": "blue"},
        {"id": "uuid", "name": "Tag2", "color": "green"}
      ]
    }
  }
}
```

Maximum 100 options.

### Status

```json
{
  "Project Status": {
    "type": "status",
    "status": {
      "options": [
        {"id": "uuid", "name": "Not started", "color": "default"},
        {"id": "uuid", "name": "In progress", "color": "blue"},
        {"id": "uuid", "name": "Done", "color": "green"}
      ],
      "groups": [
        {"id": "uuid", "name": "To-do", "color": "gray", "option_ids": ["..."]},
        {"id": "uuid", "name": "In progress", "color": "blue", "option_ids": ["..."]},
        {"id": "uuid", "name": "Complete", "color": "green", "option_ids": ["..."]}
      ]
    }
  }
}
```

**Note**: Creating new status properties via API is not supported.

### Date

```json
{
  "Due Date": {
    "type": "date",
    "date": {}
  }
}
```

### Checkbox

```json
{
  "Complete": {
    "type": "checkbox",
    "checkbox": {}
  }
}
```

### URL

```json
{
  "Website": {
    "type": "url",
    "url": {}
  }
}
```

### Email

```json
{
  "Contact": {
    "type": "email",
    "email": {}
  }
}
```

### Phone Number

```json
{
  "Phone": {
    "type": "phone_number",
    "phone_number": {}
  }
}
```

### People

```json
{
  "Assignee": {
    "type": "people",
    "people": {}
  }
}
```

### Files

```json
{
  "Attachments": {
    "type": "files",
    "files": {}
  }
}
```

### Relation

Single-direction relation:

```json
{
  "Related Tasks": {
    "type": "relation",
    "relation": {
      "database_id": "target-database-uuid",
      "type": "single_property"
    }
  }
}
```

Dual-direction relation:

```json
{
  "Related Tasks": {
    "type": "relation",
    "relation": {
      "database_id": "target-database-uuid",
      "type": "dual_property",
      "dual_property": {
        "synced_property_name": "Related Projects",
        "synced_property_id": "..."
      }
    }
  }
}
```

### Rollup

```json
{
  "Total Hours": {
    "type": "rollup",
    "rollup": {
      "relation_property_name": "Tasks",
      "relation_property_id": "...",
      "rollup_property_name": "Hours",
      "rollup_property_id": "...",
      "function": "sum"
    }
  }
}
```

Rollup functions:
- Aggregation: `count_all`, `count_values`, `count_unique_values`, `count_empty`, `count_not_empty`, `percent_empty`, `percent_not_empty`
- Numbers: `sum`, `average`, `median`, `min`, `max`, `range`
- Dates: `earliest_date`, `latest_date`, `date_range`
- Booleans: `checked`, `unchecked`, `percent_checked`, `percent_unchecked`
- Display: `show_original`, `show_unique`

### Formula

```json
{
  "Full Name": {
    "type": "formula",
    "formula": {
      "expression": "prop(\"First Name\") + \" \" + prop(\"Last Name\")"
    }
  }
}
```

### Created Time (Read-Only)

```json
{
  "Created": {
    "type": "created_time",
    "created_time": {}
  }
}
```

### Created By (Read-Only)

```json
{
  "Creator": {
    "type": "created_by",
    "created_by": {}
  }
}
```

### Last Edited Time (Read-Only)

```json
{
  "Updated": {
    "type": "last_edited_time",
    "last_edited_time": {}
  }
}
```

### Last Edited By (Read-Only)

```json
{
  "Editor": {
    "type": "last_edited_by",
    "last_edited_by": {}
  }
}
```

### Unique ID (Read-Only)

```json
{
  "ID": {
    "type": "unique_id",
    "unique_id": {
      "prefix": "PROJ"
    }
  }
}
```

---

## Property Value Objects (Page Properties)

Property values are used when creating or updating pages.

### Title Value

```json
{
  "Name": {
    "title": [
      {"type": "text", "text": {"content": "Page Title"}}
    ]
  }
}
```

### Rich Text Value

```json
{
  "Description": {
    "rich_text": [
      {"type": "text", "text": {"content": "Description text"}}
    ]
  }
}
```

### Number Value

```json
{
  "Price": {
    "number": 99.99
  }
}
```

### Select Value

```json
{
  "Status": {
    "select": {"name": "In Progress"}
  }
}
```

Or by ID:

```json
{
  "Status": {
    "select": {"id": "option-uuid"}
  }
}
```

### Multi-Select Value

```json
{
  "Tags": {
    "multi_select": [
      {"name": "Tag1"},
      {"name": "Tag2"}
    ]
  }
}
```

### Status Value

```json
{
  "Project Status": {
    "status": {"name": "In progress"}
  }
}
```

### Date Value

Single date:

```json
{
  "Due Date": {
    "date": {
      "start": "2024-12-31"
    }
  }
}
```

Date with time:

```json
{
  "Meeting": {
    "date": {
      "start": "2024-12-31T14:00:00.000Z",
      "time_zone": "America/New_York"
    }
  }
}
```

Date range:

```json
{
  "Sprint": {
    "date": {
      "start": "2024-01-01",
      "end": "2024-01-14"
    }
  }
}
```

### Checkbox Value

```json
{
  "Complete": {
    "checkbox": true
  }
}
```

### URL Value

```json
{
  "Website": {
    "url": "https://example.com"
  }
}
```

### Email Value

```json
{
  "Contact": {
    "email": "user@example.com"
  }
}
```

### Phone Number Value

```json
{
  "Phone": {
    "phone_number": "+1-555-123-4567"
  }
}
```

### People Value

```json
{
  "Assignee": {
    "people": [
      {"id": "user-uuid"}
    ]
  }
}
```

Maximum 100 users.

### Files Value

External files:

```json
{
  "Attachments": {
    "files": [
      {
        "name": "Document.pdf",
        "type": "external",
        "external": {"url": "https://example.com/doc.pdf"}
      }
    ]
  }
}
```

Uploaded files (use file upload API first):

```json
{
  "Attachments": {
    "files": [
      {
        "name": "Photo.jpg",
        "type": "file",
        "file": {"url": "https://..."}
      }
    ]
  }
}
```

**Note**: Updating files property replaces all existing files.

### Relation Value

```json
{
  "Related Tasks": {
    "relation": [
      {"id": "page-uuid-1"},
      {"id": "page-uuid-2"}
    ]
  }
}
```

Maximum 100 related pages.

### Rollup Value (Read-Only)

Rollup values are computed and cannot be set directly.

Response example:

```json
{
  "Total": {
    "type": "rollup",
    "rollup": {
      "type": "number",
      "number": 42,
      "function": "sum"
    }
  }
}
```

### Formula Value (Read-Only)

Formula values are computed and cannot be set directly.

Response example:

```json
{
  "Full Name": {
    "type": "formula",
    "formula": {
      "type": "string",
      "string": "John Doe"
    }
  }
}
```

Formula result types: `string`, `number`, `boolean`, `date`

### Created Time Value (Read-Only)

```json
{
  "Created": {
    "type": "created_time",
    "created_time": "2024-01-01T00:00:00.000Z"
  }
}
```

### Created By Value (Read-Only)

```json
{
  "Creator": {
    "type": "created_by",
    "created_by": {
      "object": "user",
      "id": "user-uuid"
    }
  }
}
```

### Last Edited Time Value (Read-Only)

```json
{
  "Updated": {
    "type": "last_edited_time",
    "last_edited_time": "2024-01-15T12:00:00.000Z"
  }
}
```

### Last Edited By Value (Read-Only)

```json
{
  "Editor": {
    "type": "last_edited_by",
    "last_edited_by": {
      "object": "user",
      "id": "user-uuid"
    }
  }
}
```

### Unique ID Value (Read-Only)

```json
{
  "ID": {
    "type": "unique_id",
    "unique_id": {
      "prefix": "PROJ",
      "number": 42
    }
  }
}
```

---

## Important Notes

### Property Value Limit

Property values in page objects have a **25 page reference limit**. Properties containing more than 25 page references (in `relation`, `people`, or `rollup` properties) only display the first 25 in standard responses.

Use the "Retrieve a page property" endpoint to get the complete list:

```bash
curl -s "https://api.notion.com/v1/pages/{page_id}/properties/{property_id}" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

### Read-Only Properties

These properties cannot be set via API:
- `created_time`
- `created_by`
- `last_edited_time`
- `last_edited_by`
- `rollup`
- `formula`
- `unique_id`

### Property References

Properties can be referenced by either:
- **Name**: `"Status"` (may change if user renames)
- **ID**: `"abc123"` (stable, recommended for integrations)

Get property IDs by retrieving the database schema.

### Null Values

To clear a property value, set it to `null`:

```json
{
  "Due Date": {
    "date": null
  }
}
```

For rich text/title, use an empty array:

```json
{
  "Description": {
    "rich_text": []
  }
}
```
