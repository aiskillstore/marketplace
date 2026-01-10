# Skills Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Claude Doesn't Use My Skill

**Symptoms:**
- Skill exists in `~/.claude/skills/` or `.claude/skills/`
- Claude completes task without mentioning or using the skill
- Skill seems invisible to Claude

**Diagnostic Steps:**

1. **Verify skill location:**
   ```bash
   # Personal skills
   ls ~/.claude/skills/my-skill-name/

   # Project skills
   ls .claude/skills/my-skill-name/
   ```
   **Expected:** Directory exists with SKILL.md inside

2. **Check YAML validity:**
   - Open SKILL.md
   - Ensure YAML frontmatter is properly formatted:
     ```yaml
     ---
     name: my-skill-name
     description: Clear description here
     ---
     ```
   - **Common errors:**
     - Missing opening/closing `---`
     - Tabs instead of spaces in YAML
     - Unescaped special characters in description

3. **Validate with quick_validate.py:**
   ```bash
   python scripts/quick_validate.py ~/.claude/skills/my-skill-name
   ```
   **Fix any errors reported**

**Solutions:**

**Solution A: Improve Description Triggers**

Claude loads skills based on description keywords. Add specific trigger terms:

❌ **Too vague:**
```yaml
description: Helps with code
```

✅ **Trigger-rich:**
```yaml
description: |
  Guides systematic code review process including security checks,
  performance analysis, style validation, and test coverage assessment.
  Use for: pull request review, code quality audit, refactoring review.
```

**Trigger term checklist:**
- [ ] Includes task-specific keywords (review, audit, analyze, etc.)
- [ ] Mentions domain (code, API, database, documentation, etc.)
- [ ] Lists use cases ("Use for: X, Y, Z")
- [ ] Under 1024 characters (YAML limit)

**Solution B: Verify Skill Name**

Skill name must match directory name exactly:

```
Directory: ~/.claude/skills/commit-helper/
YAML name: commit-helper  ✓

Directory: ~/.claude/skills/commit-helper/
YAML name: commit_helper  ✗ (underscore vs. hyphen)
```

**Fix:** Match directory name and YAML `name:` field exactly

**Solution C: Check Skill Loading**

After fixing YAML/description:
1. Restart Claude Code session (close and reopen)
2. Verify skill loads: `/skills` command (if available)
3. Try triggering with explicit keywords from description

---

### Issue 2: Skill Triggers But Guidance Is Vague

**Symptoms:**
- Claude mentions using the skill
- But doesn't follow workflow or provides generic advice
- User still confused about what to do

**Diagnostic Steps:**

1. **Read SKILL.md as if you've never seen it before**
   - Are instructions concrete or abstract?
   - Are there numbered steps or just paragraphs?
   - Are there examples showing expected output?

2. **Check for progressive disclosure violations**
   - Is SKILL.md over 500 lines?
   - Is detailed content inlined instead of referenced?
   - Are there deeply nested file references?

**Solutions:**

**Solution A: Add Concrete Examples**

Abstract guidance doesn't work. Show, don't tell:

❌ **Too abstract:**
```markdown
Make sure to follow best practices when writing tests.
```

✅ **Concrete with examples:**
```markdown
Write tests covering three scenarios:

1. **Happy path:**
   ```javascript
   test('createUser with valid data returns user object', () => {
     const user = createUser({ name: 'Alice', email: 'alice@example.com' });
     expect(user).toHaveProperty('id');
     expect(user.name).toBe('Alice');
   });
   ```

2. **Edge cases:**
   ```javascript
   test('createUser with empty name throws validation error', () => {
     expect(() => createUser({ name: '', email: 'alice@example.com' }))
       .toThrow('Name is required');
   });
   ```

3. **Error cases:**
   ```javascript
   test('createUser with invalid email throws error', () => {
     expect(() => createUser({ name: 'Alice', email: 'invalid' }))
       .toThrow('Invalid email format');
   });
   ```
```

**Solution B: Use Numbered Workflows**

Replace paragraphs with clear sequential steps:

❌ **Paragraph format:**
```markdown
You should analyze the codebase to understand what needs to be documented,
then create documentation following our standards, and make sure to validate
it before committing.
```

