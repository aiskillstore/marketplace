---
name: software-architecture
description: Document software architecture using ARCHITECTURE.md and docs/*.md files with Mermaid diagrams. Use proactively when ARCHITECTURE.md exists in project root, or invoke to create initial architecture documentation. Covers system design, data flows, component relationships, and code organization with references to key entry points and abstractions.
---

# Software Architecture Documentation

Document system architecture using a root `ARCHITECTURE.md` with detailed component docs in `docs/*.md`.

## Structure

```
project/
├── ARCHITECTURE.md      # High-level system overview
└── docs/
    ├── <component>.md   # Detailed component documentation
    └── ...
```

## Proactive Usage

When `ARCHITECTURE.md` exists in project root:

1. **Before major changes**: Read `ARCHITECTURE.md` to understand system structure
2. **After structural changes**: Update diagrams and entry points
3. **When adding components**: Create new `docs/*.md` file and link from `ARCHITECTURE.md`
4. **During refactoring**: Update affected diagrams and file references

## Creating Architecture Documentation

### Initial Setup Workflow

1. **Analyze codebase structure**
   - Identify entry points (main, CLI, API handlers)
   - Map major components and their responsibilities
   - Trace key data flows

2. **Create `ARCHITECTURE.md`**
   - Write system overview (1-2 paragraphs)
   - Add C4 Context diagram showing system boundaries
   - Document entry points table
   - List key abstractions
   - Add testing overview
   - Link to detail docs (create `docs/` section even if empty initially)

3. **Create detail docs for major components**
   - One file per logical component in `docs/`
   - Name files to match component names (flexible convention)
   - Include component-level diagrams

See [references/document-templates.md](references/document-templates.md) for complete templates.

## ARCHITECTURE.md Sections

### Required Sections

| Section | Content |
|---------|---------|
| Overview | 1-2 paragraphs on system purpose |
| System Diagram | C4 Context or Container diagram |
| Key Entry Points | Table of primary files with descriptions |
| Key Abstractions | Table of important classes/interfaces/functions |
| Testing | Overview of test strategy and key test locations |
| Detail Docs | Links to `docs/*.md` files |

### Optional Sections

| Section | Include When |
|---------|--------------|
| Data Flow | Complex pipelines or transformations |
| Code Organization | Non-obvious directory structure |
| Configuration | Significant config or environment setup |

## Detail Documents (`docs/*.md`)

Create a detail doc when a component:
- Has 3+ key files or abstractions
- Contains complex internal logic
- Interacts with multiple other components
- Needs sequence diagrams to explain flows

### Naming Convention

Flexible. Match the component's identity:
- `docs/auth.md` for authentication component
- `docs/data-pipeline.md` for data pipeline
- `docs/cli.md` for CLI handling

### Required Content

| Section | Content |
|---------|---------|
| Purpose | What this component does |
| Key Files | Table of important files |
| Key Abstractions | Classes, interfaces, functions |

### Optional Content

| Section | Include When |
|---------|--------------|
| Architecture Diagram | Multiple internal subcomponents |
| Sequence Diagram | Multi-step interactions |
| Dependencies | Non-obvious dependencies |
| Testing | Component-specific test patterns |
| Configuration | Component-specific config |

## Diagram Selection

| Diagram Type | Use For |
|--------------|---------|
| C4 Context | `ARCHITECTURE.md` - system boundaries and external actors |
| C4 Container | `ARCHITECTURE.md` - deployable units (services, databases) |
| C4 Component | `docs/*.md` - internal structure of a component |
| Flowchart | Control flow, pipelines, decision logic |
| Sequence | Request flows, API interactions, multi-step processes |
| ER Diagram | Data models, entity relationships |
| Class Diagram | Object hierarchies, interface implementations |

Start minimal (3-5 nodes). Add detail only when it improves clarity.

See [references/mermaid-patterns.md](references/mermaid-patterns.md) for diagram templates.

## Entry Points and Abstractions

### Entry Points Table

Document files that serve as starting points for understanding the codebase:

```markdown
| File | Description |
|------|-------------|
| `src/main.py` | Application entry point |
| `src/core/engine.py` | Core processing engine |
| `tests/conftest.py` | Test fixtures and setup |
```

Include:
- Application entry points (main, CLI, handlers)
- Core domain logic locations
- Configuration files
- Test setup and fixtures

### Key Abstractions Table

Document important classes, interfaces, and functions:

```markdown
| Abstraction | Location | Purpose |
|-------------|----------|---------|
| `Engine` | `src/core/engine.py` | Orchestrates processing |
| `Handler` | `src/api/base.py` | Request handling interface |
```

Focus on:
- Base classes and interfaces
- Core domain objects
- Public API surfaces
- Extension points

## Maintaining Documentation

### When to Update

| Trigger | Action |
|---------|--------|
| New component added | Create `docs/<component>.md`, add link to `ARCHITECTURE.md` |
| Entry point changed | Update entry points table |
| Major refactoring | Update affected diagrams and file references |
| New external dependency | Update C4 Context diagram |
| Component removed | Remove or archive corresponding detail doc |

### Update Checklist

After structural changes:
1. Verify entry points table is accurate
2. Check diagram nodes match actual components
3. Confirm file paths in tables are valid
4. Update any affected detail docs
