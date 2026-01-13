# Logseq Write Operations Reference

## Overview

This document details all available write operations for Logseq graphs via the HTTP API.

## Operations Summary

| Operation | Description | Returns |
|-----------|-------------|---------|
| `create_page(title)` | Create new page | `dict` |
| `get_or_create_page(title)` | Get or create page | `dict` |
| `delete_page(title)` | Delete page | `bool` |
| `create_block(parent, content)` | Create block | `dict` |
| `update_block(uuid, content)` | Update block | `dict` |
| `delete_block(uuid)` | Delete block | `bool` |
| `append_to_page(title, content)` | Append to page | `dict` |
| `set_property(uuid, key, value)` | Set property | `bool` |
| `set_properties(uuid, props)` | Set multiple properties | `bool` |
| `remove_property(uuid, key)` | Remove property | `bool` |
| `add_tag(uuid, tag)` | Add tag | `bool` |
| `add_tags(uuid, tags)` | Add multiple tags | `bool` |
| `remove_tag(uuid, tag)` | Remove tag | `bool` |
| `sync_notes(title, notes)` | Sync notes with timestamp | `dict` |

## Detailed Operations

### create_page(title, content=None, properties=None)

Creates a new page in the graph.

**Parameters**:
- `title` (str): Page title (required)
- `content` (str): Initial content for first block
- `properties` (dict): Page properties

**Returns**:
```python
{
    "uuid": "page-uuid",
    "name": "PageTitle",
    "properties": {...}
}
```

**Example**:
```python
# Simple page
page = writer.create_page("Meeting Notes")

# Page with properties
page = writer.create_page(
    "Project Alpha",
    properties={"status": "Active", "owner": "John"}
)

# Page with initial content
page = writer.create_page(
    "Daily Log",
    content="## Today's Tasks\n- Task 1\n- Task 2"
)
```

**Errors**:
- `DuplicateError`: Page already exists

---

### get_or_create_page(title, properties=None)

Gets an existing page or creates it if it doesn't exist.

**Parameters**:
- `title` (str): Page title
- `properties` (dict): Properties for new page only

**Returns**: Page data

**Example**:
```python
# Idempotent operation - safe to call multiple times
page = writer.get_or_create_page("My Notes")
```

---

### delete_page(title)

Deletes a page and all its blocks.

**Parameters**:
- `title` (str): Page title

**Returns**: `True` if deleted

**Example**:
```python
writer.delete_page("Old Notes")
```

**Errors**:
- `NotFoundError`: Page doesn't exist

---

### create_block(parent, content, properties=None, sibling=False)

Creates a new block under a parent.

**Parameters**:
- `parent` (str): Parent UUID or page title
- `content` (str): Block content
- `properties` (dict): Block properties
- `sibling` (bool): Create as sibling instead of child

**Returns**:
```python
{
    "uuid": "block-uuid",
    "content": "Block content",
    "properties": {...}
}
```

**Example**:
```python
# Add child block
block = writer.create_block(page_uuid, "Child content")

# Add sibling block
sibling = writer.create_block(block_uuid, "Sibling content", sibling=True)

# Add block with properties
task = writer.create_block(
    page_uuid,
    "Complete report",
    properties={"status": "TODO", "priority": "High"}
)
```

---

### update_block(uuid, content)

Updates the content of an existing block.

**Parameters**:
- `uuid` (str): Block UUID
- `content` (str): New content

**Returns**: Updated block data

**Example**:
```python
writer.update_block("abc-123", "Updated content here")
```

---

### delete_block(uuid)

Deletes a block and all its children.

**Parameters**:
- `uuid` (str): Block UUID

**Returns**: `True` if deleted

**Example**:
```python
writer.delete_block("abc-123")
```

**Errors**:
- `NotFoundError`: Block doesn't exist

---

### append_to_page(title, content)

Appends content to the end of a page.

**Parameters**:
- `title` (str): Page title
- `content` (str): Content to append

**Returns**: Created block data

**Example**:
```python
# Add new content to existing page
writer.append_to_page("Daily Log", "- New entry at end")

# Creates page if it doesn't exist
writer.append_to_page("New Page", "First content")
```

---

### set_property(uuid, key, value, property_type=None)

Sets a property on a block.

**Parameters**:
- `uuid` (str): Block UUID
- `key` (str): Property name
- `value` (any): Property value
- `property_type` (str): Type hint (number, date, checkbox)

**Returns**: `True` if set

**Example**:
```python
# String property
writer.set_property(uuid, "author", "John Doe")

# Number property
writer.set_property(uuid, "rating", 5, property_type="number")

# Checkbox property
writer.set_property(uuid, "done", True, property_type="checkbox")

# Date property
writer.set_property(uuid, "due", "2024-01-15", property_type="date")
```

---

### set_properties(uuid, properties)

Sets multiple properties at once.

**Parameters**:
- `uuid` (str): Block UUID
- `properties` (dict): Key-value pairs

**Returns**: `True` if all set

**Example**:
```python
writer.set_properties(uuid, {
    "author": "Jane Doe",
    "rating": 4,
    "status": "Published"
})
```

---

### remove_property(uuid, key)

Removes a property from a block.

**Parameters**:
- `uuid` (str): Block UUID
- `key` (str): Property name

**Returns**: `True` if removed

**Example**:
```python
writer.remove_property(uuid, "temporary-field")
```

---

### add_tag(uuid, tag)

Adds a tag to a block's content.

**Parameters**:
- `uuid` (str): Block UUID
- `tag` (str): Tag name (without #)

**Returns**: `True` if added

**Example**:
```python
writer.add_tag(uuid, "Important")
# Block content: "My note" -> "My note #Important"
```

---

### add_tags(uuid, tags)

Adds multiple tags to a block.

**Parameters**:
- `uuid` (str): Block UUID
- `tags` (list): List of tag names

**Returns**: `True` if added

**Example**:
```python
writer.add_tags(uuid, ["Book", "Fiction", "Favorite"])
```

---

### sync_notes(title, notes, page_prefix="Claude Notes")

Syncs notes with timestamp to a dedicated page.

**Parameters**:
- `title` (str): Note title
- `notes` (str): Note content
- `page_prefix` (str): Prefix for page path

**Returns**: Created block data

**Example**:
```python
# Creates page "Claude Notes/Meeting Summary"
writer.sync_notes(
    "Meeting Summary",
    """
Key decisions:
- Approved budget
- Set deadline for Q2
- Assigned tasks to team
"""
)
```

## Error Handling

| Exception | Cause | Recovery |
|-----------|-------|----------|
| `ConnectionError` | Cannot reach Logseq | Check if Logseq is running |
| `AuthError` | Invalid token | Verify LOGSEQ_API_TOKEN |
| `DuplicateError` | Resource exists | Use `get_or_create_*` |
| `NotFoundError` | Resource missing | Verify UUID/title |
| `ValidationError` | Invalid data | Check parameter types |

## HTTP API Reference

### Raw API Calls

```python
# Direct HTTP call
import urllib.request
import json

def logseq_api(method, args=[]):
    req = urllib.request.Request(
        "http://127.0.0.1:12315/api",
        data=json.dumps({"method": method, "args": args}).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["result"]

# Create page
logseq_api("logseq.Editor.createPage", ["Title", {}, {"createFirstBlock": True}])

# Insert block
logseq_api("logseq.Editor.insertBlock", ["parent-uuid", "Content", {}])
```
