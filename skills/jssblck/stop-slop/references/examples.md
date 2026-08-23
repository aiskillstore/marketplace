# Before and after

Rewrites from a real product landing page. Each pairs a tell with a fix and
shows what was dropped (rhetoric) and what was kept (every fact). Read these as
the voice anchor: plain, specific, mechanism-forward.

## Hero

Before:
> A merge gate you govern, not a bot you tolerate.
> Most AI reviewers are one opaque model you hope behaves. Bastion is a registry
> of small, single-concern reviewers you author and govern, and a gate that
> blocks when it can't be sure.

After:
> A merge gate built from small reviewers you write and own.
> Most AI reviewers hand the whole diff to one model. Bastion splits review into
> many narrow reviewers, each checking exactly one concern. They run in parallel
> and aggregate into one verdict; the gate blocks whenever any reviewer can't
> return a clean pass. You author them, version them in your repo, and run them
> on your own infrastructure.

Dropped: the "govern, not tolerate" antithesis and the "opaque model you hope
behaves" sneer. Kept: the real one-model-versus-many contrast and the
fail-closed mechanic, now stated as behavior.

## The virtue-framing section

Before:
> We'd rather block than pretend.
> Bastion is early software and evolving fast. The runner, the gate, and the
> Claude Code and Codex backends execute reviewers for real, and anything not
> yet wired fails closed rather than pretending. An unimplemented reviewer never
> claims to have reviewed anything. That honesty is the whole point of a gate.

After:
> Early software, fails closed.
> Bastion is early and moving fast. The runner, the gate, and the Claude Code
> and Codex backends run reviewers for real. Anything not yet implemented returns
> block instead of pass, so an unfinished backend can't wave code through by
> claiming a review it never ran.

Dropped: "we'd rather block than pretend" and "that honesty is the whole point".
Kept: the same disclosure. The candor of the plain sentence performs the honesty
the deleted lines were asserting.

## The recall section (aphorism closer)

Before:
> One checklist stretched across everything. The more you ask, the less it
> catches.

After:
> One checklist stretched across everything; each concern gets a fraction of the
> model's attention.

Dropped: the "the more you ask, the less it catches" maxim. Kept: the mechanism,
which is what the maxim was gesturing at anyway.

## The governance points (maxim + triad)

Before:
> The registry is the artifact. Review it, version it, own it.

After: cut entirely. The surrounding sentence ("any PR that weakens the gate
shows up as a diff a human must approve") already states the mechanic, so the
"review it, version it, own it" triad added rhythm and no information.

## Section headers (uniform fragments)

Before, read as a list: "Fails closed." / "Declarative and static." /
"Composable and parallel." / "Inspectable, not just trusted." Every one a clipped
declarative with a terminal period.

After: varied. "How the gate aggregates" (plain noun phrase), "Declarative and
static" (period dropped), "Open source and self-hostable." Kept "Gates block.
Advisors comment." because that pair is a real opposed contrast, not a
manufactured one.

## What stayed exactly as it was

The verdict and aggregation tables, the reviewer registry table, the recall
graphic, every code block and CLI example, and the two real opposed pairs
("gates block, advisors comment" and "gates fail closed, advisors fail open").
Deslopping is a prose edit. It does not touch data, code, or the contrasts that
name real, distinct behaviors.
