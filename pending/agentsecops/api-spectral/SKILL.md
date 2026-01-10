---
name: api-spectral
description: >
  API specification linting and security validation using Stoplight's Spectral with support for
  OpenAPI, AsyncAPI, and Arazzo specifications. Validates API definitions against security best
  practices, OWASP API Security Top 10, and custom organizational standards. Use when: (1) Validating
  OpenAPI/AsyncAPI specifications for security issues and design flaws, (2) Enforcing API design
  standards and governance policies across API portfolios, (3) Creating custom security rules for
  API specifications in CI/CD pipelines, (4) Detecting authentication, authorization, and data
  exposure issues in API definitions, (5) Ensuring API specifications comply with organizational
  security standards and regulatory requirements.
version: 0.1.0
maintainer: SirAppSec
category: appsec
tags: [api-security, openapi, asyncapi, linting, spectral, api-governance, owasp-api, specification-validation]
frameworks: [OWASP]
dependencies:
  tools: [node, npm]
  optional: [docker, git]
references:
  - https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview
  - https://github.com/stoplightio/spectral
  - https://owasp.org/API-Security/editions/2023/en/0x11-t10/
---

# API Security with Spectral

## Overview

Spectral is a flexible JSON/YAML linter from Stoplight that validates API specifications against
security best practices and organizational standards. With built-in rulesets for OpenAPI v2/v3.x,
AsyncAPI v2.x, and Arazzo v1.0, Spectral helps identify security vulnerabilities, design flaws,
and compliance issues during the API design phase—before code is written. Custom rulesets enable
enforcement of OWASP API Security Top 10 patterns, authentication standards, and data protection
requirements across your entire API portfolio.

## Quick Start

### Installation

```bash
# Install via npm
npm install -g @stoplight/spectral-cli

# Or using Yarn
yarn global add @stoplight/spectral-cli

# Or using Docker
docker pull stoplight/spectral

# Verify installation
spectral --version
```

### Basic API Specification Linting

```bash
# Lint OpenAPI specification with built-in rules
spectral lint openapi.yaml

# Lint with specific ruleset
spectral lint openapi.yaml --ruleset .spectral.yaml

# Output as JSON for CI/CD integration
spectral lint openapi.yaml --format json --output results.json
```

### Quick Security Scan

```bash
# Create security-focused ruleset
echo 'extends: ["spectral:oas"]' > .spectral.yaml

# Lint API specification
spectral lint api-spec.yaml --ruleset .spectral.yaml
```

## Core Workflow

### Workflow Checklist

Progress:
[ ] 1. Install Spectral and select appropriate base rulesets
[ ] 2. Create or configure ruleset with security rules
[ ] 3. Identify API specifications to validate (OpenAPI, AsyncAPI, Arazzo)
[ ] 4. Run linting with appropriate severity thresholds
[ ] 5. Review findings and categorize by security impact
[ ] 6. Map findings to OWASP API Security Top 10
[ ] 7. Create custom rules for organization-specific security patterns
[ ] 8. Integrate into CI/CD pipeline with failure thresholds
[ ] 9. Generate reports with remediation guidance
[ ] 10. Establish continuous validation process

Work through each step systematically. Check off completed items.

### Step 1: Ruleset Configuration

Create a `.spectral.yaml` ruleset extending built-in security rules:

```yaml
# .spectral.yaml - Basic security-focused ruleset
extends: ["spectral:oas", "spectral:asyncapi"]

rules:
  # Enforce HTTPS for all API endpoints
  oas3-valid-schema-example: true
  oas3-server-not-example.com: true

  # Authentication security
  operation-security-defined: error

  # Information disclosure prevention
  info-contact: warn
  info-description: warn
```

**Built-in Rulesets:**
- `spectral:oas` - OpenAPI v2/v3.x security and best practices
- `spectral:asyncapi` - AsyncAPI v2.x validation rules
- `spectral:arazzo` - Arazzo v1.0 workflow specifications

**Ruleset Selection Best Practices:**
- Start with built-in rulesets and progressively add custom rules
- Use `error` severity for critical security issues (authentication, HTTPS)
- Use `warn` for recommended practices and information disclosure risks
- Use `info` for style guide compliance and documentation completeness

