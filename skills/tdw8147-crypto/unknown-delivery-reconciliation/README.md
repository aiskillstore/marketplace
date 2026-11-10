# Unknown Delivery Reconciliation

When a receipt is unclear, settle what you can without sending the request twice.

## The problem

An attachment upload times out, but a matching read-only receipt says it arrived. A newer note refers to a different identifier and says only that it was sent. The operator needs to know whether the two records describe the same request before closing the case. Clicking upload again would add another attempt without settling the first.

## Before / After

Same task, same model (GPT, internal simulated test). Translated from the original Chinese output; omissions marked `…`.

**Without the skill** — careful, but open-ended:

> **Pending:** confirm whether q7 and att-901 are the same object, whether the 09:02 query covered q7, and whether q7 already has delivered evidence … Suggest only a read-only status check of the original q7, or waiting for a bounded time … The waiting period and what to do when it expires are still to be confirmed. Do not resend on our own.

**With the skill** — a capped, decidable next step:

> **Next step:** run at most **one** read-only status query on the original q7, matching target, submit time and the original attachment hash to att-901. If the latest trusted receipt for that identity is *delivered*, acceptance is met — close it; no need to wait for "read". If the query is unavailable or the identity still cannot be matched, keep it pending and stop polling. Never resend, resend under a new ID, or click to test.

Both avoid a duplicate send. The second sets a hard cap, says exactly what to match, and defines when the case is closed.

## Evidence

First-delivery all-criteria pass rate, without → with the skill: **GPT 15.4% → 33.3%; DeepSeek 92.3% → 100.0%** ([EVIDENCE.md](../EVIDENCE.md); internal simulated test, small sample). Measured on the earlier compact edition of this skill; this expanded edition has not been re-measured yet.

## Trigger phrases

- “It timed out after submit. Did it go through?”
- “Does this receipt belong to the original attachment?”
- “Sent isn't enough; confirm whether it was delivered.”
- “Write the status record without resending.”

## Install

- **Claude Code:** Put `unknown-delivery-reconciliation/SKILL.md` under `~/.claude/skills/`.
- **Codex:** Put `unknown-delivery-reconciliation/SKILL.md` under `~/.agents/skills/`.
- **Cursor:** Create `.cursor/rules/unknown-delivery-reconciliation.mdc` and paste the skill body into the rule.
- **ChatGPT / DeepSeek:** Paste the skill and the existing request and receipt evidence into the chat.

## What's inside

- `SKILL.md` — English workflow, template, examples and checklist.
- `SKILL.zh.md` — Complete Chinese version.
- `README.md` — This page: the problem, a real before/after, numbers and install steps.

## 中文简介

超时或回执冲突时，按原请求标识、目标、提交时间和内容指纹核对。只报告证据支持的层级；达标就结案，缺证据也先交记录，只留一个有界查询，不重发。
