# Comprehensive Code Review Checklist

Use this checklist as a guide for thorough code reviews. Adapt to your language, framework, and project requirements.

## Pre-Review Setup

- [ ] Pull latest changes from main/master branch
- [ ] Review PR/MR description and linked issues
- [ ] Build project locally without errors
- [ ] Run test suite - all tests pass
- [ ] Check CI/CD pipeline status

---

## 1. Security Review

### Authentication & Authorization
- [ ] Authentication checks present on all protected endpoints
- [ ] Authorization verified for resource access
- [ ] No hardcoded credentials or API keys
- [ ] Session management is secure
- [ ] Password policies enforced (if applicable)
- [ ] Multi-factor authentication considered for sensitive operations

### Input Validation
- [ ] All user inputs validated on server-side
- [ ] Input sanitization prevents SQL injection
- [ ] Protection against XSS attacks
- [ ] File upload validation (type, size, content)
- [ ] Command injection prevented
- [ ] Path traversal vulnerabilities addressed

### Data Protection
- [ ] Sensitive data encrypted in transit (HTTPS/TLS)
- [ ] Sensitive data encrypted at rest
- [ ] No sensitive data in logs
- [ ] No sensitive data in error messages
- [ ] Proper use of cryptographic libraries
- [ ] Secrets stored in secure vault/environment variables

### Dependencies & Libraries
- [ ] No known vulnerabilities in dependencies
- [ ] Dependencies are up-to-date
- [ ] Minimal dependency footprint
- [ ] Licenses compatible with project
- [ ] No deprecated libraries in use

### Common Vulnerabilities
- [ ] CSRF protection implemented
- [ ] CORS configured properly
- [ ] No unsafe deserialization
- [ ] No server-side request forgery (SSRF)
- [ ] XML external entity (XXE) protection
- [ ] Clickjacking protection (X-Frame-Options)

---

## 2. Code Quality

### Design & Architecture
- [ ] Code follows SOLID principles
- [ ] Appropriate design patterns used
- [ ] No circular dependencies
- [ ] Proper separation of concerns
- [ ] Clear module boundaries
- [ ] Dependency injection where appropriate
- [ ] No god objects or god classes

### Code Structure
- [ ] Functions have single responsibility
- [ ] Classes are cohesive
- [ ] Proper abstraction levels
- [ ] No code duplication (DRY principle)
- [ ] No dead code or commented-out code
- [ ] No magic numbers or strings

### Complexity
- [ ] Cyclomatic complexity < 10 per function
- [ ] Nesting depth < 4 levels
- [ ] Function length < 50 lines (guideline)
- [ ] Class size < 300 lines (guideline)
- [ ] Parameter count < 5 per function

### Naming
- [ ] Variables have descriptive names
- [ ] Functions named after their action
- [ ] Classes named after their responsibility
- [ ] Consistent naming conventions
- [ ] Boolean names start with is/has/should/can
- [ ] No abbreviations unless standard

### Error Handling
- [ ] Exceptions caught at appropriate level
- [ ] No bare except/catch blocks
- [ ] Meaningful error messages
- [ ] Proper exception types used
- [ ] Resources cleaned up (finally/defer/using)
- [ ] No swallowed exceptions
- [ ] Error conditions logged appropriately

### Type Safety (where applicable)
- [ ] Proper type annotations/hints
- [ ] No any/dynamic types without justification
- [ ] Type checking passes
- [ ] Null/None handled explicitly
- [ ] Optional types used appropriately

---

## 3. Performance

### Algorithm Efficiency
- [ ] No unnecessary O(n²) or worse algorithms
- [ ] Appropriate data structures chosen
- [ ] No redundant computations
- [ ] Efficient sorting/searching algorithms
- [ ] Caching implemented where beneficial

### Memory Management
- [ ] No memory leaks
- [ ] Large objects properly disposed
- [ ] Streams closed properly
- [ ] No excessive memory allocation
- [ ] Appropriate use of object pooling

### Database Operations
- [ ] No N+1 query problems
- [ ] Queries are indexed
- [ ] No SELECT * (select only needed columns)
- [ ] Batch operations used where appropriate
- [ ] Transactions used properly
- [ ] Connection pooling configured
- [ ] Pagination implemented for large datasets

### Network & I/O
- [ ] Async operations where appropriate
- [ ] Timeouts configured
- [ ] Retry logic with backoff
- [ ] Connection pooling used
- [ ] No blocking operations in hot paths
- [ ] Appropriate use of streaming

### Caching
- [ ] Cache invalidation strategy defined
- [ ] Cache keys are unique and stable
- [ ] Appropriate cache TTL
- [ ] Cache size limits set
- [ ] Cache warming strategy (if needed)

---

## 4. Testing

### Test Coverage
- [ ] Line coverage > 80%
- [ ] Branch coverage > 75%
- [ ] All new code has tests
- [ ] Critical paths have 100% coverage
- [ ] Edge cases tested

### Test Quality
- [ ] Tests have descriptive names
- [ ] Tests are independent
- [ ] Tests are repeatable
- [ ] No test interdependencies
- [ ] Tests use AAA pattern (Arrange-Act-Assert)
- [ ] Proper use of mocks and stubs
- [ ] No sleeps or arbitrary waits

