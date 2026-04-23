# Notion Block Types Reference

This document provides comprehensive documentation for all supported block types in the Notion API.

## Block Structure

Every block contains these common fields:

```json
{
  "object": "block",
  "id": "uuid",
  "type": "block_type",
  "parent": {"type": "page_id", "page_id": "..."},
  "created_time": "2024-01-01T00:00:00.000Z",
  "last_edited_time": "2024-01-01T00:00:00.000Z",
  "created_by": {"object": "user", "id": "..."},
  "last_edited_by": {"object": "user", "id": "..."},
  "archived": false,
  "in_trash": false,
  "has_children": false,
  "{type}": { /* type-specific properties */ }
}
```

## Text Blocks

### Paragraph

```json
{
  "type": "paragraph",
  "paragraph": {
    "rich_text": [{"type": "text", "text": {"content": "Paragraph text"}}],
    "color": "default"
  }
}
```

Supports children (nested blocks).

### Headings

```json
{
  "type": "heading_1",
  "heading_1": {
    "rich_text": [{"type": "text", "text": {"content": "Heading 1"}}],
    "color": "default",
    "is_toggleable": false
  }
}
```

Types: `heading_1`, `heading_2`, `heading_3`

When `is_toggleable: true`, headings can contain children.

### Quote

```json
{
  "type": "quote",
  "quote": {
    "rich_text": [{"type": "text", "text": {"content": "Quote text"}}],
    "color": "default"
  }
}
```

Supports children.

### Callout

```json
{
  "type": "callout",
  "callout": {
    "rich_text": [{"type": "text", "text": {"content": "Callout text"}}],
    "icon": {"type": "emoji", "emoji": "💡"},
    "color": "gray_background"
  }
}
```

Supports children. Icon can be emoji or file.

### Code

```json
{
  "type": "code",
  "code": {
    "rich_text": [{"type": "text", "text": {"content": "const x = 1;"}}],
    "caption": [],
    "language": "javascript"
  }
}
```

Supported languages: `abap`, `arduino`, `bash`, `basic`, `c`, `clojure`, `coffeescript`, `cpp`, `csharp`, `css`, `dart`, `diff`, `docker`, `elixir`, `elm`, `erlang`, `flow`, `fortran`, `fsharp`, `gherkin`, `glsl`, `go`, `graphql`, `groovy`, `haskell`, `html`, `java`, `javascript`, `json`, `julia`, `kotlin`, `latex`, `less`, `lisp`, `livescript`, `lua`, `makefile`, `markdown`, `markup`, `matlab`, `mermaid`, `nix`, `objective-c`, `ocaml`, `pascal`, `perl`, `php`, `plain text`, `powershell`, `prolog`, `protobuf`, `python`, `r`, `reason`, `ruby`, `rust`, `sass`, `scala`, `scheme`, `scss`, `shell`, `sql`, `swift`, `typescript`, `vb.net`, `verilog`, `vhdl`, `visual basic`, `webassembly`, `xml`, `yaml`, `java/c/c++/c#`

### Equation

```json
{
  "type": "equation",
  "equation": {
    "expression": "E = mc^2"
  }
}
```

Uses LaTeX/KaTeX syntax.

## List Blocks

### Bulleted List Item

```json
{
  "type": "bulleted_list_item",
  "bulleted_list_item": {
    "rich_text": [{"type": "text", "text": {"content": "List item"}}],
    "color": "default"
  }
}
```

Supports children (nested list items).

### Numbered List Item

```json
{
  "type": "numbered_list_item",
  "numbered_list_item": {
    "rich_text": [{"type": "text", "text": {"content": "List item"}}],
    "color": "default"
  }
}
```

Supports children.

### To-Do

```json
{
  "type": "to_do",
  "to_do": {
    "rich_text": [{"type": "text", "text": {"content": "Task"}}],
    "checked": false,
    "color": "default"
  }
}
```

Supports children.

### Toggle

```json
{
  "type": "toggle",
  "toggle": {
    "rich_text": [{"type": "text", "text": {"content": "Toggle header"}}],
    "color": "default"
  }
}
```

Supports children (the toggle content).

## Media Blocks

### Image

```json
{
  "type": "image",
  "image": {
    "type": "external",
    "external": {"url": "https://example.com/image.png"},
    "caption": []
  }
}
```

Or for uploaded files:

```json
{
  "type": "image",
  "image": {
    "type": "file",
    "file": {"url": "https://...", "expiry_time": "..."},
    "caption": []
  }
}
```

