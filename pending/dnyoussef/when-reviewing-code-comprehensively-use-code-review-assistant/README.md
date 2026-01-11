# Comprehensive Code Review Assistant

Multi-agent swarm for thorough PR reviews with specialized agents for security, performance, style, testing, and documentation.

## Quick Start

```bash
# Initialize review swarm
npx claude-flow@alpha swarm init --topology hierarchical

# Run comprehensive review on PR
npm run review:pr -- --pr-number 123

# View results
cat code-review-summary.json
```

## What This Skill Does

Orchestrates 4 specialized review agents:
- **Security Manager**: OWASP checks, vulnerability scanning
- **Performance Analyzer**: Bottleneck detection, efficiency analysis
- **Code Review Swarm**: Style conventions, linting
- **Tester**: Coverage analysis, test quality validation

## Usage

### CLI Command
```bash
# Full review
npx claude-flow@alpha task orchestrate \
  "Review PR #123 comprehensively" \
  --agents "security-manager,performance-analyzer,code-review-swarm,tester"

# Specific dimension
npm run review:security -- --pr 123
npm run review:performance -- --pr 123
npm run review:style -- --pr 123
npm run review:tests -- --pr 123
```

### CI/CD Integration
```yaml
# .github/workflows/review.yml
- name: Code Review
  run: npm run review:comprehensive
- name: Check Merge Readiness
  run: |
    SCORE=$(jq '.overall_score' code-review-summary.json)
    if [ "$SCORE" -lt 80 ]; then exit 1; fi
```

## Output Files

- `security-report.json` - Security vulnerabilities
- `performance-report.json` - Performance bottlenecks
- `style-report.json` - Style violations
- `coverage-summary.json` - Test coverage metrics
- `documentation-report.json` - Documentation gaps
- `code-review-summary.json` - Overall merge readiness
- `auto-fix-review-issues.sh` - Automated fix script

## Merge Readiness Score

```
Overall Score = (Security×0.3 + Performance×0.25 + Style×0.15 + Testing×0.2 + Docs×0.1)

Merge Approved: Score ≥ 80/100 AND zero blocking issues
```

## Configuration

```javascript
// code-review.config.js
module.exports = {
  merge_gate: {
    minimum_score: 80,
    allow_warnings: false,
    require_all_checks: true
  },
  thresholds: {
    security: { critical: 0, high: 0 },
    performance: { p0_bottlenecks: 0 },
    testing: { coverage_pct: 90 }
  }
};
```

## Best Practices

1. Run reviews on every PR
2. Apply auto-fixes first
3. Address blocking issues immediately
4. Track review scores over time
5. Customize thresholds per project

## Related Skills

- `production-readiness` - Pre-deployment validation
- `verification-quality` - Comprehensive quality checks
- `style-audit` - Detailed style analysis
