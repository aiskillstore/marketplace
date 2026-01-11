# Debugging Assistant - Process Documentation

## Overview

This document details the internal workflow, agent coordination, and technical implementation of the Debugging Assistant skill.

## Architecture

### Components

1. **Subagent** (`debugging-assistant`): Orchestrates the 5-phase process
2. **Slash Command** (`/debug-assist`): CLI interface for quick access
3. **MCP Tool** (`debug_analyze`): Integration with Claude Flow ecosystem
4. **Coordination Layer**: Memory and hooks for agent communication

### Technology Stack

- **Orchestration:** Claude Flow v2.0.0+
- **Agent Framework:** SPARC methodology
- **Memory System:** Claude Flow memory with hierarchical keys
- **Hooks System:** Pre/post task hooks for coordination
- **Testing:** Framework-agnostic (Jest, Mocha, Pytest, etc.)

## Detailed Phase Workflows

### Phase 1: Symptom Identification

**Agent:** code-analyzer

**Inputs:**
- User description of issue
- Error messages or logs (optional)
- File paths (optional)
- Recent changes (from git)

**Process Flow:**
```
1. Parse user input for key information
2. Search codebase for error locations
3. Extract stack traces and error contexts
4. Identify affected files and functions
5. Classify issue type and severity
6. Document reproduction steps
7. Store findings in memory: debug/[id]/symptoms
```

**Output Schema:**
```json
{
  "issueId": "debug-20231015-001",
  "type": "runtime-error",
  "severity": "high",
  "errorMessage": "TypeError: Cannot read property 'name' of undefined",
  "stackTrace": [...],
  "affectedFiles": ["src/users.js"],
  "affectedFunctions": ["processUser"],
  "reproductionSteps": [...],
  "environment": {
    "os": "linux",
    "nodeVersion": "18.17.0",
    "dependencies": {...}
  },
  "frequency": "always",
  "firstObserved": "2023-10-15T10:30:00Z"
}
```

**Success Criteria:**
- Issue can be consistently reproduced
- All contextual information captured
- Classification is accurate

### Phase 2: Root Cause Analysis

**Agents:** code-analyzer (primary), coder (assist)

**Inputs:**
- Symptom analysis from Phase 1
- Full codebase access
- Git history
- Test suite results

**Process Flow:**
```
1. Load symptom data from memory
2. Trace execution path from entry to failure point
3. Examine variable states at failure location
4. Identify violated assumptions or preconditions
5. Check boundary conditions and edge cases
6. Review git blame for recent changes
7. Analyze dependency interactions
8. Formulate hypothesis and verify
9. Store root cause in memory: debug/[id]/root-cause
```

**Analysis Techniques:**

#### Binary Search Debugging
```python
# Systematically narrow down problem location
def binary_search_debug(code_sections, test_case):
    if len(code_sections) == 1:
        return code_sections[0]  # Found problematic section

    mid = len(code_sections) // 2
    first_half = code_sections[:mid]
    second_half = code_sections[mid:]

    # Test each half
    if test_fails_with(first_half, test_case):
        return binary_search_debug(first_half, test_case)
    else:
        return binary_search_debug(second_half, test_case)
```

#### Data Flow Analysis
```javascript
// Trace data transformations
function traceDataFlow(startPoint, failurePoint) {
  const transformations = [];
  let currentValue = startPoint.value;

  for (const step of executionPath) {
    const prevValue = currentValue;
    currentValue = step.transform(currentValue);
    transformations.push({
      step: step.name,
      input: prevValue,
      output: currentValue,
      expected: step.expected
    });

    if (currentValue !== step.expected) {
      return {
        failurePoint: step,
        transformations: transformations
      };
    }
  }
}
```

**Output Schema:**
```json
{
  "rootCause": {
    "description": "User object is undefined because async getUserById call is not awaited",
    "location": {
      "file": "src/users.js",
      "line": 45,
      "function": "processUser"
    },
    "mechanism": "Function processUser expects a user object but receives undefined because the Promise from getUserById has not resolved yet",
    "evidence": [
      "Variable 'user' is logged as Promise { <pending> }",
      "Missing 'await' keyword before getUserById call",
      "Function is declared 'async' but doesn't use await"
    ],
    "contributingFactors": [
      "No type checking enforcing async/await patterns",
      "No runtime validation of user object"
    ]
  },
  "relatedIssues": [],
  "hypothesis": "Adding await will resolve the Promise and provide user object",
  "confidence": 0.95
}
```

