# Engagement replies — draft comment + angle, per pick

For each selected post you produce **two things**:

1. **A draft comment** — a genuinely good, ready-to-use reply the user could post with light edits.
2. **The angle** — the one-line strategy behind it (why this works here), so the user understands
   the move and can adapt it.

This is a deliberate evolution from "direction only": the user wants an optimized reply in hand,
not just a prompt to write one themselves. **But the draft is a starting point the human edits and
posts manually from their own account — never auto-posted, never pasted verbatim.** That last part
isn't just etiquette: on Reddit, identical/AI-sounding comments are an active ban vector (see
[reddit-safety.md](reddit-safety.md)), so personalization is a safety requirement, not a nicety.

## The non-negotiables for every draft

- **No fabricated experience or facts.** Never invent that the user "did X at their last company,"
  "saw this with a client," or any stat/result. If a strong reply needs lived experience, either
  (a) draw on the user's **real** background if you have it (their voice profile / positioning —
  see below), or (b) write the reply as a sharp question or a generalizable observation that needs
  no personal claim. When in doubt, ask, don't assert.
- **Sound human, not like AI.** Reddit (and increasingly LinkedIn) flag generic AI prose. Avoid the
  tells: "Great post!", "I completely agree", em-dash-stuffed balance ("not just X, but Y"),
  hedging throat-clearing, listicles where a sentence would do, and over-polished symmetry. Write
  the way a real, slightly-opinionated practitioner types: specific, a little informal, one clear
  point. Short and real beats long and smooth.
- **Lead with value, not the product.** Most good replies never mention the user's product. Mention
  it only if it is genuinely the most helpful answer, and even then as a brief aside with
  disclosure — never a pitch. On Reddit this is also a hard ban-risk line (the ~10% rule).
- **Match the platform norm and the configured `engagement_posture`** (`question-led`,
  `experience-led`, `respectful-challenge`, or `mix` → pick the best fit per post).
- **Voice-match the user.** If a voice profile exists (from their own LinkedIn / positioning —
  onboarding Stage 1b), lean into their real tone, vocabulary, and credibility. Without it, default
  to plain, specific, lightly opinionated.

## Using the user's voice profile (if present)

When `config.author_voice` exists (the user opted to share their own LinkedIn), use it to:
- **Match tone** — terse vs. warm, plainspoken vs. technical, emoji or none.
- **Borrow real credibility** — reference their *actual* role/experience where it strengthens the
  reply ("having built X…" only if their profile genuinely supports it). This is how we add
  authority without fabricating.
- **Stay on-theme** — echo the topics they actually post about, so engagement compounds their brand.

If no voice profile, never invent one — write in a neutral-practitioner voice and lean on the
question/observation framing.

## Posture playbook

- **Question-led** — ask the one sharp question that advances the thread. Best when the author is
  exploring/comparing. Lowest risk. *"What made you rule out X — latency or cost?"*
- **Experience-led** — offer a specific, generalizable lesson. Requires real experience (see the
  no-fabrication rule; use the voice profile). Frame as "here's a pattern that worked," not a pitch.
- **Respectful-challenge** — surface a non-obvious counterpoint, generously, *with a reason*. Highest
  reward and risk; never contrarian for attention. *"Counterintuitively the bottleneck's usually
  onboarding, not the model — here's why."*

## Per-platform norms

**Reddit** — community-first, allergic to marketing, AI-text-sensitive. Value-dense, peer-to-peer,
4–8 sentences with a concrete example/number/tradeoff. Lead with substance, never credentials or a
link. A product mention is tolerable *only* if it directly answers the question and is disclosed —
and most subs restrict even that. **Before drafting a Reddit reply, apply
[reddit-safety.md](reddit-safety.md)** (subreddit rules, account readiness, the 9:1 rule, no-link
default, personalize-before-posting). The draft must read like a real community member wrote it.

**LinkedIn** — identity-attached, reciprocal, visible to the author's network (that visibility *is*
the value). 2–3 warm, substantive sentences that add a distinct point beat a long comment. A
concrete example or a genuine question lands. Because discovery is cookieless and the user posts
from their real account, the draft must suit *their name* being on it publicly.

**X (if enabled)** — terse, one sharp idea or a real question. Verbosity dies.

## Output shape (per pick) — what goes in the digest

```
**[Platform] — [author or subreddit]** · fit N/10 · [recency]
[post title / first line]  ·  <url>
Why it cleared the bar: [one honest sentence tying it to the ICP]
Angle ([posture]): [the one-line strategy]

Comment (edit before posting): "[the ready-to-use reply, in the user's voice, no fabrication]"
[Reddit only] ⚠️ Safety: [sub-specific note — e.g. "r/X bans links; personalize this, don't paste"]
```

Keep each pick skimmable; the whole digest should be actionable in ~15 minutes. The draft saves the
user the blank-page problem; the angle + safety note make sure they post something that's *theirs*
and won't get them filtered.

**The `<url>` must be the full post URL — never truncated.** LinkedIn links only resolve with their
`…-activity-<id>-…` tail; a character cap silently breaks them. Use `[view post](FULL_URL)` if you
want short visible text, but keep the whole href.
