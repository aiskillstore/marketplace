---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: code-review
---

# Code Review Checklist

Comprehensive checklist for conducting thorough code reviews across different aspects of code quality.

## Security Checklist

### Authentication & Authorization

- [ ] Proper authentication implemented
- [ ] Authorization checks on all protected routes
- [ ] Role-based access control (RBAC) implemented correctly
- [ ] Session management secure
- [ ] Token expiration handled
- [ ] Password hashing used (bcrypt, argon2, etc.)
- [ ] No hardcoded credentials

### Input Validation

- [ ] All user inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection implemented
- [ ] File upload validation (type, size, content)
- [ ] Path traversal prevention
- [ ] Input sanitization applied

### Data Protection

- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit (HTTPS)
- [ ] No secrets in code or config files
- [ ] Environment variables used for secrets
- [ ] API keys properly secured
- [ ] Database credentials secure
- [ ] Logs don't contain sensitive information

### Security Headers

- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] CORS properly configured
- [ ] Content Security Policy set
- [ ] X-Frame-Options set
- [ ] X-Content-Type-Options set

## Code Quality Checklist

### Readability

- [ ] Code is clear and self-documenting
- [ ] Variable names are descriptive
- [ ] Function names describe what they do
- [ ] Comments explain why, not what
- [ ] Code follows project style guide
- [ ] Consistent formatting

### Structure

- [ ] Functions do one thing
- [ ] Functions are appropriately sized (< 50 lines ideal)
- [ ] No code duplication (DRY principle)
- [ ] Proper separation of concerns
- [ ] Logical code organization
- [ ] Appropriate use of design patterns

### Error Handling

- [ ] Errors handled appropriately
- [ ] Error messages are helpful
- [ ] No silent failures
- [ ] Proper exception types used
- [ ] Error logging implemented
- [ ] Graceful degradation

## Performance Checklist

### Algorithm Efficiency

- [ ] Appropriate data structures used
- [ ] Algorithms are efficient (O(n) vs O(n²))
- [ ] No unnecessary loops
- [ ] Early returns used when possible
- [ ] Lazy loading implemented where appropriate

### Database

- [ ] Queries are optimized
- [ ] Appropriate indexes exist
- [ ] No N+1 query problems
- [ ] Connection pooling used
- [ ] Query result caching implemented
- [ ] Batch operations used when possible

### Resource Management

- [ ] Memory leaks prevented
- [ ] Resources properly closed/released
- [ ] Connection pooling implemented
- [ ] File handles closed
- [ ] Event listeners cleaned up
- [ ] Timers/intervals cleared

## Testing Checklist

### Test Coverage

- [ ] Unit tests for new code
- [ ] Integration tests for critical paths
- [ ] Edge cases tested
- [ ] Error cases tested
- [ ] Test coverage meets threshold

### Test Quality

- [ ] Tests are independent
- [ ] Tests are deterministic
- [ ] Tests have clear names
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Mocks used appropriately
- [ ] Test data factories used

## Documentation Checklist

### Code Documentation

- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] Function parameters documented
- [ ] Return values documented
- [ ] Examples provided for complex functions

### Project Documentation

- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Architecture docs updated
- [ ] Changelog updated
- [ ] Migration guides if breaking changes

## Best Practices Checklist

### Language-Specific

- [ ] Follows language best practices
- [ ] Uses modern language features appropriately
- [ ] Avoids deprecated patterns
- [ ] Type safety (TypeScript, etc.)

### Framework-Specific

- [ ] Follows framework conventions
- [ ] Uses framework features correctly
- [ ] No anti-patterns
- [ ] Performance best practices followed

### General

- [ ] No magic numbers (use constants)
- [ ] No hardcoded values
- [ ] Configuration externalized
- [ ] Logging implemented appropriately
- [ ] Monitoring/metrics added
