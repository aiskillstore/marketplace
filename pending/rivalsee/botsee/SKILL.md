---
name: botsee
description: Monitor your brand's AI visibility via BotSee API
version: 0.3.0
---

# BotSee Skill

Monitor your brand's AI visibility (AI SEO/GEO) across ChatGPT, Claude, Perplexity, and Gemini. Provided by botsee.io, the AI Visibility tool for Claude Code and agents.

Commands:

**Workflow:**
- /botsee                                  - Quick status and help
- /botsee signup [--email EMAIL] [--name NAME] [--company COMPANY] [--api-key KEY] - Signup with credit card
- /botsee signup-usdc [--email EMAIL] [--name NAME] [--company COMPANY] [--no-email] - Signup with USDC on Base
- /botsee signup-pay-usdc --amount-cents N [--token TOKEN] [--payment PROOF] - Pay for USDC signup via x402
- /botsee signup-status [--token TOKEN]    - Check signup completion and save API key
- /botsee reset-api-key --token TOKEN    - Exchange a web-generated reset token for a new API key
- /botsee rotate-api-key --id KEY_ID     - Atomically rotate an API key (creates new, revokes old)
- /botsee topup-usdc --amount-cents N [--payment PROOF] - Add credits with USDC on Base via x402
- /botsee create-site <domain> [--types N]   - Save custom config
- /botsee config-show                      - Display saved config
- /botsee analyze                          - Run competitive analysis
- /botsee content                          - Generate blog post from analysis

**Sites:**
- /botsee list-sites             - List all sites
- /botsee get-site [uuid]        - View site details
- /botsee create-site <domain>   - Create a new site
- /botsee archive-site [uuid]    - Archive a site

**Customer Types:**
- /botsee list-types             - List customer types
- /botsee get-type <uuid>        - View type details
- /botsee create-type <name> [desc] - Create customer type
- /botsee generate-types [count] - Generate customer types
- /botsee update-type <uuid> [name] [desc] - Update customer type
- /botsee archive-type <uuid>    - Archive customer type

**Personas:**
- /botsee list-personas [type]   - List personas (all or by type)
- /botsee get-persona <uuid>     - View persona details
- /botsee create-persona <type> <name> [desc] - Create persona
- /botsee generate-personas <type> [count] - Generate personas for type
- /botsee update-persona <uuid> [name] [desc] - Update persona
- /botsee archive-persona <uuid> - Archive persona

**Questions:**
- /botsee list-questions [persona] - List questions (all or by persona)
- /botsee get-question <uuid>    - View question details
- /botsee create-question <persona> <text> - Create question
- /botsee generate-questions <persona> [count] - Generate questions for persona
- /botsee update-question <uuid> <text> - Update question text
- /botsee delete-question <uuid> - Delete question

**Results:**
- /botsee results-competitors <uuid>    - View competitor results
- /botsee results-keywords <uuid>       - View keyword results
- /botsee results-sources <uuid>        - View source results
- /botsee results-responses <uuid>      - View all AI responses

## Implementation

When user invokes a BotSee command, run the corresponding Python script. All commands use a single bundled script that handles API calls internally.

### /botsee (status)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py status
```

### /botsee signup [--email EMAIL] [--name NAME] [--company COMPANY] [--api-key KEY]

**New user signup flow (credit card):**

**Step 1: Get signup URL**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup
```

The command prints a line like:
```
Complete signup: https://app.botsee.io/setup?token=...
```

Extract that URL and tell the user:
"To complete your BotSee signup, visit this URL: **[URL from above]**

After completing signup on that page, come back here and run /botsee signup-status."

**Step 2: Save your API key**

After completing signup on that page, run:

/botsee signup-status

The script retrieves your API key from the server automatically using your signup token.
If prompted for a token, use the token from the URL on the setup page.

### /botsee signup-usdc [--email EMAIL] [--name NAME] [--company COMPANY] [--no-email]

**USDC signup flow (x402 on Base):**

**Step 1 — Ask the user before calling the API**

When `signup-usdc` is invoked without already knowing the user's preference, ask:

> "Do you want to associate an email with this account?
> - **Yes (email)** — You'll get a setup link to verify your email and access the dashboard later
> - **No (API only)** — Skip email entirely and go straight to payment"

**Step 2a — Email path**

Call:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-usdc
```
(no `--no-email` flag)

The command prints a line like:
```
Setup URL: https://app.botsee.io/setup?token=...
```

Extract that URL and tell the user:
"Visit this URL to enter and verify your email and read the setup instructions: **[URL from above]**

Once you've done that, come back here and we'll complete the USDC payment."

Do NOT call `signup-pay-usdc` yet. Wait for the user to confirm they've completed the setup URL step.

**Step 2b — No-email path**

Call:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-usdc --no-email
```

