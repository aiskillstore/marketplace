# Skill Deployment & Distribution Guide

## Overview

After creating a skill with Skills Factory, you need to **deploy** it so Claude can use it. This guide covers deployment across all Claude surfaces and sharing strategies.

**Critical concept:** Skills **DO NOT sync across surfaces**. A skill installed in Claude Code is NOT automatically available in Claude.ai, Claude Desktop, or the Claude API. You must deploy separately to each surface where you want to use it.

## Deployment Surfaces

### Surface Comparison Table

| Surface | Deployment Method | Scope | Best For |
|---------|-------------------|-------|----------|
| **Claude Code** | Filesystem (`~/.claude/skills/` or `.claude/skills/`) | Personal or project-specific | Development, team workflows |
| **Claude.ai** | Upload zip via Settings > Features | Individual user only | Personal productivity |
| **Claude Desktop** | Upload zip via Settings (similar to .ai) | Individual user only | Desktop workflows |
| **Claude API** | Upload via `/v1/skills` endpoints | Organization-wide | Production systems, automation |

**Key limitation:** Skills uploaded to one surface are NOT available on others. Plan your deployment strategy accordingly.

---

## Claude Code Deployment

### Personal Skills

**Location:** `~/.claude/skills/`

**When to use:**
- Skills you use across ALL your projects
- Personal productivity tools
- Experimental skills you're developing
- Workflows specific to your individual needs

**Installation:**

**Option A: Using package_skill.py (Recommended)**
```bash
python scripts/package_skill.py my-skill --install personal
```

This validates the skill and copies it to `~/.claude/skills/my-skill/`.

**Option B: Manual installation**
```bash
# After creating skill
cp -r my-skill ~/.claude/skills/
```

**Verification:**
```bash
# Check skill exists
ls ~/.claude/skills/my-skill/SKILL.md

# Test in Claude Code
# Ask: "What skills are available?"
# Or trigger with relevant request
```

**Updating personal skills:**
```bash
# Edit in place
code ~/.claude/skills/my-skill/SKILL.md

# Or replace entire skill
rm -rf ~/.claude/skills/my-skill
python scripts/package_skill.py my-skill-v2 --install personal
```

---

### Project Skills

**Location:** `.claude/skills/` (in project root)

**When to use:**
- Team-shared workflows and conventions
- Project-specific expertise (APIs, architecture, standards)
- Skills that should be version-controlled with project
- Collaborative skill development

**Installation:**

**Option A: Using package_skill.py (Recommended)**
```bash
# From project root
python scripts/package_skill.py my-skill --install project
```

This validates the skill and copies it to `.claude/skills/my-skill/` in your current directory.

**Option B: Manual installation**
```bash
# Create project skills directory
mkdir -p .claude/skills

# Copy skill
cp -r my-skill .claude/skills/
```

**Committing to git:**
```bash
git add .claude/skills/my-skill/
git commit -m "Add my-skill for team workflows"
git push
```

**Team members get skills automatically:**
```bash
git pull
# Skill now available immediately in Claude Code
```

**Verification:**
```bash
# Check skill exists
ls .claude/skills/my-skill/SKILL.md

# Check it's tracked in git
git status
```

---

### Personal vs. Project Decision Matrix

| Criteria | Personal | Project |
|----------|----------|---------|
| **Used across multiple projects?** | ✓ Yes → Personal | ✗ No → Project |
| **Team needs it?** | ✗ No → Personal | ✓ Yes → Project |
| **Project-specific knowledge?** | ✗ No → Personal | ✓ Yes → Project |
| **Experimental/unstable?** | ✓ Yes → Personal | ✗ No → Project |
| **Company standards/conventions?** | Maybe → Personal | ✓ Yes → Project |

**Examples:**

**Personal skills:**
- `commit-helper` - You use this across all projects
- `test-writer` - Your personal testing workflow
- `code-review-personal` - Your individual review standards

**Project skills:**
- `.claude/skills/api-conventions/` - This project's API design standards
- `.claude/skills/deployment-workflow/` - How to deploy THIS application
- `.claude/skills/db-migrations/` - Database migration process for THIS project

---

### Priority Order: Personal vs. Project

When both personal and project skills exist with the same name:

**Project skills take precedence** over personal skills.

