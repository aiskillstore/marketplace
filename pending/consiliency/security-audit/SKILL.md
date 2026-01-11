---
name: security-audit
description: "Detect common security vulnerabilities in code. Covers OWASP patterns, SQL injection, bare excepts, shell injection. Framework-agnostic."
---

# Security Audit Skill

Detect common security vulnerabilities during code review and development. Based on OWASP guidelines and common vulnerability patterns.

## Design Principle

This skill is **framework-generic**. It provides universal security patterns:
- Covers OWASP Top 10 and common CWEs
- Works with Python, TypeScript, and other languages
- Project-specific security requirements go in project-specific skills

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SEVERITY_THRESHOLD | medium | Minimum severity to report |
| SCAN_DEPTH | 3 | Directory depth for scanning |
| INCLUDE_TESTS | false | Include test files in scan |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order.

1. Identify security-sensitive code areas
2. Check for common vulnerability patterns
3. Report findings with severity
4. Suggest remediation

## Red Flags - STOP and Reconsider

If you're about to:
- Write SQL with string concatenation
- Use bare `except:` blocks
- Execute shell commands with user input
- Store secrets in code
- Disable security features "temporarily"

**STOP** -> Use parameterized queries -> Add specific exception handling -> Then proceed

## Cookbook

### SQL Injection Prevention
- IF: Writing database queries
- THEN: Read and execute `./cookbook/sql-injection.md`

### Bare Except Handling
- IF: Writing exception handlers
- THEN: Read and execute `./cookbook/bare-except.md`

### Shell Injection Prevention
- IF: Executing shell commands
- THEN: Read and execute `./cookbook/shell-injection.md`

## Vulnerability Patterns

### SQL Injection (CWE-89)

**BAD - String concatenation:**
```python
# VULNERABLE
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

query = "SELECT * FROM users WHERE name = '" + name + "'"
```

**GOOD - Parameterized queries:**
```python
# SAFE
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# SQLAlchemy
session.query(User).filter(User.id == user_id).first()

# Prisma
await prisma.user.findUnique({ where: { id: userId } })
```

### Bare Except (CWE-754)

**BAD - Catches everything:**
```python
# VULNERABLE - hides bugs, catches KeyboardInterrupt
try:
    risky_operation()
except:
    pass

# VULNERABLE - too broad
except Exception:
    log.error("Something failed")
```

**GOOD - Specific exceptions:**
```python
# SAFE - specific exceptions
try:
    risky_operation()
except ValueError as e:
    log.warning(f"Invalid value: {e}")
except ConnectionError as e:
    log.error(f"Connection failed: {e}")
    raise
```

### Shell Injection (CWE-78)

**BAD - User input in shell:**
```python
# VULNERABLE
os.system(f"grep {user_input} /var/log/app.log")

import subprocess
subprocess.run(f"ls {directory}", shell=True)
```

**GOOD - Avoid shell, use lists:**
```python
# SAFE - no shell
subprocess.run(["grep", user_input, "/var/log/app.log"])

# SAFE - validated input
if not re.match(r'^[a-zA-Z0-9_-]+$', directory):
    raise ValueError("Invalid directory name")
subprocess.run(["ls", directory])
```

### Path Traversal (CWE-22)

**BAD - User input in paths:**
```python
# VULNERABLE
path = f"/uploads/{user_filename}"
with open(path) as f:
    return f.read()
```

**GOOD - Validate and sanitize:**
```python
# SAFE
from pathlib import Path

upload_dir = Path("/uploads").resolve()
requested = (upload_dir / user_filename).resolve()

if not requested.is_relative_to(upload_dir):
    raise ValueError("Path traversal attempt")

with open(requested) as f:
    return f.read()
```

### Hardcoded Secrets (CWE-798)

**BAD - Secrets in code:**
```python
# VULNERABLE
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "super_secret_password"
```

**GOOD - Environment variables:**
```python
# SAFE
import os

API_KEY = os.environ["API_KEY"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

# Or with defaults for development
API_KEY = os.getenv("API_KEY", "dev-key-only")
```

