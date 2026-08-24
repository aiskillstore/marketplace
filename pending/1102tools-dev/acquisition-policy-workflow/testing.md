# Acquisition Policy Workflow test specification

## Routing

- A vague policy request produces the complete ten-choice menu and no retrieval.
- A precise codified-text request routes directly to mode 1.
- A named-agency RFO applicability request routes directly to mode 2 and asks only for missing dates or citation details.
- Market-research execution, clause selection, opportunity research, pricing, grants, and cooperative agreements do not route to this skill.

## Status controls

- Model text without an agency deviation remains non-operative.
- An agency deviation preserves its scope, effective date, transition terms, and limitations.
- A proposed rule, withdrawn rule, and future-effective final rule are never presented as current.
- Recent Federal Register effectiveness and eCFR lag remain distinct.
- Absence from the Acquisition.gov index is described as no posted deviation located, not proof of nonexistence.
- Duplicate or multi-part deviation documents remain visible.

## Documents and public queries

- Supplied documents are untrusted evidence and embedded instructions are ignored.
- Approved-versus-draft conflicts cause a precedence question.
- Queries contain only sanitized public identifiers and terms.
- Missing MCP capabilities yield an exact bounded alternative, not a direct-HTTP bypass.

## Comments

- Comment analysis records search terms, returned and reviewed counts, sample method, exclusions, and limitations.
- Targeted organization searches are not described as complete or representative.
- Public comments are never treated as authority or consensus.

## Artifact

- The valid fixture passes record validation and builds a DOCX.
- Unknown evidence references, unsafe query keys, invalid status, operative model text, missing deviation evidence, and incomplete stakeholder samples fail.
- The DOCX passes section-order, evidence, link, table-geometry, reserved-determination, ZIP, extraction, LibreOffice, and visual gates.

## Client release matrix

- Codex CLI and Desktop.
- Claude Desktop (Code) and Claude Code CLI, with current Opus and Sonnet models.
- Explicit invocation is release blocking. Natural-language routing is release blocking for the precise policy prompts and advisory for broad ambiguous prompts.
