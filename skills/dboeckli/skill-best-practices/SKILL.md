---
name: skill-best-practices
description: "Guide for creating, structuring, and improving Claude skills (SKILL.md). Use when building a new skill, reviewing an existing skill, writing SKILL.md frontmatter, defining trigger conditions, troubleshooting skill problems (not triggering, over-triggering, instructions not followed), or planning skill distribution. When working on any skill in this repository: also load the cc-best-practices skill, and always update both CLAUDE.md and README.md skill tables after any skill change. Do NOT use for general Claude Code configuration or hook setup."
---

---

# Skill Best Practices

Reference: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

## Instructions

### Step 1: Identify your use case category

Determine which type of skill you're building:

- **Document & Asset Creation** — consistent output (docs, designs, code)
- **Workflow Automation** — multi-step processes with consistent methodology
- **MCP Enhancement** — workflow guidance on top of MCP tool access

Define 2–3 concrete use cases before writing anything (see Planning section below).

### Step 2: Create the folder and SKILL.md

- Name the folder in kebab-case (e.g. `my-skill-name`)
- Create exactly `SKILL.md` (case-sensitive) inside it
- Write YAML frontmatter with `name` and `description` (see Technical requirements)

### Step 3: Write the description — this is the most critical part

The description controls when Claude loads your skill. It must include:

- **WHAT** the skill does
- **WHEN** to use it (specific trigger phrases)
- Optional: negative triggers ("Do NOT use for...")

See "Writing effective descriptions" for good/bad examples.

### Step 4: Write the body instructions

Follow the recommended template: `## Instructions` → numbered steps → `## Examples` → `## Troubleshooting`.
Be specific and actionable. Move detailed docs to `references/` and link to them.

### Step 5: Update CLAUDE.md and README.md

After creating or modifying any skill in this repository, always update the skill tables in both files:

- `CLAUDE.md` — skill table under "Included Skills" (Trigger column: one-line description of when it fires)
- `README.md` — skill table under "Enthaltene Skills" (Beschreibung column: German one-liner)

Both files must stay in sync. This step is mandatory and must not be skipped.

Also invoke the `cc-best-practices` skill when working on skills in this repository to ensure context and session management follow project standards.

### Step 6: Validate YAML and skills CLI compatibility

Run the validation script from the repository root before testing or committing:

```bash
bash .claude/skills/skill-best-practices/scripts/validate-skills.sh
```

Fix any `FAIL` lines before continuing. Common issues:

- `description` uses block scalar (`>` or `|`) → replace with a quoted single-line string
- Sub-keys under a parent mapping key not indented → add two-space indent

After pushing, also run the remote check to confirm `npx skills add --list` finds all skills:

```bash
bash .claude/skills/skill-best-practices/scripts/validate-skills.sh --remote
```

### Step 7: Test triggering and functional behavior

Run 10–20 test queries. Target: skill triggers on ~90% of relevant queries and never on unrelated topics.
Iterate on the description until triggering is reliable (see Testing approach).

### Step 7: Iterate based on signals

- Undertriggering → add more trigger phrases to description
- Overtriggering → add negative triggers, narrow scope
- Instructions ignored → move critical steps to top, use explicit language

---

## Examples

### Example 1: Building a new skill from scratch

User says: "Help me create a skill that plans sprints in Linear"

Actions:

1. Identify category: Workflow Automation + MCP Enhancement
2. Define use case: trigger = "plan sprint", "create sprint tasks"; steps = fetch Linear status → analyze velocity → create tasks
3. Create folder `linear-sprint-planner/SKILL.md`
4. Write description: "Manages Linear sprint planning workflows. Use when user says 'plan sprint', 'create sprint tasks', or 'set up iteration'."
5. Write step-by-step instructions with Linear MCP tool calls
6. Test with 10 trigger phrases; adjust description if skill doesn't auto-load

Result: Functional skill that auto-triggers on sprint planning requests and executes the full workflow without user re-explaining the steps each time.

### Example 2: Reviewing an existing skill

User says: "Review my SKILL.md and suggest improvements"

Actions:

1. Read the SKILL.md frontmatter — check name (kebab-case?), description (WHAT + WHEN? under 1024 chars? trigger phrases present?)
2. Check body — is it under 5,000 words? Are instructions specific and actionable? Is there a Troubleshooting section? Examples?
3. Simulate triggering — would the description cause Claude to load this skill for the right queries?
4. Report findings as: PASS / WARN / FAIL per criterion