✅ **Numbered workflow:**
```markdown
### Step 1: Identify Undocumented Code
Run: `grep -r "TODO: document" src/`
List all functions/classes needing documentation.

### Step 2: Write Documentation
For each item, include:
- Purpose (what it does)
- Parameters (types and descriptions)
- Return value (type and meaning)
- Example usage

### Step 3: Validate Documentation
Run: `bash scripts/validate_docs.py`
Fix any errors reported.

### Step 4: Commit Changes
Create commit: "docs: Add documentation for [component]"
```

**Solution C: Front-Load Critical Info**

Most important information should be in SKILL.md, not buried in references:

✅ **In SKILL.md (always loaded):**
- Core workflow steps
- Critical examples
- Key decision criteria
- References to detailed docs

✅ **In references/ (loaded as needed):**
- Comprehensive examples
- Edge case handling
- Background/rationale
- Advanced techniques

---

### Issue 3: Invalid YAML Errors

**Symptoms:**
- Validation fails with "Invalid YAML"
- Skill doesn't load at all
- YAML parser errors

**Common YAML Errors and Fixes:**

**Error A: Tabs Instead of Spaces**

❌ **Wrong:**
```yaml
---
name: my-skill
description:→[TAB]This is wrong
---
```

✅ **Correct:**
```yaml
---
name: my-skill
description: This is correct
---
```

**Fix:** Replace all tabs with spaces in YAML frontmatter

---

**Error B: Unescaped Special Characters**

❌ **Wrong:**
```yaml
description: Use for: API testing, CLI tools, & automation
```
(Ampersand `&` is special character in YAML)

✅ **Correct:**
```yaml
description: "Use for: API testing, CLI tools, & automation"
```
or
```yaml
description: Use for API testing, CLI tools, and automation
```

**Fix:** Quote strings with special characters (`:`, `&`, `*`, `#`, `-`, `|`, `>`, `[`, `]`, `{`, `}`)

---

**Error C: Multiline Description Without Pipe**

❌ **Wrong:**
```yaml
description: This is a long description
that spans multiple lines
without proper formatting
```

✅ **Correct:**
```yaml
description: |
  This is a long description
  that spans multiple lines
  with proper formatting
```

**Fix:** Use `|` (literal) or `>` (folded) for multiline descriptions

---

**Error D: Missing Closing `---`**

❌ **Wrong:**
```yaml
---
name: my-skill
description: My skill description

# Rest of SKILL.md
```

✅ **Correct:**
```yaml
---
name: my-skill
description: My skill description
---

# Rest of SKILL.md
```

**Fix:** Ensure YAML block starts with `---` and ends with `---`

---

**Quick YAML Validation:**

Use online YAML validator or Python:
```bash
python -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"
```

If no error, YAML is valid. If error, fix reported issue.

---

### Issue 4: Skill in Wrong Location

**Symptoms:**
- Skill exists but isn't loaded
- Different Claude sessions see different skills
- Confusion about which skills are active

**Understanding Skill Locations:**

| Location | Scope | Use Case |
|----------|-------|----------|
| `~/.claude/skills/` | Personal (all Claude sessions) | General-purpose skills you use everywhere |
| `.claude/skills/` | Project-specific | Skills for this project only |

**Diagnostic:**

1. **Check current working directory:**
   ```bash
   pwd
   ```

2. **List personal skills:**
   ```bash
   ls ~/.claude/skills/
   ```

3. **List project skills:**
   ```bash
   ls .claude/skills/  # Run from project root
   ```

**Solutions:**

**For general-purpose skills:** Move to `~/.claude/skills/`
```bash
mv .claude/skills/my-skill ~/.claude/skills/
```

**For project-specific skills:** Keep in `.claude/skills/` at project root
```bash
# Ensure you're in project root
cd /path/to/project

# Create project skills directory
mkdir -p .claude/skills

# Move skill
mv ~/Downloads/my-skill .claude/skills/
```

---

### Issue 5: Validation Script Fails

**Symptoms:**
- `quick_validate.py` reports errors
- Skill structure issues
- Can't package skill

**Common Validation Errors:**

**Error A: Invalid Skill Name Format**

```
❌ Skill name must be hyphen-case (lowercase alphanumeric + hyphens only)
   Got: MySkill
```

