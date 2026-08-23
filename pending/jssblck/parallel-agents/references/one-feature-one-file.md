# One feature, one file

Merge conflicts among parallel agents are a structural property, not bad luck.
They concentrate in hub files: the files every feature must touch regardless of
what the feature is. Measured over real agent-managed repos, the top conflict
files are always the same shapes: the file holding every subcommand handler,
the single integration-test main, the HTTP router, the monolithic agent doc.
Change the structure and the conflict rate follows.

## The rule

New behavior gets its own file. The shared file it plugs into grows by exactly
one line.

One line means a `mod` declaration, a route registration, a match arm that
delegates, a re-export, a table entry. The body (the handler, the scenario,
the page, the logic) lives in the new file. Two agents each adding a file plus
one registration line auto-merge almost every time; two agents each adding a
200-line function to the same file conflict almost every time.

## Recognizing a hub

A hub is any file where growth from unrelated features lands. Symptoms:

- a match or switch over subcommands or routes with the bodies inline
- a single test file holding every scenario
- a mod/index/init file that contains logic instead of only declarations
- a shared stylesheet or script that every page appends to
- a "handlers" or "commands" or "utils" file that only ever grows

If the last ten commits touching a file have nothing in common except the
file, it is a hub.

## Patterns by shape

- CLI (Rust and similar): `src/commands/<name>.rs` holding the handler, one
  dispatch arm in the command tree. A new integration scenario gets its own
  module under the test directory, never another function in a shared main.
- HTTP services (Go and similar): one file per resource for handlers; the
  router file holds registration lines only.
- Web UI: one template or component file per page; page-scoped styles live
  next to the page rather than appended to a global stylesheet.
- Tests follow the code: a new module gets its own test file. Do not append
  cases to a shared test file for convenience.

## When the hub edit cannot be one line

Some features genuinely change shared plumbing. Keep that edit minimal and
mechanical, isolate it in its own commit, and follow `mergeable-edits.md`
for how to shape it so concurrent branches still merge.

## The counter-instinct

"Just add a function here" feels cheaper in the moment, and for a solo author
it is. With parallel agents the marginal function in a shared file is exactly
where the conflicts come from. When in doubt, make the new file.
