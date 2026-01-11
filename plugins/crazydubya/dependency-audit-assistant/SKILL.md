---
name: dependency-audit-assistant
description: Reviews package dependencies for security vulnerabilities, outdated versions, and license compliance. Use when user asks about dependencies, security audits, or before releases.
allowed-tools: Read, Grep, Glob, Bash
---

# Dependency Audit Assistant

This skill helps audit project dependencies for security vulnerabilities, outdated packages, and license compliance issues.

## When to Use This Skill

- User requests a dependency audit or security check
- Before major releases or deployments
- User asks about outdated packages or vulnerabilities
- License compliance review needed
- User mentions "npm audit", "security", "dependencies", or "vulnerabilities"

## Instructions

### 1. Detect Package Manager

Identify which package manager(s) the project uses:

**JavaScript/Node.js:**
- npm: `package.json` + `package-lock.json`
- Yarn: `package.json` + `yarn.lock`
- pnpm: `package.json` + `pnpm-lock.yaml`

**Python:**
- pip: `requirements.txt` or `setup.py`
- Poetry: `pyproject.toml` + `poetry.lock`
- Pipenv: `Pipfile` + `Pipfile.lock`

**Ruby:**
- Bundler: `Gemfile` + `Gemfile.lock`

**Java:**
- Maven: `pom.xml`
- Gradle: `build.gradle` or `build.gradle.kts`

**Go:**
- Go modules: `go.mod` + `go.sum`

**Rust:**
- Cargo: `Cargo.toml` + `Cargo.lock`

**PHP:**
- Composer: `composer.json` + `composer.lock`

Use Glob to find these files.

### 2. Run Security Audit

Execute the appropriate audit command based on package manager:

**npm:** `npm audit --json` or `npm audit`
**Yarn:** `yarn audit --json` or `yarn audit`
**pnpm:** `pnpm audit --json`
**pip:** `pip-audit` or `safety check`
**Poetry:** `poetry check`
**Bundler:** `bundle audit check --update`
**Maven:** `mvn dependency:tree` + OWASP Dependency Check
**Go:** `go list -m all` + `govulncheck`
**Cargo:** `cargo audit`
**Composer:** `composer audit`

Parse the output to identify:
- Number of vulnerabilities by severity (critical, high, moderate, low)
- Affected packages and versions
- Available fixes (updates or patches)
- CVE identifiers

### 3. Check for Outdated Packages

Identify packages that have newer versions available:

**npm:** `npm outdated --json`
**Yarn:** `yarn outdated --json`
**pip:** `pip list --outdated`
**Poetry:** `poetry show --outdated`
**Bundler:** `bundle outdated`
**Cargo:** `cargo outdated`
**Go:** `go list -u -m all`

Categorize updates:
- **Patch updates** (1.0.0 → 1.0.1): Bug fixes, safe to update
- **Minor updates** (1.0.0 → 1.1.0): New features, usually safe
- **Major updates** (1.0.0 → 2.0.0): Breaking changes, needs testing

### 4. License Compliance Check

Review licenses of all dependencies:

**Steps:**
1. Extract licenses from package metadata
2. Identify license types (MIT, Apache-2.0, GPL, etc.)
3. Flag potentially problematic licenses (GPL, AGPL in commercial projects)
4. Check for unlicensed or unknown licenses
5. Reference the license compatibility matrix in `reference/licenses.md`

**Tools:**
- **npm:** `npx license-checker --json` or `npm-license-crawler`
- **Python:** `pip-licenses`
- **Ruby:** `license_finder`
- **Go:** `go-licenses`

**License categories:**
- **Permissive**: MIT, Apache-2.0, BSD - Usually safe
- **Weak copyleft**: LGPL, MPL - Requires review
- **Strong copyleft**: GPL, AGPL - May restrict commercial use
- **Unknown**: Missing or custom licenses - Needs investigation

### 5. Analyze Dependency Tree

Understand the dependency structure:

**Direct vs Transitive:**
- Direct: Listed in package.json/requirements.txt
- Transitive: Dependencies of dependencies

**Identify issues:**
- Duplicate packages at different versions
- Deep dependency trees (potential for conflicts)
- Abandoned packages (no updates in >2 years)
- High-risk transitive dependencies

**Commands:**
- **npm:** `npm ls --all`
- **Yarn:** `yarn why <package>`
- **pip:** `pipdeptree`
- **Maven:** `mvn dependency:tree`

### 6. Priority Vulnerabilities

Prioritize vulnerabilities based on:

**Severity levels:**
1. **Critical**: Remote code execution, privilege escalation
2. **High**: SQL injection, XSS, authentication bypass
3. **Moderate**: DoS, information disclosure
4. **Low**: Minor issues, edge cases