**Fix:** Rename directory and update YAML:
```bash
mv ~/.claude/skills/MySkill ~/.claude/skills/my-skill
```

Update SKILL.md:
```yaml
name: my-skill  # Changed from MySkill
```

---

**Error B: Description Too Long**

```
❌ Description exceeds 1024 characters (got: 1456)
```

**Fix:** Shorten description, move details to SKILL.md body:

❌ **Too long (1456 chars):**
```yaml
description: |
  This skill does X and Y and Z and provides comprehensive guidance
  for A, B, C situations with examples for D, E, F cases and includes
  support for G, H, I workflows... [continues for 1456 characters]
```

✅ **Concise (256 chars):**
```yaml
description: |
  Guides X, Y, Z workflows with automated validation. Use for: A, B, C
  situations. Includes examples and troubleshooting for common cases.
```
(Move comprehensive details to SKILL.md body)

---

**Error C: Missing Required Fields**

```
❌ Missing required field: 'name'
❌ Missing required field: 'description'
```

**Fix:** Ensure YAML has both fields:
```yaml
---
name: my-skill          # Required
description: Clear description  # Required
---
```

---

**Error D: TODO Markers Still Present**

```
❌ Found TODO markers in SKILL.md - replace with actual content
```

**Fix:** Search for `TODO` and replace all placeholders:
```markdown
❌ description: TODO: Add description

✅ description: API documentation generator for REST, GraphQL, and gRPC
```

---

### Issue 6: Performance Issues

**Symptoms:**
- Skill makes Claude slow
- Long wait times when skill triggers
- Token budget warnings

**Diagnostic Steps:**

1. **Check SKILL.md size:**
   ```bash
   wc -l ~/.claude/skills/my-skill/SKILL.md
   ```
   **Target:** Under 200 lines ideal, 500 lines maximum

2. **Check reference file count:**
   ```bash
   ls -la ~/.claude/skills/my-skill/references/
   ```
   **Target:** 5-10 reference files maximum

3. **Review skill description length:**
   - Metadata loaded for ALL skills at startup
   - Long descriptions increase baseline token cost

**Solutions:**

**Solution A: Apply Progressive Disclosure**

Move detailed content from SKILL.md to references/:

**Before (SKILL.md is 800 lines):**
```markdown
SKILL.md:
- Workflow steps (50 lines)
- Detailed examples (200 lines)
- Comprehensive API reference (300 lines)
- Troubleshooting (150 lines)
- Best practices (100 lines)
```

**After (SKILL.md is 150 lines):**
```markdown
SKILL.md:
- Workflow steps (50 lines)
- Key examples (30 lines)
- References to detailed docs (20 lines)
- Quick troubleshooting (30 lines)
- Essential best practices (20 lines)

references/:
- api-reference.md (300 lines) - loaded only when needed
- examples-comprehensive.md (200 lines) - loaded only when needed
- troubleshooting-detailed.md (150 lines) - loaded only when needed
```

**Solution B: Shorten Description**

Description is loaded for ALL skills, so keep it concise:

❌ **Long (500 chars):**
```yaml
description: |
  Comprehensive API documentation generator supporting REST, GraphQL,
  gRPC, WebSocket, and Server-Sent Events protocols. Automatically
  detects API type, extracts endpoints, generates OpenAPI/Swagger specs,
  validates schemas, includes authentication examples, and provides
  interactive documentation with try-it-out functionality.
```

✅ **Concise (150 chars):**
```yaml
description: |
  API documentation generator for REST, GraphQL, gRPC. Auto-detects type,
  generates specs, validates schemas. Use for: API docs, OpenAPI, schema.
```

**Solution C: Consolidate References**

Too many small reference files → overhead

❌ **Too fragmented:**
```
references/
  api-rest.md
  api-graphql.md
  api-grpc.md
  api-websocket.md
  api-sse.md
```

✅ **Consolidated:**
```
references/
  api-types.md  (covers all types in one file)
```

---

### Issue 7: Skill Conflicts

**Symptoms:**
- Multiple skills trigger for same task
- Skills provide conflicting guidance
- Unclear which skill to use

**Diagnostic:**

1. **List all active skills:**
   ```bash
   ls ~/.claude/skills/
   ls .claude/skills/
   ```

2. **Check skill descriptions for overlap:**
   - Do multiple skills handle "testing"?
   - Do multiple skills handle "documentation"?
   - Are domains clearly separated?

**Solutions:**

**Solution A: Specialize Descriptions**

Make each skill's domain distinct:

❌ **Overlapping:**
```yaml
# Skill 1
description: Helps with testing code

# Skill 2
description: Helps with code quality including tests
```

✅ **Specialized:**
```yaml
# Skill 1: test-writer
description: |
  Generates unit tests for JavaScript/Python code with Jest/pytest.
  Use for: test creation, coverage improvement, test-driven development.

# Skill 2: code-reviewer
description: |
  Systematic code review including security, performance, style.
  Use for: pull request review, refactoring audit, quality assessment.
  Does NOT generate tests (use test-writer skill for that).
```

**Solution B: Remove Redundant Skills**

If two skills do nearly the same thing, consolidate:

```bash
# Instead of:
~/.claude/skills/api-docs-rest/
~/.claude/skills/api-docs-graphql/
~/.claude/skills/api-docs-grpc/

# Use:
~/.claude/skills/api-docs/  (handles all types)
```

**Solution C: Use Project Skills for Overrides**

Project-specific skill can override personal skill for specific projects:

```
# Personal (general approach)
~/.claude/skills/commit-helper/

# Project (follows this repo's conventions)
my-project/.claude/skills/commit-helper/  (overrides personal version)
```

---

### Issue 8: Scripts Don't Execute

**Symptoms:**
- `bash scripts/validate.py` fails
- "Permission denied" errors
- Scripts referenced in skill don't work

**Solutions:**

**Solution A: Make Scripts Executable**

```bash
chmod +x ~/.claude/skills/my-skill/scripts/*.py
```

**Solution B: Verify Python Shebang**

Ensure scripts start with:
```python
#!/usr/bin/env python3
```

Not:
```python
#!/usr/bin/python  # May not exist
```

**Solution C: Use Explicit Interpreter**

In SKILL.md, reference scripts with explicit interpreter:

❌ **May fail:**
```bash
bash scripts/validate.py
```

✅ **More reliable:**
```bash
python3 scripts/validate.py
```

**Solution D: Check Script Paths**

Scripts must be referenced relative to skill directory:

✅ **Correct:**
```markdown
Run: `python scripts/validate.py config.yaml`
```

❌ **Wrong:**
```markdown
Run: `python ~/.claude/skills/my-skill/scripts/validate.py config.yaml`
```
(Absolute path breaks when skill is moved or shared)

---

### Issue 9: Skill Created But Not Available

**Symptoms:**
- Skill files exist but Claude doesn't use skill
- Created skill but can't find it in Claude Code
- Skill works when tested but not in actual use

**Diagnostic:**

1. **Check where skill was created:**
   ```bash
   pwd  # Shows current directory
   ls SKILL.md  # If this works, skill is in current dir (may be wrong location)
   ```

2. **Check if skill is installed in Claude Code:**
   ```bash
   ls ~/.claude/skills/my-skill/SKILL.md     # Personal skills
   ls .claude/skills/my-skill/SKILL.md       # Project skills
   ```

**Solutions:**

**Solution A: Install Skill to Correct Location**

If skill exists in current directory but not in skills directory:

```bash
# Install to personal skills (available everywhere)
python scripts/package_skill.py my-skill --install personal

# Or install to project skills (team-shared)
python scripts/package_skill.py my-skill --install project
```

**Solution B: Restart Claude Code**

Skills load at startup. If you just installed:
- Close and reopen Claude Code
- Or restart current session
- Then test: "What skills are available?"

---

### Issue 10: Skill Works in Code But Not in Claude.ai

**Symptoms:**
- Skill works perfectly in Claude Code
- Same skill not available in Claude.ai
- Uploaded to .ai but Claude doesn't use it

**Cause:** Skills **do not sync across surfaces**

**Solution:**

```bash
# Create zip package
python scripts/package_skill.py my-skill --package

# Upload my-skill.zip to Claude.ai:
# 1. Open claude.ai
# 2. Settings > Features
# 3. Upload skill zip file
# 4. Verify skill appears in list
```

**Verification:**
- Start new conversation in Claude.ai
- Ask: "What skills are available?"
- Look for your skill in response

