# Code Review Checklist

Use this comprehensive checklist when reviewing code to ensure thorough and consistent reviews.

---

## Pre-Review Setup

- [ ] **Read PR Description**: Understand intent and scope
- [ ] **Check CI Status**: All automated checks passing (tests, linting, type checking)
- [ ] **Review Size**: PR is manageable (< 400 lines preferred, flag if > 800)
- [ ] **Linked Issues**: PR references relevant tickets/issues
- [ ] **No Merge Conflicts**: Branch is up to date with target branch

---

## High-Level Review (Architecture & Design)

### Overall Approach

- [ ] **Problem-Solution Alignment**: Changes solve the stated problem
- [ ] **Scope Appropriate**: No unrelated changes included
- [ ] **Architecture Consistency**: Follows existing patterns and conventions
- [ ] **Design Patterns**: Appropriate patterns used (not over-engineered)
- [ ] **Separation of Concerns**: Each module/function has single responsibility

### Code Organization

- [ ] **File Structure**: New files in appropriate directories
- [ ] **Module Boundaries**: Clear separation between modules
- [ ] **Coupling**: Low coupling between modules
- [ ] **Cohesion**: High cohesion within modules

---

## Code Quality

### Readability

- [ ] **Clear Intent**: Code purpose is obvious from reading
- [ ] **Naming Conventions**: Variables, functions, classes have descriptive names
- [ ] **Consistent Style**: Follows team style guide
- [ ] **Comments**: Complex logic explained (not what, but why)
- [ ] **Magic Numbers**: Constants extracted and named
- [ ] **Code Formatting**: Properly formatted (via Prettier/Black)

### Maintainability

- [ ] **DRY Principle**: No unnecessary code duplication
- [ ] **Function Size**: Functions < 50 lines, focused on single task
- [ ] **Cyclomatic Complexity**: Functions have complexity < 10
- [ ] **Nesting Depth**: No deeply nested code (< 4 levels)
- [ ] **Dead Code**: No commented-out code or unused variables
- [ ] **TODO Comments**: Tracked in issue tracker, not just in code

---

## Functionality

### Correctness

- [ ] **Logic Errors**: No obvious bugs or logic errors
- [ ] **Edge Cases**: Boundary conditions handled
  - [ ] Null/undefined/None handled
  - [ ] Empty arrays/strings handled
  - [ ] Zero values handled
  - [ ] Negative numbers (if applicable)
  - [ ] Maximum/minimum values
- [ ] **Data Types**: Correct data types used
- [ ] **Off-by-One Errors**: Array indices and loops correct

### Error Handling

- [ ] **Try-Catch Blocks**: Errors caught where appropriate
- [ ] **Specific Exceptions**: Catching specific errors, not generic catch-all
- [ ] **Error Messages**: Clear, actionable error messages
- [ ] **Error Logging**: Errors logged with appropriate context
- [ ] **Error Propagation**: Errors bubble up or handled at right level
- [ ] **Graceful Degradation**: System handles failures gracefully
- [ ] **User Feedback**: Users see helpful error messages (not stack traces)

### Input Validation

- [ ] **Required Fields**: Required inputs validated
- [ ] **Data Types**: Input types validated
- [ ] **Ranges**: Min/max values enforced
- [ ] **Format Validation**: Email, phone, URL formats validated
- [ ] **Sanitization**: User input sanitized (XSS prevention)
- [ ] **SQL Injection Prevention**: Parameterized queries used

---

## Testing

### Test Coverage

- [ ] **Tests Exist**: New code has tests
- [ ] **Coverage Metrics**: Code coverage meets targets (80%+)
- [ ] **Happy Path**: Main functionality tested
- [ ] **Error Paths**: Error scenarios tested
- [ ] **Edge Cases**: Boundary conditions tested
- [ ] **Regression Tests**: Previous bugs have tests

### Test Quality

- [ ] **Test Names**: Clearly describe what's being tested
- [ ] **AAA Pattern**: Arrange-Act-Assert structure
- [ ] **Test Isolation**: Tests don't depend on each other
- [ ] **No Flaky Tests**: Tests pass consistently
- [ ] **Realistic Data**: Test data resembles production data
- [ ] **Mocking Strategy**: Appropriate use of mocks vs real dependencies

### Test Types

- [ ] **Unit Tests**: Business logic tested in isolation
- [ ] **Integration Tests**: Component interactions tested
- [ ] **E2E Tests**: Critical user flows tested (if applicable)
- [ ] **Performance Tests**: Performance benchmarks (if applicable)

---

## Performance

### Efficiency

- [ ] **Algorithm Complexity**: Efficient algorithms used
  - [ ] No O(n²) where O(n) is possible
  - [ ] No unnecessary nested loops