For advanced ruleset patterns, see `references/ruleset_patterns.md`.

### Step 2: Security-Focused API Linting

Run Spectral with security-specific validation:

```bash
# Comprehensive security scan
spectral lint openapi.yaml \
  --ruleset .spectral.yaml \
  --format stylish \
  --verbose

# Focus on error-level findings only (critical security issues)
spectral lint openapi.yaml \
  --ruleset .spectral.yaml \
  --fail-severity error

# Scan multiple specifications
spectral lint api-specs/*.yaml --ruleset .spectral.yaml

# Generate JSON report for further analysis
spectral lint openapi.yaml \
  --ruleset .spectral.yaml \
  --format json \
  --output security-findings.json
```

**Output Formats:**
- `stylish` - Human-readable terminal output (default)
- `json` - Machine-readable JSON for CI/CD integration
- `junit` - JUnit XML for test reporting platforms
- `html` - HTML report (requires additional plugins)
- `github-actions` - GitHub Actions annotations format

### Step 3: OWASP API Security Validation

Validate API specifications against OWASP API Security Top 10:

```yaml
# .spectral-owasp.yaml - OWASP API Security focused rules
extends: ["spectral:oas"]

rules:
  # API1:2023 - Broken Object Level Authorization
  operation-security-defined:
    severity: error
    message: "All operations must have security defined (OWASP API1)"

  # API2:2023 - Broken Authentication
  security-schemes-defined:
    severity: error
    message: "API must define security schemes (OWASP API2)"

  # API3:2023 - Broken Object Property Level Authorization
  no-additional-properties:
    severity: warn
    message: "Consider disabling additionalProperties to prevent data leakage (OWASP API3)"

  # API5:2023 - Broken Function Level Authorization
  operation-tag-defined:
    severity: warn
    message: "Operations should be tagged for authorization policy mapping (OWASP API5)"

  # API7:2023 - Server Side Request Forgery
  no-http-basic:
    severity: error
    message: "HTTP Basic auth transmits credentials in plain text (OWASP API7)"

  # API8:2023 - Security Misconfiguration
  servers-use-https:
    description: All server URLs must use HTTPS
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        match: "^https://"
    message: "Server URL must use HTTPS (OWASP API8)"

  # API9:2023 - Improper Inventory Management
  api-version-required:
    severity: error
    given: $.info
    then:
      field: version
      function: truthy
    message: "API version must be specified (OWASP API9)"
```

**Run OWASP-focused validation:**
```bash
spectral lint openapi.yaml --ruleset .spectral-owasp.yaml
```

For complete OWASP API Security Top 10 rule mappings, see `references/owasp_api_mappings.md`.

### Step 4: Custom Security Rule Development

Create organization-specific security rules using Spectral's rule engine:

```yaml
# .spectral-custom.yaml
extends: ["spectral:oas"]

rules:
  # Require API key authentication
  require-api-key-auth:
    description: All APIs must support API key authentication
    severity: error
    given: $.components.securitySchemes[*]
    then:
      field: type
      function: enumeration
      functionOptions:
        values: [apiKey, oauth2, openIdConnect]
    message: "API must define apiKey, OAuth2, or OpenID Connect security"

  # Prevent PII in query parameters
  no-pii-in-query:
    description: Prevent PII exposure in URL query parameters
    severity: error
    given: $.paths[*][*].parameters[?(@.in == 'query')].name
    then:
      function: pattern
      functionOptions:
        notMatch: "(ssn|social.?security|credit.?card|password|secret|token)"
    message: "Query parameters must not contain PII identifiers"

  # Require rate limiting headers
  require-rate-limit-headers:
    description: API responses should include rate limit headers
    severity: warn
    given: $.paths[*][*].responses[*].headers
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          properties:
            X-RateLimit-Limit: true
            X-RateLimit-Remaining: true
    message: "Consider adding rate limit headers for security"

  # Enforce consistent error responses
  error-response-format:
    description: Error responses must follow standard format
    severity: error
    given: $.paths[*][*].responses[?(@property >= 400)].content.application/json.schema
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          required: [error, message]
          properties:
            error:
              type: string
            message:
              type: string
    message: "Error responses must include 'error' and 'message' fields"
```

