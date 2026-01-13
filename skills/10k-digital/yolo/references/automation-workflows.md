# Yolo Mode: Browser Automation Workflows

Complete reference for browser automation when yolo mode is enabled.

## Overview

This document provides step-by-step instructions for automating Lovable prompt submission using Claude's browser automation capabilities.

## Performance Principles

To maximize speed and reliability, this automation follows these principles:

### Use `ref` Parameters Instead of Coordinates
- Always use `read_page` and `find` tools to get element references
- Click elements using `ref="ref_X"` instead of coordinate-based `(x, y)` clicks
- This eliminates "clicking wrong places" issues entirely

### Use `form_input` Instead of Typing
- Set input values directly using `form_input(ref=X, value="...")`
- Avoids character-by-character typing which is slow (~50ms per char) and error-prone
- Results in 20x faster prompt entry with zero mistyping

### Minimize Screenshots
- Use `read_page` to understand page state (fast, deterministic)
- Only take screenshots on errors or for final user confirmation
- Screenshots are slow (~1-2s each) and add unnecessary latency

### Model Selection (Hybrid Approach)
For optimal speed + reliability:
- **Use Haiku** for: clicking refs, form inputs, key presses, waiting
- **Use Sonnet** for: initial page understanding, error handling, parsing responses

## Prerequisites

- Claude in Chrome extension installed
- User logged into Lovable.dev
- `lovable_url` configured in CLAUDE.md
- `yolo_mode: on` in CLAUDE.md

## Trigger Modes

### 1. Auto-Deploy Mode (Recommended)
When `auto_deploy: on`:
- Triggered automatically after `git push origin main`
- Claude detects backend file changes and starts deployment
- No manual command needed

### 2. Command-Triggered Mode
When `auto_deploy: off` or using manual commands:
- Triggered by `/deploy-edge` or `/apply-migration` commands
- User explicitly initiates deployment

## Core Automation Workflow

### Step 1: Navigate to Lovable Project

**Goal:** Open the Lovable project page in the browser.

> **IMPORTANT:** After navigation, you MUST wait for GitHub sync before submitting any deployment prompts. See Step 1.5.

1. **Read configuration:**
   ```
   - Read CLAUDE.md
   - Extract `lovable_url` field
   - Example: "https://lovable.dev/projects/abc123"
   ```

2. **Open browser:**
   ```
   - Use Claude's browser automation to navigate
   - Target URL: [lovable_url from CLAUDE.md]
   - Wait for: Page load complete
   ```

3. **Check for login:**
   ```
   - If URL redirects to /login or /signin:
     → User not logged in
     → Show message: "Please log in to Lovable"
     → Wait for user to log in
     → Retry navigation

   - If URL stays on project page:
     → User is logged in
     → Proceed to next step
   ```

4. **Verify project page loaded:**
   ```
   - Wait for: Chat interface to appear
   - Timeout: 10 seconds
   - If timeout:
     → Error: "Could not load Lovable project page"
     → Fall back to manual prompt
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Step 1 - Navigate to Lovable

URL: https://lovable.dev/projects/abc123
Status: Navigating...
Wait: Page load event
Result: ✅ Loaded (1.2s)
Current URL: https://lovable.dev/projects/abc123
Login status: Authenticated
```

---

### Step 1.5: Wait for GitHub Sync (CRITICAL)

**Goal:** Verify Lovable has synced the latest code from GitHub before deployment.

> **Why this matters:** Lovable syncs from GitHub asynchronously (typically 1-2 minutes). If we submit a deployment prompt before sync completes, Lovable will deploy stale code.

> **OPTIMIZED APPROACH:** Use DOM-based detection instead of visual scanning for speed and reliability.

1. **Navigate to project immediately (no initial wait):**
   ```
   - Go directly to Lovable project page after git push
   - Don't wait 30 seconds first - sync detection starts immediately
   ```

