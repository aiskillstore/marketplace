# Stage 2: Express the change

[中文](show-changes.zh.md)

Preparing the plan requires a user-requested task and the usable map from [Stage 1](map-project.md). Implementation additionally requires confirmation of the displayed plan, as defined in [SKILL.md](../SKILL.md).
Read [contract.md](contract.md), `schemas/activity.schema.json` and the example stream.
Use exact project/map/revision/module IDs; resolve stale coverage before emitting events. Never substitute a fictional map or infer IDs from prose.

## Record operations

Before editing, follow [development.md](development.md) for the relevant task types. Include the intended observable behavior and verification method in the `planned` reason; use existing `checks` for executed results and `constraintReviews` for applicable recorded constraints. Do not add new event fields.

1. Before editing: append `planned` with complete `scope`, current `targets`, project-relative `files` and a short module-based reason. Render and deliver the plan, ask for confirmation, and wait. Do not treat the original coding request as approval of an unseen plan. Reuse confirmation already given for this same plan; honor an explicit task-specific waiver.
2. After confirmation, before each edit group: append `editing` with concrete paths and only current modules as targets.
3. Before checks: append `verifying`; test/fixture paths do not automatically count as modified files.
4. At task end: append `completed`, `failed` or `cancelled`, recording actual commands, exit codes and observations in `checks` where applicable.

Every JSONL event carries complete scope/targets. Explain scope expansion in a new `planned` event, update the preview and confirm the changed scope before editing added modules. For mapped edits, target all matching file owners; list unowned files in both `files` and `unmappedFiles`. Never invent ownership to pass validation; correct misleading rules in Stage 1.

One active task per session; sequences start at 1 and stay contiguous. After a terminal event use a new task ID, never reopen one. Keep project and map revision fixed; new revisions require a new session/file. These are agent declarations: keep checks pending until executed, and never infer success from event emission or completion.

## Render and deliver

```sh
node <skill-root>/scripts/render.mjs <map.json> <activity.html> <activity.jsonl>
```

The renderer validates the full stream before replacing output. Deliver only after success; follow Stage 1's preview checks.

- Real activity opens at the latest record; simulation at the first plan. History and collapsible files/checks describe the selected step, not cumulative Git changes.
- Architecture/changes/comparison share positions; comparison links selection, zoom and scrolling and stacks on narrow screens.
- Scope stays outlined; non-targets dim. Planned targets highlight before edits, verification targets are labelled separately, and terminal events remove target glow. No executed checks means unverified.
- Use `--simulation` only for fictional records such as `examples/harness.activity.jsonl`, never as observed work.
- For each supported activity language, supply event `translations[locale].reason` and check `translations[locale].summary`; absent translations fall back to originals.
- Updates need regeneration and refresh. No upload, auto-refresh, live interception or Git verification exists; a future display receipt would confirm rendering, not approval or correctness.