### Phase 3: Fix Generation

**Agent:** coder

**Inputs:**
- Root cause analysis from Phase 2
- Codebase context
- Project coding standards
- Similar fixes from memory

**Process Flow:**
```
1. Load root cause from memory
2. Generate 2-3 solution approaches
3. Evaluate each approach:
   - Correctness
   - Performance impact
   - Maintainability
   - Side effects risk
4. Select optimal solution
5. Implement fix with clear comments
6. Document alternatives and reasoning
7. Store fix in memory: debug/[id]/fix
```

**Solution Evaluation Matrix:**

| Criterion | Weight | Approach A | Approach B | Approach C |
|-----------|--------|------------|------------|------------|
| Correctness | 40% | 10 | 9 | 10 |
| Performance | 20% | 8 | 10 | 7 |
| Maintainability | 25% | 9 | 7 | 10 |
| Risk | 15% | 9 | 8 | 10 |
| **Total** | 100% | **9.15** | **8.55** | **9.40** |

**Fix Patterns Library:**

#### Pattern 1: Null Safety
```typescript
// Before
function processUser(user: User) {
  return user.name.toUpperCase();
}

// After
function processUser(user: User | null): string {
  if (!user?.name) {
    throw new Error('Invalid user object');
  }
  return user.name.toUpperCase();
}
```

#### Pattern 2: Async/Await
```javascript
// Before
function loadUser(id) {
  getUserById(id).then(user => {
    processUser(user);
  });
}

// After
async function loadUser(id) {
  const user = await getUserById(id);
  return processUser(user);
}
```

#### Pattern 3: Race Condition Prevention
```javascript
// Before
let counter = 0;
async function increment() {
  const current = counter;
  await delay(10);
  counter = current + 1;
}

// After
const mutex = new Mutex();
async function increment() {
  const release = await mutex.acquire();
  try {
    const current = counter;
    await delay(10);
    counter = current + 1;
  } finally {
    release();
  }
}
```

#### Pattern 4: Memory Leak Prevention
```javascript
// Before
class Component {
  constructor() {
    window.addEventListener('resize', this.handleResize);
  }
  handleResize = () => { /* ... */ }
}

// After
class Component {
  constructor() {
    this.handleResize = this.handleResize.bind(this);
    window.addEventListener('resize', this.handleResize);
  }
  handleResize() { /* ... */ }
  destroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}
```

**Output Schema:**
```json
{
  "selectedFix": {
    "approach": "Add await keyword and null validation",
    "implementation": "// File: src/users.js\n...",
    "reasoning": "This approach directly addresses the root cause with minimal code changes and no performance impact",
    "riskAssessment": "Low - isolated change with no side effects"
  },
  "alternativeApproaches": [
    {
      "description": "Use Promise.then() instead of async/await",
      "pros": ["No function signature change"],
      "cons": ["More complex control flow", "Harder to maintain"],
      "notChosen": "Less maintainable than async/await"
    }
  ],
  "codeChanges": [
    {
      "file": "src/users.js",
      "changes": "..."
    }
  ],
  "migrationNotes": null
}
```

### Phase 4: Validation Testing

**Agent:** tester

**Inputs:**
- Fix implementation from Phase 3
- Original symptom details from Phase 1
- Existing test suite

**Process Flow:**
```
1. Load fix and symptom data from memory
2. Create test case that reproduces original bug
3. Verify test fails before fix (red)
4. Apply fix
5. Verify test passes after fix (green)
6. Run full regression test suite
7. Perform exploratory testing
8. Test edge cases and boundary conditions
9. Validate in production-like environment
10. Store validation results: debug/[id]/validation
```

**Test Creation Strategy:**

