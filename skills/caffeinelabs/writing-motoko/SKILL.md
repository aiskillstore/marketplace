---
name: writing-motoko
description: >-
  Motoko language reference, architecture patterns, and dependency tooling
  (mops). Load when writing or modifying backend .mo files.
version: 0.2.9
compatibility:
  toolchain:
    moc: ">=1.11.2"
    mops: "3.x"
  mops:
    core: ">=2.6.0"
caffeineai-subscription: [none]
---

# Writing Motoko

Motoko is an under-represented language for the Internet Computer Protocol, so your pre-training data is likely to be outdated — always favour this skill and its documentation for the most up-to-date information.

## Critical Requirements

**NEVER use these:**

- `stable` keyword -- Not needed in enhanced orthogonal persistence mode
- `mo:base` library -- Deprecated. Use `mo:core` instead
- `.vals()` -- The deprecated `mo:base` iterator name. Always `.values()`. On arrays `.vals()` still compiles, so nothing flags it; on core collections it fails with M0072
- `system func preupgrade/postupgrade` -- Not needed with enhanced orthogonal persistence
- `(with migration = ...)` actor-attached migration syntax -- Use the mops-managed migration chain in `migrations/`
- Inline initializers on stable actor fields -- Initial values come from the migration chain (see `migrating-motoko-actors`)
- Module function style for `self` parameters -- Don't write `List.add(list, item)` or `Map.get(map, key)`
- Manual field-by-field record copying for immutable records -- Use record spread (`{ self with ... }`). For records with `var` fields, do not use record spread; mutate the `var` field directly or rebuild the record explicitly.
- Single-file monolithic actors -- Use the multi-file architecture: types.mo, lib/, mixins/, main.mo
- Stable state in a `mixin` block -- a bare `let`/`var` is silently stable and traps at runtime (`IC0503`). Pass state in as a parameter and keep constants in a module
- Any Motoko reserved keyword as a declared identifier -- Before writing, check parameter, variable, function, type, field, and label names against the full list in [references/reserved-keywords.md](references/reserved-keywords.md). `query` and `label` are reserved and must never be identifiers. Rename a colliding domain term instead of relying on its position or inferred meaning.
- Type annotations on an inline `func` passed as a **call argument** -- write `xs.filter(func x = x > 1)`, not `xs.filter(func(x : Nat) : Bool { x > 1 })`. The call supplies the types. If a generic cannot be inferred, instantiate the call (`map<In, Out>`), never the lambda. This applies only in argument position — named declarations still carry full signatures. **One exception:** keep `: async ()` on an async callback (`func() : async () { ... }`) — it is what makes the body async, and removing it fails with M0096

**ALWAYS use:**

- `mo:core` library version 2.6.0+ (compiler `moc` 1.11.2+)
- Contextual dot notation -- `list.add(item)`, `map.get(key)`
- An import of the key type's module in every file that operates on a `Map`/`Set` -- the implicit `compare` is resolved from the imported module (`import Nat "mo:core/Nat"` for a `Map.Map<Nat, _>`), never from the type alone. A missing key-module import is the usual cause of M0230; a record or variant key needs its own module with a `compare` (see Implicit Parameters)
- Null coalesce `??` for unwrap-or-default and unwrap-or-trap (`opt ?? default`, `opt ?? Runtime.trap(...)`) -- prefer over a two-arm `switch` on `?T` (requires `moc >= 1.7.0`)
- Plain `break` / `continue` to exit or skip a loop iteration -- they work inside `for`, `while`, and `loop` just like in other languages
- Enhanced orthogonal persistence (state persists without `stable` keyword)
- Principled Motoko Architecture -- `types.mo` (types), `lib/` (domain logic), `mixins/` (API endpoints), `main.mo` (composition root, NO public methods)
- **API reference for uncertain APIs**: Use [api-reference.md](api-reference.md) to verify exact method signatures when you are about to use an unfamiliar `mo:core` API or when a compile diagnostic points at an API mismatch. It lists only non-deprecated APIs — a symbol that is not there should not be written. Do NOT guess API shapes — a targeted lookup of a symbol you are unsure about is always worth the step; skipping it to save steps ships hallucinated APIs and costs far more in compile repair.

**When encountering compilation errors:** Re-check [api-reference.md](api-reference.md) for exact method signatures.

**Before changing actor state shape, introducing new stable fields, or upgrading canisters:** load `migrating-motoko-actors`. This guidance assumes the **mops-managed migration chain** — when a change requires a migration, it goes in the pending migration file, or a new one in `src/backend/migrations/` if none is pending. Introducing stable state for the first time always needs one (no inline initializers); trivial stable-compatible upgrades do not. See the skill. If a migration or compatibility diagnostic still does not match what the source says, or a migration file cannot be written, load `troubleshooting-motoko-migrations`.

## Toolchain (mops)

All configuration is in `mops.toml`. Only consult https://docs.mops.one/ if you encounter an unfamiliar mops error.

### Dependency management

- Never hand-edit dependency entries in `mops.toml`, and never touch `mops.lock`; use the `mops` CLI so dependency metadata and the lockfile stay atomic. (`[toolchain]` has a CLI too: `mops toolchain use <tool> [version]`.)
- Leave `[moc] args` alone. Compiler flags are a one-time project-setup concern, and many platforms own `mops.toml` and set them for you — do not inspect or change them while writing code. If you are setting up a project yourself, see [references/project-setup.md](references/project-setup.md).
- `mops add <pkg>` installs and exact-pins a published package. Use `@x.y.z` for a specific version, `<url>[#ref]` for GitHub, `./path` for a local package, and `--dev` for development dependencies.
- `mops add` accepts exactly one package name. To install several packages, chain one-package commands with `&&`; never run multiple `mops add` invocations in parallel — they race on `mops.toml` and `mops.lock`.
- `mops update [pkg]` updates a package and rewrites its exact pin.
- `mops sync` reconciles imports after bulk `.mo` changes by adding missing dependencies and removing unused ones.
- `mops.lock` is rewritten only by `mops add`, `mops update`, `mops sync`, `mops install`, and related supported mops commands.
- On a lock or integrity failure, run `mops install` — it regenerates a `mops.lock` that is missing, stale, or inconsistent with `mops.toml`. `mops verify` reports a file-hash mismatch it cannot repair; `mops cache clean` forces a verified re-download. Never `chmod`, remove, or text-edit `mops.lock`.

### Check and build

- **`mops install`** — Install dependencies and reconcile `mops.lock`, regenerating it when it is missing or no longer matches `mops.toml`.
- **`mops check --fix`** (fast — use for iteration) — Reports compile errors and auto-fixes the style warnings, where the project has them enabled (dot-notation, redundant type instantiation, redundant implicit arguments). Follow this skill's rules whether or not `--fix` enforces them. Exit 0 = success. Error format: `file:startLine.startCol-endLine.endCol: severity [code], message`. Iterate on this until it passes.
- **`mops build`** (slow — run ONCE at the end) — Produces the compiled `.wasm` and the candid interface file `.did`. Use only as final verification after `mops check --fix` passes; never put `mops build` inside the fix loop. The `.did` file drives generated client bindings — never edit it manually.

If `mops check --fix` fails: read stderr first. Do NOT call `moc` directly. Fix `.mo` source and rerun the check.

## Modern Motoko Features

### Contextual Dot Notation

**RULE:** When a function has a `self` parameter, ALWAYS use dot notation.
Dot notation is still type-specific: it only applies to APIs that the value's
module actually defines — verify against [api-reference.md](api-reference.md)
rather than inferring JavaScript-style helpers. `.some(...)` and `.every(...)`
do not exist in Motoko; the `mo:core` names are `.any(...)` and `.all(...)`.

The module a dot call resolves against is the module that **defines** the
function — usually the receiver's type's module (`map.get`, `list.add`), but
sometimes a different one: `arr.values().toList()` resolves against `List` (the
target), not the array's module. The import needed (if any) is the defining
module's, not the receiver's.

```motoko
map.get(key);
list.add(item);
array.filter(func x = x > 0); // CORRECT
Map.get(map, key);
List.add(list, item); // WRONG (M0236)

// Chaining
let doubled = numbers.map(func x = x * 2).filter(func x = x > 10);

```

Conversions are receiver calls too, but the `toX` functions are split across
modules: some are defined on the **source** module (`Nat8.toNat`), others on the
**target** (`"42".toNat()` and `"-5".toInt()` are defined by `Nat` and `Int`,
not `Text`). So `Text`-receiver conversions need the target imported (`import
Nat "mo:core/Nat"`, `import Int "mo:core/Int"`); without it, moc reports
M0070/M0072 and the call does not compile:

```motoko project=dot-notation filepath=src/backend/main.mo
import Principal "mo:core/Principal";
import Nat "mo:core/Nat";
import Text "mo:core/Text";

func conversions(caller : Principal, myNat : Nat) {
  ignore caller.toText();            // CORRECT
  ignore myNat.toText();             // CORRECT
  ignore "42".toNat();               // CORRECT (defined by Nat, imported above)
  ignore "hello".concat(" world");   // CORRECT
  ignore Principal.toText(caller);   // WRONG (M0236)
  ignore Nat.toText(myNat);          // WRONG (M0236)
};
```

**`equal` / `compare` vs `==`.** Collections take `equal` and `compare` as implicit arguments, so those are the functions to write for your own records and variants. `==` is compiler-generated structural equality and exists only for **shared** types — one `var` field takes a record out of shared and `==` stops compiling (M0060) — so do not build record comparisons on it. Comparing primitives and shared fields directly with `==` is fine, and on `Nat`, `Int`, `Float`, and the sized int types it is the only form: those declare `equal(x, y)` without a `self` parameter, so `myNat.equal(other)` fails with M0070. Other receiver methods on those types (`myNat.toText()`) are fine.

Your own records and variants get nothing derived — a record `compare` must be an explicit function, and custom variants need both `equal` and `compare` written out. See [references/equality.md](references/equality.md).

### Mixins

Composable actor services with granular state injection. Each mixin lives in its own file as a top-level `mixin` block:

```motoko project=mixin filepath=src/backend/types.mo
module {
  public type User = {
    principal : Principal;
    username : Text;
  };
};
```

```motoko project=mixin filepath=src/backend/mixins/Auth.mo
import List "mo:core/List";
import Principal "mo:core/Principal";
import Types "../types";

mixin (users : List.List<Types.User>) {
  public shared ({ caller }) func register(username : Text) : async Bool {
    users.add({ principal = caller; username });
    true
  };

  public query func listUsers() : async [Types.User] {
    users.toArray()
  };
};
```

```motoko project=mixin filepath=src/backend/main.mo
import List "mo:core/List";
import Types "types";
import AuthMixin "mixins/Auth";

actor {
  let users : List.List<Types.User>;
  include AuthMixin(users);
};
```

**Mixin Anti-Patterns — NEVER generate these:**

```motoko
// WRONG — mixin is NOT a function inside a module; wrapping in module {} is invalid
module {
  public func createMixin(state : ...) : actor { ... } { // M0001: unexpected token 'actor'
    actor { public func foo() { ... }; };
  };
}

// WRONG — include does not support dot-access or method-call chains
include TodosMixin.createMixin(state); // M0001: unexpected token '.'

// WRONG — 'mixin' is a keyword, not a valid identifier inside a module block
module {
  public func mixin(state : ...) { ... }; // M0001: unexpected token 'mixin'
}
```

Rules:
- A mixin file contains a bare `mixin (params) { ... };` block at the **top level** — not inside `module {}`, not returned from a function.
- `include` takes a bare name followed by arguments: `include MixinName(args)` — no dot-access, no chained calls.

**No stable state in Mixins.** Every top-level `let`/`var` in a `mixin` is implicitly **stable**. Only `transient` is ever allowed, but prefer putting static definitions (like literals) into modules instead!

**Sharing state between mixins — pass it as a parameter.** To share state between two or more mixins, declare that state once as an actor field and pass that same binding to each `include`. Every mixin that gets it reads and writes the same value. A mixin can take several parameters, so it can receive shared state plus its own private state.

