---
name: graph-interpretation
description: Use when interpreting scientific graphs and charts, explaining data visualizations for research presentations, writing figure captions for publications, or analyzing trends in clinical research data. Converts complex visual data into clear, accurate explanations for academic papers, clinical reports, and public presentations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Scientific Graph Interpreter

Interpret and explain scientific graphs, charts, and data visualizations for research publications, clinical presentations, and academic communications with precision and clarity.

## When to Use

- Use this skill when the task needs Use when interpreting scientific graphs and charts, explaining data visualizations for research presentations, writing figure captions for publications, or analyzing trends in clinical research data. Converts complex visual data into clear, accurate explanations for academic papers, clinical reports, and public presentations.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when interpreting scientific graphs and charts, explaining data visualizations for research presentations, writing figure captions for publications, or analyzing trends in clinical research data. Converts complex visual data into clear, accurate explanations for academic papers, clinical reports, and public presentations.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/graph-interpretation"
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
python scripts/main.py
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.graph_interpreter import GraphInterpreter

interpreter = GraphInterpreter()

# Comprehensive graph analysis
analysis = interpreter.interpret(
    image_path="figure_1.png",
    graph_type="kaplan_meier",
    context="oncology_phase3_trial",
    audience="clinicians"
)

print(analysis.statistical_summary)
print(analysis.clinical_significance)
print(analysis.suggested_caption)
```

## Core Capabilities

### 1. Multi-Type Graph Analysis

```python
analysis = interpreter.analyze(
    graph_type="forest_plot",
    data={
        "studies": ["Study A", "Study B", "Study C"],
        "effect_sizes": [1.2, 0.8, 1.5],
        "confidence_intervals": [[1.0, 1.4], [0.6, 1.0], [1.2, 1.8]],
        "overall_effect": 1.15,
        "heterogeneity_p": 0.04
    }
)
```

**Supported Graph Types:**

| Graph Type | Common Use | Key Elements to Extract |
|------------|------------|------------------------|
| **Kaplan-Meier** | Survival analysis | Median survival, HR, 95% CI, log-rank p |
| **Forest Plot** | Meta-analysis | Effect size, CI, heterogeneity (I²), weights |
| **ROC Curve** | Diagnostic accuracy | AUC, sensitivity, specificity, optimal cutoff |
| **Box Plot** | Distribution comparison | Median, IQR, outliers, whiskers |
| **Scatter Plot** | Correlation | R², p-value, trend line, outliers |
| **Bar Chart** | Group comparisons | Means, SEM/SD, significance indicators |
| **Heatmap** | Expression/omics | Scale, clustering, row/column annotations |
| **Volcano Plot** | Differential analysis | Fold change, p-value, FDR threshold |

### 2. Statistical Interpretation

```python
stats = interpreter.extract_statistics(
    graph_data,
    extract=[
        "p_values",
        "confidence_intervals", 
        "effect_sizes",
        "sample_sizes",
        "statistical_tests"
    ]
)
```

**Statistical Reporting Standards:**

```python

# Example output structure
{
    "primary_outcome": {
        "measure": "Hazard Ratio",
        "value": 0.72,
        "ci_95": [0.58, 0.89],
        "p_value": 0.003,
        "interpretation": "32% risk reduction"
    },
    "secondary_outcomes": [...],
    "significance_level": 0.05,
    "multiple_comparison_adjusted": True
}
```

### 3. Audience-Specific Explanations

```python
explanations = interpreter.generate_multi_audience(
    analysis,
    audiences=["researchers", "clinicians", "patients", "policy_makers"]
)
```

**Explanation Templates:**

**For Researchers:**
> "The Kaplan-Meier analysis demonstrates a statistically significant 
> survival advantage for the experimental arm (HR 0.72, 95% CI 0.58-0.89, 
> p=0.003). Median survival improved from 14.2 to 19.6 months. 
> The proportional hazards assumption was verified (p=0.42)."

**For Clinicians:**
> "This trial shows patients on the new treatment lived about 5 months 
> longer on average compared to standard care. The 32% reduction in 
> death risk is significant and clinically meaningful. Consider this 
> option for eligible patients."

**For Patients:**
> "The study found that people taking the new treatment lived longer 
> than those on standard treatment. About 1 in 3 patients benefited 
> from the new treatment. Side effects were manageable."

### 4. Figure Caption Generation

```python
caption = interpreter.generate_caption(
    analysis,
    style="journal",  # or "presentation", "poster"
    word_limit=250,
    include_statistics=True
)
```

**Caption Structure:**
```
Figure X. [Brief title]. [What is shown: X-axis shows..., Y-axis shows..., 
lines/bars represent...]. [Key finding: Group A showed... compared to 
Group B...]. [Statistics: HR 0.72 (95% CI 0.58-0.89), p=0.003]. 
[Conclusion: This demonstrates...].
```

### 5. Critical Appraisal

```python
appraisal = interpreter.critical_appraisal(
    graph_data,
    check=[
        "appropriate_graph_type",
        "axis_scaling",
        "error_bars_present",
        "sample_size_adequate",
        "confounding_controlled",
        "generalizability"
    ]
)
```

**Common Graph Pitfalls:**

| Issue | Problem | Better Approach |
|-------|---------|-----------------|
| Truncated y-axis | Exaggerates differences | Start at 0 or clearly indicate break |
| No error bars | Hides variability | Include SD, SEM, or 95% CI |
| 3D effects | Distorts perception | Use 2D with clear labels |
| Dual y-axes | Confusing comparison | Separate graphs or normalized scale |
| p-hacking indicators | Multiple comparisons | Adjusted p-values, Bonferroni |

## CLI Usage

```text

