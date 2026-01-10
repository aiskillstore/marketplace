# Property-Based Testing with Hypothesis

Test properties of code with generated inputs, not just examples.

## Why Property Testing?

```python
# Example-based: tests specific cases
def test_sort_examples():
    assert sort([3, 1, 2]) == [1, 2, 3]
    assert sort([]) == []
    assert sort([1]) == [1]

# Property-based: tests properties for ANY input
from hypothesis import given
from hypothesis import strategies as st

@given(st.lists(st.integers()))
def test_sort_properties(lst):
    result = sort(lst)
    # Property 1: Same length
    assert len(result) == len(lst)
    # Property 2: Sorted order
    assert all(result[i] <= result[i+1] for i in range(len(result)-1))
    # Property 3: Same elements
    assert sorted(lst) == result
```

## Basic Hypothesis Usage

```python
from hypothesis import given, settings, assume
from hypothesis import strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Addition is commutative."""
    assert a + b == b + a

@given(st.text())
def test_reverse_twice(s):
    """Reversing twice returns original."""
    assert s[::-1][::-1] == s

@given(st.lists(st.integers(), min_size=1))
def test_max_in_list(lst):
    """Max is an element of the list."""
    assert max(lst) in lst
```

## Common Strategies

```python
from hypothesis import strategies as st

# Primitives
st.integers()                    # Any integer
st.integers(min_value=0)         # Non-negative
st.floats(allow_nan=False)       # Floats without NaN
st.text()                        # Unicode strings
st.text(alphabet="abc", max_size=10)
st.booleans()
st.none()
st.binary()                      # Bytes

# Collections
st.lists(st.integers())          # List of ints
st.lists(st.text(), min_size=1, max_size=10)
st.sets(st.integers())
st.frozensets(st.text())
st.dictionaries(st.text(), st.integers())

# Tuples
st.tuples(st.integers(), st.text())   # Fixed structure
st.tuples(st.integers(), st.integers(), st.integers())

# Optional / One of
st.one_of(st.integers(), st.text())   # Either type
st.none() | st.integers()              # Optional int
st.sampled_from(["red", "green", "blue"])  # Enum-like
```

## Building Custom Strategies

```python
from hypothesis import strategies as st
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

# Strategy for User objects
user_strategy = st.builds(
    User,
    name=st.text(min_size=1, max_size=50),
    age=st.integers(min_value=0, max_value=150),
    email=st.emails()
)

@given(user_strategy)
def test_user_validation(user):
    assert validate_user(user)


# Composite strategies for complex logic
@st.composite
def sorted_lists(draw):
    """Generate pre-sorted lists."""
    lst = draw(st.lists(st.integers()))
    return sorted(lst)

@given(sorted_lists())
def test_binary_search(sorted_lst):
    if sorted_lst:
        target = sorted_lst[len(sorted_lst) // 2]
        assert binary_search(sorted_lst, target) != -1


# Dependent strategies
@st.composite
def list_and_index(draw):
    """Generate a list and valid index into it."""
    lst = draw(st.lists(st.integers(), min_size=1))
    index = draw(st.integers(min_value=0, max_value=len(lst)-1))
    return lst, index

@given(list_and_index())
def test_indexing(data):
    lst, index = data
    # This will never raise IndexError
    assert lst[index] is not None or lst[index] is None
```

## Filtering and Assumptions

```python
from hypothesis import given, assume
from hypothesis import strategies as st

# Filter strategy (preferred when possible)
@given(st.integers().filter(lambda x: x % 2 == 0))
def test_even_numbers(n):
    assert n % 2 == 0

# assume() for runtime filtering
@given(st.integers(), st.integers())
def test_division(a, b):
    assume(b != 0)  # Skip if b is 0
    assert (a // b) * b + (a % b) == a

# Combining filters
positive_even = st.integers(min_value=1).filter(lambda x: x % 2 == 0)
```

## Settings and Configuration

