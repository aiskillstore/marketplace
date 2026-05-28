---
name: hypothesis-generation
description: Structured scientific hypothesis formulation from observations; use when you have experimental observations or preliminary data and need testable hypotheses with predictions, mechanisms, and validation experiments.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Hypothesis Generation (Scientific)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Structured scientific hypothesis formulation from observations; use when you have experimental observations or preliminary data and need testable hypotheses with predictions, mechanisms, and validation experiments.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Reusable packaged asset(s), including `assets/FORMATTING_GUIDE.md`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Protocol Design/hypothesis-generation
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Packaged assets: reusable files are available under `assets/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need to turn observations into **testable, mechanistic hypotheses** and a **validation plan**, for example:

- You have experimental observations (e.g., an unexpected phenotype, trend, or anomaly) and need 3-5 competing explanations with clear mechanisms.
- You have preliminary data and must propose **testable predictions** and **decisive experiments** to discriminate between hypotheses.
- You are preparing a mechanistic study plan (molecular/cellular/system/population) and need a structured framework for causal reasoning.
- You are doing literature-grounded hypothesis development and want to identify gaps, contradictions, and plausible mechanisms.
- You need a publication-ready hypothesis report (LaTeX) with concise main claims and a detailed appendix.

## 2. Key Features

- **Scientific workflow**: observation framing → literature search → evidence synthesis → competing hypotheses → quality evaluation → experiments → predictions → structured report.
- **Competing hypotheses (3-5)**: distinct, mechanistic explanations at appropriate biological/physical scales.
- **Quality criteria**: testability, falsifiability, parsimony, explanatory power, scope, consistency, novelty (see `references/hypothesis_quality_criteria.md`).
- **Experiment design patterns**: lab, observational, clinical, computational; controls, confounders, and measurement plans (see `references/experimental_design_patterns.md`).
- **Prediction-first outputs**: quantitative/conditional predictions that differentiate hypotheses and specify falsifiers.
- **Report packaging**: LaTeX template with colored boxes and a strict main-body length budget (see `assets/hypothesis_report_template.tex`, `assets/hypothesis_generation.sty`, `assets/FORMATTING_GUIDE.md`).
- **Mandatory visuals**: every hypothesis report must include **at least 1-2 AI-generated schematics** created via the `scientific-schematics` skill.

## 3. Dependencies

- **LaTeX engine**: XeLaTeX or LuaLaTeX
- **BibTeX**: for reference compilation
- **Required LaTeX packages** (used by `assets/hypothesis_generation.sty`):
  - `tcolorbox`, `xcolor`, `fontspec`, `fancyhdr`, `titlesec`, `enumitem`, `booktabs`, `natbib`
- **Python (optional, for schematic generation script)**: Python 3.10+ recommended
- **Related skill dependency (mandatory for reports)**: `scientific-schematics` (for 1-2+ diagrams per report)

## 4. Example Usage

### A) Generate required schematics (at least 1-2)

```bash
python scripts/generate_schematic.py "Diagram showing 3 competing mechanistic hypotheses linking Observation X to Outcome Y, with key intermediates and predicted readouts." -o figures/hypothesis_framework.png

python scripts/generate_schematic.py "Experimental design flowchart comparing interventions A/B and controls, with primary/secondary endpoints and decision points." -o figures/experimental_design.png
```

### B) Create a LaTeX report using the provided template

1) Copy the template assets into a working directory:

```bash
mkdir -p hypothesis_report figures
cp assets/hypothesis_report_template.tex hypothesis_report/hypothesis_report.tex
cp assets/hypothesis_generation.sty hypothesis_report/
```

2) Edit `hypothesis_report/hypothesis_report.tex` to include:
- Executive summary
- 3-5 hypothesis boxes (each on a fresh page)
- Predictions and critical comparisons
- Appendix A-D with detailed literature, protocols, and evaluations
- References (BibTeX)

3) Compile:

```bash
cd hypothesis_report
xelatex hypothesis_report.tex
bibtex hypothesis_report
xelatex hypothesis_report.tex
xelatex hypothesis_report.tex
```

### C) Minimal LaTeX snippet demonstrating the required structure

```latex
\documentclass{article}
\usepackage{hypothesis_generation}
\usepackage{natbib}

\begin{document}

\begin{summarybox}
\textbf{Executive Summary.} Observation X shows pattern Y under condition Z. We propose 3 competing mechanisms and outline decisive experiments and predictions.
\end{summarybox}