```motoko
// types.mo:  public type GoogleState = { var connection : ?Conn; var config : ?Cfg };
let google : Types.GoogleState;          // declared once; initialized in the migration function
let bookings : Map.Map<Nat, Booking>;    // BookingsApi's own state
include GoogleApi(google);               // gets `google`
include BookingsApi(google, bookings);   // gets the SAME `google`, plus its own bookings
```

Pass the same binding to each mixin. Never build a new record at the `include` — that gives each mixin its own separate copy, so one mixin's writes never reach the others:

```motoko
include GoogleApi({ var connection = google.connection });   // WRONG: NEVER DO THIS!
```

### Null Coalesce (`??`)

Prefer `??` over a two-arm `switch` that only unwraps an option or supplies a default / trap. Requires `moc >= 1.7.0`.

```motoko
// Default when absent
let name = optName ?? "anonymous";

// Fail-fast unwrap — null means a bug / missing invariant
let user = users.find(func u = u.id == caller)
  ?? Runtime.trap("User not found");

// Nested options — chain instead of nested switches
let start = event.start.dateTime ?? event.start.date ?? "";

// RHS is lazy. A block needs `do`; a record literal needs parens:
let n = opt ?? do { let x = 1; x };
let rec = opt ?? ({ x = 0 });
```

**Use `switch` instead** when the `?v` arm transforms the value, runs side effects, or you are matching variants / multiple cases — `??` only unwraps or substitutes.

```motoko
// Keep switch: Some arm transforms / branches on the inner value
switch (users.get(caller)) {
  case (?u) { u.isAdmin };
  case null { false };
};

switch (result) {
  case (#ok value) { value };
  case (#err e) { Runtime.trap(e) };
};
```

See [references/control-flow.md](references/control-flow.md).

### Implicit Parameters

`Map` and `Set` operations take the comparison function as an **implicit** argument. `Map.empty()` itself takes no arguments — the comparator is resolved at the operations that need it (`add`, `get`, `remove`, …), not at construction.

Inference works by finding a `compare` in the module imported **for the key type**. So the import is what makes it work:

```motoko
import Map "mo:core/Map";
import Nat "mo:core/Nat"; // this import is what supplies Nat.compare

let map = Map.empty<Nat, Text>();
map.add(5, "hello"); // compare resolved from the imported Nat
```

Without `import Nat`, the same code fails — the type is known, but there is no module to take `compare` from:

```text
type error [M0230], Cannot determine implicit argument `compare` of type (Nat, Nat) -> Order
note: Did you mean to import mo:core/Int or mo:core/Nat?
```

Do **not** pass the comparator explicitly when it can be inferred; that is M0237, which `mops check --fix` removes:

```motoko
let ages = Map.empty<Text, Nat>();   // Text.compare resolved at add, from the imported Text
ages.add("Alice", 30);               // CORRECT
ages.add(Text.compare, "Alice", 30); // WRONG (M0237)
```

A custom key type works the same way — give its module a `compare` and it is inferred:

```motoko
type Point = { x : Nat; y : Nat };
module Point {
  public func compare(a : Point, b : Point) : Order.Order { ... };
};
let points = Map.empty<Point, Text>();
points.add({ x = 1; y = 2 }, "A"); // Point.compare inferred
```

Type instantiation on `empty()` follows the usual rule — needed only when the binding is unannotated. `let m : Map.Map<Nat, Text> = Map.empty();` infers it, and `Map.empty<Nat, Text>()` there would be M0223.

## Architecture Pattern

```text
backend/
├── types.mo         # Central schema, state definitions
├── lib/             # Domain logic (stateless modules with self pattern)
├── mixins/          # Service layer (stateless, state injected via parameters)
├── types/           # Type definitions for mixins and lib modules
├── migrations/      # Mops-managed migration chain. See migrating-motoko-actors.
│                    #   Each file is YYYYMMDD_HHMMSS.mo (a UTC timestamp, not a feature name); applied files are FROZEN.
└── main.mo          # Composition root (state owner, NO public methods)
```

## Import Path Conventions

Paths are **relative to the importing file**. No `.mo` extension, no `/lib.mo` suffix.

```motoko
// From main.mo
import Types "types";
import AuthMixin "mixins/Auth";
import UserLib "lib/User";
// From lib/*.mo or mixins/*.mo
import Types "../types";
import UserLib "../lib/User";
// Core library — always absolute
import Map "mo:core/Map";

// WRONG — these all cause M0009
import Types "types.mo";
import Types "types/lib.mo";
import Types "backend/types";

```

**Migration files** (`migrations/*.mo`) must be self-contained — they may only import from `mo:core/...`, never from `../types` or any project module. See `migrating-motoko-actors` for the full rules.

### The Actor Must Come Last

Imports and `type`/`let` declarations may precede the actor. Nothing may follow it — the actor is the file's result, so a trailing declaration makes the actor a non-`()` statement and fails with M0096 (`expression of type actor {...} cannot produce expected type ()`). Prefer keeping shared types in `types.mo` regardless.

### Import Hygiene

Add an import only to the file that uses the imported identifier. `Time.now()` usually belongs in a domain `lib/*.mo` implementation file, so `import Time "mo:core/Time";` belongs in that file, not `main.mo`, unless `main.mo` itself calls `Time.now()`. Every capitalized namespace call must have a matching import in the same file: if a mixin calls `TodosLib.listTodos(...)`, the file must import `TodosLib "../lib/todos"` (or use the alias it actually imported). Treat unused-import warnings as failures: remove stale `Debug`, `Time`, or helper-module imports before finishing.

## Query Functions

`query` marks a public function as a read-only call: it executes fast and unreplicated, and **every state change it makes is silently discarded when the call completes** — a write inside a query compiles, runs, and vanishes with no error or warning. Declare pure reads as `query func`; any function that must persist a change is a plain update func (no `query`). `public query func` is shorthand for `public shared query func`; both forms take `({ caller })` the same way.

```motoko
public query func getPosts() : async [Types.PostView] { ... };          // read: query
public shared ({ caller }) func addPost(t : Text) : async Nat { ... };  // persists: update
public query func resetAll() : async () { posts.clear() };              // WRONG: compiles, but the clear is discarded
```