### XSS (CWE-79)

**BAD - Unsanitized output:**
```html
<!-- VULNERABLE -->
<div>{{ user_input }}</div>
```

**GOOD - Proper escaping:**
```html
<!-- SAFE - auto-escaped in most frameworks -->
<div>{{ user_input | e }}</div>

<!-- Or use textContent in JS -->
element.textContent = userInput;  // Safe
```

## Severity Levels

| Severity | Impact | Examples |
|----------|--------|----------|
| CRITICAL | Data breach, RCE | SQL injection, shell injection |
| HIGH | Data exposure, privilege escalation | Path traversal, hardcoded secrets |
| MEDIUM | Information disclosure | Verbose errors, bare excepts |
| LOW | Best practice violation | Missing input validation |

## Detection Patterns

### Python Patterns to Search

```python
VULNERABLE_PATTERNS = {
    "sql_injection": [
        r'execute\([\'"].*%s.*[\'"].*%',  # % formatting in SQL
        r'execute\(f[\'"]',                 # f-string in SQL
        r'execute\([\'"].*\+',              # String concat in SQL
    ],
    "shell_injection": [
        r'os\.system\(',                    # os.system
        r'subprocess\..*shell=True',        # shell=True
        r'eval\(',                          # eval
        r'exec\(',                          # exec
    ],
    "bare_except": [
        r'except\s*:',                      # bare except
    ],
    "hardcoded_secrets": [
        r'password\s*=\s*[\'"]',            # password = "..."
        r'api_key\s*=\s*[\'"]',             # api_key = "..."
        r'secret\s*=\s*[\'"]',              # secret = "..."
    ],
}
```

### TypeScript Patterns to Search

```typescript
const VULNERABLE_PATTERNS = {
  sqlInjection: [
    /`SELECT.*\$\{/,        // Template literal in SQL
    /"SELECT.*" \+ /,       // String concat in SQL
  ],
  xss: [
    /innerHTML\s*=/,        // innerHTML assignment
    /dangerouslySetInnerHTML/, // React dangerous prop
  ],
  shellInjection: [
    /exec\([`'"]/,          // child_process.exec
    /spawn\(.*shell:\s*true/, // shell: true
  ],
};
```

## Audit Workflow

### Step 1: Identify Sensitive Areas

```markdown
Check these high-risk areas first:
- Authentication/authorization code
- Database queries
- File operations
- External API calls
- User input handling
- Serialization/deserialization
```

### Step 2: Run Pattern Scan

```markdown
For each source file:
  Match against vulnerability patterns
  Record file, line, pattern matched
  Assess severity
```

### Step 3: Generate Report

```markdown
# Security Audit Report

## Summary
- CRITICAL: 2
- HIGH: 5
- MEDIUM: 12

## Critical Issues

### 1. SQL Injection in user_service.py:45
Pattern: f-string in execute()
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Fix**: Use parameterized query
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```
```

## Integration

### With /ai-dev-kit:execute-lane

Run security audit in code-related lanes:

```markdown
Lane: SL-API

Post-implementation checks:
1. ✓ Tests pass
2. ✓ Lint clean
3. ⚠️ Security audit: 2 MEDIUM issues

Review security findings before merge.
```

### CI Integration

```yaml
- name: Security Audit
  run: |
    # Check for vulnerable patterns
    grep -rn "execute(f" --include="*.py" && exit 1 || true
    grep -rn "shell=True" --include="*.py" && exit 1 || true
    grep -rn "except:" --include="*.py" && echo "Warning: bare except found"
```

## Best Practices

1. **Defense in depth**: Multiple layers of security
2. **Least privilege**: Minimum permissions needed
3. **Input validation**: Validate all external input
4. **Output encoding**: Escape output appropriately
5. **Secrets management**: Never hardcode secrets
6. **Error handling**: Don't expose internal details
7. **Logging**: Log security events (not sensitive data)
8. **Updates**: Keep dependencies updated
