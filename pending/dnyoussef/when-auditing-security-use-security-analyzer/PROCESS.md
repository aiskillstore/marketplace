# Security Analyzer - Detailed Process Documentation

## Overview

This document provides in-depth workflow documentation for each security check type in the Security Analyzer skill.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Manager                         │
│                    (Orchestration Layer)                     │
└──────────┬───────────────────┬──────────────────────────────┘
           │                   │
    ┌──────▼──────┐    ┌──────▼──────┐
    │    Code     │    │   Tester    │
    │  Analyzer   │    │   Agent     │
    └──────┬──────┘    └──────┬──────┘
           │                   │
           └─────────┬─────────┘
                     │
           ┌─────────▼─────────┐
           │  Shared Memory    │
           │  swarm/security/* │
           └───────────────────┘
```

## Phase 1: Static Code Analysis

### Objective
Identify security vulnerabilities in source code without executing it.

### Agents Involved
- **Primary**: Code Analyzer
- **Coordinator**: Security Manager

### Input
- Source code files (*.js, *.ts, *.jsx, *.tsx)
- Configuration from `.security-analyzer.json`
- Previous scan results (if available)

### Process Flow

#### Step 1.1: Initialization
```bash
# Security Manager starts phase
npx claude-flow@alpha hooks pre-task --description "Static analysis initialization"

# Load configuration
CONFIG=$(cat .security-analyzer.json 2>/dev/null || echo '{"severity_threshold":"medium"}')

# Set up memory namespace
npx claude-flow@alpha memory store \
  --key "swarm/security/config" \
  --value "$CONFIG"
```

#### Step 1.2: SQL Injection Detection
**Pattern Recognition:**
- Direct string concatenation in queries
- Unparameterized database calls
- Dynamic table/column names from user input

**Scanning Logic:**
```bash
# Find potential SQL injection points
grep -rn "\.query\|\.execute\|\.raw" \
  --include="*.js" --include="*.ts" \
  --exclude-dir=node_modules \
  . | grep -v "?" | grep -v "\$[0-9]" > /tmp/sql-candidates.txt

# Analyze each candidate
while IFS=: read -r file line content; do
  # Check if parameterized
  if echo "$content" | grep -q "VALUES\s*(\?"; then
    continue  # Safe - parameterized
  fi

  # Check for concatenation with user input
  if echo "$content" | grep -qE "\+\s*(req\.|params\.|query\.|body\.)"; then
    echo "VULNERABILITY: $file:$line - SQL Injection via string concatenation"
    echo "$file:$line:$content" >> /tmp/sql-findings.txt
  fi
done < /tmp/sql-candidates.txt
```

**Vulnerability Examples:**
```javascript
// CRITICAL: Direct concatenation
const query = "SELECT * FROM users WHERE id = " + req.params.id;
db.query(query);  // ⚠️ VULNERABLE

// CRITICAL: Template literals with user input
const query = `SELECT * FROM ${req.query.table} WHERE id = ${id}`;
db.query(query);  // ⚠️ VULNERABLE

// OK: Parameterized query
const query = "SELECT * FROM users WHERE id = ?";
db.query(query, [req.params.id]);  // ✅ SAFE

// OK: ORM with parameter binding
User.findOne({ where: { id: req.params.id } });  // ✅ SAFE
```

#### Step 1.3: XSS Detection
**Pattern Recognition:**
- Direct DOM manipulation with user input
- Dangerous functions (eval, Function constructor)
- Unescaped template rendering

**Scanning Logic:**
```bash
# Find XSS vulnerabilities
grep -rn "innerHTML\|outerHTML\|document\.write" \
  --include="*.js" --include="*.jsx" --include="*.tsx" \
  . > /tmp/xss-candidates.txt

# Check for eval usage
grep -rn "eval\(.*req\.\|new Function\(.*req\." \
  --include="*.js" \
  . >> /tmp/xss-candidates.txt

# Analyze each candidate
while IFS=: read -r file line content; do
  # Check if input is sanitized
  if echo "$content" | grep -q "DOMPurify\|sanitize\|escape"; then
    continue  # Likely safe - sanitized
  fi

  echo "VULNERABILITY: $file:$line - XSS via unsafe DOM manipulation"
  echo "$file:$line:$content" >> /tmp/xss-findings.txt
done < /tmp/xss-candidates.txt
```

**Vulnerability Examples:**
```javascript
// CRITICAL: innerHTML with user input
element.innerHTML = req.body.comment;  // ⚠️ VULNERABLE

// CRITICAL: eval with user input
eval(req.query.code);  // ⚠️ VULNERABLE

// HIGH: React dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{__html: userInput}} />  // ⚠️ VULNERABLE

// OK: textContent (auto-escapes)
element.textContent = req.body.comment;  // ✅ SAFE

// OK: Sanitized input
element.innerHTML = DOMPurify.sanitize(req.body.comment);  // ✅ SAFE
```

#### Step 1.4: Path Traversal Detection
**Pattern Recognition:**
- File operations with user-controlled paths
- Lack of path validation
- No directory boundary checks

**Scanning Logic:**
```bash
# Find file operations
grep -rn "readFile\|writeFile\|createReadStream\|unlink" \
  --include="*.js" --include="*.ts" \
  . | grep "req\.\|params\.\|query\." > /tmp/path-candidates.txt

# Analyze for path traversal
while IFS=: read -r file line content; do
  # Check for path validation
  if echo "$content" | grep -q "path\.resolve\|path\.normalize"; then
    # Check for boundary validation
    if echo "$content" | grep -q "startsWith\|includes"; then
      continue  # Likely safe - validated
    fi
  fi

  echo "VULNERABILITY: $file:$line - Path Traversal"
  echo "$file:$line:$content" >> /tmp/path-traversal-findings.txt
done < /tmp/path-candidates.txt
```

**Vulnerability Examples:**
```javascript
// CRITICAL: Direct user path
fs.readFile(req.query.file, callback);  // ⚠️ VULNERABLE
// Attack: ?file=../../../../etc/passwd

// HIGH: Incomplete validation
const filePath = path.join('/uploads', req.params.filename);
fs.readFile(filePath, callback);  // ⚠️ VULNERABLE
// Attack: filename=../../../etc/passwd

// OK: Path validation and boundary check
const safePath = path.normalize(path.join('/uploads', req.params.filename));
if (!safePath.startsWith('/uploads')) {
  throw new Error('Invalid path');
}
fs.readFile(safePath, callback);  // ✅ SAFE
```

#### Step 1.5: Insecure Cryptography Detection
**Pattern Recognition:**
- Weak hashing algorithms (MD5, SHA1)
- Insecure encryption (DES, RC4)
- Hardcoded cryptographic keys
- Weak random number generation

**Scanning Logic:**
```bash
# Find cryptographic operations
grep -rn "createHash\|createCipher\|createHmac\|Math\.random" \
  --include="*.js" --include="*.ts" \
  . > /tmp/crypto-candidates.txt

# Check for weak algorithms
grep -E "md5|sha1|des|rc4" /tmp/crypto-candidates.txt >> /tmp/crypto-findings.txt

# Check for hardcoded keys
grep -rn "const.*key\s*=\s*['\"]" --include="*.js" --include="*.ts" . | \
  grep -v "process\.env" >> /tmp/crypto-findings.txt
```

**Vulnerability Examples:**
```javascript
// CRITICAL: Weak hash algorithm
crypto.createHash('md5').update(password);  // ⚠️ VULNERABLE

// CRITICAL: Insecure cipher
crypto.createCipher('des', key);  // ⚠️ VULNERABLE

// HIGH: Hardcoded key
const encryptionKey = 'my-secret-key-123';  // ⚠️ VULNERABLE

// MEDIUM: Weak random
const token = Math.random().toString(36);  // ⚠️ VULNERABLE

// OK: Strong hash
crypto.createHash('sha256').update(password);  // ✅ SAFE

// OK: Strong cipher with IV
crypto.createCipheriv('aes-256-gcm', key, iv);  // ✅ SAFE

// OK: Environment variable
const encryptionKey = process.env.ENCRYPTION_KEY;  // ✅ SAFE

// OK: Cryptographically secure random
crypto.randomBytes(32).toString('hex');  // ✅ SAFE
```

#### Step 1.6: Store Results
```bash
# Combine all findings
cat /tmp/sql-findings.txt /tmp/xss-findings.txt \
    /tmp/path-traversal-findings.txt /tmp/crypto-findings.txt \
    > /tmp/static-analysis-all.txt

# Generate JSON report
cat > /tmp/static-analysis.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "total_files_scanned": $(find . -name "*.js" -o -name "*.ts" | wc -l),
  "vulnerabilities": {
    "sql_injection": $(wc -l < /tmp/sql-findings.txt),
    "xss": $(wc -l < /tmp/xss-findings.txt),
    "path_traversal": $(wc -l < /tmp/path-traversal-findings.txt),
    "weak_crypto": $(wc -l < /tmp/crypto-findings.txt)
  },
  "findings": $(cat /tmp/static-analysis-all.txt | jq -Rs 'split("\n") | map(select(length > 0))')
}
EOF

# Store in memory
npx claude-flow@alpha memory store \
  --key "swarm/security/static-analysis" \
  --value "$(cat /tmp/static-analysis.json)"

npx claude-flow@alpha hooks post-task --task-id "static-analysis"
```

### Output
- `/tmp/static-analysis.json` - Structured results
- `/tmp/*-findings.txt` - Raw findings per vulnerability type
- Memory: `swarm/security/static-analysis`

### Validation Gate
```bash
CRITICAL_COUNT=$(jq '[.vulnerabilities | to_entries[] | select(.value > 0)] | length' /tmp/static-analysis.json)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "⚠️  WARNING: $CRITICAL_COUNT vulnerability types found"
  npx claude-flow@alpha hooks notify --message "Static analysis completed with findings"
fi
```

---

## Phase 2: Dynamic Security Testing

### Objective
Detect runtime vulnerabilities through active security testing.

### Agents Involved
- **Primary**: Tester Agent
- **Coordinator**: Security Manager

### Prerequisites
- Application must be running
- Test environment configured
- Network access enabled

### Process Flow

#### Step 2.1: Application Startup Check
```bash
# Check if app is running
if ! curl -s http://localhost:3000/health > /dev/null; then
  echo "Starting application..."
  npm start &
  APP_PID=$!

  # Wait for startup
  for i in {1..30}; do
    if curl -s http://localhost:3000/health > /dev/null; then
      echo "Application ready"
      break
    fi
    sleep 1
  done
fi
```

#### Step 2.2: Authentication Testing
**Test Cases:**
1. SQL injection in login
2. NoSQL injection
3. JWT token manipulation
4. Session fixation
5. Brute force protection

**Test Implementation:**
```javascript
// /tmp/auth-tests.js
const axios = require('axios');

async function runAuthTests() {
  const results = [];
  const baseUrl = 'http://localhost:3000';

  // Test 1: SQL Injection in Login
  console.log('Testing SQL injection in authentication...');
  const sqlInjectionPayloads = [
    { username: "admin'--", password: "anything" },
    { username: "admin' OR '1'='1", password: "password" },
    { username: "' OR 1=1--", password: "" },
    { username: "admin'/*", password: "*/" }
  ];

  for (const payload of sqlInjectionPayloads) {
    try {
      const response = await axios.post(`${baseUrl}/api/login`, payload);
      if (response.status === 200 && response.data.token) {
        results.push({
          type: 'AUTH_BYPASS',
          severity: 'CRITICAL',
          test: 'SQL Injection in Login',
          payload: payload,
          description: 'Authentication bypassed using SQL injection',
          remediation: 'Use parameterized queries for authentication'
        });
      }
    } catch (e) {
      // Expected - login should fail
    }
  }

  // Test 2: NoSQL Injection
  console.log('Testing NoSQL injection...');
  const noSqlPayloads = [
    { username: { "$ne": null }, password: { "$ne": null } },
    { username: { "$gt": "" }, password: { "$gt": "" } },
    { username: "admin", password: { "$regex": ".*" } }
  ];

  for (const payload of noSqlPayloads) {
    try {
      const response = await axios.post(`${baseUrl}/api/login`, payload);
      if (response.status === 200) {
        results.push({
          type: 'NOSQL_INJECTION',
          severity: 'CRITICAL',
          test: 'NoSQL Injection',
          payload: payload,
          description: 'NoSQL injection allows authentication bypass',
          remediation: 'Validate input types and use schema validation'
        });
      }
    } catch (e) {
      // Expected
    }
  }

  // Test 3: JWT None Algorithm Attack
  console.log('Testing JWT security...');
  const jwtPayloads = [
    'eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJ1c2VyIjoiYWRtaW4ifQ.',  // None algorithm
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjk5OTk5OTk5OTl9.invalid'  // Expired token
  ];

  for (const token of jwtPayloads) {
    try {
      const response = await axios.get(`${baseUrl}/api/protected`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.status === 200) {
        results.push({
          type: 'JWT_VULNERABILITY',
          severity: 'CRITICAL',
          test: 'JWT Token Manipulation',
          payload: token,
          description: 'JWT token validation is insufficient',
          remediation: 'Properly validate JWT signatures and reject "none" algorithm'
        });
      }
    } catch (e) {
      // Expected
    }
  }

  // Test 4: Session Fixation
  console.log('Testing session fixation...');
  try {
    const fixedSession = 'fixed-session-id-12345';
    const loginResponse = await axios.post(`${baseUrl}/api/login`, {
      username: 'test',
      password: 'test'
    }, {
      headers: { 'Cookie': `sessionId=${fixedSession}` }
    });

    const sessionAfterLogin = loginResponse.headers['set-cookie']?.[0];
    if (sessionAfterLogin && sessionAfterLogin.includes(fixedSession)) {
      results.push({
        type: 'SESSION_FIXATION',
        severity: 'HIGH',
        test: 'Session Fixation',
        description: 'Session ID not regenerated after authentication',
        remediation: 'Regenerate session ID after successful login'
      });
    }
  } catch (e) {
    // Expected
  }

  // Test 5: Brute Force Protection
  console.log('Testing brute force protection...');
  let successfulAttempts = 0;
  for (let i = 0; i < 100; i++) {
    try {
      await axios.post(`${baseUrl}/api/login`, {
        username: 'admin',
        password: `wrong-password-${i}`
      });
      successfulAttempts++;
    } catch (e) {
      if (e.response?.status === 429) {
        // Rate limited - good!
        break;
      }
    }
  }

  if (successfulAttempts >= 100) {
    results.push({
      type: 'NO_BRUTE_FORCE_PROTECTION',
      severity: 'MEDIUM',
      test: 'Brute Force Protection',
      description: '100 login attempts succeeded without rate limiting',
      remediation: 'Implement rate limiting and account lockout'
    });
  }

  return results;
}

