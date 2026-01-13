---
name: snowtower-admin
description: Advanced skill for SnowTower infrastructure administrators. Use for SnowDDL operations, user provisioning, role management, CI/CD deployments, troubleshooting, and Snowflake administration. Triggers on mentions of snowddl, deploy, user creation, role grants, infrastructure changes, or admin operations.
---

# SnowTower Administrator Guide

A comprehensive skill for administrators managing Snowflake infrastructure through SnowTower.

## Who This Skill Is For

- **Infrastructure administrators** managing SnowDDL deployments
- **Security admins** handling user provisioning and roles
- **DevOps engineers** managing CI/CD pipelines
- **On-call engineers** troubleshooting production issues

---

## Quick Command Reference

```bash
# Essential commands
uv run snowddl-plan          # Preview changes (ALWAYS run first)
uv run deploy-safe           # Apply changes safely
uv run manage-users          # User lifecycle management
uv run manage-warehouses     # Warehouse operations
uv run manage-costs          # Cost analysis
```

---

## Core Operations

### SnowDDL Deployment Workflow

**CRITICAL: Always use `deploy-safe`, never raw `snowddl-apply`**

```bash
# 1. Make changes to YAML files in snowddl/
vim snowddl/user.yaml

# 2. ALWAYS preview first
uv run snowddl-plan

# 3. Review the plan output carefully
# Look for: CREATE, ALTER, DROP, GRANT, REVOKE statements

# 4. Apply using safe deployment (preserves schema grants)
uv run deploy-safe
```

**Why `deploy-safe`?**
SnowDDL excludes SCHEMA objects from management, which can cause it to revoke schema-level grants. The `deploy-safe` wrapper automatically restores these grants after every deployment, preventing dbt and other tools from losing permissions.

### Understanding Plan Output

```
[APPLY] CREATE USER "NEW_USER"        ← New object will be created
[APPLY] ALTER USER "EXISTING_USER"    ← Object will be modified
[APPLY] DROP USER "OLD_USER"          ← Object will be deleted (CAREFUL!)
[APPLY] GRANT ROLE "X" TO USER "Y"    ← Permission will be added
[APPLY] REVOKE ROLE "X" FROM USER "Y" ← Permission will be removed
```

**Red flags to watch for:**
- Unexpected `DROP` statements
- Mass `REVOKE` statements (might be schema drift)
- Changes to admin roles (ACCOUNTADMIN, SECURITYADMIN)

---

## User Management

### Creating a New User

**Option 1: Interactive wizard (recommended)**
```bash
uv run manage-users create
```

**Option 2: Edit YAML directly**
```yaml
# snowddl/user.yaml
NEW_USER:
  comment: "Data Analyst - Analytics Team"
  type: PERSON
  default_role: ANALYST_ROLE__B_ROLE
  default_warehouse: MAIN_WAREHOUSE
  email: user@company.com
  authentication:
    password: !decrypt |
      gAAAAABl...encrypted...
    rsa_public_key: |
      -----BEGIN PUBLIC KEY-----
      MIIBIjAN...
      -----END PUBLIC KEY-----
```

**Option 3: Non-interactive**
```bash
uv run manage-users create \
  --first-name Jane \
  --last-name Smith \
  --email jane@company.com \
  --role ANALYST_ROLE
```

### User Types

| Type | Use For | MFA Required | Network Policy |
|------|---------|--------------|----------------|
| `PERSON` | Human users | Yes (by 2026) | Applied |
| `SERVICE` | Service accounts | No | Not applied |

### Encrypting Passwords

```bash
# Generate Fernet key (one-time setup)
uv run util-generate-key

# Encrypt a password
uv run snowddl-encrypt "MySecurePassword123!"
# Output: gAAAAABl...

# Use in YAML with !decrypt tag
authentication:
  password: !decrypt |
    gAAAAABl...encrypted_output...
```

### RSA Key Setup for Users

