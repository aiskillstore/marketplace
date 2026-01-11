# Workflow: Updating Existing Documentation

**When to use**: Code has changed and documentation is now outdated

## Prerequisites

- [ ] Code has changed
- [ ] Know which docs are affected

## Steps

### 1. Identify Outdated Docs

```bash
# Find docs mentioning changed code
grep -r "OldFunctionName" docs/ --include="*.md"
grep -r "old-concept" docs/ --include="*.md"
```

### 2. Check Current Implementation

```bash
# Read current code to understand changes
cat source/path/to/changed-file.ts
```

### 3. Update Documentation

Open affected documentation files and update:

**Update code references:**
```markdown
# Before
Implementation: source/old/path.ts:50

# After
Implementation: source/new/path.ts:75
```

**Update examples:**
```typescript
// Before
const old = useOldHook();

// After
const state = useNewHook();
```

**Update diagrams** (if structure changed):
```
# Before
OldComponent
  └── OldChild

# After
NewComponent
  ├── NewChild1
  └── NewChild2
```

**Update feature descriptions** (if behavior changed)

### 4. Test Examples

Manually test or run all updated code examples to verify they work.

### 5. Validate Changes

```bash
# Check line count
wc -l docs/path/to/updated-file.md

# If >500 lines, see split-large-file.md
```

### 6. Commit

```bash
git add docs/path/to/updated-file.md
git commit -m "docs(topic): update for latest changes

- Update code references to match new structure
- Fix outdated examples
- Update diagrams
"
```

## Common Updates

### Code Reference Update

```markdown
# Find all references to old path
grep -r "source/old/path.ts" docs/ --include="*.md"

# Update each to new path
source/old/path.ts:50 → source/new/path.ts:75
```

### Example Code Update

```markdown
# Replace old API
\```typescript
const result = await oldApi.call();
\```

# With new API
\```typescript
const result = await newApi.execute();
\```
```

### Diagram Update

If component structure changed, update ASCII/Mermaid diagrams.

## Checklist

- [ ] All code references updated (file:line)
- [ ] All examples tested and working
- [ ] Diagrams updated if structure changed
- [ ] File still under 500 lines
- [ ] Links still work
- [ ] Committed with clear explanation

## Tips

- **Small changes**: Update inline
- **Large changes**: Consider creating new section
- **Breaking changes**: Add migration notes
- **Deprecations**: Mark as deprecated, add alternatives
