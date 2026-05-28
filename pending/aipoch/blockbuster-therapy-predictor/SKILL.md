---
name: blockbuster-therapy-predictor
description: Comprehensive analytics tool for forecasting breakthrough therapeutic technologies by integrating multi-dimensional data sources including clinical development pipelines, intellectual property landscapes, and capital mar.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Blockbuster Therapy Predictor

Comprehensive analytics tool for forecasting breakthrough therapeutic technologies by integrating multi-dimensional data sources including clinical development pipelines, intellectual property landscapes, and capital market indicators.

## When to Use

- Use this skill when the task needs Comprehensive analytics tool for forecasting breakthrough therapeutic technologies by integrating multi-dimensional data sources including clinical development pipelines, intellectual property landscapes, and capital mar.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Comprehensive analytics tool for forecasting breakthrough therapeutic technologies by integrating multi-dimensional data sources including clinical development pipelines, intellectual property landscapes, and capital mar.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/blockbuster-therapy-predictor"
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

- **Multi-Source Data Integration**: Aggregates clinical trials, patents, and funding data
- **Predictive Scoring**: Calculates Blockbuster Index combining maturity, market potential, and momentum
- **Technology Landscape Mapping**: Tracks 10+ emerging therapeutic platforms
- **Investment Intelligence**: Provides data-driven R&D and investment recommendations
- **Trend Analysis**: Identifies acceleration patterns and inflection points

## Usage

### Basic Usage

```text

# Run complete analysis with all technologies
python scripts/main.py

# Analyze specific technologies
python scripts/main.py --tech PROTAC,mRNA,CRISPR

# Output in JSON format
python scripts/main.py --output json
```

### Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--mode` | str | full | No | Analysis mode: full or quick |
| `--tech` | str | None | No | Comma-separated list of technologies to analyze |
| `--output` | str | console | No | Output format: console or json |
| `--threshold` | float | 0 | No | Minimum blockbuster index threshold (0-100) |
| `--save` | str | None | No | Save report to file path |

### Advanced Usage

```text

# Analyze high-potential technologies only (index ≥70)
python scripts/main.py \
  --threshold 70 \
  --output json \
  --save high_potential_report.json

# Quick analysis of specific platforms
python scripts/main.py \
  --mode quick \
  --tech CAR-T,ADC,Bispecific \
  --output console
```

## Output

### Console Output

```
🏆 BLOCKBUSTER THERAPY PREDICTOR Report
Generated: 2026-02-15 10:30:00
Technologies analyzed: 10

📊 Technology Rankings
Rank  Technology       Blockbuster Index    Maturity    Market Potential    Momentum    Recommendation
🥇 1   mRNA             85.2                 78.5        92.1                88.0        Strongly Recommended
🥈 2   CAR-T            82.3                 85.2        78.5                75.0        Strongly Recommended
🥉 3   CRISPR           79.8                 72.3        88.2                68.0        Recommended
```

### JSON Output Structure

```json
{
  "generated_at": "2026-02-15T10:30:00",
  "total_routes": 10,
  "rankings": [
    {
      "rank": 1,
      "tech_name": "mRNA",
      "blockbuster_index": 85.2,
      "maturity_score": 78.5,
      "market_potential_score": 92.1,
      "momentum_score": 88.0,
      "recommendation": "Strongly Recommended",
      "key_drivers": ["Multiple Phase III trials", "Rapid patent growth"],
      "risk_factors": ["Regulatory uncertainties"],
      "timeline_prediction": "First product expected in 2-4 years"
    }
  ]
}
```

## Scoring Methodology

### Blockbuster Index Formula

```
Blockbuster Index = (Market Potential × 0.5) + (Maturity × 0.3) + (Momentum × 0.2)
```

### Component Scores

| Component | Weight | Factors |
|-----------|--------|---------|
| **Market Potential** | 50% | Market size, unmet need, competition |
| **Maturity** | 30% | Clinical stage, patent depth, funding stage |
| **Momentum** | 20% | Patent growth, funding activity, clinical progress |

### Investment Recommendation Thresholds

| Blockbuster Index | Recommendation | Action |
|-------------------|----------------|--------|
| ≥ 80 | **Strongly Recommended** | Prioritize R&D investment |
| 60-79 | **Recommended** | Active monitoring and early partnerships |
| 40-59 | **Watch** | Monitor milestones; reassess in 6-12 months |
| < 40 | **Cautious** | Minimal investment; consider divestment |

## Supported Technologies

| Technology | Category | Description |
|------------|----------|-------------|
| PROTAC | Protein Degradation | Proteolysis Targeting Chimera |
| mRNA | Nucleic Acid Drugs | Messenger RNA therapy platform |
| CRISPR | Gene Editing | CRISPR-Cas gene editing technology |
| CAR-T | Cell Therapy | Chimeric Antigen Receptor T-cell therapy |
| Bispecific | Antibody Drugs | Bispecific antibody technology |
| ADC | Antibody Drugs | Antibody-Drug Conjugate |
| RNAi | Nucleic Acid Drugs | RNA interference therapy |
| Gene Therapy | Gene Therapy | AAV vector gene therapy |
| Allogeneic | Cell Therapy | Universal/Allogeneic cell therapy |
| Cell Therapy | Cell Therapy | General cell therapy platform |

## Technical Difficulty: **MEDIUM**

⚠️ **AI independent acceptance status**: manual inspection required
This skill requires:
- Python 3.8+ environment
- Basic understanding of biotech investment analysis
- Access to clinical trial, patent, and funding databases (optional)

### Required Python Packages

```text
pip install -r requirements.txt
```

### Requirements File

```
dataclasses
enum
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts executed locally | Medium |
| Network Access | No external API calls in mock mode | Low |
| File System Access | Read/write report files only | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access (../)
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Input file paths validated (no ../ traversal)
- [x] Output directory restricted to workspace
- [x] Script execution in sandboxed environment
- [x] Error messages sanitized (no stack traces exposed)
- [x] Dependencies audited

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
1. **Basic Functionality**: Run without arguments → Expected output with all technologies
2. **Technology Filter**: Use --tech flag → Only specified technologies analyzed
3. **JSON Output**: Use --output json → Valid JSON format output
4. **Threshold Filter**: Use --threshold 70 → Only technologies with index ≥70 shown

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-15
- **Known Issues**: None
- **Planned Improvements**: 
  - Integration with real-time data APIs
  - Additional technology platforms
  - Enhanced visualization capabilities

## References

See `references/` for:
- Historical blockbuster case studies
- Clinical trial data sources
- Patent analysis methodologies
- Investment scoring frameworks

## Limitations

- **Data Source**: Uses mock data for demonstration; real-time data integration required for production use
- **Prediction Accuracy**: Model provides indicative scores; not investment advice
- **Technology Coverage**: Limited to pre-configured technology platforms
- **Market Dynamics**: Cannot predict black swan events or regulatory changes
- **Regional Bias**: Data primarily focused on US/EU markets

---

**⚠️ DISCLAIMER: This tool provides quantitative analysis for decision support only. All investment and R&D decisions should incorporate qualitative domain expertise, regulatory consultation, and comprehensive due diligence. Past performance of historical blockbusters does not guarantee future success of emerging technologies.**

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

This skill accepts requests that match the documented purpose of `blockbuster-therapy-predictor` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `blockbuster-therapy-predictor` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
