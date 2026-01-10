---
name: fiftyone-code-style
description: Write Python code following FiftyOne's official conventions. Use when contributing to FiftyOne, developing plugins, or writing code that integrates with FiftyOne's codebase.
---

# FiftyOne Code Style

## Module Template

```python
"""
Module description.

| Copyright 2017-2025, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
# Standard library
import logging
import os

# Third-party
import numpy as np

# eta (Voxel51 utilities)
import eta.core.utils as etau

# FiftyOne
import fiftyone.core.fields as fof
import fiftyone.core.labels as fol
import fiftyone.core.utils as fou

logger = logging.getLogger(__name__)


def public_function(arg):
    """Public API function."""
    return _helper(arg)


def _helper(arg):
    """Private helper (underscore prefix)."""
    return arg
```

## Import Organization

Four groups, alphabetized within each:

| Group | Example |
|-------|---------|
| 1. Standard library | `import logging`, `import os` |
| 2. Third-party | `import numpy as np`, `from PIL import Image` |
| 3. eta packages | `import eta.core.utils as etau` |
| 4. FiftyOne | `import fiftyone.core.labels as fol` |

### FiftyOne Import Aliases

| Module | Alias |
|--------|-------|
| `fiftyone` | `fo` |
| `fiftyone.core.labels` | `fol` |
| `fiftyone.core.fields` | `fof` |
| `fiftyone.core.media` | `fom` |
| `fiftyone.core.storage` | `fos` |
| `fiftyone.core.utils` | `fou` |
| `fiftyone.utils.image` | `foui` |
| `fiftyone.utils.video` | `fouv` |

## Docstrings (Google-Style)

### Function Docstring

```python
def get_operator(operator_uri, enabled=True):
    """Gets the operator with the given URI.

    Args:
        operator_uri: the operator URI
        enabled (True): whether to include only enabled operators (True) or
            only disabled operators (False) or all operators ("all")

    Returns:
        an :class:`fiftyone.operators.Operator`

    Raises:
        ValueError: if the operator is not found
    """
```

### Class Docstring

```python
class ImageMetadata(Metadata):
    """Class for storing metadata about image samples.

    Args:
        size_bytes (None): the size of the image on disk, in bytes
        mime_type (None): the MIME type of the image
        width (None): the width of the image, in pixels
        height (None): the height of the image, in pixels
    """
```

**Key patterns:**
- Args with defaults: `param (default): description`
- Multi-line descriptions: indent continuation
- Cross-references: `:class:`fiftyone.module.Class``

## Private Functions

```python
# Public API delegates to private helper
def build_for(cls, path_or_url, mime_type=None):
    """Builds a Metadata object for the given file."""
    if path_or_url.startswith("http"):
        return cls._build_for_url(path_or_url, mime_type=mime_type)
    return cls._build_for_local(path_or_url, mime_type=mime_type)

# Private: underscore prefix, focused purpose
def _build_for_local(cls, filepath, mime_type=None):
    """Internal helper for local files."""
    size_bytes = os.path.getsize(filepath)
    if mime_type is None:
        mime_type = etau.guess_mime_type(filepath)
    return cls(size_bytes=size_bytes, mime_type=mime_type)
```

## Lazy Imports

Use `fou.lazy_import()` for optional/heavy dependencies:

```python
# Basic lazy import
o3d = fou.lazy_import("open3d", callback=lambda: fou.ensure_package("open3d"))

# With ensure_import for pycocotools
mask_utils = fou.lazy_import(
    "pycocotools.mask", callback=lambda: fou.ensure_import("pycocotools")
)

# Internal module lazy import
fop = fou.lazy_import("fiftyone.core.plots.plotly")
```

**When to use:**
- Heavy packages (open3d, tensorflow, torch)
- Optional dependencies (pycocotools)
- Circular import prevention

## Guard Patterns

Use `hasattr()` for conditional behavior:

```python
# Check for optional attribute
if hasattr(label, "confidence"):
    if label.confidence is None or label.confidence < threshold:
        label = label.__class__()

# Check for config attribute
if hasattr(eval_info.config, "iscrowd"):
    crowd_attr = eval_info.config.iscrowd
else:
    crowd_attr = None

# Dynamic state initialization
if not hasattr(pb, "_next_idx"):
    pb._next_idx = 0
    pb._next_iters = []
```

