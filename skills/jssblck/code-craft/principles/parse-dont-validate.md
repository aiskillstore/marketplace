# Parse, don't validate

> Turn weak external input into a proof-carrying type once, at the boundary.

From Alexis King's article. The core move: instead of checking that data is
valid and then continuing to pass the same weak type around, convert it into a
type that *can only hold valid data*, and pass that type inward.

## Validate vs parse

```
# validate: the knowledge gained is thrown away
def handle(raw: dict):
    if not is_valid(raw):       # we learned something...
        raise BadInput
    process(raw)               # ...and immediately forgot it; process re-checks

# parse: the knowledge is captured in the type
def handle(raw: dict):
    config = parse_config(raw)  # -> Config, or raises/returns error
    process(config)            # process REQUIRES Config; cannot be called on junk
```

A validator returns a boolean or void and leaves you holding the same untrusted
value. A parser returns a new, stronger value (or an error) and makes the
untrusted value disappear. Downstream code that requires the strong type can no
longer be called with bad input, so it does not need to re-check.

## Workflow

1. **Find the boundary.** Where does weakly typed or untrusted data enter? File
   load, deserialization, CLI/env parsing, network response, generated data,
   user edits.
2. **Design the type you wish you had downstream.** What would let processing
   code stop being defensive? Prefer enums, non-empty collections, validated
   newtypes with private fields, maps/sets, bounded numbers, checked structs,
   over `string`, `list`, `null`, and loose booleans.
3. **Write the parser:** `parse(raw) -> Strong | Error`. All shape and validity
   failure happens here, once.
4. **Push the strong type down** into signatures. The check: if a caller can
   skip the parser and still type-check, you are not done. Make the inner
   functions demand the strong type.
5. **Keep failure at the boundary.** Processing code should not rediscover basic
   shape errors after it has already acted.
6. **For checked-in assets / literals**, construct the strong form at startup or
   compile time, not by sprinkling parse-and-unwrap through runtime paths.

## Smells

- A function named `validate*`/`check*`/`isValid*` that returns `bool` or
  `void`/`unit` for a boundary shape check. It throws away what it learned.
  Return the parsed value instead.
- A `Result<(), E>` / `Promise<void>` that exists only to signal "input was ok."
  Fine for genuine effects with no value; suspicious when it is guarding data
  that the caller then keeps using raw.
- Re-parsing or re-checking the same field at three different depths. The parse
  belongs once, at the edge.

## Boundary types vs domain types

It is fine, often good, to have a loose "wire" type that mirrors the external
format exactly (the raw serde struct, the zod input, the JSON shape), and a
separate checked domain type. The parser is the function between them. Name the
checked type for what it proves (`CheckedConfig`, `VerifiedOrder`, `NonEmpty
Plan`), so its meaning is visible at every call site.

## If it is already typed, do not re-parse

If a value was constructed inside trusted code and no invalid state is
representable, do not parse it again "to be safe." Make the receiving function
require the precise type. Re-parsing typed data is noise and hides the real
boundary.

See the per-language files for the idiomatic parser shape (smart constructors,
zod/valibot schemas, decode functions returning errors, pydantic models).
