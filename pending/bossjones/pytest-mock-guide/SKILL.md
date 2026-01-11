---
name: pytest-mock-guide
description: Guide for using pytest-mock plugin to write tests with mocking. Use when writing pytest tests that need mocking, patching, spying, or stubbing. Covers mocker fixture usage, patch methods, spy/stub patterns, and assertion helpers.
---

# pytest-mock Usage Guide

pytest-mock is a pytest plugin providing a `mocker` fixture as a thin wrapper around Python's `unittest.mock` patching API. It automatically undoes all mocking at the end of each test.

## The mocker Fixture

The `mocker` fixture is the main interface. Request it in your test function:

```python
def test_example(mocker):
    # All mocks are automatically cleaned up after this test
    mock_func = mocker.patch("module.function")
```

### Available Fixture Scopes

| Fixture | Scope | Use Case |
|---------|-------|----------|
| `mocker` | function | Default, per-test mocking |
| `class_mocker` | class | Share mocks across test class |
| `module_mocker` | module | Share mocks across test module |
| `package_mocker` | package | Share mocks across package |
| `session_mocker` | session | Share mocks across entire session |

## Patching Methods

### mocker.patch(target, ...)

Patch a module-level object by its dotted path:

```python
def test_patch(mocker):
    # Patch os.remove function
    mock_remove = mocker.patch("os.remove")
    mock_remove.return_value = None

    os.remove("file.txt")
    mock_remove.assert_called_once_with("file.txt")
```

### mocker.patch.object(target, attribute, ...)

Patch an attribute on an object directly:

```python
def test_patch_object(mocker):
    import os
    mock_remove = mocker.patch.object(os, "remove")

    os.remove("file.txt")
    mock_remove.assert_called_once_with("file.txt")
```

### mocker.patch.dict(in_dict, values, clear=False)

Patch a dictionary temporarily:

```python
def test_patch_dict(mocker):
    config = {"debug": False}
    mocker.patch.dict(config, {"debug": True})

    assert config["debug"] is True
    # After test, config["debug"] is False again
```

### mocker.patch.multiple(target, **kwargs)

Patch multiple attributes at once:

```python
def test_patch_multiple(mocker):
    mocks = mocker.patch.multiple(
        "os",
        remove=mocker.DEFAULT,
        listdir=mocker.DEFAULT
    )

    os.remove("file.txt")
    os.listdir("/tmp")

    mocks["remove"].assert_called_once()
    mocks["listdir"].assert_called_once()
```

### mocker.patch.context_manager(target, attribute, ...)

Same as `patch.object` but doesn't warn when mock is used as context manager:

```python
def test_context_manager(mocker):
    mock_open = mocker.patch.context_manager(builtins, "open")
    # No warning when using `with mock_open(...)`
```

## Common Patch Parameters

| Parameter | Description |
|-----------|-------------|
| `new` | Object to replace target with |
| `return_value` | Value returned when mock is called |
| `side_effect` | Exception to raise or function to call |
| `autospec` | Create mock matching target's signature |
| `spec` | Object to use as specification |
| `spec_set` | Stricter spec that prevents setting new attributes |
| `create` | Allow patching non-existent attributes |
| `new_callable` | Callable to create the mock |

## Spying with mocker.spy()

Spy wraps the real method while tracking calls:

```python
def test_spy(mocker):
    spy = mocker.spy(os.path, "exists")

    # Real method is called
    result = os.path.exists("/tmp")

    # But we can inspect calls
    spy.assert_called_once_with("/tmp")

    # Access return values
    assert spy.spy_return == result
    assert spy.spy_return_list == [result]  # All returns
```

### Spy Attributes

| Attribute | Description |
|-----------|-------------|
| `spy_return` | Last return value from real method |
| `spy_return_list` | List of all return values |
| `spy_return_iter` | Iterator copy (when `duplicate_iterators=True`) |
| `spy_exception` | Last exception raised, if any |

### Spying Iterators

```python
def test_spy_iterator(mocker):
    spy = mocker.spy(obj, "get_items", duplicate_iterators=True)

    items = list(obj.get_items())

    # Access a copy of the returned iterator
    spy_items = list(spy.spy_return_iter)
```

## Creating Stubs

### mocker.stub(name=None)

Create a stub that accepts any arguments:

```python
def test_stub(mocker):
    callback = mocker.stub(name="my_callback")

    some_function(on_complete=callback)

    callback.assert_called_once()
```

### mocker.async_stub(name=None)

Create an async stub:

```python
async def test_async_stub(mocker):
    callback = mocker.async_stub(name="async_callback")

    await some_async_function(on_complete=callback)

    callback.assert_awaited_once()
```

## Mock Helpers

### mocker.create_autospec(spec, ...)

Create a mock that matches the spec's signature:

```python
def test_autospec(mocker):
    mock_obj = mocker.create_autospec(MyClass, instance=True)

    # Calling with wrong arguments raises TypeError
    mock_obj.method()  # OK if method() takes no args
```

### Direct Mock Classes

Access mock classes directly through mocker:

```python
def test_mock_classes(mocker):
    mock = mocker.Mock()
    magic_mock = mocker.MagicMock()
    async_mock = mocker.AsyncMock()
    property_mock = mocker.PropertyMock()
    non_callable = mocker.NonCallableMock()
```

### Other Utilities

```python
def test_utilities(mocker):
    # Match any argument
    mock.assert_called_with(mocker.ANY)

    # Create call objects for assertion
    mock.assert_has_calls([mocker.call(1), mocker.call(2)])

    # Sentinel objects
    result = mocker.sentinel.my_result

    # Mock file open
    m = mocker.mock_open(read_data="file contents")
    mocker.patch("builtins.open", m)

    # Seal a mock to prevent new attributes
    mocker.seal(mock)
```

## Managing Mocks

### mocker.stopall()

Stop all patches immediately:

```python
def test_stopall(mocker):
    mocker.patch("os.remove")
    mocker.patch("os.listdir")

    mocker.stopall()  # Both patches stopped
```

### mocker.stop(mock)

Stop a specific patch:

```python
def test_stop(mocker):
    mock_remove = mocker.patch("os.remove")

    mocker.stop(mock_remove)  # Only this patch stopped
```

### mocker.resetall()

Reset all mocks without stopping them:

```python
def test_resetall(mocker):
    mock_func = mocker.patch("module.func")
    mock_func("arg1")

    mocker.resetall()

    mock_func.assert_not_called()  # Call history cleared
```

## Assertion Methods with pytest Introspection

pytest-mock enhances assertion error messages with pytest's comparison:

```python
def test_assertions(mocker):
    mock = mocker.patch("module.func")
    mock("actual_arg")

    # Enhanced error shows diff between expected and actual
    mock.assert_called_with("expected_arg")
    # AssertionError shows:
    # Args:
    # assert ('actual_arg',) == ('expected_arg',)
```

### Available Assertions

**Call Assertions:**
- `assert_called()` - Called at least once
- `assert_called_once()` - Called exactly once
- `assert_called_with(*args, **kwargs)` - Last call matches
- `assert_called_once_with(*args, **kwargs)` - Called once with args
- `assert_any_call(*args, **kwargs)` - Any call matches
- `assert_has_calls(calls, any_order=False)` - Has specific calls
- `assert_not_called()` - Never called

**Async Assertions (for AsyncMock):**
- `assert_awaited()`
- `assert_awaited_once()`
- `assert_awaited_with(*args, **kwargs)`
- `assert_awaited_once_with(*args, **kwargs)`
- `assert_any_await(*args, **kwargs)`
- `assert_has_awaits(calls, any_order=False)`
- `assert_not_awaited()`

## Configuration Options

In `pytest.ini`, `pyproject.toml`, or `setup.cfg`:

```ini
[pytest]
# Enable/disable enhanced assertion messages (default: true)
mock_traceback_monkeypatch = true

# Use standalone mock package instead of unittest.mock (default: false)
mock_use_standalone_module = false
```

## Common Patterns

### Patching Where Used (Not Where Defined)

```python
# my_module.py
from os.path import exists

def check_file(path):
    return exists(path)

# test_my_module.py
def test_check_file(mocker):
    # Patch where it's used, not where it's defined
    mocker.patch("my_module.exists", return_value=True)
    assert check_file("/any/path") is True
```

### Testing Exceptions

```python
def test_exception(mocker):
    mock_func = mocker.patch("module.func")
    mock_func.side_effect = ValueError("error message")

    with pytest.raises(ValueError, match="error message"):
        module.func()
```

### Multiple Return Values

```python
def test_multiple_returns(mocker):
    mock_func = mocker.patch("module.func")
    mock_func.side_effect = [1, 2, 3]

    assert module.func() == 1
    assert module.func() == 2
    assert module.func() == 3
```

### Async Function Mocking

```python
async def test_async(mocker):
    mock_fetch = mocker.patch("module.fetch_data")
    mock_fetch.return_value = {"data": "value"}

    result = await module.fetch_data()
    assert result == {"data": "value"}
```

### Class Method Mocking

```python
def test_class_method(mocker):
    mocker.patch.object(MyClass, "class_method", return_value="mocked")

    assert MyClass.class_method() == "mocked"
```

### Property Mocking

```python
def test_property(mocker):
    mock_prop = mocker.patch.object(
        MyClass, "my_property",
        new_callable=mocker.PropertyMock,
        return_value="mocked"
    )

    obj = MyClass()
    assert obj.my_property == "mocked"
```
