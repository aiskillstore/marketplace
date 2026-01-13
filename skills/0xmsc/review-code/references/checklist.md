# Code Review Checklist

A comprehensive checklist for senior engineer-level code reviews. Use this as a reference during the workflow.

## General
- [ ] **Purpose**: Does the change clearly address a requirement or fix a bug?
- [ ] **Scope**: Is the change focused? Avoids scope creep?
- [ ] **Testing**: Are there appropriate tests (unit, integration, e2e)?
- [ ] **Documentation**: Updated README, comments, API docs?

## Code Quality
- [ ] **Naming**: Variables, functions, classes are clear and consistent?
- [ ] **Readability**: Code is self-documenting? Complex logic explained?
- [ ] **Simplicity**: No over-engineering? Simplest solution that works?
- [ ] **Duplication**: No repeated code? Extract common patterns?
- [ ] **Magic numbers/strings**: Constants defined?
- [ ] **Comments**: Why, not what? No redundant comments?

## Design & Architecture
- [ ] **Single Responsibility**: Functions/classes do one thing?
- [ ] **Open/Closed Principle**: Open for extension, closed for modification?
- [ ] **Liskov Substitution**: Subtypes are substitutable?
- [ ] **Interface Segregation**: No fat interfaces?
- [ ] **Dependency Inversion**: Depend on abstractions, not concretions?
- [ ] **Design patterns**: Used appropriately? Not forced?
- [ ] **Coupling**: Low coupling between modules?
- [ ] **Cohesion**: High cohesion within modules?

## Security
- [ ] **Input Validation**: All external input validated?
- [ ] **Output Encoding**: Prevents XSS? SQL injection?
- [ ] **Authentication**: Proper auth checks? Not bypassable?
- [ ] **Authorization**: Role-based access control?
- [ ] **Secrets**: No hardcoded credentials? Uses secrets management?
- [ ] **Cryptographic practices**: Secure algorithms? Proper key management?
- [ ] **Error messages**: No sensitive info leaked?
- [ ] **Dependency scanning**: No known vulnerabilities?

## Performance
- [ ] **Time Complexity**: Acceptable for expected load?
- [ ] **Space Complexity**: Memory usage reasonable?
- [ ] **Database**: N+1 queries? Missing indexes? Proper transactions?
- [ ] **Caching**: Used appropriately? Invalidation strategy?
- [ ] **Network calls**: Batched? Timeouts? Retry logic?
- [ ] **Async/await**: Used where blocking would be problematic?

## Error Handling & Logging
- [ ] **Exceptions**: Caught appropriately? Not swallowed?
- [ ] **Error messages**: Informative for debugging?
- [ ] **Logging**: Sufficient level (debug, info, error)?
- [ ] **Structured logging**: For log parsing?
- [ ] **Graceful degradation**: System remains stable on failure?

## Maintainability
- [ ] **Consistency**: Follows project style guide? (linting)
- [ ] **Configurability**: Hardcoded values replaced with config?
- [ ] **Modularity**: Components can be replaced/updated?
- [ ] **Tech debt**: Acknowledged? Ticketed?
- [ ] **Backward compatibility**: Breaking changes documented?

## Testing
- [ ] **Unit tests**: Cover main logic? Edge cases?
- [ ] **Integration tests**: Cover interactions?
- [ ] **Test readability**: Tests are clear? Given/When/Then?
- [ ] **Mocking**: Proper mocking? Not over-mocked?
- [ ] **Test isolation**: No shared state between tests?

## Version Control
- [ ] **Commits**: Atomic? Meaningful messages?
- [ ] **Branch**: Up to date with main? Rebased?
- [ ] **Merge commits**: Avoided? (prefer rebase)
- [ ] **Conflicts**: Resolved correctly?

## Platform/Infrastructure
- [ ] **Environment variables**: Documented? Required defaults?
- [ ] **Docker/Container**: Builds? Optimized?
- [ ] **CI/CD**: Pipeline passes? All steps needed?
- [ ] **Monitoring**: New metrics/alerts added?
- [ ] **Rollback plan**: Exists? Tested?

## Reviewer Notes
- [ ] **Overall assessment**: Approve, request changes, or comment?
- [ ] **Priority**: Critical, major, minor, nit?
- [ ] **Suggestions**: Provide alternatives? Link to docs?
- [ ] **Positive feedback**: Acknowledge good practices?

## Tools to Run
- Linting tools (e.g., `just lint`, `eslint`, `flake8`)
- Test runners (e.g., `just test`, `npm test`, `pytest`)
- Security scanners (e.g., `npm audit`, `safety check`, `bandit`, `semgrep`)
- `git diff` to double-check changes

## Common Pitfalls
- **Over-commenting**: Commenting obvious code
- **Under-testing**: Missing edge cases
- **Premature optimization**: Optimizing before measuring
- **Inconsistent style**: Mixing tabs/spaces, etc.
- **Ignoring warnings**: Linter warnings are there for a reason