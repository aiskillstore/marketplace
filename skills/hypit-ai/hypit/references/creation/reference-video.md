# Understanding a reference video

Read this when a video or link is evidence for what the new work should preserve, adapt, or learn
from. The useful result is a timecode-level semantic reading: what the piece communicates, and how
its exact audiovisual choices make that communication work.

For a reference supplied as a link, [video download](../production/video-downloads.md) explains
`hypit download`, its explicit preparation and the saved source file used by the tools below.

## Read the whole through its details

Watch the whole reference from opening to close. Follow its hook, argument or story, shifts of
attention, payoff and intended viewer response. Read the spoken words with their times. Notice who
establishes the performance, what the pictures contribute, and which Caption, MG, Typography, Effect
and Audio systems persist or recur. Form a provisional explanation of why the piece works.

Read that meaning through its concrete realization. Each designed element deserves an account of its
content and appearance, spatial relationship, entry, active behavior, persistence and exit. Locate
these changes against the words, pauses or actions they serve. Explain what the choice does for the
viewer: establishes a person, contrasts two claims, accumulates proof, amplifies a reaction, makes
a process legible, or hands attention to the next idea. Meaning directs the close look; the close
look supplies the detail needed to recreate the expression. Close reading also reveals purposes and
connections that the first whole-piece impression missed. An interpretation earns its usefulness
by explaining the concrete choices; close observation becomes creative understanding when those
choices connect to the piece's intention. Keep both growing together throughout the reading.

When a choice is puzzling, widen the view: relate it to the surrounding words, nearby events, earlier
appearances and later consequences. Consider what those connections could explain, then examine the
relevant sequence. Read the Format or Craft for the relationship you are investigating; use it to
sharpen the question and recognize what the reference is doing.

A motion's name is a starting point. Inspect its path, scale or opacity change, pace, overshoot or
settling, and relationship to neighboring events when those make the effect distinctive. Likewise,
understand a graphic's hierarchy, typography, palette and spacing through what the viewer must read
first and compare next. Identify the coherent behavior linking the observed frames, including the
details that make its states and transitions work. A dimmer copy during an exit may be one object's fade, for example; inspect the sequence to
understand the change.

Whole-piece and close readings revise each other. An object that survives a camera cut belongs to a
system with a longer lifetime than that shot. Follow its state across the piece: a new entry may
replace an item, add to a collection, or temporarily cover it. Document the system once and locate
its changes in time. Camera boundaries help navigation; meaning and continuity determine which
things belong together.

Speak aloud as the understanding develops. During a close look, explain what the discovered timing,
placement or motion does for the viewer and how it informs the adaptation. Share representative
frames or a word-labeled grid when they make that relationship tangible. Carry a provisional reading
into the conversation, then explain how new evidence deepens or changes it. Articulating the
connection also helps you notice where your explanation is still incomplete. Analysis and Timeline
retain the detailed evidence; the conversation lets the user follow the developing interpretation
and contribute their taste. Routine progress does not require another approval.

Build an account of behavior that can become an editable production. A fixed screen image may be
the evidence the passage needs; a changing comparison also needs its arrivals, states and handoffs.
Retain what the objects do together as well as what each looks like. Several implementations can
express the observed behavior, so the account need not guess the original author's source code or
component structure.
The useful result is an explanatory model for this commission: which relationships should remain
when its person, product or wording changes, and which choices should be redesigned. Record the
observed behavior before choosing how the target will implement it. A picture, text and motion that
work together may become one component; repeated appearances may be states of that same object.

Follow the whole reference and account concretely for each distinct system and its changes.
Repeated behavior can share an explanation, with its variations and handoffs located in time.
Carry established understanding into direction and composition while pursuing the questions still
open. Preserve those questions at their source times so the next view can sharpen the account.

## Make time visible

Use `hypit transcribe` when understanding a spoken reference. Its wording and word-level times give
a strong starting point for following the argument and connecting speech to cuts, illustrations,
reveals and emphasis. Keep that transcript beside the reference and interpret its wording with the
surrounding argument, visible names and supplied context. Small transcription errors can coexist
with a clear understanding of what the passage means.

Pass the reference's spoken language explicitly: `--language zh` for Chinese, `en` for English,
`es` for Spanish, or `ko` for Korean. Actual alignment support belongs to the selected service;
for local execution, prepare that language's resources as described in
[local tools](../environment/local-tools.md). A Chinese passage can contain English brands and names while still using `zh`.
Its timed Chinese characters help locate a phrase precisely; group those characters into meaningful
phrases when describing the reference and writing the new Script.

