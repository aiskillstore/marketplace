---
name: peer-review
description: Conduct professional peer reviews for papers or theses, providing structured evaluations and improvement suggestions; use when you need a pre-submission assessment, an internal review, or academic quality control.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Peer Review

## When to Use

- **Pre-submission manuscript check**: Before submitting to a journal/conference to identify major risks and revision priorities.
- **Internal lab/group review**: For advisor or team quality control prior to external dissemination.
- **Thesis/dissertation evaluation**: To assess academic rigor, structure, and defensibility before committee review.
- **Revision planning after feedback**: To translate reviewer/editor comments into an actionable improvement roadmap.
- **Quality assurance for research outputs**: To ensure methods, reporting, and conclusions meet disciplinary standards.

## Key Features

- **Structured end-to-end review workflow**: Overall evaluation → methods/results check → issue organization → recommendation.
- **Major vs. minor issue triage**: Separates publication-blocking problems from polish-level improvements.
- **Actionable revision suggestions**: Each issue is paired with concrete steps to fix or strengthen the work.
- **Recommendation with rationale**: Clear accept/revise/reject guidance with reasons and improvement path.
- **Reusable templates and checklists**: Supports consistent formatting and comprehensive coverage (see referenced files).

## Dependencies

- **None (runtime)**

## Example Usage

Use the template to produce a structured review.

1. Open the template:
   - `assets/peer_review_template.md`

2. Fill it using the workflow below. Example (copy/paste and complete):

```markdown
# Peer Review Report

## 1. Overall Evaluation
**Summary of the work:**  
This paper investigates [research question] by using [method/data]. The main contributions are: (1) [...], (2) [...].

**Novelty and significance:**  
- Novelty: [high/medium/low] because [...]
- Significance: [high/medium/low] because [...]

## 2. Methods and Results
**Research design and methodology:**  
- Appropriateness of design: [...]
- Data and sampling: [...]
- Statistical/analytical methods: [...]
- Reproducibility (code/data availability, parameter reporting): [...]

**Results vs. conclusions:**  
- Do results support claims? [...]
- Alternative explanations addressed? [...]
- Robustness checks/ablation/sensitivity analysis: [...]

## 3. Issues and Revision Suggestions

### Major Issues (must address)
1. **Issue:** [...]
   - **Why it matters:** [...]
   - **Suggested fix:** [...]
   - **Expected impact:** [...]

2. **Issue:** [...]
   - **Why it matters:** [...]
   - **Suggested fix:** [...]
   - **Expected impact:** [...]

### Minor Issues (should address)
1. **Issue:** [...]
   - **Suggested fix:** [...]

2. **Issue:** [...]
   - **Suggested fix:** [...]

## 4. Recommendation
**Recommendation:** Accept / Minor Revision / Major Revision / Reject

**Rationale:**  
Explain the decision based on novelty, rigor, clarity, and evidence strength.

**Path to improvement:**  
List the top 3–5 changes that would most improve the manuscript.
```

For output formats, checklists, and inspection points, see:
- `references/guide.md`

## Implementation Details

### Review Workflow (Algorithm)

1. **Read for global understanding**
   - Read the abstract and full text to form an overall impression.
   - Identify the research question, claimed contributions, and target audience/venue.

2. **Overall evaluation**
   - Summarize the research questions and major contributions.
   - Assess **novelty** (what is new vs. prior work) and **significance** (why it matters).

3. **Methods and results verification**
   - Check research design, data quality, and statistical/analytical methods for correctness and suitability.
   - Evaluate whether results **logically and quantitatively** support the conclusions.
   - Flag missing details that prevent replication (e.g., parameters, datasets, baselines, evaluation protocol).

4. **Issue organization**
   - Classify findings into:
     - **Major issues**: validity threats, methodological flaws, unsupported claims, missing critical experiments, ethical/compliance gaps.
     - **Minor issues**: clarity, formatting, citations, small inconsistencies, language improvements.
   - For each issue, provide an **actionable** revision suggestion (what to change and how).

5. **Recommendation**
   - Provide a decision (accept/revise/reject) aligned with the severity and fixability of major issues.
   - Explain the rationale and provide a prioritized improvement path.

### Key Parameters / Criteria

- **Novelty**: degree of differentiation from prior work; clarity of contribution statement.
- **Significance**: practical/theoretical impact; relevance to the field and venue.
- **Rigor**: appropriateness of methods; correctness of analysis; robustness checks.
- **Evidence alignment**: strength of support from results to claims; avoidance of overgeneralization.
- **Reproducibility**: completeness of experimental details; availability of data/code; transparent reporting.
- **Clarity and structure**: logical flow, readability, figure/table quality, and citation completeness.

### Templates and References

- Template (preferred for structured output): `assets/peer_review_template.md`
- Guidance/checklists/output formats: `references/guide.md`