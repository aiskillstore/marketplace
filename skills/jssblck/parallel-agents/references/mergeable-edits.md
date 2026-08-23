# Mergeable edits

Structure prevents most conflicts (see `one-feature-one-file.md`); this file
covers the shared files that legitimately remain: registration lines,
registries, config lists, and the generated files no structure can remove.
The goal is edits shaped so git's line-based merge resolves concurrent
branches on its own.

## Lists and registries

- One item per line, with a trailing comma or delimiter on every line, so
  adding an item is a strict one-line diff that touches no neighbor.
- Insert in a stable order, alphabetical unless the list is order-sensitive.
  Appending at the bottom makes every concurrent branch collide on the same
  last line; ordered inserts scatter across the file and merge cleanly.
- For a file that is genuinely an order-independent set of lines, a
  `.gitattributes` `merge=union` driver removes conflicts entirely. Use it
  sparingly: union merge never reports a conflict, so it is only safe where a
  duplicated or reordered line is harmless.

## Formatters and lint autofixers are exempt

Always run the repo's canonical formatter and lint autofixers. Their output
is deterministic, so branches that all run them converge to the same text
instead of conflicting; skipping them is what causes the formatting
conflicts. The ownership rules below govern discretionary edits, never
tool-enforced ones.

One scoping rule: if the formatter wants to change files your work never
touched, that is pre-existing drift, not part of your change. Format the
files you edited and leave the rest, or land the drift cleanup as its own
commit. Do not fold it into feature work.

## Do not own what you did not change

- Never hand-reflow paragraphs, reorder code, renumber lists, or apply style
  preferences the repo's tools do not enforce to regions your change does
  not touch. Every line you rewrite by choice is a line you now conflict on.
- Repo-wide sweeps (adopting a new formatter config, enabling a new lint
  rule and its autofix) go in their own commit, landed when no feature
  branches are in flight, never mixed into feature work.
- No drive-by fixes inside shared files. Note the issue and fix it in a
  separate change.

## Generated files and lockfiles

- Never hand-edit them, and never hand-resolve a conflict in them. Take
  either side wholesale, then regenerate with the owning tool (`templ
  generate`, `cargo build` for Cargo.lock, `go mod tidy`, the bundler for a
  compiled asset). The generator's output is the only correct content, and a
  hand-merged version is wrong in ways tests may not catch.
- If a generated file conflicts constantly, question whether it needs to be
  checked in at all; building it in CI may be the real fix.

## Resolving a conflict in a hub

When a conflict does land in a dispatcher or registry, resolve by intent:
both branches' one-line entries survive, placed in the file's stable order.
Then rerun the formatter and the tests. The classic parallel-agent bug is a
resolved registry with one branch's entry silently dropped; check for it
explicitly before committing.
