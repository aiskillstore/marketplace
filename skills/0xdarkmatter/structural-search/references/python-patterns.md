# Python Patterns

Complete pattern library for ast-grep in Python.

## Function Definitions

```bash
# Find function definitions
sg -p 'def $NAME($$$): $$$' --lang python

# Find async function definitions
sg -p 'async def $NAME($$$): $$$' --lang python

# Find class definitions
sg -p 'class $NAME: $$$' --lang python

# Find class with inheritance
sg -p 'class $NAME($_): $$$' --lang python
```

## Decorators

```bash
# Find any decorated functions
sg -p '@$_
def $NAME($$$): $$$' --lang python

# Find pytest fixtures
sg -p '@pytest.fixture
def $NAME($$$): $$$' --lang python

# Find Flask routes
sg -p '@app.route($_)
def $NAME($$$): $$$' --lang python

# Find property decorators
sg -p '@property
def $NAME($$$): $$$' --lang python

# Find classmethod/staticmethod
sg -p '@classmethod
def $NAME($$$): $$$' --lang python
```

## Imports

```bash
# Find standard imports
sg -p 'import $_' --lang python

# Find from imports
sg -p 'from $_ import $_' --lang python

# Find aliased imports
sg -p 'import $_ as $_' --lang python

# Find wildcard imports (anti-pattern)
sg -p 'from $_ import *' --lang python
```

## Control Flow

```bash
# Find try-except blocks
sg -p 'try:
    $$$
except $_:
    $$$' --lang python

# Find with statements (context managers)
sg -p 'with $_ as $_: $$$' --lang python

# Find list comprehensions
sg -p '[$_ for $_ in $_]' --lang python

# Find dict comprehensions
sg -p '{$_: $_ for $_ in $_}' --lang python

# Find generator expressions
sg -p '($_ for $_ in $_)' --lang python
```

## String Formatting

```bash
# Find f-strings
sg -p 'f"$$$"' --lang python

# Find .format() calls
sg -p '"$$$".format($$$)' --lang python

# Find % formatting (old style)
sg -p '"$$$" % $_' --lang python
```

## Common Patterns

```bash
# Find main block
sg -p 'if __name__ == "__main__":
    $$$' --lang python

# Find dataclass definitions
sg -p '@dataclass
class $NAME:
    $$$' --lang python

# Find type hints
sg -p 'def $NAME($$$) -> $_: $$$' --lang python

# Find assert statements
sg -p 'assert $_' --lang python

# Find raise statements
sg -p 'raise $_' --lang python
```

## Testing Patterns

```bash
# Find test functions
sg -p 'def test_$NAME($$$): $$$' --lang python

# Find pytest parametrize
sg -p '@pytest.mark.parametrize($_)
def $NAME($$$): $$$' --lang python

# Find mock patches
sg -p '@patch($_)
def $NAME($$$): $$$' --lang python
```