## Error Handling

Use `logger.warning()` for non-fatal errors:

```python
# Non-fatal: warn and continue
try:
    for target in fo.config.logging_debug_targets.split(","):
        if logger_name := target.strip():
            loggers.append(logging.getLogger(logger_name))
except Exception as e:
    logger.warning(
        "Failed to parse logging debug targets '%s': %s",
        fo.config.logging_debug_targets,
        e,
    )

# Missing optional import
try:
    import resource
except ImportError as e:
    if warn_on_failure:
        logger.warning(e)
    return

# Graceful fallback
try:
    mask = etai.render_instance_image(dobj.mask, dobj.bounding_box, frame_size)
except:
    width, height = frame_size
    mask = np.zeros((height, width), dtype=bool)
```

## Avoid Redundant Implementations

Before writing new functions, check if FiftyOne already provides the functionality.

### Common Utilities in `fiftyone.core.utils` (fou)

| Function | Purpose |
|----------|---------|
| `fou.lazy_import()` | Lazy module loading |
| `fou.ensure_package()` | Install missing package |
| `fou.ensure_import()` | Verify import available |
| `fou.extract_kwargs_for_class()` | Split kwargs for class |
| `fou.load_xml_as_dict()` | Parse XML to dict |
| `fou.get_default_executor()` | Get thread pool executor |

### Common Utilities in `eta.core.utils` (etau)

| Function | Purpose |
|----------|---------|
| `etau.guess_mime_type()` | Detect file MIME type |
| `etau.is_str()` | Check if string |
| `etau.ensure_dir()` | Create directory if missing |
| `etau.ensure_basedir()` | Create parent directory |
| `etau.make_temp_dir()` | Create temp directory |

### Before Writing New Code

1. **Search existing modules** for similar functionality:
   ```bash
   grep -r "def your_function_name" fiftyone/
   grep -r "similar_keyword" fiftyone/core/utils.py
   ```

2. **Check these modules first:**
   - `fiftyone.core.utils` - General utilities
   - `fiftyone.core.storage` - File/cloud operations
   - `fiftyone.utils.*` - Format-specific utilities
   - `eta.core.utils` - Low-level helpers

3. **Red flags for redundancy:**
   - File path manipulation → check `os.path` or `etau`
   - JSON/dict operations → check `eta.core.serial`
   - Image operations → check `fiftyone.utils.image`
   - Type checking → check `etau.is_str()`, etc.

## Code Validation Checklist

Before submitting code, verify:

### Style Compliance
- [ ] Module has copyright header docstring
- [ ] Imports in 4 groups (stdlib → third-party → eta → fiftyone)
- [ ] Imports alphabetized within groups
- [ ] FiftyOne imports use standard aliases (fol, fou, etc.)
- [ ] Logger defined as `logger = logging.getLogger(__name__)`
- [ ] Google-style docstrings with Args/Returns/Raises
- [ ] Private functions prefixed with `_`

### Code Quality
- [ ] No redundant implementations (checked existing utils)
- [ ] Heavy imports use `fou.lazy_import()`
- [ ] Optional attributes use `hasattr()` guards
- [ ] Non-fatal errors use `logger.warning()`
- [ ] No bare `except:` (specify exception type when possible)

### Testing
```bash
# Run linting
pylint fiftyone/your_module.py

# Check style
black --check fiftyone/your_module.py

# Run tests
pytest tests/unittests/your_test.py -v
```

## Quick Reference

| Pattern | Convention |
|---------|------------|
| Module structure | Docstring → imports → logger → public → private → classes |
| Private functions | `_prefix`, module-level, small & focused |
| Docstrings | Google-style with Args/Returns/Raises |
| Error handling | `try/except` + `logger.warning()` for non-fatal |
| Lazy imports | `fou.lazy_import()` for optional deps |
| Guard patterns | `hasattr()` checks for conditional behavior |
| Import aliases | `fol`, `fof`, `fom`, `fos`, `fou` |
| Constants | `UPPERCASE`, private: `_UPPERCASE` |
| Class inheritance | Explicit `class Foo(object):` |
| Redundancy check | Search `fou`, `etau`, existing modules first |
