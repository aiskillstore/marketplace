# Supported Security Tools for Reviewdog

This reference documents security tools that integrate with reviewdog, their configuration, and usage patterns.

## Table of Contents

- [SAST Tools](#sast-tools)
- [Secret Detection](#secret-detection)
- [Infrastructure as Code](#infrastructure-as-code)
- [Container Security](#container-security)
- [Linters and Formatters](#linters-and-formatters)

## SAST Tools

### Semgrep

**Description**: Multi-language static analysis for finding bugs and enforcing secure coding standards.

**Installation**:
```bash
pip install semgrep
```

**Reviewdog Integration**:
```bash
semgrep --config=auto --json | reviewdog -f=semgrep -reporter=github-pr-review
```

**Custom Rules**:
```bash
# OWASP Top 10
semgrep --config "p/owasp-top-ten" --json | reviewdog -f=semgrep

# Security audit
semgrep --config "p/security-audit" --json | reviewdog -f=semgrep

# Custom rules
semgrep --config ./custom-rules.yml --json | reviewdog -f=semgrep
```

**CWE Coverage**: CWE-20, CWE-22, CWE-78, CWE-79, CWE-89, CWE-94, CWE-611, CWE-798

---

### Bandit

**Description**: Python security linter for finding common security issues.

**Installation**:
```bash
pip install bandit
```

**Reviewdog Integration**:
```bash
bandit -r . -f json | reviewdog -f=bandit -reporter=github-pr-review
```

**Configuration (.bandit)**:
```yaml
exclude_dirs:
  - /test
  - /tests
  - /.venv

tests:
  - B201  # Flask debug mode
  - B301  # Pickle usage
  - B601  # Shell injection
  - B602  # Subprocess with shell=True
```

**CWE Coverage**: CWE-78, CWE-79, CWE-89, CWE-259, CWE-327, CWE-338, CWE-502

---

### ESLint (with security plugins)

**Description**: JavaScript/TypeScript linter with security-focused plugins.

**Installation**:
```bash
npm install -D eslint eslint-plugin-security eslint-plugin-no-secrets
```

**Reviewdog Integration**:
```bash
eslint . --format=checkstyle | reviewdog -f=checkstyle -reporter=github-pr-review
```

**Configuration (.eslintrc.json)**:
```json
{
  "plugins": ["security", "no-secrets"],
  "extends": ["plugin:security/recommended"],
  "rules": {
    "no-eval": "error",
    "security/detect-object-injection": "warn",
    "security/detect-non-literal-regexp": "warn"
  }
}
```

**CWE Coverage**: CWE-79, CWE-94, CWE-798, CWE-1004

---

## Secret Detection

### Gitleaks

**Description**: SAST tool for detecting hardcoded secrets like passwords, API keys, and tokens.

**Installation**:
```bash
# Via Homebrew
brew install gitleaks

# Via Docker
docker pull zricethezav/gitleaks:latest
```

**Reviewdog Integration**:
```bash
gitleaks detect --report-format json | reviewdog -f=gitleaks -reporter=github-pr-review
```

**Configuration (.gitleaks.toml)**:
```toml
[extend]
useDefault = true

[[rules]]
id = "custom-api-key"
description = "Custom API Key Pattern"
regex = '''(?i)api[_-]?key[_-]?=.{20,}'''
```

**CWE Coverage**: CWE-798 (Use of Hard-coded Credentials)

---

### TruffleHog

**Description**: Find credentials accidentally committed to git repositories.

**Installation**:
```bash
pip install truffleHog
```

**Reviewdog Integration**:
```bash
trufflehog --json . | reviewdog -f=trufflehog -reporter=github-pr-review
```

**CWE Coverage**: CWE-798

---

## Infrastructure as Code

### Checkov

**Description**: Static code analysis for IaC (Terraform, CloudFormation, Kubernetes, etc.).

**Installation**:
```bash
pip install checkov
```

**Reviewdog Integration**:
```bash
checkov -d . -o json | reviewdog -f=checkov -reporter=github-pr-review
```

**Filter by Severity**:
```bash
# Only critical/high
checkov -d . --severity CRITICAL,HIGH -o json | reviewdog -f=checkov
```

**CWE Coverage**: CWE-250, CWE-284, CWE-326, CWE-601, CWE-668

---

### tfsec

**Description**: Security scanner for Terraform code.

**Installation**:
```bash
brew install tfsec
```

**Reviewdog Integration**:
```bash
tfsec . --format json | reviewdog -f=tfsec -reporter=github-pr-review
```

**CWE Coverage**: CWE-250, CWE-326, CWE-521

---

### Terrascan

**Description**: Detect compliance and security violations across IaC.

**Installation**:
```bash
brew install terrascan
```

**Reviewdog Integration**:
```bash
terrascan scan -o json | reviewdog -f=terrascan -reporter=github-pr-review
```

**CWE Coverage**: CWE-250, CWE-284, CWE-693

---

## Container Security

### Hadolint

**Description**: Dockerfile linter for best practices and security issues.

**Installation**:
```bash
brew install hadolint
```

**Reviewdog Integration**:
```bash
hadolint Dockerfile --format json | reviewdog -f=hadolint -reporter=github-pr-review
```

**Common Issues Detected**:
- Running as root (CWE-250)
- Exposed secrets in ENV (CWE-798)
- Outdated base images
- Missing health checks

**CWE Coverage**: CWE-250, CWE-798

---

### Trivy

**Description**: Comprehensive container and IaC security scanner.

**Installation**:
```bash
brew install trivy
```

**Reviewdog Integration**:
```bash
trivy fs --format json . | reviewdog -f=trivy -reporter=github-pr-review
```

**Scan Types**:
```bash
# Container images
trivy image --format json myimage:tag | reviewdog -f=trivy

# Filesystem
trivy fs --security-checks vuln,secret --format json . | reviewdog -f=trivy

# Kubernetes manifests
trivy k8s --report=summary --format json | reviewdog -f=trivy
```

**CWE Coverage**: Varies by vulnerability database

---

## Linters and Formatters

### ShellCheck

**Description**: Static analysis tool for shell scripts.

**Installation**:
```bash
brew install shellcheck
```

**Reviewdog Integration**:
```bash
shellcheck -f json script.sh | reviewdog -f=shellcheck -reporter=github-pr-review
```

**Security Checks**:
- Command injection (CWE-78)
- Unsafe variable expansion
- Insecure temporary files (CWE-377)

**CWE Coverage**: CWE-78, CWE-377

---

### yamllint

**Description**: YAML linter for syntax and best practices.

**Installation**:
```bash
pip install yamllint
```

**Reviewdog Integration**:
```bash
yamllint -f parsable . | reviewdog -f=yamllint -reporter=github-pr-review
```

---

### markdownlint

**Description**: Markdown linter for documentation quality.

**Installation**:
```bash
npm install -g markdownlint-cli
```

**Reviewdog Integration**:
```bash
markdownlint -j . | reviewdog -f=markdownlint -reporter=github-pr-review
```

---

## Multi-Tool Configurations

### Comprehensive Security Scan

Run all security tools in a single reviewdog session:

```yaml
# .reviewdog.yml
runner:
  semgrep:
    cmd: semgrep --config=auto --json
    format: semgrep
    name: Semgrep SAST
    level: error

  bandit:
    cmd: bandit -r . -f json
    format: bandit
    name: Python Security
    level: warning

  gitleaks:
    cmd: gitleaks detect --report-format json
    format: gitleaks
    name: Secret Detection
    level: error

  hadolint:
    cmd: hadolint Dockerfile --format json
    format: hadolint
    name: Dockerfile Security
    level: warning

  checkov:
    cmd: checkov -d . -o json --quiet
    format: checkov
    name: IaC Security
    level: error
```

Run with:
```bash
reviewdog -conf=.reviewdog.yml -reporter=github-pr-review
```

---

## Tool Selection Guide

Choose tools based on your tech stack:

**Python Projects**:
- Bandit (SAST)
- Semgrep (Multi-language SAST)
- Gitleaks (Secrets)

**JavaScript/TypeScript**:
- ESLint + security plugins
- Semgrep
- Gitleaks

**Infrastructure/Cloud**:
- Checkov (Terraform, K8s, CloudFormation)
- tfsec (Terraform-specific)
- Hadolint (Dockerfiles)
- Trivy (Containers + IaC)

**Multi-language/Polyglot**:
- Semgrep (20+ languages)
- Gitleaks (Universal secrets)
- ShellCheck (Shell scripts)

---

## Custom Tool Integration

To integrate a custom security tool:

1. **Convert output to supported format** (checkstyle, sarif, rdjson)
2. **Use rdjson for custom tools**:

```json
{
  "source": {
    "name": "custom-scanner",
    "url": "https://example.com"
  },
  "diagnostics": [
    {
      "message": "SQL Injection vulnerability detected",
      "location": {
        "path": "app/models.py",
        "range": {
          "start": {"line": 42, "column": 10}
        }
      },
      "severity": "ERROR",
      "code": {
        "value": "CWE-89",
        "url": "https://cwe.mitre.org/data/definitions/89.html"
      }
    }
  ]
}
```

3. **Pipe to reviewdog**:
```bash
./custom_scanner --json | reviewdog -f=rdjson -name="Custom Scanner"
```

---

## References

- [Reviewdog Supported Tools](https://reviewdog.github.io/supported-tools)
- [rdjson Format Specification](https://github.com/reviewdog/reviewdog/tree/master/proto/rdf)
- [SARIF Format](https://sarifweb.azurewebsites.net/)
