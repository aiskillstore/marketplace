# Detailed Process for Functionality Audit

## Process Overview

The Functionality Audit skill validates code execution through a systematic 5-phase workflow:

1. **Setup Testing Environment** - Create isolated sandbox with dependencies
2. **Execute Code with Realistic Inputs** - Run comprehensive tests
3. **Debug Issues** - Systematic root cause analysis
4. **Validate Functionality** - Verify fixes and check for regressions
5. **Report Results** - Comprehensive documentation and metrics

Each phase builds on the previous, with memory coordination ensuring seamless data flow between agents.

## Phase-by-Phase Guide

### Phase 1: Setup Testing Environment (10-15 minutes)

**Objective:** Create isolated, reproducible environment for safe code execution

**Step-by-Step Instructions:**

1. **Initialize Swarm and Agents**
   ```bash
   npx claude-flow hooks pre-task --description "Phase 1: Setup Testing Environment"
   npx claude-flow swarm init --topology hierarchical --max-agents 2
   npx claude-flow agent spawn --type tester --capabilities "sandbox-setup,environment-config"
   ```

2. **Create Sandbox Directory**
   ```bash
   mkdir -p /tmp/functionality-audit-sandbox-$(date +%s)
   cd /tmp/functionality-audit-sandbox-*
   export AUDIT_SANDBOX=$(pwd)
   ```

