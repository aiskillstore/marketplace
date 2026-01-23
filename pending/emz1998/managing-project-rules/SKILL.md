---
name: managing-project-rules
description: Creates and updates modular project rules for Claude Code in .claude/rules/ directory. Use when creating, updating, or modifying rule files, organizing project guidelines, setting up code standards, or when user mentions "create rules", "update rules", "add rules", or "rule configuration".
---

**Goal**: Create and maintain focused, well-organized rule files in `.claude/rules/` following Claude Code best practices.

**IMPORTANT**: Rules should be concise, focused, and organized by topic. Follow the reference documentation structure.

## Workflow

### Phase 1: Assessment

- Read reference documentation at `references/project-rules-docs.md`
- Analyze existing rules in `.claude/rules/` to understand patterns
- Check if rule file exists (update vs create)
- Determine rule scope (general vs path-specific)
- Identify appropriate filename and organization

### Phase 2: Configuration

- For updates: read existing file and preserve structure
- Define rule topic and scope clearly
- Structure content with clear sections and lists
- Apply YAML frontmatter for path-specific rules
- Keep content focused on one topic

### Phase 3: Implementation

- Create new or update existing rule file in `.claude/rules/`
- Use subdirectories for better organization if needed
- Validate frontmatter syntax for path-specific rules
- Report completion with file location, scope, and changes made

## Rules

- One topic per rule file (code-style, testing, security)
- Use descriptive filenames (kebab-case)
- Path-specific frontmatter only when truly needed
- For updates: extend sections, remove duplicates, preserve existing content
- Consult user before major structural changes

## Acceptance Criteria

- Rule file created or updated in `.claude/rules/` directory
- Content is focused and well-organized
- YAML frontmatter valid for path-specific rules
- Filename is descriptive and follows kebab-case
- No conflicts with existing rules
- Report includes file location, scope, and summary of changes
