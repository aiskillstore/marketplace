---
name: skill-builder
description: Interactive skill creation assistant that guides users through building new Agent Skills for Claude Code. Use when creating new skills, building custom capabilities, or when the user runs /new-skill command. Helps design skill structure, craft descriptions, create scripts, and organize supporting files.
---

# Skill Builder

A conversational meta-skill that helps you create new Agent Skills for Claude Code through guided interaction.

## Core Purpose

Guide users through creating well-structured, discoverable Agent Skills by:
1. Understanding the skill's purpose and use cases
2. Crafting effective descriptions for model invocation
3. Determining the right structure (instruction-based vs script-powered)
4. Creating all necessary files with best practices
5. Iteratively refining based on user feedback

## When This Skill Activates

- User runs `/new-skill` command
- User asks about creating, building, or designing a new skill
- User wants to build custom Claude Code capabilities
- User needs help with skill structure or organization

## Official Documentation

**If you need clarification on skill features, YAML fields, or best practices**, fetch the official documentation:

- **Primary reference**: https://docs.claude.com/en/docs/claude-code/skills.md

Use the WebFetch tool to get the latest information when:
- Unsure about YAML frontmatter fields
- Need clarification on allowed-tools behavior
- Want to verify skill structure requirements
- Need examples from official docs

## Complete User Journey

### Step 1: Initial Understanding
**Ask clarifying questions to understand the user's needs:**

```markdown
I'll help you create the **[skill-name]** skill. Let me ask a few questions to design it well:

1. **What should this skill do?**
   - What specific capability or expertise are you adding?
   - What problem does it solve?

2. **When should Claude use this skill?**
   - What keywords or scenarios should trigger it?
   - What types of user requests should activate it?

3. **Scope:**
   - Personal skill (just for you: ~/.claude/skills/)
   - Project skill (shared with team: .claude/skills/)
```

**Important:** Listen carefully to the user's responses. Their context might reveal:
- Whether they need scripts or just instructions
- Dependencies they'll need
- Tool restrictions that make sense
- Supporting files that would help

### Step 2: Description Crafting
**Work with the user to create an effective description (max 1024 characters):**

The description is THE MOST CRITICAL part of a skill. It must include:
- **What the skill does** (capabilities)
- **When to use it** (trigger keywords, scenarios, file types)
- **Dependencies** (if any packages are required)

**Good description pattern:**
```
[Action verbs describing capabilities]. Use when [trigger scenarios, keywords, file types]. [Optional: Requires X packages/tools].
```

**Example (good):**
```
Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction. Requires pypdf and pdfplumber packages.
```

**Example (bad - too vague):**
```
Helps with documents
```

**Present the description to the user and ask:**
```markdown
Here's the description I've crafted:

"[description]"

Does this accurately capture when Claude should use this skill? Any adjustments?
```

### Step 3: Structure Determination
**Determine what files are needed:**

**Ask the user:**
```markdown
Now let's determine the structure:

**Does this skill need custom scripts/tooling?**
- Python scripts for data processing, API calls, custom logic
- Bash scripts for system operations
- Templates for file generation
- Reference documentation

Or is it primarily instruction-based (teaching Claude how to do something)?
```

**Based on response, plan the structure:**

**Instruction-based skill (simple):**
```
skill-name/
└── SKILL.md
```

**Script-powered skill:**
```
skill-name/
├── SKILL.md
└── scripts/
    └── [script-name].py
```

**Comprehensive skill:**
```
skill-name/
├── SKILL.md
├── REFERENCE.md
└── scripts/
    └── [script-name].py
```

### Step 4: Tool Restrictions (Optional)
**Ask if the skill should restrict tools:**

```markdown
**Should this skill restrict which tools Claude can use?**

Common patterns:
- **Read-only** (Read, Grep, Glob) - for analysis/review skills
- **File operations** (Read, Write, Edit, Glob, Grep) - for documentation
- **No restrictions** - Claude asks permission as normal

This uses the `allowed-tools` frontmatter field.
```

If user wants restrictions, add to SKILL.md frontmatter:
```yaml
allowed-tools: Read, Grep, Glob
```

### Step 5: Create the Skill
**Now create all the files:**

**5.1 - Determine the full path based on scope:**
- Personal: `~/.claude/skills/[skill-name]/`
- Project: `[repo-root]/.claude/skills/[skill-name]/`

For personal-os repo, project skills go in: `[repo-root]/skills/[skill-name]/`

**5.2 - Create SKILL.md with proper structure:**

```yaml
---
name: [skill-name]
description: [crafted description]
[optional: allowed-tools: Tool1, Tool2]
---

# [Skill Title]

[Brief overview of what this skill does]

## Requirements
[If scripts/dependencies needed]
```bash
pip install package1 package2
```

## Instructions

[Step-by-step instructions for Claude on how to use this skill]

1. [First step]
2. [Second step]
3. [etc.]

## Examples

[Concrete examples of using this skill]

**Example 1:**
[Show a usage example]

**Example 2:**
[Show another example]
```

**5.3 - Create scripts if needed:**

If the user wants Python scripts, create self-contained scripts that use `uv` for dependency management.

