# upgrade

Bring an already-initialized project instance up to the current skill spec, or measure how far it has drifted. `cairn init` freezes the spec of its day into the project (AGENTS.md wording, config shape, LOG conventions); the skill keeps evolving, and nothing updates the frozen copy automatically. This reference is both the detection checklist and the execution manual for closing that gap.

**Current spec date: 2026-07-16**

## Two layers of "upgrade" — keep them apart

1. **The skill copy** (the installed files under the agent's skills directory). Out of scope here: the skill is documentation-only, has no self-update, and the user refreshes it however they installed it (re-run the install command / git pull).
2. **The project instance** (the project's `AGENTS.md`, `.cairn/config.yaml`, `cairn/LOG.md` conventions, and knowledge-base notes it graduated). This is what this reference upgrades.

This is a **pull model**: upstream changes never notify anyone. Drift is tolerated until an audit or an explicit upgrade request surfaces it. An instance older than its skill copy is the dangerous state (agents act on new references against old instance files); an instance matching an old skill copy is internally consistent and harmless until the copy is refreshed.

## Running an upgrade

1. Read `skill_spec_date` from the project's `.cairn/config.yaml`.
   - **Missing field** → treat as predating every entry: run the full changelog below.
2. Walk the changelog entries **newer than that date**, oldest first. For each: run **Detect**; if drifted, apply **Fix** according to its safety level — `auto` fixes may be applied directly (show the diff), `confirm` fixes are proposed and wait for the user.
3. When all entries are handled, stamp `skill_spec_date` in `.cairn/config.yaml` with the current spec date above (add the field if absent).
4. Record the upgrade as one `cairn/LOG.md` entry — what was checked, what was fixed, what was declined — same as an audit run logs itself.

`cairn audit` runs steps 1–2 as a drift check and reports findings without fixing (see `audit.md`); a user-requested upgrade runs all four steps.

## Maintaining this changelog (skill-author discipline)

Every spec change must answer one question before it lands: **does it affect already-initialized instances or already-graduated notes?** If yes, add an entry here in the same commit and bump the current spec date to the change's date. Skill-internal edits (wording, routing, new provider adapters) that leave existing instances valid do not get entries. A missed entry means that drift is never detected anywhere — this discipline is the single point of failure of the whole mechanism.

Entry format — four fixed fields:

- **Affects**: which instance surface (`AGENTS.md` / `config` / `LOG` / `knowledge-base notes` / `user environment`).
- **Detect**: one concrete, executable check.
- **Fix**: the repair action.
- **Safety**: `auto` (mechanical, apply with diff shown) or `confirm` (changes meaning, target, or anything outside the project — ask first).

## Changelog (oldest first)

### 2026-07-01 — LOG entries are reverse-chronological, newest at top

- **Affects**: `cairn/LOG.md` (+ its intro line).
- **Detect**: compare entry dates top-to-bottom; ascending order (oldest first) or new entries appended at the bottom = drifted. Also check the intro line states newest-at-top.
- **Fix**: re-sort entries newest-first and fix the intro line. Use in-entry dates as ordering evidence; where several entries share a date, preserve their relative order only if intra-day sequence is evidenced (e.g. one entry references another), otherwise keep file order within the day.
- **Safety**: `auto` when dates are unambiguous; `confirm` when ordering evidence is thin.

### 2026-07-03 — provider `target`/`index` are container-relative paths (no vault/root prefix)

- **Affects**: `config` (`graduation.target` / `graduation.index`, single-provider keys or `providers:` list entries).
- **Detect**: for filesystem-backed providers (Obsidian), a `target`/`index` that is an absolute path or begins with the vault's own name (double-nesting, e.g. `MyVault/30_kb/...` for vault `MyVault`) = drifted.
- **Fix**: rewrite to vault-relative (e.g. `30_kb/INDEX.md`). Latent until the first graduation runs, then writes land in the wrong place — fix before any graduation.
- **Safety**: `confirm` (changes where future graduations write).

### 2026-07-03 — consumption reflex uses the semantic test, not trigger words

- **Affects**: `AGENTS.md` ("Knowledge base consumption reflex" bullet).
- **Detect**: the bullet lacks the graduation-symmetry semantic test — "before work whose reusable kernel (any conclusion it **produces or depends on**) would be **graduation-worthy**, check the index first" — e.g. it still lists trigger keywords or unconditionally says "always check".
- **Fix**: replace the bullet with the current template wording (`assets/templates/AGENTS.md`), translated per the project's `language`, keeping the project's own `{{KNOWLEDGE_INDEX}}` substitution.
- **Safety**: `auto` (mechanical swap to template text; show the diff).

### 2026-07-03 — user-level cascading defaults exist (`~/.config/cairn/config.yaml`)

- **Affects**: `user environment` (nothing inside the project instance itself).
- **Detect**: `~/.config/cairn/config.yaml` absent while the user has at least one initialized project.
- **Fix**: offer to create it from this project's resolved config (shape: `assets/templates/user-config.yaml`) so future inits reuse defaults one-key. Declining is fine; this entry is an offer, not a repair.
- **Safety**: `confirm` (writes outside the project).

### 2026-07-03 — `graduated_from` paths are project-relative

- **Affects**: `knowledge-base notes` (already-graduated notes in the configured provider).
- **Detect**: any `graduated_from` entry whose `path` is absolute (leading `/` or a machine-specific prefix) = drifted.
- **Fix**: rewrite the `path` values to project-relative. Fold into the next re-graduation of that note when one is pending; otherwise fix directly.
- **Safety**: `confirm` (edits knowledge-base content).

### 2026-07-15 — `skill_spec_date` field introduced in `.cairn/config.yaml`

- **Affects**: `config`.
- **Detect**: the field is missing.
- **Fix**: run the full changelog above (missing field = predates everything), then stamp the field with the current spec date. This entry is the cold-start path for every instance initialized before the field existed.
- **Safety**: `auto` (the stamp itself; individual fixes above keep their own levels).

### 2026-07-16 — human provenance and optional origin quotes

- **Affects**: `project topic notes`, `knowledge-base notes`, stored graduation identifiers, and Notion provider database schemas.
- **Detect**: a topic created or substantively updated on/after 2026-07-16 has safely identifiable human contributors but no `contributors`; a graduation on/after 2026-07-16 lacks non-empty `graduated_by` on either side; or Notion preflight reports missing/wrongly typed `contributors` / `graduated_by` Multi-select properties. Legacy untouched notes without the fields are not drifted. Also flag an origin-quote section that is empty, unattributed, or knowingly retained on only one side after graduation because of an unresolved disclosure risk. For a previously re-graduated topic, search its provider container for duplicate same-title objects or repeated body content; if duplicates exist or the project did not retain the original provider identifier needed by update mode, the prior create-only flow drifted.
- **Fix**: add and de-duplicate the two identity lists when the identities can be confirmed; add or correct the two Notion Multi-select properties before the next graduation; backfill legacy notes only when touched or re-graduated. Remove, explicitly redact, or replace risky direct wording with a labeled scene summary on both project and knowledge-base copies after human confirmation. Preserve one canonical provider object and its identifier for future explicit update mode; propose archiving/removing accidental duplicates only after human review. Existing canonical notes are updated in place: Obsidian same path + `--force`, Lark stored node/document identifiers, Notion stored page ID.
- **Safety**: `auto` for adding confirmed identities inside the project and de-duplicating list values; `confirm` for changing provider schemas, external knowledge-base notes, attribution, quotation, or redaction.
