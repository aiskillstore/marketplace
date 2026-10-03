---
name: cold-email-subject-lines
description: Generate or critique cold-email subject lines across 4 framework families (pain, curiosity, social proof, direct). Each suggestion is ≤7 words, no spam triggers, no clickbait, includes reply-rate notes from the JMC Subject Line Swipe File (25 high-performers). Loaded by the main cold-email skill when the user asks for subject lines, openers, or to critique a draft subject.
user-invocable: false
allowed-tools: Read
  - Grep
license: MIT

---

# Cold Email Subject Lines — 4-Framework Pattern Library

Loaded by `cold-email` when the user wants subject-line suggestions or
critique.

## Activation triggers

- "Subject lines for..."
- "Subject line ideas"
- "Critique this subject"
- "Better subject than..."
- "What's a good subject for..."

## The 4 framework families

| Framework | When to use | Example |
|---|---|---|
| **Pain** | Audience is problem-aware | "Pipeline gap after the Q3 hire freeze?" |
| **Curiosity** | Audience needs a hook before they'll open | "What <peer company> tried after their Series B" |
| **Social proof** | Audience trusts other companies more than vendors | "How <peer> hit 40% reply rate" |
| **Direct** | Audience is short on time, you have a clear ask | "15 min Thursday re: demand gen?" |

The skill's job: given a draft cold email (or a target audience + EVP),
suggest 3-5 subject lines spanning at least 2 frameworks.

## Constraints (every subject)

- ≤7 words (Gmail truncates around 30 chars mobile)
- No ALL CAPS
- No emojis (deliverability)
- No `Re:` / `Fwd:` fakes (banned by bulk-sender rules)
- No clickbait ("You won't believe...", "This one trick...")
- No spam triggers — load `references/spam-trigger-words.md` for the list
- Personalization (first name, company) where relevant — but not faked
- Lowercase first letter often outperforms capitalized in B2B (test)

## Workflow

### 1. Gather context

| Input | Why needed |
|---|---|
| `audience` (PSP description) | Determines which framework family fits |
| `evp` | Anchors social-proof and pain framings |
| `intent` (open / reply / book) | Direct frameworks work better for booking |
| `relationship` (cold / re-engagement / referred) | Different opening patterns |

### 2. Generate 5 suggestions

Default: 1-2 per framework family (3-5 total). Order by predicted
fit, not framework alphabetical.

```markdown
| # | Framework | Subject | Notes |
|---|---|---|---|
| 1 | Pain | "Pipeline gap after the freeze?" | Anchors PSP directly; for problem-aware audience |
| 2 | Social proof | "How <peer> hit 40% reply rate" | Best if you have the case study |
| 3 | Curiosity | "<peer> tried this after Series B" | If audience is skeptical of direct claims |
| 4 | Direct | "15 min Thursday re: demand gen?" | If they're warm or you have signal-based timing |
| 5 | Pain | "Q3 demand gen plan question" | Conservative; fits exec inboxes |
```

### 3. Spam-trigger lint

After generating, lint each subject against
`references/spam-trigger-words.md`. Flag any that hit known triggers.

### 4. Critique mode

If user pastes a subject for critique, return:

```
Subject: "<original>"

Issues:
  - <issue 1>
  - <issue 2>

Better alternatives:
  - "<alt 1>" — <why>
  - "<alt 2>" — <why>
```

## References

- `references/spam-trigger-words.md` — banned words / phrases that hurt
  inbox placement
- The **25 High-Performing Subject Lines** PDF ships in
  [the free Cold Email Linter](https://jaymountconsulting.com/tools/cold-email-linter) — 25
  patterns organized by framework with reply-rate notes from real
  campaigns
- The full **Cold Email & Outreach Craft** course in The Compounding
  Engine:
