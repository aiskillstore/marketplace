---
name: format-standardize
description: Standardize formatting and apply consistent style to the deliverable. Use after generation to ensure the output matches the user's formatting standards and conventions.
---

# Format & Standardize Skill

## Purpose

Ensures the generated deliverable follows consistent formatting, style, and structure standards. This is the "polish" step that makes work look professional and maintainable.

## What to Do

1. **Review the generated deliverable**
2. **Load their standards** to understand formatting preferences
3. **Apply standardization**:
   - Code formatting (indentation, naming, structure)
   - Documentation formatting (headers, lists, spacing)
   - Consistency across all elements
   - Professional appearance
4. **Use their tools/conventions** if specified:
   - Example: "Use Prettier for code"
   - Example: "Use Markdown standard headers"
5. **Verify complete consistency** before delivery

## Format Checks by Type

### Code Features
- [ ] Consistent indentation (spaces/tabs)
- [ ] Naming conventions (camelCase, snake_case, etc.)
- [ ] Consistent spacing around operators and braces
- [ ] Comments formatted consistently
- [ ] Imports/exports organized
- [ ] Line length consistent
- [ ] Semicolons or no-semicolons applied consistently
- [ ] Quotes style (single/double) consistent

### Documentation
- [ ] Consistent header levels (# ## ###)
- [ ] Consistent list formatting (bullets vs numbers)
- [ ] Code blocks properly formatted
- [ ] Links properly formatted
- [ ] Consistent spacing between sections
- [ ] Table formatting (if applicable)
- [ ] Consistent punctuation

### Refactoring
- [ ] Before code formatted consistently
- [ ] After code formatted consistently
- [ ] Explanations formatted clearly
- [ ] Highlight differences clearly

### Test Suite
- [ ] Test file organization
- [ ] Test function naming consistent
- [ ] Assertion formatting consistent
- [ ] Setup/teardown indentation
- [ ] Comments consistent format

### Content Creation
- [ ] Section headers consistent
- [ ] Example formatting consistent
- [ ] List formatting consistent
- [ ] Tone/voice consistent throughout
- [ ] Line breaks for readability

## Process

1. Take the generated deliverable
2. Load their saved standards using StandardsRepository (look for formatting preferences)
3. Apply standardization rules
4. Format code/text with appropriate tools:
   - Code: ESLint, Prettier, or manual formatting
   - Docs: Markdown standards
   - Content: Style guide consistency
5. Do a final pass for consistency
6. Return the formatted output

## Loading Standards

Use StandardsRepository to access formatting preferences:

```javascript
const standards = standardsRepository.getStandards(context.projectType)
if (standards && standards.commonPatterns) {
  // Apply their formatting preferences from commonPatterns
  standards.commonPatterns.forEach(pattern => {
    // Example: "Use 2-space indentation", "Sort imports alphabetically"
    applyFormattingPattern(pattern)
  })
}
```

See `.claude/lib/standards-repository.md` for interface details.

## Output Format

```
# Formatting Applied

## Standards Used
- [First formatting standard]
- [Second formatting standard]
- [Tools/conventions applied]

## Changes Made
- [List of formatting changes applied]
- [Example: "Sorted imports alphabetically"]
- [Example: "Applied 2-space indentation"]

## The Formatted Deliverable
[Complete formatted output, ready to use]

## Validation
- Consistent formatting: ✓
- Professional appearance: ✓
- Ready for review/delivery: ✓
```

## Success Criteria

✓ All formatting is consistent
✓ Follows user's standards
✓ Professional appearance
✓ Ready for code review or publication
✓ No formatting inconsistencies remain

## Common Formatting Rules

**For Code:**
- Use their linter (ESLint, Pylint, etc.)
- Apply their code formatter (Prettier, Black, etc.)
- Follow their naming conventions
- Consistent indentation throughout

**For Documentation:**
- Consistent markdown formatting
- Proper header hierarchy
- Consistent code block formatting
- Proper link formatting

**For Content:**
- Consistent section structure
- Consistent list formatting
- Professional tone throughout
- Proper punctuation and capitalization

## Example

**Input (Before Formatting)**:
```javascript
const MyComponent = ( props ) => {
  return (
    <div>
      { props.title }
    </div>
  );
};

export default MyComponent
```

**After Formatting** (assuming standard React conventions):
```javascript
const MyComponent = (props) => {
  return (
    <div>
      {props.title}
    </div>
  );
};

export default MyComponent;
```

**Changes Made**:
- Removed spaces in function parameters
- Removed spaces around JSX expression braces
- Added semicolon
- Consistent indentation

## Notes

- If user defined formatting preferences in standards, USE THEM
- Professional formatting increases perceived quality significantly
- Consistency matters more than the specific choice (spaces vs tabs - pick one and stick with it)
- This step makes the deliverable look "production-ready"
