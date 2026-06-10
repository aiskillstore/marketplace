---
name: context-receipts
description: Emit privacy-safe receipts for context selection, deferral, hydration, compaction, pruning, delegation, usage attribution, and boundary handoffs.
---

# Context Receipts

Use this skill when an agent workflow claims to save context by selecting, deferring, hydrating, summarizing, compacting, pruning, delegating, attributing usage, or isolating context.

The job is not to log the private content. The job is to emit a small receipt that lets a reviewer answer:

> what crossed the context boundary, what stayed out, and what audit gap remains?

## Privacy defaults

Never include raw prompts, raw tool schemas, raw tool arguments, raw tool results, raw skill bodies, memory bodies, secrets, customer names, or full transcripts in the receipt.

Prefer:

- stable ids or hashed ids;
- counts and token/line buckets;
- categorical reasons;
- explicit booleans for raw content copied/not copied;
- before/after context budget buckets;
- an `audit_gap` field when the receipt proves routing but not semantic correctness.

## 60-second Tool Search smoke

For MCP Tool Search, lazy tool loading, or progressive disclosure, emit enough evidence to answer these seven checks:

1. **Index-only startup:** did the session load a compact tool/server index instead of all full schemas?
2. **Search/routing:** what hashed query/category or routing reason selected candidate tools?
3. **Hydration:** which full tool definition was loaded, why, and how many definitions stayed suppressed?
4. **Call:** which server/tool id was invoked, with argument/result redaction status and success/error status?
5. **Boundary:** if a manager subagent or child agent was used, did raw child output return to the parent?
6. **Budget:** what were the startup and post-hydration context-token buckets?
7. **Audit gap:** what is not proven, such as whether the selected tool was semantically optimal?

Minimal JSONL event names:

```jsonl
{"event":"mcp.tool_index.loaded","loaded_server_count":12,"loaded_tool_index_count":84,"full_schema_count":0,"suppressed_tool_count":84,"raw_schema_copied":false,"startup_token_bucket":"lt_1k"}
{"event":"mcp.tool_search.performed","query_hash":"sha256:...","query_category":"repo_search","candidate_tool_count":5,"selected_tool_id":"github.search_code","raw_query_copied":false}
{"event":"mcp.tool_definition.loaded","tool_id":"github.search_code","hydrate_reason":"selected_after_tool_search","suppressed_tool_count":83,"definition_token_bucket":"1k_2k","raw_schema_copied":false}
{"event":"mcp.tool_call.completed","tool_id":"github.search_code","args_hash":"sha256:...","result_token_bucket":"2k_4k","raw_args_copied":false,"raw_result_copied":false,"status":"ok"}
```

## Runtime tool-surface diff smoke

For MCP dynamic discovery, gateways, admin/Purview-style audit trails, or runtime tool catalogs, separate discovery from activation:

- which platform/gateway/audit sink observed the runtime catalog change;
- which catalog/version/hash was active before and after discovery;
- which tools were discovered, activated, withheld, or blocked;
- which validation outcome applied, such as `accepted`, `blocked_by_rai`, `blocked_by_xpia`, `schema_invalid`, or `entitlement_filtered`;
- whether only low-cardinality ids, hashes, counts, and outcome codes entered the receipt;
- the audit gap, such as not proving the tool was semantically right for the user task.

Minimal JSON shape:

```json
{
  "receipt_type": "pluribus.mcp_tool_surface_diff_receipt.v1",
  "runtime_discovery": {
    "trigger": "turn_start|admin_refresh|tool_search|manual_refresh",
    "before_catalog_hash": "sha256:...",
    "after_catalog_hash": "sha256:..."
  },
  "summary": {
    "discovered_count": 3,
    "activated_count": 1,
    "withheld_count": 1,
    "blocked_count": 1
  },
  "privacy": {
    "raw_schemas_copied": false,
    "raw_prompts_copied": false,
    "raw_results_copied": false
  },
  "audit_gap": "proves tool-surface boundary, not semantic usefulness"
}
```

## Context attention smoke

For GraphRAG, memory, code search, transcript review, or baseline-first workflows, separate retrieval from attention:

- which required context ids were selected or retrieved;
- where they were delivered, such as prompt, tool result, memory result, subagent packet, or file read;
- which ids were acknowledged before planning;
- which ids were cited before edits/tool calls;
- what the agent must stop on if a required id is missing;
- whether raw docs, prompts, results, paths, customer text, and full transcript snippets stayed out of the receipt.

Minimal JSON shape:

```json
{
  "receipt_type": "pluribus.context_attention_receipt.v1",
  "required_context_ids": ["ctx:auth-boundary", "ctx:migration-plan"],
  "delivered_context_ids": ["ctx:auth-boundary", "ctx:migration-plan"],
  "acknowledged_before_plan_ids": ["ctx:auth-boundary", "ctx:migration-plan"],
  "cited_before_edit_ids": ["ctx:auth-boundary"],
  "missing_context_stop": "stop_before_edit",
  "privacy": {
    "raw_context_copied": false,
    "raw_transcript_copied": false
  },
  "audit_gap": "proves required context was acknowledged/cited, not that the edit is correct"
}
```

## Skill / prompt context smoke

For skills, rules, AGENTS.md overlays, or instruction files, answer:

- which index/listing entered the session;
- which full skill/rule/instruction body was selected;
- which candidates were suppressed and why;
- whether the body was loaded at session start, after a search, or after an explicit command;
- source hash, delivered hash, and canonical form when available;
- whether the skill/instruction text was copied into the receipt.

Minimal event names:

- `context.skill.registry.index.loaded`
- `context.skill.registry.skill.read`
- `context.skill.registry.skill.injected`
- `context.input.loaded`
- `context.input.candidate_suppressed`

## Per-agent MCP injection smoke

For role-specific subagents or per-agent MCP configs, prove the policy boundary before debugging model quality:

- which subagent role/session requested tools;
- which MCP servers were available to that role;
- which servers were explicitly excluded before boot;
- whether startup loaded full schemas or only a compact index;
- how many tool definitions stayed deferred/suppressed; and
- the startup token bucket after policy was applied.

Minimal JSONL event names:

```jsonl
{"event":"subagent.mcp_policy.applied","subagent_role":"testing","available_server_count":2,"available_servers_hash":"sha256:...","excluded_server_count":5,"excluded_servers_hash":"sha256:...","policy_source":"role_config","raw_server_names_copied":false}
{"event":"subagent.context_boot.evaluated","subagent_role":"testing","loaded_tool_definition_count":0,"deferred_tool_definition_count":48,"startup_token_bucket":"50k_75k","raw_schema_copied":false,"audit_gap":"proves injection boundary, not tool relevance"}
```

## ToolSearch propagation smoke

For subagents that should inherit MCP through `ToolSearch`, distinguish policy, declaration, and runtime filtering:

- did the parent/orchestrator intend to expose MCP or exclude it for this subagent?
- was the subagent spawned immediately or after parent tool calls/orchestration work?
- was the `tools:` declaration wildcard, explicit include, or exclusion style?
- was `ToolSearch` declared and was it actually exposed in the subagent tool surface?
- did MCP servers/tool definitions stay deferred, or did the channel collapse to zero?
- was the agent registry loaded at session boot, making newly added agent files invisible until restart?

Minimal JSONL event names:

```jsonl
{"event":"subagent.toolsearch.propagation.evaluated","spawn_path":"Task","tools_declaration_shape":"enumerated_include","toolsearch_declared":false,"toolsearch_exposed":false,"mcp_servers_available_bucket":"0","deferred_tool_definitions_bucket":"0","filtered_by":"frontmatter_tools_policy_or_runtime_filter","raw_tool_schemas_copied":false}
{"event":"subagent.toolsearch.matrix.completed","tested_axis":"tools_frontmatter_shape","audit_gap":"proves ToolSearch exposure, not semantic tool relevance or runtime call success"}
```

## Retrieval / code-search smoke

For semantic code search, repo RAG, or MCP tools such as Claude Context, separate "search returned" from "agent context loaded":

- which index snapshot/version was used, without raw local codebase paths;
- what query/category/filter identity selected the candidates, without raw query text;
- which result ids/chunk hashes were returned, with rank, score bucket, stale flag, duplicate marker, path hash/extension, and range bucket;
- which returned chunks were actually loaded into the agent context;
- which chunks were suppressed as duplicate, stale, clipped, policy-blocked, or over budget;
- whether raw code, raw prompts, raw paths, customer names, URLs, secrets, and ticket text stayed out of the receipt;
- the audit gap: this proves retrieval/loading boundaries, not semantic answer quality.

Minimal JSONL event names:

```jsonl
{"event":"code.index.snapshot.used","snapshot_id_hash":"sha256:...","codebase_path_hash":"sha256:...","indexed_chunk_count_bucket":"over_1k","raw_codebase_path_copied":false}
{"event":"code.search.performed","query_hash":"sha256:...","query_category":"auth_debug","candidate_count_bucket":"over_1k","raw_query_copied":false}
{"event":"code.search.result.returned","rank":1,"chunk_id_hash":"sha256:...","chunk_text_hash":"sha256:...","path_hash":"sha256:...","score_bucket":"high","stale":false,"raw_code_copied":false}
{"event":"context.input.loaded","kind":"retrieved_code_chunks","loaded_chunk_count":3,"suppressed_chunk_count":2,"suppression_reasons":["duplicate","stale_snapshot_chunk"],"raw_code_copied":false}
```

## Usage attribution smoke

For `/usage`, `/context`, `/doctor`, or other context-budget breakdowns, map each displayed category to evidence that can be reviewed without exposing private content:

- what measurement window was used;
- which categories were attributed, such as skills, subagents, plugins, MCP servers, rules, memory, or project files;
- which components were loaded, deferred, hydrated, suppressed, pruned, or rolled back;
- before/after or current token/cost buckets by category;
- whether raw skill bodies, prompts, MCP schemas, tool outputs, and file paths were excluded;
- the remaining audit gap, such as not proving semantic usefulness of a high-cost component.

Minimal JSONL event names:

```jsonl
{"event":"context.usage.window.measured","window":"current_session","total_token_bucket":"100k_150k","raw_prompts_copied":false}
{"event":"context.usage.category.attributed","category":"mcp_server","component_hash":"sha256:...","loaded_token_bucket":"10k_25k","deferred_definition_count":42,"hydrated_definition_count":3,"raw_schema_copied":false}
{"event":"context.usage.breakdown.completed","categories":["skills","subagents","plugins","mcp_server"],"audit_gap":"proves attribution buckets, not whether each component was necessary"}
```

## Pruning / compaction smoke

For context-cleaning, pruning, compaction, or doctor/guard tools, answer:

- what prescription/trigger started the run;
- which strategies changed context and which candidates were protected;
- before/after token and byte buckets;
- whether summaries, behavioral digests, team messages, and backups were preserved;
- whether private transcript text, raw tool output, file paths, secrets, and customer text were excluded from the receipt;
- the remaining audit gap, such as not proving semantic quality of the pruned text.

Minimal JSONL event names:

```jsonl
{"event":"context.prune.started","prescription":"balanced","trigger":"manual_dry_run","before_token_bucket":"150k_200k","raw_transcript_copied":false}
{"event":"context.prune.strategy.evaluated","strategy":"tool-output-trim","candidate_bucket":"10_25","changed_bucket":"5_10","protected_bucket":"1_5","raw_tool_output_copied":false}
{"event":"context.prune.completed","after_token_bucket":"75k_100k","backup_verified":true,"protected_summary_count":2,"raw_text_copied":false,"audit_gap":"proves pruning/protection counts, not semantic disposability"}
```

For failed compaction, also prove transaction safety:

- did the summary call succeed, fail, or timeout;
- was a candidate summary validated before any swap;
- did the harness commit a context swap or preserve the original context;
- were deferred-tool registries and system-reminder queues restored on rollback;
- did stale system reminders/tool results replay as fresh state;
- was post-token metadata recorded as success even though summary failed.

Minimal JSONL event names:

```jsonl
{"event":"context.compaction.summary.attempted","summary_call_status":"failed_rate_limited","candidate_summary_available":false,"raw_error_copied":false}
{"event":"context.compaction.rollback.completed","swap_committed":false,"original_context_preserved":true,"deferred_tool_registry_restored":true,"system_reminder_queue_restored":true,"replayed_system_reminder_count":0}
{"event":"context.compaction.transaction.completed","status":"rolled_back","authoritative_state":"pre_compaction_context","post_tokens_recorded_as_success":false,"raw_context_copied":false}
```

## Subagent / manager boundary smoke

For subagents, manager agents, or child workers, answer:

- what task was delegated, by category and hashed objective;
- what large output was captured by the child, as line/token buckets;
- what bounded summary returned to the parent;
- whether raw child output, tool results, or MCP schemas entered the parent context;
- the remaining audit gap.

Minimal event names:

- `subagent.delegation.requested`
- `subagent.tool_output.captured`
- `subagent.summary.returned`
- `parent.context_budget.evaluated`

## Good receipt test

A receipt is useful if a maintainer can debug one of these failures without seeing private content:

- the agent never found the right tool/skill;
- the full definition loaded too early;
- too many definitions stayed in context;
- a child/subagent saved no budget because raw output returned to the parent;
- compaction/pruning happened but no one can prove what was changed, protected, backed up, summarized, or dropped.

A receipt is not enough if it only says “Tool Search enabled” or “used subagent”. It must prove the boundary behavior.