```python
from hypothesis import given, settings, Verbosity, Phase
from hypothesis import strategies as st

# Per-test settings
@settings(max_examples=500)  # More examples (default: 100)
@given(st.integers())
def test_thorough(n):
    pass

@settings(deadline=None)  # Disable timing check
@given(st.lists(st.integers()))
def test_slow_operation(lst):
    expensive_operation(lst)

@settings(
    max_examples=1000,
    verbosity=Verbosity.verbose,
    phases=[Phase.generate],  # Skip shrinking
)
@given(st.text())
def test_verbose(s):
    pass


# Profile for CI (in conftest.py)
from hypothesis import settings, Verbosity

settings.register_profile("ci", max_examples=1000)
settings.register_profile("dev", max_examples=10)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)

# Use: pytest --hypothesis-profile=ci
```

## Stateful Testing

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
from hypothesis import strategies as st

class DatabaseMachine(RuleBasedStateMachine):
    """Test database operations maintain invariants."""

    def __init__(self):
        super().__init__()
        self.db = {}  # Model
        self.real_db = RealDatabase()  # System under test

    @rule(key=st.text(), value=st.integers())
    def set_value(self, key, value):
        """Set a value in both model and real DB."""
        self.db[key] = value
        self.real_db.set(key, value)

    @rule(key=st.text())
    def get_value(self, key):
        """Get value should match model."""
        expected = self.db.get(key)
        actual = self.real_db.get(key)
        assert expected == actual

    @rule(key=st.text())
    def delete_value(self, key):
        """Delete from both."""
        self.db.pop(key, None)
        self.real_db.delete(key)

    @invariant()
    def keys_match(self):
        """Keys should always match."""
        assert set(self.db.keys()) == set(self.real_db.keys())


# Run stateful tests
TestDatabase = DatabaseMachine.TestCase
```

## pytest Integration

```python
# conftest.py
from hypothesis import settings, Verbosity, Phase

# Default profile for all tests
settings.register_profile("default", max_examples=100)

# CI profile - more examples, deterministic
settings.register_profile(
    "ci",
    max_examples=500,
    derandomize=True,  # Deterministic for CI
)

# Load profile from env or default
import os
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))


# pytest.ini
# [pytest]
# addopts = --hypothesis-profile=default
```

## Shrinking Examples

```python
from hypothesis import given, settings
from hypothesis import strategies as st

@given(st.lists(st.integers()))
def test_shrinking_demo(lst):
    """Hypothesis shrinks failing inputs to minimal examples."""
    # This will fail, but Hypothesis finds minimal case
    assert sum(lst) < 100

# Hypothesis will shrink to something like:
# Falsifying example: test_shrinking_demo(lst=[100])
# Not: test_shrinking_demo(lst=[3847, -293, 10293, ...])
```

## Common Patterns

```python
# Roundtrip / Encode-Decode
@given(st.binary())
def test_compression_roundtrip(data):
    assert decompress(compress(data)) == data

@given(st.dictionaries(st.text(), st.integers()))
def test_json_roundtrip(d):
    assert json.loads(json.dumps(d)) == d


# Oracle testing (compare implementations)
@given(st.lists(st.integers()))
def test_sort_vs_stdlib(lst):
    assert my_sort(lst) == sorted(lst)


# Metamorphic relations
@given(st.lists(st.integers()))
def test_sort_idempotent(lst):
    """Sorting twice equals sorting once."""
    assert sort(sort(lst)) == sort(lst)

@given(st.lists(st.integers()), st.integers())
def test_sort_append(lst, x):
    """Appending and sorting vs inserting sorted."""
    assert sort(lst + [x]) == sort(sorted(lst) + [x])
```

## Quick Reference

| Strategy | Description |
|----------|-------------|
| `st.integers()` | Any integer |
| `st.floats()` | Floats (configure nan, inf) |
| `st.text()` | Unicode strings |
| `st.binary()` | Byte strings |
| `st.lists(st.X())` | Lists of X |
| `st.dictionaries(k, v)` | Dict with key/value strategies |
| `st.builds(Class, ...)` | Build objects |
| `st.one_of(a, b)` | Either a or b |
| `st.sampled_from([...])` | Pick from list |
| `@st.composite` | Custom strategy |

| Setting | Purpose |
|---------|---------|
| `max_examples=N` | Number of test cases |
| `deadline=None` | Disable timing |
| `derandomize=True` | Reproducible runs |
| `verbosity=Verbosity.verbose` | Debug output |
