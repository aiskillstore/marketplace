# Reddit comment safety — how to engage without getting filtered or banned

This skill never posts for the user — the **human comments manually from their own account**. So
"safety" here means: help the human comment in a way that survives Reddit's spam filters, respects
each subreddit, and never gets their account shadowbanned. A shadowban is silent — Reddit hides
your comments from everyone while you still see them as normal — so prevention is everything.

These are current (2025–2026) community realities, not policy quotes. Apply them when drafting every
Reddit reply and surface the relevant one as the per-pick **⚠️ Safety** note in the digest.

## The ban/shadowban triggers to design around

- **Burst activity.** Real people don't post 30 comments in an hour across 20 subs. Space comments
  out; a twice-weekly routine of a handful of thoughtful comments is naturally safe.
- **Copy-paste / templated / AI-sounding text.** Identical or near-identical comments across threads,
  and generic AI prose, are flagged. Reddit's 2025+ systems actively detect AI-generated content.
  **This is why the draft must be personalized before posting** — never paste the same reply twice.
- **Links.** Outbound links (especially to the user's own domain, or any flagged domain) are the
  single biggest filter trigger. **Default to zero links in comments.** If a link is genuinely the
  most helpful thing, it's usually better to offer it only if asked, or describe it in words.
- **Self-promotion over ~10%.** The community norm (the "9:1 rule"): at least 9 genuinely helpful,
  non-promotional contributions for every 1 that mentions your product. Over-promotion gets accounts
  banned by mods and filters alike. For most picks, the right answer mentions no product at all.
- **Low-karma / brand-new accounts.** Accounts with little karma or history look suspicious.
  Comments from them are more likely to be auto-filtered, and link posts especially.

## Account-readiness check (do this once, in onboarding or first Reddit run)

Ask the user, plainly, where their Reddit account stands — it changes what's safe to recommend:
- **Established** (months old, real comment karma, posts in these subs before) → normal value-first
  commenting is fine; the only ongoing rules are per-subreddit + the 9:1 ratio + no spammy links.
- **New / low-karma / first time in these subs** → advise a ramp: **2–3 comments/day max, no link
  posts, no product mentions** for the first ~2–4 weeks while building a real history. Pure
  value-add comments on active threads. This isn't gaming the system — it's behaving like a genuine
  new community member, which is exactly what avoids false-positive filtering.

Record the answer (e.g. `config.reddit_account_status`) so later runs calibrate the safety notes
without re-asking.

## Per-subreddit rules — always check before recommending a comment

Subreddit rules vary wildly and override everything here:
- Some ban links outright; some require flair, minimum karma, or account age; some allow promotion
  only in a weekly megathread; some auto-remove comments from non-subscribers.
- When you have the post's subreddit, factor its norms into the draft and the ⚠️ Safety note (e.g.
  "r/SaaS: no promo in comments — keep this purely helpful"). If unsure of a sub's rules, default to
  the most conservative: no links, no product mention, pure value.

## Comment craft that survives filters (and actually lands)

- Comment on threads **with existing traction** (≈5+ comments) — your reply gets seen and reads as
  natural participation, not first-comment-on-a-dead-post.
- **4–8 sentences**, adding a concrete example, number, or tradeoff. Substance is both better
  engagement and a weaker spam signal than one-liners.
- Sound like a person: specific, a little informal, one clear point. Avoid the AI tells listed in
  [angles.md](angles.md).
- **Personalize the draft** this skill gives you before posting — change wording, add your own
  detail. Never paste the same text into multiple threads.

## Tell the user how to self-check

If they're worried they've been filtered: post (or check) via **r/ShadowBan** — its bot replies
immediately with their status. Worth mentioning once, especially for newer accounts.

## How this shows up in a run

- Drafting a Reddit reply → apply the triggers above; default no-link, no-promo unless the sub and
  the 9:1 ratio clearly allow it.
- Each Reddit pick's digest line gets a one-line **⚠️ Safety** note: the sub's key rule + "personalize
  before posting."
- If `reddit_account_status` is new/low-karma, prepend a single gentle reminder to the digest about
  the ramp (2–3/day, value-only, no links) rather than repeating it per pick.

Sources behind this guidance: Reddit self-promotion / 9:1 norms and shadowban-trigger write-ups
(KarmaGuy, redship, nodemaven, singlegrain, ReddiReach, 2025–2026). Re-verify periodically — Reddit's
filtering changes.
