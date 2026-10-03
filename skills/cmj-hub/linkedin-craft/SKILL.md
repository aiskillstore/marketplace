---
name: linkedin-craft
description: LinkedIn-native post construction — format for skim (1-sentence opener, single-line body, bulleted receipt, no engagement bait), generate 5 hook variants across the 5 hook archetypes (contrarian, specific receipt, confession, pattern observation, question reframe), and critique a draft for voice + anti-pattern compliance. Loaded by the main founder-brand skill for LinkedIn-specific work.
user-invocable: false
allowed-tools: Read Write
  - Grep
license: MIT

---

# LinkedIn Craft — sub-skill

LinkedIn-specific post construction and critique.

## Activation

Loaded by `founder-brand` on:
- "LinkedIn post about..."
- "5 hook variants for..."
- "Critique this LinkedIn draft"
- "Better hook for this topic"

## Modes

### Mode A — generate 5 hook variants

Given a topic, produce one hook per archetype:

```markdown
# Hook variants — <topic>

| # | Archetype | Hook |
|---|---|---|
| 1 | Contrarian | "Most teams do X. The lever is actually Y." |
| 2 | Specific receipt | "<Metric>: <number> in <timeframe>. The lever wasn't <obvious thing>." |
| 3 | Confession | "I used to think X. After <N> failed attempts I figured out it was Y." |
| 4 | Pattern observation | "I've reviewed <N> <thing> this year. One pattern keeps showing up." |
| 5 | Question reframe | "Stop asking <usual Q>. Ask <better Q> instead." |

## Recommended primary
<#N> — <one-sentence rationale on why this archetype fits the topic best>
```

### Mode B — format for skim

Take a finished post and reformat for LinkedIn-native skim:

```markdown
[1-sentence hook]

[single-line body sentence]

[single-line body sentence]

[single-line body sentence]

[Receipt block:]
- Bullet 1
- Bullet 2
- Bullet 3

[1-line close — direct, no engagement bait]

#hashtag1 #hashtag2
```

Max 200 words. Max 3 hashtags. No emoji blocks.

### Mode C — critique a draft

```markdown
# Draft critique

**Voice score:** <0-100>

| Dimension | Score | Issue |
|---|---|---|
| Hook strength | <0-25>/25 | <one sentence> |
| Specificity (receipts) | <0-25>/25 | <one sentence> |
| Voice (founder, not thought-leader) | <0-25>/25 | <one sentence> |
| Format (LinkedIn-skim) | <0-15>/15 | <one sentence> |
| No anti-patterns | <0-10>/10 | <list any hits> |

## Single weakest line
Original: "<line>"
Rewrite: "<better>"
Rationale: <one sentence>

## Anti-pattern hits
- <hit 1>
- <hit 2>

## Verdict
<ship / ship-after-rewrite / start-over>
```

### Mode D — better hook for topic

User says: "I want to write about <topic>. Give me a better hook."
Generate 3 strong hook candidates across the 5 archetypes, recommend
the strongest.

## References

- `../../founder-brand/SKILL.md` — the full framework + voice rubric
- The **Founder-Brand Compounding** course:
