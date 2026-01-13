---
name: compliance-checker
description: Check code against security compliance standards and best practices.
---

# Compliance Checker Skill

Check code against security compliance standards and best practices.

## Instructions

You are a security compliance expert. When invoked:

1. **Security Standards Compliance**:
   - OWASP Top 10
   - OWASP ASVS (Application Security Verification Standard)
   - CWE Top 25 Most Dangerous Software Weaknesses
   - SANS Top 25
   - NIST Cybersecurity Framework
   - ISO 27001 controls

2. **Industry-Specific Compliance**:
   - PCI-DSS (Payment Card Industry)
   - HIPAA (Healthcare)
   - GDPR (Data Privacy - EU)
   - SOC 2 (Service Organization Controls)
   - CCPA (California Consumer Privacy Act)
   - FERPA (Education)

3. **Coding Standards**:
   - Secure coding guidelines
   - Input validation requirements
   - Output encoding standards
   - Cryptography standards
   - Session management requirements
   - Error handling best practices

4. **Data Protection**:
   - Encryption at rest
   - Encryption in transit
   - Data classification
   - Sensitive data handling
   - Data retention policies
   - Personally Identifiable Information (PII) protection

5. **Generate Report**: Comprehensive compliance assessment with gap analysis

## OWASP Top 10 (2021)

### A01:2021 - Broken Access Control

#### Checklist
```markdown
- [ ] Authorization checks on all protected resources
- [ ] No access control bypass via URL manipulation
- [ ] Proper CORS configuration
- [ ] No insecure direct object references (IDOR)
- [ ] Metadata manipulation prevention
- [ ] JWT tokens validated properly
- [ ] Force browsing protection
- [ ] API access controls enforced
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - No authorization check
app.get('/api/users/:id', authenticateUser, async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);  // Any authenticated user can access any user data
});

// ✅ COMPLIANT - Proper authorization
app.get('/api/users/:id', authenticateUser, async (req, res) => {
  if (req.params.id !== req.user.id && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const user = await User.findById(req.params.id);
  res.json(user);
});
```

### A02:2021 - Cryptographic Failures

#### Checklist
```markdown
- [ ] Sensitive data encrypted at rest
- [ ] TLS/SSL enforced (HTTPS only)
- [ ] Strong encryption algorithms (AES-256, RSA-2048+)
- [ ] No hardcoded encryption keys
- [ ] Proper key management
- [ ] Password hashing with Argon2, bcrypt, or PBKDF2
- [ ] No weak cryptographic algorithms (MD5, SHA1, DES)
- [ ] Secure random number generation
- [ ] No sensitive data in URLs or logs
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - Weak encryption
const crypto = require('crypto');
const cipher = crypto.createCipher('des', 'password');  // DES is weak

// ❌ VIOLATION - Hardcoded key
const key = 'my-secret-key-123';

// ✅ COMPLIANT - Strong encryption
const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
const iv = crypto.randomBytes(16);
const cipher = crypto.createCipheriv(algorithm, key, iv);
```

### A03:2021 - Injection

#### Checklist
```markdown
- [ ] SQL parameterized queries (no string concatenation)
- [ ] NoSQL injection prevention
- [ ] LDAP injection prevention
- [ ] OS command injection prevention
- [ ] XML injection prevention
- [ ] Input validation on all user inputs
- [ ] Output encoding
- [ ] ORM/ODM usage with parameterized queries
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - SQL Injection
const query = `SELECT * FROM users WHERE email = '${email}'`;

// ❌ VIOLATION - NoSQL Injection
db.users.find({ email: req.body.email });  // If email is {"$ne": null}

// ❌ VIOLATION - Command Injection
exec(`ping ${userInput}`);

// ✅ COMPLIANT - Parameterized query
const query = 'SELECT * FROM users WHERE email = ?';
db.query(query, [email]);

// ✅ COMPLIANT - NoSQL with validation
const email = String(req.body.email);
db.users.find({ email: email });

// ✅ COMPLIANT - Command validation
const { execFile } = require('child_process');
execFile('ping', ['-c', '1', validatedHost]);
```

### A04:2021 - Insecure Design

#### Checklist
```markdown
- [ ] Threat modeling performed
- [ ] Security requirements defined
- [ ] Secure development lifecycle followed
- [ ] Rate limiting implemented
- [ ] Resource limits enforced
- [ ] Circuit breaker patterns for external services
- [ ] Defense in depth strategy
- [ ] Fail securely (fail closed, not open)
```

