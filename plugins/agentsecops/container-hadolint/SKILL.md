---
name: container-hadolint
description: >
  Dockerfile security linting and best practice validation using Hadolint with 100+ built-in
  rules aligned to CIS Docker Benchmark. Use when: (1) Analyzing Dockerfiles for security
  misconfigurations and anti-patterns, (2) Enforcing container image security best practices
  in CI/CD pipelines, (3) Detecting hardcoded secrets and credentials in container builds,
  (4) Validating compliance with CIS Docker Benchmark requirements, (5) Integrating shift-left
  container security into developer workflows, (6) Providing remediation guidance for insecure
  Dockerfile instructions.
version: 0.1.0
maintainer: SirAppSec
category: devsecops
tags: [docker, hadolint, dockerfile, container-security, cis-benchmark, linting, ci-cd]
frameworks: [CIS, OWASP]
dependencies:
  tools: [hadolint, docker]
references:
  - https://github.com/hadolint/hadolint
  - https://www.cisecurity.org/benchmark/docker
  - https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
---

# Dockerfile Security Linting with Hadolint

## Overview

Hadolint is a Dockerfile linter that validates container build files against security best practices and the CIS Docker Benchmark. It analyzes Dockerfile instructions to identify misconfigurations, anti-patterns, and security vulnerabilities before images are built and deployed.

Hadolint integrates ShellCheck to validate RUN instructions, ensuring shell commands follow security best practices. With 100+ built-in rules mapped to CIS Docker Benchmark controls, Hadolint provides comprehensive security validation for container images.

## Quick Start

### Install Hadolint

```bash
# macOS via Homebrew
brew install hadolint

# Linux via binary
wget -O /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Linux-x86_64
chmod +x /usr/local/bin/hadolint

# Via Docker
docker pull hadolint/hadolint
```

### Scan Dockerfile

```bash
# Scan Dockerfile in current directory
hadolint Dockerfile

# Scan with specific Dockerfile path
hadolint path/to/Dockerfile

# Using Docker
docker run --rm -i hadolint/hadolint < Dockerfile
```

### Generate Report

```bash
# JSON output for automation
hadolint -f json Dockerfile > hadolint-report.json

# GitLab Code Quality format
hadolint -f gitlab_codeclimate Dockerfile > hadolint-codeclimate.json

# Checkstyle format for CI integration
hadolint -f checkstyle Dockerfile > hadolint-checkstyle.xml
```

## Core Workflows

### 1. Local Development Scanning

Validate Dockerfiles during development:

```bash
# Basic scan with colored output
hadolint Dockerfile

# Scan with specific severity threshold
hadolint --failure-threshold error Dockerfile

# Show only warnings and errors
hadolint --no-color --format tty Dockerfile | grep -E "^(warning|error)"

# Verbose output with rule IDs
hadolint -t style -t warning -t error Dockerfile
```

**Output Format:**
```
Dockerfile:3 DL3008 warning: Pin versions in apt get install
Dockerfile:7 DL3025 error: Use JSON notation for CMD and ENTRYPOINT
Dockerfile:12 DL3059 info: Multiple RUN instructions detected
```

**When to use**: Developer workstation, pre-commit validation, iterative Dockerfile development.

### 2. CI/CD Pipeline Integration

Automate Dockerfile validation in build pipelines:

#### GitHub Actions

```yaml
name: Hadolint
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Hadolint Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: warning
          format: sarif
          output-file: hadolint.sarif

      - name: Upload SARIF to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: hadolint.sarif
```

#### GitLab CI

```yaml
hadolint:
  image: hadolint/hadolint:latest-debian
  stage: lint
  script:
    - hadolint -f gitlab_codeclimate Dockerfile > hadolint-report.json
  artifacts:
    reports:
      codequality: hadolint-report.json
    when: always
```

**When to use**: Automated security gates, pull request checks, deployment validation.

### 3. Configuration Customization

Create `.hadolint.yaml` to customize rules:

```yaml
# .hadolint.yaml
failure-threshold: warning
ignored:
  - DL3008  # Allow unpinned apt-get packages (assess risk first)
  - DL3059  # Allow multiple RUN instructions

trustedRegistries:
  - docker.io/library  # Official Docker Hub images
  - gcr.io/distroless  # Google distroless images
  - registry.access.redhat.com  # Red Hat registry

override:
  error:
    - DL3001  # Enforce: never use yum/dnf/zypper without version pins
  warning:
    - DL3015  # Warn: use --no-install-recommends with apt-get
  info:
    - DL3059  # Info: multiple RUN instructions reduce layer caching

label-schema:
  maintainer: text
  org.opencontainers.image.vendor: text
  org.opencontainers.image.version: semver
```

Use bundled templates in `assets/`:
- `assets/hadolint-strict.yaml` - Strict security enforcement (CRITICAL/HIGH only)
- `assets/hadolint-balanced.yaml` - Balanced validation (recommended)
- `assets/hadolint-permissive.yaml` - Permissive for legacy Dockerfiles

**When to use**: Reducing false positives, organizational standards, legacy Dockerfile migration.

### 4. Security-Focused Validation

Enforce critical security rules:

```bash
# Only fail on security issues (error severity)
hadolint --failure-threshold error Dockerfile

# Check specific security rules
hadolint --trusted-registry docker.io/library Dockerfile

# Scan all Dockerfiles in project
find . -name "Dockerfile*" -exec hadolint {} \;

# Generate security report with only errors
hadolint -f json Dockerfile | jq '.[] | select(.level == "error")'
```

**Critical Security Rules:**
- **DL3000**: Use absolute WORKDIR (prevents directory traversal)
- **DL3001**: Always use version pinning for package managers
- **DL3002**: Never switch to root USER in Dockerfile
- **DL3020**: Use COPY instead of ADD (prevents arbitrary URL fetching)
- **DL3025**: Use JSON notation for CMD/ENTRYPOINT (prevents shell injection)

See `references/security_rules.md` for complete security rule catalog with CIS mappings.

### 5. Multi-Stage Build Validation

Scan complex multi-stage Dockerfiles:

```bash
# Validate all stages
hadolint Dockerfile

# Stage-specific validation (use custom script)
./scripts/hadolint_multistage.py Dockerfile
```

**Common Multi-Stage Issues:**
- Using same user across build and runtime stages
- Copying unnecessary build tools to production image
- Missing security hardening in final stage
- Secrets present in build stage propagating to runtime

**When to use**: Complex builds, security-hardened images, production containerization.

### 6. Pre-Commit Hook Integration

Prevent insecure Dockerfiles from being committed:

```bash
# Install pre-commit hook using bundled script
./scripts/install_precommit.sh

# Or manually create hook
cat << 'EOF' > .git/hooks/pre-commit
#!/bin/bash
for dockerfile in $(git diff --cached --name-only | grep -E 'Dockerfile'); do
  hadolint --failure-threshold warning "$dockerfile" || exit 1
done
EOF

chmod +x .git/hooks/pre-commit
```

**When to use**: Developer workstations, team onboarding, mandatory security controls.

## Security Considerations

### Sensitive Data Handling

- **Secret Detection**: Hadolint flags hardcoded secrets in ENV, ARG, LABEL instructions
- **Build Secrets**: Use Docker BuildKit secrets (`RUN --mount=type=secret`) instead of ARG for credentials
- **Multi-Stage Security**: Ensure secrets in build stages don't leak to final image
- **Image Scanning**: Hadolint validates Dockerfile - combine with image scanning (Trivy, Grype) for runtime security

### Access Control

- **CI/CD Permissions**: Hadolint scans require read access to Dockerfile and build context
- **Report Storage**: Treat scan reports as internal documentation - may reveal security practices
- **Trusted Registries**: Configure `trustedRegistries` to enforce approved base image sources

### Audit Logging

Log the following for compliance and security auditing:
- Scan execution timestamps and Dockerfile paths
- Rule violations by severity (error, warning, info)
- Suppressed rules and justifications
- Base image registry validation results
- Remediation actions and timeline

### Compliance Requirements

- **CIS Docker Benchmark 1.6**: Hadolint rules map to CIS controls (see `references/cis_mapping.md`)
  - 4.1: Create a user for the container (DL3002)
  - 4.6: Add HEALTHCHECK instruction (DL3025)
  - 4.7: Do not use update alone in Dockerfile (DL3009)
  - 4.9: Use COPY instead of ADD (DL3020)