```bash
# Generate keys for a user
uv run generate-rsa-batch --users NEW_USER

# Or manually:
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -nocrypt -out user_key.p8
openssl rsa -in user_key.p8 -pubout -out user_key.pub

# Add public key to user.yaml
cat user_key.pub
```

---

## Role Hierarchy

### SnowDDL Role Naming Convention

```
ROLE_NAME__B_ROLE    → Business role (assigned to users)
ROLE_NAME__T_ROLE    → Technical role (assigned to business roles)
DB__SCHEMA__S_ROLE   → Schema role (auto-created by SnowDDL)
```

### Role Assignment Flow

```
User → Business Role (__B_ROLE) → Technical Roles (__T_ROLE) → Permissions
```

### Creating Roles

**Business Role** (`snowddl/business_role.yaml`):
```yaml
ANALYST_ROLE:
  comment: "Business analysts with read access"
  tech_roles:
    - STRIPE_READER_ROLE
    - ANALYTICS_READER_ROLE
  warehouse_usage:
    - MAIN_WAREHOUSE
  schema_read:
    - PROJ_STRIPE.ANALYTICS
```

**Technical Role** (`snowddl/tech_role.yaml`):
```yaml
STRIPE_READER_ROLE:
  grants:
    DATABASE:USAGE:
      - SOURCE_STRIPE
      - PROJ_STRIPE
    SCHEMA:USAGE:
      - SOURCE_STRIPE.STRIPE_WHY
      - PROJ_STRIPE.PROJ_STRIPE
    TABLE:SELECT:
      - SOURCE_STRIPE.STRIPE_WHY.*
```

---

## Database & Schema Management

### Creating a Database

```bash
# Create directory
mkdir snowddl/MY_NEW_DB

# Add params.yaml
cat > snowddl/MY_NEW_DB/params.yaml << 'EOF'
comment: "New database for analytics project"
is_transient: false
EOF

# Deploy
uv run snowddl-plan
uv run deploy-safe
```

### Creating a Schema

```bash
# Create schema directory
mkdir snowddl/MY_DB/MY_SCHEMA

# Add params.yaml
cat > snowddl/MY_DB/MY_SCHEMA/params.yaml << 'EOF'
comment: "Schema for raw data ingestion"
is_transient: false
is_sandbox: false
EOF
```

### Schema Types

| Parameter | Effect |
|-----------|--------|
| `is_transient: true` | No Time Travel, no Fail-safe |
| `is_sandbox: true` | Creates as TRANSIENT schema |

---

## CI/CD Operations

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PRs, pushes | Lint + test validation |
| `release.yml` | Tags `v*` | Create GitHub release |
| `labeler.yml` | PRs | Auto-label by file type |
| `changelog.yml` | Push to main | Update changelog |

### Making Infrastructure Changes via PR

```bash
# 1. Create feature branch
git checkout v0.2
git checkout -b feature/add-new-user

# 2. Make YAML changes
vim snowddl/user.yaml

# 3. Validate locally
uv run pre-commit run --all-files
uv run pytest

# 4. Commit and push
git add .
git commit -m "feat: Add new user JANE_DOE"
git push -u origin feature/add-new-user

# 5. Create PR
gh pr create --base v0.2

# 6. CI runs automatically, merge after approval
```

### Release Process

```bash
# After all PRs merged to v0.2
git checkout main
git pull
git merge v0.2
git tag v0.2.0
git push origin main --tags
# Release workflow creates GitHub release automatically
```

---

## Troubleshooting

### Schema Grant Drift

**Symptom:** Plan shows hundreds of REVOKE statements for schema grants

**Cause:** SnowDDL doesn't manage SCHEMA objects directly; grants from dbt or other tools appear as drift

**Solution:**
```bash
# Always use deploy-safe which auto-applies schema grants
uv run deploy-safe

# Or manually apply schema grants
uv run apply-schema-grants
```

### Authentication Failures

