---
name: graphical-abstract-wizard
description: Generate graphical abstract layout recommendations based on paper abstracts.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Graphical Abstract Wizard

This Skill analyzes academic paper abstracts and generates graphical abstract layout recommendations, including element suggestions, visual arrangements, and AI art prompts for Midjourney and DALL-E.

## When to Use

- Use this skill when the task is to Generate graphical abstract layout recommendations based on paper abstracts.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate graphical abstract layout recommendations based on paper abstracts.
- Packaged executable path(s): `scripts/main.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.8+
- OpenAI API (optional, for enhanced analysis)
- Standard library: re, json, argparse, sys

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/graphical-abstract-wizard"
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

## Usage

```text
python scripts/main.py --abstract "Your paper abstract text here"
```

Or from stdin:

```text
cat abstract.txt | python scripts/main.py
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--abstract` / `-a` | string | Yes* | The paper abstract text to analyze |
| `--style` / `-s` | string | No | Visual style preference (scientific/minimal/colorful/sketch) |
| `--format` / `-f` | string | No | Output format (json/markdown/text), default: markdown |
| `--output` / `-o` | string | No | Output file path (default: stdout) |

*Required if not providing input via stdin

## Examples

### Example 1: Basic Usage

```text
python scripts/main.py -a "We propose a novel deep learning approach for protein structure prediction that combines transformer architectures with geometric constraints. Our method achieves state-of-the-art accuracy on CASP14 benchmarks."
```

### Example 2: With Style Preference

```text
python scripts/main.py -a "abstract.txt" -s scientific -o layout.md
```

### Example 3: JSON Output for Integration

```text
python scripts/main.py -a "$(cat abstract.txt)" -f json > result.json
```

## Output Format

The Skill produces a structured analysis including:

### 1. Key Concepts Extracted
- Core research topic
- Methods/techniques used
- Key findings/results
- Implications

### 2. Visual Element Recommendations
- Recommended icons/symbols
- Color palette suggestions
- Layout structure

### 3. AI Art Prompts
- **Midjourney Prompt**: Optimized for Midjourney v6
- **DALL-E Prompt**: Optimized for DALL-E 3

### 4. Layout Blueprint
- Grid-based layout suggestion
- Element positioning
- Flow direction

## Example Output

```markdown

# Graphical Abstract Recommendation

## Abstract Summary
**Topic**: Deep learning protein structure prediction
**Method**: Transformer + Geometric constraints
**Result**: State-of-the-art CASP14 accuracy

## Key Concepts
- 🧬 Protein structures
- 🤖 Neural networks
- 📊 Accuracy metrics

## Visual Elements
| Element | Symbol | Position | Color |
|---------|--------|----------|-------|
| Core Concept | Brain + DNA | Center | Blue |
| Method | Neural Network | Left | Purple |
| Result | Trophy/Chart | Right | Gold |

## Layout Suggestion
```
┌─────────────────────────────────┐
│        [Title/Concept]          │
│            🧬🤖                 │
├──────────┬──────────┬───────────┤
│  Input   │ Process  │  Output   │
│   📥     │   ⚙️     │    📈     │
└──────────┴──────────┴───────────┘
```

## AI Art Prompts

### Midjourney
```
Scientific graphical abstract, protein structure prediction with neural networks, 3D molecular structures connected by glowing neural network nodes, blue and purple gradient background, clean minimalist style, academic journal style, high quality --ar 16:9 --v 6
```

### DALL-E
```
A clean scientific illustration for a research paper about protein structure prediction using deep learning. Show a 3D protein structure in the center surrounded by abstract neural network connections. Use a professional blue and white color scheme with subtle gradients. Include geometric shapes representing data flow. Modern, minimalist academic style suitable for a Nature or Science journal cover.
```
```

## Technical Details

The Skill uses NLP techniques to:
1. Extract named entities (methods, materials, concepts)
2. Identify research actions and outcomes
3. Map concepts to visual representations
4. Generate style-appropriate prompts

## License

MIT License - Part of OpenClaw Skills Collection

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

This skill accepts requests that match the documented purpose of `graphical-abstract-wizard` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `graphical-abstract-wizard` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
