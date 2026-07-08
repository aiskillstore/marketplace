---
name: commit-chat-push
description: Commit and push repository changes while also exporting and committing the Codex chat/session transcript that produced the feature. Use when the user asks Codex to commit, push, save provenance, include the chat, commit the session, attach the Codex conversation, or preserve the implementation chat from ~/.codex/sessions alongside code changes.
---

# Commit Chat Push

## Overview

Use this skill to turn finished work into a commit that includes both the code changes and a redacted Markdown transcript of the Codex session that made them, then push the branch.

The helper script exports a transcript from local Codex JSONL sessions. Prefer the transcript over raw JSONL because raw sessions can contain system/developer instructions, encrypted reasoning blobs, full tool outputs, and secrets.

## Workflow

1. Inspect repository state.
   - Run `git status --short --branch`.
   - Run `git remote -v` and `git branch --show-current` when push behavior is not obvious.
   - Review `git diff` and staged diff before committing.
   - Never stage unrelated dirty files. If unrelated changes exist, leave them alone.

2. Verify the change.
   - Run the narrowest meaningful tests or checks for the work.
   - If tests are unavailable or fail for unrelated reasons, record that clearly in the final response.

3. Export the Codex transcript.
   - Use an existing repo convention for transcripts if one exists, such as `docs/codex-sessions/`, `codex-sessions/`, `.codex/chats/`, or `devlog/`.
   - Otherwise use `docs/codex-sessions/`.
   - Before exporting, create a fresh marker with a tiny completed command:

```bash
python3 - <<'PY'
import datetime as dt
import secrets

print(f"codex-session-anchor: {dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(4)}")
PY
```

   - Copy the printed marker exactly, then run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/commit-chat-push/scripts/export_codex_session.py" \
  --repo "$(pwd)" \
  --anchor 'PASTE_PRINTED_MARKER_HERE' \
  --require-anchor \
  --output-dir docs/codex-sessions \
  --tool-output none
```

   - If `--require-anchor` fails, wait briefly and rerun with the same marker. If it still fails, inspect candidate sessions manually and rerun with `--session /path/to/rollout-....jsonl`.

4. Review the exported transcript before staging.
   - Read enough of the file to confirm it is the intended session.
   - Search for obvious secrets or private material:

```bash
rg -n "sk-|ghp_|github_pat_|BEGIN .*PRIVATE KEY|Authorization|Bearer |password|secret|token|api[_-]?key" docs/codex-sessions
```

   - If sensitive content appears, edit the transcript or rerun the exporter with stricter omission choices before committing.
   - Do not commit raw `~/.codex/sessions/*.jsonl` unless the user explicitly asks for raw logs after being warned about the risk.

5. Stage exactly the intended files.
   - Include the exported transcript.
   - Prefer explicit pathspecs over `git add .` when the worktree has unrelated changes.
   - Confirm with `git diff --cached --stat` and `git diff --cached`.

6. Commit.
   - Use the repo's commit-message style if visible.
   - Mention the transcript in the body when helpful, for example:

```text
feat: add commit transcript workflow

Includes Codex session transcript: docs/codex-sessions/2026-05-03-commit-transcript.md
```

7. Push.
   - If the branch already has an upstream, run `git push`.
   - If it does not and a default remote exists, run `git push -u origin HEAD`.
   - If push is rejected, inspect the reason and use the repo's normal sync workflow. Do not force-push unless the user explicitly requests it.

## Selecting A Session

Prefer anchor-based selection. The marker command above finishes before export, so the JSONL for the current session should contain the marker in a tool record even when multiple sessions share the same repo cwd. `--anchor` prefers sessions containing the exact marker; `--require-anchor` prevents silently exporting a merely-newest repo session when the marker is missing.

Without an anchor, `export_codex_session.py` selects the newest Codex JSONL session whose `session_meta.cwd` matches the current repository. If that is wrong, rerun it with `--session /path/to/rollout-....jsonl`.

Useful options:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/commit-chat-push/scripts/export_codex_session.py" --help
```

- `--output-dir PATH`: write a generated Markdown filename in `PATH`.
- `--output PATH`: write to an exact Markdown path.
- `--session PATH`: export a specific JSONL session.
- `--anchor TEXT`: prefer a session JSONL containing exact marker text.
- `--require-anchor`: fail unless the selected session contains `--anchor`.
- `--tool-output none|brief|full`: control command output included in the transcript. Default is `none`; use `brief` only after considering whether prior commands printed secrets or raw session JSON.
- `--include-local-paths`: include full local source paths in metadata. By default, home paths are shortened to `~`.

## Privacy Rules

- Treat the transcript as source-controlled provenance, not a private dump.
- Keep user and assistant messages, tool names, commands, and command exit status.
- Omit developer/system instructions, encrypted reasoning, token-count events, and bulky raw logs.
- Redaction is a helper, not a guarantee. Always scan the transcript before committing.
