# Test Patterns

TDD patterns, AAA structure, and coverage requirements for Quetrex.

## Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

1. **RED**: Write a failing test
2. **GREEN**: Write minimal code to make it pass
3. **REFACTOR**: Improve code while keeping tests green

### Why TDD?

- Tests are the specification
- Prevents over-engineering
- Ensures testable code
- Catches regressions early
- Documents behavior

---

## AAA Pattern (Arrange-Act-Assert)

### Structure

Every test should have three distinct sections:

```typescript
it('should [behavior being tested]', () => {
  // ARRANGE: Setup test data, mocks, and preconditions
  const input = createTestData()
  const mockService = jest.fn()

  // ACT: Execute the behavior being tested
  const result = functionUnderTest(input, mockService)

  // ASSERT: Verify the outcome
  expect(result).toBe(expectedValue)
  expect(mockService).toHaveBeenCalledWith(expectedArgs)
})
```

### ARRANGE Section

**Purpose:** Set up test data, mocks, and preconditions

```typescript
// ARRANGE: Setup test data
const userData = {
  email: 'test@example.com',
  password: 'Pass123!',
  name: 'Test User',
}

const mockPrisma = {
  user: {
    create: jest.fn().mockResolvedValue({ id: '123', ...userData }),
    findUnique: jest.fn().mockResolvedValue(null),
  },
}

const mockBcrypt = {
  hash: jest.fn().mockResolvedValue('hashed_password'),
}
```

### ACT Section

**Purpose:** Execute the single behavior being tested

```typescript
// ACT: Execute the behavior
const result = await authService.register(userData)
```

**Important:**
- Only ONE action per test
- If you need multiple actions, write multiple tests
- Action should be a single line or function call

### ASSERT Section

**Purpose:** Verify the outcome matches expectations

```typescript
// ASSERT: Verify outcome
expect(result.id).toBe('123')
expect(result.email).toBe('test@example.com')
expect(result).not.toHaveProperty('password')
expect(mockBcrypt.hash).toHaveBeenCalledWith('Pass123!', 12)
expect(mockPrisma.user.create).toHaveBeenCalledWith({
  data: {
    email: 'test@example.com',
    password: 'hashed_password',
    name: 'Test User',
  },
})
```

### Complete AAA Example

```typescript
describe('AuthService', () => {
  describe('register', () => {
    it('should create user with hashed password', async () => {
      // ARRANGE: Setup test data and mocks
      const userData = {
        email: 'test@example.com',
        password: 'Pass123!',
      }

      const mockPrisma = {
        user: {
          create: jest.fn().mockResolvedValue({
            id: '123',
            email: userData.email,
            password: 'hashed_password',
          }),
          findUnique: jest.fn().mockResolvedValue(null),
        },
      }

      const authService = new AuthService(mockPrisma)

      // ACT: Execute behavior
      const result = await authService.register(userData)

      // ASSERT: Verify outcome
      expect(result.id).toBe('123')
      expect(result).not.toHaveProperty('password')
      expect(mockPrisma.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          email: userData.email,
          password: expect.not.stringMatching(userData.password),
        }),
      })
    })
  })
})
```

---

## Test Coverage Requirements

### Overall Thresholds

- **Overall**: 75%+
- **Business Logic** (src/services/): 90%+
- **Utilities** (src/utils/): 90%+
- **API Routes** (src/app/api/): 75%+
- **UI Components**: 60%+

### What to Test

#### Unit Tests (90% coverage)

**Services (src/services/):**
```typescript
describe('ProjectService', () => {
  describe('create', () => {
    it('should create project with valid data', async () => {
      // Happy path
    })

    it('should throw error if name is empty', async () => {
      // Edge case: empty input
    })

    it('should throw error if user not found', async () => {
      // Error condition: invalid reference
    })

    it('should set default values for optional fields', async () => {
      // Edge case: missing optional fields
    })
  })
})
```

**Utilities (src/utils/):**
```typescript
describe('formatDate', () => {
  it('should format date in YYYY-MM-DD format', () => {
    // Happy path
  })

  it('should handle Date object', () => {
    // Different input type
  })

  it('should handle timestamp number', () => {
    // Different input type
  })

  it('should throw error for invalid input', () => {
    // Error condition
  })
})
```

#### Integration Tests (75% coverage)

**API Routes (src/app/api/):**
```typescript
describe('POST /api/projects', () => {
  it('should create project with valid data', async () => {
    // ARRANGE: Authenticated request with valid data
    const request = createAuthRequest('POST', {
      name: 'Test Project',
      description: 'Test Description',
    })

    // ACT: Call route handler
    const response = await POST(request)

    // ASSERT: Verify response and database state
    expect(response.status).toBe(201)
    const data = await response.json()
    expect(data.id).toBeDefined()
    expect(data.name).toBe('Test Project')

    const dbProject = await prisma.project.findUnique({
      where: { id: data.id },
    })
    expect(dbProject).toBeDefined()
  })

  it('should return 401 if not authenticated', async () => {
    // ARRANGE: Unauthenticated request
    const request = createRequest('POST', { name: 'Test' })

    // ACT
    const response = await POST(request)

    // ASSERT
    expect(response.status).toBe(401)
  })

  it('should return 400 for invalid input', async () => {
    // ARRANGE: Invalid data (missing required field)
    const request = createAuthRequest('POST', {
      description: 'No name provided',
    })

    // ACT
    const response = await POST(request)

    // ASSERT
    expect(response.status).toBe(400)
    const data = await response.json()
    expect(data.error).toContain('name')
  })
})
```

