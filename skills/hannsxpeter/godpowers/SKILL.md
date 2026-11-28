---
name: godpowers
description: Use when the user mentions godpowers or the repo has .godpowers/. Shared contract for state, evidence, and gates.
---

# Godpowers

Godpowers keeps a project's memory on disk and refuses unverified "done". You do the thinking. Godpowers supplies the state files, a definition of done, and gates that code enforces.

## Commands

| Command | Use it to |
| --- | --- |
| `/god` | ask what to do next, or drive a goal through the stages it needs |
| `/god-init` | set up `.godpowers/` in a repo, or migrate a 6.x project |
| `/god-plan` | write or refresh the plan |
| `/god-build` | implement plan slices test-first |
| `/god-review` | get an independent review in a fresh context |
| `/god-harden` | run a security pass |
| `/god-ship` | pass the release gate and ship |
| `/god-status` | see state, evidence, and risks |

## Files in `.godpowers/`

- `STATE.md`: the one state file. Frontmatter: `project`, `stage` (plan, build, review, harden, ship, done), `verify` (the project's check command). Optional: `fast` (a file-local check; `{files}`, a word of its own outside quotes, is replaced by the changed files as arguments, not on Windows), `docs` (globs that narrow what counts as documentation, never widen it, or `none`), `risk` (extra globs that make a change high risk). Sections: Goal, Now, Next, Risks.
- `PLAN.md`: goal, requirements with "Done when" checks, non-goals, design, slices. Skipped when the request already lists its requirements; they go under Goal in STATE.md instead.
- `DECISIONS.md`: append-only log of lasting decisions, `## YYYY-MM-DD: title`. Supersede, never edit.
- `evidence.jsonl`: written only by the CLI. Never edit it by hand.

Update STATE.md at milestones (stage change, slice done, new risk), not after every edit.

## Evidence

- Run targeted tests directly while you work. Before saying code work is done, record the project check once through the CLI: `npx -y @hxp-tools/godpowers@7 verify "<command>"`. It records the result against the exact code on disk.
- Run `npx -y @hxp-tools/godpowers@7 fast` while you work when STATE.md declares `fast`. It is cheap and never recorded.
- A passing record goes stale when code changes, so record it after your last change. `verify` reuses a passing record of the same command on unchanged code; `--force` runs it again.
- If no automated check can cover a change, record why with `npx -y @hxp-tools/godpowers@7 verify --waive "<reason>"` and say the change is unverified. Never waive a failing check.
- Record reviews with `--reviewer "<model>"` when the reviewer reported its model. `npx -y @hxp-tools/godpowers@7 verdict` prints the ledger summary to paste unedited into a PR or release notes.
- Report failures as failures, with the output.

## Risks

Risks are checkbox lines under `## Risks` in STATE.md: `- [ ] critical: what, where`. Tick the box when it is fixed. Severities: critical, high, medium, low. An open critical risk blocks shipping.

## Gates enforced by code

- Stop hook: if code changed during the session and no passing record matches it, you are asked to verify before finishing.
- Commit hook: `git commit` is blocked while `npx -y @hxp-tools/godpowers@7 lint` reports errors in `.godpowers/` (including edits to past decisions).
- Ship gate: `npx -y @hxp-tools/godpowers@7 gate ship` scales with `npx -y @hxp-tools/godpowers@7 risk`. Low risk needs a passing check, normal adds a review, high adds a security record (no base to compare means high). An open critical risk always blocks.

## Working style

- Scale the ceremony to the work. A one-line fix needs no plan. A feature gets a build and an independent review, a plan only when the request does not already list its requirements, and a security pass only when it touches a trust boundary (auth, secrets, untrusted input, money, deleting data). Ship only when the user asks.
- Delegate to a subagent only when a fresh context or parallel work helps. You choose which subagent (your host's own, or the optional god-* agents) and how it runs.
- Every time you start a subagent, size it as its own step: say which model and reasoning effort you picked and why, then pass both explicitly in the call that starts it (whichever your host accepts). Never let it inherit yours. Pick the cheapest model and the lowest effort that will do the subtask well: a small, fast model at low effort for reading, searching, running checks, and mechanical edits; your host's most capable model at high effort only for subtle design, tricky correctness, or security-critical review. Start it with a fresh context and a self-contained brief, because some hosts accept a model or effort only for a fresh-context subagent.
- Prefer a reviewer from a different model family than the builder when your host offers one: agreement between similar models proves little.
- Ask the user only for decisions that are theirs: scope, spending, credentials, and public or irreversible actions.
