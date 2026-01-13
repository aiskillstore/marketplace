# Mocking Patterns

Comprehensive guide to mocking in pytest.

## unittest.mock Basics

### Mock Object

```python
from unittest.mock import Mock

def test_mock_basics():
    mock = Mock()

    # Access any attribute (auto-created)
    mock.some_attribute
    mock.method()
    mock.nested.deeply.value

    # Configure return values
    mock.get_data.return_value = {"key": "value"}
    assert mock.get_data() == {"key": "value"}

    # Check calls
    mock.get_data.assert_called_once()
    mock.get_data.assert_called_with()  # No args
```

### MagicMock

```python
from unittest.mock import MagicMock

def test_magic_mock():
    mock = MagicMock()

    # Supports magic methods
    mock.__len__.return_value = 5
    assert len(mock) == 5

    # Iteration
    mock.__iter__.return_value = iter([1, 2, 3])
    assert list(mock) == [1, 2, 3]

    # Context manager
    mock.__enter__.return_value = "entered"
    with mock as m:
        assert m == "entered"
```

## patch Decorator

```python
from unittest.mock import patch

# Patch where used, not where defined
@patch("mymodule.requests.get")
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}

    result = mymodule.fetch_data()

    assert result["status"] == "ok"
    mock_get.assert_called_once_with("https://api.example.com/data")

# Multiple patches (applied bottom-up)
@patch("mymodule.save_to_db")
@patch("mymodule.fetch_from_api")
def test_multiple_patches(mock_fetch, mock_save):  # Note: reverse order
    mock_fetch.return_value = {"data": []}
    process_and_save()
    mock_save.assert_called_once()
```

## patch Context Manager

```python
from unittest.mock import patch

def test_with_context_manager():
    with patch("mymodule.external_service") as mock_service:
        mock_service.call.return_value = "mocked"
        result = mymodule.do_work()
        assert result == "mocked"

    # After context, original is restored
```

## patch.object

```python
from unittest.mock import patch

class MyClass:
    def method(self):
        return "real"

def test_patch_object():
    obj = MyClass()

    with patch.object(obj, "method", return_value="mocked"):
        assert obj.method() == "mocked"

    assert obj.method() == "real"  # Restored
```

## patch.dict

```python
from unittest.mock import patch
import os

def test_patch_dict():
    with patch.dict(os.environ, {"API_KEY": "test-key"}):
        assert os.environ["API_KEY"] == "test-key"

    # Clear and add
    with patch.dict(os.environ, {"NEW_VAR": "value"}, clear=True):
        assert "PATH" not in os.environ
        assert os.environ["NEW_VAR"] == "value"
```

## side_effect

```python
from unittest.mock import Mock

def test_side_effect_function():
    mock = Mock()
    mock.side_effect = lambda x: x * 2
    assert mock(5) == 10

def test_side_effect_exception():
    mock = Mock()
    mock.side_effect = ValueError("Invalid input")

    with pytest.raises(ValueError):
        mock()

def test_side_effect_list():
    mock = Mock()
    mock.side_effect = [1, 2, ValueError("Done")]

    assert mock() == 1
    assert mock() == 2
    with pytest.raises(ValueError):
        mock()
```

## spec and autospec

```python
from unittest.mock import Mock, create_autospec

class RealAPI:
    def get_user(self, user_id: int) -> dict:
        pass

    def create_user(self, name: str) -> dict:
        pass

def test_with_spec():
    # Only allows methods that exist on RealAPI
    mock = Mock(spec=RealAPI)
    mock.get_user(1)  # OK
    # mock.invalid_method()  # AttributeError

def test_with_autospec():
    # Also validates signatures
    mock = create_autospec(RealAPI)
    mock.get_user(1)  # OK
    # mock.get_user("string")  # Still OK at runtime, but IDE warns
    # mock.get_user(1, 2, 3)  # TypeError: too many args
```

## pytest-mock Plugin

```python
# pip install pytest-mock

def test_with_mocker(mocker):
    # mocker is a fixture that wraps unittest.mock
    mock = mocker.patch("mymodule.external_call")
    mock.return_value = "mocked"

    result = mymodule.process()

    assert result == "mocked"
    mock.assert_called_once()

def test_spy(mocker):
    # Spy: call real method but track calls
    spy = mocker.spy(mymodule, "helper_function")

    mymodule.main_function()

    spy.assert_called()
    # Original function was actually called

def test_stub(mocker):
    # Stub: quick attribute replacement
    mocker.patch.object(MyClass, "expensive_method", return_value="cheap")
```

## Async Mocking

```python
from unittest.mock import AsyncMock

async def test_async_mock():
    mock = AsyncMock()
    mock.return_value = {"async": "result"}

    result = await mock()

    assert result == {"async": "result"}
    mock.assert_awaited_once()

@patch("mymodule.async_fetch", new_callable=AsyncMock)
async def test_patch_async(mock_fetch):
    mock_fetch.return_value = {"data": []}

    result = await mymodule.get_data()

    assert result == {"data": []}
```

## PropertyMock

```python
from unittest.mock import PropertyMock, patch

class MyClass:
    @property
    def value(self):
        return "real"

def test_property_mock():
    with patch.object(
        MyClass, "value", new_callable=PropertyMock
    ) as mock_prop:
        mock_prop.return_value = "mocked"
        obj = MyClass()
        assert obj.value == "mocked"
```

## Common Patterns

### Mock HTTP Response

```python
def test_mock_response(mocker):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1}
    mock_response.raise_for_status = Mock()

    mocker.patch("requests.get", return_value=mock_response)

    result = fetch_user(1)
    assert result["id"] == 1
```

### Mock File Operations

```python
from unittest.mock import mock_open, patch

def test_file_read():
    m = mock_open(read_data="file content")
    with patch("builtins.open", m):
        result = read_config("config.txt")
        assert "content" in result

def test_file_write():
    m = mock_open()
    with patch("builtins.open", m):
        write_data("output.txt", "data")
        m().write.assert_called_with("data")
```

### Mock datetime

```python
from unittest.mock import patch
from datetime import datetime

def test_mock_datetime(mocker):
    mock_dt = mocker.patch("mymodule.datetime")
    mock_dt.now.return_value = datetime(2024, 1, 15, 12, 0, 0)

    result = mymodule.get_timestamp()
    assert "2024-01-15" in result
```

## Best Practices

1. **Patch where used** - Not where defined
2. **Use autospec** - Catch API mismatches
3. **Reset mocks** - In fixtures or with `mock.reset_mock()`
4. **Don't over-mock** - Test behavior, not implementation
5. **Prefer dependency injection** - Over patching
6. **Use pytest-mock** - Cleaner syntax than unittest.mock