- **OWASP Docker Security**: Validates against OWASP container security best practices
- **NIST SP 800-190**: Application container security guidance

## Bundled Resources

### Scripts (`scripts/`)

- `hadolint_scan.py` - Comprehensive scanning with multiple Dockerfiles and output formats
- `hadolint_multistage.py` - Multi-stage Dockerfile analysis with stage-specific validation
- `install_precommit.sh` - Automated pre-commit hook installation
- `ci_integration.sh` - CI/CD integration examples for multiple platforms

### References (`references/`)

- `security_rules.md` - Complete Hadolint security rules with CIS Benchmark mappings
- `cis_mapping.md` - Detailed CIS Docker Benchmark control mapping
- `remediation_guide.md` - Rule-by-rule remediation guidance with secure examples
- `shellcheck_integration.md` - ShellCheck rules for RUN instruction validation

### Assets (`assets/`)

- `hadolint-strict.yaml` - Strict security configuration
- `hadolint-balanced.yaml` - Production-ready configuration (recommended)
- `hadolint-permissive.yaml` - Legacy Dockerfile migration configuration
- `github-actions.yml` - Complete GitHub Actions workflow
- `gitlab-ci.yml` - Complete GitLab CI pipeline
- `precommit-config.yaml` - Pre-commit framework configuration

## Common Patterns

### Pattern 1: Initial Dockerfile Security Audit

First-time security assessment:

```bash
# 1. Find all Dockerfiles
find . -type f -name "Dockerfile*" > dockerfile-list.txt

# 2. Scan all Dockerfiles with JSON output
mkdir -p security-reports
while read dockerfile; do
  output_file="security-reports/$(echo $dockerfile | tr '/' '_').json"
  hadolint -f json "$dockerfile" > "$output_file" 2>&1
done < dockerfile-list.txt

# 3. Generate summary report
./scripts/hadolint_scan.py --input-dir . --output summary-report.html

# 4. Review critical/high findings
cat security-reports/*.json | jq '.[] | select(.level == "error")' > critical-findings.json
```

### Pattern 2: Progressive Remediation

Gradual security hardening:

```bash
# Phase 1: Baseline (don't fail builds yet)
hadolint --failure-threshold none -f json Dockerfile > baseline.json

# Phase 2: Fix critical issues (fail on errors only)
hadolint --failure-threshold error Dockerfile

# Phase 3: Address warnings
hadolint --failure-threshold warning Dockerfile

# Phase 4: Full compliance (including style/info)
hadolint Dockerfile
```

### Pattern 3: Security-Hardened Production Image

Build security-first container image:

```dockerfile
# Example secure Dockerfile following Hadolint best practices

# Use specific base image version from trusted registry
FROM docker.io/library/node:18.19.0-alpine3.19

# Install packages with version pinning and cleanup
RUN apk add --no-cache \
    dumb-init=1.2.5-r2 \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S -u 1001 -G appuser appuser

# Set working directory
WORKDIR /app

# Copy application files (use COPY not ADD)
COPY --chown=appuser:appuser package*.json ./
COPY --chown=appuser:appuser . .

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Switch to non-root user
USER appuser

# Expose port (document only, not security control)
EXPOSE 3000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

# Use JSON notation for entrypoint/cmd
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "server.js"]
```

Validate with Hadolint:
```bash
hadolint Dockerfile  # Should pass with no errors
```

### Pattern 4: CI/CD with Automated Remediation Suggestions

Provide actionable feedback in pull requests:

```bash
# In CI pipeline
hadolint -f json Dockerfile > hadolint.json

# Generate remediation suggestions
./scripts/hadolint_scan.py \
  --input hadolint.json \
  --format markdown \
  --output pr-comment.md

# Post to PR comment (using gh CLI)
gh pr comment --body-file pr-comment.md
```

## Integration Points

### CI/CD Integration

- **GitHub Actions**: Native hadolint-action with SARIF support for Security tab
- **GitLab CI**: GitLab Code Quality format integration
- **Jenkins**: Checkstyle format for Jenkins Warnings plugin
- **CircleCI**: Docker-based executor with artifact retention
- **Azure Pipelines**: Task integration with results publishing

### Security Tools Ecosystem

