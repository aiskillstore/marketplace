---
name: security-report
description: |
  Generate security assessment reports in docx format with findings, 
  risk ratings, and remediation recommendations.
  
  Use when: User asks for security audit report, vulnerability assessment 
  document, penetration test report, or compliance gap analysis document.
  Keywords: security report, audit findings, vulnerability report, pentest report
---

# Security Report Generator

## Quick Start

```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()
doc.add_heading('Security Assessment Report', 0)
```

## Core Workflow

1. Create document with standard sections (see structure below)
2. Apply risk rating colors (Critical=red, High=orange, Medium=yellow, Low=green)
3. Generate findings table with severity sorting
4. Add remediation timeline
5. Save to `/mnt/user-data/outputs/`

## Document Structure

```
1. Executive Summary (1 page max)
2. Scope & Methodology
3. Risk Summary (table + chart)
4. Detailed Findings (sorted by severity)
   - Finding ID
   - Title
   - Severity + CVSS
   - Description
   - Evidence
   - Remediation
   - References
5. Remediation Roadmap
6. Appendices
```

## Critical Gotchas

- **Table borders**: Must set each cell border explicitly, no table-level setting
- **Color codes**: Use RGBColor(r,g,b), not hex strings
- **Page breaks**: Add before major sections with `doc.add_page_break()`

## Risk Rating Colors

```python
RISK_COLORS = {
    'Critical': RGBColor(192, 0, 0),    # Dark red
    'High': RGBColor(255, 102, 0),      # Orange  
    'Medium': RGBColor(255, 192, 0),    # Yellow
    'Low': RGBColor(0, 176, 80),        # Green
    'Info': RGBColor(91, 155, 213)      # Blue
}
```

## Advanced Features

- [EXECUTIVE_SUMMARY.md](references/EXECUTIVE_SUMMARY.md) - C-level friendly language
- [CVSS_CALCULATOR.md](references/CVSS_CALCULATOR.md) - Scoring methodology
