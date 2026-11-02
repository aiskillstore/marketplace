<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Writing Records

Use this skill for **all data modifications** (create + update + enrichment + relation linking). Do not split work into separate "create-only" vs "edit-only" modes.

## 0. Capability Boundary Check (MANDATORY)

Before executing writes, verify that the requested operation is supported by available write/enrichment tools.

- If the request requires a capability that does not exist (for example true bulk operations, unsupported external provider enrichment, unsupported side effects), do **not** simulate or approximate it with long repetitive one-by-one tool loops.
- If only part of the request is supported, clearly state supported vs unsupported parts, then proceed only with supported parts if user intent allows.
- If unsupported, stop write attempts early and return a concise limitation response with practical alternatives.
- Never imply a tool can do something it cannot.
- If supported, execute the write path immediately; do not return limitation text.

## A. Execution Flow (MANDATORY)

0. **Record ID Provenance & Intent Gate (MANDATORY)**
  - Treat UUID-like strings found in raw unstructured content (emails, links, tracking parameters, unsubscribe URLs) as plain text unless they were returned by workspace tools in this turn.
  - Never use such raw UUIDs as `recordId` targets for `update_record`.
  - If user intent is "create", still run deduplication first. Only switch to update when an existing record is resolved with strong identity confidence.
  - Only use update path when an existing target record is confirmed by prior tool evidence (search result or `get_record_by_id`).
  - If uncertain whether an ID is a real record, verify with `get_record_by_id` first; on miss, switch back to create/dedupe flow.

1. **Mandatory Deduplication Check**
   - Before creation, you **MUST** verify whether the entity already exists.
   - **Step 1 — cast the widest net first, on exact identifiers.** List every exact identifier you hold for the entity: email, LinkedIn/profile URL, website or domain, phone, organisation number, external/registry ID, customer ID. Issue **one** `search_records` call that matches on **any** of them, by giving each filter `condition: "or"` and the same `orGroup` label:
     ```json
     {
       "table": "contacts",
       "fieldFilters": [
         { "field": "emails", "operator": "in", "value": "person@acme.com", "orGroup": "identity" },
         { "field": "urls", "operator": "in", "value": "https://www.linkedin.com/in/person", "condition": "or", "orGroup": "identity" },
         { "field": "phones", "operator": "in", "value": "+4790000000", "condition": "or", "orGroup": "identity" }
       ]
     }
     ```
     Without `orGroup` and `condition` the filters are ANDed, which only matches a record holding **every** identifier — the opposite of what deduplication needs. One OR call also costs a single lookup instead of one per identifier.
   - **An exact-anchor hit IS the entity.** Update it. Do not create a second record because the name is spelled differently, abbreviated, initialised, or has since changed — a maiden name, "A. Smith" vs "Alice Smith", or a company's legal vs trading name are all the same entity when an anchor matches.
   - **Step 2 — only if the anchor search found nothing**, or you hold no exact identifier, fall back to name matching with `semantic_search_records`.
   - **Step 3 — create only after both come back empty.** An exact-anchor search returning nothing is the strongest evidence available that the entity is genuinely new, and creating is then the correct action, not a failure.
   - Beyond deduplication, use `search_records` for structured/exact filters (IDs, relation IDs, email/phone/url, numbers, dates, select values); never for free-text name matching.
   - Keep and reuse prior lookup results from the same turn. If the entity was already found earlier, treat it as existing and do not create it again.
   - If it exists, plan update.
   - If it does not exist, plan creation.

2. **Identify Target Record Path**
  - If exact `recordId` is provided, call `get_record_by_id` directly.
  - Do **not** run `search_records` with `field=id` before `get_record_by_id`.
  - If updating and full record context is missing, fetch it first with `get_record_by_id`.
   - If exact recordId is known, do not perform name-based deduplication first.

