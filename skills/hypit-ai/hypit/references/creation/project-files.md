# Project files

Read this when starting, resuming, or reorganizing a video project. The layout below is a working
convention, not syntax: Hypit resolves ordinary paths and does not assign meaning to these directory
names.

## Establish the project boundary

Understand the current request and keep its intended result in [Brief](brief.md). Supplied paths,
the selected production's notes and their explicit references establish which work belongs here.
A request to continue or revise a named production carries that work forward. A new adaptation
starts from the supplied reference and requested changes, with its own target and working files.
When the target is clear, choose a suitable project location and tell the user where the work lives.
Clarify the intended target when the request leaves genuinely different productions possible.

The current shell directory may be the Skill or executable installation rather than a video project.
Keep discovery tied to the question being answered:

| What is needed | Where the useful evidence lives |
| --- | --- |
| An executable or prepared local service | `hypit paths`, package-manager records, the selected Profile and Provider-documented tool locations |
| Surface syntax or reusable behavior | Installed vocabulary, the owning package's documentation and a relevant component example |
| This production's inputs and completed work | Supplied files, its notes, Sources, Runs and project Result history, including explicitly linked shared assets |

Follow a path beyond the project when a supplied location, recorded dependency or documented tool
location explains its purpose. A nearby project with a similar name or subject does not establish
that connection. If the expected input is missing, report the missing item and resolve its location
or prepare the new material the commission needs. This keeps discovery useful without turning
the machine's other productions into an implicit asset library.

Judge connected earlier work by its contribution: a reference, reusable behavior, or material that
fits the intended person, product, words and presentation. Learning a component from an example
carries its mechanics into the new work; casting, prompts, assets and accounts remain this
production's choices. Explain useful reuse alongside what the requested changes require. Finding
a similar finished video answers an availability question, not whether this commission is complete.
A proposal to substitute a different existing video belongs in the conversation with the user.

Run commands from the video project's root. A small `package.json` makes that root explicit and
can later hold the project's component dependencies:

```json
{
  "name": "workshop-video",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "hypit": { "project": true }
}
```

The CLI searches upward for a `package.json` whose `hypit.project` field is `true`. It does not turn
the nearest component package or an arbitrary working directory into a project. Passing a Source or
Runtime path does not select a different project.
Sources can live below the root, with file and Source imports relative to the declaring file.

| Boundary | When to set it explicitly |
| --- | --- |
| `--project <directory>` | Choose the project root for Sources, Runtime selection, project packages and Results when running from another directory |
| `--asset-root <directory>` | Admit assets stored elsewhere while keeping Source imports in their workspace |
| `--package-root <directory>` | Resolve project packages from another installation location |

Relative command-line paths start at the shell's current directory. `--project` selects the project
without rebasing the Run, Source or `--runtime` argument. For example, from outside a project:

```bash
hypit paths --project /path/to/video-project
hypit studio --run /path/to/video-project/build.svrun --project /path/to/video-project
```

`paths` shows the resolved project and where its Runtime selection came from. Source imports and asset
references inside files remain relative to their declaring file.

