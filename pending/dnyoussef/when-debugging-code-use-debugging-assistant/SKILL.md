# Debugging Assistant Skill

## Overview

Intelligent debugging workflow that systematically identifies symptoms, performs root cause analysis, generates fixes with explanations, validates solutions, and prevents regressions through comprehensive testing.

## Metadata

- **Skill ID:** `when-debugging-code-use-debugging-assistant`
- **Category:** Development/Debugging
- **Complexity:** HIGH
- **Agents Required:** coder, code-analyzer, tester
- **Prerequisites:** Access to codebase, error logs, test environment

## Trigger Conditions

Use this skill when encountering:
- Runtime errors or exceptions
- Unexpected behavior or incorrect output
- Performance degradation or memory leaks
- Race conditions or timing issues
- Integration failures
- Test failures requiring investigation

## 5-Phase Debugging Protocol (SOP)

### Phase 1: Symptom Identification

**Objective:** Gather comprehensive information about the issue

**Agent:** code-analyzer

**Actions:**
1. Collect error messages, stack traces, and logs
2. Document expected vs actual behavior
3. Identify reproduction steps
4. Determine scope and frequency of occurrence
5. Classify issue severity and impact

**Outputs:**
- Symptom report with complete context
- Reproduction steps (manual or automated)
- Environmental context (OS, runtime version, dependencies)
- Issue classification (bug, regression, edge case)

**Success Criteria:**
- Issue can be consistently reproduced
- All relevant context is documented
- Scope of impact is clearly defined

### Phase 2: Root Cause Analysis

**Objective:** Trace execution flow and identify the underlying cause

**Agent:** code-analyzer + coder

**Actions:**
1. Trace execution path from entry point to failure
2. Examine variable states and data transformations
3. Identify assumptions that may be violated
4. Check boundary conditions and edge cases
5. Review recent code changes that may have introduced the issue
6. Analyze dependencies and external system interactions

**Techniques:**
- Binary search debugging (narrow down location)
- Hypothesis-driven investigation
- Comparative analysis (working vs broken code paths)
- Temporal analysis (when did it start failing?)

**Outputs:**
- Root cause statement with evidence
- Affected code locations and line numbers
- Explanation of why the bug occurs
- Related issues or side effects

**Success Criteria:**
- Clear understanding of the mechanism causing the failure
- Reproducible test case that isolates the root cause
- Documented reasoning chain from symptom to cause

### Phase 3: Fix Generation

**Objective:** Develop and explain solution options

**Agent:** coder

**Actions:**
1. Generate 2-3 solution approaches
2. Evaluate trade-offs for each approach
3. Select optimal solution based on:
   - Correctness and completeness
   - Performance impact
   - Code maintainability
   - Risk of side effects
4. Implement the fix with clear comments
5. Document why this approach was chosen

**Fix Patterns:**
- **Null Safety:** Add null checks, use optional chaining
- **Race Conditions:** Add synchronization, use promises properly
- **Memory Leaks:** Clean up listeners, break circular references
- **Type Errors:** Add runtime validation, improve type definitions
- **Logic Errors:** Correct conditions, fix off-by-one errors

**Outputs:**
- Implemented fix with explanation
- Alternative approaches considered
- Potential side effects documented
- Migration notes if API changes

**Success Criteria:**
- Fix addresses root cause, not just symptoms
- Code is clean and maintainable
- No new issues introduced
- Clear explanation provided

### Phase 4: Validation Testing

**Objective:** Confirm the fix resolves the issue without breaking existing functionality

**Agent:** tester

**Actions:**
1. Create test case that reproduces original bug
2. Verify test fails before fix (proves test validity)
3. Apply fix and verify test passes
4. Run full regression test suite
5. Perform exploratory testing in affected areas
6. Test edge cases and boundary conditions
7. Validate in environment matching production

**Test Coverage:**
- Unit tests for isolated logic
- Integration tests for component interactions
- End-to-end tests for user workflows
- Performance tests if relevant
- Security tests if applicable

**Outputs:**
- Test case that validates the fix
- Regression test results
- Performance benchmarks (if applicable)
- Test coverage report

