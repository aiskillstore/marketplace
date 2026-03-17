---
name: para-skill
description: >
  PARA method knowledge management for Obsidian vaults. Use this skill whenever
  the user wants to organize notes using PARA (Projects, Areas, Resources, Archive),
  classify a note into a PARA category, route a note to the right vault folder,
  normalize frontmatter fields, run a PARA hygiene review, suggest archiving, audit
  vault structure, or process new knowledge inputs into an existing PARA-based vault.
  Also trigger when the user mentions inbox processing, vault cleanup, note classification,
  PARA review, or asks "where does this note belong?". Works with existing Obsidian
  skills (obsidian-markdown, obsidian-cli) — never replaces them.
---

# PARA Obsidian Skill

## What this skill does

This skill provides PARA-method decision logic for Obsidian vaults. It decides **where** notes belong, **when** to archive, and **how** to keep the vault healthy — while leaving file creation, markdown formatting, and Obsidian syntax to the installed base skills.

PARA is an organizational framework by Tiago Forte that structures information by **action relevance**, not topic:
- **Projects** — concrete initiatives with a goal and an endpoint
- **Areas** — ongoing responsibilities with no fixed end date
- **Resources** — reference knowledge for potential future use
- **Archive** — completed, paused, or inactive content

Read `references/classification-rules.md` for detailed classification heuristics.

---

## Vault Configuration

Default paths for this vault (override in conversation if different):

```yaml
paths:
  inbox: "0_Inbox"          # created on demand if missing
  projects: "1_Projects"
  areas: "2_Areas"
  resources: "3_Resources"
  archive: "4_Archives"
```

Default mode: **cautious** — suggest first, act only when confident or explicitly asked.

---

## Core Workflow

For every PARA-related task, follow this sequence:

1. **Read** the note content, title, existing frontmatter, tags, and current file path
2. **Collect signals** — look for project indicators (deadlines, tasks, goals), area indicators (ongoing, recurring), resource indicators (reference, no action pressure), archive indicators (done, cancelled, historical)
3. **Check conventions** — respect existing `para_type` frontmatter; existing folder placement is a strong signal
4. **Classify** with a confidence level: `high`, `medium`, or `low`
5. **Plan frontmatter** additions — only add fields from the schema, never overwrite non-PARA fields
6. **Propose routing** — suggest the target path
7. **Assess risk** — only act directly when confidence is high AND the user has given explicit permission or the mode is `balanced`/`aggressive`
8. **Log changes** when writing anything

When in doubt: set `needs_review: true`, place in Inbox, and explain why.

See `references/classification-rules.md` for the full decision tree.

---

## Available Actions

### `capture` — Process new content
Accept raw text, meeting notes, ideas, or document descriptions. Classify them, propose or create a note in the right location, and set frontmatter.

**Example trigger:** "Capture this: Vorbereitung Workshop Führungsteam April"
**Output:** PARA classification + proposed path + frontmatter draft

### `classify` — Classify an existing note
Read a note and determine its PARA type. Return classification, confidence level, and reasoning.

**Example trigger:** "Welcher PARA-Typ ist diese Notiz?" or "Klassifiziere 2_Areas/Weiterbildung/..."
**Output:** `para_type`, `confidence`, explanation, suggested changes

### `route` — Determine or apply target location
Calculate the correct target folder for a note. In cautious mode: suggest only. With explicit permission: move the file.

**Example trigger:** "Wo gehört diese Notiz hin?" or "Route diese Notiz korrekt ein"
**Output:** Current path → suggested path, reasoning, conflict check

### `normalize` — Fix frontmatter
Add missing PARA frontmatter fields to a note without touching non-PARA fields. Never remove existing fields.

**Example trigger:** "Normalisiere das Frontmatter dieser Notiz" or "Füge PARA-Metadaten hinzu"
**Output:** Updated frontmatter block (show diff before applying)

### `review` — PARA hygiene report
Scan a folder or the whole vault for hygiene issues. See `references/review-playbook.md` for what to check.

**Example trigger:** "Mach einen PARA-Review" or "Zeig mir, was im Vault aufgeräumt werden sollte"
**Output:** Structured report (projects without next steps, stale areas, inbox backlog, archiving candidates)

### `archive` — Archive a note defensively
Move a note to the Archive folder with `archived: true`, `archive_date`, and updated `status`. Never delete. Preserve all wikilinks.

**Example trigger:** "Archiviere dieses Projekt" or "Das Projekt ist abgeschlossen"
**Output:** Confirmation of move + frontmatter changes (dry-run by default)

### `audit` — Full vault consistency audit
Scan all notes for PARA inconsistencies: missing frontmatter, wrong folder placement, orphaned notes, stale reviews. Produces a prioritized action list.

**Example trigger:** "Mach einen vollständigen Vault-Audit" or "Was stimmt in meinem Vault nicht?"
**Output:** Audit report with actionable items

### `suggest` — Recommendation without changes
Give a PARA recommendation with full reasoning, but make no changes to any file.

**Example trigger:** "Was würdest Du mit dieser Notiz machen?" or "Vorschlag für diese Datei"
**Output:** Recommendation + reasoning (read-only)

---

## Safety Rules

These rules are non-negotiable regardless of mode:

1. **No mass moves without explicit user authorization** — always ask first
2. **No deletion** — archive means move, never delete
3. **No overwriting non-PARA frontmatter fields** — only add/update defined PARA fields
4. **Low confidence → needs_review** — never force a classification when unsure
5. **Dry-run by default** — show what would happen before doing it
6. **Preserve wikilinks** — never rename files in ways that break `[[links]]`
7. **Log every structural change** — use the change log format below
8. **No reclassification from a single weak signal** — require 2+ supporting indicators

### Change Log Format

When making structural changes, append to a `PARA-Changelog.md` in the vault root:

```markdown
## 2026-03-14
- Classified `Meeting Notes Team Alpha` → project (confidence: medium)
- Suggested move to `1_Projects/team-alpha/` (not yet applied, needs_review: true)
- Normalized frontmatter in `2_Areas/Weiterbildung/KI-Kurs.md`
```

---

## Frontmatter Schema

Read `references/frontmatter-schema.md` for the full field definitions.

Quick reference — only write these fields:
```yaml
para_type: project        # project | area | resource | archive
status: active            # active | on-hold | done | archived | reference | needs_review
review_date: 2026-03-21
confidence: high          # high | medium | low
needs_review: false
archived: false
archive_date:             # only when archiving
source: manual            # manual | meeting | import | daily-note | web
```

Never touch: titles, body content, existing tags not prefixed with `para/`, wikilinks, non-PARA frontmatter fields.

---

## Cooperation with Other Skills

This skill handles: **classification logic, routing decisions, PARA frontmatter, review reports**

Leave to obsidian-markdown / obsidian-cli: **file creation, markdown syntax, wikilink formatting, template application, dataview queries**

When creating a new note as part of `capture` or `route`, delegate file creation to the obsidian-markdown or obsidian-cli skill if available. Only use direct file writes as fallback.

Read `references/compatibility-notes.md` for conflict avoidance rules.

---

## Response Format

Always communicate:
1. **What** you classified/found (with `para_type` and `confidence`)
2. **Why** — at least 2 supporting signals
3. **What you propose to change** (as a clear list)
4. **What you're uncertain about** (if anything)
5. **What you'll do next** — or ask for permission before acting

For reviews and audits, use the structured report format in `references/review-playbook.md`.
