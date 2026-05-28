---
name: treatment-plans
description: Generate concise (typically 1–4 pages) patient-centered medical treatment plans in LaTeX/PDF when a clinician needs an actionable plan with SMART goals, evidence-based interventions, monitoring, and HIPAA-aware documentation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to produce a **clinically actionable, professionally typeset** treatment plan (LaTeX → PDF), especially when:

1. You must create an **individualized plan** for a patient across any specialty (medicine, surgery, rehab, behavioral health).
2. You need a **concise “quick reference” plan** (often 1 page) for busy clinical workflows.
3. You are coordinating **multidisciplinary care** (e.g., PCP + specialists + PT/OT + behavioral health) with clear roles and follow-up.
4. You must document **chronic disease management** with measurable targets, monitoring cadence, and escalation thresholds.
5. You need a structured plan for **perioperative care** or **pain management** with safety checks and risk mitigation.

## Key Features

- **Concise formats by default**
  - Preferred: **1-page quick reference card**
  - Standard: **3–4 pages** (front-page executive summary + supporting detail)
  - Extended: **5–6 pages** only when complexity requires it
- **Front-page executive summary (Foundation-style)**
  - Page 1 contains only: title + patient/report info + 2–4 colored “key boxes” (goals, interventions, decision points, timeline)
- **SMART goals**
  - Short- and long-term goals with measurable targets and time bounds
- **Evidence-based interventions with minimal citations**
  - Typically **0–3 brief in-text citations** (e.g., “ADA 2024”)
- **HIPAA-aware documentation**
  - De-identification expectations and documentation hygiene
- **Validation workflow**
  - Completeness and quality checks via scripts (sections present, SMART goals, monitoring adequacy, safety/risk mitigation)
- **Professional LaTeX styling**
  - Custom style package with colored boxes and tables for scan-friendly clinical documents
- **Visual support**
  - Supports adding at least one diagram (e.g., pathway, timeline, decision algorithm) to improve usability

## Dependencies

> Versions may vary by environment; pin them in your project if you need reproducibility.

- **Python**: 3.10+
- **TeX distribution**: TeX Live 2022+ (or MiKTeX equivalent)
- **LaTeX engines**:
  - `xelatex` (recommended)
  - `pdflatex` (supported)
- **Key LaTeX packages** (commonly required by the style/templates):
  - `tcolorbox` (with `most` library), `tikz/pgf`, `geometry`, `xcolor`, `fontspec` (XeLaTeX/LuaLaTeX), `fancyhdr`, `titlesec`, `enumitem`, `booktabs`, `longtable`, `array`, `colortbl`, `hyperref`, `natbib`
- **Project scripts (as referenced by this skill)**:
  - `scripts/generate_template.py`
  - `check_completeness.py`
  - `validate_treatment_plan.py`
  - `timeline_generator.py`
  - (optional) `scripts/generate_schematic.py` for diagram generation

## Example Usage

Below is a complete, runnable example that (1) generates a template, (2) compiles to PDF, and (3) runs validation checks. Adjust paths to match your repository layout.

### 1) Generate a LaTeX template

```bash
cd .claude/skills/treatment-plans/scripts

# Generate a mental health plan template
python generate_template.py --type mental_health --output depression_treatment_plan.tex
```

### 2) (Optional) Generate a diagram for the plan

```bash
# Example: a simple treatment pathway flowchart
python scripts/generate_schematic.py "Depression treatment pathway: assessment -> CBT/SSRI -> monitoring -> escalation criteria" -o figures/depression_pathway.png
```

Include the figure in your `.tex` file (example snippet):

```latex
\begin{figure}[h]
  \centering
  \includegraphics[width=0.95\linewidth]{figures/depression_pathway.png}
  \caption{Treatment pathway overview.}
\end{figure}
```

### 3) Compile to PDF

```bash
# Recommended (better font support)
xelatex depression_treatment_plan.tex

# If you use bibliography features
bibtex depression_treatment_plan || true
xelatex depression_treatment_plan.tex
xelatex depression_treatment_plan.tex
```

