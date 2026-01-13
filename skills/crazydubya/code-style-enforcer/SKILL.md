---
name: code-style-enforcer
description: Analyzes code for style consistency and applies project-specific formatting conventions beyond what linters catch. Use when reviewing code, ensuring style consistency, or when user requests code style improvements.
allowed-tools: Read, Grep, Glob, Edit
---

# Code Style Enforcer

This skill ensures code follows project-specific style conventions and patterns that automated linters may miss.

## When to Use This Skill

- User requests code style review or improvements
- Ensuring consistency across the codebase
- Onboarding new code or contributors
- Pre-commit code review
- User mentions "style", "consistency", "formatting", or "conventions"

## Instructions

### 1. Detect Project Style Guides

Look for style configuration files:

**JavaScript/TypeScript:**
- `.eslintrc.*` - ESLint configuration
- `.prettierrc.*` - Prettier configuration
- `tsconfig.json` - TypeScript compiler options
- `.editorconfig` - Editor configuration

**Python:**
- `.pylintrc`, `pylint.cfg` - Pylint
- `pyproject.toml` - Black, isort configuration
- `.flake8` - Flake8 configuration
- `setup.cfg` - Various tool configs

**Ruby:**
- `.rubocop.yml` - RuboCop configuration

**Go:**
- `go.fmt` enforced (standard)
- `.golangci.yml` - GolangCI-Lint

**Java:**
- `checkstyle.xml` - Checkstyle
- `.editorconfig`

**General:**
- `CONTRIBUTING.md` - Contribution guidelines
- `STYLE_GUIDE.md` - Project style guide
- `.editorconfig` - Cross-editor settings

Use Glob to find these files and Read to understand the project's style preferences.

### 2. Analyze Existing Code Patterns

Sample existing code to understand implicit conventions:

**File organization:**
- Directory structure patterns
- File naming conventions (camelCase, kebab-case, snake_case)
- Import/export organization

**Code structure:**
- Class/function ordering
- Public vs private method placement
- Constant/variable declaration location

**Formatting:**
- Indentation (spaces vs tabs, size)
- Line length limits
- Blank line usage
- Comment styles

**Naming:**
- Variable naming (camelCase, snake_case)
- Class naming (PascalCase, capitalization)
- Constant naming (UPPER_CASE, etc.)
- File naming patterns

Use Grep to find common patterns across similar files.

### 3. Beyond Linters: Check for Patterns

Focus on style issues that automated tools often miss:

**Naming Consistency:**
- Boolean variables: `is`, `has`, `should` prefixes
- Event handlers: `handle*`, `on*` patterns
- Getters/setters: `get*`, `set*` consistency
- Collection naming: plural vs singular
- Acronyms: consistent capitalization

**Code Organization:**
- Related functions grouped together
- Consistent file structure across modules
- Logical ordering (public before private, etc.)
- Separation of concerns

**Comments and Documentation:**
- JSDoc/docstring completeness
- Comment style consistency
- TODO/FIXME format
- Inline vs block comments

**Import/Export Patterns:**
- Import ordering (external, internal, relative)
- Named vs default exports
- Destructuring consistency
- Aliasing patterns

**Error Handling:**
- Consistent error message format
- Error class usage
- Try/catch patterns
- Logging format

**Type Usage (TypeScript/typed languages):**
- Explicit vs inferred types
- `interface` vs `type` preference
- Generic naming (T, K, V vs descriptive)
- Null/undefined handling

### 4. Identify Common Anti-Patterns

Flag code smells and anti-patterns:

**Magic Numbers:**
```javascript
// Bad
if (status === 200) { }

// Good
const HTTP_OK = 200;
if (status === HTTP_OK) { }
```

**Inconsistent null checks:**
```javascript
// Inconsistent
if (user === null) { }
if (!data) { }
if (typeof result === 'undefined') { }

// Consistent
if (user === null) { }
if (data === null) { }
if (result === undefined) { }
```

