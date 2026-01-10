# Docstring Standards Cookbook

Guidelines for writing and updating inline documentation.

## Language-Specific Formats

### Python (Google Style)

```python
def function(param1: str, param2: int = 10) -> bool:
    """Brief one-line description.

    Longer description if needed. Can span multiple lines
    and include additional context.

    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 10.

    Returns:
        Description of return value.

    Raises:
        ValueError: If param1 is empty.
        ConnectionError: If service is unavailable.

    Example:
        >>> result = function("input", param2=20)
        >>> print(result)
        True
    """
```

### Python (NumPy Style)

```python
def function(param1, param2=10):
    """
    Brief one-line description.

    Longer description if needed.

    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int, optional
        Description of param2 (default is 10).

    Returns
    -------
    bool
        Description of return value.

    Raises
    ------
    ValueError
        If param1 is empty.

    Examples
    --------
    >>> result = function("input", param2=20)
    >>> print(result)
    True
    """
```

### Python Classes

```python
class MyClass:
    """Brief class description.

    Longer description explaining the purpose and usage
    of this class.

    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.

    Example:
        >>> obj = MyClass(value=10)
        >>> obj.do_something()
    """

    def __init__(self, value: int) -> None:
        """Initialize MyClass.

        Args:
            value: Initial value for the instance.
        """
        self.value = value
```

### TypeScript/JavaScript (JSDoc)

```typescript
/**
 * Brief one-line description.
 *
 * Longer description if needed. Can span multiple lines
 * and include additional context.
 *
 * @param param1 - Description of param1
 * @param param2 - Description of param2 (default: 10)
 * @returns Description of return value
 * @throws {Error} If param1 is empty
 *
 * @example
 * ```typescript
 * const result = myFunction("input", 20);
 * console.log(result); // true
 * ```
 */
function myFunction(param1: string, param2: number = 10): boolean {
```

### TypeScript Classes

```typescript
/**
 * Brief class description.
 *
 * Longer description explaining purpose and usage.
 *
 * @example
 * ```typescript
 * const instance = new MyClass({ value: 10 });
 * instance.doSomething();
 * ```
 */
class MyClass {
  /** Current value of the instance. */
  value: number;

  /**
   * Create a new MyClass instance.
   *
   * @param options - Configuration options
   * @param options.value - Initial value
   */
  constructor(options: { value: number }) {
    this.value = options.value;
  }
}
```

### Go

```go
// MyFunction does something with the input.
//
// It accepts a string parameter and returns a boolean
// indicating success. Returns an error if the input
// is empty.
//
// Example:
//
//	result, err := MyFunction("input")
//	if err != nil {
//	    log.Fatal(err)
//	}
func MyFunction(input string) (bool, error) {
```

### Rust

```rust
/// Brief one-line description.
///
/// Longer description if needed. Can span multiple lines
/// and include additional context.
///
/// # Arguments
///
/// * `param1` - Description of param1
/// * `param2` - Description of param2
///
/// # Returns
///
/// Description of return value.
///
/// # Errors
///
/// Returns an error if param1 is empty.
///
/// # Examples
///
/// ```
/// let result = my_function("input", 20);
/// assert!(result.is_ok());
/// ```
fn my_function(param1: &str, param2: i32) -> Result<bool, Error> {
```

## When to Update Docstrings

Update docstrings when:

| Change | Update Required |
|--------|-----------------|
| Parameter added/removed | Yes |
| Parameter type changed | Yes |
| Return type changed | Yes |
| New exception raised | Yes |
| Behavior changed | Yes |
| Performance improved | No |
| Internal refactor | No |
| Bug fixed (no API change) | No |

## Updating Checklist

When updating a function/class:

1. [ ] Update brief description if purpose changed
2. [ ] Add/remove parameters in Args section
3. [ ] Update parameter descriptions if meaning changed
4. [ ] Update return description if return value changed
5. [ ] Add new exceptions to Raises section
6. [ ] Update examples if usage changed
7. [ ] Remove outdated examples

## Common Mistakes

### Outdated Parameter Descriptions

**Bad (outdated):**
```python
def process(data: dict, format: str = "json") -> str:
    """Process data.

    Args:
        data: Input data.  # Missing new 'validate' param!

    Returns:
        Processed output.
    """
```

**Good:**
```python
def process(data: dict, format: str = "json", validate: bool = True) -> str:
    """Process data.

    Args:
        data: Input data to process.
        format: Output format. Defaults to "json".
        validate: Whether to validate input. Defaults to True.

    Returns:
        Processed output as string.
    """
```

### Missing Exception Documentation

**Bad:**
```python
def divide(a: int, b: int) -> float:
    """Divide two numbers.

    Args:
        a: Numerator.
        b: Denominator.

    Returns:
        Result of division.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")  # Not documented!
    return a / b
```

**Good:**
```python
def divide(a: int, b: int) -> float:
    """Divide two numbers.

    Args:
        a: Numerator.
        b: Denominator.

    Returns:
        Result of division.

    Raises:
        ValueError: If b is zero.
    """
```

### Broken Examples

**Bad (outdated API):**
```python
def create_user(name: str, email: str, role: str = "user") -> User:
    """Create a new user.

    Example:
        >>> user = create_user("John")  # Missing required email!
        >>> print(user.name)
    """
```

**Good:**
```python
def create_user(name: str, email: str, role: str = "user") -> User:
    """Create a new user.

    Example:
        >>> user = create_user("John", "john@example.com")
        >>> print(user.name)
        'John'
    """
```

## Docstring Verification

Run doctest to verify examples:

```bash
# Python
python -m doctest module.py

# Or with pytest
pytest --doctest-modules

# TypeScript (with ts-doctest)
npx ts-doctest src/**/*.ts
```

## Style Consistency

Match the project's existing style:

1. Check existing docstrings for format (Google, NumPy, etc.)
2. Match indentation and spacing
3. Use same sections (Args vs Parameters)
4. Match example format

If no existing style, default to:
- Python: Google style
- TypeScript: JSDoc
- Go: Standard godoc
- Rust: Standard rustdoc