runAuthTests().then(results => {
  console.log(JSON.stringify(results, null, 2));
  process.exit(results.length > 0 ? 1 : 0);
});
```

#### Step 2.3: CSRF Testing
```javascript
// /tmp/csrf-tests.js
async function testCSRF() {
  const results = [];

  // Test state-changing operations
  const stateChangingEndpoints = [
    { method: 'POST', path: '/api/transfer', data: { to: 'attacker', amount: 1000 } },
    { method: 'DELETE', path: '/api/account', data: {} },
    { method: 'PUT', path: '/api/settings', data: { email: 'attacker@evil.com' } }
  ];

  for (const endpoint of stateChangingEndpoints) {
    try {
      const response = await axios({
        method: endpoint.method,
        url: `http://localhost:3000${endpoint.path}`,
        data: endpoint.data,
        headers: {
          'Origin': 'http://evil.com',
          'Referer': 'http://evil.com/attack.html'
        }
      });

      if (response.status === 200) {
        results.push({
          type: 'CSRF',
          severity: 'HIGH',
          endpoint: endpoint.path,
          method: endpoint.method,
          description: `CSRF vulnerability on ${endpoint.method} ${endpoint.path}`,
          remediation: 'Implement CSRF tokens and validate Origin/Referer headers'
        });
      }
    } catch (e) {
      // Expected - should be blocked
    }
  }

  return results;
}
```

#### Step 2.4: Store Results
```bash
# Run all dynamic tests
node /tmp/auth-tests.js > /tmp/auth-results.json 2>&1 || true
node /tmp/csrf-tests.js > /tmp/csrf-results.json 2>&1 || true

