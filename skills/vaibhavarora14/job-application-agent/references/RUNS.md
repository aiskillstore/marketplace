# Resumable application runs

## Round lifecycle

Start each batch with an explicit ID:

```text
node scripts/job-application.mjs round start --stdin
node scripts/job-application.mjs round status [round-id]
node scripts/job-application.mjs round complete --stdin
```

Start input: `{ "requestedCount": 30 }`. Complete input: `{ "roundId": "round-..." }`.

Count only unique applications with a visible employer/ATS confirmation or a verified sent recruiting email that were also added to the ledger with the same `roundId`. Filled forms, blockers, drafts, unsent email, and ambiguous confirmations never count. `round complete` rejects an under-target round.

Run both company-level and requisition-level duplicate checks before filling and again immediately before transmission. Hard ledger-ID, canonical-URL, employer-job-ID, and requisition duplicates always stop. Same-role aliases require a verified distinct requisition and `NEW REQUISITION CONFIRMED`. A genuinely different role at the same company may proceed automatically only when `companyReapply.decision` is `eligible-after-cooldown`: 15 full days have passed since the latest company application and no outcome has been recorded. `cooldown-active` and `follow-up-present` require explicit candidate approval.

Resolve the canonical résumé with `resume path`, upload its absolute path through the browser’s privileged chooser first, and verify the filename and parsed fields. Use a visible native picker only as a fallback.

Store independent attribution on every new ledger row:

- `discoverySource`: where the lead was found (`linkedin`, `x`, `yc`, `hacker-news`, `job-board`, `direct-company`, `email`, `user-supplied`, `web-search`, or `other`).
- `discoverySourceId`: stable packaged catalog ID such as `yc-work-at-a-startup` or `hacker-news-who-is-hiring`, when known.
- `applicationChannel`: where it was submitted (`ashby`, `greenhouse`, `lever`, `workday`, `company`, `email`, and the other documented ATS values).
- `source`: the legacy-compatible application channel.

## Attention queue

Append blocked work instead of interrupting the round:

```text
node scripts/job-application.mjs attention add --stdin
node scripts/job-application.mjs attention list
node scripts/job-application.mjs attention resolve --stdin
```

Store only application ID, canonical URL, round ID, stage, blocker enum, timestamp, and bounded required-action enums. Never store passwords, MFA codes, CAPTCHA answers, demographic answers, government IDs, or legal responses. Prioritize authentication/MFA/CAPTCHA, then legal/authorization/compensation, then judgment/video/site issues. Preserve the tab when supported; otherwise reopen the canonical URL and refill verified data.

## Friction queue

Record bounded general workflow failures without candidate data:

```text
node scripts/job-application.mjs friction record --stdin
node scripts/job-application.mjs friction list
```

Use a stable kebab-case error code, documented stage and ATS, and Boolean `reproducible` and `general` fields. Only entries where both are true qualify for a tested public-agent PR. Never include URLs, form text, answers, résumé metadata, identity, or raw errors.
