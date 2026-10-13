# Troubleshooting

Common errors and solutions for `cargo-ai context` commands.

## General

**`{"errorMessage": "..."}`**
All failed commands exit non-zero and return an error JSON. Read the `errorMessage` for the specific issue.

**`Unauthorized` / `403`**
Your API token may lack the required permissions, or the workspace's context repository isn't configured. Verify with `cargo-ai whoami`; if a context repo hasn't been set up for the workspace, ask an admin (or do it via the Cargo app under workspace settings).

## Runtime — browse / read

**Path not found**
The path does not exist in the runtime sandbox. Use `cargo-ai context runtime browse --path <parent>` to confirm the file layout before reading. Paths are relative to the repo root, no leading slash (`persona/vp-sales.md`, not `/persona/vp-sales.md`).

**Out-of-range lines**
`--start-line` and `--end-line` are 1-indexed and inclusive on both ends. If they fall outside the file's line count the read fails. Read the file without a range first to confirm length, or omit one end (e.g. only `--start-line`) to read to EOF.

## Runtime — write

**Push fails / commit not appearing**
`write` pushes to the context repo's default branch. Pushes fail if the configured GitHub connector lost permissions or the branch was deleted/renamed. Verify the connector via `cargo-ai connection connector list` and check the default-branch setting in the Cargo app under workspace settings.

**No `_template.md` for the domain**
Some workspaces customize their context repo. If a domain doesn't ship a template, browse the domain (`cargo-ai context runtime browse --path <domain>`) and model the new file after an existing entry.

**Missing / empty / malformed frontmatter (not an error)**
Frontmatter is a strong convention but **not validated** — `write` never rejects a file for a missing `title`/`description` or malformed YAML; the file is committed as-is. The graph fails soft: a missing `title` falls back to the filename, the node summary falls back to the body's first paragraph, and a malformed frontmatter block is stripped so it doesn't leak into the summary. Nothing dangles, but the node indexes poorly — set `title` (and a `summary:` if you want a specific summary) on every file. Note the graph reads `summary`, not `description`.

**Other `notWritten` reasons**
`write` can fail with `repositoryNotFound`, `syncConflict`, `syncFailed`, `failedToWrite`, or `deniedPath` (writing under `.files/` — update those via Content instead). `syncFailed` / `failedToWrite` / `deniedPath` carry an `errorMessage`. See `references/response-shapes.md`.

## Runtime — edit

**`--old-string` not found**
`--old-string` did not match any substring in the file. Whitespace must match exactly — escape newlines (`\n`) where present, and watch for trailing spaces. Read the file first and copy the substring verbatim.

**`--old-string` matches more than once**
`edit` requires the match to be unique. Add enough surrounding context to make the match unique (extend with the line before or after), or do multiple targeted edits in sequence.

**Other `notEdited` reasons**
Besides the `--old-string` cases above, `edit` can return `fileNotFound`, `noOp` (the new string equals the old), `syncConflict` / `syncFailed` (push race), `failedToEdit`, or `deniedPath` (editing under `.files/`). Frontmatter is **not** validated, so an edit that removes or empties `title`/`description` still applies — keep the block intact so the node stays discoverable.

**Edits not appearing in GitHub**
`edit` commits and pushes; `execute` does **not** push. If you ran a shell command that modified files (e.g. `sed -i`, redirecting into a file), the change stays in the ephemeral sandbox and is discarded. Use `write` or `edit` for any change that should land in git.

## Runtime — execute

**Command output is empty / unexpected**
The runtime sandbox starts clean for each call; mutations from prior `execute` calls are not preserved between invocations. Don't rely on state across `execute` runs — chain operations in a single `--command` (e.g. via `sh -c`) instead.

**Side effects not pushed**
By design, `execute` does not commit. Use `execute` for inspection (`grep`, `ls`, `find`, counting, validation); use `write`/`edit` for any persistent change.

**Argument escaping**
`--args` is a **JSON array** of strings, not a shell-quoted list. Wrap the whole thing in single quotes so the shell doesn't mangle the JSON:

```bash
# Correct
cargo-ai context runtime execute --command grep --args '["-r","vp-sales","."]'

# Wrong — shell will eat the inner double quotes
cargo-ai context runtime execute --command grep --args ["-r","vp-sales","."]
```

## Graph

**Stale results after writes**
`graph get` is cached. After a series of writes, expect a short delay before the graph reflects them. Re-run after a few seconds, or restructure logic so it does not depend on immediately-fresh graph data.

**Broken cross-references**
If a file references `domain/slug` and that target doesn't exist, the link won't resolve in the graph. Use `cargo-ai context runtime browse --path <domain>` to verify the target exists before writing the reference, or pipe `graph get` through `jq` to enumerate dangling refs (see `references/examples/graph-queries.md`).

## When to escalate

If the CLI errors and `--help` plus the notes above don't get you unstuck — **file a workspace management report** rather than retrying silently. See [`cargo-workspace-management/SKILL.md`](../../cargo-workspace-management/SKILL.md) (Reports section).

```bash
cargo-ai workspaceManagement report create \
  --title "context <subcommand> fails with <errorMessage>" \
  --description "Ran: cargo-ai context ...   Got: {...errorMessage...}   Expected: ..."
```
