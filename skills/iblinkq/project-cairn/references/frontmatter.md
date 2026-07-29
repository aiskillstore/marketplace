# frontmatter

Defines project-side and knowledge-base-side frontmatter.

## Project topic note — recommended fields

- `type`
- `status`
- `summary`
- `tags`
- `contains`
- `created`
- `updated`
- `contributors` (conditionally present; add when identifiable human contributors exist)
- `graduated_by` (added at graduation time, not pre-stamped)
- `graduated_to` (added at graduation time, not pre-stamped)
- `graduated_at` (added at graduation time, not pre-stamped)
- `graduation_status` (optional; only add after a graduation-readiness judgment)
- `related`
- `authoring_mode`

## Knowledge-base note — required fields

- `type`
- `summary`
- `contains`
- `tags`
- `graduated_from`
- `graduated_by` (required for every new graduation)
- `authoring_mode`

Conditionally present when identifiable human contributors exist:

- `contributors`

`graduated_from` and a non-empty `graduated_by` are required on the knowledge-base side for every new graduation. Project-side `graduated_to` is recommended but not mandatory. Applicability, version/time context, last-verification time, and source backlinks should appear in the note body when they are not promoted to frontmatter. Legacy notes remain valid under the audit policy: backfill `contributors` when a team topic is touched and `graduated_by` when it is re-graduated.

### `graduated_from` shape

`graduated_from` is a **list of `{project, path}` entries**, not a scalar — verified against notes already graduated into the Obsidian knowledge base, several with more than one entry (a note distilled from more than one source topic/file):

```yaml
graduated_from:
  - project: "Project Cairn"
    path: "/absolute/or/vault-relative/source/path.md"
  - project: "Project Cairn"
    path: "/another/source/file.md"
```

Every provider that writes structured frontmatter (as opposed to leaving frontmatter for the caller to hand-embed, e.g. Lark) should use this shape, not a single string. `scripts/obsidian-graduate.sh` builds it from repeatable `--graduated-from "<project>|<path>"` flags.

For `path`, prefer the **source-project-relative** path (e.g. `cairn/<topic>.md`): the `project` field already says which project, and a relative path survives machine moves and repo relocations. Absolute paths appear in older production notes and remain acceptable; new graduations should write project-relative.

### Human provenance shape

Both fields are lists of human-readable names, even when one person is present. Prefer an actually exposed platform display name, but do not require a globally stable identity:

```yaml
contributors:
  - Alice
graduated_by:
  - Alice
```

- `contributors` records the people who substantively participated in forming the knowledge. Do not use it for every attendee, the Markdown typist, ownership, or AI-writing mode.
- `graduated_by` records the human or humans who explicitly confirmed graduation, not the Agent, adapter, or API client that performed the write.
- Do not pre-stamp either field empty. Add `contributors` when identifiable human contributors exist; add `graduated_by` only when graduation occurs.
- On re-graduation, merge the current confirmer into `graduated_by` without duplicating existing identities. `cairn/LOG.md` remains the dated event ledger.
- Resolve names lazily when a provenance field is needed: explicit user input -> actually exposed platform display name -> unambiguous preferred form of address -> just-in-time question. Do not move this into `cairn init`, and do not silently use OS, path, Git, repository-owner, or memory-derived names.

## Enum values

- `type` (OKF-aligned concept-object kind):
  - currently produced: `project_topic` (project side), `knowledge_note` (knowledge-base side).
  - forward-looking, not auto-created by init/maintenance: `reference`, `playbook`, `decision_record`, `log_index`.
- `status`: `active`, `superseded`, `archived`, `needs_review`.
- `contains` (controlled, multi-value): any of `decision`, `experience`, `lesson`, `procedure`, `reference`, `open_question`.
- `graduation_status` (optional): `candidate`, `deferred`, `not_applicable`.

## Field semantics

- `type` answers "what kind of knowledge object is this?" — a single concept-object kind.
- `contains` answers "what kinds of knowledge ingredients are inside?" — multi-value content composition. A single topic note can hold both experience and lessons, so never use `type: experience/lesson`; represent mixed content with `contains`.
- `tags` answers "which topics, domains, projects, or technologies should this be found under?" — open, multi-value retrieval labels; they do not drive rule decisions.
- `graduation_status` records an explicit graduation-readiness judgment when one has been made. Do not pre-stamp `not_reviewed`; absence means no graduation judgment has been recorded. Use `candidate` when the topic appears reusable and ready for confirmation, `deferred` when it may become reusable after more validation or abstraction, and `not_applicable` when the topic has been reviewed and should not graduate as a note. Keep the reason in the body when it matters.
- `authoring_mode`: `ai_generated` | `human_written` | `ai_assisted`. Records how the note was written, to separate AI-generated, human-written, and human-AI notes in the knowledge base. It does not encode trust, review status, or ownership. It is orthogonal to both human-provenance fields, `contributors` and `graduated_by`. Project Cairn auto-generated topic notes default to `ai_generated`.
