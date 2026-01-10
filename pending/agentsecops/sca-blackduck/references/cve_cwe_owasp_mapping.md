# CVE to CWE and OWASP Top 10 Mapping

## Table of Contents
- [Common Vulnerability Patterns](#common-vulnerability-patterns)
- [OWASP Top 10 2021 Mapping](#owasp-top-10-2021-mapping)
- [CWE Top 25 Mapping](#cwe-top-25-mapping)
- [Dependency Vulnerability Categories](#dependency-vulnerability-categories)

## Common Vulnerability Patterns

### Injection Vulnerabilities in Dependencies

**OWASP**: A03:2021 - Injection
**CWE**: CWE-89 (SQL Injection), CWE-78 (OS Command Injection)

Common in:
- ORM libraries with unsafe query construction
- Template engines with code execution features
- Database drivers with insufficient input sanitization

**Example CVEs**:
- CVE-2021-44228 (Log4Shell) - Remote Code Execution via JNDI injection
- CVE-2022-22965 (Spring4Shell) - RCE via Spring Framework

### Deserialization Vulnerabilities

**OWASP**: A08:2021 - Software and Data Integrity Failures
**CWE**: CWE-502 (Deserialization of Untrusted Data)

Common in:
- Java serialization libraries (Jackson, XStream, etc.)
- Python pickle
- PHP unserialize

**Example CVEs**:
- CVE-2017-5638 (Apache Struts) - Remote Code Execution
- CVE-2019-12384 (Jackson) - Polymorphic typing RCE

### Authentication and Cryptography Flaws

**OWASP**: A02:2021 - Cryptographic Failures
**CWE**: CWE-327 (Broken Crypto), CWE-311 (Missing Encryption)

Common in:
- Outdated cryptographic libraries
- JWT libraries with algorithm confusion
- SSL/TLS implementations with weak ciphers

**Example CVEs**:
- CVE-2022-21449 (Java ECDSA) - Signature validation bypass
- CVE-2020-36518 (Jackson) - Denial of Service via deeply nested objects

### XML External Entity (XXE)

**OWASP**: A05:2021 - Security Misconfiguration
**CWE**: CWE-611 (XML External Entities)

Common in:
- XML parsers with external entity processing enabled by default
- SOAP/XML-RPC libraries

**Example CVEs**:
- CVE-2021-44832 (Log4j) - Remote Code Execution
- CVE-2018-1000613 (dom4j) - XXE vulnerability

## OWASP Top 10 2021 Mapping

### A01:2021 - Broken Access Control

**Related CWEs**:
- CWE-22: Path Traversal
- CWE-284: Improper Access Control
- CWE-639: Insecure Direct Object Reference

**Dependency Examples**:
- File handling libraries with path traversal
- Authorization libraries with bypass vulnerabilities
- API frameworks with missing access controls

### A02:2021 - Cryptographic Failures

**Related CWEs**:
- CWE-327: Use of Broken Cryptography
- CWE-328: Weak Hash
- CWE-331: Insufficient Entropy

**Dependency Examples**:
- Outdated OpenSSL/BoringSSL versions
- Weak hash implementations (MD5, SHA1)
- Insecure random number generators

### A03:2021 - Injection

**Related CWEs**:
- CWE-89: SQL Injection
- CWE-78: OS Command Injection
- CWE-94: Code Injection

**Dependency Examples**:
- ORM libraries with unsafe queries
- Template engines with code execution
- Shell command utilities

### A04:2021 - Insecure Design

**Related CWEs**:
- CWE-209: Information Exposure Through Error Messages
- CWE-256: Plaintext Storage of Password
- CWE-918: SSRF

**Dependency Examples**:
- Libraries with verbose error messages
- Frameworks with insecure defaults
- HTTP clients vulnerable to SSRF

### A05:2021 - Security Misconfiguration

**Related CWEs**:
- CWE-611: XXE
- CWE-16: Configuration
- CWE-2: Environmental Security

**Dependency Examples**:
- XML parsers with XXE by default
- Web frameworks with debug mode enabled
- Default credentials in libraries

### A06:2021 - Vulnerable and Outdated Components

**Related CWEs**:
- CWE-1035: 2014 Top 25 - Insecure Interaction
- CWE-1104: Use of Unmaintained Third Party Components

**This is the primary focus of SCA tools like Black Duck**

Key risks:
- Dependencies with known CVEs
- Unmaintained or abandoned libraries
- Transitive dependencies with vulnerabilities
- License compliance issues

### A07:2021 - Identification and Authentication Failures

**Related CWEs**:
- CWE-287: Improper Authentication
- CWE-306: Missing Authentication
- CWE-798: Hard-coded Credentials

**Dependency Examples**:
- OAuth/OIDC libraries with bypass vulnerabilities
- JWT libraries with algorithm confusion
- Session management libraries with fixation issues

### A08:2021 - Software and Data Integrity Failures

**Related CWEs**:
- CWE-502: Deserialization of Untrusted Data
- CWE-829: Inclusion of Functionality from Untrusted Control Sphere
- CWE-494: Download of Code Without Integrity Check

**Dependency Examples**:
- Serialization libraries (Jackson, pickle, etc.)
- Package managers vulnerable to dependency confusion
- Libraries fetching code over HTTP

### A09:2021 - Security Logging and Monitoring Failures

**Related CWEs**:
- CWE-778: Insufficient Logging
- CWE-117: Log Injection
- CWE-532: Information Exposure Through Log Files

**Dependency Examples**:
- Logging libraries with injection vulnerabilities (Log4Shell)
- Frameworks with insufficient audit logging
- Libraries exposing sensitive data in logs

### A10:2021 - Server-Side Request Forgery (SSRF)

**Related CWEs**:
- CWE-918: SSRF

**Dependency Examples**:
- HTTP client libraries with insufficient validation
- URL parsing libraries with bypass issues
- Image processing libraries fetching remote resources

## CWE Top 25 Mapping

### Top 5 Most Dangerous in Dependencies

1. **CWE-502: Deserialization of Untrusted Data**
   - Found in: Java (Jackson, XStream), Python (pickle), .NET
   - CVSS typically: 9.0-10.0
   - Remediation: Upgrade to patched versions, avoid deserializing untrusted data

2. **CWE-78: OS Command Injection**
   - Found in: Shell utilities, process execution libraries
   - CVSS typically: 8.0-9.8
   - Remediation: Use parameterized APIs, input validation

3. **CWE-89: SQL Injection**
   - Found in: Database drivers, ORM libraries
   - CVSS typically: 8.0-9.8
   - Remediation: Use parameterized queries, upgrade to patched versions

4. **CWE-79: Cross-site Scripting (XSS)**
   - Found in: Template engines, HTML sanitization libraries
   - CVSS typically: 6.1-7.5
   - Remediation: Context-aware output encoding, upgrade libraries

5. **CWE-611: XML External Entity (XXE)**
   - Found in: XML parsers (dom4j, Xerces, etc.)
   - CVSS typically: 7.5-9.1
   - Remediation: Disable external entity processing, upgrade parsers

## Dependency Vulnerability Categories

### Remote Code Execution (RCE)

**Severity**: CRITICAL
**CVSS Range**: 9.0-10.0

**Common Patterns**:
- Deserialization vulnerabilities
- Template injection
- Expression language injection
- JNDI injection (Log4Shell)

**Remediation Priority**: IMMEDIATE

### Authentication Bypass

**Severity**: CRITICAL/HIGH
**CVSS Range**: 7.5-9.8

**Common Patterns**:
- JWT signature bypass
- OAuth implementation flaws
- Session fixation
- Hard-coded credentials

**Remediation Priority**: IMMEDIATE

### Information Disclosure

**Severity**: MEDIUM/HIGH
**CVSS Range**: 5.3-7.5

**Common Patterns**:
- Path traversal in file handlers
- XXE with data exfiltration
- Error messages exposing internals
- Memory disclosure bugs

**Remediation Priority**: HIGH

### Denial of Service (DoS)

**Severity**: MEDIUM
**CVSS Range**: 5.3-7.5

**Common Patterns**:
- Regular expression DoS (ReDoS)
- XML bomb attacks
- Resource exhaustion
- Algorithmic complexity attacks

**Remediation Priority**: MEDIUM (unless affecting critical services)

### Prototype Pollution (JavaScript)

**Severity**: HIGH
**CVSS Range**: 7.0-8.8

**Common Patterns**:
- Object merge/extend functions
- JSON parsing libraries
- Template engines

**Remediation Priority**: HIGH

## Supply Chain Attack Patterns

### Dependency Confusion

**CWE**: CWE-494 (Download of Code Without Integrity Check)

**Description**: Attacker publishes malicious package with same name as internal package to public registry.

**Detection**: Black Duck detects unexpected package sources and registry changes.

**Mitigation**:
- Use private registry with higher priority
- Implement package name reservations
- Enable registry allowlists

### Typosquatting

**CWE**: CWE-829 (Inclusion of Functionality from Untrusted Control Sphere)

**Description**: Malicious packages with names similar to popular packages.

**Detection**: Component quality analysis, community reputation scoring.

**Mitigation**:
- Review all new dependencies carefully
- Use dependency lock files
- Enable automated typosquatting detection

### Compromised Maintainer Accounts

**CWE**: CWE-1294 (Insecure Security Identifier Mechanism)

**Description**: Attacker gains access to legitimate package maintainer account.

**Detection**: Unexpected version updates, behavior changes, new maintainers.

**Mitigation**:
- Pin dependency versions
- Review all dependency updates
- Monitor for suspicious changes

## Remediation Priority Matrix

| Severity | Exploitability | Remediation Timeline |
|----------|---------------|---------------------|
| CRITICAL | High | 24-48 hours |
| HIGH | High | 1 week |
| HIGH | Low | 2 weeks |
| MEDIUM | High | 1 month |
| MEDIUM | Low | 3 months |
| LOW | Any | Next maintenance cycle |

**Factors influencing priority**:
- Exploit availability (PoC, Metasploit module, etc.)
- Attack surface (internet-facing vs. internal)
- Data sensitivity
- Compliance requirements
- Patch availability

## References

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NVD CVE Database](https://nvd.nist.gov/)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [FIRST CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
