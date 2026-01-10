# Vulnerability Remediation Guide

Security remediation patterns organized by vulnerability category.

## Table of Contents

- [SQL Injection](#sql-injection)
- [Cross-Site Scripting (XSS)](#cross-site-scripting-xss)
- [Command Injection](#command-injection)
- [Path Traversal](#path-traversal)
- [Insecure Deserialization](#insecure-deserialization)
- [Weak Cryptography](#weak-cryptography)
- [Authentication & Session Management](#authentication--session-management)
- [CSRF](#csrf)
- [SSRF](#ssrf)
- [XXE](#xxe)

## SQL Injection

### Vulnerability Pattern
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

### Secure Remediation
```python
# SECURE: Use parameterized queries
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# Or use ORM
user = User.objects.get(id=user_id)
```

### Framework-Specific Solutions

**Django:**
```python
# Use Django ORM (safe by default)
User.objects.filter(email=user_email)

# For raw SQL, use parameterized queries
User.objects.raw('SELECT * FROM myapp_user WHERE email = %s', [user_email])
```

**Node.js (Sequelize):**
```javascript
// Use parameterized queries
User.findAll({
  where: { email: userEmail }
});

// Or use replacements
sequelize.query(
  'SELECT * FROM users WHERE email = :email',
  { replacements: { email: userEmail } }
);
```

**Java (JDBC):**
```java
// Use PreparedStatement
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement stmt = conn.prepareStatement(query);
stmt.setInt(1, userId);
ResultSet rs = stmt.executeQuery();
```

## Cross-Site Scripting (XSS)

### Vulnerability Pattern
```javascript
// VULNERABLE
element.innerHTML = userInput;
document.write(userInput);
```

### Secure Remediation
```javascript
// SECURE: Use textContent for text
element.textContent = userInput;

// Or properly escape HTML
element.innerHTML = escapeHtml(userInput);

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
```

### Framework-Specific Solutions

**React:**
```javascript
// React auto-escapes by default
<div>{userInput}</div>

// For HTML content, sanitize first
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

**Flask/Jinja2:**
```python
# Templates auto-escape by default
{{ user_input }}

# For HTML content, sanitize
from markupsafe import Markup
import bleach
{{ Markup(bleach.clean(user_input)) }}
```

**Django:**
```django
{# Auto-escaped by default #}
{{ user_input }}

{# Mark as safe only after sanitization #}
{{ user_input|safe }}
```

## Command Injection

### Vulnerability Pattern
```python
# VULNERABLE
os.system(f"ping {user_host}")
subprocess.call(f"ls {user_directory}", shell=True)
```

### Secure Remediation
```python
# SECURE: Use subprocess with list arguments
import subprocess
subprocess.run(['ping', '-c', '1', user_host],
               capture_output=True, check=True)

# Validate input against allowlist
import shlex
if not re.match(r'^[a-zA-Z0-9.-]+$', user_host):
    raise ValueError("Invalid hostname")
subprocess.run(['ping', '-c', '1', user_host])
```

**Node.js:**
```javascript
// VULNERABLE
exec(`ls ${userDir}`);

// SECURE
const { execFile } = require('child_process');
execFile('ls', [userDir], (error, stdout) => {
  // Handle output
});
```

## Path Traversal

### Vulnerability Pattern
```python
# VULNERABLE
file_path = os.path.join('/uploads', user_filename)
with open(file_path) as f:
    return f.read()
```

### Secure Remediation
```python
# SECURE: Validate and normalize path
import os
from pathlib import Path

def safe_join(directory, user_path):
    # Normalize and resolve path
    base_dir = Path(directory).resolve()
    file_path = (base_dir / user_path).resolve()

    # Ensure it's within base directory
    if not str(file_path).startswith(str(base_dir)):
        raise ValueError("Path traversal detected")

    return file_path

try:
    safe_path = safe_join('/uploads', user_filename)
    with open(safe_path) as f:
        return f.read()
except ValueError:
    return "Invalid filename"
```

## Insecure Deserialization

### Vulnerability Pattern
```python
# VULNERABLE
import pickle
data = pickle.loads(user_data)
```

### Secure Remediation
```python
# SECURE: Use safe formats like JSON
import json
data = json.loads(user_data)

# If you must deserialize, validate and restrict
import yaml
data = yaml.safe_load(user_data)  # Use safe_load, not load
```

**Node.js:**
```javascript
// VULNERABLE
const data = eval(userInput);
const obj = Function(userInput)();

// SECURE
const data = JSON.parse(userInput);

// For complex objects, use schema validation
const Joi = require('joi');
const schema = Joi.object({
  name: Joi.string().required(),
  email: Joi.string().email().required()
});
const { value, error } = schema.validate(JSON.parse(userInput));
```

## Weak Cryptography

### Vulnerability Pattern
```python
# VULNERABLE
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
```

### Secure Remediation
```python
# SECURE: Use bcrypt or argon2
import bcrypt

# Hashing
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verification
if bcrypt.checkpw(password.encode(), stored_hash):
    print("Password correct")

# Or use argon2
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
ph.verify(hash, password)
```

**Encryption:**
```python
# VULNERABLE
from Crypto.Cipher import DES
cipher = DES.new(key, DES.MODE_ECB)

# SECURE: Use AES-GCM
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
```

## Authentication & Session Management

### Vulnerability Pattern
```javascript
// VULNERABLE
app.use(session({
  secret: 'weak-secret',
  cookie: { secure: false }
}));
```

### Secure Remediation
```javascript
// SECURE
const session = require('express-session');
app.use(session({
  secret: process.env.SESSION_SECRET, // Strong random secret
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,      // HTTPS only
    httpOnly: true,    // No JavaScript access
    sameSite: 'strict', // CSRF protection
    maxAge: 3600000    // 1 hour
  }
}));
```

**Password Requirements:**
```python
# Implement strong password policy
import re

def validate_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

## CSRF

### Vulnerability Pattern
```python
# VULNERABLE: No CSRF protection
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    # Process transfer
```

### Secure Remediation
```python
# SECURE: Use CSRF tokens
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
@csrf.exempt  # Only if using custom CSRF
def transfer():
    # CSRF token automatically validated
    amount = request.form['amount']
    to_account = request.form['to']
```

**Express.js:**
```javascript
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.post('/transfer', csrfProtection, (req, res) => {
  // CSRF token validated
  const { amount, to } = req.body;
});
```

## SSRF

### Vulnerability Pattern
```python
# VULNERABLE
import requests
url = request.args.get('url')
response = requests.get(url)
```

### Secure Remediation
```python
# SECURE: Validate URLs and use allowlist
import requests
from urllib.parse import urlparse

ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

def safe_fetch(url):
    parsed = urlparse(url)

    # Check protocol
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("Invalid protocol")

    # Check domain against allowlist
    if parsed.netloc not in ALLOWED_DOMAINS:
        raise ValueError("Domain not allowed")

    # Block internal IPs
    import ipaddress
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private:
            raise ValueError("Private IP not allowed")
    except ValueError:
        pass  # Not an IP, continue

    return requests.get(url, timeout=5)
```

## XXE

### Vulnerability Pattern
```python
# VULNERABLE
from lxml import etree
tree = etree.parse(user_xml)
```

### Secure Remediation
```python
# SECURE: Disable external entities
from lxml import etree

parser = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    dtd_validation=False
)
tree = etree.parse(user_xml, parser)

# Or use defusedxml
from defusedxml import ElementTree
tree = ElementTree.parse(user_xml)
```

**Node.js:**
```javascript
// Use secure XML parser
const libxmljs = require('libxmljs');
const xml = libxmljs.parseXml(userXml, {
  noent: false,  // Disable entity expansion
  dtdload: false,
  dtdvalid: false
});
```

## General Security Principles

1. **Input Validation**: Validate all user input against expected format
2. **Output Encoding**: Encode output based on context (HTML, URL, SQL, etc.)
3. **Least Privilege**: Grant minimum necessary permissions
4. **Defense in Depth**: Use multiple layers of security controls
5. **Fail Securely**: Ensure failures don't expose sensitive data
6. **Secure Defaults**: Use secure configuration by default
7. **Keep Dependencies Updated**: Regularly update libraries and frameworks

## Testing Remediation

After applying fixes:

1. **Verify with Semgrep**: Re-scan to ensure vulnerability is resolved
   ```bash
   semgrep --config <ruleset> fixed_file.py
   ```

2. **Manual Testing**: Attempt to exploit the vulnerability
3. **Code Review**: Have peer review the fix
4. **Integration Tests**: Add tests to prevent regression

## References

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE Mitigations](https://cwe.mitre.org/)
- [Semgrep Autofix](https://semgrep.dev/docs/writing-rules/autofix/)
