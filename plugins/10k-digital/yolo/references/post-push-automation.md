# Post-Push Automatic Deployment

Reference for automatic deployment detection and execution after git push.

## Overview

When `auto_deploy: on` is enabled in CLAUDE.md, Claude automatically detects backend changes after a successful `git push` to `main` and proceeds with Lovable deployment without requiring manual `/deploy-edge` or `/apply-migration` commands.

## When Auto-Deploy Triggers

Auto-deploy activates when ALL of these conditions are met:

1. **Yolo mode is enabled** (`yolo_mode: on` in CLAUDE.md)
2. **Auto-deploy is enabled** (`auto_deploy: on` in CLAUDE.md)
3. **Git push to main was successful**
4. **Backend files were modified** in the push:
   - Edge functions: `supabase/functions/**/*`
   - Migrations: `supabase/migrations/*.sql`

## Detection Flow After Git Push

```
User completes work on backend files
    |
    v
git add . && git commit -m "..."
    |
    v
git push origin main
    |
    v
[Push succeeds]
    |
    v
Claude detects backend changes
    |
    +---> Edge functions modified?
    |         |
    |         +--> Yes: Queue edge function deployment
    |
    +---> Migrations added?
              |
              +--> Yes: Queue migration application
    |
    v
Check yolo_mode and auto_deploy settings
    |
    +--> Both ON: Execute automated deployment
    |
    +--> yolo_mode ON but auto_deploy OFF:
    |       Show: "Backend changes detected. Run /deploy-edge to deploy."
    |
    +--> yolo_mode OFF:
            Show manual prompts with tip to enable yolo mode
```

## Implementation Steps

### Step 1: Detect Backend Changes in Push

After a successful `git push origin main`:

```
1. Get the commit range that was pushed:
   - Run: git log origin/main@{1}..origin/main --name-only --pretty=format:""
   - This shows all files changed in the push

2. Check for edge function changes:
   - Filter files matching: supabase/functions/**/*
   - Extract function names (directory names under supabase/functions/)

3. Check for migration changes:
   - Filter files matching: supabase/migrations/*.sql
   - List new migration files

4. Build deployment queue:
   - If edge functions changed: Add "deploy-edge" task
   - If migrations added: Add "apply-migration" task
```

**Example detection output:**
```
Push analysis:
  Files changed: 5
  Edge functions modified: send-email, process-payment
  New migrations: 20250103_add_user_preferences.sql

Deployment queue:
  1. Deploy edge functions: send-email, process-payment
  2. Apply migration: 20250103_add_user_preferences.sql
```

### Step 2: Check Configuration

Read CLAUDE.md and verify settings:

```
1. Read CLAUDE.md file
2. Find "## Yolo Mode Configuration (Beta)" section
3. Extract:
   - yolo_mode: on/off
   - auto_deploy: on/off
   - yolo_testing: on/off
   - yolo_debug: on/off

4. Decision:
   - If yolo_mode: on AND auto_deploy: on → Proceed with automation
   - If yolo_mode: on AND auto_deploy: off → Show notification only
   - If yolo_mode: off → Show manual prompts
```

### Step 3: Execute Automated Deployment

When conditions are met, proceed with deployment:

```
Show progress message:
  "Auto-deploy: Backend changes detected, starting deployment..."

IMPORTANT: Wait for Lovable to sync from GitHub first!
  1. Navigate to Lovable project
  2. Wait for GitHub sync to complete (up to 2 minutes)
  3. Verify the pushed commit is visible in Lovable
  4. Only then proceed with deployment prompts

For edge functions:
  1. Validate secrets (scan for Deno.env.get patterns)
  2. If missing secrets → Warn and ask user to add them first
  3. Wait for sync verification
  4. If secrets OK and sync complete → Execute browser automation
  5. Run verification tests if yolo_testing: on

For migrations:
  1. Check for destructive operations
  2. If destructive → Warn and get user confirmation
  3. Wait for sync verification
  4. If safe or confirmed and sync complete → Execute browser automation
  5. Verify schema after application
```

### Step 3.5: Wait for GitHub Sync (CRITICAL)

**Why this matters:** Lovable syncs from GitHub asynchronously. If we submit a deployment prompt before Lovable has the latest code, the deployment will use stale code and fail or deploy the wrong version.

**Sync timing:** Lovable typically syncs within 1-2 minutes of a push to main.

> **NEW APPROACH:** Navigate immediately, check chat history for sync confirmation.

