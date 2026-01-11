# Code Review Assistant Process Walkthrough

## Overview

This process orchestrates 4 specialized agents for comprehensive PR review across 5 dimensions: security, performance, style, testing, and documentation.

---

## Phase 1: Security Review (15 minutes)

### Agent: security-manager

**Purpose**: Identify vulnerabilities, OWASP violations, and security misconfigurations.

### Steps

1. **Initialize Security Scan**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "security-manager" \
     --description "Security vulnerability scanning"
   ```

2. **Run Security Tools**
   ```bash
   # ESLint security rules
   npx eslint . --config .eslintrc-security.json --format json > security-report.json

   # Dependency vulnerabilities
   npm audit --json > npm-audit.json

   # Secret scanning
   npx gitleaks detect --report-path gitleaks-report.json
   ```

3. **Analyze Authentication/Authorization**
   - Check JWT validation
   - Verify password hashing (bcrypt/argon2)
   - Detect SQL injection patterns
   - Validate CSRF protection

4. **Generate Security Report**
   - Critical issues (merge blockers)
   - High priority issues
   - Medium/low issues
   - Auto-fix suggestions

5. **Store Findings**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "security-report.json" \
     --memory-key "swarm/security-manager/findings"
   ```

### Success Criteria
- Zero critical security issues
- All OWASP Top 10 checks pass
- No hardcoded secrets
- Authentication properly implemented

---

## Phase 2: Performance Review (20 minutes)

### Agent: performance-analyzer

**Purpose**: Detect bottlenecks, inefficient algorithms, and performance regressions.

### Steps

1. **Initialize Performance Analysis**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "performance-analyzer" \
     --description "Performance bottleneck analysis"
   ```

2. **Static Analysis**
   - Detect nested loops (O(n²) or worse)
   - Find blocking operations (sync file I/O)
   - Identify N+1 query patterns
   - Check memory leaks

3. **Runtime Profiling**
   ```bash
   # Performance benchmarks
   npm run test:perf -- --profile

   # Bundle analysis
   npx webpack-bundle-analyzer stats.json

   # Memory profiling
   node --inspect --expose-gc performance-test.js
   ```

4. **Bottleneck Detection**
   - Measure current latency
   - Calculate optimized latency
   - Estimate improvement factor
   - Provide fix recommendations

5. **Generate Performance Report**
   - P0/P1/P2 bottlenecks
   - Performance metrics vs targets
   - Optimization recommendations
   - Estimated impact

6. **Store Performance Data**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "performance-report.json" \
     --memory-key "swarm/performance-analyzer/metrics"
   ```

### Success Criteria
- API response time <200ms
- Memory usage <256MB
- No O(n²) algorithms
- Bundle size <1MB

---

## Phase 3: Style Review (10 minutes)

### Agent: code-review-swarm

**Purpose**: Verify code conventions, linting, and consistent formatting.

### Steps

1. **Initialize Style Check**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "code-review-swarm" \
     --description "Code style audit"
   ```

2. **Run Linting Tools**
   ```bash
   # ESLint
   npx eslint . --format json > eslint-report.json

   # Prettier
   npx prettier --check "**/*.{js,jsx,ts,tsx,json,css,md}" > prettier-report.txt

   # TypeScript
   npx tsc --noEmit > typescript-errors.txt
   ```

3. **Check Naming Conventions**
   - Classes: PascalCase
   - Functions: camelCase
   - Constants: UPPER_SNAKE_CASE
   - Files: kebab-case

4. **Verify Code Organization**
   - Max file length: 500 lines
   - Max function length: 50 lines
   - Max parameters: 4
   - Max nesting depth: 4

5. **Generate Style Report**
   - ESLint errors/warnings
   - Prettier violations
   - Naming convention issues
   - Auto-fix script

6. **Store Style Findings**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "style-report.json" \
     --memory-key "swarm/code-review-swarm/style"
   ```

### Success Criteria
- Zero ESLint errors
- All files Prettier formatted
- Naming conventions followed
- TypeScript types valid

---

## Phase 4: Test Coverage Review (15 minutes)

### Agent: tester

**Purpose**: Validate test coverage, test quality, and edge case handling.

### Steps

1. **Initialize Test Analysis**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "tester" \
     --description "Test coverage validation"
   ```

2. **Run Coverage Analysis**
   ```bash
   # Jest coverage
   npm run test:coverage -- --json --outputFile=coverage-summary.json

   # Find untested files
   find src -name "*.js" | while read file; do
     test_file="${file%.js}.test.js"
     [ ! -f "$test_file" ] && echo "$file" >> missing-tests.txt
   done
   ```

3. **Analyze Test Quality**
   - Assertions per test
   - Edge cases covered (null, undefined, empty)
   - Error handling tested
   - Async/await coverage
   - Proper mock usage

4. **Check Coverage Thresholds**
   - Statements: 90%
   - Branches: 85%
   - Functions: 90%
   - Lines: 90%

5. **Generate Coverage Report**
   - Coverage summary
   - Untested files (critical)
   - Missing test types
   - Test quality issues
   - Recommendations

6. **Store Test Data**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "coverage-summary.json" \
     --memory-key "swarm/tester/coverage"
   ```

