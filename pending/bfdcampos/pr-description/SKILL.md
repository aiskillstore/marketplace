---
name: pr-description
description: Guide for creating comprehensive PR descriptions with proper structure, diagrams, and documentation for code reviews.
---

# PR Description Skill

This skill provides a structured approach to creating comprehensive pull request descriptions that help reviewers understand changes quickly.

## When to Use

Use this skill when:
- Creating a new pull request
- User asks to "create a PR description" or "write a PR description"
- Documenting significant code changes for review

## File Creation (Optional)

If saving the PR description to a file:
- **Pattern**: `pr_description_<descriptive_title>_<timestamp>.md`
- **Get timestamp**: `date +"%Y%m%d_%H%M%S"`
- **Example**: `pr_description_user_auth_refactor_20250612_152832.md`

## Required Structure

```markdown
# PR Title: [Descriptive Title]

## 📋 Summary
Brief overview of what this PR accomplishes in 2-3 sentences.

## 📊 Data Flow Diagram
[Mermaid diagram showing the flow/architecture - use `mermaid` skill for styling]

## 🗂️ Entity Relationship Diagram
[Include if creating/modifying data relationships - Mermaid ERD]

## 🎯 Goals
- Primary objective 1
- Primary objective 2
- Any secondary objectives

## 🔍 Changes in this PR
- Description of key changes
- Any config file changes
- Schema modifications
- Breaking changes (if any)

## 🧪 Testing
### Commands Run
```bash
# List exact commands used for testing
npm test
npm run lint
```

### Results
- ✅ All tests passed
- ✅ Linting passed
- ✅ Build successful
- Include any relevant screenshots or output

### Validation
- Key scenarios tested
- Edge cases covered
- Performance considerations

## 📋 Notes for Reviewers
- Pay attention to: [specific areas]
- Assumptions made: [list any assumptions]
- Dependencies: [any upstream/downstream impacts]

## 🔜 Future Work
- Any follow-up tasks not included in this PR
- Potential optimisations
- Additional testing needed
```

## Mermaid Diagrams

**Use the `mermaid` skill** for diagram syntax and styling that works in both light and dark mode.

### Data Flow Diagram
Show the complete flow of data or logic:
- Input sources
- Processing steps
- Output destinations
- Include a colour-coded legend

### Entity Relationship Diagram (When Applicable)
Show object/data relationships:
- Primary keys (PK)
- Foreign keys (FK)
- Relationship cardinality (one-to-many, many-to-many)

## Content Guidelines

### Summary Section
- Explain business context briefly
- Highlight key benefits
- Keep it to 2-3 sentences

### Changes Section
- Focus on what matters to reviewers
- Group related changes together
- Note any breaking changes prominently

### Testing Section
- **ALWAYS include exact commands run**
- Show evidence of successful tests
- Include validation results
- Add screenshots when helpful

### Future Work Section
- List intentionally deferred items
- Suggest optimisations or enhancements
- Note any technical debt created

## Key Principles

1. **Be specific**: Include exact commands, concrete examples
2. **Show evidence**: Screenshots, command outputs, test results
3. **Think reviewer-first**: What would a reviewer need to understand the changes?
4. **Business context**: Explain the "why" not just the "what"
5. **Keep it scannable**: Use headers, bullet points, and formatting

## Good Examples

### Good Summary
"This PR refactors the user authentication flow to use JWT tokens instead of session cookies. The change improves scalability for our microservices architecture and reduces server-side session storage requirements."

### Good Testing Description
```bash
# Commands run
npm run test:unit
npm run test:integration
npm run lint
```

**Results:**
- ✅ 47 unit tests passed
- ✅ 12 integration tests passed
- ✅ No linting errors
- ✅ Manual testing completed on staging environment

## Error Handling

- If unable to determine scope of changes, ask user for clarification
- If testing hasn't been completed, remind user to run tests first
- If no diagrams provided, create placeholder diagrams and ask user to review
