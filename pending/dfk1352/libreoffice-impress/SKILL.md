---
name: libreoffice-impress
description: Use when creating, editing, formatting, or extracting LibreOffice Impress (.odp) presentations via UNO, including slides, content placement, tables, charts, media, notes, master pages, find & replace, and snapshots.
---

# LibreOffice Impress

## Overview
Use the `impress` modules to create and edit Impress
presentations with UNO-backed operations. Prefer these high-level functions
instead of raw UNO calls or a CLI.

## Quick Reference
- `core.create_presentation(path)`
- `core.get_slide_count(path)`
- `core.export_presentation(path, output_path, format)`
- `slides.add_slide(path, index=None, layout="BLANK")`
- `slides.delete_slide(path, index)`
- `slides.move_slide(path, from_index, to_index)`
- `slides.duplicate_slide(path, index)`
- `slides.get_slide_inventory(path, index)`
- `content.set_title(path, slide_index, text)`
- `content.set_body(path, slide_index, text)`
- `content.add_text_box(path, slide_index, text, x_cm, y_cm, width_cm, height_cm)`
- `content.add_image(path, slide_index, image_path, x_cm, y_cm, width_cm=10.0, height_cm=10.0)`
- `content.add_shape(path, slide_index, shape_type, x_cm, y_cm, width_cm, height_cm, fill_color=None, line_color=None)`
- `tables.add_table(path, slide_index, rows, cols, x_cm, y_cm, width_cm, height_cm, data=None)`
- `tables.set_table_cell(path, slide_index, shape_index, row, col, text)`
- `tables.format_table_cell(path, slide_index, shape_index, row, col, bold=False, font_size=None, fill_color=None)`
- `charts.add_chart(path, slide_index, chart_type, data, x_cm, y_cm, width_cm, height_cm, title=None)`
- `media.add_audio(path, slide_index, media_path, x_cm, y_cm, width_cm, height_cm)`
- `media.add_video(path, slide_index, media_path, x_cm, y_cm, width_cm, height_cm)`
- `formatting.format_shape_text(path, slide_index, shape_index, bold=False, italic=False, underline=False, font_size=None, font_name=None, color=None, alignment=None)`
- `formatting.set_slide_background(path, slide_index, color)`
- `notes.set_notes(path, slide_index, text)`
- `notes.get_notes(path, slide_index)`
- `master.list_master_pages(path)`
- `master.apply_master_page(path, master_name)`
- `master.import_master_from_template(path, template_path)`
- `master.set_master_background(path, master_name, color)`
- `find_replace.find_replace(path, find, replace, match_case=False, whole_word=False)`
- `snapshot.snapshot_slide(doc_path, slide_index, output_path, width=1280, height=720)`
- `colors.resolve_color(color)`

## Usage Notes
- Use absolute file paths for presentations and media assets.
- Ensure the bundled modules are on `PYTHONPATH`.
  The modules are bundled under `scripts/` in this skill directory. Set:
  `PYTHONPATH=<skill_base_dir>/scripts` where `<skill_base_dir>` is the base
  directory reported when this skill was loaded (e.g. the path shown as
  "Base directory" in the skill output).
- Slide indices are zero-based.
- Position and size arguments use centimetres at the API boundary.
- Layouts: `BLANK`, `TITLE_SLIDE`, `TITLE_AND_CONTENT`, `TITLE_ONLY`,
  `TWO_CONTENT`, `CENTERED_TEXT`.
- Shape types: `rectangle`, `ellipse`, `triangle`, `line`, `arrow`.
- Chart types: `bar`, `line`, `pie`, `scatter`.
- Alignment values are case-insensitive. Unknown values raise `ValueError`.
- Color fields accept either a `0xRRGGBB` integer or a CSS color name string.

## Example: Create a Simple Deck
```python
from pathlib import Path

from impress.core import create_presentation, export_presentation
from impress.content import add_text_box, add_shape
from impress.formatting import format_shape_text, set_slide_background
from impress.slides import add_slide

output = Path("test-output/demo.odp").resolve()
create_presentation(str(output))

add_slide(str(output), layout="TITLE_SLIDE")
add_text_box(str(output), 1, "Quarterly Review", 2.0, 2.0, 16.0, 3.0)

shape_idx = add_shape(
    str(output),
    1,
    "rectangle",
    2.0,
    6.0,
    8.0,
    4.0,
    fill_color="lightsteelblue",
    line_color="black",
)

format_shape_text(
    str(output),
    1,
    shape_idx,
    bold=True,
    font_size=18,
    color="navy",
    alignment="center",
)

set_slide_background(str(output), 1, "white")
export_presentation(str(output), str(output.with_suffix(".pdf")), "pdf")
```

## Visual Snapshots

Use `snapshot.snapshot_slide()` to capture a slide as PNG for layout
verification. PNG export uses LibreOffice's CLI conversion pipeline.

```python
from impress.snapshot import snapshot_slide

result = snapshot_slide(str(doc_path), 0, "/tmp/slide1.png")
# result.file_path, result.width, result.height, result.dpi
```

**Parameters:**
- `doc_path`: Absolute path to the presentation.
- `slide_index`: Zero-based slide index.
- `output_path`: File path for the PNG output.
- `width`, `height`: Pixel dimensions (default: 1280x720).

**When to snapshot:**
- After applying master pages to confirm styling.
- After inserting charts or media to confirm layout.
- Before finalizing a deck for delivery.

**Cleanup:** Remove snapshot PNGs after verification. Do not let temporary
images accumulate.

```python
Path(result.file_path).unlink(missing_ok=True)
```

## Common Mistakes
- Passing relative paths (UNO loads absolute URLs).
- Using 1-based slide indices.
- Forgetting to create the document before inserting content.
- Passing lowercase layout names - layouts use UPPER_SNAKE_CASE
  (e.g., `BLANK`, `TITLE_SLIDE`).
- Passing uppercase shape types - shape types use lowercase
  (e.g., `rectangle`, `ellipse`).
