# Commit Chat Push

Commit Chat Push is a Codex skill for shipping code with its implementation provenance. It guides Codex through reviewing changes, exporting a redacted transcript from `~/.codex/sessions`, committing the transcript alongside the feature, and pushing the branch.

## What It Does

- Finds the relevant Codex session JSONL file.
- Exports a Markdown transcript instead of committing raw session logs.
- Redacts common secret formats and shortens home-directory paths.
- Records user/assistant messages, tool calls, commands, and command exit status.
- Leaves command output disabled by default to avoid re-committing bulky logs or accidentally printed secrets.
- Guides Codex through explicit staging, commit, and push checks.

## Install

Clone this repository into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/bertona88/commit-chat-push.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/commit-chat-push"
```

Restart or open a new Codex thread if the skill is not immediately visible.

## Use

Ask Codex:

```text
Use $commit-chat-push to commit these changes, include the Codex chat transcript, and push the branch.
```

The skill exports transcripts to `docs/codex-sessions/` unless the repository already has a clearer convention.

## Exporter

The bundled exporter can also be run directly:

```bash
python3 scripts/export_codex_session.py \
  --repo "$(pwd)" \
  --output-dir docs/codex-sessions \
  --tool-output none
```

Useful options:

- `--session PATH`: export a specific Codex JSONL session.
- `--output PATH`: write to an exact Markdown file.
- `--tool-output none|brief|full`: include no command output, truncated command output, or full command output.
- `--include-local-paths`: keep full local paths in transcript metadata.

## Privacy Model

Raw Codex sessions can include system/developer instructions, full command outputs, local paths, and sensitive text that appeared in the terminal. This skill commits a redacted Markdown transcript instead of raw JSONL.

Redaction is a safety net, not a guarantee. Before committing a transcript, scan it for secrets:

```bash
rg -n "sk-|ghp_|github_pat_|BEGIN .*PRIVATE KEY|Authorization|Bearer |password|secret|token|api[_-]?key" docs/codex-sessions
```

## Repository Layout

```text
.
|-- SKILL.md
|-- README.md
|-- agents/
|   `-- openai.yaml
|-- docs/
|   `-- codex-sessions/
`-- scripts/
    `-- export_codex_session.py
```

## Validation

```bash
python3 -m py_compile scripts/export_codex_session.py
python3 /path/to/skill-creator/scripts/quick_validate.py .
```
