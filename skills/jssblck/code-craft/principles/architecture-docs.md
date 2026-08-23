# Architecture docs are a stable map

> Keep a short, durable description of boundaries and invariants. Update the map
> when code moves; keep churny detail in the code.

From Matklad's `ARCHITECTURE.md` guidance. A good architecture doc is the thing
a new contributor (human or agent) reads to know where code lives and why,
without reading all of it.

## What goes in

- **A plain-language overview.** One or two paragraphs: what problem this solves
  and the shape of the solution. Written for someone who has never seen the
  repo.
- **Coarse boundaries.** The handful of major modules/layers and what each owns.
  Name the important files, types, and traits/interfaces, so the reader can
  jump. A codemap, not a tutorial.
- **Invariants and cross-cutting concerns.** The rules that hold across the
  system: "all external input is parsed in `boundary/` before reaching `core/`",
  "the renderer never touches the network", "gates fail closed."
- **Deliberate absences.** What is intentionally *not* there or *not* allowed:
  "no generic plugin scheduler, watch is hand-rolled", "Win32 calls stay out of
  the logic layer." Absences are as load-bearing as presences and far less
  discoverable from the code.

## What stays out

- Implementation detail that churns: function-level behavior, exact signatures,
  step-by-step algorithms. Those live in code comments and module docs, where
  they sit next to the thing they describe and get updated with it.
- Fragile links to specific line numbers or volatile paths. Name modules and
  types; avoid pinning to coordinates that rot.
- History. The doc describes the current shape, not how it got there.

## Maintenance rules

- **When code moves, update the map, do not append a migration note.** The doc
  describes now, not the journey. "X used to be in Y, now in Z" is noise; just
  say X is in Z.
- **State invariants where the boundary is described**, especially when the
  invariant is enforced by construction (a type, a parse step, a config check).
  The reader should learn both the rule and where it is guaranteed.
- **Split before it sprawls.** When one section grows too detailed, move it to a
  focused doc and leave a pointer-level summary in the main map.
- **The map and the code must agree.** A review that changes module boundaries
  changes the map in the same change. A stale architecture doc is worse than
  none, because it is believed.

## Why it pays for agents specifically

A coding agent re-reads the map every session. A tight, accurate codemap is the
single highest-leverage doc for getting an agent to the right file fast and
keeping it inside the intended boundaries. The `AGENTS.md` architecture section
and the architecture doc serve the same role; keep them consistent.
