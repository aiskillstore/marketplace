# Test Examples for GabeDA

Complete examples for all test types used in the GabeDA application.

## 1. Unit Test Example (Backend - pytest)

**File**: `gabeda_backend/tests/unit/accounts/test_rut_validation.py`

```python
import pytest
from apps.accounts.utils import validate_rut_field, clean_rut, format_rut
from django.core.exceptions import ValidationError


class TestRUTValidation:
    """Test RUT validation utilities"""

    def test_validate_rut_with_valid_format_returns_cleaned(self):
        """Validate RUT - valid format - returns cleaned RUT"""
        # Arrange
        rut = '12.345.678-9'

        # Act
        result = validate_rut_field(rut)

        # Assert
        assert result == '123456789'

    def test_validate_rut_with_invalid_check_digit_raises_error(self):
        """Validate RUT - invalid check digit - raises ValidationError"""
        # Arrange
        rut = '12.345.678-0'

        # Act & Assert
        with pytest.raises(ValidationError, match='RUT inválido'):
            validate_rut_field(rut)

    def test_clean_rut_removes_formatting(self):
        """Clean RUT - formatted input - returns only digits and K"""
        # Arrange
        rut = '12.345.678-K'

        # Act
        result = clean_rut(rut)

        # Assert
        assert result == '12345678K'

    def test_format_rut_adds_formatting(self):
        """Format RUT - unformatted input - returns formatted RUT"""
        # Arrange
        rut = '123456789'

        # Act
        result = format_rut(rut)

        # Assert
        assert result == '12.345.678-9'
```

## 2. Integration Test Example (Backend - pytest)

**File**: `gabeda_backend/tests/integration/test_company_creation.py`

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.accounts.models import Company, CompanyMember

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture to create API client"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Fixture to create test user"""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.mark.django_db
class TestCompanyCreation:
    """Test company creation workflow"""

    def test_create_company_authenticated_user_creates_company_and_membership(self, api_client, test_user):
        """Create company - authenticated user - creates company and admin membership"""
        # Arrange
        api_client.force_authenticate(user=test_user)
        company_data = {
            'rut': '76.123.456-7',
            'name': 'Test Company',
            'industry': 'retail',
            'location': 'Santiago, Chile',
            'currency': 'CLP'
        }

        # Act
        response = api_client.post('/api/accounts/companies/', company_data)

        # Assert
        assert response.status_code == 201
        assert Company.objects.filter(name='Test Company').exists()

        company = Company.objects.get(name='Test Company')
        assert company.created_by == test_user

        membership = CompanyMember.objects.filter(company=company, user=test_user).first()
        assert membership is not None
        assert membership.role == 'admin'

    def test_create_company_duplicate_rut_returns_error(self, api_client, test_user):
        """Create company - duplicate RUT - returns validation error"""
        # Arrange
        api_client.force_authenticate(user=test_user)
        Company.objects.create(
            created_by=test_user,
            rut='76.123.456-7',
            rut_cleaned='761234567',
            name='Existing Company',
            industry='retail'
        )

        company_data = {
            'rut': '76.123.456-7',
            'name': 'New Company',
            'industry': 'retail'
        }

        # Act
        response = api_client.post('/api/accounts/companies/', company_data)

        # Assert
        assert response.status_code == 400
        assert 'rut' in response.data
```

## 3. E2E Test Example (Frontend - Playwright)

**File**: `gabeda_frontend/tests/e2e/login-flow.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('Login - valid credentials - redirects to dashboard', async ({ page }) => {
    // Arrange
    await page.goto('http://localhost:5173/');

    // Act
    await page.fill('input[type="email"]', 'testuser@gabeda.com');
    await page.fill('input[type="password"]', 'gabe123123');
    await page.click('button[type="submit"]');

    // Wait for navigation
    await page.waitForURL('**/dashboard');

    // Assert
    expect(page.url()).toContain('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });

  test('Login - invalid credentials - shows error message', async ({ page }) => {
    // Arrange
    await page.goto('http://localhost:5173/');

    // Act
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Wait for error message
    await page.waitForSelector('[role="alert"]');

    // Assert
    const errorMessage = await page.locator('[role="alert"]').textContent();
    expect(errorMessage).toContain('Invalid credentials');
  });

  test('Login - stores tokens in localStorage', async ({ page }) => {
    // Arrange
    await page.goto('http://localhost:5173/');

    // Act
    await page.fill('input[type="email"]', 'testuser@gabeda.com');
    await page.fill('input[type="password"]', 'gabe123123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    // Assert
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));

    expect(accessToken).toBeTruthy();
    expect(refreshToken).toBeTruthy();
  });
});
```

## 4. Smoke Test Example (Frontend - Playwright)

**File**: `gabeda_frontend/tests/smoke/critical-paths.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Smoke Tests - Critical Paths', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:5173/');
    await page.fill('input[type="email"]', 'testuser@gabeda.com');
    await page.fill('input[type="password"]', 'gabe123123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('Smoke - can access dashboard', async ({ page }) => {
    // Assert
    expect(page.url()).toContain('/dashboard');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('Smoke - can navigate to create company', async ({ page }) => {
    // Act
    await page.click('button:has-text("Create Company")');

    // Assert
    await page.waitForURL('**/create-company');
    expect(page.url()).toContain('/create-company');
  });

  test('Smoke - API endpoints respond', async ({ page }) => {
    // Act - trigger profile API call
    await page.goto('http://localhost:5173/dashboard');

    // Assert - check API response
    const response = await page.waitForResponse(
      response => response.url().includes('/api/accounts/profile/') && response.status() === 200
    );

    expect(response.status()).toBe(200);
  });
});
```

## 5. Component Test Example (Frontend - Vitest + React Testing Library)

**File**: `gabeda_frontend/tests/components/StatsCard.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatsCard from '@/components/dashboard/StatsCard';
import { ChartBarIcon } from '@heroicons/react/24/outline';

