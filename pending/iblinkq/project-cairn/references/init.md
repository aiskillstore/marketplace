# init

Initialize or retrofit Project Cairn in a project. This is an interactive setup process; ask before writing.

## Decisions to collect

1. Project name and one-line summary.
2. Whether `cairn/` is committed, ignored, or privately synced (`git_policy`: `track` | `ignore` | `private_sync`). If `cairn/Reference/` (see decision list in `assets/templates/config.yaml`) is expected to hold externally-owned or sensitive raw material — a client's PDF, a call transcript — offer a separate, optionally more conservative `reference_git_policy` for it alone; omitting it means Reference/ simply inherits `git_policy`.
3. Graduation provider(s): collect zero or more targets (e.g. Obsidian, Lark/Feishu CLI, Notion). "Not yet" is a first-class answer — the user may defer connecting any knowledge base until the first graduation (see "Deferred graduation provider" below).
4. For each provider, collect target and index location. Do not hardcode concrete Obsidian vault paths or directory names; those are user/project choices.
5. Historical knowledge strategy (`migration_mode`). Default: `start_fresh`.
6. Documentation language used when writing generated files (`AGENTS.md`, `cairn/LOG.md`, `cairn/ROADMAP.md`, topic notes). Default: `en`.

Resolve each decision through the cascading defaults below instead of re-asking from scratch every project.

## Cascading defaults

Config resolves through three layers, highest wins (same model as git/npm/eslint):

1. **Project-level** — `.cairn/config.yaml` in the project. Overrides everything.
2. **User-level** — `~/.config/cairn/config.yaml`, shaped like `assets/templates/user-config.yaml`. Personal defaults: a `providers` directory keyed by provider type (look up by name, e.g. `providers.notion` — it is a dict, not a list to scan) holding the targets the user normally graduates to, plus their usual `git_policy` / `migration_mode` / `language` under `defaults`.
3. **Built-in** — the template defaults shipped in `assets/templates/config.yaml` (`knowledge_dir: cairn`, `migration_mode: start_fresh`, `language: en`).

Credentials (tokens, vault secrets, Lark app secrets) never go in either config file. Keep them in `.env` or a secret store and reference them by name; they are never committed.

### First run vs. later runs

- **First run (no user-level config):** ask the full question set above. After collecting answers, offer to save them as user-level defaults at `~/.config/cairn/config.yaml`, so the next project does not repeat the interview.
- **Later runs (user-level config exists):** show the resolved defaults and offer one-key reuse, phrased in the project's resolved `language` (e.g. in English: "Reuse usual config? [Enter]"). Only re-ask the decisions the user wants to change.
- **Non-interactive mode:** when a user-level config exists, apply the resolved values silently without prompting (for scripted or unattended setup).

### Documentation language

Decision #6 resolves through the same three layers above. One extra rule governs what to *suggest* on a first run, when no user-level default exists yet — check in order, stop at the first hit:

1. **Explicit global language directive** — if the current agent's own user-level instructions state one (e.g. a Codex `~/.codex/AGENTS.md` or a Claude Code `~/.claude/CLAUDE.md` saying "respond in Chinese" / "用中文回答"), suggest that language.
2. **Conversation language** — otherwise, suggest the language of the user's most recent message.
3. **English** — otherwise (a very first short instruction, mixed-language input, or non-interactive/scripted init), fall back to English.

This is a suggested default, not a silent decision: the user still confirms or overrides it like any other init question. Once confirmed, `language` is saved into `~/.config/cairn/config.yaml` exactly like `git_policy` / `migration_mode`; the next `cairn init` — on either agent, in this project or a new one — reuses it via the "later runs" one-key flow above instead of re-detecting or re-asking.

When the resolved `language` is not English, write `AGENTS.md` / `cairn/LOG.md` / `cairn/ROADMAP.md` / topic notes in that language: translate prose and section headings, but keep `{{PLACEHOLDER}}` tokens, frontmatter keys, and file names exactly as the English templates in `assets/templates/` define them, and preserve the same heading sequence. For Chinese, match established terms — including heading labels — using `references/zh-glossary.md` so wording stays consistent across independently-initialized projects.

### What lands in the project

The project-level `.cairn/config.yaml` stores the **fully resolved (frozen) config**, not just the diff against user-level defaults — so a collaborator who clones the repo gets a complete, portable config without needing the author's `~/.config/cairn`. (A sparse "diff-only" form is a possible later optimization; the current format freezes the full result.)

### Multiple providers

When more than one provider is enabled, write `graduation.providers` as a list instead of the single `provider`/`target`/`index` keys (see `assets/templates/config.yaml` for the shape). Each entry needs `target` + `index` plus whatever **provider-specific adapter settings** the writer requires — these are not uniform across providers:

- Obsidian: `link_format: wikilink`, vault-relative `target`/`index`.
- Lark/Feishu wiki: `space_id`, `index_node_token`, `scope: wiki:wiki`, `api: native`, `identity: user`, `link_format: url` (see `graduation/lark-wiki.md`).

Collect these per-provider details at init time; do not assume one provider's fields apply to another.

### Multi-provider `AGENTS.md` rendering

When more than one provider is enabled, `AGENTS.md`'s three `Init configuration` placeholder lines each list every enabled provider, not just one:

- `{{GRADUATION_PROVIDER}}` → `<Provider1> (<primary identifying value>), <Provider2> (<primary identifying value>)`
- `{{KNOWLEDGE_INDEX}}` and `{{GRADUATION_TARGET}}` → `<Provider1> → <value>; <Provider2> → <value>`, semicolon-separated, one clause per provider

Example (Obsidian + Notion): `Graduation provider(s): Obsidian (vault: ExampleVault), Notion (database: example-db-id-0000)`.

This joined multi-value form applies specifically to the three `Init configuration` bullets. The same `{{KNOWLEDGE_INDEX}}` / `{{GRADUATION_TARGET}}` tokens also recur in two other template sentences — the "Knowledge base consumption reflex" bullet and the "Knowledge distillation rules" bullet. For multi-provider projects, don't repeat the full joined value there; point back to the section instead: replace `check {{KNOWLEDGE_INDEX}} first` with `check the configured provider indices first (see Init configuration above)`, and `distilled into {{GRADUATION_TARGET}} via the graduation mechanism` with `distilled into the configured provider target(s) via the graduation mechanism (see Init configuration above)`. Single-provider projects keep the direct substitution unchanged in all four locations.

### Deferred graduation provider (connect later)

