# Code Style Audit Process Walkthrough

## Overview

This process executes comprehensive code style audit across 5 phases: scan codebase, compare to standards, report violations, auto-fix issues, and validate compliance.

---

## Phase 1: Scan Codebase (8 minutes)

### Agent: code-analyzer

**Purpose**: Identify all style violations, formatting issues, and convention inconsistencies.

### Steps

1. **Initialize Style Scan**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "code-analyzer" \
     --description "Comprehensive code style scanning"
   ```

2. **Run ESLint Scan**
   ```bash
   # Complete ESLint scan
   npx eslint . --ext .js,.jsx,.ts,.tsx --format json > eslint-report.json

   # Identify auto-fixable issues
   npx eslint . --ext .js,.jsx,.ts,.tsx --format json --fix-dry-run > eslint-fixable-report.json
   ```

3. **Run Prettier Check**
   ```bash
   # Check formatting violations
   npx prettier --check "**/*.{js,jsx,ts,tsx,json,css,md}" --list-different > prettier-violations.txt
   ```

4. **Run TypeScript Validation**
   ```bash
   # Strict type checking
   npx tsc --noEmit --strict > typescript-strict-errors.txt

   # Check for any types
   grep -r ": any" src/ --include="*.ts" --include="*.tsx" > any-types.txt
   ```

5. **Analyze Naming Conventions**
   - Files: kebab-case (user-service.js)
   - Classes: PascalCase (UserService)
   - Functions: camelCase (getUserById)
   - Constants: UPPER_SNAKE_CASE (MAX_RETRIES)
   - Components: PascalCase (LoginForm)

6. **Check Code Organization**
   - Max file length: 500 lines
   - Max function length: 50 lines
   - Max parameters: 4
   - Max nesting depth: 4

7. **Generate Scan Report**
   ```markdown
   ## Scan Results
   - ESLint violations: 247 (189 auto-fixable)
   - Prettier violations: 147 files
   - TypeScript issues: 67
   - Naming violations: 89
   - Organization issues: 56
   ```

8. **Store Scan Results**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "style-scan-report.json" \
     --memory-key "swarm/code-analyzer/scan-results"
   ```

### Success Criteria
- Complete codebase scanned
- All violation types identified
- Auto-fixable issues flagged
- Report generated

---

## Phase 2: Compare to Standards (5 minutes)

### Agent: reviewer

**Purpose**: Compare violations against project coding standards and best practices.

### Steps

1. **Initialize Standards Comparison**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "reviewer" \
     --description "Compare violations to coding standards"
   ```

2. **Load Project Standards**
   - ESLint config (.eslintrc.json)
   - Prettier config (.prettierrc.json)
   - TypeScript config (tsconfig.json)
   - Custom naming conventions (docs/coding-standards.md)

3. **Compare ESLint Configuration**
   - Configured rules: 178 / 247 (72.1%)
   - Base standard: Airbnb
   - Missing critical rules: 7
   - Conflicting rules: 3
   - Disabled important rules: 5

4. **Compare Prettier Configuration**
   - Configuration completeness: 88.9%
   - Differences from recommended:
     - singleQuote: false → true
     - printWidth: 80 → 100

5. **Assess TypeScript Strictness**
   - Strict mode: Disabled
   - Individual strict checks: 3/7 enabled (42.9%)
   - Recommendations: Enable "strict": true

6. **Generate Comparison Report**
   ```markdown
   ## Standards Comparison
   - ESLint compliance: 72.1%
   - Prettier compliance: 88.9%
   - TypeScript strictness: 42.9%
   - Naming conventions documented: Yes
   ```

7. **Store Comparison Results**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "standards-comparison-report.json" \
     --memory-key "swarm/reviewer/standards-comparison"
   ```

### Success Criteria
- Standards documented
- Comparison complete
- Gaps identified
- Recommendations generated

---

## Phase 3: Report Violations (5 minutes)

### Agent: code-analyzer

**Purpose**: Generate comprehensive violation reports with prioritization and fix recommendations.

### Steps

