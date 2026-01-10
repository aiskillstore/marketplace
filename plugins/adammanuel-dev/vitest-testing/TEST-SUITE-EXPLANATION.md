# UserService Test Suite - Pattern Application Guide

This document explains how the comprehensive test suite for `UserService` applies patterns from the vitest-testing skill.

---

## 📚 Vitest-Testing Skill References

### Primary Pattern Sources
1. **[Black Box Testing Strategy](strategies/black-box-testing.md)** - Testing through public API only
2. **[F.I.R.S.T Principles](principles/first-principles.md)** - Fast, Isolated, Repeatable, Self-Checking, Timely
3. **[AAA Pattern](principles/aaa-pattern.md)** - Arrange-Act-Assert structure
4. **[Async Testing Patterns](patterns/async-testing.md)** - Promise handling and async/await
5. **[Error Testing Patterns](patterns/error-testing.md)** - Exception and error scenario coverage

---

## 🎯 Pattern Application Breakdown

### 1. F.I.R.S.T Principles Application

#### ⚡ Fast
**Reference:** `principles/first-principles.md` (lines 9-148)

**Applied:**
- All tests use mocked dependencies (no real database or email service)
- Tests complete in < 10ms each
- No I/O operations, network calls, or file system access

**Example from test suite:**
```typescript
beforeEach(() => {
  mockDb = {
    users: {
      create: vi.fn(),
      findByEmail: vi.fn()
    }
  }
  // Mocks ensure speed - no real database calls
})
```

**Why it matters:** Fast tests encourage frequent execution during development, providing immediate feedback.

---

#### 🔒 Isolated
**Reference:** `principles/first-principles.md` (lines 151-297)

**Applied:**
- Fresh mock instances in `beforeEach` for every test
- No shared state between tests
- Tests can run in any order or in parallel
- Each test verifies one specific behavior

**Example from test suite:**
```typescript
beforeEach(() => {
  // Fresh mocks for each test - complete isolation
  mockDb = { /* new mocks */ }
  mockEmailService = { /* new mocks */ }
  userService = new UserService(mockDb, mockEmailService)
})
```

**Why it matters:** Isolated tests pinpoint exact failure locations and don't affect each other.

---

#### 🔁 Repeatable
**Reference:** `principles/first-principles.md` (lines 300-422)

**Applied:**
- Deterministic mock responses (no randomness)
- No reliance on real time or external APIs
- Same inputs always produce same outputs

**Example from test suite:**
```typescript
it('[REPEATABLE] produces same result on multiple runs', async () => {
  const expectedUser: User = {
    id: 'user-repeatable',
    email: userData.email,
    name: userData.name,
    createdAt: new Date('2024-01-15T10:00:00Z') // Fixed date
  }
  // Same result every run
})
```

**Why it matters:** Repeatable tests build trust - failures always indicate real bugs.

---

#### ✔️ Self-Checking
**Reference:** `principles/first-principles.md` (lines 425-514)

**Applied:**
- All tests use `expect()` assertions
- No manual log inspection required
- Clear automated pass/fail criteria
- CI/CD integration ready

**Example from test suite:**
```typescript
// Self-checking assertions
expect(result.email).toBe(userData.email)
expect(mockDb.users.create).toHaveBeenCalledTimes(1)
expect(mockEmailService.sendWelcome).toHaveBeenCalledWith(userData.email)
```

**Why it matters:** Automated verification scales infinitely with zero manual effort.

---

#### ⏱️ Timely / Maintainable
**Reference:** `principles/first-principles.md` (lines 517-620)

**Applied:**
- Clear, descriptive test names explain behavior
- Simple assertions easy to update
- Tests serve as living documentation
- Well-organized test structure

**Example from test suite:**
```typescript
describe('register - Email Validation', () => {
  it('rejects email without @ symbol', async () => {
    // Clear purpose from test name
    // Simple, maintainable assertions
  })
})
```

**Why it matters:** Maintainable tests remain valuable assets as code evolves.

---

### 2. AAA Pattern (Arrange-Act-Assert)

**Reference:** `principles/aaa-pattern.md` (entire document)

**Applied:** Every test follows strict AAA structure with clear phase separation.

#### Arrange Phase
**Reference:** `principles/aaa-pattern.md` (lines 27-115)

