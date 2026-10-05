# Feature Roadmap Discovery

Use this reference to decide whether Step 3 may begin. The gate protects the audit from comparing code with an invented target.

## Search sequence

1. List documentation before searching content:

   ```bash
   rg --files docs
   ```

2. Search the exact feature name and repository-observed aliases in Markdown, MDX, YAML, and JSON documentation.
3. Search likely target-language terms: `roadmap`, `plan`, `milestone`, `phase`, `acceptance`, `definition of done`, `migration`, `cutover`, and `rollout`.
4. Follow direct links from matching `docs/` pages to adjacent repository documentation. Do not treat a ticket or external URL as read unless its contents are actually available.
5. Record every candidate path, why it matches, and whether it contains actionable target items.

Escape user-provided search text or use fixed-string search. Do not interpolate untrusted feature text into a shell expression.

## Clear-roadmap test

A repository document passes the gate only when the answer to all applicable questions is yes:

- Does it identify the requested feature or an evidence-backed alias?
- Does it define concrete outcomes, phases, deliverables, acceptance conditions, or migration targets?
- Can at least one target item be compared with observable repository or runtime evidence?
- Is it authoritative enough to distinguish a requirement from an idea, example, historical note, or rejected proposal?
- When multiple documents conflict, is the active one identifiable by status, revision, repository instruction, or explicit user decision?

Issue checklists and ADRs may supplement a roadmap. They do not replace the `docs/` gate unless the user explicitly supplies or designates them as the roadmap.

## Hard-stop response

When the gate fails, do not classify implementation state. Return:

```markdown
Roadmap required for `<feature>` before the audit can continue.

- Target revision: `<branch>@<sha>`
- Searched: `<paths>`
- Terms: `<feature name, aliases, roadmap terms>`
- Candidates found: `<none or paths with rejection reason>`
- Needed from you: a roadmap file/path or the roadmap contents
```

Do not create a roadmap from the code. Current implementation cannot define its own expected completeness.

## User-provided roadmap

If the user supplies roadmap text or points to a readable non-`docs/` artifact after the hard stop:

1. Label the source and revision as user-provided.
2. Confirm the feature identity and target branch still match.
3. Extract concrete items without adding requirements.
4. Resume at the traceability matrix.

If the supplied text is still aspirational or ambiguous, ask only for the missing acceptance boundary; do not guess.
