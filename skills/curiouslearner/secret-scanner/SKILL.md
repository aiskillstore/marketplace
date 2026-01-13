---
name: secret-scanner
description: Detect accidentally committed secrets, credentials, and sensitive information in code.
---

# Secret Scanner Skill

Detect accidentally committed secrets, credentials, and sensitive information in code.

## Instructions

You are a secret detection expert. When invoked:

1. **Scan for Secrets**:
   - API keys and tokens
   - Passwords and credentials
   - Private keys and certificates
   - Database connection strings
   - OAuth tokens and secrets
   - Cloud provider credentials (AWS, GCP, Azure)
   - Encryption keys

2. **Pattern Detection**:
   - Regex-based secret detection
   - Entropy analysis for high-randomness strings
   - Known secret patterns (AWS keys, GitHub tokens, etc.)
   - Custom secret patterns
   - File type analysis (.env, config files)
   - Comment analysis (TODO: remove this key)

3. **Contextual Analysis**:
   - Distinguish real secrets from examples/test data
   - Check if secrets are in version control history
   - Identify false positives
   - Determine secret exposure scope
   - Check if secrets are still active

4. **Risk Assessment**:
   - Classify severity (Critical, High, Medium, Low)
   - Determine potential impact
   - Check if secret has been exposed publicly
   - Assess exploitability
   - Identify affected systems

5. **Generate Report**: Create comprehensive secret exposure report with remediation steps

## Secret Types and Patterns

### Cloud Provider Credentials

#### AWS
```regex
# AWS Access Key ID
AKIA[0-9A-Z]{16}

# AWS Secret Access Key
[0-9a-zA-Z/+=]{40}

# AWS Session Token
[A-Za-z0-9/+=]{200,}
```

#### Google Cloud
```regex
# GCP API Key
AIza[0-9A-Za-z-_]{35}

# GCP Service Account
"type": "service_account"
```

#### Azure
```regex
# Azure Storage Key
[a-zA-Z0-9+/]{88}==

# Azure Client Secret
[0-9a-zA-Z-_~]{34,}
```

### Version Control Tokens

#### GitHub
```regex
# GitHub Personal Access Token
ghp_[0-9a-zA-Z]{36}

# GitHub OAuth Token
gho_[0-9a-zA-Z]{36}

# GitHub App Token
(ghu|ghs)_[0-9a-zA-Z]{36}
```

#### GitLab
```regex
glpat-[0-9a-zA-Z-_]{20}
```

### Database Credentials
```regex
# MongoDB Connection String
mongodb(\+srv)?://[^\s]+

# PostgreSQL Connection String
postgres(ql)?://[^\s]+

# MySQL Connection String
mysql://[^\s]+

# Generic DB Password
(password|pwd|pass)\s*[:=]\s*['"][^'"]+['"]
```

### API Keys and Tokens
```regex
# Generic API Key
api[_-]?key\s*[:=]\s*['"][^'"]+['"]

# Stripe
sk_live_[0-9a-zA-Z]{24,}

# Slack
xox[baprs]-[0-9a-zA-Z-]{10,}

# Twilio
SK[0-9a-fA-F]{32}

# SendGrid
SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}
```

### Private Keys
```regex
-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----
```

### JWT Tokens
```regex
eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*
```

## Usage Examples

```
@secret-scanner
@secret-scanner --severity high
@secret-scanner --git-history
@secret-scanner src/
@secret-scanner --include-env-files
@secret-scanner --entropy-check
@secret-scanner --report
```

## Scanning Commands

### Using git-secrets
```bash
# Install git-secrets
brew install git-secrets  # macOS
# or
git clone https://github.com/awslabs/git-secrets.git

# Initialize
git secrets --install
git secrets --register-aws

# Scan repository
git secrets --scan
git secrets --scan-history

# Add custom patterns
git secrets --add 'api[_-]?key\s*[:=]\s*['"'"'][^'"'"']+['"'"']'
git secrets --add 'password\s*[:=]\s*['"'"'][^'"'"']+['"'"']'
```

### Using truffleHog
```bash
# Install
pip install truffleHog

# Scan repository
trufflehog git file://. --json

# Scan remote repository
trufflehog git https://github.com/user/repo.git

# Scan with high entropy only
trufflehog git file://. --entropy-only

# Scan specific branch
trufflehog git file://. --branch main
```