- [ ] **Database Queries**: Optimized queries
  - [ ] No N+1 query problems
  - [ ] Eager loading where needed
  - [ ] Appropriate indexes exist
- [ ] **Caching**: Used where appropriate
- [ ] **Lazy Loading**: Heavy operations deferred when possible

### Resource Management

- [ ] **Memory Leaks**: No obvious memory leaks
  - [ ] Event listeners cleaned up
  - [ ] Subscriptions unsubscribed
  - [ ] Timers/intervals cleared
- [ ] **File Handles**: Files closed after use
- [ ] **Database Connections**: Connections properly managed (pooling)
- [ ] **Large Collections**: Large arrays/lists handled efficiently

---

## Security

### Authentication & Authorization

- [ ] **Auth Required**: Protected endpoints require authentication
- [ ] **Permission Checks**: User permissions verified before actions
- [ ] **JWT Validation**: Tokens validated and not expired
- [ ] **Session Security**: Sessions managed securely
- [ ] **Password Requirements**: Password complexity enforced

### Data Protection

- [ ] **Sensitive Data**: No secrets in code (API keys, passwords)
- [ ] **Environment Variables**: Secrets in environment, not hardcoded
- [ ] **Encryption**: Sensitive data encrypted (passwords, PII)
- [ ] **HTTPS Only**: Production uses HTTPS
- [ ] **Secure Headers**: Security headers set (CSP, X-Frame-Options)

### Common Vulnerabilities

- [ ] **SQL Injection**: Parameterized queries used
- [ ] **XSS**: User input sanitized, output encoded
- [ ] **CSRF**: CSRF tokens for state-changing operations
- [ ] **Insecure Dependencies**: No known vulnerabilities (`npm audit`)
- [ ] **Rate Limiting**: Public endpoints rate-limited
- [ ] **File Upload Security**: File type/size restrictions

---

## API Design (if applicable)

### REST Principles

- [ ] **Resource Naming**: Plural nouns, kebab-case
- [ ] **HTTP Methods**: Correct methods (GET, POST, PUT, DELETE)
- [ ] **Status Codes**: Appropriate status codes (200, 201, 400, 404, 500)
- [ ] **Idempotency**: PUT/DELETE are idempotent
- [ ] **Pagination**: Large lists paginated
- [ ] **Versioning**: API version strategy followed

### Request/Response

- [ ] **Request Validation**: Request body validated
- [ ] **Response Format**: Consistent response structure
- [ ] **Error Format**: Standardized error responses
- [ ] **Field Naming**: Consistent naming (camelCase or snake_case)
- [ ] **Timestamps**: ISO 8601 format

---

## Database (if applicable)

### Schema Design

- [ ] **Migrations**: Database changes have migrations
- [ ] **Rollback Migrations**: Rollback scripts provided
- [ ] **Indexes**: Appropriate indexes created
- [ ] **Foreign Keys**: Relationships properly defined
- [ ] **Constraints**: Unique, not-null constraints defined
- [ ] **Normalization**: Appropriate normalization level

### Queries

- [ ] **Parameterized Queries**: No SQL injection risk
- [ ] **Query Optimization**: Queries are efficient
- [ ] **Transaction Management**: ACID properties maintained
- [ ] **Connection Pooling**: Database connections pooled

---

## Frontend (if applicable)

### React/Component Best Practices

- [ ] **Component Size**: Components < 300 lines
- [ ] **Props Validation**: PropTypes or TypeScript interfaces
- [ ] **Key Props**: Proper keys in lists (not index)
- [ ] **State Management**: State lifted appropriately
- [ ] **Side Effects**: useEffect dependencies correct
- [ ] **Memoization**: Expensive calculations memoized

### Accessibility

- [ ] **Keyboard Navigation**: All interactive elements keyboard accessible
- [ ] **ARIA Labels**: Screen reader support
- [ ] **Color Contrast**: WCAG AA compliance (4.5:1 ratio)
- [ ] **Focus Indicators**: Visible focus states
- [ ] **Semantic HTML**: Using proper HTML elements

### Performance

- [ ] **Bundle Size**: No unnecessary dependencies
- [ ] **Code Splitting**: Large components lazy-loaded
- [ ] **Image Optimization**: Images compressed and sized appropriately
- [ ] **Render Optimization**: No unnecessary re-renders

---

## Documentation

### Code Documentation

- [ ] **Inline Comments**: Complex logic explained
- [ ] **JSDoc/Docstrings**: Public APIs documented
- [ ] **Type Annotations**: TypeScript/Python type hints used
- [ ] **Examples**: Usage examples provided (if library/utility)

### Project Documentation

- [ ] **README Updated**: If functionality changed
- [ ] **API Docs Updated**: If API changed
- [ ] **CHANGELOG Updated**: Breaking changes documented
- [ ] **Migration Guide**: If breaking changes
- [ ] **Architecture Diagrams**: Updated (if relevant)