**Example from test suite:**
```typescript
it('registers a new user with valid data', async () => {
  // --- ARRANGE ---
  const validUserData = {
    email: 'john.doe@example.com',
    name: 'John Doe',
    password: 'SecurePass123!'
  }

  const expectedUser: User = {
    id: 'user-123',
    email: validUserData.email,
    name: validUserData.name,
    createdAt: new Date('2024-01-15T10:00:00Z')
  }

  mockDb.users.findByEmail.mockResolvedValue(null)
  mockDb.users.create.mockResolvedValue(expectedUser)
  mockEmailService.sendWelcome.mockResolvedValue(undefined)

  // Setup complete - ready for action
})
```

**Applied correctly:**
- Test data clearly defined
- Expected values declared upfront
- Mocks configured with return values
- No actions executed yet

---

#### Act Phase
**Reference:** `principles/aaa-pattern.md` (lines 118-187)

**Example from test suite:**
```typescript
  // --- ACT ---
  const result = await userService.register(validUserData)
```

**Applied correctly:**
- Single focused action (one line)
- Calls public API only (not private methods)
- Result captured for verification

---

#### Assert Phase
**Reference:** `principles/aaa-pattern.md` (lines 189-294)

**Example from test suite:**
```typescript
  // --- ASSERT ---
  expect(result).toEqual(expectedUser)

  // Verify database interactions
  expect(mockDb.users.findByEmail).toHaveBeenCalledWith(validUserData.email)
  expect(mockDb.users.findByEmail).toHaveBeenCalledTimes(1)

  expect(mockDb.users.create).toHaveBeenCalledWith({
    email: validUserData.email,
    name: validUserData.name,
    passwordHash: 'hashed_SecurePass123!',
    createdAt: expect.any(Date)
  })

  // Verify email was sent
  expect(mockEmailService.sendWelcome).toHaveBeenCalledWith(validUserData.email)
})
```

**Applied correctly:**
- Verifies return value
- Checks mock interactions
- Multiple assertions verify same outcome
- No additional actions

---

### 3. Black Box Testing Strategy

**Reference:** `strategies/black-box-testing.md` (entire document)

**Core Principle:** Test WHAT the code does, not HOW it does it.

#### Testing Only Public API
**Reference:** `strategies/black-box-testing.md` (lines 9-17)

**Applied:**
- Tests only call `register()` method (public API)
- Never test `hashPassword()` private method directly
- Verify behavior through observable outputs

**Example from test suite:**
```typescript
it('successfully hashes password before storage', async () => {
  // Black Box: Don't call hashPassword() directly
  // Instead, verify it happened through observable behavior

  await userService.register(userData)

  expect(mockDb.users.create).toHaveBeenCalledWith(
    expect.objectContaining({
      passwordHash: 'hashed_MyPlainTextPassword' // Verify hashing occurred
    })
  )
})
```

**NOT testing private implementation:**
```typescript
// ❌ BAD: Don't do this
const hashed = userService['hashPassword']('test') // Accessing private method
```

---

#### Equivalence Partitioning
**Reference:** `strategies/black-box-testing.md` (lines 39-73)

**Applied:** Dividing input data into logical groups.

**Example from test suite:**
```typescript
it('accepts valid email formats', async () => {
  // Equivalence Partitioning: Testing valid email partition
  const validEmails = [
    'simple@example.com',           // Simple format
    'user.name@example.com',        // With dots
    'user+tag@example.co.uk',       // With plus sign
    'user_name@sub.example.com'     // With underscore and subdomain
  ]

  for (const email of validEmails) {
    await expect(
      userService.register({ email, name: 'Test', password: 'Pass123' })
    ).resolves.toBeDefined()
  }
})
```

**Partitions identified:**
1. Valid emails (various formats)
2. Invalid emails (missing @)
3. Empty emails

---

#### Boundary Value Analysis
**Reference:** `strategies/black-box-testing.md` (lines 75-106)

**Applied:** Testing edges of input ranges.

**Example from test suite:**
```typescript
describe('register - Boundary Value Testing', () => {
  it('handles minimum valid email length', async () => {
    const minEmailData = {
      email: 'a@b.c', // Minimal valid email (boundary)
      name: 'Min Email',
      password: 'Password123'
    }
    // Test passes at lower boundary
  })

  it('handles maximum realistic email length', async () => {
    const localPart = 'a'.repeat(64)  // Max local part (boundary)
    const domain = 'b'.repeat(180) + '.com'
    const maxEmail = `${localPart}@${domain}`
    // Test passes at upper boundary
  })
})
```

**Boundaries tested:**
- Minimum email length: `a@b.c`
- Maximum email length: 254 characters (RFC 5321)
- Empty string boundary
- Special character boundaries

---

### 4. Async Testing Patterns

**Reference:** `patterns/async-testing.md` (entire document)

#### Promise Testing with async/await
**Reference:** `patterns/async-testing.md` (lines 20-77)