### A05:2021 - Security Misconfiguration

#### Checklist
```markdown
- [ ] No default credentials
- [ ] No unnecessary features enabled
- [ ] Security headers configured
- [ ] Error messages don't leak information
- [ ] Latest security patches applied
- [ ] No directory listing
- [ ] Proper file permissions
- [ ] Secure admin interfaces
- [ ] No debug mode in production
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - Debug mode enabled
if (process.env.NODE_ENV === 'production') {
  app.use(express.errorHandler());  // Leaks stack traces
}

// ❌ VIOLATION - Detailed error messages
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack,  // Information disclosure
    query: req.query
  });
});

// ✅ COMPLIANT - Generic error messages
app.use((err, req, res, next) => {
  logger.error(err);  // Log details server-side
  res.status(500).json({
    error: 'Internal server error'  // Generic message
  });
});
```

### A06:2021 - Vulnerable and Outdated Components

#### Checklist
```markdown
- [ ] Dependencies regularly updated
- [ ] No known vulnerable dependencies
- [ ] Dependency scanning in CI/CD
- [ ] Unused dependencies removed
- [ ] Dependencies from trusted sources only
- [ ] Software Bill of Materials (SBOM) maintained
- [ ] Security advisories monitored
```

### A07:2021 - Identification and Authentication Failures

#### Checklist
```markdown
- [ ] Strong password requirements
- [ ] Multi-factor authentication available
- [ ] Secure session management
- [ ] No credential stuffing vulnerabilities
- [ ] Account lockout after failed attempts
- [ ] Secure password recovery
- [ ] Session invalidation on logout
- [ ] Session timeout implemented
- [ ] No weak password hashing
```

### A08:2021 - Software and Data Integrity Failures

#### Checklist
```markdown
- [ ] Code signing implemented
- [ ] Integrity checks for updates
- [ ] No insecure deserialization
- [ ] CI/CD pipeline security
- [ ] Dependency integrity verification (SRI)
- [ ] No untrusted data deserialization
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - Insecure deserialization
const userData = JSON.parse(req.body.data);
eval(userData.code);  // Never do this

// ❌ VIOLATION - No integrity check
<script src="https://cdn.example.com/library.js"></script>

// ✅ COMPLIANT - Subresource Integrity
<script
  src="https://cdn.example.com/library.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/ux..."
  crossorigin="anonymous">
</script>
```

### A09:2021 - Security Logging and Monitoring Failures

#### Checklist
```markdown
- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Input validation failures logged
- [ ] Logs protected from tampering
- [ ] Sensitive data not logged
- [ ] Centralized logging
- [ ] Log retention policy
- [ ] Alerting for suspicious activities
- [ ] Regular log review
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - No logging
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  res.json({ token: generateToken(user) });
  // No logging of authentication attempts
});

// ❌ VIOLATION - Logging sensitive data
logger.info('User login', {
  email: user.email,
  password: req.body.password,  // Never log passwords
  ssn: user.ssn
});

// ✅ COMPLIANT - Proper security logging
app.post('/login', async (req, res) => {
  try {
    const user = await authenticate(req.body);
    logger.info('Successful login', {
      userId: user.id,
      ip: req.ip,
      timestamp: new Date()
    });
    res.json({ token: generateToken(user) });
  } catch (error) {
    logger.warn('Failed login attempt', {
      email: req.body.email,  // OK to log email
      ip: req.ip,
      timestamp: new Date()
    });
    res.status(401).json({ error: 'Invalid credentials' });
  }
});
```

### A10:2021 - Server-Side Request Forgery (SSRF)

#### Checklist
```markdown
- [ ] URL validation for user-provided URLs
- [ ] Whitelist of allowed domains
- [ ] No access to internal network resources
- [ ] Network segmentation
- [ ] Disable unnecessary URL schemas (file://, gopher://)
```