**Exploitability:**
- Known exploits in the wild
- PoC (Proof of Concept) available
- Requires special conditions

**Exposure:**
- Production dependencies vs dev dependencies
- Direct dependencies vs deep transitive dependencies
- Code paths actually used in the application

### 7. Generate Recommendations

For each issue found, provide:

**Vulnerabilities:**
```
Package: lodash@4.17.15
Severity: High
CVE: CVE-2020-8203
Issue: Prototype pollution
Recommendation: Upgrade to lodash@4.17.21 or higher
Command: npm install lodash@4.17.21
```

**Outdated packages:**
```
Package: react@16.14.0
Current: 16.14.0
Latest: 18.2.0
Type: Major update
Recommendation: Test thoroughly before upgrading (breaking changes)
Notes: Review migration guide at https://react.dev/blog/2022/03/08/react-18-upgrade-guide
```

**License issues:**
```
Package: some-gpl-library@1.0.0
License: GPL-3.0
Issue: GPL license may conflict with proprietary code
Recommendation: Find alternative with permissive license or consult legal
Alternatives: [list of similar packages with MIT/Apache licenses]
```

### 8. Update Strategy

Suggest an update approach:

**Safe updates (automated):**
- Patch updates with no breaking changes
- Security fixes for vulnerabilities
- Update: `npm update` or `npm audit fix`

**Careful updates (manual testing):**
- Minor version bumps
- Major updates to well-maintained packages
- Update individually and test

**Research needed:**
- Major breaking changes
- Abandoned packages (find alternatives)
- License conflicts

### 9. Generate Summary Report

Provide a comprehensive audit summary:

```
Dependency Audit Report
=======================

Overview:
- Total dependencies: 150 (120 direct, 30 transitive)
- Vulnerabilities: 5 (1 high, 3 moderate, 1 low)
- Outdated packages: 23
- License issues: 2

Security Vulnerabilities:
[List by severity with fix recommendations]

Outdated Packages:
[Categorized by update type: patch/minor/major]

License Compliance:
[List of licenses with any concerns]

Recommended Actions:
1. [Immediate] Fix high-severity vulnerabilities
2. [Soon] Update packages with moderate vulnerabilities
3. [Review] Address license compliance issues
4. [Optional] Update outdated packages to latest

Commands to run:
npm audit fix  # Fix vulnerabilities automatically
npm update     # Update to latest compatible versions
```

### 10. Continuous Monitoring

Suggest ongoing practices:

- **Automated audits**: Run in CI/CD pipeline
- **Dependabot/Renovate**: Auto-create PRs for updates
- **Regular reviews**: Monthly or quarterly audits
- **Security alerts**: Enable GitHub/GitLab security alerts
- **Lock files**: Commit lock files for reproducible builds

## Best Practices

1. **Fix vulnerabilities promptly**: Especially high/critical severity
2. **Test updates**: Even patch updates can cause issues
3. **Read changelogs**: Understand what changed before updating
4. **Use lock files**: Ensure consistent installations across environments
5. **Minimize dependencies**: Fewer deps = smaller attack surface
6. **Review new additions**: Audit before adding new dependencies
7. **Stay current**: Regular updates are easier than large jumps
8. **Document decisions**: Why certain packages are pinned or not updated

## Security Best Practices

- Never commit secrets in dependencies or env files
- Review dependency source code for popular/critical packages
- Use private registries for internal packages
- Enable 2FA on package registry accounts
- Use SRI (Subresource Integrity) for CDN resources
- Scan container images if using Docker

## Supporting Files

- `scripts/check-licenses.sh`: Extract and check license information
- `reference/licenses.md`: License compatibility matrix
- `reference/common-vulnerabilities.md`: Common vulnerability patterns

## Common Commands Reference

**npm:**
```bash
npm audit                 # Show vulnerabilities
npm audit fix            # Auto-fix vulnerabilities
npm audit fix --force    # Force major updates
npm outdated            # Check for outdated packages
npm update              # Update to latest compatible
```

**Yarn:**
```bash
yarn audit               # Show vulnerabilities
yarn upgrade-interactive # Interactive update
yarn outdated           # Check for outdated
```

**pip:**
```bash
pip-audit               # Audit vulnerabilities
pip list --outdated     # Check outdated
pip install --upgrade   # Update package
```

**Poetry:**
```bash
poetry check            # Check lock file
poetry show --outdated  # Show outdated
poetry update           # Update packages
```

**Cargo:**
```bash
cargo audit             # Audit vulnerabilities
cargo outdated          # Check outdated
cargo update            # Update packages
```
