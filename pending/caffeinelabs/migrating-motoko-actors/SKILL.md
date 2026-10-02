---
name: migrating-motoko-actors
description: >-
  Motoko actor migration and schema evolution with the enhanced migration
  chain (migrations/). Load when upgrading canisters or changing actor
  state shape.
version: 0.2.6
compatibility:
  toolchain:
    moc: ">=1.11.2"
  mops:
    core: ">=2.5.0"
caffeineai-subscription: [none]
---

# Motoko Actor Migrations

Expert guidance for migrating actor state across canister upgrades with orthogonal persistence.

## Critical: Never use classical persistence or pre/post upgrade

Do not use classical (legacy) persistence or `system func preupgrade` / `system func postupgrade`. They are error-prone, can leave canisters stuck if they trap, and do not scale.

Also do not use the legacy `(with migration = ...)` actor-attached syntax. This skill covers **mops-managed migrations**. When a change requires an explicit migration, write it as a timestamped file in `src/backend/migrations/`; the chain replays automatically.

## How stable state is initialized

Stable actor fields have no initializers in the actor body. The chain in `src/backend/migrations/` is what gives them values: the runtime walks it in lexicographic order, running every file on a fresh install and only the files not yet applied to the canister on an upgrade.

## When to Use This Skill

- Planning or implementing a canister upgrade that changes actor state
- Deciding between implicit vs explicit migration
- Writing or refactoring a migration function
- Introducing stable state for the first time (a migration with `OldActor = {}`, or fold it into the first one if that is still pending)

## Migration Folder Rules

- **All migrations live in `src/backend/migrations/`.** The full chain replays in lexicographic filename order on fresh install; on upgrade, only entries newer than the deployed tail run. (The directory is declared as `chain = ...` under `[canisters.<name>.migrations]` in `mops.toml`; an imported project using a non-default canister name may place it elsewhere — read `mops.toml` rather than assuming.)
- **At most one pending migration per build** (`check-limit = 1` in `mops.toml`). If a migration is already pending (not yet applied), **edit that file** to fold in further changes instead of adding another. `mops check` compares the deployed `.most` baseline and names the latest pending file to fold into when the limit is exceeded. Where a hosting platform owns the migrations section and `check-limit`, never edit them to clear an error.
- **Name new files with just the UTC timestamp**, no suffix: `YYYYMMDD_HHMMSS.mo`. The timestamp must sort after every existing file. Do NOT encode the change in the name (no `AddPriority`, `AddTags`, `Init`, …) — any feature-ish name tempts you to add another file for the next change instead of editing the one pending file.
- **Never modify, delete, or rename a migration that was already applied.** Applied migrations are tracked by module name, so a rename makes the runtime treat the file as never applied, and an edit to an already-applied file never executes. Some platforms enforce this by making applied migrations read-only, in which case writes to them simply fail. A migration that was not applied yet is pending: **edit** it rather than add a second migration for the same change.
- **Migrations must be self-contained.** Inline BOTH old types AND new types in the migration file. Only `mo:core/...` and mops package imports are allowed — never `../types` or any project module. The chain replays forever; a frozen migration that imported `Types.Note` becomes wrong the moment `Note` changes in an incompatible way. Component-owned opaque state is the reason package imports are allowed: `AccessControl.initState()` from `mo:caffeineai-authorization/access-control` can only be constructed by importing the package.
- `mops check --fix` automatically verifies upgrade compatibility.

## Two Kinds of Migration

### 1. Implicit migration (no code)

The runtime allows the upgrade if the new program is compatible with the old. No migration function needed.

> **Do NOT add a migration file for changes in the implicit list below.** Every migration file replays forever on fresh install; adding a no-op file bloats the chain, slows fresh installs, and creates a frozen artifact you can never delete. A long enough chain becomes undeployable in a way no retry recovers, and `mops check` will not warn you. **Fewer migrations are always better.**
>
> **Identity body = no migration.** If your `(old : OldActor) : NewActor` body would just be `old` (or rebuild the same record field-by-field with no transformation), the change is stable-compatible — delete the file.

**Allowed without explicit migration (typical compatible changes):**

- Changing mutability of a field (`var` to `let` or vice versa)
- Adding variant constructors
- Changing `Nat` to `Int` (and other safe supertypes)
- Other changes that satisfy Motoko stable subtyping

**Require explicit migration:**

- Removing any actor field the previous version exposes — consume it in `OldActor`, omit from `NewActor`
- Promoting to `Any` or other lossy supertypes
- Renaming fields (map old to new in migration)
- Non-trivial transformations (e.g. `Int` to `Float`, restructuring records)
- Adding new stable fields (initial values must come from the migration; no inline initializers allowed)
- Introducing stable state for the first time (the migration supplies the initial values; the actor declares stable fields with types only, no inline initializers)

### 2. Explicit migration (migration function)

Use when the new state shape or types are not a simple compatible extension of the old.

