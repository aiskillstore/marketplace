# para-skill

> PARA-method decision logic for AI-assisted knowledge management.

![Version](https://img.shields.io/badge/version-0.1.0-blue) ![License](https://img.shields.io/badge/license-MIT-green)

---

## What it does

`para-skill` encodes the decision logic of the [PARA method](https://fortelabs.com/blog/para/) — the organizational framework by Tiago Forte that structures information by **action relevance** rather than topic. It tells an AI assistant *where* a note belongs, *when* to archive it, and *how* to keep a knowledge base healthy.

PARA organizes all information into four categories:

- **Projects** — concrete initiatives with a goal and an endpoint
- **Areas** — ongoing responsibilities with no fixed end date
- **Resources** — reference knowledge for potential future use
- **Archive** — completed, paused, or inactive content

The skill handles **classification logic and routing decisions**. File operations, markup formatting, and tool-specific syntax stay with whatever tools are already in use.

---

## Attribution

The PARA method was created by **Tiago Forte** and is described in detail in his book *Building a Second Brain*. All rights to the PARA method belong to Tiago Forte.

This skill is an independent, unofficial implementation of the PARA organizational framework. It is not affiliated with, endorsed by, or officially connected to Tiago Forte or Forte Labs in any way.

If you find PARA valuable, consider supporting Tiago Forte's work:
- [Forte Labs](https://fortelabs.com)
- [Building a Second Brain](https://buildingasecondbrain.com)

---

## Features

8 core actions:

| Action | Description |
|---|---|
| `capture` | Process raw text, meeting notes, or ideas — classify and place in the right location |
| `classify` | Determine the PARA type of an existing note with confidence level and reasoning |
| `route` | Calculate the correct target folder; suggest only (cautious) or move with permission |
| `normalize` | Add missing PARA frontmatter fields without touching existing content |
| `review` | Weekly/monthly/quarterly hygiene reports for the whole knowledge base |
| `archive` | Defensively move a note to Archive with proper metadata (dry-run by default) |
| `audit` | Full consistency audit — missing metadata, wrong placement, orphaned notes |
| `suggest` | Read-only PARA recommendation with full reasoning, no file changes |

---

## Compatibility

`para-skill` is designed for use with agentic CLI tools that support context loading via markdown files — [Claude Code](https://claude.ai/code) being the primary reference implementation, though other agentic tools with similar skill/context mechanisms work the same way.

On the notes side, the skill is developed and tested against [Obsidian](https://obsidian.md) vaults, but the PARA decision logic applies to any markdown-based PKM (Logseq, Foam, plain-text systems, etc.) — folder paths and frontmatter fields are fully configurable.

---

## Installation

Copy or clone this repository so that `SKILL.md` is discoverable by your AI assistant. The exact location depends on the tool you use — place it where your assistant loads context files or skills from.

```bash
git clone https://github.com/scifishelf/para-skill
```

---

## Quick Start

Use natural language to trigger the skill:

```
"Capture this: Prepare leadership team workshop for April"
```
→ Classifies as Project, proposes path `1_Projects/`, drafts frontmatter.

```
"Classify this note: 2_Areas/Learning/AI-Course.md"
```
→ Returns PARA type, confidence level, and 2+ supporting signals.

```
"Run a PARA review of my knowledge base"
```
→ Structured report: inbox backlog, projects without next steps, archive candidates.

---

## Folder Configuration

The skill uses these default paths (matching a numbered-prefix convention common in many PKM setups):

```yaml
paths:
  inbox: "0_Inbox"        # created on demand if missing
  projects: "1_Projects"
  areas: "2_Areas"
  resources: "3_Resources"
  archive: "4_Archives"
```

To use different paths, tell your assistant at the start of a session:

```
"My notes use 'Projects/', 'Areas/', 'Resources/', 'Archive/' — adjust your paths."
```

Default mode is **cautious** — the skill suggests before acting. Override per session:

```
"Use balanced mode for this session."
```

---

## How it works

The skill is a `SKILL.md` file that loads domain-specific decision logic into the AI context. It ships with four reference documents:

| File | Purpose |
|---|---|
| `references/classification-rules.md` | Full decision tree and indicator signals |
| `references/frontmatter-schema.md` | All PARA metadata fields and writing rules |
| `references/review-playbook.md` | Review rhythms, report format, hygiene checks |
| `references/compatibility-notes.md` | Role division with file-handling tools |

---

## Safety principles

These rules apply regardless of mode:

1. **No mass moves without explicit authorization** — always ask first
2. **No deletion** — archive means *move*, never delete
3. **No overwriting non-PARA metadata** — only add/update defined PARA fields
4. **Low confidence → `needs_review`** — never force a classification when uncertain
5. **Dry-run by default** — show what would happen before doing it
6. **Preserve links** — never rename files in ways that break internal references
7. **Log every structural change** — appends to `PARA-Changelog.md` in the notes root
8. **Require 2+ signals for reclassification** — no snap judgments from weak evidence

---

## Contributing

Issues and pull requests welcome. Please keep changes focused — this skill is intentionally minimal and decision-logic only.

---

## License

MIT — see [LICENSE](LICENSE).