**Custom Rule Development Resources:**
- `references/custom_rules_guide.md` - Complete rule authoring guide with functions
- `references/custom_functions.md` - Creating custom JavaScript/TypeScript functions
- `assets/rule-templates/` - Reusable rule templates for common security patterns

### Step 5: CI/CD Pipeline Integration

Integrate Spectral into continuous integration workflows:

**GitHub Actions:**
```yaml
# .github/workflows/api-security-lint.yml
name: API Security Linting

on: [push, pull_request]

jobs:
  spectral:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Spectral
        run: npm install -g @stoplight/spectral-cli

      - name: Lint API Specifications
        run: |
          spectral lint api-specs/*.yaml \
            --ruleset .spectral.yaml \
            --format github-actions \
            --fail-severity error

      - name: Generate Report
        if: always()
        run: |
          spectral lint api-specs/*.yaml \
            --ruleset .spectral.yaml \
            --format json \
            --output spectral-report.json

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: spectral-security-report
          path: spectral-report.json
```

**GitLab CI:**
```yaml
# .gitlab-ci.yml
api-security-lint:
  stage: test
  image: node:18
  script:
    - npm install -g @stoplight/spectral-cli
    - spectral lint api-specs/*.yaml --ruleset .spectral.yaml --fail-severity error
  artifacts:
    when: always
    reports:
      junit: spectral-report.xml
```

**Docker-Based Pipeline:**
```bash
# Run in CI/CD with Docker
docker run --rm \
  -v $(pwd):/work \
  stoplight/spectral lint /work/openapi.yaml \
  --ruleset /work/.spectral.yaml \
  --format json \
  --output /work/results.json

# Fail build on critical security issues
if jq -e '.[] | select(.severity == 0)' results.json > /dev/null; then
  echo "Critical security issues detected!"
  exit 1
fi
```

For complete CI/CD integration examples, see `scripts/ci_integration_examples/`.

### Step 6: Results Analysis and Remediation

Analyze findings and provide security remediation:

```bash
# Parse Spectral JSON output for security report
python3 scripts/parse_spectral_results.py \
  --input spectral-report.json \
  --output security-report.html \
  --map-owasp \
  --severity-threshold error

# Generate remediation guidance
python3 scripts/generate_remediation.py \
  --input spectral-report.json \
  --output remediation-guide.md
```

**Validation Workflow:**
1. Review all error-level findings (critical security issues)
2. Verify each finding in API specification context
3. Map findings to OWASP API Security Top 10 categories
4. Prioritize by severity and exploitability
5. Apply fixes to API specifications
6. Re-lint to verify remediation
7. Document security decisions and exceptions

**Feedback Loop Pattern:**
```bash
# 1. Initial lint
spectral lint openapi.yaml --ruleset .spectral.yaml -o scan1.json

# 2. Apply security fixes to API specification

# 3. Re-lint to verify fixes
spectral lint openapi.yaml --ruleset .spectral.yaml -o scan2.json

# 4. Compare results
python3 scripts/compare_spectral_results.py scan1.json scan2.json
```

## Advanced Patterns

### Pattern 1: Multi-Specification Governance

Enforce consistent security standards across API portfolio:

```bash
# Scan all API specifications with organization ruleset
find api-specs/ -name "*.yaml" -o -name "*.json" | while read spec; do
  echo "Linting: $spec"
  spectral lint "$spec" \
    --ruleset .spectral-org-standards.yaml \
    --format json \
    --output "reports/$(basename $spec .yaml)-report.json"
done

# Aggregate findings across portfolio
python3 scripts/aggregate_api_findings.py \
  --input-dir reports/ \
  --output portfolio-security-report.html
```

### Pattern 2: Progressive Severity Enforcement

Start with warnings and progressively enforce stricter rules:

```yaml
# .spectral-phase1.yaml - Initial rollout (warnings only)
extends: ["spectral:oas"]
rules:
  servers-use-https: warn
  operation-security-defined: warn

# .spectral-phase2.yaml - Enforcement phase (errors)
extends: ["spectral:oas"]
rules:
  servers-use-https: error
  operation-security-defined: error
```

