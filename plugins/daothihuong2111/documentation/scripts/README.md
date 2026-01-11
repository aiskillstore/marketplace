# Documentation Scripts

Efficient section-level interaction with markdown documentation files, inspired by Serena MCP's LSP-based approach for code.

## Philosophy

Instead of reading entire files, these scripts work at **section-level** (markdown headings as "symbols"), enabling:
- ✅ Find content without reading full files
- ✅ Get specific sections only
- ✅ Update/delete sections without loading entire document
- ✅ Minimal context usage (similar to LSP for code)

## Available Scripts

### 1. doc-search.sh
Search for content across documentation files.

**Usage:**
```bash
./scripts/doc-search.sh <pattern> [directory]
```

**Examples:**
```bash
# Search in all docs
./scripts/doc-search.sh "slash command"

# Search in specific screen
./scripts/doc-search.sh "validation" docs/screens/config
```

**Output**: Matching lines with 2 lines of context (before/after)

---

### 2. doc-list-sections.sh
List all sections (headings) in a markdown file.

**Usage:**
```bash
./scripts/doc-list-sections.sh <file>
```

**Example:**
```bash
./scripts/doc-list-sections.sh docs/screens/home/README.md
```

**Output**:
```
Home Screen (line 1)
  Overview (line 5)
  Features (line 11)
    Core Features (line 13)
      1. Conversation History (line 15)
```

**Use case**: Navigate file structure without reading entire file

---

### 3. doc-get-section.sh
Extract a specific section from markdown file.

**Usage:**
```bash
./scripts/doc-get-section.sh <file> <section-heading>
```

**Examples:**
```bash
# Get Features section
./scripts/doc-get-section.sh docs/screens/home/README.md "Features"

# Get subsection
./scripts/doc-get-section.sh docs/screens/home/README.md "Core Features"
```

**Output**: Only the requested section (heading + content until next same-level heading)

**Use case**: Read specific section without loading 500+ lines

---

### 4. doc-update-section.sh
Update a specific section content.

**Usage:**
```bash
./scripts/doc-update-section.sh <file> <section-heading> <new-content-file>
```

**Example:**
```bash
# Update Features section
echo "## Features\n\nNew content here" > new-features.md
./scripts/doc-update-section.sh docs/screens/home/README.md "Features" new-features.md
```

**Use case**: Update one section without reading/modifying entire file

---

### 5. doc-delete-section.sh
Delete a specific section.

**Usage:**
```bash
./scripts/doc-delete-section.sh <file> <section-heading>
```

**Example:**
```bash
# Remove deprecated section
./scripts/doc-delete-section.sh docs/screens/home/README.md "Old Feature"
```

**Use case**: Remove section without loading entire file

---

### 6. doc-insert-after.sh
Insert content after a specific section.

**Usage:**
```bash
./scripts/doc-insert-after.sh <file> <section-heading> <new-content-file>
```

**Example:**
```bash
# Add new section after Features
echo "## New Feature\n\nDescription" > new-section.md
./scripts/doc-insert-after.sh docs/screens/home/README.md "Features" new-section.md
```

**Use case**: Add content at specific position without reading full file

---

### 7. doc-metadata.sh
Get metadata about a documentation file.

**Usage:**
```bash
./scripts/doc-metadata.sh <file>
```

**Example:**
```bash
./scripts/doc-metadata.sh docs/screens/home/README.md
```

**Output**:
```
File: docs/screens/home/README.md
----------------------------------------
Lines: 261
Size Status: ✅ OK (<400 lines)
H2 Sections: 8
H3 Subsections: 12
Code Blocks: 6
Links: 5
Last Modified: 2025-11-09

Top-level sections:
  - Overview
  - Features
  - Usage
```

**Use case**: Check file stats without reading content

---

### 8. doc-find-duplicates.sh
Find duplicate content across documentation files.

**Usage:**
```bash
./scripts/doc-find-duplicates.sh [directory]
```

