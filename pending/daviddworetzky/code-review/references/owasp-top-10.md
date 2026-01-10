# OWASP Top 10 Quick Reference for Code Review

This reference provides concrete code patterns to look for when reviewing for security vulnerabilities.

## 1. Injection Flaws

### SQL Injection

**❌ Vulnerable:**
```python
# String concatenation/formatting
query = f"SELECT * FROM users WHERE email = '{email}'"
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute("SELECT * FROM users WHERE name = '%s'" % username)

# Raw SQL with user input
session.execute(f"DELETE FROM posts WHERE id = {post_id}")
```

**✅ Secure:**
```python
# SQLAlchemy ORM (parameterized)
user = session.query(User).filter(User.email == email).first()

# Parameterized raw SQL
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

### Command Injection

**❌ Vulnerable:**
```python
# Direct string formatting in shell commands
os.system(f"ping {user_input}")
subprocess.call(f"ls {directory}", shell=True)
subprocess.run(f"convert {filename} output.jpg", shell=True)
```

**✅ Secure:**
```python
# Pass arguments as list (no shell interpretation)
subprocess.run(["ping", "-c", "1", user_input])
subprocess.run(["ls", directory])
subprocess.run(["convert", filename, "output.jpg"])
```

### LDAP/NoSQL Injection

**❌ Vulnerable:**
```python
# MongoDB query with direct user input
db.users.find({"username": username, "password": password})

# LDAP filter with string formatting
filter = f"(uid={username})"
```

**✅ Secure:**
```python
# Validate and escape user input
username = escape_ldap(username)
filter = f"(uid={username})"

# Use parameterized queries where possible
```

## 2. Broken Authentication

**❌ Vulnerable:**
```python
# Weak password validation
if len(password) < 6:
    return "Password too short"

# Session token in URL
redirect(f"/dashboard?session={session_token}")

# No session timeout
session.permanent = True

# Storing passwords in plain text
user.password = password
```

**✅ Secure:**
```python
# Strong password requirements
if len(password) < 12 or not has_special_chars(password):
    return "Password must be 12+ chars with special characters"

# Use secure session management
session.permanent = False
session.modified = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Hash passwords
from werkzeug.security import generate_password_hash
user.password_hash = generate_password_hash(password)

# Use HTTP-only, secure cookies
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
```

## 3. Sensitive Data Exposure

**❌ Vulnerable:**
```python
# Logging sensitive data
logger.info(f"User {username} logged in with password {password}")
print(f"Credit card: {credit_card}")

# Storing sensitive data unencrypted
user.ssn = request.form['ssn']
config['api_key'] = "sk-1234567890abcdef"

# Sending sensitive data over HTTP
response = requests.post("http://api.example.com/payment", data=payment_info)
```

**✅ Secure:**
```python
# Don't log sensitive data
logger.info(f"User {username} logged in successfully")

# Encrypt sensitive data at rest
from cryptography.fernet import Fernet
cipher = Fernet(encryption_key)
user.ssn_encrypted = cipher.encrypt(ssn.encode())

# Use environment variables for secrets
api_key = os.environ.get('API_KEY')

# Use HTTPS for all sensitive communications
response = requests.post("https://api.example.com/payment", data=payment_info)
```

## 4. XML External Entities (XXE)

**❌ Vulnerable:**
```python
# Default XML parser (allows external entities)
import xml.etree.ElementTree as ET
tree = ET.parse(user_uploaded_file)

from lxml import etree
parser = etree.XMLParser()
tree = etree.parse(xml_file, parser)
```

**✅ Secure:**
```python
# Disable external entities
import xml.etree.ElementTree as ET
from defusedxml import ElementTree as DefusedET
tree = DefusedET.parse(user_uploaded_file)

# Or configure parser to disable features
from lxml import etree
parser = etree.XMLParser(resolve_entities=False, no_network=True)
tree = etree.parse(xml_file, parser)
```

## 5. Broken Access Control

**❌ Vulnerable:**
```python
# No authorization check
@app.route('/admin/delete_user/<user_id>')
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
    return "User deleted"

# Trusting client-side data for authorization
@app.route('/api/salary/<user_id>')
def get_salary(user_id):
    # Anyone can access anyone's salary
    user = User.query.get(user_id)
    return {"salary": user.salary}

# Insecure direct object reference
file_path = f"/uploads/{request.args.get('file')}"
return send_file(file_path)
```

**✅ Secure:**
```python
# Verify user authorization
@app.route('/admin/delete_user/<user_id>')
@require_admin
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    User.query.filter_by(id=user_id).delete()
    return "User deleted"

# Verify user can access their own data
@app.route('/api/salary/<user_id>')
@login_required
def get_salary(user_id):
    if current_user.id != int(user_id) and not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    return {"salary": user.salary}

# Validate file access
file_id = request.args.get('file_id')
file = File.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
return send_file(file.path)
```

## 6. Security Misconfiguration

**❌ Vulnerable:**
```python
# Debug mode in production
app.debug = True

