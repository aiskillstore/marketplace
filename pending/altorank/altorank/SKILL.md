---
name: altorank
description: Use AltoRank's tools to audit whether AI assistants can read a site, propose missing JSON-LD, read Search Console, research keywords, move the content plan, and write SEO drafts into a person's review queue. Use when the user asks about SEO, AI-search (GEO) readiness, Search Console numbers, keywords, or drafting articles for their site. Never publishes or approves.
---

# AltoRank

AltoRank writes search and AI-search content for websites. Its tools come
from the `altorank` MCP server bundled with this plugin. You can read an
account, create **drafts**, move planned keywords, edit a draft by
find-and-replace, and pause or resume a workspace. A person decides what
publishes. There is no approve, hold or delete tool and no tool that
publishes a draft, and you must not look for a way around that. The one
publish-side tool, `altorank_retry_publish`, only re-runs a failed publish of
an article a person already approved.

## Two kinds of tools

- **Any domain:** `altorank_check_readiness`, `altorank_propose_schema`,
  `altorank_generate_machine_readable`, `altorank_readiness_report`. Work on
  any public domain, not only the person's own sites.
- **Workspace tools:** everything else. They act on the person's AltoRank
  account. Write access is opt-in on the OAuth consent screen; a `forbidden`
  error means they did not grant it. `unauthorized` means the connection
  expired and the person has to reconnect.

## Reading results

Every tool returns `{ ok, data | error, agent_guidance }`.

- Read `agent_guidance` first. It is written for you.
- `_human`, when present, is how to describe a record to a person. Use its
  labels, not raw field names or enum values.
- Articles and keywords carry `allowed_mutations`. If a verb is
  `allowed: false`, tell the person the `reason` and do not retry.
- Articles carry `editor_url`. That is the link you give a person.
- `null` means unknown or unmeasured. Say "unknown", never 0.

## Preflight

1. `altorank_whoami`: confirms the connection, lists workspaces and quota.
2. One workspace: use it. Several: ask which, unless the conversation says.
3. `altorank_get_workspace`: no CMS connected means the person publishes by hand.
4. `altorank_readiness_report`: if the score is low, fixing readiness comes
   before writing more content.

## Writing a draft

1. `altorank_list_keywords`. Prefer a keyword whose
   `allowed_mutations.generate_draft.allowed` is true.
2. Nothing fits: `altorank_suggest_keywords`. It spends research credits, so
   **ask first**. Results are candidates, not saved.
3. Agree the keyword (and optionally a title) with the person.
4. `altorank_generate_draft` with one `idempotency_key` per intended draft.
   Nothing is published.
5. Poll `altorank_get_article` every 30-60 seconds until `status` is `review`
   (about two minutes). `error` means the run failed; `generation` says why.
6. Tell the person the draft is ready at its `editor_url`, then stop.

A timeout is not a failure: the draft has usually started. Repeat the call
with the **same** `idempotency_key`, never a fresh one.

## Changes (need write access)

Always inspect, propose, confirm, then write.

- `altorank_replace_in_article` / `altorank_bulk_replace_in_articles`: the
  first call is a preview. Show the hits, get a yes, then apply. Approved,
  scheduled and live articles are refused.
- `altorank_reschedule_keywords`, `altorank_remove_keywords_from_plan`: only
  unwritten planned entries move. Removing keeps the keyword tracked.
- `altorank_retry_publish`: only when `allowed_mutations.retry_publish.allowed`
  is true (approved, then the publish failed). Tell the person first.
- `altorank_pause_workspace` / `altorank_resume_workspace`: pause stops
  drafting and publishing; resume re-plans from today.

## Search Console

`altorank_gsc_performance`, `altorank_gsc_cannibalization`,
`altorank_gsc_coverage` and `altorank_gsc_url_inspection` read stored data;
nothing calls Google. Keep these states apart:

- `not_available`: Search Console is not connected, Google refused the stored
  token (a person reconnects), or no sync has succeeded (relay the error in
  `agent_guidance`). No data; do not say "no traffic".
- `has_data: false`: connected, nothing synced for the window. Never report 0.
- `has_data: true` with zeros: Google measured nothing. The site is not being
  shown in search.

`changePct: null` means no comparison: it is given only when both windows are
wholly synced (`comparable: true`). Coverage `bucket: "unknown"` means nobody
asked Google and the page was not seen in search, not "not indexed".
`inspection_superseded: true` means Google served the page after an old
"not indexed" verdict, so it is indexed now.

## Rules

- Never try to publish, approve, schedule or delete, and never change a
  workspace's automatic-publishing rule.
- Ask before spending: keyword suggestions cost credits, each draft costs quota.
  Past the included volume, only send `allow_overage: true` after a yes.
- One draft at a time per keyword. Do not regenerate a draft nobody has read.
- Never invent metrics. Volume, difficulty, scores and traffic come from the
  tools or they do not exist.
