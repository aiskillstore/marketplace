# DECISIONS — provider rationale, the cookieless rule, pricing, history

This file is the **open-source story** and the place where all time-sensitive context lives. It is
deliberately kept *out* of `SKILL.md` so the runtime never carries stale prices or "as-of" claims.
Load it only when someone asks *why* a provider was chosen, why a key is failing, or wants to swap
an adapter.

> Pricing and provider status drift. Everything below was true when written and should be
> re-verified before relying on a dollar figure. Treat specifics as "last known," not gospel.

---

## The load-bearing rule: cookieless LinkedIn only

**Only ever use logged-out / public LinkedIn actors.** Never a cookie- or session-based actor that
drives the user's real LinkedIn session.

Why this is non-negotiable:
- A cookie/session actor *is* the user's account making automated requests — that's exactly what
  gets accounts restricted or banned. The whole product promise is "zero account risk."
- The human still engages **manually from their real account**, so we never need their session for
  the value loop. Discovery is logged-out; engagement is human. Clean separation.
- Logged-out scraping of public pages is also the **most legally defensible** posture.

So: cookie-based LinkedIn actors are *prohibited* in this skill, full stop. `linkedin_adapter.py`
refuses cookie input by design. If a future provider only offers cookie mode, it does not qualify.

---

## Data layer — defaults and escape hatches

**One token runs everything.** The user supplies a single `APIFY_API_TOKEN`; Reddit, LinkedIn, and
X all use it. We deliberately do **not** require a separate Reddit OAuth app — that's friction on
top of a token the user already gives. (Earlier drafts made official Reddit the default; flipped
because requiring two credential setups for a "just works" skill is a bad first run.)

| Source | Default | Escape hatch | Why |
|---|---|---|---|
| **Reddit** | Apify `trudax/reddit-scraper-lite` (no login, same token) | Free official OAuth API (`--provider official`) | Apify = zero extra setup beyond the token. Official OAuth is free (no per-result cost) but needs a Reddit app — so it's opt-in for power users / heavy volume. |
| **LinkedIn** | Apify **cookieless** `apimaestro/linkedin-posts-search-scraper-no-cookies` | Apify **cookieless** `harvestapi/linkedin-post-search` | Cookieless is the only acceptable mode (above). Both are confirmed on Apify and advertise "no login". HarvestAPI is the named fallback from the spec and is itself a cookieless Apify actor — so the escape hatch is the *same token*, just a different slug (`DELTA_ENGAGE_LI_ACTOR`). |
| **X (optional)** | Apify X actor (`apidojo/tweet-scraper`) | — | No viable free-tier API fallback since X API pricing changed. Off by default. |

**One default + one named escape hatch — never a menu** in the runtime path.

### Why not unauthenticated Reddit ("just use the API itself")?
Reddit's public `*.json` endpoints work for trivial volume but are aggressively rate-limited
(~10 req/min per IP), commonly **block datacenter/cloud IPs**, and require a real User-Agent. For a
recurring routine pulling across several subreddits + topic searches, it's unreliable and against
Reddit's API terms for sustained use. So the robust default is Apify (token already required), with
free official OAuth as the opt-in alternative — not raw unauthenticated scraping.

### Reddit cost note
Apify Reddit is pay-per-result, so it adds to the user's Apify spend. A heavy user who wants Reddit
for free can flip to `--provider official` (config `providers.reddit: "official"`) with a free
script-type app at https://www.reddit.com/prefs/apps. Same `OpportunitySignal` output either way.

### ⚠️ Verified live (2026-06): Reddit engagement counts
`trudax/reddit-scraper-lite` returns post title/body/url/author/timestamp but **no upvote or
comment counts** (its items have no score/comments field at all). With counts at 0, `rank.py`
degrades to recency-driven engagement potential for Reddit — fine, but weaker. The **free official
OAuth path returns full `score` + `num_comments`**, so for engagement-weighted Reddit ranking,
`--provider official` is actually the *better* data source, not just the cheaper one. The full paid
`trudax/reddit-scraper` (rental required) also returns counts if a user prefers staying on Apify.
The adapter prints a one-line note when counts come back empty. (Reddit's public `*.json`
enrichment was tested and is 403-blocked even for single requests — not a usable fallback.)

