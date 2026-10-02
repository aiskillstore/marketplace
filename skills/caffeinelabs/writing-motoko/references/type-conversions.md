# Type Conversions

Reference for Motoko numerical type conversions. Load when you need to convert between `Nat`, `Int`, and their sized variants.

**Every conversion is spelled `to`, on the source value.** Widening and narrowing are both receiver calls; `Module.fromX` is deprecated. Do not write `Nat8.fromNat64(n)` even where it still compiles — write `n.toNat8()`.

## Nat to Int

```motoko
let natValue = 42;
let intValue = natValue.toInt();
let backToNat = Int.abs(intValue); // Only if non-negative

```

## Nat Size Conversions

```motoko
let nat8 : Nat8 = 255;
let nat16 = nat8.toNat16();
let nat32 = nat16.toNat32();
let nat64 = nat32.toNat64();
let backToNat8 = nat64.toNat8(); // Narrow — traps on overflow

```

Conversion chain: `Nat8 → Nat16 → Nat32 → Nat64` (widen) and back (narrow). Both directions are `toXX` on the value.

## Int Size Conversions

```motoko
let int8 : Int8 = -128;
let int16 = int8.toInt16();
let int32 = int16.toInt32();
let int64 = int32.toInt64();
let backToInt8 = int64.toInt8(); // Narrow — traps on overflow

```

Conversion chain: `Int8 → Int16 → Int32 → Int64` (widen) and back (narrow). Both directions are `toXX` on the value.

## Common Conversion Patterns

```motoko
// Nat to Text
let text = myNat.toText(); // dot notation

// Int to Text
let text = myInt.toText(); // dot notation

// Text to Nat/Int (returns optional) — receiver form on the Text
let maybeNat = "42".toNat(); // ?Nat
let maybeInt = "-5".toInt(); // ?Int

// Nat to Float
let f = myNat.toFloat();

// Int to Float
let f = myInt.toFloat();

// Time is Int — use Int conversions
let timestamp = Time.now(); // Int (nanoseconds)
let milliseconds = timestamp / 1_000_000;

```
