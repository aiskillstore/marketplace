# provider-interface

The behavioral contract every graduation-provider adapter script (preflight + graduate) must satisfy, plus the read-side query capability contract used at consumption time. Read this before adding a 4th provider or changing an existing one — the per-provider references under `graduation/` show how each of the three current providers satisfies this contract, not a separate set of rules. Ordinary graduation execution does not need this file; the selected provider reference carries each principle's provider-specific consequence.

## Preflight scripts

- Read-only. Perform no writes, ever.
- Print a JSON verdict to stdout with at minimum `status` (string) and `next` (string, human-actionable guidance) keys. Additional provider-specific diagnostic fields (`cli_installed`, `db_readable`, `has_wiki_scope`, ...) are expected and do not need to match names across providers.
- Exit code 0 if and only if `status == "ok"`. Every other status exits 1.
- `status == "ok"` is the caller's signal that it is safe to proceed to the graduate script — nothing else needs to be re-checked.
- A schema-backed provider must validate both required property names and their types. Missing names and incompatible existing types are different failures: Notion reports `db_props_missing` for the former and `db_prop_type_mismatch` plus `{property,expected,actual}` entries for the latter.

## `create_note` (the graduate script's core operation)

- Must support `--dry-run`. In dry-run mode, the script must make **no provider-side writes and no mutating API calls** — it may still perform read-only calls (e.g. resolving a target) and local-only filesystem scratch work (e.g. a `mktemp`'d payload file, cleaned up on exit) since neither touches the provider's actual state. It must print what it would have done to stderr, plus a JSON object to stdout that is **a superset of the real success shape** (every key the real output has, with placeholder values; extra informational keys are allowed) — not required to match it key-for-key.
- Must resolve/verify its write target before writing to it (a **read dependency precedes the write** — verified in all three: Lark reads the target space before creating a node; Notion's preflight confirms the DB is shared/readable before create; Obsidian resolves the vault's real filesystem path before writing a file into it). A provider adapter must not assume write access implies the target is valid.
- **Every adapter must provide flag-driven frontmatter construction; callers should never need to hand-embed frontmatter into `--content`.** `--content` (when accepted) is body-only. This is a hard requirement on the adapter's *capability* — the flags must exist and, when used, must be what builds the frontmatter. It is not a requirement that every call site pass them.
  - The realization is **not** uniform across providers:
    - **Native structured fields** (Notion): frontmatter flags map to real database properties (Select/Multi-select/Text/Date), physically separate from the page body.
    - **Embedded text block** (Obsidian, Lark): frontmatter flags are assembled into a YAML-formatted text block written as literal content at the top of the note/document. This is not "native" the way Notion's properties are. For Obsidian it matches the platform's own on-disk format exactly. For Lark, this is a human-readable text expression of structured intent; confirmed NOT to survive as parseable YAML through Feishu's markdown conversion — the `---` markers themselves survive as literal text, but nested list entries (`graduated_from`'s `- project: ... / path: ...`) lose their indentation on round-trip, so a YAML parser either errors or silently misassigns `path` as a top-level sibling key instead of a field of the list entry. Treat the Lark frontmatter block as documentation for a human/agent reader, not a machine-re-parseable structure — see `cairn/LOG.md` 2026-07-02 for what was actually observed when this was tested.
  - `--graduated-from` is not a standardized flag across providers: Obsidian and Lark take it as a repeatable `"<project>|<path>"` structured entry (matching production `graduated_from` frontmatter — see `frontmatter.md`); Notion's existing `--graduated-from` takes a single plain-text value written into one `rich_text` property. Same flag name, three different semantics — don't assume interchangeable.
  - Every adapter must provide repeatable `--contributor NAME` and `--graduated-by NAME` capabilities. Each flag occurrence adds one human-readable name to the corresponding list; preserve list shape even when there is only one name, and de-duplicate repeated identities without changing their first-seen order. Identity resolution belongs to the graduation workflow, not the low-level adapter.
  - Low-level adapters must remain backward-compatible when these flags are omitted. The graduation workflow, however, must always pass at least one `--graduated-by NAME` for every new graduation and re-graduation; absence is supported only for legacy/direct low-level calls, not new workflow output.
