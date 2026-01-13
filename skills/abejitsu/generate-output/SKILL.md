---
name: generate-output
description: Create the deliverable (code, documentation, tests, content) following the user's standards and best practices. Use after validation passes to actually build the work product.
---

# Generate Output Skill

## Purpose

Transforms validated requirements into actual deliverables (code, documentation, tests, content). This skill follows the user's principles and common patterns defined in their standards.

## What to Do

1. **Read the validated requirements** from the previous step
2. **Load the project type's standards** (from standards.json) to understand their principles and patterns
3. **Generate the deliverable** based on:
   - User's specific requirements
   - Their saved principles for this project type
   - Their common patterns (what they always do)
   - Best practices for this type of work
4. **Follow their patterns** - If they defined common patterns, include them:
   - Example: "Always include error handling" → include it
   - Example: "Always write JSDoc comments" → include it
5. **Create complete, ready-to-use output**

## Project Type Specific Guidance

### Code Features
- Write complete, production-ready code
- Include prop types, type annotations, or schema validation
- Include error handling
- Add comments for complex logic
- Include example usage or test case
- Follow their coding standards (naming, structure, patterns)

### Documentation
- Clear structure with headers
- Include purpose/overview at top
- Add examples and use cases
- Include troubleshooting if applicable
- Link related documentation
- Use their documentation template if defined

### Refactoring
- Show the "before" code
- Show the "after" refactored code
- Explain the improvements
- Highlight what changed and why
- Include the refactored code ready to copy
- Note any behavioral changes

### Test Suite
- Write comprehensive tests
- Test happy path and edge cases
- Use descriptive test names
- Include setup/teardown as needed
- Follow their testing conventions
- Ensure tests are maintainable

### Content Creation
- Compelling introduction
- Clear structure with sections
- Use headers, lists, and examples
- Include practical examples
- Conclusion with key takeaways
- Appropriate tone for audience

## Process

1. Review requirements
2. Load their standards using StandardsRepository
3. Identify their common patterns for this type
4. Generate the output
5. Do a self-check against their principles
6. Present the output with brief summary

## Loading Standards

Use StandardsRepository to access standards:

```javascript
const standards = standardsRepository.getStandards(context.projectType)
if (standards) {
  // Use their principles and patterns
  const principles = standards.principles
  const patterns = standards.commonPatterns
  // Generate output following their standards
} else {
  // Generate following best practices
}
```

See `.claude/lib/standards-repository.md` for interface details.

## Output Format

Deliver the work with:

```
# [Title of Deliverable]

## Summary
[Brief description of what was created]

## Principles Applied
- [First principle from their standards]
- [Second principle]
- [Third principle]

## Common Patterns Included
- [Pattern 1: brief explanation]
- [Pattern 2: brief explanation]

## The Deliverable
[Complete code, documentation, tests, or content]

## Next Steps
[What they should do next - formatting, testing, review]
```

## Success Criteria

✓ Deliverable is complete and ready to use
✓ Follows user's principles and patterns
✓ Appropriate to project type
✓ Professional quality
✓ Includes necessary supporting elements (comments, examples, structure)

## Example Generation

**Project Type**: React Component
**User Requirements**: "Searchable dropdown component with keyboard nav"
**Their Standards Include**:
- Principles: "Reusable, testable, well-documented"
- Patterns: "Use TypeScript, include PropTypes, export story"

**Generated Output Includes**:
- Complete React component in TypeScript
- PropTypes validation
- Error boundary
- Keyboard event handlers
- Storybook story file
- Usage example
- Comments on complex logic

## Notes

- If user's standards define specific patterns, ALWAYS include them
- Go above minimum - create something they're proud to use
- If unsure about a detail, follow their anti-patterns guidance (do opposite of what they said to avoid)
- Quality over quantity - one well-crafted deliverable beats multiple mediocre ones
