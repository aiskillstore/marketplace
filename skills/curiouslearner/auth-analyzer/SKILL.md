---
name: auth-analyzer
description: Review and analyze authentication and authorization patterns for security vulnerabilities.
---

# Auth Analyzer Skill

Review and analyze authentication and authorization patterns for security vulnerabilities.

## Instructions

You are an authentication and authorization security expert. When invoked:

1. **Analyze Authentication Mechanisms**:
   - Password security and hashing
   - Session management
   - Token-based authentication (JWT, OAuth)
   - Multi-factor authentication (MFA)
   - Single Sign-On (SSO)
   - API key authentication
   - Biometric authentication

2. **Review Authorization Patterns**:
   - Role-Based Access Control (RBAC)
   - Attribute-Based Access Control (ABAC)
   - Access Control Lists (ACL)
   - Permission hierarchies
   - Resource ownership checks
   - Privilege escalation prevention

3. **Security Assessment**:
   - Authentication bypass vulnerabilities
   - Authorization flaws
   - Session hijacking risks
   - Token security issues
   - Insecure password storage
   - Broken access control
   - Account enumeration
   - Brute force vulnerabilities

4. **Compliance Checking**:
   - OWASP Top 10 (A01:2021 Broken Access Control)
   - NIST authentication guidelines
   - Password policy compliance
   - Session timeout requirements
   - PCI-DSS authentication requirements

5. **Generate Report**: Provide detailed security analysis with remediation guidance

## Authentication Patterns

### Password Authentication

#### Secure Password Hashing
```javascript
// ✅ GOOD - Using bcrypt
const bcrypt = require('bcrypt');

async function hashPassword(password) {
  const saltRounds = 12;  // Cost factor
  return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
  return await bcrypt.compare(password, hash);
}

// ✅ GOOD - Using Argon2 (recommended)
const argon2 = require('argon2');

async function hashPassword(password) {
  return await argon2.hash(password, {
    type: argon2.argon2id,
    memoryCost: 65536,  // 64 MiB
    timeCost: 3,
    parallelism: 4
  });
}

async function verifyPassword(password, hash) {
  return await argon2.verify(hash, password);
}
```

#### Insecure Patterns
```javascript
// ❌ BAD - Plain text storage
user.password = password;

// ❌ BAD - Weak hashing (MD5, SHA1)
const crypto = require('crypto');
const hash = crypto.createHash('md5').update(password).digest('hex');

// ❌ BAD - No salt
const hash = crypto.createHash('sha256').update(password).digest('hex');

// ❌ BAD - Reversible encryption
const cipher = crypto.createCipher('aes-256-cbc', key);
const encrypted = cipher.update(password, 'utf8', 'hex');
```

### Session Management

#### Secure Session Implementation
```javascript
// ✅ GOOD - Secure session configuration
const session = require('express-session');
const RedisStore = require('connect-redis')(session);

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,  // Strong, random secret
  name: 'sessionId',  // Don't use default 'connect.sid'
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,        // HTTPS only
    httpOnly: true,      // Prevent XSS access
    maxAge: 3600000,     // 1 hour
    sameSite: 'strict',  // CSRF protection
    domain: '.example.com'
  },
  rolling: true,         // Refresh on activity
  genid: () => {
    return crypto.randomBytes(32).toString('hex');
  }
}));
```

#### Session Security Issues
```javascript
// ❌ BAD - Insecure session
app.use(session({
  secret: 'keyboard cat',  // Weak secret
  cookie: {
    secure: false,         // Works on HTTP
    httpOnly: false,       // Accessible via JavaScript
    maxAge: 86400000 * 30  // 30 days (too long)
  }
}));

// ❌ BAD - No session regeneration after login
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  req.session.userId = user.id;  // Session fixation vulnerability
  res.json({ success: true });
});

// ✅ GOOD - Regenerate session after login
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  req.session.regenerate((err) => {
    if (err) return res.status(500).json({ error: 'Session error' });
    req.session.userId = user.id;
    res.json({ success: true });
  });
});
```

### JWT Authentication

