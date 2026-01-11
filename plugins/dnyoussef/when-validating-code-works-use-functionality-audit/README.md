# Functionality Audit

Quick start guide for validating code execution and functionality.

## Installation

```bash
# Ensure Claude Flow is installed
npm install -g claude-flow@alpha

# Verify installation
npx claude-flow --version

# Install testing dependencies in your project
npm install --save-dev jest @types/jest ts-node typescript
```

## Usage

### Basic Usage

```bash
# Run complete functionality audit
npx claude-flow sparc run functionality-audit "Validate authentication module"

# With specific test scope
npx claude-flow sparc run functionality-audit "Validate /api/users endpoints" --scope api

# Quick validation (skip full debugging)
npx claude-flow sparc run functionality-audit "Quick check payment processor" --quick
```

### Advanced Usage

```bash
# Audit with custom coverage threshold
npx claude-flow sparc run functionality-audit "Validate data layer" --coverage 90

# Parallel validation of multiple modules
npx claude-flow sparc concurrent functionality-audit modules.txt

# Integration with CI/CD
npx claude-flow sparc run functionality-audit "Pre-deployment validation" --production-mode

# Generate detailed report
npx claude-flow sparc run functionality-audit "Audit core services" --report detailed
```

## When to Use

Use this skill when:
- Code has been generated or significantly modified
- You need to verify functionality beyond static analysis
- Preparing for production deployment or PR merge
- Debugging reported issues or unexpected behavior
- Validating third-party integrations
- Running quality assurance workflows
- Testing after refactoring or framework migration

## Prerequisites

**Required:**
- Node.js 18+ or Python 3.9+
- Testing framework installed (Jest, Mocha, pytest, etc.)
- Code to validate accessible in filesystem

**Optional:**
- Docker for isolated sandbox environments
- CI/CD integration for automated validation
- Code coverage tools (istanbul, coverage.py)

## Quick Start Example

```bash
# 1. Initialize audit
npx claude-flow hooks pre-task --description "Audit login functionality"

# 2. Create sandbox
mkdir -p /tmp/audit-sandbox
cd /tmp/audit-sandbox

# 3. Run validation
npx claude-flow sparc run functionality-audit "Validate src/auth/login.js"

# 4. Review results
cat functionality-audit-report.md
```

## Output

The skill generates:
- `functionality-audit-report.md` - Comprehensive audit report
- `test-output.log` - Complete test execution logs
- `coverage/` - Code coverage reports
- `issue-analysis.json` - Categorized issues and fixes
- `production-readiness.json` - Deployment readiness assessment

## Related Skills

- **when-detecting-fake-code-use-theater-detection** - Pre-audit detection
- **when-reviewing-code-comprehensively-use-code-review-assistant** - Post-audit review
- **when-verifying-quality-use-verification-quality** - Comprehensive validation
- **when-auditing-code-style-use-style-audit** - Style compliance check

## Troubleshooting

**Issue: Sandbox creation fails**
```bash
# Solution: Clean and reinitialize
rm -rf /tmp/audit-sandbox
mkdir -p /tmp/audit-sandbox
npm install --force
```

**Issue: Tests timeout**
```bash
# Solution: Increase timeout in jest.config.js
module.exports = {
  testTimeout: 30000 // 30 seconds
};
```

**Issue: Coverage below threshold**
```bash
# Solution: Identify untested code
npx jest --coverage --verbose
# Add tests for uncovered lines
```

## Support

- Documentation: [Claude Flow Docs](https://github.com/ruvnet/claude-flow)
- Issues: [GitHub Issues](https://github.com/ruvnet/claude-flow/issues)
- Community: [Discussions](https://github.com/ruvnet/claude-flow/discussions)