2. **DOM-Based Sync Detection (FAST & RELIABLE):**
   ```
   Use read_page or JavaScript to find sync confirmation:

   METHOD 1: Use read_page to search accessibility tree
   - Call read_page(tabId=X)
   - Search for text containing commit message (first ~30 chars)
   - Look for elements with "github" or commit text in their content

   METHOD 2: Use JavaScript for direct DOM query
   - Use javascript_tool to run:
     ```javascript
     // Get all text content from sidebar
     const sidebar = document.querySelector('[data-sidebar]') ||
                     document.querySelector('.sidebar') ||
                     document.querySelector('nav');
     const text = sidebar?.textContent || '';
     // Check if commit message appears
     text.includes('YOUR_COMMIT_MESSAGE_PREFIX')
     ```

   METHOD 3: Use find tool
   - Call find(query="conversation item with YOUR_COMMIT_MESSAGE", tabId=X)
   - If element found with matching text, sync is confirmed

   WHY THIS IS BETTER:
   - No screenshots needed (saves ~1-2s per check)
   - Deterministic - text matching vs visual icon recognition
   - Faster polling interval possible (2s vs 4s)
   - More reliable - doesn't depend on icon rendering
   ```

3. **Verification loop (optimized):**
   ```
   attempts = 0
   max_attempts = 30  # 2s each = 60 seconds max (faster checks)
   commit_prefix = first 30 chars of commit message

   # Check immediately first using read_page
   page_content = read_page(tabId=X)
   if commit_prefix in page_content:
     → Sync confirmed, proceed to Step 2

   # If not found, wait and retry
   while not synced and attempts < max_attempts:
     wait 2 seconds  # Faster than 4s since no screenshot overhead
     page_content = read_page(tabId=X)
     if commit_prefix in page_content:
       → Sync confirmed, proceed to Step 2
       break
     attempts++

   if not synced after max_attempts:
     → Show sync timeout warning
     → Offer options to user
   ```

4. **If sync verified:**
   ```
   ✅ Step 2/8: Sync verified - Lovable has latest code
      Commit: abc1234 "Add email notifications"
   ```

5. **If sync times out:**
   ```
   ⚠️ Sync verification timeout

   Lovable hasn't synced the latest changes after 60 seconds.

   **Options:**
   1. Wait and retry (I'll check again in 30s)
   2. Proceed anyway (may deploy stale code)
   3. Cancel and verify manually

   What would you like to do?
   ```

6. **Handle sync timeout user choice:**
   ```
   If user chooses "retry":
     → Wait 30s, check again
     → Up to 2 more attempts

   If user chooses "proceed":
     → Continue with warning
     → Note in summary: "⚠️ Deployed without sync verification"

   If user chooses "cancel":
     → Show manual fallback prompt
     → Exit automation
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Step 1.5 - GitHub Sync Verification (DOM-based)

Commit just pushed:
  Hash: abc1234
  Message: "Add email notifications"
  Search prefix: "Add email notifications"

Sync check #1 (0s - immediate):
  Method: read_page DOM query
  Looking for: "Add email notifications"
  Result: Not found yet

Sync check #2 (2s):
  Method: read_page DOM query
  Looking for: "Add email notifications"
  Result: Not found yet

Sync check #3 (4s):
  Method: read_page DOM query
  Found: ✅ Text "Add email notifications feat..." in sidebar
  Status: ✅ Synced

Result: ✅ Sync verified (4s) - DOM-based detection is faster and more reliable!
```

---

### Step 2: Locate Chat Interface

**Goal:** Find and prepare the CORRECT chat input element using ref-based approach.

> **CRITICAL:** Use the LOWER LEFT corner chat input, NOT the top input for preview!

> **OPTIMIZED APPROACH:** Use `find` tool to get element ref directly - no coordinates needed!

1. **Use `find` tool for reliable element location:**
   ```
   PREFERRED METHOD: Use find tool with natural language query
   - Call: find(query="Ask Lovable chat input textarea", tabId=X)
   - Returns: Element ref (e.g., ref_42) that can be used for all interactions
   - No coordinate calculations needed
   - Guaranteed to interact with correct element

   ALTERNATIVE: Use read_page + search
   - Call: read_page(tabId=X, filter="interactive")
   - Search for element with "Ask Lovable" in name/placeholder
   - Extract ref from matching element

   WHY THIS IS BETTER:
   - Refs are stable - clicking ref_42 always clicks that exact element
   - No viewport/resolution dependencies
   - No "clicking wrong places" issues
   - Works even if UI positions change
   ```

