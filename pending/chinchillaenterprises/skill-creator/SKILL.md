---
name: skill-creator
description: How to properly create Claude Code skills - teaches global vs project-local, naming conventions, and proper file structure
---

# Skill Creator - How to Properly Create Claude Code Skills

## Purpose
This skill teaches you how to create new Claude Code skills and where to put them. Use this EVERY TIME you need to create a new skill to avoid common mistakes.

## Critical Rule: Global vs Project-Local

### **DEFAULT: GLOBAL SKILLS** (`~/.claude/skills/`)
**99% of skills belong here.** This is your personal skills library that works across ALL projects.

Examples of global skills:
- `housekeeping` - Repository cleanup (works on any repo)
- `update-readme` - Documentation updates (works on any repo)
- `handbook` - Amplify Gen 2 knowledge (works across projects)
- `skills-sync` - Skill management (global utility)

**Location:** `~/.claude/skills/skill-name/SKILL.md`

### **RARE: PROJECT-LOCAL SKILLS** (`.claude/skills/`)
Only use this for skills that are **specific to ONE project and make no sense elsewhere**.

Example of a valid project-local skill:
- `documentation-updater` - Updates docs using THIS project's specific structure

**Location:** `.claude/skills/skill-name.md`

### **When in Doubt: USE GLOBAL!**

If you're asking "Should this be global or local?" → **It's global.**

---

## How to Create a New Skill (Step-by-Step)

### Step 1: Decide the Skill Name
Use lowercase-with-hyphens:
- ✅ `housekeeping`
- ✅ `update-readme`
- ✅ `code-review`
- ❌ `Housekeeping` (no capital letters)
- ❌ `update_readme` (use hyphens, not underscores)

### Step 2: Create the Directory
```bash
# For GLOBAL skills (default):
mkdir -p ~/.claude/skills/skill-name

# For PROJECT-LOCAL skills (rare):
mkdir -p .claude/skills/
```

### Step 3: Create the SKILL.md File
```bash
# For GLOBAL skills:
# Use the Write tool to create:
# /Users/feather/.claude/skills/skill-name/SKILL.md

# For PROJECT-LOCAL skills:
# Use the Write tool to create:
# .claude/skills/skill-name.md
```

### Step 4: Write the Skill Content

**🚨 CRITICAL: Every SKILL.md MUST start with YAML frontmatter!**

```markdown
---
name: skill-name
description: Brief description of what this skill does and when to use it (max 1024 chars)
---

# Skill Name - Brief Description

## Purpose
What does this skill do? When should it be used?

## Activation
How do users invoke this skill?

Example:
"Hey Claude, use your skill-name skill to..."

## Workflow Overview
Step-by-step process of what the skill does.

## Critical Rules
Important things to remember.

## Success Criteria
How to know the skill completed successfully.

## Example
Show a real example of the skill in action.
```

**YAML Frontmatter Requirements:**
- `name`: Must match directory name, lowercase-with-hyphens (max 64 chars)
- `description`: What the skill does AND when to use it (max 1024 chars)
  - Include key trigger words users would mention
  - Be specific about when Claude should activate it
  - Example: "Extract text from PDFs, fill forms. Use when working with PDF files or when user mentions documents, forms, or PDFs."

**Without YAML frontmatter, Claude cannot discover or use your skill!**

### Step 5: Commit to ChillSkills (GLOBAL ONLY)

```bash
cd ~/.claude/skills
git add skill-name/
git commit -m "feat: Add skill-name skill for [purpose]"
git pull --rebase origin main
git push origin main
```

**DO NOT commit project-local skills to ChillSkills!**

---

## Common Mistakes to Avoid

### ❌ Mistake #1: Creating in Project-Local by Default
```bash
# WRONG:
vim .claude/skills/new-skill.md
```

```bash
# RIGHT:
mkdir -p ~/.claude/skills/new-skill
vim ~/.claude/skills/new-skill/SKILL.md
```

### ❌ Mistake #2: Wrong File Name
```bash
# WRONG:
~/.claude/skills/housekeeping/housekeeping.md

# RIGHT:
~/.claude/skills/housekeeping/SKILL.md
```

### ❌ Mistake #3: Using Underscores
```bash
# WRONG:
~/.claude/skills/update_readme/

# RIGHT:
~/.claude/skills/update-readme/
```

### ❌ Mistake #4: Missing YAML Frontmatter
**CRITICAL ERROR** - Skill won't work without it!

```markdown
# WRONG - No frontmatter:
# My Skill

## Purpose
...

# RIGHT - Has frontmatter:
---
name: my-skill
description: Does X when you need Y
---

# My Skill

## Purpose
...
```

