# Pull Request Review Checklist

## Code Quality
- [ ] Code follows project style guidelines
- [ ] No unnecessary code duplication
- [ ] Functions/methods have single responsibility
- [ ] Variable and function names are descriptive
- [ ] No hardcoded values (use constants/config)

## Testing
- [ ] Unit tests added for new functionality
- [ ] Existing tests updated for changes
- [ ] All tests pass locally
- [ ] Edge cases covered
- [ ] Integration tests if applicable

## Security
- [ ] No sensitive data exposed (passwords, keys, tokens)
- [ ] Input validation implemented
- [ ] SQL/command injection prevented
- [ ] Authentication/authorization checks in place
- [ ] Dependencies checked for vulnerabilities

## Documentation
- [ ] Code comments for complex logic
- [ ] README updated if needed
- [ ] API documentation updated
- [ ] CHANGELOG entry added

## Performance
- [ ] No unnecessary database queries
- [ ] Large data sets handled efficiently
- [ ] Caching considered where appropriate
- [ ] No memory leaks introduced

## Breaking Changes
- [ ] Breaking changes documented
- [ ] Migration guide provided
- [ ] Version bump appropriate (major for breaking)
- [ ] Deprecation warnings added

## CI/CD
- [ ] All CI checks passing
- [ ] Build succeeds
- [ ] Linting passes
- [ ] Coverage threshold met

## General
- [ ] PR title follows convention
- [ ] PR description complete
- [ ] Related issues linked
- [ ] Assignees and labels set
- [ ] Ready for review (not draft)
