---
name: cold-email-craft
description: Draft a single signal-anchored cold email or a 3-touch follow-up sequence using the JMC framework — <90 words, binary CTA, no banned openers. Anchors on a Pain Signal Profile (not demographics). Loaded by the main cold-email skill when the user asks to write or sequence outreach. Includes the surgical "rewrite the weakest line" mode for ship-or-cut review.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Cold Email Craft — sub-skill

Drafts the actual email(s). Loaded by `cold-email` when the user wants
to write or sequence outreach.

## Activation

The main `cold-email` skill routes here when the user says any of:

- "Write a cold email to..."
- "Draft an outreach to..."
- "Build a 3-touch sequence for..."
- "Follow-up to <name> at <company>"
- "Rewrite this cold email"

## Workflow

### 1. Gather the six framework variables

Required:

| Variable | Source | Ask if missing |
|---|---|---|
| `firstName` | User-provided | "What's the recipient's first name?" |
| `role` | User-provided or LinkedIn | "What's their role?" |
| `company` | User-provided | "Which company?" |
| `signal` | Public, recent, verifiable | "What did they just do publicly? (Job post, funding, launch, hire, content)" |
| `pain` | What the signal implies operationally | "What does that signal imply about their pipeline / motion / stack?" |
| `evp` | One-line value prop | "What's your one-line EVP for this segment? (≤22 words)" |
| `senderName` | User | "Who are you signing as?" |

**Do not fabricate.** If any are missing, ask. Never assume role,
company, or signal — wrong assumptions kill cold email.

### 2. Validate the framework

Before generating, validate:

- **Signal** is something they DID, not who they ARE. If user provides
  "VP of Marketing at Series B SaaS", push back: "That's a demographic,
  not a signal. What did they post/announce/ship in the last 30 days?"
- **Pain** uses their language, not yours. No "synergy" / "optimize" /
  "leverage".
- **EVP** is ≤22 words, has one specific outcome, one tradeoff.

### 3. Generate

Use the canonical template from `references/copy-frameworks.md`:

```
Subject: <see references/subject-line-patterns.md>

{firstName} —

<Quote the signal verbatim, 1 sentence.>

<Pain in their language, 1 sentence.>

<EVP, ≤22 words.>

<Binary CTA, time-bound.>

— {senderName}
```

### 4. Self-check against constraints

After generating, verify:

- [ ] Total word count <90
- [ ] No banned openers ("Hope you're well", "Just wanted to")
- [ ] No banned closes ("Let me know your thoughts", "Happy to chat")
- [ ] Binary CTA (yes/no answerable)
- [ ] Signal is quoted verbatim (not paraphrased)
- [ ] Pain uses recipient's language
- [ ] EVP ≤22 words
- [ ] Subject ≤7 words, no clickbait

If any check fails, regenerate that block before showing the user.

### 5. Offer the "rewrite the weakest line" pass

After delivering the draft, offer:

> "Want me to identify the single weakest line and rewrite it? (1
> sentence + rationale, no full rewrite.)"

This is the canonical ship-or-cut decision aid.

## 3-touch sequence mode

When the user asks for a sequence, generate all four touches at once:

| Day | Touch | Length | Shape |
|---|---|---|---|
| 0 | T1 | <90 words | Full signal-anchored opener (above) |
| 3 | T2 | <70 words | 1-line case study + binary close |
| 7 | T3 | <70 words | Different angle on same PSP (cost / risk / opportunity-cost) |
| 14 | T4 | <60 words | Binary close: continue or close the loop |

Each touch references the same signal but reframes the pain. No
"following up on my last email" anywhere.

## Output format

Default: plain text with clearly labeled subject + body.

If user requests JSON: `{ subject, preheader, body, touchNumber,
wordCount, framework: { signal, pain, evp, ask } }`.

## Reference

- `references/copy-frameworks.md` — canonical templates
- `../../cold-email/references/jmc-framework.md` — full framework
- `../../cold-email/references/banned-patterns.md` — what NOT to write
- `../../cold-email/references/binary-ctas.md` — 30 binary CTA patterns
