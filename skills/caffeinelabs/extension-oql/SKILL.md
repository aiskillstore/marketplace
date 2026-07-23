---
name: extension-oql
description: Make a canister's data queryable by the Caffeine Data Intelligence agent. Use whenever an app stores structured data (Maps/Lists/arrays of records) that should be answerable in natural language — "top customers", "revenue by region", "active projects". Adds a discoverable `schema()` and a JSON `execute()` query endpoint via the `caffeineai-oql` mops package's `Expose` mixin.
version: 0.4.0
compatibility:
  mops:
    caffeineai-oql: "~0.4.0"
caffeineai-subscription: [none]
---

# OQL — Object Query Layer

Go over the actor's fields (non-transient) and, for each collection worth querying,
consider how its data maps to a **table** in a database (an *entity*). You only
declare one entity per table — the `Expose` mixin makes them queryable.

# Backend

Each entity carries an authorization level; the default `.controllerOnly()` is
safe (private to users, still readable by the Data Intelligence agent). Model
your entities first, then pick a level per entity — see `## Auth`.

## Setup

Run `mops add caffeineai-oql@0.4.0` in the **same write batch** as your first
`mo:caffeineai-oql/...` import. Auto-derivation requires `moc >= 1.11` (the
generated-app template already satisfies this).

## Declare entities and install

`.toEntity(name, typeName, primaryKey)` turns a collection of records into a
queryable entity; the compiler auto-derives the fields. Each entity sets its own
authorization level (see `## Auth`); the example below shows one table per level.
`Expose` adds only the OQL query methods (`schema` / `execute`) — your existing
state, types, and `shared` methods are untouched.

```motoko filepath=src/backend/main.mo
import Map       "mo:core/Map";
import Nat       "mo:core/Nat";
import Principal "mo:core/Principal";
import OQL       "mo:caffeineai-oql";
import Expose    "mo:caffeineai-oql/Expose";

actor {
  type Product  = { id : Nat; name : Text; priceUsd : Nat };
  type Vendor   = { id : Nat; name : Text };
  type AuditLog = { id : Nat; action : Text; atNs : Nat };
  type Note     = { id : Nat; user : Principal; body : Text };
  type Document = { id : Nat; owner : Principal; title : Text };
  type User     = { id : Principal; isAdmin : Bool };

  let products  = Map.empty<Nat, Product>();
  let vendors   = Map.empty<Nat, Vendor>();
  let supplies  = Map.empty<Product, Vendor>();    
  let auditLogs = Map.empty<Nat, AuditLog>();
  let notes     = Map.empty<Nat, Note>();
  let documents = Map.empty<Nat, Document>();
  // not all collections need to be exposed if there is no need — `users` backs
  // auth only, so it is intentionally never turned into an entity below
  let users     = Map.empty<Principal, User>();

  let anyP = Principal.fromText("aaaaa-aa");   // sample owner; the value is ignored

  // Look up whether a caller is an admin.
  func isAdmin(p : Principal) : Bool =
    switch (users.get(p)) { case (?u) u.isAdmin; case null false };

  // A custom .ownedByWith rule: admins see every document, everyone else only
  // their own. `owner` is the field's Value — a Principal column arrives as #text.
  func canSeeDocument(caller : Principal, owner : OQL.Value) : Bool =
    isAdmin(caller) or owner == #text(caller.toText());

  include Expose({
    entities = [
      // #public_ — anyone, incl. anonymous, reads the whole catalogue
      products.toEntity("product", "Product", "id")
        .sample({ id = 0; name = ""; priceUsd = 0 })
        .public_()
        .build(),
      vendors.toEntity("vendor", "Vendor", "id")
        .sample({ id = 0; name = "" })
        .public_()
        .build(),
      // `supplies : Map<Product, Vendor>` — a map between two non-primitive types.
      // The identity lives in the key/value records, not a field, so iterate
      // .entries() in manual mode, promote each side's id, and .edge both — a
      // query can then traverse "product.name" and "vendor.name".
      OQL.Entity.manual<(Product, Vendor)>("supply", func () = supplies.entries(), "Supply", "key")
        .payload("key",     func ((p, v)) = p.id.toText() # ":" # v.id.toText())
        .payload("product", func ((p, _)) = p.id) .edge("product", "product")
        .payload("vendor",  func ((_, v)) = v.id) .edge("vendor",  "vendor")
        .controllerOnly()
        .build(),
      // #controllerOnly (the default, shown explicitly) — only the platform reads
      auditLogs.toEntity("auditLog", "AuditLog", "id")
        .sample({ id = 0; action = ""; atNs = 0 })
        .controllerOnly()
        .build(),
      // #scopedPerUser — each signed-in user reads only their own rows
      notes.toEntity("note", "Note", "id")
        .sample({ id = 0; user = anyP; body = "" })
        .ownedBy("user")
        .scopedPerUser()
        .build(),
      // #controllerOrScoped — controller reads all; scoped reads use canSeeDocument.
      documents.toEntity("document", "Document", "id")
        .sample({ id = 0; owner = anyP; title = "" })
        .ownedByWith("owner", canSeeDocument)
        .controllerOrScoped()
        .build(),
    ];
  });
}
```