# Combine results
jq -s 'add' /tmp/auth-results.json /tmp/csrf-results.json > /tmp/dynamic-findings.json

# Store in memory
npx claude-flow@alpha memory store \
  --key "swarm/security/dynamic-testing" \
  --value "$(cat /tmp/dynamic-findings.json)"

npx claude-flow@alpha hooks post-task --task-id "dynamic-testing"

# Cleanup
kill $APP_PID 2>/dev/null || true
```

### Output
- `/tmp/dynamic-findings.json` - Test results
- Memory: `swarm/security/dynamic-testing`

### Validation Gate
```bash
CRITICAL_RUNTIME=$(jq '[.[] | select(.severity == "CRITICAL")] | length' /tmp/dynamic-findings.json)

if [ "$CRITICAL_RUNTIME" -gt 0 ]; then
  echo "🚨 CRITICAL: $CRITICAL_RUNTIME runtime vulnerabilities detected"
  exit 1  # Hard stop
fi
```

---

## Phase 3: Dependency Security Audit

### Objective
Identify known vulnerabilities in project dependencies.

### Process Flow

#### Step 3.1: NPM Audit
```bash
# Run npm audit
npm audit --json > /tmp/npm-audit-raw.json 2>&1 || true

# Parse results
jq '{
  critical: [.vulnerabilities | to_entries[] | select(.value.severity == "critical") | {
    name: .key,
    severity: .value.severity,
    via: .value.via,
    fixAvailable: .value.fixAvailable
  }],
  high: [.vulnerabilities | to_entries[] | select(.value.severity == "high") | {
    name: .key,
    severity: .value.severity,
    via: .value.via,
    fixAvailable: .value.fixAvailable
  }],
  summary: .metadata.vulnerabilities
}' /tmp/npm-audit-raw.json > /tmp/npm-audit.json
```

#### Step 3.2: License Compliance
```bash
# Check licenses
npx license-checker --json > /tmp/licenses-raw.json 2>&1 || true

