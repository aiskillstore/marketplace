---
name: quality-report-generate
description: Generate comprehensive quality report with metrics and verification. Produces final CHAPTER_XX_VERIFICATION.md and quality_metrics.json for deployment approval.
---

# Quality Report Generate Skill

## Purpose

This skill generates the **final quality report** documenting everything about a chapter's generation and validation. The report:

- **Aggregates all validation results** from previous gates
- **Calculates quality metrics** (content size, structure complexity, accuracy)
- **Generates human-readable markdown report** for review
- **Creates machine-readable JSON metrics** for tracking and CI/CD
- **Provides deployment decision** (pass/fail/requires-review)

This is the **final skill before validation gates**, producing the evidence needed to approve or reject a chapter for deployment.

## What to Do

1. **Collect all validation artifacts**
   - Load `validation_structure.json` (Gate 1 results)
   - Load `validation_semantic.json` (Gate 2 results)
   - Load `consolidation_log.json` (consolidation data)
   - Load final `chapter_XX.html` file

2. **Extract metadata from chapter**
   - Parse HTML to extract structure
   - Count content elements (headings, paragraphs, lists)
   - Calculate word count and content size
   - Verify CSS class usage

3. **Calculate quality metrics**
   - Overall validation score (0-100)
   - Structural compliance percentage
   - Semantic compliance percentage
   - Content completeness estimate
   - Accuracy score (if reference data available)

4. **Generate markdown report**
   - Create human-readable verification report
   - Include summary status (✅ PASS / ⚠️ REVIEW / ❌ FAIL)
   - Document all validation results
   - List findings and recommendations

5. **Generate JSON metrics**
   - Machine-readable metrics for tracking
   - Suitable for CI/CD pipelines
   - Enable automated quality dashboards
   - Support trend analysis

6. **Save both report formats**
   - Save: `output/chapter_XX/chapter_artifacts/CHAPTER_XX_VERIFICATION.md`
   - Save: `output/chapter_XX/chapter_artifacts/quality_metrics.json`
   - Timestamp both files
   - Create summary statistics

## Input Files

**Validation reports** (from previous gates):
- `validation_structure.json` - HTML structure validation results
- `validation_semantic.json` - Semantic validation results
- `consolidation_log.json` - Page consolidation metadata

**Chapter content**:
- `chapter_XX.html` - Final consolidated HTML
- `page_artifacts/page_YY/*.html` - Individual page HTML (optional, for analysis)

**Reference data** (optional):
- `page_artifacts/page_YY/02_page_XX.png` - Original PDF pages (for visual comparison)

## Quality Metrics Calculation

### Overall Validation Score (0-100)

```
base_score = 100

# Deduct for structure issues
if structure_errors > 0:
    base_score -= (structure_errors * 10)

# Deduct for semantic issues
if semantic_errors > 0:
    base_score -= (semantic_errors * 5)

# Deduct for warnings
warning_count = structure_warnings + semantic_warnings
base_score -= (warning_count * 2)

# Bonus for semantic classes
if semantic_classes_ratio > 0.8:
    base_score += 5

overall_score = max(0, min(100, base_score))
```

### Content Completeness

```
expected_pages = last_page - first_page + 1
pages_with_content = count_pages_with_substantial_content()
completeness_percent = (pages_with_content / expected_pages) * 100
```

### Structural Compliance

```
checks_passed = structure_validation_checks_passed
checks_total = structure_validation_checks_total
compliance_percent = (checks_passed / checks_total) * 100
```

### Semantic Compliance

```
required_classes = [
    'page-container', 'page-content', 'chapter-header',
    'section-heading', 'paragraph', 'bullet-list'
]
found_classes = [c for c in required_classes if c in html]
compliance_percent = (len(found_classes) / len(required_classes)) * 100
```

## Output: Markdown Report

**Path**: `output/chapter_XX/chapter_artifacts/CHAPTER_XX_VERIFICATION.md`

**Example structure**:

```markdown
# Chapter 2 HTML Accuracy Verification Report

## Summary
**Status**: ✅ **VERIFIED ACCURATE**

The Chapter 2 HTML document has been thoroughly verified for accuracy and quality. All validation gates passed successfully.

---

## Overall Quality Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Overall Quality Score** | 96/100 | ≥85 | ✅ PASS |
| **Structure Validation** | 100% | 100% | ✅ PASS |
| **Semantic Validation** | 98% | ≥90% | ✅ PASS |
| **Content Completeness** | 100% | 100% | ✅ PASS |
| **Visual Accuracy** | 94% | ≥85% | ✅ PASS |

---

## Content Summary

### Pages
- **Book Pages**: 16-29 (14 pages)
- **PDF Indices**: 15-28
- **Chapter**: 2 - Rights in Real Estate

### Content Elements
- **Total Paragraphs**: 156
- **Total Headings**: 28 (1 h1, 4 h2, 23 h4)
- **Total Lists**: 12 (132 total items)
- **Total Tables/Exhibits**: 3
- **Total Images**: 5
- **Total Words**: 12,547

---

## Validation Results

### ✅ HTML Structure Validation (PASSED)

All structural checks passed:
- ✓ HTML5 DOCTYPE valid
- ✓ `<html>`, `<head>`, `<body>` tags properly formed
- ✓ Meta charset and viewport tags present
- ✓ Title tag with descriptive content
- ✓ CSS stylesheet linked correctly
- ✓ `<div class="page-container">` wrapper present
- ✓ `<main class="page-content">` structure valid
- ✓ All tags properly matched and closed
- ✓ No unclosed or improperly nested tags

**Errors**: 0
**Warnings**: 0

### ✅ Semantic Validation (PASSED)

All semantic checks passed:
- ✓ Required CSS classes present and correct
- ✓ Heading hierarchy valid (no jumps, logical flow)
- ✓ All paragraphs properly formatted
- ✓ All lists correctly structured
- ✓ Tables properly formatted
- ✓ Semantic class usage consistent throughout
- ✓ Page maintains continuous format (no pagination)

**Errors**: 0
**Warnings**: 0

### ✅ Visual Accuracy Check (PASSED)

Comparison with original PDF pages:
- Overall similarity: 94%
- Page-by-page average: 94%
- All pages ≥ 85% threshold
- Layout matches original
- Content positioning accurate
- Text rendering correct

---

## Consolidation Details

**Chapter Opening**: Page 16 (Chapter header and navigation included)
**Consolidation**: Pages 16-29 merged into single continuous document
**Pages Merged**: 14
**Page Headers Removed**: 13 (continuation pages)
**Duplicate Content**: None detected

**Consolidation Log**:
```json
{
  "pages_merged": 14,
  "pages_include": [...],
  "heading_hierarchy": {
    "h1": 1,
    "h2": 4,
    "h4": 23
  },
  "content_statistics": {
    "paragraphs": 156,
    "lists": 12,
    "tables": 3,
    "images": 5,
    "total_words": 12547
  }
}
```

---

## CSS Classes Used

**Core Structure**: page-container, page-content, chapter-header (6 classes)
**Content**: section-heading, subsection-heading, paragraph, bullet-list, bullet-item (12 classes)
**Exhibits**: exhibit, exhibit-table, exhibit-title, exhibit-header (4 classes)
**Navigation**: section-navigation, nav-item (2 classes)
**Special**: section-divider, page-footer (2 classes)

**Total unique classes**: 26
**Classes found as required**: 6/6 (100%)

---

## Issues & Findings

### ✅ No Critical Issues Found
- ✓ No missing sections
- ✓ No missing content
- ✓ No structural problems
- ✓ No broken internal links
- ✓ No invalid HTML
- ✓ No semantic violations

### ⚠️ Minor Notes
- None - all validation gates passed

---

## Generation Process

**Extraction**: Rich data extracted from PDF pages (text, fonts, images)
**ASCII Preview**: Structural layout created for AI reference
**AI Generation**: Individual pages generated using 3-input approach:
- Visual reference (PNG rendering of PDF)
- Parsed text data (JSON with metadata)
- Layout structure (ASCII preview)
**Structure Validation**: HTML5 compliance verified
**Consolidation**: Pages merged into continuous chapter
**Semantic Validation**: Structure and classes verified
**Quality Report**: Final metrics and status

---

## Accuracy Assessment

| Criterion | Result | Assessment |
|-----------|--------|------------|
| **Content Completeness** | 100% | All sections present |
| **Page Coverage** | 14/14 | All pages included |
| **Heading Accuracy** | ✅ | Correct hierarchy |
| **List Accuracy** | ✅ | All items present |
| **Table Accuracy** | ✅ | Proper formatting |
| **Image References** | ✅ | Correct paths |
| **Semantic Structure** | ✅ | Proper classes |
| **Visual Fidelity** | 94% | Matches original layout |

---

## Recommendation

✅ **APPROVED FOR DEPLOYMENT**

This chapter has passed all quality gates:
1. ✓ HTML structure is valid
2. ✓ Semantic requirements met
3. ✓ Content is complete and accurate
4. ✓ Visual appearance matches original
5. ✓ Ready for production use

**Next Steps**:
- Deploy to production website
- Monitor user feedback
- Archive validation artifacts
- Proceed with next chapter

---

## Technical Details

**Generated**: 2025-11-08T14:40:00Z
**Generator**: Calypso Quality Report System
**Report Version**: 2.0
**Chapter**: 2
**Status**: ✅ PASSED ALL GATES

```json
{
  "report_metadata": {
    "chapter": 2,
    "generated_at": "2025-11-08T14:40:00Z",
    "validation_status": "PASS",
    "overall_score": 96,
    "deployable": true
  }
}
```

---

**Report prepared by**: Calypso Verification Pipeline
**Quality Standards Version**: 2025-11-08
**Verification Status**: ✅ PASSED
```

## Output: JSON Metrics

**Path**: `output/chapter_XX/chapter_artifacts/quality_metrics.json`

```json
{
  "chapter": 2,
  "title": "Rights in Real Estate",
  "book_pages": "16-29",
  "pdf_indices": "15-28",
  "report_generated_at": "2025-11-08T14:40:00Z",
  "overall_status": "PASS",
  "overall_quality_score": 96,
  "deployment_approved": true,
  "validation_results": {
    "structure_validation": {
      "status": "PASS",
      "checks_passed": 10,
      "checks_failed": 0,
      "checks_total": 10,
      "compliance_percent": 100,
      "errors": [],
      "warnings": []
    },
    "semantic_validation": {
      "status": "PASS",
      "checks_passed": 8,
      "checks_failed": 0,
      "checks_total": 8,
      "compliance_percent": 100,
      "errors": [],
      "warnings": []
    },
    "visual_accuracy": {
      "status": "PASS",
      "overall_similarity": 0.94,
      "threshold": 0.85,
      "page_results": [
        {
          "page": 16,
          "similarity": 0.96,
          "status": "PASS"
        },
        {
          "page": 17,
          "similarity": 0.93,
          "status": "PASS"
        }
        // ... all pages
      ]
    }
  },
  "content_metrics": {
    "total_pages": 14,
    "total_headings": 28,
    "heading_breakdown": {
      "h1": 1,
      "h2": 4,
      "h3": 0,
      "h4": 23
    },
    "total_paragraphs": 156,
    "total_lists": 12,
    "total_list_items": 132,
    "total_tables": 3,
    "total_images": 5,
    "total_words": 12547,
    "estimated_reading_time_minutes": 45
  },
  "structure_metrics": {
    "css_classes_found": 26,
    "required_classes_present": 6,
    "required_classes_total": 6,
    "page_container_valid": true,
    "page_content_valid": true,
    "continuous_format": true,
    "heading_hierarchy_valid": true
  },
  "content_completeness": {
    "expected_pages": 14,
    "pages_with_content": 14,
    "completeness_percent": 100,
    "sections_verified": [
      "Chapter Header",
      "Real Property Rights",
      "Physical Characteristics",
      "Interdependence",
      "Government Rights",
      "Regulations and Licensing"
    ]
  },
  "quality_assessment": {
    "accuracy_level": "HIGH",
    "confidence_level": "HIGH",
    "ready_for_deployment": true,
    "requires_manual_review": false,
    "requires_fixes": false
  }
}
```

## Implementation

Generate report using Python script:

```bash
cd Calypso/tools

# Generate quality report
python3 generate_quality_report.py \
  --chapter 2 \
  --html-file "../output/chapter_02/chapter_artifacts/chapter_02.html" \
  --validation-structure "../output/chapter_02/chapter_artifacts/validation_structure.json" \
  --validation-semantic "../output/chapter_02/chapter_artifacts/validation_semantic.json" \
  --consolidation-log "../output/chapter_02/chapter_artifacts/consolidation_log.json" \
  --output-dir "../output/chapter_02/chapter_artifacts"
```

## Report Contents

The markdown report includes:

1. **Executive Summary** - Quick status overview
2. **Quality Metrics Table** - Key metrics vs targets
3. **Content Summary** - Page count, element counts
4. **Validation Results** - Structure and semantic checks
5. **Consolidation Details** - Page merge information
6. **CSS Classes** - Class usage summary
7. **Issues & Findings** - Any problems found
8. **Generation Process** - How content was created
9. **Accuracy Assessment** - Verification against criteria
10. **Recommendation** - Deploy or review needed
11. **Technical Details** - Metadata and timestamps

## Success Criteria

✓ Markdown report created with comprehensive information
✓ JSON metrics valid and machine-parseable
✓ Quality score calculated correctly
✓ All validation results aggregated
✓ Content metrics accurate
✓ Deployment recommendation provided
✓ Report ready for stakeholder review

## Report Usage

**For stakeholders**: Read markdown report for human-friendly overview
**For CI/CD**: Parse JSON metrics for automated decisions
**For archival**: Both formats saved for audit trail
**For monitoring**: JSON feeds quality dashboards

## Next Steps

Once quality report is generated:
1. **Quality Gate 3** (visual-accuracy-check) performs final visual validation
2. If all gates pass: Chapter approved for deployment
3. If gates fail: Report flags issues, user reviews and fixes

## Design Notes

- Combines data from all previous validations
- Generates both human and machine-readable formats
- Provides decision support (approve/review/fix)
- Creates permanent audit record
- Ready for automated quality tracking
