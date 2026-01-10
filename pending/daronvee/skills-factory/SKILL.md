---
name: skills-factory
description: Meta-skill for creating production-ready Claude Code skills using evaluation-driven development, progressive disclosure patterns, comprehensive validation, and two-Claude iterative methodology
---

# Skills Factory

A comprehensive meta-skill for creating, validating, and iterating on production-ready Claude Code skills.

## About Skills

Skills extend Claude Code's capabilities with specialized knowledge and workflows. They use a **progressive disclosure system** that loads content in three levels:

1. **Metadata** (YAML) - Always loaded at startup (~100 tokens)
2. **Instructions** (SKILL.md body) - Loaded when triggered (<5,000 tokens)
3. **Resources** (supporting files) - Loaded as needed (effectively unlimited)

Skills are filesystem-based tools that live in `~/.claude/skills/` (personal) or `.claude/skills/` (project-specific).

## Skill Creation Process

### Step 1: Understanding the Domain

Before writing anything, deeply understand what you're building:

**Ask Critical Questions:**
- What specific problem does this skill solve?
- Who is the user and what's their context?
- What tasks should be automated vs. guided?
- What knowledge must Claude have vs. can reference?
- How will success be measured?

**Research Thoroughly:**
- Review similar existing skills
- Study relevant documentation
- Understand the workflow domain
- Identify edge cases and failure modes

**Define Success Criteria:**
- What specific outcomes indicate the skill works?
- What would success look like without the skill vs. with it?
- How will you evaluate effectiveness?

**See:** [references/EVALUATION_GUIDE.md](references/EVALUATION_GUIDE.md) for evaluation-driven development methodology.

### Step 2: Planning Your Architecture

Design your skill's structure before implementation:

**Choose Your Pattern:**
- **Simple skill**: SKILL.md only (~100-300 lines)
- **Standard skill**: SKILL.md + 1-3 reference files
- **Script-heavy skill**: SKILL.md + scripts/ + validation patterns
- **Reference-heavy skill**: SKILL.md + references/ with 5+ supporting docs

**Plan Progressive Disclosure:**
- What must be in SKILL.md? (triggers, core workflow, navigation)
- What goes to references/? (detailed guides, examples, context)
- What goes to scripts/? (validation, automation, processing)
- Keep SKILL.md under 200 lines when possible

**Design Workflows:**
- Linear process? Use simple sequential steps
- Quality gates? Use checklist workflow
- Conditional paths? Design decision tree
- Iteration needed? Plan feedback loop

**See:** [references/WORKFLOW_PATTERNS.md](references/WORKFLOW_PATTERNS.md) and [references/VALIDATION_PATTERNS.md](references/VALIDATION_PATTERNS.md)

### Step 3: Initialize Skill Structure

Create your skill's foundation:

```bash
cd ~/.claude/skills  # or .claude/skills for project-specific
python /path/to/init_skill.py my-skill-name
```

This creates:
```
my-skill-name/
├── SKILL.md          # Main skill file (YAML + instructions)
├── scripts/          # Executable scripts (optional)
├── references/       # Supporting documentation (optional)
└── assets/           # Images, templates, data files (optional)
```

**Post-Initialization:**
- Replace ALL `TODO:` placeholders in YAML frontmatter
- Draft description with key trigger terms (max 1024 chars)
- Ensure name is hyphen-case (lowercase + hyphens only)
- Plan your progressive disclosure structure

**See:** Bundled `scripts/init_skill.py`

### Step 4: Design & Implement

Build your skill following best practices:

**YAML Frontmatter Requirements:**
```yaml
---
name: skill-name          # Required: hyphen-case, max 64 chars
description: |            # Required: max 1024 chars, include trigger terms
  Clear, specific description of what this skill does.
  Include key terms that should trigger the skill.
  Focus on capabilities and use cases.
allowed-tools:            # Optional: Pre-approved tools list (Claude Code only)
  - Read
  - Grep
  - Glob
metadata:                 # Optional: Custom key-value pairs for tracking
  author: "TeamName"
  version: "1.0.0"
  category: "data-processing"
---
```

**Optional YAML Fields:**

