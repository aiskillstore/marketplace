# Code Quality Best Practices Checklist

Comprehensive guide for writing clean, maintainable, and high-quality code.

## SOLID Principles

### Single Responsibility Principle (SRP)
- [ ] Each class/module has one reason to change
- [ ] Functions do one thing well
- [ ] Classes have single, well-defined purpose
- [ ] Separation of concerns maintained

### Open/Closed Principle (OCP)
- [ ] Open for extension, closed for modification
- [ ] Use inheritance/composition for new behavior
- [ ] Avoid modifying existing working code
- [ ] Use strategy pattern, plugins, or decorators

### Liskov Substitution Principle (LSP)
- [ ] Subtypes can replace base types
- [ ] Derived classes don't break parent class contracts
- [ ] Overridden methods maintain expected behavior
- [ ] Preconditions not strengthened in subtypes
- [ ] Postconditions not weakened in subtypes

### Interface Segregation Principle (ISP)
- [ ] Clients shouldn't depend on unused interfaces
- [ ] Split large interfaces into smaller ones
- [ ] Role-based interfaces
- [ ] Avoid fat interfaces

### Dependency Inversion Principle (DIP)
- [ ] Depend on abstractions, not concretions
- [ ] High-level modules don't depend on low-level modules
- [ ] Use dependency injection
- [ ] Inversion of control containers where appropriate

---

## Clean Code Practices

### Naming
- [ ] Use meaningful, descriptive names
- [ ] Names reveal intent
- [ ] Avoid abbreviations (unless standard)
- [ ] Use pronounceable names
- [ ] Use searchable names
- [ ] Avoid encoding (Hungarian notation)
- [ ] Class names are nouns
- [ ] Function names are verbs
- [ ] Boolean variables start with is/has/can
- [ ] Constants are UPPER_SNAKE_CASE
- [ ] Avoid mental mapping

**Good Examples**:
```typescript
// Good
const userAge = 25;
const isAuthenticated = true;
function calculateTotalPrice() {}
class UserRepository {}

// Bad
const u = 25;  // What is 'u'?
const flag = true;  // What flag?
function calc() {}  // Calculate what?
class UM {}  // What is UM?
```

### Functions
- [ ] Keep functions small (< 20 lines ideal)
- [ ] One level of abstraction per function
- [ ] Do one thing (SRP)
- [ ] Descriptive names
- [ ] Few parameters (0-3 ideal, max 5)
- [ ] No side effects
- [ ] Command-query separation
- [ ] Extract to reduce complexity
- [ ] Avoid flag parameters
- [ ] Pure functions when possible

**Parameter Guidelines**:
```typescript
// Too many parameters - hard to remember order
function createUser(name, email, password, age, address, phone, role) {}

// Better - use object parameter
function createUser(userData: UserData) {}

// Best - with type
interface UserData {
  name: string;
  email: string;
  password: string;
  age?: number;
  address?: string;
  phone?: string;
  role?: UserRole;
}
```

### Comments
- [ ] Explain WHY, not WHAT
- [ ] Code is self-documenting when possible
- [ ] Remove commented-out code
- [ ] Keep comments up-to-date
- [ ] Use TODO/FIXME with tickets
- [ ] API documentation (JSDoc, etc.)
- [ ] Complex algorithms explained

```typescript
// Bad - explains what (obvious from code)
// Increment counter by 1
counter++;

// Good - explains why
// Skip the first element as it's a header row
const dataRows = rows.slice(1);

// Good - documents complex logic
/**
 * Calculates tax using progressive tax brackets.
 * Uses 2025 tax table: 10% up to $10k, 20% from $10k-$50k, etc.
 */
function calculateTax(income: number): number {
  // Implementation...
}
```

### Formatting
- [ ] Consistent indentation (2 or 4 spaces)
- [ ] Vertical spacing for readability
- [ ] Horizontal alignment
- [ ] Line length < 100-120 characters
- [ ] Use linter/formatter (Prettier, ESLint)
- [ ] Consistent brace style
- [ ] Group related code together

---

## DRY (Don't Repeat Yourself)

### Code Duplication
- [ ] Extract repeated code to functions
- [ ] Use inheritance/composition
- [ ] Create utility functions
- [ ] Use loops instead of repetition
- [ ] Configuration over code
- [ ] Templates for similar structures

**Rule of Three**: If code appears 3 times, extract it.

