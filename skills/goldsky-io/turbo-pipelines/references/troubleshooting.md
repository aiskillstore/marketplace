# Turbo Pipeline Troubleshooting Reference

## CLI Hanging or Not Responding

If `goldsky` commands hang without producing output:

**Symptom:** Command runs but produces no output, cursor just sits there.

**Cause:** Often caused by the update notifier trying to check for updates and failing (network issues, DNS resolution, etc.)

**Solutions:**

1. **Disable update notifier:**

   ```bash
   GOLDSKY_NO_UPDATE_NOTIFIER=1 goldsky project list
   ```

2. **Set timeout for commands:**

   ```bash
   timeout 30 goldsky project list
   ```

3. **Check network connectivity:**

   ```bash
   curl -I https://goldsky.com
   ```

4. **If the goldsky CLI works but `turbo` commands hang:**

   The `turbo` binary may need to be reinstalled:

   ```bash
   # Remove existing turbo binary
   rm -f ~/.goldsky/bin/turbo

   # Reinstall
   curl https://install-turbo.goldsky.com | sh
   ```

## Turbo Binary Not Found

**Symptom:** `goldsky turbo list` shows "The turbo binary is not installed"

**Solution:**

```bash
curl https://install-turbo.goldsky.com | sh
```

Then verify:

```bash
goldsky turbo list
```

## Common Validation Errors

**Error: Unknown dataset**

```
Error: Source 'my_source' references unknown dataset 'invalid.dataset'
```

Fix: Use correct format `<chain>.<dataset_type>`. Use validation to test: `goldsky turbo validate pipeline.yaml`. Note: `raw_transactions` not `transactions`.

**Error: Missing primary_key**

```
Error: Transform 'my_transform' requires primary_key
```

Fix: Add `primary_key: id` (or appropriate column) to the transform.

**Error: Unknown source reference**

```
Error: Transform 'filtered' references unknown source 'wrong_name'
```

Fix: Check the `FROM` clause in SQL matches the source name exactly.

**Error: Secret not found**

```
Error: Secret 'MY_SECRET' not found
```

Fix: Create the secret first with `goldsky secret create --name MY_SECRET`.

**Error: Invalid YAML syntax**

```
Error: YAML parsing failed
```

Fix: Check indentation (use spaces, not tabs). Validate YAML syntax online.

**Error: Duplicate primary key**

```
Error: Duplicate primary key in transform 'my_transform'
```

Fix: Ensure your SQL produces unique values for the `primary_key` column.

## Common Runtime Errors (After Deployment)

These errors appear in `goldsky turbo logs <pipeline>` after deployment:

**Error: Password authentication failed**

```
Execution error: Failed to create PostgreSQL connection: error returned from database: password authentication failed for user 'username'
```

**Cause:** Secret has incorrect credentials.
**Fix:**

1. Verify credentials work: `psql 'postgresql://user:pass@host/db'`
2. Update the secret: `goldsky secret update SECRET_NAME --value '...'`
3. Redeploy: `goldsky turbo apply pipeline.yaml`

**Error: Project size limit exceeded (Neon free tier)**

```
Execution error: Failed to create table '...': error returned from database: could not extend file because project size limit (512 MB) has been exceeded
```

**Cause:** Neon free tier databases are limited to 512MB.
**Fix:**

1. Upgrade Neon plan, OR
2. Use a different database, OR
3. Clear existing data from the database

**Error: Connection refused**

```
Execution error: Failed to create PostgreSQL connection: Connection refused
```

**Cause:** Database is unreachable (firewall, wrong host, database down).
**Fix:**

1. Verify the host is correct
2. Check database is running
3. Ensure Goldsky IPs are allowed through firewall

**Error: SSL required**

```
Execution error: SSL connection is required
```

**Cause:** Database requires SSL but secret doesn't enable it.
**Fix:** Most managed PostgreSQL (Neon, Supabase) handle SSL automatically. If using self-hosted, configure SSL in your database.

## Quick Troubleshooting Table

| Issue                          | Action                                                            |
| ------------------------------ | ----------------------------------------------------------------- |
| **CLI hangs / no output**      | Run with `GOLDSKY_NO_UPDATE_NOTIFIER=1 goldsky <command>`         |
| **Turbo binary not installed** | Run `curl https://install-turbo.goldsky.com \| sh`                |
| **"turbo binary not found"**   | Same as above - Turbo is a separate binary that must be installed |
| Not logged in                  | Use `/auth-setup` skill                                           |
| Secret not found               | Use `/secrets` skill to create it                                 |
| Dataset not found              | Use `raw_transactions` not `transactions`. Validate first         |
| Validation failed              | Review error message and fix YAML syntax                          |
| Pipeline name exists           | Use different name or delete existing pipeline                    |
| Permission denied              | Check you have Editor or Admin role                               |
| Transform not working          | Verify SQL syntax and column names                                |
| Sink not receiving data        | Check `from` field points to correct source/transform             |
| Data not flowing               | Check logs with `goldsky turbo logs <pipeline>`                   |
| Want to restart from scratch   | Rename the source or pipeline name                                |
| **Auth failed (runtime)**      | Update secret credentials, redeploy pipeline                      |
| **Storage limit exceeded**     | Neon free tier is 512MB - upgrade or use different DB             |