Extend the pending migration if there is one; otherwise add a new timestamped file to `src/backend/migrations/`. The chain replays automatically.

**Rules:**

- Migration function type: `(old : OldActor) : NewActor`. Both record types must be stable (no shared/local functions; use primitive types, records, variants, Option, Map, List, etc.).
- **Domain** `OldActor`: record of old stable fields (names and types as in the previous version). If the retired actor is missing a field the domain expects, the upgrade traps and is aborted.
- **Codomain** `NewActor`: record of new stable fields; each field must exist in the new actor with the same name and a supertype of the codomain type. Use `var x = ...` or `x = ...` in the output to match the actor's `var` vs `let`.
- On fresh install, the entire chain replays in order starting from an empty actor (`OldActor = {}` for the first migration); on upgrade, only entries newer than the deployed tail run. Exception: in a project converted from legacy persistence the first file's `OldActor` is the pre-conversion stable shape, not `{}` — leave it alone (see `troubleshooting-motoko-migrations`).
- Each `NewActor` field's value comes from the migration body. The actor body has no initializers in enhanced mode.
- List every stable field in both `OldActor` and `NewActor` (including unchanged ones) is the canonical form for clarity. A partial `OldActor`/`NewActor` that lists only the fields being changed (subset form) is also supported: unchanged fields carry through automatically. Either way, a field in `OldActor` but not in `NewActor` is an explicit discard (possible data loss).
- If the migration function traps, the upgrade is aborted and the canister remains on the old version. Keep the migration pure and free of operations that can trap unexpectedly.

Multi-step upgrades (e.g. v1 to v2 to v3): Each upgrade step has one migration from the previously deployed version. The next version can use a new migration (or none if the change is stable-compatible).

## Authoring a migration

Pick a bare UTC-timestamp filename (`YYYYMMDD_HHMMSS.mo`, no suffix) that sorts after every existing entry, then write the module:

```motoko
module {
  type OldActor = { /* old stable fields, inlined */ };
  type NewActor = { /* new stable fields */ };

  public func migration(old : OldActor) : NewActor {
    { /* produce new fields from old */ };
  };
};

```

- Must be a `module` exporting `public func migration(old : OldActor) : NewActor` (the function name is required — the chain runner discovers it by name).
- Both `OldActor` and `NewActor` must be inlined in the file — no project imports.

## Actor body: types only, no initializers

Stable vars are declared with types, no initial values. Transient let/var fields use initializers as usual.

