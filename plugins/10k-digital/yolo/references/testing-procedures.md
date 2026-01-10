# Yolo Mode: Testing Procedures

Detailed verification workflows for each testing level.

## Overview

When `yolo_testing: on`, run three levels of verification after successful deployment:
1. **Level 1**: Basic deployment verification (via Lovable)
2. **Level 2**: Console error checking (production URL)
3. **Level 3**: Functional testing (actual feature testing)

When `yolo_testing: off`, skip all testing.

---

## Level 1: Basic Deployment Verification

**Goal:** Confirm deployment succeeded using Lovable's own tools.

### For Edge Functions

**Procedure:**

1. **Submit follow-up prompt to Lovable:**
   ```
   "Show logs for [function-name] edge function"
   ```

2. **Wait for response** (60 second timeout)

3. **Analyze logs response:**
   ```
   Success indicators:
   - Logs show recent deployment timestamp
   - Function status: "active" or "deployed"
   - No error messages in recent logs
   - Deployment success message present

   Warning indicators:
   - Old deployment timestamp (> 5 min ago)
   - Warnings in logs (non-fatal)

   Error indicators:
   - "No logs found"
   - Errors in recent logs
   - Function status: "inactive" or "failed"
   - Deployment error messages
   ```

4. **Report result:**
   ```
   ✅ Basic verification: Deployment logs confirm success
   ⚠️ Basic verification: Logs show warnings (details)
   ❌ Basic verification: Errors found in logs (details)
   ```

**Example - Success:**
```
Prompt: "Show logs for send-email edge function"

Response excerpt:
"Here are the recent logs for send-email:
 [2024-01-15 10:30:15] Deployment started
 [2024-01-15 10:30:18] Function deployed successfully
 [2024-01-15 10:30:19] Function is now active
 No errors in the last 100 log entries."

Analysis:
✅ Recent deployment (< 1 minute ago)
✅ Status: "deployed successfully", "active"
✅ No errors mentioned

Result: ✅ PASS
```

### For Migrations

**Procedure:**

1. **Identify what was migrated:**
   ```
   - Parse migration file name
   - Extract table/operation from SQL
   - Example: "add_user_preferences.sql" → table: users, operation: add column
   ```

2. **Submit follow-up prompt to Lovable:**
   ```
   For table creation:
   "Show me the [table-name] table structure"

   For column addition:
   "Describe the [table-name] table"

   For index creation:
   "Show indexes on [table-name]"
   ```

3. **Wait for response** (60 second timeout)

4. **Analyze schema response:**
   ```
   Success indicators:
   - Table exists (if CREATE TABLE)
   - Column exists (if ADD COLUMN)
   - Schema matches migration
   - No error messages

   Error indicators:
   - "table does not exist"
   - "column not found"
   - Schema doesn't match migration
   ```

5. **Report result:**
   ```
   ✅ Basic verification: Migration applied (schema confirmed)
   ❌ Basic verification: Schema doesn't match migration
   ```

**Example - Success:**
```
Migration: 20240115_add_user_preferences.sql
Content: ALTER TABLE users ADD COLUMN preferences JSONB;

Prompt: "Describe the users table"

Response excerpt:
"The users table has these columns:
 - id (uuid, primary key)
 - email (text)
 - created_at (timestamp)
 - preferences (jsonb)  ← new column
 ..."

Analysis:
✅ Column "preferences" exists
✅ Type matches: jsonb
✅ In correct table: users

Result: ✅ PASS
```

---

## Level 2: Console Error Checking

**Goal:** Monitor production URL for JavaScript and network errors.

### Procedure

1. **Navigate to production URL:**
   ```
   - Read: production_url from CLAUDE.md
   - Example: "https://my-app.lovable.app"
   - Open: New browser tab
   - Wait: Page load complete
   ```

2. **Access browser console:**
   ```
   - Open developer tools
   - Navigate to Console tab
   - Clear existing messages
   ```

3. **Monitor for 10-15 seconds:**
   ```
   Capture:

   JavaScript Errors:
   - Uncaught exceptions
   - Reference errors (undefined variables)
   - Type errors (wrong types)
   - Syntax errors

   Network Errors:
   - Failed API requests (status 400-599)
   - Edge function call failures
   - CORS errors
   - Timeout errors
   ```

4. **Filter noise:**
   ```
   Ignore:
   - Third-party script errors (analytics, ads)
   - Browser extension errors
   - Deprecation warnings
   - Info messages

   Focus on:
   - Errors from application domain
   - Errors related to deployed feature
   - Network errors to Supabase
   ```

5. **Categorize errors:**
   ```
   For each error:
   - Type: JS error, network error, etc.
   - Source: File and line number
   - Message: Full error text
   - Severity: Critical, warning, info
   - Related to deployment: yes/no
   ```

6. **Report findings:**
   ```
   No errors:
   ✅ Console check: No errors detected

   Warnings only:
   ⚠️ Console check: 2 non-critical warnings
   - Warning: "Cookie SameSite attribute" (browser)
   - Warning: "Deprecated API usage" (third-party)

   Errors found:
   ❌ Console check: 2 errors detected
   - Network: Edge function /send-email returned 500
     Details: "Internal Server Error"
   - JS Error: Cannot read property 'data' of undefined
     Location: app.js:45
     Context: After clicking send button
   ```

**Example - With Errors:**
```
Console monitoring (15 seconds):

[0.2s] Info: "App initialized"
[1.5s] Warning: "Third-party cookie will be blocked" (chrome)
[3.2s] ❌ Error: "Failed to fetch https://abc.supabase.co/functions/v1/send-email"
       Status: 500 Internal Server Error
       Initiator: app.js:45
[3.2s] ❌ Error: Uncaught TypeError: Cannot read property 'data' of undefined
       at handleEmailResponse (app.js:47)

Analysis:
Total errors: 2
Related to send-email function: ✅ Yes
Severity: High (breaks functionality)

Result: ❌ FAIL
Errors directly related to deployed edge function
```

---

## Level 3: Functional Testing

**Goal:** Test that the deployed feature actually works.

### For Edge Functions

**Procedure:**

1. **Determine endpoint URL:**
   ```
   Pattern: https://{project-ref}.supabase.co/functions/v1/{function-name}

   Get project-ref from:
   - CLAUDE.md (if documented)
   - src/integrations/supabase/client.ts
   - Ask Lovable: "What's my Supabase project ref?"
   ```

2. **Prepare test payload:**
   ```
   Option A: Known test data
   - If function has documented test in CLAUDE.md
   - Use predefined test payload

   Option B: Minimal valid payload
   - For send-email: {"to": "test@example.com", "subject": "Test"}
   - For process-payment: Skip (don't test real payments)

   Option C: Ask user
   - "What test data should I use for [function]?"
   - Wait for user input
   ```

3. **Make HTTP request:**
   ```
   Method: POST (usually)
   URL: https://{ref}.supabase.co/functions/v1/{function}
   Headers:
     Authorization: Bearer {anon-key} (from client.ts)
     Content-Type: application/json
   Body: {test payload}
   Timeout: 30 seconds
   ```

4. **Evaluate response:**
   ```
   Success: HTTP 200-299
   - Check: Response body structure
   - Verify: Expected fields present
   - Confirm: No error messages

   Client error: HTTP 400-499
   - Indicates: Bad request or auth issue
   - Check: Error message for details

   Server error: HTTP 500-599
   - Indicates: Function failed
   - Check: Error details
   - May need: Secrets, dependencies

   Timeout:
   - Indicates: Function hung or very slow
   - Check: Function complexity
   ```

5. **Report result:**
   ```
   Success:
   ✅ Functional test: Function responds correctly (200 OK)
   Response: {"success": true, "messageId": "abc-123"}
   Time: 1.2s

   Error:
   ❌ Functional test: Function error (500)
   Response: {"error": "RESEND_API_KEY not set"}
   Suggestion: Add secret in Cloud → Secrets

   Skipped:
   ⏭️ Functional test: Skipped (no safe test available)
   To test manually: POST to [endpoint] with [example payload]
   ```

