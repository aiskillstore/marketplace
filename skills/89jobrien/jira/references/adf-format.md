---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: jira
---

# Atlassian Document Format (ADF) Reference

Jira Cloud API v3 uses ADF for rich text fields like `description` and `comment.body`.

## Basic Structure

Every ADF document has this structure:

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    // Array of block nodes
  ]
}
```

## Block Nodes

### Paragraph

```json
{
  "type": "paragraph",
  "content": [
    { "type": "text", "text": "Plain text here" }
  ]
}
```

### Heading

```json
{
  "type": "heading",
  "attrs": { "level": 2 },
  "content": [
    { "type": "text", "text": "Heading Text" }
  ]
}
```

Levels: 1-6

### Bullet List

```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Item 1" }]
        }
      ]
    },
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Item 2" }]
        }
      ]
    }
  ]
}
```

### Ordered List

```json
{
  "type": "orderedList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [{ "type": "text", "text": "Step 1" }]
        }
      ]
    }
  ]
}
```

### Code Block

```json
{
  "type": "codeBlock",
  "attrs": { "language": "python" },
  "content": [
    { "type": "text", "text": "def hello():\n    print('Hello')" }
  ]
}
```

### Blockquote

```json
{
  "type": "blockquote",
  "content": [
    {
      "type": "paragraph",
      "content": [{ "type": "text", "text": "Quoted text" }]
    }
  ]
}
```

### Rule (Horizontal Line)

```json
{
  "type": "rule"
}
```

## Inline Formatting (Marks)

Add `marks` array to text nodes for formatting:

### Bold

```json
{
  "type": "text",
  "text": "Bold text",
  "marks": [{ "type": "strong" }]
}
```

### Italic

```json
{
  "type": "text",
  "text": "Italic text",
  "marks": [{ "type": "em" }]
}
```

### Code (Inline)

```json
{
  "type": "text",
  "text": "code snippet",
  "marks": [{ "type": "code" }]
}
```

### Link

```json
{
  "type": "text",
  "text": "Click here",
  "marks": [
    {
      "type": "link",
      "attrs": { "href": "https://example.com" }
    }
  ]
}
```

### Combined Marks

```json
{
  "type": "text",
  "text": "Bold and italic",
  "marks": [
    { "type": "strong" },
    { "type": "em" }
  ]
}
```

## Special Nodes

### Mention User

```json
{
  "type": "mention",
  "attrs": {
    "id": "account-id-here",
    "text": "@username"
  }
}
```

### Emoji

```json
{
  "type": "emoji",
  "attrs": {
    "shortName": ":thumbsup:",
    "text": "thumbs up"
  }
}
```

### Hard Break (Line Break)

```json
{
  "type": "hardBreak"
}
```

## Complete Examples

### Simple Comment

```json
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "This is a comment." }
        ]
      }
    ]
  }
}
```

### Issue Description with Formatting

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [{ "type": "text", "text": "Summary" }]
    },
    {
      "type": "paragraph",
      "content": [
        { "type": "text", "text": "This issue tracks " },
        { "type": "text", "text": "important", "marks": [{ "type": "strong" }] },
        { "type": "text", "text": " changes." }
      ]
    },
    {
      "type": "heading",
      "attrs": { "level": 2 },
      "content": [{ "type": "text", "text": "Steps" }]
    },
    {
      "type": "orderedList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{ "type": "text", "text": "First step" }]
            }
          ]
        },
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{ "type": "text", "text": "Second step" }]
            }
          ]
        }
      ]
    }
  ]
}
```

## Tips

1. Always wrap text in paragraph nodes for block content
2. The `version` must be `1`
3. Empty content arrays are invalid - omit the field or include content
4. Test complex ADF in Jira's editor first, then inspect the API response
