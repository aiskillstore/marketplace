---
name: typescript-review
description: Review TypeScript and JavaScript code changes for compliance with Metabase coding standards, style violations, and code quality issues. Use when reviewing pull requests or diffs containing TypeScript/JavaScript code.
allowed-tools: Read, Grep, Bash, Glob
---

# TypeScript/JavaScript Code Review Skill
## Linting and Formatting

- **Lint:** `yarn lint-eslint-pure`
  - Run ESLint on the codebase
- **Format:** `yarn prettier`
  - Format code using Prettier
- **Type Check:** `yarn type-check-pure`
  - Run TypeScript type checking

## Testing

### JavaScript/TypeScript Tests

- **Test a specific file:** `yarn test-unit-keep-cljs path/to/file.unit.spec.js`
- **Test by pattern:** `yarn test-unit-keep-cljs -t "pattern"`
  - Runs tests matching the given pattern

### ClojureScript Tests

- **Test ClojureScript:** `yarn test-cljs`
  - Run ClojureScript tests

## Code Review Guidelines

Review pull requests with a focus on:

- Compliance with project coding standards and conventions
- Code quality and best practices
- Clear and correct JSDoc comments
- Type safety and proper TypeScript usage
- React best practices (when applicable)