# Decision records

This repo records significant decisions as short, numbered documents (ADR-style), held firm once
accepted. Everything lives under `docs/decisions/`, so nothing here is confused with the repo's
other docs.

## Working with an agent (the easy way)

If you use an agent that has the **decision-records** skill installed, just ask — it knows the
lifecycle, mints IDs, runs the tool, and keeps the index and links correct. For example:

- "Capture what we just discussed into a decision draft."
- "Draft an architecture decision: we'll use X for Y."
- "Promote that draft." / "Promote CONF."
- "Supersede our caching decision with a new one that does Z instead."
- "What have we decided about authentication?"
- "Regenerate the decision index."

Promoting and superseding finalize a record, so the agent confirms with you first.

## The lifecycle

A decision moves through three stages, one directory each:

| Stage    | Directory          | Identified by                         | Meaning                                       |
| :------- | :----------------- | :------------------------------------ | :-------------------------------------------- |
| Draft    | `drafts/`          | a 4-uppercase-letter mnemonic (CONF)  | a work-in-progress candidate; edit freely     |
| Accepted | `accepted/<type>/` | a zero-padded counter (0001, 0002, …) | a finalized decision, **held firm**           |
| Retired  | `archived/`        | (keeps its counter)                   | superseded or deprecated; kept for the record |

There is no "proposed" stage — *proposing* a decision is the act of opening a pull request that
promotes a draft. Once a draft lands in `accepted/` it is held firm: changing course means
superseding it with a newer decision, never rewriting it; decider-approved maintenance edits
(clarity, staleness, consistency) are allowed. `<type>` is an open lowercase label you choose
(architecture, product, security, policy, legal, …); each type is its own subdirectory under
`accepted/`.

## Reading the records

Start at [INDEX.md](./INDEX.md) — a generated table of every accepted and retired decision with its
type, summary, status, and tags. Open the records you need; skip `archived/` unless you're tracing
why a decision changed.

## Authoring & cross-referencing

- Copy `_template.md` for a decision, or `drafts/_template.md` for a draft, and fill it in.
- Mint a draft's 4-letter ID yourself (a mnemonic of the topic). Accepted records get the next
  global counter automatically when a draft is promoted.
- Refer to another record by writing its ID inline — the tooling renders IDs as links and keeps them
  correct when files move. Never hand-write a path to a record.

## Promotion & superseding

Promotion turns a draft into the next accepted decision; it is a finalizing step that needs human
sign-off. To replace an existing decision, set the draft's `supersedes` front-matter to that
decision's counter. On promotion (confirmed with `--allow-replace`) the tool **automatically retires
the superseded record for you** — it moves the old record to `archived/`, flips its status to
`superseded`, and records the new counter in the old record's `superseded_by`. You never hand-edit
the record being replaced.

## The tooling

`scripts/decisions.py` generates the index and cross-links, validates the tree, and promotes drafts:

```sh
python scripts/decisions.py build [--relink]            # regenerate INDEX.md (+ refresh links)
python scripts/decisions.py check                       # validate (CI-safe; exit 1 if stale)
python scripts/decisions.py promote <name…> [--deref] [--allow-replace]   # draft(s) -> accepted/
python scripts/decisions.py rename-draft-id <name> <NEW>                  # re-ID a draft
python scripts/decisions.py install [repo]              # adopt in a repo: symlink + pre-commit
```

Run `python scripts/decisions.py --help` for the rest. This convention is provided by the
**decision-records** skill, which is the source of truth for how the tooling behaves; this file is a
local orientation guide.