### When await is allowed

A plain `query func` cannot call any other canister function, whether that callee is a query or an update. Writing `await someCall()` inside one fails with a paired `M0038` (misplaced await) + `M0188` (send capability required: "cannot call a `shared` function from a `query` function"), always on the same statement. Pick the function kind by what the body must call:

| Body must call                          | Declare                                 | Can `await`                              |
| --------------------------------------- | --------------------------------------- | ---------------------------------------- |
| another canister's `query`/`composite query` | `public shared composite query func` | those query callees                     |
| an update (`shared` func) or oneway     | a normal `public shared func`           | that update                              |
| nothing across canisters                | `public shared query func`              | nothing                                  |

A `composite query` is a read-only function that can `await` other canisters' queries. Loop over callees and `await` each:

```motoko
public shared composite query func sum(counters : [Counter]) : async Nat {
  var total = 0;
  for (counter in counters.values()) {
    total += await counter.peek();
  };
  total
};
```

A `composite query` can call `query` and `composite query` callees but not updates or other `shared` functions; awaiting an update there is `M0187` ("send capability required ... only calls to `query` and `composite query` functions are allowed"). If the body must `await` an update, no flavor of query works — make it an update func.

A composite query can only be initiated as an ingress call, e.g. from a frontend — calling one from an update or oneway func is `M0186`, from a plain `query func` `M0188`. Within the call tree it composes: it may call other canisters' `query`/`composite query` functions.

## Shared Types

Public functions accept/return only **shared types** (serializable):

- Shared: `Nat`, `Int`, `Text`, `Bool`, `Principal`, `Blob`, `Float`, `[T]`, `?T`, records, variants
- **Not shared**: Functions, `var` fields, objects, `Map`, `Set`, `List`, `Queue`, `Stack`

If internal state uses mutable containers, define a separate immutable public type for the API boundary:

```motoko
public type PostInternal = { id : Nat; likedBy : Set.Set<Principal> }; // internal
public type Post = { id : Nat; likedBy : [Principal] }; // shared

public func toPublic(self : Types.PostInternal) : Types.Post {
  { self with likedBy = self.likedBy.toArray() };
};

```

## Collections

For full API signatures, read [api-reference.md](api-reference.md).

```motoko
import Map "mo:core/Map";
import List "mo:core/List";
import Queue "mo:core/Queue";
import Stack "mo:core/Stack";
import Array "mo:core/Array";
import Set "mo:core/Set";

```

**Map** (B-tree, O(log n)): `Map.empty<K, V>()`, `.add(k, v)`, `.get(k) → ?V`, `.remove(k)`, `.entries()`
**List** (growable array, O(1) access): `List.empty<T>()`, `.add(item)`, `.get(i) → ?T`, `.at(i) → T` (traps on OOB)
**Queue** (FIFO): `Queue.empty<T>()`, `.pushBack(item)`, `.popFront() → ?T`
**Stack** (LIFO): `Stack.empty<T>()`, `.push(item)`, `.pop() → ?T`
**Array**: `[var 0, 0, 0]` (mutable), `[1, 2, 3]` (immutable)
**Set** (B-tree, O(log n)): `Set.empty<T>()`, `.add(item)`, `.contains(item)`, `.remove(item)`

**Warning**: Never call `list.add()` inside a `retain` callback. Use `mapInPlace` to update items in place.

```motoko
todos.mapInPlace(
  func(todo) {
    if (todo.id == targetId) { { todo with completed = not todo.completed } } else {
      todo;
    };
  }
);

```

**Important**: Always use opaque type aliases (`List.List<T>`, `Map.Map<K, V>`, `Set.Set<T>`) in type declarations. Never use raw internal structure or `.filter`, `.map()` won't resolve (M0072).

When a domain helper receives a core collection, type the parameter as the concrete opaque collection type (e.g. `todos : List.List<Types.Todo>`) and import that module in the helper file. Do not use structural method-record parameters such as `{ add : (Types.Todo) -> (); toArray : () -> [Types.Todo] }` for core collection values. A compiler error saying `List.List<T>` cannot produce an expected type with fields like `add`, `toArray`, or `clear` means the helper signature is wrong; fix the signature to `List.List<T>` and keep the collection — do not switch to an invented module such as `mo:core/Buffer`, and do not regress to module-function calls like `List.toArray(todos)` or `List.add(todos, todo)`.

### Arrays vs Core Collections

Core collections (`List.List<T>`, `Map.Map<K, V>`, `Set.Set<T>`, `Queue.Queue<T>`, `Stack.Stack<T>`) have receiver helpers because their modules define self-parameter APIs. A value of type `[T]` or `[var T]` is an array snapshot, not a `List.List<T>`.

- After `let snapshot = list.toArray()`, only use array operations whose exact signatures are shown here or verified in the API reference — with receiver dot notation: `snapshot.filter(pred)`, `snapshot.map(mapper)`, `snapshot.sort(comparator)`, `snapshot.concat([item])`. Do not call those as module functions such as `Array.filter<T>(snapshot, pred)` or `Array.append(snapshot, [item])`.
- If a value is an array (`[T]`) or came from `.toArray()` / `.filter(...)`, then `.map(...)` already returns an array; do not append `.toArray()` to that array-map result. (`List.List<T>.map(...)` returns a `List`, so it still needs `.toArray()` when the caller expects an array.)
- Arrays DO support predicate search: `.find(predicate) : ?T`, `.findIndex(predicate) : ?Nat`, `.any(predicate)`, and `.all(predicate)` are all in `mo:core/Array` (see the API reference). The JS spellings `.some(...)` / `.every(...)` do not exist — use `.any` / `.all`.
- Arrays DO have `.contains(element)` (`equal` is implicit, so pass only the element). Reach for `.indexOf(element)` when you need the position — it returns `?Nat`, so keep the option and use it; and for `.any(pred)` when membership is decided by a predicate rather than equality:

```motoko
// Overlap between two tag arrays
let matched = leftTags.any(func left = rightTags.any(func right = left == right));
```

- Do not copy a collection just to search it: prefer `templates.find(func ...)` on the original `List.List<T>` over `templates.toArray().find(func ...)` — the intermediate array is a wasted copy.
- Use `.values()` when iterating array snapshots. Do not write `.vals()` in new Motoko code.