### Using gitleaks
```bash
# Install
brew install gitleaks  # macOS

# Scan repository
gitleaks detect --source . --verbose

# Scan with report
gitleaks detect --source . --report-format json --report-path report.json

# Scan uncommitted files
gitleaks protect --staged

# Scan git history
gitleaks detect --source . --log-opts "--all"
```

### Using detect-secrets
```bash
# Install
pip install detect-secrets

# Create baseline
detect-secrets scan > .secrets.baseline

# Audit baseline
detect-secrets audit .secrets.baseline

# Scan for new secrets
detect-secrets scan --baseline .secrets.baseline
```

### Using custom grep patterns
```bash
# Scan for AWS keys
grep -r "AKIA[0-9A-Z]\{16\}" .

# Scan for private keys
grep -r "BEGIN.*PRIVATE KEY" .

# Scan for passwords
grep -ri "password\s*=\s*['\"]" . --include="*.js" --include="*.py"

# High entropy strings
grep -r "[a-zA-Z0-9]\{32,\}" .
```

## Secret Scanner Report Format

```markdown
# Secret Scanner Report

**Repository**: my-application
**Scan Date**: 2024-01-15 14:30:00 UTC
**Branch**: main
**Commits Scanned**: 1,234
**Files Scanned**: 456

---

## Executive Summary

🔴 **CRITICAL SECURITY ISSUE DETECTED**

**Total Secrets Found**: 12
- Critical: 4
- High: 3
- Medium: 3
- Low: 2

**Immediate Actions Required**: 4 secrets need rotation NOW

---

## Critical Secrets (4)

### 🔴 AWS Access Key Exposed
**Severity**: Critical
**File**: src/config/aws.js
**Line**: 12
**Commit**: a3f5c2b (2024-01-10)
**Age**: 5 days

**Secret Found**:
```javascript
const AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE';
const AWS_SECRET_ACCESS_KEY = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY';
```

**Pattern Match**: AWS Access Key ID pattern
**Entropy Score**: 4.2 (High)

**Risk Assessment**:
- **Impact**: CRITICAL - Full AWS account access
- **Scope**: All AWS resources in the account
- **Exploitability**: HIGH - Key is in public repository
- **Data at Risk**: Production databases, S3 buckets, EC2 instances

**Exposure**:
- ✅ Committed to repository: Yes
- ✅ Pushed to remote: Yes
- ✅ In public repository: Yes
- ⚠️  Visible in GitHub: Since 2024-01-10
- ⚠️  Present in 5 commits

**Immediate Actions**:
1. ✅ ROTATE CREDENTIALS IMMEDIATELY
2. ✅ Revoke exposed keys in AWS Console
3. ✅ Check AWS CloudTrail for unauthorized access
4. ✅ Review all AWS resources for tampering
5. ✅ Enable AWS GuardDuty alerts
6. ✅ Implement MFA on root account

**Remediation**:
```bash
# 1. Revoke key immediately via AWS Console or CLI
aws iam delete-access-key --access-key-id AKIAIOSFODNN7EXAMPLE

# 2. Create new key
aws iam create-access-key --user-name production-user

# 3. Update environment variables (DO NOT COMMIT)
export AWS_ACCESS_KEY_ID="new-key-id"
export AWS_SECRET_ACCESS_KEY="new-secret-key"

# 4. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch src/config/aws.js" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo Cleaner
bfg --replace-text passwords.txt
```

**Prevention**:
```javascript
// NEVER do this:
const AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE';

// ALWAYS do this:
const AWS_ACCESS_KEY_ID = process.env.AWS_ACCESS_KEY_ID;

// Add to .gitignore:
.env
.env.local
.env.production
credentials.json
aws-config.json
```

**Git History Cleanup Required**: YES
**Priority**: P0 - Fix immediately

---

### 🔴 Database Password in Connection String
**Severity**: Critical
**File**: config/database.yml
**Line**: 8
**Commit**: f9e2a1d (2024-01-05)

**Secret Found**:
```yaml
production:
  url: postgresql://admin:SuperSecret123!@prod-db.example.com:5432/appdb
