# human-docs Skill

**Version:** 1.0.0
**Created:** 2025-11-01
**Purpose:** Transform detailed AI documentation into human-friendly formats

---

## Overview

The `human-docs` skill creates **human-optimized documentation** from detailed AI context documents. It generates three complementary formats:

1. **SUMMARY** - 20% of original length, executive overview
2. **QUICKSTART** - 5-minute read, hands-on tutorial
3. **DIAGRAMS** - Visual representation with Mermaid.js

---

## When to Use

Use this skill when:
- ✅ You need to share AI documentation with human developers
- ✅ Documentation is too detailed for quick reference
- ✅ Visual diagrams would improve understanding
- ✅ You want consistent, maintainable human docs
- ✅ You need to onboard new team members quickly

**Do NOT use when:**
- ❌ Working with AI agents (they read ai/ folder directly)
- ❌ Creating new documentation from scratch (use appropriate domain skill)
- ❌ Making minor edits to existing docs

---

## Skill Structure

```
.claude/skills/human-docs/
├── Skill.md                           # Main skill prompt
├── README.md                          # This file
├── assets/
│   └── templates/
│       ├── summary_template.md        # Template for summaries
│       ├── quickstart_template.md     # Template for quick starts
│       └── diagrams_template.md       # Template for visual guides
├── references/
│   └── mermaid_examples.md            # Mermaid.js diagram templates
└── scripts/                           # (Future) Automation scripts
```

---

## Output Structure

The skill creates parallel folder structure:

```
ai/                                    docs/
├── architect/                         ├── architect/
│   ├── app/                          │   ├── app/
│   │   ├── 01_CORE_DATA_PIPELINE.md  │   │   ├── 01_CORE_DATA_PIPELINE_SUMMARY.md
│   │   │                             │   │   ├── 01_CORE_DATA_PIPELINE_QUICKSTART.md
│   │   │                             │   │   └── 01_CORE_DATA_PIPELINE_DIAGRAMS.md
│   │   └── 02_BACKEND_REQUIREMENTS.md│   │   └── 02_BACKEND_REQUIREMENTS_SUMMARY.md
```

**Key Principle:** `ai/` remains **source of truth** (detailed, for AI), `docs/` contains **human extracts** (concise, visual, actionable).

---

## How to Invoke

```
Skill(human-docs)
```

Then request a specific workflow:

### Example 1: Create all three formats
```
Create human docs for ai/architect/app/01_CORE_DATA_PIPELINE.md
```

### Example 2: Update existing human doc
```
Update docs/architect/app/01_CORE_DATA_PIPELINE_SUMMARY.md to reflect changes in AI doc
```

### Example 3: Batch creation
```
Create summaries for all documents in ai/architect/app/
```

---

## Workflows

The skill supports 5 workflows:

1. **NEW_DOCUMENT** - Create all 3 formats from AI doc
2. **UPDATE_EXISTING** - Sync human doc with AI changes
3. **DIAGRAMS_ONLY** - Extract/create visual diagrams
4. **BATCH_SUMMARIES** - Process multiple AI docs
5. **MIGRATE_EXISTING** - Convert old docs to new format

See `Skill.md` for detailed workflow descriptions.

---

## Quality Standards

All human documentation must meet:

### Summaries
- ✅ 20% or less of original length
- ✅ Executive summary section
- ✅ 5 key points maximum
- ✅ Quick reference table
- ✅ Clear "when to read full doc" guidance

### Quick Starts
- ✅ 5-minute read maximum
- ✅ Copy-paste ready commands
- ✅ Working code examples
- ✅ Verification steps
- ✅ Common issues and fixes

### Diagrams
- ✅ Mermaid.js syntax (renders in GitHub/markdown)
- ✅ Consistent color scheme (blue=input, green=output, yellow=decision)
- ✅ Clear labels and legends
- ✅ Editable source code included
- ✅ Multiple views (overview, flow, detail, schema)

---

## Maintenance Guidelines

### When AI docs change:
1. Update AI document in `ai/` folder (source of truth)
2. Invoke `Skill(human-docs)` with UPDATE_EXISTING workflow
3. Skill will sync changes to `docs/` folder
4. Review human docs for clarity

### When creating new AI docs:
1. Create detailed AI doc in `ai/` folder first
2. Invoke `Skill(human-docs)` with NEW_DOCUMENT workflow
3. Skill generates 3 human-friendly formats
4. Review and refine if needed

**Golden Rule:** Never manually edit `docs/` without updating `ai/` first. Always use the skill to maintain consistency.

---

## Templates

The skill uses three templates in `assets/templates/`:

1. **summary_template.md** - Structured format for summaries
2. **quickstart_template.md** - Hands-on tutorial format
3. **diagrams_template.md** - Visual guide format

Templates ensure consistency across all human documentation.

---

## References

The skill includes ready-to-use resources:

1. **mermaid_examples.md** - 5+ diagram types with working examples:
   - Flowcharts
   - Sequence diagrams
   - Entity-relationship diagrams
   - State diagrams
   - Gantt charts

---

## Examples

### Example 1: Create Summary for Backend Requirements

**Command:**
```
Skill(human-docs)
Create summary for ai/architect/app/02_BACKEND_REQUIREMENTS.md
```

**Output:**
- `docs/architect/app/02_BACKEND_REQUIREMENTS_SUMMARY.md`
- Contains: Executive summary, 5 key points, quick reference table, when to read full doc

### Example 2: Create Quick Start for CSV Upload

**Command:**
```
Skill(human-docs)
Create quick start for ai/architect/app/05_CSV_UPLOAD_SPECIFICATION.md
```

**Output:**
- `docs/architect/app/05_CSV_UPLOAD_SPECIFICATION_QUICKSTART.md`
- Contains: 5-min tutorial, copy-paste commands, working code, verification steps

### Example 3: Create Diagrams for Data Flow

**Command:**
```
Skill(human-docs)
Create diagrams for ai/architect/app/07_WORKFLOWS_AND_DATA_FLOW.md
```

**Output:**
- `docs/architect/app/07_WORKFLOWS_AND_DATA_FLOW_DIAGRAMS.md`
- Contains: System overview, data flow, component interaction, process flow diagrams

---

## Version History

**v1.0.0 (2025-11-01)** - Initial release
- Three format types (SUMMARY, QUICKSTART, DIAGRAMS)
- Five workflows
- Three templates
- Mermaid.js diagram library
- Quality standards

---

## Future Enhancements

Potential future additions:
- Automation scripts for batch processing
- HTML/PDF export
- Interactive diagram editor
- Translation support for multiple languages
- Auto-sync with AI doc changes (git hooks)

---

## Related Documentation

- **Skill prompt:** `Skill.md`
- **Mermaid examples:** `references/mermaid_examples.md`
- **Templates:** `assets/templates/*.md`
- **Documentation standard:** `ai/DOCUMENTATION_STANDARD.md`

---

**Status:** ✅ Complete and ready to use
