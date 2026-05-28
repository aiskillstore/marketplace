---
name: fda-guideline-search
description: Search FDA industry guidelines by therapeutic area or topic.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# FDA Guideline Search

Quickly search and retrieve FDA industry guidelines by therapeutic area.

## When to Use

- Use this skill when the task needs Search FDA industry guidelines by therapeutic area or topic.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Search FDA industry guidelines by therapeutic area or topic.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/fda-guideline-search"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Features

- Search FDA guidelines by therapeutic area (oncology, cardiology, neurology, etc.)
- Filter by document type (draft, final, ICH guidelines)
- Download and cache guideline documents
- Search within document content

## Usage

### Python Script

```text
python scripts/main.py --area <therapeutic_area> [options]
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--area` | string | - | Yes | Therapeutic area (oncology, cardiology, rare-disease) |
| `--type` | string | all | No | Document type (all, draft, final, ich) |
| `--year` | string | - | No | Filter by year (e.g., 2023, 2020-2024) |
| `--download` | flag | false | No | Download PDF to local cache |
| `--search` | string | - | No | Search term within documents |
| `--limit` | int | 20 | No | Max results (1-100) |

### Examples

```text

# Search oncology guidelines
python scripts/main.py --area oncology

# Search for rare disease draft guidelines
python scripts/main.py --area "rare disease" --type draft

# Search with download
python scripts/main.py --area cardiology --download --limit 10
```

## Technical Details

- **Source**: FDA CDER/CBER Guidance Documents Database
- **API**: FDA Open Data / Web scraping with rate limiting
- **Cache**: Local PDF storage in `references/cache/`
- **Difficulty**: Medium

## Output Format

Results are returned as structured JSON:

```json
{
  "query": {
    "area": "oncology",
    "type": "all",
    "limit": 20
  },
  "total_found": 45,
  "guidelines": [
    {
      "title": "Clinical Trial Endpoints for the Approval of Cancer Drugs...",
      "document_number": "FDA-2020-D-0623",
      "issue_date": "2023-03-15",
      "type": "Final",
      "therapeutic_area": "Oncology",
      "pdf_url": "https://www.fda.gov/.../guidance.pdf",
      "local_path": "references/cache/..."
    }
  ]
}
```

## References

- [FDA Search Strategy](./references/search-strategy.md)
- [Therapeutic Area Mappings](./references/area-mappings.json)
- [FDA API Documentation](./references/fda-api-notes.md)

## Limitations

- Rate limited to 10 requests/minute to respect FDA servers
- Some historical documents may not have digital PDFs
- ICH guidelines require separate search scope

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture

## Prerequisites

No additional Python packages required.

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `fda-guideline-search` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `fda-guideline-search` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
