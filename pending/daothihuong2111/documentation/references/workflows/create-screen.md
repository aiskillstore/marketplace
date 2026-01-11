# Workflow: Creating New Screen Documentation

**When to use**: After fully implementing and testing a new screen

## Prerequisites

- [ ] Screen is fully implemented
- [ ] Screen is tested
- [ ] Screen is merged to main branch

## Steps

### 1. Check for Existing Documentation

```bash
# Search for screen name
grep -r "ScreenName" docs/ --include="*.md"

# List all screen docs
ls -la docs/screens/
```

**If docs exist**: STOP and update instead (see `update-existing.md`)

### 2. Create Directory

```bash
mkdir -p docs/screens/{screen-name}
```

### 3. Create README.md (Required)

Load template: `assets/templates/screen-readme.md`

Include:
- Overview
- Features (bullet points)
- Basic usage
- Component hierarchy
- Keyboard shortcuts

**Max lines**: 300

### 4. Create technical.md (Required)

Load template: `assets/templates/screen-technical.md`

Include:
- Architecture diagram
- State management
- Code examples
- Testing approach

**Max lines**: 500

### 5. Create features.md (Optional)

**Only if** screen has 5+ complex features

Load template: `assets/templates/screen-features.md`

Include:
- Each feature in detail
- Usage examples
- Error handling

**Max lines**: 400

### 6. Create flows.md (Optional)

**Only if** screen has complex multi-step workflows

Load template: `assets/templates/screen-flows.md`

Include:
- Step-by-step flows
- State transitions
- Diagrams

**Max lines**: 300

### 7. Validate

```bash
# Check line counts
wc -l docs/screens/{screen-name}/*.md

# All files should be under limits:
# - README.md < 300 lines
# - technical.md < 500 lines
# - features.md < 400 lines (if exists)
# - flows.md < 300 lines (if exists)
```

### 8. Update Main Index

Edit `docs/README.md` to add links to new screen.

### 9. Test Links

Open each file and verify all cross-references work.

### 10. Commit

```bash
git add docs/screens/{screen-name}/
git commit -m "docs(screen-name): add screen documentation

- Add overview and features
- Document technical implementation
- Include usage examples
"
```

## Checklist

Before finalizing:

- [ ] Searched for existing docs (no duplicates)
- [ ] Screen is complete and tested
- [ ] Created README.md
- [ ] Created technical.md
- [ ] Created optional files (if needed)
- [ ] All files under line limits
- [ ] Code references include file:line
- [ ] All examples tested
- [ ] Updated docs/README.md
- [ ] Tested all links
- [ ] Committed with descriptive message

## Example

See existing screen docs:
- `docs/screens/home/`
- `docs/screens/config/`
- `docs/screens/welcome/`
