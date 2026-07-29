# graduation

Human-confirmed promotion of validated project knowledge into an external knowledge base. One-directional: project → knowledge base. The Skill must not silently graduate knowledge.

## Candidate criteria

A graduation candidate must be:

- Verified in the project, not just guessed.
- Reusable outside the current project.
- Abstracted from local implementation details.
- Not an engineering asset itself (assets never graduate; only knowledge about them does).
- Safe to move into the target knowledge base.
- Traceable with `graduated_from`.

## Deferred provider (connect at first graduation)

`graduation.provider: none` in `.cairn/config.yaml` means the project deliberately deferred connecting a knowledge base at init (see `init.md` → Deferred graduation provider). Candidate detection and human confirmation (Flow steps 1–3) work unchanged — only the provider write is blocked. When a confirmed candidate is ready to graduate:

1. Collect the provider decisions now — init decisions #3–#4, with cascading defaults applying as usual (a user-level `~/.config/cairn/config.yaml` offers one-key reuse).
2. Run the chosen provider's preflight (`init.md` → Tool-backed provider preflight) until it reports `ok`.
3. Freeze the result into `.cairn/config.yaml`, replacing the `provider: none` marker with the standard single- or multi-provider form.
4. Update `AGENTS.md`: restore the deferred renderings (the three `Init configuration` lines, the consumption-reflex bullet, the distillation bullet) to the standard connected form per `init.md`.
5. Continue the normal Flow below; fold "connected provider X" into the graduation's own `cairn/LOG.md` entry (or give the connection its own entry if the graduation is then aborted).

If the user still declines to connect a provider, stop — graduation cannot proceed without one. The candidate stays recorded (optionally `graduation_status: candidate`) and audit keeps surfacing it.

## Flow

1. Propose candidates (the Skill may detect them; audit is the backstop).
2. The user confirms before anything is written or prepared.
3. If a project topic has been explicitly judged, optionally record `graduation_status` on the project topic note: `candidate`, `deferred`, or `not_applicable`. Do not add this field to every topic by default.
4. After human confirmation and before the provider write:
   1. Resolve the confirmer identity per `frontmatter.md` and pass it as `graduated_by` on both the project and knowledge-base sides.
   2. Merge and de-duplicate `contributors` from all source topics when graduating from multiple sources.
   3. Re-check any Origin quote against the target audience. Carry a safe quote into the knowledge-base note's **Background**; if risk is found, sanitize both copies consistently or omit it from both.
   4. Treat quote absence as valid and never create a placeholder section.
5. Prepare the knowledge-base note with required frontmatter (`graduated_from` and non-empty `graduated_by` mandatory; see `frontmatter.md`), and record `graduated_by` on the project topic note. Optionally record `graduated_to` / `graduated_at` there as well. When choosing `tags`, check the provider's existing tag inventory first (Obsidian: `obsidian tags counts`) and prefer reusing an existing tag over coining a near-synonym — consumption-time tag-query recall depends on this discipline (see `provider-interface.md` → Read side).
6. Record the graduation itself as one `cairn/LOG.md` entry — summary plus a pointer to the knowledge-base note — the same way an audit run logs itself (see `audit.md` → Behavior).

## Note body structure

The knowledge-base note body must open with **Background**, then **Conclusion**, in that order. Sections after those two are not fixed — shape them to what the knowledge itself needs:

1. **Background** (required, first) — the situation the knowledge arose from: what problem it was solving, how it was discovered or encountered, why it was needed. Readers need the origin to judge whether the note applies to their case.
2. **Conclusion** (required, second) — the core claim or solution itself.
3. **Further sections** (as needed, follow the knowledge) — evidence (reasoning, verified cases, comparisons, counter-examples) when the claim needs backing; a practice guide (procedures, safe patterns, decision tests) when the knowledge is operational; applicability, boundaries, or when-not-to-apply where useful.

Do not open the body with the conclusion. Quick scanning is served by the frontmatter `summary` (a one-line conclusion), so the body does not need to lead with it. Chinese names for common headings are fixed in `zh-glossary.md`.

