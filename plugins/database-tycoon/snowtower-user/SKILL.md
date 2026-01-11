---
name: snowtower-user
description: Helps end-users get Snowflake access and use the platform. Use when users ask about requesting access, generating RSA keys, connecting to Snowflake, or basic Snowflake usage. Triggers on mentions of access requests, RSA keys, connection issues, or "how do I get access".
---

# SnowTower End-User Guide

A skill for helping end-users navigate the SnowTower platform to get Snowflake access and start working with data.

## Who This Skill Is For

- **Data analysts** who need to query Snowflake data
- **Data scientists** who need database access for analysis
- **Engineers** who need to connect applications to Snowflake
- **New team members** requesting their first Snowflake account

## Quick Reference

### Getting Access (3 Steps)

```
Step 1: Generate RSA Keys    →    Step 2: Submit Request    →    Step 3: Connect
   (on your machine)              (GitHub issue)               (after approval)
```

---

## Step 1: Generate Your RSA Keys

**You MUST do this BEFORE requesting access.**

```bash
# Generate RSA key pair (run on your local machine)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -nocrypt -out ~/.ssh/snowflake_rsa_key.p8
openssl rsa -in ~/.ssh/snowflake_rsa_key.p8 -pubout -out ~/.ssh/snowflake_rsa_key.pub

# Secure your private key (IMPORTANT!)
chmod 400 ~/.ssh/snowflake_rsa_key.p8

# Display your PUBLIC key (copy this for the access request)
cat ~/.ssh/snowflake_rsa_key.pub
```

**Output looks like:**
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
...many lines of characters...
-----END PUBLIC KEY-----
```

### Key Security Rules

| Key Type | File | Share? |
|----------|------|--------|
| **Private key** | `~/.ssh/snowflake_rsa_key.p8` | **NEVER share this** |
| **Public key** | `~/.ssh/snowflake_rsa_key.pub` | Safe to share |

---

## Step 2: Request Access

1. Go to the **[Access Request Form](../../issues/new/choose)**
2. Select "New User Request"
3. Fill in your details:
   - Full name
   - Email address
   - Team/department
   - Reason for access
   - **Paste your PUBLIC key** (from Step 1)
4. Submit the form

**Typical approval time:** 3-5 business days

---

## Step 3: Connect to Snowflake

After your account is approved, you'll receive:
- Your **username** (usually FIRSTNAME_LASTNAME)
- The **account identifier**
- Your **default role** and **warehouse**

### Using Snow CLI (Recommended)

```bash
# Add your connection
snow connection add \
  --connection-name prod \
  --account YOUR_ACCOUNT \
  --user YOUR_USERNAME \
  --authenticator SNOWFLAKE_JWT \
  --private-key-path ~/.ssh/snowflake_rsa_key.p8

# Test the connection
snow sql -c prod -q "SELECT CURRENT_USER(), CURRENT_ROLE()"
```

### Using Python

```python
import snowflake.connector

conn = snowflake.connector.connect(
    account='YOUR_ACCOUNT',
    user='YOUR_USERNAME',
    private_key_file_pwd=None,
    private_key_file='~/.ssh/snowflake_rsa_key.p8',
    warehouse='MAIN_WAREHOUSE',
    role='YOUR_ROLE'
)
```

### Using the Snowflake Web UI

1. Go to your organization's Snowflake URL
2. Enter your username
3. Use the **password provided by IT** (not your RSA key)
4. Enable MFA when prompted

---

## What You Get After Approval

### Your Default Role

New users typically receive a role like `SNOWTOWER_USERS__T_ROLE` which grants:
- Read access to shared production data
- Access to common warehouses
- Ability to create objects in your personal database

### Your Personal Database

You get your own database: `DEV_YOURNAME`

```sql
-- Switch to your database
USE DATABASE DEV_YOURNAME;

-- Create schemas and tables freely
CREATE SCHEMA my_analysis;
CREATE TABLE my_analysis.test_data (id INT, value VARCHAR);
```

### Your Default Warehouse

Usually `MAIN_WAREHOUSE`:
- Auto-suspends after 60 seconds of inactivity
- X-Small size by default
- Shared resource - be mindful of heavy queries

---

## First Session Checklist

```sql
-- 1. Check your current context
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();

-- 2. See what databases you can access
SHOW DATABASES;

-- 3. See what roles you have
SHOW ROLES;

-- 4. Switch to your dev database
USE DATABASE DEV_YOURNAME;

-- 5. Create your first schema
CREATE SCHEMA IF NOT EXISTS sandbox;
USE SCHEMA sandbox;

-- 6. Test creating a table
CREATE TABLE test (id INT);
INSERT INTO test VALUES (1), (2), (3);
SELECT * FROM test;
DROP TABLE test;
```

---

## Common Issues & Solutions

### "Authentication failed"

**Cause:** RSA key mismatch or incorrect setup

**Solution:**
```bash
# Verify your private key is readable
ls -la ~/.ssh/snowflake_rsa_key.p8

# Check permissions (should be 400 or 600)
chmod 400 ~/.ssh/snowflake_rsa_key.p8

# Verify the public key matches what was submitted
cat ~/.ssh/snowflake_rsa_key.pub
```

### "Insufficient privileges"

**Cause:** You don't have access to that object

**Solution:**
- Check you're using the correct role: `SELECT CURRENT_ROLE();`
- Request additional access if needed via GitHub issue

### "Warehouse is suspended"

**Cause:** Warehouse auto-suspended to save costs

**Solution:**
```sql
-- Just run a query - it auto-resumes
SELECT 1;
```

### "Cannot connect to Snowflake"

**Checklist:**
1. Is your account approved? (Check the GitHub issue)
2. Is the account identifier correct?
3. Is your private key path correct?
4. Are you on the corporate network / VPN if required?

---

## Getting More Access

Need access to additional databases, schemas, or roles?

1. Open a new GitHub issue
2. Specify exactly what you need access to
3. Include business justification
4. Your request will be reviewed by an admin

---

## Two Authentication Methods

| Method | Use For | How |
|--------|---------|-----|
| **RSA Key** | CLI, scripts, applications | Private key file |
| **Password** | Web UI only | Provided by IT |

**Best Practice:** Always use RSA key authentication for programmatic access. Only use password for the web interface.

---

## Need Help?

- **Access issues:** Open a GitHub issue
- **Connection problems:** Check the troubleshooting section above
- **General questions:** Ask your team lead or Snowflake admin
