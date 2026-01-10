# OWASP Top 10 to CWE Mapping with Semgrep Rules

## Table of Contents

- [A01:2021 - Broken Access Control](#a012021---broken-access-control)
- [A02:2021 - Cryptographic Failures](#a022021---cryptographic-failures)
- [A03:2021 - Injection](#a032021---injection)
- [A04:2021 - Insecure Design](#a042021---insecure-design)
- [A05:2021 - Security Misconfiguration](#a052021---security-misconfiguration)
- [A06:2021 - Vulnerable and Outdated Components](#a062021---vulnerable-and-outdated-components)
- [A07:2021 - Identification and Authentication Failures](#a072021---identification-and-authentication-failures)
- [A08:2021 - Software and Data Integrity Failures](#a082021---software-and-data-integrity-failures)
- [A09:2021 - Security Logging and Monitoring Failures](#a092021---security-logging-and-monitoring-failures)
- [A10:2021 - Server-Side Request Forgery (SSRF)](#a102021---server-side-request-forgery-ssrf)

## A01:2021 - Broken Access Control

### CWE Mappings
- CWE-22: Path Traversal
- CWE-23: Relative Path Traversal
- CWE-35: Path Traversal
- CWE-352: Cross-Site Request Forgery (CSRF)
- CWE-434: Unrestricted Upload of Dangerous File Type
- CWE-639: Authorization Bypass Through User-Controlled Key
- CWE-918: Server-Side Request Forgery (SSRF)

### Semgrep Rules
```bash
# Path traversal detection
semgrep --config "r/python.lang.security.audit.path-traversal"

# Missing authorization checks
semgrep --config "r/generic.secrets.security.detected-generic-secret"

# CSRF protection
semgrep --config "r/javascript.express.security.audit.express-check-csurf-middleware-usage"
```

### Detection Patterns
- Unrestricted file access using user input
- Missing or improper authorization checks
- Insecure direct object references (IDOR)
- Elevation of privilege vulnerabilities

## A02:2021 - Cryptographic Failures

### CWE Mappings
- CWE-259: Use of Hard-coded Password
- CWE-326: Inadequate Encryption Strength
- CWE-327: Use of Broken/Risky Crypto Algorithm
- CWE-328: Reversible One-Way Hash
- CWE-330: Use of Insufficiently Random Values
- CWE-780: Use of RSA Without OAEP

### Semgrep Rules
```bash
# Weak crypto algorithms
semgrep --config "p/crypto"

# Hard-coded secrets
semgrep --config "p/secrets"

# Insecure random
semgrep --config "r/python.lang.security.audit.insecure-random"
```

### Detection Patterns
- Use of MD5, SHA1 for cryptographic purposes
- Hard-coded passwords, API keys, tokens
- Weak encryption algorithms (DES, RC4)
- Insecure random number generation

## A03:2021 - Injection

### CWE Mappings
- CWE-79: Cross-site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code (eval injection)
- CWE-917: Expression Language Injection
- CWE-943: Improper Neutralization of Special Elements in Data Query Logic

### Semgrep Rules
```bash
# SQL Injection
semgrep --config "r/python.django.security.injection.sql"
semgrep --config "r/javascript.sequelize.security.audit.sequelize-injection"

# XSS
semgrep --config "r/javascript.express.security.audit.xss"
semgrep --config "r/python.flask.security.audit.template-xss"

# Command Injection
semgrep --config "r/python.lang.security.audit.dangerous-subprocess-use"

# Code Injection
semgrep --config "r/python.lang.security.audit.exec-used"
semgrep --config "r/javascript.lang.security.audit.eval-detected"
```

### Detection Patterns
- Unsafe SQL query construction
- Unescaped user input in HTML context
- OS command execution with user input
- Use of eval() or similar dynamic code execution

## A04:2021 - Insecure Design

### CWE Mappings
- CWE-209: Generation of Error Message with Sensitive Information
- CWE-256: Unprotected Storage of Credentials
- CWE-501: Trust Boundary Violation
- CWE-522: Insufficiently Protected Credentials

### Semgrep Rules
```bash
# Information disclosure
semgrep --config "r/python.flask.security.audit.debug-enabled"

# Missing security controls
semgrep --config "p/security-audit"
```

### Detection Patterns
- Debug mode enabled in production
- Verbose error messages exposing internals
- Missing rate limiting
- Insecure default configurations

## A05:2021 - Security Misconfiguration

### CWE Mappings
- CWE-16: Configuration
- CWE-611: Improper Restriction of XML External Entity Reference
- CWE-614: Sensitive Cookie in HTTPS Session Without 'Secure' Attribute
- CWE-756: Missing Custom Error Page
- CWE-776: Improper Restriction of Recursive Entity References in DTDs

### Semgrep Rules
```bash
# XXE vulnerabilities
semgrep --config "r/python.lang.security.audit.avoid-lxml-in-xml-parsing"

# Insecure cookie settings
semgrep --config "r/javascript.express.security.audit.express-cookie-settings"

# CORS misconfiguration
semgrep --config "r/javascript.express.security.audit.express-cors-misconfiguration"
```

### Detection Patterns
- XML External Entity (XXE) vulnerabilities
- Insecure cookie flags (missing Secure, HttpOnly, SameSite)
- Open CORS policies
- Unnecessary features enabled

## A06:2021 - Vulnerable and Outdated Components

### CWE Mappings
- CWE-1035: Using Components with Known Vulnerabilities
- CWE-1104: Use of Unmaintained Third Party Components

### Semgrep Rules
```bash
# Known vulnerable dependencies
semgrep --config "p/supply-chain"

# Deprecated APIs
semgrep --config "p/owasp-top-ten"
```

### Detection Patterns
- Outdated library versions
- Dependencies with known CVEs
- Use of deprecated/unmaintained packages
- Insecure package imports

## A07:2021 - Identification and Authentication Failures

### CWE Mappings
- CWE-287: Improper Authentication
- CWE-288: Authentication Bypass Using Alternate Path/Channel
- CWE-306: Missing Authentication for Critical Function
- CWE-307: Improper Restriction of Excessive Authentication Attempts
- CWE-521: Weak Password Requirements
- CWE-798: Use of Hard-coded Credentials
- CWE-916: Use of Password Hash With Insufficient Computational Effort

### Semgrep Rules
```bash
# Weak password hashing
semgrep --config "r/python.lang.security.audit.hashlib-md5-used"

# Missing authentication
semgrep --config "p/jwt"

# Session management
semgrep --config "r/javascript.express.security.audit.express-session-misconfiguration"
```

### Detection Patterns
- Weak password hashing (MD5, SHA1 without salt)
- Missing multi-factor authentication
- Predictable session identifiers
- Credential stuffing vulnerabilities

## A08:2021 - Software and Data Integrity Failures

### CWE Mappings
- CWE-345: Insufficient Verification of Data Authenticity
- CWE-502: Deserialization of Untrusted Data
- CWE-829: Inclusion of Functionality from Untrusted Control Sphere
- CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes

### Semgrep Rules
```bash
# Unsafe deserialization
semgrep --config "r/python.lang.security.audit.unsafe-pickle"
semgrep --config "r/javascript.lang.security.audit.unsafe-deserialization"

# Prototype pollution
semgrep --config "r/javascript.lang.security.audit.prototype-pollution"
```

### Detection Patterns
- Unsafe deserialization (pickle, YAML, JSON)
- Missing integrity checks on updates
- Prototype pollution in JavaScript
- Unsafe code loading from external sources

## A09:2021 - Security Logging and Monitoring Failures

### CWE Mappings
- CWE-117: Improper Output Neutralization for Logs
- CWE-223: Omission of Security-relevant Information
- CWE-532: Information Exposure Through Log Files
- CWE-778: Insufficient Logging

### Semgrep Rules
```bash
# Log injection
semgrep --config "r/python.lang.security.audit.logging-unsanitized-input"

# Sensitive data in logs
semgrep --config "p/secrets"
```

### Detection Patterns
- Log injection vulnerabilities
- Sensitive data logged (passwords, tokens)
- Missing security event logging
- Insufficient audit trails

## A10:2021 - Server-Side Request Forgery (SSRF)

### CWE Mappings
- CWE-918: Server-Side Request Forgery (SSRF)

### Semgrep Rules
```bash
# SSRF detection
semgrep --config "r/python.requests.security.audit.requests-http-request"
semgrep --config "r/javascript.lang.security.audit.detect-unsafe-url"
```

### Detection Patterns
- Unvalidated URL fetching
- Internal network access via user input
- Missing URL validation
- Bypassing access controls via SSRF

## Using This Mapping

### Scan for Specific OWASP Category

```bash
# Example: Scan for Injection vulnerabilities (A03)
semgrep --config "r/python.django.security.injection.sql" \
        --config "r/python.lang.security.audit.exec-used" \
        /path/to/code
```

### Comprehensive OWASP Top 10 Scan

```bash
semgrep --config="p/owasp-top-ten" /path/to/code
```

### Filter by CWE

```bash
# Scan and filter results by CWE
semgrep --config="p/security-audit" --json /path/to/code | \
  jq '.results[] | select(.extra.metadata.cwe == "CWE-89")'
```

## References

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Semgrep Rule Registry](https://semgrep.dev/explore)
