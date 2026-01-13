# Simple Deck Template

Use this template for presentations with ≤15 slides that can be generated in a single conversation context.

## Template Structure

```
[WORKFLOW ENFORCEMENT]
Use html2pptx workflow only. Debug any installation issues; do not switch to alternative 
approaches. Read entire pptx skill documentation first, then confirm which workflow you'll 
use before proceeding.

[DESIGN RESTRICTIONS]
• NO BORDER BOXES around text elements
• NO OUTLINE SHAPES containing text content
• NO ROUNDED RECTANGLES with text inside
• Use clean typography, spacing, and subtle color blocks instead
• Text should sit directly on slide background or solid color areas

[PRE-EXECUTION DESIGN PLAN]
Before writing any code, describe:
- Clean layout approach without border elements
- Color palette (high contrast, no outlined text boxes)
- Typography hierarchy and spacing strategy
- Visual emphasis through color blocks, not borders

[OBJECTIVE]
Generate PowerPoint slide deck from [describe data/purpose] addressing [specific goals].

[INPUTS]
• [Data source 1]: filename1.csv
• [Data source 2]: filename2.txt
• [Data source 3]: filename3.pdf

[LAYOUT APPROACH]
• Clean white or light colored backgrounds
• Text directly on background (no containers)
• Visual separation through spacing and typography
• Colored accent bars or background sections (not outlined boxes)
• Subtle background color zones instead of bordered elements

[ACCESSIBILITY & CONTRAST REQUIREMENTS]
• All text must have minimum 4.5:1 contrast ratio
• No dark text on dark backgrounds
• Light backgrounds with dark text preferred
• Test readability at thumbnail size

[LAYOUT CONSTRAINTS]
• Maximum 3 bullets per slide
• 18pt minimum font size (24pt for titles)
• 0.5" minimum margins on all sides
• No overlapping text elements
• Single visual element per slide maximum
• NO BORDERED TEXT BOXES OR OUTLINE SHAPES

[SLIDE-BY-SLIDE REQUIREMENTS]
Slide 1: [Title and purpose]
- [Specific content requirements]
- [Visual emphasis points]

Slide 2: [Section title]
- [Content specifications]
- [Data to include]

[Continue for each slide...]

[VALIDATION GATES]
After generation, please:
• Show thumbnail preview
• Verify contrast ratios (calculate and display)
• Confirm no border boxes or outline shapes present
• Test readability at reduced size
• Validate font sizes meet minimums
• Check margin measurements

[FAILURE CONDITIONS]
If you encounter any of these, STOP and report:
• Generic slides without specific insights
• Missing synthesis of data
• Charts without clear decision implications
• Visual elements that don't support narrative
• Any deviation from design restrictions
```

## Example: Financial Analysis Deck