> This no-initializer rule applies to enhanced-migration projects (this skill's subject), where the migration chain owns initial values. In a plain project without the enhanced-migration chain, stable fields are initialized with inline values in the actor body as usual (e.g. `persistent actor { let m = Map.empty<Nat, Text>(); }`).

```motoko
actor {
  let tasks : Map.Map<Text, Task>;
  var nextId : Nat;

  transient var cache = List.empty<Text>();
};

```

Initial values come from the migration chain. When you introduce stable state for the first time, write a migration whose `OldActor = {}` and `NewActor` enumerates **every** stable field declared in `main.mo`. The migration body must produce a value for each. Missing fields surface as compatibility warnings and break subsequent upgrades.

> If an example anywhere shows inline initializers like `let accessControlState = AccessControl.initState();` or `let users = Map.empty<Principal, User>();` directly in the actor body, it predates enhanced migration. Under enhanced migration that is a compile error (M0014, M0250). Treat such examples as state-shape hints only: copy the field name and type into your actor (without initializer), and **move the initializer expression into the migration function's `NewActor` output**.

## Stable-Compatible (definition)

**Old** signature is **stable-compatible** with **new** if, for every stable field `id : T` in the old signature:

- The new signature has a stable field `id : U` such that T is a stable subtype of U (the old value can be used as the new field's initial value without loss of data).
- The new signature may include additional fields not present in the old one (each supplied by a migration).
- Matching fields may differ in mutability (`var` vs non-`var`).

So: you can widen types (e.g. `Nat` to `Int`) and change mutability without an explicit migration. You cannot remove fields, rename them, or narrow types. **Adding a stable field always requires a migration**: inline initializers are not allowed, so the new field's initial value must come from a migration file's `NewActor`.

## Patterns

### Add record field with default

Use `record with newField = value` to add a field to every element:

```motoko
// Add required field zipCode to each taxpayer
old.taxPayers.map<Nat, OldTaxPayer, NewTaxPayer>(
  func(_id, oldTaxPayer) { { oldTaxPayer with zipCode = "" } }
);

```

For a new optional field, set it to `null`:

```motoko
{ task with var status = task.status; var assignee = null : ?Principal }

```

### Add or extend variant type

Adding a variant tag -- cast the old value to the new variant type:

```motoko
var status = bounty.status : NewTaskStatus // OldTaskStatus had #open;#claimed;#completed; New adds #expired

```

Replacing a Bool with a variant:

```motoko
var status = if (task.completed) { #completed } else { #pending };

```

### Map over a collection

Transform each value in a `Map` with `map<K, OldV, NewV>(func(key, oldVal) { ... })`:

```motoko
let todos = old.todos.map<TaskID, OldTask, NewTask>(
  func(_, task) {
    {
      task with
      due = 0;
      var status = if (task.completed) { #completed } else { #pending };
    };
  }
);
{ var todos; var nextTaskId = old.nextTaskId };

```

### Add new top-level stable field (computed from old state)

Include the new field in the migration output and compute it from old fields:

```motoko
let times = List.repeat<Time.Time>(0, old.messages.size());
{ var messages = old.messages; var times };

```

### Restructure: change shape of state

When the new state has a different structure, provide a transformation function from the old field type to the new one and implement it according to the application's migration logic. Build the new value in the migration from the old state and return a record that matches NewActor.

### Change type of a field

**Rename/conceptual change** -- e.g. `artist : Text` to `artists : Set.Set<Text>`:

```motoko
{ oldPainting with artists = Set.singleton<Text>(oldPainting.artist) }

```

### Rename or change type of a single field

Input record uses old name/type, output record uses new name/type:

```motoko project=rename-field filepath=src/backend/migrations/20260101_000000.mo
// src/backend/migrations/YYYYMMDD_HHMMSS.mo
import Int "mo:core/Int";

module {
  type OldActor = { var state : Int };
  type NewActor = { var newState : Float };

  public func migration(old : OldActor) : NewActor {
    { var newState = old.state.toFloat() };
  };
};

```

### Drop a field intentionally

Consume it in the migration input but do not include it in the output. Expect a compiler warning; ensure the loss is intentional.

### Add a new field

Add the field to `main.mo` with type only (no initializer) AND add it to the next migration's `NewActor` with a value computed from old fields or a constant. The actor body cannot supply the initial value under enhanced migration.

## Migration-Time Semantics

- The migration function runs once at upgrade time, in the upgrade context. Values like `Time.now()` in the migration body are the time of the upgrade, not of each original record creation.
- Do not use constants or magic values in migrations; derive defaults from the migration input or from well-defined application types.

## Compatibility and Tooling

The upgrade safety check compares the new actor body against the last deployed stable signature: a `.most` file (an encoded snapshot of the stable signature — field names and types) referenced from `mops.toml` under `[canisters.<name>.check-stable]`. When that is configured, `mops check --fix` picks it up automatically. Hosted platforms typically wire this up for you and keep the previous `.most` alongside the project.

For the check to pass: the new migration's `OldActor` must match the previously deployed signature, and its `NewActor` must match (or be a stable supertype of) the new actor body.

To derive `OldActor` deterministically: your `OldActor` equals the `NewActor` of the file that precedes yours in `src/backend/migrations/` (lex-order), or `{}` if yours is the first file in the chain. `{}` applies only when the chain starts from an empty canister — a project converted from legacy persistence starts from its pre-conversion stable shape instead, and its existing first file already reflects that.

## Checklist for Upgrades

- [ ] Decide: implicit (compatible change) vs explicit (migration file)
- [ ] **At most ONE pending migration file per build.** Before creating a file, check `src/backend/migrations/` — if a migration is already pending, edit it instead of adding a second
- [ ] If explicit: pick a bare UTC-timestamp filename (`YYYYMMDD_HHMMSS.mo`, no suffix) that sorts after every existing file; do not encode the change in the name
- [ ] Set `OldActor` to the `NewActor` of the file that precedes yours in `src/backend/migrations/` (lex-order), or `{}` if yours is the first file in a project that started out with a chain. Never from current `main.mo`. Never the file's own `NewActor`.
- [ ] When the directory is empty (init migration), `NewActor` must list every stable field declared in `main.mo`, with a value for each
- [ ] Inline both `OldActor` (with old types) and `NewActor` (with new types) — no project imports
- [ ] Implement `public func migration(old : OldActor) : NewActor`
- [ ] Never modify or delete a migration that was already applied; edit (don't duplicate) a pending one
- [ ] Do not use preupgrade/postupgrade or `(with migration = ...)` for data migration
- [ ] Iterate on `mops check --fix` (fast) until it passes — it verifies compilation and upgrade safety
- [ ] Run `mops build` ONCE at the end (slow) to compile the backend and produce the updated IDL bindings

## Additional Resources

- **Migration examples**: See [examples.md](examples.md) for minimal, self-contained examples (add field, map over collection, add optional field)
- **When something does not add up**: Load `troubleshooting-motoko-migrations` for compatibility diagnostics you cannot explain, write failures on frozen files, projects converted from legacy persistence, and requests to remove the chain. Not needed on the normal path.
- **General Motoko development**: Use `writing-motoko` for language fundamentals, core library reference, and architecture patterns
- [Motoko Docs: Data persistence](https://docs.internetcomputer.org/motoko/main/actors/stable-variables)
- [Motoko Docs: Compatibility](https://docs.internetcomputer.org/motoko/main/actors/upgrades)
