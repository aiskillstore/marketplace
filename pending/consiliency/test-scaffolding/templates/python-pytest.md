# Python + pytest Template

Template for generating pytest test scaffolds from Python source files.

## Variables

| Variable | Description |
|----------|-------------|
| `{module_name}` | Source module name (e.g., `login`) |
| `{module_path}` | Relative import path (e.g., `src.auth.login`) |
| `{import_path}` | Python import path (e.g., `src.auth.login`) |
| `{symbols}` | Comma-separated list of imported symbols |
| `{class_name}` | Name of class being tested |
| `{function_name}` | Name of function being tested |
| `{method_tests}` | Generated method test stubs |
| `{function_tests}` | Generated function test stubs |

## File Template

```python
"""Tests for {module_name}.

Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
Fill in test implementations and remove TODO comments.
"""
from __future__ import annotations

import pytest

from {import_path} import {symbols}


{class_tests}


{function_tests}
```

## Class Test Template

```python
class Test{class_name}:
    """Tests for {class_name}."""

    @pytest.fixture
    def instance(self) -> {class_name}:
        """Create {class_name} instance for testing.

        TODO: Configure fixture with appropriate test data.
        """
        return {class_name}()

{method_tests}
```

## Method Test Template

```python
    def test_{method_name}(self, instance: {class_name}) -> None:
        """Test {class_name}.{method_name}.

        TODO: Implement test for {method_name}.
        - Test happy path
        - Test edge cases
        - Test error conditions
        """
        # TODO: Implement this test
        raise NotImplementedError("Test not yet implemented")
```

## Function Test Template

```python
def test_{function_name}() -> None:
    """Test {function_name}.

    TODO: Implement test for {function_name}.
    - Test happy path
    - Test edge cases
    - Test error conditions
    """
    # TODO: Implement this test
    raise NotImplementedError("Test not yet implemented")
```

## Parameterized Test Template

For functions with multiple test cases:

```python
@pytest.mark.parametrize(
    "input_value,expected",
    [
        # TODO: Add test cases
        pytest.param(None, None, id="placeholder"),
    ],
)
def test_{function_name}_parametrized(input_value, expected) -> None:
    """Parametrized tests for {function_name}.

    TODO: Add test cases above and implement assertion.
    """
    # TODO: Implement this test
    result = {function_name}(input_value)
    assert result == expected
```

## Fixture Template

For shared test data:

```python
@pytest.fixture
def sample_{fixture_name}() -> {fixture_type}:
    """Provide sample {fixture_name} for testing.

    TODO: Configure with appropriate test data.
    """
    return {fixture_type}()
```

## Example Output

Given source file `src/auth/login.py`:
```python
class UserSession:
    def __init__(self, user_id: str):
        self.user_id = user_id

    def refresh(self) -> bool:
        ...

    def invalidate(self) -> None:
        ...

def authenticate(username: str, password: str) -> UserSession:
    ...

def logout(session: UserSession) -> bool:
    ...
```

Generated scaffold `tests/auth/test_login.py`:
```python
"""Tests for login.

Auto-generated scaffold by /ai-dev-kit:scaffold-tests.
Fill in test implementations and remove TODO comments.
"""
from __future__ import annotations

import pytest

from src.auth.login import UserSession, authenticate, logout


class TestUserSession:
    """Tests for UserSession."""

    @pytest.fixture
    def instance(self) -> UserSession:
        """Create UserSession instance for testing.

        TODO: Configure fixture with appropriate test data.
        """
        return UserSession(user_id="test-user-id")

    def test_refresh(self, instance: UserSession) -> None:
        """Test UserSession.refresh.

        TODO: Implement test for refresh.
        - Test happy path
        - Test edge cases
        - Test error conditions
        """
        # TODO: Implement this test
        raise NotImplementedError("Test not yet implemented")

    def test_invalidate(self, instance: UserSession) -> None:
        """Test UserSession.invalidate.

        TODO: Implement test for invalidate.
        - Test happy path
        - Test edge cases
        - Test error conditions
        """
        # TODO: Implement this test
        raise NotImplementedError("Test not yet implemented")


def test_authenticate() -> None:
    """Test authenticate.

    TODO: Implement test for authenticate.
    - Test happy path
    - Test edge cases
    - Test error conditions
    """
    # TODO: Implement this test
    raise NotImplementedError("Test not yet implemented")


def test_logout() -> None:
    """Test logout.

    TODO: Implement test for logout.
    - Test happy path
    - Test edge cases
    - Test error conditions
    """
    # TODO: Implement this test
    raise NotImplementedError("Test not yet implemented")
```

## Naming Rules

| Source | Test File |
|--------|-----------|
| `src/auth/login.py` | `tests/auth/test_login.py` |
| `src/utils.py` | `tests/test_utils.py` |
| `my_package/core.py` | `tests/test_core.py` |

## Import Resolution

1. If source is in `src/`, use `from src.{path} import ...`
2. If source is package root, use `from {package}.{path} import ...`
3. Detect package name from `pyproject.toml` or directory structure
