---
name: extension-querying-oql
description: >-
  Quick reference for the Caffeine Data Intelligence agent to query an
  OQL-exposing canister (schema() + execute()) through the `icp` CLI
  against the project's `backend` canister: read the schema, form JSON
  queries (filter / order / paginate / aggregate / dotted-path edges),
  and parse the Candid result rows.
version: 0.4.0
compatibility:
  mops: {}
  npm: {}
caffeineai-subscription: [none]
---

# Querying OQL — quick reference

An OQL canister exposes two read-only methods:

| Method | Returns | Purpose |
|---|---|---|
| `schema()` | one JSON `Text` | Catalogue of the canister's entities: each entity's primary key, fields, and edges. |
| `execute(qJson : text)` | typed Candid `Result` | Runs a JSON-encoded query and returns matching rows. |

## Calling the canister

The `icp` CLI is already installed and configured in the sandbox; the
canister name `backend` resolves to the project's canister (no identity,
no canister ID). Both methods are `query` calls, so every invocation
uses `--query`:

```bash
icp canister call backend schema '()' --query
icp canister call backend execute '("<json-query>")' --query
```

`execute` takes one `text` argument — the JSON query embedded as a
Candid text literal. Wrap the JSON in `("...")` and escape every `"` as
`\"`. The query `{"start":"customer","limit":3}` becomes:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"limit\":3}")' --query
```

`schema()` returns its JSON the same way — a Candid `text` literal
`("...escaped json...")`; unescape `\"` → `"` (and `\\` → `\`) to read
it. Add `--branch live` to read the deployed canister instead of the
draft (live is query-only). If a string value contains a single quote,
escape it for the shell with `'\''`.

---

## Recipe

1. **Get the schema once.** `icp canister call backend schema '()' --query` — cache it for the session; it changes only between deployments (§1).
2. **Map the request to entities.** Pick the entity that holds the answer. Use each field's `typeName` and `values` to choose literal types, and `role: {"edge": ...}` to see how entities connect.
3. **Translate into one or more queries.** Start from the entity whose rows you want (§2). Add `where` (§2.1), `orderBy` / `limit` / `offset`, `select`, and `aggregate` / `groupBy` (§2.2). Cross a forward edge with a dotted path in a single query (§4.1); a reverse one-to-many needs the parent keys first, then `in` (§4.2).
4. **Run and read.** `icp canister call backend execute '("<json>")' --query` — parse the Candid rows by cell `name` (§3); if `hasMore`, page with `offset` (§5).
5. **Retry on traps.** There is no error envelope — re-read the schema, fix the query, rerun (§6).

---

## 1. Discover — `schema`

Fetch once and cache for the session — it only changes between canister
deployments.

```bash
icp canister call backend schema '()' --query
```

Read it like this:

- **`name`** → entity name; use it as `start` in queries.
- **`primaryKey`** → field whose value identifies a row. An edge
  `{"to": "<entity>"}` value is a primary-key value in that target.
- **`fields`** → each field's `name`, scalar `typeName`, and `role`:
  `"payload"` (plain field) or `{"edge": {"to": "<entity>"}}` (a foreign
  key — how you traverse the graph). Names may carry a `__1`, `__2`, …
  suffix when two columns would share a name — use the exact names
  `schema()` reports.
- **`values`** (optional) → the exact literals a field can hold
  (typically a variant's arms). Filter with those literals, not guesses:
  `["free","pro","enterprise"]` means query `"enterprise"`, not
  `"Enterprise"`. Absent ⇒ unbounded — sample it with a query if you
  need candidates.
- **`typeName`** → JSON literal type for `value`:
  - `"Nat"` → unsigned integer (`0`, `1`, …)
  - `"Int"` → signed integer (`-1`, `0`, `1`, …)
  - `"Float"` → JSON number with a decimal point (`0.5`, `-3.14`,
    `1.0e2`). A bare integer (`10`) is also accepted — numeric variants
    bridge, so `gt(price, 10)` matches a `price : Float = 12.5` row.
    Float equality is bitwise IEEE-754; use a range (`ge` + `le`) for
    decimals like `0.42` with no exact binary form.
  - `"Bool"` → `true` / `false`
  - `"Text"` → JSON string. `Principal` fields report as `"Text"`
    (canonical textual form) — filter them with a string value.

---

## 2. Form a query — `execute`

A query is a single JSON object. Only `start` is required.

```json
{
  "start":     "<entityName>",
  "where":     <Predicate>,
  "groupBy":   ["<fieldName>", ...],
  "aggregate": [{ "fn": "count|sum|avg|min|max", "field": "<fieldName>", "as": "<outName>" }, ...],
  "orderBy":   [{ "field": "<fieldName>", "dir": "asc|desc" }, ...],
  "offset":    <Nat>,
  "limit":     <Nat>,
  "select":    ["<fieldName>", ...]
}
```

| Field | Default | Notes |
|---|---|---|
| `start` | (required) | An entity `name` from `schema()`. |
| `where` | omit ⇒ no filter | A single predicate (§2.1) — **not** wrapped in `{"filter": ...}`. |
| `groupBy` | `[]` | Bucket rows by these fields; one output row per distinct combination (§2.2). |
| `aggregate` | `[]` | Aggregates per bucket, or over all rows when `groupBy` is empty (§2.2). |
| `orderBy` | `[]` (canister-defined order, typically insertion order) | Multi-key sort, first clause primary. `dir` defaults `"asc"`. |
| `offset` | `0` | Drop the first N matches. |
| `limit` | every match | Keep at most N. `hasMore` in the result tells you if more exist. |
| `select` | every non-hidden field (or, when aggregating, group-key + aggregate columns) | Subset projection. |

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"limit\":3}")' --query
```

