# Lark / Feishu wiki adapter

> Read [`../graduation.md`](../graduation.md) first — it owns the shared human-confirmed graduation workflow; this file carries only the Lark/Feishu wiki execution path.
> Read [`../provider-interface.md`](../provider-interface.md) only when adding or changing an adapter, not merely to execute this flow.

**Step 0 — preflight (run before any write).** `scripts/lark-preflight.sh` is read-only and returns a JSON verdict: `cli_missing` (not installed → give docs link, pause), `not_authed` (run `lark-cli auth login`), `missing_wiki_scope` (open `wiki:wiki` for user identity in the console, then re-auth), or `ok` (safe to graduate). Don't attempt the write loop until it reports `ok`.

Verified path for graduating into a Feishu knowledge base with `lark-cli`, user identity:

- **Scope:** request the coarse `wiki:wiki` (covers read + write). Granular read scopes (`wiki:space:retrieve` / `wiki:space:read` / `wiki:node:read`) may never enter the user token on CLI-style apps (they don't appear on the user consent page); the write-capable `wiki:wiki` does and reliably lands. Diagnostic: if `--as bot` works but `--as user` reports a missing scope, the block is in the user-authorization path, not the app's published permissions.
- **API:** use native resource commands (`wiki spaces get`, `wiki nodes create`, `wiki nodes list`, `wiki spaces get_node`) + `docs +update`/`docs +fetch`. The `wiki +space-list` / `+node-create` shortcuts do strict literal scope prechecks that don't recognize `wiki:wiki` coverage and reject locally.
- **Write loop:** create mode resolves the target space (`my_library` or a team `space_id`) → `wiki nodes create` (with `parent_node_token` to build the directory tree) → append initial body + frontmatter. Update mode receives the original node/document identifiers and uses the locally verified `docs +update --command overwrite` operation to replace that document. Both modes then `docs +fetch` to verify and maintain the optional INDEX/container link. Parent node = directory/index container; child nodes = individual graduated notes.
- **Executable adapter:** `scripts/lark-wiki-graduate.sh` encodes both loops end-to-end, enforcing the constraints above. Content is piped via stdin to dodge the CLI's cwd-relative `@file` restriction. Run with `--dry-run` to preview the exact native API calls before writing.
  - Frontmatter flags (`--type`/`--summary`/`--contains`/`--tags`/`--graduated-from`/`--contributor`/`--graduated-by`/`--authoring-mode`) are optional but recommended: when any is passed, the script assembles them into a YAML-formatted block prepended to the body (confirmed NOT to survive as parseable YAML after Feishu's markdown conversion — see `references/provider-interface.md` and `cairn/LOG.md` 2026-07-02). Passing none of them preserves the old exact behavior (content written as-is).
  - `--index-doc` append is idempotent: it checks the index doc for an existing `[$TITLE](` entry before appending. Re-graduation uses update mode, so neither the node nor INDEX entry is duplicated.
  - Create: `scripts/lark-wiki-graduate.sh --title T --content body.md --space-id <id|my_library> [--parent-node-token TOK] [--index-doc OBJ_TOKEN] [frontmatter flags…]`
  - Update: add `--update-node-token NODE_TOKEN --update-obj-token OBJ_TOKEN --update-url URL` and pass the full caller-unioned provenance flags; all three target values are required together.

