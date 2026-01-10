---
name: design-to-production
description: Guided workflow for implementing HTML design prototypes as production React components with glassmorphism styling and quality standards enforcement. Use when converting design prototypes to production code.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# Design to Production

Guided workflow for converting HTML prototypes to production React components.

**TL;DR**: Provide HTML file path → analyze → map components → scaffold → implement → validate

---

## Auto-Triggers

Auto-triggered by keywords:
- "implement design", "prototype to production", "convert HTML"
- "glassmorphism component", "design prototype", "HTML to React"

---

## Quick Commands

```bash
# Step 1: Analyze HTML prototype
./.claude/skills/design-to-production/scripts/extract-structure.sh <html-file-path>

# Step 3: Scaffold component (after interactive mapping)
./.claude/skills/design-to-production/scripts/scaffold-component.sh \
  --name "ComponentName" \
  --module "practice" \
  --template "interactive-card"

# Step 5: Validate implementation
./.claude/skills/design-to-production/scripts/validate.sh <component-path>
```

---

## 5-Step Workflow

### Example: Implementing `glassmorphism_hints_panel_1.html`

```
1. ANALYZE    → Extract structure from HTML
2. MAP        → Choose shadcn components + glassmorphism classes
3. SCAFFOLD   → Generate .tsx file with boilerplate
4. IMPLEMENT  → Write component logic (guided by TODOs)
5. VALIDATE   → Check quality standards
```

### Step 1: ANALYZE

**User provides**: HTML file path (e.g., `.superdesign/design_iterations/glassmorphism_hints_panel_1.html`)

**Script runs**:
```bash
./scripts/extract-structure.sh .superdesign/design_iterations/glassmorphism_hints_panel_1.html
```

**Output**: `hints-panel-structure.json` with:
- Component hierarchy
- CSS classes (glassmorphism utilities)
- Interactive elements (buttons, forms, inputs)
- Layout patterns (grid, flex, vertical-stack)

**SKILL.md presents**: Summary of detected structure

### Step 2: MAP (Interactive)

**SKILL.md guides you through 4 decisions**:

#### 2.1 Component Identification
- **Question**: "What should we call this component?"
- **Suggested**: Extracted from HTML filename or title
- **Example**: `HintsPanel`

#### 2.2 Module Placement
- **Question**: "Which module does this belong to?"
- **Options**: practice, assessment, results, profile, questions, home
- **Example**: `practice`

#### 2.3 shadcn/ui Component Mapping
For each interactive element:
- **Detected**: `<button class="btn-glass">Show Hint</button>`
- **Suggestion**: Use `Button` from `@shared/ui/button`
- **Confirm**: User approves or overrides

Common mappings:
| HTML Element | shadcn Component |
|--------------|------------------|
| `<button class="btn-*">` | `Button` |
| `<div class="glass-card">` | `Card` |
| `<input type="text">` | `Input` |
| `<select>` | `Select` |
| Badge/chip | `Badge` |

#### 2.4 Glassmorphism Class Mapping
- **Extracted from HTML**: `class="glass-card neon-glow-purple text-glow"`
- **Maps to React**: `className="glass-card neon-glow-purple text-glow"`
- **Validation**: Checks against approved classes in `styles/glassmorphism.css`

### Step 3: SCAFFOLD

**Script generates** `.tsx` file using template:

```bash
./scripts/scaffold-component.sh \
  --name "HintsPanel" \
  --module "practice" \
  --template "interactive-card" \
  --props "title:string,hints:IHint[],onShowHint:(index:number)=>void"
```

**Output**: `modules/practice/components/HintsPanel.tsx` with:
- ✅ TypeScript interface (I prefix)
- ✅ Proper imports (@shared/ui/*, glassmorphism classes)
- ✅ Props structure from HTML analysis
- ✅ TODO comments marking logic locations
- ✅ Glassmorphism classes applied

### Step 4: IMPLEMENT

**SKILL.md reminds**:
- File location: `modules/practice/components/HintsPanel.tsx`
- Quality standards: ≤180 lines, complexity <15, I prefix
- TODO items in scaffolded file mark where to add logic

**User writes**: Business logic, event handlers, state management

### Step 5: VALIDATE

```bash
./scripts/validate.sh modules/practice/components/HintsPanel.tsx
```

**Checks**:
- ✅ File size ≤180 lines
- ✅ Complexity ≤15 per function
- ✅ Interface naming (I prefix)
- ✅ Glassmorphism class validity
- ✅ Import patterns (@shared, @modules, @lib)
- ✅ No `any` types

**Output**: Pass/fail + suggestions for fixes

---

## Template Types

Choose the right template for your component:

| Template | Use For | Includes |
|----------|---------|----------|
| `interactive-card` | Buttons, forms, user actions | Card, Button, Input, event handlers |
| `display-card` | Read-only content, stats | Card, Typography, badges |
| `layout-section` | Page sections, containers | Layout wrapper, grid/flex patterns |

---

## Common Patterns

### Pattern 1: Button with Glassmorphism
**HTML**: `<button class="btn-glass">Action</button>`
**React**: `<Button className="btn-glass" onClick={handleAction}>Action</Button>`

### Pattern 2: Glass Card Container
**HTML**: `<div class="glass-card neon-glow">Content</div>`
**React**: `<Card className="glass-card neon-glow"><CardContent>Content</CardContent></Card>`

### Pattern 3: Gradient Text
**HTML**: `<h1 class="gradient-text">Title</h1>`
**React**: `<h1 className="gradient-text">Title</h1>`

---

## When to Load References

**SKILL.md is self-sufficient for**:
- Running the 5-step workflow
- Common component mappings
- Basic glassmorphism classes

**Load references when needed**:

| Need | Load |
|------|------|
| Full glassmorphism class list | `references/glassmorphism-mapping.md` |
| shadcn component decision guide | `references/shadcn-component-guide.md` |
| Complex layout patterns | `references/common-patterns.md` |
| Complete worked example | `examples/hints-panel-complete/` |

---

## Troubleshooting

**Script not found**: Ensure you're in project root (`frontend/`)

**Invalid glassmorphism class**: Check `styles/glassmorphism.css` for approved classes

**Validation fails**: Run quality-reviewer to see detailed errors

---

**Version**: 1.0.0 | **Updated**: October 2025
**Pattern**: Follows module-scaffolder optimization structure
