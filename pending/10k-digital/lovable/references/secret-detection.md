# Secret Detection Patterns and Algorithms

Reference guide for automatically detecting secrets required by a Lovable project during the init flow and deployment processes.

## Overview

The secret detection system scans the codebase and infers secret requirements through multiple patterns:
1. Direct environment variable references in code
2. Configuration files (.env.example)
3. Context-based inference from imports and service usage

## Detection Pattern 1: Edge Function Environment Variables

**What to scan:** All TypeScript files in Supabase Edge Functions

**Files:** `supabase/functions/**/*.ts`

**Pattern:** `Deno.env.get("SECRET_NAME")` or `Deno.env.get('SECRET_NAME')`

**Regex:**
```
Deno\.env\.get\(['"]([A-Z_]+)['"]\)
```

**Extraction:**
- Capture group 1 = SECRET_NAME
- Example: `Deno.env.get("RESEND_API_KEY")` → Extract `RESEND_API_KEY`

**Edge Function Linking:**
- Get function name from directory path: `supabase/functions/FUNCTION_NAME/index.ts` → `FUNCTION_NAME`
- Store: `{ name: "SECRET_NAME", usedIn: ["function_name"], source: "code" }`

**Example from codebase:**

File: `supabase/functions/send-email/index.ts`
```typescript
const apiKey = Deno.env.get("RESEND_API_KEY");
const webhookSecret = Deno.env.get("WEBHOOK_SECRET");
```

**Detected secrets:**
- `RESEND_API_KEY` (used in: send-email)
- `WEBHOOK_SECRET` (used in: send-email)

## Detection Pattern 2: .env.example Files

**What to scan:** Environment variable example files

**Files:**
- `.env.example`
- `.env.template`
- `.env.local.example`
- `env.example`

**Pattern:** Lines starting with `KEY=value` (uppercase KEY before `=`)

**Regex:**
```
^([A-Z_]+)=
```

**Extraction:**
- Capture group 1 = KEY
- Example: `OPENAI_API_KEY=sk-...` → Extract `OPENAI_API_KEY`
- Ignore: Lines starting with `#` (comments)

**Store:** `{ name: "KEY", usedIn: [], source: "env_file", purpose: "inferred" }`

**Example .env.example:**
```
# API Keys
OPENAI_API_KEY=sk-example
STRIPE_SECRET_KEY=sk_test_example
RESEND_API_KEY=re_example

# Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=public_key
```

**Detected secrets:**
- `OPENAI_API_KEY`
- `STRIPE_SECRET_KEY`
- `RESEND_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

## Detection Pattern 3: Context-Based Inference

**What to scan:** Import statements and code mentions of third-party services

**Detection logic:** Search for service names in code, then suggest their typical secret patterns

### Service Patterns

#### OpenAI
- **Search keywords:** `openai`, `gpt-`, `chatgpt`, `chat-completion`, `embedding`
- **Suggested secrets:**
  - `OPENAI_API_KEY` (always)
  - `OPENAI_ORG_ID` (if organization usage detected)
- **Purpose inference:**
  - If code mentions "embedding" → "OpenAI embeddings"
  - If code mentions "chat" or "completion" → "OpenAI chat completions"
  - Default → "OpenAI API access"

#### Stripe
- **Search keywords:** `stripe`, `checkout`, `payment`, `subscription`, `invoice`
- **Suggested secrets:**
  - `STRIPE_SECRET_KEY` (always)
  - `STRIPE_WEBHOOK_SECRET` (if webhook endpoint detected)
  - `STRIPE_PUBLISHABLE_KEY` (if client-side code)
- **Purpose inference:**
  - If "webhook" mentioned → "Stripe webhook verification"
  - If "subscription" mentioned → "Stripe subscription management"
  - Default → "Stripe payments"

#### Resend (Email)
- **Search keywords:** `resend`, `send-email`, `email`, `transactional`
- **Suggested secrets:**
  - `RESEND_API_KEY`
- **Purpose:** "Email sending via Resend"

#### Twilio (SMS/Phone)
- **Search keywords:** `twilio`, `sms`, `phone`, `voice`, `messaging`
- **Suggested secrets:**
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER` (optional)
- **Purpose inference:**
  - If "SMS" mentioned → "Twilio SMS service"
  - If "voice" mentioned → "Twilio voice calls"
  - Default → "Twilio SMS/Voice"

