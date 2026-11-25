---
name: god
description: Use for /god, "what next", or "take this to production". Reads STATE.md, names the next step or drives a goal.
argument-hint: "[goal]"
---

# /god

1. Run `npx -y @hxp-tools/godpowers@7 status`. If there is no project, offer /god-init (it also migrates 6.x projects) and stop.
2. With no goal: answer in at most five lines: where the project stands, the single next step, and the command for it.
3. With a goal, pick the smallest path that does it well, skipping any stage STATE.md shows is already done for this goal:
   - A question or assessment: answer from the code and the state files.
   - A small change (one slice, low risk, no trust boundary): make it, run `npx -y @hxp-tools/godpowers@7 verify "<verify command>"`, and touch STATE.md only if the stage or risks changed.
   - A feature: /god-plan, /god-build, then /god-review. When the request already lists its requirements, skip /god-plan: write the goal and those requirements, one line each, under Goal in STATE.md, set `stage: build`, and build from them. Decide the security pass with `npx -y @hxp-tools/godpowers@7 risk`: high means /god-harden, and a trust boundary (auth, secrets, untrusted input, money, deleting data) it misses does too.
   - A new product, or a large or unclear goal: /god-plan in full, /god-build, /god-review, and /god-harden.
4. Run /god-ship only when the user asks to ship, release, or deploy. Its gate follows the risk tier, so run /god-harden first only if the gate asks for a security record.
5. Keep going between the stages you chose without asking. Stop only for decisions that belong to the user (scope, spending, credentials, public or irreversible actions), or when the same gate fails twice for the same reason.
6. Unattended ("I'm not watching", "unattended", "full stop"): keep going until the work is ready for the step only the user takes, and never cross into a public or irreversible step. Ask only through the host's question tool (AskUserQuestion in Claude Code, request_user_input in Codex), giving the context, what blocks you, and the options with your recommendation first; a question in a normal message goes unseen and the turn looks finished. End in one state: ready (gates pass, the next step is the user's), waiting for the user's approval, or blocked (what blocks, what you tried, what is needed).
7. Finish with what changed, the verify result, open risks, and the next step.
