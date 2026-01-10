# Code Style Audit with Auto-Fix

Comprehensive code style and conventions audit with automated fix capabilities for consistent code quality.

## Quick Start

```bash
# Run complete style audit with auto-fix
npm run style:audit

# View results
cat compliance-validation-report.md

# Check compliance score
jq '.overall_compliance_pct' style-audit-summary.json
```

## What This Skill Does

Executes 5-phase style audit:
1. **Scan Codebase**: Identify all style violations (ESLint, Prettier, TypeScript, naming)
2. **Compare to Standards**: Validate against project coding standards
3. **Report Violations**: Generate prioritized violation reports
4. **Auto-Fix Issues**: Apply automated corrections (76%+ auto-fixable)
5. **Validate Compliance**: Verify fixes and calculate compliance metrics

## Agents Used

- **code-analyzer**: Scanning, auto-fixing, compliance validation
- **reviewer**: Standards comparison, manual fix recommendations

## Output Files

- `eslint-report.json` - ESLint violations
- `prettier-violations.txt` - Formatting issues
- `typescript-strict-errors.txt` - Type errors
- `naming-violations.json` - Naming convention issues
- `standards-comparison-report.json` - Standards gap analysis
- `style-violations-report.md` - Comprehensive violation report
- `auto-fix-report.json` - Auto-fix results
- `compliance-validation-report.md` - Final compliance report
- `style-audit-summary.json` - Metrics summary

## Auto-Fix Capabilities

### ESLint (76.5% auto-fixable)
- Indentation (spaces/tabs)
- Quotes (single/double)
- Semicolons
- Trailing commas
- Unused imports
- Var → let/const conversion

### Prettier (100% auto-fixable)
- All formatting issues
- Line length
- Bracket spacing
- Arrow function parens

### Manual Fixes Required
- Unused variables
- Console statements
- Variable shadowing
- Type errors (TypeScript)

## Compliance Score

```
Overall Compliance = (
  ESLint Compliance × 0.50 +
  Prettier Compliance × 0.30 +
  TypeScript Compliance × 0.20
)

Passing: ≥90% compliance
```

## Usage

### CLI Commands
```bash
# Full audit with auto-fix
npm run style:audit

# Individual phases
npm run style:scan
npm run style:compare-standards
npm run style:report
npm run style:auto-fix
npm run style:validate

# Dry run (no changes)
npm run style:audit -- --dry-run
```

### CI/CD Integration
```yaml
- name: Style Audit
  run: npm run style:audit
- name: Check Compliance
  run: |
    COMPLIANCE=$(jq '.overall_compliance_pct' style-audit-summary.json)
    if [ "$COMPLIANCE" -lt 90 ]; then exit 1; fi
```

## Configuration

```javascript
// style-audit.config.js
module.exports = {
  compliance_threshold: 90,
  auto_fix: true,
  backup_before_fix: true,

  standards: {
    eslint: '.eslintrc.json',
    prettier: '.prettierrc.json',
    typescript: 'tsconfig.json'
  },

  naming_conventions: {
    files: 'kebab-case',
    classes: 'PascalCase',
    functions: 'camelCase',
    constants: 'UPPER_SNAKE_CASE'
  }
};
```

## Violation Priority

| Priority | Description | Examples |
|----------|-------------|----------|
| P0 (Critical) | Security risks, breaking issues | `no-eval`, `no-script-url` |
| P1 (High) | Potential bugs, code smells | `no-unused-vars`, `no-unreachable` |
| P2 (Medium) | Best practices | `prefer-const`, `eqeqeq` |
| P3 (Low) | Formatting, style | `indent`, `quotes` |

## Best Practices

1. Run style audit on every PR
2. Apply auto-fixes before manual review
3. Address P0/P1 violations immediately
4. Track compliance trends over time
5. Enforce style gates in CI/CD
6. Keep configuration standards documented

## Related Skills

- `code-review-assistant` - Comprehensive PR review
- `verification-quality` - Quality verification
- `production-readiness` - Deployment readiness
