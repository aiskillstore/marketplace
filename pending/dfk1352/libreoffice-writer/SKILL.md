---
name: libreoffice-writer
description: Use when creating, editing, formatting, or extracting LibreOffice Writer (.odt) documents via UNO, including text insertion, tables, images, metadata, and paragraph styling.
---

# LibreOffice Writer

## Overview
Use the `writer` modules to create and edit Writer documents
with UNO-backed operations. Prefer the high-level functions in these modules
instead of raw UNO calls or a CLI.

## Quick Reference
- `core.create_document(path)`
- `core.read_document_text(path)`
- `text.insert_text(path, text, position=None)`
- `text.replace_text(path, old, new)`
- `formatting.apply_formatting(path, formatting, selection="all")`
- `tables.add_table(path, rows, cols, data=None, position=None)`
- `images.insert_image(path, image_path, width=None, height=None, position=None)`
- `metadata.set_metadata(path, metadata)`
- `metadata.get_metadata(path)`
- `snapshot.snapshot_page(doc_path, output_path, page=1, dpi=150)`
- `colors.resolve_color(color)`

## Usage Notes
- Use absolute file paths for documents and images.
- Ensure the bundled modules are on `PYTHONPATH`.
  The modules are bundled under `scripts/` in this skill directory. Set:
  `PYTHONPATH=<skill_base_dir>/scripts` where `<skill_base_dir>` is the base
  directory reported when this skill was loaded (e.g. the path shown as
  "Base directory" in the skill output).
- Import modules directly from `writer`; do not search for
  a separate CLI or external skill registry.
- `position` is a character index; `0` inserts at the start, `None` at the end.
- For title/body styling, insert text, then call
  `apply_formatting(..., selection="last_paragraph")`.
- Color fields accept either a `0xRRGGBB` integer or a CSS color name string.

## Example: Create a Simple Report
```python
from pathlib import Path

from writer.core import create_document
from writer.formatting import apply_formatting
from writer.metadata import set_metadata
from writer.images import insert_image
from writer.tables import add_table
from writer.text import insert_text

output = Path("test-output/report.odt").resolve()
create_document(str(output))

set_metadata(
    str(output),
    {"title": "Quarterly Report", "author": "Ops"},
)

insert_text(str(output), "Quarterly Report", position=None)
apply_formatting(
    str(output),
    {"bold": True, "font_size": 18, "align": "center"},
    selection="last_paragraph",
)
insert_text(str(output), "\n\nSummary", position=None)
insert_text(str(output), "[Draft] ", position=0)
apply_formatting(
    str(output),
    {"bold": True, "font_size": 12, "align": "left"},
    selection="last_paragraph",
)

add_table(
    str(output),
    2,
    2,
    [["Metric", "Value"], ["Revenue", "$1M"]],
    position=5,
)

insert_image(
    str(output),
    "/abs/path/to/logo.png",
    width=5000,
    height=5000,
    position=12,
)
```

## Common Mistakes
- Forgetting to create the document before inserting content.
- Passing a relative path (UNO loads absolute URLs).
- Looking for a CLI instead of using the Python modules.
- Using `position` without accounting for existing text length.

## Visual Snapshots

Use `snapshot.snapshot_page()` to capture a page as PNG for layout verification.

```python
from writer.snapshot import snapshot_page

result = snapshot_page(str(doc_path), "/tmp/page1.png", page=1, dpi=150)
# result.file_path, result.width, result.height, result.dpi
```

**Parameters:**
- `doc_path`: Absolute path to the Writer document.
- `output_path`: File path for the PNG output.
- `page`: 1-indexed page number (default: 1).
- `dpi`: Export resolution (default: 150).

**When to snapshot:**
- After inserting images to confirm alignment.
- After applying formatting to verify layout.
- Before finalizing a document for delivery.

**Cleanup:** Remove snapshot PNGs after verification. Do not let temporary
images accumulate.

```python
Path(result.file_path).unlink(missing_ok=True)
```

**Visual Red Flags:**
- Overlapping elements (text over images, tables over images).
- Cut-off text or tables at page boundaries.
- Misaligned objects (images not centered, tables not aligned).
- Inconsistent spacing between paragraphs.
- Low contrast or unreadable text.
