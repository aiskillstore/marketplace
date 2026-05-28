---
name: response-tone-polisher
description: Polishes response letters by transforming defensive or harsh language.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Response Tone Polisher

Polishes response letters to peer reviewers by softening harsh or defensive language while preserving the author's position and scientific integrity.

## When to Use

- Use this skill when the task needs Polishes response letters by transforming defensive or harsh language.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- **Tone Analysis**: Identifies defensive, confrontational, or overly direct language
- **Polite Transformation**: Converts harsh statements into courteous academic prose
- **Position Preservation**: Maintains the author's scientific stance while improving delivery
- **Context Awareness**: Adapts based on response type (acceptance, partial acceptance, respectful decline)
- **Academic Expression Library**: Built-in collection of polished academic phrasings

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `enum`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/response-tone-polisher"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Overview` above for related details.

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

## Overview

This skill analyzes author draft responses to reviewer comments and transforms confrontational or defensive phrasing into professional, diplomatic academic language. It helps researchers maintain positive relationships with reviewers while standing firm on scientifically justified positions.

## Usage Examples

### Basic Usage

```
Input:
Reviewer: The sample size is too small for meaningful conclusions.
Draft Response: I disagree. Our sample size is standard in this field.

Output:
We appreciate the reviewer's concern regarding sample size. While we acknowledge 
that larger samples provide greater statistical power, our sample size is consistent 
with established conventions in this field and meets the requirements for adequate 
power analysis (as detailed in the Methods section).
```

### Defensive Language Transformation

| Original (Defensive) | Polished (Professional) |
|---------------------|------------------------|
| "I will not change this." | "We have carefully considered this suggestion and respectfully maintain our original approach because..." |
| "The reviewer is wrong." | "We respectfully offer a different interpretation..." |
| "This is unnecessary." | "We appreciate this suggestion; however, we believe the current presentation adequately addresses this point." |
| "We already explained this." | "We have expanded our explanation to enhance clarity (Page X, Lines Y-Z)." |
| "That's not our fault." | "We acknowledge this limitation and have added appropriate caveats to the Discussion." |

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `reviewer_comment` | str | Yes | The reviewer's original comment or criticism |
| `draft_response` | str | Yes | Author's initial draft response (may contain harsh/defensive language) |
| `response_type` | str | No | One of: `accept`, `partial`, `decline` (default: auto-detect) |
| `polish_level` | str | No | `light`, `moderate`, `heavy` (default: moderate) |
| `preserve_meaning` | bool | No | Ensure scientific position is preserved (default: true) |

## Output Format

```json
{
  "polished_response": "string",
  "original_tone_score": "float (0-1, higher = more defensive)",
  "improvements": [
    {
      "original_phrase": "string",
      "polished_phrase": "string",
      "issue_type": "string"
    }
  ],
  "suggestions": ["string"],
  "politeness_score": "float (0-1)"
}
```

## Tone Patterns Detected

The skill identifies and transforms:

### 1. Direct Refusals
- "No" / "We won't" → "We respectfully decline to..."
- "We can't" → "We are unable to..."

### 2. Defensive Statements
- "But we already..." → "We have now clarified..."
- "This is not correct" → "We respectfully note that..."

### 3. Blame Shifting
- "The reviewer misunderstood" → "We apologize for the lack of clarity; we have revised..."
- "This is standard" → "This approach aligns with established conventions..."

### 4. Emotional Language
- "Unfortunately" (overused) → [removed or softened]
- "Obviously" → [removed]
- "Clearly" → [removed or context-dependent]

## Polite Academic Expressions

### Acknowledging Reviewers
- "We thank the reviewer for this insightful observation."
- "We appreciate the reviewer's careful attention to this detail."
- "We are grateful for this constructive feedback."
- "This is an excellent point."

### Expressing Disagreement Diplomatically
- "We respectfully offer an alternative interpretation..."
- "Upon careful reconsideration, we believe..."
- "While we appreciate this perspective, we note that..."
- "We respectfully maintain our position that..."

### Explaining Limitations
- "We acknowledge this limitation and have addressed it by..."
- "This constraint reflects the trade-off between..."
- "We have added appropriate caveats regarding this limitation."

### Describing Changes
- "We have revised the manuscript to clarify..."
- "We have expanded the relevant section to include..."
- "We have incorporated this suggestion by..."

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Command Line Usage

```text

# Interactive mode
python scripts/main.py --interactive

# File-based
python scripts/main.py \
  --reviewer-comment "comment.txt" \
  --draft-response "draft.txt" \
  --output "polished.txt"

# Direct input
python scripts/main.py \
  --reviewer "The data is insufficient." \
  --draft "You are wrong. We have enough data." \
  --polish-level heavy
```

## Python API

```python
from scripts.main import TonePolisher

polisher = TonePolisher()
result = polisher.polish(
    reviewer_comment="The methodology is flawed.",
    draft_response="No it's not. We did it right.",
    response_type="decline",
    polish_level="moderate"
)

print(result["polished_response"])
```

## References

- `references/polite_expressions.json` - Curated library of academic polite expressions
- `references/tone_patterns.md` - Common defensive patterns and their transformations
- `references/examples/` - Before/after polishing examples

## Limitations

- Does not verify scientific accuracy of responses
- Requires human review for complex nuanced disagreements
- May over-soften; authors should verify position is still clear
- Best for English-language responses

## Quality Checklist

After polishing, verify:
- [ ] Original scientific position is preserved
- [ ] No confrontational language remains
- [ ] Professional tone throughout
- [ ] Clear acknowledgment of reviewer's effort
- [ ] Specific changes are still referenced
- [ ] Response directly addresses the comment

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

This skill accepts requests that match the documented purpose of `response-tone-polisher` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `response-tone-polisher` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
