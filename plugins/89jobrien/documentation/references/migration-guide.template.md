---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# Migration Guide: {{FROM_VERSION}} to {{TO_VERSION}}

**Last Updated:** {{DATE}}
**Estimated Effort:** {{LOW|MEDIUM|HIGH}}
**Breaking Changes:** {{YES|NO}}

---

## Overview

{{MIGRATION_SUMMARY}}

### Who Should Migrate

- [ ] All users of {{FEATURE}}
- [ ] Users with custom {{COMPONENT}}
- [ ] Self-hosted deployments

### Prerequisites

- {{PREREQUISITE_1}}
- {{PREREQUISITE_2}}
- Backup your data before proceeding

---

## Breaking Changes

### {{BREAKING_CHANGE_1}}

**Before ({{OLD_VERSION}}):**

```{{LANGUAGE}}
{{OLD_CODE}}
```

**After ({{NEW_VERSION}}):**

```{{LANGUAGE}}
{{NEW_CODE}}
```

**Migration:**

1. {{STEP_1}}
2. {{STEP_2}}

**Automated Fix:**

```bash
{{CODEMOD_OR_SCRIPT}}
```

---

### {{BREAKING_CHANGE_2}}

**What Changed:** {{DESCRIPTION}}

**Impact:** {{WHO_IS_AFFECTED}}

**Action Required:**

- [ ] {{ACTION_1}}
- [ ] {{ACTION_2}}

---

## Deprecations

| Deprecated | Replacement | Removal Version |
|------------|-------------|-----------------|
| `{{OLD_API}}` | `{{NEW_API}}` | {{VERSION}} |
| `{{OLD_CONFIG}}` | `{{NEW_CONFIG}}` | {{VERSION}} |

### Deprecation Warnings

To see all deprecation warnings:

```bash
{{COMMAND_TO_SHOW_WARNINGS}}
```

---

## Step-by-Step Migration

### Step 1: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

```bash
{{COMMANDS}}
```

**Verification:**

```bash
{{VERIFICATION_COMMAND}}
```

Expected output:

```
{{EXPECTED_OUTPUT}}
```

---

### Step 2: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

**Before:**

```{{LANGUAGE}}
{{OLD_CODE}}
```

**After:**

```{{LANGUAGE}}
{{NEW_CODE}}
```

---

### Step 3: {{STEP_TITLE}}

{{STEP_DESCRIPTION}}

| Old | New |
|-----|-----|
| `{{OLD}}` | `{{NEW}}` |

---

## Configuration Changes

### Environment Variables

| Old Variable | New Variable | Default |
|--------------|--------------|---------|
| `{{OLD_VAR}}` | `{{NEW_VAR}}` | `{{DEFAULT}}` |

### Config File Changes

**Before (`{{CONFIG_FILE}}`):**

```{{FORMAT}}
{{OLD_CONFIG}}
```

**After (`{{CONFIG_FILE}}`):**

```{{FORMAT}}
{{NEW_CONFIG}}
```

---

## Database Migrations

### Required Migrations

```bash
{{MIGRATION_COMMAND}}
```

### Schema Changes

| Table | Change | SQL |
|-------|--------|-----|
| `{{TABLE}}` | {{ADD/MODIFY/DROP}} | `{{SQL}}` |

### Data Migration

```sql
{{DATA_MIGRATION_SQL}}
```

**Rollback:**

```sql
{{ROLLBACK_SQL}}
```

---

## Dependency Updates

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| `{{PKG}}` | `{{OLD}}` | `{{NEW}}` | {{NOTES}} |

```bash
{{UPDATE_COMMAND}}
```

---

## API Changes

### Endpoint Changes

| Old Endpoint | New Endpoint | Method |
|--------------|--------------|--------|
| `{{OLD_PATH}}` | `{{NEW_PATH}}` | {{METHOD}} |

### Request/Response Changes

**Before:**

```json
{{OLD_JSON}}
```

**After:**

```json
{{NEW_JSON}}
```

---

## Troubleshooting

### Common Issues

#### {{ISSUE_1}}

**Symptom:** {{SYMPTOM}}

**Cause:** {{CAUSE}}

**Solution:**

```bash
{{SOLUTION}}
```

---

#### {{ISSUE_2}}

**Symptom:** {{SYMPTOM}}

**Solution:** {{SOLUTION}}

---

## Rollback Procedure

If migration fails:

1. {{ROLLBACK_STEP_1}}
2. {{ROLLBACK_STEP_2}}
3. {{ROLLBACK_STEP_3}}

```bash
{{ROLLBACK_COMMANDS}}
```

---

## Verification Checklist

- [ ] All tests pass
- [ ] No deprecation warnings
- [ ] Application starts successfully
- [ ] Core functionality works
- [ ] Performance acceptable
- [ ] Logs show no errors

### Smoke Tests

```bash
{{SMOKE_TEST_COMMANDS}}
```

---

## Support

- Documentation: {{DOCS_URL}}
- Issues: {{ISSUES_URL}}
- Community: {{COMMUNITY_URL}}

---

## Quality Checklist

- [ ] All breaking changes documented
- [ ] Code examples show before/after
- [ ] Automated migration scripts provided where possible
- [ ] Rollback procedure documented
- [ ] Verification steps included
- [ ] Troubleshooting covers common issues
