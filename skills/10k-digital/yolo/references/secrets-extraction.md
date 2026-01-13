# Secrets Extraction via Browser Automation

Reference for extracting existing secrets from Lovable Cloud's settings page using browser automation. This enables the init command to see which secrets are already configured before collecting new ones.

## Overview

Navigate to Lovable Cloud settings and extract existing secret names. This helps:
- Show which secrets are already configured
- Avoid duplicate configuration attempts
- Merge Lovable Cloud secrets with codebase-detected secrets
- Provide users with complete secret status

## Prerequisites

- Lovable project URL available
- User logged into Lovable.dev in browser
- Claude in Chrome extension enabled
- Browser automation capabilities available

## Workflow Steps

### Step 1: Construct Cloud Settings URL

**Input:** Lovable project URL
```
https://lovable.dev/projects/PROJECT_ID
```

**Output:** Cloud settings URL
```
https://lovable.dev/projects/PROJECT_ID?view=cloud
```

**Example:**
- Input: `https://lovable.dev/projects/c0be81e7-dc30-4214-825a-9322c311c8df`
- Output: `https://lovable.dev/projects/c0be81e7-dc30-4214-825a-9322c311c8df?view=cloud`

### Step 2: Navigate to Cloud Page

**Sequence:**

1. Navigate to cloud URL
   ```
   URL: https://lovable.dev/projects/PROJECT_ID?view=cloud
   Action: Navigate
   Timeout: 10 seconds
   ```

2. Wait for page load
   ```
   Wait for: DOM content loaded
   Check for loading indicators: disappear
   ```

3. Check for login redirect
   ```
   If current URL contains: /login, /signin, /auth
   Then: Wait for user to login (30 second timeout)
   After login: Return to cloud URL automatically
   ```

4. If redirected by login
   ```
   Wait for: User to complete login in browser
   Timeout: 30 seconds
   Action: Return to cloud URL after login detected
   ```

**Debug output (if enabled):**
```
🐛 DEBUG: Navigation Step

Target URL: https://lovable.dev/projects/abc123?view=cloud
Navigation: Started
Status: 200 OK
Page load time: 1.2 seconds
Login detected: false
Current URL: https://lovable.dev/projects/abc123?view=cloud

Result: ✅ Loaded successfully
```

### Step 3: Locate Secrets Section

**Element selectors (try in order):**

1. **Data-testid attribute** (most reliable)
   ```
   [data-testid="secrets-section"]
   [data-testid="cloud-secrets"]
   [data-testid="secrets-list"]
   ```

2. **ARIA labels** (accessibility attributes)
   ```
   section[aria-label*="Secret"]
   div[aria-label*="Secret"]
   ```

3. **Class-based selectors** (fallback)
   ```
   div[class*="secrets"]
   div[class*="secret-list"]
   section[class*="settings"]
   ```

4. **Text content** (last resort)
   ```
   Look for heading text matching "Secrets"
   Look for section with text "Secret keys" or "Environment variables"
   ```

**Timeouts:**
- Max wait for section: 5 seconds
- If not found: Return empty array, continue

**Debug output:**
```
🐛 DEBUG: Locate Secrets Section

Selector 1: [data-testid="secrets-section"]
  Status: ✅ Found
  Element: div#secrets-section
  Location: x=200, y=400, width=600, height=400

Result: ✅ Located
```

### Step 4: Extract Secret Names

**Element patterns to extract (try in order):**

#### Pattern A: Data-testid Attributes
```
[data-testid="secret-key"]
[data-testid="secret-name"]
[data-testid="secret-item"]
```
**Action:** Get text content of element

#### Pattern B: Input Fields
```
input[name*="secret"][readonly]
input[name*="secret"][disabled]
input[name*="key"]
```
**Action:** Get `value` attribute

#### Pattern C: Code/Pre Elements
```
code
pre
span[class*="key"]
span[class*="secret"]
```
**Action:** Get text content

#### Pattern D: List Items
```
li[class*="secret"]
li[class*="key"]
tr[class*="secret"] td:first-child
```
**Action:** Get text content of first cell/child

#### Pattern E: Container Elements
```
div[class*="secret-item"] span
div[class*="secret-row"] [class*="name"]
```
**Action:** Get text content of name element

**Extraction logic:**
```typescript
function extractSecretNames(secretsSection: Element): string[] {
  const secrets = new Set<string>();

  // Try each pattern
  const patterns = [
    '[data-testid="secret-key"]',
    'input[name*="secret"][readonly]',
    'code',
    'li[class*="secret"] span:first-child',
    // ... more patterns
  ];

  for (const pattern of patterns) {
    const elements = secretsSection.querySelectorAll(pattern);
    for (const elem of elements) {
      const value = elem.textContent?.trim() || elem.value?.trim();

      if (value && isValidSecretName(value)) {
        // Extract only KEY portion (before value fields)
        const secretName = extractKeyName(value);
        secrets.add(secretName);
      }
    }
  }

  return Array.from(secrets);
}

function extractKeyName(rawValue: string): string {
  // Handle different formats:
  // "KEY=*****" → "KEY"
  // "KEY: [hidden]" → "KEY"
  // "• KEY" → "KEY"
  // "KEY (xxxxx)" → "KEY"

  const cleanValue = rawValue
    .split('=')[0]
    .split(':')[0]
    .replace(/^[•\-\*]+\s*/, '')
    .replace(/\s*\([^)]*\).*$/, '')
    .trim();

  return cleanValue.toUpperCase();
}

function isValidSecretName(value: string): boolean {
  // Valid secret names are alphanumeric + underscore
  // At least 3 characters, contains at least one letter
  return /^[A-Z_][A-Z0-9_]{2,}$/i.test(value);
}
```