2. **Store the element ref for later use:**
   ```
   chatInputRef = result from find tool (e.g., "ref_42")

   This ref will be used in Step 3 for:
   - form_input(ref=chatInputRef, value="...")
   - No need to click to focus first
   ```

3. **Verify element is correct (quick check):**
   ```
   The find tool result includes element details:
   - role: "textbox" or "textarea"
   - name: should contain "Ask Lovable" or similar
   - If name doesn't match, search read_page results manually
   ```

4. **If element not found:**
   ```
   Error: "Could not locate chat interface"

   Possible reasons:
   - Lovable UI has changed
   - Page still loading
   - Wrong tab/window focused

   Recovery:
   1. Wait 2 seconds, retry find()
   2. If still not found, try read_page(filter="interactive") and search manually
   3. If still not found, fall back to manual prompt

   Fallback: Provide manual prompt to user
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Step 2 - Locate Chat Interface (ref-based)

Method: find tool
Query: "Ask Lovable chat input textarea"
Result: ✅ Found

Element details:
  ref: ref_42
  role: textbox
  name: "Ask Lovable..."
  state: enabled, visible

Verification:
  ✅ Name contains "Ask Lovable"
  ✅ Element is enabled
  ✅ Ref stored for Step 3

Result: ✅ Chat input ref acquired (0.2s)
```

---

### Step 3: Submit the Prompt

**Goal:** Enter the Lovable prompt and submit it.

> **OPTIMIZED APPROACH:** Use `form_input` tool - 20x faster than typing, zero mistyping!

1. **Use `form_input` to set prompt value (FAST):**
   ```
   PREFERRED METHOD: Direct value setting
   - Call: form_input(ref=chatInputRef, value="Deploy the send-email edge function", tabId=X)
   - Sets the value instantly (~100ms total)
   - No clicking to focus needed
   - No character-by-character typing
   - Zero chance of mistyping

   WHY THIS IS BETTER:
   - Old approach: Click + type 40 chars × 50ms = ~2-3 seconds + possible typos
   - New approach: form_input = ~100ms, guaranteed accuracy
   - 20x faster with 100% reliability
   ```

2. **Submit the prompt:**
   ```
   PREFERRED: Press Enter using ref
   - Call: computer(action="key", text="Enter", tabId=X)
   - Wait: 200ms for form submission

   ALTERNATIVE: Click send button if Enter doesn't work
   - Call: find(query="send button", tabId=X)
   - Call: computer(action="left_click", ref=sendButtonRef, tabId=X)
   ```

3. **Confirm message sent (quick DOM check):**
   ```
   - Wait 1-2 seconds
   - Call: read_page(tabId=X) to check chat state
   - Look for user message containing our prompt text
   - Timeout: 5 seconds

   NOTE: No screenshot needed - DOM is faster and more reliable
   ```

4. **If submission fails:**
   ```
   Recovery steps:
   1. Try clicking send button instead of Enter
   2. If still fails, take screenshot for debugging
   3. Fall back to manual prompt

   Fallback: Provide manual prompt to user
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Step 3 - Submit Prompt (form_input)

Method: form_input (instant)
Ref: ref_42
Value: "Deploy the send-email edge function"
Result: ✅ Value set (0.1s)

Submission method: Enter key
Result: ✅ Submitted (0.1s)

Confirmation: read_page DOM check
Looking for: User message with "Deploy the send-email"
Result: ✅ Message confirmed in DOM (0.3s)

Total time: 0.5s (vs ~2.5s with typing)
```

---

### Step 4: Monitor Lovable's Response

**Goal:** Wait for Lovable to process the prompt and respond.

> **OPTIMIZED APPROACH:** Use `read_page` polling instead of screenshots for speed.

1. **Poll for assistant message using DOM:**
   ```
   PREFERRED METHOD: read_page polling
   - Wait 2-3 seconds initial delay (let Lovable start processing)
   - Call: read_page(tabId=X)
   - Search for new assistant message in chat
   - Look for text that wasn't there before submission

   POLLING LOOP:
   while no response and elapsed < 180 seconds:
     wait 2 seconds
     content = read_page(tabId=X)
     check for new assistant message
     if found and not loading indicator present:
       → Response received, proceed to Step 5

   WHY THIS IS BETTER:
   - No screenshots needed (saves ~1-2s per check)
   - Faster polling (2s vs 5s with screenshots)
   - More reliable text extraction
   ```

