# Core Library API Reference

Complete API signatures from `mo:core` library.

Use this as a reference when using contextual dot notation.

Generated from motoko-core's API lock by `scripts/generate-motoko-api-reference.mjs`.
Deprecated APIs are omitted — if a symbol is not here, do not write it.

## Array

- `func all<T>(self : [T], predicate : T -> Bool) : Bool`
- `func any<T>(self : [T], predicate : T -> Bool) : Bool`
- `func binarySearch<T>(self : [T], compare : (implicit : (T, T) -> Order.Order), element : T) : { #found : Nat; #insertionIndex : Nat }`
- `func compare<T>(self : [T], other : [T], compare : (implicit : (T, T) -> Order.Order)) : Order.Order`
- `func concat<T>(self : [T], other : [T]) : [T]`
- `func contains<T>(self : [T], equal : (implicit : (T, T) -> Bool), element : T) : Bool`
- `func empty<T>() : [T]`
- `func enumerate<T>(self : [T]) : Types.Iter<(Nat, T)>`
- `func equal<T>(self : [T], other : [T], equal : (implicit : (T, T) -> Bool)) : Bool`
- `func filter<T>(self : [T], f : T -> Bool) : [T]`
- `func filterMap<T, R>(self : [T], f : T -> ?R) : [R]`
- `func find<T>(self : [T], predicate : T -> Bool) : ?T`
- `func findIndex<T>(self : [T], predicate : T -> Bool) : ?Nat`
- `func flatMap<T, R>(self : [T], k : T -> Types.Iter<R>) : [R]`
- `func flatten<T>(self : [[T]]) : [T]`
- `func foldLeft<T, A>(self : [T], base : A, combine : (A, T) -> A) : A`
- `func foldRight<T, A>(self : [T], base : A, combine : (T, A) -> A) : A`
- `func forEach<T>(self : [T], f : T -> ())`
- `func indexOf<T>(self : [T], equal : (implicit : (T, T) -> Bool), element : T) : ?Nat`
- `func isEmpty<T>(self : [T]) : Bool`
- `func isSorted<T>(self : [T], compare : (implicit : (T, T) -> Order.Order)) : Bool`
- `func join<T>(self : Types.Iter<[T]>) : [T]`
- `func keys<T>(self : [T]) : Types.Iter<Nat>`
- `func lastIndexOf<T>(self : [T], equal : (implicit : (T, T) -> Bool), element : T) : ?Nat`
- `func map<T, R>(self : [T], f : T -> R) : [R]`
- `func mapEntries<T, R>(self : [T], f : (T, Nat) -> R) : [R]`
- `func nextIndexOf<T>(self : [T], equal : (implicit : (T, T) -> Bool), element : T, fromInclusive : Nat) : ?Nat`
- `func prevIndexOf<T>(self : [T], equal : (implicit : (T, T) -> Bool), element : T, fromExclusive : Nat) : ?Nat`
- `func range<T>(self : [T], fromInclusive : Int, toExclusive : Int) : Types.Iter<T>`
- `func repeat<T>(item : T, size : Nat) : [T]`
- `func reverse<T>(self : [T]) : [T]`
- `func singleton<T>(element : T) : [T]`
- `func size<T>(self : [T]) : Nat`
- `func sliceToArray<T>(self : [T], fromInclusive : Int, toExclusive : Int) : [T]`
- `func sliceToVarArray<T>(self : [T], fromInclusive : Int, toExclusive : Int) : [var T]`
- `func sort<T>(self : [T], compare : (implicit : (T, T) -> Order.Order)) : [T]`
- `func tabulate<T>(size : Nat, generator : Nat -> T) : [T]`
- `func toBlob(self : [Nat8]) : Blob`
- `func toText<T>(self : [T], f : (implicit : (toText : T -> Text))) : Text`
- `func toVarArray<T>(self : [T]) : [var T]`
- `func values<T>(self : [T]) : Types.Iter<T>`

## Blob

- `func compare(self : Blob, other : Blob) : Order.Order`
- `func empty() : Blob`
- `func equal(self : Blob, other : Blob) : Bool`
- `func greater(self : Blob, other : Blob) : Bool`
- `func greaterOrEqual(self : Blob, other : Blob) : Bool`
- `func hash(self : Blob) : Types.Hash`
- `func isEmpty(self : Blob) : Bool`
- `func less(self : Blob, other : Blob) : Bool`
- `func lessOrEqual(self : Blob, other : Blob) : Bool`
- `func notEqual(self : Blob, other : Blob) : Bool`
- `func size(self : Blob) : Nat`
- `func toArray(self : Blob) : [Nat8]`
- `func toVarArray(self : Blob) : [var Nat8]`
- `type Blob = Prim.Types.Blob`

## Bool

- `func allValues() : Iter.Iter<Bool>`
- `func compare(self : Bool, other : Bool) : Order.Order`
- `func equal(self : Bool, other : Bool) : Bool`
- `func logicalAnd(self : Bool, other : Bool) : Bool`
- `func logicalNot(self : Bool) : Bool`
- `func logicalOr(self : Bool, other : Bool) : Bool`
- `func logicalXor(self : Bool, other : Bool) : Bool`
- `func toText(self : Bool) : Text`
- `type Bool = Prim.Types.Bool`

## Char