# Overly permissive CORS
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# Exposing sensitive error details
@app.errorhandler(500)
def error_500(e):
    return f"Error: {str(e)}\n{traceback.format_exc()}"

# Default credentials
DATABASE_PASSWORD = "admin123"
```

**✅ Secure:**
```python
# Debug off in production
app.debug = False

# Restrictive CORS
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = 'https://yourdomain.com'
    return response

# Generic error messages
@app.errorhandler(500)
def error_500(e):
    logger.error(f"Internal error: {str(e)}")
    return "Internal server error", 500

# Use environment variables
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')
```

## 7. Cross-Site Scripting (XSS)

**❌ Vulnerable:**
```python
# Flask without autoescaping
return f"<h1>Hello {username}</h1>"

# React dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userComment}} />

# Direct DOM manipulation
element.innerHTML = user_input
```

**✅ Secure:**
```python
# Use template engine with autoescaping
from flask import render_template
return render_template('hello.html', username=username)

# In Jinja2 template (autoescapes by default)
<h1>Hello {{ username }}</h1>

# React (escapes by default)
<div>{userComment}</div>

# If you must use innerHTML, sanitize first
import bleach
clean_html = bleach.clean(user_input)
element.innerHTML = clean_html
```

## 8. Insecure Deserialization

**❌ Vulnerable:**
```python
# Pickle with untrusted data
import pickle
data = pickle.loads(request.data)

# eval() with user input
result = eval(user_expression)

# exec() with user input
exec(user_code)

# YAML unsafe load
import yaml
config = yaml.load(user_config)
```

**✅ Secure:**
```python
# Use JSON instead of pickle
import json
data = json.loads(request.data)

# Use ast.literal_eval for safe evaluation
import ast
result = ast.literal_eval(user_expression)

# Use safe YAML loader
import yaml
config = yaml.safe_load(user_config)

# If pickle is necessary, use HMAC to verify integrity
import hmac
import pickle

def safe_pickle_loads(data, secret_key):
    signature = data[:32]
    pickled_data = data[32:]
    expected_sig = hmac.new(secret_key, pickled_data, 'sha256').digest()
    if not hmac.compare_digest(signature, expected_sig):
        raise ValueError("Invalid signature")
    return pickle.loads(pickled_data)

# for model loading, use safe tensors
from safetensors import safe_open

tensors = {}
with safe_open("model.safetensors", framework="pt", device=0) as f:
    for k in f.keys():
        tensors[k] = f.get_tensor(k)
```

## 9. Using Components with Known Vulnerabilities

**Check for:**
- Outdated dependencies in `requirements.txt` or `package.json`
- Known vulnerable versions of libraries
- Unmaintained dependencies

**Tools to use:**
```bash
# Python
pip-audit
safety check

# JavaScript
npm audit
yarn audit
```

**❌ Vulnerable:**
```txt
# requirements.txt with old versions
Flask==0.12.0  # Known vulnerabilities
requests==2.6.0  # Very outdated
```

**✅ Secure:**
```txt
# Keep dependencies updated
Flask>=2.3.0
requests>=2.31.0
```

## 10. Insufficient Logging & Monitoring

**❌ Vulnerable:**
```python
# No logging of security events
@app.route('/login', methods=['POST'])
def login():
    if check_password(username, password):
        return "Success"
    return "Failed"

# Catch and hide exceptions
try:
    process_payment(amount)
except Exception:
    pass

# No audit trail
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()
```

**✅ Secure:**
```python
import logging

# Log security events
@app.route('/login', methods=['POST'])
def login():
    if check_password(username, password):
        logger.info(f"Successful login for user {username} from IP {request.remote_addr}")
        return "Success"
    logger.warning(f"Failed login attempt for user {username} from IP {request.remote_addr}")
    return "Failed"

# Log exceptions properly
try:
    process_payment(amount)
except Exception as e:
    logger.error(f"Payment processing failed: {str(e)}", exc_info=True)
    raise

# Create audit trail
def delete_user(user_id):
    user = User.query.get(user_id)
    logger.info(f"User {user.username} (ID: {user_id}) deleted by admin {current_user.username}")
    User.query.filter_by(id=user_id).delete()
```

## Quick Checklist for Code Review

- [ ] All database queries use parameterization (no string concatenation)
- [ ] No shell commands with `shell=True` and user input
- [ ] Passwords are hashed, never stored in plain text
- [ ] No sensitive data in logs or error messages
- [ ] All API keys and secrets are in environment variables
- [ ] HTTPS used for all external communications
- [ ] XML parsers have external entities disabled
- [ ] Authorization checks on all sensitive endpoints
- [ ] User can only access their own data (or authorized data)
- [ ] Debug mode disabled in production
- [ ] CORS properly configured (not `*`)
- [ ] All user input is escaped when rendered in templates
- [ ] No use of `eval()`, `exec()`, or unsafe `pickle`
- [ ] Dependencies are up-to-date
- [ ] Security events are logged
- [ ] Exceptions are logged with context
