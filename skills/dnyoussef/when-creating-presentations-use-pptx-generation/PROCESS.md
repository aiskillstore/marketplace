# PPTX Generation - Detailed Workflow

## Process Overview

Enterprise PowerPoint generation with design consistency, accessibility compliance, and data visualization.

## Phase Breakdown

### Phase 1: Research Content (8 min)
**Agent**: Researcher
- Gather presentation content
- Structure outline
- Extract data points
- Identify visualization opportunities

### Phase 2: Design Layout (7 min)
**Agent**: Coder
- Define design system (colors, fonts, spacing)
- Create slide layouts (title, content, two-column, chart)
- Apply accessibility constraints (WCAG 2.1 AA)
- Set color contrast ratios (≥4.5:1)

### Phase 3: Generate Slides (12 min)
**Agent**: Coder
- Initialize presentation with pptxgenjs
- Generate slides from outline
- Add data visualizations (charts, tables)
- Include alt text for accessibility

### Phase 4: Validate Quality (8 min)
**Agent**: Coder
- Scan accessibility (contrast, alt text, reading order)
- Check design consistency
- Validate data integrity
- Ensure file size < 50MB

### Phase 5: Export Final (5 min)
**Agent**: Coder
- Generate PPTX file
- Create accessibility report
- Write documentation
- Package speaker notes

## Design System

```javascript
{
  colors: { primary, secondary, accent, text, background },
  fonts: { heading: 32pt, subheading: 24pt, body: 18pt },
  layout: { margins: 0.5", spacing: 0.3" },
  accessibility: { contrast: 4.5:1, altText: true }
}
```

## Slide Layouts

- **Title**: Large heading + subtitle
- **Content**: Title + bullet points
- **Two-Column**: Split content
- **Data Visualization**: Charts with legends

## Accessibility Standards

- WCAG 2.1 Level AA
- Color contrast ≥4.5:1
- Alt text for all images
- Proper reading order
- Screen reader compatible

For implementation details, see SKILL.md