```bash
# Phase 1: Awareness (don't fail builds)
spectral lint openapi.yaml --ruleset .spectral-phase1.yaml

# Phase 2: Enforcement (fail on violations)
spectral lint openapi.yaml --ruleset .spectral-phase2.yaml --fail-severity error
```

### Pattern 3: API Security Pre-Commit Validation

Prevent insecure API specifications from being committed:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Find staged API specification files
SPECS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(yaml|yml|json)$' | grep -E '(openapi|swagger|api)')

if [ -n "$SPECS" ]; then
  echo "Validating API specifications..."
  for spec in $SPECS; do
    spectral lint "$spec" --ruleset .spectral.yaml --fail-severity error
    if [ $? -ne 0 ]; then
      echo "Security validation failed for $spec"
      exit 1
    fi
  done
fi
```

### Pattern 4: Automated Security Review Comments

Generate security review comments for pull requests:

```bash
# Generate PR review comments from Spectral findings
spectral lint openapi.yaml \
  --ruleset .spectral.yaml \
  --format json | \
python3 scripts/generate_pr_comments.py \
  --file openapi.yaml \
  --severity error,warn \
  --output pr-comments.json

# Post to GitHub PR via gh CLI
gh pr comment $PR_NUMBER --body-file pr-comments.json
```

## Custom Functions for Advanced Security Rules

Create custom JavaScript functions for complex security validation:

```javascript
// spectral-functions/check-jwt-expiry.js
export default (targetVal, opts) => {
  // Validate JWT security scheme includes expiration
  if (targetVal.type === 'http' && targetVal.scheme === 'bearer') {
    if (!targetVal.bearerFormat || targetVal.bearerFormat !== 'JWT') {
      return [{
        message: 'Bearer authentication should specify JWT format'
      }];
    }
  }
  return [];
};
```

```yaml
# .spectral.yaml with custom function
functions:
  - check-jwt-expiry
functionsDir: ./spectral-functions

rules:
  jwt-security-check:
    description: Validate JWT security configuration
    severity: error
    given: $.components.securitySchemes[*]
    then:
      function: check-jwt-expiry
```

For complete custom function development guide, see `references/custom_functions.md`.

## Automation & Continuous Validation

### Scheduled API Security Scanning

```bash
# Automated daily API specification scanning
./scripts/spectral_scheduler.sh \
  --schedule daily \
  --specs-dir api-specs/ \
  --ruleset .spectral-owasp.yaml \
  --output-dir scan-results/ \
  --alert-on error \
  --slack-webhook $SLACK_WEBHOOK
```

### API Specification Monitoring

```bash
# Monitor API specifications for security regressions
./scripts/spectral_monitor.sh \
  --baseline baseline-scan.json \
  --current-scan latest-scan.json \
  --alert-on-new-findings \
  --email security-team@example.com
```

## Security Considerations

- **Specification Security**: API specifications may contain sensitive information (internal URLs, authentication schemes) - control access and sanitize before sharing
- **Rule Integrity**: Protect ruleset files from unauthorized modification - store in version control with code review requirements
- **False Positives**: Manually review findings before making security claims - context matters for API design decisions
- **Specification Versioning**: Maintain version history of API specifications to track security improvements over time
- **Secrets in Specs**: Never include actual credentials, API keys, or secrets in example values - use placeholder values only
- **Compliance Mapping**: Document how Spectral rules map to compliance requirements (PCI-DSS, GDPR, HIPAA)
- **Governance Enforcement**: Define exception process for legitimate rule violations with security team approval
- **Audit Logging**: Log all Spectral scans, findings, and remediation actions for security auditing
- **Access Control**: Restrict modification of security rulesets to designated API security team members
- **Continuous Validation**: Re-validate API specifications whenever they change or when new security rules are added

## Bundled Resources

### Scripts (`scripts/`)

- `parse_spectral_results.py` - Parse Spectral JSON output and generate security reports with OWASP mapping
- `generate_remediation.py` - Generate remediation guidance based on Spectral findings
- `compare_spectral_results.py` - Compare two Spectral scans to track remediation progress
- `aggregate_api_findings.py` - Aggregate findings across multiple API specifications
- `spectral_ci.sh` - CI/CD integration wrapper with exit code handling
- `spectral_scheduler.sh` - Scheduled scanning with alerting
- `spectral_monitor.sh` - Continuous monitoring with baseline comparison
- `generate_pr_comments.py` - Convert Spectral findings to PR review comments

### References (`references/`)

- `owasp_api_mappings.md` - Complete OWASP API Security Top 10 rule mappings
- `custom_rules_guide.md` - Custom rule authoring with examples
- `custom_functions.md` - Creating custom JavaScript/TypeScript validation functions
- `ruleset_patterns.md` - Reusable ruleset patterns for common security scenarios
- `api_security_checklist.md` - API security validation checklist

### Assets (`assets/`)

- `spectral-owasp.yaml` - Comprehensive OWASP API Security Top 10 ruleset
- `spectral-org-template.yaml` - Organization-wide API security standards template
- `github-actions-template.yml` - Complete GitHub Actions workflow
- `gitlab-ci-template.yml` - GitLab CI integration template
- `rule-templates/` - Reusable security rule templates

## Common Patterns

### Pattern 1: Security-First API Design Validation

Validate API specifications during design phase:

```bash
# Design phase validation (strict security rules)
spectral lint api-design.yaml \
  --ruleset .spectral-owasp.yaml \
  --fail-severity warn \
  --verbose