#### Detection Patterns
```javascript
// ❌ VIOLATION - SSRF vulnerability
app.post('/fetch', async (req, res) => {
  const url = req.body.url;  // User-controlled
  const response = await fetch(url);  // Can access internal services
  res.json(await response.json());
});

// ✅ COMPLIANT - URL validation
const allowedDomains = ['api.example.com', 'cdn.example.com'];

app.post('/fetch', async (req, res) => {
  const url = new URL(req.body.url);

  // Validate protocol
  if (!['http:', 'https:'].includes(url.protocol)) {
    return res.status(400).json({ error: 'Invalid protocol' });
  }

  // Validate domain
  if (!allowedDomains.includes(url.hostname)) {
    return res.status(400).json({ error: 'Domain not allowed' });
  }

  // Prevent internal network access
  if (url.hostname === 'localhost' ||
      url.hostname.startsWith('127.') ||
      url.hostname.startsWith('192.168.') ||
      url.hostname.startsWith('10.')) {
    return res.status(400).json({ error: 'Internal network access denied' });
  }

  const response = await fetch(url.href);
  res.json(await response.json());
});
```

## PCI-DSS Compliance

### Requirement 2: Do not use vendor-supplied defaults

```markdown
- [ ] Default passwords changed
- [ ] Unnecessary default accounts removed
- [ ] Default settings reviewed and hardened
- [ ] System hardening standards implemented
```

### Requirement 3: Protect stored cardholder data

```javascript
// ❌ VIOLATION - Storing full credit card
await db.payments.create({
  cardNumber: '4532-1234-5678-9010',  // PCI violation
  cvv: '123',                         // Never store CVV
  cardholderName: 'John Doe'
});

// ✅ COMPLIANT - Tokenization
const token = await paymentProcessor.tokenize({
  cardNumber: req.body.cardNumber
});

await db.payments.create({
  token: token,                    // Store token, not card number
  last4: req.body.cardNumber.slice(-4),  // Last 4 digits OK
  cardholderName: 'John Doe'
});
```

### Requirement 6: Develop and maintain secure systems and applications

```markdown
- [ ] Security patches applied within 1 month
- [ ] Custom application code reviewed for vulnerabilities
- [ ] Secure coding guidelines followed
- [ ] Change control processes
- [ ] Separation of development, test, and production
```

### Requirement 8: Identify and authenticate access

```markdown
- [ ] Unique user IDs
- [ ] Strong authentication
- [ ] MFA for remote access
- [ ] Password requirements (min 7 chars, complex)
- [ ] Account lockout after 6 failed attempts
- [ ] Session timeout (15 min idle)
```

### Requirement 10: Log and monitor all access

```markdown
- [ ] User access logged
- [ ] Admin actions logged
- [ ] Failed access attempts logged
- [ ] Logs protected
- [ ] Daily log review
- [ ] Log retention (90 days minimum)
```

## HIPAA Compliance

### Technical Safeguards

#### Access Control (§164.312(a))
```markdown
- [ ] Unique user identification
- [ ] Emergency access procedures
- [ ] Automatic logoff
- [ ] Encryption and decryption
```

#### Audit Controls (§164.312(b))
```javascript
// ✅ COMPLIANT - HIPAA audit logging
function logPhiAccess(action, user, patient, details) {
  auditLog.create({
    timestamp: new Date(),
    action: action,              // CREATE, READ, UPDATE, DELETE
    userId: user.id,
    userName: user.name,
    patientId: patient.id,
    resourceType: 'PHI',
    ipAddress: req.ip,
    details: details,
    result: 'SUCCESS'
  });
}

app.get('/patient/:id', authenticateUser, async (req, res) => {
  const patient = await Patient.findById(req.params.id);

  logPhiAccess('READ', req.user, patient, {
    fields: ['name', 'diagnosis', 'medications']
  });

  res.json(patient);
});
```

#### Integrity (§164.312(c))
```markdown
- [ ] Data integrity mechanisms
- [ ] Protection against improper alteration/destruction
- [ ] Digital signatures or checksums
```

#### Transmission Security (§164.312(e))
```markdown
- [ ] TLS for data in transit
- [ ] End-to-end encryption
- [ ] Network security (VPN, firewalls)
```

### Protected Health Information (PHI) Handling
```javascript
// ❌ VIOLATION - PHI in logs
logger.info('Patient data:', {
  name: patient.name,
  ssn: patient.ssn,           // PHI in logs
  diagnosis: patient.diagnosis
});

// ❌ VIOLATION - PHI in URLs
app.get('/patient', (req, res) => {
  // PHI in query string (logged in access logs)
  const diagnosis = req.query.diagnosis;
});

// ✅ COMPLIANT - Protected PHI
logger.info('Patient data accessed', {
  patientId: patient.id,  // ID only, no PHI
  userId: req.user.id
});

// Use request body for PHI
app.post('/patient/search', (req, res) => {
  const diagnosis = req.body.diagnosis;  // Not in URL/logs
});
```