### ❌ Mistake #5: Forgetting to Push
After creating a global skill, ALWAYS push to ChillSkills:
```bash
cd ~/.claude/skills
git add new-skill/
git commit -m "feat: Add new-skill"
git push origin main
```

---

## Quick Reference: File Structure

### Global Skills Structure
```
~/.claude/skills/
├── .git/                           ← Git repo (ChillSkills)
├── skill-name/
│   └── SKILL.md                    ← The actual skill
├── another-skill/
│   └── SKILL.md
└── README.md
```

### Project-Local Skills Structure (Rare)
```
.claude/skills/
├── project-specific-skill.md       ← Note: .md not SKILL.md
└── another-local-skill.md
```

---

## Workflow: Creating a New Skill

### Example: Creating "code-review" Skill

```bash
# Step 1: Create directory
mkdir -p ~/.claude/skills/code-review

# Step 2: Use Write tool to create SKILL.md with YAML frontmatter
# Write to: /Users/feather/.claude/skills/code-review/SKILL.md
```

```markdown
---
name: code-review
description: Review code for best practices, security issues, and potential bugs. Use when reviewing code, checking pull requests, or analyzing code quality.
---

# Code Review Skill

## Purpose
Automated code review for quality, security, and best practices.

[Rest of skill content...]
```

```bash
# Step 3: Commit to ChillSkills
cd ~/.claude/skills
git add code-review/
git commit -m "feat: Add code-review skill for automated code reviews"
git pull --rebase origin main
git push origin main

# Done! ✅
```

---

## Testing Your New Skill

After creating the skill:

1. **Restart Claude Code** (or wait a moment for auto-reload)
2. **Invoke the skill:**
   ```
   User: "Use your skill-name skill to..."
   ```
3. **Verify it works** as expected

---

## Updating Existing Skills

### To Update a Global Skill:
```bash
# Edit the file
vim ~/.claude/skills/skill-name/SKILL.md

# Commit changes
cd ~/.claude/skills
git add skill-name/SKILL.md
git commit -m "fix: Update skill-name with improved workflow"
git push origin main
```

### To Update a Project-Local Skill:
```bash
# Edit the file
vim .claude/skills/skill-name.md

# Commit to project repo
git add .claude/skills/skill-name.md
git commit -m "chore: Update skill-name skill"
```

---

## Decision Tree: Global vs Project-Local

Ask yourself:

**Q1: Does this skill work on ANY repository?**
- Yes → GLOBAL
- No → Continue to Q2

**Q2: Is this skill specific to THIS project's unique structure/workflow?**
- Yes → PROJECT-LOCAL
- No → GLOBAL (if in doubt, always global!)

**Examples:**
- "Housekeeping" works on any repo → **GLOBAL**
- "Update README" works on any repo → **GLOBAL**
- "Deploy to AWS" works on any Amplify project → **GLOBAL**
- "Update BEONIQ-specific docs" only works here → **PROJECT-LOCAL**

---

## Success Criteria

When creating a skill, you should:

✅ **YAML frontmatter with `name` and `description` at the very top**
✅ Create in `~/.claude/skills/skill-name/SKILL.md` (global, 99% of time)
✅ Use lowercase-with-hyphens for naming
✅ File is named `SKILL.md` (not `skill-name.md`)
✅ Description includes what the skill does AND when to use it
✅ Commit and push to ChillSkills repo (for global skills)
✅ Skill has clear Purpose, Activation, and Workflow sections
✅ Test the skill works after creation

---

## Remember

**Default location:** `~/.claude/skills/skill-name/SKILL.md`

**When in doubt:** Use global, not project-local!

**Always push:** Commit global skills to ChillSkills repo!

---

## ChillSkills Repository

Global skills are version-controlled at:
`https://github.com/ChinchillaEnterprises/ChillSkills`

This ensures:
- Skills are shared across machines
- Version history is preserved
- Collaborative skill development
- Easy rollback if something breaks

---

## Quick Checklist for Creating a Skill

Before you create a skill, verify:

- [ ] **🚨 YAML frontmatter with `name` and `description` at the top**
- [ ] Skill name is lowercase-with-hyphens
- [ ] Creating in `~/.claude/skills/skill-name/` (not `.claude/skills/`)
- [ ] File is named `SKILL.md` (not `skill-name.md`)
- [ ] Description includes trigger words and when to use it
- [ ] Skill has Purpose, Activation, Workflow, and Success Criteria
- [ ] Committed and pushed to ChillSkills (if global)
- [ ] Tested that skill works after creation

---

**Every time you create a skill, follow this guide!**
