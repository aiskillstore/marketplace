---
name: documentation
description: Enforces documentation standards and structure for this project. This skill should be used when creating, updating, or organizing documentation to ensure compliance with project rules, prevent redundancy, and maintain screen-based organization. Activates when user asks to create/update docs or when documentation needs to be generated.
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Documentation Skill

Ensures all documentation follows project standards and prevents redundant files.

## Purpose

This skill provides tools and workflows for efficient documentation management:
- Section-level interaction scripts (search, get, update without reading full files)
- Document templates for consistent structure
- Workflows for common documentation tasks
- Rules and standards to prevent redundancy

## When to Use This Skill

Use this skill when:
- Creating new documentation for features, screens, or architecture
- Updating existing documentation after code changes
- Finding and consolidating duplicate documentation
- Splitting large documentation files (>500 lines)
- Searching for specific information in docs
- Checking documentation quality and compliance

## Core Principles

### 1. DRY (Don't Repeat Yourself)
- Check for existing documentation before creating new files
- Update existing docs instead of creating duplicates
- Consolidate related information into single files

### 2. Screen-Based Organization
```
docs/
├── README.md              # Master index (DO NOT MODIFY)
├── guides/                # User and developer guides
├── architecture/          # Architecture docs
└── screens/               # Screen-specific docs
    └── {screen-name}/
        ├── README.md      # Overview (required)
        ├── features.md    # Features (optional)
        ├── technical.md   # Technical (required)
        └── flows.md       # Flows (optional)
```

### 3. Size Limits
- Maximum 500 lines per file
- Split files approaching limit (>450 lines)
- Keep documents focused and scannable

## How to Use This Skill

### Step 1: Check for Existing Documentation

**Use scripts for efficient search** (80-98% context reduction):

```bash
# Search without reading full files
./scripts/doc-search.sh "topic-keyword"

# Get file metadata (0 lines read)
./scripts/doc-metadata.sh docs/path/to/file.md

# List sections to navigate (structure only)
./scripts/doc-list-sections.sh docs/file.md
```

**Complete script documentation:** See `scripts/README.md`

### Step 2: Determine Action

**If similar documentation exists:**
- Load workflow: `references/workflows/update-existing.md`
- Use `doc-get-section.sh` to read only relevant section
- Update section with `doc-update-section.sh`

**If creating new documentation:**
- Load workflow: `references/workflows/create-screen.md`
- Load template: `assets/templates/screen-readme.md` or `assets/templates/screen-technical.md`
- Follow template structure

**If file is too large (>450 lines):**
- Load workflow: `references/workflows/split-large-file.md`

**If duplicates found:**
- Load workflow: `references/workflows/consolidate-duplicates.md`

### Step 3: Validate Against Rules

Load reference file: `references/rules.md`

Check:
- ✅ No duplicate content exists
- ✅ File under 500 lines
- ✅ Code references include file:line format
- ✅ All code blocks have language specified
- ✅ Examples are tested and working

**Complete rules:** See `references/rules.md`

## Bundled Resources

### Scripts (`scripts/`)

Efficient section-level interaction tools:

- **doc-search.sh** - Search content without reading full files
- **doc-list-sections.sh** - List all headings with line numbers
- **doc-get-section.sh** - Extract specific section only (90% context reduction)
- **doc-update-section.sh** - Update section without reading full file
- **doc-delete-section.sh** - Remove section
- **doc-insert-after.sh** - Insert content after section
- **doc-metadata.sh** - Get file statistics (100% context reduction)
- **doc-find-duplicates.sh** - Find redundant content

**Benefits:** 80-98% reduction in context usage vs reading entire files

**Complete documentation:** `scripts/README.md`

### References (`references/`)

Load as needed for detailed information:

- **rules.md** - Complete documentation rules and anti-patterns
- **structure.md** - Directory organization details and navigation
- **examples.md** - Real examples from this project (good vs bad patterns)
- **workflows/** - Step-by-step workflows for common tasks:
  - `create-screen.md` - Creating new screen documentation
  - `update-existing.md` - Updating existing documentation
  - `consolidate-duplicates.md` - Consolidating duplicate docs
  - `split-large-file.md` - Splitting files >500 lines
  - `add-examples.md` - Adding examples to docs
  - `review-quarterly.md` - Quarterly documentation review

### Assets (`assets/`)

Templates used in documentation output:

- **templates/** - Document templates:
  - `screen-readme.md` - For docs/screens/{name}/README.md
  - `screen-technical.md` - For docs/screens/{name}/technical.md
  - `screen-features.md` - For docs/screens/{name}/features.md
  - `screen-flows.md` - For docs/screens/{name}/flows.md
  - `architecture.md` - For docs/architecture/*.md
  - `guide.md` - For docs/guides/*.md

## Progressive Disclosure

This skill uses filesystem-based progressive disclosure:

**Level 1: Metadata (always in context)**
- Skill name and description (~100 words)

**Level 2: SKILL.md (when skill triggers)**
- Core instructions and workflow guidance (~2k words)

**Level 3: Bundled resources (loaded as needed)**
- Scripts: Execute without reading into context
- References: Load specific file when detailed info needed
- Assets: Copy template into output

**Example:** Creating screen docs
- Before: Read all 3,620 lines
- After: SKILL.md (300 lines) + workflow (150 lines) + template (200 lines) = 650 lines (82% reduction)

## Typical Workflows

### Creating New Screen Documentation

1. **Check:** `./scripts/doc-search.sh "ScreenName"`
2. **If not exists:** Load `references/workflows/create-screen.md`
3. **Follow workflow:**
   - Create directory: `docs/screens/{screen-name}`
   - Use template: `assets/templates/screen-readme.md`
   - Use template: `assets/templates/screen-technical.md`
   - Validate against: `references/rules.md`

### Updating Existing Documentation

1. **Get metadata:** `./scripts/doc-metadata.sh docs/file.md`
2. **List sections:** `./scripts/doc-list-sections.sh docs/file.md`
3. **Get section:** `./scripts/doc-get-section.sh docs/file.md "Section"`
4. **Update section:** `./scripts/doc-update-section.sh docs/file.md "Section" new-content.md`

### Finding and Removing Duplicates

1. **Find duplicates:** `./scripts/doc-find-duplicates.sh docs/`
2. **Load workflow:** `references/workflows/consolidate-duplicates.md`
3. **Follow consolidation steps**
4. **Delete redundant files**

## Questions to Ask User

Before creating documentation:
- "Found similar docs at {path}. Update existing instead of creating new?"
- "Is this feature complete and ready to document?"
- "Should this go in screens/{screen}/, guides/, or architecture/?"
- "File is 450+ lines. Should split into multiple files?"

## Success Criteria

Good documentation is:
- ✅ Easy to find (follows structure in `references/structure.md`)
- ✅ Easy to read (under 500 lines)
- ✅ No duplicates (DRY principle)
- ✅ Up to date (matches current code)
- ✅ Actionable (includes tested examples)
- ✅ Traceable (code references with file:line format)
