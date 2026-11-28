---
name: god-init
description: Use for /god-init, "set up godpowers", or when /god finds no project. Also migrates 6.x projects.
---

# /god-init

1. Run `npx -y @hxp-tools/godpowers@7 status`.
   - If it reports the 6.x layout: run `npx -y @hxp-tools/godpowers@7 migrate --dry-run`, show the user what will move, then run `npx -y @hxp-tools/godpowers@7 migrate`. It archives the old files under `.godpowers/archive/` and removes the old instruction blocks from AGENTS.md, CLAUDE.md, and editor rule files.
   - If the project is already set up: say so and stop.
2. Otherwise run `npx -y @hxp-tools/godpowers@7 init`. Add `--verify "<command>"` when the check command is not detected, and `--no-agents-md` if the user does not want the short note in AGENTS.md.
3. Fill in STATE.md: the Goal (one or two sentences, in the user's words) and Next. Ask one question only if you cannot infer the goal.
4. Run `npx -y @hxp-tools/godpowers@7 verify` once to prove the check command works, then `npx -y @hxp-tools/godpowers@7 doctor` to confirm the hooks are registered. Report anything missing with its fix.