#### SendGrid (Email Alternative)
- **Search keywords:** `sendgrid`, `sendgrid-api`
- **Suggested secrets:**
  - `SENDGRID_API_KEY`
- **Purpose:** "Email sending via SendGrid"

#### AWS Services
- **Search keywords:** `aws`, `s3`, `lambda`, `dynamodb`, `sns`, `sqs`
- **Suggested secrets:**
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_REGION` (optional)
- **Purpose inference:** Based on service (S3, Lambda, etc.)

#### PostgreSQL/Database
- **Search keywords:** `postgresql`, `postgres`, `pg-`, `pool.query`
- **Suggested secrets:**
  - `DATABASE_URL` or `DATABASE_PASSWORD`
  - `DB_HOST`, `DB_PORT`, `DB_USER`
- **Purpose:** "PostgreSQL database access"

### Context-Based Detection Algorithm

```typescript
function detectFromContext(codeContent: string): Secret[] {
  const detectedSecrets: Secret[] = [];
  const lowerContent = codeContent.toLowerCase();

  // OpenAI detection
  if (lowerContent.includes("openai") || lowerContent.includes("gpt")) {
    detectedSecrets.push({
      name: "OPENAI_API_KEY",
      source: "context",
      confidence: "high",
      purpose: inferOpenAIPurpose(codeContent)
    });
  }

  // Stripe detection
  if (lowerContent.includes("stripe")) {
    detectedSecrets.push({
      name: "STRIPE_SECRET_KEY",
      source: "context",
      confidence: "high",
      purpose: "Stripe payments"
    });

    if (lowerContent.includes("webhook")) {
      detectedSecrets.push({
        name: "STRIPE_WEBHOOK_SECRET",
        source: "context",
        confidence: "high",
        purpose: "Stripe webhook verification"
      });
    }
  }

  // ... more service checks

  return detectedSecrets;
}

function inferOpenAIPurpose(content: string): string {
  if (content.toLowerCase().includes("embedding")) {
    return "OpenAI embeddings";
  }
  if (content.toLowerCase().includes("completion") || content.toLowerCase().includes("chat")) {
    return "OpenAI chat completions";
  }
  return "OpenAI API access";
}
```

## Detection Pattern 4: Supabase Secrets (Auto-Include)

**Always include these secrets for Lovable Cloud projects:**

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase public API key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase admin access

**Source:** Read from `src/integrations/supabase/client.ts` if present

**Example extraction:**

File: `src/integrations/supabase/client.ts`
```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = "https://xyz.supabase.co";
const supabaseAnonKey = "eyJhbG...";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

**Detected:**
- `SUPABASE_URL` - Found in code
- `SUPABASE_ANON_KEY` - Found in code
- `SUPABASE_SERVICE_ROLE_KEY` - Auto-included for Lovable Cloud

## Secret Grouping and Presentation

### Group by Status

**1. From Codebase (⚠️ Needs Setup)**
- Detected via Patterns 1, 2, 3
- Not found in Lovable Cloud
- Requires user to add to Cloud → Secrets

**2. From Lovable Cloud (✅ Already Configured)**
- Extracted via browser automation
- Already present in Lovable's secrets manager
- Status shown as "In Lovable Cloud"

**3. Suggested (💡 Optional)**
- Context-based detection with lower confidence
- User should confirm if needed
- Can be added during init or skipped

### Presentation Example

```
🔍 Secret Detection Results:

From codebase (needs setup):
- OPENAI_API_KEY (used in: chat-completion edge function)
  Purpose: OpenAI chat completions
- STRIPE_SECRET_KEY (used in: process-payment edge function)
  Purpose: Stripe payments

From Lovable Cloud (already configured):
✅ RESEND_API_KEY (already in: send-email, send-welcome)
✅ SUPABASE_SERVICE_ROLE_KEY (system)

Suggested (optional):
💡 STRIPE_WEBHOOK_SECRET (might be needed for: process-payment)
  Purpose: Stripe webhook verification

Any additional secrets to track?
(Enter comma-separated names, or press Enter to continue)
```

## Merge and Deduplication

When combining results from multiple sources:

1. **Primary source is code** - If detected in codebase, use that
2. **Merge usage info** - If same secret found in multiple functions, list all
3. **Track status** - Mark if in Lovable Cloud or needs setup
4. **Remove duplicates** - Same secret from different patterns = single entry

**Merge example:**

