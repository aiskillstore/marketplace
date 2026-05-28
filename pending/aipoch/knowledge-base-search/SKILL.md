---
name: knowledge-base-search
description: Search and locate relevant content within a local knowledge base (files, indices, or PageIndex). Use when you need verifiable citations (file + page/paragraph) to support answers from local sources.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Knowledge Base Search

## When to Use
- You need to find specific facts, definitions, or procedures from a local knowledge base and return the exact source location.
- You must provide traceable citations (file path + page/paragraph/section) for audit, compliance, or review.
- You need to verify the original wording of a claim in the source document (quote-level validation).
- You want to compare how multiple local documents discuss the same topic and identify differences.
- You need to assemble supporting snippets for a report, FAQ, or internal knowledge response using only local materials.

## Key Features
- Supports multiple retrieval approaches: direct file search, index-based search, and PageIndex-style location mapping.
- Query strategy guidance: keyword splitting, synonym expansion, and optional filters (time range, file type, tags).
- Relevance-oriented result ranking and filtering to keep the most supportive evidence first.
- Outputs verifiable hit snippets with precise citation locations (file + page/paragraph/section when available).
- Enforces local-only boundaries: searches only within authorized directories and does not modify source content.

## Dependencies
- `glob` (>= 10.0.0): file path pattern matching
- `grep` (>= 3.11): in-file text searching
- Local knowledge base index files (one or more of: filename index, content index, vector index, PageIndex mapping)
- `assets/hit_list_template.csv`: standardized hit list output template
- Optional reference: `references/guide.md` (output formats, checklists, inspection points)

## Example Usage
The following example demonstrates an end-to-end local search workflow and produces a CSV hit list compatible with `assets/hit_list_template.csv`.

### Inputs
- Knowledge base root: `./kb/`
- Query: `How do we rotate API keys?`
- Filters: file types `md,pdf`, time range `2024-01-01..2026-12-31`

### Steps
1. **Confirm index and scope**
   - Ensure the search scope is limited to authorized paths (e.g., `./kb/`).
   - Identify available indices:
     - filename/content index (fast keyword search)
     - vector index (semantic retrieval)
     - PageIndex mapping (page/paragraph location resolution)

2. **Build the query**
   - Keywords: `rotate`, `API key`, `key rotation`
   - Synonyms/variants: `credential rotation`, `token rotation`, `regenerate key`
   - Filters:
     - file type: `*.md`, `*.pdf`
     - time range: `2024-01-01..2026-12-31` (if metadata exists)

3. **Execute search (local-only)**
   - Path discovery (example):
     - `glob("./kb/**/*.md")`
     - `glob("./kb/**/*.pdf")`
   - Content search (example):
     - `grep -RIn "API key\|key rotation\|rotate" ./kb/`

4. **Filter and rank results**
   - Keep hits that directly answer the question (procedure, policy, steps, constraints).
   - Rank by:
     - term proximity (e.g., “rotate” near “API key”)
     - section relevance (e.g., “Security”, “Credentials”, “Operations”)
     - coverage (hits that include prerequisites + steps + verification)

5. **Output citations and hit list**
   - For each hit, output:
     - `file_path`
     - `location` (page number for PDFs; heading/paragraph index for Markdown; PageIndex if available)
     - `snippet` (verbatim excerpt supporting the conclusion)
     - `notes` (why it is relevant; any assumptions)
   - Save as `hit_list.csv` using `assets/hit_list_template.csv` columns.

### Example Output (CSV rows)
```csv
file_path,location,snippet,relevance_score,notes
kb/security/credential_policy.pdf,page 12,"API keys must be rotated every 90 days... Rotation requires...",0.92,"Direct policy + rotation interval + procedure reference."
kb/runbooks/api_key_rotation.md,section 'Procedure' ¶3,"To rotate an API key: (1) create a new key... (2) update services... (3) revoke old key...",0.89,"Step-by-step operational runbook."
kb/audit/controls.md,heading 'Key Management' ¶2,"Evidence of rotation includes change tickets and key revocation logs...",0.81,"Provides verification/evidence requirements."
```

## Implementation Details
### Retrieval Workflow
1. **Index confirmation**
   - Determine knowledge base root paths and last update time (if available).
   - Detect which indices exist:
     - filename index: quick narrowing by file names
     - content index: inverted index / grep-like scanning
     - vector index: semantic similarity retrieval
     - PageIndex: mapping from document offsets to page/paragraph identifiers

2. **Query strategy**
   - Tokenize the question into:
     - core entities (e.g., “API key”)
     - actions (e.g., “rotate”, “revoke”, “regenerate”)
     - constraints (e.g., “every 90 days”, “approval required”)
   - Expand with synonyms and variants.
   - Apply filters when metadata exists:
     - time range
     - file type
     - tags/collections

3. **Result filtering and ranking**
   - Remove low-signal hits (navigation, boilerplate, unrelated mentions).
   - Rank by a weighted score (example):
     - **Keyword match** (exact phrase > partial): 0.45
     - **Proximity** (terms close together): 0.20
     - **Section importance** (titles like “Procedure/Policy”): 0.20
     - **Coverage** (answers include steps + constraints + verification): 0.15
   - Keep the original text snippet verbatim for verification.

4. **Citation and location resolution**
   - Markdown/text:
     - use heading + paragraph index (or line range) as the primary locator
   - PDF:
     - use page number; optionally include bounding text around the hit
   - PageIndex (if present):
     - map internal offsets to stable `page/paragraph` identifiers

### Constraints and Limitations
- Search only within user-authorized local directories.
- Do not modify source documents.
- Do not execute scripts or arbitrary code.
- Do not access network resources or external APIs.
- If indices are missing/corrupted, fall back to direct file scanning; if scanning is not possible, report the limitation and required remediation (re-indexing).