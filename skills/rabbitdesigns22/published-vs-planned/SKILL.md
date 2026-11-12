---
name: published-vs-planned
description: >-
  Load whenever an agent has scheduled, uploaded or published content (posts, reels, stories, videos, files) on a social scheduler or a drive and must say what is actually live. Use it for "check what was actually published", "did it post", "is it scheduled", "nothing is published", "did the upload save", "revisa lo publicado", "¿ya salió?", "no salió en Instagram", "programado", "¿ya se guardó todo?", "nada está en el Drive". It builds a plan list, reads each item back from the scheduler's own list, and after the slot passes checks the LIVE public page, then reports only a planned / scheduled / live table. It never says "published", "scheduled" or "done" because a tool said success. Works for Meta Business Suite, TikTok, LinkedIn, Buffer, any scheduler, and for files uploaded to a drive. Not for designing posts or writing captions, and not for ad performance or reach numbers.
license: MIT
---

# Published vs planned

A tool saying "success" is not a post on a profile. Schedulers accept a job and fail later: expired token, wrong account, rejected format, one network silently dropped. The owner then opens the page, finds nothing, and the agent has already said "all published". This skill closes that gap with one rule: **a row is "published" only if you saw it live, in this check.**

## When to use

- You just scheduled, uploaded or published something and are about to report it.
- Someone asks "did it go out?", "is everything saved?", "why isn't it on Instagram?".
- A recurring job posts content for clients and nobody has looked at the live pages.

Do not use it to design posts, write captions, or read ad results. It only answers: did the thing I planned exist where it should, when it should?

## The method

### 1. Build the plan list first (before touching the scheduler)

One row per item per network. Cross-posting to Facebook and Instagram is two rows.

| # | Account / page | Network | Format | Planned date-time + timezone | Asset (file name or id) | Caption, first words |
|---|---|---|---|---|---|---|

Rules:
- Write the timezone on every row. The scheduler's timezone and the account's timezone often differ.
- Take the list from the brief or approved calendar, not from what you remember doing.
- If a field is unknown, say so now. Do not fill it later from guesses.

### 2. After scheduling: read back from the scheduler's own list

Close the confirmation toast. Open the scheduler's list view (scheduled posts, planner, queue) and match each row field by field:

- right account/page, right network
- right format (post vs reel vs story)
- date, time and timezone
- the right media (open the preview; count items in a carousel)
- caption intact (first words, line breaks, links, hashtags, no truncation)

Any mismatch: fix it now, then read it back again. A row not found in the list is "not scheduled", whatever the toast said.

### 3. After the slot passes: check the LIVE surface

Wait until the planned time has passed, plus a few minutes. Then open what the public sees, not the admin tool:

- the public profile or page, logged out or in the app view when possible; or the platform's own "published" list as a second source
- Instagram and Facebook **separately**. Cross-posting often drops one side without any error.
- for each row confirm: it exists, correct account, correct format, caption intact, media plays and is the right asset, posted at about the right time
- for drive uploads: open the destination folder in the web view, check file name, size greater than zero, and that it opens

Stories expire and some formats appear in a different tab (reels tab, stories archive). Look in the right place before calling something missing.

### 4. Report only the reconciliation table

Put gaps first. Give the exact check time with timezone.

| # | Item | Planned | Scheduled (list view) | Live (public page) | Gap and likely cause | Fix |
|---|---|---|---|---|---|---|

Status words per cell: `ok`, `missing`, `wrong` (say what), `not yet due`, `not checked` (say why). Then one line: "Checked 4 Nov, 21:40 (UTC-5): 7 of 9 live, 2 gaps."

### 5. Words you may and may not use

- "Published" and "live": only for rows verified on the live surface in this check.
- "Scheduled": only for rows you read back in the scheduler's list in this check.
- Never from: a tool status, a task marked "succeeded", a toast, a log line, an earlier report, or memory.
- If you could not look (login expired, page blocked), write `not checked` and why. "Unknown" beats "probably fine".
- If something is wrong and you can safely fix it (reschedule, re-upload, republish a missed slot with the owner's approval where required), do it, then re-verify and show the new evidence.

### 6. Recurring cadence

- Right after each scheduled slot: check only the rows that slot covered.
- Once a day: full table.
- Between checks, report a diff only ("2 rows changed since the last check"), not the full story again.
- Keep the last table with its timestamp so the next check can diff against it.

## Worked example

Plan: 3 items for Tuesday. Reported at 21:40.

| # | Item | Planned | Scheduled | Live | Gap and cause | Fix |
|---|---|---|---|---|---|---|
| 1 | Page A, FB, post | Tue 10:00 | ok | ok | none | none |
| 2 | Page A, IG, reel | Tue 10:00 | ok | missing | cross-post to IG failed, no error shown | republished manually 21:45, now live (verified) |
| 3 | Page B, FB, reel | Tue 18:00 | wrong: set to 08:00 | ok at wrong hour | timezone shift (scheduler on another zone) | account timezone set, note for next batch |

Bad report: "All 3 scheduled and published." (came from three success toasts.)

## Common failure causes

- Expired or revoked token, or the page's permissions changed
- Wrong account selected, or two similar pages/accounts
- Format rejected: reel too long, wrong aspect ratio, unsupported codec, caption too long
- Timezone shift between scheduler, account and the person planning
- Media upload still processing when the schedule was saved, so the post saved without media
- One network silently dropped in a cross-post
- Duplicate or draft saved instead of scheduled
- Scheduler list filtered (date range, one account) so the row seems missing, or seems present when it is another item
- Content flagged by the platform after posting, or removed by a copyright check
- Drive uploads: sync not finished, file landed in the wrong folder, zero-byte file, permissions not shared

## Limits

- You cannot see private or restricted accounts without access; say so.
- Platform lists can lag a few minutes; recheck once before calling it missing.
- This checks existence and fidelity, not whether anyone saw it.
