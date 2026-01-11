# Quality Verification and Validation

Comprehensive quality verification through static analysis, dynamic testing, integration validation, and certification gates.

## Quick Start

```bash
# Run complete quality verification
npm run verify:quality

# View certification report
cat certification-report.md

# Check certification score
jq '.certification_score' quality-verification-summary.json
```

## What This Skill Does

Executes 5-phase quality verification:
1. **Static Analysis**: Code quality metrics, complexity, maintainability
2. **Dynamic Testing**: Unit, integration, E2E tests with coverage
3. **Integration Validation**: Service health, API contracts, data flow
4. **Certification**: Quality gates, compliance checks, sign-off
5. **Report Generation**: Comprehensive documentation and visualizations

## Agents Used

- **code-analyzer**: Static code analysis (SonarQube, ESLint)
- **tester**: Dynamic testing and integration validation
- **production-validator**: Certification and compliance

## Output Files

- `static-analysis-report.json` - Code quality metrics
- `dynamic-testing-report.json` - Test results and coverage
- `integration-validation-report.json` - Integration test results
- `certification-report.md` - Quality certification documentation
- `comprehensive-quality-report.md` - Full quality report
- `quality-report.pdf` - PDF version for stakeholders
- `quality-verification-summary.json` - Metrics summary

## Certification Score

```
Certification Score = (
  Static Analysis × 0.35 +
  Dynamic Testing × 0.45 +
  Integration Validation × 0.20
)

Approved: Score ≥ 80/100 AND all compliance checks pass
```

## Quality Gates

| Gate | Threshold | Weight |
|------|-----------|--------|
| Maintainability Index | ≥65 | 15% |
| Cyclomatic Complexity | <10 | 10% |
| Code Duplication | <5% | 10% |
| Test Pass Rate | ≥95% | 20% |
| Test Coverage | ≥90% | 15% |
| Branch Coverage | ≥85% | 10% |
| Service Health | 100% | 10% |
| API Contracts | 100% | 5% |
| Integration Tests | ≥95% | 5% |

## Usage

### CLI Commands
```bash
# Full verification
npm run verify:quality

# Individual phases
npm run verify:static
npm run verify:testing
npm run verify:integration
npm run verify:certification

# Generate report
npm run verify:report
```

### CI/CD Integration
```yaml
- name: Quality Verification
  run: npm run verify:quality
- name: Check Certification
  run: |
    SCORE=$(jq '.certification_score' quality-verification-summary.json)
    if [ "$SCORE" -lt 80 ]; then exit 1; fi
```

## Configuration

```javascript
// quality-verification.config.js
module.exports = {
  thresholds: {
    certification_score: 80,
    maintainability_index: 65,
    test_pass_rate: 95,
    coverage: 90
  },
  compliance: {
    security: true,
    accessibility: true,
    privacy: true,
    performance: true
  }
};
```

## Best Practices

1. Run verification on every build
2. Track quality trends over time
3. Address high-complexity code
4. Maintain >90% test coverage
5. Validate all compliance checks
6. Generate documentation for stakeholders

## Related Skills

- `code-review-assistant` - PR review
- `production-readiness` - Deployment validation
- `style-audit` - Code style enforcement
