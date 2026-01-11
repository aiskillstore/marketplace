---
name: skill-creator
description: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Claude's capabilities with specialized knowledge, workflows, or tool integrations.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## When to Use

- Creating a new skill from scratch
- Updating an existing skill
- Organizing skill structure (scripts, references, assets)
- Packaging skills for distribution
- Reviewing skill quality

## Workflow

### Step 1: Understand Requirements

Gather examples of how the skill will be used.

### Step 2: Plan Contents

Identify scripts, references, and assets needed.

### Step 3: Initialize Structure

Run init_skill.py to create directory structure.

### Step 4: Edit SKILL.md

Define purpose, triggers, and workflow.

### Step 5: Package

Run package_skill.py to validate and zip.

### Step 6: Iterate

Test and improve based on real usage.

---

## About Skills

Skills are modular, self-contained packages that extend Claude's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Claude from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. **Specialized workflows** - Multi-step procedures for specific domains
2. **Tool integrations** - Instructions for working with specific file formats or APIs
3. **Domain expertise** - Company-specific knowledge, schemas, business logic
4. **Bundled resources** - Scripts, references, and assets for complex and repetitive tasks

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation to load into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

### Progressive Disclosure Design

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Claude (Unlimited*)

*Unlimited because scripts can be executed without reading into context window.

## Skill Creation Process

### Step 1: Understand the Skill with Examples

To create an effective skill, clearly understand concrete examples of how the skill will be used.

Questions to ask:
- "What functionality should this skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

### Step 2: Plan the Reusable Skill Contents

Analyze each example by:
1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful

**When to use scripts/**: When the same code is being rewritten repeatedly or deterministic reliability is needed.

**When to use references/**: For documentation that Claude should reference while working (schemas, API docs, policies).

**When to use assets/**: For files used in output (templates, images, boilerplate code).

### Step 3: Initialize the Skill

Run the initialization script to create the skill structure:

```bash
python .claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-directory>
```

### Step 4: Edit the Skill

**Writing Style:** Use imperative/infinitive form (verb-first instructions), not second person.

Answer these questions in SKILL.md:
1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used?
3. How should Claude use the skill? (Reference all bundled resources)

### Step 5: Package the Skill

```bash
python .claude/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder>
```

### Step 6: Iterate

After testing, improve based on real usage:
1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Update SKILL.md or bundled resources
4. Test again

## Best Practices

- Keep SKILL.md under 5k words; move detailed content to references/
- Include grep patterns for large reference files (>10k words)
- Delete unused example directories created by init script
- Avoid information duplication between SKILL.md and references
- Use descriptive metadata - it determines when Claude uses the skill
