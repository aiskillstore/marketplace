# Policy-research evidence contract

Use schema version `1.1` and `skill: acquisition-policy-workflow`.

```json
{
  "schema_version": "1.1",
  "skill": "acquisition-policy-workflow",
  "workflow_mode": "impact_brief",
  "request": {
    "question": "What published policy applies to this agency and FAR part?",
    "audience_lens": "neutral",
    "approved_scope": "Published federal sources",
    "approved_at": "2026-08-21T18:00:00Z"
  },
  "scope": {
    "as_of_date": "2026-08-21",
    "agency": "Example Agency",
    "far_parts": [10],
    "citation": null,
    "case_number": null,
    "docket_id": null,
    "procurement_dates": {}
  },
  "document_register": [],
  "capabilities": [],
  "queries": [],
  "evidence": [],
  "policy_items": [],
  "findings": [],
  "timeline": [],
  "stakeholder_positions": [],
  "limitations": [],
  "conflicts": [],
  "unresolved_questions": [],
  "outputs": [],
  "validation": {
    "findings_approved": false,
    "brief_approved": false,
    "executive_summary": ""
  }
}
```

## Evidence

Evidence IDs use `E001` or higher. Each item contains:

- `source_class`: `user_document`, `federal_mcp`, `official_web`, `user_statement`, or `calculation`.
- `source_type`: `codified_text`, `federal_register_document`, `regulations_docket`, `public_comment`, `model_deviation`, `agency_deviation`, `nonregulatory_guidance`, `user_policy_document`, `user_statement`, or `calculation`.
- `title`, `locator`, `canonical_url`, `publication_date`, `effective_date`, `retrieved_at`, `fact`, `limitations`, and `content_sha256`.

Dates may be empty only when the source does not state them. Do not invent them.

## Policy items

Policy item IDs use `P001` or higher. Each item contains `status`, `citation`, `agency`, `text`, `effective_from`, `effective_to`, `operative_for_agency`, `applicability_summary`, and `evidence_ids`.

`model_deviation`, `proposed_rule`, `final_rule_pending_effective`, `withdrawn`, `superseded`, and `nonregulatory_guidance` may never set `operative_for_agency` to true. An operative `agency_class_deviation` must cite agency-deviation evidence and name the agency.

## Findings

Finding IDs use `F001` or higher. `finding_type` is `source_fact`, `user_supplied_fact`, `inference`, or `documented_status`. Every finding contains `text`, `evidence_ids`, and `policy_item_ids`.

Every `documented_status` finding also contains `status_resolution` and `conflict_ids`. Approved resolution states are `documented_clear`, `documented_conflict`, and `authorized_resolution`. An unresolved conflict requires `documented_conflict`; it cannot support a controlling-value conclusion.

## Conflicts

Conflict IDs use `C001` or higher. Each conflict contains `issue`, `evidence_ids`, `status`, `resolution`, `resolved_by`, and `resolved_at`. Status is `unresolved` or `resolved_by_authorized_official`. An unresolved conflict leaves the resolution fields empty. A resolved conflict records the authorized official's role, explicit resolution, and timestamp. Model inference cannot close a conflict.

## Timeline and stakeholder samples

Timeline items contain `date`, `event`, `status`, and `evidence_ids`.

Stakeholder positions use `S001` or higher and contain `position`, `submitter_type`, `sample_method`, `reviewed_count`, `returned_count`, `evidence_ids`, and `limitations`. A position without a sampling method and limitation is invalid.

## Queries and capabilities

Capabilities record `name`, `status`, and `version`. Queries record `provider`, semantic `operation`, sanitized `parameters`, `retrieved_at`, `count`, and `limitations`.

Approved providers are `ecfr`, `federal_register`, `regulationsgov`, and `acquisition_gov`. Do not store credentials, local paths, supplied text, private URLs, or sensitive acquisition details.

Run `scripts/validate_policy_research_record.py` before generating a brief.