Filter + sort + project — the core shape (`where` + `orderBy` + `limit` + `select`):

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"plan\",\"value\":\"enterprise\"}},\"orderBy\":[{\"field\":\"monthlyRevenueUsd\",\"dir\":\"desc\"}],\"limit\":5,\"select\":[\"companyName\",\"monthlyRevenueUsd\",\"accountManagerName\"]}")' --query
```

### 2.1 Predicate operators

A `Predicate` is a JSON object with **exactly one key** that names the
operator.

| Operator | Shape | Meaning |
|---|---|---|
| `eq` / `ne` / `lt` / `le` / `gt` / `ge` | `{"<op>": { "field": "<name>", "value": <scalar> } }` | Scalar relation. |
| `in` | `{"in": { "field": "<name>", "value": [<scalar>, ...] } }` | Membership; empty array matches nothing. |
| `contains` / `startsWith` / `endsWith` | `{"<op>": { "field": "<name>", "value": "<text>" } }` | Case-sensitive substring / prefix / suffix on `Text` — server-side scan, no need to page rows into context. |
| `icontains` | `{"icontains": { "field": "<name>", "value": "<text>" } }` | Case-insensitive `contains`. Prefer this for user-typed search terms. |
| `and` / `or` / `not` | `{"and": [<P>, ...]}` / `{"or": [<P>, ...]}` / `{"not": <P>}` | Boolean composition. |

Text search runs server-side — "the customer whose name mentions north" is one query, not a row scan into context:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"icontains\":{\"field\":\"companyName\",\"value\":\"north\"}},\"select\":[\"companyName\",\"accountManagerName\"]}")' --query
```

`<scalar>` must match the field's `typeName`:

| JSON | Maps to | Use for fields with typeName |
|---|---|---|
| `null` | `null_` | any nullable field (rare in `where`) |
| `true` / `false` | `bool` | `"Bool"` |
| `0`, `1`, `42` | `nat` | `"Nat"` (also matches `"Float"` via numeric bridging) |
| `-1`, `-42` | `int` | `"Int"` (also matches `"Float"` via numeric bridging) |
| `0.5`, `-3.14`, `1.0e2` | `float` | `"Float"` |
| `"foo"` | `text` | `"Text"` |

A row whose field is `null_` fails every relation **except** `ne`. Filter
by relationship with `field` = `"<edge>"` and `value` = the target
entity's **primary-key value**; or read *through* an edge with
`"<edge>.<targetField>"` (§4.1).

### 2.2 Aggregate — count, groupBy, sum/avg/min/max

