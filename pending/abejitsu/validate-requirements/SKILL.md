---
name: validate-requirements
description: Validate that input meets prerequisites based on the user's saved standards for the project type. Use at the start of any quality pipeline to ensure the user has provided sufficient requirements.
---

# Validate Requirements Skill

## Purpose

Ensures the user's input (requirements, description, source material) meets the prerequisites defined in their standards for this project type. This is the first gate in the quality pipeline.

## What to Check

Based on the user's saved standards for the project type, verify:

1. **Completeness** - Is there enough information?
   - Examples: "Describe the component's purpose", "Explain what refactoring is needed", "Provide the blog topic"

2. **Clarity** - Is the description clear and specific?
   - Not vague: "Write something" → needs detail
   - Specific: "Create a dropdown component with keyboard navigation" → clear

3. **Format** - Is it in a recognizable format?
   - Code examples provided? Existing code to refactor?
   - Links to resources? Topic outline for content?

4. **Sufficiency** - Is there enough context?
   - Does the user explain the "why"?
   - Are constraints/requirements mentioned?

5. **Standards Alignment** - Does it match their defined validation rules?
   - Read the project type's saved standards (from standards.json)
   - Check against their validationRules section

## Process

1. Read the user's input/requirements
2. Load their standards for this project type using StandardsRepository
3. Check against their defined validation rules
4. Scan for common issues:
   - Empty or minimal descriptions
   - Conflicting requirements
   - Missing critical context
5. Report findings clearly

## Using Standards

Access standards through StandardsRepository:

```javascript
const standards = standardsRepository.getStandards(context.projectType)
if (standards && standards.validationRules) {
  // Check input against their validation rules
  checkAgainstRules(input, standards.validationRules)
} else {
  // No custom standards yet, use general validation
  performGeneralValidation(input)
}
```

See `.claude/lib/standards-repository.md` for interface details.

## Output

Return a structured validation result:

```json
{
  "status": "valid" or "invalid",
  "issues": [
    "list of specific problems found",
    "e.g., 'Missing example code to refactor'",
    "e.g., 'Unclear what success looks like'"
  ],
  "validationDetails": {
    "clarity": "pass" or "needs_clarification",
    "completeness": "pass" or "incomplete",
    "contextSufficient": "pass" or "needs_more_context"
  },
  "recommendation": "proceed_to_next_step" or "ask_user_to_clarify_X",
  "summary": "Brief description of validation result"
}
```

## Success Criteria

✓ Status is "valid"
✓ No critical issues found
✓ Input aligns with their standards
✓ Enough information to proceed to generation

## Example Validation

**Project Type**: React Components

**User Input**: "Create a dropdown component"

**Validation Process**:
1. Load React component standards
2. Check: "Must describe component's purpose"
   - FAIL: User only said "dropdown component"
3. Check: "Should specify required and optional props"
   - FAIL: No props mentioned
4. Output:
   ```json
   {
     "status": "invalid",
     "issues": [
       "Need more detail on component purpose (e.g., where will it be used?)",
       "Should specify what props the dropdown needs",
       "Should describe dropdown behavior (open/close, keyboard nav, etc.)"
     ],
     "recommendation": "Ask user to provide more detail before generating"
   }
   ```

**User's Updated Input**: "Create a searchable dropdown component for selecting team members. It should have keyboard navigation (arrow keys, enter to select). Props: options (array), onSelect (callback), placeholder (string)."

**Validation Result**:
```json
{
  "status": "valid",
  "issues": [],
  "summary": "Requirements are clear, specific, and complete"
}
```

## Notes for Implementation

- If user's standards don't exist yet, use general validation (is there enough to work with?)
- Always be specific about WHAT is missing, not just "not valid"
- When recommending clarification, suggest specific questions
- If input is close to valid, ask 1-2 clarifying questions instead of rejecting it
