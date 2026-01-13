# Component Testing Patterns

**Comprehensive patterns for testing React components (and other frameworks) with Vitest and Testing Library.**

Component testing focuses on verifying user-facing behavior by simulating real user interactions. This approach creates resilient tests that remain valid through refactoring and implementation changes.

---

## 🎯 Philosophy: Test Like a User

**Core Principle:** Your tests should interact with components the same way users do - through the rendered UI, not internal implementation.

**Key Guidelines:**
- Query elements by accessible roles and labels
- Trigger events through user interactions
- Assert on visible outputs and behaviors
- Avoid testing implementation details

---

## 🛠️ Setup and Configuration

### Vitest Configuration for Component Testing

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom', // Simulates browser environment
    setupFiles: ['./test/setup.ts'],
    globals: true, // Optional: enables Jest-like globals
    css: true, // Process CSS imports
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}']
    }
  }
})
```

### Test Setup File

```typescript
// test/setup.ts
import '@testing-library/jest-dom' // Adds custom matchers
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// Cleanup after each test to ensure isolation
afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

// Mock window.matchMedia if needed
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
```

---

## 📝 Basic Component Rendering Tests

### Testing Component Output

```typescript
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with text content', () => {
    // Arrange & Act
    render(<Button>Click me</Button>)

    // Assert - Query by accessible role
    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
  })

  it('applies custom className', () => {
    const { container } = render(
      <Button className="custom-class">Test</Button>
    )

    expect(container.firstChild).toHaveClass('custom-class')
    expect(container.firstChild).toHaveClass('btn') // Default class
  })

  it('renders as disabled when prop is true', () => {
    render(<Button disabled>Disabled Button</Button>)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('aria-disabled', 'true')
  })

  it('renders different button variants', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn-primary')

    // Test variant changes
    rerender(<Button variant="secondary">Secondary</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn-secondary')
  })
})
```

### Testing Conditional Rendering

```typescript
import { render, screen } from '@testing-library/react'
import { UserProfile } from './UserProfile'

describe('UserProfile conditional rendering', () => {
  it('shows user info when user is provided', () => {
    const user = { id: '1', name: 'John Doe', email: 'john@example.com' }

    render(<UserProfile user={user} />)

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('john@example.com')).toBeInTheDocument()
  })

  it('shows empty state when no user', () => {
    render(<UserProfile user={null} />)

    expect(screen.getByText(/no user selected/i)).toBeInTheDocument()
    expect(screen.queryByRole('heading')).not.toBeInTheDocument()
  })

  it('shows admin badge for admin users', () => {
    const adminUser = { id: '1', name: 'Admin', role: 'admin' }

    render(<UserProfile user={adminUser} />)

    expect(screen.getByText(/admin/i)).toBeInTheDocument()
    expect(screen.getByText(/admin/i)).toHaveClass('badge-admin')
  })
})
```

---

## 👤 Testing User Interactions

### Using userEvent (Recommended)

`userEvent` provides more realistic user interactions than `fireEvent`.

```typescript
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import { SearchForm } from './SearchForm'

