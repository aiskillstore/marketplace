# Security Patterns

AST patterns for detecting security vulnerabilities and anti-patterns.

## SQL Injection

```bash
# Find string concatenation in queries
sg -p 'query($_ + $_)'
sg -p 'execute("$$$" + $_)'

# Find template literals in queries
sg -p 'query(`$$$${$_}$$$`)'

# Find raw SQL with variables
sg -p 'raw("$$$" + $_)'
sg -p 'execute($_)' # Then inspect for string interpolation
```

## XSS Vectors

```bash
# Find innerHTML assignments
sg -p '$_.innerHTML = $_'

# Find dangerouslySetInnerHTML (React)
sg -p 'dangerouslySetInnerHTML={{ __html: $_ }}'

# Find eval calls
sg -p 'eval($_)'

# Find document.write
sg -p 'document.write($_)'

# Find outerHTML
sg -p '$_.outerHTML = $_'

# Find insertAdjacentHTML
sg -p '$_.insertAdjacentHTML($_, $_)'
```

## Secrets/Credentials

```bash
# Find hardcoded passwords
sg -p 'password = "$_"'
sg -p 'password: "$_"'
sg -p 'PASSWORD = "$_"'

# Find API keys
sg -p 'apiKey = "$_"'
sg -p 'API_KEY = "$_"'
sg -p 'api_key: "$_"'

# Find tokens
sg -p 'token = "$_"'
sg -p 'TOKEN = "$_"'
sg -p 'secret = "$_"'

# Find AWS credentials
sg -p 'aws_access_key_id = "$_"'
sg -p 'aws_secret_access_key = "$_"'
```

## Command Injection

```bash
# Find exec calls with variables
sg -p 'exec($_)' --lang python
sg -p 'system($_)' --lang python
sg -p 'subprocess.call($_)' --lang python

# Find shell=True (dangerous)
sg -p 'subprocess.run($$$, shell=True)' --lang python

# Find child_process in Node.js
sg -p 'exec($_)'
sg -p 'execSync($_)'
sg -p 'spawn($_)'
```

## Path Traversal

```bash
# Find path joins with user input
sg -p 'path.join($_, req.$_)'
sg -p 'os.path.join($_, $_)' --lang python

# Find file operations with variables
sg -p 'readFile($_)'
sg -p 'writeFile($_)'
sg -p 'open($_)' --lang python
```

## Cryptographic Issues

```bash
# Find weak hashing algorithms
sg -p 'md5($_)'
sg -p 'sha1($_)'
sg -p 'createHash("md5")'
sg -p 'createHash("sha1")'

# Find Math.random for crypto (insecure)
sg -p 'Math.random()'
```

## Authentication Issues

```bash
# Find JWT without verification
sg -p 'jwt.decode($_)'  # vs jwt.verify

# Find session without secure flag
sg -p 'session: { secure: false }'

# Find password comparison (timing attack)
sg -p 'password === $_'
sg -p 'password == $_'
```

## Python-Specific Security

```bash
# Find pickle (arbitrary code execution)
sg -p 'pickle.load($_)' --lang python
sg -p 'pickle.loads($_)' --lang python

# Find yaml.load without Loader (unsafe)
sg -p 'yaml.load($_)' --lang python

# Find assert for security checks (removed in -O)
sg -p 'assert $_' --lang python
```

## React/Frontend Security

```bash
# Find target="_blank" without rel (tabnabbing)
sg -p '<$_ target="_blank">'

# Find window.location assignment
sg -p 'window.location = $_'
sg -p 'window.location.href = $_'

# Find postMessage without origin check
sg -p 'postMessage($_)'
```

## Detection Workflow

1. Run security patterns on codebase:
```bash
# Create a security scan script
for pattern in 'eval($_)' '$_.innerHTML = $_' 'password = "$_"'; do
  echo "=== $pattern ==="
  sg -p "$pattern" -l
done
```

2. Review matches for false positives
3. Remediate confirmed issues
4. Add patterns to CI/CD pipeline
