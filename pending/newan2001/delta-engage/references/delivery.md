# Cadence & delivery — how the twice-weekly digest reaches the user

The skill never runs itself on a timer. What runs on a schedule is a **scheduled task** whose
action is `/delta-engage`. So cadence + delivery work like this:

> **Reality check on "scheduled":** a scheduled task is a prompt + cron, stored at
> `~/.claude/scheduled-tasks/<id>/SKILL.md`. It fires **while Claude Code is open**; if the app is
> closed when it's due, it runs on next launch (catch-up), not in the cloud while the user is away.
> Use the persistent `create_scheduled_task` (not the 7-day-expiring `CronCreate`). Tell the user
> this so a missed-while-closed run isn't a surprise — for true always-on delivery they'd keep the
> app running or trigger manually.

```
onboard  →  first run LIVE in chat (user sees value)  →  set up a ROUTINE
            routine fires on the user's cadence (e.g. Mon & Thu)  →  delivers the digest
            to config.delivery.channel  →  user actions it in ~15 min
```

## Setting up the routine (do this at onboarding close, after the first live run)

Use the **`/schedule`** capability to create a recurring routine:
- **Action:** run `/delta-engage` (it reads `config.json` for platforms, topics, and delivery).
- **Cron** from `config.cadence`:
  - `mon_thu` → e.g. `0 8 * * 1,5` (Mon & Thu 08:00 user-local)
  - `weekly`  → e.g. `0 8 * * 1` (Mon 08:00)
  - custom    → translate the user's words to cron.
- Confirm the schedule back in plain language ("I'll run this Mon & Thu at 8am and send it to
  Slack #growth — sound right?").

**Token prerequisite (and where it lives).** A scheduled run still calls the adapters, so it needs
`APIFY_API_TOKEN` (and `REDDIT_CLIENT_ID/SECRET` if the official Reddit path is chosen). The token
is **not** stored on the task — the task has no secrets field. It lives in the **environment Claude
Code runs in**, which the scheduled run inherits. Persistent home: the `env` block of
`~/.claude/settings.json` (set once → every interactive *and* scheduled run has it). Set it via the
update-config flow, or have the user export it in their shell profile. It's a secret on disk —
standard for a personal BYO token. If it can't be set there, fall back to `in_app` + manual runs.

**Capture it the moment the user pastes it.** When the user gives their `APIFY_API_TOKEN` (and any
Reddit creds) in chat, immediately persist it to the `env` block of `~/.claude/settings.json` — do
not just hold it for the current session, or the scheduled task (a fresh session) won't have it.
Use the update-config flow to write:

```json
{ "env": { "APIFY_API_TOKEN": "<the token>" } }
```

Confirm it's saved, never echo the token back in full, and never write it into any skill file or
the config.json. After that, both interactive and scheduled runs read it from the environment.

## The delivery channels (`config.delivery.channel`)

Three supported, all already-connected integrations (email was dropped — its tooling only drafts):

- **`in_app`** (default, zero dependencies) — the scheduled run's output *is* the digest; the user
  opens the run to read/pick it up. Always works. Best default if Slack/Notion aren't set up.
- **`slack`** — post the digest to a channel or DM via the Slack tools (`slack_send_message`).
  Needs Slack connected and a target (`config.delivery.slack_channel`). Render in Slack **mrkdwn**
  (`*bold*`, `<url|text>`, no `#` headers). Best for a real-time Mon/Thu ping you'll actually see.
- **`notion`** — append each run to Notion as a new page (or a row in a database) via the Notion
  tools, at `config.delivery.notion_target` (a page ID/URL, or a database ID). Each opportunity
  becomes a block/row with the post link + the copy-ready draft + the safety note → a persistent,
  searchable pipeline of opportunities over time. Best if the user lives in Notion and wants a log
  rather than a ping.

If the chosen channel isn't available at run time (Slack/Notion not connected, bad target),
**fall back to `in_app` and note it in the run output** rather than failing silently.

## Delivery format (simple, copy-ready)

Whatever the channel, keep it skimmable and built around two things per pick: **the post link** and
**the draft comment to copy**. Lead with the engage set, then peers/partnerships.

```
🎯 Engagement digest — [date]  ·  [K] to engage · [P] partnerships

ENGAGE (your ICP)
1. [LinkedIn] @author — fit 9/10 · 3h ago
   🔗 <post url>

   ✍️ Comment (edit before posting):
      "the suggested reply"
   ⚠️ [Reddit only] safety note

2. …

🤝 PEERS & PARTNERSHIPS  (relationship, not pitch)
6. [Reddit] r/sub — peer
   🔗 <post url>

   ✍️ Comment: "the relationship-opener"

— Reply manually from your own account. Don't paste drafts verbatim (esp. Reddit). —
```

**Full URLs only — never truncate.** On every channel, the post link must be complete; LinkedIn
URLs need their `…-activity-<id>-…` tail or they don't resolve. Use a labeled link
(`<FULL_URL|view post>` in Slack, `[view post](FULL_URL)` in Notion) if length is ugly — but the
href stays whole. A character cap on the link is a silent broken-link bug.

The canonical digest is still `assets/digest_template.md` / `scripts/digest.py` (markdown). For
`in_app` present that inline; for `slack` reshape to the compact block above in Slack mrkdwn; for
`notion` write it as page blocks / a database row (drafts in a code or quote block so they're
one-tap copyable). The point the user asked for: **links + copy-ready drafts**, nothing they have
to dig for.

## Changing it later

"Send it to Notion instead", "switch to weekly", "pause the routine" → update `config.delivery` /
`config.cadence` and update or remove the scheduled task to match. The task and the config are the
two things to keep in sync.
