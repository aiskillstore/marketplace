# Response Structure for ChatGPT Apps

## Overview

ChatGPT Apps require specific metadata in tool responses to render widgets. This document details the exact structure needed.

---

## Complete Response Structure

```python
types.CallToolResult(
    content=[
        types.TextContent(
            type="text",
            text="Human-readable response text"
        )
    ],
    structuredContent={
        # Structured data for the widget
        "key": "value",
        "items": [...]
    },
    _meta={
        "openai.com/widget": types.EmbeddedResource(
            type="resource",
            resource=types.TextResourceContents(
                uri="ui://widget/my-widget.html",
                mimeType="text/html+skybridge",
                text=WIDGET_HTML_STRING,
                title="Widget Title",
            ),
        )
    },
)
```

---

## Component Details

### content

Human-readable text shown alongside the widget. Keep it brief.

```python
content=[
    types.TextContent(
        type="text",
        text="Here's the book table of contents."
    )
]
```

### structuredContent

Data passed to the widget. The widget receives this via ChatGPT's bridge.

```python
structuredContent={
    "book": {
        "title": "The Art of Building AI Apps",
        "author": "Claude & Friends"
    },
    "chapters": [
        {"number": 1, "title": "Introduction"},
        {"number": 2, "title": "LLM Basics"}
    ]
}
```

### _meta["openai.com/widget"]

The embedded widget resource. This is REQUIRED for widget rendering.

```python
_meta={
    "openai.com/widget": types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri="ui://widget/book-reader.html",
            mimeType="text/html+skybridge",  # CRITICAL
            text=WIDGET_HTML,
            title="Book Reader",
        ),
    )
}
```

---

## MIME Type: text/html+skybridge

**CRITICAL**: The MIME type MUST be `text/html+skybridge` for widgets to render.

```python
MIME_TYPE = "text/html+skybridge"
```

Standard `text/html` will NOT work.

---

## Tool Metadata Functions

### listing_meta()

Metadata shown in the ChatGPT tool listing (before tool is called):

```python
def listing_meta() -> dict:
    """Tool metadata for ChatGPT tool listing."""
    return {
        "openai.com/widget": {
            "uri": "ui://widget/main.html",
            "title": "My Widget"
        }
    }
```

### response_meta()

Metadata included in tool response (after tool is called):

```python
def response_meta() -> dict:
    """Response metadata with embedded widget."""
    return {
        "openai.com/widget": types.EmbeddedResource(
            type="resource",
            resource=types.TextResourceContents(
                uri="ui://widget/main.html",
                mimeType="text/html+skybridge",
                text=WIDGET_HTML,
                title="My Widget",
            ),
        )
    }
```

---

## Tool Decorator Usage

```python
@mcp.tool(
    annotations={
        "title": "Open Book",
        "readOnlyHint": True,
        "openWorldHint": False,
    },
    _meta=listing_meta(),  # For tool listing
)
def open_book() -> types.CallToolResult:
    """Open the book and show table of contents."""
    return types.CallToolResult(
        content=[
            types.TextContent(
                type="text",
                text="The book is now open!"
            )
        ],
        structuredContent={
            "book_title": "The Art of Building AI Apps",
            "chapters": [
                {"number": 1, "title": "Introduction"},
            ]
        },
        _meta=response_meta(),  # For response
    )
```

---

## Widget Registry Pattern

Manage multiple widgets with a registry:

```python
WIDGETS = {
    "table-of-contents": {
        "uri": "ui://widget/toc.html",
        "html": TOC_WIDGET_HTML,
        "title": "Table of Contents",
    },
    "chapter-reader": {
        "uri": "ui://widget/reader.html",
        "html": READER_WIDGET_HTML,
        "title": "Chapter Reader",
    },
}

def _embedded_widget_resource(widget_id: str) -> types.EmbeddedResource:
    """Create embedded widget resource."""
    widget = WIDGETS[widget_id]
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget["uri"],
            mimeType="text/html+skybridge",
            text=widget["html"],
            title=widget["title"],
        ),
    )
```

---

## Resource Handler

Register a resource handler to serve widgets:

```python
@mcp.resource(
    uri="ui://widget/{widget_name}.html",
    name="Widget Resource",
    mime_type="text/html+skybridge"
)
def widget_resource(widget_name: str) -> str:
    """Serve widget HTML."""
    key = widget_name
    if key in WIDGETS:
        return WIDGETS[key]["html"]
    # Fallback to default widget
    return WIDGETS["table-of-contents"]["html"]
```

---

## Debugging Response Structure

Add debug logging to verify structure:

```python
@mcp.tool(_meta=listing_meta())
def my_tool() -> types.CallToolResult:
    result = types.CallToolResult(
        content=[types.TextContent(type="text", text="Success!")],
        structuredContent={"data": "value"},
        _meta=response_meta(),
    )

    # Debug: Print response structure
    print(f"Response _meta: {result._meta}")
    print(f"Widget HTML length: {len(WIDGETS['main']['html'])}")

    return result
```

---

## Common Mistakes

### Missing _meta

```python
# WRONG - No widget will render
return types.CallToolResult(
    content=[types.TextContent(type="text", text="Done")],
)

# CORRECT
return types.CallToolResult(
    content=[types.TextContent(type="text", text="Done")],
    _meta=response_meta(),
)
```

### Wrong MIME Type

```python
# WRONG - Widget won't render
mimeType="text/html"

# CORRECT
mimeType="text/html+skybridge"
```

### Missing EmbeddedResource Type

```python
# WRONG
_meta={
    "openai.com/widget": {
        "uri": "...",
        "html": "..."
    }
}

# CORRECT
_meta={
    "openai.com/widget": types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(...)
    )
}
```