**Verification process:**
```
1. Navigate to Lovable project page IMMEDIATELY (no initial wait)

2. Check LEFT SIDEBAR chat history for sync confirmation:
   VISUAL REFERENCE:
   See: skills/yolo/references/lovable-commented-screenshot.png
   - Left sidebar is the scrollable chat history area
   - GitHub commits appear as conversation items
   - Example: "Fix Mercado Pago installment config..." with GitHub icon

   WHAT TO LOOK FOR:
   - Conversation item in left sidebar
   - GitHub icon (looks like small octocat/mark before the text)
   - Message text matches your commit message (first ~50 chars)
   - May show "Active Edit" or "Code" buttons below
   - Appears as a clickable conversation item

   WHERE TO LOOK:
   - Left sidebar (scrollable conversation history)
   - Scroll to the BOTTOM - newest items at bottom
   - Should appear within seconds after push

   EXACT VISUAL PATTERN:
   [GitHub Icon] "Your commit message here..."
                 Active Edit        Code

   Example from screenshot: "Fix Mercado Pago installment config..."

3. Fast checking loop:
   - Check immediately first (no wait)
   - If not found: Wait 4 seconds, check again
   - Keep checking every 4 seconds
   - Max attempts: 20 (total 80 seconds max)

4. If sync found:
   → Proceed to deployment prompt

5. If not found after 80 seconds:
   → Show warning
   → Ask user to verify manually
   → Provide manual fallback prompt
```

**Sync verification output:**
```
⏳ Step 2/8: Checking for GitHub sync...
  Commit pushed: abc1234 "Add email notifications"
  Checking left sidebar chat history...
  ⏳ Checking... (0s - immediate)
  ⏳ Checking... (4s)
  ⏳ Checking... (8s)
  ✅ Sync confirmed! Found commit in chat history.

  Much faster than old 30s+ approach!
```

**If sync times out:**
```
⚠️ Sync verification timeout

Couldn't confirm GitHub sync after 80 seconds of checking.
This can happen if:
- Sync is taking longer than usual
- GitHub webhook didn't trigger
- Network issues
- Chat history not showing the commit yet

**Options:**
1. Wait and retry: I'll check again (4 more attempts)
2. Proceed anyway: Deploy with current code (may use stale version)
3. Manual check: Verify sync in Lovable, then run /deploy-edge

What would you like to do?
```

### Step 4: Show Results

After deployment completes:

```
## Auto-Deploy Summary

**Trigger:** git push to main
**Changes detected:**
- Edge functions: send-email, process-payment
- Migrations: 20250103_add_user_preferences.sql

**Deployments:**
1. ✅ Edge functions deployed
   - send-email: Deployed successfully
   - process-payment: Deployed successfully

2. ✅ Migration applied
   - 20250103_add_user_preferences.sql: Applied

**Verification:** (if testing enabled)
- ✅ Basic: All deployments confirmed
- ✅ Console: No errors detected
- ✅ Functional: All tests passed

**Duration:** 52 seconds

💡 Auto-deploy is enabled. Run `/yolo --no-auto-deploy` to disable.
```

---

## User Notifications

### When Auto-Deploy Starts

```
🤖 **Auto-Deploy Triggered**

Backend changes detected in your push to main:
- Edge functions: send-email
- Migrations: None

Starting automated deployment...

⏳ Step 1/8: Navigating to Lovable project...
⏳ Step 2/8: Waiting for GitHub sync to complete...
✅ Step 3/8: Sync verified - Lovable has latest code
⏳ Step 4/8: Locating chat interface...
```

### When Auto-Deploy is Disabled

If `yolo_mode: on` but `auto_deploy: off`:

```
📦 **Backend Changes Detected**

Your push to main included backend changes:
- Edge functions: send-email
- Migrations: 20250103_add_preferences.sql

These changes require Lovable deployment.

**Options:**
1. Run `/lovable:deploy-edge` to deploy edge functions
2. Run `/lovable:apply-migration` to apply migrations
3. Enable auto-deploy: `/lovable:yolo --auto-deploy`
```

### When Yolo Mode is Disabled

If `yolo_mode: off`:

```
📦 **Backend Changes Detected**

Your push to main included backend changes that require Lovable deployment.

**Edge Functions:** send-email

📋 **LOVABLE PROMPT:**
> "Deploy the send-email edge function"

**Migrations:** 20250103_add_preferences.sql

📋 **LOVABLE PROMPT:**
> "Apply pending Supabase migrations"

💡 **Tip:** Enable yolo mode to automate this!
   Run: /lovable:yolo on --auto-deploy
   Benefits: Automatic deployment after every push
```

---

## Graceful Fallback Handling

Auto-deploy MUST gracefully fall back to manual instructions when:

### 1. Browser Automation Unavailable

```
❌ **Auto-deploy failed:** Browser automation unavailable

The Claude in Chrome extension is required for automated deployment.

**Fallback - Manual Deployment:**

📋 **LOVABLE PROMPT (Edge Functions):**
> "Deploy all edge functions"

📋 **LOVABLE PROMPT (Migrations):**
> "Apply pending Supabase migrations"

💡 Install Chrome extension: https://chrome.google.com/webstore/detail/claude/...
```

### 2. User Not Logged Into Lovable

```
🔐 **Auto-deploy paused:** Please log in to Lovable

I opened your Lovable project but you're not logged in.
Please log in, then I'll continue automatically.

[Waiting for login...]

**Or complete manually:**
📋 "Deploy the send-email edge function"
```

### 3. Lovable UI Not Found

```
❌ **Auto-deploy failed:** Could not locate Lovable chat interface

The Lovable UI may have changed. Please complete deployment manually.

**Fallback - Manual Deployment:**

📋 **LOVABLE PROMPT:**
> "Deploy the send-email edge function"

💡 Please report this issue: https://github.com/10k-digital/lovable-claude-code/issues
```

