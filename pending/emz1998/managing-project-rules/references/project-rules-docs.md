# Modular rules with .claude/rules/

For larger projects, you can organize instructions into multiple files using the `.claude/rules/` directory. This allows teams to maintain focused, well-organized rule files instead of one large CLAUDE.md.

## Basic structure

Place markdown files in your project's `.claude/rules/` directory:

```
your-project/
├── .claude/
│   ├── CLAUDE.md          # Main project instructions
│   └── rules/
│       ├── code-style.md  # Code style guidelines
│       ├── testing.md     # Testing conventions
│       └── security.md    # Security requirements
```

All `.md` files in `.claude/rules/` are automatically loaded as project memory, with the same priority as `.claude/CLAUDE.md`.

## Path-specific rules

Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns.

```yaml
---
paths: src/api/**/*.ts
---
```

```markdown
# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

Rules without a `paths` field are loaded unconditionally and apply to all files.

## Glob patterns

The `paths` field supports standard glob patterns:

- `**/*.ts` - All TypeScript files in any directory
- `src/**/*` - All files under src/ directory
- `*.md` - Markdown files in the project root
- `src/components/*.tsx` - React components in a specific directory

You can use braces to match multiple patterns efficiently:

```yaml
---
paths: src/**/*.{ts,tsx}
---
```

This expands to match both `src/**/*.ts` and `src/**/*.tsx`.

You can also combine multiple patterns with commas:

```yaml
---
paths: {src,lib}/**/*.ts, tests/**/*.test.ts
---
```

## Subdirectories

Rules can be organized into subdirectories for better structure:

```
.claude/rules/
├── frontend/
│   ├── react.md
│   └── styles.md
├── backend/
│   ├── api.md
│   └── database.md
└── general.md
```

All `.md` files are discovered recursively.

## Symlinks

The `.claude/rules/` directory supports symlinks, allowing you to share common rules across multiple projects:

```bash
# Symlink a shared rules directory
ln -s ~/shared-claude-rules .claude/rules/shared

# Symlink individual rule files
ln -s ~/company-standards/security.md .claude/rules/security.md
```

Symlinks are resolved and their contents are loaded normally. Circular symlinks are detected and handled gracefully.

## User-level rules

You can create personal rules that apply to all your projects in `~/.claude/rules/`:

```
~/.claude/rules/
├── preferences.md   # Your personal coding preferences
└── workflows.md     # Your preferred workflows
```

User-level rules are loaded before project rules, giving project rules higher priority.

## Best practices for .claude/rules/

- **Keep rules focused** - Each file should cover one topic (e.g., testing.md, api-design.md)
- **Use descriptive filenames** - The filename should indicate what the rules cover
- **Use conditional rules sparingly** - Only add paths frontmatter when rules truly apply to specific file types
- **Organize with subdirectories** - Group related rules (e.g., frontend/, backend/)
