---
name: retraction-watcher
description: Automatically scan document reference lists and check against Retraction.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Retraction Watcher

A specialized skill for identifying retracted, corrected, or questionable papers in academic reference lists before they compromise research integrity.

## When to Use

- Use this skill when the task needs Automatically scan document reference lists and check against Retraction.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Automatically scan document reference lists and check against Retraction.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `pypdf2`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```python

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

## Purpose

Academic misconduct and errors can lead to paper retractions. Citing retracted work undermines research credibility. This skill:
- Scans reference lists from manuscripts, papers, or bibliographies
- Cross-checks citations against Retraction Watch and other retraction databases
- Identifies papers with retraction notices, expressions of concern, or corrections
- Provides detailed reports with retraction reasons and dates

## Trigger Conditions

Activate this skill when:
1. User provides a document with references and asks to check for retractions
2. User explicitly requests "check my references" or "scan for retracted papers"
3. User submits a bibliography or reference list for verification
4. Pre-submission manuscript review is requested
5. User wants to verify citation integrity

## Input Format

Accepted inputs:
- PDF files (manuscripts, papers, theses)
- Plain text files (.txt, .bib, .ris)
- Raw text containing reference lists
- URLs to papers or reference lists
- Clipboard content with citations

## Output Format

### Report Header
```
🔍 RETRACTION WATCH REPORT
Documents Scanned: [N]
References Found: [N]
Check Date: [YYYY-MM-DD]
```

### Status Categories

**🔴 RETRACTED** - Paper has been officially retracted
- Reason for retraction
- Retraction date
- Original DOI/PMID
- Recommended action: Remove citation

**🟡 EXPRESSION OF CONCERN** - Journal has raised concerns
- Nature of concern
- Date issued
- Recommended action: Verify current status, consider alternative sources

**🟠 CORRECTED** - Paper has published corrections/errata
- Correction details
- Date of correction
- Recommended action: Check if correction affects cited claims

**🟢 CLEAR** - No retraction issues found

## Technical Approach

### Citation Parsing Strategy
1. **Format Detection**: Identify citation style (APA, MLA, Vancouver, Chicago, etc.)
2. **Field Extraction**: Parse DOI, PMID, title, authors, journal, year
3. **Identifier Resolution**: Normalize DOIs (remove prefixes, validate format)
4. **Title Matching**: Extract article titles for fuzzy matching

### Database Checking
1. **Retraction Watch Database** - Primary source for retraction data
2. **Crossref API** - Retraction metadata via "update-type: retraction"
3. **PubMed API** - Retraction notices via publication type filters
4. **Open Retractions** - Aggregated retraction data

### Matching Algorithm
- **Exact Match**: DOI/PMID exact match (highest confidence)
- **Title Match**: Normalized title comparison (90%+ similarity threshold)
- **Author + Year**: Secondary verification for ambiguous matches
- **Fuzzy Matching**: Handle minor title variations and typos

## Difficulty Level

**Medium-High** - Requires:
- Robust citation parsing across multiple formats
- API integration with retraction databases
- Handling of partial/incomplete citation data
- Fuzzy matching for title-based lookups
- Rate limiting and caching for API calls

## Quality Criteria

A successful scan must:
- [ ] Parse >90% of citations correctly from standard formats
- [ ] Achieve <1% false positive rate on retraction detection
- [ ] Provide actionable recommendations for each flagged citation
- [ ] Handle missing DOIs/PMIDs via title matching fallback
- [ ] Complete checks within reasonable time (<30s for 50 references)
- [ ] Preserve reference numbering for easy identification

## Limitations

- Requires internet connection for database lookups
- Rate limits may apply to free API tiers
- Very recent retractions (<48 hours) may not be indexed
- Title-only matching may produce false positives with similar titles
- Non-English papers may have limited coverage
- Preprint citations (arXiv, bioRxiv) typically not tracked for retractions

## Check a PDF manuscript
python scripts/main.py --input manuscript.pdf --format detailed

## Check a BibTeX file
python scripts/main.py --input references.bib --output report.txt

## Check raw text
python scripts/main.py --text "[paste references here]"

## Quick check with summary only
python scripts/main.py --input paper.pdf --format summary
```

## Data Sources

- **Retraction Watch Database**: https://retractionwatch.com/
- **Crossref API**: https://api.crossref.org/
- **PubMed E-utilities**: https://www.ncbi.nlm.nih.gov/home/develop/api/
- **Open Retractions**: https://openretractions.com/

## References

See `references/` for:
- `citation-formats.md`: Supported citation format specifications
- `api-documentation.md`: Database API reference and rate limits
- `example-reports/`: Sample output reports for testing

---

**Author**: AI Assistant  
**Version**: 1.0  
**Last Updated**: 2026-02-06  
**Status**: Ready for use  
**Requires**: Internet connection for database lookups

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

```text

# Python dependencies
pip install -r requirements.txt
```

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

This skill accepts requests that match the documented purpose of `retraction-watcher` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `retraction-watcher` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

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
