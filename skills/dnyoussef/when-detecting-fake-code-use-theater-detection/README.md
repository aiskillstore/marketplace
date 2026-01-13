# Theater Code Detection

Quick start guide for detecting non-functional "theater" code.

## Installation

```bash
# Install Claude Flow
npm install -g claude-flow@alpha

# Verify installation
npx claude-flow --version
```

## Usage

### Basic Usage

```bash
# Scan entire codebase for theater code
npx claude-flow sparc run theater-detection "Scan codebase for theater patterns"

# Scan specific directory
npx claude-flow sparc run theater-detection "Scan src/ directory" --path src/

# Quick scan (pattern detection only, skip execution)
npx claude-flow sparc run theater-detection "Quick theater scan" --quick
```

### Advanced Usage

```bash
# Scan with custom confidence threshold
npx claude-flow sparc run theater-detection "Scan with high confidence" --confidence 80

# Auto-fix simple issues (empty catches, etc.)
npx claude-flow sparc run theater-detection "Scan and auto-fix" --auto-fix

# Generate detailed report
npx claude-flow sparc run theater-detection "Full theater analysis" --report detailed

# Integration with CI/CD
npx claude-flow sparc run theater-detection "Pre-commit theater check" --fail-on-critical
```

## When to Use

Use this skill when:
- Reviewing AI-generated code before merging
- Detecting code that looks complete but doesn't work
- Pre-deployment quality gates for critical systems
- Auditing third-party or unfamiliar code
- Security reviews to identify fake security measures
- Code quality initiatives to eliminate technical debt

## Prerequisites

**Required:**
- Node.js 18+ or Python 3.9+
- Codebase accessible in filesystem
- Testing framework for execution validation

**Optional:**
- Docker for isolated execution
- CI/CD integration for automated detection
- Code coverage tools

## Quick Start Example

```bash
# 1. Initialize detection
cd /path/to/project
npx claude-flow hooks pre-task --description "Theater code detection"

# 2. Run scan
npx claude-flow sparc run theater-detection "Scan for theater code"

# 3. Review report
cat theater-detection-report.md

# 4. Apply fixes
# Manual review: See fix-guide.md for files requiring manual fixes
# Automated: Run with --auto-fix flag
```

## Output

The skill generates:
- `theater-detection-report.md` - Comprehensive findings report
- `theater-metrics.json` - Machine-readable metrics
- `theater-analysis.json` - Detailed analysis with confidence scores
- `theater-categories.json` - Issues by severity (critical/high/medium/low)
- `execution-results.json` - Execution validation results
- `fix-guide.md` - Manual fix instructions

## Common Theater Patterns Detected

1. **Empty Error Handlers**
   ```javascript
   try { ... } catch (e) {} // Error swallowed
   ```

2. **No-Op Functions**
   ```javascript
   function validate() { return true; } // Always passes
   ```

3. **Always-Pass Tests**
   ```javascript
   test('works', () => expect(true).toBe(true)); // Meaningless
   ```

4. **Trivial Returns**
   ```javascript
   function process(data) { return null; } // No processing
   ```

5. **Mock Code in Production**
   ```javascript
   import { mockAuth } from 'test-utils'; // Wrong environment
   ```

## Related Skills

- **when-validating-code-works-use-functionality-audit** - Validate fixes actually work
- **when-reviewing-code-comprehensively-use-code-review-assistant** - Full code review
- **when-verifying-quality-use-verification-quality** - Comprehensive quality validation
- **when-auditing-code-style-use-style-audit** - Code style compliance

## Troubleshooting

**Issue: Too many false positives**
```bash
# Solution: Increase confidence threshold
npx claude-flow sparc run theater-detection "Scan" --confidence 70
```

**Issue: Theater code not detected**
```bash
# Solution: Lower threshold and enable execution validation
npx claude-flow sparc run theater-detection "Deep scan" --confidence 30 --execute-all
```

**Issue: Execution validation fails**
```bash
# Solution: Run in isolated sandbox
docker run -it --rm -v $(pwd):/workspace node:18 \
  npx claude-flow sparc run theater-detection "Scan"
```

## Support

- Documentation: [Claude Flow Docs](https://github.com/ruvnet/claude-flow)
- Issues: [GitHub Issues](https://github.com/ruvnet/claude-flow/issues)
- Community: [Discussions](https://github.com/ruvnet/claude-flow/discussions)
