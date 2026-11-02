<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Filter Records

## Tool Usage Strategy

- **Search Routing**:
  - **Exact record ID**: call `get_record_by_id` directly.
  - **Name/title/company-like text**: start with `semantic_search_records`.
  - **Structured values**: use `search_records` for status/stage/type, number/date filters, exact emails/phones/URLs, exact identifier text fields such as `organization_number` and `customer_id`, resolved relation IDs, and resolved member IDs.
  - **Related-record attribute predicates**: if the user is filtering a parent table by fields that live on a related table, prefer a single `search_records` call with a nested relation field path.
  - **Literal text match**: use `contains` only for exact token/phrase matching on TEXT fields. Do not use it for fuzzy entity discovery.
  - **Relations by identity**: resolve the target record first, then filter by relation ID.
  - **Relations by attributes**: do not resolve related records first if the condition is about the related record's own fields and nested relation filters can express it directly.
- **ID provenance rule**: UUID-like tokens in raw emails, URLs, or tracking params are not automatically record IDs. Treat them as record IDs only if the user explicitly says so or a prior workspace tool returned them.
- **Never** do `search_records` by id and then `get_record_by_id`. If you have a real record ID, fetch it directly.
- Reuse IDs already found in the same turn instead of re-running the same lookup.
- **Fetch data rather than guessing.** Never infer values not returned by tools.
- **Statistics**: use `record_statistic` for counts, aggregates, and grouped record metrics.

## System Fields (built-in, no field definition needed)

These fields are always available for filtering and sorting on every table:

| Field ID | Type | Description |
|----------|------|-------------|
| `__system_created_at` | datetime | Record creation timestamp |
| `__system_updated_at` | datetime | Last modification timestamp |
| `__system_created_by` | user ID | The user who created the record |
| `__system_last_interaction_at` | datetime | Last email/calendar interaction linked to this record |