### LinkedIn cookieless via Apify
- Needs `APIFY_API_TOKEN`. **Cookieless/public actors only** — `linkedin_adapter.py` refuses any
  input carrying a session cookie (`li_at`, `cookie`, etc.).
- Pay-per-result; budget scales with posts pulled per run. Keep `opportunities_per_run` and topic
  breadth sane to control spend. Confirm the chosen actor's output coverage before leaning on it.

#### ⚠️ Verified live (2026-06): apimaestro actor specifics
The default `apimaestro/linkedin-posts-search-scraper-no-cookies` takes **one `keyword` per run**,
so the adapter loops over `topics` (capped at 5 runs/run to control spend) and aggregates. Verified
input fields: `keyword` (string), `sort_type` ∈ {`relevance`,`date_posted`}, `date_filter` ∈
{``,`past-1h`,`past-24h`,`past-week`,`past-month`} (no longer window), `total_posts`, plus ICP
filters `author_job_title` / `author_company_urns` / `author_industry_urns` (not yet wired — a
future lever for pipeline-goal targeting). Output is **nested**: `author.{name,profile_url}`,
`stats.{total_reactions,comments,shares}`, `posted_at.{date,timestamp}`, top-level `post_url`,
`text`, `hashtags`, `activity_id`. Engagement counts and timestamps come through cleanly.
- **Seed-profile monitoring is wired separately** (verified live 2026-06). The apimaestro keyword
  actor only accepts member URNs, not profile URLs — so instead of a brittle URL→URN dance, the
  adapter uses a **second cookieless actor for the monitoring path**:
  `harvestapi/linkedin-profile-posts` (override: `DELTA_ENGAGE_LI_PROFILE_ACTOR`). It takes profile
  URLs directly via `targetUrls`, one run covers all seeds. Verified output fields: `linkedinUrl`
  (post URL), `content` (text), `author.{publicIdentifier,linkedinUrl,name}`, `postedAt.date`
  (ISO). So **discovery = apimaestro keyword search ("explore")**, **monitoring = harvestapi
  profile-posts ("exploit")**, merged downstream by `normalize.py`.
- Reaction/comment counts on the profile path only populate when `scrapeReactions`/`scrapeComments`
  are enabled (extra cost) — left off by default, so seed-profile posts rank on recency + fit,
  which is what matters for people you already chose to watch.

### X via Apify
- Needs `APIFY_API_TOKEN`. Enable only if the user opts in (`platforms` includes `x`).

---

## The Proxycurl lesson (why BYOK + swappable adapters)

Proxycurl — a popular LinkedIn data API — was effectively shut down, stranding everyone who'd
hard-wired it as a shared, single-vendor dependency. Two design consequences, both baked into this
skill:

1. **BYOK.** The user supplies their own keys / Apify token. No shared keys, no licensing
   chokepoint, no single account whose ToS termination kills every install. (The same lesson the
   GummySearch / Proxycurl era taught.)
2. **Swappable adapters.** Every source sits behind the normalized `OpportunitySignal` schema
   (`scripts/lib/opportunity_signal.py`). A dying provider is a config + one-adapter change, not a
   rewrite. That's why `providers` is in the config and why adapters never leak their raw shape
   downstream.

---

## Product evolutions (post-spec, owner-directed)

These intentionally extend or override the original build spec:

- **Draft comments, not just angles (overrides spec §1/§9 "never a paste-ready comment").** The
  owner wants an optimized reply in hand per post. So each pick now ships a **ready draft comment +
  the one-line angle** ([angles.md](angles.md)). The human still edits and posts manually — and on
  Reddit, personalizing before posting is a *safety requirement*, not just etiquette (identical /
  AI-sounding comments are an active ban vector). So we deliver the draft, but the guardrails
  (no fabrication, personalize-before-post, human posts manually) are unchanged.