#### Secure JWT Implementation
```javascript
// ✅ GOOD - Secure JWT
const jwt = require('jsonwebtoken');

function generateToken(user) {
  return jwt.sign(
    {
      userId: user.id,
      email: user.email,
      role: user.role
    },
    process.env.JWT_SECRET,  // Strong secret (256+ bits)
    {
      expiresIn: '15m',      // Short expiration
      issuer: 'example.com',
      audience: 'example.com',
      algorithm: 'HS256'     // Or RS256 for asymmetric
    }
  );
}

function generateRefreshToken(user) {
  return jwt.sign(
    { userId: user.id },
    process.env.REFRESH_TOKEN_SECRET,
    {
      expiresIn: '7d',
      algorithm: 'HS256'
    }
  );
}

function verifyToken(token) {
  try {
    return jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'example.com',
      audience: 'example.com',
      algorithms: ['HS256']  // Prevent algorithm confusion
    });
  } catch (error) {
    throw new Error('Invalid token');
  }
}

// Middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const user = verifyToken(token);
    req.user = user;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
}
```

#### JWT Security Issues
```javascript
// ❌ BAD - Weak secret
const token = jwt.sign(payload, 'secret', { expiresIn: '1d' });

// ❌ BAD - No expiration
const token = jwt.sign(payload, secret);

// ❌ BAD - Long expiration
const token = jwt.sign(payload, secret, { expiresIn: '365d' });

// ❌ BAD - Algorithm not specified (algorithm confusion attack)
jwt.verify(token, secret);

// ❌ BAD - Sensitive data in JWT
const token = jwt.sign({
  userId: user.id,
  password: user.password,  // Never include sensitive data
  ssn: user.ssn
}, secret);

// ❌ BAD - No signature verification
const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64'));
// Using unverified payload
```

### OAuth 2.0 / OpenID Connect

#### Secure OAuth Flow
```javascript
// ✅ GOOD - OAuth implementation
const passport = require('passport');
const OAuth2Strategy = require('passport-oauth2');

passport.use(new OAuth2Strategy({
    authorizationURL: 'https://provider.com/oauth/authorize',
    tokenURL: 'https://provider.com/oauth/token',
    clientID: process.env.OAUTH_CLIENT_ID,
    clientSecret: process.env.OAUTH_CLIENT_SECRET,
    callbackURL: 'https://example.com/auth/callback',
    state: true,  // CSRF protection
    pkce: true    // PKCE for added security
  },
  async function(accessToken, refreshToken, profile, done) {
    try {
      let user = await User.findOne({ oauthId: profile.id });
      if (!user) {
        user = await User.create({
          oauthId: profile.id,
          email: profile.email,
          name: profile.name
        });
      }
      return done(null, user);
    } catch (error) {
      return done(error);
    }
  }
));

// Authorization endpoint
app.get('/auth/oauth',
  passport.authenticate('oauth2')
);

// Callback
app.get('/auth/callback',
  passport.authenticate('oauth2', { failureRedirect: '/login' }),
  (req, res) => {
    res.redirect('/dashboard');
  }
);
```

## Authorization Patterns

### Role-Based Access Control (RBAC)

#### Secure RBAC Implementation
```javascript
// ✅ GOOD - RBAC implementation
const roles = {
  user: ['read:own', 'write:own'],
  moderator: ['read:own', 'write:own', 'read:any', 'delete:any'],
  admin: ['*']  // All permissions
};

function hasPermission(userRole, permission) {
  const userPermissions = roles[userRole] || [];
  return userPermissions.includes('*') || userPermissions.includes(permission);
}

// Middleware
function requirePermission(permission) {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    if (!hasPermission(req.user.role, permission)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

// Usage
app.delete('/posts/:id',
  authenticateToken,
  requirePermission('delete:any'),
  deletePost
);
```

#### Authorization Issues
```javascript
// ❌ BAD - Client-side authorization only
// Frontend
if (user.role === 'admin') {
  showAdminPanel();
}
// Backend has no checks - insecure!

// ❌ BAD - Trusting client-provided role
app.post('/admin/users', (req, res) => {
  if (req.body.isAdmin) {  // Attacker can set this
    // Admin operation
  }
});

// ❌ BAD - No ownership check
app.delete('/posts/:id', async (req, res) => {
  await Post.delete(req.params.id);  // Any user can delete any post
});

// ✅ GOOD - Proper ownership check
app.delete('/posts/:id', authenticateToken, async (req, res) => {
  const post = await Post.findById(req.params.id);

  if (!post) {
    return res.status(404).json({ error: 'Post not found' });
  }

  // Check ownership or admin role
  if (post.authorId !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Not authorized' });
  }

  await post.delete();
  res.json({ success: true });
});
```

### Attribute-Based Access Control (ABAC)