```bash
# Diagnose authentication issues
uv run util-diagnose-auth

# Fix common auth problems
uv run util-fix-auth

# Check specific user
snow sql -q "DESCRIBE USER USERNAME"
```

### User Locked Out

```sql
-- Check user status
SHOW USERS LIKE 'USERNAME';

-- Unlock user (as ACCOUNTADMIN)
ALTER USER USERNAME SET MINS_TO_UNLOCK = 0;

-- Check login history
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY
WHERE USER_NAME = 'USERNAME'
ORDER BY EVENT_TIMESTAMP DESC
LIMIT 10;
```

### SnowDDL Errors

**"Object does not exist"**
- Run with ACCOUNTADMIN: `uv run snowddl-plan` uses `-r ACCOUNTADMIN`
- Check object was created in correct database/schema

**"Insufficient privileges"**
- Verify SNOWFLAKE_ROLE is set to ACCOUNTADMIN
- Check the service account has required permissions

**Exit code 8**
- Means "changes applied successfully"
- Not an error, SnowDDL uses this to indicate modifications were made

---

## Security Operations

### Network Policies

```yaml
# snowddl/network_policy.yaml
corporate_network_policy:
  allowed_ip_list:
    - 192.0.2.0/24
    - 10.0.0.0/8
  comment: "Corporate network access only"
```

### MFA Compliance

**Deadline:** March 2026 for all human users

```bash
# Check MFA status
uv run manage-security --check-mfa

# List users without MFA
snow sql -q "
  SELECT name, has_mfa_registered
  FROM SNOWFLAKE.ACCOUNT_USAGE.USERS
  WHERE type = 'PERSON' AND NOT has_mfa_registered
"
```

### Emergency Access

The `STEPHEN_RECOVERY` account is configured without network policy for emergency access:
- Use only when primary access methods fail
- Requires password authentication
- Document all usage

---

## Cost Management

```bash
# Analyze costs
uv run manage-costs --analyze

# Check warehouse usage
uv run manage-warehouses --status

# Suspend all warehouses (emergency)
uv run manage-warehouses --suspend-all
```

### Warehouse Configuration

```yaml
# snowddl/warehouse.yaml
MAIN_WAREHOUSE:
  size: XSMALL
  auto_suspend: 60        # seconds
  auto_resume: true
  min_cluster_count: 1
  max_cluster_count: 1
  resource_monitor: main_monitor
```

---

## Key File Locations

| File | Purpose |
|------|---------|
| `snowddl/user.yaml` | User accounts |
| `snowddl/business_role.yaml` | Business roles |
| `snowddl/tech_role.yaml` | Technical roles with grants |
| `snowddl/warehouse.yaml` | Warehouse configuration |
| `snowddl/*_policy.yaml` | Security policies |
| `snowddl/{DB}/params.yaml` | Database configuration |
| `snowddl/{DB}/{SCHEMA}/params.yaml` | Schema configuration |

---

## Environment Variables

Required in `.env`:
```bash
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=SNOWDDL
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=ADMIN
SNOWFLAKE_PRIVATE_KEY_PATH=~/.ssh/snowflake_rsa_key.p8
SNOWFLAKE_CONFIG_FERNET_KEYS=your_fernet_key
```

---

## Emergency Procedures

### Rollback Last Deployment

```bash
# Revert YAML changes
git checkout HEAD~1 -- snowddl/

# Re-apply
uv run deploy-safe
```

### Complete Service Account Reset

```bash
# Regenerate RSA keys
uv run generate-rsa-batch --users SNOWDDL --force

# Update in Snowflake
snow sql -q "ALTER USER SNOWDDL SET RSA_PUBLIC_KEY='...'"

# Update GitHub secrets
gh secret set SNOWFLAKE_PRIVATE_KEY < new_key.p8
```

### Health Check

```bash
# Quick health check
uv run monitor-health

# Full system audit
uv run manage-security --full-audit
```
