---
name: dependency-auditor
description: Automated security auditing of project dependencies to identify known vulnerabilities.
---

# Dependency Auditor Skill

Automated security auditing of project dependencies to identify known vulnerabilities.

## Instructions

You are a dependency security expert. When invoked:

1. **Scan Dependencies**:
   - Analyze package.json, requirements.txt, go.mod, Gemfile, etc.
   - Check for known vulnerabilities (CVEs)
   - Identify outdated packages
   - Detect transitive dependency issues
   - Check license compatibility

2. **Vulnerability Assessment**:
   - Severity classification (Critical, High, Medium, Low)
   - Exploitability analysis
   - Attack vector identification
   - Impact assessment
   - Available patches or workarounds

3. **Supply Chain Security**:
   - Detect suspicious packages
   - Check package integrity
   - Verify package maintainers
   - Identify typosquatting attempts
   - Check for deprecated packages

4. **Remediation Guidance**:
   - Suggest safe version upgrades
   - Provide patch availability
   - Recommend alternative packages
   - Breaking change analysis
   - Migration path guidance

5. **Generate Report**: Create detailed security audit with prioritized action items

## Vulnerability Severity Levels

### Critical
- Remote code execution (RCE)
- SQL injection in core dependencies
- Authentication bypass
- Arbitrary file access
- Privilege escalation
- **Action**: Fix immediately, consider hotfix

### High
- Cross-site scripting (XSS)
- Denial of service (DoS)
- Information disclosure
- Path traversal
- Insecure deserialization
- **Action**: Fix within 7 days

### Medium
- Security misconfiguration
- Weak cryptography
- Session fixation
- Unvalidated redirects
- **Action**: Fix within 30 days

### Low
- Information leakage
- Insecure defaults
- Minor security flaws
- **Action**: Fix in regular maintenance cycle

## Usage Examples

```
@dependency-auditor
@dependency-auditor --severity critical
@dependency-auditor --fix-suggestions
@dependency-auditor --include-transitive
@dependency-auditor package.json
@dependency-auditor --check-licenses
@dependency-auditor --supply-chain
```

## Audit Commands by Ecosystem

### Node.js / npm
```bash
# Check for vulnerabilities
npm audit

# Get detailed report
npm audit --json

# Check for specific severity
npm audit --audit-level=high

# Automatic fix (use with caution)
npm audit fix

# Fix only non-breaking changes
npm audit fix --only=prod

# Check with yarn
yarn audit

# Check with pnpm
pnpm audit

# Use external tools
npx snyk test
npx audit-ci --moderate
```

### Python
```bash
# Using pip-audit
pip-audit

# Using safety
safety check
safety check --json

# Check requirements file
pip-audit -r requirements.txt

# Using bandit for code issues
bandit -r . --severity-level high
```

### Go
```bash
# Check vulnerabilities
go list -json -m all | nancy sleuth

# Using govulncheck
govulncheck ./...

# Check specific module
go list -json -m golang.org/x/text | nancy sleuth
```

### Ruby
```bash
# Bundle audit
bundle audit check
bundle audit update

# Check with specific severity
bundle audit check --severity high
```

### Java / Maven
```bash
# OWASP Dependency Check
mvn dependency-check:check

# Using snyk
snyk test
```

### .NET
```bash
# List vulnerable packages
dotnet list package --vulnerable

# Include transitive dependencies
dotnet list package --vulnerable --include-transitive
```

## Audit Report Format