```typescript
// Bad - repetition
function getAdminUsers() {
  return db.query('SELECT * FROM users WHERE role = "admin"');
}

function getGuestUsers() {
  return db.query('SELECT * FROM users WHERE role = "guest"');
}

// Good - extracted
function getUsersByRole(role: string) {
  return db.query('SELECT * FROM users WHERE role = ?', [role]);
}
```

---

## Error Handling

### Exception Strategy
- [ ] Use exceptions for exceptional cases
- [ ] Don't use exceptions for control flow
- [ ] Catch specific exceptions
- [ ] Provide context in error messages
- [ ] Clean up resources (finally, defer, RAII)
- [ ] Don't ignore caught exceptions
- [ ] Return error objects vs throwing (when appropriate)
- [ ] Define error hierarchies
- [ ] Log errors with context

```typescript
// Bad
try {
  // code
} catch (e) {
  // Empty catch - error is silently ignored
}

// Good
try {
  await processPayment(amount);
} catch (error) {
  if (error instanceof InsufficientFundsError) {
    logger.warn('Payment failed: insufficient funds', {
      userId: user.id,
      amount,
      balance: user.balance
    });
    return { success: false, reason: 'insufficient_funds' };
  }
  throw error; // Re-throw unexpected errors
}
```

### Input Validation
- [ ] Validate all inputs
- [ ] Fail fast
- [ ] Clear error messages
- [ ] Validate at boundaries
- [ ] Use type systems
- [ ] Sanitize user input
- [ ] Check preconditions

---

## Code Organization

### Module Structure
- [ ] Logical grouping
- [ ] Single purpose per module
- [ ] Clear dependencies
- [ ] Avoid circular dependencies
- [ ] Public API clearly defined
- [ ] Hide implementation details
- [ ] Use barrel exports (index files)

### Project Structure
- [ ] Feature-based organization (vs layer-based)
- [ ] Consistent naming conventions
- [ ] Clear folder hierarchy
- [ ] Co-locate related files
- [ ] Configuration in environment variables

**Feature-Based Structure** (Preferred for large apps):
```
src/
├── features/
│   ├── auth/
│   │   ├── AuthService.ts
│   │   ├── AuthController.ts
│   │   ├── AuthRepository.ts
│   │   └── index.ts
│   └── users/
│       ├── UserService.ts
│       ├── UserController.ts
│       └── index.ts
└── shared/
    ├── utils/
    └── types/
```

---

## Testing

### Test Coverage
- [ ] Unit tests for business logic
- [ ] Integration tests for workflows
- [ ] E2E tests for critical paths
- [ ] Test edge cases
- [ ] Test error handling
- [ ] Aim for 70-80% coverage minimum
- [ ] 100% coverage of critical paths

### Test Quality
- [ ] Tests are readable
- [ ] Tests are independent
- [ ] Tests are fast
- [ ] One assertion per test (when practical)
- [ ] AAA pattern (Arrange-Act-Assert)
- [ ] Descriptive test names
- [ ] No test interdependencies
- [ ] Mock external dependencies

```typescript
// Good test structure
describe('UserService', () => {
  describe('register', () => {
    it('should create user with hashed password', async () => {
      // Arrange
      const userData = { email: 'test@example.com', password: 'pass123' };
      const mockRepo = { save: jest.fn() };
      const service = new UserService(mockRepo);

      // Act
      await service.register(userData);

      // Assert
      expect(mockRepo.save).toHaveBeenCalledWith(
        expect.objectContaining({
          email: 'test@example.com',
          password: expect.not.stringContaining('pass123') // Hashed
        })
      );
    });

    it('should throw error for duplicate email', async () => {
      // ...
    });
  });
});
```

---

## Performance Considerations

### Code Efficiency
- [ ] Profile before optimizing
- [ ] Optimize hot paths only
- [ ] Use appropriate data structures
- [ ] Avoid premature optimization
- [ ] Cache expensive computations
- [ ] Lazy loading when possible
- [ ] Avoid memory leaks

### Scalability
- [ ] Stateless when possible
- [ ] Horizontal scaling support
- [ ] Database query optimization
- [ ] Async for I/O operations
- [ ] Connection pooling
- [ ] Rate limiting

---

## Security Practices

### Input Handling
- [ ] Validate all inputs
- [ ] Sanitize user data
- [ ] Use parameterized queries (no SQL injection)
- [ ] Escape output
- [ ] CSRF protection
- [ ] XSS prevention