# Check for restrictive licenses
jq 'to_entries | map(select(.value.licenses | contains("GPL") or contains("AGPL"))) | length' \
  /tmp/licenses-raw.json > /tmp/gpl-count.txt
```

#### Step 3.3: SBOM Generation
```bash
# Generate Software Bill of Materials
npx @cyclonedx/cyclonedx-npm --output-file /tmp/sbom.xml
```

### Output
- `/tmp/npm-audit.json` - Vulnerability report
- `/tmp/licenses-raw.json` - License information
- `/tmp/sbom.xml` - Software Bill of Materials

---

## Phase 4: Secrets Detection

### Process Flow

#### Step 4.1: Pattern Matching
```bash
# AWS Keys
grep -rEn 'AKIA[0-9A-Z]{16}' --include="*.js" --include="*.json" --exclude-dir=node_modules .

# Google API Keys
grep -rEn 'AIza[0-9A-Za-z_-]{35}' --include="*.js" --exclude-dir=node_modules .

# Private Keys
grep -rn 'BEGIN.*PRIVATE KEY' --include="*.pem" --include="*.key" .
```

#### Step 4.2: Entropy Analysis
```bash
# Find high-entropy strings (likely secrets)
find . -type f -name "*.js" -not -path "*/node_modules/*" \
  -exec grep -oE '[A-Za-z0-9+/]{40,}' {} \; | \
  awk 'length($0) >= 40' > /tmp/high-entropy.txt