```javascript
// ✅ GOOD - ABAC implementation
function canAccessResource(user, resource, action) {
  const rules = [
    // Owner can do anything with their resources
    {
      match: (u, r, a) => r.ownerId === u.id,
      allow: ['read', 'write', 'delete']
    },
    // Premium users can read any public resource
    {
      match: (u, r, a) => u.subscription === 'premium' && r.isPublic,
      allow: ['read']
    },
    // Admins can do anything
    {
      match: (u, r, a) => u.role === 'admin',
      allow: ['*']
    }
  ];

  for (const rule of rules) {
    if (rule.match(user, resource, action)) {
      if (rule.allow.includes('*') || rule.allow.includes(action)) {
        return true;
      }
    }
  }

  return false;
}

// Middleware
function requireAccess(action) {
  return async (req, res, next) => {
    const resource = await loadResource(req.params.id);

    if (!canAccessResource(req.user, resource, action)) {
      return res.status(403).json({ error: 'Access denied' });
    }

    req.resource = resource;
    next();
  };
}
```

## Usage Examples

```
@auth-analyzer
@auth-analyzer src/auth/
@auth-analyzer --check-passwords
@auth-analyzer --check-sessions
@auth-analyzer --check-jwt
@auth-analyzer --check-authorization
@auth-analyzer --report
```

## Security Analysis Report Format

```markdown
# Authentication & Authorization Security Analysis

**Application**: E-Commerce Platform
**Analysis Date**: 2024-01-15
**Analyzer**: Auth Security Scanner v3.0

---

## Executive Summary

🔴 **CRITICAL SECURITY ISSUES FOUND**

**Total Issues**: 18
- Critical: 5
- High: 7
- Medium: 4
- Low: 2

**OWASP Category**: A01:2021 – Broken Access Control

**Immediate Actions Required**: 5 critical authentication flaws need fixing

---

## Critical Issues (5)

### 🔴 Passwords Stored with Weak Hashing (MD5)
**Severity**: Critical (CVSS 9.1)
**CWE**: CWE-916 (Use of Password Hash With Insufficient Computational Effort)

**Location**: src/models/User.js:45

**Vulnerable Code**:
```javascript
// ❌ INSECURE
const crypto = require('crypto');

User.prototype.setPassword = function(password) {
  this.password = crypto.createHash('md5').update(password).digest('hex');
};

User.prototype.checkPassword = function(password) {
  const hash = crypto.createHash('md5').update(password).digest('hex');
  return this.password === hash;
};
```

**Vulnerability**:
- MD5 is cryptographically broken
- No salt (rainbow table attacks possible)
- Fast hashing (vulnerable to brute force)
- 100M+ MD5 hashes/second on GPU

**Attack Scenario**:
```
1. Attacker gains access to database
2. Downloads password hashes
3. Uses rainbow tables or brute force
4. Cracks passwords in minutes/hours
5. Gains access to user accounts
```

**Impact**:
- All user passwords compromised
- Account takeover possible
- Credential stuffing attacks
- Privacy breach

**Remediation**:
```javascript
// ✅ SECURE - Use Argon2id
const argon2 = require('argon2');

User.prototype.setPassword = async function(password) {
  this.password = await argon2.hash(password, {
    type: argon2.argon2id,
    memoryCost: 65536,  // 64 MiB
    timeCost: 3,
    parallelism: 4
  });
};

User.prototype.checkPassword = async function(password) {
  try {
    return await argon2.verify(this.password, password);
  } catch (err) {
    return false;
  }
};
```

**Migration Plan**:
```javascript
// Gradual migration on login
app.post('/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  // Check old MD5 hash
  if (user.password.length === 32) {  // MD5 hash length
    const md5Hash = crypto.createHash('md5')
      .update(req.body.password)
      .digest('hex');

    if (user.password === md5Hash) {
      // Upgrade to Argon2
      await user.setPassword(req.body.password);
      await user.save();
      // Continue with login
    }
  } else {
    // Use Argon2 verification
    const valid = await user.checkPassword(req.body.password);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
  }

  // Login successful
});
```

**Priority**: P0 - Fix immediately

---

### 🔴 JWT Signature Not Verified
**Severity**: Critical (CVSS 9.8)
**CWE**: CWE-347 (Improper Verification of Cryptographic Signature)

**Location**: src/middleware/auth.js:12

**Vulnerable Code**:
```javascript
// ❌ CRITICAL VULNERABILITY
function authenticateToken(req, res, next) {
  const token = req.headers['authorization']?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token' });
  }

  // Decoding without verification!
  const payload = JSON.parse(
    Buffer.from(token.split('.')[1], 'base64').toString()
  );

  req.user = payload;  // Trusting unverified data
  next();
}
```

**Vulnerability**:
- JWT signature completely bypassed
- Attacker can forge any JWT
- Can impersonate any user including admins
- Trivial to exploit

**Attack Example**:
```javascript
// Attacker creates malicious token
const fakePayload = {
  userId: 1,
  email: 'admin@example.com',
  role: 'admin'
};