## GDPR Compliance

### Data Processing Principles

#### Lawfulness, Fairness, and Transparency
```markdown
- [ ] Legal basis for processing documented
- [ ] Privacy policy published
- [ ] Consent mechanisms implemented
- [ ] Data processing purposes defined
```

#### Purpose Limitation
```javascript
// ✅ COMPLIANT - Clear purpose
const userConsent = {
  email: {
    marketing: false,      // User opted out
    transactional: true,   // Necessary for service
    newsletter: true       // User opted in
  }
};

// Check consent before processing
async function sendEmail(user, type, content) {
  if (!user.consent.email[type]) {
    logger.warn('Email not sent - no consent', {
      userId: user.id,
      type: type
    });
    return;
  }

  await emailService.send(user.email, content);
}
```

#### Data Minimization
```javascript
// ❌ VIOLATION - Collecting unnecessary data
const user = {
  name: req.body.name,
  email: req.body.email,
  ssn: req.body.ssn,           // Not needed for account
  dob: req.body.dob,           // Not needed
  mothersMaiden: req.body.mothersMaiden  // Excessive
};

// ✅ COMPLIANT - Only necessary data
const user = {
  name: req.body.name,
  email: req.body.email
  // Only collect what's needed for service
};
```

#### Storage Limitation
```javascript
// ✅ COMPLIANT - Data retention policy
const RETENTION_PERIOD = 90 * 24 * 60 * 60 * 1000; // 90 days

// Automated deletion
async function cleanupOldData() {
  const cutoffDate = new Date(Date.now() - RETENTION_PERIOD);

  await InactiveAccounts.deleteMany({
    lastLogin: { $lt: cutoffDate }
  });

  logger.info('Data cleanup completed', {
    deletedBefore: cutoffDate
  });
}

// Schedule daily
cron.schedule('0 2 * * *', cleanupOldData);
```

#### Integrity and Confidentiality
```markdown
- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] Access controls
- [ ] Pseudonymization where possible
- [ ] Regular security assessments
```

### GDPR Rights Implementation

#### Right to Access (Article 15)
```javascript
app.get('/api/user/data-export', authenticateUser, async (req, res) => {
  const userData = await User.findById(req.user.id);
  const userPosts = await Post.find({ authorId: req.user.id });
  const userComments = await Comment.find({ authorId: req.user.id });

  const dataExport = {
    personalData: {
      name: userData.name,
      email: userData.email,
      createdAt: userData.createdAt
    },
    posts: userPosts,
    comments: userComments,
    exportedAt: new Date(),
    format: 'JSON'
  };

  res.json(dataExport);
});
```

#### Right to Erasure (Article 17)
```javascript
app.delete('/api/user/account', authenticateUser, async (req, res) => {
  // Verify user intent
  if (req.body.confirm !== 'DELETE') {
    return res.status(400).json({ error: 'Confirmation required' });
  }

  const userId = req.user.id;

  // Delete all user data
  await User.deleteOne({ _id: userId });
  await Post.deleteMany({ authorId: userId });
  await Comment.deleteMany({ authorId: userId });
  await Session.deleteMany({ userId: userId });

  // Log deletion for compliance
  logger.info('User data deleted', {
    userId: userId,
    deletedAt: new Date(),
    requestIp: req.ip
  });

  res.json({ success: true, message: 'All data deleted' });
});
```

#### Right to Data Portability (Article 20)
```javascript
app.get('/api/user/data-portable', authenticateUser, async (req, res) => {
  const format = req.query.format || 'json';

  const data = await getUserData(req.user.id);

  if (format === 'csv') {
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename=data.csv');
    res.send(convertToCSV(data));
  } else {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Content-Disposition', 'attachment; filename=data.json');
    res.json(data);
  }
});
```

## Usage Examples

```
@compliance-checker
@compliance-checker --standard owasp
@compliance-checker --standard pci-dss
@compliance-checker --standard hipaa
@compliance-checker --standard gdpr
@compliance-checker --report
@compliance-checker src/
```

## Compliance Report Format

