# Context repo conventions

The conventions below are inherited from the canonical context repository [`getcargohq/cargo-workspaces`](https://github.com/getcargohq/cargo-workspaces). When in doubt, read its `README.md` and the `_template.md` file in the relevant domain.

## Domains

| Domain | Purpose |
|---|---|
| `global/` | Company-level context: mission, voice, positioning, narrative, pricing |
| `icp/` | Ideal Customer Profile segments |
| `persona/` | Buyer personas (roles inside an ICP) |
| `jtbd/` | Jobs-to-be-done framings |
| `alternative/` | Competitors, substitutes, status quo |
| `client/` | Customer profiles, case studies, reference accounts |
| `insight/` | Market insights and observations |
| `medium/` | Channel playbooks (email, LinkedIn, cold call, etc.) |
| `objection/` | Objections + responses + proof |
| `play/` | GTM plays (signal → audience → channel → sequence → outcome) |
| `proof/` | Atomic proof points (metrics, quotes, case data) |
| `signal/` | Buying signals and intent triggers |

## File conventions

- **Filename:** `kebab-case.md` (e.g. `vp-sales-mid-market.md`). Use ASCII letters, digits, and hyphens only.
- **Frontmatter:** YAML with `title` and `description` on every `.md`/`.mdx` file. This is a **strong convention, not enforced** — a write with missing, empty, or malformed frontmatter is still committed; it just indexes poorly. The graph reads `title` (fallback: filename) and `summary` (fallback: first paragraph), **not** `description`. See [Source references and the knowledge graph](#source-references-and-the-knowledge-graph).
- **Cross-references:** `domain/slug` form, **no `.md` extension** (e.g. `persona/vp-sales-mid-market`). To register as a graph **edge**, a reference must appear as a wikilink, a markdown link, or a frontmatter `references:` entry (see below) — a bare `domain/slug` or file path in plain prose is not parsed.
- **Templates:** each domain ships an `_template.md`. Read it (`cargo-ai context runtime read --path <domain>/_template.md`) before authoring a new entry. `_template.*` files are excluded from the graph — never reference them.
- **Bidirectional links:** keep cross-refs symmetric when it makes sense — a `play` that targets a `persona` should appear in the persona's `Preferred channels` or `How we land` sections when relevant.

## Source references and the knowledge graph

The graph is built from **every `.md`, `.mdx`, `.yaml`, and `.yml` file** in the repo (any folder; only `.git/` is excluded). Each file becomes a node. **Edges are created only from these three forms** — everything else is invisible to the graph:

1. **Frontmatter `references:` list** (preferred for source citations — keeps prose clean, and the edge carries a `frontmatter` origin):

   ```yaml
   ---
   title: AgoraPulse expansion thesis
   description: Why the AgoraPulse account is ready for a multi-thread expansion play.
   references:
     - outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md
   ---
   ```

2. **A Markdown link in the body** — use when the citation needs surrounding prose. Write standard `[label]` immediately followed by `(path)` link syntax pointing at the source file, e.g. an "AgoraPulse session outcomes" anchor linking to `outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes.md`.

3. **Wikilinks in the body** (extension optional):

   ```markdown
   [[outputs/sales-notes/2026-06-05-agorapulse-build-session-1-outcomes]]
   ```

### Linking rules

- **Never cite a source as a bare path in prose.** A `Source:` line that just mentions `outputs/sales-notes/foo.md` as plain text is **not** parsed and creates **no** edge. Always use one of the three forms above.
- **Prefer root-relative paths.** Paths resolve root-relative first (from the repo root), then relative to the citing file's directory. Root-relative paths work regardless of where the citing document lives.
- **Extensions are optional.** The resolver auto-tries `.md`, `.mdx`, `.yaml`, `.yml` (in that preference order). Including the extension is fine too.
- **The target must exist.** A reference only resolves if the target file is actually in the repo — nonexistent targets become **broken** edges (dead links in the graph UI). Verify the path before citing it (`cargo-ai context runtime browse --path <dir>`).
- **`_template.*` files are excluded** from the graph — don't reference `_template.md` / `.mdx` / `.yaml` / `.yml`.
- **YAML data files:** `title`, `summary`, and `references` are read from top-level keys; YAML bodies produce no link edges.
- **Node title/summary:** titles come from frontmatter `title:` (fallback: filename); summaries from frontmatter `summary:` (fallback: the body's first paragraph, truncated to 280 chars). The graph does **not** read `description` — set a `summary:` if you want the node summary to differ from the first paragraph. Always set `title` so the node is discoverable.

### Citing sources in insight / learning documents

When a document has a **Source** or **Evidence** section, cite the source files in **frontmatter `references:`** — this keeps the prose clean and gives the edges a `frontmatter` origin. Use inline markdown links when the citation needs surrounding prose.

## How to read the context

Start at `global/` for company context. Walk `icp/` → `persona/` → `jtbd/` to understand the buyer. Use `play/` for outbound motions and `objection/` + `proof/` for live conversations.

## Domain templates

The most commonly authored domains. For domains not shown here (`icp/`, `jtbd/`, `alternative/`, `client/`, `insight/`, `medium/`, `signal/`), read the in-repo `_template.md` directly:

```bash
cargo-ai context runtime read --path icp/_template.md
cargo-ai context runtime read --path signal/_template.md
# ...
```

### `global/_template.md`

```markdown
---
title:
description:
---

## Summary

_One-line version._

## Detail

_Full version. Mission, voice, positioning, narrative, pricing — whatever this entry is._

## Source

_Where this comes from. Founder note, brand doc, board deck, prior conversation._
```

### `persona/_template.md`

```markdown
---
title:
description:
---

## Role

- Title:
- Seniority:
- Function:
- Reports to:

## KPIs

-

## Pains

-

## Motivations

-

## Day-to-day

_What this person actually does on a Tuesday._

## Preferred channels

_Cross-ref `medium/...`._

-

## Common objections

_Cross-ref `objection/...`._

-

## How we land

_The angle, the pitch, the moment they get it._
```

### `play/_template.md`

```markdown
---
title:
description:
---

## Hypothesis

_Why this play should work. The bet._

## Trigger

_Cross-ref `signal/...`._

-

## Audience

_Cross-ref `icp/...` or `persona/...`._

-

## Channel

_Cross-ref `medium/...`._

-

## Sequence

1.
2.
3.

## Proof

_Cross-ref `proof/...`._

-

## Success metric

_What we measure. Target._

## Owner

_Role accountable for running this._

## Variants

-
```

### `proof/_template.md`

```markdown
---
title:
description:
---

## Type

_metric | quote | case | benchmark | screenshot_

## Content

_The actual proof point. Number, quote, fact._

## Source

_Where it comes from. Customer, study, internal data._

## Client

_Optional. Cross-ref `client/...`._

## Context

_What claim this supports. Why we cite it._

## Use cases

_Where this shows up: objections, plays, posts, decks._

-
```

### `objection/_template.md`

Objections pair a stated buyer concern with the response and the proof that backs it up:

```markdown
---
title:
description:
---

## Objection

_The buyer's stated concern, in their own words._

## Response

_Our reframe. Short, calm, specific._

## Proof

_Cross-ref `proof/...`._

-

## Personas

_Cross-ref `persona/...` — who raises this most._

-
```

## Authoring rules of thumb

- **One concept per file.** If you're tempted to add a second `## Persona` or a second `## Play` heading inside one file, you actually want two files.
- **Title is a label, description is a hook.** `title` shows up in lists; `description` is the one-line that explains why this entry exists.
- **Cross-refs over duplication.** If a fact already lives in `proof/...`, link to it from the play or objection rather than re-stating it.
- **Atomic proof.** Each `proof/` entry is one fact / quote / metric. Bundled proof points break filtering in the knowledge graph.
- **Repetition threshold for call-derived claims.** A single sales call is anecdote, not evidence. Before promoting an objection / pain / missed-proof claim from call analysis into the context repo, require it to surface across multiple calls. Suggested defaults:
  - Call-rich workspaces (≥ 50 transcripts / quarter): **3 occurrences**.
  - Medium volume: **2 occurrences**.
  - New / call-poor workspaces (< 10 transcripts): **1 occurrence**, and cite the source via frontmatter `references:` (or a markdown link) so the citation registers as a graph edge — see [Source references and the knowledge graph](#source-references-and-the-knowledge-graph).
  The threshold applies to claims, not to facts a call directly confirms (a named customer, a verbatim quote, a competitor explicitly mentioned). See `examples/lifecycle.md` for the full refresh loop.