**CRUD List patterns:** Do not invent helpers on `List`. There is no `filterInPlace`, and record spread fails on records with `var` fields.

**An inline `func` passed as a call argument takes no type annotations.** The call already fixes the parameter and result types, so annotating repeats them and lets them drift as the code changes. Use the expression form `func x = <expr>`:

```motoko
todos.find(func todo = todo.id == targetId);            // CORRECT
todos.find(func(todo : Types.Todo) : Bool { todo.id == targetId }); // WRONG: annotated
```

This is about **argument position only**. A named declaration still carries its full signature, and a lambda bound on its own has nothing to infer from — `let f = func x = x > 1` fails with M0103 (`cannot infer type of variable`).

```motoko
public func toView(t : Types.Todo) : Types.TodoView { ... }; // annotated, as always
```

When the types are not obvious to a reader, or a generic cannot be inferred, say it **on the call** rather than on the lambda — it reads better and keeps one source of truth:

```motoko
photos.map(func p = { id = p.id; url = p.url.toText() }); // inferred — preferred
photos.map<PhotoInternal, Photo>(func p = { ... });       // when M0098 demands it
```

Add `<In, Out>` only when the compiler actually reports M0098; adding it when inference already succeeded is M0223 (redundant type instantiation).

The one exception is a callback that must return `async`. There `: async ()` is load-bearing — it is what makes the body async, and there is no unannotated form (`func() = async { ... }` does not work either). Without it the lambda infers `() -> ()` and the call fails with M0096:

```motoko
Timer.recurringTimer<system>(#seconds(3600), func() : async () { cleanup() });
```

```motoko
// Toggle a mutable field by finding the record and mutating the var field.
switch (todos.find(func todo = todo.id == targetId)) {
  case (?todo) {
    todo.completed := not todo.completed;
    ?toView(todo);
  };
  case null { null };
};

// Delete from List by rebuilding from an array snapshot.
var removed = false;
let snapshot = todos.toArray();
todos.clear();
for (todo in snapshot.values()) {
  if (todo.id == targetId) {
    removed := true;
  } else {
    todos.add(todo);
  };
};
removed;

// To change an immutable field on a record that also has var fields, rebuild it.
let updated : Types.Todo = {
  id = todo.id;
  text = newText;
  var completed = todo.completed;
  createdAt = todo.createdAt;
};
let snapshot = todos.toArray();
todos.clear();
for (todo in snapshot.values()) {
  if (todo.id == targetId) {
    todos.add(updated);
  } else {
    todos.add(todo);
  };
};
```

For delete-style operations that return whether a record was removed, prefer a `var removed = false` flag while rebuilding from the array snapshot. Do not call `todos.size()` unless the parameter type explicitly exposes `size()`, such as `List.List<T>`.

### Iteration and Chaining

```motoko
let doubled = numbers.map(func x = x * 2).filter(func x = x > 10);
let sum = scores.filter(func s = s > 15).foldLeft(0, func(acc, s) = acc + s);
switch (numbers.find(func n = n > 5)) {
  case (?found) { /* use */ };
  case null {};
};

```

### Sorting Arrays

`Array`/array receiver helpers such as `.sort(...)` return a value. Do not use them as standalone sequenced statements; Motoko rejects sequencing a non-`()` expression.

```motoko
let all = todos.toArray();
let sorted = all.sort(func (a, b) =
  if (a.createdAt > b.createdAt) { #less }
  else if (a.createdAt < b.createdAt) { #greater }
  else { #equal }
);
sorted.map(func todo = {
  id = todo.id; text = todo.text; completed = todo.completed; createdAt = todo.createdAt
});

// WRONG: `.sort(...)` returns an array, so this is not a valid statement.
all.sort(func (a, b) = Int.compare(b.createdAt, a.createdAt));
all.map(func todo = { ... });
```

### `contains` vs `find`

- **`contains(element)`** -- equality check on `List`/`Set`/etc. Does NOT take a predicate.
- **`find(predicate)`** -- predicate search on `List.List<T>` and `[T]`. Returns `?T`.
- Both `List.List<T>` and `[T]` have `contains`. Use `.any(func x = ...)` when the test is a predicate, not equality.

```motoko
numbers.contains(3); // equal inferred from the imported Nat
friends.contains(p); // likewise from Principal — passing Principal.equal here is M0237
todos.find(func todo = todo.id == targetId); // returns ?Todo
// WRONG: friends.contains(func(f) { f == p })  → M0096/M0103

```

### Text Search and Case Folding

Motoko `Text` uses contextual receiver methods for case folding and substring checks. Do not use JavaScript spellings such as `.toLowerCase()` or `.toLowercase()`, and do not call `Text.contains(...)` for ordinary substring search.

```motoko
let term = searchTerm.toLower();
textValue.toLower().contains(#text term)
```

### Joining Text

`join` takes the **iterator as its receiver and the separator as its argument** — easy to invert. Use dot notation; the module form is an M0236 violation that `mops check --fix` rewrites for you.

```motoko
["a", "b"].values().join(", ");     // CORRECT → "a, b"
Text.join(["a", "b"].values(), ", "); // WRONG (M0236)
```

Note the receiver is an **iterator**, not an array: call `.values()` on an array first.

### Variant Tag Arguments

Always parenthesize a variant tag's argument. A tag binds only to the atom immediately after it, tighter than any operator, so an unparenthesized argument silently loses everything past the first term:

```motoko
#tag(n + 1) // CORRECT
#tag n + 1  // WRONG: parses as (#tag n) + 1 → M0060, operator is not defined for operand types
```

### Explicit Type Instantiation

Let inference work first. With unannotated lambdas the compiler resolves `.map()` to a different type on its own, so write the plain call:

```motoko
let photos = internalPhotos.map(
  func p = { id = p.id; url = p.url; uploadedBy = p.uploadedBy.toText() }
);
```

Add explicit type parameters **only** when the compiler reports M0098 (`no best choice for type parameter`):

```motoko
let photos = internalPhotos.map<PhotoInternal, Photo>(func p = { ... });
```