**`allowed-tools`** (Claude Code only):
- **Purpose**: Restricts which tools Claude can use when this skill is active
- **Format**: YAML list of tool names
- **Use Cases**:
  - Read-only skills (prevent file modification): `[Read, Grep, Glob]`
  - Security-sensitive workflows (limit tool scope)
  - Data analysis only (no write/execute permissions)
- **Known Tools**: Read, Write, Edit, Grep, Glob, Bash, Task, SlashCommand, Skill
- **Example**:
  ```yaml
  ---
  name: safe-file-reader
  description: Read and analyze files without making changes
  allowed-tools: [Read, Grep, Glob]
  ---
  ```

**`metadata`** (All platforms):
- **Purpose**: Store custom key-value pairs for tracking and categorization
- **Format**: YAML dictionary (string keys → string values)
- **Use Cases**:
  - Version tracking: `{version: "2.1.0"}`
  - Team ownership: `{author: "TeamName", contact: "team@example.com"}`
  - Categorization: `{category: "content-creation", domain: "marketing"}`
  - Custom tracking IDs: `{internal-id: "SKILL-12345"}`
- **Best Practice**: Use unique key names to avoid conflicts with other tools
- **Example**:
  ```yaml
  ---
  name: pdf-processor
  description: Extract text and tables from PDF files
  metadata:
    author: "ContentTeam"
    version: "2.1.0"
    category: "document-processing"
    last-updated: "2025-11-22"
  ---
  ```