```

**Pattern Match**: PostgreSQL connection string with password
**Entropy Score**: 3.8 (High)

**Risk Assessment**:
- **Impact**: CRITICAL - Production database access
- **Scope**: All production data
- **Exploitability**: HIGH
- **Data at Risk**: User data, financial records, PII

**Immediate Actions**:
1. ✅ Change database password immediately
2. ✅ Review database access logs for unauthorized queries
3. ✅ Check for data exfiltration
4. ✅ Update application configuration
5. ✅ Implement database firewall rules

**Remediation**:
```yaml
# Use environment variables
production:
  url: <%= ENV['DATABASE_URL'] %>

# Or use secrets manager
production:
  url: <%= SecretsManager.get('database_url') %>
```

**Priority**: P0 - Fix immediately

---

### 🔴 Private SSH Key Committed
**Severity**: Critical
**File**: deploy/keys/id_rsa
**Line**: 1-27
**Commit**: b4c7e3a (2023-12-20)

**Secret Found**:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA1234567890...
[REDACTED]
-----END RSA PRIVATE KEY-----
```

**Pattern Match**: RSA Private Key
**Age**: 26 days

**Risk Assessment**:
- **Impact**: CRITICAL - Server access
- **Scope**: All servers using this key
- **Exploitability**: HIGH

**Immediate Actions**:
1. ✅ Revoke key from all servers immediately
2. ✅ Generate new SSH key pair
3. ✅ Update authorized_keys on all servers
4. ✅ Check server logs for unauthorized access
5. ✅ Rotate any secrets on accessed servers

**Remediation**:
```bash
# 1. Remove key from servers
ssh user@server "sed -i '/ssh-rsa AAAA.../d' ~/.ssh/authorized_keys"

# 2. Generate new key (DO NOT COMMIT)
ssh-keygen -t ed25519 -C "deployment@example.com"

# 3. Add to .gitignore
*.pem
*.key
id_rsa
id_rsa.pub
*.ppk
```

**Priority**: P0 - Fix immediately

---

### 🔴 Stripe Secret Key
**Severity**: Critical
**File**: src/payments/stripe.js
**Line**: 5
**Commit**: d8f1a2c (2024-01-12)

**Secret Found**:
```javascript
const stripe = require('stripe')('sk_live_51Abc123XYZ...');
```

**Pattern Match**: Stripe Live Secret Key
**Entropy Score**: 4.1 (High)

**Risk Assessment**:
- **Impact**: CRITICAL - Payment processing access
- **Scope**: All customer payments, refunds, financial data
- **Exploitability**: HIGH
- **Financial Risk**: Unlimited charges, refunds, data theft

**Immediate Actions**:
1. ✅ Revoke API key in Stripe Dashboard immediately
2. ✅ Generate new secret key
3. ✅ Review recent charges and transactions
4. ✅ Check for unauthorized refunds or transfers
5. ✅ Enable Stripe fraud detection
6. ✅ Notify security team

**Remediation**:
```javascript
// NEVER do this:
const stripe = require('stripe')('sk_live_51Abc123XYZ...');

// ALWAYS do this:
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

**Priority**: P0 - Fix immediately

---

## High Severity Secrets (3)

### 🟠 GitHub Personal Access Token
**Severity**: High
**File**: .github/workflows/deploy.yml
**Line**: 23
**Commit**: e3b9c4f (2024-01-14)

**Secret Found**:
```yaml
env:
  GITHUB_TOKEN: ghp_1234567890abcdefghijklmnopqrstuvwx
```

**Pattern Match**: GitHub Personal Access Token
**Scope**: Repository access, potentially org-wide

**Immediate Actions**:
1. Revoke token in GitHub settings
2. Generate new token with minimal scopes
3. Use GitHub Actions secrets instead

**Remediation**:
```yaml
# Use built-in GITHUB_TOKEN (automatically available)
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# Or store in repository secrets
env:
  CUSTOM_TOKEN: ${{ secrets.CUSTOM_GITHUB_TOKEN }}
```

**Priority**: P1 - Fix within 24 hours

---

### 🟠 SendGrid API Key
**Severity**: High
**File**: src/email/sender.js
**Line**: 8

**Secret Found**:
```javascript
const apiKey = 'SG.1234567890abcdefgh.ijklmnopqrstuvwxyz1234567890abcdefgh';
```

**Risk**: Unauthorized email sending, quota exhaustion
**Action**: Rotate key, use environment variable

**Priority**: P1 - Fix within 24 hours

---

### 🟠 JWT Secret Key
**Severity**: High
**File**: src/auth/config.js
**Line**: 15

**Secret Found**:
```javascript
const JWT_SECRET = 'my-super-secret-jwt-key-123';
```

**Risk**: Token forgery, authentication bypass
**Action**: Generate strong secret, store securely

**Remediation**:
```javascript
// Generate strong secret
const crypto = require('crypto');
const secret = crypto.randomBytes(64).toString('hex');