## Auth

Authorization is **per entity** — each builder declares a level, and `schema()`
and `execute()` both run the check against the live `caller`. No app-wide config,
no tokens. The default when none is set is `#controllerOnly`.

| Builder call | Who reads | Rows returned |
|---|---|---|
| `.public_()` | anyone (incl. anonymous) | all |
| `.controllerOnly()` *(default)* | controllers only | all |
| `.scopedPerUser()` | any signed-in caller | only the caller's own |
| `.controllerOrScoped()` | controllers + signed-in callers | controller: all; user: own |

### Choosing a level

Pick per entity by who should read its rows — when in doubt, keep the default.

- **`.controllerOnly()`** *(default)* — private app data the agent should answer
  over, but no end user reads directly (orders, metrics, audit logs, config). The
  agent calls as the controller, so it reads everything while the data stays
  private to users.
- **`.public_()`** — world-readable data, including logged-out visitors (public
  catalogue, published content, leaderboards).
- **`.controllerOrScoped()`** — per-user data where each user reads only their own
  rows, but the agent must still answer aggregate questions (profiles, a user's
  orders). Requires an owner column.
- **`.scopedPerUser()`** — strictly private per-user data: each user reads only
  their own, and the agent is scoped too, so it **cannot** answer over this table
  (DMs, private journals). Requires an owner column — prefer
  `.controllerOrScoped()` unless the agent must be blind to it.

The user may override per entity; if a request implies per-user data but is
ambiguous, ask.

### Per-user (row-level) scoping

Scoped levels (`.scopedPerUser()`, `.controllerOrScoped()`) need a way to know
which rows belong to the caller — an **owner column** or a subject-honouring
source. `.build()` traps if a scoped entity has neither, and also traps if a
`.public_()` entity declares an owner (the check would never run). This is the
guardrail against the common data-leak footgun.

**When to tag:** a `Principal` field is the signal.

- `.ownedBy(field)` — the field *is* the owner; visibility is identity equality.
- `.ownedByWith(field, canSee)` — custom visibility (teams, admins, sharing).
  `canSee : (caller : Principal, owner : Value) -> Bool` decides per row; `field`
  need not be a `Principal`, and the closure can read actor state.

A scoped caller sees only its owned rows — both as the query target and through a
join — so traversal can never leak another owner's rows.

```mo
// Per-user notes: each signed-in user reads only their own rows.
notes.toEntity("note", "Note", "id")
  .sample({ id = 0; owner = Principal.fromText("aaaaa-aa") /* any principal */; body = "" })
  .ownedBy("owner")
  .scopedPerUser()
  .build()

// .ownedByWith custom rule: the owner sees their own docs, listed admins see
// everyone's, and the platform controller sees all (#controllerOrScoped).
// `owner` is the field's Value — a Principal column arrives as #text(principal).
docs.toEntity("doc", "Doc", "id")
  .ownedByWith("owner", func (caller, owner) =
    admins.get(caller) != null or owner == #text(caller.toText()))
  .controllerOrScoped()
  .build()
```

`.ownedBy(f)` is exactly `.ownedByWith(f, OQL.Entity.ownerIsCaller)`. At most one
owner column; it must be a real field, not also `.edge` / `.hidden`. For
owner-keyed storage (`Map<Principal, List<T>>`) use
`OQL.Entity.newScoped(name, scopedIter, typeName, primaryKey)` so the scan is
O(user rows): `scopedIter(?p)` returns only `p`'s rows, `scopedIter(null)` all
(schema seeding).

## Entity builder

Two modes, picked by the row type `T`.

### Auto-derivation — `.toEntity`

For records whose fields are all primitives with a built-in `_toRow` (`Nat`,
`Int`, `Float`, `Text`, `Bool`, the sized `Nat`/`Int` widths, `Principal`):

```mo
customers.toEntity(name, typeName, primaryKey)
  .sample(template)              // REQUIRED if the collection may be empty at build
  .edge(field, targetEntity)     // tag an existing field as a foreign key
  .ownedBy(field)                // (or .ownedByWith(field, canSee)) per-user scoping
  .scopedPerUser()               // auth level: .public_ / .controllerOnly (default) / .scopedPerUser / .controllerOrScoped
  .hidden(field)                 // drop a field from schema + default projection
  .build()
```

- `.toEntity` is sugar for `OQL.Entity.new<T>(name, func () = coll.values(), …)`;
  it exists on `Map`, `Set`, `List`, `[T]`, and `[var T]`. It iterates **values
  only** — if a row's identity (PK or owner) lives in the *Map key*, it is not a
  field: promote it via manual mode over `.entries()`, or `OQL.Entity.newScoped`
  when it's the owner.
- `primaryKey`, and any `.edge` / `.ownedBy` field, must name a real,
  non-`.hidden` column of the row.
