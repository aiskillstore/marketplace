---
name: inkos
description: Use InkOS as a Pi-agent creative harness for novels, short fiction, scripts, storyboards, interactive films, open worlds, derivative works, and long-document translation.
---

# InkOS Creative Harness

InkOS is a text-creation harness. The main Pi agent understands the request, activates professional Skills, invokes typed capability actions, and reports only persisted results.

## Core contract

- Discussion stays discussion. Creation and mutation happen only through capability actions.
- A successful action is proven by its `ActionResult` and artifact revision, never by assistant prose.
- User intent, current Work constraints, established facts, and explicit prohibitions outrank model defaults.
- Skills provide professional methods but never grant write permission.
- Review returns evidence-backed observations. It does not score prose, reject a chapter, or authorize an automatic rewrite.
- Revision is an explicit action. Preserve source revisions and report the new artifact revision.
- Context is assembled per task: LLM semantic selection chooses relevant source sections after deterministic candidate discovery. Protected intent and selected current facts are never compressed; lower-priority context is semantically compiled only on budget overflow.

## Creation profiles

- `longform-novel`: foundation, chapter planning, writing, review, revision, state projection, forecast, cover.
- `short-fiction`: complete short story, plan, review notes, sales package, cover.
- `script`: screenplay, vertical short drama, audio drama, interactive script.
- `storyboard`: editable storyboard, typed image-prompt assets, image generation.
- `interactive-film`: story tree, flags, script, storyboard, image assets, playable graph, export.
- `play-world`: open-world or guided interaction with persistent entities, relationships, time, evidence, inventory, scenes, and images.
- `fanfic`, `spinoff`, `imitation`, `continuation`: derivative creation with explicit lineage and source canon.
- `translation`: multilingual long-document translation with terminology and resumable artifacts.

## Natural-language use

Use normal conversation to discuss or request work. The agent chooses the relevant profile and Skill. A creation proposal may require confirmation; recoverable edits inside the current Work can run directly.

Force a Skill when needed:

```text
@inkos-story-review review chapter 8 against the current reader promise
@inkos-imitation-writing keep the reference cadence but create a new story
```

Inspect available Skills and Works through the agent tools rather than guessing storage paths.

## Explicit CLI actions

```bash
inkos studio
inkos tui
inkos book create --title "My Story" --genre other --lang en
inkos write next <book-id> --count 3
inkos revise <book-id> <chapter> --mode rewrite
inkos review <book-id>
inkos short run --title "A Short Story"
inkos fanfic init --title "Derived Story" --from source.txt --mode canon
inkos export <book-id> --format epub
```

Internal planning, semantic context selection, writing, state projection, and review are one Harness trajectory. `review` displays persisted qualitative observations.

## Revision modes

- `spot-fix`: exact local text patches applied by the host.
- `polish`: prose-surface changes only.
- `rewrite`: rewrite the affected passage or chapter while preserving authority.
- `rework`: restructure scenes when the user explicitly requests structural change.
- `anti-detect`: explicit prose cleanup using the activated de-slop Skill.

## Context and persistence

- Human-readable story assets remain Markdown.
- Host-consumed state and action results use typed JSON/tool schemas.
- Planner, writer, reviewer, reviser, settler, Play, translation, and production-document compilers submit typed results through Pi tools.
- Conversation compaction and story-context compaction are separate. Both preserve protected current intent and use semantic compilation only after budget overflow.
- Work manifests, artifact revisions, episode events, and model-call traces provide observable lineage.

## Failure handling

- Model/provider failures remain operational errors; they are never converted into fictional world outcomes or content verdicts.
- A failed optional asset is reported as an observation without invalidating a successfully persisted manuscript.
- Interrupted actions preserve the last committed artifact and can be retried from persisted state.
- Never claim a file was created or changed without an artifact reference from the action result.