- `func compare(self : Char, other : Char) : { #less; #equal; #greater }`
- `func equal(self : Char, other : Char) : Bool`
- `func greater(self : Char, other : Char) : Bool`
- `func greaterOrEqual(self : Char, other : Char) : Bool`
- `func isAlphabetic(self : Char) : Bool`
- `func isDigit(self : Char) : Bool`
- `func isLower(self : Char) : Bool`
- `func isUpper(self : Char) : Bool`
- `func isWhitespace(self : Char) : Bool`
- `func less(self : Char, other : Char) : Bool`
- `func lessOrEqual(self : Char, other : Char) : Bool`
- `func notEqual(self : Char, other : Char) : Bool`
- `func toNat32(self : Char) : Nat32`
- `func toText(self : Char) : Text`
- `type Char = Prim.Types.Char`

## Debug

- `func print(text : Text) : ()`
- `func todo() : None`

## Error

- `func code(self : Error) : ErrorCode`
- `func isCleanReject(self : Error) : Bool`
- `func isRetryPossible(self : Error) : Bool`
- `func message(self : Error) : Text`
- `func reject(message : Text) : Error`
- `type Error = Prim.Types.Error`
- `type ErrorCode = Prim.ErrorCode`

## Float

- `func abs(x : Float) : Float`
- `func add(x : Float, y : Float) : Float`
- `func arccos(x : Float) : Float`
- `func arcsin(x : Float) : Float`
- `func arctan(x : Float) : Float`
- `func arctan2(y : Float, x : Float) : Float`
- `func ceil(x : Float) : Float`
- `func compare(x : Float, y : Float) : Order.Order`
- `func copySign(x : Float, y : Float) : Float`
- `func cos(x : Float) : Float`
- `func div(x : Float, y : Float) : Float`
- `func equal(x : Float, y : Float, epsilon : Float) : Bool`
- `func exp(x : Float) : Float`
- `func floor(x : Float) : Float`
- `func format(self : Float, fmt : { #fix : Nat8; #exp : Nat8; #gen : Nat8; #exact }) : Text`
- `func fromInt64(x : Int64) : Float`
- `func greater(x : Float, y : Float) : Bool`
- `func greaterOrEqual(x : Float, y : Float) : Bool`
- `func isNaN(self : Float) : Bool`
- `func less(x : Float, y : Float) : Bool`
- `func lessOrEqual(x : Float, y : Float) : Bool`
- `func log(x : Float) : Float`
- `func max(x : Float, y : Float) : Float`
- `func min(x : Float, y : Float) : Float`
- `func mul(x : Float, y : Float) : Float`
- `func nearest(x : Float) : Float`
- `func neg(x : Float) : Float`
- `func notEqual(x : Float, y : Float, epsilon : Float) : Bool`
- `func pow(x : Float, y : Float) : Float`
- `func rem(x : Float, y : Float) : Float`
- `func sin(x : Float) : Float`
- `func sqrt(x : Float) : Float`
- `func sub(x : Float, y : Float) : Float`
- `func tan(x : Float) : Float`
- `func toFloat32(self : Float) : Prim.Types.Float32`
- `func toInt(self : Float) : Int`
- `func toInt64(self : Float) : Int64`
- `func toText(self : Float) : Text`
- `func trunc(x : Float) : Float`
- `let e : Float`
- `let pi : Float`
- `type Float = Prim.Types.Float`

## Int

- `func abs(x : Int) : Nat`
- `func add(x : Int, y : Int) : Int`
- `func compare(x : Int, y : Int) : Order.Order`
- `func div(x : Int, y : Int) : Int`
- `func equal(x : Int, y : Int) : Bool`
- `func fromText(text : Text) : ?Int`
- `func greater(x : Int, y : Int) : Bool`
- `func greaterOrEqual(x : Int, y : Int) : Bool`
- `func less(x : Int, y : Int) : Bool`
- `func lessOrEqual(x : Int, y : Int) : Bool`
- `func max(x : Int, y : Int) : Int`
- `func min(x : Int, y : Int) : Int`
- `func mul(x : Int, y : Int) : Int`
- `func neg(x : Int) : Int`
- `func notEqual(x : Int, y : Int) : Bool`
- `func pow(x : Int, y : Int) : Int`
- `func range(fromInclusive : Int, toExclusive : Int) : Iter.Iter<Int>`
- `func rangeBy(fromInclusive : Int, toExclusive : Int, step : Int) : Iter.Iter<Int>`
- `func rangeByInclusive(from : Int, to : Int, step : Int) : Iter.Iter<Int>`
- `func rangeInclusive(from : Int, to : Int) : Iter.Iter<Int>`
- `func rem(x : Int, y : Int) : Int`
- `func sub(x : Int, y : Int) : Int`
- `func toFloat(self : Int) : Float`
- `func toInt(self : Text) : ?Int`
- `func toInt16(self : Int) : Int16`
- `func toInt32(self : Int) : Int32`
- `func toInt64(self : Int) : Int64`
- `func toInt8(self : Int) : Int8`
- `func toNat(self : Int) : Nat`
- `func toText(self : Int) : Text`
- `type Int = Prim.Types.Int`

## Iter

