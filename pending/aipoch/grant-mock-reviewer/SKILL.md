---
name: grant-mock-reviewer
description: Simulates NIH study section peer review for grant proposals. Triggers.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Grant Mock Reviewer

A simulated NIH study section reviewer that provides structured, rigorous critique of grant proposals using the official NIH scoring criteria and methodology.

## When to Use

- Use this skill when the task needs Simulates NIH study section peer review for grant proposals. Triggers.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Simulates NIH study section peer review for grant proposals. Triggers.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `enum`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/grant-mock-reviewer"
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
python scripts/main.py -h
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Capabilities

1. **NIH Scoring Rubric Application**: Official 1-9 scale scoring across all 5 criteria
2. **Weakness Identification**: Systematic detection of common proposal flaws
3. **Critique Generation**: Structured written critiques for each review criterion
4. **Summary Statement**: Complete mock Summary Statement output
5. **Revision Guidance**: Prioritized, actionable recommendations for improvement

## Usage

### Command Line

```text

# Full mock review with Summary Statement
python3 scripts/main.py --input proposal.pdf --format pdf --output review.md

# Review Specific Aims only
python3 scripts/main.py --input aims.pdf --section aims --output aims_review.md

# Targeted review (specific criterion focus)
python3 scripts/main.py --input proposal.pdf --focus approach --output approach_critique.md

# Generate NIH-style scores only
python3 scripts/main.py --input proposal.pdf --scores-only --output scores.json

# Compare before/after revision
python3 scripts/main.py --original original.pdf --revised revised.pdf --compare
```

### As Library

```python
from scripts.main import GrantMockReviewer

reviewer = GrantMockReviewer()
result = reviewer.review(
    proposal_text=proposal_content,
    grant_type="R01",
    section="full"
)
print(result.summary_statement)
print(result.scores)
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input` | string | - | Yes | Path to proposal file (PDF, DOCX, TXT, MD) |
| `--format` | string | auto | No | Input file format (pdf, docx, txt, md) |
| `--section` | string | full | No | Section to review (full, aims, significance, innovation, approach) |
| `--grant-type` | string | R01 | No | Grant mechanism (R01, R21, R03, K99, F32) |
| `--focus` | string | - | No | Focus on specific criterion (significance, investigator, innovation, approach, environment) |
| `--scores-only` | flag | false | No | Output scores only (JSON) |
| `--output`, `-o` | string | stdout | No | Output file path |
| `--original` | string | - | No | Original proposal for comparison |
| `--revised` | string | - | No | Revised proposal for comparison |
| `--compare` | flag | false | No | Enable comparison mode |

## NIH Scoring System

### Overall Impact Score (1-9)
The single most important score reflecting the likelihood of the project to exert a sustained, powerful influence on the research field.

| Score | Descriptor | Likelihood of Funding |
|-------|------------|----------------------|
| 1 | Exceptional | Very High |
| 2 | Outstanding | High |
| 3 | Excellent | Good |
| 4 | Very Good | Moderate |
| 5 | Good | Low-Moderate |
| 6 | Satisfactory | Low |
| 7 | Fair | Very Low |
| 8 | Marginal | Unlikely |
| 9 | Poor | Not Fundable |

### Individual Criteria (1-9 each)

1. **Significance**: Does the project address an important problem? Will scientific knowledge be advanced?
2. **Investigator(s)**: Are the PIs well-suited? Adequate experience and training?
3. **Innovation**: Does it challenge current paradigms? Novel concepts, approaches, methods?
4. **Approach**: Sound research design? Appropriate methods? Adequate controls? Address pitfalls?
5. **Environment**: Adequate institutional support? Scientific environment conducive to success?

### Score Interpretation
- **1-3 (High Priority)**: Compelling, well-developed proposals with strong approach
- **4-5 (Medium Priority)**: Good proposals with some weaknesses
- **6-9 (Low Priority)**: Significant weaknesses that diminish enthusiasm

## Review Output Format

### 1. Score Summary
```
Overall Impact: [Score] - [Descriptor]

Criterion Scores:
- Significance: [Score]
- Investigator(s): [Score]
- Innovation: [Score]
- Approach: [Score]
- Environment: [Score]
```

### 2. Strengths
Bullet-point list of major strengths by criterion

### 3. Weaknesses
Bullet-point list of major weaknesses by criterion

### 4. Detailed Critique
Paragraph-form critique for each criterion following NIH style

### 5. Summary Statement
Complete narrative synthesis of the review

### 6. Revision Recommendations
Prioritized, actionable suggestions for improvement

## Common Weaknesses Detected

### Significance
- Insufficient justification for the research problem
- Incremental rather than transformative impact
- Unclear connection to human health/disease
- Overstatement of clinical significance without evidence

### Investigator
- Lack of relevant expertise for proposed aims
- Insufficient track record in key methodologies
- PI overcommitted (excessive effort on other grants)
- Missing key collaborator expertise

### Innovation
- Straightforward extension of published work
- Methods are standard rather than novel
- No challenging of existing paradigms
- Incremental rather than breakthrough potential

### Approach
- Aims too ambitious for timeframe
- Insufficient preliminary data
- Inadequate experimental controls
- No discussion of pitfalls and alternatives
- Statistical analysis plan missing or inadequate
- Sample size/power calculations absent

### Environment
- Inadequate institutional resources
- Missing core facility access
- Lack of relevant equipment
- Insufficient collaborative environment

## Technical Difficulty

**High** - Requires deep understanding of NIH peer review processes, ability to apply standardized scoring rubrics consistently, and generation of clinically/scientifically accurate critique across diverse research domains.

**Review Required**: Human verification recommended before deployment in production settings.

## References

- `references/nih_scoring_rubric.md` - Complete NIH scoring guidelines
- `references/review_criteria_explained.md` - Detailed criterion descriptions
- `references/common_weaknesses_catalog.md` - Database of typical proposal flaws
- `references/summary_statement_templates.md` - NIH-style statement templates
- `references/score_calibration_guide.md` - Score assignment guidelines

## Best Practices for Users

1. **Provide Complete Proposals**: The tool works best with full Research Strategy sections
2. **Include Preliminary Data**: Approach critique depends on feasibility evidence
3. **Review Multiple Times**: Use iteratively as you revise
4. **Compare Versions**: Track improvement between drafts
5. **Consider Multiple Perspectives**: Supplement with human reviewer feedback

## Limitations

1. Cannot access external literature to verify claims
2. May not capture domain-specific methodological nuances
3. Scoring is simulated and may not match actual study section scores
4. Best used as preparatory tool, not replacement for human review

## Version

- 1.0.0 - Initial release with NIH R01/R21/R03 support

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

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

This skill accepts requests that match the documented purpose of `grant-mock-reviewer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `grant-mock-reviewer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
