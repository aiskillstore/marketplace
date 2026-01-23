# UI/UX Specifications - [PROJECT NAME]

> **Template Instructions**: Replace all placeholders in [BRACKETS] with project-specific details. Remove sections that don't apply to your project.

## 1. Design Principles

**Core Philosophy**

- [Design principle 1 - e.g., "Mode-specific visual language separates workflows"]
- [Design principle 2 - e.g., "Minimal UI maximizes focus"]
- [Design principle 3 - e.g., "Instant change visibility builds confidence"]
- [Design principle 4 - e.g., "Accessibility-first with WCAG AA compliance"]

**Design System Foundation**

- Base unit: [X]px spacing grid
- Typography: [Primary font family], [Secondary font family]
- Type scale: [Min]px to [Max]px with appropriate line heights
- Border radius: [Tight]px (tight), [Medium]px (medium), [Loose]px (loose)
- Elevation: [Shadow strategy - e.g., "Subtle shadows for layering and depth"]

## 2. Color System

### Primary Colors

**[Feature/Mode Name 1] - [Color Name]**

- Primary: `[HEX]` (HSL: [H] [S]% [L]%)
- Foreground: [Color]
- Use: [When to use this color - e.g., "Active state, accents, focus indicators"]

**[Feature/Mode Name 2] - [Color Name]**

- Primary: `[HEX]` (HSL: [H] [S]% [L]%)
- Foreground: [Color]
- Use: [When to use]

### Semantic Colors

**Light Theme**

- Background: [Color/HEX]
- Foreground: [Color/HEX]
- Card: [Color/HEX]
- Border: [Color/HEX]
- Muted: [Description and color]
- Destructive: [Color for dangerous actions]
- Success: [Color for positive actions]
- Warning: [Color for caution states]

**Dark Theme**

- Background: [Color/HEX]
- Foreground: [Color/HEX]
- Card: [Color/HEX]
- Border: [Color/HEX]
- Muted: [Description and color]
- Destructive: [Adjusted for dark mode]
- Success: [Adjusted for dark mode]
- Warning: [Adjusted for dark mode]

### Special Color Contexts

**[Context Name - e.g., "Diff Colors", "Status Indicators"]**

**[State 1 - e.g., "Additions"]**

- Light: [Background color], [Text color]
- Dark: [Background color], [Text color]
- Styling: [Additional styling - e.g., "Background highlight"]

**[State 2 - e.g., "Deletions"]**

- Light: [Background color], [Text color]
- Dark: [Background color], [Text color]
- Styling: [Additional styling - e.g., "Strikethrough"]

## 3. Core Architecture

### [Main Feature/Component Name]

**Visual Design**

- Type: [Component type - e.g., "3-way segmented control"]
- Position: [Where it appears - e.g., "Top bar (desktop), bottom navigation (mobile)"]
- Container: [Height/width], [Border radius], [Background]
- [Element 1]: [Dimensions and styling]
- [Element 2]: [Dimensions and styling]
- Active state: [How it looks when active]
- Inactive state: [How it looks when inactive]
- Hover: [Hover state styling]
- Animation: [Transition timing and effects]

**Behavior**

- [Interaction 1 - e.g., "Single selection only"]
- [Interaction 2 - e.g., "Keyboard navigation with arrow keys"]
- [Interaction 3 - e.g., "Click or Enter to activate"]

### [Dialog/Modal Name]

**Visual Design**

- Trigger: [What causes it to appear]
- Layout: [Layout description]
  - Desktop: [Dimensions]
  - Mobile: [Dimensions]
- Header: [Header content and styling]
- Metadata: [What metadata is shown and how]
- Actions: [Action buttons and layout]
  - [Action 1]: [Dimensions, styling, icon]
  - [Action 2]: [Dimensions, styling, icon]
  - Hover: [Hover effect]
- Backdrop: [Backdrop styling]

**Behavior**

- [Trigger condition]
- [Dismissal behavior]
- [Keyboard navigation]
- [Selection behavior]

## 4. Core Components

### [Component Name 1 - e.g., "Rich Text Editor"]

**Visual Design**

- Container: [Max-width], [Alignment]
- Padding: [Horizontal], [Vertical]
- Font: [Size], [Line-height], [Font family]
- Placeholder: [Text and styling]
- Selection highlight: [Color and opacity]
- [Other styling details]