describe('SearchForm user interactions', () => {
  it('handles text input', async () => {
    // Setup userEvent
    const user = userEvent.setup()

    render(<SearchForm />)

    const searchInput = screen.getByRole('textbox', { name: /search/i })

    // Type into input (simulates real typing with delays)
    await user.type(searchInput, 'typescript')

    expect(searchInput).toHaveValue('typescript')
  })

  it('submits form with entered values', async () => {
    const user = userEvent.setup()
    const handleSubmit = vi.fn()

    render(<SearchForm onSubmit={handleSubmit} />)

    // Fill form
    await user.type(screen.getByRole('textbox', { name: /search/i }), 'vitest')

    // Submit
    await user.click(screen.getByRole('button', { name: /search/i }))

    expect(handleSubmit).toHaveBeenCalledWith({
      query: 'vitest'
    })
  })

  it('clears input when clear button is clicked', async () => {
    const user = userEvent.setup()

    render(<SearchForm />)

    const input = screen.getByRole('textbox')

    await user.type(input, 'test query')
    expect(input).toHaveValue('test query')

    await user.click(screen.getByRole('button', { name: /clear/i }))
    expect(input).toHaveValue('')
  })
})
```

### Keyboard Navigation

```typescript
describe('Form keyboard navigation', () => {
  it('allows tabbing between fields', async () => {
    const user = userEvent.setup()

    render(<RegistrationForm />)

    const nameInput = screen.getByLabelText(/name/i)
    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)

    // Focus first input
    await user.click(nameInput)
    expect(nameInput).toHaveFocus()

    // Tab to email
    await user.tab()
    expect(emailInput).toHaveFocus()

    // Tab to password
    await user.tab()
    expect(passwordInput).toHaveFocus()

    // Shift+Tab back to email
    await user.tab({ shift: true })
    expect(emailInput).toHaveFocus()
  })

  it('submits form on Enter key', async () => {
    const user = userEvent.setup()
    const handleSubmit = vi.fn()

    render(<LoginForm onSubmit={handleSubmit} />)

    const emailInput = screen.getByLabelText(/email/i)

    await user.type(emailInput, 'test@example.com')
    await user.keyboard('{Enter}')

    expect(handleSubmit).toHaveBeenCalled()
  })
})
```

### Complex Interactions

```typescript
describe('Dropdown menu interactions', () => {
  it('opens and closes on click', async () => {
    const user = userEvent.setup()

    render(<DropdownMenu />)

    const trigger = screen.getByRole('button', { name: /menu/i })

    // Menu closed initially
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()

    // Click to open
    await user.click(trigger)
    expect(screen.getByRole('menu')).toBeInTheDocument()

    // Click again to close
    await user.click(trigger)
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('selects option from dropdown', async () => {
    const user = userEvent.setup()
    const handleSelect = vi.fn()

    render(<DropdownMenu onSelect={handleSelect} />)

    // Open menu
    await user.click(screen.getByRole('button', { name: /menu/i }))

    // Select option
    await user.click(screen.getByRole('menuitem', { name: /option 2/i }))

    expect(handleSelect).toHaveBeenCalledWith('option-2')
  })
})
```

---

## ⚛️ Testing Custom Hooks

### Basic Hook Testing

```typescript
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { useCounter } from './useCounter'

describe('useCounter hook', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter())

    expect(result.current.count).toBe(0)
  })

  it('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(10))

    expect(result.current.count).toBe(10)
  })

  it('increments counter', () => {
    const { result } = renderHook(() => useCounter())

    act(() => {
      result.current.increment()
    })

    expect(result.current.count).toBe(1)
  })

  it('decrements counter', () => {
    const { result } = renderHook(() => useCounter(5))

    act(() => {
      result.current.decrement()
    })

    expect(result.current.count).toBe(4)
  })

  it('resets counter', () => {
    const { result } = renderHook(() => useCounter(10))

    act(() => {
      result.current.increment()
      result.current.increment()
    })

    expect(result.current.count).toBe(12)

    act(() => {
      result.current.reset()
    })

    expect(result.current.count).toBe(10)
  })
})
```

### Hook with Dependencies

```typescript
describe('useLocalStorage hook', () => {
  it('loads initial value from localStorage', () => {
    localStorage.setItem('test-key', JSON.stringify({ value: 'stored' }))

    const { result } = renderHook(() => useLocalStorage('test-key', { value: 'default' }))

    expect(result.current[0]).toEqual({ value: 'stored' })
  })

  it('updates localStorage when value changes', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))

    act(() => {
      result.current[1]('updated')
    })

    expect(result.current[0]).toBe('updated')
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify('updated'))
  })

  it('handles prop changes', () => {
    const { result, rerender } = renderHook(
      ({ key, initial }) => useLocalStorage(key, initial),
      { initialProps: { key: 'key1', initial: 'value1' } }
    )

    expect(result.current[0]).toBe('value1')

    // Change the key
    rerender({ key: 'key2', initial: 'value2' })

    expect(result.current[0]).toBe('value2')
  })
})
```

---

## 🔄 Testing Async Components

### Loading States

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { UserProfile } from './UserProfile'

// Mock the API module
vi.mock('./api', () => ({
  fetchUser: vi.fn()
}))

import { fetchUser } from './api'

describe('UserProfile async behavior', () => {
  it('shows loading state initially', () => {
    // Mock never resolves
    vi.mocked(fetchUser).mockImplementation(() => new Promise(() => {}))

    render(<UserProfile userId="123" />)

    expect(screen.getByText(/loading/i)).toBeInTheDocument()
    expect(screen.getByRole('status')).toBeInTheDocument() // Loading spinner
  })

  it('displays user data when loaded', async () => {
    const mockUser = {
      id: '123',
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://example.com/avatar.jpg'
    }

    vi.mocked(fetchUser).mockResolvedValue(mockUser)

    render(<UserProfile userId="123" />)

    // Wait for async operation
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getByText('john@example.com')).toBeInTheDocument()
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
  })

  it('handles errors gracefully', async () => {
    vi.mocked(fetchUser).mockRejectedValue(new Error('User not found'))

    render(<UserProfile userId="invalid" />)

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })

    expect(screen.getByText(/user not found/i)).toBeInTheDocument()
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument()
  })

  it('shows retry button on error', async () => {
    const user = userEvent.setup()
    vi.mocked(fetchUser).mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ id: '123', name: 'John' })

    render(<UserProfile userId="123" />)

    // Wait for error
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })

    // Click retry
    await user.click(screen.getByRole('button', { name: /retry/i }))

    // Wait for successful load
    await waitFor(() => {
      expect(screen.getByText('John')).toBeInTheDocument()
    })

    expect(fetchUser).toHaveBeenCalledTimes(2)
  })
})
```