```
[WORKFLOW ENFORCEMENT]
Use html2pptx workflow only. Debug any installation issues; do not switch to alternative 
approaches. Read entire pptx skill documentation first, then confirm which workflow you'll 
use before proceeding.

[DESIGN RESTRICTIONS]
• NO BORDER BOXES around text elements
• NO OUTLINE SHAPES containing text content
• NO ROUNDED RECTANGLES with text inside
• Use clean typography, spacing, and subtle color blocks instead
• Text should sit directly on slide background or solid color areas

[PRE-EXECUTION DESIGN PLAN]
Before writing any code, describe:
- Clean layout approach without border elements
- Color palette (high contrast, no outlined text boxes)
- Typography hierarchy and spacing strategy
- Visual emphasis through color blocks, not borders

[OBJECTIVE]
Generate PowerPoint slide deck from Q3 2024 financial data addressing budget concerns 
and competitive threats for executive review.

[INPUTS]
• Financial CSV: enterprise_financial_data.csv
• Executive memo: executive_memo_q3_2024.txt
• Email thread: email_thread_budget_conflict.txt

[LAYOUT APPROACH]
• Clean white backgrounds
• Dark navy text (#1a1a2e) for maximum contrast
• Accent color: Corporate blue (#0066cc) for emphasis bars
• Typography: 24pt bold titles, 18pt body text, clean sans-serif
• Visual separation through generous spacing (never borders)
• Color blocks for section emphasis (light blue #e6f2ff backgrounds)

[ACCESSIBILITY & CONTRAST REQUIREMENTS]
• All text must have minimum 4.5:1 contrast ratio (will verify)
• No dark text on dark backgrounds
• Primary: Dark text on white background
• Accents: Dark text on light blue background
• Test readability at thumbnail size

[LAYOUT CONSTRAINTS]
• Maximum 3 bullets per slide
• 18pt minimum font size (24pt for titles)
• 0.5" minimum margins on all sides
• No overlapping text elements
• Single chart per slide maximum
• NO BORDERED TEXT BOXES OR OUTLINE SHAPES

[SLIDE-BY-SLIDE REQUIREMENTS]

Slide 1: Executive Summary
- Title: "Q3 2024 Financial Review: Budget Analysis & Competitive Response"
- 3 key takeaways maximum
- Each takeaway on separate visual line with generous spacing
- Use subtle color block for emphasis (not borders)

Slide 2: Revenue Overview
- Title: "Revenue Performance: Q3 2024"
- Simple bar chart comparing planned vs actual
- 3 key insights as bullets below chart
- Highlight variance with color (not outlined boxes)

Slide 3: Cost Structure Analysis
- Title: "Cost Breakdown & Budget Variance"
- Clean pie chart or horizontal bar chart
- Label major cost categories directly on chart
- 2-3 bullets explaining significant changes

Slide 4: Competitive Landscape
- Title: "Market Position & Competitive Threats"
- Simple comparison table or chart
- 3 bullets maximum explaining strategic implications
- Use color blocks to show our position vs competitors

Slide 5: Recommendations
- Title: "Strategic Actions: Q4 2024"
- 3 clear recommendations
- Each with brief rationale (sub-bullet)
- Use accent color bar to emphasize priority action

[VALIDATION GATES]
After generation, please:
• Show thumbnail preview of all slides
• Verify contrast ratios (calculate and display):
  - Navy text on white: should be >12:1
  - Navy text on light blue: should be >7:1
• Confirm zero border boxes or outline shapes present
• Test readability at 25% size
• Validate all font sizes ≥18pt (≥24pt for titles)
• Measure margins ≥0.5" on all slides
• Verify maximum 3 bullets per slide

[FAILURE CONDITIONS]
If you encounter any of these, STOP and report:
• Unable to extract meaningful insights from financial data
• Data inconsistencies between sources
• Charts too complex for single-visual-element constraint
• Contrast ratios below 4.5:1
• Any border boxes or outline shapes appearing
• Text overlapping or extending beyond margins
```

## Key Principles for Simple Decks

1. **Complete prompt in one block**: All instructions, constraints, and requirements in single comprehensive prompt

2. **Explicit workflow enforcement first**: Lead with html2pptx requirement to prevent tool degradation

3. **Design plan before code**: Require written design description before any slide generation

4. **Negative constraints prominent**: Prohibitions in CAPITAL LETTERS, repeated multiple times

5. **Quantified specifications**: Exact measurements, not vague descriptors

6. **Validation built-in**: Request specific validation checks as part of generation process

7. **Slide-by-slide clarity**: Specify exactly what each slide should contain and emphasize

## Common Mistakes to Avoid

❌ **DON'T**: "Make a professional deck about our financials"
✅ **DO**: Specify exact slides, data sources, visual constraints, validation requirements

❌ **DON'T**: "Use clean design and good contrast"
✅ **DO**: "4.5:1 minimum contrast ratio, 18pt minimum font size, 0.5" margins"

❌ **DON'T**: "Make it look nice but readable"
✅ **DO**: "NO BORDER BOXES, NO OUTLINE SHAPES, text directly on background, test at thumbnail size"

❌ **DON'T**: Generate slides without design plan
✅ **DO**: Force written design description addressing all restrictions before code generation

## Validation Checklist for Simple Decks

After generation, verify:

- [ ] html2pptx workflow was actually used (not alternative)
- [ ] Design plan was created and documented before code
- [ ] Zero border boxes present in any slide
- [ ] Zero outline shapes present in any slide  
- [ ] Zero rounded rectangles with text present
- [ ] All text contrast ratios ≥4.5:1 (calculated and verified)
- [ ] All body text ≥18pt
- [ ] All titles ≥24pt
- [ ] All margins ≥0.5" (measured)
- [ ] Maximum 3 bullets on any slide
- [ ] No text overlapping
- [ ] Single visual element per slide (or fewer)
- [ ] Thumbnail readability confirmed
- [ ] Visual consistency across all slides
- [ ] Narrative flows logically
- [ ] Data accuracy verified against sources
