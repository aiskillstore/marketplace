# Documentation Workflows

Index of all workflows. Load specific workflow when needed.

## Available Workflows

### Creation Workflows

- **[create-screen.md](./create-screen.md)** - Creating new screen documentation
- **[add-examples.md](./add-examples.md)** - Adding examples to existing docs

### Update Workflows

- **[update-existing.md](./update-existing.md)** - Updating existing documentation
- **[split-large-file.md](./split-large-file.md)** - Splitting files >500 lines

### Maintenance Workflows

- **[consolidate-duplicates.md](./consolidate-duplicates.md)** - Consolidating duplicate docs
- **[review-quarterly.md](./review-quarterly.md)** - Quarterly documentation review

## Quick Decision Trees

### Should I Create Documentation?

```
Is feature complete? ──No──> STOP (don't create)
       │
      Yes
       │
Does similar doc exist? ──Yes──> See update-existing.md
       │
       No
       │
Is it temporary/WIP? ──Yes──> STOP (use GitHub Issue)
       │
       No
       │
CREATE → See create-screen.md or appropriate workflow
```

### Where Should Documentation Go?

```
What are you documenting?
       │
       ├─ Screen feature? → docs/screens/{screen-name}/
       ├─ User guide? → docs/guides/
       ├─ Architecture? → docs/architecture/
       └─ Configuration? → docs/guides/configuration.md
```

### Should I Split This File?

```
Current lines: ___
       │
   >500 lines? ──Yes──> See split-large-file.md (MUST split)
       │
       No
       │
   >450 lines? ──Yes──> See split-large-file.md (SHOULD split)
       │
       No
       │
     <450 lines ──────> OK (no split needed)
```

## Quick Commands

```bash
# Check for existing docs
grep -r "keyword" docs/ --include="*.md"

# Count lines
wc -l docs/path/to/file.md

# List screens
ls -la docs/screens/

# Test links
grep -o "\[.*\](.*)" docs/file.md
```