2. **Detect loading state:**
   ```
   During polling, check for loading indicators in DOM:
   - Text containing "Thinking", "Generating", "Loading"
   - Elements with loading/spinner roles

   If loading indicator present:
     → Response in progress, keep waiting
   If loading gone + new text present:
     → Response complete, capture text
   ```

3. **Capture response text:**
   ```
   Once response detected:
   - Extract assistant message text from DOM
   - Store full text for Step 5 analysis
   - No screenshot needed unless debugging
   ```

4. **If timeout (180 seconds):**
   ```
   ⏱️ Lovable hasn't responded after 3 minutes

   The operation may still be processing.
   Please check Lovable manually to verify status.

   Prompt that was submitted:
   📋 "Deploy the send-email edge function"

   At this point: Take ONE screenshot for user reference
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Step 4 - Monitor Response (DOM polling)

Method: read_page polling (2s interval)
Elapsed: 0s → 2s → 4s → 6s

Poll #1 (2s):
  New content: None yet
  Loading indicator: "Thinking..."
  Status: ⏳ Still processing

Poll #2 (4s):
  New content: Detected new text
  Loading indicator: None
  Status: ✅ Response complete

Response extracted:
  Length: 245 characters
  Content: "I'll deploy the send-email edge function now..."

Result: ✅ Response received (4s) - No screenshots used!
```

---

### Step 5: Detect Success or Failure

**Goal:** Determine if the deployment was successful based on Lovable's response.

**Success Indicators:**

Look for these keywords in the response (case-insensitive):

For edge functions:
- "deploy" or "deployed"
- "function is live"
- "successfully deployed"
- "deployment complete"
- "available at"

For migrations:
- "migration applied"
- "database updated"
- "successfully ran"
- "schema updated"
- "migration complete"

**Error Indicators:**

Look for these keywords in the response:

- "error"
- "failed"
- "could not"
- "unable to"
- "invalid"
- "syntax error"
- "constraint"
- "permission denied"

**Detection Logic:**

```
1. Convert response to lowercase
2. Count success keywords found
3. Count error keywords found

4. If error keywords > 0:
   → Deployment failed
   → Extract error message
   → Show error to user

5. Else if success keywords > 0:
   → Deployment succeeded
   → Proceed to testing (if enabled)

6. Else:
   → Unclear response
   → Show response to user
   → Ask user to verify manually
```

**Examples:**

Success response:
```
"I'll deploy the send-email edge function now..."
→ Found: "deploy", "function"
→ No errors found
→ Status: ✅ Success
```

Error response:
```
"I encountered an error deploying the function. The syntax is invalid..."
→ Found: "error", "invalid"
→ Status: ❌ Failed
→ Error: "syntax is invalid"
```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Step 5 - Detect Success/Failure

Response analysis:
  Length: 245 characters
  Lowercase: "i'll deploy the send-email..."

Keyword search:
  Success keywords:
    - "deploy" → ✅ Found (position 6)
    - "deployed" → Not found
    - "function is live" → Not found
    - "successfully" → Not found

  Error keywords:
    - "error" → Not found
    - "failed" → Not found
    - "could not" → Not found

Result:
  Success keywords: 1
  Error keywords: 0
  Status: ✅ SUCCESS
```

---

## Testing Workflows

When `yolo_testing: on`, run these verification tests after successful deployment.

### Level 1: Basic Deployment Verification

**Goal:** Confirm deployment completed via Lovable's own confirmation.

**For Edge Functions:**

1. **Ask Lovable for deployment logs:**
   ```
   Submit follow-up prompt:
   "Show logs for [function-name] edge function"

   Wait for response (60 second timeout)
   ```

2. **Check logs response:**
   ```
   Success indicators in logs:
   - No deployment errors
   - Function shows as "active" or "running"
   - Recent timestamp matches deployment time

   Error indicators:
   - "no logs found"
   - Error messages in logs
   - Function shows as "inactive"
   ```

3. **Report result:**
   ```
   ✅ Basic verification: Deployment logs show no errors
   OR
   ⚠️ Basic verification: Logs show warnings
   OR
   ❌ Basic verification: Deployment errors in logs
   ```

**For Migrations:**

1. **Ask Lovable for schema confirmation:**
   ```
   Submit follow-up prompt:
   "Show me the [table-name] table structure"

   Wait for response (60 second timeout)
   ```

2. **Check schema response:**
   ```
   Success indicators:
   - Table exists
   - Columns match migration
   - No schema errors

   Error indicators:
   - "table does not exist"
   - Missing columns
   - Type mismatches
   ```

3. **Report result:**
   ```
   ✅ Basic verification: Migration applied (schema confirmed)
   OR
   ❌ Basic verification: Schema doesn't match migration
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Level 1 - Basic Verification

Follow-up prompt: "Show logs for send-email edge function"
Response time: 2.1s
Response excerpt:
  "Here are the recent logs for send-email:
   [2024-01-15 10:30:00] Function deployed
   [2024-01-15 10:30:01] Function active
   No errors found."

Analysis:
  Deployment timestamp: Recent (< 1 min ago)
  Status: Active
  Errors: None found

Result: ✅ PASS (2.1s)
```

---

### Level 2: Console Error Checking

**Goal:** Monitor the production URL for JavaScript and network errors.

1. **Navigate to production URL:**
   ```
   - Read `production_url` from CLAUDE.md
   - Example: "https://my-app.lovable.app"
   - Navigate to URL in new tab
   - Wait for: Page load complete
   ```

2. **Open browser console:**
   ```
   - Access browser developer tools
   - Navigate to Console tab
   - Clear existing console messages
   ```

3. **Monitor for errors:**
   ```
   Watch for (10-15 seconds):

   JavaScript errors:
   - Uncaught exceptions
   - Reference errors
   - Type errors

   Network errors:
   - Failed API calls (500, 404 status)
   - Edge function call failures
   - CORS errors
   ```

4. **Capture and categorize errors:**
   ```
   For each error found:
   - Source: Which file/line
   - Type: JS error, network error, etc.
   - Message: Full error text
   - Severity: Error vs Warning

   Filter out:
   - Third-party script errors (analytics, etc.)
   - Known warnings that are safe
   ```

5. **Report findings:**
   ```
   If no errors:
   ✅ Console check: No errors detected

   If warnings only:
   ⚠️ Console check: 2 warnings found (non-critical)

   If errors:
   ❌ Console check: 3 errors found
   - Network error: Edge function call to /send-email returned 500
   - JS error: Cannot read property 'data' of undefined (app.js:45)
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Level 2 - Console Error Checking

Navigation:
  URL: https://my-app.lovable.app
  Load time: 1.8s
  Status: 200 OK

Console monitoring (15s):
  Errors: 0
  Warnings: 1
  Info: 5

Warning details:
  [1] DevTools: Third-party cookie warning
    Source: Chrome
    Severity: Low
    Filter: ✅ Ignored (third-party)

Network requests (during monitoring):
  Total: 12
  Success: 12
  Failed: 0

Result: ✅ PASS - No errors (0.1s monitoring)
```

---

### Level 3: Functional Testing

**Goal:** Test that the deployed feature actually works.

**For Edge Functions:**

1. **Determine function endpoint:**
   ```
   Pattern: https://{supabase-ref}.supabase.co/functions/v1/{function-name}

   Get supabase-ref from:
   - CLAUDE.md (if documented)
   - Lovable response (if mentioned)
   - Ask user if not available
   ```

2. **Determine test payload:**
   ```
   Option A: Known test payload
   - If function has documented test data
   - Example: send-email might test with dummy email

   Option B: Ask user
   - "What test data should I send to test [function-name]?"
   - Wait for user input

   Option C: No-payload test
   - For functions that don't require input
   - Just check if endpoint responds
   ```

3. **Make test request:**
   ```
   - HTTP POST to function endpoint
   - Include: Auth headers (if needed), test payload
   - Timeout: 30 seconds
   - Capture: Status code, response body
   ```

4. **Verify response:**
   ```
   Success indicators:
   - Status code: 200-299
   - Response body: Expected structure
   - No error messages in body

   Failure indicators:
   - Status code: 400-599
   - Timeout
   - Error in response body
   ```

5. **Report result:**
   ```
   ✅ Functional test: Function responds correctly (200 OK)
   Response: {"success": true, "message": "Email sent"}

   OR

   ⚠️ Functional test: Function responds with error (500)
   Response: {"error": "SMTP connection failed"}

   OR

   ⏭️ Functional test: Skipped (no test payload available)
   To test manually: [show endpoint and example payload]
   ```

**For Migrations:**

1. **Determine test query:**
   ```
   Based on migration type:

   CREATE TABLE: "SELECT * FROM [table] LIMIT 1"
   ADD COLUMN: "SELECT [column] FROM [table] LIMIT 1"
   CREATE INDEX: "EXPLAIN SELECT * FROM [table] WHERE [indexed-column]"
   ```

2. **Execute test query via Lovable:**
   ```
   Submit prompt to Lovable:
   "Run this query: [test-query]"

   Wait for response (60 second timeout)
   ```

3. **Verify query result:**
   ```
   Success indicators:
   - Query executes without error
   - Returns expected structure
   - No permission errors

   Failure indicators:
   - "relation does not exist"
   - "column does not exist"
   - Permission denied
   ```

4. **Report result:**
   ```
   ✅ Functional test: Test query succeeded
   Query: SELECT * FROM users LIMIT 1
   Result: Table structure confirmed

   OR

   ❌ Functional test: Query failed
   Error: column "new_field" does not exist
   ```

**Debug output (if `yolo_debug: on`):**
```
🐛 DEBUG: Level 3 - Functional Testing

Function: send-email
Endpoint: https://abc123.supabase.co/functions/v1/send-email

Test payload:
  Method: POST
  Headers:
    Authorization: Bearer [token]
    Content-Type: application/json
  Body:
    {
      "to": "test@example.com",
      "subject": "Test",
      "body": "Test message"
    }

Request: Sending...
Response time: 1.2s
Status: 200 OK
Headers:
  Content-Type: application/json
Body:
  {
    "success": true,
    "messageId": "abc-123-def"
  }

Analysis:
  Status code: ✅ 200 (success range)
  Response structure: ✅ Valid JSON
  Error indicators: ❌ None found

Result: ✅ PASS (1.2s)
```

---

## Error Handling Reference

### Error Categories

**1. Browser/Navigation Errors**

```
Could not access browser:
→ Check Chrome extension installed
→ Check browser is running
→ Fallback: Manual prompt

Could not navigate to URL:
→ Check lovable_url is valid
→ Check internet connection
→ Fallback: Manual prompt

Login required:
→ Instruct user to log in
→ Retry automatically
→ Timeout after 2 minutes → manual prompt
```

**2. UI Element Errors**

```
Chat interface not found:
→ Try alternative selectors
→ Wait longer (Lovable may be loading)
→ If still not found → Manual prompt
→ Suggest reporting issue

Element not interactable:
→ Scroll into view
→ Wait for animations to complete
→ Remove overlays if present
→ If still blocked → Manual prompt
```

**3. Submission Errors**

```
Could not submit prompt:
→ Try Enter key
→ Try click send button
→ Try paste and submit
→ If all fail → Manual prompt

Message not confirmed:
→ Wait longer (up to 5s)
→ Check if message appeared later
→ If still not confirmed → Warn user, continue
```

**4. Response Errors**

```
Timeout (no response):
→ Warn: "3 minutes without response"
→ Suggest manual check
→ Show what prompt was submitted

Lovable returned error:
→ Parse error message
→ Show to user
→ Suggest fixes based on error type
→ Offer to help debug
```

**5. Testing Errors**

```
Test failed:
→ Show which test failed
→ Show specific error
→ Mark deployment as "⚠️ Deployed but test failed"
→ Suggest manual verification

Could not run test:
→ Skip that test level
→ Continue with remaining tests
→ Note in summary: "Some tests skipped"
```

### Fallback Strategy

For ANY automation failure:

1. **Capture the error**
2. **Show user-friendly message**
3. **Provide manual prompt as fallback:**
   ```
   ❌ [Error description]

   Fallback: Here's the prompt to run manually in Lovable:
   📋 "Deploy the send-email edge function"

   [Context-specific troubleshooting]
   ```
4. **Never block the user** - always provide a way forward

---

## User Notification Templates

### Progress Notifications

**Standard mode (debug off):**
```
🤖 Yolo mode: Deploying send-email edge function

