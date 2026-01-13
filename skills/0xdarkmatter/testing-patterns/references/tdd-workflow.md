# Test-Driven Development (TDD)

Red-Green-Refactor cycle for quality code.

## The TDD Cycle

```
┌─────────────────────────────────────────┐
│                                         │
│   ┌─────┐    ┌─────┐    ┌─────────┐    │
│   │ RED │ -> │GREEN│ -> │REFACTOR │ ──┐│
│   └─────┘    └─────┘    └─────────┘   ││
│       ^                               │ │
│       └───────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### 1. RED: Write a Failing Test

```python
# Start with the test
def test_calculate_discount_applies_percentage():
    cart = Cart()
    cart.add_item(Item(price=100))

    total = cart.calculate_total(discount_percent=10)

    assert total == 90  # Fails - function doesn't exist yet
```

### 2. GREEN: Make It Pass (Minimal Code)

```python
# Write minimal code to pass
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def calculate_total(self, discount_percent=0):
        total = sum(item.price for item in self.items)
        return total * (1 - discount_percent / 100)
```

### 3. REFACTOR: Improve the Code

```python
# Clean up while tests pass
class Cart:
    def __init__(self):
        self._items: list[Item] = []

    def add_item(self, item: Item) -> None:
        self._items.append(item)

    @property
    def subtotal(self) -> Decimal:
        return sum(item.price for item in self._items)

    def calculate_total(self, discount_percent: int = 0) -> Decimal:
        discount_multiplier = Decimal(100 - discount_percent) / 100
        return self.subtotal * discount_multiplier
```

## TDD Rules

### Three Laws of TDD

1. **Don't write production code** until you have a failing test
2. **Write only enough test** to fail (compilation counts)
3. **Write only enough production code** to pass the test

### Test Size Rules

```
Tests should be:
- Fast (< 100ms each)
- Isolated (no shared state)
- Repeatable (same result every time)
- Self-validating (pass/fail, no manual inspection)
- Timely (written before production code)
```

## TDD Workflow Example

### Step 1: List Test Cases

```
Feature: Shopping Cart Discount

Test cases:
[ ] Empty cart returns 0
[ ] Single item returns item price
[ ] Multiple items returns sum
[ ] Percentage discount applied correctly
[ ] Maximum discount capped at 50%
[ ] Negative discount treated as 0
```

### Step 2: Start with Simplest Test

```python
def test_empty_cart_returns_zero():
    cart = Cart()
    assert cart.calculate_total() == 0
```

### Step 3: Implement and Move to Next

```python
# After passing, add next test
def test_single_item_returns_price():
    cart = Cart()
    cart.add_item(Item(price=50))
    assert cart.calculate_total() == 50
```

### Step 4: Build Up Complexity

```python
def test_discount_capped_at_50_percent():
    cart = Cart()
    cart.add_item(Item(price=100))

    total = cart.calculate_total(discount_percent=75)

    assert total == 50  # Capped at 50% max discount
```

## When to Use TDD

### Good For:
- Business logic
- Algorithms
- Data transformations
- API contracts
- Complex conditionals

### Less Suitable For:
- UI/visual elements
- Exploratory prototyping
- One-off scripts
- Integration with external systems

## TDD Anti-Patterns

### Testing Implementation Details

```python
# BAD - Tests internal state
def test_cart_has_items_list():
    cart = Cart()
    cart.add_item(Item(price=10))
    assert len(cart._items) == 1  # Tests implementation!

# GOOD - Tests behavior
def test_cart_counts_items():
    cart = Cart()
    cart.add_item(Item(price=10))
    assert cart.item_count == 1  # Tests public interface
```

### Tests That Mirror Code

```python
# BAD - Test duplicates implementation
def test_calculate_total():
    cart = Cart()
    cart.add_item(Item(price=10))
    cart.add_item(Item(price=20))

    # This is just reimplementing the function
    expected = 10 + 20
    assert cart.calculate_total() == expected

# GOOD - Tests expected outcome
def test_calculate_total():
    cart = Cart()
    cart.add_item(Item(price=10))
    cart.add_item(Item(price=20))

    assert cart.calculate_total() == 30
```

## Kata Practice

### String Calculator

```
Create a calculator that takes a string of numbers and returns their sum.

Step 1: "" returns 0
Step 2: "1" returns 1
Step 3: "1,2" returns 3
Step 4: Handle unknown number of numbers
Step 5: Handle newlines as delimiters: "1\n2,3" returns 6
Step 6: Support custom delimiters: "//;\n1;2" returns 3
Step 7: Throw on negative numbers with message including all negatives
```

### FizzBuzz

```
Step 1: Return "1" for 1
Step 2: Return "2" for 2
Step 3: Return "Fizz" for 3
Step 4: Return "Buzz" for 5
Step 5: Return "Fizz" for 6 (multiple of 3)
Step 6: Return "Buzz" for 10 (multiple of 5)
Step 7: Return "FizzBuzz" for 15 (multiple of both)
```
