---
name: codebase-analysis
description: Systematically analyze codebase structure, complexity, dependencies, and architectural patterns to understand project organization
version: 1.0.0
author: AI-Vibe-Prompts
tags: [analysis, code-quality, architecture, dependencies]
auto_invoke: true
---

# Codebase Analysis Skill

## Objective

Perform comprehensive, systematic analysis of project codebases to understand:
- Project structure and organization
- Technology stack and dependencies
- Architectural patterns and conventions
- Code complexity and quality metrics
- Key components and their relationships

## When to Use This Skill

Auto-invoke when:
- Starting work on a new project
- User asks to "analyze", "review", "audit", or "understand" the codebase
- Before making architectural decisions
- Planning refactoring or major changes
- Onboarding new developers

## Analysis Methodology

### Phase 1: Discovery (Project Structure)

**Goal**: Map the high-level project organization

**Tools**: Glob, LS, Read

**Process**:
1. **Identify project type** by reading `package.json`, `tsconfig.json`, or framework-specific configs
2. **Map directory structure** using LS at root level:
   ```
   Key directories to identify:
   - Source code: src/, app/, pages/, components/
   - Tests: __tests__/, tests/, *.test.*, *.spec.*
   - Config: config/, .config/
   - Documentation: docs/, README.md
   - Build output: dist/, build/, .next/
   ```
3. **Scan for important files**:
   - Build configs: `vite.config.*, webpack.config.*, next.config.*`
   - TypeScript: `tsconfig.json`, `tsconfig.*.json`
   - Package management: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - Environment: `.env*`, `.env.example`
   - Git: `.gitignore`, `.git/`

### Phase 2: Technology Stack Analysis

**Goal**: Identify frameworks, libraries, and versions

**Tools**: Read, Grep

**Process**:
1. **Read package.json**:
   - Extract `dependencies` (runtime libraries)
   - Extract `devDependencies` (development tools)
   - Note `scripts` (available commands)
   - Check `engines` (Node.js version requirements)

2. **Identify framework**:
   - Next.js: Check for `next` in dependencies, `next.config.*`, `app/` or `pages/` directory
   - React: Check for `react` and `react-dom`
   - Vue: Check for `vue`, `*.vue` files
   - Svelte: Check for `svelte`, `*.svelte` files
   - Angular: Check for `@angular/core`, `angular.json`

3. **Identify key libraries**:
   - State management: Redux, Zustand, MobX, Pinia
   - Routing: react-router, vue-router, next/navigation
   - UI libraries: MUI, Ant Design, shadcn/ui, Chakra UI
   - Styling: Tailwind CSS, styled-components, emotion, CSS modules
   - Testing: Vitest, Jest, Playwright, Cypress
   - Build tools: Vite, Webpack, esbuild, Turbopack

### Phase 3: Architecture Pattern Analysis

**Goal**: Understand code organization and patterns

**Tools**: Grep, Glob, Read

**Process**:
1. **Component patterns** (for React/Vue/Svelte):
   ```
   Use Glob to find: **/*.{jsx,tsx,vue,svelte}
   Analyze:
   - Component naming conventions
   - File structure (co-located styles, tests)
   - Component size (lines of code)
   ```

2. **API/Backend patterns**:
   ```
   Use Grep to search for:
   - API routes: "export.*GET|POST|PUT|DELETE"
   - Database queries: "prisma\.|mongoose\.|sql"
   - Authentication: "auth|jwt|session"
   ```

3. **State management patterns**:
   ```
   Use Grep to find:
   - Context API: "createContext|useContext"
   - Redux: "createSlice|useSelector"
   - Zustand: "create.*useStore"
   ```

4. **File organization patterns**:
   - Monorepo: Check for `packages/`, `apps/`, `turbo.json`, `nx.json`
   - Feature-based: Check for directories like `features/`, `modules/`
   - Layer-based: Check for `components/`, `services/`, `utils/`, `hooks/`

