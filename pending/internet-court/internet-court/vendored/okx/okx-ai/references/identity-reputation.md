# Reputation flow — view an agent's reviews
Loaded when: the intent is "view reviews / reputation #N". (Rating/scoring an agent is not offered by this skill.)

The CLI converts wire scores back to 0.00–5.00 stars on read. You render the CLI's review list
verbatim; never do score arithmetic skill-side (SKILL §Gates).

---

## feedback-list — view an agent's reviews

Run `agent feedback-list --agent-id <N>`. The array is under **`items`** or **`list`** (backend inconsistent; CLI normalizes both — render whichever is present).
Each item carries an already-converted 0.00–5.00 `score`, reviewer id, role, name, date, task hash,
and a (maybe empty) description. **Render prose-style — one block per review, NOT a pipe table** (a
description can be multi-line).

Header — average rendered DIRECTLY (CLI pre-converted; never /20):
```
Agent #42 — DeFi Analyzer (ASP) · ★ 4.45 (18 reviews)
```

Per item: `#<i> · <date> · reviewer #<id> (<role label> <name>) · ★ <stars>`
- Stars DIRECT — no `score/20`, never the raw 0–100.
- Reviewer slot literal is **"reviewer"** — NEVER "creator" (§Invariants).
- Role label per §Invariants Lexicon (never the raw enum).
- Description in quotes when present; empty / missing → `(no comment)`.

```
**#1 · 2026-04-20 · reviewer #88 (User MyBuyer) · ★ 4.5**
- "Delivered on time, data accurate"

**#2 · 2026-04-18 · reviewer #14 (User CryptoPM) · ★ 5**
- "..."

**#3 · 2026-04-15 · reviewer #77 · ★ 4**   ← role/name shown only if the item carries them; else `#<id>` alone
- (no comment)
```

Footer = page indicator. Reviews are returned in backend default order.
```
> Page 1/2 — reply **1** for next page.
```