Requiring a provider at init would gate first contact on having Obsidian/Notion/Lark ready — but the core mechanisms (LOG, topic notes, audit, consuming the project's own notes) need no provider at all; graduation is a cross-project feature, not a first-contact requirement. So "not yet" is a valid answer to decision #3. When the user defers:

- Skip decision #4 and every provider preflight.
- Freeze the deferred state into `.cairn/config.yaml` as `provider: none` under `graduation:` (form (c) in `assets/templates/config.yaml`) — no `target`/`index` keys, no `providers:` list.
- Do not write `none` into `~/.config/cairn/config.yaml`: deferring is a per-project choice, and the user-level `providers` directory holds real targets only. When a user-level config with saved providers exists, still offer the one-key reuse — but a deliberate "not yet" wins over the saved defaults.
- Everything else about init proceeds unchanged.

Late binding: the provider decisions (#3–#4) are collected at the first graduation instead — see `graduation.md` → "Deferred provider". Until then, `consume.md`'s external INDEX check has no target and reduces to the project's own `cairn/` notes, and `audit.md` surfaces confirmed candidates left waiting.

**`AGENTS.md` rendering when deferred** — the three `Init configuration` lines:

- `Graduation provider(s):` → `none yet (deferred — connect a knowledge base at first graduation)`
- `Knowledge base index:` and `Graduation target:` → `not configured yet`

And the two body sentences that reuse the same tokens:

- The "Knowledge base consumption reflex" bullet becomes: `Before work whose reusable kernel — any conclusion it produces or depends on — would be graduation-worthy, consult this project's own cairn/ topic notes; no external knowledge base is connected yet (provider deferred — see Init configuration above), so the external index check and cairn/Cited.md citations activate once one is connected.`
- In the "Knowledge distillation rules" bullet, replace `distilled into {{GRADUATION_TARGET}} via the graduation mechanism` with `distilled via the graduation mechanism once a knowledge base is connected (provider deferred — see Init configuration above)`.

When a provider is connected later, restore all these locations to the standard single-/multi-provider rendering above. Translate per the project's `language` (Chinese: 暂缓对接, see `references/zh-glossary.md`).

### Provider target naming

Any human-facing name for a graduation target — an Obsidian folder, a Notion database title, a Lark/Feishu wiki space — is the **user's** to choose, not Project Cairn's. Ask for it explicitly during provider collection (decision #4) and freeze the answer into `.cairn/config.yaml`; never default it to "Project Cairn" or any other tool-authored string, even when Project Cairn itself is the project being initialized. When a provider adapter script needs the name to create something new (e.g. `notion-init-db.sh --title`), pass the collected value — the script should refuse to invent one.

### Tool-backed provider preflight

A provider that depends on an external tool (Lark/Feishu CLI, Notion API, a sync binary…) has out-of-band setup the project cannot assume: the tool installed, authorized, and granted the right permissions. The moment the user picks such a provider, **detect the dependencies automatically — do not ask the user "is it installed?"**. Run the provider's preflight and act on the verdict:

1. **Dependencies present → continue** to the next init step.
2. **Missing → give the official install/docs link, AND offer to install it for the user**: "Want me to install it now?"
   - User confirms → the agent runs the documented install commands directly, then re-runs the preflight and continues.
   - User declines → pause; let them install manually, then resume.
3. **Installed but not authorized / missing permission → guide** through the exact auth/console step from the preflight's `next` field (don't fail on the first real write).

**Lark/Feishu wiki provider:**
- Detect: run `scripts/lark-preflight.sh` (read-only) → JSON `status` ∈ `cli_missing` / `not_authed` / `missing_wiki_scope` / `ok`, each with the exact next action in `next`.
- Install (offer to run for the user on confirmation): `npm install -g @larksuite/cli && npx skills add larksuite/cli -y -g`, then `lark-cli config init` and `lark-cli auth login --recommend`. Docs: <https://github.com/larksuite/cli>.
- The console step (open the coarse `wiki:wiki` scope for the **user** identity) is inherently manual — relay the preflight's instruction; the agent cannot click it. See `graduation/lark-wiki.md`.

**Notion provider:**
- Detect: run `scripts/notion-preflight.sh --db <DATABASE_ID>` (read-only) → JSON `status` ∈ `not_authed` / `db_unshared` / `db_props_missing` / `db_prop_type_mismatch` / `net_error` / `ok`, each with the exact next action in `next`; type mismatches include stable `{property,expected,actual}` details.
- Setup (mostly manual — credentials/account steps the agent cannot do): create an internal integration at <https://www.notion.so/profile/integrations> (Read+Insert+Update content) → put its `ntn_` token in `.env` as `NOTION_API_TOKEN` → create/pick the knowledge-base **database** and **share it with the integration** (••• → Connections). The agent CAN create the DB + property columns via REST once the token is set and a parent page is shared.
- Transport: direct REST via curl (the `ntn` CLI is unreliable behind an HTTPS proxy). See `graduation/notion.md`.

**Obsidian provider:**
- Detect: run `scripts/obsidian-preflight.sh --vault "<vault name>" [--target "<folder>"] [--index "<folder>/INDEX.md"]` (read-only) → JSON `status` ∈ `cli_missing` / `app_unreachable` / `vault_unknown` / `vault_unreachable` / `ok`, each with the exact next action in `next`.
- Install: unlike Lark/Notion, there is **no command the agent can run to install this** — the `obsidian` CLI ships inside the Obsidian.app bundle itself (1.12+) and is enabled with a GUI toggle: Settings → General → "Command line interface". Relay that exact step and stop; step 2's "offer to install it" does not apply here. Docs: <https://help.obsidian.md/cli>.
- Setup: the target **vault** must already be registered with Obsidian (opened at least once via File → Open vault) and the desktop app must be running when preflight/graduation runs — the CLI talks to a live instance, not vault files directly.
- Reliability note: switching the CLI's active vault is asynchronous and its exit codes are not trustworthy signals of success/failure in general — `obsidian-preflight.sh` retries past known-empty-response and known-nonzero-exit-but-actually-failed cases; don't reimplement a one-shot check against this CLI elsewhere.
- Writing: `scripts/obsidian-graduate.sh` writes the note directly to the vault's filesystem (not through the CLI) and owns YAML frontmatter construction, including the structured `graduated_from` list. See `graduation/obsidian.md`.

## Files to create or update

- `AGENTS.md` — from `assets/templates/AGENTS.md`, substituting the five placeholders.
- `CLAUDE.md` — from `assets/templates/CLAUDE.md` (one line `@AGENTS.md`).
- `.cairn/config.yaml` — from `assets/templates/config.yaml`, with the collected values frozen in. `{{SKILL_SPEC_DATE}}` is stamped automatically from `references/upgrade.md`'s "Current spec date" — it is not a user decision and is never asked; it anchors later instance-drift checks (see `upgrade.md`).
- `cairn/LOG.md` — from `assets/templates/LOG.md`.
- `cairn/ROADMAP.md` — optional; only when the project has goals that outlast one session.

Do not pre-create empty topic notes, `Reference/`, or `Cited.md`. Those are created on first trigger.

## History handling

Do not auto-rewrite historical documents. If historical content exists, offer inventory (`inventory_only`) or selective migration (`selective_migrate`) as a separate, explicit action the user confirms — never as part of init itself.

`.cairn/config.yaml` is the machine source of truth. `AGENTS.md` may summarize the same provider target(s) for humans, but tools read the config file.
