---
name: cold-email-onboarding
description: First-run interactive setup for the cold-email skill pack. Walks the operator through brand-config.json (ICP, PSP, EVP, tone, infrastructure) and SOUL.md (voice fingerprints, banned phrases, stories you lean on) in ~10 minutes. Refuses to let the operator skip — generic output is worse than no output. Loaded automatically by the main cold-email skill when brand-config.json or SOUL.md is missing.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Cold Email Onboarding — first-run setup

Walks the operator through 10 minutes of setup that makes every
downstream output 10x more useful than generic framework prose.

## Activation

Loaded automatically by `cold-email` (the orchestrator) on first
invocation when `brand-config.json` and/or `SOUL.md` are missing from
the project root.

Also user-invocable on demand:
- "Set up brand config"
- "Configure my voice"
- "Re-run cold-email onboarding"
- "Update brand-config"

## Why this exists

Generic cold-email output is worse than no output. The framework is
generic — your ICP + PSP + voice are specific. Without those, the
skill produces vibes-emails that look like every other AI-generated
cold email.

This onboarding sub-skill captures the operator's:

1. **ICP precision** (specific segment, exclusion criteria)
2. **PSP** (signal anchors → felt pain → vocabulary)
3. **EVP** (Schwartz tier + the 22-word line + proof)
4. **Voice** (phrases used + phrases banned + tone settings)
5. **Stories** (case-study reservoir to pull from)
6. **Infrastructure** (domain, inbox provider, deliverability state)
7. **Operations** (weekly cadence, reply routing, experiment log)

Output: `brand-config.json` + `SOUL.md` at the project root, both
filled in.

## Workflow

### Step 0 — Detect prior state

```python
# Pseudo-code logic
exists_brand = file_exists("brand-config.json")
exists_soul = file_exists("SOUL.md")

if exists_brand and exists_soul:
    ask: "Both files exist. Refresh them, or skip onboarding?"
elif exists_brand:
    "I see brand-config.json but no SOUL.md. Let's add the voice piece."
elif exists_soul:
    "I see SOUL.md but no brand-config.json. Let's add the config."
else:
    "Welcome. ~10 minute setup. Ready?"
```

### Step 1 — Operator + company

Ask in one batch:

```
First, the basics:

1. Your name (for the sign-off line)?
2. Your title?
3. Your company?
4. Your calendar / booking link?
```

Save to `brand-config.operator`.

### Step 2 — ICP precision check

```
Now your ICP. Be specific. "B2B SaaS" is too broad.

Tell me:
1. The 1-sentence segment (with stage / size / motion / region)
2. The 3 role-titles you target most
3. The 3 exclusion criteria (who you DON'T sell to)

If you're unsure on any of these, that's a signal you need to
sharpen ICP before launching outreach. Let me know if you want to
talk through it, or use a placeholder for now.
```

Save to `brand-config.icp`.

If the operator says "I don't know yet" — push back ONCE:

> A vague ICP produces vague cold email. Want to use placeholders
> like "Tech companies, role: VP+, exclusion: pre-PMF" — and we'll
> mark this for review after the first 100 sends?

### Step 3 — Pain Signal Profile (PSP)

```
The PSP is the bridge from a public signal to felt operational pain.

Tell me:
1. 3 public signals you anchor outreach on (job posts, funding, hires, launches, pricing changes)
2. The primary pain the signal implies — in YOUR buyer's vocabulary, not your category jargon
3. The 90-day trigger that makes it acute right now: new-exec / budget-cycle / obvious-failure
4. The role that FEELS the pain (often a layer below the buying authority)
5. 4-8 phrases your buyer uses about this pain (read their job posts, LinkedIn comments, conference talks)
```

If the operator hasn't built a PSP yet, suggest installing the
companion skill:

> Haven't built a PSP yet? Install `cmj-hub/claude-psp` first — it
> walks you through the full 5-component PSP construction. I'll wait.

Save to `brand-config.psp`.

### Step 4 — EVP