No setup URL will be returned. Immediately proceed to payment.

**Step 3 — Payment (both paths)**

After the email-path user confirms they visited the setup URL (or immediately for no-email path):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-pay-usdc --amount-cents 250
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-status
```

**x402 flow details:**
1. `signup-usdc` creates a USDC signup token via `POST /api/v1/signup/usdc`
2. `signup-pay-usdc --amount-cents N` calls `POST /api/v1/signup/:token/pay-usdc` without a payment header → server returns 402 with payment requirements (network, amount, `payTo` address)
3. Use a wallet (Pinch, Coinbase CDP Agentic Wallet) to send USDC to the returned address
4. Retry with the payment proof: `signup-pay-usdc --amount-cents N --payment <proof>`
5. `signup-status` polls until complete and saves the API key

### /botsee signup-pay-usdc --amount-cents N [--token TOKEN] [--payment PROOF]

```bash
# Step 1: Get 402 challenge (no --payment → returns payment requirements)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-pay-usdc --amount-cents 250

# Step 2: Retry with proof after wallet pays
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-pay-usdc --amount-cents 250 --payment <proof>
```

Omit `--payment` to get a 402 challenge with network, amount, and `payTo` address.
Include `--payment <base64-proof>` on the final retry after your wallet has made the payment.

### /botsee signup-status [--token TOKEN]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py signup-status
```

Saves API key to `~/.botsee/config.json` automatically once signup is completed.

### /botsee reset-api-key --token TOKEN

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py reset-api-key --token <token>
```

Exchanges a one-time reset token (generated on the BotSee web dashboard) for a new API key.
The token is single-use and expires in 15 minutes.
On success, the new key is saved to `~/.botsee/config.json` and the old key is revoked.

### /botsee topup-usdc --amount-cents N [--payment PROOF]

```bash
# Step 1: Get 402 challenge (no --payment → returns payment requirements)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py topup-usdc --amount-cents 5000

# Step 2: Retry with proof after wallet pays
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py topup-usdc --amount-cents 5000 --payment <proof>
```

Omit `--payment` to get a 402 challenge with network, amount, and `payTo` address.
Include `--payment <base64-proof>` on the final retry after your wallet has made the payment.

### /botsee create-site <domain> [--types T] [--personas P] [--questions Q]

**Requires:** API key from `/botsee signup`

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py create-site <domain>
```

**Optional parameters:**
- `--types` (default: 2, range: 1-3)
- `--personas` (default: 2, range: 1-3)
- `--questions` (default: 5, range: 3-10)

**What happens:**
1. Creates a site for the domain
2. Generates customer types, personas, and questions
3. Saves configuration to workspace and user config

**Customize generation counts:**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py create-site <domain> --types 3 --personas 2 --questions 10
```

### /botsee config-show

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py config-show
```

### /botsee analyze

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py analyze
```

Starts analysis, polls until complete, then displays competitors, keywords, and sources.

### /botsee content

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py content
```

Generates blog post from latest analysis. Auto-saves to `botsee-YYYYMMDD-HHMMSS.md`.

---

## Usage & Billing Commands

### /botsee usage-by-site [--from DATE] [--to DATE] [--site-uuid UUID]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py usage-by-site
```

Credit usage grouped by site: per-site totals plus a per-category breakdown.
`--from`/`--to` are ISO 8601 dates; `--site-uuid` limits to one site. (`GET /api/v1/usage/by-site`)

### /botsee usage-line-items [--from DATE] [--to DATE] [--site-uuid UUID] [--category CAT] [--limit N]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py usage-line-items
```

Individual paid operations (line items), newest first — date, site, category,
operation, and credits. Same data as the dashboard "Details" table and CSV export.
(`GET /api/v1/usage/line-items`)

---

## Sites Commands

### /botsee list-sites

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py list-sites
```

### /botsee get-site [uuid]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py get-site [uuid]
```

If uuid is omitted, uses the site from `~/.botsee/config.json`.

### /botsee create-site <domain>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py create-site <domain>
```

### /botsee archive-site [uuid]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py archive-site [uuid]
```

---

## Customer Types Commands

### /botsee list-types

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py list-types
```

### /botsee get-type <uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py get-type <uuid>
```

### /botsee create-type <name> [description]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py create-type "Enterprise Buyers" "Large companies seeking solutions"
```

### /botsee generate-types [count]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py generate-types 3
```

Defaults to 2 if count is omitted.

### /botsee update-type <uuid> [name] [description]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py update-type <uuid> --name "New Name" --description "New description"
```

### /botsee archive-type <uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py archive-type <uuid>
```

---

## Personas Commands

### /botsee list-personas [type_uuid]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py list-personas
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py list-personas <type_uuid>
```

### /botsee get-persona <uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py get-persona <uuid>
```

