# Ranking rubric — intent first, then fit, then engagement potential

A post earns its place on **three** things now, in this order. The first is the fix for the most
common failure mode: surfacing competitors and sales content instead of real buyers.

```
1. intent     (you classify: buyer | peer_competitor | kol | noise)
2. fit_score  (you, 0–10 — conditioned on intent AND the user's goal)
3. engagement_potential  (scripts/rank.py, 0–1 — recency/velocity/headroom/reach)

final_score = fit_score × engagement_potential   (rank.py)
```

## Why intent comes first — supply vs demand

Keyword search returns whatever is **published** about a topic, and what's published skews
**supply-side**: other practitioners, agencies, and marketers *broadcasting* sales/thought-leadership
content. The people who actually **need** the service (demand-side) rarely name it — they voice the
**pain**. Example (EI / leadership consulting):

- ❌ *supply / peer:* "5 ways emotional intelligence transforms teams 🧵 — DM me to work together."
  (another consultant; matches keywords; **not a buyer**)
- ✅ *demand / buyer:* "My team keeps having the same conflict and I don't know how to get through to
  them." (the actual ICP, voicing the pain — **this is who to engage**)

If a run returns mostly people who *talk about* the service, that's this failure. The discovery fix
is searching the **pain language**, not the category (see onboarding). The ranking fix is classifying
intent so topical-match alone never wins.

## Step 1 — Classify intent (you, per post)

Read the post and tag one `intent`:

- **`buyer`** — voicing the problem, asking for help, comparing options, venting the exact pain the
  user's offer addresses. First-person situation, a question, no service being sold. **This is the
  real ICP demand signal.** Tells: "how do I/we…", "struggling with…", "any advice on…", "we keep…".
- **`peer_competitor`** — offering the same/similar service or broadcasting expertise/sales content.
  Same keywords, opposite intent. Tells: "I help [X] do [Y]", "DM me / book a call / link in bio",
  framework drops, credentials-forward thought-leadership. **Not a buyer — route to partnerships.**
- **`kol`** — a large-audience voice in the space (not necessarily a buyer or a direct competitor)
  worth being seen near. Valuable for brand.
- **`noise`** — off-topic, spam, job listings, pure broadcast with no opening to add value.

Write the tag onto each signal as `"intent": "..."`. When genuinely ambiguous (e.g. a buyer who's
also a light practitioner), prefer `buyer` if there's a real pain to help with.

## Step 2 — Fit score (you, 0–10) — conditioned on intent AND goal

Fit is *"how well does engaging here serve this user,"* not *"how on-topic is it."* Weight by intent
and the configured `primary_goal`:

| intent | goal = pipeline | goal = brand |
|---|---|---|
| **buyer** | **8–10** — your person, real pain, a helpful comment lands | 5–7 — good, but brand wants reach |
| **kol** | 4–6 — reach, not a direct buyer | **8–10** — being seen adding value here builds brand |
| **peer_competitor** | **2–4 as a *sales* target, but tag `bucket: partnership`** — engage to build a relationship/collab, never to pitch | 3–5 + `bucket: partnership` |
| **noise** | 0–1 — drop | 0–1 — drop |

Within a band, reward posts that are *recent, discussion-inviting, and where a thoughtful comment is
genuinely welcome*. Be honest about "would my comment add value here, or would it read as trawling?"
— if the only way in is a pitch, it's not a fit.

**Peers are not discarded.** Set `fit_score` modestly and add `"bucket": "partnership"` — the digest
surfaces them in a separate *Peers & partnerships* section so the user can start collabs and
conversations, exactly the relationship angle they're worth. Everything else is `"bucket": "engage"`.

Write `fit_score`, `intent`, and `bucket` onto each signal before running `rank.py`.

## Step 3 — Engagement potential (the script computes this, 0–1)

`rank.py` derives this deterministically so it's consistent and you don't spend judgment on
arithmetic: **recency** (steep decay — stale threads are wasted), **discussion velocity**
(comments/age — is it live?), **headroom** (a slight penalty for 100s-of-comments pile-ons; a rising
thread with a handful is the sweet spot), and **platform-normalized reach** (Reddit upvotes ≠
LinkedIn reactions). You don't compute these — the lever you control is `fit_score`/`intent`.

> Platform note: **Reddit skews demand** (people post problems in communities) — your best *buyer*
> signal. **LinkedIn skews supply** (people broadcast/sell) — expect more `peer`/`kol` there; it's
> stronger for partnerships, KOL proximity, and reaching buyers via *their* engagement than for raw
> buyer pain. Set the user's expectations accordingly.

## Output

`rank.py` writes `ranked.json` sorted by `final_score`, carrying your `intent`/`bucket` tags through.
`select.py` then fills the **engage** bucket (buyers/KOLs per goal) and reserves a few slots for the
**partnership** bucket so peers surface without crowding out real ICP. You write the human-facing
"why this cleared the bar" per pick at reply time — one honest sentence on the *intent* and the ICP
tie, not a restatement of the math.