**Example - Success:**
```
Function: send-email
Endpoint: https://abc123.supabase.co/functions/v1/send-email

Test request:
  POST /functions/v1/send-email
  Body: {
    "to": "test@example.com",
    "subject": "Test from yolo mode",
    "body": "This is a test"
  }

Response:
  Status: 200 OK
  Time: 1.4s
  Body: {
    "success": true,
    "messageId": "550e8400-e29b-41d4-a716-446655440000"
  }

Analysis:
✅ Status code in success range
✅ Response has expected structure
✅ "success": true present
✅ Message ID returned
✅ No error fields

Result: ✅ PASS
```

**Example - Error (Missing Secret):**
```
Function: send-email
Endpoint: https://abc123.supabase.co/functions/v1/send-email

Response:
  Status: 500 Internal Server Error
  Time: 0.3s
  Body: {
    "error": "Deno.env.get('RESEND_API_KEY') returned undefined"
  }

Analysis:
❌ Server error (500)
❌ Error message: Secret not configured

Diagnosis:
The function code looks for RESEND_API_KEY but it's not set.

Result: ❌ FAIL

Fix:
1. Go to Cloud → Secrets in Lovable
2. Add: RESEND_API_KEY = [your key]
3. Redeploy the function
```

### For Migrations

**Procedure:**

1. **Determine test query:**
   ```
   Based on migration type:

   CREATE TABLE:
     SELECT COUNT(*) FROM [table-name];
     → Should succeed and return 0 or more

   ADD COLUMN:
     SELECT [new-column] FROM [table-name] LIMIT 1;
     → Should succeed (even if no rows)

   CREATE INDEX:
     EXPLAIN SELECT * FROM [table] WHERE [indexed-column] = 'value';
     → Should show index usage

   ADD CONSTRAINT:
     Try to violate constraint
     → Should fail with constraint error
   ```

2. **Execute test via Lovable:**
   ```
   Submit prompt:
   "Run this query: [test-query]"

   Wait for response (60 second timeout)
   ```

3. **Analyze result:**
   ```
   Success indicators:
   - Query executes without error
   - Returns expected result
   - For EXPLAIN: Shows index is used

   Error indicators:
   - "relation does not exist"
   - "column does not exist"
   - Permission denied
   - Syntax error (migration may be malformed)
   ```

4. **Report result:**
   ```
   ✅ Functional test: Query succeeded, migration verified
   ❌ Functional test: Query failed, migration may not be applied
   ⏭️ Functional test: Skipped (destructive or complex test)
   ```

**Example - Success:**
```
Migration: 20240115_add_user_preferences.sql
Operation: ADD COLUMN preferences JSONB

Test query: SELECT preferences FROM users LIMIT 1;

Lovable response:
"Query executed successfully:
 Result: 1 row returned
 preferences: null"

Analysis:
✅ Query succeeded
✅ Column exists and is accessible
✅ Type appears correct (returns null, not error)

Result: ✅ PASS
```

---

## Testing Summary Template

After all 3 levels complete, show summary:

**All tests passed:**
```
**Verification Tests:**
1. ✅ Basic verification: Deployment confirmed
2. ✅ Console check: No errors detected
3. ✅ Functional test: Feature works correctly
   [details]

**Overall:** ✅ All tests passed
```

**Some tests failed:**
```
**Verification Tests:**
1. ✅ Basic verification: Deployment confirmed
2. ⚠️ Console check: 1 warning found (non-critical)
   - Warning: [details]
3. ❌ Functional test: Error detected
   - Error: [details]
   - Fix: [suggestion]

**Overall:** ⚠️ Deployed but issues found
```

**Tests skipped (yolo_testing: off):**
```
**Verification Tests:**
- Skipped (yolo_testing is off)

**Overall:** Deployment completed (not verified)
💡 Enable testing with: /yolo on --testing
```

---

## Performance Benchmarks

**Typical test timings:**
- Level 1: 2-5 seconds
- Level 2: 10-15 seconds
- Level 3: 1-5 seconds

**Total testing time:** 15-25 seconds

**When to skip testing:**
- Time-sensitive deployments
- Repeat deployments (already verified)
- Trusted code changes

**When to run testing:**
- First deployment of new function
- After significant changes
- Before production deployment
- When debugging issues

---

*These testing procedures ensure deployed features work correctly and catch issues early.*
