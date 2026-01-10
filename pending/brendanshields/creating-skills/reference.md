# Skill Creation Reference

Detailed best practices for creating Claude Code skills.

## Core Principles

### Conciseness is Essential

Skills share context with system prompts, conversation, and other skills. Challenge each piece:
- Does Claude really need this?
- Can it be moved to a reference file?
- Is this duplicating Claude's existing knowledge?

**Target**: SKILL.md under 500 lines, ideally under 300.

### Claude is Already Intelligent

Don't explain basic concepts Claude knows. Focus on:
- Your specific domain knowledge
- Unique workflows and patterns
- Project-specific conventions

### Match Specificity to Task Fragility

| Freedom Level | Use For | Format |
|---------------|---------|--------|
| High | Flexible tasks | Text instructions |
| Medium | Preferred patterns | Pseudocode |
| Low | Error-prone operations | Exact scripts |

## Progressive Disclosure Patterns

### Pattern 1: High-Level Guide with References

```markdown
# SKILL.md

## Quick Start
[Essential workflow]

## Advanced Features
See [FORMS.md](FORMS.md)

## API Reference
See [REFERENCE.md](REFERENCE.md)
```

### Pattern 2: Domain-Specific Organization

```
bigquery-skill/
├── SKILL.md (overview)
└── reference/
    ├── finance.md
    ├── sales.md
    └── product.md
```

### Pattern 3: Conditional Details

```markdown
## Basic Usage
[Core workflow here]

<details>
<summary>Advanced Options</summary>

[Detailed content only when needed]
</details>
```

## Workflow Design

### Use Checklists for Complex Tasks

```markdown
Progress:
- [ ] Step 1: Analyze input
- [ ] Step 2: Transform data
- [ ] Step 3: Validate output
- [ ] Step 4: Report results
```

### Implement Feedback Loops

For quality-critical operations:
1. Generate output
2. Run validation
3. If errors, fix and repeat
4. Confirm success

## Content Guidelines

### Avoid Time-Sensitive Information

| Avoid | Use Instead |
|-------|-------------|
| "As of 2024..." | "Current best practice..." |
| "Version 3.2 adds..." | Document features directly |
| "Deprecated in Q3..." | "Legacy pattern (see alternatives)" |

### Maintain Consistency

Choose one term and use it everywhere:
- "API endpoint" not sometimes "URL" or "route"
- "function" not sometimes "method" or "procedure"

### Provide Concrete Examples

```markdown
## Example

Input:
- Added user authentication feature

Output:
feat(auth): implement JWT-based authentication

Add login endpoint with token validation middleware.
Includes refresh token rotation and session management.
```

## Anti-Patterns in Detail

### Path Format Errors

```bash
# Wrong - Windows style
python scripts\helper.py

# Correct - Unix style (works everywhere)
python scripts/helper.py
```

### Decision Paralysis

```markdown
# Wrong - too many choices
You can use pypdf, pdfplumber, PyMuPDF, pdf2image,
camelot, tabula-py, or pdfminer...

# Correct - sensible default
Use pdfplumber for text extraction.
For scanned documents, use pdf2image with Tesseract.
```

### Missing Dependencies

```markdown
# Wrong - assumes installation
Run the analysis script.

# Correct - explicit requirements
Required: `pip install pandas numpy`
Then run: `python scripts/analyze.py`
```

### Vague Descriptions

```yaml
# Wrong - when would this activate?
description: Helps with data stuff

# Correct - clear triggers
description: |
  Analyzes CSV and Excel files for data quality issues.
  Use when user mentions data validation, CSV errors,
  or spreadsheet analysis.
```

## Scripts and Automation

### Error Handling

Scripts should solve problems, not punt to Claude:

```python
# Wrong - asks Claude to handle error
if not os.path.exists(path):
    raise FileNotFoundError(f"File not found: {path}")

# Better - handles gracefully
if not os.path.exists(path):
    with open(path, 'w') as f:
        f.write(default_content)
```

### Configuration Values

Justify all magic numbers:

```python
# Wrong - unexplained constant
MAX_RETRIES = 3

# Correct - documented reasoning
# 3 retries covers transient network issues
# without excessive delay on permanent failures
MAX_RETRIES = 3
```

### Verification Steps

For critical operations, use plan-validate-execute:

```bash
# 1. Generate plan
python scripts/plan_changes.py > changes.json

# 2. Validate plan
python scripts/validate_plan.py changes.json

# 3. Execute only after validation passes
python scripts/apply_changes.py changes.json
```

## Testing Skills

### Build Evaluations First

Create test cases before writing documentation:

```json
{
  "skills": ["your-skill-name"],
  "query": "User request that should trigger skill",
  "expected_behavior": [
    "Activates correctly",
    "Follows documented workflow",
    "Produces expected output"
  ]
}
```

### Test Across Models

Verify behavior with:
- Claude Opus (most capable)
- Claude Sonnet (balanced)
- Claude Haiku (may need more detail)

### Observe Navigation

Watch how Claude uses your skill:
- Does it read files in expected order?
- Which sections get accessed repeatedly?
- What content goes unused?

Iterate based on actual usage, not assumptions.

## Quality Checklist

### Core Quality
- [ ] Description specific with trigger terms
- [ ] SKILL.md under 500 lines
- [ ] Complex content in separate files
- [ ] No time-sensitive information
- [ ] Consistent terminology
- [ ] Concrete examples included
- [ ] One-level-deep references
- [ ] Clear workflow steps

### Code and Scripts
- [ ] Scripts handle errors gracefully
- [ ] Configuration values justified
- [ ] Required packages documented
- [ ] Unix-style paths only
- [ ] Validation for critical operations

### Testing
- [ ] At least 3 test scenarios
- [ ] Tested with target models
- [ ] Real usage validated