Pattern 1 finds: `RESEND_API_KEY` (used in: send-email)
Pattern 3 infers: `RESEND_API_KEY` (context: resend import)
Lovable Cloud: `RESEND_API_KEY` (exists)

**Result:**
```json
{
  "name": "RESEND_API_KEY",
  "purpose": "Email sending via Resend",
  "usedIn": ["send-email"],
  "status": "✅ In Lovable Cloud",
  "source": "merged"
}
```

## Handling Edge Cases

### Case 1: Secret in .env.example but not in Code

**Example:**
- `.env.example` contains `ANALYTICS_KEY=...`
- No code references it

**Handling:**
- Include in detected list
- Mark "usedIn" as empty or "(in env template)"
- Show with note: "Configured in .env.example but not used in current code"

### Case 2: Secret Reference but No Value Pattern

**Example:**
```typescript
const apiKey = Deno.env.get(someVariable);  // Can't extract secret name
```

**Handling:**
- Cannot detect automatically
- Skip this one
- Mention in summary: "Found dynamic env access - manual review recommended"

### Case 3: Same Secret Used in Multiple Functions

**Example:**
- `send-email/index.ts`: `Deno.env.get("RESEND_API_KEY")`
- `send-welcome/index.ts`: `Deno.env.get("RESEND_API_KEY")`

**Handling:**
- Single entry for `RESEND_API_KEY`
- `usedIn: ["send-email", "send-welcome"]`
- Show as comma-separated in CLAUDE.md

### Case 4: Secret Name Typos or Variations

**Example:**
```typescript
Deno.env.get("OPENAI_API_KEY")
Deno.env.get("OPENAI_KEY")
Deno.env.get("OPENAI_API_SECRET")
```

**Handling:**
- Detect all variations
- Ask user to confirm/clarify: "Found 3 OpenAI-related secrets - are these all needed or typos?"
- Store user's clarification in CLAUDE.md

## Integration Points

### During Init Flow

- **After Q4** (Backend selection): Scan codebase
- **During Q6** (Secret Detection Method):
  - If auto-detect: Run all 4 patterns
  - If browser automation available: Get from Lovable Cloud
  - Merge and present results
- **After Q6**: Ask for additional secrets

### During deploy-edge Command

- Scan function being deployed for new secrets
- Compare against CLAUDE.md secrets table
- Warn if new secret detected that's not in CLAUDE.md or not configured

### During Secret Dependency Analysis

Link secrets to functions:
- When user changes Edge Function, check if new secrets needed
- Suggest adding to CLAUDE.md Secrets table
- Warn if required secret not in Lovable Cloud

## Performance Considerations

**Timeouts:**
- Codebase scanning: 5 seconds max
- .env file parsing: < 100ms
- Context scanning: < 2 seconds
- Browser automation: 30 seconds max

**Caching:**
- Cache scan results during single init session
- Don't re-scan if user navigates back
- Clear cache between separate init runs

## Testing the Detection Logic

### Test Case 1: Mixed Project

**Setup:**
- 3 Edge Functions: send-email, process-payment, chat-completion
- .env.example with 5 keys
- Code uses some keys, env file has others

**Expected:**
- Detect all keys from code
- Detect all keys from .env
- Merge with no duplicates
- Show ~5-7 total secrets depending on overlap

### Test Case 2: Service Context Detection

**Setup:**
- Project imports `openai` and `stripe` packages
- Code references chatCompletion and payment processing
- No direct env.get() for some typical secrets

**Expected:**
- Detect direct references from code
- Infer `STRIPE_WEBHOOK_SECRET` from webhook context
- Infer `OPENAI_API_KEY` from import presence
- Present with confidence levels

### Test Case 3: Browser Automation Merging

**Setup:**
- 3 secrets in code: OPENAI_API_KEY, STRIPE_SECRET_KEY, NEW_SECRET
- 2 secrets in Lovable Cloud: RESEND_API_KEY, STRIPE_SECRET_KEY
- Browser automation succeeds

**Expected:**
- Show OPENAI_API_KEY (⚠️ not in Cloud)
- Show STRIPE_SECRET_KEY (✅ in Cloud)
- Show RESEND_API_KEY (✅ in Cloud)
- Show NEW_SECRET (⚠️ not in Cloud)
- Total: 4 unique secrets

---

This reference enables the init command to provide intelligent, automated secret detection while maintaining a fallback for manual entry.
