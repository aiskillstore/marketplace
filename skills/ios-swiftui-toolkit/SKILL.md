---
name: ios-swiftui-toolkit
description: A curated bundle of three SwiftUI skills covering UI patterns, performance auditing, and view refactoring. Use when developing or improving iOS/macOS apps with SwiftUI.
---

# iOS SwiftUI Toolkit

A curated collection of three expert SwiftUI skills for building production-quality iOS and macOS applications.

## Bundled Skills

### 1. SwiftUI UI Patterns (`swiftui-ui-patterns`)
Best practices and example-driven guidance for building SwiftUI views and components.

**Use when:** designing tab architecture with TabView, composing screens, creating forms, handling lists/grids, managing navigation stacks, routing sheets/modals, implementing theming and haptics.

### 2. SwiftUI Performance Audit (`swiftui-performance-audit`)
Audit and improve SwiftUI runtime performance from code review and architecture analysis.

**Use when:** diagnosing slow rendering, janky scrolling, high CPU/memory usage, excessive view updates, or layout thrash — and when Instruments profiling is needed to confirm root causes.

### 3. SwiftUI View Refactor (`swiftui-view-refactor`)
Refactor and review SwiftUI view files for consistent structure, dependency injection, and Observation usage.

**Use when:** cleaning up view layout and ordering, fixing view model initialization, standardizing `@Observable` state usage, or applying MV patterns to keep views small and composable.

## Quick Reference

| Scenario | Skill |
|----------|-------|
| New screen or component | `swiftui-ui-patterns` |
| Slow scrolling / jank | `swiftui-performance-audit` |
| Refactoring existing views | `swiftui-view-refactor` |
| Performance regression | `swiftui-performance-audit` |
| Navigation architecture | `swiftui-ui-patterns` |

## How to Use

Each skill is a self-contained directory. Read the `SKILL.md` inside each subdirectory for full guidance:

```
ios-swiftui-toolkit/
├── swiftui-ui-patterns/
│   └── SKILL.md + references/
├── swiftui-performance-audit/
│   └── SKILL.md + references/
└── swiftui-view-refactor/
    └── SKILL.md + references/
```