### Authentication & Authorization
- [ ] Hash passwords (bcrypt, argon2)
- [ ] Never log sensitive data
- [ ] Use HTTPS
- [ ] Secure session management
- [ ] Implement proper authorization
- [ ] Principle of least privilege

### Dependencies
- [ ] Keep dependencies updated
- [ ] Audit for vulnerabilities
- [ ] Minimize dependencies
- [ ] Use lock files
- [ ] Review third-party code

---

## Documentation

### Code Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] README for each module/package
- [ ] Setup instructions
- [ ] Usage examples
- [ ] Architecture decisions recorded (ADRs)

### Types & Interfaces
- [ ] Use type systems (TypeScript, types, etc.)
- [ ] Document complex types
- [ ] Avoid `any` type
- [ ] Define clear interfaces
- [ ] Use enums for fixed values

---

## Code Review Checklist

### Before Submitting
- [ ] Code works as expected
- [ ] Tests pass
- [ ] Linter passes
- [ ] No console.logs or debugger statements
- [ ] No commented-out code
- [ ] Dependencies updated in package.json
- [ ] README updated if needed
- [ ] Breaking changes documented

### Reviewing Code
- [ ] Does it solve the problem?
- [ ] Is it readable?
- [ ] Are there tests?
- [ ] Are there security issues?
- [ ] Is error handling proper?
- [ ] Are names descriptive?
- [ ] Is it consistent with codebase?
- [ ] Could it be simpler?

---

## Language-Specific Best Practices

### TypeScript
- [ ] Enable strict mode
- [ ] Avoid `any` type
- [ ] Use type inference
- [ ] Define interfaces for objects
- [ ] Use enums for constants
- [ ] Leverage union types
- [ ] Use readonly where applicable

### JavaScript
- [ ] Use const/let, not var
- [ ] Prefer arrow functions
- [ ] Use template literals
- [ ] Destructuring for objects/arrays
- [ ] Spread operator
- [ ] Optional chaining (?.)
- [ ] Nullish coalescing (??)
- [ ] Async/await over callbacks

### Python
- [ ] Follow PEP 8
- [ ] Use type hints
- [ ] Docstrings for functions/classes
- [ ] List comprehensions when appropriate
- [ ] Context managers (with statement)
- [ ] Use f-strings for formatting
- [ ] Virtual environments

### Go
- [ ] gofmt for formatting
- [ ] Error handling (don't ignore errors)
- [ ] Defer for cleanup
- [ ] Use interfaces
- [ ] Avoid global state
- [ ] Use goroutines carefully
- [ ] Handle panics

---

## Refactoring Indicators

### When to Refactor
- [ ] Code is duplicated
- [ ] Functions are too long (>20 lines)
- [ ] Classes are too large (>300 lines)
- [ ] Too many parameters (>3)
- [ ] Deep nesting (>3 levels)
- [ ] Complex conditionals
- [ ] Long switch statements
- [ ] Feature envy (accessing other class's data)
- [ ] Primitive obsession
- [ ] Magic numbers

### Refactoring Techniques
- [ ] Extract method
- [ ] Extract class
- [ ] Rename for clarity
- [ ] Move method
- [ ] Replace magic numbers with constants
- [ ] Simplify conditionals
- [ ] Decompose complex expressions

---

## Tools

### Static Analysis
- [ ] ESLint (JavaScript/TypeScript)
- [ ] SonarQube
- [ ] Pylint (Python)
- [ ] golangci-lint (Go)
- [ ] RuboCop (Ruby)

### Formatters
- [ ] Prettier (JavaScript/TypeScript)
- [ ] Black (Python)
- [ ] gofmt (Go)
- [ ] rustfmt (Rust)

### Code Quality Metrics
- [ ] Cyclomatic complexity < 10
- [ ] Code coverage > 70%
- [ ] Code duplication < 5%
- [ ] Maintainability index > 65
- [ ] Technical debt ratio < 5%

---

## Quick Quality Checklist

Before committing code, verify:

1. [ ] **It works** - Tests pass, manual testing done
2. [ ] **It's readable** - Clear names, proper formatting
3. [ ] **It's tested** - Unit tests for logic
4. [ ] **It's simple** - Simplest solution that works
5. [ ] **It's safe** - Input validated, errors handled
6. [ ] **It's documented** - Complex logic explained
7. [ ] **It's consistent** - Follows project conventions
8. [ ] **It's necessary** - No over-engineering

---

**Remember**:
> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand." - Martin Fowler

**Last Updated**: 2025-01-15
**Version**: 1.0.0