- `func all<T>(self : Iter<T>, f : T -> Bool) : Bool`
- `func any<T>(self : Iter<T>, f : T -> Bool) : Bool`
- `func concat<T>(self : Iter<T>, other : Iter<T>) : Iter<T>`
- `func contains<T>(self : Iter<T>, equal : (implicit : (T, T) -> Bool), value : T) : Bool`
- `func drop<T>(self : Iter<T>, n : Nat) : Iter<T>`
- `func dropWhile<T>(self : Iter<T>, f : T -> Bool) : Iter<T>`
- `func empty<T>() : Iter<T>`
- `func enumerate<T>(self : Iter<T>) : Iter<(Nat, T)>`
- `func filter<T>(self : Iter<T>, f : T -> Bool) : Iter<T>`
- `func filterMap<T, R>(self : Iter<T>, f : T -> ?R) : Iter<R>`
- `func find<T>(self : Iter<T>, f : T -> Bool) : ?T`
- `func findIndex<T>(self : Iter<T>, predicate : T -> Bool) : ?Nat`
- `func flatMap<T, R>(self : Iter<T>, f : T -> Iter<R>) : Iter<R>`
- `func flatten<T>(self : Iter<Iter<T>>) : Iter<T>`
- `func foldLeft<T, R>(self : Iter<T>, initial : R, combine : (R, T) -> R) : R`
- `func foldRight<T, R>(self : Iter<T>, initial : R, combine : (T, R) -> R) : R`
- `func forEach<T>(self : Iter<T>, f : (T) -> ())`
- `func infinite<T>(item : T) : Iter<T>`
- `func map<T, R>(self : Iter<T>, f : T -> R) : Iter<R>`
- `func max<T>(self : Iter<T>, compare : (implicit : (T, T) -> Order.Order)) : ?T`
- `func min<T>(self : Iter<T>, compare : (implicit : (T, T) -> Order.Order)) : ?T`
- `func reduce<T>(self : Iter<T>, combine : (T, T) -> T) : ?T`
- `func repeat<T>(item : T, count : Nat) : Iter<T>`
- `func reverse<T>(self : Iter<T>) : Iter<T>`
- `func scanLeft<T, R>(self : Iter<T>, initial : R, combine : (R, T) -> R) : Iter<R>`
- `func scanRight<T, R>(self : Iter<T>, initial : R, combine : (T, R) -> R) : Iter<R>`
- `func singleton<T>(value : T) : Iter<T>`
- `func size<T>(self : Iter<T>) : Nat`
- `func sort<T>(self : Iter<T>, compare : (implicit : (T, T) -> Order.Order)) : Iter<T>`
- `func step<T>(self : Iter<T>, n : Nat) : Iter<T>`
- `func take<T>(self : Iter<T>, n : Nat) : Iter<T>`
- `func takeWhile<T>(self : Iter<T>, f : T -> Bool) : Iter<T>`
- `func toArray<T>(self : Iter<T>) : [T]`
- `func toVarArray<T>(self : Iter<T>) : [var T]`
- `func unfold<T, S>(initial : S, step : S -> ?(T, S)) : Iter<T>`
- `func zip3<A, B, C>(self : Iter<A>, other1 : Iter<B>, other2 : Iter<C>) : Iter<(A, B, C)>`
- `func zip<A, B>(self : Iter<A>, other : Iter<B>) : Iter<(A, B)>`
- `func zipWith3<A, B, C, R>(self : Iter<A>, other1 : Iter<B>, other2 : Iter<C>, f : (A, B, C) -> R) : Iter<R>`
- `func zipWith<A, B, R>(self : Iter<A>, other : Iter<B>, f : (A, B) -> R) : Iter<R>`
- `type Iter<T> = Types.Iter<T>`

## List