When a safe short direct excerpt materially restores the scene, place it inside **Background** in this portable Markdown form:

```markdown
### Origin quote

> "Exact excerpt."
>
> — identity, YYYY-MM-DD, short context
```

Preserve direct wording and apply the redaction/scene-summary rules in `maintenance.md`. The subsection is optional; never add an empty heading or placeholder when no suitable quote exists.

## Re-graduation (updating an already-graduated topic)

A project topic note is not frozen once it has graduated — it stays the project's local current truth and can keep being updated in place as the project progresses. "One-directional" means the knowledge-base note is never silently overwritten by a project-side edit, not that the project-side source can no longer change.

When a topic that already has `graduated_to` gains a substantive new development (a real update, not a typo fix), propose re-graduating: run the same graduation flow again in the adapter's explicit update mode, targeting the same knowledge-base note (same provider adapter and stored identifier), update `graduated_at` to the new date, and union the current confirmer into `graduated_by` on both sides without duplicating an existing identity. Resolve that union before invoking the low-level adapter; the adapter writes the supplied current truth and does not infer prior identities. Keep the event/time/target and confirmer association in `cairn/LOG.md`; frontmatter remains a de-duplicated identity list rather than an event history. This is a normal repeat of the one-directional `graduate` action, not a new synchronization mechanism — the user still confirms before anything is written, same as a first-time graduation. Until a re-graduation happens, the knowledge-base note remains the cross-project current truth but may be behind the project's latest local state; `cairn audit` flags this (see `audit.md`).

## Provider adapter constraints

Every adapter script must satisfy `references/provider-interface.md`. Cross-provider transport and API-surface principles live there; each provider reference below adds that provider's consequences.

Write mechanics differ per provider; keep them in each provider's `.cairn/config.yaml` entry, not hardcoded in the flow.

Provider mechanics live in one reference per provider. Before any write, read that reference, run its Step 0 preflight, and proceed only on `status: ok`.

| Provider type | Required provider reference | Required Step 0 preflight | Write adapter |
|---|---|---|---|
| `obsidian` | [`graduation/obsidian.md`](graduation/obsidian.md) | `scripts/obsidian-preflight.sh` | `scripts/obsidian-graduate.sh` |
| `lark-wiki` | [`graduation/lark-wiki.md`](graduation/lark-wiki.md) | `scripts/lark-preflight.sh` | `scripts/lark-wiki-graduate.sh` |
| `notion` | [`graduation/notion.md`](graduation/notion.md) | `scripts/notion-preflight.sh` | `scripts/notion-graduate.sh` |

The write-adapter column pins each provider's primary single-note entry; the provider reference enumerates that provider's complete script set. If the configured provider is `none`, stay in the Deferred provider flow above until one is chosen. If the provider value is unsupported, its reference is missing or unread, or the named preflight has not returned `ok`, stop before any provider-side write and report the error. An absent preflight result is a blocking state, not permission to reconstruct provider mechanics from memory; a dry-run does not substitute for this gate before a later real write.

### Lark / Feishu wiki adapter (worked example)

Moved to [`graduation/lark-wiki.md`](graduation/lark-wiki.md).

### Notion adapter (worked example)

Moved to [`graduation/notion.md`](graduation/notion.md).

### Obsidian adapter (worked example)

Moved to [`graduation/obsidian.md`](graduation/obsidian.md).

## Knowledge-base links

When the target provider supports wiki-style links, add links only when they are useful in context. Do not add a generic "Related" list just to connect notes.

- Add a wiki link when a specific sentence or paragraph depends on, explains, contrasts with, or operationalizes another knowledge note.
- Put the link inside that local context, with surrounding text that makes the reason for the connection clear.
- Do not link merely because two notes share a tag, came from the same project, or were graduated in the same batch.

After graduation the knowledge-base note is the cross-project current truth for that topic and is not rewritten back from the project. The project topic note remains the current truth within this project's local context (and a historical record of how the knowledge was reached); the two layers do not compete.