#### Unit Test Template
```javascript
describe('Bug Fix: [Issue Description]', () => {
  describe('Reproduction Case', () => {
    it('should fail before fix', () => {
      // This test documents the bug
      // Normally would be disabled or removed
      expect(() => {
        processUser(undefined);
      }).toThrow();
    });

    it('should handle null/undefined user gracefully', () => {
      expect(() => processUser(null)).toThrow('Invalid user object');
      expect(() => processUser(undefined)).toThrow('Invalid user object');
    });
  });

  describe('Expected Behavior', () => {
    it('should process valid user correctly', () => {
      const user = { name: 'John Doe' };
      expect(processUser(user)).toBe('JOHN DOE');
    });

    it('should handle edge cases', () => {
      expect(processUser({ name: '' })).toBe('');
      expect(processUser({ name: 'a' })).toBe('A');
    });
  });

  describe('Regression Protection', () => {
    it('should maintain backward compatibility', () => {
      // Ensure fix doesn't break existing functionality
      const existingBehavior = legacyTest();
      expect(existingBehavior).toBeTruthy();
    });
  });
});
```

#### Integration Test Template
```javascript
describe('Integration: User Processing Flow', () => {
  it('should handle complete user workflow', async () => {
    // Setup
    const userId = await createTestUser();

    // Execute
    const result = await loadAndProcessUser(userId);

    // Verify
    expect(result).toBeDefined();
    expect(result.name).toBeTruthy();

    // Cleanup
    await deleteTestUser(userId);
  });

  it('should handle missing users gracefully', async () => {
    const result = await loadAndProcessUser('nonexistent-id');
    expect(result).toBeNull();
  });
});
```

**Validation Checklist:**

- [ ] Original issue is resolved
- [ ] Test reproduces original bug
- [ ] Test passes after fix
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] No new test failures introduced
- [ ] Edge cases covered
- [ ] Performance benchmarks within acceptable range
- [ ] Security implications reviewed
- [ ] Accessibility maintained
- [ ] Documentation updated

**Output Schema:**
```json
{
  "validation": {
    "originalIssueResolved": true,
    "testCreated": {
      "file": "tests/users.test.js",
      "description": "Test for null user handling"
    },
    "regressionResults": {
      "totalTests": 247,
      "passed": 247,
      "failed": 0,
      "skipped": 0
    },
    "coverageImpact": {
      "before": 85.2,
      "after": 87.1,
      "delta": +1.9
    },
    "performanceBenchmark": {
      "baseline": "100ms",
      "afterFix": "102ms",
      "acceptable": true
    }
  }
}
```

### Phase 5: Regression Prevention

**Agents:** tester (primary), coder (assist)

**Inputs:**
- Validation results from Phase 4
- Fix implementation from Phase 3
- Project documentation

**Process Flow:**
```
1. Load validation and fix data from memory
2. Add permanent test to test suite
3. Update code comments explaining fix
4. Document bug in changelog/knowledge base
5. Add monitoring or assertions if applicable
6. Search codebase for similar patterns
7. Update development guidelines if needed
8. Create PR with all changes
9. Store prevention measures: debug/[id]/prevention
```

**Documentation Updates:**

#### Code Comments
```javascript
/**
 * Processes user data and returns formatted name.
 *
 * @param {User|null|undefined} user - User object to process
 * @returns {string} Formatted user name
 * @throws {Error} If user is null/undefined or missing name property
 *
 * @bugfix 2023-10-15: Added null/undefined validation to prevent
 * TypeError when user object is not properly loaded. See issue #1234.
 * The function now explicitly validates the user object and provides
 * a clear error message rather than failing with "Cannot read property".
 */
async function processUser(user) {
  if (!user?.name) {
    throw new Error('Invalid user object: user and user.name are required');
  }
  return user.name.toUpperCase();
}
```

#### Changelog Entry
```markdown
## [1.2.3] - 2023-10-15

### Fixed
- **User Processing:** Fixed TypeError when processing null/undefined user objects
  - Added validation to `processUser()` function
  - Improved error messages for debugging
  - Added comprehensive test coverage
  - Issue: #1234
```

