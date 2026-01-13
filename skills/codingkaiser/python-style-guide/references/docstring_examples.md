# Docstring Examples

Complete examples of Google-style docstrings for various Python constructs.

## Module Docstring

```python
"""This is an example module docstring.

This module provides utilities for processing user data. It includes functions
for validation, transformation, and persistence of user information.

Typical usage example:

    user = create_user("John Doe", "john@example.com")
    validate_user(user)
    save_user(user)
"""
```

## Function Docstrings

### Simple Function

```python
def greet(name: str) -> str:
    """Returns a greeting message.

    Args:
        name: The name of the person to greet.

    Returns:
        A greeting string.
    """
    return f"Hello, {name}!"
```

### Function with Multiple Arguments

```python
def calculate_total(
    price: float,
    quantity: int,
    discount: float = 0.0,
    tax_rate: float = 0.0
) -> float:
    """Calculates the total cost including discount and tax.

    Args:
        price: The unit price of the item.
        quantity: The number of items.
        discount: The discount as a decimal (e.g., 0.1 for 10% off).
            Defaults to 0.0.
        tax_rate: The tax rate as a decimal (e.g., 0.08 for 8% tax).
            Defaults to 0.0.

    Returns:
        The total cost after applying discount and tax.

    Raises:
        ValueError: If price or quantity is negative.
    """
    if price < 0 or quantity < 0:
        raise ValueError("Price and quantity must be non-negative")
    
    subtotal = price * quantity * (1 - discount)
    return subtotal * (1 + tax_rate)
```

### Function with Complex Return Type

```python
def parse_config(
    config_path: str
) -> tuple[dict[str, str], list[str]]:
    """Parses a configuration file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        A tuple containing:
        - A dictionary of configuration key-value pairs.
        - A list of warning messages encountered during parsing.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        ValueError: If the config file is malformed.
    """
    ...
```

### Function with Side Effects

```python
def update_database(
    user_id: int,
    data: dict[str, Any]
) -> None:
    """Updates user data in the database.

    Note:
        This function modifies the database directly. Ensure proper
        transaction handling in the calling code.

    Args:
        user_id: The ID of the user to update.
        data: Dictionary containing fields to update.

    Raises:
        DatabaseError: If the database operation fails.
        ValueError: If user_id is invalid or data is empty.
    """
    ...
```

## Class Docstrings

### Simple Class

```python
class User:
    """Represents a user in the system.

    Attributes:
        username: The user's unique username.
        email: The user's email address.
        created_at: Timestamp when the user was created.
    """

    def __init__(self, username: str, email: str):
        """Initializes a new User.

        Args:
            username: The desired username.
            email: The user's email address.
        """
        self.username = username
        self.email = email
        self.created_at = datetime.now()
```

### Complex Class with Properties

```python
class Rectangle:
    """Represents a rectangle with width and height.

    This class provides methods for calculating area and perimeter,
    and properties for accessing dimensions.

    Attributes:
        width: The width of the rectangle.
        height: The height of the rectangle.

    Example:
        >>> rect = Rectangle(10, 5)
        >>> rect.area
        50
        >>> rect.perimeter
        30
    """

    def __init__(self, width: float, height: float):
        """Initializes a Rectangle.

        Args:
            width: The width of the rectangle. Must be positive.
            height: The height of the rectangle. Must be positive.

        Raises:
            ValueError: If width or height is not positive.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        """Gets the width of the rectangle."""
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        """Sets the width of the rectangle.

        Args:
            value: The new width. Must be positive.

        Raises:
            ValueError: If value is not positive.
        """
        if value <= 0:
            raise ValueError("Width must be positive")
        self._width = value

    @property
    def area(self) -> float:
        """Calculates and returns the area of the rectangle."""
        return self._width * self._height

    @property
    def perimeter(self) -> float:
        """Calculates and returns the perimeter of the rectangle."""
        return 2 * (self._width + self._height)
```

## Generator Functions

```python
def fibonacci(n: int) -> Iterator[int]:
    """Generates the first n Fibonacci numbers.

    Args:
        n: The number of Fibonacci numbers to generate.

    Yields:
        The next Fibonacci number in the sequence.

    Raises:
        ValueError: If n is negative.

    Example:
        >>> list(fibonacci(5))
        [0, 1, 1, 2, 3]
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b
```

## Exception Classes

```python
class InvalidUserError(Exception):
    """Raised when user data is invalid.

    This exception is raised during user validation when the provided
    data doesn't meet the required criteria.

    Attributes:
        username: The invalid username that caused the error.
        message: Explanation of the validation failure.
    """

    def __init__(self, username: str, message: str):
        """Initializes the exception.

        Args:
            username: The username that failed validation.
            message: Description of why validation failed.
        """
        self.username = username
        self.message = message
        super().__init__(f"{username}: {message}")
```

## Context Manager

```python
class DatabaseConnection:
    """Context manager for database connections.

    Automatically handles connection setup and teardown.

    Example:
        >>> with DatabaseConnection("localhost", 5432) as conn:
        ...     conn.execute("SELECT * FROM users")
    """

    def __init__(self, host: str, port: int):
        """Initializes the database connection parameters.

        Args:
            host: The database host address.
            port: The database port number.
        """
        self.host = host
        self.port = port
        self._connection = None

    def __enter__(self) -> "DatabaseConnection":
        """Establishes the database connection.

        Returns:
            The DatabaseConnection instance.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        self._connection = create_connection(self.host, self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Closes the database connection.

        Args:
            exc_type: The exception type, if an exception occurred.
            exc_val: The exception value, if an exception occurred.
            exc_tb: The exception traceback, if an exception occurred.

        Returns:
            False to propagate exceptions, True to suppress them.
        """
        if self._connection:
            self._connection.close()
        return False
```

## Async Functions

```python
async def fetch_data(url: str, timeout: float = 30.0) -> dict[str, Any]:
    """Asynchronously fetches data from a URL.

    Args:
        url: The URL to fetch data from.
        timeout: Maximum time to wait for response in seconds.
            Defaults to 30.0.

    Returns:
        A dictionary containing the fetched data.

    Raises:
        aiohttp.ClientError: If the request fails.
        asyncio.TimeoutError: If the request times out.

    Example:
        >>> data = await fetch_data("https://api.example.com/data")
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.json()
```

## Test Functions

```python
def test_user_creation():
    """Tests that User objects are created correctly.

    This test verifies:
    - Username is set correctly
    - Email is set correctly
    - created_at is set to current time
    """
    user = User("john_doe", "john@example.com")
    assert user.username == "john_doe"
    assert user.email == "john@example.com"
    assert isinstance(user.created_at, datetime)
```

## Docstring Sections

Common sections in Google-style docstrings:

- **Args:** Function/method parameters
- **Returns:** Return value description
- **Yields:** For generator functions
- **Raises:** Exceptions that may be raised
- **Attributes:** For classes, describes instance attributes
- **Example:** Usage examples
- **Note:** Important notes or warnings
- **Warning:** Critical warnings
- **Todo:** Planned improvements
- **See Also:** Related functions or classes

## Style Guidelines

1. Use triple double quotes (`"""`) for all docstrings
2. First line is a brief summary (one sentence, no period needed if one line)
3. Leave a blank line before sections (Args, Returns, etc.)
4. Capitalize section headers
5. Use imperative mood ("Returns" not "Return")
6. Be specific and concise
7. Include type information in Args and Returns when not obvious from annotations
8. Always document exceptions that can be raised
9. Include examples for complex functions
10. Keep line length under 80 characters where possible
