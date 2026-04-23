# Notion Rich Text Reference

This document provides comprehensive documentation for rich text objects in the Notion API.

## Rich Text Array Structure

Rich text in Notion is represented as an array of rich text objects. Each block or property that supports formatted text uses this structure:

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {"content": "Hello "},
      "annotations": {"bold": false, "italic": false, "strikethrough": false, "underline": false, "code": false, "color": "default"},
      "plain_text": "Hello ",
      "href": null
    },
    {
      "type": "text",
      "text": {"content": "world", "link": {"url": "https://example.com"}},
      "annotations": {"bold": true, "italic": false, "strikethrough": false, "underline": false, "code": false, "color": "default"},
      "plain_text": "world",
      "href": "https://example.com"
    }
  ]
}
```

## Common Fields

All rich text objects contain:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | The type of rich text object |
| `annotations` | object | Styling applied to the text |
| `plain_text` | string | Plain text without formatting |
| `href` | string or null | URL if the text is a link |

---

## Rich Text Types

### Text

Basic text content with optional link:

```json
{
  "type": "text",
  "text": {
    "content": "Link text",
    "link": {"url": "https://example.com"}
  },
  "annotations": { /* ... */ },
  "plain_text": "Link text",
  "href": "https://example.com"
}
```

Without link:

```json
{
  "type": "text",
  "text": {
    "content": "Plain text"
  },
  "annotations": { /* ... */ },
  "plain_text": "Plain text",
  "href": null
}
```

### Equation

Inline mathematical expressions using LaTeX/KaTeX:

```json
{
  "type": "equation",
  "equation": {
    "expression": "E = mc^2"
  },
  "annotations": { /* ... */ },
  "plain_text": "E = mc^2",
  "href": null
}
```

### Mention

References to other Notion objects or users.

#### User Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "user",
    "user": {
      "object": "user",
      "id": "user-uuid",
      "name": "John Doe",
      "avatar_url": "https://...",
      "type": "person",
      "person": {"email": "john@example.com"}
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "@John Doe",
  "href": "https://www.notion.so/user-uuid"
}
```

#### Page Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "page",
    "page": {
      "id": "page-uuid"
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "Page Title",
  "href": "https://www.notion.so/page-uuid"
}
```

**Note**: If the integration doesn't have access to the mentioned page, only the ID is returned.

#### Database Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "database",
    "database": {
      "id": "database-uuid"
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "Database Title",
  "href": "https://www.notion.so/database-uuid"
}
```