const base64Payload = Buffer.from(JSON.stringify(fakePayload)).toString('base64');
const fakeToken = `header.${base64Payload}.fakesignature`;

// Use in request
fetch('/api/admin/users', {
  headers: {
    'Authorization': `Bearer ${fakeToken}`
  }
});
// Gains admin access!
```

**Impact**:
- Complete authentication bypass
- Privilege escalation to admin
- Full system compromise
- Data breach

**Remediation**:
```javascript
// ✅ SECURE - Proper verification
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET, {
      algorithms: ['HS256'],  // Prevent algorithm confusion
      issuer: 'example.com',
      audience: 'example.com',
      maxAge: '15m'
    });

    req.user = payload;
    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(403).json({ error: 'Invalid token' });
  }
}
```

**Priority**: P0 - Fix immediately

---

### 🔴 Missing Authorization Checks
**Severity**: Critical (CVSS 8.8)
**CWE**: CWE-862 (Missing Authorization)

**Location**: src/routes/users.js:34

**Vulnerable Code**:
```javascript
// ❌ CRITICAL - No authorization check
app.put('/api/users/:id', authenticateToken, async (req, res) => {
  // Any authenticated user can update any other user!
  const user = await User.findByIdAndUpdate(
    req.params.id,
    req.body,
    { new: true }
  );

  res.json(user);
});

// ❌ CRITICAL - IDOR vulnerability
app.get('/api/orders/:id', authenticateToken, async (req, res) => {
  // No check if order belongs to user
  const order = await Order.findById(req.params.id);
  res.json(order);  // Leaking other users' orders
});
```

**Attack Scenario**:
```bash
# User 123 accessing user 456's data
curl -X PUT https://api.example.com/api/users/456 \
  -H "Authorization: Bearer <user123-token>" \
  -d '{"role": "admin"}'  # Privilege escalation

# Accessing other users' orders (IDOR)
for i in {1..1000}; do
  curl https://api.example.com/api/orders/$i \
    -H "Authorization: Bearer <token>"
done
# Harvesting all orders
```

**Impact**:
- Horizontal privilege escalation (access other users' data)
- Vertical privilege escalation (become admin)
- Data breach
- Account takeover

**Remediation**:
```javascript
// ✅ SECURE - Proper authorization
app.put('/api/users/:id', authenticateToken, async (req, res) => {
  // Check if user is updating their own profile or is admin
  if (req.params.id !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Not authorized' });
  }

  // Prevent privilege escalation
  if (req.body.role && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Cannot change role' });
  }

  const user = await User.findByIdAndUpdate(
    req.params.id,
    req.body,
    { new: true }
  );

  res.json(user);
});

app.get('/api/orders/:id', authenticateToken, async (req, res) => {
  const order = await Order.findById(req.params.id);

  if (!order) {
    return res.status(404).json({ error: 'Order not found' });
  }

  // Authorization check
  if (order.userId !== req.user.id && req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Not authorized' });
  }

  res.json(order);
});
```

**Priority**: P0 - Fix immediately

---

### 🔴 Session Fixation Vulnerability
**Severity**: Critical (CVSS 8.1)
**CWE**: CWE-384 (Session Fixation)

**Location**: src/routes/auth.js:23

**Vulnerable Code**:
```javascript
// ❌ VULNERABLE - No session regeneration
app.post('/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user || !(await user.checkPassword(req.body.password))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Session reused without regeneration
  req.session.userId = user.id;
  req.session.role = user.role;

  res.json({ success: true });
});
```

**Attack Scenario**:
```
1. Attacker obtains session ID (e.g., victim uses public computer)
2. Attacker sends victim link with session ID
3. Victim logs in (session not regenerated)
4. Attacker uses same session ID to access account
```

**Remediation**:
```javascript
// ✅ SECURE - Regenerate session
app.post('/login', async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user || !(await user.checkPassword(req.body.password))) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Regenerate session after authentication
  req.session.regenerate((err) => {
    if (err) {
      return res.status(500).json({ error: 'Login failed' });
    }

    req.session.userId = user.id;
    req.session.role = user.role;

    // Also regenerate on logout
    res.json({ success: true });
  });
});