#### E2E Tests (Critical paths only)

**User Journeys:**
```typescript
describe('Project Creation Flow', () => {
  it('should create project from dashboard', async () => {
    // ARRANGE: User logged in and on dashboard
    await loginAs('test@example.com')
    await navigateTo('/dashboard')

    // ACT: Complete creation flow
    await clickButton('New Project')
    await fillInput('name', 'Test Project')
    await fillTextarea('description', 'Test Description')
    await clickButton('Create')

    // ASSERT: Project appears in list
    await expectToSee('Test Project')
    await expectToSee('Test Description')

    // Verify in database
    const project = await db.project.findFirst({
      where: { name: 'Test Project' },
    })
    expect(project).toBeDefined()
  })
})
```

---

## UI Component Testing

### DOM State Assertions (REQUIRED)

UI tests MUST verify what the user sees, not just mock function calls.

#### Bad Example (Mock-Only)

```typescript
// ❌ BAD: Only checks mock, doesn't verify UI state
it('should toggle theme', () => {
  const { getByTestId } = render(<ThemeToggle />)
  const button = getByTestId('theme-toggle')

  fireEvent.click(button)

  expect(mockSetTheme).toHaveBeenCalledWith('dark')
})
```

**Why bad?**
- Doesn't verify button appearance changed
- Doesn't verify icon changed
- Doesn't verify CSS classes applied
- User sees nothing, but test passes

#### Good Example (DOM State)

```typescript
// ✅ GOOD: Verifies actual DOM state
it('should toggle theme', () => {
  const { getByTestId } = render(<ThemeToggle />)
  const button = getByTestId('theme-toggle')

  // Initial state (light theme)
  expect(button).toHaveClass('bg-white', 'text-gray-900')
  expect(button).toHaveAttribute('aria-label', 'Switch to dark theme')
  const icon = within(button).getByTestId('sun-icon')
  expect(icon).toBeInTheDocument()

  // After toggle (dark theme)
  fireEvent.click(button)
  expect(button).toHaveClass('bg-gray-900', 'text-white')
  expect(button).toHaveAttribute('aria-label', 'Switch to light theme')
  const moonIcon = within(button).getByTestId('moon-icon')
  expect(moonIcon).toBeInTheDocument()
  expect(icon).not.toBeInTheDocument()

  // Verify callback was also called
  expect(mockSetTheme).toHaveBeenCalledWith('dark')
})
```

### Visual State Verification Checklist

For UI components, verify:

- [ ] **CSS Classes**: `.toHaveClass('expected-class')`
- [ ] **Inline Styles**: `.toHaveStyle({ color: 'rgb(...)' })`
- [ ] **Visibility**: `.toBeVisible()` / `.not.toBeVisible()`
- [ ] **Attributes**: `.toHaveAttribute('aria-label', 'value')`
- [ ] **Text Content**: `.toHaveTextContent('expected text')`
- [ ] **Element Presence**: `.toBeInTheDocument()` / `.not.toBeInTheDocument()`

### Multi-State Components

Test ALL states:

```typescript
describe('LoadingButton', () => {
  it('should show all states correctly', () => {
    const { getByTestId, rerender } = render(
      <LoadingButton loading={false} disabled={false}>
        Submit
      </LoadingButton>
    )
    const button = getByTestId('loading-button')

    // State 1: Normal (enabled, not loading)
    expect(button).toBeEnabled()
    expect(button).toHaveTextContent('Submit')
    expect(button).toHaveClass('bg-blue-500', 'cursor-pointer')
    expect(within(button).queryByTestId('spinner')).not.toBeInTheDocument()

    // State 2: Loading (disabled, showing spinner)
    rerender(
      <LoadingButton loading={true} disabled={false}>
        Submit
      </LoadingButton>
    )
    expect(button).toBeDisabled()
    expect(button).toHaveClass('bg-blue-300', 'cursor-not-allowed')
    expect(within(button).getByTestId('spinner')).toBeInTheDocument()

    // State 3: Disabled (disabled, not loading)
    rerender(
      <LoadingButton loading={false} disabled={true}>
        Submit
      </LoadingButton>
    )
    expect(button).toBeDisabled()
    expect(button).toHaveClass('bg-gray-300', 'cursor-not-allowed')
    expect(within(button).queryByTestId('spinner')).not.toBeInTheDocument()
  })
})
```

---

## Pattern-Specific Testing

### SSE (Server-Sent Events) Pattern