#### Date Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "date",
    "date": {
      "start": "2024-01-15",
      "end": null,
      "time_zone": null
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "January 15, 2024",
  "href": null
}
```

With date range:

```json
{
  "type": "mention",
  "mention": {
    "type": "date",
    "date": {
      "start": "2024-01-15",
      "end": "2024-01-20",
      "time_zone": null
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "January 15, 2024 → January 20, 2024",
  "href": null
}
```

#### Link Preview Mention

```json
{
  "type": "mention",
  "mention": {
    "type": "link_preview",
    "link_preview": {
      "url": "https://github.com/..."
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "https://github.com/...",
  "href": "https://github.com/..."
}
```

#### Template Mention (Date)

Used in template blocks for dynamic dates:

```json
{
  "type": "mention",
  "mention": {
    "type": "template_mention",
    "template_mention": {
      "type": "template_mention_date",
      "template_mention_date": "today"
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "@today",
  "href": null
}
```

Template date options: `today`, `now`

#### Template Mention (User)

Used in template blocks for dynamic user references:

```json
{
  "type": "mention",
  "mention": {
    "type": "template_mention",
    "template_mention": {
      "type": "template_mention_user",
      "template_mention_user": "me"
    }
  },
  "annotations": { /* ... */ },
  "plain_text": "@me",
  "href": null
}
```

---

## Annotations

Annotations control text styling:

```json
{
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `bold` | boolean | Bold text |
| `italic` | boolean | Italic text |
| `strikethrough` | boolean | Strikethrough text |
| `underline` | boolean | Underlined text |
| `code` | boolean | Inline code styling |
| `color` | string | Text or background color |

### Color Options

Text colors:
- `default`
- `gray`
- `brown`
- `orange`
- `yellow`
- `green`
- `blue`
- `purple`
- `pink`
- `red`

Background colors:
- `gray_background`
- `brown_background`
- `orange_background`
- `yellow_background`
- `green_background`
- `blue_background`
- `purple_background`
- `pink_background`
- `red_background`

---

## Creating Rich Text

### Simple Text

```json
[
  {
    "type": "text",
    "text": {"content": "Simple text"}
  }
]
```

### Formatted Text

```json
[
  {
    "type": "text",
    "text": {"content": "Bold and italic"},
    "annotations": {"bold": true, "italic": true}
  }
]
```

### Mixed Formatting

```json
[
  {"type": "text", "text": {"content": "Normal "}},
  {"type": "text", "text": {"content": "bold"}, "annotations": {"bold": true}},
  {"type": "text", "text": {"content": " and "}},
  {"type": "text", "text": {"content": "italic"}, "annotations": {"italic": true}},
  {"type": "text", "text": {"content": " text."}}
]
```

### Text with Link

```json
[
  {"type": "text", "text": {"content": "Check out "}},
  {
    "type": "text",
    "text": {"content": "this link", "link": {"url": "https://example.com"}}
  },
  {"type": "text", "text": {"content": " for more info."}}
]
```

### Code Styling

```json
[
  {"type": "text", "text": {"content": "Use the "}},
  {"type": "text", "text": {"content": "console.log()"}, "annotations": {"code": true}},
  {"type": "text", "text": {"content": " function."}}
]
```

### Colored Text

```json
[
  {
    "type": "text",
    "text": {"content": "Important!"},
    "annotations": {"color": "red", "bold": true}
  }
]
```

### With Background Color

```json
[
  {
    "type": "text",
    "text": {"content": "Highlighted text"},
    "annotations": {"color": "yellow_background"}
  }
]
```

### User Mention

```json
[
  {"type": "text", "text": {"content": "Assigned to "}},
  {
    "type": "mention",
    "mention": {
      "type": "user",
      "user": {"id": "user-uuid"}
    }
  }
]
```

### Page Mention

```json
[
  {"type": "text", "text": {"content": "See also: "}},
  {
    "type": "mention",
    "mention": {
      "type": "page",
      "page": {"id": "page-uuid"}
    }
  }
]
```

### Date Mention

```json
[
  {"type": "text", "text": {"content": "Due: "}},
  {
    "type": "mention",
    "mention": {
      "type": "date",
      "date": {"start": "2024-12-31"}
    }
  }
]
```

### Inline Equation

```json
[
  {"type": "text", "text": {"content": "The formula is "}},
  {"type": "equation", "equation": {"expression": "x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}"}},
  {"type": "text", "text": {"content": "."}}
]
```

---

## Limits

| Type | Limit |
|------|-------|
| Rich text content | 2000 characters per rich text object |
| Rich text array | 100 items max |
| Equations | 1000 characters |

---

## Reading Rich Text

When processing rich text from API responses, you can:

1. **Get plain text**: Concatenate all `plain_text` values
2. **Preserve formatting**: Process each object and apply `annotations`
3. **Extract links**: Check `href` field or `text.link.url`

Example (JavaScript):

```javascript
function getPlainText(richTextArray) {
  return richTextArray.map(rt => rt.plain_text).join('');
}

function getLinks(richTextArray) {
  return richTextArray
    .filter(rt => rt.href)
    .map(rt => ({text: rt.plain_text, url: rt.href}));
}
```

Example (bash with jq):

```bash
# Get plain text
echo "$rich_text_json" | jq -r '[.[].plain_text] | join("")'

# Get all links
echo "$rich_text_json" | jq '[.[] | select(.href != null) | {text: .plain_text, url: .href}]'
```