describe('StatsCard', () => {
  it('StatsCard - renders with title and value', () => {
    // Arrange & Act
    render(
      <StatsCard
        title="Total Uploads"
        value="42"
        icon={ChartBarIcon}
      />
    );

    // Assert
    expect(screen.getByText('Total Uploads')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('StatsCard - renders icon', () => {
    // Arrange & Act
    const { container } = render(
      <StatsCard
        title="Total Uploads"
        value="42"
        icon={ChartBarIcon}
      />
    );

    // Assert
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });

  it('StatsCard - renders description when provided', () => {
    // Arrange & Act
    render(
      <StatsCard
        title="Total Uploads"
        value="42"
        icon={ChartBarIcon}
        description="Last 30 days"
      />
    );

    // Assert
    expect(screen.getByText('Last 30 days')).toBeInTheDocument();
  });
});
```

## 6. API Endpoint Test Example (Backend - pytest with DRF)

**File**: `gabeda_backend/tests/api/test_company_stats_endpoint.py`

```python
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.accounts.models import Company, CompanyMember
from apps.data_uploads.models import DataUpload

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def test_company(db, test_user):
    company = Company.objects.create(
        created_by=test_user,
        rut='76.123.456-7',
        rut_cleaned='761234567',
        name='Test Company',
        industry='retail'
    )
    CompanyMember.objects.create(
        company=company,
        user=test_user,
        role='admin'
    )
    return company


@pytest.mark.django_db
class TestCompanyStatsEndpoint:
    """Test company stats API endpoint"""

    def test_company_stats_authenticated_user_returns_stats(self, api_client, test_user, test_company):
        """Company stats - authenticated user - returns company statistics"""
        # Arrange
        api_client.force_authenticate(user=test_user)

        # Create test data
        DataUpload.objects.create(
            company=test_company,
            uploaded_by=test_user,
            file_name='test.csv',
            status='completed'
        )

        # Act
        response = api_client.get(f'/api/accounts/companies/{test_company.id}/stats/')

        # Assert
        assert response.status_code == 200
        assert 'total_uploads' in response.data
        assert 'total_members' in response.data
        assert 'analytics_generated' in response.data
        assert response.data['total_uploads'] == 1
        assert response.data['total_members'] == 1

    def test_company_stats_unauthenticated_user_returns_401(self, api_client, test_company):
        """Company stats - unauthenticated user - returns 401"""
        # Act
        response = api_client.get(f'/api/accounts/companies/{test_company.id}/stats/')

        # Assert
        assert response.status_code == 401
```

## Test Data Patterns

### Using Fixtures (pytest)

```python
@pytest.fixture
def sample_companies(db, test_user):
    """Create multiple test companies"""
    companies = []
    for i in range(3):
        company = Company.objects.create(
            created_by=test_user,
            rut=f'76.123.45{i}-7',
            rut_cleaned=f'7612345{i}7',
            name=f'Test Company {i}',
            industry='retail'
        )
        CompanyMember.objects.create(
            company=company,
            user=test_user,
            role='admin'
        )
        companies.append(company)
    return companies
```

### Using Playwright Fixtures

```typescript
import { test as base } from '@playwright/test';

type TestFixtures = {
  authenticatedPage: Page;
};

const test = base.extend<TestFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Login before each test
    await page.goto('http://localhost:5173/');
    await page.fill('input[type="email"]', 'testuser@gabeda.com');
    await page.fill('input[type="password"]', 'gabe123123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');

    await use(page);
  },
});

export { test };
```

## Assertion Patterns

### Backend Assertions

```python
# Exact match
assert response.status_code == 200
assert company.name == 'Test Company'

# Contains
assert 'error' in response.data
assert 'Test Company' in str(companies)

# Existence
assert Company.objects.filter(name='Test Company').exists()
assert membership is not None

# Count
assert Company.objects.count() == 3
assert len(response.data) == 5

# Type checks
assert isinstance(response.data, dict)
assert isinstance(companies, list)
```

### Frontend Assertions (Playwright)

```typescript
// Visibility
await expect(page.locator('h1')).toBeVisible();
await expect(page.locator('[data-testid="company-name"]')).toBeHidden();

// Text content
await expect(page.locator('h1')).toContainText('Dashboard');
await expect(page.locator('.company-name')).toHaveText('Test Company');

// URL
expect(page.url()).toContain('/dashboard');
await page.waitForURL('**/dashboard');

// Count
const items = await page.locator('.company-item').count();
expect(items).toBe(2);

// Attributes
await expect(page.locator('input[name="email"]')).toHaveValue('test@example.com');
await expect(page.locator('button')).toBeDisabled();
```

## Test Cleanup

### Backend Cleanup (pytest with transactions)

```python
@pytest.mark.django_db(transaction=True)
class TestWithCleanup:
    """Tests that need transaction support"""

    def test_example(self, db):
        # Test runs in transaction
        # Automatically rolled back after test
        pass
```

### Frontend Cleanup (Playwright)

```typescript
test.afterEach(async ({ page }) => {
  // Clear localStorage
  await page.evaluate(() => localStorage.clear());

  // Clear cookies
  await page.context().clearCookies();
});
```
