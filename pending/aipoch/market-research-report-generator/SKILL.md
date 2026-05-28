---
name: market-research-report-generator
description: Generates professional market research reports by analyzing business intent, decision levels, and conducting multi-source data retrieval (Web, PubMed, Clinical Trials).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Market Research Report Generator

This skill generates comprehensive market research reports based on a topic and optional requirements. It follows a strict workflow: Intent Analysis -> Decision Level Analysis -> Question Generation -> Data Collection -> Report Synthesis.

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Generates professional market research reports by analyzing business intent, decision levels, and conducting multi-source data retrieval (Web, PubMed, Clinical Trials).
- Packaged executable path(s): `scripts/research_orchestrator.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/market-research-report-generator"
python -m py_compile scripts/research_orchestrator.py
python scripts/research_orchestrator.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/research_orchestrator.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/research_orchestrator.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Input
- `topic` (required): The main subject of the research (e.g., "Low-altitude economy", "Humanoid robots").
- `requirements` (optional): Specific focus areas or constraints.

## Output
- A Markdown report containing Executive Summary, Market Overview, Competitive Landscape, Technical/Clinical Analysis, and Strategic Recommendations.

## Workflow

### 1. Intent & Strategy Analysis
First, analyze the user's request to determine the business intent and the target audience's decision-making level.
- **Intent Analysis**: Classify the request into categories like Market Entry, Investment, or Product Strategy. Refer to `references/intent_classification.md` for guidelines.
- **Decision Level**: Determine if the report is for C-Level (strategic, concise), VP/Director (tactical, detailed), or R&D (technical). Refer to `references/decision_level.md`.

### 2. Core Question Generation
Based on the intent and level, generate 5-7 core questions that the research must answer.
- For Investment reports, focus on ROI, CAGR, and risks.
- For Product Strategy, focus on features, competitors, and user needs.
- For C-Level, prioritize high-level trends and financial impact.

### 3. Data Collection (Multi-Source)
You must collect data from multiple sources to ensure accuracy and depth.
**Do NOT make up data.** Use the following tools:

#### A. General Market Search (If available)
If the environment provides a web search capability (e.g., `WebSearch` tool):
- Generate 3-5 distinct search queries based on the Core Questions.
- Find market size, trends, and news.

#### B. Clinical/Medical Search (If applicable)
If the topic is related to healthcare, medicine, or bio-tech:
- **Unified Database Search**: Use the provided script to query both `clinicaltrials.gov` and `PubMed` simultaneously.
  - Command: `python scripts/research_orchestrator.py '["query1", "query2"]'`
  - The script will return JSON data containing results from both sources.

### 4. Data Aggregation & Synthesis
- Review all gathered information.
- Cross-reference numbers (e.g., market size predictions) from different sources.
- Highlight conflicts or uncertainties.

### 5. Report Generation
Write the final report in Markdown.
- **Tone**: Professional, objective, and aligned with the Decision Level (e.g., "Strategic & Direct" for C-Level).
- **Structure**:
  1. **Executive Summary**: Key findings and bottom-line recommendations (BLUF).
  2. **Market Overview**: Size, growth (CAGR), and drivers.
  3. **Competitive Landscape**: Key players and their market share/positioning.
  4. **Technical/Clinical Analysis**: (If applicable) Technology maturity or clinical evidence.
  5. **Strategic Recommendations**: Actionable steps based on the Intent.

## Quality Rules
- **QR-INTENT-001**: The report must directly address the identified Business Intent.
- **QR-LEVEL-001**: The language complexity must match the Decision Level.
- **QR-SOURCE-001**: You must cite sources (e.g., "According to Gartner...", "ClinicalTrials.gov data shows...").

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `market_research_report_generator_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/research_orchestrator.py --help
```

Expected output format:

```text
Result file: market_research_report_generator_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