1. **Initialize Violation Reporting**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "code-analyzer" \
     --description "Generate violation reports"
   ```

2. **Prioritize Violations**
   - P0 (Critical): 0 - Security risks, breaking issues
   - P1 (High): 34 - Potential bugs, code smells
   - P2 (Medium): 73 - Best practices
   - P3 (Low): 140 - Formatting, style

3. **Categorize by File**
   ```
   Top 5 Worst Files:
   1. src/api/order-processor.js: 45 violations
   2. src/utils/data-transformer.js: 38 violations
   3. src/api/user-controller.js: 32 violations
   4. src/services/payment.js: 28 violations
   5. src/utils/validator.js: 24 violations
   ```

4. **Generate Fix Recommendations**
   - Auto-fixable: 189 (76.5%)
   - Semi-auto-fixable: 23 (9.3%)
   - Manual fix required: 35 (14.2%)

5. **Create Violation Report**
   ```markdown
   ## Violations Report

   ### Top 10 Rules Violated
   1. indent: 67 (P3, auto-fixable)
   2. no-unused-vars: 34 (P1, manual)
   3. prefer-const: 28 (P2, auto-fixable)
   4. no-console: 23 (P1, manual)
   5. quotes: 19 (P3, auto-fixable)

   ### Auto-Fix Command
   ```bash
   npx eslint . --fix
   npx prettier --write "**/*.{js,ts,jsx,tsx}"
   ```
   ```

6. **Export Multi-Format Reports**
   - JSON (for CI/CD)
   - Markdown (for documentation)
   - HTML (for viewing)
   - CSV (for analysis)

7. **Store Violation Reports**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "style-violations-report.json" \
     --memory-key "swarm/code-analyzer/violations-report"
   ```

### Success Criteria
- All violations reported
- Violations prioritized
- Fix recommendations generated
- Multi-format exports created

---

## Phase 4: Auto-Fix Issues (5 minutes)

### Agent: code-analyzer

**Purpose**: Apply automated fixes for style violations safely.

### Steps

1. **Initialize Auto-Fix**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "code-analyzer" \
     --description "Apply automated style fixes"
   ```

2. **Create Backup**
   ```bash
   # Backup before applying fixes
   BACKUP_DIR="style-audit-backup-$(date +%Y%m%d-%H%M%S)"
   git diff --name-only | xargs -I {} cp --parents {} "$BACKUP_DIR/"
   ```

3. **Apply ESLint Auto-Fixes**
   ```bash
   # Fix all auto-fixable issues
   npx eslint . --fix --ext .js,.jsx,.ts,.tsx

   # Count fixed issues
   FIXED_COUNT=$(jq '[.[] | .messages | .[] | select(.fix)] | length' eslint-fix-results.json)
   echo "ESLint fixed: $FIXED_COUNT issues"
   ```

4. **Apply Prettier Formatting**
   ```bash
   # Format all files
   npx prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"

   # Count formatted files
   FORMATTED_COUNT=$(grep -c "✅" prettier-fix-log.txt)
   echo "Prettier formatted: $FORMATTED_COUNT files"
   ```

5. **Apply TypeScript Fixes**
   ```bash
   # Limited TypeScript auto-fixes
   # Most require manual intervention
   ```

6. **Apply Safe Naming Fixes**
   ```javascript
   // Only apply if no breaking changes
   // File renames with reference updates
   ```

7. **Verify Fixes**
   ```bash
   # Run linting again
   npx eslint . --format json > eslint-post-fix.json

   # Run tests
   npm test
   ```

8. **Generate Fix Report**
   ```markdown
   ## Auto-Fix Results
   - ESLint fixes: 189
   - Prettier formatting: 147 files
   - Remaining manual: 58
   - Tests: All passing ✅
   ```

9. **Store Fix Results**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "auto-fix-report.json" \
     --memory-key "swarm/code-analyzer/auto-fix-results"
   ```

### Success Criteria
- Backup created
- Auto-fixes applied
- Tests pass
- No regressions

---

## Phase 5: Validate Compliance (2 minutes)

### Agent: reviewer

**Purpose**: Verify fixes and confirm adherence to coding standards.

### Steps

1. **Initialize Compliance Validation**
   ```bash
   npx claude-flow@alpha hooks pre-task \
     --agent-id "reviewer" \
     --description "Validate style compliance"
   ```

2. **Run Comprehensive Linting**
   ```bash
   # ESLint validation
   npx eslint . --ext .js,.jsx,.ts,.tsx --max-warnings 0

   # Prettier validation
   npx prettier --check "**/*.{js,jsx,ts,tsx,json,css,md}"

   # TypeScript validation
   npx tsc --noEmit --strict
   ```

3. **Calculate Compliance Metrics**
   ```
   ESLint Compliance: 95.8%
   Prettier Compliance: 100%
   TypeScript Compliance: 76.4%
   Naming Conventions: 89.2%

   Overall Compliance: 91.2% ✅
   ```

4. **Run Test Suite**
   ```bash
   # Verify no regressions
   npm run test:all -- --coverage
   ```

5. **Validate Build**
   ```bash
   # Ensure project builds
   npm run build
   ```

6. **Generate Compliance Report**
   ```markdown
   ## Compliance Validation

   ### Overall: 91.2% ✅ (Threshold: 90%)

   ### By Category
   - ESLint: 95.8% ✅
   - Prettier: 100% ✅
   - TypeScript: 76.4% ⚠️
   - Naming: 89.2% ⚠️

   ### Test Results
   - Unit: 342/342 ✅
   - Integration: 89/89 ✅
   - E2E: 42/42 ✅

   ### Build: ✅ Success
   ```