---

### Issue 11: Team Members Don't Have Skill

**Symptoms:**
- Skill works for you
- Team members report skill doesn't work
- "Skill not found" errors for teammates

**Diagnostic:**

1. **Determine skill type:**
   ```bash
   # Project skill?
   ls .claude/skills/my-skill/

   # Personal skill?
   ls ~/.claude/skills/my-skill/
   ```

2. **For project skills, check git:**
   ```bash
   git status | grep .claude/skills
   git log .claude/skills/my-skill/
   ```

**Solutions:**

**Solution A: For Project Skills (Claude Code)**

Ensure skill is committed and team has pulled:

```bash
# You: Commit skill
git add .claude/skills/my-skill/
git commit -m "Add my-skill for team"
git push

# Team: Pull latest
git pull
# Skill now available automatically
```

**Solution B: For Claude.ai/Desktop**

Each person must upload individually:
```bash
# You: Package skill
python scripts/package_skill.py my-skill --package

# Share my-skill.zip with team (email, Slack, drive)

# Each team member: Upload via Settings > Features
```

**Solution C: For API (Organization-Wide)**

Upload once, available to all:
```bash
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "file=@my-skill.zip"

# Skill automatically available to all org members
```

---

### Issue 12: Skill Update Not Reflecting

**Symptoms:**
- Updated skill but changes don't appear
- Claude still uses old version
- Edits not taking effect

**Solutions:**

**For Claude Code:**

**Option A: Restart Session**
```bash
# Close and reopen Claude Code
# Skills reload on startup
```

**Option B: Verify File Updated**
```bash
# Check modification time
ls -l ~/.claude/skills/my-skill/SKILL.md

# Or check content
cat ~/.claude/skills/my-skill/SKILL.md | head -20
```

**For Claude.ai/Desktop:**

Must re-upload:
```bash
# 1. Package updated skill
python scripts/package_skill.py my-skill --package

# 2. Delete old skill from Settings > Features

# 3. Upload new my-skill.zip

# 4. Verify in new conversation
```

**For Claude API:**

Upload new version (gets new skill_id):
```bash
# Delete old version
curl -X DELETE https://api.anthropic.com/v1/skills/skill_old123 \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Upload new version
curl -X POST https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -F "file=@my-skill.zip"

# Update API calls to use new skill_id
```

---

## Troubleshooting Workflow

When encountering issues:

1. **Identify symptom** (skill not loading, vague guidance, etc.)
2. **Run diagnostics** (validate YAML, check location, review content)
3. **Apply targeted fix** (improve description, add examples, restructure)
4. **Validate fix** (run quick_validate.py, restart Claude, test trigger)
5. **Iterate if needed** (use Two-Claude methodology for complex issues)

## Prevention Checklist

Avoid issues by following these practices:

**Before creating skill:**
- [ ] Clear use case defined (not too broad)
- [ ] Check for existing similar skills (avoid duplication)
- [ ] Domain specialization clear (no overlap with other skills)

**During development:**
- [ ] Run quick_validate.py regularly
- [ ] Test skill in realistic scenario (Two-Claude method)
- [ ] Keep SKILL.md under 200 lines (use references)
- [ ] Include concrete examples (not abstract guidance)

**Before shipping:**
- [ ] All TODO markers removed
- [ ] YAML valid (no tabs, special chars escaped)
- [ ] Description trigger-rich and under 1024 chars
- [ ] Scripts executable and tested
- [ ] Validation passes (comprehensive_validate.py)
- [ ] Documented in project or personal skills directory appropriately

---

## Getting Help

**When troubleshooting doesn't resolve the issue:**

1. **Review best practices:** Check [references/best-practices.md](../Resources/processed/04-best-practices-comprehensive.md)
2. **Examine example skills:** Study annotated examples in `references/examples/`
3. **Test incrementally:** Start with minimal viable skill, expand gradually
4. **Use Two-Claude methodology:** Systematic observation reveals issues
5. **Validate comprehensively:** Run `comprehensive_validate.py` for detailed analysis

**Still stuck?** Check skill-creator documentation in original skill-creator resources.

---

**Remember:** Most issues stem from vague descriptions, invalid YAML, or overly complex SKILL.md. Start simple, validate often, and expand based on real usage patterns.
