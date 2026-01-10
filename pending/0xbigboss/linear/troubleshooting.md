# Troubleshooting

Common errors and their solutions when using the Linear CLI.

## Table of Contents

1. [Authentication Errors](#authentication-errors)
2. [Empty Results](#empty-results)
3. [Mutation Errors](#mutation-errors)
4. [GraphQL Errors](#graphql-errors)
5. [Connection Errors](#connection-errors)
6. [Debugging Steps](#debugging-steps)

---

## Authentication Errors

### 401 Unauthorized

**Symptom:** Command fails with `401` or "Unauthorized" message.

**Causes:**
- API key not configured
- API key expired or revoked
- Wrong API key format

**Solutions:**

```bash
# Test current auth
linear auth test

# Reconfigure API key
linear auth set

# Check what key is configured (masked)
linear auth show --redacted
```

**Note:** API keys are created at [Linear Settings → API](https://linear.app/settings/api).

### Missing API Key

**Symptom:** "No API key configured" or similar message.

**Solution:**
```bash
# Option 1: Interactive setup
linear auth set

# Option 2: Environment variable
export LINEAR_API_KEY="lin_api_..."
linear auth test

# Option 3: Direct flag
linear auth set --api-key "lin_api_..."
```

---

## Empty Results

### No Issues Returned

**Symptom:** `linear issues list` returns 0 items.

**Causes:**
1. No team specified and no default team set
2. All issues are completed/canceled (filtered by default)
3. Wrong team key/ID

**Solutions:**

```bash
# List available teams first
linear teams list

# Specify team explicitly
linear issues list --team TEAM_KEY

# Include all issues (including completed/canceled)
linear issues list --team TEAM_KEY --state-type backlog,unstarted,started,completed,canceled
```

### Issue Not Found

**Symptom:** "Issue not found" when using `issue view`.

**Causes:**
- Using UUID instead of identifier (or vice versa)
- Issue was deleted
- No access to that issue

**Solutions:**
```bash
# Use identifier format (preferred)
linear issue view ENG-123

# If you have UUID, it also works
linear issue view "uuid-string-here"
```

---

## Mutation Errors

### Mutation Does Nothing

**Symptom:** `issue create` or `issue delete` exits without action.

**Cause:** Mutations require explicit confirmation.

**Solution:** Add `--yes` flag:
```bash
linear issue create --team OUT --title "Task" --yes
linear issue delete ENG-123 --yes
```

### Missing Required Fields

**Symptom:** "Missing required field" error on create.

**Required fields for `issue create`:**
- `--team` (team ID or key)
- `--title` (issue title)
- `--yes` (confirmation)

```bash
linear issue create --team OUT --title "My task" --yes
```

---

## GraphQL Errors

### Invalid Query Syntax

**Symptom:** GraphQL syntax error.

**Solutions:**
1. Validate query in [Apollo Studio](https://studio.apollographql.com/public/Linear-API/variant/current/explorer)
2. Check for missing braces or typos
3. Ensure variable types match schema

### Variable Type Mismatch

**Symptom:** "Variable $x got invalid value" error.

**Common issues:**
- String where ID expected (use UUID, not identifier)
- Missing required variables
- Wrong enum value

```bash
# Wrong: using identifier
--vars '{"issueId":"ENG-123"}'

# Correct: using UUID
--vars '{"issueId":"abc123-uuid-here"}'
```

### Field Not Found

**Symptom:** "Cannot query field X on type Y"

**Cause:** Field doesn't exist or is named differently.

**Solution:** Check schema in [Apollo Studio](https://studio.apollographql.com/public/Linear-API/variant/current/schema/reference).

---

## Connection Errors

### Timeout

**Symptom:** Request times out.

**Solutions:**
```bash
# Increase timeout (milliseconds)
linear issues list --timeout-ms 30000

# Retry on failure
linear issues list --retries 3
```

### Network Errors

**Symptom:** Connection refused or network unreachable.

**Solutions:**
1. Check internet connection
2. Verify Linear API is up: https://status.linear.app
3. Check if corporate firewall blocks `api.linear.app`

---

## Debugging Steps

### Step 1: Verify Authentication
```bash
linear auth test
```

Expected: Shows your user info.

### Step 2: Check Team Access
```bash
linear teams list
```

Verify your team appears in the list.

### Step 3: Test Simple Query
```bash
linear me
```

Should show your user details.

### Step 4: Check Issue Exists
```bash
linear issue view ISSUE-ID --json
```

### Step 5: Enable Verbose Output
```bash
# Get full JSON response
linear issues list --team TEAM --json

# For GraphQL, check raw response
echo 'query { viewer { id } }' | linear gql --json
```

### Step 6: Validate GraphQL in Studio

1. Go to [Apollo Studio Explorer](https://studio.apollographql.com/public/Linear-API/variant/current/explorer)
2. Add header: `Authorization: YOUR_API_KEY`
3. Test your query interactively

---

## Config File Issues

### Location
Config is stored at `~/.config/linear/config.json`.

### Check Current Config
```bash
cat ~/.config/linear/config.json
```

### Reset Config
```bash
rm ~/.config/linear/config.json
linear auth set
```

### Permission Issues
Config should have mode 0600. If warnings appear:
```bash
chmod 600 ~/.config/linear/config.json
```