⏳ Step 1/8: Navigating to Lovable project...
⏳ Step 2/8: Waiting for GitHub sync...
✅ Step 3/8: Sync verified - Lovable has latest code
✅ Step 4/8: Located chat interface
✅ Step 5/8: Submitted prompt
⏳ Step 6/8: Waiting for Lovable response...
✅ Step 7/8: Deployment confirmed
⏳ Step 8/8: Running verification tests...
  ⏳ Basic verification...
  ⏳ Console error checking...
  ⏳ Functional testing...
✅ Step 8/8: All tests passed

✅ Complete! Edge function deployed and verified.
```

### Summary Notifications

**Success with all tests passed:**
```
## Deployment Summary

**Operation:** Edge Function Deployment
**Function:** send-email
**Status:** ✅ Success
**Duration:** 45 seconds

**Automation Steps:**
1. ✅ Navigated to Lovable project
2. ✅ GitHub sync verified
3. ✅ Submitted deployment prompt
4. ✅ Deployment confirmed by Lovable

**Verification Tests:**
1. ✅ Basic verification: Deployment logs show no errors
2. ✅ Console check: No errors in browser console
3. ✅ Functional test: Function endpoint responds (200 OK)
   Response: {"success": true, "messageId": "abc-123"}

**Production Status:**
- Function is live at endpoint
- No errors detected
- Ready for use

💡 Yolo mode is still enabled. Run `/yolo off` to disable.
```

**Success with test warnings:**
```
## Deployment Summary

**Operation:** Edge Function Deployment
**Function:** send-email
**Status:** ⚠️ Deployed (with warnings)
**Duration:** 52 seconds

**Automation Steps:**
1. ✅ Navigated to Lovable project
2. ✅ GitHub sync verified
3. ✅ Submitted deployment prompt
4. ✅ Deployment confirmed by Lovable

**Verification Tests:**
1. ✅ Basic verification: Deployment logs show no errors
2. ⚠️ Console check: 1 warning found (non-critical)
   - Warning: "Rate limit approaching for Resend API"
3. ✅ Functional test: Function responds (200 OK)

**Recommendation:**
- Function deployed successfully
- Monitor the rate limit warning
- Consider upgrading Resend plan if needed

💡 Yolo mode is still enabled. Run `/yolo off` to disable.
```

**Deployment succeeded but testing failed:**
```
## Deployment Summary

**Operation:** Edge Function Deployment
**Function:** send-email
**Status:** ⚠️ Deployed (test failures)
**Duration:** 48 seconds

**Automation Steps:**
1. ✅ Navigated to Lovable project
2. ✅ GitHub sync verified
3. ✅ Submitted deployment prompt
4. ✅ Deployment confirmed by Lovable

**Verification Tests:**
1. ✅ Basic verification: Passed
2. ✅ Console check: Passed
3. ❌ Functional test: Failed
   Status: 500 Internal Server Error
   Error: "RESEND_API_KEY not found"

**Issue Found:**
The function deployed but isn't working because the RESEND_API_KEY
secret is missing.

**Next Steps:**
1. Go to Cloud → Secrets in Lovable
2. Add: RESEND_API_KEY = [your key]
3. Test the function again