- `.edge(name, target)` tags an **existing** field (it does not add one) as an FK,
  enabling dotted-path traversal `"name.targetField"` in queries. FK/PK types
  must be `Text`, `Nat`/`Int`, or `Bool` (`Float` keys are rejected), and the
  target's primary key must not be `.hidden`.
- `.sample(template)` seeds schema discovery; without it an empty collection
  yields an empty schema. Only the shape matters, not the values.

Schema fields are listed in **lexicographic order** (the `__record` combiner's
canonical form); sort client-side if display order matters.

### Manual mode — `.toEntityManual` / `OQL.Entity.manual`

For non-record `T`, computed fields, or records with nested / variant / option /
collection fields:

```mo
authors.toEntityManual<Author>("author", "Author", "id")
  .payload("name", func a = a.name)        // one field; extract returns a _toRow value
  .flatten(func a = a.address)             // splice a nested record's fields as columns
  .payload("tagCount", func a = a.tags.size())
  // .edge / .hidden work as in auto mode, by field name
  .build()
```

- `.payload(name, extract)` — `name` must not contain `.`. For options/variants,
  return `Text`/`Nat` with a sentinel (see below).
- `.flatten(extract : T -> S)` — `S` must be flat; each of its fields becomes a
  top-level column. Drop unwanted ones with `.hidden`. Name collisions get
  `__1`, `__2` suffixes (nothing is dropped).
- `OQL.Entity.manual<T>(name, iter, typeName, primaryKey)` for arbitrary row
  sources (custom flatteners, filtered iterators).

`OQL.Value` is `{ #null_; #bool; #nat; #int; #float; #text }`. Numeric variants
compare across each other, so a JSON integer threshold matches a `Float` value.

| Row type `T` | Mode |
|---|---|
| All-primitive record | `.toEntity` |
| Record with `?` / variant / nested field | `.toEntity` once you ship `<Type>Value.mo` (below); else manual |
| Record with a collection field | manual — `.size()` or `Text.join` into a payload |
| Tuple / primitive / computed | manual |

## Converting non-primitive fields

To keep a record on the auto-derive path, give each non-primitive field type a
`_toRow : T -> OQL.Value`: one file per type named `<TypeName>Value.mo`, a single
`public func _toRow`, imported **top-level** in the file that declares entities
(the resolver does not walk submodules). Parent records then ride `.toEntity(...)`
with no per-field `.payload`.

```mo
// OptTextValue.mo — option → sentinel
module { public func _toRow(self : ?Text) : OQL.Value =
  switch self { case null { #text("") }; case (?t) { #text(t) } }; };

// StatusValue.mo — variant → tag text
module { public func _toRow(self : Status) : OQL.Value =
  #text(switch self { case (#draft) "draft"; case (#published) "published" }); };

// DepartmentValue.mo — nested record → child PK (then .edge the field)
module { public func _toRow(self : Department) : OQL.Value = #text(self.name); };
```

**Always return ONE `Value` variant**, even for null (sentinel `""` / `0` /
`false`) — a `_toRow` that sometimes returns `#null_` makes the reported schema
type flip-flop by row order. Sentinels keep the field queryable (`eq value ""`
matches the nulls). For a one-off field, inline the same conversion in a
`.payload` instead of a module; lift to a module only when 2+ entities need it.
A record used both as an entity and as a nested field just ships its
`<Type>Value.mo` — the structural `Row` derivation and your `Value` collapse are
distinct types and coexist.

## Entity patterns beyond one-row-per-record

The same storage can back several entities — pick what the client should see:

- **reshaped** — flatten `Map<K1, Map<K2, V>>` into rows; have the flattener emit
  a flat **record** (not a tuple) so it still auto-derives, then `.edge` the
  promoted keys.
- **enumerated** — derive an entity from index keys (`Map<Author, …>.keys()`) via
  `OQL.Entity.manual`; entries with no rows simply don't appear.
- **synthetic** — project a junction from an array field to make a many-to-many
  queryable from both sides:

```mo
OQL.Entity.manual<(Article, Text)>("articleTag", func () = flattenTags(articles), "Pair", "pair")
  .payload("article", func ((a, _)) = a.id) .edge("article", "article")
  .payload("tag",     func ((_, t)) = t)    .edge("tag", "tag")
  .build()
```

## Checklist

- [ ] `mops add caffeineai-oql@0.4.0` in the same batch as the first import
- [ ] Each entity: row iterator exists; `.toEntity` (all-primitive) or
      `.toEntityManual` / `OQL.Entity.manual` otherwise
- [ ] `<Type>Value.mo` for every non-primitive field reused across entities,
      imported top-level
- [ ] `.sample(template)` whenever the collection may be empty at build time
- [ ] FK fields `.edge(name, target)`; filter-only fields `.hidden(name)`
- [ ] Every sentinel conversion returns ONE `Value` variant
- [ ] Per-user entities use `.ownedBy` / `.ownedByWith` **and** a scoped level
      (`.scopedPerUser()` / `.controllerOrScoped()`) — never bare
      `.controllerOnly()`
