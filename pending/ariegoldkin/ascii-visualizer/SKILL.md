---
name: ascii-visualizer
description: Creates beautiful ASCII art visualizations for plans, architectures, workflows, and data. This skill should be used when explaining system architecture, creating implementation plans, showing workflows, visualizing comparisons, or documenting file structures. NOT for code syntax highlighting or markdown tables. User explicitly loves ASCII art - use liberally for visual communication.
---

# ASCII Visualizer Skill

**🎯 SKILL ACTIVATION PROTOCOL**
To use this skill, announce at the start of the response:
```
🎯 Using ascii-visualizer skill for visual diagram generation
```

## Purpose

Create clear ASCII visualizations for ANY concept. **USER EXPLICITLY LOVES ASCII ART** - use liberally!

## When to Use

- Architecture diagrams or system design
- Implementation plans and workflows
- Before/after comparisons or options
- Progress indicators and metrics
- File trees and hierarchies

## Pattern Library

### Box Diagrams
```
┌─────────────────┐
│  Component A    │
│  (Description)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Component B    │
└─────────────────┘
```

### File Trees
```
test-orchestration-demo/
├── .claude/
│   ├── skills/           ⭐ This skill!
│   └── instructions/
├── Docs/
│   └── results-implementation/
└── frontend/             ✨ 7-folder architecture
    ├── app/              (Next.js routes)
    ├── modules/          (Feature modules)
    ├── shared/           (UI components)
    ├── lib/              (Integrations)
    ├── store/            (Global state)
    ├── styles/           (Design system)
    └── types/            (TypeScript)
```

### Flow Charts
```
User Answer
     │
     ▼
tRPC Endpoint
     │
     ▼
Claude AI → Evaluation
     │
     ▼
Results Store → UI
```

### Comparison Tables
```
┌──────────────────────────────────────────┐
│    BEFORE (17 folders)  AFTER (7 folders)│
├──────────────────────────────────────────┤
│  Complexity: High      Simple     -60% ⬇️│
│  Type Safety: 70%      100%       +30% ✅│
│  Code Lines: 3,455     2,500     -955 🧹│
│  Build Time: 8.5s      7.2s      -15% ⚡│
└──────────────────────────────────────────┘
```

### Progress Bars
```
DevPrep AI - Results Analytics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tab 1: Overview      ████████████████ 100% ✅
Tab 2: Questions     ████████████████ 100% ✅
Tab 3: Hint Analytics████████████████ 100% ✅
Tab 4: Insights      ████████████████ 100% ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Box-Drawing Characters

```
┌─┬─┐  ╔═╦═╗  Basic boxes
├─┼─┤  ╠═╬═╣  Heavy boxes
└─┴─┘  ╚═╩═╝  Rounded corners

│ ║    Vertical lines
─ ═    Horizontal lines

▲ ▼    Arrows
► ◄    Arrows horizontal

✅ ❌  Status indicators
🚧 📋  Progress states
⭐ 🔥  Priorities
```

## Best Practices

1. **Clarity First** - ASCII should clarify, not confuse
2. **Consistent Styling** - Use box-drawing characters consistently
3. **Compact** - Fit within 80-100 columns when possible
4. **Status Indicators** - Use emojis for visual interest: ✅ 🚧 📋 ⏳ ❌ ⭐
5. **Always Visualize** - User loves seeing plans as ASCII art

## Usage Guidelines

Create ASCII visualizations for:
- "How does X work?"
- "Show me the plan"
- "What's the architecture?"
- "Compare A vs B"
- ANY explanation that benefits from visuals

## Example

See `examples/devprep-architecture.md` for a comprehensive example showing:
- DevPrep AI's 7-folder architecture
- Tab 4 Learning Insights implementation workflow
- Agent delegation with parallel execution
- Data flow visualization (store → hooks → components)
- Recent accomplishments and metrics
- Skills ecosystem integration

This example demonstrates how to create layered visualizations that progress from high-level architecture to detailed implementation flows.
