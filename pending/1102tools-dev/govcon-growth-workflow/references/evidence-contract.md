# Research evidence contract

Market Research uses schema version `1.2`; GovCon Growth retains schema `1.1`. Both use these shared top-level fields. The example below is the Market Research artifact form:

```json
{
  "schema_version": "1.2",
  "skill": "market-research-workflow",
  "workflow_mode": "complete_report",
  "question": "What market evidence informs this acquisition?",
  "scope": {"as_of_date": "2026-08-21", "agency": null, "naics": [], "psc": [], "period": null},
  "document_register": [],
  "user_context": [],
  "assumptions": [],
  "web_research": {
    "mode": "no_public_web",
    "approved": true,
    "approved_at": "2026-08-21T18:00:00Z",
    "disclosure_acknowledged": true,
    "planned_providers": [],
    "providers_used": [],
    "fallback_events": []
  },
  "queries": [],
  "evidence": [],
  "findings": [],
  "inferences": [],
  "user_decisions": [],
  "conflicts": [],
  "unresolved_questions": [],
  "outputs": [],
  "validation": {
    "findings_approved": false,
    "findings_approved_at": "",
    "decisions_approved": false,
    "decisions_approved_at": "",
    "unresolved_items_disposition_approved": false,
    "unresolved_items_disposition_approved_at": ""
  }
}
```

Every evidence item has a stable ID such as `E001`, source class, title, locator or operation, retrieval time, as-of date when known, concise fact, and limitations. Source classes are `document`, `federal_mcp`, `official_web`, `other_web`, `user_statement`, and `calculation`.

Every source call in `queries` has a stable ID such as `Q001` and records provider, semantic operation, sanitized parameters, the timestamp recorded when that call completed, count or coverage, and limitations. For GovCon Growth, evidence from `federal_mcp`, `official_web`, or `other_web` sources includes `source_call_ids`; its `retrieved_at` must match one of the linked source-call timestamps. Report-build time is never substituted for retrieval time.

Every finding has a stable ID such as `F001`, text, and one or more supporting evidence IDs. Inferences have their own IDs, cite evidence IDs, and state the reasoning and uncertainty. Queries record provider, semantic operation, sanitized parameters, retrieval time, count or coverage, and limitations. The `web_research` object records explicit approval, planned and used providers, and any approved fallback. Never store credentials or sensitive source text.

Every decision string begins with a stable identifier such as `D001:`. Every unresolved-question string begins with a stable identifier such as `U001:`. For a complete Market Research report, `validation` records explicit findings approval, decision approval, and unresolved-item-disposition approval with UTC timestamps. A deferred unresolved item is valid only when its disposition explicitly carries it forward as a limitation.

Market Research schema `1.1` records remain readable for archive review and refresh intake. They must be migrated to `1.2` before a formal report can be generated.

Use `scripts/validate_research_record.py` before generating an artifact. The validator rejects duplicate IDs, unknown evidence references, missing required fields, unapproved enumerations, secrets, and unsafe query keys.