**Common secret name formats in Lovable:**
- `KEY=*****` → Extract "KEY"
- `KEY: [hidden]` → Extract "KEY"
- `• KEY_NAME` → Extract "KEY_NAME"
- `KEY_NAME (last rotated: 2024-01-01)` → Extract "KEY_NAME"
- Plain text: `RESEND_API_KEY` → Extract "RESEND_API_KEY"

**Expected output:**
```json
[
  "RESEND_API_KEY",
  "SUPABASE_SERVICE_ROLE_KEY",
  "OPENAI_API_KEY",
  "STRIPE_SECRET_KEY"
]
```

**Debug output:**
```
🐛 DEBUG: Extract Secret Names

Secrets section found: true
Number of secret items detected: 4

Extraction method: data-testid attributes
Items found: 4

Extracted secrets:
  1. RESEND_API_KEY
  2. SUPABASE_SERVICE_ROLE_KEY
  3. OPENAI_API_KEY
  4. STRIPE_SECRET_KEY

Result: ✅ Success (extracted 4 secrets)
```

### Step 5: Return Results

**Return format:**
```json
{
  "success": true,
  "secrets": [
    "RESEND_API_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "OPENAI_API_KEY"
  ],
  "count": 3,
  "source": "lovable_cloud",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Return values:**

| Status | Secrets Array | Meaning |
|--------|---------------|---------|
| `success: true` | Array of names | Extraction succeeded, use secrets |
| `success: true` | Empty array `[]` | No secrets configured yet |
| `success: false` | Empty array `[]` | Extraction failed, fallback to manual |

## Error Handling

### Scenario 1: Page Not Found (404)

**Detection:**
```
URL returns 404 status
OR "Page not found" message visible
OR Redirect to homepage detected
```

**Handling:**
```
Log: "Lovable project URL not found"
Return: { success: true, secrets: [] }
Reason: Project may not exist or URL may be incorrect
Fallback: Continue with codebase-only detection
```

**User message:** "Could not access Lovable Cloud settings (project not found). Using codebase detection only."

### Scenario 2: Login Required

**Detection:**
```
Current URL contains: /login, /signin, /auth
OR Login form visible
OR "Sign in" button present
```

**Handling:**
```
Log: "User login required"
Message: "Please log in to Lovable"
Wait: 30 seconds for user to complete login
Check: After login redirect, return to cloud URL
Timeout: If login not completed in 30s
  → Cancel automation
  → Return { success: true, secrets: [] }
  → Continue with fallback
```

**User message:** "Please log in to Lovable in your browser, then we'll extract your secrets. (Waiting up to 30 seconds...)"

### Scenario 3: Secrets Section Not Found

**Detection:**
```
None of the selectors return elements
Timeout: Section not visible after 5 seconds
```

**Handling:**
```
Log: "Secrets section not found - Lovable UI may have changed"
Return: { success: true, secrets: [] }
Reason: Selectors may be outdated
Fallback: Continue with codebase-only detection
```

**User message:** "Could not locate secrets section in Lovable Cloud (UI may have changed). Using codebase detection only."

### Scenario 4: No Secrets Configured

**Detection:**
```
Secrets section is visible and loaded
No secret items found
OR Empty state message visible: "No secrets yet", "Add your first secret"
```

**Handling:**
```
Log: "Secrets section found but empty"
Return: { success: true, secrets: [] }
Reason: This is valid - new project has no secrets yet
Fallback: Continue - codebase detection will find what's needed
```

**User message:** "No secrets configured in Lovable Cloud yet. We'll help you add them."

### Scenario 5: Extraction Timeout (Total)

**Detection:**
```
Navigation + extraction takes > 30 seconds total
```

**Timeout breakdown:**
- Navigation: 10 seconds
- Wait for section: 5 seconds
- Wait for login: 30 seconds (optional, only if needed)
- Extraction: 5 seconds
- **Total max:** 30 seconds of actual time

**Handling:**
```
If any step exceeds timeout:
  Log: "Secrets extraction timed out"
  Return: { success: true, secrets: [] }
  Action: Don't retry - move forward
```

**User message:** "Secrets extraction took too long, skipping. Using codebase detection only."

### Scenario 6: Extraction Partial Failure

**Detection:**
```
Some secrets extracted, some failed
HTML structure partially changed
Only 2/5 expected secrets found
```

**Handling:**
```
Return successfully with partial results:
  { success: true, secrets: ["SECRET1", "SECRET2"] }
