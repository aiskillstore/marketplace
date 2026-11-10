# Reactive Form Input

The field can look right and still be empty where the application makes decisions.

## The problem

A profile page has a visible contact email field and a hidden email field. A DOM write makes the address appear, but the application model is empty. The submit button stays disabled, and the team needs a record of what actually took effect. Submitting the form is not part of that check.

## Before / After

Same task, same model (GPT, internal simulated test). Translated from the original Chinese output; omissions marked `…`.

**Without the skill** — a status line with nothing to act on:

> **Current conclusion:** state sync and blocked submit have been reported; cause and verification results are pending, so the check cannot be called complete or passed.

**With the skill** — what was shown vs what the app accepted:

> - **On record:** after the DOM write the displayed value is correct, but React state is empty and the submit button is disabled. The record does not say when this was observed, whether a validation message appeared, or whether async validation finished.
> - Displayed value and app state disagree, so the DOM value alone does not prove the input took effect. Status: **not confirmed as accepted** — and also not proven to have failed. …

The second one separates the displayed value from the app's own state and lists exactly which evidence is missing, without pretending a live test ran.

<sub>This excerpt comes from an earlier full-length draft of the skill; the saved archive has no compact-version sample for this task.</sub>

## Evidence

First-delivery all-criteria pass rate, without → with the skill: **GPT 33.3% → 100.0%; DeepSeek 80.0% → 100.0%** ([EVIDENCE.md](../EVIDENCE.md); internal simulated test, small sample). Measured on the earlier compact edition of this skill; this expanded edition has not been re-measured yet.

## Trigger phrases

- “The field looks filled, but the app hasn't picked it up.”
- “Check the visible contact field, not the hidden duplicate.”
- “Is this input accepted, still validating, or unverified?”
- “Check the form state without submitting it.”

## Install

- **Claude Code:** Put `reactive-form-input/SKILL.md` under `~/.claude/skills/`.
- **Codex:** Put `reactive-form-input/SKILL.md` under `~/.agents/skills/`.
- **Cursor:** Create `.cursor/rules/reactive-form-input.mdc` and paste the skill body into the rule.
- **ChatGPT / DeepSeek:** Paste the skill and the page or interaction notes into the chat.

## What's inside

- `SKILL.md` — English workflow, template, examples and checklist.
- `SKILL.zh.md` — Complete Chinese version.
- `README.md` — This page: the problem, a real before/after, numbers and install steps.

## 中文简介

表单明明显示了值，应用却可能没接收。这个技能让代理认准目标字段、分开记录显示值与应用信号，区分已生效、未生效、校验中和未验证；不靠提交业务表单来试。