### 4. Timeout

```
⏱️ **Auto-deploy timeout:** No response after 3 minutes

The deployment may still be processing. Please check Lovable manually.

**What was submitted:**
📋 "Deploy the send-email edge function"

**Suggestions:**
- Check Lovable for deployment status
- Look for error messages in Lovable
- Try refreshing the Lovable page
```

### 5. Deployment Failed in Lovable

```
❌ **Auto-deploy failed:** Lovable reported an error

**Error from Lovable:**
"Could not deploy function: RESEND_API_KEY is not set"

**Suggested fixes:**
1. Add the missing secret in Cloud → Secrets
2. Re-run deployment with `/lovable:deploy-edge`

**Or manually in Lovable:**
📋 "Deploy the send-email edge function"
```

### 6. Missing Secrets

```
⚠️ **Auto-deploy blocked:** Missing secrets

The following secrets are required but not configured:
- STRIPE_SECRET_KEY (used by process-payment)
- RESEND_API_KEY (used by send-email)

**To proceed:**
1. Go to Cloud → Secrets in Lovable
2. Add the missing secrets
3. Push changes again or run `/lovable:deploy-edge`

**I'll wait here.** Let me know when secrets are added, or:
- Type "skip" to deploy anyway (function will fail without secrets)
- Type "cancel" to skip deployment
```

---

## Order of Operations

When both edge functions and migrations need deployment:

```
1. **Apply migrations FIRST**
   - Migrations often create tables/columns that functions depend on
   - Wait for migration to complete before deploying functions

2. **Deploy edge functions SECOND**
   - Functions may reference new tables from migrations
   - Deploy after schema is updated

Example sequence:
  ⏳ Step 1: Applying migration 20250103_add_preferences.sql...
  ✅ Migration applied
  ⏳ Step 2: Deploying send-email edge function...
  ✅ Edge function deployed
  ⏳ Step 3: Running verification tests...
  ✅ All tests passed
```

---

## Configuration in CLAUDE.md

Add this to the Yolo Mode Configuration section:

```markdown
## Yolo Mode Configuration (Beta)

- **Status**: on
- **Auto-Deploy**: on     # NEW: Deploy automatically after git push
- **Deployment Testing**: on
- **Auto-run Tests**: off
- **Debug Mode**: off
- **Last Updated**: 2025-01-03 10:30:00
```

**Configure with:**
```
/lovable:yolo on --auto-deploy     # Enable auto-deploy
/lovable:yolo on --no-auto-deploy  # Disable auto-deploy (manual commands only)
```

---

## Debug Mode Output

When `yolo_debug: on`, show detailed auto-deploy information:

```
🐛 DEBUG: Auto-Deploy Detection

Git push completed to: origin/main
Commit range: abc123..def456

Files in push:
  - supabase/functions/send-email/index.ts (modified)
  - supabase/functions/send-email/utils.ts (modified)
  - src/components/EmailForm.tsx (modified)

Backend file analysis:
  Edge functions:
    - send-email: 2 files changed
  Migrations:
    - None

Configuration check:
  CLAUDE.md found: Yes
  yolo_mode: on
  auto_deploy: on
  yolo_testing: on
  yolo_debug: on

Decision: ✅ Proceed with automated deployment

Secret validation:
  Scanning supabase/functions/send-email/...
  Found: RESEND_API_KEY
  Status: ✅ In Lovable Cloud (from CLAUDE.md secrets table)

Starting automation workflow...
```

---

## Best Practices

### When to Enable Auto-Deploy

**Good for:**
- Active development with frequent backend changes
- Solo developers who want maximum automation
- Teams with robust CI/CD who trust automated deployments

**Less ideal for:**
- Production environments requiring review
- Teams with strict change management
- Projects with complex secret dependencies

### Recommendations

1. **Start with auto-deploy off**
   - Get comfortable with yolo mode first
   - Enable auto-deploy once workflow is established

2. **Keep testing enabled**
   - Even with auto-deploy, verification tests catch issues
   - Only disable testing for speed-critical workflows

3. **Monitor first few auto-deploys**
   - Watch the automation run
   - Verify deployments complete successfully
   - Adjust settings based on results

4. **Have a rollback plan**
   - Know how to revert deployments in Lovable
   - Keep backup of previous function versions

---

## Error Recovery

If auto-deploy fails repeatedly:

1. **Disable auto-deploy temporarily:**
   ```
   /lovable:yolo --no-auto-deploy
   ```

2. **Debug the issue:**
   - Enable debug mode: `/lovable:yolo --debug`
   - Push changes and observe detailed output
   - Check for patterns in failures

3. **Fix underlying issue:**
   - Missing secrets: Add to Cloud → Secrets
   - UI changes: Report issue, use manual commands
   - Login issues: Ensure logged into Lovable

4. **Re-enable when fixed:**
   ```
   /lovable:yolo --auto-deploy
   ```

---

*This reference enables fully automated deployment after git push while maintaining safety through graceful fallbacks and clear error messages.*
