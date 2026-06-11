---
name: ariadne-loop
description: Write verifiable Loop Engineering specs for Codex, Claude Code, OpenClaw, and AI coding agents.
version: 0.10.3
metadata:
  short-description: Write verifiable loop specs for coding agents
  openclaw:
    homepage: https://github.com/zhangzeyu99-web/ariadne-loop
    skillKey: ariadne-loop
---

# Ariadne Loop

Use this skill to turn vague agent work into a bounded loop contract for
OpenClaw, Codex, Claude Code, or another coding agent. The goal is not to make
a longer prompt. The goal is to make the next agent turn verifiable.

## When to Use

Use this skill when the user asks for any of these:

- a loop, agent loop, or Loop Engineering spec,
- a resumable handoff for OpenClaw, Codex, Claude Code, or another coding agent,
- a GitHub issue converted into an executable agent task,
- release, refactor, bugfix, or documentation work that needs explicit gates,
- supervision rules for repeated agent reports.

## Preferred Workflow

1. Identify the source shape:
   - rough notes,
   - GitHub issue title and body,
   - release/refactor/bugfix request,
   - long thread handoff.
2. Create a snapshot JSON with:
   - `title`,
   - `goal`,
   - `current_state`,
   - `recent_progress`,
   - `constraints`,
   - `verifiers`,
   - `external_effects`,
   - `risk`.
3. Generate or write an agent packet that includes:
   - inspect -> act -> verify -> decide cycle,
   - concrete verifiers,
   - stop rules,
   - rollback behavior,
   - human gates for external effects,
   - JSON-only report contract.
4. If the user wants a first-run demo and the Ariadne Loop CLI is installed:

   ```bash
   ariadne-loop quickstart --output .ariadne/quickstart
   ```

   This creates a snapshot, loop JSON, agent packet, sample reports, and a
   supervision decision.

5. For real work, prefer using the CLI:

   ```bash
   ariadne-loop init --preset bugfix --output loop-snapshot.json
   ariadne-loop write --input loop-snapshot.json --output loop-report.md --format markdown
   ariadne-loop make --input loop-snapshot.json --output loop.json --format json
   ariadne-loop check --input loop.json
   ```

6. If the work starts from a GitHub issue body:

   ```bash
   ariadne-loop from-issue \
     --title "Issue title" \
     --body-file issue.md \
     --output issue-loop.json
   ```

7. For running loops, ask the agent to append JSON reports to JSONL and use:

   ```bash
   ariadne-loop supervise \
     --loop loop.json \
     --reports reports.jsonl \
     --output decision.json
   ```

## If the CLI Is Not Installed

Do not block. Produce the snapshot JSON and the agent packet directly in the
response or in files. Tell the user they can use the browser builder:

```text
https://zhangzeyu99-web.github.io/ariadne-loop/playground.html
```

Use this report contract:

```json
{
  "action_id": "inspect|act|verify|decide",
  "status": "continue|stop|needs_human|rollback",
  "evidence": ["specific evidence observed in this turn"],
  "next_step": "the next concrete action",
  "passed_verifiers": ["gate ids that passed in this turn"],
  "failed_verifiers": ["gate ids that failed in this turn"]
}
```

## Verifier Rules

Prefer observable gates:

- command output,
- rendered page or screenshot readback,
- generated artifact exists and validates,
- remote GitHub issue, PR, release, or Pages output is read back,
- diff contains no unrelated churn,
- failing reproduction now passes.

Avoid weak gates:

- "looks good",
- "done",
- "agent says it completed",
- unverified screenshots,
- claims about remote state without readback.

## Human Gates

Require human confirmation before:

- `commit`,
- `push`,
- tag or release creation,
- package publish,
- deploy,
- deletion,
- sending external messages,
- payment or billing actions.

After any approved external effect, read back the real target before reporting
success.