**Applied:**
- All async tests use `async/await` syntax
- Always await async assertions
- Proper error handling with `.rejects`

**Example from test suite:**
```typescript
it('registers a new user with valid data', async () => {
  // async function

  mockDb.users.create.mockResolvedValue(expectedUser)

  const result = await userService.register(validUserData) // await the call

  expect(result).toEqual(expectedUser)
})
```

---

#### Testing Promise Rejections
**Reference:** `patterns/async-testing.md` (lines 109-136)

**Applied:**
- Use `.rejects` matcher for async errors
- Verify error messages
- Check no side effects occurred

**Example from test suite:**
```typescript
it('rejects email without @ symbol', async () => {
  const invalidUserData = {
    email: 'invalid-email-no-at-sign',
    name: 'Invalid User',
    password: 'Password123'
  }

  const registerInvalidUser = () => userService.register(invalidUserData)

  await expect(registerInvalidUser()).rejects.toThrow('Invalid email format')

  // Verify no side effects
  expect(mockDb.users.create).not.toHaveBeenCalled()
})
```

---

#### Mocking Async Dependencies
**Reference:** `patterns/async-testing.md` (lines 80-122)

**Applied:**
- Mock async database calls
- Mock async email service
- Control timing and responses

**Example from test suite:**
```typescript
beforeEach(() => {
  mockDb = {
    users: {
      create: vi.fn(),           // Sync mock
      findByEmail: vi.fn()       // Sync mock
    }
  }

  // Configure async responses
  mockDb.users.create.mockResolvedValue(user)
  mockDb.users.findByEmail.mockRejectedValue(error)
})
```

---

### 5. Error Testing Patterns

**Reference:** `patterns/error-testing.md` (entire document)

#### Testing Expected Exceptions
**Reference:** `patterns/error-testing.md` (lines 28-68)

**Applied:**
- Test all error scenarios thoroughly
- Verify error messages are clear
- Check state consistency after errors

**Example from test suite:**
```typescript
describe('register - Email Validation', () => {
  it('rejects email without @ symbol', async () => {
    await expect(registerInvalidUser()).rejects.toThrow('Invalid email format')

    // Verify no database calls were made
    expect(mockDb.users.findByEmail).not.toHaveBeenCalled()
    expect(mockDb.users.create).not.toHaveBeenCalled()
  })
})
```

---

#### Testing Error Messages
**Reference:** `patterns/error-testing.md` (lines 70-102)

**Applied:**
- Verify exact error messages
- Ensure messages are helpful
- Include context in assertions

**Example from test suite:**
```typescript
it('rejects registration when email already exists', async () => {
  mockDb.users.findByEmail.mockResolvedValue(existingUser)

  await expect(registerDuplicate()).rejects.toThrow('Email already exists')

  // Specific, helpful error message
})
```

---

#### Testing Async Errors
**Reference:** `patterns/error-testing.md` (lines 105-186)

**Applied:**
- Handle promise rejections
- Test API errors
- Verify error propagation

**Example from test suite:**
```typescript
describe('register - Database Failure Scenarios', () => {
  it('propagates database error when findByEmail fails', async () => {
    const dbError = new Error('Database connection failed')
    mockDb.users.findByEmail.mockRejectedValue(dbError)

    await expect(register()).rejects.toThrow('Database connection failed')

    // Verify no side effects
    expect(mockDb.users.create).not.toHaveBeenCalled()
  })
})
```

---

#### Testing Error Recovery
**Reference:** `patterns/error-testing.md` (lines 357-401)

**Applied:**
- Verify state consistency after errors
- Check rollback behavior
- Ensure no partial updates

**Example from test suite:**
```typescript
it('propagates database error when create fails', async () => {
  mockDb.users.findByEmail.mockResolvedValue(null)
  const createError = new Error('Failed to insert into database')
  mockDb.users.create.mockRejectedValue(createError)

  await expect(register()).rejects.toThrow('Failed to insert into database')

  // Verify email was NOT sent (rollback behavior)
  expect(mockEmailService.sendWelcome).not.toHaveBeenCalled()
})
```

---

## 🎨 Test Organization Structure

### Test Suite Hierarchy