- `func add<T>(self : List<T>, element : T)`
- `func addAll<T>(self : List<T>, iter : Types.Iter<T>)`
- `func addRepeat<T>(self : List<T>, initValue : T, count : Nat)`
- `func all<T>(self : List<T>, predicate : T -> Bool) : Bool`
- `func any<T>(self : List<T>, predicate : T -> Bool) : Bool`
- `func append<T>(self : List<T>, added : List<T>)`
- `func at<T>(self : List<T>, index : Nat) : T`
- `func binarySearch<T>(self : List<T>, compare : (implicit : (T, T) -> Types.Order), element : T) : { #found : Nat; #insertionIndex : Nat }`
- `func clear<T>(self : List<T>)`
- `func clone<T>(self : List<T>) : List<T>`
- `func compare<T>(self : List<T>, other : List<T>, compare : (implicit : (T, T) -> Types.Order)) : Types.Order`
- `func contains<T>(self : List<T>, equal : (implicit : (T, T) -> Bool), element : T) : Bool`
- `func deduplicate<T>(self : List<T>, equal : (implicit : (T, T) -> Bool))`
- `func empty<T>() : List<T>`
- `func enumerate<T>(self : List<T>) : Types.Iter<(Nat, T)>`
- `func equal<T>(self : List<T>, other : List<T>, equal : (implicit : (T, T) -> Bool)) : Bool`
- `func fill<T>(self : List<T>, value : T)`
- `func filter<T>(self : List<T>, predicate : T -> Bool) : List<T>`
- `func filterMap<T, R>(self : List<T>, f : T -> ?R) : List<R>`
- `func find<T>(self : List<T>, predicate : T -> Bool) : ?T`
- `func findIndex<T>(self : List<T>, predicate : T -> Bool) : ?Nat`
- `func findLastIndex<T>(self : List<T>, predicate : T -> Bool) : ?Nat`
- `func first<T>(self : List<T>) : ?T`
- `func flatMap<T, R>(self : List<T>, k : T -> Types.Iter<R>) : List<R>`
- `func flatten<T>(self : List<List<T>>) : List<T>`
- `func foldLeft<A, T>(self : List<T>, base : A, combine : (A, T) -> A) : A`
- `func foldRight<T, A>(self : List<T>, base : A, combine : (T, A) -> A) : A`
- `func forEach<T>(self : List<T>, f : T -> ())`
- `func forEachEntry<T>(self : List<T>, f : (Nat, T) -> ())`
- `func forEachInRange<T>(self : List<T>, f : T -> (), fromInclusive : Nat, toExclusive : Nat)`
- `func fromArray<T>(array : [T]) : List<T>`
- `func fromIter<T>(iter : Types.Iter<T>) : List<T>`
- `func fromVarArray<T>(array : [var T]) : List<T>`
- `func get<T>(self : List<T>, index : Nat) : ?T`
- `func indexOf<T>(self : List<T>, equal : (implicit : (T, T) -> Bool), element : T) : ?Nat`
- `func isEmpty<T>(self : List<T>) : Bool`
- `func isSorted<T>(self : List<T>, compare : (implicit : (T, T) -> Types.Order)) : Bool`
- `func join<T>(self : Types.Iter<List<T>>) : List<T>`
- `func keys<T>(self : List<T>) : Types.Iter<Nat>`
- `func last<T>(self : List<T>) : ?T`
- `func lastIndexOf<T>(self : List<T>, equal : (implicit : (T, T) -> Bool), element : T) : ?Nat`
- `func map<T, R>(self : List<T>, f : T -> R) : List<R>`
- `func mapEntries<T, R>(self : List<T>, f : (T, Nat) -> R) : List<R>`
- `func mapInPlace<T>(self : List<T>, f : T -> T)`
- `func mapResult<T, R, E>(self : List<T>, f : T -> Types.Result<R, E>) : Types.Result<List<R>, E>`
- `func max<T>(self : List<T>, compare : (implicit : (T, T) -> Types.Order)) : ?T`
- `func min<T>(self : List<T>, compare : (implicit : (T, T) -> Types.Order)) : ?T`
- `func nextIndexOf<T>(self : List<T>, equal : (implicit : (T, T) -> Bool), element : T, fromInclusive : Nat) : ?Nat`
- `func prevIndexOf<T>(self : List<T>, equal : (implicit : (T, T) -> Bool), element : T, fromExclusive : Nat) : ?Nat`
- `func put<T>(self : List<T>, index : Nat, value : T)`
- `func range<T>(self : List<T>, fromInclusive : Int, toExclusive : Int) : Types.Iter<T>`
- `func reader<T>(self : List<T>, start : Nat) : () -> T`
- `func removeLast<T>(self : List<T>) : ?T`
- `func repeat<T>(initValue : T, size : Nat) : List<T>`
- `func retain<T>(self : List<T>, predicate : T -> Bool)`
- `func reverse<T>(self : List<T>) : List<T>`
- `func reverseEnumerate<T>(self : List<T>) : Types.Iter<(Nat, T)>`
- `func reverseForEach<T>(self : List<T>, f : T -> ())`
- `func reverseForEachEntry<T>(self : List<T>, f : (Nat, T) -> ())`
- `func reverseInPlace<T>(self : List<T>)`
- `func reverseValues<T>(self : List<T>) : Types.Iter<T>`
- `func singleton<T>(element : T) : List<T>`
- `func size<T>(self : List<T>) : Nat`
- `func sliceToArray<T>(self : List<T>, fromInclusive : Int, toExclusive : Int) : [T]`
- `func sliceToVarArray<T>(self : List<T>, fromInclusive : Int, toExclusive : Int) : [var T]`
- `func sort<T>(self : List<T>, compare : (implicit : (T, T) -> Types.Order)) : List<T>`
- `func sortInPlace<T>(self : List<T>, compare : (implicit : (T, T) -> Types.Order))`
- `func tabulate<T>(size : Nat, generator : Nat -> T) : List<T>`
- `func toArray<T>(self : List<T>) : [T]`
- `func toList<T>(self : Types.Iter<T>) : List<T>`
- `func toText<T>(self : List<T>, toText : (implicit : T -> Text)) : Text`
- `func toVarArray<T>(self : List<T>) : [var T]`
- `func truncate<T>(self : List<T>, newSize : Nat)`
- `func values<T>(self : List<T>) : Types.Iter<T>`
- `type List<T> = Types.List<T>`

## Map

