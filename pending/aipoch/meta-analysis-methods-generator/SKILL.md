---
name: meta-analysis-methods-generator
description: Generates the Methods section for a meta-analysis paper, including search strategy, screening, quality assessment, data extraction, and statistical analysis.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Meta Analysis Methods Generator

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates the Methods section for a meta-analysis paper, including search strategy, screening, quality assessment, data extraction, and statistical analysis.
- Packaged executable path(s): `scripts/validate_skill.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Academic Writing/meta-analysis-methods-generator"
python -m py_compile scripts/validate_skill.py
python scripts/validate_skill.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/validate_skill.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/validate_skill.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

## User Intent Examples

- "Generate a methods section for a meta-analysis on..."
- "Write the methods part for my paper using these criteria..."

## IO Contract

**Inputs:**
- `criteria` (string, required): Inclusion and exclusion criteria.
- `PICOS` (string, required): Population, Intervention, Comparison, Outcome, Study design.
- `title` (string, required): The risk of bias assessment tool to use (e.g., ROB2, NOS, ROBINS-I, ROBINS-E, QUADAS, QUIPS, PROBAST).
- `language` (string, required): Output language (Chinese or English).

**Outputs:**
- `methods_section` (markdown): The complete Methods section.

## Workflow

1.  **Input Validation**: Verify `criteria`, `PICOS`, `title`, and `language` are provided.
2.  **Context Retrieval**: Obtain `current_time`.
3.  **Execution Steps**:
    -   **Step 1: Search Strategy**
        -   Action: Generate content using [Search Strategy](#search-strategy) prompt.
        -   Inputs: `PICOS`, `current_time`, `language`.
    -   **Step 2: Inclusion and Exclusion Criteria**
        -   Action: Generate content using [Inclusion and Exclusion Criteria](#inclusion-and-exclusion-criteria) prompt.
        -   Inputs: `criteria`, `language`.
    -   **Step 3: Literature Screening**
        -   Action: Generate content using [Literature Screening](#literature-screening) prompt.
        -   Inputs: `language`.
    -   **Step 4: Quality Assessment**
        -   Action: Generate content using [Quality Assessment](#quality-assessment) prompt.
        -   Inputs: `title`, `PICOS`, `language`.
    -   **Step 5: Data Extraction**
        -   Action: Generate content using [Data Extraction](#data-extraction) prompt.
        -   Inputs: `language`.
    -   **Step 6: Statistical Analysis**
        -   Action: Generate content using [Statistical Analysis](#statistical-analysis) prompt.
        -   Inputs: `language`.
4.  **Compilation**: Combine all generated sections into a single Markdown document.

## Quality Rules

- **QR-LANG-001**: Output must be in the specified language.
- **QR-FORMAT-001**: Follow the specific outline for each subsection.
- **QR-CONTENT-001**: Include all 6 required subsections.

## Prompts and Templates

## Inclusion and Exclusion Criteria
**Role**: System
**Content**:

## The user will input a section of inclusion and exclusion criteria. Please:

## Specific Requirements:
1. Remove JSON formatting.
2. Output the inclusion and exclusion criteria completely; do not modify.
3. Please output all content in **{{ language }}**.

## Literature Screening
**Role**: System
**Content**:
**Literature screening**

## Write a paragraph about literature screening for the methods section of a meta-analysis, following the outline below. Note that the outline is not an example; please expand or modify appropriately based on the outline. Write general information, avoiding specific details.
Please always remember that I want the text paragraph to be random, not static.

## Outline:
1. Initial screening: Two experts.
2. Initial screening results are: "Yes", "No", and "Maybe".
3. Secondary screening: Three experts.
4. Please output all content in **{{ language }}**, more than 200 words.

## Quality Assessment
**Role**: System
**Content**:
**Quality assessment**

## Please select the appropriate scale type according to the following rules.
- Etiological studies use ROBINS-E or NOS.
- RCT: use ROB2.
- Non-RCT (Clinical Trials): use ROBINS-I.
- Observational studies: use NOS.
- Prognostic studies use QUIPS or PROBAST.

## Based on the title and PICOS entered by the user, infer the quality assessment scale that might be used, write a section on quality assessment for the meta-analysis methods part, and follow the outline below:
1. ROB2: Covers random sequence generation, allocation concealment, the use of blinding, data completeness, selective reporting, and other potential sources of bias.
NOS: This scale assesses the quality of selection, comparability, and outcome.
ROBINS-I: ROBINS-I involves seven domains: confounding, selection of participants, classification of interventions, deviations from intended interventions, missing data, measurement of outcomes, and selection of the reported results. Each domain has ratings of low, moderate, serious, or unclear risk of bias.
ROBINS-E: The ROBINS-E tool includes seven domains: confounding, measurement of the exposure, participant selection, post-exposure interventions, missing data, measurement of the outcome, and selection of the reported result.
QUIPS: Overall risk of bias is 'low', 'moderate', or 'high'. Assess the 6 items of QUIPS: [1] study participation, [2] study attrition, [3] prognostic factor measurement, [4] outcome measurement, [5] study confounding, and [6] statistical analysis and reporting.
PROBAST: The answer for each domain is classified as low, high, or unclear. If at least one domain is assessed as high risk, then the overall assessment is high risk. If at least one domain is rated as unclear and there is no high risk, then the overall assessment is unclear.
2. Please output all content in **{{ language }}**!!!

## Data Extraction
**Role**: System
**Content**:

## Write a paragraph about data extraction for the meta-analysis methods section, following the outline below:
1. Extract author name, year of publication, and basic characteristics of participants (number, age, gender).
2. Please output all content in **{{ language }}**, more than 200 words.

## Statistical Analysis
**Role**: System
**Content**:
**Statistical analysis**

## Write a section on data analysis for the meta-analysis methods part, following the outline below. Note that the outline is not an example; please expand or modify appropriately based on the outline. Write general information, avoiding specific details.

## Outline:
1. Use R packages for statistical analysis.
2. I^2 is used to assess heterogeneity; values of 25%, 50%, and 75% are considered low, moderate, and high, respectively. If I^2 < 50%, use the fixed-effects model for data analysis; otherwise, use the random-effects model.
3. Use funnel plots to detect publication bias. p < 0.05 indicates statistical significance.
4. Please output all content in **{{ language }}**, more than 200 words.

## Search Strategy
**Role**: System
**Content**:

## The user will input several PICOS keywords. Please write a search strategy paragraph for the meta-analysis methods section based on the keywords.

## Specific Requirements:
1. The search strategy should explicitly state that all literature searches are conducted via the official PubMed API, and the search time is {{ current_time }}.
2. Describe the keywords.
3. Please output all content in **{{ language }}**.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `meta_analysis_methods_generator_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: meta_analysis_methods_generator_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
