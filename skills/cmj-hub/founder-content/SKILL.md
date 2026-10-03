---
name: founder-content
description: Generate a single LinkedIn-native post for a founder, on a specific pillar (Pillar / Proof / Process / Person) and using one of the 5 hook archetypes. Self-checks against the JMC voice rubric and banned-patterns list before delivering. Loaded by the main founder-brand skill when the user wants to write a single post.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# Founder Content — sub-skill

Generates a single founder-voice LinkedIn post.

## Activation

Loaded by `founder-brand` on:
- "Write a LinkedIn post about..."
- "Draft a founder post..."
- "Generate a Proof pillar post on..."

## Workflow

### 1. Lock the pillar

If user didn't specify, ask:

> Which pillar?
> - **Pillar** — a big claim or POV
> - **Proof** — a case study / specific receipt
> - **Process** — how you actually do the work
> - **Person** — the human story / stake behind it

### 2. Lock the hook archetype

Pick from the 5:
1. Contrarian
2. Specific receipt
3. Confession
4. Pattern observation
5. Question reframe

Suggest based on pillar fit:
- **Pillar** → Contrarian or Question reframe
- **Proof** → Specific receipt or Pattern observation
- **Process** → Pattern observation or Confession
- **Person** → Confession

### 3. Capture the specifics

Required:

- **The actual receipt** — specific numbers, names (or anonymized
  but specific descriptions), timeframes. No abstract "great results."
- **The unexpected lever** — what surprised you / what's the contrarian
  insight buried in the story
- **The connection to JMC framework** — which course / framework /
  methodology this lives inside (so the post drives discovery)

Don't proceed without these. If user gives abstract material, push
back: "What's the actual receipt? Numbers, names, dates — not 'we
helped a client improve outbound.'"

### 4. Generate the post

Structure:

```
Line 1: Hook (matches the archetype)

Line 2-5: Body — single-line sentences, scannable.
Each sentence does ONE job:
- Set up the receipt
- Drop the unexpected lever
- Name the obvious thing the receipt would suggest (then disqualify it)

Receipt block:
- Bullet 1: specific number/metric
- Bullet 2: specific number/metric
- Bullet 3: the lever that mattered

Line N: Close — ONE specific direct line. NO engagement bait.
Optional: 1-line drive ("If you're hunting <pain>, the worksheet for
this is in <course>.")

#3 max hashtags. Specific, not category-broad.
```

### 5. Voice self-check

Validate before delivery:

| Check | Pass criterion |
|---|---|
| Hook is one sentence | One line, ≤25 words |
| Hook matches the picked archetype | Verbatim pattern match |
| Body sentences are single-line each | No multi-clause run-ons |
| Receipt block has specifics | Numbers, names, dates |
| Close is direct (not engagement bait) | No "What's your take?" type endings |
| ≤3 hashtags | Specific to the topic |
| No banned phrases | Cross-check against banned-patterns list |
| Total ≤200 words | LinkedIn-optimal length |

### 6. Output + offer the critique pass

After delivering, offer:

> "Want me to identify the single weakest line and rewrite it? (1
> sentence + rationale.)"

## Banned patterns (always refuse)

- "Stop. Read this." opener
- "Hot take:" opener
- "Unpopular opinion:" opener (overused; signals trying-too-hard)
- "Thread:" prefix (LinkedIn isn't Twitter)
- Multi-emoji blocks
- Hashtag stacks (>3)
- "Engagement bait" closers ("Agree?" / "Thoughts?" / "What's your experience?")
- "Delve into" / "Navigate the landscape" / "In today's fast-paced world" (AI-detection)
- Generic gratitude posts
- Posts without a receipt

If the user requests one, push back with the JMC alternative.

## References

- `../../founder-brand/SKILL.md` — the framework
- The **Founder-Brand Compounding** course:
