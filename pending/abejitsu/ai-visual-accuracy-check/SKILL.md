---
name: ai-visual-accuracy-check
description: Use AI to compare rendered HTML to original PDF page. AI makes contextual judgment about visual accuracy with explainable reasoning. BLOCKING quality gate - stops pipeline if score below 85%.
---

# AI Visual Accuracy Check Skill

## Purpose

This is a **BLOCKING quality gate** that uses **AI to validate visual accuracy** of generated HTML against the original PDF page. Unlike pixel-perfect comparison, AI understands:

- Visual hierarchy and layout intent
- Contextual differences (web rendering vs PDF)
- Whether readers would have similar experience
- Trade-offs between CSS limitations and HTML accuracy

The AI provides:
- Objective similarity score (0-100%)
- Breakdown by evaluation criteria
- Specific differences noted
- Clear pass/fail recommendation
- Explanation for decisions

This combines **AI's contextual understanding** with **deterministic gating** (must pass 85+ to continue).

## What to Do

1. **Load input files**
   - Read `chapter_XX.html` (generated consolidated HTML)
   - Read `02_page_XX.png` (original PDF page image)

2. **Render HTML to image**
   - Use headless browser (Playwright/Selenium) to render HTML as PNG
   - Capture full page screenshot
   - Save rendered image for comparison

3. **Invoke Claude with visual comparison**
   - Attach original PDF PNG as image 1
   - Attach rendered HTML screenshot as image 2
   - Request detailed visual comparison
   - Ask AI to score on multiple criteria

4. **Parse AI response**
   - Extract overall similarity score
   - Extract criterion-specific scores
   - Parse differences noted
   - Get recommendation (PASS/FAIL)

5. **Save comparison report**
   - Save to: `output/chapter_XX/chapter_artifacts/ai_visual_accuracy.json`
   - Include timestamp, inputs used, AI model

6. **Make gate decision**
   - If score ≥ 85: PASS (exit code 0, continue)
   - If score < 85: FAIL (exit code 1, trigger hook)

## Input Parameters

```
html_file: <str>          - Path to chapter_XX.html
pdf_page_png: <str>       - Path to original PDF page PNG (or multiple for multi-page)
output_dir: <str>         - Directory for report
chapter: <int>            - Chapter number (for reporting)
book_pages: <str>         - Page range (for reporting)
threshold: <float>        - Minimum score to pass (default: 85.0)
```

## AI Prompt Template