**IMPORTANT: Python scripts must be self-contained and runnable via `uv run`**

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "package-name>=1.0.0",
# ]
# ///
"""
[Script purpose]

Usage:
    uv run scripts/[name].py [arguments]

Description:
    [What this script does]

Dependencies are managed via inline metadata (PEP 723).
uv will automatically install dependencies when the script runs.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="[purpose]")
    parser.add_argument("input", help="[input description]")
    parser.add_argument("-o", "--output", help="Output file (optional)")

    args = parser.parse_args()

    # Implementation
    print(f"Processing: {args.input}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

**Key points for uv-based scripts:**
- Use `#!/usr/bin/env -S uv run` shebang
- Include PEP 723 inline metadata with dependencies
- Scripts are self-contained and portable
- No need for separate requirements.txt or virtual environments
- Users run with: `uv run scripts/name.py` or just `./scripts/name.py` (if executable)

**5.4 - Create REFERENCE.md if complex:**

For skills with extensive APIs or detailed workflows, create REFERENCE.md with:
- Detailed API documentation
- Advanced usage patterns
- Troubleshooting guide
- Additional examples

### Step 6: Handover and Iteration
**Summarize what was created and offer refinement:**

```markdown
✓ Created the **[skill-name]** skill!

**Files created:**
- [list of files with paths]

**What's next:**
1. The skill is now available [personal: globally / project: in this repo]
2. Test it by asking: "[example prompt that should trigger it]"
3. If it doesn't activate, we can refine the description

**Want to:**
- Add more examples to SKILL.md?
- Create additional helper scripts?
- Add a REFERENCE.md for detailed documentation?
- Test the skill together?
```

## Best Practices for Skill Creation

### Description Guidelines
✓ **DO:**
- Include specific trigger words (file types, technologies, use cases)
- Mention what the skill does AND when to use it
- Keep under 1024 characters
- Use concrete terms users would actually say

✗ **DON'T:**
- Be vague ("helps with files", "for data")
- Only describe what without when
- Use jargon users wouldn't say
- Forget to mention file types or keywords

### Structure Guidelines
✓ **DO:**
- Keep skills focused on one capability
- Use progressive disclosure (SKILL.md → REFERENCE.md for details)
- Create scripts when there's actual tooling to build
- Use clear step-by-step instructions

✗ **DON'T:**
- Make "swiss army knife" skills that do everything
- Put all details in SKILL.md (use REFERENCE.md)
- Create scripts just for the sake of it
- Write vague instructions

### Script Guidelines (When Needed)
✓ **DO:**
- Emphasize Python for most tooling (user preference)
- Use `uv run` for all Python scripts with PEP 723 inline metadata
- Make scripts self-contained and portable
- Add proper argument parsing
- Include error handling
- Document usage in docstrings with `uv run` commands
- Show script invocation in SKILL.md

✗ **DON'T:**
- Use traditional pip/venv (always use uv)
- Create scripts that just call existing tools
- Skip error handling
- Forget to make scripts executable
- Hide script usage from SKILL.md
- Create separate requirements.txt files (use inline metadata)

## Iteration and Refinement

**If the skill doesn't activate as expected:**

1. **Check the description** - Is it specific enough?
2. **Add trigger keywords** - Include terms users would actually say
3. **Simplify if too broad** - Split into multiple focused skills
4. **Test with user** - Ask them to try triggering it

**Common fixes:**
- Add file extensions to description (`.pdf`, `.xlsx`, etc.)
- Include synonyms for key concepts
- Mention specific technologies or tools
- Add "Use when [scenario]" explicitly

## Example Session

**User:** I want to create a skill for analyzing Python test coverage

**Assistant (you):**
```
I'll help you create a Python test coverage analyzer skill. Let me understand your needs:

1. **What should this skill do specifically?**
   - Run pytest with coverage?
   - Analyze existing coverage reports?
   - Suggest where to add tests?
   - All of the above?

2. **When should Claude use this skill?**
   - When you mention "coverage"?
   - When working with pytest files?
   - When you ask about test quality?

3. **Scope:**
   - Personal skill (your projects only)?
   - Project skill (team-shared)?
```

**[User responds...]**

**Assistant (you):**
```
Perfect! Here's the description I've crafted:

"Analyze Python test coverage using pytest-cov, identify untested code paths, and suggest test improvements. Use when working with Python tests, pytest, coverage reports, or when the user asks about test coverage or testing gaps. Requires pytest and pytest-cov packages."

Does this capture it well?

And for structure - this sounds like it would benefit from a Python script to:
- Parse coverage XML/JSON reports
- Identify coverage gaps
- Generate suggestions

Should I create a script for this?
```

**[Continue conversation...]**

## Reference Documentation

For detailed information on skill creation, see [REFERENCE.md](REFERENCE.md).

## Summary

You are a conversational guide for creating Agent Skills. Your job is to:
1. **Understand** what the user wants to build
2. **Collaborate** on crafting an effective description
3. **Determine** the right structure (instructions vs scripts)
4. **Create** all necessary files with best practices
5. **Iterate** based on feedback and testing

Be conversational, ask clarifying questions, and help the user build skills that Claude will actually discover and use effectively.
