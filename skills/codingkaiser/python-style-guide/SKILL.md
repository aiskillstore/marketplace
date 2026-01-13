---
name: python-style-guide
description: Comprehensive Python programming guidelines based on Google's Python Style Guide. Use when Claude needs to write Python code, review Python code for style issues, refactor Python code, or provide Python programming guidance. Covers language rules (imports, exceptions, type annotations), style rules (naming conventions, formatting, docstrings), and best practices for clean, maintainable Python code.
license: Complete terms in LICENSE.txt
---

# Python Style Guide

Comprehensive guidelines for writing clean, maintainable Python code based on [Google's Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Core Philosophy

**BE CONSISTENT.** Match the style of the code around you. Use these guidelines as defaults, but always prioritize consistency with existing code.

## Language Rules

### Imports

Use `import` statements for packages and modules only, not for individual classes or functions.

**Yes:**
```python
from doctor.who import jodie
import sound_effects.utils
```

**No:**
```python
from sound_effects.utils import EffectsRegistry  # Don't import classes directly
```

#### Import Formatting

- Group imports: standard library, third-party, application-specific
- Alphabetize within each group
- Use absolute imports (not relative imports)
- One import per line (except for multiple items from `typing` or `collections.abc`)

```python
# Standard library
import os
import sys

# Third-party
import numpy as np
import tensorflow as tf

# Application-specific
from myproject.backend import api_utils
```

### Exceptions

Use exceptions appropriately. Do not suppress errors with bare `except:` clauses.

**Yes:**
```python
try:
    result = risky_operation()
except ValueError as e:
    logging.error(f"Invalid value: {e}")
    raise
```

**No:**
```python
try:
    result = risky_operation()
except:  # Too broad, hides bugs
    pass
```

### Type Annotations

Annotate all function signatures. Type annotations improve code readability and catch errors early.

**General rules:**
- Annotate all public APIs
- Use built-in types (`list`, `dict`, `set`) instead of `typing.List`, etc. (Python 3.9+)
- Import typing symbols directly: `from typing import Any, Union`
- Use `None` instead of `type(None)` or `NoneType`

```python
def fetch_data(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch data from URL."""
    ...

def process_items(items: list[str]) -> None:
    """Process a list of items."""
    ...
```

### Default Argument Values

Never use mutable objects as default values in function definitions.

**Yes:**
```python
def foo(a: int, b: list[int] | None = None) -> None:
    if b is None:
        b = []
```

**No:**
```python
def foo(a: int, b: list[int] = []) -> None:  # Mutable default - WRONG!
    b.append(a)
```

### True/False Evaluations

Use implicit false where possible. Empty sequences, `None`, and `0` are false in boolean contexts.

**Yes:**
```python
if not users:  # Preferred
if not some_dict:
if value:
```

**No:**
```python
if len(users) == 0:  # Verbose
if users == []:
if value == True:  # Never compare to True/False explicitly
```

### Comprehensions & Generators

Use comprehensions and generators for simple cases. Keep them readable.

**Yes:**
```python
result = [x for x in data if x > 0]
squares = (x**2 for x in range(10))
```

**No:**
```python
# Too complex
result = [
    x.strip().lower() for x in data 
    if x and len(x) > 5 and not x.startswith('#')
    for y in x.split(',') if y
]  # Use a regular loop instead
```

### Lambda Functions

Use lambdas for one-liners only. For anything complex, define a proper function.

**Yes:**
```python
sorted(data, key=lambda x: x.timestamp)
```

**Acceptable but prefer named function:**
```python
def get_timestamp(item):
    return item.timestamp

sorted(data, key=get_timestamp)
```

## Style Rules

### Line Length

Maximum line length: 80 characters. Exceptions allowed for imports, URLs, and long strings that can't be broken.

### Indentation

Use 4 spaces per indentation level. Never use tabs.

For hanging indents, align wrapped elements vertically or use 4-space hanging indent:

```python
# Aligned with opening delimiter
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# Hanging indent (4 spaces)
foo = long_function_name(
    var_one, var_two, var_three,
    var_four)
```

### Blank Lines

- Two blank lines between top-level definitions
- One blank line between method definitions
- Use blank lines sparingly within functions to show logical sections

### Naming Conventions

| Type | Convention | Examples |
|------|-----------|----------|
| Packages/Modules | `lower_with_under` | `my_module.py` |
| Classes | `CapWords` | `MyClass` |
| Functions/Methods | `lower_with_under()` | `my_function()` |
| Constants | `CAPS_WITH_UNDER` | `MAX_SIZE` |
| Variables | `lower_with_under` | `my_var` |
| Private | `_leading_underscore` | `_private_var` |

**Avoid:**
- Single character names except for counters/iterators (`i`, `j`, `k`)
- Dashes in any name
- `__double_leading_and_trailing_underscore__` (reserved for Python)

### Comments and Docstrings

#### Docstring Format

Use Google-style docstrings for all public modules, functions, classes, and methods.

**Function docstring:**
```python
def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """Fetches rows from a Smalltable.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle. String keys will be UTF-8 encoded.

    Args:
        table_handle: An open smalltable.Table instance.
        keys: A sequence of strings representing the key of each table
            row to fetch. String keys will be UTF-8 encoded.
        require_all_keys: If True, raise ValueError if any key is missing.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings.

    Raises:
        IOError: An error occurred accessing the smalltable.
        ValueError: A key is missing and require_all_keys is True.
    """
    ...
```

**Class docstring:**
```python
class SampleClass:
    """Summary of class here.

    Longer class information...
    Longer class information...

    Attributes:
        likes_spam: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(self, likes_spam: bool = False):
        """Initializes the instance based on spam preference.

        Args:
            likes_spam: Defines if instance exhibits this preference.
        """
        self.likes_spam = likes_spam
        self.eggs = 0
```

#### Block and Inline Comments

- Use complete sentences with proper capitalization
- Block comments indent to the same level as the code
- Inline comments should be separated by at least 2 spaces
- Use inline comments sparingly

```python
# Block comment explaining the following code.
# Can span multiple lines.
x = x + 1  # Inline comment (use sparingly)
```

### Strings

Use f-strings for formatting (Python 3.6+).

**Yes:**
```python
x = f"name: {name}; score: {score}"
```

**Acceptable:**
```python
x = "name: %s; score: %d" % (name, score)
x = "name: {}; score: {}".format(name, score)
```

**No:**
```python
x = "name: " + name + "; score: " + str(score)  # Avoid + for formatting
```

#### Logging

Use `%` formatting for logging, not f-strings (allows lazy evaluation):

```python
logging.info("Request from %s resulted in %d", ip_address, status_code)
```

### Files and Resources

Always use context managers (`with` statements) for file operations:

```python
with open("file.txt") as f:
    data = f.read()
```

### Statements

Generally avoid multiple statements on one line.

**Yes:**
```python
if foo:
    bar()
```

**No:**
```python
if foo: bar()  # Avoid
```

### Main

For executable scripts, use:

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

### Function Length

Keep functions focused and reasonably sized. If a function exceeds about 40 lines, consider splitting it unless it remains very readable.

## Type Annotation Details

### Forward Declarations

Use string quotes for forward references:

```python
class MyClass:
    def method(self) -> "MyClass":
        return self
```

### Type Aliases

Create aliases for complex types:

```python
from typing import TypeAlias

ConnectionOptions: TypeAlias = dict[str, str]
Address: TypeAlias = tuple[str, int]
Server: TypeAlias = tuple[Address, ConnectionOptions]
```

### TypeVars

Use descriptive names for TypeVars:

```python
from typing import TypeVar

_T = TypeVar("_T")  # Good: private, unconstrained
AddableType = TypeVar("AddableType", int, float, str)  # Good: descriptive
```

### Generics

Always specify type parameters for generic types:

**Yes:**
```python
def get_names(employee_ids: list[int]) -> dict[int, str]:
    ...
```

**No:**
```python
def get_names(employee_ids: list) -> dict:  # Missing type parameters
    ...
```

### Imports for Typing

Import typing symbols directly:

```python
from collections.abc import Mapping, Sequence
from typing import Any, Union

# Use built-in types for containers (Python 3.9+)
def foo(items: list[str]) -> dict[str, int]:
    ...
```

## Common Patterns

### Properties

Use properties for simple attribute access:

```python
class Square:
    def __init__(self, side: float):
        self._side = side
    
    @property
    def area(self) -> float:
        return self._side ** 2
```

### Conditional Expressions

Use ternary operators for simple conditions:

```python
x = "yes" if condition else "no"
```

### Context Managers

Create custom context managers when appropriate:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwargs):
    resource = acquire_resource(*args, **kwargs)
    try:
        yield resource
    finally:
        release_resource(resource)
```

## Linting

Run `pylint` on all Python code. Suppress warnings only when necessary with clear explanations:

```python
dict = 'something'  # pylint: disable=redefined-builtin
```

## Summary

When writing Python code:

1. Use type annotations for all functions
2. Follow naming conventions consistently
3. Write clear docstrings for all public APIs
4. Keep functions focused and reasonably sized
5. Use comprehensions for simple cases
6. Prefer implicit false in boolean contexts
7. Use f-strings for formatting
8. Always use context managers for resources
9. Run pylint and fix issues
10. **BE CONSISTENT** with existing code

## Additional Resources

For detailed reference on specific topics, see:

- **references/advanced_types.md** - Advanced type annotation patterns including Protocol, TypedDict, Literal, ParamSpec, and more
- **references/antipatterns.md** - Common Python mistakes and their fixes
- **references/docstring_examples.md** - Comprehensive docstring examples for all Python constructs