3. **Enrich When Strong External Identity Exists**
    - If a website/domain, work email, LinkedIn URL or Norwegian org number is provided or on the record, call `enrich` first. It matches the CRM record itself and saves deterministically: `save:"fill"` fills only empty fields; `save:"overwrite"` with `overwriteFields` only after the user confirmed the `diff`. Reuse the preview's `lookupId` when saving. Do not re-map its fields by hand with `update_record`.
   - Use enrichment as structured input, not as a final narrative blob.
     - Do not generate LinkedIn URLs. Use only values present in input/context.
   - Do not overwrite explicit user-provided values unless enrichment provides clearly newer/correct data.

4. **Field-First Mapping (CRITICAL)**
   - Map data to dedicated structured fields first (text/number/date/select/arrays/relation/user).
   - **Never dump all enrichment details into one description/textarea field.**
   - Use long text only for residual context that cannot be represented in structured fields.
   - If high-signal residual facts remain after structured mapping and a textarea-like field exists, write a concise residual summary (2-6 bullets). Do not leave residual notes empty in that case.

5. **Relation Resolution (CRITICAL)**
   - For relation targets in enrichment output (for example, current organization):
     1. search/deduplicate target records,
     2. if not found, create minimal related records,
     3. link by UUID in updates (or relation mapping token in same creation batch).
   - Prioritize **current/active** relations by default. Ignore historical items unless explicitly requested.
   - **MANDATORY RELATION GATE**:
     - If enrichment provides a current active related entity (for example current company) **and** the target table has a matching relation field to that entity table, you MUST resolve and write that relation.
    - If search finds no related record, you MUST call `record_creation` for that related entity before final `update_record`.
     - An update that only fills text fields while skipping required relation linking is incomplete.
   - **MATCH CONFIDENCE GATE (MANDATORY)**:
     - Do not link relation fields by semantic rank alone.
     - Do not treat prefix/substring similarity as sufficient evidence (for example "ACME" must not auto-link to "ACMEnergy" without additional corroboration).
     - Require corroboration before linking: either (1) one strong identity anchor (domain alignment, registry/external id, or canonical URL match) plus name evidence, or (2) at least two independent moderate signals (for example domain alignment + high semantic/name similarity).
     - If corroboration is missing, create a new minimal related record and link to that new record instead of reusing a weak candidate.

6. **Execute Writes**
  - Use `record_creation` for new records.
  - Use `update_record` for existing records.
   - If both are needed, create missing related records first, then update records that reference them.
  - Do not convert unsupported mass-intent requests into unbounded per-record loops. Require an explicitly supported operation path.

7. **Plan & Confirm**
   - Present plan naturally; avoid technical payload details.
   - If standard fields are missing (emails, phones, titles), ask concise advisory confirmation.

## B. Case Router (CHOOSE THE CORRECT WRITE PATTERN)

Use this decision logic to avoid conflicting write behavior:

1. **Create-only (all main entities are new)**
  - Use **one** `record_creation` call.
   - If parent+child are both new (for example organization + person), create them in the same batch, assign the parent a unique `_ref`, and use that reference in the child's relation field.

2. **Update-only (target record already exists and no new related records are needed)**
  - Use `update_record` only.
  - Do not call `record_creation`.

3. **Hybrid (target exists, but related record is missing)**
  - First create missing related record(s) with `record_creation`.
  - Then update the existing target with `update_record` using returned UUID(s).
   - Do not try to force this into one update payload.

4. **Exact recordId provided**
  - Start with `get_record_by_id` (never search-by-id first), then apply one of the above patterns.
  - If `get_record_by_id` does not confirm the record exists, do not call `update_record`; continue with create/hybrid flow.

5. **Explicit multi-entity delivery**
  - When the user explicitly requires multiple people, organisations, or person–organisation pairs, treat every named member as a required record outcome, not merely as supporting context for a primary record.
  - Create or update the organisation record for every required organisation as well as the contact record for every required person. A task's primary customer or a source item's business relevance does not reduce the requested record set.
  - When the user asks to link a task or other work item to all of those entities, include every resolved/created contact and organisation in the relation fields in the same creation payload when possible; verify the returned record includes those relations before answering.

### Dedupe Enforcement (MANDATORY)

- Correct sequence:
  1. One `search_records` call OR-ing together every exact identifier you hold (see A.1). Skip only if you hold none.
  2. If that returns nothing, `semantic_search_records` with the name query.
  3. If needed, refine the chosen candidate with `get_record_by_id` or structured filters.
- For company/person/entity **name** checks, do NOT use:
  - `search_records` + `operator: "eq"` on name/title/company fields.
- Do NOT skip step 1 because the name search already found something plausible. The anchor search is what distinguishes the right record from a namesake, and what finds the record whose name no longer matches.

**BAD (name-only dedupe, so the same person is created twice)**
```text
1. semantic_search_records "Aurora Lindqvist"  → weak hits, the record is filed as "A. Lindqvist-Berg"
2. record_creation → a second contact for a person already in the workspace
```

**GOOD (anchor first)**
```text
1. search_records, emails OR urls OR phones → finds "A. Lindqvist-Berg" on the LinkedIn URL
2. update_record on that record
```

### Weak Semantic Candidate Handling (MANDATORY)

- If top semantic hits are only loosely related, treat as **no confident match**.
- Do not auto-pick the first semantic hit for relation linking when evidence is only rank or partial-string similarity.
- Short or single-token names are high-risk for false positives; require corroborating identity anchors before linking.
- Prefer creating a new record from source value, then linking it, rather than mis-linking to an unrelated existing entity.

**BAD (name dedupe via strict eq)**
```json
{
  "table": "companies",
  "fieldFilters": [
    { "field": "name", "operator": "eq", "value": "Apple Inc" }
  ],
  "limit": 1
}
```

**GOOD (name dedupe via semantic first)**
```json
{
  "table": "companies",
  "query": "Apple Inc"
}
```

## C. Relation Linking Examples (CRITICAL)

**User Request**: "Create Acme Corp and Alice working there."

**Correct (Batch Creation in One Call)**
```json
{
  "tables": {
    "companies": [{ "_ref": "company_acme", "name": "Acme Corp" }],
    "contacts": [{ "_ref": "contact_alice", "first_name": "Alice", "companies": ["company_acme"], "emails": ["alice@acme.com"] }]
  },
  "deduplicateFields": {
    "companies": "name",
    "contacts": "emails"
  },
  "groupLinks": {
    "companies": "group-uuid-companies",
    "contacts": "group-uuid-contacts"
  }
}
```

**Incorrect (Multi-step and inefficient)**
```text
Step 1: create company
Step 2: search company to get ID
Step 3: create contact with that ID
```

Rules:
- Give each same-batch record that another record must link to a short, unique `_ref` string.
- Put that exact `_ref` string in relation fields. The tool resolves its target table and deduplication value from the workspace schema; do not repeat those details in the relation value.
- A display name is not a reference unless you deliberately used that exact string as the record's `_ref`.
- For linking to pre-existing records, use UUIDs.

## D. Enrich Update Examples (BAD vs GOOD)

**BAD (description dump, no structured mapping, no relation resolution)**
```json
{
  "people_table": {
    "recordId": "person-record-uuid",
    "data": {
      "<notes_textarea_field>": "- Senior role at Company A
- Location: ...
- Skills: ...
- Experience: ..."
    }
  }
}
```

Why this is bad:
- It skips structured field mapping.
- It does not resolve or link related entities.
- It stores high-value facts as unstructured text only.

**GOOD A (HYBRID: existing target + missing related entity)**
```text
1) search_records/semantic_search_records for the target person
2) enrich using an available LinkedIn profile URL
3) resolve related entity from current active experience:
   - search target relation table by dedup key
   - if missing, create minimal related record with record_creation
4) update_record on the person:
   - map title/location/contact arrays into structured fields
   - set relation field with resolved UUID(s)
   - keep textarea short and only for residual context not represented elsewhere
```

**BAD A (INCOMPLETE HYBRID)**
```text
1) enrich
2) update_record only with title/location/description
3) skip creating/linking current related entity
```

Why BAD A is invalid:
- It violates the mandatory relation gate.
- It leaves cross-table data fragmented despite clear relation evidence from enrichment.

**BAD B (over-correction: empty residual notes despite leftover facts)**
```text
1) map only a few structured fields
2) leave textarea/notes empty
3) ignore leftover high-signal context (summary, key skills/themes, important background)
```

Why BAD B is invalid:
- It loses useful context that does not cleanly fit structured fields.
- Field-first mapping does not mean dropping residual facts.

**GOOD A payload shape example (generic apiNames)**
```json
{
  "person_table_apiName": {
    "recordId": "person-record-uuid",
    "data": {
      "<role_title_field_apiName>": "Current role title",
      "<location_field_apiName>": "Current location",
      "<email_array_field_apiName>": ["person@example.com"],
      "<relation_field_to_related_table_apiName>": ["related-record-uuid"],
      "<notes_textarea_field_apiName>": "- Current summary only
- High-signal residual details only"
    }
  }
}
```

**GOOD B (CREATE-ONLY: both parent and child are new)**
```json
{
  "tables": {
    "parent_table_apiName": [{ "_ref": "parent_x", "<parent_dedup_field_apiName>": "Parent X" }],
    "child_table_apiName": [{
      "_ref": "child_y",
      "<child_primary_field_apiName>": "Child Y",
      "<relation_to_parent_field_apiName>": ["parent_x"]
    }]
  },
  "deduplicateFields": {
    "parent_table_apiName": "<parent_dedup_field_apiName>",
    "child_table_apiName": "<child_dedup_field_apiName>"
  },
  "groupLinks": {
    "parent_table_apiName": "group-uuid-parent",
    "child_table_apiName": "group-uuid-child"
  }
}
```

**GOOD C (balanced residual notes)**
```text
After structured mapping is done, keep residual notes concise:
- 2-6 bullets
- high-signal only
- no duplication of already-filled structured fields
- no full profile dump
```

## E. Field Formatting Rules

When calling `record_creation`, you must provide:
1. `tables`
2. `deduplicateFields` (every table in `tables` must have one)
3. `groupLinks` (every table in `tables` must have one)

- **TEXT fields**:
  - _email_: Ensure valid email format.
  - _phone_: Extract/normalize phone numbers.
  - _url_: Validate and extract URL values.
  - _textarea_: Break long text into bullet lines using "
- ". Never send one giant paragraph.
  - _textarea_: keep concise and non-duplicative with structured fields.
  - _textarea_: if residual high-signal facts exist, include them as a short summary instead of leaving empty.
  - _arrays_: use `[]` if empty. Never `null`.

- **NUMBER fields**:
  - Use raw numeric values only.

- **DATE fields**:
  - _date_: ISO date (e.g. `2024-12-14`).
  - _datetime_: ISO datetime (e.g. `2024-12-14T10:30:00Z`).
  - _time_: ISO time (e.g. `10:30:00`).

- **SELECT / MULTI_SELECT fields**:
  - Use exact choice values from workspace field options.
  - Never invent new option values.

- **RELATION fields**:
  - Existing related record: use UUID.
  - Same-batch related record creation: assign the target record a unique `_ref` and use that exact string.
  - Never guess IDs.

- **USER fields**:
  - Use UUID.

## F. Tool Requirements

- `record_creation`:
  - Provide `tables`, `deduplicateFields`, and `groupLinks`.
  - Every table in `tables` must have matching entries in both `deduplicateFields` and `groupLinks`.

- `update_record`:
  - Group payload by table apiName.
  - Per table provide:
    1. `recordId`
    2. `data`
  - Update only changed fields with high confidence.
  - You can update multiple tables in one call, but only one record per table.

## G. Data Safety Rules

- Respect existing non-null values unless the new data is a major contradiction or clearly newer.
- Never invent select options.
- Prefer structured fields over long narrative text for token efficiency.
