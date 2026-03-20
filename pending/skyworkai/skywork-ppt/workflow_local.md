# Local PPTX Operations Workflow (Layer 3)

No backend or token needed — uses `python-pptx` to operate on local `.pptx` files directly.

---

## Install Dependencies

```bash
pip install python-pptx
```

---

## Trigger Keywords

When the user expresses the following intents, use this workflow (instead of calling the backend API):

| User Intent | Example Keywords |
|----------|-----------|
| View file info | View PPT page count, how many pages, pptx info |
| Delete specific slides | Delete slide N, remove slide 3, delete slide 3, remove page 5 |
| Reorder slides | Reorder PPT, rearrange slide order, reorder slides |
| Extract slides | Extract slides 1-3, export certain slides, extract slides |
| Merge files | Merge two PPTs, merge pptx, combine a and b |

---

## Unified Entry Point

All operations are done via `scripts/local_pptx_ops.py`:

```bash
$PYTHON_CMD scripts/local_pptx_ops.py <subcommand> [arguments]
```

---

## Subcommand Details

### info — View file info

```bash
$PYTHON_CMD scripts/local_pptx_ops.py info --file my.pptx
```

Output: file path, total slides, dimensions, title of each slide.

---

### delete — Delete slides

```bash
# Delete slide 3
$PYTHON_CMD scripts/local_pptx_ops.py delete --file my.pptx --slides 3

# Delete slides 3, 5, 7-9, overwrite the original file
$PYTHON_CMD scripts/local_pptx_ops.py delete --file my.pptx --slides 3,5,7-9

# Save to a new file after deletion (don't overwrite the original)
$PYTHON_CMD scripts/local_pptx_ops.py delete --file my.pptx --slides 3,5,7-9 -o trimmed.pptx
```

**Note**:
- Page numbers are 1-based (slide 1 = 1)
- Supports comma-separated and `-` ranges, e.g. `1,3,5-8,10`
- If `-o` is not specified, the original file is overwritten

---

### reorder — Reorder slide order

```bash
# Move original slide 2 to position 1, slide 1 to position 2 (rest unchanged)
$PYTHON_CMD scripts/local_pptx_ops.py reorder --file my.pptx --order 2,1,3,4,5

# Save to a new file
$PYTHON_CMD scripts/local_pptx_ops.py reorder --file my.pptx --order 2,1,3,4,5 -o reordered.pptx
```

**Note**: `--order` must include all page numbers — no omissions or duplicates.

---

### extract — Extract specific slides

```bash
# Extract slides 1 through 3
$PYTHON_CMD scripts/local_pptx_ops.py extract --file my.pptx --slides 1-3 -o subset.pptx

# Extract slides 1, 3, 5
$PYTHON_CMD scripts/local_pptx_ops.py extract --file my.pptx --slides 1,3,5 -o subset.pptx
```

Extracted result is saved as a new file (original file is not modified).

---

### merge — Merge multiple files

```bash
# Merge two files
$PYTHON_CMD scripts/local_pptx_ops.py merge --files a.pptx b.pptx -o merged.pptx

# Merge three or more
$PYTHON_CMD scripts/local_pptx_ops.py merge --files a.pptx b.pptx c.pptx -o merged.pptx
```

**Note**: The slide dimensions of the first file are used as the standard; shapes are preserved as much as possible during merging, but complex animations/video effects may be lost.

---

## Agent Decision Logic

User intent → Route selection:

```
User says "Generate a PPT about X"
  → Layer 1: scripts/run_ppt_write.py (call backend to generate)

User says "Delete slide 3 from this PPT" / "Merge these two pptx" / "Extract the first 5 slides"
  → Layer 3: scripts/local_pptx_ops.py (local operation, no token needed)
```

---

## FAQ

**Q: Do page numbers change after deletion?**
A: Yes. After deletion, page numbers are renumbered starting from 1. If you need to delete multiple slides, it's recommended to pass them all at once (`--slides 3,5,7`) rather than running multiple times.

**Q: What if styles are wrong after merging?**
A: Merging uses deep-copy of the shape tree; themes/masters come from the first file. If there are significant style differences, manual adjustments in PowerPoint are recommended.

**Q: Does python-pptx support deleting slides?**
A: Not natively. This tool operates on the underlying XML (`_sldIdLst`), consistent with common python-pptx community approaches.