**Nested ternaries:**
```javascript
// Hard to read
const value = a ? b ? c : d : e;

// Better
let value;
if (a) {
  value = b ? c : d;
} else {
  value = e;
}
```

**Long parameter lists:**
```python
# Hard to maintain
def create_user(name, email, age, address, phone, ...):

# Better
def create_user(user_data: UserData):
```

### 5. Check Project-Specific Conventions

Look for patterns unique to this project:

- Custom naming for specific domains (e.g., "repo" vs "repository")
- Preferred libraries for common tasks
- Architectural patterns (MVC, service layer, etc.)
- Test file naming and structure
- Configuration patterns

Read `CONTRIBUTING.md`, `README.md`, or similar docs for explicit guidelines.

### 6. Generate Style Recommendations

For each issue, provide:

**Current code:**
```javascript
function getData(id) {
  const d = fetch('/api/users/' + id);
  return d;
}
```

**Issue:**
- Inconsistent naming (`getData` vs other functions use `fetch*`)
- Single-letter variable name (`d`)
- String concatenation instead of template literals

**Recommended:**
```javascript
function fetchUser(id) {
  const userData = fetch(`/api/users/${id}`);
  return userData;
}
```

### 7. Prioritize Issues

Order by impact:

**High Priority (Consistency):**
- Naming inconsistencies across similar functions
- Mixed indentation or formatting
- Inconsistent error handling

**Medium Priority (Readability):**
- Magic numbers/strings
- Unclear variable names
- Missing documentation

**Low Priority (Nice-to-have):**
- Comment formatting
- Import ordering
- Extra blank lines

### 8. Suggest Automated Tools

Recommend tools to enforce styles:

**JavaScript/TypeScript:**
```bash
npm install --save-dev prettier eslint
npx prettier --write .
npx eslint --fix .
```

**Python:**
```bash
pip install black isort flake8
black .
isort .
```

**Go:**
```bash
go fmt ./...
golangci-lint run
```

**Ruby:**
```bash
gem install rubocop
rubocop -a
```

### 9. Create or Update EditorConfig

Suggest `.editorconfig` if missing:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{js,ts,jsx,tsx}]
indent_style = space
indent_size = 2

[*.py]
indent_style = space
indent_size = 4

[*.go]
indent_style = tab
```

### 10. Style Review Checklist

When reviewing code for style:

- [ ] Naming follows project conventions
- [ ] Indentation and formatting consistent
- [ ] Imports organized properly
- [ ] Comments where needed, not excessive
- [ ] No magic numbers or strings
- [ ] Error handling consistent
- [ ] File organization matches project structure
- [ ] No obvious code smells
- [ ] Type annotations consistent (if applicable)
- [ ] Tests follow testing conventions

## Best Practices

1. **Consistency over perfection**: Follow existing patterns even if not ideal
2. **Document decisions**: Add style guides for ambiguous cases
3. **Automate where possible**: Use Prettier, Black, gofmt, etc.
4. **Be pragmatic**: Don't refactor working code just for style
5. **Team agreement**: Align on styles that matter
6. **Incremental improvement**: Fix styles in touched files, not all at once
7. **Readability first**: Style serves readability, not vice versa

## Common Style Conflicts

### Tabs vs Spaces
- Check `.editorconfig` or existing files
- When in doubt, use project majority

### Quote Style (Single vs Double)
- JavaScript: Single (`'`) common
- Python: Either, be consistent
- Go: Always double (`"`)
- Follow linter config if present

### Semicolons (JavaScript)
- Check existing code majority
- If mixed, suggest Prettier to enforce

### Line Length
- Common limits: 80, 100, 120 characters
- Check linter config or `.editorconfig`

### Import Ordering
- Usually: stdlib, external, internal, relative
- Use automated tools (isort, organize imports)

## Supporting Files

- `reference/style-guides.md`: Links to popular style guides
- `examples/before-after.md`: Code examples showing improvements