```

### Pattern 2: API Specification Diff Analysis

Detect security regressions between API versions:

```bash
# Compare two API specification versions
spectral lint api-v2.yaml --ruleset .spectral.yaml -o v2-findings.json
spectral lint api-v1.yaml --ruleset .spectral.yaml -o v1-findings.json

python3 scripts/compare_spectral_results.py \
  --baseline v1-findings.json \
  --current v2-findings.json \
  --show-regressions
```

### Pattern 3: Multi-Environment API Security

Different rulesets for development, staging, production:

```yaml
# .spectral-dev.yaml (permissive)
extends: ["spectral:oas"]
rules:
  servers-use-https: warn

# .spectral-prod.yaml (strict)
extends: ["spectral:oas"]
rules:
  servers-use-https: error
  operation-security-defined: error
```

## Integration Points

- **CI/CD**: GitHub Actions, GitLab CI, Jenkins, CircleCI, Azure DevOps
- **API Gateways**: Kong, Apigee, AWS API Gateway (validate specs before deployment)
- **IDE Integration**: VS Code extension, JetBrains plugins for real-time validation
- **API Documentation**: Stoplight Studio, Swagger UI, Redoc
- **Issue Tracking**: Jira, GitHub Issues, Linear (automated ticket creation for findings)
- **API Governance**: Backstage, API catalogs (enforce standards across portfolios)
- **Security Platforms**: Defect Dojo, SIEM platforms (via JSON export)

## Troubleshooting

### Issue: Too Many False Positives

**Solution**:
- Start with `error` severity only: `spectral lint --fail-severity error`
- Progressively add rules and adjust severity levels
- Use `overrides` section in ruleset to exclude specific paths
- See `references/ruleset_patterns.md` for filtering strategies

### Issue: Custom Rules Not Working

**Solution**:
- Verify JSONPath expressions using online JSONPath testers
- Check rule syntax with `spectral lint --ruleset .spectral.yaml --verbose`
- Use `--verbose` flag to see which rules are being applied
- Test rules in isolation before combining them

### Issue: Performance Issues with Large Specifications

**Solution**:
- Lint specific paths only: `spectral lint api-spec.yaml --ignore-paths "components/examples"`
- Use `--skip-rules` to disable expensive rules temporarily
- Split large specifications into smaller modules
- Run Spectral in parallel for multiple specifications

### Issue: CI/CD Integration Failing

**Solution**:
- Check Node.js version compatibility (requires Node 14+)
- Verify ruleset path is correct relative to specification file
- Use `--fail-severity` to control when builds should fail
- Review exit codes in `scripts/spectral_ci.sh`

## References

- [Spectral Documentation](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview)
- [Spectral GitHub Repository](https://github.com/stoplightio/spectral)
- [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [AsyncAPI Specification](https://www.asyncapi.com/docs/reference/specification/latest)