7. **Store Compliance Results**
   ```bash
   npx claude-flow@alpha hooks post-edit \
     --file "compliance-validation-report.json" \
     --memory-key "swarm/reviewer/compliance-validation"
   ```

8. **Commit Fixed Changes**
   ```bash
   git add .
   git commit -m "style: Apply automated style fixes

   - ESLint auto-fixes: 189 issues
   - Prettier formatting: 147 files
   - Remaining manual: 58 issues
   - Compliance: 91.2%"
   ```

### Success Criteria
- Overall compliance ≥90%
- All tests passing
- Build successful
- No regressions

---

## Final Session Cleanup

```bash
# Export audit session
npx claude-flow@alpha hooks session-end \
  --session-id "style-audit-${AUDIT_ID}" \
  --export-metrics true \
  --export-path "./style-audit-summary.json"

# Notify completion
npx claude-flow@alpha hooks notify \
  --message "Style audit complete: ${COMPLIANCE_PCT}% compliance"
```

---

## Workflow Diagram

```
┌─────────────────────────────────┐
│   Code Style Audit Workflow     │
└─────────────────────────────────┘
              │
   ┌──────────┴──────────┐
   │  Phase 1: Scan      │
   │  Codebase           │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  ESLint             │
   │  Prettier           │
   │  TypeScript         │
   │  Naming             │
   │  Organization       │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Phase 2: Compare   │
   │  to Standards       │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Gap Analysis       │
   │  Recommendations    │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Phase 3: Report    │
   │  Violations         │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Prioritize (P0-P3) │
   │  Categorize by File │
   │  Fix Recommendations│
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Phase 4: Auto-Fix  │
   │  Issues             │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Backup             │
   │  ESLint --fix       │
   │  Prettier --write   │
   │  Verify & Test      │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Phase 5: Validate  │
   │  Compliance         │
   └──────────┬──────────┘
              │
   ┌──────────▼──────────┐
   │  Calculate Metrics  │
   │  Run Tests          │
   │  Validate Build     │
   └──────────┬──────────┘
              │
        ┌─────┴─────┐
        │           │
        ▼           ▼
  ┌─────────┐  ┌─────────┐
  │ ≥90%    │  │ <90%    │
  │ PASS ✅ │  │ FAIL ⚠️ │
  └─────────┘  └─────────┘
```

---

## Real-World Example

### Scenario: Legacy Codebase Style Cleanup

**Codebase Details:**
- 247 JavaScript/TypeScript files
- 45,000 lines of code
- No consistent style enforcement

**Audit Execution:**

```bash
npm run style:audit
```

**Results After 25 Minutes:**

```json
{
  "total_violations_found": 247,
  "violations_auto_fixed": 189,
  "violations_remaining": 58,
  "compliance_before": 61.3,
  "compliance_after": 91.2,
  "improvement": 29.9,
  "auto_fix_success_rate": 76.5
}
```

**Breakdown:**
- ESLint fixes: 189 (indent, quotes, semi, prefer-const, etc.)
- Prettier formatting: 147 files
- Manual fixes needed: 58 (no-unused-vars, no-console)
- Tests: All passing ✅
- Build: Success ✅

**Outcome:** Style compliance improved from 61.3% to 91.2% with zero regressions.

---

## Best Practices

1. **Run Regularly**: Schedule weekly style audits
2. **Auto-Fix First**: Apply automated fixes before manual review
3. **Prioritize P0/P1**: Address high-priority violations immediately
4. **Track Trends**: Monitor compliance over time
5. **Enforce in CI**: Block merges below compliance threshold
6. **Document Standards**: Keep coding standards up-to-date
7. **Educate Team**: Share style guide with all developers

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Style Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Dependencies
        run: npm ci

      - name: Run Style Audit
        run: npm run style:audit

      - name: Check Compliance
        run: |
          COMPLIANCE=$(jq '.overall_compliance_pct' style-audit-summary.json)
          echo "Style Compliance: $COMPLIANCE%"
          if [ "$COMPLIANCE" -lt 90 ]; then
            echo "Style compliance below 90% threshold"
            exit 1
          fi

      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: style-audit-reports
          path: |
            compliance-validation-report.md
            style-violations-report.md

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const summary = JSON.parse(fs.readFileSync('style-audit-summary.json'));
            const body = `## Style Audit Results\n\n**Compliance:** ${summary.overall_compliance_pct}%\n**Violations Fixed:** ${summary.violations_auto_fixed}\n**Remaining:** ${summary.violations_remaining}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

---

## Related Skills

- `code-review-assistant` - Comprehensive PR review
- `verification-quality` - Quality verification
- `production-readiness` - Deployment validation