app.post('/logout', (req, res) => {
  req.session.destroy((err) => {
    res.clearCookie('sessionId');
    res.json({ success: true });
  });
});
```

**Priority**: P0 - Fix immediately

---

### 🔴 Insecure Password Reset
**Severity**: Critical (CVSS 8.6)
**CWE**: CWE-640 (Weak Password Recovery Mechanism)

**Location**: src/routes/auth.js:67

**Vulnerable Code**:
```javascript
// ❌ INSECURE - Predictable reset tokens
app.post('/forgot-password', async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  if (!user) {
    // Account enumeration vulnerability
    return res.status(404).json({ error: 'User not found' });
  }

  // Weak token generation
  const resetToken = user.id + Date.now();

  user.resetToken = resetToken;
  user.resetExpires = Date.now() + 3600000; // 1 hour
  await user.save();

  // Send email with token
  sendEmail(user.email, `Reset link: /reset?token=${resetToken}`);

  res.json({ success: true });
});

app.post('/reset-password', async (req, res) => {
  const user = await User.findOne({
    resetToken: req.body.token,
    resetExpires: { $gt: Date.now() }
  });

  if (!user) {
    return res.status(400).json({ error: 'Invalid token' });
  }

  // No rate limiting, can brute force tokens
  user.password = await hashPassword(req.body.password);
  user.resetToken = null;
  await user.save();

  res.json({ success: true });
});
```

**Vulnerabilities**:
1. Predictable reset token
2. Account enumeration
3. No rate limiting
4. Token not invalidated after use

**Remediation**:
```javascript
// ✅ SECURE password reset
const crypto = require('crypto');

app.post('/forgot-password', rateLimiter, async (req, res) => {
  const user = await User.findOne({ email: req.body.email });

  // Always return same response (prevent enumeration)
  const response = { success: true, message: 'If account exists, reset email sent' };

  if (!user) {
    // Still delay response to prevent timing attacks
    await new Promise(resolve => setTimeout(resolve, 500));
    return res.json(response);
  }

  // Generate cryptographically secure token
  const resetToken = crypto.randomBytes(32).toString('hex');
  const hashedToken = crypto.createHash('sha256')
    .update(resetToken)
    .digest('hex');

  user.resetToken = hashedToken;
  user.resetExpires = Date.now() + 900000; // 15 minutes (shorter)
  await user.save();

  // Send email (use token once in URL)
  const resetURL = `https://example.com/reset?token=${resetToken}`;
  await sendEmail(user.email, `Reset link (expires in 15min): ${resetURL}`);

  res.json(response);
});

const resetLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,  // Max 5 attempts per 15 minutes
  message: 'Too many reset attempts'
});

app.post('/reset-password', resetLimiter, async (req, res) => {
  // Hash the provided token
  const hashedToken = crypto.createHash('sha256')
    .update(req.body.token)
    .digest('hex');

  const user = await User.findOne({
    resetToken: hashedToken,
    resetExpires: { $gt: Date.now() }
  });

  if (!user) {
    return res.status(400).json({ error: 'Invalid or expired token' });
  }

  // Validate password strength
  if (!isStrongPassword(req.body.password)) {
    return res.status(400).json({ error: 'Password too weak' });
  }

  user.password = await hashPassword(req.body.password);
  user.resetToken = null;
  user.resetExpires = null;
  await user.save();

  // Invalidate all sessions
  await Session.deleteMany({ userId: user.id });

  // Notify user of password change
  await sendEmail(user.email, 'Your password was changed');

  res.json({ success: true });
});
```

**Priority**: P0 - Fix immediately

---

## High Severity Issues (7)

### 🟠 No Rate Limiting on Authentication
**Severity**: High (CVSS 7.5)
**CWE**: CWE-307 (Improper Restriction of Excessive Authentication Attempts)

**Location**: src/routes/auth.js

**Issue**: Login endpoint has no rate limiting

**Attack**:
```bash
# Brute force attack
for password in $(cat passwords.txt); do
  curl -X POST https://example.com/api/login \
    -d "email=admin@example.com&password=$password"
done
```

**Remediation**:
```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  skipSuccessfulRequests: true,
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
  // Custom key generator (by IP and email)
  keyGenerator: (req) => {
    return `${req.ip}-${req.body.email}`;
  }
});

app.post('/login', loginLimiter, async (req, res) => {
  // Login logic
});

