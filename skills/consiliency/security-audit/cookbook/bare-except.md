# Bare Except Handling Cookbook

How to properly handle exceptions instead of using bare `except:` blocks.

## Why Bare Except is Bad

```python
# BAD: Catches EVERYTHING including:
try:
    do_something()
except:  # <-- bare except
    pass

# This catches:
# - KeyboardInterrupt (Ctrl+C)
# - SystemExit (sys.exit())
# - GeneratorExit
# - Actual bugs you want to see
# - All the exceptions you didn't anticipate
```

## The Problems

### 1. Hides Bugs

```python
# BAD: Bug is hidden
def calculate(x, y):
    try:
        result = x / y  # ZeroDivisionError hidden!
        return rezult  # NameError hidden!
    except:
        return 0
```

### 2. Prevents Interruption

```python
# BAD: Can't Ctrl+C out of this
try:
    while True:
        do_work()
except:  # Catches KeyboardInterrupt!
    pass
```

### 3. Silently Fails

```python
# BAD: No idea what went wrong
try:
    complex_operation()
except:
    return default_value  # What failed? Why?
```

## Proper Exception Handling

### Catch Specific Exceptions

```python
# GOOD: Catch specific exceptions
try:
    result = int(user_input)
except ValueError:
    print("Please enter a valid number")
except TypeError:
    print("Input must be a string")
```

### Multiple Exceptions

```python
# GOOD: Multiple specific exceptions
try:
    data = fetch_and_parse(url)
except ConnectionError:
    log.warning("Network issue, retrying...")
    data = retry_fetch(url)
except json.JSONDecodeError:
    log.error("Invalid JSON response")
    data = None
except TimeoutError:
    log.error("Request timed out")
    raise
```

### Catch Base Exception Class

```python
# ACCEPTABLE: When you really need to catch all
try:
    risky_operation()
except Exception as e:  # Not BaseException
    log.error(f"Operation failed: {e}")
    # Still allows KeyboardInterrupt, SystemExit

# RARELY NEEDED: BaseException
try:
    critical_cleanup()
except BaseException as e:
    # Document WHY you need this
    log.critical(f"Cleanup failed: {e}")
    raise  # Re-raise after logging
```

### Re-raise After Handling

```python
# GOOD: Log then re-raise
try:
    important_operation()
except SomeError as e:
    log.error(f"Failed: {e}")
    notify_admin(e)
    raise  # Let it propagate
```

### Transform Exceptions

```python
# GOOD: Wrap in domain exception
class ServiceError(Exception):
    pass

try:
    response = api_call()
except ConnectionError as e:
    raise ServiceError(f"API unreachable: {e}") from e
except json.JSONDecodeError as e:
    raise ServiceError(f"Invalid response: {e}") from e
```

## Detection Pattern

```python
# Regex to find bare excepts
BARE_EXCEPT_PATTERN = r'except\s*:'

# To find in codebase
grep -rn "except:" --include="*.py" .
```

## Remediation Examples

### Before/After: File Operations

```python
# BEFORE (bad)
def read_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except:
        return {}

# AFTER (good)
def read_config():
    try:
        with open("config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        log.info("No config file, using defaults")
        return {}
    except json.JSONDecodeError as e:
        log.error(f"Invalid config JSON: {e}")
        raise ConfigurationError(f"Malformed config: {e}") from e
    except PermissionError:
        log.error("Cannot read config file: permission denied")
        raise
```

### Before/After: API Calls

```python
# BEFORE (bad)
def fetch_data(url):
    try:
        response = requests.get(url)
        return response.json()
    except:
        return None

# AFTER (good)
def fetch_data(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        log.warning(f"Request to {url} timed out")
        return None
    except requests.HTTPError as e:
        log.warning(f"HTTP error from {url}: {e.response.status_code}")
        return None
    except requests.RequestException as e:
        log.error(f"Failed to fetch {url}: {e}")
        return None
    except json.JSONDecodeError:
        log.error(f"Invalid JSON from {url}")
        return None
```

### Before/After: Database Operations

```python
# BEFORE (bad)
def save_user(user):
    try:
        db.add(user)
        db.commit()
    except:
        db.rollback()

# AFTER (good)
def save_user(user):
    try:
        db.add(user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e):
            raise DuplicateUserError(f"User already exists: {user.email}")
        raise
    except OperationalError as e:
        db.rollback()
        log.error(f"Database error: {e}")
        raise DatabaseError("Failed to save user") from e
```

## Exception Hierarchy

Know the Python exception hierarchy:

```
BaseException
├── BaseExceptionGroup
├── GeneratorExit
├── KeyboardInterrupt
├── SystemExit
└── Exception  <-- Catch this for "normal" errors
    ├── ArithmeticError
    │   ├── FloatingPointError
    │   ├── OverflowError
    │   └── ZeroDivisionError
    ├── AssertionError
    ├── AttributeError
    ├── BufferError
    ├── EOFError
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── MemoryError
    ├── NameError
    │   └── UnboundLocalError
    ├── OSError
    │   ├── ConnectionError
    │   ├── FileExistsError
    │   ├── FileNotFoundError
    │   ├── PermissionError
    │   └── TimeoutError
    ├── RuntimeError
    │   └── RecursionError
    ├── StopIteration
    ├── SyntaxError
    ├── TypeError
    └── ValueError
```

## Best Practices

1. **Be specific**: Catch the narrowest exception possible
2. **Log it**: Always log what went wrong
3. **Re-raise when appropriate**: Don't swallow exceptions silently
4. **Use `from e`**: Preserve exception chain with `raise X from e`
5. **Document handlers**: Comment why you're catching each exception
6. **Test error paths**: Write tests for exception handling