Result: Prioritized list of improvements with specific fixes for each issue.

### Example 3: Troubleshooting a skill that doesn't trigger

User says: "My skill never loads automatically, I always have to invoke it manually"

Actions:

1. Read the description field — is it too generic? ("Helps with projects" won't work)
2. Check for missing trigger phrases — does it include words users would actually say?
3. Ask Claude: "When would you use the [skill name] skill?" — Claude quotes the description back; gaps become obvious
4. Rewrite description to add specific trigger phrases and retest

Result: Updated description with concrete triggers; skill auto-loads on relevant queries.

---

## What is a skill?

A skill is a folder containing:

- `SKILL.md` (required): Instructions in Markdown with YAML frontmatter
- `scripts/` (optional): Executable code (Python, Bash, etc.)
- `references/` (optional): Documentation loaded as needed
- `assets/` (optional): Templates, fonts, icons used in output

## Core design principles

**Progressive Disclosure** — three levels:

1. YAML frontmatter: always in system prompt; tells Claude _when_ to load the skill
2. SKILL.md body: loaded when relevant; full instructions
3. Linked files in `references/`: loaded on demand

**Composability** — skills work alongside others; don't assume exclusivity.

**Portability** — works identically across Claude.ai, Claude Code, and API.

---

## Planning: Start with use cases

Before writing, define 2–3 concrete use cases:

```
Use Case: <name>
Trigger: User says "<phrase>" or "<phrase>"
Steps:
  1. ...
  2. ...
Result: <expected outcome>
```

Ask yourself:

- What does the user want to accomplish?
- What multi-step workflow is required?
- Which tools are needed (built-in or MCP)?
- What domain knowledge should be embedded?

### Three skill categories

| Category                      | When to use                                           | Key techniques                                      |
| ----------------------------- | ----------------------------------------------------- | --------------------------------------------------- |
| **Document & Asset Creation** | Consistent, high-quality output (docs, designs, code) | Style guides, templates, quality checklists         |
| **Workflow Automation**       | Multi-step processes with consistent methodology      | Step-by-step with validation gates, iterative loops |
| **MCP Enhancement**           | Workflow guidance on top of MCP tool access           | Sequential MCP calls, embedded domain expertise     |

---

## Technical requirements

### File & folder naming

- Folder: **kebab-case** only (`notion-project-setup`) — no spaces, underscores, or capitals
- File: exactly **`SKILL.md`** (case-sensitive) — no variations
- No `README.md` inside the skill folder (put docs in `SKILL.md` or `references/`)

### YAML frontmatter

Minimal required format:

```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

**`name`** (required):

- kebab-case, no spaces or capitals
- Must match folder name

**`description`** (required):

- MUST include BOTH: what the skill does AND when to use it (trigger conditions)
- Under 1024 characters
- No XML tags (`<` or `>`)
- Include specific trigger phrases users would actually say
- Mention file types if relevant

**Optional fields:**

```yaml
license: MIT
compatibility: "Requires Python 3.10+"
metadata:
  author: Your Name
  version: 1.0.0
  mcp-server: server-name
```

**Security restrictions — forbidden in frontmatter:**

- XML angle brackets (`< >`)
- Names containing "claude" or "anthropic" (reserved)

---

## Writing effective descriptions

Structure: `[What it does] + [When to use it] + [Key capabilities]`

**Good examples:**

```yaml
# Specific and actionable
description: Analyzes Figma design files and generates developer handoff docs.
  Use when user uploads .fig files, asks for "design specs", "component
  documentation", or "design-to-code handoff".

# Includes trigger phrases
description: Manages Linear project workflows including sprint planning and
  task creation. Use when user mentions "sprint", "Linear tasks", or asks
  to "create tickets".
```

**Bad examples:**

```yaml
# Too vague
description: Helps with projects.

# Missing triggers
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.
```

---

## Writing instructions (SKILL.md body)

Recommended structure:

```markdown
# Your Skill Name

## Instructions

### Step 1: [First Major Step]

Clear explanation of what happens.

### Step 2: ...

## Examples

### Example 1: [Common scenario]

User says: "..."
Actions:

1. ...
   Result: ...

## Troubleshooting

### Error: [Common error message]

**Cause:** Why it happens
**Solution:** How to fix
```

### Best practices for instructions

**Be specific and actionable:**

```
# Good
Run `python scripts/validate.py --input {filename}` to check data format.
If validation fails, common issues:
- Missing required fields (add to CSV)
- Invalid date formats (use YYYY-MM-DD)

# Bad
Validate the data before proceeding.
```

**Include error handling** — document common errors with cause and solution.

**Reference bundled resources clearly:**

```
Before writing queries, consult `references/api-patterns.md` for:
- Rate limiting guidance
- Pagination patterns
```

**Use progressive disclosure** — keep SKILL.md focused on core instructions; move detailed docs to `references/` and link to them. Keep SKILL.md under 5,000 words.

**For critical validations**, prefer a bundled script over language instructions — code is deterministic, language interpretation isn't.

---

## Testing approach

### 1. Triggering tests

Run 10–20 queries. Skill should trigger on ~90% of relevant queries and NOT trigger on unrelated topics.

```
Should trigger:
- "Help me set up a new ProjectHub workspace"
- "I need to create a project in ProjectHub"

Should NOT trigger:
- "What's the weather?"
- "Help me write Python code"
```

**Debugging:** Ask Claude "When would you use the [skill name] skill?" — it will quote the description back.

### 2. Functional tests

- Valid outputs generated
- API calls succeed
- Error handling works
- Edge cases covered

### 3. Performance comparison

Compare token count, tool calls, and back-and-forth messages with vs. without the skill.

**Pro tip:** Iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill.

---

## Troubleshooting

### Skill won't upload

| Error                     | Cause                      | Fix                                |
| ------------------------- | -------------------------- | ---------------------------------- |
| "Could not find SKILL.md" | Wrong filename             | Rename exactly to `SKILL.md`       |
| "Invalid frontmatter"     | YAML formatting            | Add `---` delimiters, close quotes |
| "Invalid skill name"      | Spaces or capitals in name | Use kebab-case                     |

### Skill doesn't trigger (undertriggering)

- Description too generic
- Missing trigger phrases users actually say
- Missing relevant file type mentions

**Fix:** Add more specific keywords and phrases to the description.

### Skill triggers too often (overtriggering)

Add negative triggers and narrow the scope:

```yaml
description: Advanced data analysis for CSV files. Use for statistical modeling,
  regression, clustering. Do NOT use for simple data exploration.
```

### Instructions not followed

1. **Too verbose** — keep concise, use bullet points, move details to `references/`
2. **Instructions buried** — put critical instructions at top, use `## Critical` headers
3. **Ambiguous language** — be explicit: "CRITICAL: Before calling X, verify: ..."
4. **Model laziness** — add to user prompts (more effective than SKILL.md): "Take your time, quality over speed, do not skip validation steps"

### Large context / slow responses

- Move detailed docs to `references/`
- Keep SKILL.md under 5,000 words
- Reduce simultaneous enabled skills (evaluate if you have more than 20–50)

---

## Workflow patterns

Five patterns cover most skill types: Sequential orchestration, Multi-MCP coordination, Iterative refinement, Context-aware tool selection, and Domain-specific intelligence.

For detailed examples and implementation templates for each pattern, consult `references/patterns.md`.

---

## Quick checklist

**Before you start:**

- [ ] Identified 2–3 concrete use cases
- [ ] Tools identified (built-in or MCP)
- [ ] Planned folder structure

**During development:**

- [ ] Folder named in kebab-case
- [ ] `SKILL.md` exists (exact spelling, case-sensitive)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name`: kebab-case, no spaces, no capitals
- [ ] `description` includes WHAT and WHEN
- [ ] No XML tags (`< >`) anywhere
- [ ] Instructions clear and actionable
- [ ] Error handling included
- [ ] Examples provided
- [ ] References clearly linked

**Repository sync (mandatory for this repo):**

- [ ] `CLAUDE.md` skill table updated
- [ ] `README.md` skill table updated
- [ ] `cc-best-practices` skill was loaded during this session
- [ ] `validate-skills.sh` run — no `FAIL` lines
- [ ] After push: `validate-skills.sh --remote` run — all skills found by `npx skills`

**Before upload:**

- [ ] Triggers on obvious tasks
- [ ] Triggers on paraphrased requests
- [ ] Does NOT trigger on unrelated topics
- [ ] Functional tests pass

**After upload:**

- [ ] Test in real conversations
- [ ] Monitor for under/over-triggering
- [ ] Iterate on description and instructions
