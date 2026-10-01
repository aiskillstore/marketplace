# The JsonLogic standard

Source: https://jsonlogic.com (fetched 2026-09-16). This describes the format itself,
not any particular library's implementation of it — see `libraries.md` for that layer.

## Shape of a rule

A JsonLogic rule is a JSON value. A rule that does something is an object with exactly
one key — the operator — whose value is the array of arguments:

```json
{ "operator": ["arg1", "arg2", ...] }
```

A single argument may be written unwrapped: `{"!": true}` is equivalent to
`{"!": [true]}`. Rules nest: any argument position can itself be a rule, and evaluation
resolves innermost-first, tree style. A JSON value that isn't an operator object (a
plain number, string, `true`, an array without an operator key) evaluates to itself.

## Design goals (as stated by the spec)

- **Terse** — minimal syntax overhead.
- **Consistent** — operator as key, arguments as array, always.
- **Flexible** — easy to add operators, easy to compose into larger rules.
- **"Not for programming"** — no loops, no functions, no assignment, no side effects.
  That's a deliberate ceiling, not a missing feature: it's what makes a rule safe to
  accept from an untrusted source and run with bounded, deterministic cost.

## Data access: `var`

`{"var": "key"}` reads `key` from the data object passed at evaluation time.
`{"var": "a.b.c"}` walks dot-separated nested paths. `{"var": 1}` (or any integer)
indexes into an array. `{"var": ""}` or `{"var": null}` returns the entire data object.
A second array element gives a default: `{"var": ["key", "default"]}` returns
`"default"` when `key` is absent.

A rule is evaluated *against* data — the same rule produces different results for
different data objects. Always be explicit about what shape of data a rule expects.

## Truthiness and type coercion

Built-in operators already follow JsonLogic's own (JS-style) semantics — verified
by actually running both through [scripts/jsonlogic.rb](scripts/jsonlogic.rb), not
just reading the gem's source. No setup needed; this is the default.

```bash
echo '{">=": [1, "1.0"]}' > rule.json && ruby scripts/jsonlogic.rb rule.json
# => true    (a number and a numeric string compare fine, JS-style)

echo '{"!!": [[]]}' > rule.json && ruby scripts/jsonlogic.rb rule.json
# => false   (an empty array is falsy in JsonLogic, unlike plain Ruby)
```

### Where this stops being automatic: custom Ruby operations

That JS-style behavior is baked into each built-in operator's own implementation —
it isn't something this skill or a rule author opts into. It only becomes your
problem if you write a *custom* operation for `json-logic-rb` (via its extension
API) whose Ruby code compares or truth-tests values directly, since plain Ruby
doesn't coerce types or treat an empty array as falsy the way JsonLogic does:

```ruby
# plain Ruby, inside a custom operation's own code
1 >= "1.0"
# ArgumentError: comparison of Integer with String failed

!![]
# => true
```

`using JsonLogic::Semantics` gives your custom operation's code that same
JS-style coercion and truthiness:

```ruby
using JsonLogic::Semantics

1 >= "1.0"
# => true

!![]
# => false
```

`scripts/jsonlogic.rb` doesn't enable this refinement itself — add
`using JsonLogic::Semantics` inside your custom operation's own file if its code
needs to match what the built-in operators already get for free.

## Missing data

`{"missing": ["a", "b"]}` returns the array of keys from its argument list that are
absent from the data (an empty array — falsy — means all keys were present).
`{"missing_some": [minCount, ["a","b","c"]]}` checks that at least `minCount` of the
listed keys are present, returning the missing ones if not. These exist so a rule can
validate its own input requirements before other operations run.

## What "compliant" means

jsonlogic.com does not publish a formal conformance test suite as part of the base
spec; different libraries describe their own compliance level, and that claim isn't
independently checked anywhere in this skill — treat it as the library's own word.
When a rule needs to run identically across two libraries, the only reliable
check is running the same rule against the same data on both and diffing the result —
don't assume "spec compliant" means byte-identical behavior on edge cases like
`0 == false` or three-argument range comparisons.

## Where this skill's other references pick up

- Full operator list and behavior: `operations.md`.
- Running a rule in a specific language: `libraries.md`.
