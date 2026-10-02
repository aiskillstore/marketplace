# Equality and Comparison

Load when choosing between `==`, `equal`, and `compare`, or when a `.equal(...)` call fails with M0070.

## `==` vs `equal`

**`==` compares two values; `equal` and `compare` are functions you can pass.** Collections need the function form, so write it for the records and variants you use as keys or elements. For a direct comparison of primitives or shared fields, `==` is fine — and on `Nat`, `Int`, `Float`, and the sized int types it is the only receiver form available, where `a == b` is shorter than `Nat.equal(a, b)` and needs no import.

`==` is compiler-generated structural equality, and it only exists for **shared** types. That is the catch: a single `var` field takes a record out of shared, and `==` stops compiling:

```motoko
type Todo = { id : Nat; var completed : Bool };
a == b
// type error [M0060], operator is not defined for operand types
```

Internal state records routinely have `var` fields, so code written around `==` breaks the moment a field becomes mutable. `equal`/`compare` functions do not have that failure mode, which is why record and variant comparisons belong in them rather than in `==`.

`equal` and `compare` are also what **collections** take, as implicit arguments: `Map`, `Set`, `contains`, and the collection-level `equal`/`compare` helpers. The compiler infers them, so you rarely name them:

```motoko
let map = Map.empty<Nat, Text>(); // compare resolved at add/get, from the imported Nat
numbers.contains(3);              // likewise Nat.equal
```

Inference finds `equal`/`compare` in the module imported for the element type, so the import is what makes it work — without `import Nat`, you get M0230. Passing the module's own function explicitly is redundant and warns:

```motoko
friends.contains(p);                  // CORRECT
friends.contains(Principal.equal, p); // WRONG (M0237)
```

Name a function only when you want **different** behaviour from the module default — a case-insensitive match, a reversed order:

```motoko
names.contains(func (x, y) = x.toLower() == y.toLower(), q);
```

## Which types allow receiver `.equal` / `.compare`

The general dot-notation rule applies: a receiver call works only when the module declares the function with a `self` parameter. `Text.equal` is `(self : Text, other : Text)`, so `a.equal(b)` resolves. `Nat.equal` is `(x : Nat, y : Nat)` — no `self`, so it does **not**.

| Type | `a.equal(b)` | `a.compare(b)` | Module form |
|---|---|---|---|
| `Text`, `Principal`, `Bool`, `Char`, `Blob` | yes | yes | also fine |
| `Order` | yes | **no such function** | `Order.equal(a, b)` only |
| `Nat`, `Int`, `Float` | **no** | **no** | `Nat.equal(a, b)` |
| `Nat8`…`Nat64`, `Int8`…`Int64` | **no** | **no** | `Nat64.equal(a, b)` |

`mo:core/Order` has no `compare` in any form — `Order.compare(a, b)` is M0072 (`field compare does not exist`), not just a missing receiver.

Calling the receiver form on a numeric type fails:

```motoko
myNat.equal(other)   // WRONG
// type error [M0070], expected object type, but expression produces type Nat

Nat.equal(myNat, other)  // CORRECT — or just: myNat == other
```

This is the one place where "always use dot notation" does not hold, and it is worth remembering: numeric types **do** support other receiver methods (`myNat.toText()` is correct), just not `equal` and `compare`.

## Your own records, tuples, and variants

Nothing is derived for them. A record or variant used as a `Map`/`Set` key needs a `compare` the compiler can find, or you get:

```text
type error [M0230], Cannot determine implicit argument `compare`
```

**Record `compare` must be an explicit function.** There is no sensible default — which field dominates, and in what direction, is a decision only you can make. Write it out and be deliberate about the tie-breaking:

```motoko
type Point = { x : Nat; y : Nat };
module Point {
  public func compare(a : Point, b : Point) : Order.Order {
    switch (Nat.compare(a.x, b.x)) {
      case (#equal) { Nat.compare(a.y, b.y) }; // x first, then y
      case other { other };
    }
  };
};
```

Put it in the module named after the type and inference will find it, exactly as it finds `Nat.compare`.

**Custom variants need both `equal` and `compare` written out.** `mo:core` types are the exception — `Result` already ships them:

```motoko
a.equal(b, Nat.equal, Text.equal); // Result.equal, sub-functions for Ok and Err
```

For a one-off equality check on an immutable record, tuple, or variant, `==` still works and is fine — the guidance above is about the functions collections need, and about not building on `==` for types whose fields may become `var`.