- `func add<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K, value : V)`
- `func all<K, V>(self : Map<K, V>, predicate : (K, V) -> Bool) : Bool`
- `func any<K, V>(self : Map<K, V>, predicate : (K, V) -> Bool) : Bool`
- `func clear<K, V>(self : Map<K, V>)`
- `func clone<K, V>(self : Map<K, V>) : Map<K, V>`
- `func compare<K, V>(self : Map<K, V>, other : Map<K, V>, compareKey : (implicit : (compare : (K, K) -> Order.Order)), compareValue : (implicit : (compare : (V, V) -> Order.Order))) : Order.Order`
- `func containsKey<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K) : Bool`
- `func empty<K, V>() : Map<K, V>`
- `func entries<K, V>(self : Map<K, V>) : Types.Iter<(K, V)>`
- `func entriesFrom<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K) : Types.Iter<(K, V)>`
- `func equal<K, V>(self : Map<K, V>, other : Map<K, V>, compare : (implicit : (K, K) -> Types.Order), equal : (implicit : (V, V) -> Bool)) : Bool`
- `func filter<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), criterion : (K, V) -> Bool) : Map<K, V>`
- `func filterMap<K, V1, V2>(self : Map<K, V1>, compare : (implicit : (K, K) -> Order.Order), project : (K, V1) -> ?V2) : Map<K, V2>`
- `func foldLeft<K, V, A>(self : Map<K, V>, base : A, combine : (A, K, V) -> A) : A`
- `func foldRight<K, V, A>(self : Map<K, V>, base : A, combine : (K, V, A) -> A) : A`
- `func forEach<K, V>(self : Map<K, V>, operation : (K, V) -> ())`
- `func fromArray<K, V>(array : [(K, V)], compare : (implicit : (K, K) -> Order.Order)) : Map<K, V>`
- `func fromIter<K, V>(iter : Types.Iter<(K, V)>, compare : (implicit : (K, K) -> Order.Order)) : Map<K, V>`
- `func fromVarArray<K, V>(array : [var (K, V)], compare : (implicit : (K, K) -> Order.Order)) : Map<K, V>`
- `func get<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K) : ?V`
- `func isEmpty<K, V>(self : Map<K, V>) : Bool`
- `func keys<K, V>(self : Map<K, V>) : Types.Iter<K>`
- `func map<K, V1, V2>(self : Map<K, V1>, project : (K, V1) -> V2) : Map<K, V2>`
- `func maxEntry<K, V>(self : Map<K, V>) : ?(K, V)`
- `func minEntry<K, V>(self : Map<K, V>) : ?(K, V)`
- `func remove<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K)`
- `func replace<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K, value : V) : ?V`
- `func reverseEntries<K, V>(self : Map<K, V>) : Types.Iter<(K, V)>`
- `func reverseEntriesFrom<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K) : Types.Iter<(K, V)>`
- `func singleton<K, V>(key : K, value : V) : Map<K, V>`
- `func size<K, V>(self : Map<K, V>) : Nat`
- `func swap<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K, value : V) : ?V`
- `func take<K, V>(self : Map<K, V>, compare : (implicit : (K, K) -> Order.Order), key : K) : ?V`
- `func toArray<K, V>(self : Map<K, V>) : [(K, V)]`
- `func toMap<K, V>(self : Types.Iter<(K, V)>, compare : (implicit : (K, K) -> Order.Order)) : Map<K, V>`
- `func toText<K, V>(self : Map<K, V>, keyFormat : (implicit : (toText : K -> Text)), valueFormat : (implicit : (toText : V -> Text))) : Text`
- `func toVarArray<K, V>(self : Map<K, V>) : [var (K, V)]`
- `func values<K, V>(self : Map<K, V>) : Types.Iter<V>`
- `type Map<K, V> = Types.Map<K, V>`

## Nat

- `func add(x : Nat, y : Nat) : Nat`
- `func allValues() : Iter.Iter<Nat>`
- `func bitshiftLeft(x : Nat, y : Nat32) : Nat`
- `func bitshiftRight(x : Nat, y : Nat32) : Nat`
- `func compare(x : Nat, y : Nat) : Order.Order`
- `func div(x : Nat, y : Nat) : Nat`
- `func equal(x : Nat, y : Nat) : Bool`
- `func fromText(text : Text) : ?Nat`
- `func greater(x : Nat, y : Nat) : Bool`
- `func greaterOrEqual(x : Nat, y : Nat) : Bool`
- `func less(x : Nat, y : Nat) : Bool`
- `func lessOrEqual(x : Nat, y : Nat) : Bool`
- `func max(x : Nat, y : Nat) : Nat`
- `func min(x : Nat, y : Nat) : Nat`
- `func mul(x : Nat, y : Nat) : Nat`
- `func notEqual(x : Nat, y : Nat) : Bool`
- `func pow(x : Nat, y : Nat) : Nat`
- `func range(fromInclusive : Nat, toExclusive : Nat) : Iter.Iter<Nat>`
- `func rangeBy(fromInclusive : Nat, toExclusive : Nat, step : Int) : Iter.Iter<Nat>`
- `func rangeByInclusive(from : Nat, to : Nat, step : Int) : Iter.Iter<Nat>`
- `func rangeInclusive(from : Nat, to : Nat) : Iter.Iter<Nat>`
- `func rem(x : Nat, y : Nat) : Nat`
- `func sub(x : Nat, y : Nat) : Nat`
- `func toFloat(self : Nat) : Float`
- `func toInt(self : Nat) : Int`
- `func toNat(self : Text) : ?Nat`
- `func toNat16(self : Nat) : Nat16`
- `func toNat32(self : Nat) : Nat32`
- `func toNat64(self : Nat) : Nat64`
- `func toNat8(self : Nat) : Nat8`
- `func toText(self : Nat) : Text`
- `type Nat = Prim.Types.Nat`

## Option

