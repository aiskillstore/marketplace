# Git Operations with Bitbucket Credentials

## Critical Discovery: Email vs Username Requirements

Through testing, we've discovered that Bitbucket has **DIFFERENT** authentication requirements for API vs Git operations:

### Test Results Summary

| Operation Type | Email (`akhil@apra.in`) | Username (`kumaakh`) |
|----------------|------------------------|---------------------|
| **API Calls** | ✅ **Works** (HTTP 200) | ❌ **Fails** (HTTP 401) |
| **Git Operations** | ❌ **Fails** (Auth failed) | ✅ **Works** (Success) |

### Detailed Test Evidence

#### API Authentication Test
```bash
# With EMAIL - SUCCESS
curl -u "akhil@apra.in:APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/kumaakh"
# Result: HTTP 200 ✅

# With USERNAME - FAILURE
curl -u "kumaakh:APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/kumaakh"
# Result: HTTP 401 Unauthorized ❌
```

#### Git Authentication Test
```bash
# With EMAIL - FAILURE
git ls-remote https://akhil%40apra.in:APP_PASSWORD@bitbucket.org/kumaakh/repo.git HEAD
# Result: Authentication failed ❌

# With USERNAME - SUCCESS
git ls-remote https://kumaakh:APP_PASSWORD@bitbucket.org/kumaakh/repo.git HEAD
# Result: Returns HEAD commit ✅
```

## Why This Happens

**Bitbucket App Passwords are tied to your ACCOUNT (email), not your workspace:**

1. **API Operations:** Authenticate against your Bitbucket account → requires **EMAIL**
2. **Git Operations:** Authenticate against the repository workspace → requires **USERNAME** (workspace slug)

## Current Skill Configuration (IMPLEMENTED)

The skill now uses separate fields for API and git operations:

```json
{
  "url": "https://api.bitbucket.org/2.0",
  "workspace": "kumaakh",
  "user_email": "akhil@apra.in",
  "username": "kumaakh",
  "password": "APP_PASSWORD"
}
```

**Status:**
- ✅ All API operations work (using `user_email`)
- ✅ Git operations work (using `username`)
- ✅ Validation prevents field confusion

## Implementation Details

The refactoring uses clear, semantically correct field names:

### Credential Mapping

```javascript
// In bitbucket-mcp/src/index-cli.ts loadConfig():
return {
  baseUrl: creds.url || "https://api.bitbucket.org/2.0",
  username: creds.user_email,        // API auth uses email
  password: creds.password,
  defaultWorkspace: creds.workspace || creds.username,
  gitUsername: creds.username,       // Git ops use username
};
```

### Git Helper Functions (lib/helpers.js)

```javascript
export function buildGitUrl(workspace, repo) {
  const creds = loadCredentials();

  // Git operations use username (workspace slug), not user_email
  const gitUsername = creds.username;  // "kumaakh" not "akhil@apra.in"
  const password = creds.password;

  const encodedPassword = encodeURIComponent(password);
  return `https://${gitUsername}:${encodedPassword}@bitbucket.org/${workspace}/${repo}.git`;
}

export function testGitAuth(workspace, repo) {
  const gitUrl = buildGitUrl(workspace, repo);
  const result = execSync(`git ls-remote ${gitUrl} HEAD`, {
    encoding: 'utf-8',
    stdio: ['pipe', 'pipe', 'pipe']
  });

  const commit = result.trim().split('\t')[0];
  return { success: true, commit };
}

export function cloneRepository(workspace, repo, targetDir = null) {
  const gitUrl = buildGitUrl(workspace, repo);
  const target = targetDir || repo;

  execSync(`git clone ${gitUrl} ${target}`, {
    encoding: 'utf-8',
    stdio: 'inherit'
  });

  return { success: true, directory: target };
}
```

### Validation

The skill validates credentials and provides helpful errors:

**Email in `username` field:**
```
Error: Invalid credentials:
  'username' should be your Bitbucket username, not email.
  Got: "akhil@apra.in" (this looks like an email)
  Expected: Your workspace slug (e.g., "kumaakh")
  Fix: Change "username": "akhil@apra.in" to "username": "kumaakh"
```

**Missing `user_email`:**
```
Error: Missing required field:
  'user_email' (your Bitbucket account email) is required.
  Example: "user_email": "akhil@apra.in"
```

## Using Git Operations

The skill includes built-in git helper commands:

### Test Git Authentication
```bash
node lib/helpers.js test-git-auth kumaakh apra-licensing-core
```

**Output:**
```json
{
  "success": true,
  "commit": "372812ce91cd5f27df3bd7dcdb00ffd20ab704ce",
  "message": "Git authentication successful for kumaakh/apra-licensing-core"
}
```

### Clone a Repository
```bash
node lib/helpers.js clone-repo kumaakh my-repo [target-dir]
```

**Output:**
```json
{
  "success": true,
  "directory": "my-repo",
  "message": "Successfully cloned kumaakh/my-repo to my-repo"
}
```

## Security Note

When building git URLs with embedded credentials:
- ✅ Use for temporary operations (clone, pull in scripts)
- ❌ Don't log or display the full URL (contains password)
- ✅ Consider using git credential helpers for persistent operations

## Summary

**Implemented Solution:**
- ✅ `user_email`: Email address for Bitbucket API authentication
- ✅ `username`: Workspace slug for git operations
- ✅ Validation prevents accidental field swapping
- ✅ Git helper functions included (`test-git-auth`, `clone-repo`)

**Benefits:**
1. **Clear semantics**: Fields named for their actual purpose
2. **No confusion**: Validation catches common mistakes
3. **Git-ready**: Git operations work out of the box
4. **Self-documenting**: Code clearly shows what each field does

**Key Insight:**
The workspace slug serves triple duty:
1. Repository path in Bitbucket URLs
2. Username for git authentication
3. Default workspace for API operations

By separating `user_email` (for API) from `username` (for git), the skill now supports both operations seamlessly! 🎯
