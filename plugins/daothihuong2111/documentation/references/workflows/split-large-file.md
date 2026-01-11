# Workflow: Splitting Large Documentation File

**When to use**: File exceeds 500 lines or approaching limit (450+)

## Prerequisites

- [ ] File is >450 lines
- [ ] Have identified logical split points

## Steps

### 1. Count Lines

```bash
wc -l docs/path/to/large-file.md
# Output: 650 large-file.md
```

### 2. Analyze Content

Read through file and identify logical sections:

```
Section 1: Overview (100 lines) ← Keep in README
Section 2: Features (300 lines) ← Split to features.md
Section 3: Technical (250 lines) ← Split to technical.md
Total: 650 lines
```

### 3. Plan Split

Decide what goes where:

```
KEEP in README.md:
- Overview
- Basic features (top 5)
- Quick start

MOVE to features.md:
- Detailed features (all)
- Advanced usage
- Configuration options

MOVE to technical.md:
- Implementation details
- Code examples
- Testing approach
```

### 4. Create New Files

```bash
# For screen docs
touch docs/screens/{screen-name}/features.md
touch docs/screens/{screen-name}/technical.md

# For other docs
touch docs/guides/{topic}-advanced.md
```

### 5. Move Content

**For each new file:**

1. Load appropriate template from `assets/templates/`
2. Cut sections from large file
3. Paste into new file
4. Follow template structure
5. Update headings

**Example:**

```markdown
# Cut from large README.md
## Feature 5: Advanced Usage
[300 lines of content]

# Paste into features.md
# {Screen Name} - Features

## Feature 5: Advanced Usage
[same 300 lines, reformatted]
```

### 6. Add Cross-References

**In README.md:**
```markdown
For detailed features, see [features.md](./features.md).
For technical details, see [technical.md](./technical.md).
```

**In features.md:**
```markdown
See [README.md](./README.md) for overview.
See [technical.md](./technical.md) for implementation.
```

**In technical.md:**
```markdown
See [README.md](./README.md) for overview.
See [features.md](./features.md) for feature details.
```

### 7. Validate

```bash
# Check all file sizes
wc -l docs/screens/{screen-name}/*.md

# All should be under limits:
# - README.md < 300
# - features.md < 400
# - technical.md < 500
# - flows.md < 300

# Test all links
grep -r "\[.*\](.*)" docs/screens/{screen-name}/
```

### 8. Commit

```bash
git add docs/screens/{screen-name}/
git commit -m "docs(screen-name): split large documentation

- Split 650-line README into 3 files
- README.md now 200 lines (overview)
- features.md now 300 lines (detailed features)
- technical.md now 250 lines (implementation)
- Added cross-references between files
"
```

## Split Strategies

### Screen Documentation

**If >500 lines total:**

```
README.md (overview) < 300
features.md (details) < 400
technical.md (impl) < 500
flows.md (workflows) < 300
```

### Guide Documentation

**If >500 lines:**

```
{guide}.md (main) < 500
{guide}-advanced.md (advanced) < 500
```

Or split by topic:
```
{topic}-basics.md
{topic}-advanced.md
{topic}-reference.md
```

### Architecture Documentation

**If >500 lines:**

Split by component or layer:
```
architecture/overview.md
architecture/layer1-cli.md
architecture/layer2-core.md
architecture/layer3-infrastructure.md
```

## Checklist

- [ ] Counted lines (confirmed >450)
- [ ] Identified logical split points
- [ ] Created new files with templates
- [ ] Moved content to new files
- [ ] All files under line limits
- [ ] Added cross-references
- [ ] Tested all links
- [ ] Committed with explanation

## Common Mistakes

 **Splitting mid-topic**: Don't split in the middle of a feature
 **No cross-references**: Files should link to each other
 **Inconsistent naming**: Use standard names (README, features, technical, flows)
 **Still too large**: Each file should be well under 500 lines

✅ **Split at logical boundaries**: Complete sections
✅ **Add navigation**: Cross-reference related files
✅ **Follow templates**: Use standard structure
✅ **Leave buffer**: Aim for 300-400 lines, not 499