- `func apply<T, R>(self : ?T, f : ?(T -> R)) : ?R`
- `func chain<T, R>(self : ?T, f : T -> ?R) : ?R`
- `func compare<T>(self : ?T, other : ?T, compare : (implicit : (T, T) -> Types.Order)) : Types.Order`
- `func equal<T>(self : ?T, other : ?T, eq : (implicit : (equal : (T, T) -> Bool))) : Bool`
- `func flatten<T>(self : ??T) : ?T`
- `func forEach<T>(self : ?T, f : T -> ())`
- `func get<T>(self : ?T, default : T) : T`
- `func getMapped<T, R>(self : ?T, f : T -> R, default : R) : R`
- `func isNull(self : ?Any) : Bool`
- `func isSome(self : ?Any) : Bool`
- `func map<T, R>(self : ?T, f : T -> R) : ?R`
- `func some<T>(self : T) : ?T`
- `func toText<T>(self : ?T, toText : (implicit : T -> Text)) : Text`
- `func unwrap<T>(self : ?T) : T`

## Order

- `func allValues() : Types.Iter<Order>`
- `func equal(self : Order, other : Order) : Bool`
- `func isEqual(self : Order) : Bool`
- `func isGreater(self : Order) : Bool`
- `func isLess(self : Order) : Bool`
- `type Order = Types.Order`

## Principal

- `func anonymous() : Principal`
- `func compare(self : Principal, other : Principal) : { #less; #equal; #greater }`
- `func equal(self : Principal, other : Principal) : Bool`
- `func fromActor(a : actor {}) : Principal`
- `func fromBlob(blob : Blob) : Principal`
- `func fromText(t : Text) : Principal`
- `func greater(self : Principal, other : Principal) : Bool`
- `func greaterOrEqual(self : Principal, other : Principal) : Bool`
- `func hash(self : Principal) : Types.Hash`
- `func isAnonymous(self : Principal) : Bool`
- `func isCanister(self : Principal) : Bool`
- `func isController(self : Principal) : Bool`
- `func isReserved(self : Principal) : Bool`
- `func isSelfAuthenticating(self : Principal) : Bool`
- `func less(self : Principal, other : Principal) : Bool`
- `func lessOrEqual(self : Principal, other : Principal) : Bool`
- `func notEqual(self : Principal, other : Principal) : Bool`
- `func toActor<A <: actor {}>(p : Principal) : A`
- `func toBlob(self : Principal) : Blob`
- `func toLedgerAccount(self : Principal, subAccount : ?Blob) : Blob`
- `func toText(self : Principal) : Text`
- `type Principal = Prim.Types.Principal`

## Queue

- `func all<T>(self : Queue<T>, predicate : T -> Bool) : Bool`
- `func any<T>(self : Queue<T>, predicate : T -> Bool) : Bool`
- `func clear<T>(self : Queue<T>)`
- `func clone<T>(self : Queue<T>) : Queue<T>`
- `func compare<T>(self : Queue<T>, other : Queue<T>, compare : (implicit : (T, T) -> Order.Order)) : Order.Order`
- `func contains<T>(self : Queue<T>, equal : (implicit : (T, T) -> Bool), element : T) : Bool`
- `func empty<T>() : Queue<T>`
- `func equal<T>(self : Queue<T>, other : Queue<T>, equal : (implicit : (T, T) -> Bool)) : Bool`
- `func filter<T>(self : Queue<T>, criterion : T -> Bool) : Queue<T>`
- `func filterMap<T, U>(self : Queue<T>, project : T -> ?U) : Queue<U>`
- `func forEach<T>(self : Queue<T>, operation : T -> ())`
- `func fromArray<T>(array : [T]) : Queue<T>`
- `func fromIter<T>(iter : Iter.Iter<T>) : Queue<T>`
- `func fromVarArray<T>(array : [var T]) : Queue<T>`
- `func isEmpty<T>(self : Queue<T>) : Bool`
- `func map<T, U>(self : Queue<T>, project : T -> U) : Queue<U>`
- `func peekBack<T>(self : Queue<T>) : ?T`
- `func peekFront<T>(self : Queue<T>) : ?T`
- `func popBack<T>(self : Queue<T>) : ?T`
- `func popFront<T>(self : Queue<T>) : ?T`
- `func pushBack<T>(self : Queue<T>, element : T)`
- `func pushFront<T>(self : Queue<T>, element : T)`
- `func reverseValues<T>(self : Queue<T>) : Iter.Iter<T>`
- `func singleton<T>(element : T) : Queue<T>`
- `func size<T>(self : Queue<T>) : Nat`
- `func toArray<T>(self : Queue<T>) : [T]`
- `func toQueue<T>(self : Iter.Iter<T>) : Queue<T>`
- `func toText<T>(self : Queue<T>, format : (implicit : (toText : T -> Text))) : Text`
- `func toVarArray<T>(self : Queue<T>) : [var T]`
- `func values<T>(self : Queue<T>) : Iter.Iter<T>`
- `type Queue<T> = Types.Queue.Queue<T>`

## Result