### /botsee create-persona <type_uuid> <name> [description]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py create-persona <type_uuid> "Sarah Chen" "VP of Marketing at mid-sized SaaS company"
```

### /botsee generate-personas <type_uuid> [count]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py generate-personas <type_uuid> 3
```

Defaults to 2 if count is omitted.

### /botsee update-persona <uuid> [name] [description]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py update-persona <uuid> --name "New Name" --description "New description"
```

### /botsee archive-persona <uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py archive-persona <uuid>
```

---

## Questions Commands

### /botsee list-questions [persona_uuid]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py list-questions
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py list-questions <persona_uuid>
```

### /botsee get-question <uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py get-question <uuid>
```

### /botsee create-question <persona_uuid> <question_text>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py create-question <persona_uuid> "What are the best email marketing tools?"
```

### /botsee generate-questions <persona_uuid> [count]

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py generate-questions <persona_uuid> 5
```

Defaults to 5 if count is omitted.

### /botsee update-question <uuid> <question_text>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py update-question <uuid> "What are the best affordable email marketing tools?"
```

### /botsee delete-question <uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py delete-question <uuid>
```

---

## Results Commands

### /botsee results-competitors <analysis_uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py results-competitors <analysis_uuid>
```

### /botsee results-keywords <analysis_uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py results-keywords <analysis_uuid>
```

### /botsee results-sources <analysis_uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py results-sources <analysis_uuid>
```

### /botsee results-responses <analysis_uuid>

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/botsee/botsee.py results-responses <analysis_uuid>
```

**Getting the Analysis UUID:**
The analysis UUID is displayed when you run `/botsee analyze`:
```
📊 Analysis started: abc-def-123
```
Copy the UUID and use it with the results commands to view detailed analysis data.

---

## Agent Usage Notes

This skill is designed for **non-interactive agent usage**. All commands accept arguments via command-line flags - no prompts or user input required.

### Key Considerations for Agents

**1. Signup Flow Requires Human Intervention**

For **new users** without an API key, the signup command creates a signup token and displays a URL:
```bash
/botsee signup
# Outputs signup URL for browser completion
```

**Agents should:**
- Use the `--api-key` flag if API key is available
- Inform user if signup is needed (cannot be completed by agent)
- Consider API key as a prerequisite for autonomous operation

**2. Async Operations with Polling**

Two commands can involve waiting/polling:
- `/botsee signup-status` (checks signup completion)
- `/botsee analyze`: up to 10 minute timeout

Commands will block until complete or timeout. No intermediate progress updates.

**3. Analysis Discovery**

To view detailed results after analysis:
1. Run `/botsee analyze` and capture the analysis UUID from output
2. Use UUID with `/botsee results-*` commands

**Recommended pattern:**
```bash
# Run analysis
output=$(/botsee analyze)
# Extract UUID (line containing "Analysis started:")
uuid=$(echo "$output" | grep "Analysis started:" | awk '{print $NF}')
# View results
/botsee results-competitors "$uuid"
```

**4. Configuration Files**

Two config files exist:
- **User config:** `~/.botsee/config.json` (API key + site UUID)
- **Workspace config:** `.context/botsee-config.json` (generation defaults, optional)

Agents can discover state via:
- `/botsee` - Shows account status
- `/botsee config-show` - Shows workspace config

**5. Credit Costs**

All operations that consume credits display remaining balance. Agents should:
- Check balance before expensive operations (`/botsee` command)
- Handle "Insufficient credits" errors gracefully
- Monitor credit usage (shown after each operation)

**Costs:**
- Setup (~75 credits with defaults 2/2/5)
- Analysis (~660 credits per run)
- Content generation (15 credits)

**6. Error Handling**

All errors exit with code 1 and print to stderr. Error messages include:
- HTTP status codes (when relevant)
- Actionable next steps
- No API key leakage (sanitized)

**7. Idempotency**

- **Safe to retry:** Status, list, get commands (read-only)
- **Not idempotent:** Create commands (will create duplicates)
- **Updates:** Require specific UUID, safe to retry

**8. Output Format**

- **CRUD operations:** JSON output for parsing
- **Workflow commands:** Human-readable formatted text
- **Status/balance:** Always displayed at command completion

### Example Agent Workflow

```bash
# 1. Check status (discover state)
/botsee

# 2. Save API key if provided by user
/botsee signup --api-key bts_live_abc123

# 3. Create a site
/botsee create-site https://example.com

# 4. Run analysis (captures UUID)
analysis_output=$(/botsee analyze)
uuid=$(echo "$analysis_output" | grep -oP '(?<=Analysis started: )\S+')

# 5. View results
/botsee results-competitors "$uuid"

# 6. Generate content
/botsee content

# 7. Check final balance
/botsee
```