\newpage
\begin{hypothesisbox1}[Hypothesis 1: Mechanism A]
\textbf{Mechanistic explanation.} Brief causal chain describing how A produces Y under Z.

\textbf{Key supporting evidence.}
\begin{itemize}
  \item Evidence point 1 \citep{author2023}.
  \item Evidence point 2 \citep{author2021}.
\end{itemize}

\textbf{Core assumptions.}
\begin{itemize}
  \item Assumption 1.
\end{itemize}
\end{hypothesisbox1}

\newpage
\begin{hypothesisbox2}[Hypothesis 2: Mechanism B]
% Keep concise; move details to Appendix.
\end{hypothesisbox2}

\begin{predictionbox}
\textbf{Testable predictions.}
\begin{itemize}
  \item If Hypothesis 1 is correct, intervention I increases readout R by ~20-40\% under Z.
  \item If Hypothesis 2 is correct, R does not change, but marker M shifts directionally.
\end{itemize}
\end{predictionbox}

\begin{comparisonbox}
\textbf{Critical comparisons.} Prioritize experiments that maximally separate predictions across hypotheses.
\end{comparisonbox}

\end{document}
```

## 5. Implementation Details

### 5.1 End-to-end workflow (recommended)

1. **Define the phenomenon**
   - State the observation/pattern to explain, scope, constraints, and what is known vs unknown.
2. **Literature search**
   - Use domain-appropriate sources (e.g., PubMed for biomedical topics; general scholarly search otherwise).
   - Apply strategies in `references/literature_search_strategies.md`.
3. **Evidence synthesis**
   - Summarize consensus mechanisms, contradictions, and gaps; extract candidate causal links.
4. **Generate 3-5 competing hypotheses**
   - Each must be mechanistic (how/why), distinct, and grounded in evidence or plausible analogies.
5. **Evaluate hypothesis quality**
   - Use criteria in `references/hypothesis_quality_criteria.md`:
     - Testability, falsifiability, parsimony, explanatory power, scope, consistency, novelty.
   - Record strengths/weaknesses explicitly.
6. **Design experimental tests**
   - Use patterns in `references/experimental_design_patterns.md`.
   - Specify: measurements, controls, comparisons, confounders, sample size/statistics (as appropriate).
7. **Formulate testable predictions**
   - Provide discriminative predictions (direction, magnitude when possible), boundary conditions, and falsifiers.
8. **Produce structured report**
   - Use `assets/hypothesis_report_template.tex` and `assets/hypothesis_generation.sty`.
   - Include **1-2+ schematics** generated via `scientific-schematics`.

### 5.2 Mandatory schematic requirement

- Every hypothesis generation report must include **at least 1-2 diagrams** (framework, mechanism, experimental flowchart, decision tree, causal graph).
- Reports without visuals are considered incomplete.
- Recommended placement: one schematic in the main body (overview), additional schematics in the appendix (mechanisms/experimental details).

### 5.3 LaTeX formatting constraints (overflow prevention)

- The main body should be **≤ 4 pages** (template-guided).
- Insert `\newpage` **before each hypothesis box**; `tcolorbox` environments do not reliably break across pages.
- Keep each hypothesis box to roughly **0.5-0.6 page**:
  - Mechanism: 1-2 short paragraphs (≈ 6-10 sentences)
  - Evidence: 2-3 bullets with key citations
  - Assumptions: 1-2 bullets
- Move extended rationale, extra citations, and protocol details to the appendix.

### 5.4 Citation targets

- Main body: ~10-15 carefully selected citations (only the most decisive evidence).
- Appendix A: ~40-70+ citations for comprehensive coverage.
- Total references goal: **50+** entries when the topic warrants it.
- Use `\citep{author2023}` for parenthetical citations (per template conventions).

### 5.5 Included repository resources

- `references/hypothesis_quality_criteria.md`: evaluation rubric for hypothesis strength.
- `references/experimental_design_patterns.md`: reusable experimental design templates.
- `references/literature_search_strategies.md`: search tactics for PubMed and general scientific sources.
- `assets/hypothesis_generation.sty`: colored box environments and report styling.
- `assets/hypothesis_report_template.tex`: full report template (main body + appendix).
- `assets/FORMATTING_GUIDE.md`: examples and troubleshooting for box usage and layout.

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
- If a file is produced, prefer a deterministic output name such as `hypothesis_generation_result.md` unless the skill documentation defines a better convention.
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
Result file: hypothesis_generation_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
