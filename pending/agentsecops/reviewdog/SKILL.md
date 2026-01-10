---
name: reviewdog
description: >
  Automated code review and security linting integration for CI/CD pipelines using reviewdog.
  Aggregates findings from multiple security and quality tools (SAST, linters, formatters) into
  unified code review comments on pull requests. Use when: (1) Integrating security scanning
  into code review workflows, (2) Automating security feedback on pull requests,
  (3) Consolidating multiple tool outputs into actionable review comments, (4) Enforcing
  secure coding standards in CI/CD pipelines, (5) Providing inline security annotations
  during development.
version: 0.1.0
maintainer: asrour
category: secsdlc
tags: [code-review, ci-cd, automation, security-feedback, pull-request, linting, sast-integration]
frameworks: [OWASP, CWE]
dependencies:
  tools: [reviewdog, git]
  optional: [semgrep, bandit, hadolint, checkov, gitleaks, shellcheck, eslint]
references:
  - https://github.com/reviewdog/reviewdog
  - https://reviewdog.github.io/
---

# Reviewdog - Automated Security Code Review

## Overview

Reviewdog is an automated code review tool that integrates security scanning and linting results
into pull request review comments. It acts as a universal adapter between various security tools
(SAST scanners, linters, formatters) and code hosting platforms (GitHub, GitLab, Bitbucket),
enabling seamless security feedback during code review.

**Key Capabilities:**
- Aggregates findings from multiple security and quality tools
- Posts inline review comments on specific code lines
- Supports 40+ linters and security scanners out-of-the-box
- Integrates with GitHub Actions, GitLab CI, CircleCI, and other CI platforms
- Filters findings to show only new issues in diff (fail-on-diff mode)
- Supports custom rulesets and security policies

## Quick Start

### Basic reviewdog usage with a security scanner:

```bash
# Install reviewdog
go install github.com/reviewdog/reviewdog/cmd/reviewdog@latest

# Run a security scanner and pipe to reviewdog
bandit -r . -f json | reviewdog -f=bandit -reporter=github-pr-review

# Or use with Semgrep
semgrep --config=auto --json | reviewdog -f=semgrep -reporter=local
```

### GitHub Actions integration:

```yaml
- name: Run reviewdog
  uses: reviewdog/action-setup@v1
- name: Security scan with reviewdog
  env:
    REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    bandit -r . -f json | reviewdog -f=bandit -reporter=github-pr-review
```

## Core Workflow

### Step 1: Install reviewdog

Install reviewdog in your CI environment or locally:

```bash
# Via Go
go install github.com/reviewdog/reviewdog/cmd/reviewdog@latest

# Via Homebrew (macOS/Linux)
brew install reviewdog

# Via Docker
docker pull reviewdog/reviewdog:latest
```

### Step 2: Configure Security Tools

Set up the security scanners you want to integrate. Reviewdog supports multiple input formats:

**Supported Security Tools:**
- **SAST**: Semgrep, Bandit, ESLint Security, Brakeman
- **Secret Detection**: Gitleaks, TruffleHog, detect-secrets
- **IaC Security**: Checkov, tfsec, terrascan
- **Container Security**: Hadolint, Trivy, Dockle
- **General Linters**: ShellCheck, yamllint, markdownlint

### Step 3: Integrate into CI/CD Pipeline

Add reviewdog to your CI pipeline to automatically post security findings as review comments:

**GitHub Actions Example:**
```yaml
name: Security Review
on: [pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup reviewdog
        uses: reviewdog/action-setup@v1

      - name: Run Bandit SAST
        env:
          REVIEWDOG_GITHUB_API_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          pip install bandit
          bandit -r . -f json | \
            reviewdog -f=bandit \
                     -name="Bandit SAST" \
                     -reporter=github-pr-review \
                     -filter-mode=added \
                     -fail-on-error
```