// Use environment variable
const JWT_SECRET = process.env.JWT_SECRET;

// Validation
if (!JWT_SECRET || JWT_SECRET.length < 32) {
  throw new Error('JWT_SECRET must be at least 32 characters');
}
```

**Priority**: P1 - Fix within 24 hours

---

## Medium Severity Secrets (3)

### 🟡 Hardcoded API Endpoint with Key
**Severity**: Medium
**File**: src/api/client.js
**Line**: 12

**Secret Found**:
```javascript
const API_URL = 'https://api.example.com?key=abc123def456';
```

**Risk**: API quota abuse, service disruption
**Action**: Move to environment variable

**Priority**: P2 - Fix within 7 days

---

## Low Severity Secrets (2)

### 🟢 Development Database Password
**Severity**: Low
**File**: docker-compose.yml
**Line**: 18

**Secret Found**:
```yaml
POSTGRES_PASSWORD: devpassword123
```

**Risk**: Low (development only)
**Note**: Still use environment variables for consistency

**Priority**: P3 - Fix in next sprint

---

## False Positives (5)

### Example API Key in Documentation
**File**: README.md
**Line**: 45
```markdown
Example: api_key="your-api-key-here"
```
**Reason**: Example/placeholder text
**Action**: None (consider adding comment to prevent future flags)

---

## Git History Analysis

**Total Commits Analyzed**: 1,234
**Commits with Secrets**: 8
**Branches Affected**: main, develop, feature/payment

**Historical Secret Exposure**:
```
Commit: a3f5c2b - AWS keys (2024-01-10)
Commit: f9e2a1d - DB password (2024-01-05)
Commit: b4c7e3a - SSH key (2023-12-20)
Commit: d8f1a2c - Stripe key (2024-01-12)
```

**Recommendation**: Rewrite git history to remove secrets

---

## Files Requiring Cleanup

### Immediate Removal Required
- src/config/aws.js (AWS credentials)
- config/database.yml (DB password)
- deploy/keys/id_rsa (Private key)
- src/payments/stripe.js (Stripe key)

### Should Be Gitignored
- .env*
- *.pem
- *.key
- credentials.json
- secrets.yml
- config/production/*

---

## Remediation Checklist

### Immediate (Critical - 0-24 hours)
- [ ] Rotate all exposed AWS credentials
- [ ] Change database passwords
- [ ] Revoke and regenerate SSH keys
- [ ] Rotate Stripe API keys
- [ ] Review CloudTrail/access logs for unauthorized activity
- [ ] Check for data breaches

### Short-term (High - 24-48 hours)
- [ ] Rotate GitHub tokens
- [ ] Regenerate SendGrid API keys
- [ ] Generate new JWT secret
- [ ] Remove secrets from git history
- [ ] Force push cleaned repository

### Medium-term (7 days)
- [ ] Implement secrets management solution
- [ ] Set up pre-commit hooks
- [ ] Add .gitignore rules
- [ ] Train team on secret handling
- [ ] Document secrets policy

### Long-term (Ongoing)
- [ ] Regular secret scanning (automated)
- [ ] Quarterly security audits
- [ ] Secret rotation policy (90 days)
- [ ] Monitor for exposed secrets

---

## Git History Cleanup

### Using BFG Repo Cleaner (Recommended)
```bash
# 1. Clone fresh copy
git clone --mirror https://github.com/user/repo.git

# 2. Create file with secrets to remove
cat > secrets.txt << EOF
AKIAIOSFODNN7EXAMPLE
SuperSecret123!
sk_live_51Abc123XYZ
ghp_1234567890abcdefghijklmnopqrstuvwx
EOF

# 3. Run BFG
bfg --replace-text secrets.txt repo.git

# 4. Clean up
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push
git push --force
```

### Using git-filter-repo
```bash
# Install
pip install git-filter-repo

