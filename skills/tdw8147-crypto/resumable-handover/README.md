# Resumable Handover

Give the next shift a starting point, not a transcript to reread.

## The problem

A four-page manual has been exported and its body checked, but nobody has opened the latest PDF. A new revision changed only the cover. The next operator needs to know what the older review still covers, what to open first, and when to restore the cover. A long list of things to reconfirm obscures that decision.

## Before / After

Same task, same model (GPT, internal simulated test). Translated from the original Chinese output; omissions marked `…`.

**Without the skill** — the handover ends in an open question list:

> **To confirm**
> - The exact path of v3, how to restore the cover, and who signs off delivery after review. …

**With the skill** — the handover starts with one action and a finish line:

> **First action:** locate and open the latest v3 file. **Done when:** you actually see the v3 preview. If it cannot be located yet, wait for the v3 file location. …

The second one tells the next person exactly what to do first and how they will know it worked. It names the one missing input instead of blocking the whole handover on it.

## Evidence

First-delivery all-criteria pass rate, without → with the skill: **GPT 23.1% → 100.0%; DeepSeek 66.7% → 100.0%** ([EVIDENCE.md](../EVIDENCE.md); internal simulated test, small sample). Measured on the earlier compact edition of this skill; this expanded edition has not been re-measured yet.

## Trigger phrases

- “Leave a handover for the next shift.”
- “What is the first action when we resume?”
- “This revision changed only the cover. What still needs checking?”
- “Capture the pending request without trying it again.”

## Install

- **Claude Code:** Put `resumable-handover/SKILL.md` under `~/.claude/skills/`.
- **Codex:** Put `resumable-handover/SKILL.md` under `~/.agents/skills/`.
- **Cursor:** Create `.cursor/rules/resumable-handover.mdc` and paste the skill body into the rule.
- **ChatGPT / DeepSeek:** Paste the English or Chinese skill and the current notes into the chat.

## What's inside

- `SKILL.md` — English workflow, template, examples and checklist.
- `SKILL.zh.md` — Complete Chinese version.
- `README.md` — This page: the problem, a real before/after, numbers and install steps.

## 中文简介

暂停、换班或转交时，用现有资料直接产出断点单：写清已完成证据支持哪个版本、下一步做什么、看到什么才算做完。资料不全也先交，未完成的业务动作不代做。
