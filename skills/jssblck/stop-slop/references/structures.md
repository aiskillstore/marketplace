# The structural tells, in depth

Each tell below has the same shape: what it is, why a model reaches for it, a
kill-or-keep test, and a rewrite. The tells are ordered roughly by how often
they show up and how much damage they do.

## 1. Virtue and character framing

The text tells you the subject is honest, trustworthy, principled, careful, or
humble, instead of showing behavior that would let you conclude that yourself.
This is the biggest offender and the one most specific to model output: it
moralizes reliability rather than stating it.

Tells: "built to be trusted", "fails honestly", "that honesty is the whole point",
"knows its edges", "we would rather block than pretend", "inspectable, not just
trusted".

Test: does the sentence assert a character trait? If so, delete the assertion
and state the mechanism. The candor of a plain factual sentence performs the
honesty better than the word "honest" ever does.

Before: "Anything not yet wired fails closed rather than pretending. An
unimplemented backend never claims to have reviewed anything. That honesty is
the whole point of a gate."
After: "Anything not yet implemented returns block instead of pass, so an
unfinished backend cannot wave code through by claiming a review it never ran."

## 2. Manufactured antithesis ("X, not Y")

A contrast is invented to manufacture emphasis. The structure is fine; the
problem is when the second half is a strawman nobody was proposing, or a vibe
rather than a real alternative.

Test: do both halves name real, distinct, true things? Keep it. Is the second
half a punching bag built for cadence? Cut it and keep only the true half.

KILL: "a merge gate you govern, not a bot you tolerate"; "inspectable, not just
trusted"; "convergence over time beats strict perfection up front".
KEEP: "gates block, advisors comment"; "gates fail closed, advisors fail open".

Before: "Bastion does not take the human out of the loop, it moves them up a
level."
After: "The human moves from reviewing every diff to authoring and governing the
reviewers that do."

## 3. Aphorism openers and closers

A section opens or closes on a small general maxim that wraps the point in a
fortune cookie. Humans rarely preface a concrete point with a generalization;
models love to.

Tells: "attention is scarce, for humans and for agents, and smarter models do
not change that"; "the more you ask, the less it catches"; "the registry is the
artifact: review it, version it, own it".

Test: remove the maxim. Did you lose any fact? If not, it was scaffolding. The
graph, table, or sentence next to it already made the point.

## 4. Triadic parallelism

Rule-of-three cadence: "read, audit, and build on", "clone, run it once, and you
are reading", "capture to definition". Three balanced items feel complete, so
models reach for three whether or not there are three real things.

Test: are there exactly three real, distinct items, or did the third get added
for rhythm? If the third is filler or a restatement, cut to two or rewrite flat.

## 5. The dramatic colon

Setup on the left, payoff on the right, staged for a small reveal: "runs locally,
end to end: capture to definition." Used once it is fine; as a habit it is a
fingerprint.

Test: is the colon introducing or expanding something real, or performing
suspense? If it is theater, rewrite as a plain sentence.

## 6. Uniform clipped-fragment headers

Every section header is a short declarative sentence with a terminal period:
"Point at the word. The meaning is there." The cadence itself becomes the tell
once every header has it.

Test: read the headers as a list. Do they all have the same punchy shape? Vary
them. Let some be plain noun phrases ("How the gate aggregates", "Running it in
CI") and keep a punchy one only where it earns its place.

## 7. The meta-pattern: nothing is allowed to be boring

Every sentence is doing work: contrasting, reassuring, resolving, landing a beat.
Real product writing is lumpier. It lets some sentences just state a fact and
stop. It varies sentence length unevenly instead of settling into a balanced
rhythm.

Test: find the flattest, most purely informational sentence in the piece. If
there isn't one, that is the problem. Add some boring.

## Over-correction is a tell too

A deslopped piece that swung too far reads as conspicuously fragment-phobic and
antithesis-phobic, every sentence the same medium length and the same flat
register. The fix for slop is variation, not flatness. Keep the real contrasts,
keep one beat of personality per section, and let the rhythm stay uneven.