- `func assertErr(self : Result<Any, Any>)`
- `func assertOk(self : Result<Any, Any>)`
- `func chain<Ok1, Ok2, Err>(self : Result<Ok1, Err>, f : Ok1 -> Result<Ok2, Err>) : Result<Ok2, Err>`
- `func compare<Ok, Err>(self : Result<Ok, Err>, other : Result<Ok, Err>, compareOk : (implicit : (compare : (Ok, Ok) -> Order.Order)), compareErr : (implicit : (compare : (Err, Err) -> Order.Order))) : Order.Order`
- `func equal<Ok, Err>(self : Result<Ok, Err>, other : Result<Ok, Err>, equalOk : (implicit : (equal : Ok, Ok) -> Bool), equalErr : (implicit : (equal : (Err, Err) -> Bool))) : Bool`
- `func flatten<Ok, Err>(self : Result<Result<Ok, Err>, Err>) : Result<Ok, Err>`
- `func forErr<Ok, Err>(self : Result<Ok, Err>, f : Err -> ())`
- `func forOk<Ok, Err>(self : Result<Ok, Err>, f : Ok -> ())`
- `func fromOption<Ok, Err>(x : ?Ok, err : Err) : Result<Ok, Err>`
- `func fromUpper<Ok, Err>(result : { #Ok : Ok; #Err : Err }) : Result<Ok, Err>`
- `func isErr(self : Result<Any, Any>) : Bool`
- `func isOk(self : Result<Any, Any>) : Bool`
- `func mapErr<Ok, Err1, Err2>(self : Result<Ok, Err1>, f : Err1 -> Err2) : Result<Ok, Err2>`
- `func mapOk<Ok1, Ok2, Err>(self : Result<Ok1, Err>, f : Ok1 -> Ok2) : Result<Ok2, Err>`
- `func toOption<Ok, Err>(self : Result<Ok, Err>) : ?Ok`
- `func toUpper<Ok, Err>(self : Result<Ok, Err>) : { #Ok : Ok; #Err : Err }`
- `type Result<Ok, Err> = Types.Result<Ok, Err>`

## Runtime

- `func envVar<system>(name : Text) : ?Text`
- `func envVarNames<system>() : [Text]`
- `func trap(errorMessage : Text) : None`
- `func unreachable() : None`

## Set

- `func add<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), element : T)`
- `func addAll<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), iter : Types.Iter<T>)`
- `func all<T>(self : Set<T>, predicate : T -> Bool) : Bool`
- `func any<T>(self : Set<T>, predicate : T -> Bool) : Bool`
- `func clear<T>(self : Set<T>)`
- `func clone<T>(self : Set<T>) : Set<T>`
- `func compare<T>(self : Set<T>, other : Set<T>, compare : (implicit : (T, T) -> Order.Order)) : Order.Order`
- `func contains<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), element : T) : Bool`
- `func deleteAll<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), iter : Types.Iter<T>) : Bool`
- `func difference<T>(self : Set<T>, other : Set<T>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func empty<T>() : Set<T>`
- `func equal<T>(self : Set<T>, other : Set<T>, compare : (implicit : (T, T) -> Types.Order)) : Bool`
- `func filter<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), criterion : T -> Bool) : Set<T>`
- `func filterMap<T1, T2>(self : Set<T1>, compare : (implicit : (T2, T2) -> Order.Order), project : T1 -> ?T2) : Set<T2>`
- `func flatten<T>(self : Set<Set<T>>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func foldLeft<T, A>(self : Set<T>, base : A, combine : (A, T) -> A) : A`
- `func foldRight<T, A>(self : Set<T>, base : A, combine : (T, A) -> A) : A`
- `func forEach<T>(self : Set<T>, operation : T -> ())`
- `func fromArray<T>(array : [T], compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func fromIter<T>(iter : Types.Iter<T>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func insertAll<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), iter : Types.Iter<T>) : Bool`
- `func intersection<T>(self : Set<T>, other : Set<T>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func isEmpty<T>(self : Set<T>) : Bool`
- `func isSubset<T>(self : Set<T>, other : Set<T>, compare : (implicit : (T, T) -> Order.Order)) : Bool`
- `func join<T>(setIterator : Types.Iter<Set<T>>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func map<T1, T2>(self : Set<T1>, compare : (implicit : (T2, T2) -> Order.Order), project : T1 -> T2) : Set<T2>`
- `func max<T>(self : Set<T>) : ?T`
- `func min<T>(self : Set<T>) : ?T`
- `func remove<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), element : T) : ()`
- `func retainAll<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), predicate : T -> Bool) : Bool`
- `func reverseValues<T>(self : Set<T>) : Types.Iter<T>`
- `func reverseValuesFrom<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), element : T) : Types.Iter<T>`
- `func singleton<T>(element : T) : Set<T>`
- `func size<T>(self : Set<T>) : Nat`
- `func toArray<T>(self : Set<T>) : [T]`
- `func toSet<T>(self : Types.Iter<T>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func toText<T>(self : Set<T>, toText : (implicit : T -> Text)) : Text`
- `func union<T>(self : Set<T>, other : Set<T>, compare : (implicit : (T, T) -> Order.Order)) : Set<T>`
- `func values<T>(self : Set<T>) : Types.Iter<T>`
- `func valuesFrom<T>(self : Set<T>, compare : (implicit : (T, T) -> Order.Order), element : T) : Types.Iter<T>`
- `type Set<T> = Types.Set.Set<T>`

## Stack

