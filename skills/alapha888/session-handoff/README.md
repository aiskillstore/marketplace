# Session Handoff Kit

A free kit for users of AI coding agents (Claude Code, Codex, Cursor): end every session with a structured handoff, so the next session — or the next agent — starts from facts, not from a degraded, over-full context.

## What's inside

| File | What it is |
| --- | --- |
| `SKILL.md` | A ready-to-install agent skill: when context fills up or a session ends, the agent produces a structured handoff note (goal state, decisions and why, files touched, open loops, next action). |
| `context-hygiene-checklist.md` | One-page decision guide: when to `/clear`, when to `/compact`, when to start fresh — and the 2-minute routine to run before any reset. |
| `handoff-template.md` | A fill-in handoff note template with per-section guidance. |

## Install the skill

Copy `SKILL.md` into a `session-handoff` folder in your agent's skills directory, or use the skills CLI:

```bash
npx skills add alapha888/session-handoff-kit
```

## Why

Agent output quality drops as context fills with stale exploration. The fix is not a bigger context window; it is a habit: capture state before you reset, in a format the next session can execute from without re-asking you everything.

MIT licensed. Feedback via GitHub issues.

## Install via skills.sh

Listed at [skills.sh/alapha888/session-handoff-kit](https://skills.sh/alapha888/session-handoff-kit).

Listed on OpenAgentSkill: [alapha888-session-handoff-kit](https://www.openagentskill.com/skills/alapha888-session-handoff-kit)

```bash
npx skills add alapha888/session-handoff-kit
```

Adds the `session-handoff` skill to your agent environment. Free to use. No account required.
