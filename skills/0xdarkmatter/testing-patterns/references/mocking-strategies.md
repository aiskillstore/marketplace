# Mocking Strategies

When, what, and how to mock effectively.

## When to Mock

### ALWAYS Mock
- External HTTP APIs
- Databases in unit tests
- File system in unit tests
- Time-dependent operations
- Random number generators
- Email/SMS services

### SOMETIMES Mock
- Internal services (depends on test type)
- Caches
- Message queues

### NEVER Mock
- The code under test itself
- Simple value objects
- Pure functions without side effects

## The Testing Boundary

```
┌─────────────────────────────────────────────────────┐
│                  Your Application                    │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Business │ -> │ Service  │ -> │Repository│      │
│  │  Logic   │    │  Layer   │    │  Layer   │      │
│  └──────────┘    └──────────┘    └──────────┘      │
│                                        │            │
│                                        ▼            │
│                              ┌─────────────────┐   │
│                              │   BOUNDARY      │   │
│                              │ (Mock Here!)    │   │
│                              └─────────────────┘   │
│                                        │            │
└────────────────────────────────────────│────────────┘
                                         ▼
                              ┌─────────────────┐
                              │External Services│
                              │ - Database      │
                              │ - APIs          │
                              │ - File System   │
                              └─────────────────┘
```

## Mock Patterns

### Stub Pattern (Canned Responses)

```python
# Use when you need predictable return values
def test_get_user_returns_user_data(mocker):
    mock_db = mocker.patch("app.database.get_user")
    mock_db.return_value = {"id": 1, "name": "Alice"}

    result = user_service.get_user(1)

    assert result["name"] == "Alice"
```

### Mock Pattern (Verify Interactions)

```python
# Use when you need to verify calls were made
def test_order_sends_confirmation_email(mocker):
    mock_email = mocker.patch("app.email.send")

    order_service.place_order(user_id=1, items=[...])

    mock_email.assert_called_once_with(
        to="user@example.com",
        subject="Order Confirmation",
        body=mocker.ANY
    )
```

### Spy Pattern (Record + Real Implementation)

```python
# Use when you want real behavior but need to track calls
def test_caching_reduces_db_calls(mocker):
    spy = mocker.spy(database, "query")

    # First call hits database
    result1 = cached_service.get_data("key")
    # Second call should use cache
    result2 = cached_service.get_data("key")

    assert spy.call_count == 1  # Only called once
    assert result1 == result2
```

### Fake Pattern (Simplified Implementation)

```python
# Use for complex dependencies that need real behavior
class FakeEmailService:
    def __init__(self):
        self.sent_emails = []

    def send(self, to, subject, body):
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })

def test_order_workflow(fake_email):
    order_service = OrderService(email_service=fake_email)
    order_service.place_order(user_id=1, items=[...])

    assert len(fake_email.sent_emails) == 1
    assert "Order Confirmation" in fake_email.sent_emails[0]["subject"]
```

## Mock Anti-Patterns

### Over-Mocking

```python
# BAD - Mocking everything
def test_order_total(mocker):
    mock_cart = mocker.Mock()
    mock_item = mocker.Mock()
    mock_item.price = 100
    mock_cart.items = [mock_item]
    mock_cart.calculate_total.return_value = 100  # ?!

    # This tests nothing - we mocked the thing we're testing!
    assert mock_cart.calculate_total() == 100

# GOOD - Only mock boundaries
def test_order_total():
    cart = Cart()
    cart.add_item(Item(price=100))

    assert cart.calculate_total() == 100
```

### Mocking Too Deep

```python
# BAD - Mocking internal implementation
def test_process_order(mocker):
    mocker.patch("app.order.Order._validate_inventory")
    mocker.patch("app.order.Order._calculate_tax")
    mocker.patch("app.order.Order._apply_discount")
    # Now coupled to internal implementation!

# GOOD - Mock at the boundary
def test_process_order(mocker):
    mocker.patch("app.inventory_service.check_availability")
    mocker.patch("app.tax_service.calculate")
    # External services, not internal methods
```

### Mock Setup Longer Than Test

```python
# BAD - Test is mostly setup
def test_user_registration(mocker):
    mock_db = mocker.patch("app.db")
    mock_email = mocker.patch("app.email")
    mock_validator = mocker.patch("app.validator")
    mock_logger = mocker.patch("app.logger")
    mock_db.create_user.return_value = {"id": 1}
    mock_email.send.return_value = True
    mock_validator.validate.return_value = []
    # ... 20 more lines of setup

    # The actual test is tiny
    result = register_user("test@example.com")
    assert result.success

# GOOD - Use fixtures and factories
@pytest.fixture
def registration_mocks(mocker):
    return RegistrationMocks(mocker)  # Encapsulate setup

def test_user_registration(registration_mocks):
    result = register_user("test@example.com")
    assert result.success
```

## Dependency Injection for Testability

```python
# Hard to test - creates own dependencies
class OrderService:
    def __init__(self):
        self.db = Database()  # Can't mock!
        self.email = EmailService()

# Easy to test - dependencies injected
class OrderService:
    def __init__(self, db: Database, email: EmailService):
        self.db = db
        self.email = email

# Test with mocks
def test_order_service(mocker):
    mock_db = mocker.Mock()
    mock_email = mocker.Mock()
    service = OrderService(db=mock_db, email=mock_email)
```

## Contract Testing

When mocking external services, verify your mocks match reality:

```python
# Record real responses
@pytest.fixture(scope="session")
def vcr_config():
    return {"record_mode": "once"}

@pytest.mark.vcr()
def test_github_api():
    response = github_client.get_user("octocat")
    assert response["login"] == "octocat"

# Or use contract testing (Pact)
def test_user_service_contract():
    pact.given("user exists").upon_receiving(
        "a request for user"
    ).with_request(
        method="GET",
        path="/users/1"
    ).will_respond_with(
        status=200,
        body={"id": 1, "name": Like("string")}
    )
```
