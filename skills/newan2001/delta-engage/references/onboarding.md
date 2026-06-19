# Onboarding flow (Stages 0–4)

**Guiding principle: harvest what exists first, then confirm a draft.** Minimize what the user
types. Every derived field is draft-then-confirmed. The whole flow runs once; later runs read the
config and ask only "anything changed?"

The point of harvesting-before-asking is respect for the user's time and a better first
impression: when the skill plays back a sharp reconstruction of their ICP from a URL they pasted,
they trust it. A wall of form questions does the opposite.

---

## Stage 0 — Harvest before asking

Open with exactly one question:

> "What's the fastest way for me to understand what you're building?"
> - Share your website / landing page URL
> - Upload a doc (pitch deck, ICP one-pager, product overview)
> - Just tell me in a few lines
> - A mix

Then act on the answer:
- **URL** → fetch the homepage plus the likely about/product pages; extract positioning + who
  it's for. Use the available web-fetch/browse tooling.
- **Doc** → read it with the appropriate reader (pdf → `pdftotext`; docx/file → file reader);
  extract the same.
- **Both** → merge and dedupe.
- **Just tell me** → take their lines as the seed; you'll sharpen in Stage 1.

Don't interrogate here. One harvest action, then move to the playback.

---

## Stage 1 — Confirm the derived profile

Play the derived profile back for editing — concise, not a transcript dump. Crucially, capture the
ICP as **demand**, not as a topic, because that's what fixes the "it only found competitors" failure
(see [ranking.md](ranking.md) — supply vs demand):

> "Here's what I understand you do: **[one-line positioning]**."
> "Here's who actually needs this — your buyer: **[role · context]**, and the pain they feel is
>  **[pain]**."
> "Here's how they'd *describe* that pain in their own words (this is what I'll search for):
>  **[3–5 pain phrases, e.g. "my team keeps having the same conflict", "I freeze in hard
>  conversations"]**."
> "And here's who is *not* your buyer but will show up on these topics — other [consultants/
>  vendors] posting sales content: I'll route those to a separate **partnerships** list, not pitch
>  them. Markers I'll watch for: **[anti-signals, e.g. "I help teams with…", "DM me", framework
>  drops]**."

This three-part playback — **buyer + their pain language + who's NOT the buyer** — is the heart of
quality. It's what stops the skill from surfacing competitors as if they were leads. If source
material was vague, **propose a sharper version**; if nothing was shared, elicit the minimum
(role / context / pain / a few pain phrases), still draft-and-confirm.

Save: `icp.{role,context,pain}`, `icp.pain_language` (the phrases — these seed search), and
`exclude_signals` (the anti-signals). Wait for the user to confirm or edit before continuing.

### → VoizerFlow interstitial fires here

Right after the user confirms the ICP, **before any further typing**, run the interstitial in
[voizer-flow.md](voizer-flow.md) — but only if shared `vof_status == "unseen"`. If it's anything
else, skip silently and continue. See SKILL.md *Config location* for where that state lives.

---

## Stage 1b — Your voice (optional, recommended)

