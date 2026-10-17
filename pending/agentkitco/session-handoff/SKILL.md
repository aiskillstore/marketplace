---
name: session-handoff
description: Write a HANDOFF.md that lets a fresh agent session continue the work, with goal, state, decisions, next steps and traps. Use when ending a long session, hitting context limits or switching agents.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Hand off the session

Goal: a new session (or a different agent, or you tomorrow) can resume in minutes without re-discovering anything. Write facts you verified, not impressions.

## Steps

1. **Check the real state.** Run `git status --short`, `git branch --show-current` and `git log --oneline -10`. Run the project's quick tests or build if you can, so the handoff says whether the tree is green or red.
2. **Write `HANDOFF.md`** in the repository root (or the path the user names) with the sections below. Keep it under about 80 lines.
3. **Do not commit it** unless asked. Mention that it is untracked and should not be committed to a shared branch by accident.
4. **Tell the user** how to resume: for example "start a new session and say: read HANDOFF.md and continue".

## HANDOFF.md template

```
# Handoff: <short task name>
Written: <date and time>  Branch: <branch>  Last commit: <hash subject>

## Goal
<What done looks like, in 2 to 4 lines. Include the user's own wording where it matters.>

## Current state
- Working tree: <clean | uncommitted changes in ...>
- Tests/build: <command> -> <pass | fail with the key error>
- Done: <bullets, each verifiable>
- In progress: <what is half-finished, which files>

## Decisions and why
- <Decision>: <reason>. Rejected: <alternative and why>.

## Next steps (in order)
1. <Specific action with the file or command>
2. ...

## Traps and facts learned
- <Things that wasted time: flaky test, misleading error, env quirk, file that must not be edited>
- <Commands that work / do not work>

## Open questions for the user
- <Anything blocked on a human decision>

## Not verified
- <Claims you did not check>
```

## Rules

- Separate verified facts from guesses. If you did not run it, list it under "Not verified".
- No secrets, tokens or personal data in the file.
- Next steps must be actionable by someone with no memory of this session.
- Include the exact failing command and error text for anything red; a paraphrase is not enough.
