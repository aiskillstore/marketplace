---
name: skill-standardization
description: >
  Standardize and validate SKILL.md files against the Agent Skills specification
  (agentskills.io). Use when creating new skills, auditing existing skills for
  spec compliance, converting legacy skill formats to standard structure, or
  improving descriptions for reliable triggering. Triggers on: "validate skill",
  "create SKILL.md", "standardize skill format", "check skill spec", "skill
  frontmatter", "improve skill description", "add evals to skill".
allowed-tools: Bash Read Write Edit Glob Grep
compatibility: Designed for Claude Code and compatible agent clients with filesystem access
metadata:
  tags: skill-management, standardization, validation, agentskills-spec, automation
  version: "2.0"
---

# Skill Standardization

## When to use this skill

- Creating a new SKILL.md file from scratch
- Auditing existing skills for Agent Skills specification compliance
- Converting legacy skill formats (non-standard headings, frontmatter) to standard
- Improving skill descriptions to trigger more reliably on relevant prompts
- Adding evaluation test cases (`evals/evals.json`) to a skill
- Batch-validating all skills in a directory for consistency

## Agent Skills Specification Reference

### Frontmatter fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1–64 chars, lowercase alphanumeric + hyphens, no leading/trailing/consecutive hyphens, must match parent directory name |
| `description` | Yes | 1–1024 chars, must describe what skill does AND when to trigger |
| `allowed-tools` | No | Space-delimited list of pre-approved tools |
| `compatibility` | No | Max 500 chars, environment requirements |
| `license` | No | License name or reference to bundled file |
| `metadata` | No | Arbitrary key-value map for additional fields |

### Standard directory structure

```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Optional: executable scripts
├── references/       # Optional: detailed documentation
├── assets/           # Optional: templates, images, data
└── evals/            # Optional: evaluation test cases
    └── evals.json
```

### Progressive disclosure tiers

| Tier | What's loaded | When | Token budget |
|------|--------------|------|-------------|
| 1. Catalog | name + description | Session start | ~100 tokens per skill |
| 2. Instructions | Full SKILL.md body | On activation | < 5000 tokens (500 lines max) |
| 3. Resources | scripts/, references/ | When needed | Varies |

## Instructions

### Step 1: Validate an existing skill

Run the validation script on a skill directory:

```bash
bash scripts/validate_skill.sh path/to/skill-directory
```

Validate all skills in a directory:

```bash
bash scripts/validate_skill.sh --all .agent-skills/
```

The script checks:
- Required frontmatter fields (`name`, `description`)
- `name` format: lowercase, no consecutive hyphens, matches directory name
- `description` length: 1–1024 characters
- `allowed-tools` format: space-delimited (not YAML list)
- Recommended sections present
- File length: warns if over 500 lines

### Step 2: Write an effective description

The `description` field determines when a skill triggers. A weak description means the skill never activates; an over-broad one triggers at wrong times.

**Template:**
```yaml
description: >
  [What the skill does — list specific operations.]
  Use when [trigger conditions]. Even if the user doesn't explicitly
  mention [domain keyword] — also triggers on: [synonym list].
```

**Principles** (from agentskills.io):
1. **Imperative phrasing** — "Use this skill when..." not "This skill does..."
2. **User intent, not implementation** — describe what the user wants to achieve
3. **Be explicit about edge cases** — "even if they don't say X"
4. **List trigger keywords** — synonyms, related terms the user might type
5. **Stay under 1024 characters** — descriptions grow during editing; watch the limit

**Before / After:**
```yaml
# Before (weak — never triggers)
description: Helps with PDFs.

# After (optimized — reliable triggering)
description: >
  Extract text and tables from PDF files, fill forms, merge and split documents.
  Use when the user needs to work with PDF files, even if they don't explicitly
  say 'PDF' — triggers on: fill form, extract text from document, merge files,
  read scanned pages.
```

### Step 3: Create a new SKILL.md

Use this template as the starting point:

```markdown
---
name: skill-name
description: >
  [What it does and specific operations it handles.]
  Use when [trigger conditions]. Triggers on: [keyword list].
allowed-tools: Bash Read Write Edit Glob Grep
metadata:
  tags: tag1, tag2, tag3
  version: "1.0"
---

# Skill Title

## When to use this skill
- Scenario 1
- Scenario 2

## Instructions

### Step 1: [Action]
Content...

### Step 2: [Action]
Content...

## Examples

### Example 1: [Scenario]
Input: ...
Output: ...

## Best practices
1. Practice 1
2. Practice 2

## References
- [Link](url)
```

### Step 4: Convert legacy section headings

| Legacy heading | Standard heading |
|----------------|-----------------|
| `## Purpose` | `## When to use this skill` |
| `## When to Use` | `## When to use this skill` |
| `## Procedure` | `## Instructions` |
| `## Best Practices` | `## Best practices` |
| `## Reference` | `## References` |
| `## Output Format` | `## Output format` |

### Step 5: Add evaluation test cases

Create `evals/evals.json` with 2–5 realistic test prompts:

```json
{
  "skill_name": "your-skill-name",
  "evals": [
    {
      "id": 1,
      "prompt": "Realistic user message that should trigger this skill",
      "expected_output": "Description of what success looks like",
      "assertions": [
        "Specific verifiable claim (file exists, count is correct, format is valid)",
        "Another specific claim"
      ]
    }
  ]
}
```

Good assertions are **verifiable**: file exists, JSON is valid, chart has 3 bars. Avoid vague assertions like "output is good."

## Available scripts

- **`scripts/validate_skill.sh`** — Validates a SKILL.md against the Agent Skills spec

## Examples

### Example 1: Validate a skill directory

```bash
bash scripts/validate_skill.sh .agent-skills/my-skill/
```

Output:
```
Validating: .agent-skills/my-skill/SKILL.md
✓ Required field: name = 'my-skill'
✓ Required field: description present
✗ Description length: 1087 chars (max 1024)
✓ Name format: valid lowercase
✗ Name/directory mismatch: name='myskill' vs dir='my-skill'
✓ Recommended section: When to use this skill
✓ Recommended section: Instructions
⚠ Missing recommended section: Examples
✓ File length: 234 lines (OK)

Issues: 2 errors, 1 warning
```

### Example 2: Batch validate all skills

```bash
bash scripts/validate_skill.sh --all .agent-skills/
```

### Example 3: Fix common frontmatter issues

```yaml
# WRONG — tags inside metadata is non-standard for some validators
metadata:
  tags: [tag1, tag2]   # list syntax
  platforms: Claude    # non-spec field

# CORRECT — per Agent Skills spec
metadata:
  tags: tag1, tag2     # string value
allowed-tools: Bash Read Write  # space-delimited, not a YAML list
```

## Best practices

1. **Description quality first** — weak descriptions mean the skill never activates; improve it before anything else
2. **Keep SKILL.md under 500 lines** — move detailed reference docs to `references/`
3. **Pin script versions** — use `uvx ruff@0.8.0` not just `ruff` to ensure reproducibility
4. **No interactive prompts in scripts** — agents run in non-interactive shells; use `--flag` inputs, never TTY prompts
5. **Structured output from scripts** — prefer JSON/CSV over free-form text; send data to stdout, diagnostics to stderr
6. **Add evals before publishing** — at least 2–3 test cases covering core and edge cases

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [Optimizing Descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Evaluating Skills](https://agentskills.io/skill-creation/evaluating-skills)
- [Using Scripts](https://agentskills.io/skill-creation/using-scripts)
- [Adding Skills Support](https://agentskills.io/client-implementation/adding-skills-support)