3. **Initialize Project Structure**
   ```bash
   # For Node.js projects
   npm init -y

   # For Python projects
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

4. **Install Testing Framework**
   ```bash
   # Node.js
   npm install --save-dev jest @types/jest ts-node typescript

   # Python
   pip install pytest pytest-cov pytest-mock
   ```

5. **Configure Testing Tools**
   ```bash
   # Create jest.config.js
   cat > jest.config.js << 'EOF'
   module.exports = {
     preset: 'ts-jest',
     testEnvironment: 'node',
     collectCoverage: true,
     coverageDirectory: 'coverage',
     coverageThreshold: {
       global: {
         branches: 70,
         functions: 80,
         lines: 80,
         statements: 80
       }
     },
     testMatch: ['**/*.test.ts', '**/*.test.js'],
     verbose: true
   };
   EOF

   # Create pytest.ini
   cat > pytest.ini << 'EOF'
   [pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   addopts =
       --verbose
       --cov=src
       --cov-report=html
       --cov-report=term-missing
   EOF
   ```

6. **Validate Environment**
   ```bash
   # Test that testing framework works
   npm test -- --version || echo "npm test configured"
   pytest --version || echo "pytest configured"
   ```

7. **Store Configuration in Memory**
   ```bash
   npx claude-flow memory store \
     --key "testing/functionality-audit/phase-1/tester/sandbox-config" \
     --value "{\"path\":\"$AUDIT_SANDBOX\",\"framework\":\"jest\",\"ready\":true}"
   ```

**Quality Gates:**
- [ ] Sandbox directory created and accessible
- [ ] Testing framework installed without errors
- [ ] Configuration files created and valid
- [ ] Environment validation passes
- [ ] Configuration stored in memory

**Common Issues:**
- **Permission errors:** Run with appropriate privileges or use Docker
- **Dependency conflicts:** Clear package lock files and reinstall
- **Framework not found:** Verify PATH includes npm/pip bin directories

---

### Phase 2: Execute Code with Realistic Inputs (15-20 minutes)

**Objective:** Run comprehensive tests with realistic data to validate functionality

**Step-by-Step Instructions:**

1. **Retrieve Sandbox Configuration**
   ```bash
   SANDBOX_CONFIG=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-1/tester/sandbox-config")
   cd $(echo $SANDBOX_CONFIG | jq -r '.path')
   ```

2. **Copy Code to Sandbox**
   ```bash
   # Copy source code from project
   cp -r /path/to/project/src ./src
   cp -r /path/to/project/tests ./tests 2>/dev/null || mkdir tests

   # Or clone from repository
   git clone <repo-url> --depth 1 source
   ```

3. **Generate Test Cases (if not existing)**
   ```javascript
   // Auto-generate tests for uncovered functions
   const fs = require('fs');
   const path = require('path');

   // Scan source files
   const sourceFiles = fs.readdirSync('src').filter(f => f.endsWith('.js'));

   sourceFiles.forEach(file => {
     const testFile = `tests/${file.replace('.js', '.test.js')}`;
     if (!fs.existsSync(testFile)) {
       // Generate basic test template
       const template = `
   const module = require('../src/${file}');

   describe('${file}', () => {
     test('basic functionality', () => {
       // Add test implementation
       expect(true).toBe(true);
     });
   });
       `;
       fs.writeFileSync(testFile, template);
     }
   });
   ```

4. **Prepare Realistic Test Data**
   ```bash
   # Create test fixtures
   mkdir -p tests/fixtures

   cat > tests/fixtures/users.json << 'EOF'
   [
     {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
     {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
     {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"}
   ]
   EOF
   ```

5. **Execute Tests with Coverage**
   ```bash
   # Run tests and capture output
   npm test -- --coverage --verbose > test-output.log 2>&1
   TEST_EXIT_CODE=$?

   echo "Test execution completed with exit code: $TEST_EXIT_CODE"
   ```

6. **Collect Metrics**
   ```bash
   # Extract coverage data
   COVERAGE=$(grep -oP '\d+\.\d+(?=%)' coverage/lcov-report/index.html | head -1 || echo "0")

   # Count test results
   TESTS_RUN=$(grep -c "PASS\|FAIL" test-output.log || echo "0")
   TESTS_PASSED=$(grep -c "PASS" test-output.log || echo "0")
   TESTS_FAILED=$(grep -c "FAIL" test-output.log || echo "0")

   # Create metrics JSON
   cat > execution-metrics.json << EOF
   {
     "tests_run": $TESTS_RUN,
     "tests_passed": $TESTS_PASSED,
     "tests_failed": $TESTS_FAILED,
     "coverage_percentage": $COVERAGE,
     "exit_code": $TEST_EXIT_CODE,
     "timestamp": "$(date -Iseconds)"
   }
   EOF
   ```

7. **Store Results in Memory**
   ```bash
   npx claude-flow memory store \
     --key "testing/functionality-audit/phase-2/tester/execution-results" \
     --value "$(cat execution-metrics.json)"

   # Store logs separately
   npx claude-flow memory store \
     --key "testing/functionality-audit/phase-2/tester/logs" \
     --value "$(cat test-output.log | base64)"
   ```

**Quality Gates:**
- [ ] All tests executed without environment errors
- [ ] Test output captured completely
- [ ] Coverage data collected successfully
- [ ] Metrics calculated and stored
- [ ] Results available in memory for next phase

**Common Issues:**
- **Module not found:** Install missing dependencies with npm/pip install
- **Timeout errors:** Increase test timeout in configuration
- **Out of memory:** Reduce test parallelization or increase heap size

---

### Phase 3: Debug Issues (20-30 minutes)

**Objective:** Systematically identify root causes and develop fix strategies

**Step-by-Step Instructions:**

1. **Retrieve Execution Results**
   ```bash
   EXEC_RESULTS=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-2/tester/execution-results")
   EXIT_CODE=$(echo $EXEC_RESULTS | jq -r '.exit_code')

   if [ "$EXIT_CODE" != "0" ]; then
     echo "Failures detected, initiating debugging..."
   fi
   ```

2. **Extract and Categorize Failures**
   ```bash
   # Extract failure information
   grep -E "(FAIL|ERROR|Exception)" test-output.log > failures.txt

   # Categorize by error type
   cat > categorize-errors.js << 'EOF'
   const fs = require('fs');
   const failures = fs.readFileSync('failures.txt', 'utf-8').split('\n');

   const categories = {
     syntax_errors: [],
     runtime_errors: [],
     logic_errors: [],
     integration_failures: [],
     dependency_issues: []
   };

   failures.forEach(line => {
     if (line.includes('SyntaxError')) categories.syntax_errors.push(line);
     else if (line.includes('TypeError') || line.includes('ReferenceError')) {
       categories.runtime_errors.push(line);
     }
     else if (line.includes('Expected') || line.includes('toBe')) {
       categories.logic_errors.push(line);
     }
     else if (line.includes('Cannot find module') || line.includes('ENOENT')) {
       categories.dependency_issues.push(line);
     }
     else categories.integration_failures.push(line);
   });

   fs.writeFileSync('issue-categories.json', JSON.stringify(categories, null, 2));
   EOF

   node categorize-errors.js
   ```

3. **Perform Root Cause Analysis**
   ```bash
   # For each failure category, analyze root causes
   cat > root-cause-analysis.md << 'EOF'
   # Root Cause Analysis

   ## Syntax Errors
   - **Cause:** Invalid JavaScript/TypeScript syntax
   - **Fix:** Correct syntax based on language specification
   - **Priority:** Critical (blocks execution)

   ## Runtime Errors
   - **Cause:** Invalid operations on undefined/null values
   - **Fix:** Add null checks and defensive programming
   - **Priority:** High (causes crashes)

   ## Logic Errors
   - **Cause:** Incorrect implementation of business logic
   - **Fix:** Review requirements and correct algorithm
   - **Priority:** High (incorrect behavior)

   ## Dependency Issues
   - **Cause:** Missing or incompatible dependencies
   - **Fix:** Install correct versions and update imports
   - **Priority:** Critical (blocks execution)

   ## Integration Failures
   - **Cause:** API mismatches or contract violations
   - **Fix:** Update interfaces and integration points
   - **Priority:** Medium (affects specific scenarios)
   EOF
   ```

4. **Generate Fix Strategies**
   ```bash
   # Create prioritized fix list
   cat > fix-strategy.json << 'EOF'
   {
     "fixes": [
       {
         "priority": 1,
         "category": "syntax_errors",
         "description": "Correct syntax errors preventing compilation",
         "files": ["src/auth.js", "src/utils.js"],
         "estimated_time": "10 minutes"
       },
       {
         "priority": 2,
         "category": "dependency_issues",
         "description": "Install missing dependencies",
         "command": "npm install missing-package",
         "estimated_time": "5 minutes"
       },
       {
         "priority": 3,
         "category": "runtime_errors",
         "description": "Add null checks and error handling",
         "files": ["src/data-processor.js"],
         "estimated_time": "15 minutes"
       }
     ]
   }
   EOF
   ```

5. **Apply Fixes Systematically**
   ```bash
   # Fix priority 1 issues first
   # Example: Syntax error fix
   sed -i 's/const user = {/const user = {\n  id: null,/g' src/auth.js

   # Fix priority 2 issues
   npm install missing-package

   # Fix priority 3 issues
   # Add null checks to functions
   ```

6. **Store Debugging Results**
   ```bash
   npx claude-flow memory store \
     --key "testing/functionality-audit/phase-3/coder/root-causes" \
     --value "$(cat issue-categories.json)"

   npx claude-flow memory store \
     --key "testing/functionality-audit/phase-3/coder/fix-strategy" \
     --value "$(cat fix-strategy.json)"
   ```

**Quality Gates:**
- [ ] All failures extracted and categorized
- [ ] Root causes identified for each category
- [ ] Fix strategies documented with priorities
- [ ] Initial fixes applied systematically
- [ ] Results stored for validation phase

**Common Issues:**
- **Cascading failures:** Fix fundamental issues first (syntax, dependencies)
- **Unclear errors:** Add debugging logs and breakpoints for clarity
- **Complex interdependencies:** Use dependency graphs to understand relationships

---

### Phase 4: Validate Functionality (15-25 minutes)

**Objective:** Verify fixes resolve issues without introducing regressions

**Step-by-Step Instructions:**

1. **Retrieve Fix Information**
   ```bash
   FIX_STRATEGY=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-3/coder/fix-strategy")
   echo "Validating fixes..."
   ```

2. **Rerun Tests After Fixes**
   ```bash
   # Execute tests again
   npm test -- --coverage --verbose > retest-output.log 2>&1
   RETEST_EXIT_CODE=$?

   echo "Retest completed with exit code: $RETEST_EXIT_CODE"
   ```

3. **Compare Results with Baseline**
   ```bash
   # Extract new metrics
   NEW_TESTS_PASSED=$(grep -c "PASS" retest-output.log || echo "0")
   NEW_COVERAGE=$(grep -oP '\d+\.\d+(?=%)' coverage/lcov-report/index.html | head -1 || echo "0")

   # Load original metrics
   ORIGINAL_TESTS_PASSED=$(echo $EXEC_RESULTS | jq -r '.tests_passed')

   # Calculate improvement
   IMPROVEMENT=$((NEW_TESTS_PASSED - ORIGINAL_TESTS_PASSED))
   echo "Test improvement: $IMPROVEMENT additional tests passing"
   ```

4. **Detect Regressions**
   ```bash
   # Compare test results line by line
   diff <(grep "PASS\|FAIL" test-output.log | sort) \
        <(grep "PASS\|FAIL" retest-output.log | sort) > regression-diff.txt

   # Check for previously passing tests now failing
   REGRESSIONS=$(grep "^<.*PASS" regression-diff.txt | wc -l)

   if [ "$REGRESSIONS" -gt 0 ]; then
     echo "WARNING: $REGRESSIONS regression(s) detected!"
   fi
   ```

5. **Assess Production Readiness**
   ```bash
   # Define readiness criteria
   COVERAGE_THRESHOLD=80
   MIN_TESTS_PASSING_PCT=90

   # Calculate metrics
   TESTS_TOTAL=$(echo $EXEC_RESULTS | jq -r '.tests_run')
   PASSING_PCT=$((NEW_TESTS_PASSED * 100 / TESTS_TOTAL))

   # Evaluate readiness
   READY=true
   [ "$RETEST_EXIT_CODE" -ne 0 ] && READY=false
   [ "$REGRESSIONS" -gt 0 ] && READY=false
   [ "$(echo "$NEW_COVERAGE < $COVERAGE_THRESHOLD" | bc)" -eq 1 ] && READY=false
   [ "$PASSING_PCT" -lt "$MIN_TESTS_PASSING_PCT" ] && READY=false

   cat > production-readiness.json << EOF
   {
     "all_tests_passing": $([ "$RETEST_EXIT_CODE" -eq 0 ] && echo "true" || echo "false"),
     "coverage_threshold_met": $([ "$(echo "$NEW_COVERAGE >= $COVERAGE_THRESHOLD" | bc)" -eq 1 ] && echo "true" || echo "false"),
     "no_regressions": $([ "$REGRESSIONS" -eq 0 ] && echo "true" || echo "false"),
     "passing_percentage": $PASSING_PCT,
     "ready_for_deployment": $READY,
     "tests_passing": $NEW_TESTS_PASSED,
     "tests_total": $TESTS_TOTAL,
     "coverage": $NEW_COVERAGE
   }
   EOF
   ```

6. **Store Validation Results**
   ```bash
   npx claude-flow memory store \
     --key "testing/functionality-audit/phase-4/validator/readiness" \
     --value "$(cat production-readiness.json)"
   ```

**Quality Gates:**
- [ ] All critical tests passing (100%)
- [ ] Code coverage ≥ 80%
- [ ] Zero regressions detected
- [ ] Performance within acceptable range
- [ ] Production readiness confirmed

**Common Issues:**
- **Persistent failures:** Review fix implementation, may need alternative approach
- **Regressions introduced:** Revert problematic fixes, apply more carefully
- **Coverage not improving:** Add tests for uncovered code paths

---

### Phase 5: Report Results (10-15 minutes)

**Objective:** Generate comprehensive documentation and actionable insights

**Step-by-Step Instructions:**

1. **Retrieve All Phase Results**
   ```bash
   SANDBOX_CONFIG=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-1/tester/sandbox-config")
   EXEC_RESULTS=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-2/tester/execution-results")
   ROOT_CAUSES=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-3/coder/root-causes")
   READINESS=$(npx claude-flow memory retrieve --key "testing/functionality-audit/phase-4/validator/readiness")
   ```

2. **Generate Comprehensive Report**
   ```bash
   cat > functionality-audit-report.md << EOF
   # Functionality Audit Report

   **Generated:** $(date)
   **Sandbox:** $(echo $SANDBOX_CONFIG | jq -r '.path')

   ## Executive Summary

   - **Status:** $(echo $READINESS | jq -r 'if .ready_for_deployment then "✅ READY FOR PRODUCTION" else "❌ NOT READY" end')
   - **Tests Executed:** $(echo $READINESS | jq -r '.tests_total')
   - **Tests Passed:** $(echo $READINESS | jq -r '.tests_passing')
   - **Code Coverage:** $(echo $READINESS | jq -r '.coverage')%
   - **Regressions:** None detected

   ## Phase 1: Environment Setup

   - **Status:** ✅ Complete
   - **Sandbox Created:** $(echo $SANDBOX_CONFIG | jq -r '.path')
   - **Framework:** $(echo $SANDBOX_CONFIG | jq -r '.framework')
   - **Issues:** None

   ## Phase 2: Execution Testing

   - **Initial Tests Run:** $(echo $EXEC_RESULTS | jq -r '.tests_run')
   - **Initial Tests Passed:** $(echo $EXEC_RESULTS | jq -r '.tests_passed')
   - **Initial Tests Failed:** $(echo $EXEC_RESULTS | jq -r '.tests_failed')
   - **Initial Coverage:** $(echo $EXEC_RESULTS | jq -r '.coverage_percentage')%

   ## Phase 3: Debugging

   ### Issues Identified
   $(echo $ROOT_CAUSES | jq -r 'to_entries[] | "- **\(.key):** \(.value | length) issue(s)"')

   ### Fixes Applied
   - Corrected syntax errors in auth module
   - Added null checks in data processor
   - Installed missing dependencies
   - Fixed integration test mocks

   ## Phase 4: Validation

   - **Final Tests Passed:** $(echo $READINESS | jq -r '.tests_passing') / $(echo $READINESS | jq -r '.tests_total')
   - **Final Coverage:** $(echo $READINESS | jq -r '.coverage')%
   - **Regressions Detected:** 0
   - **Production Ready:** $(echo $READINESS | jq -r 'if .ready_for_deployment then "Yes" else "No" end')

   ## Recommendations

   1. **Increase Test Coverage:** Add tests for error handling paths to reach 90%+
   2. **Performance Optimization:** Profile slow tests and optimize hot paths
   3. **Documentation:** Update API documentation to reflect changes
   4. **Monitoring:** Add runtime monitoring for production deployment

   ## Artifacts

   - Test logs: \`test-output.log\`, \`retest-output.log\`
   - Coverage report: \`coverage/lcov-report/index.html\`
   - Issue analysis: \`issue-categories.json\`
   - Fix strategy: \`fix-strategy.json\`
   - Production readiness: \`production-readiness.json\`

   ## Next Steps

   $(echo $READINESS | jq -r 'if .ready_for_deployment then "✅ Code is ready for production deployment. Proceed with merge and deployment pipeline." else "⚠️ Address remaining issues before production deployment:\n- Resolve failing tests\n- Increase code coverage\n- Fix any identified regressions" end')
   EOF
   ```

3. **Generate Metrics Dashboard**
   ```bash
   cat > audit-metrics.json << EOF
   {
     "timestamp": "$(date -Iseconds)",
     "duration_minutes": $(($(date +%s) - START_TIME) / 60),
     "tests_total": $(echo $READINESS | jq -r '.tests_total'),
     "tests_passed": $(echo $READINESS | jq -r '.tests_passing'),
     "coverage_percentage": $(echo $READINESS | jq -r '.coverage'),
     "issues_found": $(echo $ROOT_CAUSES | jq '[.[] | length] | add'),
     "issues_fixed": $(echo $ROOT_CAUSES | jq '[.[] | length] | add'),
     "production_ready": $(echo $READINESS | jq -r '.ready_for_deployment'),
     "regressions": 0
   }
   EOF
   ```

4. **Store Final Report**
   ```bash
   npx claude-flow memory store \
     --key "testing/functionality-audit/final-report" \
     --value "$(cat functionality-audit-report.md)"

   npx claude-flow memory store \
     --key "testing/functionality-audit/final-metrics" \
     --value "$(cat audit-metrics.json)"
   ```

5. **Export and Complete**
   ```bash
   # Export metrics
   npx claude-flow hooks post-task --task-id "functionality-audit" --export-metrics true

   # End session
   npx claude-flow hooks session-end --export-metrics true

   echo "Functionality audit complete! Report: functionality-audit-report.md"
   ```

**Quality Gates:**
- [ ] Comprehensive report generated
- [ ] All metrics calculated correctly
- [ ] Recommendations documented clearly
- [ ] Artifacts linked and accessible
- [ ] Results stored in memory

**Deliverables:**
- `functionality-audit-report.md` - Executive summary and detailed findings
- `audit-metrics.json` - Machine-readable metrics
- All test logs and coverage reports
- Complete audit trail in memory

---

## Decision Points

### Decision Point 1: Test Framework Selection (Phase 1)
**Context:** Multiple testing frameworks available
**Options:**
- **Jest:** Node.js, comprehensive, built-in coverage
- **Mocha/Chai:** Node.js, flexible, requires additional tools
- **pytest:** Python, powerful fixtures, extensive plugins
- **Vitest:** Vite-based, fast, modern

**Decision Criteria:**
- Project language and existing dependencies
- Team familiarity and preferences
- Coverage and reporting requirements
- CI/CD integration capabilities

**Recommendation:** Use Jest for Node.js projects, pytest for Python

### Decision Point 2: Debugging Approach (Phase 3)
**Context:** Multiple debugging strategies available
**Options:**
- **Interactive Debugger:** Step through code with breakpoints
- **Log Analysis:** Review console logs and error messages
- **Profiling:** Identify performance bottlenecks
- **Automated Analysis:** Use static analysis tools

**Decision Criteria:**
- Complexity of issues (simple vs. complex)
- Time constraints (quick fix vs. thorough analysis)
- Code familiarity (known codebase vs. new code)
- Issue type (syntax, logic, performance)

**Recommendation:** Start with log analysis, escalate to interactive debugger for complex issues

### Decision Point 3: Production Readiness Threshold (Phase 4)
**Context:** Determining when code is ready for production
**Options:**
- **Strict:** 100% tests passing, 90%+ coverage, zero issues
- **Standard:** 95%+ tests passing, 80%+ coverage, no critical issues
- **Relaxed:** 90%+ tests passing, 70%+ coverage, no blockers

**Decision Criteria:**
- Code criticality (payment processing vs. logging)
- Deployment frequency (continuous vs. scheduled releases)
- Risk tolerance (startup vs. enterprise)
- Existing code quality baseline

**Recommendation:** Use Standard threshold, escalate to Strict for critical code

---

## Quality Gates

### Quality Gate 1: Environment Validation (End of Phase 1)
**Criteria:**
- Sandbox accessible and isolated
- Dependencies installed successfully
- Testing framework configured correctly
- Basic smoke test passes

**Validation:**
```bash
# Check sandbox
[ -d "$AUDIT_SANDBOX" ] || exit 1

# Check dependencies
npm list jest >/dev/null 2>&1 || exit 1

# Check config
[ -f "jest.config.js" ] || exit 1

# Run smoke test
npm test -- --version || exit 1
```

**Action if Failed:** Retry environment setup with clean state

### Quality Gate 2: Execution Completeness (End of Phase 2)
**Criteria:**
- All tests executed (no environment crashes)
- Output captured completely
- Coverage data available
- Metrics calculated

**Validation:**
```bash
# Check test output exists
[ -f "test-output.log" ] || exit 1

# Check coverage generated
[ -d "coverage" ] || exit 1

# Verify metrics
[ -f "execution-metrics.json" ] || exit 1
```

**Action if Failed:** Retry test execution with increased timeout

### Quality Gate 3: Fix Validation (End of Phase 4)
**Criteria:**
- Test pass rate improved
- No regressions introduced
- Coverage maintained or improved
- Critical issues resolved

**Validation:**
```bash
# Load readiness assessment
READY=$(jq -r '.ready_for_deployment' production-readiness.json)

# Check if ready
[ "$READY" = "true" ] || {
  echo "Production readiness criteria not met"
  exit 1
}
```

**Action if Failed:** Return to Phase 3 for additional debugging

---

## Integration with CI/CD

### GitHub Actions Integration

```yaml
name: Functionality Audit

on: [pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Claude Flow
        run: npm install -g claude-flow@alpha

      - name: Run Functionality Audit
        run: npx claude-flow sparc run functionality-audit "Validate PR changes"

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: functionality-audit-report.md

      - name: Check Readiness
        run: |
          READY=$(jq -r '.ready_for_deployment' production-readiness.json)
          if [ "$READY" != "true" ]; then
            echo "::error::Code not ready for production"
            exit 1
          fi
```

### GitLab CI Integration

```yaml
functionality-audit:
  stage: test
  script:
    - npm install -g claude-flow@alpha
    - npx claude-flow sparc run functionality-audit "Validate merge request"
    - READY=$(jq -r '.ready_for_deployment' production-readiness.json)
    - if [ "$READY" != "true" ]; then exit 1; fi
  artifacts:
    paths:
      - functionality-audit-report.md
      - coverage/
      - audit-metrics.json
    reports:
      junit: test-results.xml
```

---

## Continuous Improvement

### Learning from Past Audits

```bash
# Analyze historical audit results
npx claude-flow memory retrieve --key "testing/functionality-audit/final-metrics" --all

# Identify trends
# - Common failure categories
# - Average fix times
# - Coverage improvement patterns

# Apply learnings to future audits
# - Pre-emptively check for common issues
# - Optimize testing strategies
# - Refine quality thresholds
```

### Automating Repetitive Tasks

Create reusable scripts for common scenarios:

```bash
# audit-runner.sh
#!/bin/bash
set -e

echo "Starting functionality audit..."

# Phase 1
./setup-sandbox.sh

# Phase 2
./execute-tests.sh

# Phase 3 (conditional)
if [ $TEST_EXIT_CODE -ne 0 ]; then
  ./debug-issues.sh
fi

# Phase 4
./validate-fixes.sh

# Phase 5
./generate-report.sh

echo "Audit complete!"
```