# Comprehensive analysis
python scripts/graph_interpreter.py \
  --image survival_curve.png \
  --type kaplan_meier \
  --context "phase_3_oncology" \
  --audience clinicians \
  --output analysis.json

# Generate publication caption
python scripts/graph_interpreter.py \
  --image forest_plot.png \
  --type forest_plot \
  --generate caption \
  --journal-style nature \
  --word-limit 200

# Batch process figures
python scripts/graph_interpreter.py \
  --batch figures/ \
  --output report.html \
  --template comprehensive
```

## Common Patterns

### Pattern 1: Clinical Trial Primary Endpoint

```python

# Analyze survival curve
analysis = interpreter.interpret(
    graph_type="kaplan_meier",
    primary_endpoint="overall_survival",
    treatment_arms=["Experimental", "Control"],
    key_metrics=["median_os", "hr", "ci", "p_value"]
)

# Generate regulatory-ready summary
regulatory_summary = interpreter.generate_regulatory_summary(
    analysis,
    guideline="ICH_E3"
)
```

### Pattern 2: Meta-Analysis Forest Plot

```python

# Interpret meta-analysis
analysis = interpreter.interpret_forest_plot(
    studies=included_studies,
    check_heterogeneity=True,
    assess_publication_bias=True
)

# Generate GRADE assessment
grade_rating = interpreter.generate_grade_rating(analysis)
```

### Pattern 3: Diagnostic Accuracy ROC

```python

# Analyze diagnostic test
analysis = interpreter.interpret_roc(
    curves=["Test A", "Test B", "Combined"],
    optimal_cutoffs=True,
    clinical Utility=True
)

# Clinical decision support
decision_aid = interpreter.generate_decision_aid(analysis)
```

## Quality Checklist

**Before Interpretation:**
- [ ] Graph type appropriate for data
- [ ] Axes clearly labeled with units
- [ ] Sample sizes indicated
- [ ] Statistical tests specified
- [ ] Confidence intervals present

**During Interpretation:**
- [ ] Effect size calculated
- [ ] Clinical significance assessed
- [ ] Confidence intervals interpreted
- [ ] Limitations noted
- [ ] Generalizability considered

**After Interpretation:**
- [ ] Explanation appropriate for audience
- [ ] Statistical terms explained
- [ ] Uncertainty communicated
- [ ] Actionable insights highlighted

## Best Practices

**Statistical Communication:**
- Always report confidence intervals with point estimates
- Distinguish statistical from clinical significance
- Note limitations and generalizability
- Avoid causal language in observational studies

**Visual Analysis:**
- Check axis scales for distortion
- Note truncated axes or breaks
- Identify outliers and their impact
- Verify error bar representation (SD vs SEM)

## Common Pitfalls

❌ **Correlation = Causation**: "X causes Y because they're correlated"
✅ **Cautious Interpretation**: "X is associated with Y; other factors may explain this"

❌ **Overstating Significance**: "Highly significant (p<0.001)" as meaning large effect
✅ **Proper Framing**: "Statistically significant but modest effect size (d=0.2)"

❌ **Ignoring Confidence Intervals**: Reporting point estimate only
✅ **Interval Reporting**: "Effect: 1.5 (95% CI: 0.9-2.4), suggesting uncertainty"

---

**Skill ID**: 209 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `graph-interpretation` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `graph-interpretation` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