Would you like me to help you find your Resend API key?
```

---

## Configuration Options

### Testing Control

**Enable all tests (default):**
```
yolo_testing: on
```
Runs all 3 testing levels after each deployment.

**Disable all tests:**
```
yolo_testing: off
```
Only deploys, no verification. Faster but less safe.

### Debug Control

**Enable debug output:**
```
yolo_debug: on
```
Shows verbose logs with timing, selectors, full responses.

**Disable debug output (default):**
```
yolo_debug: off
```
Shows minimal progress indicators only.

---

## Screenshot Policy

To maximize performance, follow these guidelines for screenshot usage:

### DO Take Screenshot:
- **On errors** - Capture state for debugging when something fails
- **Final confirmation** - One screenshot after deployment completes (optional)
- **User request** - If user explicitly asks to see what happened
- **Debugging mode** - When `yolo_debug: on` and investigating issues

### DO NOT Take Screenshot:
- **For element location** - Use `read_page` and `find` tools instead
- **For sync verification** - Use DOM-based text search
- **Between each step** - Too slow, use DOM polling
- **For response monitoring** - Use `read_page` to check chat state
- **For success detection** - Parse text from DOM, not screenshot

### Why This Matters:
- Each screenshot adds ~1-2 seconds latency
- Old approach: 5-8 screenshots = 5-16 seconds of overhead
- New approach: 1-2 screenshots = 1-4 seconds of overhead
- **75% reduction in screenshot-related latency**

---

## Performance Notes

**Optimized timing (with ref-based approach):**
- Navigation: 1-2s
- Element location: 0.1-0.2s (using find/read_page)
- Prompt submission: 0.1-0.3s (using form_input)
- Sync verification: 2-10s (DOM polling every 2s)
- Lovable response: 3-10s
- Basic verification: 2-5s
- Console checking: 10-15s
- Functional testing: 1-5s

**Total automation time (optimized):**
- Without testing: ~5-12s (was 15-45s)
- With testing: ~15-30s (was 20-40s)

**Improvement summary:**
| Step | Old Time | New Time | Improvement |
|------|----------|----------|-------------|
| Element location | 0.5-2s | 0.1-0.2s | 5-10x faster |
| Prompt entry | 2-3s | 0.1-0.3s | 10-20x faster |
| Sync verification | 30-80s | 2-20s | 3-4x faster |
| Screenshots | 5-16s overhead | 1-4s overhead | 75% reduction |

**Timeout limits:**
- Page load: 10s
- Element finding: 5s (usually <1s with find tool)
- Sync verification: 60s (faster polling than before)
- Lovable response: 180s (3 min)
- Test requests: 30-60s

---

## Graceful Fallback Strategy

**CRITICAL:** Browser automation MUST always fall back gracefully to manual instructions. Never leave the user stuck.

### Fallback Principles

1. **Always provide manual prompt** - Every failure message includes the Lovable prompt to copy-paste
2. **Clear error explanation** - Tell user why automation failed
3. **Actionable next steps** - Provide troubleshooting or workaround
4. **Never block progress** - User can always complete task manually

### Auto-Deploy Fallback Flow

```
git push origin main
    ↓
Detect backend changes
    ↓
Attempt automation
    ↓
┌─ Success → Show deployment summary
│
└─ Failure → Graceful fallback:
      1. Show clear error message
      2. Explain what went wrong
      3. Provide manual Lovable prompt
      4. Suggest troubleshooting steps
      5. Offer to disable auto-deploy if needed
```

### Fallback Message Templates

**For auto-deploy failures:**
```
❌ Auto-deploy failed: [specific error]

Backend changes were pushed successfully to GitHub.
Lovable will sync the code, but deployment requires a prompt.

**Complete manually in Lovable:**

📋 **LOVABLE PROMPT:**
> "Deploy the [function-name] edge function"

**Troubleshooting:**
[Context-specific suggestions]

💡 To disable auto-deploy: /lovable:yolo --no-auto-deploy
```

**For command-triggered failures:**
```
❌ Browser automation failed: [specific error]

**Fallback - run this prompt in Lovable:**

📋 **LOVABLE PROMPT:**
> "[the prompt that was going to be submitted]"

**What happened:**
[Brief explanation]

**Suggestions:**
[How to fix or work around]
```

### Error-Specific Fallbacks

| Error | Fallback Message |
|-------|------------------|
| Extension not installed | Prompt + link to install Chrome extension |
| Not logged in | Prompt + "Please log in to Lovable" |
| GitHub sync timeout | Prompt + "Lovable hasn't synced yet, verify manually or wait" |
| UI element not found | Prompt + "Lovable UI may have changed" + report link |
| Timeout | Prompt + "Check Lovable manually, may still be processing" |
| Deployment error | Prompt + error details + suggested fixes |
| Network error | Prompt + "Check internet connection" |

### Recovery Options

After any failure, offer these options:

1. **Manual completion** - Provide exact prompt to copy-paste
2. **Retry** - User can try automation again
3. **Change mode** - Suggest switching to manual mode if errors persist
4. **Report issue** - Link to GitHub issues for persistent problems

---

*This reference should be consulted for all browser automation operations in yolo mode.*
