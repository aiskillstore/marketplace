---
name: skill-name-here
description: This skill should be used when... [Be specific about what it does and when to use it]
allowed-tools: (optional - leave empty to allow all tools, or specify: Read, Write, Bash, etc.)
---

# Skill Title

Brief overview of what this skill does and its purpose.

## Instructions

Provide step-by-step instructions using imperative/infinitive form (verb-first):

1. **First step** - Describe action to take
   - Sub-detail if needed
   - Another detail

2. **Second step** - Provide clear guidance
   - Use objective language: "To accomplish X, do Y"
   - Avoid second person: ~~"You should do X"~~

3. **Additional steps** - As needed for the workflow

## Working with Bundled Resources

### Scripts

If the skill includes scripts in `scripts/` directory:

```bash
# Execute the script
python scripts/example_script.py --param value
```

Explain when and how to use each script.

### References

If the skill includes reference documentation in `references/` directory:

- Read `references/schema.md` for database schema information
- Refer to `references/api_docs.md` for API specifications
- Check `references/policies.md` for company guidelines

Load references into context only when needed for the task.

### Assets

If the skill includes assets in `assets/` directory:

- Copy `assets/template.html` to output location
- Use `assets/logo.png` in generated documents
- Base new files on `assets/boilerplate/` template

Assets are not loaded into context but used directly in output.

## Examples (Optional)

Provide concrete examples of skill usage:

**Example 1:**
```
User: "Rotate this PDF 90 degrees"
Action: Execute scripts/rotate_pdf.py with angle=90
Output: Rotated PDF file
```

## Important Notes (Optional)

- Any constraints or limitations
- Prerequisites or dependencies
- Common gotchas to avoid
- Integration with other tools/skills

## Success Criteria (Optional)

Define what successful execution looks like:
- ✓ Criterion 1 met
- ✓ Criterion 2 met
- ✓ Output validated
