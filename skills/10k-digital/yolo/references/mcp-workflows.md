# Yolo Mode: Lovable MCP Workflows

Reference for submitting Lovable prompts via the official Lovable MCP server. This is the **preferred method** over browser automation - it is faster, more reliable, and does not require the Chrome extension.

## Overview

The Lovable MCP server (`https://mcp.lovable.dev`) exposes tools that let Claude send prompts directly to a Lovable project via API. When the user has connected Lovable MCP in their Claude settings, Claude can call `send_message` instead of navigating the browser.

**Priority order for yolo mode:**
1. **MCP** (preferred) - Use Lovable MCP tools if available
2. **Browser automation** (fallback) - Use Claude's browser automation
3. **Manual** (last resort) - Show prompt for the user to copy-paste

## Prerequisites

- User has added Lovable as a connector in Claude settings (see `connect-mcp.md` command)
- `lovable_url` is set in CLAUDE.md (to extract the project ID)
- Lovable Pro or higher plan (required by Lovable MCP)

## Detecting MCP Availability

Before attempting MCP, check if Lovable MCP tools are available in the current session:

```
1. Look for available MCP tools that match "lovable" or have "send_message"
2. The tool will typically be named: mcp__Lovable__send_message
   (or similar depending on the connector name the user used)
3. If found → use MCP workflow
4. If not found → fall back to browser automation
```

**Detection approach:**
- Try to call `send_message` and check if the tool exists
- If tool not found, treat as MCP unavailable and fall back gracefully
- Do NOT error or block the user - MCP is optional

## Extracting the Project ID

The project ID is extracted from `lovable_url` in CLAUDE.md:

```
lovable_url: https://lovable.dev/projects/abc123-def456
                                          ^^^^^^^^^^^^^^^
                                          This is the project_id
```

Extraction logic:
```
1. Read `lovable_url` from CLAUDE.md
2. Parse the URL: https://lovable.dev/projects/{project_id}
3. Extract everything after the last `/`
4. Use this as the `project_id` parameter for send_message
```

Example:
- URL: `https://lovable.dev/projects/8f3a2b1c-4d5e-6789-abcd-ef0123456789`
- Project ID: `8f3a2b1c-4d5e-6789-abcd-ef0123456789`

## Core MCP Workflow

### Step 1: Check for GitHub Sync (Still Required)

Even with MCP, Lovable needs the latest code from GitHub before deploying:

```
IMPORTANT: send_message tells Lovable to deploy the code it has synced from GitHub.
If you send the prompt before GitHub sync completes, Lovable will deploy stale code.

Wait procedure (same as browser automation):
1. Confirm git push succeeded
2. Wait for GitHub → Lovable sync (typically 30-60 seconds)
3. Proceed with send_message once sync is expected to be complete

Alternatively: send_message with a note for Lovable to wait for latest sync
```

**Practical approach:**
- For auto-deploy: Wait ~30 seconds after git push before calling send_message
- For manual `/deploy-edge`: Code was pushed earlier, proceed immediately
- Lovable's agent is smart enough to verify sync state - trust it

### Step 2: Call send_message

Use the Lovable MCP `send_message` tool:

```
Tool: send_message (via Lovable MCP connector)

Parameters:
  project_id: [extracted from lovable_url]
  message: [the Lovable deployment prompt]

Example call:
  send_message(
    project_id: "abc123",
    message: "Deploy the send-email edge function"
  )
```

**Important:** `send_message` is **asynchronous** - Lovable's agent starts processing but the response may not be immediate. The tool may return a message ID that you can poll with `get_message`.

### Step 3: Poll for Completion

If `send_message` returns a message ID (async mode):

```
Poll using get_message:
  get_message(message_id: "[returned id]")

Polling strategy:
  - Poll every 5 seconds
  - Timeout after 180 seconds (3 minutes)
  - Check response for completion indicators

Completion indicators in response:
  - "deployed successfully"
  - "function is live"
  - "migration applied"
  - "deployment complete"

Error indicators:
  - "error"
  - "failed"
  - "could not"
```

If `send_message` returns the full response synchronously, skip polling.

### Step 4: Parse the Result

```
Success indicators:
  Edge functions:
  - "deploy" or "deployed"
  - "function is live"
  - "successfully deployed"

  Migrations:
  - "migration applied"
  - "database updated"
  - "schema updated"

Error indicators:
  - "error", "failed", "could not", "invalid", "syntax error"

Unclear response:
  - Show full response to user
  - Ask them to verify in Lovable manually
```

### Step 5: Run Verification Tests (if enabled)

After successful deployment, run tests based on `yolo_testing` setting.

**With MCP, Level 1 verification** (basic logs) is simplified:

```
Submit follow-up via send_message:
  message: "Show logs for [function-name] edge function"

Analyze response for:
  - No error indicators
  - Recent deployment timestamp
  - Function status: active
```

Level 2 (console checking) and Level 3 (functional testing) are the same as browser automation - they test the production URL directly, not through Lovable.

## Complete MCP Deployment Flow

### Edge Function Deployment

