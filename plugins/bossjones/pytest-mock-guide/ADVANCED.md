# Advanced pytest-mock Patterns

## Testing with Scoped Fixtures

### Class-scoped Mocking

```python
import pytest

@pytest.fixture(scope="class")
def mocked_api(class_mocker):
    """Share mock across all tests in class."""
    return class_mocker.patch("myapp.api.client")

class TestAPIIntegration:
    def test_fetch(self, mocked_api):
        mocked_api.get.return_value = {"data": 1}
        # test...

    def test_update(self, mocked_api):
        # Same mock instance, call history preserved
        mocked_api.put.return_value = {"updated": True}
```

### Module-scoped Mocking

```python
@pytest.fixture(scope="module")
def mock_database(module_mocker):
    """Expensive setup shared across module."""
    mock_db = module_mocker.patch("myapp.database.connection")
    mock_db.return_value.is_connected = True
    return mock_db
```

## Complex Side Effects

### Dynamic Side Effects

```python
def test_dynamic_side_effect(mocker):
    def dynamic_response(*args, **kwargs):
        if args[0] == "error":
            raise ValueError("Invalid input")
        return f"processed: {args[0]}"

    mock_func = mocker.patch("module.process")
    mock_func.side_effect = dynamic_response

    assert module.process("data") == "processed: data"
    with pytest.raises(ValueError):
        module.process("error")
```

### Generator Side Effects

```python
def test_generator_side_effect(mocker):
    def generate_responses():
        yield "first"
        yield "second"
        raise StopIteration

    mock_func = mocker.patch("module.get_next")
    mock_func.side_effect = generate_responses()

    assert module.get_next() == "first"
    assert module.get_next() == "second"
```

## Autospec Deep Dive

### Instance vs Class Autospec

```python
def test_autospec_instance(mocker):
    # Mock as if it's an instance
    mock_instance = mocker.create_autospec(MyClass, instance=True)

    # Methods work as instance methods
    mock_instance.method.return_value = "result"

def test_autospec_class(mocker):
    # Mock the class itself
    MockClass = mocker.create_autospec(MyClass, instance=False)

    # Instantiation returns an autospec'd instance
    instance = MockClass()
    instance.method.return_value = "result"
```

### Spec Set for Strict Mocking

```python
def test_spec_set(mocker):
    mock = mocker.create_autospec(MyClass, spec_set=True)

    mock.existing_method()  # OK
    mock.nonexistent_method()  # Raises AttributeError
```

## Spying on Properties

```python
class MyClass:
    @property
    def value(self):
        return self._compute_value()

def test_spy_property(mocker):
    obj = MyClass()

    # Spy on the underlying method
    spy = mocker.spy(obj, "_compute_value")

    _ = obj.value  # Triggers property

    spy.assert_called_once()
```

## Patching Built-ins

### Patching open()

```python
def test_file_read(mocker):
    mock_file = mocker.mock_open(read_data="file content")
    mocker.patch("builtins.open", mock_file)

    with open("any_file.txt") as f:
        content = f.read()

    assert content == "file content"
    mock_file.assert_called_once_with("any_file.txt")
```

### Patching print()

```python
def test_print(mocker):
    mock_print = mocker.patch("builtins.print")

    my_function_that_prints()

    mock_print.assert_called()
```

### Patching datetime

```python
from datetime import datetime

def test_datetime(mocker):
    mock_datetime = mocker.patch("mymodule.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

    result = mymodule.get_current_time()
    assert result == datetime(2024, 1, 1, 12, 0, 0)
```

## Async Testing Patterns

### Mocking Async Context Managers

```python
async def test_async_context_manager(mocker):
    mock_session = mocker.AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    async with aiohttp.ClientSession() as session:
        # session is mock_session
        pass
```

### Mocking Async Iterators

```python
async def test_async_iterator(mocker):
    async def async_gen():
        yield 1
        yield 2
        yield 3

    mock_iter = mocker.patch("module.async_iterator")
    mock_iter.return_value = async_gen()

    results = [item async for item in module.async_iterator()]
    assert results == [1, 2, 3]
```

## Testing Callbacks

```python
def test_callback_registration(mocker):
    callback = mocker.stub(name="callback")

    event_emitter = EventEmitter()
    event_emitter.on("event", callback)
    event_emitter.emit("event", data="payload")

    callback.assert_called_once_with(data="payload")
```

## Verifying Call Order

```python
def test_call_order(mocker):
    mock1 = mocker.patch("module.func1")
    mock2 = mocker.patch("module.func2")

    do_something()

    # Verify order using a manager
    manager = mocker.Mock()
    manager.attach_mock(mock1, "func1")
    manager.attach_mock(mock2, "func2")

    expected_calls = [
        mocker.call.func1(),
        mocker.call.func2(),
    ]
    manager.assert_has_calls(expected_calls)
```

## Partial Mocking

```python
def test_partial_mock(mocker):
    # Only mock specific method, keep others real
    mocker.patch.object(MyClass, "expensive_method", return_value="cached")

    obj = MyClass()
    obj.cheap_method()  # Real implementation
    obj.expensive_method()  # Mocked
```

## Mock Chaining

```python
def test_mock_chain(mocker):
    mock_client = mocker.patch("module.Client")

    # Set up chained calls
    mock_client.return_value.get_session.return_value.execute.return_value = "result"

    client = module.Client()
    session = client.get_session()
    result = session.execute()

    assert result == "result"
```

## Testing with Fixtures Composition

```python
@pytest.fixture
def mock_dependencies(mocker):
    """Compose multiple mocks into a single fixture."""
    return {
        "db": mocker.patch("myapp.database"),
        "cache": mocker.patch("myapp.cache"),
        "api": mocker.patch("myapp.external_api"),
    }

def test_with_all_deps(mock_dependencies):
    mock_dependencies["db"].query.return_value = [1, 2, 3]
    mock_dependencies["cache"].get.return_value = None

    result = my_function()

    mock_dependencies["db"].query.assert_called_once()
    mock_dependencies["cache"].set.assert_called()
```

## Introspecting Mock Calls

```python
def test_call_inspection(mocker):
    mock = mocker.patch("module.func")

    module.func("a", key="value")
    module.func("b")

    # Get all calls
    assert mock.call_count == 2

    # Access individual calls
    first_call = mock.call_args_list[0]
    assert first_call.args == ("a",)
    assert first_call.kwargs == {"key": "value"}

    # Get last call
    assert mock.call_args.args == ("b",)
```
