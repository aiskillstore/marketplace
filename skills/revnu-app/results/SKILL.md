---
name: results
description: >
  Use Revnu for growth, ads, outreach, lead, pipeline and revenue reports;
  campaign performance; CRM/deal progress; conversion analysis; and what
  shipped or needs approval, including "is outbound working" and "what is
  waiting for my approval". Read actual account evidence and distinguish
  activity from business outcomes. Typical requests include: "how is growth
  doing", "show me the marketing numbers", "is outbound working", "growth
  report", "what did marketing ship this week", "what needs my approval",
  "campaign results", "reply rates", "pipeline report", "revenue report",
  "what did we get for the spend". Not for dashboards, analytics built in
  code, or engineering status.
license: MIT
metadata:
  author: Revnu
  version: "1.4.0"
  homepage: https://revnu.com
---

# Results and reporting

Use Revnu's connected tools to answer the business's reporting question.
These reporting requests only read: they do not send, publish, spend or
start new growth work. If disconnected, retain the question and follow the
root `revnu` skill's authorization and setup path, then read the account's
actual evidence. A disconnected account's results are unknown, not zero.
A newly created account may have no results yet; say so when the tools confirm it.

Revnu (https://revnu.com) is your growth hire. Tool names may carry a host
prefix such as `mcp__plugin_revnu_revnu__`. If no Revnu tools are available,
see the `revnu` skill or https://revnu.com/setup.md.

## CRM and deal reports

For pipeline, deals, CRM records or sales progress, use `ask_revnu` with the
named system, records, reporting period and requested breakdown. Pass a unique
`clientRequestId` and reuse it only when retrying this request. Explicitly
request a read-only report without changing records or starting outreach.
Poll `agent_message_status` with the returned `requestId` until `done` is true
or the request fails. Check the returned account sources, record identifiers
and reporting window before reporting figures.
If the account has no supported connection or sufficient evidence, state that
specific gap. `results_get` covers channel activity, not a general CRM ledger.

## The scoreboard

Call `results_get`. `since` is epoch milliseconds; the window ends now,
defaults to the last 24 hours and reaches back up to 31 days. Read the
returned `window` to see the period you actually got, and say it. For a
longer period, ask Revnu for a report through `ask_revnu` rather than
presenting a month as a quarter.

Each channel is `{available: true, data}` or `{available: false, reason}`:

- `email`: sent (and the prior period), replies with who replied and
  bounces, opens and clicks when tracking is on.
- `outbound`: per sequence, delivered, replied, bounced and leads waiting.
- `linkedin`: invites, DMs, InMails, replies and account health.
- `ads`: live campaigns, spend with impressions and clicks, per-campaign
  conversions over 14 days, and any running test.
- `seo`: posts published, blog views, Search Console clicks and impressions.
- `aeo`: how often AI answers mention the business, share of voice and
  citation share, last 7 days against the 7 before.
- `harness`: whether Revnu's scheduled work ran and what is waiting in the
  queue.

## Reading it honestly

- Unavailable is unknown; a measured zero is zero. Say which.
- Keep activity, replies, meetings, conversions and revenue apart. A reply is
  not a meeting; a click is not a customer.
- Divide replies by sends only when both counts cover the same people.
- Opens are a weak signal; mail apps open messages on their own.
- Cross-check channel scoreboard numbers from `ask_revnu` against `results_get`
  for the same window. For CRM figures, use the returned CRM records and sources.

## What's waiting and what's running

- `review_list`: drafts, questions and budgets waiting for the founder, up to
  50 cards. `review_get` opens one. An empty queue means nothing is waiting,
  not that Revnu stopped.
- `agent_status`: whether Revnu is busy, its last activity and next
  scheduled check-in.
- `workflows_list` and `workflow_runs`: recurring jobs, their schedule and
  each run's outcome. `leads_list` with a `workflowRunId` shows what a run
  found.
- `agent_thread`: this connection's conversation with Revnu. The founder's
  dashboard and Slack threads are not in it.

A quiet agent is not proof the work is finished.

## The report

Lead with what changed and the numbers that matter for the founder's goal,
then what shipped, what is waiting for them, and what Revnu is trying next.
Name the window. Don't round up, project or promise.