---

## Language-Specific Checks

### JavaScript/TypeScript

- [ ] **Async/Await**: Promises handled with async/await
- [ ] **Error Handling**: Async errors caught
- [ ] **Type Safety**: No `any` types (TypeScript)
- [ ] **Null Safety**: Optional chaining (`?.`) used
- [ ] **Const vs Let**: Immutable values use `const`
- [ ] **Arrow Functions**: Used appropriately
- [ ] **Template Literals**: Used instead of string concatenation
- [ ] **Destructuring**: Used for readability
- [ ] **Modern Syntax**: ES6+ features used appropriately

### Python

- [ ] **PEP 8**: Follows Python style guide
- [ ] **Type Hints**: Function annotations provided
- [ ] **F-Strings**: Modern string formatting
- [ ] **List Comprehensions**: Used appropriately (not overused)
- [ ] **Context Managers**: `with` for file/connection handling
- [ ] **Exception Handling**: Specific exceptions, no bare `except:`
- [ ] **Generator Expressions**: Used for memory efficiency
- [ ] **Dataclasses**: Used for data structures (Python 3.7+)

---

## Dependencies

### Dependency Management

- [ ] **Necessary Dependencies**: New dependencies justified
- [ ] **Version Pinning**: Dependencies pinned to specific versions
- [ ] **Lock Files Updated**: package-lock.json / Pipfile.lock updated
- [ ] **No Vulnerabilities**: `npm audit` / `pip-audit` clean
- [ ] **License Compatibility**: Dependency licenses compatible
- [ ] **Bundle Size Impact**: Large dependencies justified

---

## CI/CD & Deployment

### Continuous Integration

- [ ] **All Checks Pass**: Linting, tests, type checking
- [ ] **Build Succeeds**: Application builds successfully
- [ ] **No Warnings**: Build generates no warnings

### Deployment Considerations

- [ ] **Feature Flags**: New features behind flags (if applicable)
- [ ] **Database Migrations**: Safe for zero-downtime deployment
- [ ] **Backward Compatibility**: No breaking changes to API contracts
- [ ] **Rollback Plan**: Can revert if issues arise
- [ ] **Environment Variables**: New env vars documented

---

## Breaking Changes

### Impact Assessment

- [ ] **No Breaking Changes** (or marked as breaking change)
- [ ] **Migration Path**: Clear upgrade path provided
- [ ] **Deprecation Warnings**: Old APIs deprecated, not removed immediately
- [ ] **Version Bump**: Semantic versioning followed (major version bump)
- [ ] **Stakeholder Notification**: Affected teams notified

---

## Follow-Up Work

### Technical Debt

- [ ] **TODO Items**: Tracked in issue tracker
- [ ] **Known Limitations**: Documented
- [ ] **Refactoring Needed**: Follow-up issues created
- [ ] **Performance Optimizations**: Future work identified

---

## Final Checks

### Before Approving

- [ ] **All Blocking Issues Addressed**: Critical problems resolved
- [ ] **Questions Answered**: Author responded to clarifications
- [ ] **Tests Pass**: All automated checks green
- [ ] **Documentation Complete**: Necessary docs updated
- [ ] **Security Reviewed**: No security vulnerabilities
- [ ] **Performance Acceptable**: No significant regressions

### Approval Decision

- ✅ **Approve**: Ready to merge, no blocking issues
- 💬 **Comment**: Feedback provided, no action required
- 🔄 **Request Changes**: Blocking issues must be addressed

---

## Common Issues to Watch For

### Frequent Problems

- ❌ Missing null/undefined checks
- ❌ No error handling in async operations
- ❌ N+1 database queries
- ❌ Hardcoded secrets or API keys
- ❌ Missing input validation
- ❌ Commented-out code
- ❌ console.log / print statements
- ❌ TODO comments without issue references
- ❌ Magic numbers (unnamed constants)
- ❌ Deep nesting (> 4 levels)
- ❌ Large functions (> 50 lines)
- ❌ Missing tests for new code

---

## Review Etiquette

### For Reviewers

- [ ] Use conventional comments (praise, issue, suggestion, question)
- [ ] Be specific and actionable
- [ ] Explain the "why" behind suggestions
- [ ] Acknowledge good work (use "praise" labels)
- [ ] Assume positive intent
- [ ] Provide timely feedback (< 24 hours)

### For Authors

- [ ] Respond to all comments
- [ ] Ask for clarification if needed
- [ ] Accept feedback gracefully
- [ ] Make changes promptly
- [ ] Thank reviewers for their time

---

**Checklist Version**: 1.0.0
**Skill**: code-review-playbook v1.0.0
**Last Updated**: 2025-10-31
