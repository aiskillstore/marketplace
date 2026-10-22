---
name: agent-transit
description: A transit map for your coding-agent sessions. Use when the user wants to visualize one Claude Code, Codex CLI, or Cursor coding-agent session as a subway map of tool calls.
---
<!-- Generated from src/agent-transit/SKILL.md; do not edit -->


# Agent Transit

A local subway map for one AI coding-agent session: tool families are lines and tool calls are stations.

🔒 Session logs can contain prompts, source code, command output, credentials, and other secrets. This skill is default-deny: it keeps only tool name, family, target basename, timing, status, and `agent.source`. Prompt text, assistant text, tool output, file contents, full commands, and arguments are dropped. `--show-args` is an explicit opt-in and includes only a truncated, redacted argument preview.

## Where things are

`<skill>` means the folder containing this file. Run scripts from it by absolute path, e.g. `node <skill>/src/agent-transit/scripts/find-session.mjs --source codex`. The shared engine is at `<skill>/core/`.

## Steps

1. Find the newest local session path without reading its contents: `node <skill>/src/agent-transit/scripts/find-session.mjs --source claude-code|codex|cursor`.
2. Build one page to share: `node <skill>/core/build.mjs <session.jsonl> --format claude-code --share --title "Agent: one coding session, tool by tool"`.
   Without `--out` the file is named after the title and the first failed tool call, in `./transit-out/`, e.g. `transit-out/agent-shell-git-service-alert.html`.
   `--share` scrubs at the strict level, refuses `--no-scrub`, and opens the page paused on the first failed call with a one-line verdict above the map.
   Idle stretches with nothing running (e.g. model thinking time between tool calls) longer than 3 s are shortened to 3 s so the animation isn't dead air; the header says how many were shortened and the root span keeps the wall time as `transit.wall_ms`. Pass `--max-gap-ms N` to change the cap, or `--max-gap-ms 0` for true wall-clock timing.
3. Share the HTML file: give the user its path and the verdict line the build printed, ready to paste with the file in Slack
   (desktop and iOS open it as the interactive page). Use the printed verdict as is. For example:
   > shell · git failed after 12.0 s: denied · SERVICE ALERT · 18 calls
   > `agent-shell-git-service-alert.html` opens on the denied call. Only tool names and timing are in it.
4. Optional teaser (GIF + MP4) with the bundled renderer: `node <skill>/core/render.mjs <session.jsonl> --format claude-code --name agent`.
5. Check it with the bundled verifier: `node <skill>/core/verify.mjs <session.jsonl> --format claude-code --name agent`.

Use `--format codex` or `--format cursor` for those sources.

Cursor: most Cursor installs keep chats only in `state.vscdb`, not as transcripts. Export one composer to a metadata-only JSONL (tool name, status, file basename or command word, timestamps; never message text, params or results), opened read-only:
`node <skill>/src/agent-transit/scripts/export-cursor.mjs --list` (sessions for the current workspace; `--workspace DIR` or `--all-workspaces`), then `node <skill>/src/agent-transit/scripts/export-cursor.mjs --composer <id or prefix> --out ./transit-out/agent/cursor.cursor.jsonl`, and build that with `--format cursor`.
Cursor builds since about Sep 2025 stamp each message bubble with `createdAt`, so calls start at real times; Cursor stores no tool end time, so each call ends at the next message (an upper bound). Older bubbles and `agent-transcripts` files have no timestamps: order only, with uniform synthetic durations. Keep session files local and never upload them. Synthetic fixtures are provided in `samples/`; no real home-directory logs belong in this repository.

## Rules

- Never expose or copy prompts, code, command lines, outputs, or arguments by default.
- Only use the bundled build/render/verify scripts; never hand-write a substitute renderer.
- Do not upload a session or render unless the user explicitly asks.
- Review errors, denials, slow calls, and subagent branches in the map without revealing their payloads.