Reason: Partial extraction is useful
User will add any missing manually
```

**User message:** "Extracted some existing secrets from Lovable Cloud. Review and add any additional ones needed."

## Edge Cases

### Case 1: Secret Names with Special Characters

**Example:** `API-KEY-v2`, `API.KEY`, `API KEY`

**Handling:**
```
Normalize to uppercase + underscore: API_KEY_V2
Ask user to confirm: "Found 'API_KEY_V2', is this correct?"
Store as provided if user confirms
```

### Case 2: Very Long Secret Names

**Example:** `VERY_VERY_VERY_LONG_SECRET_NAME_WITH_MANY_PARTS`

**Handling:**
```
Extract fully (no length limit)
Display with truncation if needed: "VERY_VERY_...NAME_WITH_MANY_PARTS"
Store complete name
```

### Case 3: Duplicate Detection

**Example:** UI shows same secret twice (bug or UI duplication)

**Handling:**
```
Use Set to deduplicate
Return unique secrets only
Log: "Removed 1 duplicate: SECRET_NAME"
```

### Case 4: Hidden/Masked Values

**Example:** Input shows `RESEND_API_KEY: ••••••••••••••••`

**Handling:**
```
Extract "RESEND_API_KEY"
Ignore the masked value portion (•••••)
Store secret name only (values not extracted for security)
```

## Integration with Init Flow

### When to Trigger

Called during **Question 6 (Secret Detection Method)** when:

1. ✅ User chooses option "A) Auto-detect"
2. ✅ Lovable project URL was provided in Q5
3. ✅ Browser automation is available
4. ✅ First attempt only (don't retry if failed)

### Data Flow

```
User provides Lovable URL (Q5)
    ↓
User chooses auto-detect (Q6 option A)
    ↓
Secrets extraction workflow starts
    ├─ Navigate to Cloud URL
    ├─ Extract secret names
    └─ Return list
    ↓
Merge with codebase-detected secrets
    ↓
Present merged results to user
    ↓
Ask for additional secrets
```

### Error Recovery

```
If browser automation fails:
  ├─ Log error
  ├─ Return empty list
  └─ Fall back to codebase-only detection
     ↓
  User still sees codebase results
  User still asked for additional secrets
  Init completes successfully
```

## Performance Metrics

**Typical timings:**
- Navigation: 1-2 seconds
- Wait for section: 1-2 seconds
- Extraction: 0.5-1 seconds
- **Total: 3-5 seconds** (most cases)

**Worst case:**
- Navigation: 10 seconds
- Wait for section: 5 seconds
- **Total: 15 seconds** (rare)

**Timeout ceiling:** 30 seconds total, never blocks init

## Debug Mode Output

When `yolo_debug: on` in CLAUDE.md:

```
🐛 DEBUG: Secrets Extraction

Step 1: Navigation
  URL: https://lovable.dev/projects/abc123?view=cloud
  Status: 200 OK
  Load time: 1.2s
  Login required: false
  Result: ✅ Loaded

Step 2: Locate Secrets Section
  Selector 1: [data-testid="secrets-section"] → ✅ Found
  Element: div#secrets-container
  Visibility: visible
  Location: x=200, y=400
  Result: ✅ Located

Step 3: Extract Secret Names
  Pattern 1: [data-testid="secret-key"] → Found 4 items
  Items: ["RESEND_API_KEY", "STRIPE_SECRET_KEY", "OPENAI_API_KEY", "SUPABASE_SERVICE_ROLE_KEY"]
  Validation: All valid secret names
  Deduplication: 0 duplicates found
  Result: ✅ Extracted

Summary:
  Total time: 2.3 seconds
  Secrets found: 4
  Success rate: 100%

Extracted secrets:
  1. RESEND_API_KEY
  2. STRIPE_SECRET_KEY
  3. OPENAI_API_KEY
  4. SUPABASE_SERVICE_ROLE_KEY

Result: ✅ Success
```

## Fallback Manual Instructions

If browser automation is unavailable or fails, provide these instructions:

```
ℹ️ Could not automatically extract secrets from Lovable Cloud

To view your existing secrets:
1. Open your Lovable project: https://lovable.dev/projects/YOUR_PROJECT_ID
2. Click "Cloud" in the left sidebar
3. Select the "Secrets" tab
4. You'll see all configured secret names

These secrets are already configured:
- Check the list in Lovable
- Compare with the code-detected secrets below

Then we'll merge them together.
```

## Testing Checklist

- [ ] Test with login required (user needs to login)
- [ ] Test with no secrets configured (empty state)
- [ ] Test with many secrets (10+)
- [ ] Test with special characters in secret names
- [ ] Test timeout behavior (page takes >30s to load)
- [ ] Test with different Lovable Cloud UI versions
- [ ] Test fallback when automation unavailable
- [ ] Test debug output with yolo_debug: on
- [ ] Test with duplicate secret names
- [ ] Test with very long secret names

---

This workflow enables the init command to automatically gather secret configuration status from Lovable Cloud, improving the user experience and reducing manual steps.
