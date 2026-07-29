# branch-closure

Review that salvages knowledge when an exploration branch is merged, abandoned, or rolled back. Triggered by reading project `AGENTS.md` rules; there is no automatic hook. Git decides the code line's fate; this review decides whether the branch's experience is worth keeping.

## When

Before merging, abandoning, or rolling back an exploration branch whose `cairn/` notes or process artifacts (e.g. under `docs/superpowers/`) changed.

## Classify each change

Put every branch change into exactly one bucket:

- **discard** — dead-end or superseded exploration noise. Do not bring it into `main`.
- **merge-to-project** — a validated negative result, decision, or lesson that is still true. Distill it into a `main` `cairn/<topic>.md` (update in place or create), and add a short `cairn/LOG.md` pointer.
- **graduate** — knowledge reusable beyond this project. Flag it as a graduation candidate (`graduation_status: candidate` on the topic note). Do not write the knowledge base here; that goes through the human-confirmed `graduation.md` flow. Never silently graduate.
- **archive-reference** — a process artifact (spec/plan) worth keeping. Record a pointer to its path; do not copy its body into `cairn/`.

## Principle

`main` receives only distilled current truth, never the branch's whole exploration history. A branch being reverted does not mean its knowledge should disappear. Do not delete existing `main` conclusions just because a branch was dropped (one-directional, like graduation).

## Output

Record the classification (in a real project, a short review note or a `cairn/LOG.md` entry). Apply the merge-to-project distillations and the graduate flags, keep discard items out of `main`, and record archive pointers.
