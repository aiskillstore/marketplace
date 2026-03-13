---
name: web-design-guidelines
description: "Review UI code for Web Interface Guidelines compliance. Use when asked to \"review my UI\", \"check accessibility\", \"audit design\", \"review UX\", or \"check my site against best practices\". Fetches latest Vercel guidelines and checks files against all rules."
metadata:
  author: vercel
  version: 1.0.0
  argument-hint: "<file-or-pattern>"
  tags: UI, review, web-interface, guidelines, vercel, design-audit, UX
  platforms: Claude, ChatGPT, Gemini
---


# Web Interface Guidelines Review

Review files for compliance with Vercel's Web Interface Guidelines.

## When to use this skill

- **UI code review**: check compliance with Web Interface Guidelines
- **Accessibility check**: when asked "check accessibility"
- **Design audit**: when asked "audit design"
- **UX review**: when asked "review UX"
- **Best practices review**: when asked "check my site against best practices"

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Instructions

### Step 1: Fetch Guidelines

**Use WebFetch**:
```
WebFetch URL: https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
Prompt: "Extract all UI rules and guidelines"
```

### Step 2: Analyze Files

Read and analyze the files or patterns provided by the user.

**Files to analyze**:
- React/Vue/Svelte components
- HTML files
- CSS/SCSS files
- TypeScript/JavaScript files

### Step 3: Apply Rules

Apply all rules from the fetched guidelines to the files and output violations.

## Input Format

### Required info
- **File or pattern**: file path or glob pattern to review

### Input examples

```
Review my UI code:
- File: src/components/Button.tsx
```

```
Check accessibility:
- Pattern: src/**/*.tsx
```

## Output Format

Follow the format specified in the guidelines (typically `file:line`):

```
src/components/Button.tsx:15 - Button should have aria-label for icon-only buttons
src/components/Modal.tsx:42 - Modal should trap focus within itself
src/pages/Home.tsx:8 - Main content should be wrapped in <main> element
```

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

## Constraints

### Required Rules (MUST)

1. **Use latest guidelines**: fetch fresh guidelines from the source URL for every review
2. **Apply all rules**: check every rule from the fetched guidelines
3. **Accurate locations**: specify violation locations in `file:line` format

### Prohibited (MUST NOT)

1. **Use stale cache**: always fetch the latest guidelines
2. **Partial check**: do not apply only some rules

## Best practices

1. **Limit file scope**: be careful about context overflow when reviewing too many files at once
2. **Prioritize**: report critical issues first
3. **Suggest fixes**: include how to fix along with each violation

## References

- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## Metadata

### Version
- **Current version**: 1.0.0
- **Last updated**: 2026-01-22
- **Supported platforms**: Claude, ChatGPT, Gemini
- **Source**: vercel/agent-skills

### Related Skills
- [web-accessibility](../web-accessibility/SKILL.md): WCAG accessibility implementation
- [ui-component-patterns](../ui-component-patterns/SKILL.md): UI component patterns

### Tags
`#UI` `#review` `#web-interface` `#guidelines` `#vercel` `#design-audit` `#UX` `#frontend`
