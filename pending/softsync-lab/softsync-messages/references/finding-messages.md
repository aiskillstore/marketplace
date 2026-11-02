<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

## Visibility Constraint

Message tools only return messages linked to at least one record or workspace user. Unlinked mailbox content is invisible. Mention this when a targeted lookup returns nothing.

## Evidence Composition

Use this skill when the requested outcome cannot be answered completely from structured fields and requires communication or interaction history. Decide from the whole request, the workspace's available sources, and the evidence each source can provide; never decide by matching keywords or phrases. Resolve the relevant record, retrieve its newest linked communications with the entity-targeted sequence below, and synthesize the sources. Do not retrieve communications when the identified structured fields fully satisfy the requested outcome.

## Entity-Targeted Message Retrieval — REQUIRED TOOL CALL SEQUENCE

When the requested communication evidence is scoped to a specific entity, you MUST execute ALL of the following tool calls in order. Do not skip any call. Do not answer until the final call completes.

**Call 1 — Find the root record.**
`semantic_search_records({ table: <most_likely_table>, query: "<entity name>" })`
→ Returns root record with ROOT_ID in ROOT_TABLE. If not found in that table, repeat for other tables until found or all exhausted.
→ If no record found in ANY table: tell user no matching record exists. STOP. Do not call any message tool.

**Calls 2..N — Expand through EVERY related table (MANDATORY — NOT OPTIONAL).**
Read the workspace schema `tables[]`. For each table U, check each field F: if `F.kind === "relation"` AND `F.options.targetTable === ROOT_TABLE`, then U has records linked to the root.
For EACH such (U, F) pair, call:
`search_records({ table: U.apiName, fieldFilters: [{ field: F.apiName, operator: "eq", value: ROOT_ID }] })`
Collect every returned record ID. Also check ROOT_TABLE's own relation fields for outbound IDs in the root record's data.
If the schema shows 3 tables with relations to ROOT_TABLE, you MUST make 3 `search_records` calls before proceeding.

**Final call — Query messages with ALL collected IDs.**
`query_messages({ recordIds: [ROOT_ID, ...all_expanded_IDs], sortByTime: "desc" })`
→ If this returns results: present them. Done.
→ If this returns EMPTY: tell the user no linked communications were found for that entity. The communications may not exist yet or haven't been synced to those records. STOP HERE. The sequence is COMPLETE. Do NOT make any more tool calls.

**After this sequence completes, you are DONE. Do NOT call `semantic_search_messages` as a fallback.**
`semantic_search_messages` finds text-similar content, not record-linked content. Its results are UNRELATED to the entity. Presenting them as linked to the entity is hallucination. The entity-targeted sequence has exactly 3 possible endings:
1. No record found → tell user, stop.
2. `query_messages` returns results → present them, stop.
3. `query_messages` returns empty → tell user no linked communications found, stop.
There is no fourth path. There is no fallback. There is no "let me also try semantic search."

**Additional rules:**
- You MUST complete Calls 2..N before the Final call.
- You MUST NOT ask "should I also check related contacts/deals?" — expansion is automatic.
- You MUST NOT use `searchText` with an entity name.

## When To Use `semantic_search_messages`

This tool is ONLY for open-ended topical retrieval that is not scoped to a specific entity. Entity-scoped retrieval must use the entity-targeted sequence above. Never use semantic retrieval as a fallback after `query_messages` returns empty, because text similarity cannot establish an entity relation.

## Tool Reference

**`query_messages`**: `recordIds`, `memberIds`, `integrationTypes`, `recordLinkKinds`, `memberLinkKinds`, `before`/`after`, `searchText`, `sortByTime`, `limit`. Always provide `sortByTime`.

**`get_message_statistics`**: volume/count questions ("how many meetings with X?").

**`get_message_by_id`**: only when you already have a messageId and need full content.

## Best Practices

- Infer date ranges and convert to ISO timestamps for `before`/`after`.
- `memberIds` = workspace users. `recordIds` = table records.