Compute on the canister instead of fetching every row and tallying
client-side. `fn` is `count`/`sum`/`avg`/`min`/`max`; `field` is required
for every fn except `count`; `min`/`max` also work on text. `as` renames
the output column (default `count`, `sum_<field>`, …) and must not
contain `.` (dots are the edge-traversal separator — parse error). For a
dotted `field` the default joins segments with `_` (`sum` of
`dept.budget` → `sum_dept_budget`). `aggregate` with no `groupBy` → one
row over the whole filtered set (`count` of an empty match is `0`).
`groupBy` with no `aggregate` → a server-side DISTINCT. Output rows
contain only the group-key + aggregate columns.

"How many enterprise customers?" — `count` over a filtered set, one row out:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"plan\",\"value\":\"enterprise\"}},\"aggregate\":[{\"fn\":\"count\"}]}")' --query
```

"Which account manager has the most customers, and total MRR?" — `groupBy` + `count` + `sum`:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"groupBy\":[\"accountManager\"],\"aggregate\":[{\"fn\":\"count\"},{\"fn\":\"sum\",\"field\":\"monthlyRevenueUsd\",\"as\":\"mrr\"}],\"orderBy\":[{\"field\":\"count\",\"dir\":\"desc\"}],\"limit\":1}")' --query
```

---

## 3. Read the result

```candid
type Value  = variant { null_; bool : bool; nat : nat; int : int; float : float; text : text };
type Cell   = record { name : text; value : Value };
type Result = record { rows : vec vec Cell; hasMore : bool };
```

The outer `rows = vec { ... }` is the row list; each inner `vec { ... }`
is one row. Each `record { value = variant { "<tag>" = <payload> }; name = "<field>" }`
is one cell — `name` tells you which field, the `<tag>` tells you the
scalar type, the payload is the value. `35_000 : nat` underscores are
digit separators — strip them if parsing. `hasMore = false` ⇒ you got
every match; `hasMore = true` ⇒ truncated, fetch the next page. Look
cells up by `name`, not position — order shifts if `select` changes.

---

## 4. Walk edges (joins)

**Forward (single-valued) relationships are one query**: a dotted path
crosses a declared edge, in any field position. **Reverse (one-to-many)
relationships stay two queries** with the `in` pattern (§4.2).

### 4.1 Forward (child → parent): dotted paths

`"<edgeField>.<targetField>"` reads through the edge server-side — in
`where`, `groupBy`, `orderBy`, `aggregate.field`, and `select`. Project
through an edge in one query:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"companyName\",\"value\":\"Northstar Public\"}},\"select\":[\"companyName\",\"accountManager.name\",\"accountManager.office\"]}")' --query
```

Multi-hop chains work (`"manager.department.name"`, max 4 hops), and it
composes with aggregation — "average revenue by the account manager's
office" is one call:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"groupBy\":[\"accountManager.office\"],\"aggregate\":[{\"fn\":\"avg\",\"field\":\"monthlyRevenueUsd\",\"as\":\"avg_mrr\"}],\"orderBy\":[{\"field\":\"avg_mrr\",\"dir\":\"desc\"}]}")' --query
```

Rules:

- The head segment must be a field whose `role` is
  `{"edge": {"to": ... }}` in `schema()` — a dotted path into a
  non-edge field **traps**, even if its values look like foreign keys
  (traversal is schema-driven, not name-guessed). If the author didn't
  declare the edge, fall back to the two-query pattern below.
- A null or dangling FK resolves the whole dotted path to `null`
  (left-join): the row fails every relation except `ne`, and projects
  the cell as `null`.
- **Aggregate from the many side.** Cross-entity aggregates run over the
  start entity's rows: `avg` of `"department.budget"` from `employee` is
  employee-weighted. For per-department numbers, start from
  `department` — or group by the dotted path and aggregate start-entity
  fields.
- Selecting the bare edge field (`"accountManager"`) still returns the
  FK scalar; there is no `.*` — name each target field you want.

### 4.2 Reverse (one parent → many children)

`eq` for one parent primary key, `in` for a batch — on the edge field,
with the target entity's primary-key values.

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"accountManager\",\"value\":\"daniel@helix.systems\"}},\"select\":[\"companyName\",\"monthlyRevenueUsd\"]}")' --query
```

When the parent condition is a plain predicate, you don't need the batch
— it's a forward filter through the edge (§4.1). "All customers managed
by anyone in the Berlin office" is one query:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"accountManager.office\",\"value\":\"Berlin\"}},\"select\":[\"companyName\",\"monthlyRevenueUsd\"]}")' --query
```

