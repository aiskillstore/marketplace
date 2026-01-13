# Workflow: Consolidating Duplicate Documentation

**When to use**: Found duplicate or redundant documentation

## Prerequisites

- [ ] Identified duplicate documentation
- [ ] Have time to consolidate properly

## Steps

### 1. Identify All Duplicates

```bash
# Search for similar content
grep -r "topic keyword" docs/ --include="*.md"
```

List all files with duplicate content:
```
docs/old-guide.md
docs/another-guide.md
docs/screens/home/duplicate.md
```

### 2. Analyze Content

For each duplicate file:

1. Read through content
2. Identify unique information
3. Identify redundant information
4. Note which file should be the "primary" one

### 3. Create Consolidation Plan

```
PRIMARY: docs/screens/home/README.md (keep this)

MERGE FROM:
- docs/old-guide.md (sections 1-3)
- docs/another-guide.md (section 5 only)

DELETE:
- docs/old-guide.md
- docs/another-guide.md
```

### 4. Merge Content

**Steps:**

1. Open primary file
2. Copy unique content from each duplicate
3. Paste into appropriate section of primary file
4. Remove redundant information
5. Reorganize for clarity
6. Update headings for consistency

**Example:**

```markdown
# Primary file before
## Feature A
Brief description

# After merging
## Feature A

Brief description (from primary)

### Advanced Usage
Advanced info (merged from old-guide.md)

### Configuration
Config details (merged from another-guide.md)
```

### 5. Update Cross-References

Search for links to deleted files:

```bash
grep -r "old-guide.md" docs/ --include="*.md"
grep -r "another-guide.md" docs/ --include="*.md"
```

Update each link to point to primary file:

```markdown
# Before
See [guide](../old-guide.md)

# After
See [guide](./screens/home/README.md)
```

### 6. Delete Redundant Files

```bash
git rm docs/old-guide.md
git rm docs/another-guide.md
```

### 7. Validate

```bash
# Check consolidated file size
wc -l docs/screens/home/README.md

# If >500 lines, see split-large-file.md

# Check for broken links
grep -r "\[.*\](.*)" docs/ --include="*.md"
# Manually verify each link works
```

### 8. Commit

```bash
git add -A docs/
git commit -m "docs: consolidate duplicate documentation

- Merged 3 duplicate files into screens/home/README.md
- Removed 15 redundant lines
- Updated all cross-references
- Deleted old-guide.md and another-guide.md

Reduces total docs from 70 to 14 files.
"
```

## Checklist

- [ ] Identified all duplicates
- [ ] Analyzed content of each file
- [ ] Created consolidation plan
- [ ] Merged unique content into primary file
- [ ] Updated all cross-references
- [ ] Deleted redundant files
- [ ] Consolidated file under 500 lines
- [ ] No broken links
- [ ] Committed with detailed message

## Decision: Which File to Keep?

Keep the file that:
- ✅ Follows current structure (e.g., `screens/{name}/README.md`)
- ✅ Is most up-to-date
- ✅ Is most complete
- ✅ Has better organization

Delete files that:
-  Don't follow structure
-  Are outdated
-  Have partial information
-  Have poor organization

## Example

See commit: `dc96738` where 59 duplicate files were consolidated into 14.