```typescript
describe('useSSE hook', () => {
  it('should subscribe to SSE on mount', () => {
    // ARRANGE
    const mockEventSource = jest.fn()
    global.EventSource = mockEventSource

    // ACT
    renderHook(() => useSSE('/api/stream'))

    // ASSERT
    expect(mockEventSource).toHaveBeenCalledWith('/api/stream')
  })

  it('should update state when event received', () => {
    // ARRANGE
    let eventHandler: (e: MessageEvent) => void
    const mockEventSource = {
      addEventListener: jest.fn((event, handler) => {
        if (event === 'message') eventHandler = handler
      }),
      close: jest.fn(),
    }
    global.EventSource = jest.fn(() => mockEventSource)

    // ACT
    const { result } = renderHook(() => useSSE('/api/stream'))

    // Simulate event
    eventHandler!(new MessageEvent('message', { data: '{"value": 42}' }))

    // ASSERT
    expect(result.current.data).toEqual({ value: 42 })
  })

  it('should cleanup connection on unmount', () => {
    // ARRANGE
    const mockClose = jest.fn()
    const mockEventSource = {
      addEventListener: jest.fn(),
      close: mockClose,
    }
    global.EventSource = jest.fn(() => mockEventSource)

    // ACT
    const { unmount } = renderHook(() => useSSE('/api/stream'))
    unmount()

    // ASSERT
    expect(mockClose).toHaveBeenCalled()
  })
})
```

### React Server Components Pattern

```typescript
describe('ProjectsPage (Server Component)', () => {
  it('should fetch and render projects', async () => {
    // ARRANGE: Mock Prisma
    const mockProjects = [
      { id: '1', name: 'Project 1' },
      { id: '2', name: 'Project 2' },
    ]
    mockPrisma.project.findMany.mockResolvedValue(mockProjects)

    // ACT: Render server component
    const Component = await ProjectsPage()
    const { getByText } = render(Component)

    // ASSERT: Verify projects rendered
    expect(getByText('Project 1')).toBeInTheDocument()
    expect(getByText('Project 2')).toBeInTheDocument()
  })
})
```

### Zod Validation Pattern

```typescript
describe('User Validation Schema', () => {
  it('should validate correct user data', () => {
    // ARRANGE
    const validData = {
      email: 'test@example.com',
      password: 'Pass123!',
    }

    // ACT
    const result = userSchema.safeParse(validData)

    // ASSERT
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data).toEqual(validData)
    }
  })

  it('should reject invalid email', () => {
    // ARRANGE
    const invalidData = {
      email: 'not-an-email',
      password: 'Pass123!',
    }

    // ACT
    const result = userSchema.safeParse(invalidData)

    // ASSERT
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('email')
    }
  })
})
```

---

## Coverage Reporting

### Run Coverage

```bash
npm test -- --coverage --run
```

### Expected Output

```
---------------------|---------|----------|---------|---------|
File                 | % Stmts | % Branch | % Funcs | % Lines |
---------------------|---------|----------|---------|---------|
All files            |   75.5  |   75.2   |  75.8   |  75.5   |
 src/services/       |   92.1  |   90.5   |  93.2   |  92.1   |
  auth.service.ts    |   95.0  |   92.0   |  96.0   |  95.0   |
  project.service.ts |   90.0  |   88.0   |  91.0   |  90.0   |
 src/utils/          |   91.5  |   89.0   |  92.0   |  91.5   |
  formatDate.ts      |   100   |   100    |  100    |  100    |
  validation.ts      |   85.0  |   80.0   |  86.0   |  85.0   |
 src/app/api/        |   78.0  |   76.0   |  79.0   |  78.0   |
 src/components/     |   62.0  |   60.0   |  63.0   |  62.0   |
---------------------|---------|----------|---------|---------|
```

### Coverage Thresholds

Set in `vitest.config.ts`:

```typescript
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 75,
      functions: 75,
      branches: 75,
      statements: 75,
      // Per-folder thresholds
      perFile: true,
      thresholds: {
        'src/services/**/*.ts': {
          lines: 90,
          functions: 90,
          branches: 90,
          statements: 90,
        },
        'src/utils/**/*.ts': {
          lines: 90,
          functions: 90,
          branches: 90,
          statements: 90,
        },
      },
    },
  },
})
```

---

## Test Organization

### File Structure

```
tests/
├── unit/
│   ├── services/
│   │   ├── auth.service.test.ts
│   │   └── project.service.test.ts
│   └── utils/
│       ├── formatDate.test.ts
│       └── validation.test.ts
├── integration/
│   └── api/
│       ├── auth.test.ts
│       └── projects.test.ts
└── e2e/
    ├── auth-flow.test.ts
    └── project-creation.test.ts
```

### Naming Conventions

- Test files: `*.test.ts` or `*.test.tsx`
- One test file per source file
- Mirror source directory structure

---

## Summary

**AAA Pattern**: Arrange → Act → Assert

**Coverage**: 75% overall, 90% business logic, 60% UI

**UI Testing**: Verify DOM state, not just mocks

**TDD**: Red → Green → Refactor

**Quality**: One behavior per test, clear sections, comprehensive assertions