```

---

## Phase 5: OWASP Compliance Check

### Process Flow

Automated compliance checking against OWASP Top 10 2021, combining results from previous phases.

### Output
- `/tmp/owasp-final.json` - Compliance report with score

---

## Performance Metrics

| Phase | Duration | Files Scanned | Checks Performed |
|-------|----------|---------------|------------------|
| Static Analysis | 30-60s | ~1000 | 4 vulnerability types |
| Dynamic Testing | 2-5m | N/A | 15+ security tests |
| Dependency Audit | 10-20s | package.json | All dependencies |
| Secrets Detection | 15-30s | ~1000 | 10+ secret patterns |
| OWASP Compliance | 5-10s | N/A | 10 categories |

**Total**: ~5-10 minutes for comprehensive audit

---

## Error Handling

Each phase includes error handling:

```bash
# Example: Handle network failures in dynamic testing
if ! curl -s http://localhost:3000/health > /dev/null; then
  echo "ERROR: Application not responding"
  npx claude-flow@alpha memory store \
    --key "swarm/security/errors" \
    --value '{"phase":"dynamic","error":"app_not_running"}'
  exit 3  # Configuration error
fi
```

---

## Continuous Improvement

Results from each audit are stored in memory and can be used for:
- Trend analysis
- False positive reduction
- Custom rule creation
- Team security training
