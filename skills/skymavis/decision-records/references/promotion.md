# Promoting drafts — mechanics

Promotion turns a draft into an accepted decision. **An accepted decision must never reference a
draft** (a breach). When promoting a draft that references other drafts, each reference to a draft
*outside the promoted set* is one of:

| Reference                      | Direction | Resolution                                                                                   |
| :----------------------------- | :-------- | :------------------------------------------------------------------------------------------- |
| `relates_to` (front-matter)    | symmetric | **dereference** — drop here; the referenced draft gains your new counter in its `relates_to` |
| `superseded_by` (front-matter) | forward   | **dereference** — drop here; the referenced draft gains your new counter in its `supersedes` |
| `supersedes` → a draft         | backward  | **blocking** — promote that draft first                                                      |
| `` `DRFT` `` in the body       | content   | **blocking** — promote that draft first (bare or already linked; `--relink` links them all)  |

`supersedes` → an existing **decision** is a real supersession, gated behind `--allow-replace`.

## What `promote` does

`promote <name…>` is advisory — it never silently promotes extras or rewrites refs:

| Situation                             | Result                                                                                                            |
| :------------------------------------ | :---------------------------------------------------------------------------------------------------------------- |
| self-contained                        | promotes it                                                                                                       |
| only **dereferenceable** refs         | refuses; re-run `promote <name…> --deref` (shows the moves)                                                       |
| any **blocking** ref                  | refuses; prints the minimal blocking set to co-promote (your draft highlighted) **and a copy-paste agent prompt** |
| `supersedes` an existing **decision** | refuses; re-run `promote <name…> --allow-replace`                                                                 |

- `promote <name…> --deref` inverts the dereferenceable edges, then promotes — refused if any
  blocking ref is present.
- `promote <name…> --allow-replace` confirms archiving the decisions the draft `supersedes` (the IDs
  are shown in the preview, so the flag is just intent).
- Promote several at once, space- or comma-separated. Refs *within* the set become counter↔counter
  automatically, and the counters are assigned **in the order the arguments are given** — name the
  record the others build on first and it reads as the earlier decision.

**Invariant:** after any promotion, everything the promoted record pointed at refers back to it —
via the inverted edge (`--deref`) or a counter rewrite (co-promoted).

## What the move rewrites

A promotion changes a record's ID *and* its directory, and both ripple. `promote` carries all of it,
so a promoted record needs no hand-correction before commit:

| Rewritten                                            | From → to                                                                          |
| :--------------------------------------------------- | :--------------------------------------------------------------------------------- |
| the H1                                               | `# CONF — <title>` → `# 0016 — <title>` (every accepted record reads `# NNNN — …`) |
| every relative link in the body                      | re-pathed for the extra level (`../../glossary.md` → `../../../glossary.md`)       |
| the mnemonic in prose — its own and every referrer's | `CONF` → `0016`, in the body and in front-matter prose like `summary`              |
| a spelled-out path to the draft file                 | `docs/decisions/drafts/CONF-x.md` → `docs/decisions/accepted/<type>/0016-x.md`     |

Two deliberate exclusions, both because a 4-letter mnemonic also reads as a plausible identifier:

- **Code is never edited.** Fenced blocks, inline code spans, and link targets keep the mnemonic —
  `CONF = "conf"` in an example is an enum member, not a reference.
- **Nothing outside `docs/` is edited.** Every remaining mention (code comments, test names) is
  *listed* after the promotion instead. Work through it by hand and leave the identifiers alone.

`promote` exits non-zero if any link is still broken afterwards, so a failed promotion is loud.
`mdformat` reflows the rewritten paragraphs on commit — that churn is expected.
