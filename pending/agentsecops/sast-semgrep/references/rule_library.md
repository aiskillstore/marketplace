# Semgrep Rule Library

Curated collection of useful Semgrep rulesets and custom rule writing guidance.

## Table of Contents

- [Official Rulesets](#official-rulesets)
- [Language-Specific Rules](#language-specific-rules)
- [Framework-Specific Rules](#framework-specific-rules)
- [Custom Rule Writing](#custom-rule-writing)
- [Rule Testing](#rule-testing)

## Official Rulesets

### Comprehensive Rulesets

| Ruleset | Config | Description | Use Case |
|---------|--------|-------------|----------|
| Auto | `auto` | Automatically selected rules based on detected languages | Quick scans, baseline |
| Security Audit | `p/security-audit` | Comprehensive security rules across languages | Deep security review |
| OWASP Top 10 | `p/owasp-top-ten` | OWASP Top 10 2021 coverage | Compliance, security gates |
| CWE Top 25 | `p/cwe-top-25` | SANS/CWE Top 25 dangerous errors | Critical vulnerability detection |
| CI | `p/ci` | Fast, low false-positive rules for CI/CD | Pull request gates |
| Default | `p/default` | Balanced security and quality rules | General purpose scanning |

### Specialized Rulesets

| Ruleset | Config | Focus Area |
|---------|--------|------------|
| Secrets | `p/secrets` | Hard-coded credentials, API keys |
| Cryptography | `p/crypto` | Weak crypto, hashing issues |
| Supply Chain | `p/supply-chain` | Dependency vulnerabilities |
| JWT | `p/jwt` | JSON Web Token security |
| SQL Injection | `p/sql-injection` | SQL injection patterns |
| XSS | `p/xss` | Cross-site scripting |
| Command Injection | `p/command-injection` | OS command injection |

## Language-Specific Rules

### Python

```bash
# Django security
semgrep --config "p/django"

# Flask security
semgrep --config "r/python.flask.security"

# General Python security
semgrep --config "r/python.lang.security"

# Specific vulnerabilities
semgrep --config "r/python.lang.security.audit.exec-used"
semgrep --config "r/python.lang.security.audit.unsafe-pickle"
semgrep --config "r/python.lang.security.audit.dangerous-subprocess-use"
```

**Key Python Rules:**
- `python.django.security.injection.sql.sql-injection-db-cursor-execute`
- `python.flask.security.xss.audit.template-xss`
- `python.lang.security.audit.exec-used`
- `python.lang.security.audit.dangerous-os-module-methods`
- `python.lang.security.audit.hashlib-md5-used`

### JavaScript/TypeScript

```bash
# Express.js security
semgrep --config "p/express"

# React security
semgrep --config "p/react"

# Node.js security
semgrep --config "r/javascript.lang.security"

# Specific vulnerabilities
semgrep --config "r/javascript.lang.security.audit.eval-detected"
semgrep --config "r/javascript.lang.security.audit.unsafe-exec"
```

**Key JavaScript Rules:**
- `javascript.express.security.audit.xss.mustache.var-in-href`
- `javascript.lang.security.audit.eval-detected`
- `javascript.lang.security.audit.path-traversal`
- `javascript.sequelize.security.audit.sequelize-injection-express`

### Java

```bash
# Spring security
semgrep --config "p/spring"

# General Java security
semgrep --config "r/java.lang.security"

# Specific frameworks
semgrep --config "r/java.spring.security"
```

**Key Java Rules:**
- `java.lang.security.audit.sqli.jdbc-sqli`
- `java.lang.security.audit.xxe.xmlinputfactory-xxe`
- `java.spring.security.audit.spring-cookie-missing-httponly`

### Go

```bash
# Go security rules
semgrep --config "r/go.lang.security"

# Specific vulnerabilities
semgrep --config "r/go.lang.security.audit.net.use-of-tls-with-go-sql-driver"
semgrep --config "r/go.lang.security.audit.crypto.use_of_weak_crypto"
```

### PHP

```bash
# PHP security
semgrep --config "p/php"

# Laravel security
semgrep --config "r/php.laravel.security"

# Specific vulnerabilities
semgrep --config "r/php.lang.security.audit.sqli"
semgrep --config "r/php.lang.security.audit.dangerous-exec"
```

## Framework-Specific Rules

### Web Frameworks

**Django:**
```bash
semgrep --config "p/django"
# Covers: SQL injection, XSS, CSRF, auth issues
```

**Flask:**
```bash
semgrep --config "r/python.flask.security"
# Covers: XSS, debug mode, secure cookies
```

**Express.js:**
```bash
semgrep --config "p/express"
# Covers: XSS, CSRF, session config, CORS
```

**Spring Boot:**
```bash
semgrep --config "p/spring"
# Covers: SQL injection, XXE, auth, SSRF
```

### Cloud & Infrastructure

**Terraform:**
```bash
semgrep --config "r/terraform.lang.security"
# Covers: S3 buckets, security groups, encryption
```

**Kubernetes:**
```bash
semgrep --config "r/yaml.kubernetes.security"
# Covers: privileged containers, secrets, rbac
```

**Docker:**
```bash
semgrep --config "r/dockerfile.security"
# Covers: unsafe base images, secrets, root user
```

## Custom Rule Writing

### Rule Anatomy

```yaml
rules:
  - id: custom-rule-id
    pattern: execute($SQL)
    message: Potential security issue detected
    severity: WARNING
    languages: [python]
    metadata:
      category: security
      cwe: "CWE-89"
      owasp: "A03:2021-Injection"
      confidence: HIGH
```

### Pattern Types

**1. Basic Pattern**
```yaml
pattern: dangerous_function($ARG)
```

**2. Pattern-Inside (Context)**
```yaml
patterns:
  - pattern: execute($QUERY)
  - pattern-inside: |
      $QUERY = $USER_INPUT + ...
```

**3. Pattern-Not (Exclusion)**
```yaml
patterns:
  - pattern: execute($QUERY)
  - pattern-not: execute("SELECT * FROM safe_table")
```

**4. Pattern-Either (OR logic)**
```yaml
pattern-either:
  - pattern: eval($ARG)
  - pattern: exec($ARG)
```

**5. Metavariable Comparison**
```yaml
patterns:
  - pattern: crypto.encrypt($DATA, $KEY)
  - metavariable-comparison:
      metavariable: $KEY
      comparison: len($KEY) < 16
```

### Example Custom Rules

**Detect Hard-coded AWS Keys:**
```yaml
rules:
  - id: hardcoded-aws-key
    patterns:
      - pattern-regex: 'AKIA[0-9A-Z]{16}'
    message: Hard-coded AWS access key detected
    severity: ERROR
    languages: [python, javascript, java, go]
    metadata:
      category: security
      cwe: "CWE-798"
      confidence: HIGH
```

**Detect Unsafe File Operations:**
```yaml
rules:
  - id: unsafe-file-read
    patterns:
      - pattern: open($PATH, ...)
      - pattern-inside: |
          def $FUNC(..., $USER_INPUT, ...):
            ...
            $PATH = ... + $USER_INPUT + ...
            ...
    message: File path constructed from user input (path traversal risk)
    severity: WARNING
    languages: [python]
    metadata:
      cwe: "CWE-22"
      owasp: "A01:2021-Broken-Access-Control"
```

**Detect Missing CSRF Protection:**
```yaml
rules:
  - id: flask-missing-csrf
    patterns:
      - pattern: |
          @app.route($PATH, methods=[..., "POST", ...])
          def $FUNC(...):
            ...
      - pattern-not-inside: |
          @csrf.exempt
          ...
      - pattern-not-inside: |
          csrf_token = ...
          ...
    message: POST route without CSRF protection
    severity: ERROR
    languages: [python]
    metadata:
      cwe: "CWE-352"
      owasp: "A01:2021-Broken-Access-Control"
```

**Detect Insecure Random:**
```yaml
rules:
  - id: insecure-random-for-crypto
    patterns:
      - pattern-either:
          - pattern: random.random()
          - pattern: random.randint(...)
      - pattern-inside: |
          def ..._token(...):
            ...
    message: Using insecure random for security token
    severity: ERROR
    languages: [python]
    metadata:
      cwe: "CWE-330"
      fix: "Use secrets module: secrets.token_bytes(32)"
```

### Rule Metadata Best Practices

Include comprehensive metadata:
```yaml
metadata:
  category: security          # Type of issue
  cwe: "CWE-XXX"             # CWE mapping
  owasp: "AXX:2021-Name"     # OWASP category
  confidence: HIGH|MEDIUM|LOW # Detection confidence
  likelihood: HIGH|MEDIUM|LOW # Exploitation likelihood
  impact: HIGH|MEDIUM|LOW     # Security impact
  subcategory: [vuln-type]   # More specific categorization
  source-rule: url           # If adapted from elsewhere
  references:
    - https://example.com/docs
```

## Rule Testing

### Test File Structure
```
custom-rules/
├── rules.yaml          # Your custom rules
└── tests/
    ├── test-sqli.py   # Test cases
    └── test-xss.js    # Test cases
```

### Writing Tests

```python
# tests/test-sqli.py

# ruleid: custom-sql-injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ok: custom-sql-injection
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Running Tests

```bash
# Test custom rules
semgrep --config rules.yaml --test tests/

# Validate rule syntax
semgrep --validate --config rules.yaml
```

## Rule Performance Optimization

### 1. Use Specific Patterns
```yaml
# SLOW
pattern: $X

# FAST
pattern: dangerous_function($X)
```

### 2. Limit Language Scope
```yaml
# Only scan relevant languages
languages: [python, javascript]
```

### 3. Use Pattern-Inside Wisely
```yaml
# Narrow down context early
patterns:
  - pattern-inside: |
      def handle_request(...):
        ...
  - pattern: execute($QUERY)
```

### 4. Exclude Test Files
```yaml
paths:
  exclude:
    - "*/test_*.py"
    - "*/tests/*"
    - "*_test.go"
```

## Community Rules

Explore community-contributed rules:

```bash
# Browse rules by technology
semgrep --config "r/python.django"
semgrep --config "r/javascript.react"
semgrep --config "r/go.gorilla"

# Browse by vulnerability type
semgrep --config "r/generic.secrets"
semgrep --config "r/generic.html-templates"
```

**Useful Community Rulesets:**
- `r/python.aws-lambda.security` - AWS Lambda security
- `r/terraform.aws.security` - AWS Terraform
- `r/dockerfile.best-practice` - Docker best practices
- `r/yaml.github-actions.security` - GitHub Actions security

## References

- [Semgrep Rule Syntax](https://semgrep.dev/docs/writing-rules/rule-syntax/)
- [Semgrep Registry](https://semgrep.dev/explore)
- [Pattern Examples](https://semgrep.dev/docs/writing-rules/pattern-examples/)
- [Rule Writing Tutorial](https://semgrep.dev/learn)