[Service selection](../environment/model-and-provider.md#choose-the-practical-capability-path-with-the-user)
explains assessing local preparation and choosing the local or hosted path for this transcription.

WhisperX's recognized spelling reflects the recognizer's interpretation of the audio. Coined words
and unfamiliar names are especially prone to substitutions, so a spelling difference alone cannot
establish a pronunciation error. The transcript helps recover the reference's content and locate
its moments. For the new work, [Script pronunciation](script-and-time.md#write-the-intended-pronunciation)
expresses the words and readings the generation request should perform.

For speechless work, locate meaning through actions and changes in the scene.

The local `hypit media` commands expose the source at the scale needed:

- `probe` gives duration, dimensions, frame rate and audio presence;
- `cut` saves a selected passage as a clip;
- `frames` extracts chosen moments or a range at a chosen interval;
- `tile` and `tiles` arrange time-labeled frames for inspecting change, with optional word context;
- `boundaries` locates abrupt visual changes worth inspecting;
- `fetch` saves a supported video link locally.

For a close reading of motion, `frames --every-frame` and `tiles --every-frame` retain every original
frame in the selected interval. Each interval is decoded continuously once, then the images are
paginated at the requested cell size. Actual source timestamps preserve variable-rate footage.
Use `--ranges` with `tiles` to visit several intervals, and `--transcript` to read their word context.

```bash
hypit media tiles references/ad/source.mp4 --start 6.8 --end 8.4 --every-frame \
  --columns 4 --rows 3 --cell 480 --transcript references/ad/transcript.json \
  --to references/ad/evidence/list-motion
```

For the production being composed, [snapshot](../production/snapshots.md) captures its existing
picture directly from Studio or compiled HTML. Align the comparison by the event's meaning and
then inspect its concrete frames. Coarse and fine readings continue to inform each other: understand
the whole work, establish the particular behavior, and revisit the whole explanation with that knowledge.

Read grids along the developing explanation, using the transcript's phrases and word times as the
preferred guide for spoken references. Pass `--transcript` to keep those words beside the frames;
`--around` can locate the phrase whose picture change you want to understand.

Continuously adjust the viewed range, sampling interval and cell size to the question. Widen the
range to understand an argument or a persistent system; narrow it and bring samples closer to trace
an entrance, change or handoff; enlarge a frame to read its typography or spatial detail. These are
scales of the same investigation. Move between them whenever a detail changes the explanation or
the explanation directs attention elsewhere. A long reference can be read in manageable passages
while keeping its whole development clear.

Samples establish what appears at their times, with gaps between them. A wider overview can miss a
brief event even when neighboring samples look unchanged. Follow the words and visual systems
through those intervals at a useful density, accounting for their entries, changes, persistence and
exits. A few representative stills cannot supply that temporal account.

```bash
hypit transcribe references/ad/source.mp4 \
  --language en --to references/ad/transcript.json

hypit media tile references/ad/source.mp4 --start 0 --end 12 --every 1 \
  --transcript references/ad/transcript.json \
  --to references/ad/evidence/opening.jpg

hypit media tile references/ad/source.mp4 --start 6.8 --end 8.4 --every 0.1 \
  --transcript references/ad/transcript.json --columns 4 --cell 480 \
  --to references/ad/evidence/list-change.jpg

hypit media cut references/ad/source.mp4 --start 6.8 --end 8.4 --label-time \
  --to references/ad/evidence/list-change.mp4

hypit media frames references/ad/source.mp4 --at 6.9,7.3,7.8 --label-time \
  --to references/ad/evidence/list-frames
```

Time labels identify positions in the input media. Give `--transcript` the transcript of that same
media; its word times share that clock. Word labels sit below the picture so the original Caption
and MG remain visible. Keep useful evidence under `evidence/` and use descriptive names that make it
easy to reopen the relevant question.

To inspect a spoken phrase, use `--around "the phrase" --transcript references/ad/transcript.json`
in place of `--start` and `--end`. `--padding` adds surrounding time; repeated phrases can be selected
with `--occurrence`. Use `tiles` with `--columns` and `--rows` to page a dense sequence into readable
grids. Keep the range broad enough to see the incoming and outgoing handoffs.

For Caption, inspect each meaningfully different configuration: speaker treatment, placement,
emphasis, Cue shape and animation. Follow transitions between configurations too. Repeated uses of
the same behavior can share its description, with their differing content and times recorded.

When two readings conflict, reopen the relevant source interval and make the disputed detail legible.
State what is visible or audible separately from what you infer it means. Player controls and other
viewing context belong to the viewing surface; distinguish them from the designed video content.

## Preserve a connected account

Write the understanding into the project as it develops. Preserve both the whole-piece explanation
and the detailed reading, with source times and useful evidence paths so someone can pick up the
same work from the files. Include what a choice does for the viewer alongside how it appears.

`ANALYSIS.md` carries the whole-piece model: what the work is trying to achieve, how its story and
pacing work, what each visual or sound system contributes, which systems persist or recur, and how
distant moments relate. Keep the reference's facts and your interpretation distinguishable in
ordinary prose.

`TIMELINE.md` carries time-locatable realization. Organize it into sections named by source-media
time and a meaningful phase. Within each, connect the active objects and their detailed behavior to
the words or actions they serve. An account should let someone find the event, understand its
expression and implement an appropriate counterpart. For example:

```md
## 6.07–8.27 · The workload accelerates

The spoken list reaches “videos / voiceovers / ads / scripts”. Each noun brings a new full-frame
illustration and a marker-style word at its center, replacing the preceding pair. The lower spoken
Caption gives way to these central labels so each example reads as one unit.

The word and picture enter together on each noun; the labels pop to size, settle briefly, and leave
with their picture on the next cut. The increasingly short holds make the workload feel excessive.
The 6.8–8.4 clip and list-change grid show the handoffs; word times are in transcript.json.
```

These sections can overlap and contain finer timed notes where the work is dense. A persistent
title, board, sound bed or Caption system can span several sections; refer to the same system and
describe what changes. Keep exact text, meaningful colors, positions, motion phases and timings where
they are needed to understand or reproduce the design. Reopen the media for facts still in doubt.

Use production vocabulary by function. A-roll establishes the semantic performance even inside a
small inset or behind a full-frame B-roll. Caption displays the speech; Typography carries independent
writing. MG and UI can contain text of their own. A sound can support a continuing argument across
several picture changes. Name the roles that clarify this particular work.

## Turn understanding into new direction

Source time locates evidence. Record both the original seconds and the expressive relationship:
a reveal answers a question, an image illustrates a phrase, an exit makes room for the next claim,
or an audio handoff begins the next speaker under the previous picture.

The user's request determines how those relationships should live in the new piece. A different
person or product may change the argument, copy, number of examples, graphic content, placement and
duration. Use [transformations](transformations.md) to think through that adaptation. Prefer
Selections for meaningful spans and Moments for events in the target Script, and let the accepted
performance establish their time. [Script syntax](../production/script-syntax.md) owns that authoring language.

For generated camera imagery, [image direction](../playbooks/craft/image-direction.md#two-ideas-behind-every-sentence)
turns the observed appearance into a coherent styling and scene direction, with the decisive details
the target needs. The reference notes retain the observations behind those choices.

For the designed picture, use [component design](../production/component-design.md) to turn the
target's relationships into useful objects, parameters and events. A system can span several shots;
one shot can contain several independent systems. Choose the new component boundaries from shared
behavior, with the details required to realize it. [Direction and its inputs](../production/system.md#give-each-part-the-direction-it-can-realize)
connects the whole creative design to its separate material and composition instructions.

The recorded account should explain the whole piece from opening to close and make its distinct
visual systems and their changes locatable. It should be concrete enough to direct the new work:
what to preserve or adapt, how it is expressed, and why it belongs. Continue investigating an
unexplained relationship where it could change that direction.

Keep the current question, passages or systems still to examine, and next useful action in
`PROGRESS.md`. Write discoveries into Analysis and Timeline while they are fresh, and revise those
accounts when the reading changes. When resuming, read these files and reopen the source at the
recorded locations. The user's goal remains in Brief and your new design in Treatment.

When the intended adaptation depends on a performed, physical or camera relationship unfolding in
time, preserve a useful source excerpt as temporal evidence for [reference-directed generation](../playbooks/craft/video-direction.md#let-footage-carry-temporal-behavior-that-matters).
The analysis explains what matters; the footage can carry that behavior into the model request.