For example, `hypit check authors/main.svml --asset-root /path/to/shared-media` admits intentionally
referenced shared media. Keep the same relevant boundaries for subsequent commands. An ordinary
project uses its own package installation. Embedded Core comes from the selected Distribution;
product-selected default packages are ordinary dependencies installed with it. Independently
distributed project packages, including `@hypit/*` packages, remain ordinary project dependencies.
[Distribution](../environment/distribution.md) explains locating that executable,
and [component vocabulary](../production/vocabulary.md#let-ordinary-package-management-own-distribution)
explains installing project packages.

## Keep reference truth and target truth separate

A reference archive says what an existing piece does. A production says what the new piece should do
and contains the files that make it. One reference can inform several productions, and one production
can draw from several references; ordinary relative links express those relationships without a
central project index.

```text
project/
├── references/
│   └── <reference>/
│       ├── source.*
│       ├── ANALYSIS.md
│       ├── TIMELINE.md
│       ├── transcript.json
│       ├── evidence/
│       ├── PROGRESS.md          # only while understanding is in progress
│       └── drafts/              # optional observation experiments
├── productions/
│   └── <target>/
│       ├── BRIEF.md
│       ├── TREATMENT.md
│       ├── PROGRESS.md
│       ├── authors/
│       ├── recipes/
│       ├── runs/
│       ├── assets/
│       └── drafts/
├── assets/                      # inputs shared by several targets
├── packages/                    # project Author Packages shared by targets
├── hypit.runtime.json
└── package.json
```

A target may have several Author Sources, Recipe Sources, and Runs. Re-running one Run creates another
Build, not another target. Keep files for one target together so their relationship is readable from
the filesystem rather than inferred from matching names elsewhere in the project.

For example, one understood reference can support two distinct target works without being copied:

```text
references/viral-ad/
productions/product-version/
productions/short-version/
```

Each production links to `../../references/viral-ad/` from its own Brief or Treatment and keeps its own
Sources and Runs.

The CLI finds the project from the command's working directory as described above; Source and Run files may live in any
subdirectory inside it. Shared assets and packages can stay at project root. Target-specific assets
stay with that target. A reference file that is also intentionally used in the new film can be
referenced in place; its documentary role does not require a duplicate.

## Give each document one job

- `ANALYSIS.md` is the current whole-piece understanding of a reference: form, story, recurring
  systems, relationships, function, and why the work holds together.
- `TIMELINE.md` connects what happens when with what it does for the viewer. Preserve the content,
  placement, entry, changes, persistence and exit of the reference's visual systems, their word or
  action relationships, source times and useful evidence paths. Concurrent picture, speech, Caption,
  Typography, MG, Effect and Audio behavior belong to the same connected account. These are reference
  timeline notes; the target's actual placements belong to the `time:Timeline` declaration in Source.
- `transcript.json` is word-level speech evidence. It is evidence, not the director's interpretation.
- `evidence/` contains only media worth reopening, with ordinary human-readable names.
- `BRIEF.md` preserves the user's goal, facts, constraints, requested changes and
  [agreed paid scope](brief.md#brief-preserves-user-authority).
- `TREATMENT.md` is the director's current answer to the Brief: the intended new piece in complete
  creative terms, before implementation details.
- `authors/`, `recipes/`, and `runs/` are the exact production implementation.
- `PROGRESS.md` is a short photograph of the work now: the live question, what remains to examine or
  make, next useful action, real blockers, active Build ids and reusable Results. Keep cost information
  relevant to the remaining work here when it affects the agreed budget. When handing work
  over, retain the relevant Run and Runtime Profile, exact Build id and public Output names needed
  to continue. Run Candidates own
  the actual reuse choices; the note points to them. Established conclusions belong in their owning
  document instead.

Rewrite these files when the current truth changes. They are not logs. `PROGRESS.md` may exist beside
a reference or a production because either kind of work can span conversations; it does not mark a
stage and can disappear when there is nothing useful to hand over.

Use these files as the working memory across conversations. Write discoveries and decisions into
their owning documents as the work develops, preserving both the explanation and its concrete
details. Let provisional accounts grow with the understanding, keeping detailed evidence once and
linking to its owner. Share the meaning of discoveries in conversation while the files retain the
full account. Resume by reading the current project files and relevant Skill pages; use Progress to find
the next question and the saved evidence, Sources, Runs or Results to continue it. A new discovery
updates the account it changes so the next session inherits the improved understanding.

## Drafts and Results are different things

`drafts/` holds unpublished authoring material that is not part of the current Source: trial copy,
temporary designs, or media deliberately exported for further work. A Build output remains in that
Build's Result even if a later Run does not use it. The absence of a later reference already says it
was not adopted; it does not need to be copied into `drafts/`.

When an output is deliberately exported into the project, place it according to its new role. It may
become an `asset`, a `draft`, or direct input to another production.

## Hand over an editable production

A finished MP4 is a viewing deliverable. To continue making the piece, the recipient also needs the
authored work and the produced values that its Runs select:

- Sources, Recipes, Runs, project notes and referenced input assets, keeping their relative layout;
- project component source or installed-release dependencies, `package.json`, its lockfile and any
  tarballs referenced by `file:` dependencies;
- the completed Results used by `build-record` Candidates, including their media and Composite value
  documents;
- the intended Runtime configuration, with account access configured on the receiving machine through
  its own Credential Store.

For the default filesystem repository, preserving `.hypit/results/` intact with the project is the
straightforward handoff. Include the hidden directory and keep its date/Build subdirectories. Some
Results forward an Output to its original owning Build, so copying only the latest Build directory
can omit media still in use. Archive or migrate completed Results explicitly when they should live
outside the project.

External input files remain live dependencies, including when referenced inside structured Outputs.
The Node workspace records their resolved file addresses. When moving to another machine, provide
those inputs and update affected references to their new locations. Copying Result directories alone
does not collect external files; an explicit `hypit get` export does collect the selected Output's
referenced bytes.

The recipient installs the selected Distribution and project dependencies, configures their Runtime,
and inspects the received Results. Planning the intended Run shows whether its reuse choices still
resolve and what new work remains. Active execution stays with the originating Runtime until that
attempt ends; an editable handoff carries authored work and required Results rather than the originating
Runtime's execution state.

`hypit get` is useful when handing over a particular output. Exported image/video/audio files can be
selected as file Candidates. A Composite export contains `value.json` and its resource files for
inspection and transport; that document uses the Result value format, whereas a Run `<value>` accepts
a StoredValue wrapper. To retain structured normalized media, local-domain or alignment reuse, keep
its Result available and select each required Output with `build-record`. [Builds and Results](../production/builds.md)
explains Result reuse and export.

## Resume from present facts

After interruption or context compaction, read the current Brief, Treatment, reference archive,
Source, Recipe, Run, and the short `PROGRESS.md` that applies. Then inspect the project's actual Build
Results and Runtime status. Continue from usable outputs already present; loss of conversation context
is not a reason to submit the same paid work again.

A command interruption or missing reply can leave the Worker running. [Builds](../production/builds.md)
explains how to identify active work and continue through a new Run after a failed attempt.
Completed Outputs remain in Results without being exported as files. Keep or add their Run Candidates
when revising downstream work; neither the notes nor an unchanged output name selects them automatically.

## Keep review notes with the work

Studio's `FEEDBACK.json` belongs to the workspace and records timestamped comments for its Runs.
[Working from Comments](../production/studio.md#revise-from-timestamped-comments) explains reading,
resolving and preserving these shared notes. Carry settled creative choices into Treatment and
execution progress into Progress; retain comments as the review conversation.