### 4) Run completeness and quality validation

```bash
python check_completeness.py depression_treatment_plan.tex
python validate_treatment_plan.py depression_treatment_plan.tex
```

### 5) (Optional) Generate a timeline artifact

```bash
python timeline_generator.py --plan depression_treatment_plan.tex --output timeline.pdf
```

## Implementation Details

### Document length strategy

- Start with the **1-page format** whenever possible.
- Expand to **3–4 pages** only when you need supporting detail (education, coordination, safety monitoring).
- Use **5–6 pages** rarely (multiple comorbidities, complex monitoring, research protocols).

### Front-page executive summary (required pattern)

- Page 1 must be a scan-friendly summary:
  - Title/subtitle
  - Patient/report info box (de-identified)
  - 2–4 colored boxes:
    - **Goals** (SMART bullets)
    - **Core interventions**
    - **Critical decision points / safety thresholds**
    - **Timeline overview**
- Table of contents (if used) begins on page 2; detailed sections follow.

Minimal LaTeX skeleton:

```latex
\maketitle
\thispagestyle{empty}

\begin{patientinfo}
  % De-identified demographics, diagnosis, date, framework
\end{patientinfo}

\begin{goalbox}[Primary Treatment Goals]
  \begin{itemize}
    \item Goal 1 (metric + timeframe)
    \item Goal 2 (metric + timeframe)
  \end{itemize}
\end{goalbox}

\begin{keybox}[Core Interventions]
  \begin{itemize}
    \item Intervention 1 (dose/frequency if applicable)
    \item Intervention 2 (visit cadence / therapy frequency)
  \end{itemize}
\end{keybox}

\begin{warningbox}[Critical Decision Points]
  \begin{itemize}
    \item Escalate if threshold X is met
  \end{itemize}
\end{warningbox}

\newpage
\tableofcontents
\newpage
```

### Core clinical sections (for standard 3–4 page plans)

Include only what changes decisions; prefer tables/bullets:

- Patient info (de-identified), diagnoses (ICD-10 where applicable)
- Assessment summary and risk stratification
- SMART goals (short- and long-term)
- Interventions:
  - pharmacologic (dose/route/frequency/titration + monitoring)
  - non-pharmacologic (lifestyle, therapy, education)
  - procedural/referrals/testing
- Timeline and follow-up schedule
- Monitoring parameters + escalation thresholds
- Expected outcomes (brief)
- Patient education (3–5 key takeaways + red flags)
- Risk mitigation (high-yield safety items only)
- Signature/date block

### Citation policy (minimalist)

- Use **brief in-text citations** only when needed (guidelines, nonstandard regimens, controversial interventions).
- Typical target: **0–3 citations** for a 3–4 page plan.
- Avoid long bibliographies unless explicitly required.

### Validation logic (what scripts should check)

- **Completeness**: required sections exist (goals, interventions, monitoring, follow-up, education, risk mitigation).
- **SMART quality**: goals include metric + timeframe; avoid vague phrasing.
- **Feasibility**: timeline cadence matches interventions; monitoring is realistic.
- **Safety**: contraindications, interaction checks, escalation thresholds, opioid safeguards (if applicable).
- **Compliance hygiene**: de-identification expectations and documentation defensibility.

### Template selection guidance

- `one_page_treatment_plan.tex`: default for most cases (quick reference)
- `general_medical_treatment_plan.tex`: internal medicine / general practice
- `rehabilitation_treatment_plan.tex`: PT/OT/SLP protocols and milestones
- `mental_health_treatment_plan.tex`: psychotherapy + pharmacotherapy + safety plan
- `chronic_disease_management_plan.tex`: long-term targets + coordination
- `perioperative_care_plan.tex`: pre/intra/post-op structure (ERAS, VTE, antibiotics)
- `pain_management_plan.tex`: multimodal analgesia + opioid risk mitigation