- **Image Scanning**: Combine with Trivy, Grype, Clair for runtime vulnerability scanning
- **Secret Scanning**: Integrate with Gitleaks, TruffleHog for comprehensive secret detection
- **IaC Security**: Chain with Checkov for Kubernetes/Terraform validation
- **SBOM Generation**: Export findings alongside Syft/Trivy SBOM reports
- **Security Dashboards**: Export JSON to Grafana, Kibana, Datadog for centralized monitoring

### SDLC Integration

- **Development**: Pre-commit hooks provide immediate feedback
- **Code Review**: PR checks prevent insecure Dockerfiles from merging
- **Testing**: Scan test environment Dockerfiles
- **Staging**: Validation gate before production promotion
- **Production**: Periodic audits of deployed container configurations

## Troubleshooting

### Issue: Too Many False Positives

**Symptoms**: Legitimate patterns flagged (legacy Dockerfiles, specific use cases)

**Solution**:
```yaml
# Create .hadolint.yaml
ignored:
  - DL3059  # Multiple RUN instructions (valid for complex builds)

# Or use inline ignores
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y curl
```

Consult `references/remediation_guide.md` for rule-specific guidance.

### Issue: Base Image Registry Not Trusted

**Symptoms**: Error about untrusted registry even for legitimate images

**Solution**:
```yaml
# Add to .hadolint.yaml
trustedRegistries:
  - mycompany.azurecr.io
  - gcr.io/my-project
  - docker.io/library
```

### Issue: ShellCheck Warnings in RUN Instructions

**Symptoms**: SC2086, SC2046 warnings from ShellCheck integration

**Solution**:
```dockerfile
# Bad: Unquoted variables
RUN echo $MY_VAR > file.txt

# Good: Quoted variables
RUN echo "$MY_VAR" > file.txt

# Or disable specific ShellCheck rule
# hadolint ignore=DL4006
RUN echo $MY_VAR > file.txt
```

See `references/shellcheck_integration.md` for complete ShellCheck guidance.

### Issue: Multi-Stage Build Not Recognized

**Symptoms**: Errors about missing USER instruction despite proper multi-stage setup

**Solution**:
```dockerfile
# Ensure each stage has appropriate USER
FROM node:18 AS builder
# Build operations...

FROM node:18-alpine AS runtime
USER node  # Add USER in final stage
CMD ["node", "app.js"]
```

### Issue: CI Pipeline Failing on Warnings

**Symptoms**: Build fails on low-severity issues

**Solution**:
```bash
# Adjust failure threshold in CI
hadolint --failure-threshold error Dockerfile

# Or configure per-environment
if [ "$CI_ENVIRONMENT" == "production" ]; then
  hadolint --failure-threshold warning Dockerfile
else
  hadolint --failure-threshold error Dockerfile
fi
```

## Advanced Configuration

### Custom Rule Severity Override

```yaml
# .hadolint.yaml
override:
  error:
    - DL3001  # Package versioning is critical
    - DL3020  # COPY vs ADD is security-critical
  warning:
    - DL3059  # Multiple RUN is warning, not info
  info:
    - DL3008  # Downgrade apt-get pinning to info for dev images
```

### Inline Suppression

```dockerfile
# Suppress single rule for one instruction
# hadolint ignore=DL3018
RUN apk add --no-cache curl

# Suppress multiple rules
# hadolint ignore=DL3003,DL3009
WORKDIR /tmp
RUN apt-get update && apt-get install -y wget

# Global suppression (use sparingly)
# hadolint global ignore=DL3059
```

### Trusted Registry Enforcement

```yaml
# .hadolint.yaml
trustedRegistries:
  - docker.io/library      # Official images only
  - gcr.io/distroless      # Google distroless
  - cgr.dev/chainguard     # Chainguard images

# This will error on:
# FROM nginx:latest                    ❌ (docker.io/nginx)
# FROM docker.io/library/nginx:latest  ✅ (trusted)
```

### Label Schema Validation

```yaml
# .hadolint.yaml
label-schema:
  maintainer: text
  org.opencontainers.image.created: rfc3339
  org.opencontainers.image.version: semver
  org.opencontainers.image.vendor: text
```

Ensures Dockerfile LABELs conform to OCI image specification.

## References

- [Hadolint GitHub Repository](https://github.com/hadolint/hadolint)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [ShellCheck Documentation](https://www.shellcheck.net/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
