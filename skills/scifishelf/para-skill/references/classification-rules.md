# PARA Classification Rules

## Decision Framework

The central question for any note is:

> **Wofür wird diese Information aktuell benötigt?**

Classification follows this priority order when signals conflict:

1. Explicit `para_type` in existing frontmatter → always wins
2. Current folder placement → strong signal, don't override lightly
3. Active project with goal + endpoint → Project
4. Ongoing responsibility, no end date → Area
5. Reference knowledge, no action pressure → Resource
6. Completed, cancelled, or inactive → Archive

---

## Classification Decision Tree

```
Does the note have explicit `para_type` frontmatter?
  YES → Use it (check if it still seems correct, flag if stale)
  NO  → Continue below

Is the content completed, historical, or explicitly done/cancelled?
  YES → Archive (if confidence high) or needs_review
  NO  → Continue below

Is there a concrete goal + a natural endpoint?
  YES → Does it have active next steps or a deadline?
          YES → Project (high confidence)
          NO  → Project (medium) or needs_review
  NO  → Continue below

Is this an ongoing responsibility that needs recurring attention?
  YES → Area
  NO  → Continue below

Is this reference material, a knowledge collection, or has no direct action pressure?
  YES → Resource
  NO  → needs_review (send to Inbox)
```

---

## Indicator Signals

### Project Indicators (2+ required for high confidence)
- Deadline, target date, or time-bounded language ("bis April", "im Q2")
- Open tasks or next steps ("TODO", "- [ ]", "nächste Schritte")
- Goal description ("Ziel:", "wir möchten", "deliverable")
- Action verbs: "vorbereiten", "abschließen", "umsetzen", "launchen", "planen"
- Status markers: `active`, `in-progress`
- Named project with a specific outcome

### Area Indicators (2+ required)
- Recurring responsibility language ("laufend", "kontinuierlich", "Routine")
- No natural endpoint described
- Domain keywords: Gesundheit, Finanzen, Karriere, Familie, Team, Weiterbildung
- Review-oriented content (checklists, habits, standards)
- Status markers: `ongoing`, `active` without a deadline
- "Area:" or "Bereich:" explicitly mentioned

### Resource Indicators (2+ required)
- Knowledge/reference framing ("Notizen zu", "Guide", "Referenz", "Zusammenfassung")
- No current action pressure
- Educational or informational content
- Bookmarks, link collections, reading notes
- Topic-focused (not person or project-focused)
- No open tasks

### Archive Indicators (1 strong OR 2+ weak)
- Explicit "done", "abgeschlossen", "erledigt", "archiviert", "cancelled"
- Status markers: `done`, `archived`, `cancelled`, `inactive`
- Historical framing ("Retrospektive 2024", "ehemals", "war")
- Very old last-modified date + completed context
- Belongs to a project now marked as done

---

## Conflict Resolution

### Project vs. Area
A project has an **endpoint**. If you can ask "When will this be done?" and there's a real answer → Project. If the answer is "never, it just continues" → Area.

Example edge case: "Weiterbildung KI" — could be either.
- If tied to a specific course/certification → Project
- If ongoing self-development without a finish line → Area
- If unclear → needs_review, ask the user

### Area vs. Resource
An area involves **active responsibility** (you're accountable for its quality). A resource is **passive knowledge** (interesting but no accountability).

Example: "React Patterns" notes — Resource. "Frontend Engineering" (your job domain) — Area.

### Resource vs. Archive
A resource is something you might actively **use** in the future. Archive is something you're keeping for **historical reference** but wouldn't expect to pull out.

### Ambiguous Cases
When two categories seem equally plausible:
- Set `needs_review: true`
- Set `confidence: low`
- Propose **both** options with reasoning
- Place in Inbox if currently unplaced
- Never force a classification on ambiguous input

---

## Confidence Levels

| Confidence | Meaning | Action |
|---|---|---|
| `high` | 3+ strong signals, no contradictions | May act directly (if in balanced/aggressive mode) |
| `medium` | 2 signals, minor contradictions | Propose + ask for confirmation |
| `low` | 1 signal or conflicting signals | needs_review, Inbox, explain uncertainty |

---

## Common Pitfalls

1. **Don't classify by topic alone** — "AI" can be a Project (build an AI tool), Area (AI team leadership), or Resource (AI learning notes)
2. **Don't archive prematurely** — a note that hasn't been touched in 3 months isn't automatically dead
3. **Don't mistake meeting notes for projects** — a meeting note belongs to whatever project/area the meeting was about
4. **Don't confuse size with type** — a huge document can be a Resource; a one-liner can be a Project
5. **Folder location is a signal, not a verdict** — if a note is in 3_Resources but has clear project indicators, flag it; don't silently accept the wrong placement
