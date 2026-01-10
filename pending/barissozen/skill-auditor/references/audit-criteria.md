# Skill Audit Criteria

Detailed scoring rubrics and guidelines for auditing skills.

## Scoring Rubric

### Score Deductions

| Issue | Deduction | Severity |
|-------|-----------|----------|
| Missing SKILL.md | -10 | Critical |
| Missing frontmatter | -3 | Error |
| Missing name field | -2 | Error |
| Missing description field | -2 | Error |
| Short description (<50 chars) | -1 | Warning |
| TODO in description | -2 | Error |
| TODO placeholder in content | -0.5 each | Warning |
| Missing "When to Use" section | -1 | Warning |
| Missing "Workflow" section | -1 | Warning |
| Excessive word count (>5000) | -1 | Warning |
| Empty subdirectory | -0.5 | Warning |
| Non-executable Python script | -0.5 | Warning |

### Score Interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 9-10 | Excellent | Ready for use |
| 7-8.9 | Good | Minor improvements recommended |
| 5-6.9 | Needs Work | Address warnings before use |
| <5 | Critical | Must fix errors before use |

## Frontmatter Requirements

### Required Fields

**name:**
- Must be present
- Use hyphens for multi-word names (e.g., `my-skill-name`)
- Should be descriptive and unique

**description:**
- Must be present
- Minimum 50 characters recommended
- Should clearly state what the skill does
- Should specify trigger conditions (e.g., "Use when users want to...")
- Must NOT contain TODO placeholders

### Good Description Examples

```yaml
# Good - specific triggers
description: Validates type consistency across Rust, TypeScript, PostgreSQL boundaries. Use when reviewing code, debugging type mismatches, or validating API contracts.

# Good - clear purpose
description: DeFi protocol expert ensuring correct data formats, types, denominations, and API structures. MUST be consulted before writing ANY protocol integration code.

# Bad - too short
description: Helps with code review.

# Bad - contains TODO
description: TODO: Write a description for this skill.
```

## Content Structure

### Required Sections

1. **Title (H1)** - Clear skill name
2. **Introduction** - 2-3 sentences explaining purpose
3. **When to Use** - Bullet list of trigger conditions
4. **Workflow** - Step-by-step instructions

### Optional Sections

- **Bundled Resources** - Document scripts, references, assets
- **Best Practices** - Guidelines for effective use
- **Examples** - Usage examples

## Decomposition Guidelines

### When to Split a Skill

Consider splitting when ANY of these apply:

1. **Word count exceeds 5000**
   - Move detailed content to references/
   - Split into focused sub-skills

2. **More than 3 distinct concerns**
   - Each concern should be its own skill
   - Create a parent skill that orchestrates sub-skills

3. **Complex workflow (>8 steps)**
   - Break into logical phases
   - Each phase can be a sub-skill

4. **Multiple file formats or tools**
   - Consider format-specific skills
   - Create a router skill that delegates

5. **Mixed audiences**
   - Separate technical vs. user-facing skills
   - Create role-specific variations

### Decomposition Patterns

**Hub and Spoke:**
```
parent-skill/
├── SKILL.md (orchestrates sub-skills)
└── sub-skills/
    ├── sub-skill-a/
    ├── sub-skill-b/
    └── sub-skill-c/
```

**Layered:**
```
skills/
├── core-skill/      (foundational logic)
├── extended-skill/  (uses core-skill)
└── specialized-skill/ (domain-specific)
```

**Format-Specific:**
```
skills/
├── document-processor/  (router)
├── pdf-processor/       (format-specific)
├── docx-processor/      (format-specific)
└── xlsx-processor/      (format-specific)
```

## Resource Guidelines

### scripts/

**Include when:**
- Same code written repeatedly
- Deterministic reliability needed
- Complex transformations required

**Requirements:**
- Python scripts must be executable (`chmod +x`)
- Include shebang line (`#!/usr/bin/env python3`)
- Provide usage documentation in docstring

### references/

**Include when:**
- Detailed documentation needed
- Information exceeds SKILL.md limits
- Schemas, APIs, or specifications to reference

**Best practices:**
- Keep files focused (<10k words each)
- Include grep patterns for large files
- Use clear file naming

### assets/

**Include when:**
- Templates needed for output
- Images, icons, or media required
- Boilerplate code used in generation

**Note:** Assets are NOT loaded into context, only used in output.

## Common Issues and Fixes

### Issue: TODO Placeholders Remain

**Fix:** Replace all TODO items with actual content or remove if not needed.

```markdown
# Bad
- TODO: Describe trigger condition 1

# Good
- Users ask to convert PDF files
- File path ends with .pdf extension
```

### Issue: Description Too Generic

**Fix:** Add specific trigger conditions and use cases.

```markdown
# Bad
description: Helps with code tasks.

# Good
description: Reviews Python code for security vulnerabilities, focusing on OWASP Top 10. Use when auditing code for security issues or before deploying to production.
```

### Issue: Empty Subdirectories

**Fix:** Either add relevant content or remove the directory entirely.

```bash
# Remove if not needed
rm -rf skill-name/assets/
rm -rf skill-name/references/
```

### Issue: Non-Executable Scripts

**Fix:** Add executable permission.

```bash
chmod +x skill-name/scripts/*.py
```

### Issue: Excessive Word Count

**Fix:** Move detailed content to references.

1. Identify detailed sections (schemas, long explanations)
2. Create files in `references/` directory
3. Reference them in SKILL.md: "See `references/details.md`"
4. Add grep patterns for navigation