```
🤖 Yolo mode (MCP): Deploying send-email edge function

Step 1/5: Verifying code is pushed to GitHub... ✅
Step 2/5: Sending deployment prompt via Lovable MCP...
  → send_message(project_id="abc123", message="Deploy the send-email edge function")
  → Response received (3.2s)
Step 3/5: Parsing Lovable response... ✅ Deployment confirmed
Step 4/5: Running verification tests...
  → Level 1: Basic logs... ✅
  → Level 2: Console check... ✅
  → Level 3: Functional test... ✅
Step 5/5: All tests passed ✅

## Deployment Summary

Operation: Edge Function Deployment
Function: send-email
Method: Lovable MCP
Status: ✅ Success
Duration: 15 seconds
```

### Migration Application

```
🤖 Yolo mode (MCP): Applying database migration

Step 1/4: Verifying migration file is pushed to GitHub... ✅
Step 2/4: Sending migration prompt via Lovable MCP...
  → send_message(project_id="abc123", message="Apply pending Supabase migrations")
  → Response received (5.1s)
Step 3/4: Parsing Lovable response... ✅ Migration applied
Step 4/4: Running verification tests...
  → Level 1: Schema confirmation... ✅

## Migration Summary

Operation: Database Migration
Method: Lovable MCP
Status: ✅ Success
Duration: 12 seconds
```

## Error Handling

### MCP Not Available

```
When send_message tool is not found:

⚠️ Lovable MCP not connected

Falling back to browser automation...

[Continue with browser automation workflow]
```

If browser automation also fails:
```
❌ Automated deployment unavailable

MCP not connected + Browser automation failed.

Fallback: Run this prompt manually in Lovable:
📋 "Deploy the send-email edge function"

To enable MCP (recommended): /lovable:connect-mcp
```

### Missing Project ID

```
When lovable_url is not set in CLAUDE.md:

❌ Cannot use Lovable MCP: project URL not configured

Please provide your Lovable project URL to use MCP:
  1. Add to CLAUDE.md: Lovable Project URL: https://lovable.dev/projects/YOUR_ID
  2. Or run /lovable:init to reconfigure

Fallback: Run this prompt manually in Lovable:
📋 "[deployment prompt]"
```

### Deployment Failed via MCP

```
When send_message returns an error:

❌ Deployment failed via Lovable MCP

Error from Lovable:
[captured error message]

Suggested fixes:
- Check function code for syntax errors
- Verify required secrets are set in Cloud → Secrets
- Review function logs in Lovable

Fallback: You can also try running this manually:
📋 "[deployment prompt]"
```

### Authentication Error

```
When MCP returns auth/permission errors:

🔐 Lovable MCP authentication issue

Your Lovable MCP connection may have expired.

To reconnect:
  Run: /lovable:connect-mcp
  Then re-authorize via OAuth

Fallback: Run this prompt manually in Lovable:
📋 "[deployment prompt]"
```

### Rate Limit / Credits

```
When credits are insufficient:

⚠️ Lovable credits exhausted

send_message and create_project operations use Lovable credits.
Your workspace may have run out.

To check: Log in to Lovable → Workspace Settings → Credits

Fallback: Run this prompt manually in Lovable:
📋 "[deployment prompt]"
```

## Comparison: MCP vs Browser Automation

| Aspect | MCP | Browser Automation |
|--------|-----|-------------------|
| Speed | ~5-15s total | ~20-60s total |
| Reliability | High (API) | Medium (UI-dependent) |
| Requirements | Lovable Pro + connector | Chrome extension |
| GitHub sync wait | Still needed | Still needed |
| UI changes break it | No | Yes |
| Debug complexity | Low | High |

## Configuration in CLAUDE.md

The `Deployment Method` field controls which method to use:

```markdown
## Yolo Mode Configuration (Beta)

- **Status**: on
- **Deployment Method**: auto   # auto | mcp | browser
- **Deployment Testing**: on
- **Debug Mode**: off
```

**Options:**
- `auto` (default): Try MCP first, fall back to browser if not available
- `mcp`: Use MCP only, show manual prompt if MCP fails (skip browser)
- `browser`: Use browser automation only (legacy behavior)

## Progress Notifications

**MCP mode (debug off):**
```
🤖 Yolo mode (MCP): Deploying [function-name]

⏳ Sending prompt to Lovable via MCP...
✅ Deployment confirmed by Lovable
⏳ Running verification tests...
✅ All tests passed
```

**MCP mode (debug on):**
```
🐛 DEBUG: Yolo mode - MCP Deployment

Project ID: abc123
Tool: send_message
Message: "Deploy the send-email edge function"

Request: Sending...
Response time: 3.2s
Response:
  "I'll deploy the send-email edge function now. Checking the latest
   code from GitHub... The function looks good. Deploying..."

Analysis:
  Success keywords: "deploy" ✅, "deploying" ✅
  Error keywords: none
  Status: ✅ SUCCESS
```

---

*This reference is used by the yolo skill when Lovable MCP is connected. See `connect-mcp.md` command for setup instructions.*