- Output JSON must include one location/identifier field and one link/URL field, at minimum. Exact field names are provider-appropriate, not standardized (`{id,url}` for Notion, `{path,obsidian_url}` for Obsidian, `{node_token,obj_token,url}` for Lark).
- Must attempt a read-back verification after writing. A verification mismatch or failure degrades to a `warn:` on stderr — it must never roll back or fail the overall operation, since the object/file has already been created.

## `update_note` (re-graduation into an existing target)

- Every provider adapter must expose an explicit update mode that targets the exact location/identifier returned by the original `create_note`. Create mode remains backward-compatible when the update identifier is omitted.
- Update mode replaces the existing note's body and writes the supplied current properties/frontmatter on that same object. It must not create a second provider object and must not append a second copy of the body.
- The graduation workflow, not the low-level adapter, reads the prior provenance and resolves the new de-duplicated `graduated_by` union. The adapter faithfully writes the complete supplied list; it must neither invent identities nor silently merge against provider state.
- Provider identifiers are explicit: Obsidian uses the same vault-relative note path (`--force` authorizes overwrite); Lark requires the existing `node_token`, `obj_token`, and URL; Notion requires the existing page ID. The success JSON returns those same identifiers.
- Replacement mechanics are provider-native: Obsidian atomically replaces the same file; Lark uses the installed CLI's `docs +update --command overwrite`; Notion PATCHes page properties, archives every current top-level child block, then appends the replacement children. Replacement can remove provider-only body content, so re-graduation remains human-confirmed.
- Read-back and `--dry-run` obligations from `create_note` apply equally to update mode.

## `update_index` (optional per provider)

- Not every provider needs this step. When a provider's container structure already serves as the index (Notion: the database's own views/properties), there is no separate index step, and the contract does not require inventing one.
- When a provider does support an index-append step, **it must be idempotent**: before appending, check whether an entry for this note already exists in the index, and skip the append if so. Match on a bounded, unambiguous delimiter (e.g. the markdown link-open form `[$TITLE](` or a WikiLink `[[$TITLE]]`) — a bare substring check produces false positives (an entry titled "Lark CLI 踩坑合集" would substring-match a new graduation titled "Lark CLI") that skip the append and leave the newly-created object orphaned, unreachable from the index, which is worse than the duplicate line this clause exists to prevent.
- Idempotent index-append does not turn create mode into an upsert. A repeated create call may still make another underlying object; re-graduation must select explicit `update_note` mode with the stored original identifier.

## Cross-provider transport and API-surface principles

Learned from real runs across the three providers; each provider reference under `graduation/` carries the provider-specific consequence.

- **`create_note` is not always a pure write.** Some providers must *resolve the target* (space/folder/node) before creating, and resolution needs read access. A wiki provider's "create node" implicitly reads the space, so a write-only grant is insufficient. Model the read dependency explicitly; don't assume write scope alone lets you create.
- **A provider's CLI conveniences may be stricter than its API.** Prefer the provider's raw/native API for graduation writes when its high-level shortcuts add their own preconditions (e.g. literal scope prechecks) that reject otherwise-valid calls.
- **A provider's official CLI is not automatically the most reliable transport.** A CLI that fetches a remote spec to resolve endpoints, or that ignores `HTTPS_PROXY`, can fail in proxied/CI environments while direct REST against the same API works. Verify the transport in the real environment; be ready to fall back to direct REST (curl) with per-request retry for flaky egress (e.g. random SSL EOFs).

## Read side: `query` (documented capability, not an adapter script)

The consumption flow (`consume.md` → Retrieval) needs a read path into the knowledge base. Unlike the write side, the read side ships **no adapter scripts**: queries are ad-hoc, composed per task by the consuming agent, and freezing them into a script would fix the funnel shape without removing any real complexity. What this contract standardizes is the capability classes, the preference order, and the fallback rules.

### Capability classes

A provider's read-side description must state which of these four query classes it supports, and with what:

1. **Structured** — filter by frontmatter/properties (`type`, `contains`, `tags`, `graduated_from`, ...).
2. **Tag** — enumerate the tag inventory or list notes carrying a tag.
3. **Fulltext** — content search, ideally scoped to the knowledge-base container.
4. **Graph** — follow links/backlinks from a hit to adjacent notes.

Providers are not required to support all four; the funnel in `consume.md` uses what exists and skips what doesn't.

### Rules

- **Provider-native query interfaces are preferred over raw filesystem `grep`.** A native interface queries the provider's semantic index — frontmatter and inline tags unified under one tag query, aliases resolved into backlinks, saved views evaluated — none of which a literal text grep over note files reproduces. Raw grep/direct reads are a *fallback*, not the default.
- **The fallback must stay explicit and available.** When the native interface is unavailable or hits a known unreliability (CLI missing, app not running, false-success exit codes), degrade to direct filesystem/API reads rather than aborting the consumption flow.
- **A query miss is not proof of absence.** Whatever the tier, the funnel ends by scanning the relevant (sub-)INDEX as the recall safety net — see `consume.md` → Retrieval.
- **Write-side counterpart: tag discipline.** Tag-query recall depends on tags chosen at graduation time. Before inventing a new tag, check the provider's tag inventory and prefer reuse over near-synonyms (see the corresponding step in `graduation.md` → Flow).

### Per-provider mapping

- **Obsidian** — the full four classes via the `obsidian` CLI (primitives confirmed present on CLI 1.12; not yet exercised at scale): structured `properties` / `property:read` / `base:query` (Bases saved views, `format=json`); tag `tag name=<tag> verbose` / `tags counts`; fulltext `search` / `search:context` (`path=` scoped to the knowledge folder, `format=json`); graph `backlinks` / `links`. Curation extras for audit-style sweeps: `orphans` / `deadends` / `unresolved`. Reliability caveats are the same ones the write side already documents (`rc=0` false successes, async vault switching, requires the app running) → fallback is direct filesystem reads under the resolved vault path.
- **Notion** — the database *is* the index, so structured query is native: `POST /v1/databases/{id}/query` with property filters (same transport rules as the write side: direct REST + retry, pinned `Notion-Version`). Tag is just a Multi-select property filter, not a separate mechanism. Fulltext `POST /v1/search` is workspace-wide and coarse — filter results back to the KB database. Graph is weak (page mentions only).
- **Lark wiki** — verified read path is tree traversal (`wiki nodes list`) plus INDEX-doc fetch (`docs +fetch`); suite-wide search APIs exist but are **unverified** for this flow — do not rely on them until tested in a real environment.

## Cross-cutting

- Error handling: hard failures call a `die()`-style helper (message to stderr, `exit 1`). Soft/recoverable issues (e.g. a read-back mismatch, a missing optional dependency) print `warn: ...` to stderr and continue.
- macOS Bash 3.2 compatibility is a hard requirement for every bash adapter: no `mapfile`/`readarray`, no associative arrays, no `timeout`/`gtimeout` assumed present. **Iterating a possibly-empty array under `set -u` needs `"${ARR[@]:-}"`, not bare `"${ARR[@]}"`** — confirmed on real bash 3.2.57 that the bare form throws `unbound variable` when the array has zero elements, even though it's declared. Non-bash adapters (e.g. `notion-graduate-batch.py`) are exempt from the bash-specific rules by construction.
- **No shared code between adapter scripts.** Each script is a complete, standalone, top-to-bottom-readable unit — no `lib.sh`. The retry/preflight patterns look similar across providers but check genuinely different conditions (Lark: OAuth scope state machine; Notion: network/SSL flakiness; Obsidian: async vault-load race); a shared helper would either be too generic to save real complexity or would leak provider-specific branching back into the "shared" file. Project Cairn's audience for these scripts (an agent reading the shared graduation core plus one selected provider reference, then invoking one script end-to-end) benefits more from single-file self-containment than from DRY. Revisit only when a 4th provider is added and a genuinely stable common helper becomes visible.