### System field operators
- `__system_created_at`, `__system_updated_at`, `__system_last_interaction_at`: support `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `is_empty`, `is_not_empty`
- `__system_created_by`: supports `eq`, `ne`, `is_empty`, `is_not_empty`

### System field examples

**Sort by last interaction (most recent first)**
```json
{
  "table": "contacts",
  "sort": { "field": "__system_last_interaction_at", "direction": "desc" },
  "limit": 20
}
```

**Filter records with no interaction**
```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "__system_last_interaction_at", "operator": "is_empty" }]
}
```

**Filter records not interacted with since a date**
```json
{
  "table": "contacts",
  "fieldFilters": [{ "field": "__system_last_interaction_at", "operator": "lt", "value": "2026-04-01" }]
}
```

**Sort by creation date**
```json
{
  "table": "deals",
  "sort": { "field": "__system_created_at", "direction": "desc" },
  "limit": 10
}
```

## Operator Validation Rules (CRITICAL)

These rules are enforced server-side. Violating them causes errors.

| Operator | Allowed field kinds | Notes |
|----------|-------------------|-------|
| `eq`, `ne` | ALL (text, number, date, select, multi_select, relation, user) | Universal |
| `gt`, `gte`, `lt`, `lte` | NUMBER, DATE only | Rejected on text/select/relation/user |
| `contains` | TEXT, DATE only | Rejected on select, multi_select, number, relation, user |
| `in` | Array fields only (isMany: true) | For multi_select, text[] (emails/phones), relation[], user[] |
| `is_empty`, `is_not_empty` | ALL | Always allowed |

### Key constraints
- **`contains` on MULTI_SELECT → ERROR.** Use `in` instead to check membership.
- **`contains` on SELECT → ERROR.** Use `eq` for exact match.
- **`in` on non-array fields → ERROR.** Only works on fields with `isMany: true`.
- **`in` value must be scalar** (not an array). It checks if the value exists IN the field's array.
- **`gt/gte/lt/lte` on TEXT/SELECT → ERROR.** These are only for numeric/date comparisons.

### Common mistakes to avoid
- ❌ `{ "field": "status", "operator": "contains", "value": "active" }` → status is SELECT, use `eq`
- ❌ `{ "field": "labels", "operator": "contains", "value": "VIP" }` → labels is MULTI_SELECT, use `in`
- ❌ `{ "field": "emails", "operator": "eq", "value": "x@y.com" }` → emails is isMany TEXT, use `in`
- ❌ `{ "field": "companies", "operator": "in", "value": ["id1", "id2"] }` → value must be scalar string
- ✅ `{ "field": "status", "operator": "eq", "value": "active" }`
- ✅ `{ "field": "labels", "operator": "in", "value": "VIP" }`
- ✅ `{ "field": "emails", "operator": "in", "value": "x@y.com" }`

## Agent-Facing Tool Shapes (CRITICAL)

- Use actual tool payloads, not internal DTOs.
- `semantic_search_records`: `{ table, query, sort?, groupId?, limit? }`
- `search_records`: `{ table, fieldFilters: [{ field, operator, value }], sort?, groupId?, limit?, cursor? }`
- Use table API names and field API names from workspace description, not labels.
  - Good: `table: "deals"`, `field: "deal_value"`
  - Bad: `table: "Deals"`, `field: "Deal Value"`
- Filters are ANDed by default. To OR some of them, give each of those filters the same `orGroup` label and `condition: "or"` — see the OR example below.
- Supported exposed operators: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `in`, `is_empty`, `is_not_empty`.
- For array fields, `in` expects one member value, not an array.
- `is_empty` and `is_not_empty` require no `value` property and work for every filterable field kind.
- The tool validates field/operator compatibility and, for SELECT/MULTI_SELECT fields with `allowCustom: false`, returns the configured choice values when a value is invalid.
- Do not invent other filter keys such as `groupId` or arbitrary extra properties. `condition` and `orGroup` are the only grouping keys.

## CRM Filter And Sort Cookbook

Use CRM fields as the model:

- Companies: `name`, `status`, `service`, `emails`, `phones`, `websites`, `revenue`, `organization_number`, `account_owner`
- Contacts: `first_name`, `last_name`, `emails`, `companies`, `status`
- Tasks: `title`, `status`, `end_date`, `owner`, `contacts`
- Deals: `title`, `company`, `contacts`, `deal_value`, `close_date`, `stage`

### Semantic Lookup

**GOOD**
```json
{ "table": "companies", "query": "Acme Corporation", "limit": 5 }
```

**BAD**
```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "name", "operator": "eq", "value": "Acme Corporation" }]
}
```

### Exact Structured TEXT

**GOOD: exact email / identifier**
```json
{
  "table": "contacts",
  "fieldFilters": [{ "field": "emails", "operator": "in", "value": "sarah@acme.com" }]
}
```

```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "organization_number", "operator": "eq", "value": "123456789" }]
}
```

**BAD: `in` with array value**
```json
{
  "table": "contacts",
  "fieldFilters": [{ "field": "emails", "operator": "in", "value": ["a@acme.com", "b@acme.com"] }]
}
```

### Select, Number, Date, Sort

**GOOD: select**
```json
{
  "table": "deals",
  "fieldFilters": [{ "field": "stage", "operator": "eq", "value": "negotiation" }]
}
```

**GOOD: records where a field is populated**
```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "industry", "operator": "is_not_empty" }]
}
```

**GOOD: numeric/date filter with sort**
```json
{
  "table": "deals",
  "fieldFilters": [{ "field": "deal_value", "operator": "gte", "value": 50000 }],
  "sort": { "field": "deal_value", "direction": "desc" },
  "limit": 20
}
```

```json
{
  "table": "tasks",
  "fieldFilters": [
    { "field": "end_date", "operator": "lt", "value": "2026-04-16" },
    { "field": "status", "operator": "ne", "value": "completed" }
  ],
  "sort": { "field": "end_date", "direction": "asc" }
}
```

**BAD: wrong enum label or wrong operator kind**
```json
{
  "table": "deals",
  "fieldFilters": [{ "field": "stage", "operator": "eq", "value": "Negotiation" }]
}
```

```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "industry", "operator": "gte", "value": "saas" }]
}
```

### User And Relation Filters

Use member UUIDs for USER fields and record UUIDs for RELATION fields.

**GOOD**
```json
{
  "table": "tasks",
  "fieldFilters": [{ "field": "owner", "operator": "eq", "value": "<member-uuid>" }]
}
```

```json
{
  "table": "contacts",
  "fieldFilters": [{ "field": "companies", "operator": "in", "value": "<company-record-uuid>" }]
}
```

**BAD**
```json
{
  "table": "deals",
  "fieldFilters": [{ "field": "company", "operator": "eq", "value": "Acme" }]
}
```

### Literal TEXT Contains

**GOOD**
```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "description", "operator": "contains", "value": "ERP" }]
}
```

**BAD**
```json
{
  "table": "companies",
  "fieldFilters": [{ "field": "name", "operator": "contains", "value": "Acme" }]
}
```

## Nested Field Guidance

- The read engine supports nested relation paths in the form `relationField.nestedField`.
- Unprefixed nested paths behave like `any:`.
- When the user asks for parent records constrained by properties of related records, nested field filters are the default first choice because they keep the query in one structured search.
- Quantifiers:
  - `any:companies.country` = at least one related company matches.
  - `all:companies.country` = every related company matches.
- Use nested fields only for relation traversal, not for arbitrary dot notation.
- Nested filtering is best for questions like:
  - contacts whose related companies match a field
  - tasks whose related contacts/deals match a field
  - deals whose related contacts match a field
- Nested operators follow the nested field type:
  - TEXT: `eq`, `ne`, `contains`
  - NUMBER/DATE: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`

### Nested Field Examples

**If the runtime tool schema exposes nested field names, these are valid patterns:**

**GOOD: any related company is in Norway**
```json
{
  "table": "contacts",
  "fieldFilters": [{ "field": "any:companies.country", "operator": "eq", "value": "Norway" }]
}
```

**GOOD: all related companies are active**
```json
{
  "table": "contacts",
  "fieldFilters": [{ "field": "all:companies.status", "operator": "eq", "value": "active" }]
}
```

**GOOD: tasks with any related contact whose country is Sweden**
```json
{
  "table": "tasks",
  "fieldFilters": [{ "field": "any:contacts.country", "operator": "eq", "value": "Sweden" }]
}
```

**GOOD: deals with any related contact whose last name literally contains Chen**
```json
{
  "table": "deals",
  "fieldFilters": [{ "field": "any:contacts.last_name", "operator": "contains", "value": "Chen" }]
}
```

**BAD: raw dotted path when schema does not expose nested fields**
```json
{
  "table": "tasks",
  "fieldFilters": [{ "field": "contacts.status", "operator": "eq", "value": "active" }]
}
```

**GOOD: OR — any related company is in Norway or Sweden**
```json
{
  "table": "contacts",
  "fieldFilters": [
    { "field": "any:companies.country", "operator": "eq", "value": "Norway", "orGroup": "country" },
    { "field": "any:companies.country", "operator": "eq", "value": "Sweden", "condition": "or", "orGroup": "country" }
  ]
}
```

**BAD: invented grouping key (`groupId` is not a filter key)**
```json
{
  "table": "contacts",
  "fieldFilters": [
    { "field": "any:companies.country", "operator": "eq", "value": "Norway", "groupId": "g1" },
    { "field": "any:companies.country", "operator": "eq", "value": "Sweden", "condition": "or", "groupId": "g1" }
  ]
}
```

### Nested Fallback Rule

If the current tool schema does **not** expose nested field names, do not invent them. Use tool chaining instead:

```text
1. resolve the related records first (semantic or structured search)
2. pick the target record IDs
3. filter the parent table by the relation field using those IDs
```

Example: “Find contacts at Acme”

```text
1. semantic_search_records on companies with query "Acme"
2. choose the correct company record ID
3. search_records on contacts with { field: "companies", operator: "in", value: "<company-record-uuid>" }
```

## Practical Decision Rules

- Name/title/company-like phrase: start with `semantic_search_records`.
- Exact structured value: use `search_records`.
- Relation by identity or by name of a related entity: resolve the related record first, then filter by relation ID.
- Relation by attributes on the related entity: prefer nested `search_records` field filters first; only fall back to chaining if nested field paths are unavailable in the current tool schema.
- Recent/biggest/soonest: choose the right search strategy first, then add sort.
- If the current tool schema cannot express the requested nested logic, use a small number of deliberate chained calls rather than inventing unsupported payload structure.

## Handling Statistics or Counting Tasks

- **Tool Selection**: Use `record_statistic` for any queries involving counting, summing, averaging, or ratios of record data. Do NOT fetch all records to count them manually.
- **Handling Aliases (CRITICAL)**:
  - Users might refer to fields by their *semantic meaning* (alias) rather than their label.
  - **Example**: A "Stage" field might have options like "New", "Negotiation", "Won", but also aliases like "0%", "50%", "100%" representing "probability".
  - If a user asks for "deal value by probability", they likely mean "SUM of deal value grouped by Stage (using aliases)".
  - In such cases, set `options: { useViewByAlias: true }` in the tool call to use these semantic values for grouping.
  - **Interpreting Results**: When `useViewByAlias` is true, the tool aggregates data by the alias (e.g., "0%").
    - The `label` property in the result will be the alias (e.g., "0%").
    - The `name` property will be the name of choice(s) that maps to this alias (e.g., "Lost").
    - If displaying a table/chart, use the `label` as the category name, not the representative `name`.
- **Chart Type**:
  - Metric: Use for single value metrics, like "total deal value", "average deal value", etc.
  - Bar: Use for comparing values across categories, like "deal value by stage", "deal value by probability", etc.
- **Parameter mapping**:
  - `viewByField`: The primary categorization field (X-axis).
  - `measureField`: The field being calculated (Y-axis), e.g., "Deal Value".
