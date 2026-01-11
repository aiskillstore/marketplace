# PPTX Generation - Quick Start

## Purpose
Enterprise-grade PowerPoint generation with accessibility compliance (WCAG 2.1 AA) and constraint-based design.

## When to Use
- Board presentations
- Business reviews
- Technical reports
- Client proposals

## Quick Start

```bash
npx claude-flow@alpha skill-run pptx-generation \
  --content "content-outline.json" \
  --output "presentation.pptx"
```

## 5-Phase Process

1. **Research** (8 min) - Gather content and structure
2. **Design** (7 min) - Create layouts and design system
3. **Generate** (12 min) - Build slides with visualizations
4. **Validate** (8 min) - Accessibility and quality checks
5. **Export** (5 min) - Final PPTX with documentation

## Features

- WCAG 2.1 AA compliance
- Consistent design system
- Data visualizations (charts, tables)
- Speaker notes
- Alt text for accessibility
- 30+ slide support

## Output

- **presentation.pptx**: PowerPoint file
- **accessibility-report.json**: Compliance scan
- **documentation.md**: Generation details

For detailed documentation, see SKILL.md