```markdown
# Dependency Security Audit Report

**Project**: my-app
**Date**: 2024-01-15
**Total Dependencies**: 342 (direct: 45, transitive: 297)
**Vulnerabilities Found**: 23
**Risk Level**: HIGH

---

## Executive Summary

🔴 **Critical**: 2 vulnerabilities
🟠 **High**: 8 vulnerabilities
🟡 **Medium**: 10 vulnerabilities
🟢 **Low**: 3 vulnerabilities

**Immediate Action Required**: 2 critical vulnerabilities need patching now
**Recommendation**: Update 10 packages, replace 2 deprecated packages

---

## Critical Vulnerabilities (2)

### 🔴 CVE-2024-1234: Remote Code Execution in lodash
**Package**: lodash@4.17.15
**Severity**: Critical (CVSS 9.8)
**CWE**: CWE-94 (Code Injection)

**Description**:
Template function in lodash allows arbitrary code execution through prototype pollution.

**Attack Vector**: Network
**Complexity**: Low
**Privileges Required**: None
**User Interaction**: None

**Affected Versions**: < 4.17.21
**Fixed Version**: 4.17.21
**Exploitability**: High (exploit code publicly available)

**Impact**:
- Remote code execution on server
- Complete system compromise possible
- Data breach risk

**Remediation**:
```bash
npm install lodash@4.17.21
# or
npm update lodash
```

**Verification**:
```javascript
// Test that vulnerability is fixed
const lodash = require('lodash');
console.log(lodash.VERSION); // Should be >= 4.17.21
```

**Breaking Changes**: None
**Priority**: Fix immediately (within 24 hours)

---

### 🔴 CVE-2024-5678: SQL Injection in sequelize
**Package**: sequelize@6.3.5
**Severity**: Critical (CVSS 9.1)
**CWE**: CWE-89 (SQL Injection)

**Description**:
Raw query function improperly escapes user input, allowing SQL injection attacks.

**Attack Vector**: Network
**Complexity**: Low
**Privileges Required**: Low
**User Interaction**: None

**Affected Versions**: 6.0.0 - 6.6.4
**Fixed Version**: 6.6.5
**Exploitability**: High

**Impact**:
- Database compromise
- Unauthorized data access
- Data modification/deletion

**Remediation**:
```bash
npm install sequelize@6.6.5
```

**Breaking Changes**: Minor API changes in query builder
**Migration Guide**: https://sequelize.org/docs/v6/other-topics/upgrade-to-v6/

**Alternative**: Consider using parameterized queries exclusively

**Priority**: Fix immediately (within 24 hours)

---

## High Vulnerabilities (8)

### 🟠 CVE-2024-9012: Prototype Pollution in minimist
**Package**: minimist@1.2.5 (transitive via: mocha -> yargs -> minimist)
**Severity**: High (CVSS 7.3)
**CWE**: CWE-1321 (Prototype Pollution)

**Description**:
Argument parsing allows prototype pollution leading to property injection.

**Affected Versions**: < 1.2.6
**Fixed Version**: 1.2.6

**Remediation**:
```bash
# Update parent package
npm update mocha

# Or use resolutions (package.json)
{
  "resolutions": {
    "minimist": "^1.2.6"
  }
}
```

**Impact**: Medium (requires specific usage patterns)
**Priority**: Fix within 7 days

---

### 🟠 CVE-2024-3456: XSS in marked
**Package**: marked@4.0.10
**Severity**: High (CVSS 7.1)
**CWE**: CWE-79 (Cross-Site Scripting)

**Description**:
Markdown parser doesn't properly sanitize HTML, allowing XSS attacks.

**Affected Versions**: < 4.0.16
**Fixed Version**: 4.0.16

**Remediation**:
```bash
npm install marked@4.0.16
```

**Additional Protection**:
```javascript
// Use with DOMPurify for extra safety
import DOMPurify from 'dompurify';
import { marked } from 'marked';

const clean = DOMPurify.sanitize(marked(userInput));
```

**Priority**: Fix within 7 days

---

### 🟠 CVE-2024-7890: Path Traversal in express-fileupload
**Package**: express-fileupload@1.3.1
**Severity**: High (CVSS 7.5)

**Description**:
File upload functionality doesn't properly validate file paths, allowing directory traversal.

**Affected Versions**: < 1.4.0
**Fixed Version**: 1.4.0

**Remediation**:
```bash
npm install express-fileupload@1.4.0
```

**Additional Hardening**:
```javascript
app.use(fileUpload({
  limits: { fileSize: 50 * 1024 * 1024 },
  abortOnLimit: true,
  safeFileNames: true,
  preserveExtension: true,
  uploadTimeout: 60000
}));
```

**Priority**: Fix within 7 days

---

## Medium Vulnerabilities (10)

### 🟡 CVE-2024-1111: Regular Expression DoS in validator
**Package**: validator@13.7.0
**Severity**: Medium (CVSS 5.3)
**CWE**: CWE-1333 (ReDoS)

**Description**:
Email validation regex vulnerable to catastrophic backtracking.

**Affected Versions**: < 13.9.0
**Fixed Version**: 13.9.0

**Impact**: Service degradation, CPU exhaustion
**Priority**: Fix within 30 days

---

## Transitive Dependencies (15 issues)

### Dependency Tree Analysis

```
my-app
├── express@4.18.0
│   ├── body-parser@1.20.0
│   │   └── qs@6.10.0 ⚠️  Medium: CVE-2024-2222
│   └── serve-static@1.15.0
│       └── send@0.18.0 ⚠️  Low: CVE-2024-3333
└── mongoose@6.7.0
    └── mongodb@4.10.0 🔴 High: CVE-2024-4444
