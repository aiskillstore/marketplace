---
name: skill-auditor
description: Audits and validates skill definitions for quality, completeness, and best practices. Use when reviewing existing skills for proper formatting, evaluating if skills should be split into sub-skills, or ensuring skills follow established conventions.
---

# Skill Auditor

This skill audits other skills for quality, completeness, and adherence to best practices. It validates skill structure, evaluates content quality, and recommends improvements or decomposition into sub-skills.

## When to Use

This skill should be triggered when:
- Reviewing existing skills for quality issues
- Checking if a skill follows proper formatting conventions
- Evaluating whether a skill should be divided into sub-skills
- Performing bulk audits across all project skills
- Validating skills before packaging or distribution

## Workflow

### Step 1: Discover Skills

List all skills in the `.claude/skills/` directory:

```bash
ls -la .claude/skills/
```

For each skill directory, verify it contains the required `SKILL.md` file.

### Step 2: Run Automated Validation

Execute the audit script to check structural requirements:

```bash
python .claude/skills/skill-auditor/scripts/audit_skills.py .claude/skills/
```

The script validates:
- YAML frontmatter presence and required fields
- Description quality (length, specificity)
- Word count limits (<5000 words recommended)
- Unfinished placeholder detection
- Empty directory warnings
- Script executability

### Step 3: Manual Quality Review

For each skill, evaluate against these criteria:

**Frontmatter Quality:**
- `name`: Uses hyphens, is descriptive
- `description`: 50+ characters, specific about triggers, no placeholders

**Content Structure:**
- Clear "When to Use" section with specific triggers
- Workflow with actionable steps
- Bundled resources properly documented

**Decomposition Analysis:**
- Evaluate if skill handles >3 distinct concerns
- Check if skill exceeds 5000 words
- Identify reusable components that could be shared

### Step 4: Generate Audit Report

Produce a structured report for each skill:

```
## Skill: [name]

### Validation Results
- Frontmatter: PASS/FAIL
- Structure: PASS/FAIL
- Word Count: X words (PASS/WARNING/FAIL)
- Unfinished Placeholders: X found

### Quality Score: X/10

### Recommendations
1. [Specific improvement]
2. [Another improvement]

### Decomposition Analysis
- Should split: YES/NO
- Reason: [explanation]
- Suggested sub-skills: [list if applicable]
```

### Step 5: Apply Fixes

For automated fixes, use the audit script with `--fix` flag:

```bash
python .claude/skills/skill-auditor/scripts/audit_skills.py .claude/skills/ --fix
```

For manual improvements, edit SKILL.md files directly following recommendations.

## Audit Criteria Reference

See `references/audit-criteria.md` for detailed scoring rubrics and decomposition guidelines.

## Bundled Resources

### Scripts

- `scripts/audit_skills.py` - Automated validation and reporting script

### References

- `references/audit-criteria.md` - Detailed audit criteria and scoring rubrics
