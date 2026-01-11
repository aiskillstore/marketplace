# Security Analyzer Skill - Quick Start

Comprehensive security auditing across 5 vectors: static analysis, dynamic testing, dependency audit, secrets detection, and OWASP compliance.

## Installation

```bash
# Ensure Claude Flow is installed
npm install -g claude-flow@alpha

# Verify skill is available
npx claude-flow@alpha skills list | grep security-analyzer
```

## Quick Usage

### Run Full Security Audit
```bash
npx claude-flow@alpha skill run when-auditing-security-use-security-analyzer
```

### Run via Slash Command
```bash
/security-analyzer --type all --path .
```

### Run Specific Phases
```bash
# Static analysis only
/security-analyzer --type static

# Dynamic testing only
/security-analyzer --type dynamic

# Secrets detection only
/security-analyzer --type secrets
```

## What Gets Scanned

### 1. Static Code Analysis
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) vulnerabilities
- Path traversal vulnerabilities
- Insecure cryptography usage
- Dangerous functions (eval, innerHTML, etc.)

### 2. Dynamic Security Testing
- Authentication bypass attempts
- CSRF vulnerability testing
- Rate limiting verification
- Session management issues
- Authorization flaws

### 3. Dependency Security Audit
- Known CVEs in npm packages
- Outdated dependencies
- License compliance
- Malicious package detection
- SBOM (Software Bill of Materials) generation

### 4. Secrets Detection
- API keys (AWS, Google, Stripe, etc.)
- Hardcoded passwords
- Private keys
- Database connection strings
- JWT tokens
- High-entropy strings

### 5. OWASP Top 10 Compliance
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable Components
- A07: Authentication Failures
- A08: Software/Data Integrity
- A09: Logging/Monitoring Failures
- A10: Server-Side Request Forgery

## Output

### Terminal Output
Real-time progress with validation gates:
```
✅ Phase 1: Static Analysis - 3 issues found
⚠️  Phase 2: Dynamic Testing - 1 critical vulnerability
✅ Phase 3: Dependency Audit - No critical CVEs
🚨 Phase 4: Secrets Detection - 2 API keys exposed
✅ Phase 5: OWASP Compliance - 85% score
```

### Generated Reports
- `/tmp/SECURITY-AUDIT-REPORT.md` - Human-readable report
- `/tmp/security-audit-report.json` - Machine-readable results
- `/tmp/*-findings.txt` - Detailed findings per phase

## Common Use Cases

### Pre-Commit Security Check
```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
npx claude-flow@alpha skill run when-auditing-security-use-security-analyzer --quick
```

### CI/CD Integration
```yaml
# GitHub Actions
- name: Security Audit
  run: npx claude-flow@alpha skill run when-auditing-security-use-security-analyzer

- name: Upload Report
  uses: actions/upload-artifact@v3
  with:
    name: security-report
    path: /tmp/SECURITY-AUDIT-REPORT.md
```

### Scheduled Audits
```bash
# Weekly security scan
0 0 * * 0 cd /path/to/project && npx claude-flow@alpha skill run when-auditing-security-use-security-analyzer
```

### Vulnerability Triage
```bash
# Focus on critical issues only
/security-analyzer --severity critical --output /tmp/critical-only.json
```

## Configuration

Create `.security-analyzer.json` in project root:

```json
{
  "severity_threshold": "medium",
  "skip_phases": [],
  "frameworks": ["owasp", "cwe", "sans-25"],
  "exclude_patterns": [
    "test/**",
    "docs/**",
    "*.test.js"
  ],
  "custom_rules": {
    "max_function_complexity": 10,
    "require_auth_on_routes": true,
    "enforce_https": true
  }
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Critical vulnerabilities found |
| 2 | High-severity issues (warnings) |
| 3 | Configuration error |
| 4 | Scan incomplete |

## Quick Fixes

### Fix SQL Injection
```bash
# Find all SQL injection risks
grep -rn "\.query.*\+" --include="*.js" .

# Apply fix pattern
# Before: db.query("SELECT * FROM users WHERE id = " + userId)
# After:  db.query("SELECT * FROM users WHERE id = ?", [userId])
```

### Remove Exposed Secrets
```bash
# Find secrets
/security-analyzer --type secrets

# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/file" \
  --prune-empty --tag-name-filter cat -- --all
```

### Update Vulnerable Dependencies
```bash
# Auto-fix with npm
npm audit fix --force

# Manual review
npm audit
npm update <package>
```

## Memory Access

View scan results from memory:

```bash
# View static analysis results
npx claude-flow@alpha memory retrieve --key "swarm/security/static-analysis"

# View OWASP compliance
npx claude-flow@alpha memory retrieve --key "swarm/security/owasp-compliance"

# View final report
npx claude-flow@alpha memory retrieve --key "swarm/security/final-report"
```

## Agent Coordination

This skill uses 3 coordinated agents:

1. **security-manager**: Orchestrates scan phases, dependency audit, OWASP compliance
2. **code-analyzer**: Static analysis, secrets detection, pattern matching
3. **tester**: Dynamic security testing, fuzzing, runtime vulnerability detection

All agents communicate via Claude Flow hooks and shared memory.

## Troubleshooting

### "No findings detected" but you know there are issues
```bash
# Verify patterns are loaded
cat /tmp/secret-patterns.txt

# Run with verbose logging
npx claude-flow@alpha skill run when-auditing-security-use-security-analyzer --verbose
```

### Dynamic testing fails
```bash
# Ensure app is running
npm start &
sleep 5  # Wait for startup
/security-analyzer --type dynamic
```

### False positives
```bash
# Add to .security-analyzer.json
{
  "ignore_patterns": [
    "test/fixtures/*",
    "examples/*"
  ]
}
```

## Examples

### Example 1: New Project Setup
```bash
# Initialize project
npm init -y
npm install express helmet

# Run initial security audit
/security-analyzer --baseline

# Store baseline for future comparison
cp /tmp/security-audit-report.json .security-baseline.json
```

### Example 2: Pre-Release Audit
```bash
# Full audit before production deployment
/security-analyzer --type all --severity critical --strict

# Fail if any critical issues
if [ $? -ne 0 ]; then
  echo "❌ Security audit failed - deployment blocked"
  exit 1
fi
```

### Example 3: Continuous Monitoring
```bash
# Daily automated scan
#!/bin/bash
REPORT_DATE=$(date +%Y-%m-%d)
/security-analyzer --output /reports/security-$REPORT_DATE.json

# Send notifications on findings
if [ $(jq '.summary.critical' /reports/security-$REPORT_DATE.json) -gt 0 ]; then
  curl -X POST $SLACK_WEBHOOK -d '{"text":"🚨 Critical security issues found"}'
fi
```

## Best Practices

1. **Run early, run often**: Integrate into pre-commit hooks
2. **Automate**: Add to CI/CD pipeline
3. **Baseline**: Establish security baseline for your project
4. **Prioritize**: Fix critical issues first
5. **Monitor**: Set up alerts for new vulnerabilities
6. **Document**: Keep security decisions in version control
7. **Train**: Educate team on common vulnerabilities

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [National Vulnerability Database](https://nvd.nist.gov/)
- [Snyk Vulnerability Database](https://snyk.io/vuln/)

## Support

Issues? Check:
1. `/tmp/security-audit-report.json` for detailed diagnostics
2. Memory at `swarm/security/*` for intermediate results
3. [PROCESS.md](./PROCESS.md) for detailed workflow
4. [SKILL.md](./SKILL.md) for complete SOP