#### Knowledge Base Entry
```markdown
# Common Bug: Null/Undefined User Objects

## Problem
Functions expecting user objects may receive null/undefined due to:
- Async database queries not properly awaited
- Optional user lookups returning null
- Error conditions not handled upstream

## Solution Pattern
Always validate object presence before accessing properties:

```javascript
if (!user?.name) {
  throw new Error('Invalid user object');
}
```

## Related Issues
- #1234 - processUser TypeError
- #1189 - Similar issue in formatUserEmail

## Prevention
- Use TypeScript for compile-time null checking
- Enable ESLint rule: no-unsafe-optional-chaining
- Add runtime validation library (e.g., Zod)
```

**Monitoring and Assertions:**

```javascript
// Add assertion in development
if (process.env.NODE_ENV === 'development') {
  console.assert(user && user.name, 'User object must have name property');
}

// Add monitoring in production
if (!user?.name) {
  logger.error('Invalid user object detected', {
    context: 'processUser',
    userId: userId,
    stackTrace: new Error().stack
  });
  metrics.increment('errors.invalid_user_object');
  throw new Error('Invalid user object');
}
```

**Similar Pattern Detection:**

```bash
# Search for similar patterns that might have the same bug
npx claude-flow@alpha hooks grep --pattern "user\\.\\w+\\." --exclude "*.test.js"
# Review each occurrence for proper null checking
```

**Output Schema:**
```json
{
  "prevention": {
    "testAdded": {
      "file": "tests/users.test.js",
      "permanent": true,
      "coverage": ["null handling", "undefined handling", "edge cases"]
    },
    "documentation": {
      "codeComments": true,
      "changelog": true,
      "knowledgeBase": "docs/kb/null-user-objects.md"
    },
    "monitoring": {
      "assertions": true,
      "logging": true,
      "metrics": ["errors.invalid_user_object"]
    },
    "similarIssues": [
      {
        "file": "src/emails.js",
        "function": "formatUserEmail",
        "status": "fixed",
        "pr": "#5678"
      }
    ],
    "guidelinesUpdated": [
      "docs/coding-standards.md: Added null checking requirements"
    ]
  }
}
```

## Agent Coordination

### Memory Structure

```
debug/
├── [issue-id]/
│   ├── symptoms          # Phase 1 output
│   ├── root-cause        # Phase 2 output
│   ├── fix               # Phase 3 output
│   ├── validation        # Phase 4 output
│   └── prevention        # Phase 5 output
├── patterns/
│   ├── null-errors       # Pattern library
│   ├── race-conditions
│   └── memory-leaks
└── metrics/
    ├── success-rate
    └── time-to-fix
```

### Hook Integration

**Session Start:**
```bash
npx claude-flow@alpha hooks pre-task \
  --description "Debug: [issue-description]" \
  --tags "debugging,bug-fix" \
  --session-id "debug-[issue-id]"
```

**Between Phases:**
```bash
npx claude-flow@alpha hooks notify \
  --message "Phase [N] complete: [summary]" \
  --memory-key "debug/[issue-id]/phase[N]"
```

**Session End:**
```bash
npx claude-flow@alpha hooks post-task \
  --task-id "debug-[issue-id]" \
  --export-metrics true \
  --summary "Fixed [issue]: [solution-summary]"
```

### Agent Communication Protocol

```
┌─────────────────┐
│  User Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ code-analyzer   │ Phase 1: Symptom Identification
│  (Orchestrator) │ → Memory: debug/[id]/symptoms
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ code-analyzer + │ Phase 2: Root Cause Analysis
│     coder       │ → Memory: debug/[id]/root-cause
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      coder      │ Phase 3: Fix Generation
│                 │ → Memory: debug/[id]/fix
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     tester      │ Phase 4: Validation Testing
│                 │ → Memory: debug/[id]/validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  tester + coder │ Phase 5: Regression Prevention
│                 │ → Memory: debug/[id]/prevention
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Final Report to │
│      User       │
└─────────────────┘
```

## Performance Optimization

### Parallel Operations

Where possible, execute operations in parallel:

```javascript
// Parallel symptom gathering
const [errorLogs, gitHistory, testResults] = await Promise.all([
  getErrorLogs(),
  getGitHistory(),
  runTestSuite()
]);

// Parallel validation
const [unitTests, integrationTests, e2eTests] = await Promise.all([
  runUnitTests(),
  runIntegrationTests(),
  runE2ETests()
]);
```

