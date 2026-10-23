# Work in Studio

Read this when opening a Run, choosing its interface language, using its timeline and Inspector, or giving a project component a
useful Studio presentation. For component implementation, read [Companion authoring](studio-companions.md).
[Review](review.md) owns the judgment made from the visible work;
[Track authoring](track-authoring.md) owns the component's production behavior.

## Open the actual Run

From the video project, use the installed Distribution's command:

```bash
hypit studio --run build.svrun
```

Supply `--runtime <profile>` when intentionally using a different Profile from the project's
`hypit runtime use` selection. Studio needs a Run whose selected targets reach one Film with resolved
composition and time. The Timeline supplies the work's clock and extent; optional projections
provide domain evidence such as Script anchors. Pure animation uses the same editor. An image-generation-only Run is not a Film view; several distinct
Films need separate Runs or sessions.

Open the URL actually printed by the process and retain it with the Run it serves. For review, open
that URL with `#comments` appended, such as `http://localhost:5179/#comments`; this selects the
Comments view directly. The printed port is authoritative. The default
requested port is 5179; `--port` selects another, and an occupied port can cause Vite to choose a
different one. Reuse an existing session when it serves the intended project and Run.

The startup output identifies the project, absolute Run path, Runtime Profile and selection source.
An explicit `--runtime` applies to this session; the project's default comes from `.hypit/runtime`.
When launching from another directory, use `--project` to select the project and supply the Run
path from the current directory, as shown in [project boundaries](../creation/project-files.md#establish-the-project-boundary).

Studio watches the Run and its loaded Author/Recipe Sources and recompiles them after changes.
Changing package code, adding a package import, changing Companion activation, or selecting another
Runtime or Result repository requires restarting that Studio session: those implementations and
selections are loaded at startup. A browser refresh alone does not reload the server-side modules.
Stop only the relevant Studio process; stopping Studio does not cancel a submitted Build.

## Choose the interface language

The globe menu to the left of **Studio / Comments** changes the interface language. English and
Simplified Chinese are included. The first visit follows browser language preferences; later visits
remember the user's choice. Switching preserves the playhead, selection and comment draft. When
introducing the review, point out this menu if it helps the user work in their preferred language.
This choice affects Studio's interface, not the video's Script, captions or user comments;
component-owned names and Companion labels retain their authored text.

Additional languages are ordinary JSON data, loaded explicitly when opening Studio:

```bash
hypit studio --check-locale ./studio-ja.json
hypit studio --run build.svrun --locale-pack ./studio-ja.json
```

For a new translation, copy `locales/en.json` from the installed `@hypit/studio` package.
Set `locale`, the native language `name`, and `direction` (`ltr` or `rtl`); translate `messages`
while keeping their IDs and named variables such as `{count}`. Missing entries use English.
The check command reports missing entries, unknown IDs and invalid variables without opening a Run.
Relative file paths start at the command's working directory. Repeat `--locale-pack` for several
languages, or pass an installed package's JSON export instead, such as
`--locale-pack @your-scope/studio-ja/locale.json`. A local file is enough; sharing it as a package
is optional. Restart Studio to load changed language files. The installed
`@hypit/studio` package's `LOCALIZATION.md` covers plural forms and JSON package exports.

## Discuss the work while composing

When the user is collaborating locally, open the actual composition once a meaningful passage is
available and keep its Studio URL connected to the current Run. Point to the passage, object or
transition being discussed so the user can give concrete direction. Continue through settled choices;
showing progress need not become an approval stop. Use the prepared production media and explain
which passages are already composed. A rendered frame or clip remains useful when it answers the
current question more directly.

Check that the objects being discussed are recognizable and that their useful author choices are
available. A successful preview establishes that the picture renders; the component's Companion
establishes what the user can select and revise. [Companion authoring](studio-companions.md) explains
this view of the same Source, including generic fallback and project-defined families.

## Revise from timestamped Comments

Open Comments directly when the user wants to point at a moment and describe a change.
It gives the same composition a larger player and a comment column. A change of visual style,
choreography or graphic structure often needs authored code or direction, while a position or color
may fit an Inspector field. Both are ordinary collaboration: Comments carries the desired result,
and the Agent chooses the owning Source, Recipe, component or material decision to change.

Comments live in `FEEDBACK.json` at the project workspace root. Read the entries for the reviewed Run
and the open notes before revising. Each entry has a stable `id`, workspace-relative `run`, `at` in
seconds, `text`, and optional `resolved` (false when omitted). For example:

```json
{"comments":[{"id":"opening-title","run":"runs/render.svrun","at":1.5,
"text":"Give the title a softer pink and a stronger offset shadow.","resolved":false}]}
```

The UI displays notes in time order; its `#` labels follow submission order within that Run. Identify
file edits by `id` and preserve the array order and unrelated entries. Clicking a note seeks to its
saved time. Interpret that time with its words and the reviewed composition: changing Script or media
placement can move the intended event. Comments retain the reviewed seconds rather than silently
following new semantic timing.

Explain the changes you will make, apply them to their owning facts, and inspect the affected passage
and handoffs. Mark the addressed notes `resolved: true`; a note can be reopened with false. Both the
user and Agent can edit this file, and Studio observes saved changes. Read the current file before
writing so newly added comments survive. Retain useful directing decisions in Treatment or Progress;
comments remain the concrete review conversation.

Send saves a comment. Agent notification is not connected yet; when the user asks for another review
pass, read the latest file. [Composition review](review.md) explains the judgment, and
[project files](../creation/project-files.md) owns the production's durable memory.

## Review before export

For visual inspection, use [snapshot](snapshots.md) on this session first. It reads the current
compiled `HtmlProgram` and selected resources, captures exact original frames, and writes PNGs with
optional grids. Studio remains the interactive view for playback, sound and editing.


When the composition is substantially ready and the user can access it, open the current Run at
`#comments` for discussion and introduce Comments and Studio together. Comments lets the user
pause and leave direction at a time; Studio shows the timeline, component relationships and exposed
parameters they can adjust. Both views stay with the same work and playhead. Browser playback does not render an MP4,
create an export Build or save frame sequences. It can therefore show real material and animation
while avoiding a full encode for changes the user is still choosing. Use Studio's other view for
Inspector or timeline edits, and an encoded frame or clip when that evidence is needed.

Introduce the review in the user's language: explain what is ready, invite timestamped comments,
and say whether export is waiting for their review or already covered by their request. For example:
“I've opened the editable video. You can pause and leave timestamped notes in Comments, or switch
to Studio to explore the timeline and adjust available parameters. When you're happy with it,
I can export the video.” This is a collaboration choice, not a mandatory
approval stage. A user who has asked for final export has already chosen that step.

A first-time reviewer may benefit from one short welcome note at the relevant time, saved with
`resolved: true`. Write it explicitly as the Agent's invitation, such as “You can pause here and
leave a note about anything you'd like changed.” It demonstrates the file workflow without adding
an unfinished production task or pretending that the user requested a change. Keep this optional
and specific to the collaboration; existing comments need no repeated welcome.

Once export is wanted, reuse the accepted material in a Build, retrieve its completed video and
check that encoded deliverable. [Rendering](rendering.md) and [Builds](builds.md) own that execution.
Comments is a review view of the editable work; the exported file is the deliverable.

## Show the finished work

Alongside the delivered video, a brief look at its editable production can make the handoff more
tangible. When Studio is readily accessible to the user, open the finished work and share the session
URL. Use a Run that reuses the completed normalized media, local domains and alignment evidence while keeping its Tracks and Recipes
available for editing. Reuse a suitable existing session or launch one as described above.

Point out something specific to this piece: a reveal tied to a word, the Caption styling, or a
component parameter they can adjust. Let the actual work demonstrate the editing experience. For a
remote user, a readily available screenshot or short recording can provide the same introduction.
[Project handoff](../creation/project-files.md#hand-over-an-editable-production) explains what to
include when the user wants to continue editing on another machine.

## Read the different views

| View | What it shows and what it can change |
| --- | --- |
| Source | The exact Run, Author and imported Source/Recipe files. Select a file and use Edit source; changes save automatically, and Cmd/Ctrl+S saves immediately. Check save/error state. This is not a project filesystem browser. |
| Preview | The selected Film composition evaluated from its compiled `HtmlProgram` in the browser. Play or seek with the transport or timeline. Selecting a component-declared visual part selects its corresponding timeline Item; adjust its exposed position in the Inspector. |
| Timeline | Projected domain evidence, resolved named Instants, plus component-projected Track Items and their visible intervals, materials or event lanes. A rectangle may describe occupancy, activation or persistent visibility; read the component's meaning. |
| Inspector | With nothing selected, project, Canvas, time and Run facts. For a selected Item, its declared read-only facts and adjustable fields, organized under Where, When and How where applicable. |
| Tasks | One card per Build, grouped into ongoing and finished. Active status and progress come from the selected Runtime; completed, failed and cancelled Builds come from project Results. Cards retain the source Run, times and any failure or attention reason. |
| Artifacts | Image, video and audio file Outputs from project Results, including those already published by ongoing Builds. Use the sidebar to choose all media, videos, images or audio. View media on a Build opens its Outputs; opening the Artifacts tab returns to project media. Structured Outputs such as normalized media and NarrativeAlignment stay intact and do not add their internal files to this gallery. Click a card to view it in the central preview; video and audio have playback and a time slider. Back to composition returns to the existing composition position. Previewing a file does not select it as a Candidate in the Run. |

A declared lane stays one row even when items overlap. Later items cover earlier ones at equal
stacking order; selecting an item brings its full rectangle forward within that lane. This changes
editor selection, not the Film's paint order. The same behavior applies to attached child lanes.
The time ruler, each projection's mapping and evidence rows, and the shared Instant row
form one pinned Timeline area. A work without a domain projection keeps the ruler and Instant row.
Window intervals appear through the Track Items that consume them; their references remain available
in the owning Source and declared Inspector fields.
Select an overlapping object to bring it forward, or right-click the overlap to choose one covered
by its peers. This changes editor selection, not the composition.

Open either library tab or click Refresh to read its latest state. These lists do not poll.
Refresh replaces the view; scrolling to the end loads more. Media categories query matching files
across Result pages, so an intervening Build without that kind of media does not require a separate action. A failed refresh keeps the
previous view and displays the error. Multiple references to one stored file share a media card;
its source details retain the originating Builds and Outputs. Highlighted Outputs appear first.
Names show up to two lines. Double-click a name or press F2 to edit; Enter or leaving the field
saves, and Escape cancels. Renaming changes the displayed Output name in the finished Result,
not its reference identifier or media file.

Use [Builds and Results](builds.md) to inspect Output names, export media, finish an incomplete Result,
edit Result presentation metadata or select an earlier Output. Studio reads the same project Result
repository. With no Runtime selected, finished Results remain accessible; preview works when its
display closure needs no unresolved Endpoint work. Active Runtime status and transient Endpoint
processing require the selected environment.

Studio opens the selected work for interactive playback and editing. It creates no Build and submits
no paid generation. It can evaluate deterministic Producers and the exact immediate capabilities a
Provider permits for transient authoring, such as media inspection and normalization. Select existing
files or produced Outputs through the Run for the material the view needs. If a required generation
is still running, continue component work and open its resulting composition when the material is ready.

[Runs](runs.md) explains selection and reuse. [Snapshots](snapshots.md) captures the current picture
directly with `hypit snapshot --studio <this-studio-url>`. [Rendering](rendering.md) provides frame-range Builds
for inspecting the composition as encoded media; choose the view that helps answer the current question.

## Edit the owning Source fact

Inspector fields and timeline handles write back to actual Source endpoints. A field can live in a
referenced Frame, Style or SVS Recipe rather than on the selected Track tag. Editing a shared Recipe
changes every consumer that uses it; create and select a separate authored instance when the design
needs independent variation. Lists and records save their complete validated value when editing ends. Required fields that are
still incomplete remain in the editor with a completion hint. Check save status and the resulting preview.

Where groups position, size, fitting and layout. When groups timing, playback, trims and motion.
How groups content, typography, color, effects and audio levels. Components name their own pages
and sections within these questions. Numeric units sit outside the editable value: a width authored
as `78%` keeps `%` when edited, while a fractional opacity may display as a percentage and write
back as a fraction. Dropdowns can have readable option names and previews; their underlying value
is what the Source receives. Color fields support exact hex values and suggested swatches.

For catalog fonts, Caption, Typography and Ranking can expose the primary font family's dropdown
through the selected Style. It edits the shared font declaration; its weight and style must be
available in the chosen family. A local font continues to use its exact file. A project component
can offer its own font or preset choices through Companion fields.

Named Instants provide timeline locators. Windows remain reusable interval values. Edit their
`at`, `from`, `until`, `for` and `end` declarations in Source when temporal construction should change.
Edit the Timeline declaration or domain projection declaration that owns a temporal relationship.
Clip editing handles its source occurrence; a component Companion handles its own Sources, Uses or
events. Time handles follow the consumed value's declared inverse relationship to its owning Source.

Timing edits follow the authored relationship. A direct Selection or Moment edits that identity
in Script; a quoted expression edits its local clock value or offset; a duration changes independently.
[Timing and edit behavior](timing.md#choose-what-a-later-edit-changes) gives the complete forms,
affinity choices and shared-consumer consequences. Marker moves preserve unrelated prose whitespace. With unchanged spoken tokens and identities,
new marker references can use the existing alignment evidence. [Reuse boundaries](authoring.md#reuse-produced-work-explicitly)
explain when to retain media, its local domain, alignment evidence or only an upstream generated file.

A successful parameter or timeline edit saves the owning Source and recompiles the selected Run
for the view. Rejected edits retain the accepted Source and values. Result renaming instead updates
Result presentation metadata; it does not change the authored composition or trigger a Build.

Source edits outside Studio are observed too. If a stale UI edit conflicts with a newer file, read
the current Source and retry the intended change against it instead of overwriting the newer work.
Composition edits return to the ordinary Sources; they do not create a second Studio project.

## Give a project component a useful Companion

A Companion makes the component's own production relationships legible and editable: a board's
lifetime, a reveal event, a Cue's actual Style, or a scene's layout choices. Its Producers still own
the rendered work. Generic Track projection is useful when no additional authoring concepts are
needed; a component with meaningful child events or controls can publish those directly.

Read [Companion authoring](studio-companions.md) for Items and child lanes, picture selection,
parameter controls, unit conversion, semantic writeback and package activation. It builds on the
same [component design](component-design.md) decisions used to make the video.