- `func all<T>(self : Stack<T>, predicate : T -> Bool) : Bool`
- `func any<T>(self : Stack<T>, predicate : T -> Bool) : Bool`
- `func clear<T>(self : Stack<T>)`
- `func clone<T>(self : Stack<T>) : Stack<T>`
- `func compare<T>(self : Stack<T>, other : Stack<T>, compare : (implicit : (T, T) -> Order.Order)) : Order.Order`
- `func contains<T>(self : Stack<T>, equal : (implicit : (T, T) -> Bool), element : T) : Bool`
- `func empty<T>() : Stack<T>`
- `func equal<T>(self : Stack<T>, other : Stack<T>, equal : (implicit : (T, T) -> Bool)) : Bool`
- `func filter<T>(self : Stack<T>, predicate : T -> Bool) : Stack<T>`
- `func filterMap<T, U>(self : Stack<T>, project : T -> ?U) : Stack<U>`
- `func find<T>(self : Stack<T>, predicate : T -> Bool) : ?T`
- `func findIndex<T>(self : Stack<T>, predicate : T -> Bool) : ?Nat`
- `func forEach<T>(self : Stack<T>, operation : T -> ())`
- `func fromArray<T>(array : [T]) : Stack<T>`
- `func fromIter<T>(iter : Types.Iter<T>) : Stack<T>`
- `func fromVarArray<T>(array : [var T]) : Stack<T>`
- `func get<T>(self : Stack<T>, position : Nat) : ?T`
- `func isEmpty<T>(self : Stack<T>) : Bool`
- `func map<T, U>(self : Stack<T>, project : T -> U) : Stack<U>`
- `func peek<T>(self : Stack<T>) : ?T`
- `func pop<T>(self : Stack<T>) : ?T`
- `func push<T>(self : Stack<T>, value : T)`
- `func reverse<T>(self : Stack<T>)`
- `func reverseValues<T>(self : Stack<T>) : Iter.Iter<T>`
- `func singleton<T>(element : T) : Stack<T>`
- `func size<T>(self : Stack<T>) : Nat`
- `func tabulate<T>(size : Nat, generator : Nat -> T) : Stack<T>`
- `func toArray<T>(self : Stack<T>) : [T]`
- `func toStack<T>(self : Types.Iter<T>) : Stack<T>`
- `func toText<T>(self : Stack<T>, format : (implicit : (toText : T -> Text))) : Text`
- `func toVarArray<T>(self : Stack<T>) : [var T]`
- `func values<T>(self : Stack<T>) : Types.Iter<T>`
- `type Stack<T> = Types.Stack<T>`

## Text

- `func compare(self : Text, other : Text) : Order.Order`
- `func compareWith(self : Text, other : Text, compare : (Char, Char) -> Order.Order) : Order.Order`
- `func concat(self : Text, other : Text) : Text`
- `func contains(self : Text, p : Pattern) : Bool`
- `func decodeUtf8(self : Blob) : ?Text`
- `func encodeUtf8(self : Text) : Blob`
- `func endsWith(self : Text, p : Pattern) : Bool`
- `func equal(self : Text, other : Text) : Bool`
- `func flatMap(self : Text, f : Char -> Text) : Text`
- `func foldLeft<A>(self : Text, base : A, combine : (A, Char) -> A) : A`
- `func fromArray(a : [Char]) : Text`
- `func fromIter(cs : Iter.Iter<Char>) : Text`
- `func fromVarArray(a : [var Char]) : Text`
- `func greater(self : Text, other : Text) : Bool`
- `func greaterOrEqual(self : Text, other : Text) : Bool`
- `func isEmpty(self : Text) : Bool`
- `func join(self : Iter.Iter<Text>, sep : Text) : Text`
- `func less(self : Text, other : Text) : Bool`
- `func lessOrEqual(self : Text, other : Text) : Bool`
- `func map(self : Text, f : Char -> Char) : Text`
- `func notEqual(self : Text, other : Text) : Bool`
- `func replace(self : Text, p : Pattern, r : Text) : Text`
- `func reverse(self : Text) : Text`
- `func size(self : Text) : Nat`
- `func split(self : Text, p : Pattern) : Iter.Iter<Text>`
- `func startsWith(self : Text, p : Pattern) : Bool`
- `func stripEnd(self : Text, p : Pattern) : ?Text`
- `func stripStart(self : Text, p : Pattern) : ?Text`
- `func toArray(self : Text) : [Char]`
- `func toIter(self : Text) : Iter.Iter<Char>`
- `func toLower(self : Text) : Text`
- `func toText(self : Text) : Text`
- `func toUpper(self : Text) : Text`
- `func toVarArray(self : Text) : [var Char]`
- `func tokens(self : Text, p : Pattern) : Iter.Iter<Text>`
- `func trim(self : Text, p : Pattern) : Text`
- `func trimEnd(self : Text, p : Pattern) : Text`
- `func trimStart(self : Text, p : Pattern) : Text`
- `type Pattern = Types.Pattern`
- `type Text = Prim.Types.Text`

## Time

- `func now() : Time`
- `func toNanoseconds(duration : Duration) : Nat`
- `type Duration = Types.Duration`
- `type Time = Types.Time`
- `type TimerId = Nat`

> No `Time.compare` — use `Int.compare` to compare times.

## Timer

- `func cancelTimer(TimerId) : ()`
- `func recurringTimer<system>(duration : Time.Duration, job : () -> async ()) : TimerId`
- `func setTimer<system>(duration : Time.Duration, job : () -> async ()) : TimerId`
- `type TimerId = Nat`
