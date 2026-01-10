# Pytest Patterns for GabeDA Backend

Best practices and patterns for writing reliable backend tests with pytest and Django.

## Table of Contents
1. [Test Organization](#test-organization)
2. [Fixtures](#fixtures)
3. [Database Testing](#database-testing)
4. [API Testing](#api-testing)
5. [Mocking](#mocking)
6. [Parameterization](#parameterization)
7. [Common Patterns](#common-patterns)

## Test Organization

### File Structure

```
tests/
├── unit/
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_serializers.py
│   │   └── test_utils.py
│   └── data_uploads/
│       ├── __init__.py
│       └── test_processors.py
├── integration/
│   ├── test_company_creation.py
│   └── test_user_registration.py
├── api/
│   ├── test_auth_endpoints.py
│   ├── test_company_endpoints.py
│   └── test_upload_endpoints.py
├── conftest.py  # Shared fixtures
└── pytest.ini
```

### Test Class Organization

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserModel:
    """Test User model functionality"""

    @pytest.mark.django_db
    def test_create_user_with_email_creates_user(self):
        """Create user - with email - creates user successfully"""
        # Arrange
        email = 'test@example.com'
        password = 'testpass123'

        # Act
        user = User.objects.create_user(email=email, password=password)

        # Assert
        assert user.email == email
        assert user.check_password(password)
        assert user.is_active

    @pytest.mark.django_db
    def test_create_user_without_email_raises_error(self):
        """Create user - without email - raises ValueError"""
        # Act & Assert
        with pytest.raises(ValueError, match='Email is required'):
            User.objects.create_user(email='', password='testpass123')
```

## Fixtures

### Basic Fixtures

**File**: `conftest.py`

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.accounts.models import Company, CompanyMember

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client for testing"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create test user"""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user(db):
    """Create admin user"""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def test_company(db, test_user):
    """Create test company"""
    return Company.objects.create(
        created_by=test_user,
        rut='76.123.456-7',
        rut_cleaned='761234567',
        name='Test Company',
        industry='retail',
        location='Santiago, Chile',
        currency='CLP'
    )


@pytest.fixture
def company_membership(db, test_company, test_user):
    """Create company membership"""
    return CompanyMember.objects.create(
        company=test_company,
        user=test_user,
        role='admin'
    )
```

### Fixture Scopes

```python
# Function scope (default) - runs before each test
@pytest.fixture
def test_user(db):
    return User.objects.create_user(email='test@example.com', password='test123')

# Class scope - runs once per test class
@pytest.fixture(scope='class')
def test_company(db):
    return Company.objects.create(name='Test Company')

# Module scope - runs once per module
@pytest.fixture(scope='module')
def api_client():
    return APIClient()

# Session scope - runs once per test session
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Setup test database once
        pass
```

### Fixture Factories

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user_factory(db):
    """Factory to create multiple users"""
    def create_user(email=None, **kwargs):
        if email is None:
            email = f'user{User.objects.count() + 1}@example.com'

        return User.objects.create_user(
            email=email,
            password=kwargs.pop('password', 'testpass123'),
            **kwargs
        )
    return create_user


@pytest.fixture
def company_factory(db, test_user):
    """Factory to create multiple companies"""
    def create_company(**kwargs):
        defaults = {
            'created_by': test_user,
            'industry': 'retail',
            'location': 'Santiago, Chile',
            'currency': 'CLP',
        }
        defaults.update(kwargs)

        # Generate unique RUT if not provided
        if 'rut' not in defaults:
            count = Company.objects.count() + 1
            defaults['rut'] = f'76.123.45{count}-7'
            defaults['rut_cleaned'] = f'7612345{count}7'

        return Company.objects.create(**defaults)
    return create_company


# Usage
def test_user_with_multiple_companies(user_factory, company_factory):
    user = user_factory(email='multi@example.com')
    company1 = company_factory(name='Company 1', created_by=user)
    company2 = company_factory(name='Company 2', created_by=user)

    assert Company.objects.filter(created_by=user).count() == 2
```

### Parametrized Fixtures

```python
import pytest


@pytest.fixture(params=['admin', 'member', 'viewer'])
def user_with_role(request, db, test_company):
    """Create user with different roles"""
    role = request.param
    user = User.objects.create_user(
        email=f'{role}@example.com',
        password='testpass123'
    )
    CompanyMember.objects.create(
        company=test_company,
        user=user,
        role=role
    )
    return user, role


# This test runs 3 times (once per role)
def test_user_permissions_by_role(user_with_role, test_company):
    user, role = user_with_role
    membership = CompanyMember.objects.get(user=user, company=test_company)
    assert membership.role == role
```

## Database Testing

### Using pytest-django

```python
import pytest


# Mark single test
@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(email='test@example.com', password='test123')
    assert User.objects.count() == 1


# Mark entire class
@pytest.mark.django_db
class TestUserOperations:
    def test_create_user(self):
        user = User.objects.create_user(email='test@example.com', password='test123')
        assert user.is_active

    def test_delete_user(self):
        user = User.objects.create_user(email='test@example.com', password='test123')
        user.delete()
        assert User.objects.count() == 0
```

### Transaction Testing

```python
import pytest


# Default behavior - each test runs in transaction (rolled back after)
@pytest.mark.django_db
def test_with_automatic_rollback():
    User.objects.create_user(email='test@example.com', password='test123')
    # Transaction rolled back after test


# Transaction=True allows testing transaction behavior
@pytest.mark.django_db(transaction=True)
def test_with_transaction_support():
    from django.db import transaction

    with transaction.atomic():
        user = User.objects.create_user(email='test@example.com', password='test123')
        # Can test transaction.on_commit() callbacks
```

### Database Fixture

```python
import pytest


# Using db fixture (implicit transaction rollback)
def test_with_db_fixture(db):
    User.objects.create_user(email='test@example.com', password='test123')
    assert User.objects.count() == 1


# Using transactional_db fixture
def test_with_transactional_db(transactional_db):
    from django.db import transaction

    with transaction.atomic():
        User.objects.create_user(email='test@example.com', password='test123')
```

## API Testing

### Basic API Tests

```python
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCompanyAPI:
    """Test company API endpoints"""

    def test_list_companies_authenticated_returns_companies(self, api_client, test_user, test_company):
        """List companies - authenticated user - returns companies"""
        # Arrange
        api_client.force_authenticate(user=test_user)

        # Act
        response = api_client.get('/api/accounts/companies/')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_create_company_valid_data_creates_company(self, api_client, test_user):
        """Create company - valid data - creates company"""
        # Arrange
        api_client.force_authenticate(user=test_user)
        data = {
            'rut': '76.123.456-7',
            'name': 'New Company',
            'industry': 'retail'
        }

        # Act
        response = api_client.post('/api/accounts/companies/', data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Company'
        assert Company.objects.filter(name='New Company').exists()

    def test_create_company_unauthenticated_returns_401(self, api_client):
        """Create company - unauthenticated - returns 401"""
        # Arrange
        data = {
            'rut': '76.123.456-7',
            'name': 'New Company',
            'industry': 'retail'
        }

        # Act
        response = api_client.post('/api/accounts/companies/', data)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### Testing Permissions

```python
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestCompanyPermissions:
    """Test company permissions"""

    def test_admin_can_delete_company(self, api_client, test_company):
        """Delete company - admin user - deletes company"""
        # Arrange
        admin = test_company.created_by
        api_client.force_authenticate(user=admin)

        # Act
        response = api_client.delete(f'/api/accounts/companies/{test_company.id}/')

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Company.objects.filter(id=test_company.id).exists()

    def test_member_cannot_delete_company(self, api_client, test_company, user_factory):
        """Delete company - member user - returns 403"""
        # Arrange
        member = user_factory(email='member@example.com')
        CompanyMember.objects.create(
            company=test_company,
            user=member,
            role='member'
        )
        api_client.force_authenticate(user=member)

        # Act
        response = api_client.delete(f'/api/accounts/companies/{test_company.id}/')

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Company.objects.filter(id=test_company.id).exists()
```

### Testing File Uploads

```python
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_upload_csv_file(api_client, test_user, test_company):
    """Upload CSV - valid file - creates data upload"""
    # Arrange
    api_client.force_authenticate(user=test_user)

    csv_content = b'date,product,quantity,total\n2024-01-01,Product A,10,1000'
    csv_file = SimpleUploadedFile(
        'test.csv',
        csv_content,
        content_type='text/csv'
    )

    data = {
        'company': test_company.id,
        'file': csv_file
    }

    # Act
    response = api_client.post('/api/data-uploads/', data, format='multipart')

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert DataUpload.objects.filter(file_name='test.csv').exists()
```

## Mocking

### Mock External Services

```python
import pytest
from unittest.mock import patch, Mock


def test_send_email_notification(test_user):
    """Send email - user registered - sends notification"""
    # Arrange
    with patch('apps.accounts.services.send_mail') as mock_send_mail:
        # Act
        send_welcome_email(test_user)

        # Assert
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        assert test_user.email in call_args[1]['recipient_list']
```

### Mock API Calls

```python
import pytest
from unittest.mock import patch


def test_fetch_external_data():
    """Fetch data - external API - returns data"""
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {'data': 'test'}
    mock_response.status_code = 200

    with patch('requests.get', return_value=mock_response) as mock_get:
        # Act
        result = fetch_external_data('https://api.example.com/data')

        # Assert
        assert result == {'data': 'test'}
        mock_get.assert_called_once_with('https://api.example.com/data')
```

### Mock Django Settings

```python
import pytest
from django.test import override_settings


@override_settings(DEBUG=True)
def test_debug_mode():
    """Test - debug mode enabled - returns debug info"""
    from django.conf import settings
    assert settings.DEBUG is True


@pytest.mark.django_db
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def test_send_email():
    """Send email - uses test backend - email captured"""
    from django.core import mail

    send_welcome_email('test@example.com')

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ['test@example.com']
```

## Parameterization

### Parametrize Tests

```python
import pytest


@pytest.mark.parametrize('rut,expected', [
    ('12.345.678-9', '123456789'),
    ('12345678-9', '123456789'),
    ('12.345.678-K', '12345678K'),
    ('12345678K', '12345678K'),
])
def test_clean_rut_various_formats(rut, expected):
    """Clean RUT - various formats - returns cleaned RUT"""
    result = clean_rut(rut)
    assert result == expected


@pytest.mark.parametrize('email,password,expected_status', [
    ('valid@example.com', 'goodpass123', 200),
    ('invalid@example.com', 'wrongpass', 401),
    ('', 'password', 400),
    ('test@example.com', '', 400),
])
@pytest.mark.django_db
def test_login_various_credentials(api_client, email, password, expected_status):
    """Login - various credentials - returns expected status"""
    # Arrange
    if expected_status == 200:
        User.objects.create_user(email=email, password=password)

    # Act
    response = api_client.post('/api/accounts/login/', {
        'email': email,
        'password': password
    })

    # Assert
    assert response.status_code == expected_status
```

### Parametrize Fixtures

```python
import pytest


@pytest.fixture(params=[
    {'industry': 'retail', 'currency': 'CLP'},
    {'industry': 'manufacturing', 'currency': 'USD'},
    {'industry': 'technology', 'currency': 'EUR'},
])
def company_with_industry(request, db, test_user):
    """Create company with different industries"""
    return Company.objects.create(
        created_by=test_user,
        rut='76.123.456-7',
        rut_cleaned='761234567',
        name=f'Test {request.param["industry"]} Company',
        **request.param
    )


# This test runs 3 times
def test_company_industry_configurations(company_with_industry):
    assert company_with_industry.industry in ['retail', 'manufacturing', 'technology']
    assert company_with_industry.currency in ['CLP', 'USD', 'EUR']
```

## Common Patterns

### Testing Model Methods

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model methods"""

    def test_get_full_name_returns_full_name(self):
        """Get full name - user with first and last name - returns full name"""
        # Arrange
        user = User.objects.create_user(
            email='test@example.com',
            password='test123',
            first_name='John',
            last_name='Doe'
        )

        # Act
        full_name = user.get_full_name()

        # Assert
        assert full_name == 'John Doe'

    def test_get_primary_company_returns_most_recent(self, user_factory, company_factory):
        """Get primary company - user with multiple companies - returns most recent"""
        # Arrange
        user = user_factory()
        company1 = company_factory(name='Company 1', created_by=user)
        company2 = company_factory(name='Company 2', created_by=user)

        CompanyMember.objects.create(company=company1, user=user, role='admin')
        CompanyMember.objects.create(company=company2, user=user, role='admin')

        # Act
        primary_company = user.get_primary_company()

        # Assert
        assert primary_company == company2
```

### Testing Serializers

```python
import pytest
from apps.accounts.serializers import UserSerializer, CompanyCreateSerializer


@pytest.mark.django_db
class TestUserSerializer:
    """Test UserSerializer"""

    def test_serialize_user_returns_expected_fields(self, test_user):
        """Serialize user - valid user - returns expected fields"""
        # Act
        serializer = UserSerializer(test_user)

        # Assert
        assert 'id' in serializer.data
        assert 'email' in serializer.data
        assert 'first_name' in serializer.data
        assert 'password' not in serializer.data  # Should not expose password

    def test_deserialize_user_valid_data_creates_user(self):
        """Deserialize user - valid data - creates user"""
        # Arrange
        data = {
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password2': 'newpass123'
        }

        # Act
        serializer = UserRegistrationSerializer(data=data)

        # Assert
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'new@example.com'
        assert user.check_password('newpass123')
```

### Testing Signals

```python
import pytest
from django.db.models.signals import post_save


@pytest.mark.django_db
def test_company_created_signal_creates_membership(test_user):
    """Company created - signal triggered - creates admin membership"""
    # Arrange & Act
    company = Company.objects.create(
        created_by=test_user,
        rut='76.123.456-7',
        rut_cleaned='761234567',
        name='Test Company',
        industry='retail'
    )

    # Assert
    membership = CompanyMember.objects.filter(
        company=company,
        user=test_user,
        role='admin'
    ).first()

    assert membership is not None
```

### Testing Custom Managers

```python
import pytest


@pytest.mark.django_db
class TestCompanyManager:
    """Test custom Company manager"""

    def test_for_user_returns_user_companies(self, user_factory, company_factory):
        """For user - user with companies - returns user's companies"""
        # Arrange
        user1 = user_factory(email='user1@example.com')
        user2 = user_factory(email='user2@example.com')

        company1 = company_factory(name='Company 1', created_by=user1)
        company2 = company_factory(name='Company 2', created_by=user1)
        company3 = company_factory(name='Company 3', created_by=user2)

        CompanyMember.objects.create(company=company1, user=user1, role='admin')
        CompanyMember.objects.create(company=company2, user=user1, role='admin')
        CompanyMember.objects.create(company=company3, user=user2, role='admin')

        # Act
        user1_companies = Company.objects.for_user(user1)

        # Assert
        assert user1_companies.count() == 2
        assert company1 in user1_companies
        assert company2 in user1_companies
        assert company3 not in user1_companies
```

## Configuration

**File**: `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = gabeda_backend.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --strict-markers
    --tb=short
    --reuse-db
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

**File**: `conftest.py` (project root)

```python
import pytest
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
```