```markdown
# Security Compliance Assessment Report

**Application**: Healthcare Portal
**Assessment Date**: 2024-01-15
**Standards Checked**: OWASP Top 10, HIPAA, GDPR
**Assessor**: Security Compliance Scanner v2.0

---

## Executive Summary

**Overall Compliance**: 64%
**Status**: ⚠️  PARTIALLY COMPLIANT

**Violations by Severity**:
- Critical: 8
- High: 15
- Medium: 23
- Low: 12

**Standards Summary**:
- OWASP Top 10: 58% compliant
- HIPAA: 71% compliant
- GDPR: 69% compliant

---

## OWASP Top 10 Compliance

**Score**: 58/100 (F)

| Category | Status | Issues |
|----------|--------|--------|
| A01: Broken Access Control | ❌ FAIL | 12 |
| A02: Cryptographic Failures | ⚠️  PARTIAL | 3 |
| A03: Injection | ✅ PASS | 0 |
| A04: Insecure Design | ⚠️  PARTIAL | 5 |
| A05: Security Misconfiguration | ❌ FAIL | 8 |
| A06: Vulnerable Components | ⚠️  PARTIAL | 6 |
| A07: Auth Failures | ❌ FAIL | 11 |
| A08: Data Integrity | ✅ PASS | 1 |
| A09: Logging Failures | ⚠️  PARTIAL | 7 |
| A10: SSRF | ✅ PASS | 0 |

### Critical Violations

#### A01: Missing Authorization Checks (12 endpoints)
**Files**: src/routes/patients.js, src/routes/records.js

```javascript
// src/routes/patients.js:45
app.get('/api/patients/:id', authenticateUser, async (req, res) => {
  const patient = await Patient.findById(req.params.id);
  res.json(patient);  // ❌ No authorization check
});
```

**Required Fix**:
```javascript
app.get('/api/patients/:id', authenticateUser, async (req, res) => {
  const patient = await Patient.findById(req.params.id);

  // Check authorization
  if (!canAccessPatient(req.user, patient)) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  res.json(patient);
});
```

---

## HIPAA Compliance

**Score**: 71/100 (C)

### Administrative Safeguards: 75%
- ✅ Security Management Process
- ✅ Assigned Security Responsibility
- ⚠️  Workforce Security (incomplete training)
- ✅ Information Access Management
- ⚠️  Security Awareness Training (no annual updates)

### Physical Safeguards: 80%
- ✅ Facility Access Controls
- ✅ Workstation Use Policy
- ✅ Workstation Security
- ⚠️  Device and Media Controls (incomplete)

### Technical Safeguards: 65%
- ⚠️  Access Control (§164.312(a))
  - ✅ Unique User Identification
  - ❌ Emergency Access Procedure missing
  - ⚠️  Automatic Logoff (inconsistent timeout)
  - ✅ Encryption and Decryption

- ✅ Audit Controls (§164.312(b))
  - ✅ Logging implemented
  - ✅ Regular log review

- ⚠️  Integrity (§164.312(c))
  - ⚠️  Mechanism to authenticate PHI (partial)

- ⚠️  Transmission Security (§164.312(e))
  - ✅ TLS enforced
  - ❌ End-to-end encryption missing for backups

### Critical Findings

#### PHI in Application Logs
**Severity**: Critical
**Regulation**: §164.312(b)

```javascript
// src/utils/logger.js:34
logger.info('Patient record accessed', {
  patientName: patient.name,     // ❌ PHI in logs
  ssn: patient.ssn,              // ❌ PHI in logs
  diagnosis: patient.diagnosis   // ❌ PHI in logs
});
```

**Required Fix**: Remove PHI from logs, use IDs only

#### Missing Automatic Logoff
**Severity**: High
**Regulation**: §164.312(a)(2)(iii)

Currently: No automatic session timeout
Required: 15-minute idle timeout

**Fix**:
```javascript
app.use(session({
  cookie: {
    maxAge: 15 * 60 * 1000  // 15 minutes
  },
  rolling: true
}));
```

---

## GDPR Compliance

**Score**: 69/100 (D)

### Lawfulness of Processing: 80%
- ✅ Legal basis documented
- ✅ Privacy policy published
- ⚠️  Consent mechanism (needs opt-in for marketing)
- ✅ Data processing purposes defined

### Data Subject Rights: 60%
- ✅ Right to Access (implemented)
- ⚠️  Right to Rectification (partial)
- ❌ Right to Erasure (not implemented)
- ❌ Right to Data Portability (not implemented)
- ⚠️  Right to Object (partial)

### Security of Processing: 75%
- ✅ Encryption in transit
- ✅ Encryption at rest
- ⚠️  Access controls (needs improvement)
- ✅ Pseudonymization (where applicable)
- ⚠️  Regular security assessments

### Critical Findings

#### Right to Erasure Not Implemented
**Severity**: Critical
**Article**: 17 GDPR

No endpoint for users to delete their data.

**Required Implementation**:
```javascript
app.delete('/api/user/delete-account', async (req, res) => {
  // Implement full data deletion
  await deleteUserData(req.user.id);
  res.json({ success: true });
});
```

#### Excessive Data Collection
**Severity**: High
**Principle**: Data Minimization

Currently collecting: name, email, phone, address, DOB, SSN, income
Required for service: name, email

**Fix**: Remove unnecessary fields from registration

---

## Remediation Plan

### Phase 1: Critical (0-7 days)
1. Add authorization checks to all endpoints
2. Remove PHI from application logs
3. Implement Right to Erasure (GDPR)
4. Fix automatic session timeout
5. Reduce data collection to minimum

**Estimated Effort**: 40 hours
**Priority**: P0

### Phase 2: High (7-30 days)
6. Implement data portability
7. Add emergency access procedures
8. Complete security awareness training
9. Implement end-to-end encryption for backups
10. Update consent mechanisms

**Estimated Effort**: 60 hours
**Priority**: P1

### Phase 3: Medium (30-90 days)
11. Enhance audit logging
12. Implement data retention automation
13. Complete workforce security training
14. Enhance access control mechanisms
15. Regular security assessments

**Estimated Effort**: 80 hours
**Priority**: P2

---

## Compliance Metrics

### Current State
- **OWASP**: 58% (F)
- **HIPAA**: 71% (C)
- **GDPR**: 69% (D)
- **Overall**: 64% (D)

### Target State (Post-Remediation)
- **OWASP**: 95%+ (A)
- **HIPAA**: 95%+ (A)
- **GDPR**: 95%+ (A)
- **Overall**: 95%+ (A)

### Timeline to Compliance
- Phase 1: 7 days
- Phase 2: 30 days
- Phase 3: 90 days
- **Full Compliance**: 90 days

---

## Recommendations

### Immediate
1. Assign compliance officer
2. Create compliance roadmap
3. Implement critical fixes
4. Document all changes

### Short-term
5. Regular compliance audits (monthly)
6. Security training for all staff
7. Penetration testing
8. Third-party compliance audit

### Long-term
9. Continuous compliance monitoring
10. Automated compliance checking in CI/CD
11. Regular security assessments
12. Compliance dashboard for stakeholders

---

## Certification Status

| Standard | Current | Target | Date |
|----------|---------|--------|------|
| SOC 2 Type II | ❌ Not Certified | ✅ Certified | Q2 2024 |
| HIPAA | ⚠️  Partial | ✅ Full | Q1 2024 |
| GDPR | ⚠️  Partial | ✅ Full | Q1 2024 |
| PCI-DSS | N/A | N/A | N/A |

---

## Next Steps

1. ✅ Review this report with stakeholders
2. ⬜ Approve remediation plan
3. ⬜ Allocate resources
4. ⬜ Begin Phase 1 fixes
5. ⬜ Schedule follow-up assessment in 30 days
```

## Best Practices

### Compliance as Code
```javascript
// Define compliance rules
const complianceRules = {
  owasp: {
    'no-sql-injection': {
      test: (code) => !code.includes('${') || code.includes('?'),
      severity: 'critical'
    }
  },
  hipaa: {
    'phi-not-logged': {
      test: (code) => !code.match(/logger.*patient\.(ssn|diagnosis)/),
      severity: 'critical'
    }
  }
};

// Automated checking
function checkCompliance(file, standard) {
  const violations = [];
  const code = fs.readFileSync(file, 'utf8');

  for (const [name, rule] of Object.entries(complianceRules[standard])) {
    if (!rule.test(code)) {
      violations.push({
        rule: name,
        severity: rule.severity,
        file: file
      });
    }
  }

  return violations;
}
```

### Continuous Monitoring
- Automated compliance scanning in CI/CD
- Regular third-party audits
- Compliance dashboards
- Real-time alerting on violations
- Documentation of all compliance decisions

## Notes

- Compliance is ongoing, not one-time
- Document all compliance decisions
- Regular training for development team
- Keep up with regulation changes
- Compliance != Security (need both)
- Automate compliance checking where possible
- Third-party audits recommended annually
- Maintain evidence of compliance efforts
- Privacy by design, security by default
