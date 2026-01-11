# Logseq Write Safety Guidelines

## Overview

Writing to Logseq modifies user data. Follow these guidelines to ensure safe operations.

## Core Principles

### 1. Verify Before Modify

Always confirm the target exists before modifying:

```python
# Good - check first
page = client.get_page("My Page")
if page:
    writer.update_block(page["uuid"], "New content")

# Bad - assume it exists
writer.update_block(unknown_uuid, "New content")  # May fail silently
```

### 2. Prefer Append Over Replace

When adding content, append rather than overwrite:

```python
# Good - append new content
writer.append_to_page("Notes", "New entry")

# Risky - replaces all content
writer.update_block(first_block_uuid, "All new content")
```

### 3. Use Idempotent Operations

Prefer operations that are safe to run multiple times:

```python
# Good - idempotent
page = writer.get_or_create_page("My Page")

# Not idempotent - fails on second run
page = writer.create_page("My Page")  # Raises DuplicateError
```

## Delete Operations

### Never Delete Without Confirmation

In automated scripts, add safety checks:

```python
def safe_delete_block(uuid):
    # Get block first
    block = client.get_block(uuid)
    if not block:
        raise ValueError(f"Block {uuid} not found")

    # Check if it has children
    if block.get("children"):
        raise ValueError(f"Block has {len(block['children'])} children")

    # Now safe to delete
    writer.delete_block(uuid)
```

### Avoid Bulk Deletes

```python
# Dangerous - don't do this
for block in all_blocks:
    writer.delete_block(block["uuid"])

# Better - be selective
target_blocks = [b for b in all_blocks if should_delete(b)]
for block in target_blocks[:10]:  # Limit batch size
    writer.delete_block(block["uuid"])
```

## Property Operations

### Validate Property Types

```python
def safe_set_property(uuid, key, value, expected_type):
    # Validate type
    if expected_type == "number" and not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")

    if expected_type == "checkbox" and not isinstance(value, bool):
        raise ValueError(f"{key} must be boolean")

    writer.set_property(uuid, key, value, property_type=expected_type)
```

### Don't Overwrite System Properties

```python
# System properties to avoid modifying directly
SYSTEM_PROPERTIES = [
    "id", "uuid", "created-at", "updated-at",
    "block/uuid", "block/page", "block/parent"
]

def safe_set_property(uuid, key, value):
    if key in SYSTEM_PROPERTIES:
        raise ValueError(f"Cannot modify system property: {key}")
    writer.set_property(uuid, key, value)
```

## Page Operations

### Handle Namespaced Pages Carefully

```python
# Namespaced pages are hierarchy
# "Project/Tasks" and "Project/Notes" are different

def create_namespaced_page(namespace, name):
    full_title = f"{namespace}/{name}"

    # Check parent namespace exists
    parent = client.get_page(namespace)
    if not parent:
        # Create parent first or warn user
        print(f"Warning: Parent namespace '{namespace}' doesn't exist")

    return writer.create_page(full_title)
```

### Avoid Duplicate Pages

```python
def create_unique_page(base_title):
    """Create page with unique title if base exists."""
    title = base_title
    counter = 1

    while client.get_page(title):
        title = f"{base_title} ({counter})"
        counter += 1

    return writer.create_page(title)
```

## Content Formatting

### Escape Special Characters

```python
def safe_content(text):
    """Escape characters that have special meaning in Logseq."""
    # Escape double brackets if not intended as links
    if "[[" in text and not is_intended_link(text):
        text = text.replace("[[", "\\[\\[")

    # Escape hash if not intended as tag
    if text.startswith("#") and not is_intended_tag(text):
        text = "\\" + text

    return text
```

### Validate Markdown

```python
def safe_markdown(content):
    """Basic validation of markdown content."""
    # Check for unclosed code blocks
    if content.count("```") % 2 != 0:
        raise ValueError("Unclosed code block")

    # Check for unclosed brackets
    if content.count("[[") != content.count("]]"):
        raise ValueError("Mismatched page references")

    return content
```

## Error Recovery

### Implement Retry Logic

```python
import time

def retry_operation(operation, max_retries=3, delay=1):
    """Retry an operation with exponential backoff."""
    last_error = None

    for attempt in range(max_retries):
        try:
            return operation()
        except ConnectionError as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))

    raise last_error
```

### Handle Partial Failures

```python
def bulk_create_blocks(parent, contents):
    """Create multiple blocks, tracking failures."""
    results = {"success": [], "failed": []}

    for content in contents:
        try:
            block = writer.create_block(parent, content)
            results["success"].append(block)
        except Exception as e:
            results["failed"].append({"content": content, "error": str(e)})

    return results
```

## Rate Limiting

### Don't Spam the API

```python
import time

def batch_operations(operations, delay=0.1):
    """Execute operations with delay between each."""
    results = []

    for op in operations:
        result = op()
        results.append(result)
        time.sleep(delay)

    return results
```

### Use Batching When Possible

```python
# Instead of many individual calls
for item in items:
    writer.set_property(uuid, item["key"], item["value"])

# Consider combining into single content update
content_parts = [f"{k}:: {v}" for k, v in properties.items()]
writer.update_block(uuid, "\n".join(content_parts))
```

## Logging and Auditing

### Log All Write Operations

```python
import logging

logger = logging.getLogger("logseq-writer")

class AuditedWriter(LogseqWriter):
    def create_page(self, title, **kwargs):
        logger.info(f"Creating page: {title}")
        result = super().create_page(title, **kwargs)
        logger.info(f"Created page: {result.get('uuid')}")
        return result

    def delete_block(self, uuid):
        logger.warning(f"Deleting block: {uuid}")
        return super().delete_block(uuid)
```

## Testing

### Use Test Graphs

```python
# Create a test graph for development
TEST_PAGE_PREFIX = "__test__"

def create_test_page(title):
    return writer.create_page(f"{TEST_PAGE_PREFIX}/{title}")

def cleanup_test_pages():
    # Clean up test pages after testing
    pages = client.list_pages()
    for page in pages:
        if page["title"].startswith(TEST_PAGE_PREFIX):
            writer.delete_page(page["title"])
```

## Checklist

Before deploying write operations:

- [ ] Verified on test graph first
- [ ] Added error handling for all operations
- [ ] Implemented retry logic for network issues
- [ ] Added logging for audit trail
- [ ] Validated all user inputs
- [ ] Checked for duplicate/existing resources
- [ ] Limited batch sizes
- [ ] Added rate limiting if needed
- [ ] Documented expected behavior