### Testing Data Fetching

```typescript
describe('ProductList data fetching', () => {
  it('fetches and displays products', async () => {
    const mockProducts = [
      { id: '1', name: 'Product 1', price: 19.99 },
      { id: '2', name: 'Product 2', price: 29.99 }
    ]

    vi.mocked(fetchProducts).mockResolvedValue(mockProducts)

    render(<ProductList category="electronics" />)

    // Wait for products to load
    await waitFor(() => {
      expect(screen.getByText('Product 1')).toBeInTheDocument()
    })

    expect(screen.getByText('Product 2')).toBeInTheDocument()
    expect(screen.getByText('$19.99')).toBeInTheDocument()
    expect(screen.getByText('$29.99')).toBeInTheDocument()

    // Verify API was called correctly
    expect(fetchProducts).toHaveBeenCalledWith({ category: 'electronics' })
  })

  it('refetches when category changes', async () => {
    const electronicsProducts = [{ id: '1', name: 'Laptop' }]
    const booksProducts = [{ id: '2', name: 'Book' }]

    vi.mocked(fetchProducts)
      .mockResolvedValueOnce(electronicsProducts)
      .mockResolvedValueOnce(booksProducts)

    const { rerender } = render(<ProductList category="electronics" />)

    await waitFor(() => {
      expect(screen.getByText('Laptop')).toBeInTheDocument()
    })

    // Change category
    rerender(<ProductList category="books" />)

    await waitFor(() => {
      expect(screen.getByText('Book')).toBeInTheDocument()
    })

    expect(screen.queryByText('Laptop')).not.toBeInTheDocument()
    expect(fetchProducts).toHaveBeenCalledTimes(2)
  })
})
```

---

## 🎨 Testing Context Providers

### Basic Context Testing