```
You are validating the visual accuracy of a generated HTML page against the original PDF.

ORIGINAL PDF PAGE:
[PNG Image of original PDF page attached]

GENERATED HTML (Rendered):
[PNG Image of rendered HTML page attached]

TASK:
Compare these two images and determine if the HTML accurately recreates the visual appearance and layout of the PDF page.

EVALUATION CRITERIA:

1. Layout Match (40% weight)
   - Overall page structure matches original
   - Sections in correct order and position
   - Spacing between elements appropriate
   - Page dimensions/aspect ratio similar

2. Visual Hierarchy (30% weight)
   - Headings stand out with appropriate prominence
   - Section breaks clearly visible
   - Emphasis (bold, italic) preserved or equivalent
   - Visual relationships between elements clear

3. Content Positioning (20% weight)
   - Elements aligned correctly (left, center, right)
   - Lists indented with proper spacing
   - Tables/exhibits positioned and aligned correctly
   - Paragraph flow matches original

4. Typography & Styling (10% weight)
   - Font sizes relative to each other correct
   - Text styling appropriate (bold, italic, caps)
   - Color scheme preserved (if applicable)
   - Overall readability equivalent or better

SCORING GUIDELINES:

For each criterion:
- 90-100%: Excellent, no issues
- 80-89%: Good, minor cosmetic differences
- 70-79%: Acceptable, noticeable but not critical
- Below 70%: Poor, significant differences

IMPORTANT CONTEXT:
- HTML rendering in browser may differ slightly from PDF (spacing, fonts)
- Focus on INTENT and READABILITY, not pixel-perfect match
- Small spacing/margin differences (2-5px) are acceptable
- Font rendering differences are acceptable if hierarchy preserved
- Web rendering constraints are acceptable (no absolute PDF positioning)

OUTPUT FORMAT:

Provide your analysis in this exact JSON format:

```json
{
  "overall_score": 92.5,
  "threshold": 85.0,
  "recommendation": "PASS",
  "criteria_analysis": {
    "layout_match": {
      "score": 94,
      "feedback": "Overall page structure matches well. Section order correct, spacing appropriate."
    },
    "visual_hierarchy": {
      "score": 90,
      "feedback": "Headings clearly distinguished. Visual relationships preserved. Minor font size variance acceptable."
    },
    "content_positioning": {
      "score": 91,
      "feedback": "Element alignment correct. Lists properly indented. Tables positioned correctly."
    },
    "typography_styling": {
      "score": 88,
      "feedback": "Text styling preserved. Bold and italic distinctions clear. Readability excellent."
    }
  },
  "differences_noted": [
    "Paragraph line-height 1.6 vs 1.5 in PDF (acceptable, improves readability)",
    "Bullet list indentation 20px vs 15px in PDF (acceptable, clear and readable)"
  ],
  "visual_fidelity_assessment": "EXCELLENT",
  "confidence_level": 0.95,
  "explanation": "The HTML accurately recreates the PDF page layout and visual hierarchy. All major elements are positioned correctly. Minor spacing and font differences are within acceptable tolerances for web rendering and actually improve readability.",
  "pass_fail_verdict": "PASS"
}
```

VALIDATION:
- Overall score must be numeric (0-100)
- All criteria must have scores
- Recommendation must be PASS or FAIL
- Explanation must be clear and actionable
```

## Process Flow

```
┌─ Load HTML & PNG ──────────────────┐
│ • chapter_XX.html                  │
│ • 02_page_XX.png                   │
└────────┬────────────────────────────┘
         │
         ▼
┌─ Render HTML to PNG ───────────────┐
│ • Headless browser                 │
│ • Full page screenshot             │
│ • Save to temp location            │
└────────┬────────────────────────────┘
         │
         ▼
┌─ Invoke Claude API ────────────────┐
│ • Send original PDF PNG            │
│ • Send rendered HTML PNG           │
│ • Multi-modal comparison prompt    │
│ • Request JSON response            │
└────────┬────────────────────────────┘
         │
         ▼
┌─ Parse & Save Report ──────────────┐
│ • Extract JSON from response       │
│ • Validate score 0-100             │
│ • Save to JSON file                │
└────────┬────────────────────────────┘
         │
         ▼
┌─ Gate Decision ────────────────────┐
│ • If score ≥ 85: PASS              │
│ • If score < 85: FAIL              │
└────────┬────────────────────────────┘
         │
         ▼
  Exit with code 0 or 1
```

## Output File Format

**Path**: `output/chapter_XX/chapter_artifacts/ai_visual_accuracy.json`

```json
{
  "chapter": 2,
  "book_pages": "16-29",
  "validation_type": "ai_visual_accuracy",
  "validation_timestamp": "2025-11-08T14:45:00Z",
  "overall_score": 92.5,
  "threshold": 85.0,
  "status": "PASS",
  "ai_model": "claude-3-5-sonnet-20241022",
  "inputs": {
    "html_file": "chapter_02.html",
    "original_pdf_png": "02_page_16.png",
    "rendered_html_png": "rendered_chapter_02.png"
  },
  "criteria_scores": {
    "layout_match": 94,
    "visual_hierarchy": 90,
    "content_positioning": 91,
    "typography_styling": 88
  },
  "differences": [
    "Paragraph line-height 1.6 vs 1.5 in PDF (acceptable)",
    "Bullet list indentation 20px vs 15px in PDF (acceptable)"
  ],
  "visual_fidelity": "EXCELLENT",
  "confidence": 0.95,
  "explanation": "The HTML accurately recreates the PDF page layout and visual hierarchy...",
  "recommendation": "PASS",
  "notes": "All criteria well within acceptable ranges. Minor web rendering differences do not impact readability or intent."
}
```