**Success Criteria:**
- Original issue is resolved
- No regression failures
- Test coverage increased
- Fix validated in realistic environment

### Phase 5: Regression Prevention

**Objective:** Ensure the issue doesn't recur

**Agent:** tester + coder

**Actions:**
1. Add permanent test case to test suite
2. Document the bug and fix in code comments
3. Update architecture documentation if patterns exposed
4. Add monitoring or assertions to catch similar issues
5. Consider if similar bugs exist elsewhere in codebase
6. Update development guidelines if needed

**Documentation:**
- Add comments explaining non-obvious fixes
- Update CHANGELOG or bug tracking system
- Create knowledge base entry for complex issues
- Document lessons learned

**Outputs:**
- Automated test preventing recurrence
- Updated documentation
- Code review checklist items (if applicable)
- Monitoring/alerting improvements

**Success Criteria:**
- Test suite will catch this issue if reintroduced
- Knowledge is preserved for team
- Similar issues are preventable
- Monitoring is in place (if applicable)

## Coordination Protocol

### Agent Communication Flow

```
1. User reports issue → code-analyzer (Symptom Identification)
2. code-analyzer findings → coder (Root Cause Analysis)
3. coder diagnosis → coder (Fix Generation)
4. coder fix → tester (Validation Testing)
5. tester results → coder + tester (Regression Prevention)
6. Final report → User
```

### Memory Coordination

**Memory Keys:**
- `debug/[issue-id]/symptoms` - Symptom analysis
- `debug/[issue-id]/root-cause` - RCA findings
- `debug/[issue-id]/fix` - Solution implementation
- `debug/[issue-id]/validation` - Test results
- `debug/[issue-id]/prevention` - Long-term measures

### Hooks Integration

**Pre-Debug Hook:**
```bash
npx claude-flow@alpha hooks pre-task --description "Debug: [issue-description]"
npx claude-flow@alpha hooks session-restore --session-id "debug-[issue-id]"
```

**Post-Fix Hook:**
```bash
npx claude-flow@alpha hooks post-edit --file "[fixed-file]" --memory-key "debug/[issue-id]/fix"
npx claude-flow@alpha hooks notify --message "Fix applied: [description]"
```

**Session End Hook:**
```bash
npx claude-flow@alpha hooks post-task --task-id "debug-[issue-id]"
npx claude-flow@alpha hooks session-end --export-metrics true
```

## Common Debugging Scenarios

### Scenario 1: Null Pointer Exception

**Symptom:**
```
TypeError: Cannot read property 'name' of undefined
  at processUser (users.js:45)
```

**Root Cause:** User object not validated before property access

**Fix:**
```javascript
// Before
function processUser(user) {
  return user.name.toUpperCase();
}

// After
function processUser(user) {
  if (!user || !user.name) {
    throw new Error('Invalid user object');
  }
  return user.name.toUpperCase();
}
```

**Test:**
```javascript
test('processUser handles missing user gracefully', () => {
  expect(() => processUser(null)).toThrow('Invalid user object');
  expect(() => processUser({})).toThrow('Invalid user object');
  expect(processUser({name: 'john'})).toBe('JOHN');
});
```

### Scenario 2: Async Race Condition

**Symptom:** Intermittent test failures, data corruption in production

**Root Cause:** Multiple async operations modifying shared state without synchronization

**Fix:**
```javascript
// Before - Race condition
async function updateCart(userId, item) {
  const cart = await getCart(userId);
  cart.items.push(item);
  await saveCart(userId, cart);
}

// After - Using optimistic locking
async function updateCart(userId, item) {
  let attempts = 0;
  while (attempts < 3) {
    const cart = await getCart(userId);
    const version = cart._version;
    cart.items.push(item);
    cart._version = version + 1;

    try {
      await saveCartWithVersion(userId, cart, version);
      return cart;
    } catch (error) {
      if (error.code === 'VERSION_CONFLICT') {
        attempts++;
        continue;
      }
      throw error;
    }
  }
  throw new Error('Failed to update cart after 3 attempts');
}
```

