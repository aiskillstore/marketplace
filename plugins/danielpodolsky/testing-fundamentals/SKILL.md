---
name: Testing Fundamentals
description: Auto-invoke when reviewing test files or discussing testing strategy. Enforces testing pyramid, strategic coverage, and stack-appropriate frameworks.
---

# Testing Fundamentals Review

> "If you can't test it, you don't understand it. Tests are proof of understanding."

## When to Apply

Activate this skill when:
- Reviewing test files (*.test.ts, *.spec.ts, *.test.js)
- Junior asks about testing strategy
- Completing a feature without tests
- Discussing coverage or test quality

---

## The Testing Pyramid

```
        ▲
       ╱ ╲     E2E (10%)
      ╱   ╲    Playwright - Full user flows
     ╱─────╲
    ╱       ╲  Integration (20%)
   ╱         ╲ Vitest + RTL - Component interactions
  ╱───────────╲
 ╱             ╲ Unit (70%)
╱               ╲ Vitest - Functions, utils, logic
─────────────────
```

- **Unit Tests (70%)**: Fast, isolated, test one thing
- **Integration Tests (20%)**: Components working together
- **E2E Tests (10%)**: Critical user journeys only

---

## Stack-Specific Framework Guide

| Stack | Unit/Integration | E2E |
|-------|------------------|-----|
| Vite + React | **Vitest** + React Testing Library | Playwright |
| Create React App | Jest + RTL | Playwright |
| Next.js | Vitest or Jest + RTL | Playwright |
| Node.js | **Vitest** (native ESM) | - |
| Python | pytest | - |
| Go | go test | - |

**Why Vitest for Vite?**
- 10-20x faster than Jest in watch mode
- Native ESM support
- Same config as Vite (vite.config.ts)
- Compatible with Jest API

---

## What to Test (The 3 Questions)

1. **Happy Path**: Does it work when everything goes right?
2. **Edge Cases**: What happens with empty, null, max values?
3. **Error States**: Does it fail gracefully?

### Good Tests Check:
- [ ] Component renders without crashing
- [ ] User interactions work (click, type, submit)
- [ ] Error states display correctly
- [ ] Loading states appear and disappear
- [ ] Data flows correctly through the component

### Bad Tests Check:
- [ ] Implementation details (internal state, method calls)
- [ ] Styling or CSS classes
- [ ] Third-party library internals
- [ ] Snapshot tests of large components (brittle)

---

## Common Mistakes (Anti-Patterns)

### 1. Testing Implementation, Not Behavior

```typescript
// ❌ BAD: Testing internal state
expect(component.state.isLoading).toBe(true);

// ✅ GOOD: Testing what user sees
expect(screen.getByText('Loading...')).toBeInTheDocument();
```

### 2. Over-Mocking

```typescript
// ❌ BAD: Mock everything
jest.mock('./utils');
jest.mock('./api');
jest.mock('./hooks');
// What are you even testing at this point?

// ✅ GOOD: Mock only external boundaries
vi.mock('./api'); // Mock the API, test the rest
```

### 3. Testing Third-Party Libraries

```typescript
// ❌ BAD: Testing that React Query works
expect(useQuery).toHaveBeenCalledWith('users');

// ✅ GOOD: Testing YOUR code's behavior
await waitFor(() => {
  expect(screen.getByText('User Name')).toBeInTheDocument();
});
```

### 4. Brittle Selectors

```typescript
// ❌ BAD: Breaks if you change CSS
screen.getByClassName('btn-primary-large-blue');

// ✅ GOOD: Semantic and stable
screen.getByRole('button', { name: 'Submit' });
```

### 5. Testing Everything

```typescript
// ❌ BAD: 100% coverage goal
// Results in tests that exist just for coverage

// ✅ GOOD: Strategic coverage
// Test critical paths, edge cases, complex logic
```

---

## Socratic Questions

Ask these instead of giving answers:

1. **Strategy**: "What's the most critical user flow that needs testing?"
2. **Coverage**: "If this test passes but the feature is broken, how would you know?"
3. **Edge Cases**: "What inputs could break this? Empty? Null? 10,000 items?"
4. **Isolation**: "Are you testing YOUR code or a library's code?"
5. **Value**: "Would this test catch a real bug?"

---

## Test Structure (AAA Pattern)

```typescript
describe('LoginForm', () => {
  it('shows error when password is too short', async () => {
    // Arrange
    render(<LoginForm />);

    // Act
    await userEvent.type(screen.getByLabelText('Password'), '123');
    await userEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Assert
    expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();
  });
});
```

---

## Red Flags to Call Out

| Flag | Question |
|------|----------|
| No tests for feature | "What tests prove this works?" |
| Only happy path tested | "What if the API fails? What if input is empty?" |
| Mocking everything | "What are you actually testing here?" |
| Testing implementation | "Would this test break if you refactored but behavior stayed the same?" |
| getByClassName usage | "Is there a more semantic way to select this element?" |
| Large snapshot tests | "Will you actually review this diff when it changes?" |

---

## MCP Usage

### Context7 - Framework Docs
```
Fetch: Vitest documentation
Fetch: React Testing Library queries
Fetch: Playwright best practices
```

### Octocode - Real Examples
```
Search: "vitest react testing library" in popular repos
Search: "playwright e2e test login" for E2E patterns
```

---

## Test Naming Convention

```typescript
// Pattern: it('should [expected behavior] when [condition]')

it('should display error message when password is invalid')
it('should redirect to dashboard when login succeeds')
it('should disable submit button when form is submitting')
```

---

## Interview Gold

> "I implemented comprehensive testing with 85% coverage focusing on critical user flows. I used Vitest for unit tests, React Testing Library for component integration tests, and Playwright for E2E tests covering login, checkout, and payment flows."

Tests are interview talking points. Every test you write is proof you understand the code.
