### Phase 1: Establish Safety Net
- [ ] Ensure tests exist for code being refactored
- [ ] Run tests - all must pass (baseline)
- [ ] Run make check - must pass
- [ ] Commit current state (safety checkpoint)
- [ ] Document current behavior

### Phase 2: Identify Improvements
- [ ] Identify code smells (duplication, complexity)
- [ ] Find violations of SOLID principles
- [ ] Look for unclear naming
- [ ] Identify missing abstractions
- [ ] List specific improvements needed

### Phase 3: Plan Refactoring Steps
- [ ] Break into small, safe steps
- [ ] Prioritize by risk/impact
- [ ] Identify dependencies between steps
- [ ] Plan to keep tests green throughout
- [ ] Consider breaking into multiple commits

### Phase 4: Refactor Incrementally
- [ ] Make one small change at a time
- [ ] Run tests after each change
- [ ] Keep tests passing (always green)
- [ ] Commit after each successful step
- [ ] If tests fail, revert and adjust approach

### Phase 5: Improve Design
- [ ] Extract methods/functions
- [ ] Remove duplication (DRY)
- [ ] Improve naming (clarity)
- [ ] Simplify complex conditionals
- [ ] Add type hints for clarity

### Phase 6: Quality Verification
- [ ] Run make check (must pass)
- [ ] Verify no behavior changes
- [ ] Check performance not degraded
- [ ] Review with tdd-reviewer agent
- [ ] Ensure coverage maintained

### Phase 7: Documentation
- [ ] Update docstrings for changed interfaces
- [ ] Add comments for complex logic
- [ ] Document why refactoring was needed
- [ ] Update architecture docs if applicable
- [ ] Record design decisions
