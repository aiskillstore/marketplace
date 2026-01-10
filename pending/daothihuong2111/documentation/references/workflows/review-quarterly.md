# Workflow: Quarterly Documentation Review

**When to use**: Every quarter or before major releases

## Prerequisites

- [ ] Set aside 2-4 hours
- [ ] Have latest code checked out
- [ ] Have access to all documentation

## Steps

### 1. List All Documentation

```bash
find docs -type f -name "*.md" | sort > docs-inventory.txt
cat docs-inventory.txt
```

### 2. For Each File

Work through each file systematically.

#### a. Verify Accuracy

1. Read documentation
2. Compare with current code
3. Check code references (file:line)
4. Test all examples

**Check code references:**
```bash
# Extract references from doc
grep -o "source/.*\.ts:[0-9]*" docs/screens/home/README.md

# Verify each file exists
cat source/path/to/file.ts | head -n 50
```

#### b. Check Links

```bash
# Extract all markdown links
grep -o "\[.*\](.*)" docs/file.md

# Test each link manually
```

#### c. Check File Size

```bash
wc -l docs/**/*.md

# Flag files >450 lines
wc -l docs/**/*.md | awk '$1 > 450 {print $0}'
```

#### d. Check for Duplicates

```bash
# Search for similar content
grep -r "keyword" docs/ --include="*.md"
```

### 3. Create Fix List

Document all issues found:

```
Issues Found:

OUTDATED:
- [ ] home/README.md - examples use old API
- [ ] config/technical.md - code refs wrong

BROKEN LINKS:
- [ ] guides/user-guide.md - link to deleted file

TOO LARGE:
- [ ] architecture/overview.md - 550 lines (split)

DUPLICATES:
- [ ] home/features.md + old-home.md - consolidate
```

### 4. Fix Issues

**For outdated docs:**
- See `update-existing.md`

**For broken links:**
- Update links to correct paths
- Or remove if target deleted

**For large files:**
- See `split-large-file.md`

**For duplicates:**
- See `consolidate-duplicates.md`

### 5. Document Review

```bash
git add -A docs/
git commit -m "docs: quarterly documentation review

- Updated 12 code references
- Fixed 3 broken links
- Split 2 large files
- Consolidated 4 duplicate files
- Tested all examples
- All docs now current
"
```

### 6. Update Review Log

Create/update `docs/.review-log.md`:

```markdown
# Documentation Review Log

## 2025-Q1 Review (2025-03-15)

**Reviewed by**: Claude
**Duration**: 3 hours
**Files reviewed**: 14

**Issues found**:
- 5 outdated code references
- 2 broken links
- 1 file too large
- 2 duplicate files

**Actions taken**:
- Updated all code references
- Fixed broken links
- Split large file
- Consolidated duplicates
- Tested all examples

**Status**: ✅ All documentation current

## 2024-Q4 Review (2024-12-15)

[Previous review...]
```

## Review Checklist

For each documentation file:

**Accuracy:**
- [ ] Content matches current code
- [ ] Code references are correct (file:line)
- [ ] Examples still work
- [ ] APIs haven't changed

**Quality:**
- [ ] Clear and understandable
- [ ] Has examples
- [ ] No typos or grammar issues
- [ ] Follows template structure

**Structure:**
- [ ] Under 500 lines
- [ ] Proper headings (H2, H3)
- [ ] Table of contents (if >200 lines)
- [ ] Cross-references present

**Links:**
- [ ] All internal links work
- [ ] All external links work
- [ ] No broken references

**Duplication:**
- [ ] No duplicate content exists elsewhere
- [ ] Information is DRY

## Review Schedule

**Quarterly** (every 3 months):
- Full review of all docs
- Update all code references
- Test all examples
- Fix all issues

**Before major release**:
- Full review
- Focus on user-facing docs
- Ensure examples work with new version

**After major refactoring**:
- Review affected documentation
- Update architecture docs
- Update code references

## Batch Operations

**Update multiple code references:**
```bash
# Find all references to old path
grep -r "source/old/path.ts" docs/ --include="*.md"

# Use sed to replace (careful!)
find docs -name "*.md" -exec sed -i 's/source\/old\/path\.ts/source\/new\/path.ts/g' {} \;

# Verify changes
git diff docs/
```

**Check all file sizes:**
```bash
wc -l docs/**/*.md | sort -nr | head -20
```

**Find all TODO comments:**
```bash
grep -r "TODO" docs/ --include="*.md"
```

## Metrics to Track

After each review, note:

```
Total files: 14
Total lines: 5,200
Average lines per file: 371
Files >400 lines: 2
Broken links: 0
Outdated references: 0
Duplicate content: 0
```

## Tips

- **Automate**: Create script for common checks
- **Prioritize**: Review user-facing docs first
- **Test**: Always test code examples
- **Update**: Update as you review, don't delay
- **Document**: Keep review log for next time
