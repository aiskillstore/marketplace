### Phase 1: Research & Design
- [ ] Review related code in the codebase
- [ ] Identify integration points
- [ ] Design data models and interfaces
- [ ] Document API contracts
- [ ] Consider edge cases and error scenarios

### Phase 2: Write Tests (TDD)
- [ ] Write tests for happy path scenarios
- [ ] Write tests for edge cases
- [ ] Write tests for error handling
- [ ] Write integration tests
- [ ] Ensure tests fail initially (red phase)

### Phase 3: Implementation
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Add input validation
- [ ] Add logging
- [ ] Run tests - should pass (green phase)

### Phase 4: Refactoring
- [ ] Remove duplication (DRY)
- [ ] Simplify complex logic
- [ ] Improve naming
- [ ] Add type hints where missing
- [ ] Keep tests passing

### Phase 5: Quality Check
- [ ] Run make check (format, lint, test, security)
- [ ] Fix all quality issues
- [ ] Verify coverage ≥ 80%
- [ ] Review with tdd-reviewer agent
- [ ] Apply quality-fixer for auto-fixable issues

### Phase 6: Documentation
- [ ] Update README if user-facing changes
- [ ] Add/update docstrings
- [ ] Update API documentation
- [ ] Add usage examples
- [ ] Document configuration changes

### Phase 7: Final Review
- [ ] Review all changes with git diff
- [ ] Test manually in development
- [ ] Verify all edge cases work
- [ ] Check performance implications
- [ ] Ready for PR/commit
