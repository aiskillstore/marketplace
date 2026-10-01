# Testing and verification

## Three levels of confidence — say which one you're giving

1. **Verified by execution** — you actually ran the rule (in a sandbox, a script, the
   target language's REPL) against real input and observed the output.
2. **Verified against documentation/source** — you checked the library's README, docs
   site, or source code, but didn't run it.
3. **Unverified / needs checking** — you're reasoning from the general JsonLogic spec
   or from memory of how a library usually behaves, without checking this specific
   case.

Label which one applies rather than letting "here's a rule" imply level 1 when it's
really level 2 or 3. This matters more for JsonLogic than most formats because the same
rule can legitimately behave differently across libraries (coercion, empty-array
behavior, unsupported operators) — see `jsonlogic.md` and
`libraries.md`.

## How to actually verify a rule

**Syntax/structure validity** — check it's valid JSON, and that it follows the
`{"operator": [args]}` shape recursively. `scripts/validate_skill.rb` in this skill's
`scripts/` folder does this for offline sanity-checking; for real execution, feed the
rule to an actual JsonLogic evaluator.

**Semantic validity** — run the rule against representative data, including:
- the "happy path" the requirement describes
- data missing the fields the rule reads (does `missing`/a default handle it, or does
  it error?)
- boundary values for any comparison (exactly equal, just above, just below)
- empty arrays/strings where the rule uses array or string operators — remember `all`
  is false and `none` is true on an empty array (see `operations.md`)
- type edge cases if the rule uses `==` (loose) rather than `===`

**Cross-implementation comparison** — if the same rule needs to run in two languages
(e.g. validated in a JS frontend, enforced again in a Ruby backend), run it against
the *same* data in both and diff the results rather than assuming parity. Differences
usually trace back to truthiness/coercion settings (e.g. `json-logic-rb`'s
`JsonLogic::Semantics` mode) or an operator one library implements slightly
differently.

## Writing tests for a rule

A minimal test for a JsonLogic rule is just data-in/result-out pairs — no framework
required. In whatever language executes the rule:

```json
[
  {"data": {"age": 20}, "expected": true},
  {"data": {"age": 17}, "expected": false},
  {"data": {}, "expected": false}
]
```

Cover the normal case and the boundary. Add at least one "missing/absent field" case
too. Add more only where the rule's branching actually calls for it — a three-line rule
doesn't need ten test cases.

## What not to claim

- Don't say a rule "works" based only on reading it — say it's "structurally valid" or
  "should behave as follows" unless you ran it.
- Don't say a library "fully supports the spec" unless that's what its own
  documentation claims and you're passing that claim along, clearly attributed (see how
  `libraries.md` phrases this).
- Don't claim two libraries produce identical output on an untested edge case just
  because they both claim spec compliance.