**SKILL.md Body Guidelines:**
- Start with clear "About" section explaining purpose
- Use concrete examples over abstract explanations
- Break complex workflows into numbered steps
- Reference detailed content (don't inline everything)
- Keep total SKILL.md under 500 lines (ideally under 200)

**Progressive Disclosure Rules:**
- Reference files ONE level deep: `[Guide](references/guide.md)` ✓
- No nested references: `references/category/subcategory/file.md` ✗
- Load scripts when needed: "Run validation: `bash scripts/validate.py`"
- Front-load critical info, defer details to references

**Workflow Integration:**
- Add validation checkpoints after key steps
- Design feedback loops for quality assurance
- Use scripts to automate validation (not punt to Claude)
- Provide clear error messages with actionable fixes

**See:** [references/WORKFLOW_PATTERNS.md](references/WORKFLOW_PATTERNS.md), [references/VALIDATION_PATTERNS.md](references/VALIDATION_PATTERNS.md)

### Step 5: Validate & Package

Ensure quality before distribution:

**Comprehensive Validation:**
```bash
python scripts/comprehensive_validate.py /path/to/my-skill-name
```

This checks:
- ✓ YAML structure and required fields
- ✓ Naming conventions (hyphen-case, no invalid chars)
- ✓ Description quality (length, clarity, trigger terms)
- ✓ Progressive disclosure (file references one-level deep)
- ✓ Best practices (no absolute paths, TODO markers, etc.)
- ✓ Content quality (examples present, clear structure)
- ✓ Workflow validation (if workflows present)

**Fix all errors and warnings before packaging.**

**Package for Distribution:**
```bash
python scripts/package_skill.py /path/to/my-skill-name
```

Creates: `my-skill-name.zip` ready for sharing or installation.

**See:** Bundled `scripts/comprehensive_validate.py` and `scripts/package_skill.py`

### Step 6: Iterate Using Two-Claude Methodology

Most skills require iteration to reach production quality. Use the **Two-Claude Method**:

**Claude A (Builder):**
- Has the skill loaded in their environment
- Performs realistic tasks the skill should help with
- Documents behavior, errors, confusion points
- Takes notes on what works and what doesn't

**Claude B (Tester/Observer):**
- Reviews Claude A's session logs and outputs
- Analyzes where the skill succeeded vs. failed
- Identifies improvement opportunities
- Proposes specific edits to skill files

**Iteration Cycle:**
1. Claude A uses the skill on realistic task
2. Observe and document behavior (what happened?)
3. Claude B analyzes session (what should change?)
4. Edit skill files based on findings
5. Re-validate with comprehensive_validate.py
6. Repeat until skill performs well consistently

**Key Observation Points:**
- Did Claude invoke the skill when appropriate?
- Did the skill provide sufficient guidance?
- Were workflows clear and easy to follow?
- Did validation catch errors effectively?
- What caused confusion or errors?

**See:** [references/TWO_CLAUDE_METHODOLOGY.md](references/TWO_CLAUDE_METHODOLOGY.md) for complete iteration framework.

### Step 7: Deploy & Distribute

After validation and iteration, deploy your skill so Claude can use it.

**Deploy to Claude Code:**

For personal use (across all projects):
```bash
python scripts/package_skill.py my-skill --install personal
```
Installs to `~/.claude/skills/my-skill/` - immediately available in all Claude Code sessions.

For team/project use (shared via git):
```bash
python scripts/package_skill.py my-skill --install project
git add .claude/skills/my-skill/
git commit -m "Add my-skill for team workflows"
git push
```
Team members get skill automatically on `git pull`.

**Deploy to Claude.ai / Claude Desktop:**
```bash
python scripts/package_skill.py my-skill --package
```
Upload generated `my-skill.zip` via Settings > Features.

**Deploy to Claude API:**
Upload via `/v1/skills` endpoint for organization-wide availability.

**Verification:**
- Claude Code: Ask "What skills are available?"
- Claude.ai/Desktop: Check Settings > Features shows skill
- API: List skills via API endpoint

**Important:** Skills **do not sync across surfaces**. Must deploy separately to each platform (Code, .ai, Desktop, API).

**See:** [references/DEPLOYMENT_GUIDE.md](references/DEPLOYMENT_GUIDE.md) for complete deployment workflows, surface-specific instructions, and team distribution strategies.

## Troubleshooting

**Common Issues:**
- "Claude doesn't use my skill" → Check description triggers, YAML validity
- "Skill loaded but ignored" → Add concrete examples, improve clarity
- "Validation failing" → Run comprehensive_validate.py for specific errors
- "Skill too complex" → Apply progressive disclosure, move content to references
- "Skill created but not available" → Check installation location, use --install flag
- "Skill works in Code but not .ai" → Skills don't sync, must upload separately
- "Team doesn't have skill" → Commit to git (project) or share zip (other surfaces)

**See:** [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for comprehensive troubleshooting guide.

## Reference Documentation

- **[EVALUATION_GUIDE.md](references/EVALUATION_GUIDE.md)** - Evaluation-driven development methodology
- **[TWO_CLAUDE_METHODOLOGY.md](references/TWO_CLAUDE_METHODOLOGY.md)** - Complete iterative testing framework
- **[WORKFLOW_PATTERNS.md](references/WORKFLOW_PATTERNS.md)** - Workflow design patterns and examples
- **[VALIDATION_PATTERNS.md](references/VALIDATION_PATTERNS.md)** - Feedback loops and validation strategies
- **[DEPLOYMENT_GUIDE.md](references/DEPLOYMENT_GUIDE.md)** - Complete deployment and distribution guide
- **[TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)** - Common issues and solutions

## Example Skills

See `references/examples/` for annotated example skills demonstrating best practices:
- **simple-skill/** - Minimal viable skill (commit-helper)
- **standard-skill/** - Moderate complexity with references (pdf-processor)
- **complex-skill/** - Full progressive disclosure (data-analysis)

Each example includes `ANNOTATIONS.md` explaining architectural decisions.

## Scripts

- **init_skill.py** - Generate new skill from template
- **comprehensive_validate.py** - Deep validation (structure, content, best practices)
- **package_skill.py** - Create distributable .zip file

## Version History

**v1.1.0** (2025-10-19)
- Added deployment layer with cross-surface support
- Enhanced package_skill.py with --install flag (personal/project)
- Enhanced init_skill.py with interactive location prompt
- Created DEPLOYMENT_GUIDE.md reference (~4,000 words)
- Added deployment troubleshooting (Issues 9-12)
- Complete end-to-end workflow: creation → deployment → distribution

**v1.0.0** (2025-10-19)
- Initial production release
- Evaluation-driven development framework
- Two-Claude iterative methodology
- Comprehensive validation script
- Workflow patterns (Sequential, Checklist, Conditional, Iterative)
- Validation patterns (Script-based, Reference-based, Plan-validate-execute, Multi-stage)
- Progressive disclosure implementation
- Troubleshooting guide (8 common issues)

---

**Created with Skills Factory** - Meta-skill for production-ready Claude Code skills
