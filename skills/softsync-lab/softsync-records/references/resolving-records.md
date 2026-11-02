<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

## Entity Resolution + Relation Expansion

Entity resolution is NOT complete until relation expansion is done. These are one operation. Never answer or call downstream tools after finding a root record without expanding.

**1. Find the root record.**
`semantic_search_records` requires a `table` parameter — it searches one table per call. Pick the most likely table for the entity based on context (e.g. a company name → companies table). If found, proceed to step 2. If not found, try other tables in the workspace schema until you find it or exhaust all tables.

**2. Expand through ALL related tables.**
Once you have root record R (id: ROOT_ID) in table T (apiName: ROOT_TABLE):

  a) Read the workspace schema. For EVERY other table U, check each field: if `field.kind === "relation"` and `field.options.targetTable === ROOT_TABLE`, that table has records linked to R.

  b) For EACH such table U and relation field F found in (a), call:
     `search_records({ table: U.apiName, fieldFilters: [{ field: F.apiName, operator: "eq", value: ROOT_ID }] })`
     Collect every record ID returned.

  c) Also check T's own fields for outbound relations (`kind: "relation"` pointing to other tables). The root record's data may already contain those IDs.

  d) Do this for EVERY related table found in (a), not just one. If the schema shows 3 tables with relations to T, make 3 `search_records` calls.

**3. Collect the complete ID set.**
finalIds = [ROOT_ID, ...all IDs from step 2]. This is the result. Never return only the root ID.

**Prohibitions:**
- NEVER ask the user "do you want me to check related [table]?" — always expand automatically.
- NEVER skip expansion. NEVER offer it as an optional follow-up.
- NEVER answer or call downstream tools (like `query_messages`) with only the root ID.