**GitLab CI Example:**
```yaml
security_review:
  stage: test
  script:
    - pip install bandit reviewdog
    - bandit -r . -f json |
        reviewdog -f=bandit
                 -reporter=gitlab-mr-discussion
                 -filter-mode=diff_context
  only:
    - merge_requests
```

### Step 4: Configure Review Behavior

Customize reviewdog's behavior using flags:

```bash
# Filter to show only issues in changed lines
reviewdog -filter-mode=diff_context

# Filter to show only issues in added lines
reviewdog -filter-mode=added

# Fail the build if findings are present
reviewdog -fail-on-error

# Set severity threshold
reviewdog -level=warning
```

### Step 5: Review Security Findings

Reviewdog posts findings as inline comments on the pull request:

- **Inline annotations**: Security issues appear directly on affected code lines
- **Severity indicators**: Critical, High, Medium, Low severity levels
- **Remediation guidance**: Links to CWE/OWASP references when available
- **Diff-aware filtering**: Only shows new issues introduced in the PR

## Security Considerations

- **API Token Security**: Store GitHub/GitLab tokens in secrets management (GitHub Secrets, GitLab CI/CD variables)
  - Never commit tokens to version control
  - Use minimum required permissions (read/write on pull requests)
  - Rotate tokens regularly

- **Access Control**:
  - Configure reviewdog to run only on trusted branches
  - Use CODEOWNERS to require security team approval for reviewdog config changes
  - Restrict who can modify `.reviewdog.yml` configuration

- **Audit Logging**:
  - Log all security findings to SIEM or security monitoring platform
  - Track when findings are introduced and resolved
  - Monitor for bypassed security checks

- **Compliance**:
  - Maintains audit trail of security reviews (SOC2, ISO27001)
  - Enforces security policy compliance in code review
  - Supports compliance reporting through CI/CD artifacts

- **Safe Defaults**:
  - Use `fail-on-error` to block PRs with security findings
  - Enable `filter-mode=added` to catch new vulnerabilities
  - Configure severity thresholds appropriate to your risk tolerance

## Bundled Resources

### Scripts (`scripts/`)

- `setup_reviewdog.py` - Automated reviewdog installation and CI configuration generator
- `run_security_suite.sh` - Runs multiple security scanners through reviewdog

### References (`references/`)

- `supported_tools.md` - Complete list of supported security tools with configuration examples
- `reporter_formats.md` - Available output formats and reporter configurations
- `cwe_mapping.md` - Mapping of common tool findings to CWE categories

### Assets (`assets/`)

- `github_actions_template.yml` - GitHub Actions workflow for multi-tool security scanning
- `gitlab_ci_template.yml` - GitLab CI configuration for reviewdog integration
- `.reviewdog.yml` - Sample reviewdog configuration file
- `pre_commit_config.yaml` - Pre-commit hook integration

## Common Patterns

### Pattern 1: Multi-Tool Security Suite

Run multiple security tools and aggregate results in a single review:

```bash
#!/bin/bash
# Run comprehensive security scan

# Python security
bandit -r . -f json | reviewdog -f=bandit -name="Python SAST" -reporter=github-pr-review &

# Secrets detection
gitleaks detect --report-format json | reviewdog -f=gitleaks -name="Secret Scan" -reporter=github-pr-review &

# IaC security
checkov -d . -o json | reviewdog -f=checkov -name="IaC Security" -reporter=github-pr-review &

wait
```

### Pattern 2: Severity-Based Gating

Block PRs based on severity thresholds:

```yaml
- name: Critical findings - Block PR
  run: |
    semgrep --config=p/security-audit --severity=ERROR --json | \
      reviewdog -f=semgrep -level=error -fail-on-error -reporter=github-pr-review

- name: Medium findings - Comment only
  run: |
    semgrep --config=p/security-audit --severity=WARNING --json | \
      reviewdog -f=semgrep -level=warning -reporter=github-pr-review
```

### Pattern 3: Differential Security Scanning

Only flag new security issues introduced in the current PR:

```bash
# Only show findings in newly added code
reviewdog -filter-mode=added -fail-on-error

# Show findings in modified context (added + surrounding lines)
reviewdog -filter-mode=diff_context
```

### Pattern 4: Custom Security Rules

Integrate custom security policies using grep or custom parsers:

```bash
# Check for prohibited patterns
grep -nH -R "eval(" . --include="*.py" | \
  reviewdog -f=grep -name="Dangerous Functions" -reporter=github-pr-review

# Custom JSON parser
./custom_security_scanner.py --json | \
  reviewdog -f=rdjson -name="Custom Policy" -reporter=github-pr-review
```

## Integration Points

- **CI/CD Platforms**:
  - GitHub Actions (native action available)
  - GitLab CI/CD
  - CircleCI
  - Jenkins
  - Azure Pipelines
  - Bitbucket Pipelines

- **Security Tools**:
  - **SAST**: Semgrep, Bandit, ESLint, Brakeman, CodeQL
  - **Secrets**: Gitleaks, TruffleHog, detect-secrets
  - **IaC**: Checkov, tfsec, terrascan, kics
  - **Containers**: Hadolint, Trivy, Dockle

- **Code Hosting**:
  - GitHub (PR comments, check runs, annotations)
  - GitLab (MR discussions)
  - Bitbucket (inline comments)
  - Gerrit (review comments)

- **SDLC Integration**:
  - **Pre-commit hooks**: Fast local feedback before push
  - **PR/MR review**: Automated security review on code changes
  - **Trunk protection**: Block merges with security findings
  - **Security dashboard**: Aggregate findings for visibility

## Troubleshooting

### Issue: Reviewdog not posting comments

**Solution**:
- Verify GitHub token has correct permissions (`repo` scope for private repos, `public_repo` for public)
- Check CI environment has `REVIEWDOG_GITHUB_API_TOKEN` or `GITHUB_TOKEN` set
- Ensure repository settings allow PR comments from workflows
- Verify reviewdog is running in PR context (not on push to main)

### Issue: Too many false positives

**Solution**:
- Use `filter-mode=added` to only show new issues
- Configure tool-specific suppressions in `.reviewdog.yml`
- Adjust severity thresholds with `-level` flag
- Use baseline files to ignore existing issues

### Issue: Performance issues with large repositories

**Solution**:
- Run reviewdog only on changed files using `filter-mode=diff_context`
- Cache tool dependencies and databases in CI
- Run expensive scanners on scheduled jobs, lightweight ones on PR
- Use parallel execution for multiple tools

### Issue: Integration with custom security tools

**Solution**:
- Convert tool output to supported format (checkstyle, sarif, rdjson, rdjsonl)
- Use `-f=rdjson` for custom JSON output following reviewdog diagnostic format
- Create errorformat pattern for text-based outputs
- See `references/reporter_formats.md` for format specifications

## Advanced Configuration

### Custom reviewdog configuration (`.reviewdog.yml`)

```yaml
runner:
  bandit:
    cmd: bandit -r . -f json
    format: bandit
    name: Python Security
    level: warning

  semgrep:
    cmd: semgrep --config=auto --json
    format: semgrep
    name: Multi-language SAST
    level: error

  gitleaks:
    cmd: gitleaks detect --report-format json
    format: gitleaks
    name: Secret Detection
    level: error
```

### Integration with Security Frameworks

Map findings to OWASP Top 10 and CWE:

```bash
# Semgrep with OWASP ruleset
semgrep --config "p/owasp-top-ten" --json | \
  reviewdog -f=semgrep -name="OWASP Top 10" -reporter=github-pr-review

# Include CWE references in comments
reviewdog -f=semgrep -name="CWE Analysis" -reporter=github-pr-review
```

## References

- [Reviewdog Documentation](https://github.com/reviewdog/reviewdog)
- [Supported Tools and Formats](https://reviewdog.github.io/supported-tools)
- [GitHub Actions Integration](https://github.com/reviewdog/action-setup)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
