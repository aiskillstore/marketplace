---
name: scholar-evaluation
description: Implements the ScholarEval framework to evaluate scholarly documents; trigger when the user provides a PDF/DOCX/TXT file or pasted text and requests critique, scoring, or quality assessment.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Evaluate a research paper, thesis, or proposal and produce a structured critique with scores.
- Generate actionable revision recommendations across core academic writing dimensions.
- Compare multiple drafts/versions of a manuscript using consistent rubric-based scoring.
- Assess submission readiness (e.g., for a conference/journal) and identify major weaknesses.
- Review a document provided as a PDF/DOCX/TXT file when the user expects automatic text extraction.

## Key Features

- **Automatic text extraction** from **PDF/DOCX/TXT** via `scripts/extract_text.py` (intended as the first step for file inputs).
- **ScholarEval rubric** with **8 evaluation dimensions** (see `references/evaluation_framework.md`).
- **Per-dimension scoring (1–5)** with qualitative feedback and concrete recommendations.
- **Weighted score calculation** via `scripts/calculate_scores.py` from a JSON score file.
- Produces a final report summarizing **strengths, weaknesses, and next steps**.

## Dependencies

- Python **3.10+**
- See `requirements.txt` for pinned Python package versions (install via `pip install -r requirements.txt`).

## Example Usage

### A) Evaluate a PDF/DOCX/TXT file (end-to-end)

1) Extract text (run this first for file inputs):
```bash
python scripts/extract_text.py "paper.pdf"
```

2) Create a scores JSON (example: `scores.json`):
```json
{
  "problem_formulation": 4,
  "literature_review": 3,
  "methodology": 4,
  "data_quality": 3,
  "analysis": 4,
  "results": 3,
  "writing_quality": 4,
  "citations": 3
}
```

3) Compute the weighted/aggregate score:
```bash
python scripts/calculate_scores.py --scores scores.json
```

4) Use the extracted text plus the rubric to generate the evaluation report:
- Apply the 8-dimension criteria from `references/evaluation_framework.md`
- Provide per-dimension justification, then summarize strengths/risks and prioritized revisions

### B) Evaluate pasted text (no extraction)

If the user pastes text directly (e.g., abstract, full paper text), skip extraction and evaluate immediately using the 8 dimensions and the 1–5 scale.

## Implementation Details

### File ingestion protocol (for PDF/DOCX/TXT)

- For any user-provided file, run:
  ```bash
  python scripts/extract_text.py "<filename-or-path>"
  ```
- The extraction script is designed to locate the file even if the full path is not provided.
- Use the extracted plain text as the sole input to the evaluation rubric and scoring.

### Evaluation dimensions (8)

The framework evaluates:
1. Problem Formulation  
2. Literature Review  
3. Methodology  
4. Data Quality  
5. Analysis  
6. Results  
7. Writing Quality  
8. Citations  

Detailed criteria and guidance are defined in:
- `references/evaluation_framework.md`

### Scoring scale (1–5)

- **1 — Poor**: Major flaws; not usable as-is.
- **2 — Weak**: Significant issues; major revision required.
- **3 — Average**: Acceptable baseline; improvement needed.
- **4 — Good**: Strong overall; minor issues.
- **5 — Excellent**: High quality; clear impact and rigor.

### Score calculation

- Raw per-dimension scores are stored in a JSON file and passed to:
  ```bash
  python scripts/calculate_scores.py --scores <path_to_scores_json>
  ```
- The script computes an aggregate score (and any configured weighting logic) based on the provided metrics.