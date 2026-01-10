# Nuclei Template Development Guide

## Table of Contents
- [Template Structure](#template-structure)
- [Template Types](#template-types)
- [Matchers and Extractors](#matchers-and-extractors)
- [Advanced Techniques](#advanced-techniques)
- [Testing and Validation](#testing-and-validation)
- [Best Practices](#best-practices)

## Template Structure

### Basic Template Anatomy

```yaml
id: unique-template-id
info:
  name: Human-readable template name
  author: your-name
  severity: critical|high|medium|low|info
  description: Detailed description of what this template detects
  reference:
    - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-XXXXX
    - https://nvd.nist.gov/vuln/detail/CVE-2024-XXXXX
  tags: cve,owasp,misconfig,custom

# Template type: http, dns, network, file, etc.
http:
  - method: GET
    path:
      - "{{BaseURL}}/vulnerable-endpoint"

    matchers:
      - type: status
        status:
          - 200

      - type: word
        words:
          - "vulnerable signature"
```

### Required Fields

- **id**: Unique identifier (kebab-case, organization-scoped for custom templates)
- **info.name**: Clear, descriptive name
- **info.author**: Template author
- **info.severity**: One of: critical, high, medium, low, info
- **info.description**: What vulnerability this detects
- **info.tags**: Searchable tags for filtering

### Optional but Recommended Fields

- **info.reference**: Links to CVE, advisories, documentation
- **info.classification**: CWE, CVE, OWASP mappings
- **info.metadata**: Additional metadata (max-request, verified, etc.)

## Template Types

### HTTP Templates

Most common template type for web application testing:

```yaml
id: http-example
info:
  name: HTTP Template Example
  author: security-team
  severity: high
  tags: web,http

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/users"
      - "{{BaseURL}}/api/admin"

    headers:
      Authorization: "Bearer {{token}}"

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200

      - type: word
        part: body
        words:
          - "\"role\":\"admin\""
          - "sensitive_data"

    extractors:
      - type: regex
        name: user_ids
        regex:
          - '"id":([0-9]+)'
```

### DNS Templates

Test for DNS misconfigurations and subdomain takeovers:

```yaml
id: dns-takeover-check
info:
  name: DNS Subdomain Takeover Detection
  author: security-team
  severity: high
  tags: dns,takeover

dns:
  - name: "{{FQDN}}"
    type: CNAME

    matchers:
      - type: word
        words:
          - "amazonaws.com"
          - "azurewebsites.net"
          - "herokuapp.com"
```

### Network Templates

TCP/UDP port scanning and service detection:

```yaml
id: exposed-redis
info:
  name: Exposed Redis Instance
  author: security-team
  severity: critical
  tags: network,redis,exposure

network:
  - inputs:
      - data: "*1\r\n$4\r\ninfo\r\n"

    host:
      - "{{Hostname}}"
      - "{{Hostname}}:6379"

    matchers:
      - type: word
        words:
          - "redis_version"
```

## Matchers and Extractors

### Matcher Types

#### Status Matcher
```yaml
matchers:
  - type: status
    status:
      - 200
      - 201
    condition: or
```

#### Word Matcher
```yaml
matchers:
  - type: word
    part: body  # body, header, all
    words:
      - "error"
      - "exception"
    condition: and
    case-insensitive: true
```

#### Regex Matcher
```yaml
matchers:
  - type: regex
    regex:
      - "(?i)password\\s*=\\s*['\"]([^'\"]+)['\"]"
    part: body
```

#### Binary Matcher
```yaml
matchers:
  - type: binary
    binary:
      - "504B0304"  # ZIP file signature (hex)
    part: body
```

#### DSL Matcher (Dynamic Expressions)
```yaml
matchers:
  - type: dsl
    dsl:
      - "status_code == 200 && len(body) > 1000"
      - "contains(tolower(body), 'admin')"
```

### Matcher Conditions

- **and**: All matchers must match
- **or**: At least one matcher must match (default)

```yaml
matchers-condition: and
matchers:
  - type: status
    status:
      - 200
  - type: word
    words:
      - "admin"
```

### Extractors

Extract data from responses for reporting or chaining:

#### Regex Extractor
```yaml
extractors:
  - type: regex
    name: api_keys
    part: body
    regex:
      - 'api[_-]?key["\s:=]+([a-zA-Z0-9_-]{32,})'
    group: 1
```

#### JSON Extractor
```yaml
extractors:
  - type: json
    name: user_data
    json:
      - ".users[].email"
      - ".users[].id"
```

#### XPath Extractor
```yaml
extractors:
  - type: xpath
    name: titles
    xpath:
      - "//title"
```

## Advanced Techniques

### Request Chaining (Workflows)

Execute templates in sequence, passing data between them:

```yaml
id: workflow-example
info:
  name: Multi-Step Authentication Test
  author: security-team

workflows:
  templates:
    - template: login.yaml
    - template: fetch-user-data.yaml
```

**login.yaml**:
```yaml
id: login-template
info:
  name: Login and Extract Token
  author: security-team
  severity: info

http:
  - method: POST
    path:
      - "{{BaseURL}}/api/login"

    body: '{"username":"test","password":"test"}'

    extractors:
      - type: json
        name: auth_token
        json:
          - ".token"
        internal: true  # Pass to next template
```

### Variables and Helpers

Use dynamic variables and helper functions:

```yaml
http:
  - method: GET
    path:
      - "{{BaseURL}}/api/users/{{username}}"

    # Available variables:
    # {{BaseURL}}, {{Hostname}}, {{Host}}, {{Port}}, {{Path}}
    # {{RootURL}}, {{Scheme}}, {{username}} (from previous extractor)

    matchers:
      - type: dsl
        dsl:
          # Helper functions: len(), contains(), regex_match(), etc.
          - 'len(body) > 500'
          - 'contains(tolower(header), "x-api-key")'
          - 'status_code >= 200 && status_code < 300'
```

### Payloads and Fuzzing

Use payload files for fuzzing:

```yaml
id: sqli-fuzzing
info:
  name: SQL Injection Fuzzing
  author: security-team
  severity: critical

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/users?id={{payload}}"

    payloads:
      payload:
        - "1' OR '1'='1"
        - "1' UNION SELECT NULL--"
        - "'; DROP TABLE users--"

    matchers:
      - type: word
        words:
          - "SQL syntax"
          - "mysql_fetch"
          - "ORA-01756"
```

Or use external payload file:

```yaml
payloads:
  payload: payloads/sql-injection.txt

attack: clusterbomb  # pitchfork, clusterbomb, batteringram
```

### Rate Limiting and Threads

Control request rate to avoid overwhelming targets:

```yaml
id: rate-limited-scan
info:
  name: Rate-Limited Vulnerability Scan
  author: security-team
  severity: medium
  metadata:
    max-request: 50  # Maximum requests per template execution

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/endpoint"

    threads: 5  # Concurrent requests (default: 25)
```

## Testing and Validation

### Local Testing

Test templates against local test servers:

```bash
# Test single template
nuclei -t custom-templates/my-template.yaml -u http://localhost:8080 -debug

# Validate template syntax
nuclei -t custom-templates/my-template.yaml -validate

# Test with verbose output
nuclei -t custom-templates/my-template.yaml -u https://target.com -verbose
```

### Template Validation

Use the bundled validation script:

```bash
python3 scripts/template_validator.py custom-templates/my-template.yaml
```

### Test Lab Setup

Create a vulnerable test application for template development:

```bash
# Use DVWA (Damn Vulnerable Web Application)
docker run -d -p 80:80 vulnerables/web-dvwa

# Or OWASP Juice Shop
docker run -d -p 3000:3000 bkimminich/juice-shop
```

## Best Practices

### 1. Accurate Severity Classification

- **Critical**: RCE, authentication bypass, full system compromise
- **High**: SQL injection, XSS, significant data exposure
- **Medium**: Missing security headers, information disclosure
- **Low**: Minor misconfigurations, best practice violations
- **Info**: Technology detection, non-security findings

### 2. Minimize False Positives

```yaml
# Use multiple matchers with AND condition
matchers-condition: and
matchers:
  - type: status
    status:
      - 200

  - type: word
    words:
      - "admin"
      - "dashboard"
    condition: and

  - type: regex
    regex:
      - '<title>.*Admin.*Panel.*</title>'
    case-insensitive: true
```

### 3. Clear Naming Conventions

- **id**: `organization-vulnerability-type-identifier`
  - Example: `acme-api-key-exposure-config`
- **name**: Descriptive, clear purpose
  - Example: "ACME Corp API Key Exposure in Config Endpoint"

### 4. Comprehensive Documentation

```yaml
info:
  name: Detailed Template Name
  description: |
    Comprehensive description of what this template detects,
    why it's important, and how it works.

    References:
    - CVE-2024-XXXXX
    - Internal ticket: SEC-1234

  reference:
    - https://nvd.nist.gov/vuln/detail/CVE-2024-XXXXX
    - https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-XXXXX

  classification:
    cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
    cvss-score: 9.8
    cve-id: CVE-2024-XXXXX
    cwe-id: CWE-89

  metadata:
    verified: true
    max-request: 10
    shodan-query: 'http.title:"Admin Panel"'

  tags: cve,owasp,sqli,high-severity,verified
```

### 5. Responsible Testing Parameters

```yaml
# Avoid aggressive fuzzing in default templates
info:
  metadata:
    max-request: 10  # Limit total requests

http:
  - method: GET
    threads: 5  # Limit concurrent requests

    # Use specific, targeted payloads
    payloads:
      test: ["safe-payload-1", "safe-payload-2"]
```

### 6. Error Handling

```yaml
http:
  - method: GET
    path:
      - "{{BaseURL}}/api/test"

    # Handle various response scenarios
    matchers:
      - type: dsl
        dsl:
          - "status_code == 200 && contains(body, 'vulnerable')"
          - "status_code == 500 && contains(body, 'error')"
        condition: or

    # Negative matchers (must NOT match)
    matchers:
      - type: word
        negative: true
        words:
          - "404 Not Found"
          - "403 Forbidden"
```

### 7. Template Organization

```
custom-templates/
├── api/
│   ├── api-key-exposure.yaml
│   ├── graphql-introspection.yaml
│   └── rest-api-misconfig.yaml
├── cves/
│   ├── 2024/
│   │   ├── CVE-2024-12345.yaml
│   │   └── CVE-2024-67890.yaml
├── exposures/
│   ├── sensitive-files.yaml
│   └── backup-exposure.yaml
└── misconfig/
    ├── cors-misconfiguration.yaml
    └── debug-mode-enabled.yaml
```

### 8. Version Control and Maintenance

- Use Git to track template changes
- Tag templates with version numbers in metadata
- Document changes in template comments
- Regularly test templates against updated applications

```yaml
info:
  metadata:
    version: 1.2.0
    last-updated: 2024-11-20
    changelog: |
      1.2.0 - Added additional matcher for new vulnerability variant
      1.1.0 - Improved regex pattern to reduce false positives
      1.0.0 - Initial release
```

## Example: Complete Custom Template

```yaml
id: acme-corp-api-debug-exposure
info:
  name: ACME Corp API Debug Endpoint Exposure
  author: acme-security-team
  severity: high
  description: |
    Detects exposed debug endpoint in ACME Corp API that leaks
    sensitive configuration including database credentials,
    API keys, and internal service URLs.

  reference:
    - https://internal-wiki.acme.com/security/SEC-1234

  classification:
    cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
    cvss-score: 7.5
    cwe-id: CWE-200

  metadata:
    verified: true
    max-request: 3
    version: 1.0.0

  tags: acme,api,exposure,debug,high-severity

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/v1/debug/config"
      - "{{BaseURL}}/api/v2/debug/config"
      - "{{BaseURL}}/debug/config"

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200

      - type: word
        part: body
        words:
          - "database_url"
          - "api_secret_key"
        condition: or

      - type: regex
        part: body
        regex:
          - '"(password|secret|token)":\s*"[^"]+"'

    extractors:
      - type: regex
        name: exposed_secrets
        part: body
        regex:
          - '"(database_url|api_secret_key|jwt_secret)":\s*"([^"]+)"'
        group: 2

      - type: json
        name: config_data
        json:
          - ".database_url"
          - ".api_secret_key"
```

## Resources

- [Official Nuclei Template Guide](https://docs.projectdiscovery.io/templates/introduction)
- [Nuclei Templates Repository](https://github.com/projectdiscovery/nuclei-templates)
- [Template Editor](https://templates.nuclei.sh/)
- [DSL Functions Reference](https://docs.projectdiscovery.io/templates/reference/matchers#dsl-matcher)
