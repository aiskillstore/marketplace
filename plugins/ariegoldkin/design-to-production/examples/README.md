# Design-to-Production Examples

Complete worked examples showing the full workflow from HTML prototype to production React component.

---

## Example: Hints Panel

**Source HTML**: `.superdesign/design_iterations/glassmorphism_hints_panel_1.html`

**Workflow Steps**:

### 1. Extract Structure
```bash
./.claude/skills/design-to-production/scripts/extract-structure.sh \
  .superdesign/design_iterations/glassmorphism_hints_panel_1.html
```

**Output**: `HintsPanel-structure.json`
```json
{
  "componentName": "HintsPanel",
  "sourceFile": ".superdesign/design_iterations/glassmorphism_hints_panel_1.html",
  "glassmorphismClasses": [
    "glass-card",
    "neon-glow-purple",
    "btn-glass",
    "text-glow"
  ],
  "interactiveElements": {
    "buttons": 3,
    "inputs": 0,
    "selects": 0,
    "forms": 0
  },
  "layoutPattern": "vertical-stack",
  "suggestedTemplate": "interactive-card"
}
```

### 2. Interactive Mapping

**SKILL.md guides you through**:
- Component name: `HintsPanel`
- Module: `practice`
- Template: `interactive-card` (buttons detected)
- shadcn components: Button, Card, Alert
- Props: `hints: IHint[]`, `onRevealHint: (level: number) => void`

### 3. Scaffold Component
```bash
./.claude/skills/design-to-production/scripts/scaffold-component.sh \
  --name "HintsPanel" \
  --module "practice" \
  --template "interactive-card"
```

**Output**: `modules/practice/components/HintsPanel.tsx` (generated from template)

### 4. Implement Logic

Developer fills in TODOs:
- Add IHint interface definition
- Implement reveal/hide logic
- Add state management for revealed hints
- Apply conditional rendering

**Final Component**: See `references/common-patterns.md` Pattern 3 for complete implementation

### 5. Validate
```bash
./.claude/skills/design-to-production/scripts/validate.sh \
  modules/practice/components/HintsPanel.tsx
```

**Result**: ✅ All checks passed
- File size: 78 lines (≤180 ✓)
- Interfaces: I prefix ✓
- No 'any' types ✓
- Valid glassmorphism classes ✓
- Import patterns ✓

---

## Time Savings

**Manual workflow**: 2-4 hours
- Analysis: 30 min
- Planning: 30 min
- Implementation: 2-3 hours
- Validation: 15 min

**With design-to-production skill**: 30-45 minutes
- Extract structure: 1 min (automated)
- Interactive mapping: 5-10 min (guided)
- Scaffold: 1 min (automated)
- Implementation: 20-30 min (focused on logic only)
- Validation: 1 min (automated)

**Time saved**: ~2-3 hours per component (70-75% reduction)

---

## Other Examples

For additional patterns, see:
- `references/common-patterns.md` - 7 complete patterns with implementations
- `references/glassmorphism-mapping.md` - Class mapping examples
- `references/shadcn-component-guide.md` - Component decision trees

---

## Real Production Components

These DevPrep AI components were created using this workflow:
- `modules/practice/components/PracticeWizard/components/GlassCheckboxItem.tsx`
- `modules/home/components/NavigationHeader.tsx`
- Multiple wizard step components

All follow the same pattern:
1. HTML prototype in `.superdesign/design_iterations/`
2. Guided workflow with scripts
3. Quality standards automatically enforced
4. Consistent glassmorphism styling
