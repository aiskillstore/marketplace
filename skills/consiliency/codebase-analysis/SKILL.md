---
name: codebase-analysis
description: "Patterns and techniques for analyzing brownfield codebases. Use when onboarding to unfamiliar code, preparing for refactoring, conducting architecture reviews, or identifying technical debt."
---

# Codebase Analysis Skill

Systematically explore and understand existing codebases, including entry point discovery, dependency tracing, pattern detection, and technical debt identification.

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| ANALYSIS_DEPTH | standard | `quick` (5min), `standard` (30min), `deep` (1hr+) |
| OUTPUT_FORMAT | markdown | `markdown`, `json`, `c4` |
| INCLUDE_DEBT | true | Include technical debt assessment |
| INCLUDE_DIAGRAMS | true | Generate C4 diagrams |

## Instructions

**MANDATORY** - Follow the Workflow steps below in order. Do not skip steps.

- Start with entry points, not random files
- Trace dependencies before analyzing patterns
- Document findings as you go

## Red Flags - STOP and Reconsider

If you're about to:
- Analyze random files without finding entry points first
- Make architectural claims without tracing dependencies
- Skip pattern detection before identifying anti-patterns
- Report technical debt without severity classification

**STOP** -> Read the appropriate cookbook file -> Follow the workflow -> Then proceed

## Workflow

1. [ ] Quick Assessment: Project size, structure, config files
2. [ ] **CHECKPOINT**: Identify entry points (read `cookbook/entry-point-discovery.md`)
3. [ ] Trace dependencies from entry points
4. [ ] Detect architectural patterns
5. [ ] **CHECKPOINT**: Verify pattern detection before anti-pattern search
6. [ ] Identify anti-patterns and technical debt
7. [ ] Document findings with C4 diagrams (if INCLUDE_DIAGRAMS)

## Cookbook

### Entry Point Discovery
- IF: Starting analysis of unfamiliar codebase
- THEN: Read `cookbook/entry-point-discovery.md`
- RESULT: List of main entry points by framework

### Dependency Tracing
- IF: Need to understand how modules connect
- THEN: Read `cookbook/dependency-tracing.md`
- RESULT: Import chains, dependency graph

### Pattern Detection
- IF: Need to identify architectural style
- THEN: Read `cookbook/pattern-detection.md`
- RESULT: Identified patterns (MVC, Layered, etc.)

### Technical Debt Identification
- IF: Assessing code quality and debt
- THEN: Read `cookbook/debt-identification.md`
- RESULT: Prioritized debt inventory

## Quick Reference

### Entry Points by Stack

| Stack | Look For |
|-------|----------|
| Node.js | `package.json` main/bin, `index.js`, `server.js` |
| TypeScript | `tsconfig.json`, `src/index.ts` |
| Python | `__main__.py`, `app.py`, `wsgi.py` |
| Go | `main.go`, `cmd/*/main.go` |
| React | `src/index.tsx`, `pages/_app.tsx` |

See `reference/framework-patterns.md` for complete list.

### Common Patterns

| Pattern | Directory Signs |
|---------|-----------------|
| MVC | `models/`, `views/`, `controllers/` |
| Layered | `presentation/`, `business/`, `data/` |
| Hexagonal | `domain/`, `ports/`, `adapters/` |
| Microservices | `services/*/`, `packages/*/` |

## Output

### Standard Report Format

```markdown
# Codebase Analysis: [Project Name]

## Overview
- **Size**: X files, Y lines
- **Primary Language**: TypeScript
- **Framework**: Next.js
- **Architecture**: [Pattern]

## Entry Points
1. `src/pages/_app.tsx` - Application root
2. `src/api/` - API routes

## Key Dependencies
- [External deps list]

## Architecture Diagram
[C4 diagram if INCLUDE_DIAGRAMS]

## Technical Debt (if INCLUDE_DEBT)
| Issue | Severity | Location |
|-------|----------|----------|
| ... | High | ... |
```