```typescript
import { render, screen } from '@testing-library/react'
import { ThemeProvider } from './ThemeContext'
import { ThemedButton } from './ThemedButton'

// Helper to render with context
const renderWithTheme = (ui: React.ReactElement, theme = 'light') => {
  return render(
    <ThemeProvider initialTheme={theme}>
      {ui}
    </ThemeProvider>
  )
}

describe('Themed components', () => {
  it('uses light theme by default', () => {
    renderWithTheme(<ThemedButton>Click</ThemedButton>)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('theme-light')
  })

  it('uses dark theme when specified', () => {
    renderWithTheme(<ThemedButton>Click</ThemedButton>, 'dark')

    const button = screen.getByRole('button')
    expect(button).toHaveClass('theme-dark')
  })

  it('updates when theme changes', async () => {
    const user = userEvent.setup()

    renderWithTheme(
      <>
        <ThemeToggle />
        <ThemedButton>Click</ThemedButton>
      </>
    )

    const button = screen.getByRole('button', { name: /click/i })
    expect(button).toHaveClass('theme-light')

    // Toggle theme
    await user.click(screen.getByRole('button', { name: /toggle theme/i }))

    await waitFor(() => {
      expect(button).toHaveClass('theme-dark')
    })
  })
})
```

### Testing Multiple Providers

```typescript
// Helper for multiple providers
const AllProviders = ({ children }) => {
  return (
    <AuthProvider>
      <ThemeProvider>
        <I18nProvider>
          {children}
        </I18nProvider>
      </ThemeProvider>
    </AuthProvider>
  )
}

const renderWithProviders = (ui: React.ReactElement) => {
  return render(ui, { wrapper: AllProviders })
}

describe('App with multiple providers', () => {
  it('renders with all context', () => {
    renderWithProviders(<Dashboard />)

    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})
```

---

## 🧭 Testing with React Router

### Route-Based Testing

```typescript
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { HomePage } from './HomePage'
import { AboutPage } from './AboutPage'

const renderWithRouter = (ui: React.ReactElement, { route = '/' } = {}) => {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  )
}

describe('Routing', () => {
  it('renders home page at root route', () => {
    renderWithRouter(
      <Routes>
        <Route path="/" element={<HomePage />} />
      </Routes>
    )

    expect(screen.getByText(/welcome home/i)).toBeInTheDocument()
  })

  it('renders about page at /about', () => {
    renderWithRouter(
      <Routes>
        <Route path="/about" element={<AboutPage />} />
      </Routes>,
      { route: '/about' }
    )

    expect(screen.getByText(/about us/i)).toBeInTheDocument()
  })

  it('navigates on link click', async () => {
    const user = userEvent.setup()

    renderWithRouter(
      <>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
        </nav>
        <Routes>
          <Route path="/" element={<div>Home Content</div>} />
          <Route path="/about" element={<div>About Content</div>} />
        </Routes>
      </>
    )

    expect(screen.getByText('Home Content')).toBeInTheDocument()

    await user.click(screen.getByRole('link', { name: /about/i }))

    expect(screen.getByText('About Content')).toBeInTheDocument()
    expect(screen.queryByText('Home Content')).not.toBeInTheDocument()
  })
})
```

---

## ♿ Accessibility Testing

### Basic Accessibility Checks

```typescript
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { LoginForm } from './LoginForm'

expect.extend(toHaveNoViolations)

describe('LoginForm accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = render(<LoginForm />)
    const results = await axe(container)

    expect(results).toHaveNoViolations()
  })

  it('has proper ARIA labels', () => {
    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    expect(emailInput).toHaveAttribute('aria-required', 'true')
    expect(emailInput).toHaveAttribute('aria-invalid', 'false')

    const submitButton = screen.getByRole('button', { name: /log in/i })
    expect(submitButton).toHaveAccessibleName()
  })

  it('announces errors to screen readers', async () => {
    const user = userEvent.setup()

    render(<LoginForm />)

    // Submit empty form
    await user.click(screen.getByRole('button', { name: /log in/i }))

    // Check for ARIA live region
    const errorMessage = screen.getByRole('alert')
    expect(errorMessage).toHaveAttribute('aria-live', 'polite')
    expect(errorMessage).toHaveTextContent(/email is required/i)
  })

  it('supports keyboard-only navigation', async () => {
    const user = userEvent.setup()

    render(<LoginForm />)

    // Navigate with Tab
    await user.tab()
    expect(screen.getByLabelText(/email/i)).toHaveFocus()

    await user.tab()
    expect(screen.getByLabelText(/password/i)).toHaveFocus()

    await user.tab()
    expect(screen.getByRole('button', { name: /log in/i })).toHaveFocus()
  })
})
```

