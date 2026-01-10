# Reference Document Template

This file demonstrates how to structure detailed reference material that Claude loads on-demand.

**When to use this reference**: Include a clear statement about when Claude should consult this document.
For example: "Consult this reference when analyzing Python code for security vulnerabilities and needing detailed remediation patterns."

**Document purpose**: Briefly explain what this reference provides that's not in SKILL.md.

---

## Table of Contents

**For documents >100 lines, always include a table of contents** to help Claude navigate quickly.

- [When to Use References](#when-to-use-references)
- [Document Organization](#document-organization)
- [Detailed Technical Content](#detailed-technical-content)
- [Security Framework Mappings](#security-framework-mappings)
  - [OWASP Top 10](#owasp-top-10)
  - [CWE Mappings](#cwe-mappings)
  - [MITRE ATT&CK](#mitre-attck)
- [Remediation Patterns](#remediation-patterns)
- [Advanced Configuration](#advanced-configuration)
- [Examples and Code Samples](#examples-and-code-samples)

---

## When to Use References

**Move content from SKILL.md to references/** when:

1. **Content exceeds 100 lines** - Keep SKILL.md concise
2. **Framework-specific details** - Detailed OWASP/CWE/MITRE mappings
3. **Advanced user content** - Deep technical details for expert users
4. **Lookup-oriented content** - Rule libraries, configuration matrices, comprehensive lists
5. **Language-specific patterns** - Separate files per language/framework
6. **Historical context** - Old patterns and deprecated approaches

**Keep in SKILL.md**:
- Core workflows (top 3-5 use cases)
- Decision points and branching logic
- Quick start guidance
- Essential security considerations

---

## Document Organization

### Structure for Long Documents

For references >100 lines:

```markdown
# Title

**When to use**: Clear trigger statement
**Purpose**: What this provides

## Table of Contents
- Links to all major sections

## Quick Reference
- Key facts or commands for fast lookup

## Detailed Content
- Comprehensive information organized logically

## Framework Mappings
- OWASP, CWE, MITRE ATT&CK references

## Examples
- Code samples and patterns
```

### Section Naming Conventions

- Use **imperative** or **declarative** headings
- ✅ "Detecting SQL Injection" not "How to detect SQL Injection"
- ✅ "Common Patterns" not "These are common patterns"
- Make headings **searchable** and **specific**

---

## Detailed Technical Content

This section demonstrates the type of detailed content that belongs in references rather than SKILL.md.

### Example: Comprehensive Vulnerability Detection

#### SQL Injection Detection Patterns

**Pattern 1: String Concatenation in Queries**

```python
# Vulnerable pattern
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(query)

# Detection criteria:
# - SQL keyword (SELECT, INSERT, UPDATE, DELETE)
# - String concatenation operator (+, f-string)
# - Variable user input (request params, form data)

# Severity: HIGH
# CWE: CWE-89
# OWASP: A03:2021 - Injection
```

**Remediation**:
```python
# Fixed: Parameterized query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# OR using ORM
user = User.objects.get(id=user_id)
```

**Pattern 2: Unsafe String Formatting**

```python
# Vulnerable patterns
query = f"SELECT * FROM users WHERE name = '{username}'"
query = "SELECT * FROM users WHERE name = '%s'" % username
query = "SELECT * FROM users WHERE name = '{}'".format(username)

# All three patterns are vulnerable to SQL injection
```

#### Cross-Site Scripting (XSS) Detection

**Pattern 1: Unescaped Output in Templates**

```javascript
// Vulnerable: Direct HTML injection
element.innerHTML = userInput;
document.write(userInput);

// Vulnerable: React dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userComment}} />

// Detection criteria:
# - Direct DOM manipulation (innerHTML, document.write)
# - React dangerouslySetInnerHTML with user data
# - Template engines with autoescaping disabled

// Severity: HIGH
// CWE: CWE-79
// OWASP: A03:2021 - Injection
```

**Remediation**:
```javascript
// Fixed: Escaped output
element.textContent = userInput;  // Auto-escapes

// Fixed: Sanitization library
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(userComment);
<div dangerouslySetInnerHTML={{__html: clean}} />
```

---

## Security Framework Mappings

This section provides comprehensive security framework mappings for findings.

### OWASP Top 10

Map security findings to OWASP Top 10 (2021) categories:

| Category | Title | Common Vulnerabilities |
|----------|-------|----------------------|
| **A01:2021** | Broken Access Control | Authorization bypass, privilege escalation, IDOR |
| **A02:2021** | Cryptographic Failures | Weak crypto, plaintext storage, insecure TLS |
| **A03:2021** | Injection | SQL injection, XSS, command injection, LDAP injection |
| **A04:2021** | Insecure Design | Missing security controls, threat modeling gaps |
| **A05:2021** | Security Misconfiguration | Default configs, verbose errors, unnecessary features |
| **A06:2021** | Vulnerable Components | Outdated libraries, unpatched dependencies |
| **A07:2021** | Auth & Session Failures | Weak passwords, session fixation, missing MFA |
| **A08:2021** | Software & Data Integrity | Unsigned updates, insecure CI/CD, deserialization |
| **A09:2021** | Logging & Monitoring Failures | Insufficient logging, no alerting, log injection |
| **A10:2021** | SSRF | Server-side request forgery, unvalidated redirects |

**Usage**: When reporting findings, map to primary OWASP category and reference the identifier (e.g., "A03:2021 - Injection").

### CWE Mappings

Map to relevant Common Weakness Enumeration categories for precise vulnerability classification:

#### Injection Vulnerabilities
- **CWE-78**: OS Command Injection
- **CWE-79**: Cross-site Scripting (XSS)
- **CWE-89**: SQL Injection
- **CWE-90**: LDAP Injection
- **CWE-91**: XML Injection
- **CWE-94**: Code Injection

#### Authentication & Authorization
- **CWE-287**: Improper Authentication
- **CWE-288**: Authentication Bypass Using Alternate Path
- **CWE-290**: Authentication Bypass by Spoofing
- **CWE-294**: Authentication Bypass by Capture-replay
- **CWE-306**: Missing Authentication for Critical Function
- **CWE-307**: Improper Restriction of Excessive Authentication Attempts
- **CWE-352**: Cross-Site Request Forgery (CSRF)

#### Cryptographic Issues
- **CWE-256**: Plaintext Storage of Password
- **CWE-259**: Use of Hard-coded Password
- **CWE-261**: Weak Encoding for Password
- **CWE-321**: Use of Hard-coded Cryptographic Key
- **CWE-326**: Inadequate Encryption Strength
- **CWE-327**: Use of Broken or Risky Cryptographic Algorithm
- **CWE-329**: Not Using a Random IV with CBC Mode
- **CWE-798**: Use of Hard-coded Credentials

#### Input Validation
- **CWE-20**: Improper Input Validation
- **CWE-73**: External Control of File Name or Path
- **CWE-434**: Unrestricted Upload of File with Dangerous Type
- **CWE-601**: URL Redirection to Untrusted Site

#### Sensitive Data Exposure
- **CWE-200**: Information Exposure
- **CWE-209**: Information Exposure Through Error Message
- **CWE-312**: Cleartext Storage of Sensitive Information
- **CWE-319**: Cleartext Transmission of Sensitive Information
- **CWE-532**: Information Exposure Through Log Files

**Usage**: Include CWE identifier in all vulnerability reports for standardized classification.

### MITRE ATT&CK

Reference relevant tactics and techniques for threat context:

#### Initial Access (TA0001)
- **T1190**: Exploit Public-Facing Application
- **T1133**: External Remote Services
- **T1078**: Valid Accounts

#### Execution (TA0002)
- **T1059**: Command and Scripting Interpreter
- **T1203**: Exploitation for Client Execution

#### Persistence (TA0003)
- **T1098**: Account Manipulation
- **T1136**: Create Account
- **T1505**: Server Software Component

#### Privilege Escalation (TA0004)
- **T1068**: Exploitation for Privilege Escalation
- **T1548**: Abuse Elevation Control Mechanism

#### Defense Evasion (TA0005)
- **T1027**: Obfuscated Files or Information
- **T1140**: Deobfuscate/Decode Files or Information
- **T1562**: Impair Defenses

#### Credential Access (TA0006)
- **T1110**: Brute Force
- **T1555**: Credentials from Password Stores
- **T1552**: Unsecured Credentials

#### Discovery (TA0007)
- **T1083**: File and Directory Discovery
- **T1046**: Network Service Scanning

#### Collection (TA0009)
- **T1005**: Data from Local System
- **T1114**: Email Collection

#### Exfiltration (TA0010)
- **T1041**: Exfiltration Over C2 Channel
- **T1567**: Exfiltration Over Web Service

**Usage**: When identifying vulnerabilities, consider which ATT&CK techniques an attacker could use to exploit them.

---

## Remediation Patterns

This section provides specific remediation guidance for common vulnerability types.

### SQL Injection Remediation

**Step 1: Identify vulnerable queries**
- Search for string concatenation in SQL queries
- Check for f-strings or format() with SQL keywords
- Review all database interaction code

**Step 2: Apply parameterized queries**

```python
# Python with sqlite3
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# Python with psycopg2 (PostgreSQL)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Python with SQLAlchemy (ORM)
from sqlalchemy import text
result = session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

**Step 3: Validate and sanitize input** (defense in depth)
```python
import re

# Validate input format
if not re.match(r'^\d+$', user_id):
    raise ValueError("Invalid user ID format")

# Use ORM query builders
user = User.query.filter_by(id=user_id).first()
```

**Step 4: Implement least privilege**
- Database user should have minimum required permissions
- Use read-only accounts for SELECT operations
- Never use admin/root accounts for application queries

### XSS Remediation

**Step 1: Enable auto-escaping**
- Most modern frameworks escape by default
- Ensure auto-escaping is not disabled

**Step 2: Use framework-specific safe methods**

```javascript
// React: Use JSX (auto-escapes)
<div>{userInput}</div>

// Vue: Use template syntax (auto-escapes)
<div>{{ userInput }}</div>

// Angular: Use property binding (auto-escapes)
<div [textContent]="userInput"></div>
```

**Step 3: Sanitize when HTML is required**

```javascript
import DOMPurify from 'dompurify';

// Sanitize HTML content
const clean = DOMPurify.sanitize(userHTML, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p'],
  ALLOWED_ATTR: []
});
```

**Step 4: Content Security Policy (CSP)**

```html
<!-- Add CSP header -->
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'
```

---

## Advanced Configuration

This section contains detailed configuration options and tuning parameters.

### Example: SAST Tool Configuration

```yaml
# Advanced security scanner configuration
scanner:
  # Severity threshold
  severity_threshold: MEDIUM

  # Rule configuration
  rules:
    enabled:
      - sql-injection
      - xss
      - hardcoded-secrets
    disabled:
      - informational-only

  # False positive reduction
  confidence_threshold: HIGH
  exclude_patterns:
    - "*/test/*"
    - "*/tests/*"
    - "*/node_modules/*"
    - "*.test.js"
    - "*.spec.ts"

  # Performance tuning
  max_file_size_kb: 2048
  timeout_seconds: 300
  parallel_jobs: 4

  # Output configuration
  output_format: json
  include_code_snippets: true
  max_snippet_lines: 10
```

---

## Examples and Code Samples

This section provides comprehensive code examples for various scenarios.

### Example 1: Secure API Authentication

```python
# Secure API key handling
import os
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load API key from environment (never hardcode)
VALID_API_KEY = os.environ.get('API_KEY')
if not VALID_API_KEY:
    raise ValueError("API_KEY environment variable not set")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'API key required'}), 401

        # Constant-time comparison to prevent timing attacks
        import hmac
        if not hmac.compare_digest(api_key, VALID_API_KEY):
            return jsonify({'error': 'Invalid API key'}), 403

        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/secure-endpoint')
@require_api_key
def secure_endpoint():
    return jsonify({'message': 'Access granted'})
```

### Example 2: Secure Password Hashing

```python
# Secure password storage with bcrypt
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)  # Cost factor: 12 (industry standard)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )

# Usage
stored_hash = hash_password("user_password")
is_valid = verify_password("user_password", stored_hash)  # True
```

### Example 3: Secure File Upload

```python
# Secure file upload with validation
import os
import magic
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png',
    'image/jpeg'
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def is_allowed_file(filename: str, file_content: bytes) -> bool:
    """Validate file extension and MIME type."""
    # Check extension
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False

    # Check MIME type (prevent extension spoofing)
    mime = magic.from_buffer(file_content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        return False

    return True

def handle_upload(file):
    """Securely handle file upload."""
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        raise ValueError("File too large")

    # Read content for validation
    content = file.read()
    file.seek(0)

    # Validate file type
    if not is_allowed_file(file.filename, content):
        raise ValueError("Invalid file type")

    # Sanitize filename
    filename = secure_filename(file.filename)

    # Generate unique filename to prevent overwrite attacks
    import uuid
    unique_filename = f"{uuid.uuid4()}_{filename}"

    # Save to secure location (outside web root)
    upload_path = os.path.join('/secure/uploads', unique_filename)
    file.save(upload_path)

    return unique_filename
```

---

## Best Practices for Reference Documents

1. **Start with "When to use"** - Help Claude know when to load this reference
2. **Include table of contents** - For documents >100 lines
3. **Use concrete examples** - Code samples with vulnerable and fixed versions
4. **Map to frameworks** - OWASP, CWE, MITRE ATT&CK for context
5. **Provide remediation** - Don't just identify issues, show how to fix them
6. **Organize logically** - Group related content, use clear headings
7. **Keep examples current** - Use modern patterns and current framework versions
8. **Be concise** - Even in references, challenge every sentence