Adding them when inference already succeeded is a warning of its own — M0223, redundant type instantiation — which `mops check --fix` strips. Annotating the lambda instead of instantiating the call is always wrong.

### Function Literals as Arguments

Do NOT put a semicolon after a function body passed as an argument:

```motoko
list.filter(func(item) { item.id != targetId }) // CORRECT
list.filter(func(item) { item.id != targetId; }) // WRONG: trailing semicolon makes the block return `()`

```

Do not inline imperative statement blocks as boolean operands:

```motoko
// WRONG: parser can treat the block after `or` as an invalid expression shape.
let matches = titleMatches or {
  var found = false;
  for (tag in tags.values()) {
    if (tag == q) { found := true };
  };
  found
};

// CORRECT: compute the loop result before the final boolean expression.
var tagMatches = false;
for (tag in tags.values()) {
  if (tag == q) { tagMatches := true };
};
let matches = titleMatches or tagMatches;
```

Every `switch` case must be separated with a semicolon before the next `case`, even in compact one-line switches:

```motoko
switch (pricing) { case (#free) { true }; case (#paid(_)) { false }; } // CORRECT
switch (pricing) { case (#free) { true } case (#paid(_)) { false } } // WRONG
```

### Declaration Terminators

Top-level and nested function declarations inside `module`, `actor`, and `mixin` blocks must end with `;`. A missing `};` after a function commonly surfaces as a syntax error near the next declaration, e.g. `unexpected token 'public'`.

### Local Mutability

Use `let` for local bindings unless the variable is reassigned with `:=`. Never use `var` for a local binding only because the value it references is mutable. Mutating an object through methods such as adding to a collection does not require the binding itself to be `var`; use `let` for collection builders and other accumulator objects unless the binding is later reassigned.

### Safe Nat Arithmetic

Avoid `Nat` subtraction unless the compiler can prove the result is non-negative at the operation itself. `a - b` traps when `b > a`, and the compiler can still warn when safety depends on a previous branch. Prefer bounds checks, bounded addition, loop counters, or helper branches that do not subtract one `Nat` from another.

## Option Handling

**Prefer `??` for unwrap-or-default and unwrap-or-trap.** Do not write a nested `switch` solely to peel `?T`.

```motoko
// Unwrap with trap when null means something is wrong
let user = users.find(func u = u.id == caller)
  ?? Runtime.trap("User not found");

// Default when absence is fine
let caption = optLabel ?? "(untitled)"; // not `label` — reserved word

// Only return ?T when absence is a normal, expected outcome
public query func findUserByName(name : Text) : async ?User {
  users.find(func u = u.name == name);
};

// Keep switch when the Some arm maps / mutates / has side effects
switch (todos.find(func todo = todo.id == targetId)) {
  case (?todo) {
    todo.completed := not todo.completed;
    ?toView(todo);
  };
  case null { null };
};
```

## Error Handling: `Result`

Use `mo:core/Result` to return a failure a caller can act on. `Result<Ok, Err>` is `{ #ok : Ok; #err : Err }`, so it crosses the API boundary as Candid whenever `Ok` and `Err` are themselves shared, which for `Ok` usually means the view type, not the internal record.

**Pick the return type by what the failure means:**

| The call can fail because…                          | Return                 |
| --------------------------------------------------- | ---------------------- |
| the caller did something the caller can fix         | `Result<Ok, Err>`      |
| the thing simply is not there, and that is normal   | `?T`                   |
| an invariant this code is responsible for is broken | trap (`Runtime.trap`)  |

```motoko
import Result "mo:core/Result";

public type BookingError = {
  #slotTaken : { until : Time.Time };
  #notAuthorized;
  #unknownRoom : Nat;
};

public shared ({ caller }) func book(roomId : Nat, at : Time.Time) : async Result.Result<Booking, BookingError> {
  // ...
};
```

**Never launder an error into `Text`.** `Result<Booking, Text>` forces every caller — including the frontend — to string-match to tell "slot taken" from "not authorized". Make `Err` a variant; put the data each failure needs inside its own tag. A `Text` payload is fine *inside* a tag when it is a message for a human, not a discriminator.

**Do not trap on caller error.** A trap rolls back the whole message and reaches the frontend as an opaque reject — the caller cannot branch on it and the user gets no actionable message. Reserve traps for "this cannot happen" (see `?? Runtime.trap(...)` above).

**Chain, do not nest.** `mapOk`, `mapErr`, and `chain` take `self`, so they are dot notation like every other self-parameter API and a pipeline stays flat. `Result.fromOption` has no `self` — it is the module-call bridge from `?T` at the edge where absence becomes a caller-visible error.

```motoko project=result-chain filepath=src/backend/main.mo
import Result "mo:core/Result";
import Map "mo:core/Map";
import Nat "mo:core/Nat";

actor {
  type Room = { id : Nat; name : Text };
  type RoomView = { name : Text };
  type BookingError = { #unknownRoom : Nat; #notAuthorized };

  let rooms : Map.Map<Nat, Room>;

  func toView(room : Room) : RoomView = { name = room.name };
  func reserve(room : Room) : Result.Result<Room, BookingError> = #ok(room);

  public shared ({ caller }) func book(roomId : Nat) : async Result.Result<RoomView, BookingError> {
    Result.fromOption(rooms.get(roomId), #unknownRoom(roomId))
      .chain(func room = reserve(room))
      .mapOk(toView);
  };
};
```

Use `switch` on `#ok` / `#err` when the arms do different work; do not write `isOk`/`isErr` followed by an unwrap — that discards the payload the type was carrying.

## Common Patterns

### Module with Self Pattern

```motoko
// lib/User.mo
module {
  public type User = Types.User;
  public func new(id : Principal, name : Text) : User {
    { id; var name; var isActive = true };
  };
  public func ban(self : User) { self.isActive := false };
};
// Usage: user.ban(); -- dot notation!

```

### Record Spread with `with`

**RULE:** Use record spread for immutable records. Never use record spread on a record type that contains `var` fields; Motoko rejects that with `base has non-aliasable var field`.

