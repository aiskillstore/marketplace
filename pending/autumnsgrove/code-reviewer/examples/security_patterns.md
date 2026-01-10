# Security Patterns and Common Vulnerabilities

A comprehensive guide to identifying and fixing common security vulnerabilities in code reviews.

## Table of Contents

1. [Injection Attacks](#injection-attacks)
2. [Authentication & Authorization](#authentication--authorization)
3. [Sensitive Data Exposure](#sensitive-data-exposure)
4. [Security Misconfiguration](#security-misconfiguration)
5. [Cross-Site Scripting (XSS)](#cross-site-scripting-xss)
6. [Insecure Deserialization](#insecure-deserialization)
7. [Cryptographic Issues](#cryptographic-issues)
8. [Security Headers](#security-headers)

---

## Injection Attacks

### SQL Injection

**❌ Vulnerable Code:**
```python
# Python - String concatenation
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)

# SQL concatenation
username = request.form['username']
query = "SELECT * FROM users WHERE id = " + user_id
```

**✅ Secure Code:**
```python
# Python - Parameterized query
query = "SELECT * FROM users WHERE username = %s AND password = %s"
cursor.execute(query, (username, password))

# Using ORM (SQLAlchemy)
user = User.query.filter_by(username=username).first()

# Multiple parameters
query = "SELECT * FROM orders WHERE user_id = %s AND status = %s"
cursor.execute(query, (user_id, status))
```

**Detection Tips:**
- Look for string concatenation or f-strings in SQL queries
- Check for `.format()` or `+` operators with SQL
- Verify all user input is parameterized

### Command Injection

**❌ Vulnerable Code:**
```python
# Python - Unsafe shell execution
import os
filename = request.form['filename']
os.system(f"cat {filename}")

# JavaScript - Unsafe exec
eval(user_input)
exec(user_code)
```

**✅ Secure Code:**
```python
# Python - Safe subprocess usage
import subprocess
filename = request.form['filename']
# Validate filename first
if not is_valid_filename(filename):
    raise ValueError("Invalid filename")
subprocess.run(['cat', filename], check=True, shell=False)

# Avoid eval/exec entirely
# If necessary, use ast.literal_eval for data structures
import ast
data = ast.literal_eval(user_input)
```

**Prevention:**
- Never use `shell=True` with user input
- Whitelist valid inputs
- Use libraries instead of shell commands
- Avoid `eval()`, `exec()`, `Function()` with user input

### Path Traversal

**❌ Vulnerable Code:**
```python
# Python - Unsafe file access
filename = request.args.get('file')
with open(f'/uploads/{filename}', 'r') as f:
    content = f.read()

# User could pass: ../../../../etc/passwd
```

**✅ Secure Code:**
```python
import os
from pathlib import Path

filename = request.args.get('file')
# Resolve to absolute path
upload_dir = Path('/uploads').resolve()
file_path = (upload_dir / filename).resolve()

# Check if file is within allowed directory
if not str(file_path).startswith(str(upload_dir)):
    raise ValueError("Invalid file path")

with open(file_path, 'r') as f:
    content = f.read()
```

**Prevention:**
- Always validate and sanitize file paths
- Use absolute paths and check containment
- Implement whitelist of allowed files
- Don't expose internal directory structure

---

## Authentication & Authorization

### Broken Authentication

**❌ Vulnerable Code:**
```python
# Weak password hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# No password complexity requirements
if len(password) < 4:
    return "Password too short"

# Session without timeout
session['user_id'] = user.id
# No expiration set
```

**✅ Secure Code:**
```python
# Strong password hashing with bcrypt
import bcrypt

# Hashing
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verification
if bcrypt.checkpw(password.encode(), stored_hash):
    # Password correct
    pass

# Password requirements
def is_strong_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True

# Session with timeout
session['user_id'] = user.id
session.permanent = True
app.permanent_session_lifetime = timedelta(hours=1)
```

### Broken Access Control

**❌ Vulnerable Code:**
```python
# No authorization check
@app.route('/user/<user_id>/profile')
def view_profile(user_id):
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)
# Any logged-in user can view any profile!

# Insecure direct object reference
@app.route('/delete/<order_id>')
def delete_order(order_id):
    Order.query.filter_by(id=order_id).delete()
# No check if user owns the order!
```

**✅ Secure Code:**
```python
# Proper authorization
@app.route('/user/<user_id>/profile')
@login_required
def view_profile(user_id):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)  # Forbidden
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)

# Verify ownership
@app.route('/delete/<order_id>')
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)
    order.delete()
    return redirect('/orders')
```

---

## Sensitive Data Exposure

### Hardcoded Secrets

**❌ Vulnerable Code:**
```python
# Hardcoded credentials
API_KEY = "sk-abc123def456"
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# Committed .env file with secrets
# .env (in git)
SECRET_KEY=super-secret-key-12345
```

**✅ Secure Code:**
```python
# Environment variables
import os
API_KEY = os.environ.get('API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Secret management service
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)
api_key = client.get_secret("api-key").value

# .gitignore includes
.env
.env.local
secrets.json
credentials.json
```

### Information Disclosure

**❌ Vulnerable Code:**
```python
# Detailed error messages to users
try:
    process_payment(card_number)
except Exception as e:
    return f"Error: {str(e)}\nStack trace: {traceback.format_exc()}"

# Sensitive data in logs
logger.info(f"User {username} logged in with password {password}")
logger.debug(f"Credit card: {card_number}")
```

**✅ Secure Code:**
```python
# Generic error messages
try:
    process_payment(card_number)
except PaymentError as e:
    logger.error(f"Payment failed for user {user_id}: {e}", exc_info=True)
    return "Payment processing failed. Please try again."
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    return "An error occurred. Please contact support."

# Sanitized logging
logger.info(f"User {username} logged in successfully")
logger.debug(f"Credit card ending in: {card_number[-4:]}")
# Better: Don't log sensitive data at all
```

### Unencrypted Data Storage

**❌ Vulnerable Code:**
```python
# Storing sensitive data in plain text
user.ssn = request.form['ssn']
user.save()

# No encryption at rest
with open('sensitive_data.txt', 'w') as f:
    f.write(credit_card_number)
```

**✅ Secure Code:**
```python
# Encrypt sensitive fields
from cryptography.fernet import Fernet

class User(db.Model):
    ssn_encrypted = db.Column(db.LargeBinary)

    @property
    def ssn(self):
        cipher = Fernet(encryption_key)
        return cipher.decrypt(self.ssn_encrypted).decode()

    @ssn.setter
    def ssn(self, value):
        cipher = Fernet(encryption_key)
        self.ssn_encrypted = cipher.encrypt(value.encode())

# Use database encryption at rest
# PostgreSQL: Enable transparent data encryption
# MySQL: Use encrypted tablespaces
```

---

## Security Misconfiguration

### Debug Mode in Production

**❌ Vulnerable Code:**
```python
# Flask - Debug mode enabled
app.run(debug=True)

# Django - Debug in settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
```

**✅ Secure Code:**
```python
# Flask - Environment-based debug
debug_mode = os.environ.get('FLASK_ENV') == 'development'
app.run(debug=debug_mode)

# Django - Separate settings
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# settings/development.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### CORS Misconfiguration

**❌ Vulnerable Code:**
```python
# Flask-CORS - Allow all origins
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Express.js - Wildcard origin
app.use(cors({
  origin: '*',
  credentials: true  // Dangerous with wildcard!
}));
```

**✅ Secure Code:**
```python
# Flask-CORS - Specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://example.com", "https://app.example.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Express.js - Whitelist
const allowedOrigins = ['https://example.com'];
app.use(cors({
  origin: function(origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));
```

---

## Cross-Site Scripting (XSS)

### Reflected XSS

**❌ Vulnerable Code:**
```python
# Flask - Unescaped output
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"<h1>Search results for: {query}</h1>"
# User input: <script>alert('XSS')</script>

# JavaScript - innerHTML with user input
searchInput = document.getElementById('search').value;
resultsDiv.innerHTML = `<h2>Results for ${searchInput}</h2>`;
```

**✅ Secure Code:**
```python
# Flask - Auto-escaped templates
from flask import render_template, escape

@app.route('/search')
def search():
    query = request.args.get('q')
    return render_template('search.html', query=query)
# In template: <h1>Search results for: {{ query }}</h1>

# Manual escaping
return f"<h1>Search results for: {escape(query)}</h1>"

# JavaScript - textContent instead of innerHTML
searchInput = document.getElementById('search').value;
resultsDiv.textContent = `Results for ${searchInput}`;

// Or sanitize with DOMPurify
import DOMPurify from 'dompurify';
resultsDiv.innerHTML = DOMPurify.sanitize(`<h2>Results for ${searchInput}</h2>`);
```

### Content Security Policy

**✅ Secure Code:**
```python
# Flask - Add CSP header
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.example.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https://api.example.com; "
        "frame-ancestors 'none';"
    )
    return response
```

---

## Insecure Deserialization

**❌ Vulnerable Code:**
```python
# Python - Unsafe pickle
import pickle
user_data = pickle.loads(request.data)

# JavaScript - eval of JSON
const data = eval('(' + userInput + ')');

# PHP - unserialize
$data = unserialize($_POST['data']);
```

**✅ Secure Code:**
```python
# Python - Use JSON instead
import json
try:
    user_data = json.loads(request.data)
except json.JSONDecodeError:
    return "Invalid data", 400

# If pickle is necessary, sign it
import hmac
import hashlib

def secure_serialize(obj, secret_key):
    pickled = pickle.dumps(obj)
    signature = hmac.new(secret_key.encode(), pickled, hashlib.sha256).hexdigest()
    return signature + pickled.hex()

def secure_deserialize(data, secret_key):
    signature = data[:64]
    pickled = bytes.fromhex(data[64:])
    expected_sig = hmac.new(secret_key.encode(), pickled, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    return pickle.loads(pickled)

# JavaScript - JSON.parse (not eval)
const data = JSON.parse(userInput);
```

---

## Cryptographic Issues

### Weak Encryption

**❌ Vulnerable Code:**
```python
# Weak hashing algorithm
import hashlib
token = hashlib.md5(data.encode()).hexdigest()

# Custom encryption (never do this!)
def custom_encrypt(text, shift):
    return ''.join(chr(ord(c) + shift) for c in text)

# Weak key generation
secret_key = "12345678"
```

**✅ Secure Code:**
```python
# Strong hashing with salt
import hashlib
import secrets

salt = secrets.token_hex(16)
hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
password_hash = salt + hash_obj.hex()

# Use established crypto libraries
from cryptography.fernet import Fernet

# Generate strong key
key = Fernet.generate_key()

# Encrypt
cipher = Fernet(key)
encrypted = cipher.encrypt(data.encode())

# Decrypt
decrypted = cipher.decrypt(encrypted).decode()

# Secure random for tokens
token = secrets.token_urlsafe(32)
```

### Insufficient Randomness

**❌ Vulnerable Code:**
```python
# Weak random for security purposes
import random
session_id = random.randint(1000000, 9999999)
reset_token = str(random.random())
```

**✅ Secure Code:**
```python
# Cryptographically secure random
import secrets

session_id = secrets.token_hex(32)
reset_token = secrets.token_urlsafe(32)
random_number = secrets.randbelow(1000000)
```

---

## Security Headers

### Essential Security Headers

```python
# Flask - Comprehensive security headers
from flask import Flask

app = Flask(__name__)

@app.after_request
def set_security_headers(response):
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # Force HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Permissions policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

    return response
```

---

## Quick Security Checklist

- [ ] No SQL injection (use parameterized queries)
- [ ] No command injection (avoid shell=True, validate input)
- [ ] No XSS (escape output, use CSP)
- [ ] No hardcoded secrets (use environment variables)
- [ ] Strong password hashing (bcrypt, argon2)
- [ ] Proper authentication checks
- [ ] Authorization on all resources
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Sensitive data encrypted
- [ ] No debug mode in production
- [ ] Dependencies scanned for vulnerabilities
- [ ] Input validation on all user input
- [ ] Secure session management

---

*Stay updated with OWASP Top 10 and security best practices for your language/framework.*
