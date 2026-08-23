# Make illegal states unrepresentable

> Encode invariants in types, not in names, comments, or conventions.

This folds together three ideas that are really one: "make illegal states
unrepresentable," "names are not type safety," and "newtypes over primitives."
The common thread: a caller should not be able to construct or pass a wrong
value and still type-check.

## The test

Ask of every wrapper or type you introduce: **what illegal operation or invalid
state does this prevent?**

- If the honest answer is "it documents the role," you do not need a new type.
  Use a field name, a type alias, or a doc comment.
- If the answer is "it enforces an invariant" (non-empty, in-range, validated,
  one-of-N states, parsed-once), encode that invariant by construction.

A type that any caller can build from raw parts in any shape proves nothing. The
invariant lives in the constructor, and the constructor must be the only door.

## Names are not type safety

`type UserId = string` (or a public tuple struct that wraps a `String` with a
public field) gives you a nicer name and zero safety: every string is still a
valid `UserId`, and you can pass an `OrderId` where a `UserId` is wanted. Two
ways to make it real:

- **Just a label?** A transparent alias is fine. Be honest that it is
  documentation, not a guarantee.
- **A guarantee?** Hide the inner value behind a private field and a smart
  constructor (a parser) that is the only way in. Now "I hold one of these"
  means "it passed the check."

Avoid auto-deriving broad conversions (`From`, `Into`, blanket serde/JSON
decode, `DerefMut`) on a checked type when the derive lets a caller route around
the constructor. Every public constructor is a potential trapdoor; keep the
trusted module small.

## States: enums/unions over flag soup

When a value can be in one of several mutually exclusive states, model it as a
sum type (Rust `enum`, TS discriminated union, Go a sealed interface or a small
state enum, Python `Enum`/`match` over a union). Booleans multiply into
impossible combinations:

```
# illegal combinations are representable, so they will happen
is_loading: bool
is_error:   bool
data:       T | null
# (loading && error)? (data while loading)? nothing stops it.

# one state at a time, data attached to the state that has it
state = Loading | Error(message) | Ready(data)
```

Carry the data on the variant that owns it. `Ready` holds the data; `Loading`
and `Error` cannot accidentally expose a half-populated value.

## Newtypes over primitives

Wrap distinct domain values in distinct types so the compiler enforces the
distinction and parsing happens once:

- IDs: `UserId`, `OrderId` instead of bare integers/strings that swap silently.
- Validated values: `Email`, `Url`, `NonEmpty<T>`, `Percentage` (0..=100).
- Units: `Cents` vs `Dollars`, `Millis` vs `Seconds`. Mixing units is a classic
  outage; types make the mix a compile error.

## When a transparent wrapper is still worth it

Sometimes you wrap not for an invariant but for: secrecy/redaction (a `Secret`
that does not print its contents), trait/interface coherence, or clarity across
a long call chain. That is legitimate. Document that it discourages misuse but
does not prove safety, so no one mistakes it for an enforced invariant.

## Do not over-split

Do not mint a new type for every real-world noun. Split types when they **behave
differently** or **rule out different states**, not merely because the domain
uses different words. Two concepts that are interchangeable in code can share a
type.

See the per-language files for the concrete spelling (private fields and smart
constructors, branded types, unexported struct fields, frozen dataclasses).