```motoko
{ self with newField = "" }; // CORRECT for immutable records

// CORRECT for a record type containing var fields:
let updated : Types.Todo = {
  id = todo.id;
  text = newText;
  var completed = todo.completed;
  createdAt = todo.createdAt;
};

{ todo with text = newText }; // WRONG if Todo contains any var field

```

### State Definition

Entity types live in `types.mo`. State fields as direct actor bindings — no `AppState` wrapper.

Stable actor fields are declared with **types only — no initializers** (initial values come from the migration chain). Transient fields use initializers as usual.

```motoko
// types.mo
module {
  public type User = {
    id : Principal;
    var username : Text;
    var isActive : Bool;
  };
};
```

```motoko
// main.mo
actor {
  let users : List.List<Types.User>;
  let state : { var nextPostId : Nat };
  include AuthMixin(users);
};

```

### Mutable State for Mixins

Never declare `var` actor-fields (e.g. `var nextPostId : Nat`) you intend to share with mixins — `var` parameters are passed by value, so the mixin's mutations don't propagate back. Wrap mutables in a record and pass the record; records are shared by reference. In the actor, declare the record type-only (`let state : { var nextPostId : Nat };`) — its initial value (e.g. `{ var nextPostId = 0 }`) comes from the migration chain, like every stable field.

Preserve the exact field names on shared mutable state records across actor, mixin, and helper modules. If the actor declares `let state : { var nextId : Nat }` and the mixin receives `state`, helper parameters must accept `{ var nextId : Nat }` and update `state.nextId`. Do not rename the field to `val` or `counter` in helper signatures, and do not create wrapper copies like `{ var val = state.nextId }`; the copy mutates only itself and leaves actor state unchanged.

### Transient State & Static/Module Fields

Enhanced orthogonal persistence makes every top-level `let`/`var` in an actor or mixin **stable** (persisted across upgrades) by default — there is no `stable` keyword. Prefix a binding with `transient` to keep it OUT of stable storage; it is re-initialized on every (re)start instead of being persisted. Use it for anything that isn't durable state — caches, capability handles, and constants.

**Constants** — Motoko has no `const`, and a bare `let X = ...` in an actor or mixin is stable state. Put a fixed value in a **module** when its right-hand side is a **static** expression (namespaced, reusable, never state); otherwise keep it as `transient let` in the actor/mixin:

```motoko
transient let admin = Principal.fromText("..."); // non-static (a call) — can't be a module `let`
transient let cache = Map.empty<Text, User>();   // derived; rebuilt after each upgrade
```

**Static** (what a module `let` field allows) = literals, variant tags (`#x`), options (`?x`), tuples, immutable arrays and records, function values, and imported/variable names — plus `.field` projection over those. **Non-static** = function calls, operators (`+`, `==`, `#`), control flow (`if`/`switch`/loops), and array indexing (`a[i]`).

## Numeric Conversion Hygiene

Treat deprecation warnings as failures. **Every conversion is spelled `to`, on the source value** — never a `Module.fromX` call, and never a chain through the sized numeric modules. A conversion is one receiver call:

```motoko
import Nat "mo:core/Nat";

let average = sum.toFloat() / count.toFloat(); // Nat.toFloat
```

| Instead of                | write             |
| ------------------------- | ----------------- |
| `Float.fromInt(i)`        | `i.toFloat()`     |
| `Float.fromInt64(i)`      | `i.toFloat()`     |
| `Nat.fromNat64(n)`        | `n.toNat()`       |
| `Int.fromNat(n)`          | `n.toInt()`       |
| `Nat64.fromNat(n)`        | `n.toNat64()`     |
| `Blob.fromArray(bytes)`   | `bytes.toBlob()`  |
| `Iter.fromArray(a)`       | `a.values()`      |

A conversion that needs several hops is a sign the wrong function was picked: verify the exact `mo:core` signature in [api-reference.md](api-reference.md), which lists only non-deprecated APIs.

## Security and Authorization

Every public update function MUST verify the caller via `{caller}` destructuring. Enforce authorization on the backend — never trust client-side checks.

Attaching cycles to an inter-canister call (`await (with cycles = ...) <call>`) hands them to the callee, so treat any endpoint that can trigger one as spend authority: gate it on the caller, bound the amount, and never let an unauthenticated path reach it. Some platforms forbid outbound cycles entirely — follow the hosting platform's own guidance where it applies.

## Common Compile Error Patterns