---

## 🎭 Component Mocking

### Mocking Child Components

```typescript
import { vi } from 'vitest'

// Mock a child component
vi.mock('./UserAvatar', () => ({
  UserAvatar: vi.fn(({ userId, size }) => (
    <div data-testid="mock-avatar" data-user-id={userId} data-size={size}>
      Mock Avatar
    </div>
  ))
}))

import { ParentComponent } from './ParentComponent'
import { UserAvatar } from './UserAvatar'

describe('ParentComponent', () => {
  it('renders child with correct props', () => {
    render(<ParentComponent userId="123" />)

    expect(UserAvatar).toHaveBeenCalledWith(
      expect.objectContaining({
        userId: '123',
        size: 'medium'
      }),
      expect.anything()
    )

    const avatar = screen.getByTestId('mock-avatar')
    expect(avatar).toHaveAttribute('data-user-id', '123')
  })
})
```

---

## 📊 Performance Testing

### React Profiler

```typescript
import { Profiler } from 'react'
import { vi } from 'vitest'

describe('Component performance', () => {
  it('renders efficiently', () => {
    const onRender = vi.fn()

    const { rerender } = render(
      <Profiler id="test" onRender={onRender}>
        <ExpensiveComponent data={[1, 2, 3]} />
      </Profiler>
    )

    // Initial render
    expect(onRender).toHaveBeenCalledTimes(1)
    const [id, phase, actualDuration] = onRender.mock.calls[0]

    expect(phase).toBe('mount')
    expect(actualDuration).toBeLessThan(100) // < 100ms

    // Re-render with same props (should skip if memoized)
    rerender(
      <Profiler id="test" onRender={onRender}>
        <ExpensiveComponent data={[1, 2, 3]} />
      </Profiler>
    )

    // If properly memoized, shouldn't re-render
    expect(onRender).toHaveBeenCalledTimes(1)
  })
})
```

---

## 📋 Best Practices

### ✅ Do

- **Query by accessible roles/labels** - `getByRole('button')`, `getByLabelText('Email')`
- **Use userEvent over fireEvent** - More realistic interactions
- **Test user-visible behavior** - Focus on what users see and do
- **Wait for async operations** - Use `waitFor`, `findBy` queries
- **Clean up after tests** - Use `afterEach(cleanup)`
- **Mock external dependencies** - APIs, timers, localStorage

### ❌ Don't

- **Test implementation details** - Component state, props, methods
- **Use test IDs excessively** - Prefer accessible queries
- **Assert on snapshots for logic** - Use for UI regression only
- **Query by CSS classes** - Fragile to style changes
- **Test third-party libraries** - Trust they work correctly
- **Write integration tests as unit tests** - Keep tests focused

---

## 🔗 Related Patterns

- **[F.I.R.S.T Principles](../principles/first-principles.md)** - Fast, Isolated component tests
- **[AAA Pattern](../principles/aaa-pattern.md)** - Structure tests clearly
- **[Test Doubles](test-doubles.md)** - Mock child components and APIs
- **[Async Testing](async-testing.md)** - Handle loading and data fetching

---

**Next Steps:**
- Implement [Accessibility Testing](https://testing-library.com/docs/react-testing-library/setup#custom-render)
- Review [Testing Library Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- Explore [Component Testing with Vitest Browser Mode](https://vitest.dev/guide/browser.html)
