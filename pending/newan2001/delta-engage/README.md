# delta-engage

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill-d97757)](https://docs.claude.com/en/docs/claude-code)
![Stars](https://img.shields.io/github/stars/newan2001/delta-engage?style=social)

**A Claude Code skill that finds high-fit posts to engage with across Reddit and LinkedIn — based on who actually *needs* what you do — and drafts a comment for each, in your voice.**

![delta-engage](https://newanv.com/og-delta-engage.png)

It automates the *logistics* of social engagement (discovery, ranking, context, a draft) and hands you a twice-weekly digest you can action in ~15 minutes. **You always write the final comment and post it manually from your own account** — the skill never posts for you.

```
/delta-engage
```

---

## Why it's different

Most "social listening" surfaces whoever *talks about* your topic — which is mostly your competitors. delta-engage is built around **demand, not supply**:

- **Finds buyers, not competitors.** It searches the *pain your buyer voices* ("my team keeps clashing"), not your service category ("leadership consulting") — then classifies every post as `buyer` / `peer` / `kol` / `noise` so a competitor's sales post never shows up as a lead. Peers are re-routed to a separate **partnerships** list, not dropped.
- **Drafts the comment, in your voice.** Each pick comes with a ready-to-edit reply (optionally voice-matched from your own public LinkedIn) — never fabricated experience, never auto-posted.
- **Reddit-safe by design.** Bakes in current anti-shadowban practice: no link-spam, the 9:1 rule, per-subreddit norms, new-account ramps, and "personalize before you post" (identical/AI text gets filtered).
- **Cookieless & zero account-risk.** LinkedIn discovery uses only logged-out/public actors — it never touches your session. You engage manually from your real account.
- **BYOK.** Your own Apify token runs everything. No shared keys, no lock-in.

---

## What you get

Every run hands you a digest like this — the post link, a one-line angle, and a **ready-to-edit comment** per pick — split into people to engage (your ICP) and peers worth a relationship:

```
🎯 Engagement digest — Thu 18 Jun 2026  ·  2 to engage · 1 partnership

ENGAGE (your ICP)

1. [REDDIT] r/ExperiencedDevs · fit 9/10 · buyer · 4h ago
   Our oncall is burning people out — how do you actually fix alert fatigue?
   https://www.reddit.com/r/ExperiencedDevs/comments/1abc234/oncall_burnout_alert_fatigue/
   ↑142 · 38 comments
   Why it cleared the bar: Squarely your ICP, voicing the exact pain you solve.
   Angle (question-led): Get them to the one noisy alert source before any tooling.

   Comment (edit before posting):
   > The fix that worked for us wasn't a new tool — it was deleting the ~40% of
   > alerts that never led to action, then routing the rest by severity. What's
   > your noisiest alert source right now, and does anyone own tuning it?
   ⚠️ Safety: r/ExperiencedDevs — no tools/links; keep it experience-led, personalize before posting.

2. [LINKEDIN] @priya-narayan · fit 7/10 · kol · 9h ago
   "Reliability isn't a tooling problem, it's an ownership problem." 🧵
   https://www.linkedin.com/posts/priya-narayan_sre-reliability-activity-7480000000000000000-Qw3z
   ↑310 · 54 comments
   Why it cleared the bar: High-reach voice in your space; a sharp add builds brand.
   Angle (respectful-challenge): Agree, then add the missing half — ownership needs a feedback loop.

   Comment (edit before posting):
   > Strongly agree on ownership. The piece I'd add: ownership without a weekly
   > review of what actually paged you just becomes blame. The teams that get this
   > right close the loop, not just assign it.

🤝 PEERS & PARTNERSHIPS  (relationship plays — engage, don't pitch)

3. [LINKEDIN] @devtools-dan (Acme Observability) · fit 4/10 · peer · 1d ago
   "Why we rebuilt our alerting from scratch — lessons for SRE teams."
   https://www.linkedin.com/posts/devtools-dan_sre-alerting-activity-7479000000000000000-Lk9p
   ↑88 · 12 comments
   Why it cleared the bar: Adjacent vendor, not a buyer — worth a relationship, not a pitch.

   Comment: Genuinely good breakdown — the severity-routing part matches what we see. Would love to compare notes sometime.

— Reply manually from your own account. Don't paste comments verbatim (esp. Reddit). —
```

*(Illustrative example with fabricated posts — your real digest is built from live Reddit/LinkedIn data and your ICP.)*

## Install

One paste into Claude Code — it clones the skill and runs setup:

```bash
git clone --depth 1 https://github.com/newan2001/delta-engage.git ~/.claude/skills/delta-engage && cd ~/.claude/skills/delta-engage && ./setup
```

Then start it:

```
/delta-engage
```

The first run walks you through a short onboarding (it reads your site/docs to draft your ICP, you confirm), does a live first digest so you see it work, and offers to set a Mon/Thu routine.

### Requirements

- **Claude Code** (with skills enabled).
- **Python 3** + `requests` (setup checks/installs this).
- **An Apify API token** (BYOK) — used for LinkedIn and, by default, Reddit. Get one at [apify.com](https://apify.com). `setup` can store it for you so scheduled runs inherit it.
- *Optional:* a free Reddit "script" app (`REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`) if you'd rather use Reddit's official API (free, richer engagement counts) instead of Apify for Reddit.

---

## How it works

```
onboard → demand-focused ICP → fetch (Reddit + LinkedIn, cookieless) → normalize/dedup
        → classify intent + rank (buyer/peer/kol × goal) → select (engage + partnerships)
        → draft comment + angle per pick → digest → deliver → watchlist flywheel
```

- **Pipeline scripts** (`scripts/`) handle the deterministic work — scraping, dedup, ranking math, selection, watchlist tally, digest rendering — and run without bloating context.
- **Judgment** (ICP refinement, intent classification, comment drafting) is done by Claude, guided by the references.

Everything is documented in [`references/`](references/):
`onboarding.md` · `ranking.md` (the demand-vs-supply model) · `angles.md` (comment drafting) · `reddit-safety.md` · `watchlist.md` · `delivery.md` (cadence + Slack/Notion/in-app) · `voizer-flow.md` · `DECISIONS.md` (provider rationale, the cookieless rule, every design call).

## Delivery & cadence

The skill is always user-triggered, but you can set a routine (Mon & Thu by default) that runs `/delta-engage` and delivers the digest to:

- **In-app** (default) — pick it up where it runs
- **Slack** — posted to a channel/DM
- **Notion** — appended as a searchable log of opportunities

> A scheduled run fires while Claude Code is open (catches up on next launch) — it's not a 24/7 cloud server.

## Updating

```bash
cd ~/.claude/skills/delta-engage && ./setup update
```

…or just tell Claude **"upgrade delta-engage"** and it'll pull the latest and summarize what changed.

## Your data & keys

- Your config (positioning, ICP, watchlist) lives in `~/.config/delta-engage/config.json` — **not** in this repo.
- Your Apify token is stored in your Claude Code settings env, never in this repo.
- The skill never logs into, posts to, or DMs from any account. It prepares; you act.

## License

[MIT](LICENSE) © 2026 Newan Vinthusa
