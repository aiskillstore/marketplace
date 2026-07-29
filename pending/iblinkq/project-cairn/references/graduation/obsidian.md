# Obsidian adapter

> Read [`../graduation.md`](../graduation.md) first — it owns the shared human-confirmed graduation workflow; this file carries only the Obsidian execution path.
> Read [`../provider-interface.md`](../provider-interface.md) only when adding or changing an adapter, not merely to execute this flow.

**Step 0 — preflight (run before any write).** `scripts/obsidian-preflight.sh --vault "<vault name>" [--target "<folder>"] [--index "<folder>/INDEX.md"]` is read-only and returns a JSON verdict: `cli_missing`, `app_unreachable`, `vault_unknown`, `vault_unreachable`, or `ok`. Don't write until `ok`.

Verified path for graduating into an Obsidian vault:

- **The `obsidian` CLI is used only to resolve the vault path (read dependency) and, optionally, to read a note back for verification — not to write the note.** `obsidian create` takes content as a shell argument, the same length/quoting fragility Lark's adapter routes around with stdin; here the note is written directly to the vault's filesystem instead.
- **Frontmatter is native YAML embedded in the note**, not external properties (Notion) and not left for the caller to hand-embed (Lark). The adapter owns frontmatter construction from flags, the same way `notion-graduate.sh` owns DB properties.
- **`graduated_from` is a structured list of `{project, path}` entries**, not a scalar — see `frontmatter.md` → "`graduated_from` shape". Verified against notes already in production; several cite more than one source.
- **`[[wikilinks]]` pass through unchanged.** Obsidian is the one provider with native WikiLink support (`config.yaml`'s `link_format: wikilink`) — no rewrite step, unlike Notion's two-pass mention conversion.
- **Overwrite protection and update mode.** A direct filesystem write can silently clobber an existing note with the same title, so create mode refuses to overwrite. Re-graduation deliberately passes `--force`, atomically replacing that same vault-relative path with the full current note; the idempotent INDEX check preserves one `[[Title]]` entry.
- **Two real CLI reliability gaps found while building this** (see `obsidian-preflight.sh` for the fixes): switching the CLI's active vault is asynchronous (first query after a switch can return an empty result with `rc=0`, not an error); several commands (e.g. reading a missing file) also return `rc=0` on failure, with the error only visible in the printed text. Don't trust a one-shot check or a bare exit code against this CLI.
- **Executable adapter** (`--dry-run` previews the frontmatter and target path without touching the filesystem):
  - `scripts/obsidian-graduate.sh --vault "<name>" --title T --target "<folder>" [--content body.md] [--index "<folder>/INDEX.md"] [--summary …] [--contains a,b] [--tags a,b] --graduated-from "<project>|<path>" [--graduated-from … repeatable] --contributor Alice --graduated-by Alice [--authoring-mode …] [--force]` — writes the note, optionally appends a `[[WikiLink]]` line to the INDEX file (creating it if it doesn't exist yet).