### Test Types
- [ ] Unit tests for business logic
- [ ] Integration tests for component interaction
- [ ] End-to-end tests for critical flows
- [ ] Performance tests (if applicable)
- [ ] Security tests (if applicable)
- [ ] Regression tests for bug fixes

### Test Scenarios
- [ ] Happy path tested
- [ ] Error conditions tested
- [ ] Edge cases tested
- [ ] Boundary values tested
- [ ] Null/empty input tested
- [ ] Concurrent access tested (if applicable)

---

## 5. Documentation

### Code Documentation
- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] Function/method parameters documented
- [ ] Return values documented
- [ ] Exceptions documented
- [ ] Examples provided for complex APIs

### Comments
- [ ] Comments explain WHY, not WHAT
- [ ] No outdated comments
- [ ] No commented-out code
- [ ] TODOs have associated tickets
- [ ] FIXMEs addressed or ticketed

### External Documentation
- [ ] README updated (if applicable)
- [ ] API documentation updated
- [ ] Configuration changes documented
- [ ] Migration guide provided (if breaking changes)
- [ ] Changelog updated
- [ ] Architecture diagrams updated (if applicable)

---

## 6. Best Practices

### Version Control
- [ ] Commit messages are descriptive
- [ ] Logical, atomic commits
- [ ] No merge commits in PR (rebase preferred)
- [ ] No binary files committed (unless necessary)
- [ ] .gitignore properly configured
- [ ] No sensitive data in commit history

### Configuration
- [ ] Configuration externalized (not hardcoded)
- [ ] Environment-specific configs separated
- [ ] Sensible defaults provided
- [ ] Configuration validated at startup
- [ ] Feature flags used for gradual rollout (if applicable)

### Logging
- [ ] Appropriate log levels used
- [ ] No sensitive data in logs
- [ ] Structured logging format
- [ ] Request IDs for tracing
- [ ] Error stack traces logged
- [ ] Performance metrics logged (if applicable)

### Backwards Compatibility
- [ ] Breaking changes documented
- [ ] Deprecation warnings added
- [ ] Migration path provided
- [ ] API versioning considered
- [ ] Database migrations reversible

---

## 7. Language-Specific Checks

### Python
- [ ] PEP 8 style guide followed
- [ ] Type hints used (Python 3.5+)
- [ ] Context managers for resources (with)
- [ ] No mutable default arguments
- [ ] List/dict comprehensions not overly complex
- [ ] Generators used for large datasets
- [ ] Virtual environment requirements.txt updated

### JavaScript/TypeScript
- [ ] ESLint rules followed
- [ ] Async/await used (not callback hell)
- [ ] Event listeners properly cleaned up
- [ ] No memory leaks in closures
- [ ] Proper TypeScript types (no any abuse)
- [ ] package.json dependencies updated
- [ ] .npmrc configured properly

### Java
- [ ] Checkstyle/PMD rules followed
- [ ] Proper exception handling
- [ ] Try-with-resources used
- [ ] Immutability preferred
- [ ] Thread safety considered
- [ ] Proper use of streams
- [ ] pom.xml/build.gradle updated

### Go
- [ ] gofmt/goimports run
- [ ] Errors not ignored
- [ ] Defer used for cleanup
- [ ] Goroutine leaks prevented
- [ ] Race conditions checked (go test -race)
- [ ] Context used for cancellation
- [ ] go.mod dependencies updated

---

## 8. Deployment & Operations

### Monitoring
- [ ] Metrics exposed
- [ ] Health check endpoint added
- [ ] Alerts configured (if applicable)
- [ ] Dashboards updated (if applicable)

### Deployment
- [ ] Database migrations included
- [ ] Rollback plan documented
- [ ] Feature flags for risky changes
- [ ] Zero-downtime deployment strategy
- [ ] Infrastructure as code updated

### Scalability
- [ ] Horizontal scaling considered
- [ ] No hardcoded instance-specific values
- [ ] Stateless design (where appropriate)
- [ ] Resource limits configured

---

## Post-Review

- [ ] All review comments addressed
- [ ] Follow-up tickets created for deferred items
- [ ] Approval given or changes requested
- [ ] Knowledge shared with team (if applicable)

---

## Severity Guidelines

Use these severity levels for issues found:

- **🔴 Critical**: Security vulnerabilities, data corruption, complete feature breakage
- **🟠 High**: Performance issues, major bugs, significant code quality problems
- **🟡 Medium**: Minor bugs, code quality improvements, refactoring opportunities
- **🟢 Low**: Style issues, typos, minor optimizations
- **💡 Suggestion**: Nice-to-have improvements, alternative approaches

---

## Review Efficiency Tips

1. **Use automated tools first** - Let linters, formatters, and scanners catch mechanical issues
2. **Focus on high-value areas** - Security, business logic, public APIs
3. **Don't bikeshed** - Don't argue over trivial style preferences
4. **Be timely** - Review within 24 hours when possible
5. **Be thorough but pragmatic** - Balance perfect vs. good enough
6. **Provide context** - Explain WHY changes are needed
7. **Offer solutions** - Don't just point out problems
8. **Recognize good work** - Comment on well-written code too

---

*Customize this checklist for your team's specific needs, coding standards, and tech stack.*