**States**

- Empty: [How it looks when empty]
- Loading: [Loading state appearance]
- Disabled: [Disabled state appearance]
- Error: [Error state appearance]

**[State-Specific Variations - if applicable]**

- [State 1]: [Styling]
- [State 2]: [Styling]
- [State 3]: [Styling]

### [Component Name 2 - e.g., "Autocomplete Popup"]

**Visual Design**

- Width: [Width]
- Position: [Positioning strategy]
- Max items: [Number visible], [Scroll behavior]
- Item height: [Height per item]
- Border: [Border styling]
- Background: [Background color and effects]
- Selected item: [Selection styling]
- Font: [Font styling]

**Behavior**

- Trigger: [When it appears - e.g., "After Xms pause in typing"]
- Active in: [Where it's available]
- Keyboard: [Keyboard controls]
- Mouse: [Mouse interactions]
- Disappears: [When it closes]

**Performance**

- Target: [Performance target - e.g., "<100ms to display"]
- Debounce: [Debounce timing]

### [Component Name 3 - e.g., "Sidebar/Panel"]

**Visual Design**

- Desktop: [Layout and dimensions]
- Mobile: [Layout and dimensions]
- Background: [Background styling]
- Border: [Border styling]
- Padding: [Padding values]

**Header**

- Title: [Title styling]
- [Other header elements and styling]

**[Section Name - e.g., "Action Button"]**

- [Styling details]
- Text: [Button text and icon]
- Style: [Button style]

**[Section Name - e.g., "Content List"]**

- Scrollable area: [Height calculation]
- Items: [Item styling and layout]
  - [Detail 1]
  - [Detail 2]
  - Hover: [Hover effect]
  - Layout: [Layout description]
  - [Gap between items]

**Behavior**

- [Interaction 1]
- [Interaction 2]
- [Interaction 3]

## 5. Application Screens

### [Screen Name 1 - e.g., "Onboarding"]

**Screen 1: [Substep Name]**

- Container: [Max-width], [Alignment], [Padding]
- Headline: [Text and styling]
- Subheadline: [Text and styling]
- [Content section]: [Layout description]
  - Each [element]: [Styling]
  - [Element detail 1]: [Styling]
  - [Element detail 2]: [Styling]
  - [Gap between elements]
- CTA: [Button text and styling]

**Screen 2: [Substep Name]**

- Headline: [Text and styling]
- Content: [Content description]
- CTA: [Button text and styling]

### [Screen Name 2 - e.g., "Main Dashboard"]

**Header Section**

- Title: [Title text and styling]
- [Metadata element]: [Content and styling]
- Action: [Action button and styling]

**[Section Name - e.g., "Search & Filter Bar"]**

- [Element 1]: [Description and styling]
- [Element 2]: [Description and styling]
- [Gap between elements]

**[Section Name - e.g., "Content Grid/List"]**

- Layout: [Layout type and gap]
- Each [item]:
  - Padding: [Padding]
  - Border: [Border styling]
  - Hover: [Hover effect]
  - [Content 1]: [Styling]
  - [Content 2]: [Styling]
  - [Content 3]: [Styling]

**Behavior**

- [Interaction 1]
- [Interaction 2]
- [Loading state]

## 6. Responsive Design

### Breakpoints

- Mobile: < [X]px
- Tablet: [X]px - [Y]px
- Desktop: [X]px+
- Large Desktop: [X]px+

### Responsive Adaptations

**[Component/Feature 1]**

- Desktop: [Desktop layout]
- Tablet: [Tablet layout]
- Mobile: [Mobile layout]

**[Component/Feature 2]**

- Desktop: [Desktop layout]
- Mobile: [Mobile layout]

**[Component/Feature 3]**

- Desktop: [Desktop behavior]
- Mobile: [Mobile behavior]

## 7. Accessibility

### Keyboard Navigation

**Shortcuts**

- [Key combo 1]: [Action]
- [Key combo 2]: [Action]
- [Key combo 3]: [Action]
- Escape: [Dismiss behavior]
- Tab: [Tab navigation behavior]
- Enter: [Enter behavior]
- Arrow keys: [Arrow key behavior]

**Focus Indicators**

- Visible ring around all interactive elements
- [Color strategy for focus ring]
- [Width]px width, [Offset]px offset
- Never remove focus indicators

### ARIA Attributes

**[Component 1]**

- Role: [ARIA role]
- [Attribute 1]: [Usage]
- [Attribute 2]: [Usage]

**[Component 2]**

- Role: [ARIA role]
- [Attribute 1]: [Usage]
- [Attribute 2]: [Usage]

**[Component 3]**

- Role: [ARIA role]
- [Attribute 1]: [Usage]
- Focus trap: [If applicable]

### Screen Reader Support

- All icons have text labels or aria-label
- All images have alt text
- Loading states announced
- Error messages announced
- Form inputs properly labeled
- [Other accessibility features]

## 8. Animation & Motion

### Transition Timing

- Instant: < [X]ms ([Use case])
- Quick: [X]ms ([Use case])
- Standard: [X]ms ([Use case])
- Slow: [X]ms ([Use case])

### Animation Principles

**[Animation Context 1 - e.g., "Mode Transitions"]**

- [Property] changes: [Timing] [Transition type]
- [Constraint 1 - e.g., "No layout shift"]
- [Constraint 2 - e.g., "Text remains readable"]

**[Animation Context 2 - e.g., "Modal Animations"]**

- [Element 1]: [Timing and effect]
- [Element 2]: [Timing and effect]
- Exit: [Exit behavior]
- Easing: [Easing function]

**[Animation Context 3 - e.g., "Micro-interactions"]**

- [Interaction 1]: [Effect and timing]
- [Interaction 2]: [Effect and timing]
- [Interaction 3]: [Effect and timing]

**Performance Considerations**

- Use CSS transforms (translate, scale) over position changes
- Avoid animating layout properties (width, height, padding)
- Prefer opacity over visibility for fades
- Respect `prefers-reduced-motion` setting
- [Other performance guidelines]

## 9. Dark Mode

### Theme Switching

**Controls**

- Toggle button in [location]
- Icon: [Light mode icon] / [Dark mode icon]
- [Transition effect]
- Persists choice to [storage method]

**System Integration**

- Default: [Default behavior]
- Options: [Available options]
- No flash of wrong theme on page load

**Color Adaptations**

- [Color category 1]: [How it adapts]
- [Color category 2]: [How it adapts]
- [Contrast consideration]
- [Shadow adjustment]

## 10. Performance Targets

### Critical Metrics

- **[Metric 1]**: < [X]ms
- **[Metric 2]**: < [X]ms
- **[Metric 3]**: < [X]ms
- **[Metric 4]**: < [X]s
- **Initial page load**: < [X]s (LCP)
- **Time to interactive**: < [X]s
- **First Contentful Paint**: < [X]s
- **Cumulative Layout Shift**: < [X]

### Optimization Strategies

- [Strategy 1 - e.g., "Lazy load components"]
- [Strategy 2 - e.g., "Debounce expensive operations"]
- [Strategy 3 - e.g., "Virtual scrolling for long lists"]
- [Strategy 4 - e.g., "Server-side rendering"]
- [Strategy 5 - e.g., "Progressive enhancement"]
- [Strategy 6 - e.g., "Skeleton loading states"]

## 11. Design Checklist (MVP)

**Before [Milestone Name - e.g., "Beta Launch"]**

- [ ] [Feature 1 with clear visual indicators]
- [ ] [Feature 2 with specific behavior]
- [ ] [Feature 3 in specific context]
- [ ] [Component 1 implementation]
- [ ] [Component 2 implementation]
- [ ] [Flow 1 complete]
- [ ] [Flow 2 complete]
- [ ] Fully responsive (mobile, tablet, desktop)
- [ ] WCAG AA compliant
- [ ] Dark mode support
- [ ] Keyboard navigation throughout
- [ ] Loading and error states for all components
- [ ] Smooth transitions and animations
- [ ] Performance targets met
- [ ] [Project-specific requirement 1]
- [ ] [Project-specific requirement 2]

---

**Design System**: [Design system description - e.g., "Built on Shadcn UI components with Tailwind CSS for styling consistency and accessibility compliance."]

**Additional Resources**:

- Design files: [Link or path]
- Component library: [Link or path]
- Brand guidelines: [Link or path]