### Caching

Cache frequent operations:

```javascript
// Cache file analysis
const fileCache = new Map();
function analyzeFile(filePath) {
  if (fileCache.has(filePath)) {
    return fileCache.get(filePath);
  }
  const analysis = performAnalysis(filePath);
  fileCache.set(filePath, analysis);
  return analysis;
}
```

### Early Termination

Stop processing when high-confidence solution found:

```javascript
if (rootCauseConfidence > 0.95 && fixValidated) {
  return earlySuccess();
}
```

## Error Handling

### Fallback Strategies

```javascript
async function debugWithFallback(issue) {
  try {
    return await fullDebugProcess(issue);
  } catch (error) {
    if (error.code === 'CANNOT_REPRODUCE') {
      return await manualReproductionGuide(issue);
    }
    if (error.code === 'COMPLEX_ROOT_CAUSE') {
      return await escalateToHumanExpert(issue);
    }
    throw error;
  }
}
```

### Partial Success Handling

```javascript
// If validation fails but fix is sound
if (fixGenerated && !allTestsPassed) {
  return {
    status: 'partial',
    fix: generatedFix,
    failingTests: failedTests,
    recommendation: 'Review failing tests - may be pre-existing issues'
  };
}
```

## Metrics and Monitoring

### Key Performance Indicators

- **Mean Time To Root Cause (MTTRC):** Average time to complete Phase 2
- **Fix Success Rate:** Percentage of fixes that pass validation
- **Regression Rate:** Percentage of fixes that introduce new bugs
- **Test Coverage Delta:** Average increase in test coverage
- **Issue Recurrence Rate:** Percentage of issues that recur after fix

### Instrumentation

```javascript
const metrics = {
  startTime: Date.now(),
  phaseTimings: {},
  agentCalls: 0,
  memoryReads: 0,
  memoryWrites: 0,
  testExecutions: 0
};

// Track phase timing
function trackPhase(phaseName, fn) {
  const start = Date.now();
  const result = await fn();
  metrics.phaseTimings[phaseName] = Date.now() - start;
  return result;
}
```

## Integration Points

### Issue Tracking Systems
- JIRA, GitHub Issues, Linear
- Auto-link fixes to issues
- Update issue status on completion

### Version Control
- Auto-create feature branches
- Generate descriptive commit messages
- Create pull requests with context

### CI/CD Pipelines
- Trigger test runs
- Block deployment if tests fail
- Auto-merge if all checks pass

### Monitoring Systems
- DataDog, New Relic, Sentry
- Send metrics on fix completion
- Alert on recurring issues

## Advanced Scenarios

### Multi-Service Debugging

For issues spanning multiple microservices:

```javascript
async function debugDistributed(issue) {
  // Trace request across services
  const trace = await getDistributedTrace(issue.requestId);

  // Identify failing service
  const failurePoint = trace.find(span => span.error);

  // Debug specific service
  return await debugService(failurePoint.service, issue);
}
```

### Performance Debugging

For performance degradation issues:

```javascript
async function debugPerformance(issue) {
  // Baseline performance
  const baseline = await getBenchmark(issue.operation, issue.baselineCommit);

  // Current performance
  const current = await getBenchmark(issue.operation, 'HEAD');

  // Binary search for regression commit
  const regressionCommit = await gitBisect(
    issue.baselineCommit,
    'HEAD',
    (commit) => getBenchmark(issue.operation, commit) < baseline * 1.5
  );

  return analyzeCommit(regressionCommit);
}
```

### Security Debugging

For security vulnerabilities:

```javascript
async function debugSecurity(vulnerability) {
  // Run security scanners
  const scanResults = await runSecurityScans();

  // Analyze attack surface
  const attackSurface = analyzeAttackSurface(vulnerability);

  // Generate secure fix
  const fix = await generateSecureFix(vulnerability, scanResults);

  // Verify fix doesn't introduce new vulnerabilities
  await validateSecurityFix(fix);

  return fix;
}
```

---

This process documentation provides the foundation for effective, systematic debugging. Adapt and extend as needed for your specific project context.