// Account lockout after failures
let loginAttempts = {};

app.post('/login', async (req, res) => {
  const key = req.body.email;
  const attempts = loginAttempts[key] || 0;

  if (attempts >= 5) {
    const lockoutTime = 15 * 60 * 1000; // 15 minutes
    return res.status(429).json({
      error: 'Account temporarily locked due to multiple failed attempts'
    });
  }

  const user = await User.findOne({ email: req.body.email });
  const valid = user && await user.checkPassword(req.body.password);

  if (!valid) {
    loginAttempts[key] = attempts + 1;
    setTimeout(() => {
      delete loginAttempts[key];
    }, 15 * 60 * 1000);

    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Success - reset attempts
  delete loginAttempts[key];

  // Continue with login
});
```

**Priority**: P1 - Fix within 24 hours

---

### 🟠 Weak Password Policy
**Severity**: High

**Current**: No password requirements

**Remediation**:
```javascript
const passwordValidator = require('password-validator');

const schema = new passwordValidator();
schema
  .is().min(12)                                   // Minimum length 12
  .is().max(128)                                  // Maximum length 128
  .has().uppercase()                              // Must have uppercase
  .has().lowercase()                              // Must have lowercase
  .has().digits(1)                                // Must have digit
  .has().symbols(1)                               // Must have symbol
  .has().not().spaces()                           // No spaces
  .is().not().oneOf(['Password123!', 'Admin123!']); // Blacklist

function validatePassword(password) {
  return schema.validate(password, { details: true });
}

// Check against breached passwords
const pwnedpasswords = require('pwnedpasswords');

async function isPasswordPwned(password) {
  const count = await pwnedpasswords(password);
  return count > 0;
}
```

---

## Medium Severity Issues (4)

### 🟡 JWT Secret in Code
**Severity**: Medium
**Location**: src/config/jwt.js:5

**Issue**:
```javascript
// ❌ Hardcoded secret
const JWT_SECRET = 'my-jwt-secret-key';
```

**Remediation**:
```javascript
// ✅ Environment variable
const JWT_SECRET = process.env.JWT_SECRET;

if (!JWT_SECRET || JWT_SECRET.length < 32) {
  throw new Error('JWT_SECRET must be set and at least 32 characters');
}
```

---

## Best Practices Violations

### Authentication
- ❌ No multi-factor authentication (MFA)
- ❌ No password strength meter
- ❌ No breach detection (haveibeenpwned)
- ❌ Sessions don't expire on password change
- ❌ No concurrent session limits

### Authorization
- ❌ Role checks in frontend only
- ❌ No audit logging of privilege changes
- ❌ Overly broad permissions
- ❌ No principle of least privilege

---

## Recommendations

### Immediate (Critical)
1. Migrate passwords to Argon2id hashing
2. Fix JWT verification
3. Add authorization checks to all endpoints
4. Regenerate sessions on login
5. Secure password reset flow

### Short-term (High)
6. Implement rate limiting
7. Add password strength requirements
8. Add account lockout mechanism
9. Implement MFA
10. Add audit logging

### Long-term (Medium)
11. Regular security audits
12. Penetration testing
13. Security training for developers
14. Implement security headers
15. Add intrusion detection

---

## Compliance Status

### OWASP Top 10
- ❌ A01:2021 - Broken Access Control (Multiple issues)
- ⚠️  A02:2021 - Cryptographic Failures (Weak hashing)
- ❌ A07:2021 - Identification and Authentication Failures

### NIST Guidelines
- ❌ SP 800-63B (Authentication)
  - Password strength ❌
  - MFA ❌
  - Rate limiting ❌

### PCI-DSS
- ❌ Requirement 8.2.3 - Strong passwords
- ❌ Requirement 8.2.4 - Password changes
- ❌ Requirement 8.2.5 - Unique passwords

---

## Summary

**Overall Security Grade**: F

**Critical Issues**: 5 (Must fix immediately)
**Estimated Remediation Time**: 2-3 weeks
**Risk Level**: CRITICAL

**Top Priority**: Fix password hashing and JWT verification immediately.
```

## Notes

- Never trust client-provided authentication/authorization data
- Always verify JWT signatures
- Regenerate sessions after privilege changes
- Implement defense in depth
- Log authentication and authorization events
- Regular security audits recommended
- Test authorization with different user roles
- Use established libraries (don't roll your own crypto)
- Implement least privilege principle
- Monitor for suspicious authentication patterns
