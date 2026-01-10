# Design-to-Production Skill - User Guide

**Version**: 1.0.0 | **Updated**: October 2025

Complete guide for converting HTML design prototypes to production React components using the design-to-production skill.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [When to Use This Skill](#when-to-use-this-skill)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Detailed Workflow](#detailed-workflow)
6. [Interactive Mapping Guide](#interactive-mapping-guide)
7. [Best Practices](#best-practices)
8. [Integration with Other Skills](#integration-with-other-skills)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Overview

The **design-to-production** skill automates the conversion of HTML design prototypes into production-ready React components with glassmorphism styling and enforced quality standards.

### What It Does

✅ **Automates**:
- HTML structure extraction
- Component scaffolding with templates
- Quality validation (≤180 lines, I prefix, etc.)

✅ **Guides You Through**:
- Component naming and placement
- shadcn/ui component mapping
- Glassmorphism class selection
- Props interface design

✅ **Enforces**:
- DevPrep AI quality standards
- Consistent glassmorphism styling
- Proper TypeScript patterns

### Time Savings

- **Manual workflow**: 2-4 hours per component
- **With this skill**: 30-45 minutes per component
- **Reduction**: 70-75% time savings

---

## When to Use This Skill

### ✅ Use This Skill When:

1. **Converting HTML prototypes to React**
   - You have an HTML file in `.superdesign/design_iterations/`
   - You need a production React component
   - The prototype uses glassmorphism styling

2. **Creating new UI components**
   - The design is finalized
   - You need consistent styling
   - Quality standards must be enforced

3. **Implementing design system components**
   - Using shadcn/ui as base
   - Applying glassmorphism effects
   - Following DevPrep AI patterns

### ❌ Don't Use This Skill When:

1. **No HTML prototype exists**
   - Use `rapid-ui-designer` agent to create prototype first
   - Or code directly if design is simple

2. **Component already exists**
   - Use direct editing/refactoring instead
   - Or quality-reviewer to validate existing code

3. **Non-glassmorphism designs**
   - This skill is optimized for glassmorphism
   - For other styles, code manually

---

## Prerequisites

### Required Files

1. **HTML Prototype**
   - Location: `.superdesign/design_iterations/`
   - Naming: `{theme}_{component}_{version}.html`
   - Example: `glassmorphism_hints_panel_1.html`

2. **Module Must Exist**
   - Target module in `frontend/src/modules/`
   - Use `module-scaffolder` to create if needed

### Required Knowledge

- Basic React/TypeScript
- shadcn/ui component library
- Glassmorphism design system
- DevPrep AI folder structure

---

## Quick Start

### 1. Prepare HTML Prototype

Ensure your HTML prototype is in `.superdesign/design_iterations/`:

```bash
ls -la .superdesign/design_iterations/glassmorphism_*.html
```

### 2. Invoke the Skill

In Claude Code, type:
```
"Please implement glassmorphism_hints_panel_1.html as a React component"
```

Or explicitly:
```
"Use design-to-production skill to convert .superdesign/design_iterations/glassmorphism_hints_panel_1.html"
```

### 3. Follow the Guided Workflow

The skill will walk you through 5 steps:
1. **ANALYZE** - Automated extraction
2. **MAP** - Interactive decisions
3. **SCAFFOLD** - Automated generation
4. **IMPLEMENT** - You write logic
5. **VALIDATE** - Automated checks

### 4. Complete Implementation

The skill creates a component with TODOs. You fill in:
- Business logic
- Event handlers
- State management

---

## Detailed Workflow

### Step 1: ANALYZE (Automated)

**What Happens**:
```bash
./.claude/skills/design-to-production/scripts/extract-structure.sh <html-file>
```

**Output**: JSON structure file

**Example Output**:
```json
{
  "componentName": "HintsPanel",
  "glassmorphismClasses": [
    "glass-card",
    "neon-glow-purple",
    "btn-glass",
    "text-glow"
  ],
  "interactiveElements": {
    "buttons": 3,
    "inputs": 0
  },
  "layoutPattern": "vertical-stack",
  "suggestedTemplate": "interactive-card"
}
```

**Review**: Claude presents summary, asks for confirmation

---

### Step 2: MAP (Interactive)

This is where you make decisions. Claude will guide you through 4 key questions:

#### 2.1 Component Naming

**Question**: "What should we call this component?"

**Claude suggests**: Name extracted from HTML filename

**Your options**:
- Accept suggestion (most common)
- Provide custom name (PascalCase required)

**Example**:
```
Suggested: HintsPanel
Your choice: ProgressiveHintsPanel  (if you want more specific name)
```

#### 2.2 Module Placement

**Question**: "Which module does this belong to?"

**Available modules**:
- practice
- assessment
- results
- profile
- questions
- home

**Example**:
```
For hints panel in practice session:
Your choice: practice
```

#### 2.3 shadcn/ui Component Mapping

**What happens**: Claude shows detected interactive elements and suggests shadcn components

**Example**:
```
Detected: <button class="btn-glass">Show Hint</button>
Suggested: Button from @shared/ui/button
Confirm? [yes/no]
```

**Common mappings**:
| HTML Element | Suggested Component |
|--------------|---------------------|
| `<button>` | `Button` |
| `<div class="glass-card">` | `Card` + `CardContent` |
| `<input type="text">` | `Input` |
| `<select>` | `Select` |
| Badge/chip | `Badge` |

**Your role**: Confirm or suggest alternatives

#### 2.4 Glassmorphism Class Mapping

**What happens**: Claude extracts CSS classes and maps to production utilities

**Example**:
```
HTML classes: glass-card neon-glow-purple text-glow
React className: "glass-card neon-glow-purple text-glow"
Validation: ✓ All classes valid
```

**If invalid classes detected**:
```
Warning: 'glass-effect' is not a valid class
Suggested replacement: 'glass-card'
```

---

### Step 3: SCAFFOLD (Automated)

**What Happens**:
```bash
./.claude/skills/design-to-production/scripts/scaffold-component.sh \
  --name "HintsPanel" \
  --module "practice" \
  --template "interactive-card"
```

**Generated File**: `modules/practice/components/HintsPanel.tsx`

**What's Included**:
- ✅ TypeScript interface (I prefix)
- ✅ Proper imports (@shared/ui/*)
- ✅ Glassmorphism classes applied
- ✅ Component structure from template
- ✅ TODO comments for logic

**Template Types**:
- `interactive-card` - Has buttons/forms/user actions
- `display-card` - Read-only content display
- `layout-section` - Page sections/containers

---

### Step 4: IMPLEMENT (Your Turn)

**What You Do**: Open the generated file and complete TODOs

**Example Generated Code**:
```tsx
export function HintsPanel({
  className,
}: IHintsPanelProps): React.JSX.Element {
  // TODO: Add state management
  // Example: const [isOpen, setIsOpen] = React.useState(false);

  // TODO: Add event handlers
  // Example: const handleClick = () => { ... };

  return (
    <Card className={cn("glass-card", className)}>
      <CardHeader>
        <CardTitle className="text-glow">
          {/* TODO: Replace with dynamic title from props */}
          Component Title
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* TODO: Add component content from HTML prototype */}
        <Button className="btn-glass w-full">
          Action Button
        </Button>
      </CardContent>
    </Card>
  );
}
```

**Your Implementation**:
1. Add missing props to interface
2. Implement state management
3. Add event handlers
4. Fill in dynamic content
5. Test interactivity

**Typical Time**: 20-30 minutes (focused on logic only)

---

### Step 5: VALIDATE (Automated)

**What Happens**:
```bash
./.claude/skills/design-to-production/scripts/validate.sh <component-path>
```

**Checks Performed**:
- ✅ File size ≤180 lines
- ✅ Interface naming (I prefix)
- ✅ No `any` types
- ✅ Valid glassmorphism classes only
- ✅ Import patterns (@shared, @modules, @lib)

**Example Output** (Success):
```
🔍 Validating component...

✓ File size: 78 lines
✓ Interface naming (I prefix)
✓ No 'any' types
✓ Glassmorphism classes valid
✓ Import patterns

======================================
✅ Validation PASSED
Component meets all DevPrep AI standards!
======================================
```

**Example Output** (Failure):
```
🔍 Validating component...

✗ File size: 195 lines (exceeds 180)
✓ Interface naming (I prefix)
⚠ Found 2 usage(s) of 'any' type
✓ Glassmorphism classes valid
⚠ Found 5 relative imports (consider using @shared, @modules, @lib)

======================================
❌ Validation FAILED
Found 1 error(s) and 2 warning(s)
======================================
```

**If Validation Fails**: Claude will suggest fixes based on errors

---

## Interactive Mapping Guide

### Decision Framework

When Claude asks questions during Step 2 (MAP), use this framework:

#### Question 1: Component Name

**Consider**:
- Purpose of component
- Where it will be used
- Existing naming patterns

**Good names**:
- `ProgressiveHintsPanel` ✅ (descriptive)
- `FeedbackModal` ✅ (clear purpose)
- `SessionSplitLayout` ✅ (indicates structure)

**Bad names**:
- `Component1` ❌ (not descriptive)
- `hints` ❌ (not PascalCase)
- `TheHintsPanelComponent` ❌ (redundant)

#### Question 2: Module Placement

**Decision Tree**:
```
What feature is this for?
├─ Practice sessions? → practice
├─ Assessments? → assessment
├─ Results/analytics? → results
├─ User profile? → profile
├─ Question library? → questions
└─ Landing/home page? → home
```

**Cross-module components**: Use `shared/components/` instead

#### Question 3: shadcn/ui Mapping

**Always confirm** unless:
- You know a better component exists
- The suggested component doesn't fit semantically
- You plan to use a custom component

**Example override**:
```
Claude suggests: Button
You override: Badge (because it's non-interactive label)
```

#### Question 4: Class Mapping

**Always accept** unless:
- Invalid class detected (Claude will warn)
- You want to add additional classes
- You want to change emphasis (e.g., neon-glow-purple → neon-glow-cyan)

---

## Best Practices

### Before Starting

1. ✅ **Finalize HTML prototype**
   - Design should be complete
   - All interactive elements present
   - Glassmorphism classes applied

2. ✅ **Ensure module exists**
   ```bash
   ls -la frontend/src/modules/practice/
   ```
   - If not, use `module-scaffolder` first

3. ✅ **Review similar components**
   - Check existing patterns in the module
   - Ensure naming consistency

### During Workflow

1. ✅ **Take time on mapping decisions**
   - Component name affects maintainability
   - Module placement affects architecture
   - These are hard to change later

2. ✅ **Trust the automation**
   - Scripts are tested and reliable
   - Validation catches errors automatically

3. ✅ **Don't skip validation**
   - Always run final validation
   - Fix errors before committing

### After Implementation

1. ✅ **Test the component**
   - Render in Storybook (if available)
   - Test all interactive elements
   - Verify glassmorphism effects

2. ✅ **Update barrel exports**
   ```tsx
   // In modules/practice/components/index.ts
   export * from "./HintsPanel";
   ```

3. ✅ **Optional: Generate documentation**
   - Create component-mapping.md if needed
   - Document usage examples

---

## Integration with Other Skills

### Before design-to-production

#### Use `brainstorming` if:
- Component design is complex
- Multiple implementation approaches possible
- Need to clarify requirements

**Example workflow**:
```
1. Use brainstorming skill → Design component architecture
2. Create HTML prototype
3. Use design-to-production → Implement component
```

#### Use `module-scaffolder` if:
- Target module doesn't exist yet
- Creating new feature domain

**Example workflow**:
```
1. Use module-scaffolder → Create 'analytics' module
2. Design HTML prototypes for analytics components
3. Use design-to-production → Implement components
```

### After design-to-production

#### Use `quality-reviewer` if:
- Want deeper code analysis
- Need complexity checks
- Validating multiple files

**Example workflow**:
```
1. Use design-to-production → Implement component
2. Use quality-reviewer → Full quality audit
3. Fix any issues found
```

#### Use `trpc-scaffolder` if:
- Component needs API endpoints
- Implementing data-fetching logic

**Example workflow**:
```
1. Use design-to-production → Create UI component
2. Use trpc-scaffolder → Create API endpoints
3. Connect component to API
```

---

## Troubleshooting

### Issue: "HTML file not found"

**Error**:
```
Error: HTML file not found at .superdesign/design_iterations/...
```

**Solution**:
```bash
# Check file exists
ls -la .superdesign/design_iterations/

# Verify path is correct (relative to project root)
# Correct: .superdesign/design_iterations/file.html
# Wrong: frontend/.superdesign/... (don't include frontend/)
```

### Issue: "Module does not exist"

**Error**:
```
Error: Module 'analytics' does not exist at frontend/src/modules/analytics
```

**Solution**:
```bash
# Create module first
./.claude/skills/module-scaffolder/scripts/create-module.sh analytics

# Then run design-to-production again
```

### Issue: "Validation FAILED - File size exceeds 180 lines"

**Error**:
```
✗ File size: 195 lines (exceeds 180)
```

**Solutions**:
1. **Split component into smaller parts**:
   ```tsx
   // Before: One 195-line component
   // After:
   // - HintsPanel.tsx (120 lines) - Main component
   // - HintItem.tsx (40 lines) - Child component
   // - hooks/useHints.ts (35 lines) - Logic
   ```

2. **Extract hooks**:
   ```tsx
   // Move state management to custom hook
   // hooks/useHintsPanel.ts
   ```

3. **Extract utilities**:
   ```tsx
   // Move helper functions to utils
   // utils/hintHelpers.ts
   ```

### Issue: "Invalid glassmorphism class"

**Warning**:
```
⚠ Potentially invalid glassmorphism classes:
  className="glass-effect"
```

**Solution**:
```tsx
// Check valid classes in styles/glassmorphism.css
// Replace with:
className="glass-card"  // Not 'glass-effect'
```

**Valid classes**: See `references/glassmorphism-mapping.md`

### Issue: "Interface without I prefix"

**Error**:
```
✗ Found interface(s) without 'I' prefix
```

**Solution**:
```tsx
// Before
interface HintsPanelProps { ... }

// After
interface IHintsPanelProps { ... }
```

### Issue: "Component too complex"

**Symptom**: Implementation taking longer than expected

**Solutions**:
1. **Break into smaller components**
2. **Use existing patterns** from `references/common-patterns.md`
3. **Ask for help**: Request Claude to review complexity

---

## Examples

### Example 1: Simple Display Card

**Scenario**: Convert stat card prototype to React

**HTML**: `glassmorphism_stat_card_1.html`
```html
<div class="glass-card neon-glow-cyan text-center">
  <div class="text-4xl font-bold">5,000+</div>
  <div class="text-sm">Active Users</div>
</div>
```

**Workflow**:
```
1. ANALYZE
   Input: .superdesign/design_iterations/glassmorphism_stat_card_1.html
   Detected: 0 buttons, 0 inputs → display-card template

2. MAP
   Name: StatCard
   Module: home
   Template: display-card
   Classes: glass-card, neon-glow-cyan ✓

3. SCAFFOLD
   Generated: modules/home/components/StatCard.tsx

4. IMPLEMENT (5 minutes)
   - Added props: value, label
   - No state needed (read-only)

5. VALIDATE
   Result: ✅ PASSED (32 lines)
```

**Time**: 10 minutes total

---

### Example 2: Interactive Form Component

**Scenario**: Convert practice setup form to React

**HTML**: `glassmorphism_practice_setup_1.html`
```html
<div class="glass-card">
  <h3>Practice Settings</h3>
  <input type="number" placeholder="Duration (min)">
  <select>
    <option>Easy</option>
    <option>Medium</option>
    <option>Hard</option>
  </select>
  <button class="btn-primary-glass">Start</button>
</div>
```

**Workflow**:
```
1. ANALYZE
   Detected: 1 button, 1 input, 1 select → interactive-card template

2. MAP
   Name: PracticeSetupForm
   Module: practice
   Components: Input, Select, Button ✓
   Classes: glass-card, btn-primary-glass ✓

3. SCAFFOLD
   Generated: modules/practice/components/PracticeSetupForm.tsx

4. IMPLEMENT (25 minutes)
   - Added props: onSubmit, defaultValues
   - State: duration, difficulty
   - Handlers: handleSubmit, handleChange
   - Validation: duration > 0

5. VALIDATE
   Result: ✅ PASSED (89 lines)
```

**Time**: 35 minutes total

---

### Example 3: Complex Layout Section

**Scenario**: Convert hero section with stats grid

**HTML**: `glassmorphism_home_1.html` (extract hero section)
```html
<section class="glass-card-static py-24">
  <h1 class="gradient-text">DevPrep AI</h1>
  <p>Master technical interviews...</p>
  <div class="grid grid-cols-3 gap-6">
    <!-- 3 stat cards -->
  </div>
  <button class="btn-primary-glass">Get Started</button>
</section>
```

**Workflow**:
```
1. ANALYZE
   Detected: Complex layout, grid pattern → layout-section template

2. MAP
   Name: HeroSection
   Module: home
   Components: Badge, Button, custom stat cards
   Classes: glass-card-static, gradient-text, btn-primary-glass ✓

3. SCAFFOLD
   Generated: modules/home/components/HeroSection.tsx

4. IMPLEMENT (40 minutes)
   - Created separate StatCard component (15 min)
   - Implemented layout (10 min)
   - Added props and handlers (15 min)

5. VALIDATE
   HeroSection.tsx: ✅ PASSED (95 lines)
   StatCard.tsx: ✅ PASSED (32 lines)
```

**Time**: 50 minutes total (2 components)

---

## Summary

### Workflow Checklist

- [ ] HTML prototype is finalized
- [ ] Target module exists
- [ ] Invoke design-to-production skill
- [ ] Complete Step 1: ANALYZE (automated)
- [ ] Complete Step 2: MAP (answer 4 questions)
- [ ] Complete Step 3: SCAFFOLD (automated)
- [ ] Complete Step 4: IMPLEMENT (write logic)
- [ ] Complete Step 5: VALIDATE (automated)
- [ ] Fix any validation errors
- [ ] Test component functionality
- [ ] Update barrel exports
- [ ] Commit changes

### Key Takeaways

1. ✅ **Save 70-75% time** vs manual implementation
2. ✅ **Quality standards enforced** automatically
3. ✅ **Consistent glassmorphism** styling
4. ✅ **Interactive guidance** for decisions
5. ✅ **Automated validation** catches errors

### Getting Help

If you encounter issues not covered here:

1. **Check references**:
   - `references/glassmorphism-mapping.md`
   - `references/shadcn-component-guide.md`
   - `references/common-patterns.md`

2. **Review examples**:
   - `examples/README.md`

3. **Use quality-reviewer**:
   - For detailed code analysis

4. **Ask Claude**:
   - "How do I map this HTML element to shadcn?"
   - "What glassmorphism class should I use for X?"

---

**Happy implementing!** 🎨→⚛️
