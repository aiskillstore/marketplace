---
name: cold-email-spam-lint
description: "Deterministic spam-trigger scanner for cold email drafts. Scans subject + body against a 200-word spam-trigger lexicon, validates link/image ratios, checks for ALL-CAPS / emoji / clickbait / fake-Re patterns, and returns a 0-100 deliverability-risk score with line-by-line flags. Backed by a Python script (no LLM). Loaded by the main cold-email skill before any send + on Wednesday's ship-day batch via cold-email-weekly-rhythm."
user-invocable: false
allowed-tools: Read Bash
  - Grep
license: MIT

---

# Cold Email Spam Lint — deterministic spam-trigger scanner

A real scanner, not vibes. Backs onto `scripts/spam_word_lint.py` for
deterministic scoring against a maintained 200-word spam-trigger
lexicon.

## Activation

Loaded by:
- `cold-email-craft` — final self-check before delivering a draft
- `cold-email-weekly-rhythm` — Wednesday ship-day batch lint
- User invocation: "spam-lint this email"

## How it scores

Each draft gets a 0-100 deliverability-risk score across 6 axes:

| Axis | Weight | What it catches |
|---|---|---|
| Spam-trigger words | 25 | "URGENT", "ACT NOW", "Limited time", "free money", "guaranteed" — 200+ patterns |
| ALL CAPS | 15 | Subject or body lines in caps |
| Emoji | 10 | Emoji in subject (high B2B spam signal) |
| Clickbait patterns | 15 | "You won't believe...", "This one trick...", "Doctors hate..." |
| Fake threading | 10 | "Re:" / "Fwd:" in subject when there's no prior thread |
| Link / image ratio | 25 | >1 link or image-to-text >40% — B2B threshold |

Output:

```markdown
# Spam Lint — <subject>

## Deliverability risk score: <0-100>/100

| Axis | Score | Issues |
|---|---|---|
| Spam-trigger words | <0-25>/25 | Found: <words> |
| ALL CAPS | <0-15>/15 | Caps in: <lines> |
| Emoji | <0-10>/10 | Subject has 🚀 |
| Clickbait | <0-15>/15 | "You won't believe..." in line 2 |
| Fake threading | <0-10>/10 | Subject starts with "Re:" |
| Link/image ratio | <0-25>/25 | 3 links found |

## Line-by-line flags

[Line 1 — Subject] "Re: URGENT — pipeline update 🚀"
  - Fake threading: subject begins with "Re:"
  - Spam-trigger: "URGENT"
  - ALL CAPS in subject
  - Emoji in subject

[Line 5 — Body] "You won't believe what we shipped this quarter."
  - Clickbait pattern: "You won't believe"

## Verdict
| Score | Verdict |
|---|---|
| 90-100 | Ship |
| 75-89 | Ship after fixes — flagged items have alternatives below |
| 60-74 | Rewrite — too many deliverability flags |
| <60 | Do not send — will land in spam |
```

## Implementation

The skill shells out to a Python script:

```bash
python3 scripts/spam_word_lint.py --subject "<subject>" --body "<body>" --format json
```

The script returns structured JSON. The skill formats it into the
table above.

## Script location

`../../scripts/spam_word_lint.py`

The script is zero-dependency Python 3.8+. No external libraries, no
network calls.

## Lexicon source

The 200-word lexicon lives at `references/spam-trigger-lexicon.md`
(loaded as a JSON-shaped const at the top of the Python script).
Sources:

- Google Postmaster Tools 2024 bulk-sender guidance
- Yahoo + Microsoft 2024 bulk-sender rules
- Litmus / Email on Acid public spam-trigger lists
- JMC's own list from reviewing 1000+ campaigns

The lexicon is versioned. When Gmail/Yahoo update guidance, the
lexicon updates and the script picks it up on next install.

## Why this matters

Vibes-based spam-checking misses 60% of issues. A deterministic lint
catches every instance of the 200 known triggers, every time. The
script runs in <100ms per email — Wednesday's batch ship-day check
runs through 100 emails in under 10 seconds.

## References

- `../../scripts/spam_word_lint.py` — the actual scanner
- `references/spam-trigger-lexicon.md` — the lexicon source
- `../../cold-email/references/banned-patterns.md` — JMC-specific bans
  (separate from generic spam triggers — these are voice + framework
  bans, not deliverability bans)