**Test:**
```javascript
test('updateCart handles concurrent modifications', async () => {
  const userId = 'user123';
  await createCart(userId);

  // Simulate concurrent updates
  const updates = await Promise.all([
    updateCart(userId, {id: 'item1'}),
    updateCart(userId, {id: 'item2'}),
    updateCart(userId, {id: 'item3'})
  ]);

  const finalCart = await getCart(userId);
  expect(finalCart.items).toHaveLength(3);
  expect(finalCart._version).toBe(3);
});
```

### Scenario 3: Memory Leak

**Symptom:** Application memory usage grows continuously, eventual crash

**Root Cause:** Event listeners not removed, causing references to remain

**Fix:**
```javascript
// Before - Memory leak
class DataStream {
  constructor() {
    this.listeners = [];
  }

  subscribe(callback) {
    window.addEventListener('data', callback);
    this.listeners.push(callback);
  }
}

// After - Proper cleanup
class DataStream {
  constructor() {
    this.listeners = new Set();
  }

  subscribe(callback) {
    window.addEventListener('data', callback);
    this.listeners.add(callback);

    // Return unsubscribe function
    return () => {
      window.removeEventListener('data', callback);
      this.listeners.delete(callback);
    };
  }

  destroy() {
    // Clean up all listeners
    this.listeners.forEach(callback => {
      window.removeEventListener('data', callback);
    });
    this.listeners.clear();
  }
}
```

**Test:**
```javascript
test('DataStream cleans up event listeners', () => {
  const stream = new DataStream();
  const callback1 = jest.fn();
  const callback2 = jest.fn();

  const unsubscribe1 = stream.subscribe(callback1);
  const unsubscribe2 = stream.subscribe(callback2);

  expect(stream.listeners.size).toBe(2);

  unsubscribe1();
  expect(stream.listeners.size).toBe(1);

  stream.destroy();
  expect(stream.listeners.size).toBe(0);
});
```

## Best Practices

### Do's
- Always reproduce the issue before attempting fixes
- Document your reasoning at each phase
- Write tests before applying fixes (TDD approach)
- Consider multiple solution approaches
- Validate fixes in realistic environments
- Add permanent regression tests
- Share knowledge with the team

### Don'ts
- Don't make assumptions without verification
- Don't fix symptoms without understanding root cause
- Don't skip test validation
- Don't introduce fixes that break existing functionality
- Don't leave debugging code in production
- Don't rush to a solution without analysis

## Performance Metrics

- **Time to Root Cause:** Target < 30 minutes for typical bugs
- **Fix Accuracy:** Target > 95% first-attempt success rate
- **Regression Rate:** Target < 2% of fixes introduce new issues
- **Test Coverage Increase:** Target +5-10% coverage per debug session

## Integration with Development Workflow

1. **Issue Reporting:** Link to bug tracking system
2. **Version Control:** Create fix branches following git-flow
3. **Code Review:** All fixes require peer review
4. **CI/CD:** Automated testing gates deployment
5. **Monitoring:** Alert on recurrence patterns

## Advanced Features

### Distributed Debugging
- Use MCP tools for coordinating multi-service debugging
- Trace distributed transactions across microservices
- Correlate logs from multiple systems

### Proactive Debugging
- Analyze error patterns to predict issues
- Use static analysis to find potential bugs
- Monitor performance metrics for anomalies

### Learning System
- Train neural patterns from successful debugging sessions
- Build knowledge base of common issues and solutions
- Improve diagnostic suggestions over time

## Troubleshooting the Debugging Process

If debugging is not progressing:
1. **Expand scope:** Issue may involve more components
2. **Narrow focus:** Try isolating a smaller reproduction case
3. **Fresh perspective:** Switch agents or involve another developer
4. **Rubber duck:** Explain the problem step-by-step
5. **Break and return:** Sometimes distance provides clarity

## References

- SPARC Methodology: Systematic problem-solving approach
- Claude Flow Hooks: Coordination and memory management
- Test-Driven Development: Fix validation patterns
- Root Cause Analysis: 5 Whys, Fishbone diagrams