**Example:**
```bash
./scripts/doc-find-duplicates.sh docs/screens
```

**Output**:
- Duplicate section headings
- Files with >80% similar content
- Duplicate code blocks

**Use case**: Detect redundant documentation (DRY principle)

---

## Comparison with Reading Full Files

### Traditional Approach (Read Tool)
```
User: "Update the Features section in home screen docs"
Claude:
1. Read docs/screens/home/README.md (261 lines) ← READ ALL
2. Find Features section
3. Edit section
4. Write back entire file
= 261 lines read
```

### Script-Based Approach
```
User: "Update the Features section in home screen docs"
Claude:
1. Run doc-list-sections.sh (see structure) ← METADATA ONLY
2. Run doc-get-section.sh "Features" ← READ SECTION ONLY
3. Run doc-update-section.sh ← UPDATE SECTION ONLY
= ~50 lines read (80% reduction)
```

## Integration with Skill

These scripts are automatically used by the documentation skill when:
- Searching for content → `doc-search.sh`
- Checking file metadata → `doc-metadata.sh`
- Getting specific section → `doc-get-section.sh`
- Updating section → `doc-update-section.sh`
- Detecting duplicates → `doc-find-duplicates.sh`

## Technical Details

### Section Detection

Scripts identify sections by markdown headings:
- `#` (H1) - Title
- `##` (H2) - Main section
- `###` (H3) - Subsection
- `####` (H4) - Sub-subsection

### Section Extraction Algorithm

```bash
1. Find target heading (case-insensitive)
2. Get heading level (count #)
3. Extract all content until:
   - Next same-level heading OR
   - Higher-level heading OR
   - End of file
```

### Safety

- All update/delete operations use temp files
- Atomic file replacement (mv)
- Original file preserved until successful write
- Case-insensitive section matching

## Performance

**File**: 500 lines, 10 sections

| Operation | Read Tool | Script | Savings |
|-----------|-----------|--------|---------|
| Search | 500 lines | ~10 lines | 98% |
| Get section | 500 lines | ~50 lines | 90% |
| Update section | 500 lines | ~50 lines | 90% |
| Metadata | 500 lines | 0 lines | 100% |

## Error Handling

All scripts:
- ✅ Validate input parameters
- ✅ Check file existence
- ✅ Provide helpful error messages
- ✅ Return appropriate exit codes

## Examples

### Workflow: Update a Section

```bash
# 1. Check file metadata
./scripts/doc-metadata.sh docs/screens/home/README.md

# 2. List sections to find target
./scripts/doc-list-sections.sh docs/screens/home/README.md

# 3. Get current section content
./scripts/doc-get-section.sh docs/screens/home/README.md "Features" > current-features.md

# 4. Edit content (create new-features.md)

# 5. Update section
./scripts/doc-update-section.sh docs/screens/home/README.md "Features" new-features.md
```

### Workflow: Find and Remove Duplicates

```bash
# 1. Find duplicates
./scripts/doc-find-duplicates.sh docs/

# 2. For each duplicate section, get content
./scripts/doc-get-section.sh docs/file1.md "Duplicate Section"
./scripts/doc-get-section.sh docs/file2.md "Duplicate Section"

# 3. Choose which to keep, delete others
./scripts/doc-delete-section.sh docs/file2.md "Duplicate Section"
```

## Future Enhancements

Potential additions:
- [ ] `doc-rename-section.sh` - Rename section heading
- [ ] `doc-move-section.sh` - Move section to different file
- [ ] `doc-merge-sections.sh` - Merge multiple sections
- [ ] `doc-validate.sh` - Validate markdown structure
- [ ] `doc-stats.sh` - Generate documentation statistics

## See Also

- [Serena MCP](https://github.com/oraios/serena) - Inspiration for section-level interaction
- [../SKILL.md](../SKILL.md) - Main documentation skill
- [../rules.md](../rules.md) - Documentation rules
