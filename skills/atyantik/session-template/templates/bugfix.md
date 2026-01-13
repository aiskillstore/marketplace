### Phase 1: Reproduction
- [ ] Reproduce the bug reliably
- [ ] Document steps to reproduce
- [ ] Identify affected components
- [ ] Check if regression (previously working)
- [ ] Review related issues

### Phase 2: Root Cause Analysis
- [ ] Add debug logging
- [ ] Trace execution flow
- [ ] Identify exact failure point
- [ ] Understand why it fails
- [ ] Document root cause

### Phase 3: Write Reproduction Test (TDD)
- [ ] Write test that reproduces the bug
- [ ] Verify test fails (confirms bug exists)
- [ ] Test should be specific to the bug
- [ ] Include edge cases related to bug
- [ ] Document expected vs actual behavior

### Phase 4: Fix Implementation
- [ ] Implement minimal fix for root cause
- [ ] Avoid over-engineering the fix
- [ ] Add defensive checks if needed
- [ ] Add logging for future debugging
- [ ] Verify test now passes

### Phase 5: Regression Prevention
- [ ] Add tests for related scenarios
- [ ] Check if bug exists elsewhere
- [ ] Add validation to prevent recurrence
- [ ] Update error messages if applicable
- [ ] Document why bug occurred

### Phase 6: Quality & Testing
- [ ] Run full test suite (no regressions)
- [ ] Run make check
- [ ] Verify coverage maintained/improved
- [ ] Test manually with original report steps
- [ ] Check performance not degraded

### Phase 7: Documentation
- [ ] Update changelog
- [ ] Document fix in commit message
- [ ] Add code comments explaining fix
- [ ] Update docs if behavior changed
- [ ] Reference issue number if applicable
