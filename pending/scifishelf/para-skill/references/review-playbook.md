# Review Playbook

## Review Rhythms

### Weekly Review (Projects focus)
Check every active project:
- [ ] Has at least one open next step?
- [ ] Deadline/target date still valid?
- [ ] Any project that reached `done` but not yet archived?
- [ ] Inbox notes from the past week — classified?
- [ ] Resources that might now belong to an active project?

### Monthly Review (Areas + Resources focus)
- [ ] Any Area without an update in 30+ days? Flag for attention.
- [ ] Any Area that has become a completed project? Reclassify.
- [ ] Resources that are clearly obsolete or superseded?
- [ ] Duplicate notes or heavily overlapping content?
- [ ] Projects with `done` status for 30+ days → archive candidates

### Quarterly Review (Archive + Structure)
- [ ] Archive folder: any notes that shouldn't be there?
- [ ] Folder structure still matching PARA intent?
- [ ] Frontmatter consistency across all notes?
- [ ] Review rules or path config that need updating?
- [ ] Dead areas (no notes for 90+ days)?

---

## Review Report Format

Always structure review output as follows:

```markdown
# PARA Review Bericht — [date]

## Inbox
- [N] Einträge ohne Klassifikation
- [list of unclassified notes]

## Projekte
- [N] Projekte ohne nächsten Schritt
- [N] Projekte mit möglichem Abschluss (status: done or no activity > 14 days)
- [list if any]

## Bereiche (Areas)
- [N] Bereiche ohne Update seit > 30 Tagen
- [list if any]

## Ressourcen
- [N] Ressourcen mit möglichem Projektbezug
- [N] Veraltete oder möglicherweise obsolete Ressourcen
- [list if any]

## Archiv
- [N] Archivierungskandidaten (projects with status:done)
- Keine Auffälligkeiten / [issues if any]

## Offene Entscheidungen (needs_review)
- [N] Notizen mit needs_review: true
- [list with brief reasoning]

## Empfehlungen
1. [Highest priority action]
2. [Second priority]
3. [etc.]
```

---

## Hygiene Checks

### Finding Projects Without Next Steps
Look for notes in `1_Projects/` where:
- No `- [ ]` checkbox exists in the body
- No "nächste Schritte", "next steps", "TODO", "action" section
- `status` is `active` but no tasks visible

### Finding Stale Areas
Areas in `2_Areas/` where:
- Last modified date > 30 days ago (for weekly-reviewed areas)
- Last modified date > 90 days ago (for any area)
- No `review_date` set

### Finding Archive Candidates
Notes where ANY of these are true:
- `status: done` for 30+ days
- Explicit "abgeschlossen", "erledigt" in content or title
- `para_type: archive` but not yet in `4_Archives/` folder
- Project with past deadline and no open tasks

### Finding Inbox Backlog
Notes in `0_Inbox/` (or root of vault) where:
- No `para_type` in frontmatter
- `needs_review: true`
- Creation date > 7 days ago without classification

### Finding Orphaned Content
Notes where:
- Not linked from any other note
- No tags
- No `area` or `project` frontmatter reference
- Located in root or unclear subfolder

---

## Archiving Criteria

Archive a note only when ALL of these apply (or user explicitly asks):
1. The content is clearly completed, historical, or inactive
2. Confidence is `high`
3. The note is NOT currently linked from active notes (or links will be preserved)
4. Either the user confirmed, or the mode is `balanced`/`aggressive` and evidence is overwhelming

### Archiving Procedure
1. Verify no active wikilinks point to the note (or accept that they'll still work after move in Obsidian)
2. Update frontmatter: `archived: true`, `archive_date: [today]`, `status: archived`
3. Move to `4_Archives/[year]/[original-name].md`
4. Log the action in `PARA-Changelog.md`
5. Default: show dry-run first and ask for confirmation

### Never Archive
- Notes with `needs_review: true` (resolve the review first)
- Notes linked from active projects without checking
- Notes the user is currently editing or viewing
- Notes with `status: on-hold` (that's a pause, not completion)
