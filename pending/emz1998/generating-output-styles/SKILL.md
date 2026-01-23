---
name: generating-output-styles
description: Creates custom output styles for Claude Code that modify system prompts and behavior. Use when the user asks to create output styles, customize Claude's response format, generate output-style files, or mentions output style configuration.
---

# Generating Output Styles

Creates custom output styles for Claude Code following Anthropic's standards and best practices.

## Context

Output styles modify Claude Code's system prompt to adapt its behavior beyond software engineering. They directly affect the main agent loop and control response tone, structure, and approach.

**Key capabilities:**
- Generate valid output style markdown files with frontmatter
- Apply proper naming and description standards
- Structure instructions following progressive disclosure
- Configure keep-coding-instructions appropriately
- Place files in correct locations (user vs project level)

## Workflow

### Phase 1: Gather Requirements

1. Determine the output style purpose and target behavior
2. Identify if coding instructions should be retained
3. Choose placement: `~/.claude/output-styles/` (user) or `.claude/output-styles/` (project)
4. Reference output style documentation at `.claude/skills/output-style/references/output-style-docs.md`

### Phase 2: Create Output Style File

1. **Craft frontmatter:**
   - `name`: Clear, descriptive name (shown in UI)
   - `description`: Brief explanation for users
   - `keep-coding-instructions`: true/false (default: false)

2. **Write system prompt modifications:**
   - Start with role definition
   - Define specific behaviors and approaches
   - Include formatting guidelines
   - Add any special instructions or constraints
   - Keep instructions concise and actionable

3. **Structure content:**
   - Use markdown headers for organization
   - Provide concrete examples when helpful
   - Avoid contradicting core Claude Code functionality
   - Focus on additive instructions, not restrictions

### Phase 3: Validate and Save

1. Verify YAML frontmatter syntax (opening/closing ---)
2. Ensure description is user-friendly and clear
3. Confirm keep-coding-instructions matches requirements
4. Save to appropriate location
5. Test activation with `/output-style` command

## Implementation Strategy

**File format:**
```markdown
---
name: Style Name
description: User-facing description of what this style does
keep-coding-instructions: false
---

# Custom Style Instructions

You are an interactive CLI tool that helps users with software engineering tasks. [Custom instructions...]

## Specific Behaviors

[Define how the assistant should behave in this style...]
```

**Naming guidelines:**
- Use title case for `name` field
- Keep names concise but descriptive
- Avoid technical jargon in names
- Examples: "Explanatory", "Learning", "Technical Writer"

**Description guidelines:**
- Write for end users, not developers
- Explain what the style does, not how
- Keep under 200 characters
- Focus on benefits and use cases

**keep-coding-instructions:**
- `false` (default): Removes software engineering instructions, clean slate
- `true`: Retains coding guidance, adds modifications on top

## Constraints

- Must include valid YAML frontmatter with all required fields
- System prompt modifications should complement, not contradict, core Claude Code
- Cannot override tool permissions or security restrictions
- File must use `.md` extension
- Must be placed in recognized output-styles directory
- Description shown in UI, so must be user-friendly

## Success Criteria

- Valid markdown file with proper YAML frontmatter
- Name and description follow guidelines
- keep-coding-instructions set appropriately
- System prompt instructions are clear and actionable
- File saved to correct location
- Can be activated via `/output-style` command
- Produces expected behavioral changes when active

## Examples

**Example 1: Technical Writer Style**

```markdown
---
name: Technical Writer
description: Produces detailed documentation with comprehensive explanations
keep-coding-instructions: true
---

# Technical Writer Instructions

You are an interactive CLI tool that helps users with software engineering tasks.

## Documentation Approach

- Provide comprehensive explanations for all code changes
- Include detailed comments in code
- Document edge cases and assumptions
- Create thorough README sections when relevant
- Explain trade-offs in implementation decisions

## Formatting

- Use clear section headers
- Include code examples with explanations
- Add inline comments for complex logic
- Structure responses with intro, body, conclusion
```

**Example 2: Minimalist Style**

```markdown
---
name: Minimalist
description: Provides concise responses with minimal explanation
keep-coding-instructions: true
---

# Minimalist Instructions

You are an interactive CLI tool that helps users with software engineering tasks.

## Communication Style

- Keep responses under 5 lines when possible
- Use code without explanatory prose
- Omit obvious explanations
- Respond with direct answers
- Only elaborate when explicitly asked
```

## Quick Reference

**Common output style patterns:**

1. **Educational styles**: Set `keep-coding-instructions: true`, add explanatory guidance
2. **Specialized domain styles**: Set `keep-coding-instructions: false`, define new role
3. **Formatting styles**: Set `keep-coding-instructions: true`, add response structure rules
4. **Tone modifiers**: Set `keep-coding-instructions: true`, adjust communication style

**Testing workflow:**
1. Create output style file
2. Run `/output-style` to verify it appears in menu
3. Activate the style
4. Test with representative tasks
5. Iterate based on behavior
6. Verify style persists in `.claude/settings.local.json`

## Related Documentation

- Output Style Docs: `.claude/skills/output-style/references/output-style-docs.md`
- Output Style Template: `.claude/templates/output-style.md` (if exists)
- Settings Documentation: Claude Code settings reference
