# Playwright Best Practices

A structured repository for creating and maintaining Playwright TypeScript Best Practices optimized for agents and LLMs.

## Structure

- `rules/` - Individual rule files (one per rule)
  - `_sections.md` - Section metadata (titles, impacts, descriptions)
  - `_template.md` - Template for creating new rules
  - `area-description.md` - Individual rule files
- `src/` - Build scripts and utilities
- `metadata.json` - Document metadata (version, organization, abstract)
- **`AGENTS.md`** - Compiled output (generated)
- **`test-cases.json`** - Test cases for LLM evaluation (generated)

## Getting Started

```bash
pnpx add-skill https://github.com/vitalics/playwright-labs/tree/main/packages/playwright-best-practices # pnpm
npx add-skill https://github.com/vitalics/playwright-labs/tree/main/packages/playwright-best-practices # npm
```

## Getting Started (contributing)

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Build AGENTS.md from rules:

   ```bash
   pnpm build
   ```

3. Validate rule files:

   ```bash
   pnpm validate
   ```

4. Extract test cases:
   ```bash
   pnpm extract-tests
   ```

## Creating a New Rule

1. Copy `rules/_template.md` to `rules/area-description.md`
2. Choose the appropriate area prefix:
   - `stable-` for Test Stability & Reliability (Section 1)
   - `speed-` for Test Execution Speed (Section 2)
   - `locator-` for Locator Best Practices (Section 3)
   - `assertion-` for Assertions & Waiting (Section 4)
   - `parallel-` for Parallel Execution (Section 5)
   - `fixture-` for Fixtures & Test Organization (Section 6)
   - `debug-` for Debugging & Maintenance (Section 7)
   - `advanced-` for Advanced Patterns (Section 8)
3. Fill in the frontmatter and content
4. Ensure you have clear examples with explanations
5. Run `pnpm build` to regenerate AGENTS.md and test-cases.json

## Rule File Structure

Each rule file should follow this structure:

````markdown
---
title: Rule Title Here
impact: MEDIUM
impactDescription: Optional description
tags: tag1, tag2, tag3
---

## Rule Title Here

Brief explanation of the rule and why it matters.

**Incorrect (description of what's wrong):**

```typescript
// Bad code example
```
````

**Correct (description of what's right):**

```typescript
// Good code example
```

Optional explanatory text after examples.

Reference: [Link](https://example.com)

## File Naming Convention

- Files starting with `_` are special (excluded from build)
- Rule files: `area-description.md` (e.g., `stable-auto-waiting.md`)
- Section is automatically inferred from filename prefix
- Rules are sorted alphabetically by title within each section
- IDs (e.g., 1.1, 1.2) are auto-generated during build

## Impact Levels

- `CRITICAL` - Highest priority, major stability/performance gains
- `HIGH` - Significant test reliability improvements
- `MEDIUM-HIGH` - Moderate-high gains
- `MEDIUM` - Moderate improvements
- `LOW-MEDIUM` - Low-medium gains
- `LOW` - Incremental improvements

## Scripts

- `pnpm build` - Compile rules into AGENTS.md
- `pnpm validate` - Validate all rule files
- `pnpm extract-tests` - Extract test cases for LLM evaluation
- `pnpm dev` - Build and validate

## Contributing

When adding or modifying rules:

1. Use the correct filename prefix for your section
2. Follow the `_template.md` structure
3. Include clear bad/good examples with explanations
4. Add appropriate tags
5. Run `pnpm build` to regenerate AGENTS.md and test-cases.json
6. Rules are automatically sorted by title - no need to manage numbers!

## Categories Overview

### 1. Test Stability & Reliability (CRITICAL)

The foundation of reliable test automation. Flaky tests undermine confidence and waste developer time.

### 2. Test Execution Speed (CRITICAL)

Fast feedback loops are essential for developer productivity and CI/CD pipelines.

### 3. Locator Best Practices (HIGH)

Robust locators are the backbone of maintainable tests that survive UI changes.

### 4. Assertions & Waiting (HIGH)

Proper assertions and waiting strategies prevent flakiness and ensure tests validate the right things.

### 5. Parallel Execution (MEDIUM-HIGH)

Efficient parallel test execution dramatically reduces total test suite runtime.

### 6. Fixtures & Test Organization (MEDIUM)

Well-organized tests with proper fixtures improve maintainability and reusability.

### 7. Debugging & Maintenance (MEDIUM)

Good debugging practices and maintainable test code reduce time spent fixing tests.

### 8. Advanced Patterns (LOW)

Advanced patterns for specific cases that require careful implementation.

## Acknowledgments

Inspired by the agent-skills repository structure from [@shuding](https://x.com/shuding) at [Vercel](https://vercel.com).