```
Your EVP — the one-line value prop.

1. Which Schwartz awareness tier (1-5) is your primary outreach
   audience in? (Most B2B cold-email targets are Tier 2 or 3.)
2. Your 22-word EVP using the shape: "For <ICP>, in <pain>, we ship
   <specific outcome> without <specific tradeoff>."
3. The specific outcome (must include a number)
4. The specific tradeoff
5. Your strongest proof point (case study / metric / receipt)
```

If the operator hasn't built an EVP yet:

> Haven't built an EVP yet? Install `cmj-hub/claude-evp` first — it
> generates 3 variants per tier and a structured 3-tier brief. I'll
> wait.

Save to `brand-config.evp`.

### Step 5 — Voice fingerprints (SOUL.md)

```
Now your voice. This is what makes the output sound like YOU,
not Jay Mount or ChatGPT.

1. 5-10 phrases you use a lot in your writing (look at your last 10
   emails / posts — what shows up repeatedly?)
2. 5-10 phrases you would NEVER write (your hard nos)
3. Tone settings:
   - Formality: Casual / Professional / Direct
   - Sentence length: Short / Medium / Mixed
   - Confidence: High / Hedged / Calibrated
   - Humor: Dry / Never / Always
   - First-person: I / We / Both
4. 3-5 stories or receipts you reference often (these become the case-study reservoir)
5. Any topic you absolutely will not write about (boundaries)
```

Save to `SOUL.md` (not JSON — markdown, since voice is descriptive).

### Step 6 — Infrastructure

```
Your sending setup:

1. Sending domain (e.g. outreach.acmecloud.com)
2. Inbox provider (smartlead / instantly / GSuite / O365 / custom)
3. Warm-up status (fresh / ramped / mature)
4. Last deliverability audit date
5. DMARC policy (none / quarantine / reject)
```

If the operator hasn't run deliverability, suggest:

> Want me to run a deliverability audit now? (15 DNS + reputation
> checks; no paid APIs. Takes ~30 seconds.) Or save this for later?

Save to `brand-config.infrastructure`.

### Step 7 — Operations

```
Your weekly cadence + reply routing.

Pick a weekly rhythm:
- Mon/Wed/Fri (default — most teams)
- Daily small batch
- Custom

Reply routing — when a reply comes in, what should happen?
- buy_signal → ?
- positive → ?
- neutral → ?
- not_interested → ?
```

Save to `brand-config.operations`.

### Step 8 — Write the files

Write `brand-config.json` + `SOUL.md` at the project root with the
captured data. Show the operator a preview:

```
✓ brand-config.json (24 fields populated)
✓ SOUL.md (voice fingerprints + 5 stories)

Try a quick test:
> Write a cold email to <name>, <role> at <company>. They just <signal>.

The output will now use:
- Your ICP precision
- Your EVP variant
- Your voice (phrases-you-use + phrases-banned)
- The JMC framework on top
```

### Step 9 — Re-onboarding cadence

```
Final note — brand profiles decay. Re-run this onboarding when:
- Your ICP shifts (new segment / segment cull)
- Your EVP changes (especially after a 30-day reply-rate review)
- Your buyer's vocabulary evolves
- Quarterly minimum

Re-run with: `/cold-email onboarding refresh`
```

## Stress-test mode

User-invocable: `/cold-email onboarding stress-test`

Loads existing brand-config + SOUL and walks the operator through
edge cases:

- "Your ICP says <X>. Show me a real prospect that fits — does the
  signal-pain-EVP chain hold?"
- "Your EVP says <Y>. Read it out loud. Does it sound like something
  your buyer would say back? If not, refine."
- "Your banned-phrases list has 5 items. I'll generate a 'banned'
  email and see if you accept or reject. If you accept any, the list
  needs more items."

## References

- `../../brand-config.example.json` — full template
- `../../SOUL.md` — voice template
- `../../AGENTS.md` — behavior rules
- Sister skills:
  - `cold-email-kickoff` — adaptive router that uses these files
  - `cold-email-craft` — drafts emails using brand + voice
  - `cold-email-audit` — audits programs against brand + voice