### Success Criteria
- Statement coverage ≥90%
- Branch coverage ≥85%
- Function coverage ≥90%
- All critical paths tested

---

## Phase 5: Documentation Review (10 minutes)

### Agent: code-review-swarm

**Purpose**: Validate API docs, inline comments, and README completeness.

### Steps

1. **Initialize Documentation Check**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "code-review-swarm" \
     --description "Documentation audit"
   ```

2. **Check JSDoc/TypeDoc Coverage**
   ```bash
   # JSDoc coverage
   npx jsdoc-coverage-checker src/**/*.js --threshold 80 > jsdoc-report.json

   # Find undocumented functions
   grep -r "^function\|^const.*=.*=>" src/ | grep -v "\/\*\*" > undocumented-functions.txt
   ```

3. **Validate API Documentation**
   - OpenAPI/Swagger spec exists
   - All endpoints documented
   - Request/response schemas defined
   - Error responses documented
   - Authentication documented
   - Examples provided

4. **Check README Completeness**
   - Project description
   - Installation steps
   - Usage examples
   - API reference
   - Environment variables
   - Testing instructions
   - Contributing guide
   - License info

5. **Analyze Comment Quality**
   - Total comments
   - Useful comments (explain "why")
   - Redundant comments (obvious)
   - Outdated comments
   - Comment-to-code ratio (10-20%)

6. **Generate Documentation Report**
   - API documentation status
   - JSDoc coverage
   - Missing documentation
   - README improvements
   - Inline comment issues

7. **Store Documentation Findings**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "documentation-report.json" \
     --memory-key "swarm/code-review-swarm/documentation"
   ```

### Success Criteria
- JSDoc coverage ≥80%
- All public APIs documented
- README complete
- OpenAPI spec exists

---

## Final Integration: Merge Readiness Assessment

### Aggregate Results

**Calculate Overall Score:**
```javascript
const overallScore = (
  securityScore * 0.30 +
  performanceScore * 0.25 +
  styleScore * 0.15 +
  testCoverageScore * 0.20 +
  documentationScore * 0.10
);

const mergeApproved = (
  overallScore >= 80 &&
  blockingIssues.length === 0
);
```

### Generate Comprehensive Report

```markdown
## Merge Readiness Report

### Overall Score: 66.4/100 ⚠️ CHANGES REQUIRED

| Dimension | Score | Status | Blocking Issues |
|-----------|-------|--------|-----------------|
| Security | 65/100 | ⚠️ FAIL | 2 critical, 5 high |
| Performance | 58/100 | ⚠️ FAIL | 3 P0 bottlenecks |
| Style | 74/100 | ⚠️ WARN | 92 violations |
| Test Coverage | 73/100 | ⚠️ FAIL | 16.5% below target |
| Documentation | 62/100 | ⚠️ WARN | 38% undocumented |

### Blocking Issues (Must Fix Before Merge)
1. [SECURITY] SQL injection vulnerability (user.controller.js:45)
2. [SECURITY] Hardcoded API key (config/production.js:12)
3. [PERFORMANCE] N+1 query pattern (api/users.controller.js:67)
4. [TESTING] Critical files untested (auth/jwt-validator.js: 0%)

### Estimated Time to Merge-Ready: 4-6 hours
```

### Generate Auto-Fix Script

```bash
#!/bin/bash
# auto-fix-review-issues.sh

# Fix style violations
npx eslint . --fix
npx prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"

# Fix simple security issues
sed -i 's/API_KEY = ".*"/API_KEY = process.env.API_KEY/g' config/production.js

# Add missing test files
for file in $(cat missing-tests.txt); do
  test_file="${file%.js}.test.js"
  cat > "$test_file" << 'EOF'
describe('Test', () => {
  it('should be implemented', () => {
    expect(true).toBe(true);
  });
});
EOF
done
```

### Session Cleanup

```bash
# Export review session
npx claude-flow@alpha hooks session-end \
  --session-id "code-review-swarm-${PR_ID}" \
  --export-metrics true \
  --export-path "./code-review-summary.json"

# Notify completion
npx claude-flow@alpha hooks notify \
  --message "Code review complete: Score ${OVERALL_SCORE}/100" \
  --level "info"
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────┐
│           Code Review Assistant Workflow             │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │   Initialize Review Swarm     │
         │   (Hierarchical Topology)     │
         └───────────────┬───────────────┘
                         │
          ┌──────────────┴──────────────┐
          │  Parallel Agent Deployment  │
          └──────────────┬──────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐      ┌──────────────┐      ┌─────────┐
│Security │      │ Performance  │      │  Style  │
│Manager  │      │  Analyzer    │      │ Review  │
└────┬────┘      └──────┬───────┘      └────┬────┘
     │                  │                   │
     │  ┌───────────────┴───────────────┐  │
     │  │         Tester Agent          │  │
     │  │    (Coverage & Quality)       │  │
     │  └───────────────┬───────────────┘  │
     │                  │                   │
     └──────────────────┼───────────────────┘
                        │
            ┌───────────▼───────────┐
            │  Memory Coordination  │
            │  (Store All Findings) │
            └───────────┬───────────┘
                        │
            ┌───────────▼───────────┐
            │ Aggregate Results &   │
            │ Calculate Score       │
            └───────────┬───────────┘
                        │
            ┌───────────▼───────────┐
            │  Merge Readiness      │
            │  Decision (≥80/100)   │
            └───────────┬───────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
         ▼                             ▼
    ┌─────────┐                  ┌──────────┐
    │ APPROVE │                  │ REJECT & │
    │  MERGE  │                  │ GENERATE │
    │         │                  │ FIX PLAN │
    └─────────┘                  └──────────┘
```