The batch `in` pattern is required when the parent set needs its own
query shape (top-N, ordered, paginated): collect the keys first, then
`in` on the edge field. "Customers managed by the three most senior
employees" is two queries:

```bash
icp canister call backend execute '("{\"start\":\"employee\",\"orderBy\":[{\"field\":\"level\",\"dir\":\"desc\"}],\"limit\":3,\"select\":[\"email\"]}")' --query
# collect the three emails from the rows, then:
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"in\":{\"field\":\"accountManager\",\"value\":[\"alex@helix.systems\",\"james@helix.systems\",\"sarah@helix.systems\"]}},\"select\":[\"companyName\",\"monthlyRevenueUsd\"]}")' --query
```

Always batch with `in` rather than running N separate `eq` queries.

### 4.3 Compound conditions

Stack with `and` / `or`:

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"and\":[{\"eq\":{\"field\":\"plan\",\"value\":\"enterprise\"}},{\"in\":{\"field\":\"country\",\"value\":[\"US\",\"CA\",\"DE\"]}},{\"ge\":{\"field\":\"monthlyRevenueUsd\",\"value\":20000}}]},\"orderBy\":[{\"field\":\"monthlyRevenueUsd\",\"dir\":\"desc\"}]}")' --query
```

### 4.4 Two-hop / self-edge join

When the parent key isn't given but must be looked up first — e.g. "who
reports to the lead of project `forge20`?" — run two queries. The second
filters on a self-edge (`employee.manager` → `employee`) by the key the
first query returned:

```bash
icp canister call backend execute '("{\"start\":\"project\",\"where\":{\"eq\":{\"field\":\"codename\",\"value\":\"forge20\"}},\"select\":[\"lead\"]}")' --query
# the row's `lead` cell is the lead's email, e.g. priya@helix.systems — use it as the parent key:
icp canister call backend execute '("{\"start\":\"employee\",\"where\":{\"eq\":{\"field\":\"manager\",\"value\":\"priya@helix.systems\"}},\"select\":[\"name\",\"jobTitle\",\"level\"]}")' --query
```

---

## 5. Pagination

`limit` caps results. `hasMore` reports truncation. Walk pages with
`offset`:

```text
offset = 0
limit  = 25
loop:
  result = icp canister call backend execute '("{\"start\":\"...\",\"limit\":25,\"offset\":<offset>,...}")' --query
  consume result.rows
  if not result.hasMore: break
  offset += limit
```

Always set `limit` explicitly. OQL itself imposes no cap (omitting
`limit` returns every match), and a canister author may add one — in
which case over-asking is silently truncated.

---

## 6. Pitfalls

| Symptom | Cause / Fix |
|---|---|
| `execute` traps `OQL: unknown entity '...'` | `start` doesn't match any `name` from `schema()` — entity names are case-sensitive. Re-read the schema. |
| `execute` traps with a parse error | The JSON was malformed (trailing comma, single quotes), or not escaped as a Candid text literal — wrap as `("...")` with every inner `"` escaped as `\"`. Validate the JSON with `python3 -m json.tool` first. |
| No rows returned for a filter you expect to match | (1) `value` literal type doesn't match the field's `typeName` (`"5"` for a `Nat`); (2) typo in `field` — unknown fields are silently `null_`, so most predicates fail; (3) the field is genuinely `null_` in storage. |
| `gt` / `lt` returns weird results across types | Mixed-type comparisons aren't defined. Make sure both operands are the same `typeName`. |
| `contains` misses rows you can see | `contains` / `startsWith` / `endsWith` are case-sensitive. Use `icontains` for user-typed search terms. |
| Dotted path traps `'x' is not an edge of 'y'` | The head segment isn't a declared edge — traversal is schema-driven even when values look like FKs. Use the two-query `in` pattern instead. |
| Cross-entity average looks wrong | Aggregates run over the **start** entity's rows. Start from the entity whose rows you want averaged, or group by the dotted path and aggregate start-entity fields. |
| `execute` returns rows but missing fields | A field you `select`-ed isn't in the entity (typo, or hidden by the author). Drop it from `select`, or remove `select` for the default projection. |

There is **no structured error envelope**. Any failure is a trap — fix
the query and retry.