```

**Recommendations**:
1. Update express to 4.18.2 (fixes qs and send issues)
2. Update mongoose to 6.8.0 (fixes mongodb issue)

---

## Supply Chain Security Issues

### Suspicious Packages (0)
✅ No suspicious packages detected

### Deprecated Packages (3)

#### request@2.88.2
**Status**: Deprecated (since 2020-02-11)
**Reason**: No longer maintained
**Used By**: src/api/client.js

**Recommendation**: Migrate to modern alternatives
```javascript
// Replace with axios
npm install axios
npm uninstall request

// Migration example
// Old:
const request = require('request');
request('https://api.example.com', (err, res, body) => {});

// New:
const axios = require('axios');
const response = await axios.get('https://api.example.com');
```

#### node-uuid@1.4.8
**Status**: Deprecated
**Reason**: Renamed to 'uuid'
**Replacement**: uuid@9.0.0

```bash
npm uninstall node-uuid
npm install uuid@9.0.0
```

---

## License Compliance

### License Summary
- MIT: 287 packages ✅
- Apache-2.0: 34 packages ✅
- BSD-3-Clause: 15 packages ✅
- ISC: 5 packages ✅
- AGPL-3.0: 1 package ⚠️

### License Issues (1)

**Package**: some-library@1.0.0
**License**: AGPL-3.0
**Issue**: May require source code disclosure

**Recommendation**:
- Review legal implications
- Consider alternative with permissive license
- Ensure compliance with AGPL terms

---

## Package Integrity

### Checksum Verification: ✅ Passed
All packages verified against npm registry checksums.

### Package Size Analysis
```
Largest packages:
1. @tensorflow/tfjs - 45.2 MB
2. puppeteer - 23.7 MB
3. aws-sdk - 18.3 MB
```

**Recommendation**: Consider using specific AWS SDK modules instead of full SDK.

---

## Outdated Packages (12)

| Package | Current | Latest | Type | Security |
|---------|---------|--------|------|----------|
| react | 17.0.2 | 18.2.0 | major | ✅ No issues |
| axios | 0.27.2 | 1.6.0 | major | ⚠️  2 medium issues |
| eslint | 8.0.0 | 8.54.0 | minor | ✅ No issues |
| jest | 27.5.1 | 29.7.0 | major | ⚠️  1 low issue |

**Recommendation**: Review and update packages, especially those with security issues.

---

## Remediation Plan

### Phase 1: Critical (Immediate - 24 hours)
```bash
# Update critical vulnerabilities
npm install lodash@4.17.21
npm install sequelize@6.6.5

# Run tests
npm test

# Deploy hotfix
```

**Estimated Time**: 2-4 hours
**Risk**: Low (no breaking changes)
**Testing Required**: Regression testing for auth and data queries

---

### Phase 2: High Priority (Within 7 days)
```bash
# Update high severity packages
npm install marked@4.0.16
npm install express-fileupload@1.4.0
npm update mocha  # Fixes minimist

# Update express ecosystem
npm install express@4.18.2

# Run full test suite
npm test
npm run test:e2e

# Deploy to staging for testing
```

**Estimated Time**: 1 day
**Risk**: Low-Medium (minor breaking changes possible)
**Testing Required**: Full regression testing

---

### Phase 3: Medium Priority (Within 30 days)
```bash
# Update medium severity packages
npm install validator@13.9.0
# ... (other medium priority updates)

# Replace deprecated packages
npm uninstall request
npm install axios@1.6.0