# Remove specific files
git filter-repo --path src/config/aws.js --invert-paths

# Remove secrets by pattern
git filter-repo --replace-text secrets.txt
```

### Warning Team
```
⚠️  IMPORTANT: After history rewrite
1. All team members must delete local clones
2. Clone repository fresh
3. DO NOT merge old branches
4. Update all CI/CD pipelines
```

---

## Prevention Strategy

### 1. Pre-commit Hooks
```bash
# .husky/pre-commit
#!/bin/sh
gitleaks protect --staged --verbose --redact
```

### 2. Update .gitignore
```gitignore
# Secrets
.env
.env.*
!.env.example
*.pem
*.key
*.ppk
*_rsa
*_dsa
credentials.json
secrets.yml
secrets.yaml
config/credentials/*
aws-config.json

# OS Files
.DS_Store
Thumbs.db
```

### 3. Environment Template
```bash
# .env.example (commit this)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here

# .env (DO NOT COMMIT - add to .gitignore)
DATABASE_URL=postgresql://admin:RealPassword@prod.db.com:5432/prod
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```

### 4. Code Review Checklist
- [ ] No hardcoded credentials
- [ ] All secrets in environment variables
- [ ] .env files not committed
- [ ] Secret scanner run and passed
- [ ] No TODO comments about removing secrets

### 5. Secrets Management Solutions

**HashiCorp Vault**
```javascript
const vault = require('node-vault');
const client = vault({ endpoint: process.env.VAULT_ADDR });

async function getSecret(path) {
  const result = await client.read(path);
  return result.data;
}

const dbPassword = await getSecret('secret/database/password');
```

**AWS Secrets Manager**
```javascript
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();

async function getSecret(secretName) {
  const data = await secretsManager.getSecretValue({
    SecretId: secretName
  }).promise();
  return JSON.parse(data.SecretString);
}
```

**Doppler**
```bash
# Install Doppler CLI
doppler setup

# Run app with secrets
doppler run -- node app.js
```

---

## CI/CD Integration

### GitHub Actions
```yaml
name: Secret Scanning
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
```

---

## Best Practices

### Secret Handling
- ✅ Never commit secrets to version control
- ✅ Use environment variables
- ✅ Use secrets management systems
- ✅ Rotate secrets regularly (90 days)
- ✅ Use different secrets for dev/staging/prod
- ✅ Implement principle of least privilege
- ✅ Audit secret access
- ✅ Encrypt secrets at rest

### Development Workflow
- ✅ Use .env.example templates
- ✅ Document required environment variables
- ✅ Validate environment on startup
- ✅ Never log secrets
- ✅ Redact secrets in error messages
- ✅ Use short-lived tokens when possible

### Code Review
- ✅ Run secret scanner before committing
- ✅ Review all config files carefully
- ✅ Check for TODO comments about secrets
- ✅ Verify .gitignore is comprehensive
- ✅ Double-check before public repository

---

## Incident Response Plan

If secrets are exposed:

### 1. Immediate Actions (0-1 hour)
- Stop the breach (revoke credentials)
- Assess scope (what was exposed, for how long)
- Check for unauthorized access
- Notify security team

### 2. Short-term Actions (1-24 hours)
- Rotate all affected credentials
- Review logs for abuse
- Remove secrets from git history
- Force push cleaned repository
- Notify affected parties if data breach

### 3. Long-term Actions (1-7 days)
- Post-mortem analysis
- Update security procedures
- Implement additional controls
- Train team on lessons learned
- Monitor for long-term impact

---

## Summary

**Secrets Found**: 12
**Critical**: 4 (require immediate rotation)
**High**: 3 (rotate within 24h)
**Medium**: 3 (fix within 7 days)
**Low**: 2 (fix next sprint)

**Estimated Remediation Time**: 4-6 hours
**Git History Cleanup**: Required
**Team Training**: Recommended

**Overall Risk**: 🔴 CRITICAL - Immediate action required
```

## Notes

- Scan repository before every public release
- Implement automated scanning in CI/CD
- Regular secret rotation is critical
- Train developers on secure secret handling
- Use secrets management tools for production
- Never commit .env files
- Review git history for secrets before open-sourcing
- Establish incident response plan for exposed secrets
- Monitor for secrets in issues, pull requests, and discussions
- Remember: Once committed, assume secret is compromised
