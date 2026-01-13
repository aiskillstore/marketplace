# Logseq Read Operations Reference

## Overview

This document details all available read operations in the Logseq client library.

## Operations Summary

| Operation | Description | Returns |
|-----------|-------------|---------|
| `get_graph_info()` | Graph metadata | `dict` |
| `get_page(title)` | Page by title | `dict` or `None` |
| `get_block(uuid)` | Block by UUID | `dict` or `None` |
| `list_pages()` | All pages | `list[dict]` |
| `search(query)` | Full-text search | `list[dict]` |
| `datalog_query(query)` | Execute Datalog | `list` |
| `get_backlinks(title)` | References to page | `list[dict]` |
| `get_page_properties(title)` | Page properties | `dict` |
| `get_block_properties(uuid)` | Block properties | `dict` |

## Detailed Operations

### get_graph_info()

Returns information about the current Logseq graph.

**Returns**:
```python
{
    "name": "my-graph",
    "path": "/path/to/graph",
    "type": "db"  # or "md"
}
```

**Example**:
```python
info = client.get_graph_info()
print(f"Working with graph: {info['name']}")
```

---

### get_page(title, include_children=True)

Retrieves a page by its title.

**Parameters**:
- `title` (str): Page title to fetch
- `include_children` (bool): Include child blocks (default: True)

**Returns**:
```python
{
    "title": "My Page",
    "uuid": "abc-123-def",
    "properties": {
        "created": "2024-01-01",
        "tags": ["important"]
    },
    "blocks": [  # if include_children=True
        {
            "uuid": "block-1",
            "content": "First block",
            "children": [...]
        }
    ]
}
```

**Example**:
```python
# Get full page with blocks
page = client.get_page("Project Notes")
if page:
    print(f"Page has {len(page.get('blocks', []))} top-level blocks")

# Get page metadata only (faster)
page = client.get_page("Project Notes", include_children=False)
```

---

### get_block(uuid, include_children=True)

Retrieves a block by its UUID.

**Parameters**:
- `uuid` (str): Block UUID
- `include_children` (bool): Include child blocks (default: True)

**Returns**:
```python
{
    "uuid": "abc-123",
    "content": "Block content here",
    "properties": {...},
    "children": [...]  # if include_children=True
}
```

**Example**:
```python
block = client.get_block("abc-123-def-456")
if block:
    print(f"Content: {block['content']}")
    for child in block.get('children', []):
        print(f"  - {child['content']}")
```

---

### list_pages(limit=None)

Lists all pages in the graph.

**Parameters**:
- `limit` (int): Maximum pages to return (default: all)

**Returns**:
```python
[
    {"title": "Page 1", "uuid": "..."},
    {"title": "Page 2", "uuid": "..."},
    ...
]
```

**Example**:
```python
# Get all pages
all_pages = client.list_pages()
print(f"Graph has {len(all_pages)} pages")

# Get first 10 pages
some_pages = client.list_pages(limit=10)
```

---

### search(query_text, limit=50)

Searches for blocks containing the specified text.

**Parameters**:
- `query_text` (str): Text to search for
- `limit` (int): Maximum results (default: 50)

**Returns**:
```python
[
    {
        "uuid": "...",
        "content": "...matching content...",
        "page": {"title": "Parent Page"}
    },
    ...
]
```

**Example**:
```python
results = client.search("meeting notes")
for result in results:
    print(f"Found in {result['page']['title']}: {result['content'][:50]}...")
```

---

### datalog_query(query, params=None)

Executes a raw Datalog query against the graph.

**Parameters**:
- `query` (str): Datalog query string
- `params` (list): Optional query parameters for `:in` clause

**Returns**: Raw query results (structure depends on query)

**Example**:
```python
# Simple query
titles = client.datalog_query('''
    [:find ?title
     :where [?p :block/title ?title]]
''')

# Query with parameters
books = client.datalog_query('''
    [:find (pull ?b [*])
     :in $ ?min-rating
     :where
     [?b :block/tags ?t]
     [?t :block/title "Book"]
     [?b :user.property/rating ?r]
     [(>= ?r ?min-rating)]]
''', [4])  # min rating = 4
```

---

### get_backlinks(title)

Gets all blocks that reference a specific page.

**Parameters**:
- `title` (str): Page title to find references to

**Returns**:
```python
[
    {
        "uuid": "...",
        "content": "See [[Page Title]] for more",
        "page": {"title": "Referencing Page"}
    },
    ...
]
```

**Example**:
```python
refs = client.get_backlinks("Project Alpha")
print(f"'{title}' is referenced in {len(refs)} blocks:")
for ref in refs:
    print(f"  - {ref['page']['title']}")
```

---

### get_page_properties(title)

Gets the properties of a page.

**Parameters**:
- `title` (str): Page title

**Returns**:
```python
{
    "property-name": "value",
    "tags": ["tag1", "tag2"],
    "created": "2024-01-01"
}
```

**Example**:
```python
props = client.get_page_properties("My Book")
print(f"Author: {props.get('author', 'Unknown')}")
print(f"Rating: {props.get('rating', 'Unrated')}")
```

---

### get_block_properties(uuid)

Gets the properties of a specific block.

**Parameters**:
- `uuid` (str): Block UUID

**Returns**:
```python
{
    "status": "In Progress",
    "priority": "High",
    "due": "2024-12-31"
}
```

**Example**:
```python
props = client.get_block_properties("task-uuid")
status = props.get("status", "Unknown")
print(f"Task status: {status}")
```

## Error Handling

All operations can raise these exceptions:

| Exception | Cause |
|-----------|-------|
| `ConnectionError` | Cannot connect to Logseq |
| `AuthError` | Invalid or missing token |
| `NotFoundError` | Resource doesn't exist |
| `QueryError` | Query execution failed |

**Example**:
```python
try:
    page = client.get_page("My Page")
except client.ConnectionError:
    print("Cannot connect - is Logseq running?")
except client.AuthError:
    print("Invalid token")
```

## Performance Considerations

1. **Use specific queries** - `get_page()` with `include_children=False` is faster
2. **Batch operations** - Use single `datalog_query()` for multiple items
3. **Limit results** - Use `limit` parameter when possible
4. **Cache results** - Store frequently accessed data locally