**Example:**
```
~/.claude/skills/commit-helper/  (Personal: generic commit messages)
.claude/skills/commit-helper/    (Project: includes project-specific conventions)

→ Claude uses .claude/skills/commit-helper/ when in this project
```

**Use case:** Override personal skill with project-specific version for specific projects.

---

## Claude.ai Deployment

### Upload Process

1. **Create zip package:**
   ```bash
   python scripts/package_skill.py my-skill --package
   # Creates: my-skill.zip
   ```

2. **Upload to Claude.ai:**
   - Open [claude.ai](https://claude.ai)
   - Go to Settings > Features
   - Find "Custom Skills" section
   - Click "Upload Skill"
   - Select `my-skill.zip`
   - Confirm upload

3. **Verification:**
   - Start new conversation
   - Ask: "What skills are available?"
   - Test trigger: Use keywords from skill description

### Limitations

**Individual user only:**
- Skills uploaded by you are ONLY available to you
- Other team members must upload separately
- No admin/centralized management
- Each user manages their own skills

**No sync with other surfaces:**
- Skills in Claude.ai are NOT available in Claude Code
- Must upload separately to each surface

**Requirements:**
- Pro, Max, Team, or Enterprise plan
- Code execution enabled

**Sharing with team:**

Since Claude.ai doesn't support org-wide distribution:

**Option A: Distribute zip file**
```bash
# You create skill
python scripts/package_skill.py team-skill --package

# Share team-skill.zip with team (email, Slack, shared drive)

# Each team member uploads individually via Settings > Features
```

**Option B: Use Claude API instead** (see below) for org-wide distribution

---

## Claude Desktop Deployment

**Note:** Claude Desktop uses similar upload mechanism to Claude.ai

### Upload Process

1. **Create zip package:**
   ```bash
   python scripts/package_skill.py my-skill --package
   ```

2. **Upload to Claude Desktop:**
   - Open Claude Desktop application
   - Go to Settings > Features (or similar - UI may vary)
   - Upload `my-skill.zip`

3. **Verification:**
   - Start new conversation
   - Test skill triggers correctly

### Limitations

Same limitations as Claude.ai:
- Individual user only
- No sync across surfaces
- Requires manual upload by each user

---

## Claude API Deployment

### Prerequisites

**Required beta headers:**
```
anthropic-beta: code-execution-2025-08-25,skills-2025-10-02,files-api-2025-04-14
```

### Upload via Skills API

**Step 1: Create skill package**
```bash
python scripts/package_skill.py my-skill --package
# Creates: my-skill.zip
```

**Step 2: Upload to API**
```bash
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: code-execution-2025-08-25,skills-2025-10-02,files-api-2025-04-14" \
  -F "file=@my-skill.zip"
```

**Response:**
```json
{
  "skill_id": "skill_abc123...",
  "name": "my-skill",
  "created_at": "2025-10-19T..."
}
```

**Step 3: Use skill in API calls**
```python
import anthropic

client = anthropic.Anthropic(api_key="...")

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=[{"type": "code_execution_2025-08-25"}],
    betas=["code-execution-2025-08-25", "skills-2025-10-02", "files-api-2025-04-14"],
    container={
        "skills": ["skill_abc123"]  # Your uploaded skill
    },
    messages=[{"role": "user", "content": "Use my-skill to..."}]
)
```

### Organization-Wide Availability

**Key benefit:** Skills uploaded via API are **organization-wide**
- All workspace members can use uploaded skills
- Centralized management
- Single upload, available to entire team

**Managing API skills:**

**List skills:**
```bash
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-beta: skills-2025-10-02"
```

**Delete skill:**
```bash
curl -X DELETE https://api.anthropic.com/v1/skills/skill_abc123 \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-beta: skills-2025-10-02"
```

**Update skill:**
- Delete old version
- Upload new version
- Update API calls to use new skill_id

---

## Team Distribution Strategies

### Strategy 1: Git (Project Skills) - Best for Development Teams

**Use when:**
- Team uses Claude Code
- Skill is project-specific
- Version control desired
- Continuous collaboration

**Process:**
1. Create skill in `.claude/skills/`
2. Commit to git
3. Team members pull
4. Skill available immediately

**Pros:**
- Automatic distribution
- Version controlled
- Easy updates (git pull)
- No manual steps for team

**Cons:**
- Only works for Claude Code
- Requires git workflow

---

### Strategy 2: Plugins - Best for Reusable Skills

**Use when:**
- Skill is reusable across projects
- Want marketplace distribution
- Building skill library

**Process:**
1. Create plugin with skills/ directory
2. Publish to plugin marketplace
3. Team installs plugin

**Pros:**
- Professional distribution
- Discoverability
- Versioning support
- Works across teams/organizations

**Cons:**
- More setup overhead
- Requires plugin development

See [Claude Code plugin documentation](https://docs.claude.com/en/docs/claude-code/plugins) for details.

---

### Strategy 3: Zip Files - Best for Ad-Hoc Sharing

**Use when:**
- One-time distribution
- Small team
- Mixed surfaces (some use .ai, some use Code)

**Process:**
1. Create zip: `python scripts/package_skill.py my-skill --package`
2. Share `my-skill.zip` (email, Slack, drive)
3. Team members install manually:
   - Claude.ai/Desktop: Upload via Settings
   - Claude Code: Unzip to `~/.claude/skills/`

**Pros:**
- Simple, no infrastructure needed
- Works across surfaces

**Cons:**
- Manual installation by each person
- No automatic updates
- Version tracking manual

---

### Strategy 4: API Upload - Best for Production Systems

**Use when:**
- Using Claude API
- Need org-wide availability
- Production/automated systems

**Process:**
1. Create zip
2. Upload via `/v1/skills` endpoint
3. Reference `skill_id` in API calls
4. Automatically available to all workspace members

**Pros:**
- Organization-wide distribution
- Single upload
- Centralized management

**Cons:**
- Only works for API usage
- Requires API integration

---

## Cross-Surface Deployment Workflow

**Scenario:** You want skill available everywhere (Code, .ai, Desktop, API)

**Step-by-step:**

**1. Develop in Claude Code** (fastest iteration)
```bash
# Create in personal skills for testing
python scripts/init_skill.py my-skill
# Choose: 1 (Personal)

# Iterate using Skills Factory
# Test in Claude Code

# Validate
python scripts/comprehensive_validate.py ~/.claude/skills/my-skill
```

**2. Package for distribution**
```bash
python scripts/package_skill.py my-skill --package
# Creates: my-skill.zip
```

**3. Deploy to each surface:**

**Claude Code (team):**
```bash
# If team needs it in specific project
python scripts/package_skill.py my-skill --install project
git add .claude/skills/my-skill/
git commit -m "Add my-skill"
git push
```

**Claude.ai:**
- Upload `my-skill.zip` via Settings > Features
- (Each team member does this individually)

**Claude Desktop:**
- Upload `my-skill.zip` via Settings
- (Each team member does this individually)

**Claude API:**
```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "file=@my-skill.zip"
# Save skill_id for API calls
```

**4. Maintain across surfaces:**

**When updating skill:**
- Update in Claude Code (personal or project)
- Re-package: `python scripts/package_skill.py my-skill --package`
- Re-upload to .ai/Desktop/API
- Update project skills via git if applicable

**Version tracking:**
- Include version in SKILL.md body (not YAML frontmatter)
- Document changes
- Communicate updates to team

---

## Surface-Specific Considerations

### Runtime Environment Constraints

**All surfaces run in code execution container with:**

❌ **No network access** - Skills cannot make external API calls
❌ **No runtime package installation** - Can't install new packages during execution
✓ **Pre-installed packages only** - [See available packages](https://docs.claude.com/en/docs/agents-and-tools/tool-use/code-execution-tool)

**Design implications:**
- Bundle all required data in skill (don't fetch externally)
- Only use pre-installed packages
- Scripts must work offline

### File Access

**Claude Code:**
- Full filesystem access to user's machine
- Can read/write project files

**Claude.ai / Desktop / API:**
- Sandboxed container
- Only access to uploaded files and skill contents

**Design implication:** Skills should work in both environments (don't assume access to arbitrary paths)

---

## Installation Verification

### Verify Claude Code Installation

**Personal skills:**
```bash
# Check file exists
ls ~/.claude/skills/my-skill/SKILL.md

# Check YAML valid
head -n 10 ~/.claude/skills/my-skill/SKILL.md

# Test in Claude Code
# Open Claude Code, ask: "What skills are available?"
```

**Project skills:**
```bash
# Check file exists
ls .claude/skills/my-skill/SKILL.md

# Check tracked in git
git status | grep .claude/skills

# Test in Claude Code
```

**Debugging:**
```bash
# Run Claude Code with debug mode
claude --debug

# Errors show skill loading issues
```

### Verify Claude.ai / Desktop Installation

1. Start new conversation
2. Ask: "What skills are available?" or "List all skills"
3. Look for your skill name in response

**If skill not listed:**
- Check upload succeeded (Settings > Features should show skill)
- Verify YAML frontmatter valid
- Check description is clear and specific

### Verify API Installation

**List uploaded skills:**
```bash
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-beta: skills-2025-10-02"
```

**Test in API call:**
```python
# Use skill in conversation
# Check Claude references the skill in its response
```

---

## Common Deployment Issues

### Issue 1: Skill Created But Not Available

**Symptom:** Skill files exist but Claude doesn't use skill

**Check installation location:**
```bash
# Where did you create it?
pwd  # Should be ~/.claude/skills or .claude/skills

# Or did you create in wrong location?
ls my-skill/SKILL.md  # If this shows file, it's in current dir (wrong)
```

**Fix:**
```bash
# Install to correct location
python scripts/package_skill.py my-skill --install personal
# or
python scripts/package_skill.py my-skill --install project
```

---

### Issue 2: Skill Works in Code But Not in Claude.ai

**Symptom:** Skill works in Claude Code but not available in Claude.ai

**Cause:** Skills don't sync across surfaces

**Fix:**
```bash
# Package skill
python scripts/package_skill.py my-skill --package

# Upload my-skill.zip to Claude.ai via Settings > Features
```

---

### Issue 3: Team Members Don't Have Skill

**Symptom:** Skill works for you but not for team

**Diagnosis:**

**If using project skills:**
```bash
# Did they pull latest?
git pull

# Is skill in .claude/skills/ ?
ls .claude/skills/my-skill/
```

**If using Claude.ai:**
- Each person must upload individually
- Skills are per-user, not org-wide

**If using Claude API:**
- Verify skill uploaded to organization workspace
- Check they're using correct `skill_id` in API calls

---

### Issue 4: Skill Update Not Reflecting

**Symptom:** Updated skill but changes not visible

**Claude Code:**
- Restart Claude Code session (changes load on startup)
- Or reload configuration

**Claude.ai / Desktop:**
- Delete old skill via Settings
- Upload new zip package

**Claude API:**
- Upload new version (new skill_id)
- Update API calls to use new skill_id

---

## Deployment Checklist

Before deploying skill:

- [ ] Skill validated with `comprehensive_validate.py` (no errors)
- [ ] Tested in Claude Code (triggers correctly, works as expected)
- [ ] Deployment surface(s) identified (Code / .ai / Desktop / API)
- [ ] Installation location chosen (personal / project / API)
- [ ] Team distribution strategy selected (git / plugin / zip / API)

For Claude Code:
- [ ] Installed to `~/.claude/skills/` (personal) or `.claude/skills/` (project)
- [ ] If project: Committed to git
- [ ] Verified skill loads: "What skills are available?"
- [ ] Tested trigger with realistic request

For Claude.ai / Desktop:
- [ ] Packaged with `package_skill.py --package`
- [ ] Uploaded via Settings > Features
- [ ] Verified skill appears in available skills
- [ ] Team members notified (if sharing)

For Claude API:
- [ ] Uploaded via `/v1/skills` endpoint
- [ ] `skill_id` saved for API calls
- [ ] Tested in API call
- [ ] Team/organization notified

---

## Next Steps

After successful deployment:

1. **Monitor usage** - Does skill trigger when expected?
2. **Gather feedback** - Are instructions clear? Missing edge cases?
3. **Iterate using Two-Claude methodology** - Improve based on real usage
4. **Document version** - Track changes over time
5. **Share learnings** - Help team understand when/how to use skill

For ongoing maintenance, see [references/TWO_CLAUDE_METHODOLOGY.md](TWO_CLAUDE_METHODOLOGY.md) for systematic iteration approach.

---

**Remember:** Skills don't sync across surfaces. Plan your deployment strategy based on where you need the skill to be available, and deploy separately to each surface.
