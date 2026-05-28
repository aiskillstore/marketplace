---
name: discussion-section-architect
description: Structures and writes discussion sections for academic papers and research reports. Use when writing a discussion section, interpreting research results, connecting findings to existing literature, addressing study limitations, synthesizing conclusions, or drafting any part of an academic discussion. Helps researchers organize arguments, contextualize data, and produce clear, publication-ready discussion prose.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Discussion Section Architect

## When to Use

- Use this skill when the task needs Structures and writes discussion sections for academic papers and research reports. Use when writing a discussion section, interpreting research results, connecting findings to existing literature, addressing study limitations, synthesizing conclusions, or drafting any part of an academic discussion. Helps researchers organize arguments, contextualize data, and produce clear, publication-ready discussion prose.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Structures and writes discussion sections for academic papers and research reports. Use when writing a discussion section, interpreting research results, connecting findings to existing literature, addressing study limitations, synthesizing conclusions, or drafting any part of an academic discussion. Helps researchers organize arguments, contextualize data, and produce clear, publication-ready discussion prose.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/discussion-section-architect"
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

## Quick Start

1. Provide your **research question**, **key results**, and any **prior literature** you want to reference.
2. Choose a structure (see workflows below).
3. Generate a draft discussion section with clearly organized subsections.
4. Run the **Draft → Revise loop** (see below).

---

## Core Capabilities

### 1. Interpret and Contextualize Results

- State whether results support or contradict the original hypothesis.
- Explain unexpected findings with reasoned interpretations.
- Quantify effect sizes or patterns when relevant.

**Example prompt input:**
```
Results: Group A showed a 23% reduction in symptom severity (p=0.003) vs. control.
Hypothesis: Intervention would reduce symptom severity.
Task: Interpret this result for the discussion section.
```

**Example output excerpt:**
```
The 23% reduction in symptom severity (p=0.003) supports the primary hypothesis.
This effect size is clinically meaningful and consistent with the mechanistic
rationale proposed in the introduction...
```

---

### 2. Connect Findings to Existing Literature

- Identify studies that corroborate the findings.
- Highlight where results diverge from prior literature and offer explanations.
- Use hedged academic language appropriate to the field.

**Example:**
```
Finding: Effect was stronger in older participants.
Literature: Smith et al. (2019) found age-moderated responses in a similar cohort.
Task: Connect finding to literature.
```

**Output:**
```
The age-moderated effect aligns with Smith et al. (2019), who reported attenuated
responses in younger adults. One possible explanation is differential receptor
sensitivity across age groups, as suggested by...
```

---

### 3. Address Limitations

Draft a limitations subsection that is honest but does not undermine the contribution:

```
Limitation: [Describe constraint]
Impact: [How it affects interpretation]
Mitigation / Future direction: [How it could be addressed]
```

---

### 4. Synthesize Conclusions

Generate a closing paragraph that:

- Restates the core finding in plain language.
- States the theoretical or practical contribution.
- Ends with a forward-looking statement about implications or next steps.

---

## Recommended Discussion Structure

```
1. Opening: Restate the research question and summarize the key finding (2–3 sentences).
2. Interpretation: Explain what the results mean mechanistically or theoretically.
3. Comparison to Literature: Agree/contrast with prior studies; explain divergences.
4. Implications: Theoretical contributions and/or practical applications.
5. Limitations: Honest scope boundaries with future directions.
6. Conclusion: Synthesis and forward-looking close.
```

---

## Draft → Revise Loop

Use this iterative workflow after generating an initial draft:

**Step 1 — Draft**: Generate the full discussion section using the structure above.

**Step 2 — Check**: Review against the checklist:
- [ ] Each finding from the Results section is explicitly addressed.
- [ ] Claims are supported by citations or logical reasoning — not stated as facts.
- [ ] Unexpected or null results are acknowledged and interpreted.
- [ ] Limitations are stated without dismissing the study's contribution.
- [ ] No new data or results are introduced in the discussion.
- [ ] Hedged language used appropriately (e.g., "suggests," "indicates," "may reflect").
- [ ] Conclusion ties back to the original research question.

**Step 3 — Revise**: For each failed checklist item, revise only the affected paragraph(s).

**Step 4 — Re-check**: Re-run the checklist on revised paragraphs to confirm resolution before finalizing.

---

## References

- `references/guide.md` - Detailed documentation
- `references/examples/` - Sample inputs and outputs

---

**Skill ID**: 950 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `discussion-section-architect` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `discussion-section-architect` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
