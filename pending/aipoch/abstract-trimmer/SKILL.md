---
name: abstract-trimmer
description: Precision editing tool that reduces abstract word count through intelligent compression techniques, maintaining scientific rigor while meeting strict journal and conference requirements.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Abstract Trimmer

Precision editing tool that reduces abstract word count through intelligent compression techniques, maintaining scientific rigor while meeting strict journal and conference requirements.

## When to Use

- Use this skill when the task needs Precision editing tool that reduces abstract word count through intelligent compression techniques, maintaining scientific rigor while meeting strict journal and conference requirements.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Precision editing tool that reduces abstract word count through intelligent compression techniques, maintaining scientific rigor while meeting strict journal and conference requirements.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/abstract-trimmer"
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
python scripts/main.py --text "Background Methods Results Conclusion blood pressure improved with lifestyle coaching over 12 weeks." --target 40
python scripts/main.py --text "Brief abstract for audit validation with measurable endpoints." --target 20 --check-only
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Features

- **Smart Compression**: Multiple strategies (aggressive, conservative, balanced)
- **Key Information Preservation**: Retains critical findings and statistics
- **Structural Integrity**: Maintains Background-Methods-Results-Conclusion flow
- **Quantitative Safety**: Protects numbers, P-values, and confidence intervals
- **Batch Processing**: Trim multiple abstracts efficiently
- **Quality Validation**: Post-trim readability and accuracy checks

## Usage

### Basic Usage

```text

# Trim abstract from file
python scripts/main.py --input abstract.txt --target 250

# Trim abstract from command line
python scripts/main.py --text "Your abstract here..." --target 200

# Check word count only
python scripts/main.py --input abstract.txt --target 250 --check-only
```

### Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | str | None | No | Input file containing abstract |
| `--text`, `-t` | str | None | No | Abstract text (alternative to --input) |
| `--target`, `-T` | int | 250 | No | Target word count |
| `--strategy`, `-s` | str | balanced | No | Trimming strategy (conservative/balanced/aggressive) |
| `--output`, `-o` | str | None | No | Output file path |
| `--check-only`, `-c` | flag | False | No | Only check word count without trimming |
| `--format` | str | json | No | Output format (json/text) |

### Advanced Usage

```text

# Aggressive trimming with text output
python scripts/main.py \
  --input abstract.txt \
  --target 200 \
  --strategy aggressive \
  --format text \
  --output trimmed.txt

# Batch check multiple abstracts
for file in *.txt; do
  python scripts/main.py --input "$file" --target 250 --check-only
done
```

## Trimming Strategies

| Strategy | Approach | Best For |
|----------|----------|----------|
| **Conservative** | Remove filler words, simplify sentences | Minor trims (10-20 words) |
| **Balanced** | Condense phrases, merge sentences | Moderate trims (20-50 words) |
| **Aggressive** | Remove secondary details, abbreviate | Major trims (50+ words) |

## Output Format

### JSON Output

```json
{
  "trimmed_abstract": "Compressed abstract text...",
  "original_words": 320,
  "final_words": 248,
  "reduction_percent": 22.5
}
```

### Text Output

```
Compressed abstract text...
```

## Technical Difficulty: **LOW**

⚠️ **AI independent acceptance status**: manual inspection required
This skill requires:
- Python 3.7+ environment
- No external dependencies

### Required Python Packages

```text
pip install -r requirements.txt
```

### Requirements File

No external dependencies required (uses only Python standard library).

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts executed locally | Low |
| Network Access | No network access | Low |
| File System Access | Read/write text files only | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | No sensitive data exposure | Low |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access (../)
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Input file paths validated
- [x] Output directory restricted to workspace
- [x] Script execution in sandboxed environment
- [x] Error messages sanitized
- [x] Dependencies audited

## Prerequisites

```text

# No dependencies required
python scripts/main.py --help
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully trims abstracts to target word count
- [ ] Preserves key scientific information
- [ ] Maintains grammatical correctness
- [ ] Handles edge cases gracefully

### Test Cases
1. **Basic Trimming**: Input abstract → Trimed to target word count
2. **Check Mode**: --check-only flag → Reports word count statistics
3. **File I/O**: Read from file, write to file → Correct file handling
4. **Different Strategies**: All three strategies work → Different compression levels

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-15
- **Known Issues**: None
- **Planned Improvements**: 
  - Enhanced protection for quantitative data
  - Support for structured abstracts
  - Batch processing mode

## References

See `references/` for:
- Compression strategies documentation
- Protected elements guidelines
- Journal word limits by publisher

## Limitations

- **Language**: Optimized for English academic abstracts
- **Content Type**: Designed for structured abstracts (BMRC format)
- **No Rewriting**: Only removes/compresses; doesn't rephrase
- **Final Review**: Automated trimming requires human validation

---

**✂️ Remember: This tool helps meet word limits, but never sacrifice scientific accuracy. Always validate that trimmed abstracts maintain the integrity of your findings.**

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

This skill accepts requests that match the documented purpose of `abstract-trimmer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `abstract-trimmer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