```
UserService
├── register - Happy Paths
│   ├── registers a new user with valid data
│   ├── successfully hashes password before storage
│   └── sends welcome email after user creation
├── register - Email Validation
│   ├── rejects email without @ symbol
│   ├── rejects empty email
│   └── accepts valid email formats
├── register - Duplicate Email Handling
│   ├── rejects registration when email already exists
│   └── checks for existing email before creating user
├── register - Database Failure Scenarios
│   ├── propagates database error when findByEmail fails
│   └── propagates database error when create fails
├── register - Email Service Failure Scenarios
│   ├── propagates email service error
│   └── handles email service timeout
├── register - Edge Cases
│   ├── handles special characters in email
│   ├── handles very long names
│   ├── handles special characters in name
│   └── handles empty password string
├── register - Boundary Value Testing
│   ├── handles minimum valid email length
│   └── handles maximum realistic email length
└── register - F.I.R.S.T Compliance Verification
    ├── [FAST] completes registration in minimal time
    ├── [ISOLATED] runs independently of other tests
    ├── [REPEATABLE] produces same result on multiple runs
    ├── [SELF-CHECKING] automatically determines pass/fail
    └── [TIMELY] tests are easy to maintain and understand
```

**Organization benefits:**
- Clear grouping by scenario type
- Easy to locate specific test cases
- Logical flow from happy paths to edge cases
- Self-documenting structure

---

## 📊 Coverage Summary

### Scenarios Covered

1. **Happy Paths (3 tests)**
   - Successful user registration
   - Password hashing verification
   - Welcome email sending

2. **Email Validation (3 tests)**
   - Invalid format rejection
   - Empty email rejection
   - Valid format acceptance

3. **Duplicate Handling (2 tests)**
   - Duplicate rejection
   - Check-before-create verification

4. **Database Failures (2 tests)**
   - findByEmail failure
   - create failure

5. **Email Service Failures (2 tests)**
   - Service unavailable error
   - Timeout handling

6. **Edge Cases (4 tests)**
   - Special characters in email
   - Very long names
   - Special characters in name
   - Empty password

7. **Boundary Values (2 tests)**
   - Minimum email length
   - Maximum email length

8. **F.I.R.S.T Verification (5 tests)**
   - Fast execution
   - Isolation verification
   - Repeatability check
   - Self-checking validation
   - Maintainability demonstration

**Total: 23 comprehensive tests**

---

## ✅ Checklist: Pattern Compliance

### Black Box Testing ✅
- [x] Tests only public API (`register()` method)
- [x] Never accesses private methods (`hashPassword()`)
- [x] Verifies behavior through observable outputs
- [x] Uses equivalence partitioning
- [x] Uses boundary value analysis
- [x] Focuses on WHAT, not HOW

### F.I.R.S.T Principles ✅
- [x] **Fast:** All tests use mocks, complete in < 10ms
- [x] **Isolated:** Fresh mocks in `beforeEach`, no shared state
- [x] **Repeatable:** Deterministic responses, no randomness
- [x] **Self-Checking:** All tests use `expect()` assertions
- [x] **Timely:** Clear names, simple assertions, maintainable

### AAA Pattern ✅
- [x] All tests clearly divided into Arrange-Act-Assert
- [x] Comments mark each phase
- [x] Arrange sets up test data and mocks
- [x] Act contains single focused action
- [x] Assert verifies expected outcomes

### Async Testing ✅
- [x] All async tests use `async/await`
- [x] Always await async calls
- [x] Use `.rejects` for error testing
- [x] Mock async dependencies properly

### Error Testing ✅
- [x] Test all error scenarios
- [x] Verify error messages
- [x] Check state consistency after errors
- [x] Test error propagation
- [x] Verify no side effects on error

---

## 🎯 Key Takeaways

1. **Black Box Focus:** Tests survive refactoring because they test behavior, not implementation.

2. **F.I.R.S.T Compliance:** Fast, isolated, repeatable tests build trust and encourage frequent execution.

3. **AAA Structure:** Clear phase separation makes tests readable and maintainable.

4. **Comprehensive Coverage:** Tests cover happy paths, error scenarios, edge cases, and boundaries.

5. **Mock Usage:** Proper mocking ensures speed and isolation while maintaining test reliability.

6. **Living Documentation:** Test names and structure document expected behavior.

---

## 📚 Additional Resources

- **[vitest-testing skill root](.)** - Complete testing pattern library
- **[Black Box Testing](strategies/black-box-testing.md)** - Deep dive into behavior testing
- **[F.I.R.S.T Principles](principles/first-principles.md)** - Quality test attributes
- **[AAA Pattern](principles/aaa-pattern.md)** - Test structure guidelines
- **[Async Testing](patterns/async-testing.md)** - Promise and async/await patterns
- **[Error Testing](patterns/error-testing.md)** - Exception handling patterns

---

**This test suite demonstrates inevitable testing:** Tests that feel like the only sensible way to verify the `UserService` behavior, written in a way that makes maintenance effortless and refactoring fearless.