---

## Real-World Example

### Scenario: E-commerce API PR Review

**PR Details:**
- 15 files changed
- 847 lines added, 234 deleted
- Features: Payment processing, user authentication

**Review Execution:**

```bash
# Initialize review
npx claude-flow@alpha swarm init --topology hierarchical --agents 4

# Run comprehensive review (parallel)
npm run review:comprehensive -- --pr 456
```

**Results After 12 Minutes:**

```json
{
  "overall_score": 68.2,
  "merge_approved": false,
  "security": {
    "score": 62,
    "critical_issues": 1,
    "high_issues": 3,
    "findings": [
      "SQL injection in payment-processor.js:78",
      "Hardcoded Stripe API key in config/payment.js:15",
      "Missing rate limiting on /api/auth/login"
    ]
  },
  "performance": {
    "score": 71,
    "p0_bottlenecks": 2,
    "findings": [
      "N+1 query loading user orders (estimated 27x improvement)",
      "Synchronous crypto operations blocking event loop"
    ]
  },
  "style": {
    "score": 85,
    "eslint_errors": 23,
    "auto_fixable": 19
  },
  "testing": {
    "score": 58,
    "coverage_pct": 58.3,
    "untested_critical_files": [
      "payment-processor.js",
      "auth/jwt-validator.js"
    ]
  },
  "documentation": {
    "score": 73,
    "api_docs_missing": 12
  },
  "estimated_fix_time_hours": 6
}
```

**Actions Taken:**

1. **Auto-fix applied** (style violations)
   ```bash
   npx eslint . --fix
   npx prettier --write "**/*.{js,ts,jsx,tsx}"
   ```

2. **Security fixes** (manual)
   - Moved Stripe key to environment variable
   - Implemented parameterized queries
   - Added rate limiting middleware

3. **Performance optimizations** (manual)
   - Converted N+1 to single JOIN query
   - Changed crypto to async operations

4. **Tests added** (manual)
   - Payment processor tests (edge cases)
   - JWT validation tests

**Re-review After Fixes:**

```json
{
  "overall_score": 87.4,
  "merge_approved": true,
  "blocking_issues": 0
}
```

**Outcome:** PR approved and merged after 6 hours of fixes.

---

## Best Practices

1. **Run Early**: Review on every PR, not just before merge
2. **Auto-Fix First**: Apply automated fixes before manual review
3. **Prioritize Blocking**: Address critical/high issues first
4. **Incremental Review**: Review commits incrementally
5. **Custom Thresholds**: Adjust scoring based on project criticality
6. **Track Metrics**: Monitor review scores over time
7. **Integrate CI/CD**: Automate reviews in pipeline

---

## Troubleshooting

### High False Positive Rate
```javascript
// Adjust security rules
{
  "rules": {
    "security/detect-object-injection": "warn",
    "security/detect-non-literal-regexp": "off"
  }
}
```

### Review Timeout on Large PRs
```bash
# Increase timeout
export REVIEW_TIMEOUT=1800

# Review specific paths
npm run review:pr -- --files "src/critical/**"
```

### Coverage Calculation Wrong
```bash
# Clear cache and regenerate
rm -rf coverage/ .nyc_output/
npm run test:coverage -- --clearCache
```

---

## Integration with CI/CD

### GitHub Actions
```yaml
name: Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Dependencies
        run: npm ci

      - name: Run Code Review Swarm
        run: |
          npx claude-flow@alpha swarm init --topology hierarchical
          npm run review:comprehensive

      - name: Check Merge Readiness
        run: |
          SCORE=$(jq '.overall_score' code-review-summary.json)
          if [ "$SCORE" -lt 80 ]; then
            echo "Review score $SCORE below threshold 80"
            exit 1
          fi

      - name: Post Review Comment
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const summary = JSON.parse(fs.readFileSync('code-review-summary.json'));
            const body = `## Code Review Results\n\n**Overall Score:** ${summary.overall_score}/100\n\n**Status:** ${summary.merge_approved ? '✅ APPROVED' : '⚠️ CHANGES REQUIRED'}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

---

## Related Skills

- `production-readiness` - Pre-deployment validation
- `verification-quality` - Quality verification
- `style-audit` - Detailed style analysis
- `smart-bug-fix` - Intelligent bug fixing