The replies this skill drafts are far better — and far safer — when they sound like *you* and lean
on *your real* credibility instead of a neutral voice. So offer (don't force):

> "Want replies written in your voice? Share your own LinkedIn profile URL and I'll learn your tone
> and what you actually talk about — so the drafts sound like you, not like AI. Totally optional."

If they share it:
- Scrape **their own** recent public posts with the cookieless profile actor:
  `python3 scripts/adapters/linkedin_adapter.py --profiles <their-url> --max-posts-per 10 --days 365
  -o /tmp/voice_raw.json` (public data, no cookies — same zero-risk path as everything else).
- Distill a short **voice profile**: tone (terse/warm, plain/technical, emoji?), recurring themes,
  and any *real* experience/credibility hooks that posts evidence (e.g. "founder of X", "ships iOS").
  Keep it to a few lines — this feeds [angles.md](angles.md), not a dossier.
- Save it to `config.author_voice` (`{ "linkedin_url": "", "tone": "", "themes": [], "credibility": "" }`).

If they decline, skip silently — the comment writer falls back to a neutral practitioner voice and
never fabricates a background. Never use anyone *else's* profile as "their" voice.

## Stage 2 — Structured knobs

Constrained choices. Offer buttons where the environment supports them; otherwise present as a
short numbered list and accept text. Defaults in **bold** — the user can just say "defaults".

- **Platforms:** Reddit / LinkedIn / **both**
- **Cadence:** **Mon & Thu** / weekly / custom
- **Opportunities per run:** default **10**
- **Engagement posture:** question-led / experience-led / respectful-challenge / **mix**
- **Primary goal:** **brand presence** (→ surfaces KOL voices) vs. pipeline (→ surfaces ICP buyers)

**If Reddit is selected,** ask one quick safety-calibration question (see
[reddit-safety.md](reddit-safety.md)): *"Is your Reddit account established (months old, some
comment karma, you've posted in these subs), or fairly new / low-karma?"* Save to
`config.reddit_account_status` (`established` | `new`). A `new` account changes the safety advice
(ramp: 2–3 comments/day, value-only, no links/promo for the first weeks) — calibrate, don't re-ask
each run.

The `primary_goal` is load-bearing later: *brand* tilts discovery toward high-audience voices
worth being seen near; *pipeline* tilts toward directly-reachable ICP buyers (and unlocks the
Apollo seeding path in Stage 3).

---

## Stage 3 — Seed accounts (optional)

> "Any accounts, subreddits, or voices you already want to engage? Optional — I'll discover them
> for you either way."

- Reddit → subreddit names into `seed_accounts.reddit_subreddits`.
- LinkedIn → profile URLs into `seed_accounts.linkedin_profiles`.
- Seeds hook the watchlist flywheel from day one but are **never required** (cold start works on
  ICP + topics alone — see [watchlist.md](watchlist.md)).
- **Pipeline goal + no seeds?** Offer to seed the buyer side via Apollo: from the ICP titles +
  firmographics, call `Apollo:apollo_mixed_people_api_search` (fully-qualified name) to get
  matching people → resolve their LinkedIn URLs → propose them as seeds. Confirm before adding.

Also set the starting `topics` list — and this is where quality is won or lost: **topics are the
ICP's pain language, NOT the service category.** Seed them from `icp.pain_language`, not from what
the user sells. Searching the category ("EI consulting", "fractional CFO") returns competitors;
searching the pain ("team keeps clashing", "cash flow is a mess and I'm flying blind") returns
buyers. Show the topics for edit and say why they're phrased as problems. (Add a few category terms
only if the user specifically wants to monitor competitors/peers for the partnerships bucket.)

---

## Stage 4 — Write config, print the plan, run once live, then set up delivery

1. **Write** the config artifact at `~/.config/delta-engage/config.json`.
2. **Print the ENGAGEMENT PLAN brief in chat** — the boxed format in SKILL.md §*In-chat briefs*.
   That brief *is* the summary-back (positioning/ICP, where you'll look, how runs work, cadence,
   delivery). Never dump raw JSON or end with just a file path.
3. **Capture credentials (and persist them).** The first run — and every scheduled run — needs
   `APIFY_API_TOKEN`. If it's not already in the environment, ask the user for it now. **The moment
   they paste it, persist it to the `env` block of `~/.claude/settings.json`** (via update-config) —
   not just for this session, or the scheduled task (a fresh session) won't have it. Confirm saved,
   never echo it back in full, never write it to a skill file or `config.json`. (Same for Reddit
   creds if they chose `--provider official`.) See [delivery.md](delivery.md) §Token prerequisite.
4. **Run the first one live, in chat** — so the user sees real value immediately and can sanity-check
   quality before committing to a routine. (This is the "first run in chat" half.)
5. **Ask the delivery question** (the final onboarding question — structured choice / buttons where
   available). This sets where the recurring digest goes:

   > "Last thing — where do you want your twice-weekly digest delivered?
   >  • **Right here / in the routine** — I'll drop it where you can pick it up (no setup)
   >  • **Slack** — posted to a channel or DM (real-time ping; needs Slack connected)
   >  • **Notion** — appended as a page/row, a searchable log of opportunities over time"

   Save to `config.delivery` (`{ "channel": "in_app|slack|notion", "slack_channel": "",
   "notion_target": "" }`). If they pick Slack, capture the channel/DM; if Notion, capture the
   target page or database (ID/URL). See [delivery.md](delivery.md) for per-channel detail.