Supported formats: `.bmp`, `.gif`, `.heic`, `.jpeg`, `.jpg`, `.png`, `.svg`, `.tif`, `.tiff`

### Video

```json
{
  "type": "video",
  "video": {
    "type": "external",
    "external": {"url": "https://www.youtube.com/watch?v=..."},
    "caption": []
  }
}
```

Supported formats: `.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv`, plus YouTube links

### Audio

```json
{
  "type": "audio",
  "audio": {
    "type": "external",
    "external": {"url": "https://example.com/audio.mp3"},
    "caption": []
  }
}
```

Supported formats: `.mp3`, `.wav`, `.ogg`, `.oga`, `.m4a`

### File

```json
{
  "type": "file",
  "file": {
    "type": "external",
    "external": {"url": "https://example.com/doc.pdf"},
    "caption": [],
    "name": "Document.pdf"
  }
}
```

### PDF

```json
{
  "type": "pdf",
  "pdf": {
    "type": "external",
    "external": {"url": "https://example.com/document.pdf"},
    "caption": []
  }
}
```

### Bookmark

```json
{
  "type": "bookmark",
  "bookmark": {
    "url": "https://example.com",
    "caption": []
  }
}
```

### Embed

```json
{
  "type": "embed",
  "embed": {
    "url": "https://example.com/embed",
    "caption": []
  }
}
```

**Note**: Embed rendering may differ from Notion app due to lack of iFramely integration.

### Link Preview

```json
{
  "type": "link_preview",
  "link_preview": {
    "url": "https://example.com"
  }
}
```

**Read-only** - cannot be created via API.

## Structural Blocks

### Divider

```json
{
  "type": "divider",
  "divider": {}
}
```

### Table of Contents

```json
{
  "type": "table_of_contents",
  "table_of_contents": {
    "color": "default"
  }
}
```

### Breadcrumb

```json
{
  "type": "breadcrumb",
  "breadcrumb": {}
}
```

### Column List and Column

```json
{
  "type": "column_list",
  "column_list": {}
}
```

Column list contains column children:

```json
{
  "type": "column",
  "column": {}
}
```

Columns contain actual content blocks. **Note**: Column list must have at least 2 columns.

### Table

```json
{
  "type": "table",
  "table": {
    "table_width": 3,
    "has_column_header": true,
    "has_row_header": false
  }
}
```

Table contains `table_row` children:

```json
{
  "type": "table_row",
  "table_row": {
    "cells": [
      [{"type": "text", "text": {"content": "Cell 1"}}],
      [{"type": "text", "text": {"content": "Cell 2"}}],
      [{"type": "text", "text": {"content": "Cell 3"}}]
    ]
  }
}
```

**Note**: `table_width` can only be set at creation, not updated later.

## Special Blocks

### Child Page

```json
{
  "type": "child_page",
  "child_page": {
    "title": "Page Title"
  }
}
```

**Read-only** - use Create Page endpoint to create pages.

### Child Database

```json
{
  "type": "child_database",
  "child_database": {
    "title": "Database Title"
  }
}
```

**Read-only** - use Create Database endpoint to create databases.

### Synced Block

Original synced block:

```json
{
  "type": "synced_block",
  "synced_block": {
    "synced_from": null
  }
}
```

Reference to synced block:

```json
{
  "type": "synced_block",
  "synced_block": {
    "synced_from": {
      "type": "block_id",
      "block_id": "original-block-id"
    }
  }
}
```

**Note**: API doesn't support updating synced block content.

### Template (Deprecated)

```json
{
  "type": "template",
  "template": {
    "rich_text": [{"type": "text", "text": {"content": "Template button"}}]
  }
}
```

**Deprecated** as of March 27, 2023 - use database templates instead.

### Unsupported

```json
{
  "type": "unsupported",
  "unsupported": {}
}
```

Represents blocks not supported by the API.

## Color Options

Available colors for blocks that support the `color` property:

- `default`
- `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`
- `gray_background`, `brown_background`, `orange_background`, `yellow_background`, `green_background`, `blue_background`, `purple_background`, `pink_background`, `red_background`

## Blocks That Support Children

The following block types can contain nested blocks:
- `paragraph`
- `bulleted_list_item`
- `numbered_list_item`
- `to_do`
- `toggle`
- `quote`
- `callout`
- `column_list` (contains `column` children)
- `column` (contains content blocks)
- `table` (contains `table_row` children)
- `synced_block`
- `template`
- `heading_1`, `heading_2`, `heading_3` (when `is_toggleable: true`)
- `child_page` (conceptually, via separate API calls)
- `child_database` (conceptually, via separate API calls)