### Phase 4: Code Quality & Complexity Assessment

**Goal**: Identify potential issues and technical debt

**Tools**: Grep, Bash, Read

**Process**:
1. **Linting & Formatting**:
   - Check for: `.eslintrc*`, `.prettierrc*`, `biome.json`
   - Run linter if available: `npm run lint` (via Bash)

2. **Testing coverage**:
   - Find test files: Use Glob for `**/*.{test,spec}.{js,ts,jsx,tsx}`
   - Calculate coverage: Run `npm run test:coverage` if available

3. **TypeScript strictness**:
   - Read `tsconfig.json`
   - Check `strict: true`, `strictNullChecks`, etc.
   - Look for `@ts-ignore` or `any` usage (Grep)

4. **Code complexity indicators**:
   ```
   Use Grep to flag potential issues:
   - Large files: Find files > 500 lines
   - Deep nesting: Search for excessive indentation
   - TODO/FIXME comments: Grep for "TODO|FIXME|HACK"
   - Console logs: Grep for "console\.(log|debug|warn)"
   ```

### Phase 5: Dependency & Security Analysis

**Goal**: Identify outdated or vulnerable dependencies

**Tools**: Bash, Read

**Process**:
1. **Check for lock files**:
   - Presence of `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`

2. **Run security audit** (if npm/pnpm available):
   ```bash
   npm audit --json
   # or
   pnpm audit --json
   ```

3. **Check for outdated dependencies**:
   ```bash
   npm outdated
   ```

## Output Format

Provide a structured analysis report:

```markdown
# Codebase Analysis Report

## Project Overview
- **Name**: [project name from package.json]
- **Type**: [framework/library]
- **Version**: [version]
- **Node.js**: [required version]

## Technology Stack
### Core Framework
- [Framework name & version]

### Key Dependencies
- UI: [library]
- State: [library]
- Routing: [library]
- Styling: [library]
- Testing: [library]

### Build Tools
- [Vite/Webpack/etc]

## Architecture

### Directory Structure
```
[tree-like representation of key directories]
```

### Patterns Identified
- [Component patterns]
- [State management approach]
- [API structure]
- [File organization]

## Code Quality Metrics
- **TypeScript**: [strict/loose/none]
- **Linting**: [ESLint/Biome/none]
- **Testing**: [X test files found, coverage: Y%]
- **Code Issues**: [TODOs: X, Console logs: Y]

## Recommendations
1. [Priority recommendation]
2. [Next priority]
3. ...

## Risk Areas
- [Potential issues or technical debt]

## Next Steps
- [Suggested actions based on analysis]
```

## Best Practices

1. **Progressive Detail**: Start with high-level overview, dive deeper only when needed
2. **Context Window Management**: For large codebases, analyze in chunks (by directory/feature)
3. **Tool Selection**: 
   - Use Glob for file discovery (faster than find)
   - Use Grep for pattern search (faster than reading all files)
   - Use Read only for critical files (package.json, configs)
4. **Time Efficiency**: Complete analysis in < 60 seconds for typical projects
5. **Actionable Insights**: Always provide specific, actionable recommendations

## Integration with Other Skills

This skill works well with:
- `quality-gates` - Use analysis results to run appropriate quality checks
- `project-initialization` - Compare against templates to identify missing setup
- `refactoring-safe` - Identify refactoring opportunities
- Framework-specific skills (`nextjs-optimization`, `react-patterns`) - Auto-invoke based on detected framework

## Error Handling

If analysis cannot complete:
1. **Missing dependencies**: Suggest running `npm install`
2. **Corrupted files**: Report specific files and continue with partial analysis
3. **Large codebase**: Switch to targeted analysis mode (specific directories only)
4. **Permission issues**: Request necessary file access permissions

## Version History

- **1.0.0** (2025-01-03): Initial skill creation with progressive disclosure support