## Multi-Page Chapters

For chapters spanning multiple pages:

1. **Option A: Compare key pages**
   - Compare opening page (establishes style)
   - Compare middle pages (continuation pages)
   - Compare final pages (consistency check)
   - Average scores across pages

2. **Option B: Compare consolidated view**
   - Render full consolidated chapter
   - Compare overall structure
   - Spot-check specific pages visually

**Approach**: Use Option A for thorough validation
- Score each page separately (0-100)
- Average to get overall score
- Report per-page breakdown

## Gate Decision Threshold

```
Score ≥ 85:  PASS  → Continue to deployment
Score < 85:  FAIL  → Trigger hook, block pipeline

Interpretation:
  90-100: Excellent, no concerns
  85-89:  Good, minor cosmetic differences acceptable
  < 85:   Requires review and likely fixes
```

## Error Handling

**If HTML rendering fails**:
- Log error with details
- Try alternative rendering method
- Escalate if both fail

**If AI response is invalid JSON**:
- Request retry
- Fall back to text parsing if needed
- Escalate if repeated failures

**If score seems wrong (too high/low)**:
- AI's judgment takes precedence
- Trust AI's contextual understanding
- Log for future analysis

**If original PNG is missing**:
- Use reference page from PDF directly
- Or extract from PDF again
- Proceed with best available image

## Quality Checks

Before saving report:

1. **Score validity**
   - [ ] Overall score 0-100
   - [ ] All criteria scores 0-100
   - [ ] Scores reasonable and justified

2. **Report completeness**
   - [ ] All criteria included
   - [ ] Differences documented
   - [ ] Explanation provided
   - [ ] Recommendation clear

3. **AI reasoning**
   - [ ] Explanation matches score
   - [ ] Differences explain score deductions
   - [ ] Confidence level appropriate

## Success Criteria

✓ Visual accuracy report generated successfully
✓ Overall score calculated and justified
✓ All criteria scored and explained
✓ Differences clearly documented
✓ Pass/fail decision clear
✓ Exit code 0 if PASS, 1 if FAIL
✓ Report saved in JSON format

## Next Steps After PASS

If validation passes (score ≥ 85):
1. Gate decision: PASS
2. Continue to deployment approval
3. Chapter ready for production

## Next Steps After FAIL

If validation fails (score < 85):
1. **PIPELINE STOPS**
2. Hook `calypso-visual-accuracy.sh` triggered
3. User receives report with visual comparison details
4. Options:
   - Review differences and re-generate
   - Adjust CSS styling
   - Lower threshold if differences acceptable
   - Manual override if justified

## Design Notes

- This skill is **AI-powered** (probabilistic)
- Uses **visual reasoning** (not pixel-diff)
- Makes **contextual judgments** (understands intent)
- Provides **explainable decisions** (clear reasoning)
- Acts as **BLOCKING gate** (score must pass threshold)
- Part of **quality assurance** (ensures visual accuracy)

## Testing

To test AI visual accuracy:

```bash
# Generate chapter HTML (previous steps)
# Render to PNG
# Compare with original PDF

# Expected behavior:
# - AI compares images
# - Scores layout, hierarchy, positioning, typography
# - Generates report with score and explanation
# - Returns PASS (score ≥ 85) or FAIL (score < 85)
```

## Key Advantage Over Python Pixel-Diff

| Aspect | Python Pixel-Diff | AI Visual Comparison |
|--------|------------------|----------------------|
| **Understanding** | Detects changes | Understands intent |
| **Flexibility** | Exact match required | Accepts valid variations |
| **Explanation** | Pixel coordinates | Semantic feedback |
| **Tolerance** | Binary (match/no match) | Graduated (85%+ acceptable) |
| **Context** | No context | Full visual context |
| **Human-like** | No | Yes, like QA reviewer |

AI visual accuracy validation is **smarter and more human-like** than pixel-perfect comparison.