| Error pattern                                          | Cause                        | Fix                                         |
| ------------------------------------------------------ | ---------------------------- | ------------------------------------------- |
| `field append does not exist`                          | Array.append removed         | receiver `.concat(...)`                     |
| `field put does not exist`                             | Map.put renamed              | `.add()`                                    |
| `field delete is deprecated`                           | Map.delete renamed           | `.remove()`                                 |
| `field toLowerCase does not exist`                     | JS Text API spelling         | `.toLower()`                                |
| `field toLowercase does not exist`                     | JS Text API spelling         | `.toLower()`                                |
| `You can use the dot notation ... contains`            | Wrong Text contains shape    | `text.toLower().contains(#text term)`       |
| `operator may trap for inferred type Nat`              | Potentially unsafe Nat math  | Avoid `Nat` subtraction; use bounds/loops   |
| `Int cannot produce expected type Nat`                 | Int/Nat mismatch             | `.toNat()`                                  |
| `field fromX is deprecated`                            | Deprecated `fromX` conversion | The `toX` counterpart on the source value: `n.toFloat()`, `bytes.toBlob()` |
| `syntax error, unexpected token '.'`                   | Missing parens               | `#text (searchTerm.toLower())`              |
| `syntax error, unexpected token ','`                   | Missing parens in for        | `for ((key, value) in map.entries())`       |
| `Compatibility error [M0170]`                          | Missing migration            | Load `migrating-motoko-actors`            |
| `M0250` initialized stable field                       | Initializer on a stable actor field | Declare it type-only; move the value into the migration's `NewActor` |
| `M0254` / `M0267` initial actor requires field         | Stable field no migration supplies | Add it to the pending migration's `NewActor` |
| `M0255` stable signature downgrade                     | Chain or migrations config removed | Restore it — enhanced migration is one-way; load `troubleshooting-motoko-migrations` |
| `shared function has non-shared parameter/return type` | Mutable type in API          | Return `[T]` not `List<T>`, no `var` fields |
| `send capability required`                             | Async in non-async (`async*`/local non-shared target) | Add `<system>` capability                   |
| M0038 misplaced await + M0188 send capability (paired) | `await <call>` inside a plain `query func` | Make it a `composite query func` (queries) or a plain update func (updates) |
| `M0187` send capability in a composite query           | calling/awaiting an update from a `composite query func` | Make it a plain update func                |
| `M0186` composite send capability required             | calling a `composite query func` from a non-composite func | Only ingress calls initiate composite queries; call it from the frontend, or make the callee a plain `query` |
| `unexpected token '<name>'` at an identifier declaration | Reserved word used as an identifier | Rename it consistently across its contract and callers; see [references/reserved-keywords.md](references/reserved-keywords.md) |
| `unexpected token 'public'` after a function           | Missing declaration `;`      | End function declarations with `};`         |
| `M0219` implicitly transient                           | Actor not persistent         | Write `persistent actor`; see [references/project-setup.md](references/project-setup.md) |
| `M0220` actor should be declared `persistent`          | Actor not persistent         | Write `persistent actor`; see [references/project-setup.md](references/project-setup.md) |
| `M0218` redundant `stable` keyword                     | `stable` under EOP           | Remove `stable` — a plain `let`/`var` is already stable |
| `M0064` misplaced `'!'`                                | `!` outside an option block  | Wrap in `do ? { ... }`                      |
| `M0145` `does not cover value`                         | Non-exhaustive switch        | Add the missing cases or a `case _`         |
| `M0060` operator not defined for `{#tag : T}`          | Unparenthesized variant tag  | `#tag(x)`, never `#tag x`                   |
| `M0060` operator not defined, on `==`                  | `==` on a record with a `var` field (not shared) | Use an `equal` function instead |
| `M0230` cannot determine implicit argument `compare`   | Key type's module not in scope | Usually a missing import: `import` the key type's module (`Nat`, `Text`, …) in that file. For a record/variant key, add `compare` to the type's own module |
| `M0070` expected object type, produces `Nat`           | Receiver `.equal`/`.compare` on a number | Use `==` or `Nat.equal(a, b)`   |
| `M0096` actor cannot produce expected type `()`        | Declaration after the actor  | The actor must be the last declaration in the file |
| `field compare does not exist` on Time                 | No Time.compare              | Use `Int.compare`                           |
| `unexpected token ';'` in function call                | Semicolon after func literal | Remove `;` before `)`                       |
| `unbound variable X`                                   | Missing import               | `import X "mo:core/X"`                      |
| `M0098` no best choice for type param                  | Generic needs explicit types | `list.map<In, Out>(...)`                    |
| `M0096` on `contains` callback                         | Predicate passed to contains | `contains` takes an element; for a predicate use `.any(pred)` for a Bool, `.find(pred)` for the element |
| `M0009` import file does not exist                     | Wrong path                   | Relative, no `.mo` extension                |
| `M0244 variable ... is never reassigned`               | Unneeded `var` binding       | Use `let` unless reassigned with `:=`       |

## Quick Reference

**Basic Types:** `Nat` `Int` `Text` `Bool` `Principal` `?T` `[T]` `[var T]` `Blob` `Float` — `Time.now()` returns `Int` (nanoseconds)

**Common Operations:** `debug_show(value)` → Text | `assert condition` | `# "text"` concatenation | `break` / `continue` inside `for`, `while`, `loop`

| Structure | Use Case         | Key Operations     | Complexity  |
| --------- | ---------------- | ------------------ | ----------- |
| Map       | Key-value pairs  | get, add, remove   | O(log n)    |
| List      | Growable array   | add, get, at       | O(1) access |
| Queue     | FIFO processing  | pushBack, popFront | O(1)        |
| Stack     | LIFO processing  | push, pop          | O(1)        |
| Array     | Fixed collection | index, map, filter | O(1) access |
| Set       | Unique values    | contains, add      | O(log n)    |

## Best Practices

1. Always `mo:core`, never `mo:base`
2. No `stable` keyword — enhanced orthogonal persistence handles state
3. Dot notation for all `self`-parameter functions
4. Unwrap with `??` (`opt ?? Runtime.trap(...)` or `opt ?? default`); reserve `switch` for transforms/side effects/variants; `?T` only when absence is expected
5. types.mo / lib/ / mixins/ / main.mo structure
6. Mixins receive only needed state slices
7. Queries for read-only, updates for state changes
8. Iterator chaining to avoid intermediate collections
9. Record spread `{ self with ... }` for immutable records; mutate or rebuild records that contain `var` fields
10. No inline initializers on stable actor fields — initial values come from the migration chain
11. Inline `func` arguments carry no type annotations (except `: async ()` on async callbacks); instantiate the call instead, and only when the compiler reports M0098

## Additional Resources

- **Control flow**: [references/control-flow.md](references/control-flow.md) — `??`, `do ? { ... }` option chaining, switch statements, loops, `break` / `continue`
- **Reserved keywords**: [references/reserved-keywords.md](references/reserved-keywords.md) — full list to check identifiers against
- **Equality & comparison**: [references/equality.md](references/equality.md) — which types support receiver `.equal`, and when `==` differs from `equal`
- **Type conversions**: [references/type-conversions.md](references/type-conversions.md) — Nat/Int size conversions
- **Project setup**: [references/project-setup.md](references/project-setup.md) — one-time `[moc] args` flags. Skip this if your platform manages `mops.toml`
- **Design review**: Load `reviewing-motoko` when reviewing, auditing, or refactoring existing `.mo` files — type-encoded invariants, state/persistence discipline, and file structure
- **Actor migrations**: Load `migrating-motoko-actors` when upgrading canisters or changing actor state shape
- **Migration failures**: Load `troubleshooting-motoko-migrations` for unexplained compatibility diagnostics, frozen migration files, or converted legacy projects
- **API signatures**: [api-reference.md](api-reference.md) — complete function signatures
- **Complete examples**: [examples.md](examples.md) — full working code samples
