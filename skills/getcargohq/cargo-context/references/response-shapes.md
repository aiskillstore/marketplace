# Response shapes

JSON response structures returned by Cargo CLI commands used in the `cargo-context` skill.

> Unlike the workspace storage / orchestration skills, the context CLI commands return shapes that depend on the underlying file content and on the graph derived from it. Field names below are the ones used throughout this skill's examples (`nodes`, `slug`, `frontmatter`, `links`, etc.); for a given workspace, confirm the exact shape with `--help` and a one-shot invocation before scripting against it.

## Error shape (every command)

Failed commands exit non-zero and return:

```json
{
  "errorMessage": "..."
}
```

`cargo-ai context runtime edit` fails with this shape when `--old-string` matches zero or multiple times in the target file. See `references/troubleshooting.md`.

## cargo-ai context runtime browse

Lists entries at the sandbox root (or under `--path`). Returns the directory listing — file and folder names under the requested path. Combine with `cargo-ai context runtime read --path <file>` to inspect any entry.

```bash
cargo-ai context runtime browse
cargo-ai context runtime browse --path persona
```

Run once at the top of a session to confirm the exact JSON shape for your workspace.

## cargo-ai context runtime read

Returns the file content at `--path`, optionally restricted to `--start-line`/`--end-line` (1-indexed, inclusive). Use this to read frontmatter + body before editing.

```bash
cargo-ai context runtime read --path persona/vp-sales-mid-market.md
cargo-ai context runtime read --path play/inbound-trial-to-paid.md --start-line 1 --end-line 40
```

## cargo-ai context runtime write

Creates (or overwrites) the file at `--path` and pushes a commit to the default branch. Returns the commit metadata. The `--commit-message` flag controls the commit subject.

```bash
cargo-ai context runtime write \
  --path persona/vp-sales-mid-market.md \
  --content "<file body with frontmatter>" \
  --commit-message "Add VP of Sales mid-market persona"
```

On failure it returns the generic error shape (see [Error shape](#error-shape-every-command)); the context-specific case to know is a denied write under `.files/` (update those via Content instead). Frontmatter is **not** validated — a file missing `title`/`description` or with malformed frontmatter is written, not rejected. Failure reasons are enumerated in `references/troubleshooting.md`.

## cargo-ai context runtime edit

Replaces a single exact substring in the file at `--path` and pushes a commit. `--old-string` must match **exactly once** — read the file with `runtime read` first and copy the substring verbatim, whitespace included. Pass an empty `--new-string` to delete the match. Returns the commit metadata on success.

```bash
cargo-ai context runtime edit \
  --path global/positioning.md \
  --old-string "We help RevOps automate workflows." \
  --new-string "We help RevOps run AI-native GTM motions." \
  --commit-message "Refresh positioning one-liner"
```

On failure it returns the generic error shape — most often because `--old-string` matched zero or multiple times. Frontmatter is not validated, so an edit that strips `title`/`description` still applies. Failure reasons are enumerated in `references/troubleshooting.md`.

## cargo-ai context runtime execute

Runs a shell command in the sandbox and returns its stdout / stderr / exit code. **Does not push** any file changes — use only for inspection (`grep`, `ls`, `pwd`, `find`). `--args` is a JSON array of string arguments; omit for a no-arg command.

```bash
cargo-ai context runtime execute --command grep --args '["-r","-l","persona/vp-sales-mid-market","."]'
cargo-ai context runtime execute --command ls --args '["-1","persona"]'
cargo-ai context runtime execute --command pwd
```

## cargo-ai context graph get

Returns the typed knowledge graph derived from every markdown/MDX file in the context repo. Shape used throughout `references/examples/graph-queries.md`:

```json
{
  "nodes": [
    {
      "slug": "persona/vp-sales-mid-market",
      "frontmatter": {
        "title": "VP of Sales, mid-market",
        "description": "Owns pipeline, quota, and rep productivity at a 200–2,000-person company."
      },
      "links": [
        "medium/linkedin-outbound",
        "medium/exec-warm-intro",
        "objection/we-already-have-an-ai-sdr"
      ]
    }
  ]
}
```

**Key fields:**

- `nodes[].slug` — `domain/slug` (no `.md` extension), the canonical identifier used in cross-references.
- `nodes[].frontmatter` — parsed YAML frontmatter. `title` and `description` are required on every file.
- `nodes[].links` — outbound `domain/slug` references found in the body. Missing or empty when the file links nowhere.

For ready-to-run queries (count per domain, dangling references, plays missing proof, inbound references to a node), see `references/examples/graph-queries.md`.