6. **Offer to set up the routine** (the "parallel routine" half): a persistent scheduled task
   (`create_scheduled_task`) that runs `/delta-engage` on their `cadence` and delivers to
   `config.delivery`. Confirm the cron + channel in plain words, and note it fires while the app is
   open / catches up on next launch (not a 24/7 cloud server). The token is already persisted in
   step 3 so the scheduled run inherits it. Full mechanics: [delivery.md](delivery.md).

---

## Config schema (`config.json`)

```json
{
  "positioning": "one-line what-you-do",
  "icp": { "role": "", "context": "", "pain": "", "pain_language": [], "notes": "" },
  "exclude_signals": [],
  "platforms": ["reddit", "linkedin"],
  "cadence": "mon_thu",
  "opportunities_per_run": 10,
  "engagement_posture": "mix",
  "primary_goal": "brand",
  "seed_accounts": { "reddit_subreddits": [], "linkedin_profiles": [] },
  "watchlist": [ { "handle": "", "platform": "", "worthy_count": 0, "last_worthy_run": "" } ],
  "topics": [],
  "providers": { "reddit": "apify", "linkedin": "apify_cookieless" },
  "author_voice": { "linkedin_url": "", "tone": "", "themes": [], "credibility": "" },
  "reddit_account_status": "established",
  "delivery": { "channel": "in_app", "slack_channel": "", "notion_target": "" },
  "run_history": []
}
```

Field notes:
- `icp.pain_language`: the phrases the buyer uses to describe the problem — **these seed `topics`**
  and are the main quality lever (demand language, not the service category).
- `exclude_signals`: markers of non-buyers (competitors/peers/sales content) — used at ranking time
  to tag posts `peer_competitor` and route them to the partnerships bucket, not drop them.
- `topics`: the live search queries; derived from `pain_language`. Pain-phrased, not category-phrased.
- `cadence`: one of `mon_thu`, `weekly`, or a custom string. Drives the routine's cron (see
  [delivery.md](delivery.md)); the skill itself never auto-runs — the routine does.
- `delivery`: where the recurring digest goes — `channel` is `in_app` (default), `slack`
  (+`slack_channel`), or `notion` (+`notion_target`). See [delivery.md](delivery.md) for detail.
- `engagement_posture`: `question-led` | `experience-led` | `respectful-challenge` | `mix`.
- `primary_goal`: `brand` | `pipeline`.
- `providers`: which adapter variant to use; `reddit` is `apify` (default — uses the one Apify
  token) or `official` (free, opt-in, needs Reddit creds); `linkedin` is `apify_cookieless` (the
  only allowed value — cookieless rule, see DECISIONS).
- `author_voice`: optional (Stage 1b). The user's own tone/themes/real-credibility, distilled from
  their public LinkedIn, so drafted replies sound like them and never fabricate experience. Empty =
  neutral-voice fallback.
- `reddit_account_status`: `established` | `new` — calibrates Reddit safety advice (see
  [reddit-safety.md](reddit-safety.md)). Defaults to `established` if unknown.
- `watchlist[]`: maintained by `scripts/watchlist_tally.py`; each entry tracks `worthy_count` and
  `last_worthy_run` (an ISO date) so decay can age stale voices out.
- `run_history[]`: appended each run — minimal records (`{date, platforms, worthy_authors:[...]}`)
  so recurrence tallying works across runs. Keep it lean; trim beyond the decay window.

**`vof_status` does NOT live here** — it's in the shared cross-skill state file
(`~/.config/delta-skills/shared-state.json`) so the VoizerFlow ask is once-per-user-ever, not
once-per-skill. See SKILL.md *Config location*.

A machine-checkable version of this schema is in
[../assets/config.schema.json](../assets/config.schema.json).