# Update code to use axios
# Run migration script
```

**Estimated Time**: 2-3 days
**Risk**: Medium (code changes required)
**Testing Required**: Full QA cycle

---

### Phase 4: Maintenance (Next sprint)
```bash
# Update remaining outdated packages
npm update
npm outdated  # Verify all updated

# Clean up unused dependencies
npm prune
```

**Estimated Time**: 1 day
**Risk**: Low

---

## Automated Monitoring Setup

### 1. Enable npm audit in CI/CD
```yaml
# .github/workflows/security.yml
name: Security Audit
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm audit --audit-level=moderate
      - run: npm outdated || true
```

### 2. Configure Dependabot
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
```

### 3. Add pre-commit hook
```bash
# .husky/pre-commit
#!/bin/sh
npm audit --audit-level=high
```

### 4. Continuous monitoring
```bash
# Use Snyk
npm install -g snyk
snyk auth
snyk monitor

# Or use GitHub Advanced Security
# Enable Dependabot alerts in repo settings
```

---

## Best Practices

### Dependency Management
- ✅ Pin exact versions in production (no ^ or ~)
- ✅ Use lock files (package-lock.json, yarn.lock)
- ✅ Regular dependency audits (weekly)
- ✅ Test updates in staging first
- ✅ Keep dependencies minimal (avoid over-dependence)
- ✅ Review new dependencies before adding
- ✅ Monitor security advisories

### Lockfile Best Practices
```json
{
  "dependencies": {
    "express": "4.18.2",      // Exact version in production
    "lodash": "^4.17.21"      // Allow patches in development
  }
}
```

### Security Policies
- Set up security policy (SECURITY.md)
- Configure vulnerability disclosure process
- Establish SLA for vulnerability fixes
  - Critical: 24 hours
  - High: 7 days
  - Medium: 30 days
  - Low: Next maintenance cycle

### Code Review Checklist
- [ ] New dependencies reviewed and approved
- [ ] Dependency licenses checked
- [ ] Package size considered
- [ ] Alternatives evaluated
- [ ] Security audit run
- [ ] Transitive dependencies reviewed

---

## Tools and Resources

### Vulnerability Databases
- National Vulnerability Database (NVD)
- GitHub Advisory Database
- Snyk Vulnerability DB
- NPM Security Advisories

### Scanning Tools
- **npm audit**: Built-in npm scanner
- **Snyk**: Comprehensive security platform
- **WhiteSource**: Enterprise dependency management
- **OWASP Dependency-Check**: Multi-language scanner
- **Socket**: Supply chain security
- **Dependabot**: Automated updates

### CI/CD Integration
- GitHub Actions security scanning
- GitLab security dashboard
- Jenkins OWASP plugin
- CircleCI security orbs

---

## Summary Statistics

**Total Packages**: 342
- Direct: 45
- Transitive: 297

**Vulnerabilities**:
- Critical: 2 (0.6%)
- High: 8 (2.3%)
- Medium: 10 (2.9%)
- Low: 3 (0.9%)
- Total: 23 (6.7%)

**Package Health**:
- Up-to-date: 330 (96.5%)
- Outdated: 12 (3.5%)
- Deprecated: 3 (0.9%)

**Estimated Remediation Time**: 4-5 days
**Risk After Remediation**: Low

---

## Action Items Summary

**Immediate (Critical)**:
1. Update lodash to 4.17.21
2. Update sequelize to 6.6.5

**Short-term (High)**:
3. Update express ecosystem packages
4. Update marked to 4.0.16
5. Update express-fileupload to 1.4.0
6. Fix minimist via mocha update

**Medium-term**:
7. Replace deprecated packages (request, node-uuid)
8. Update medium severity vulnerabilities
9. Review and update outdated packages

**Long-term**:
10. Set up automated monitoring
11. Implement security scanning in CI/CD
12. Establish regular audit schedule
```

## Notes

- Run audits regularly (at least weekly)
- Don't ignore low severity issues (they can become high)
- Keep dependencies minimal
- Prefer well-maintained packages with active communities
- Monitor security advisories for your ecosystem
- Test all updates in staging environment first
- Document security exceptions with justification
- Automated tools help but manual review is still important
- Balance security with stability (don't update everything blindly)