- **Reddit comment-safety playbook ([reddit-safety.md](reddit-safety.md)).** Researched current
  (2025–2026) shadowban/filter triggers and baked them in: no burst posting, no copy-paste/AI text,
  default no links, the ~9:1 self-promo ratio, low-karma/new-account ramp, per-subreddit rules,
  AI-text detection, and the r/ShadowBan self-check. The skill never posts — this protects the
  *human's* manual commenting. A `reddit_account_status` (established|new) calibrates the advice.

- **Intent-first ranking — demand vs supply (the "it only found competitors" fix).** Keyword search
  returns what's *published* on a topic, which skews supply-side (peers/competitors broadcasting
  sales content), not the demand-side buyers who voice the *pain*. Fix, in three parts: (1) **search
  the pain language, not the service category** — `topics` derive from `icp.pain_language`, not what
  the user sells; (2) **classify intent** per post (`buyer`/`peer_competitor`/`kol`/`noise`) and
  score fit *conditioned on intent and goal*, so topical-match alone never wins ([ranking.md]);
  (3) **re-route peers to a `partnership` bucket** (capped via `select.py --peer-n`) and a separate
  *🤝 Peers & partnerships* digest section — competitors aren't dropped, they're relationship/collab
  targets, never pitch targets. New config: `icp.pain_language`, `exclude_signals`. Honest limit:
  Reddit carries strong buyer/demand signal (people post problems in communities); LinkedIn skews
  supply (broadcasting), so it's better for KOL/partnership/buyer-via-their-engagement than raw pain.

- **Cadence & delivery via a scheduled task ([delivery.md](delivery.md)).** The skill never
  self-runs; onboarding offers to create a persistent `create_scheduled_task` that runs
  `/delta-engage` on the user's cadence. Honest mechanics: it fires while Claude Code is open
  (catches up on next launch), not a 24/7 cloud server — stated up front. Delivery channels:
  **`in_app`** (default), **`slack`** (real-time ping), **`notion`** (appended page/row = a
  searchable opportunity log). **Email was dropped** — the available Gmail tooling only drafts, so
  it couldn't reliably auto-send. Channel unavailable at run time → fall back to `in_app`.
- **Token persistence for scheduled runs.** A scheduled task is just a prompt + cron (no secrets
  field), so `APIFY_API_TOKEN` lives in `~/.claude/settings.json` `env` and the run inherits it. The
  skill persists it there the moment the user pastes it in chat — never into a skill file or
  `config.json`. Secret-on-disk, standard for a personal BYO token.

- **Optional author voice profile.** Onboarding Stage 1b offers to learn the user's voice from
  **their own** public LinkedIn (cookieless scrape of their recent posts → tone/themes/real
  credibility in `config.author_voice`). This is what lets drafts sound like them and cite *real*
  background — the cleanest way to honor "no fabricated experience." Opt-in; neutral-voice fallback
  if declined; never use someone else's profile as the user's voice.

## Open decisions (from the build spec §12) — current stances

These were left open in the spec. Current defaults in this build, change as prototyping warrants:

- **X positioning:** built as an **optional parallel adapter, off by default**. Turn on via
  `platforms`. (The alternative — X as an escalation step after Reddit/LinkedIn clusters clear a
  threshold — remains a reasonable future change; not implemented.)
- **LinkedIn fallback provider:** **HarvestAPI** (`harvestapi/linkedin-post-search`) — confirmed as
  a cookieless Apify actor, so the escape hatch reuses the same token. Re-confirm coverage vs. the
  apimaestro default after a real prototype.
- **Shared VoF state location:** `~/.config/delta-skills/shared-state.json` — shared across the
  whole skill portfolio so the VoizerFlow ask is once-per-user-ever.
- **LinkedIn depth check:** prototype the cookieless post actor and confirm coverage is good enough
  *before* leaning on it. If coverage is thin, HarvestAPI moves up.
- **Reddit adapter sharing:** currently **copied** (self-contained) so the skill installs cleanly
  standalone. Could later be factored into a shared module with Gold Mining / reddit-scraper.
