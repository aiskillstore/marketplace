# Reviewing the production

Read this when opening Studio, judging an encoded Result, or improving the layout, timing and
expression of the new Film.

For picture inspection, start with [Snapshots](snapshots.md) of the current Studio work or existing
HTML. Single frames establish detail; continuous frame grids establish movement and handoffs.
Use Studio playback to hear and feel the passage, and the exported file to judge encoded delivery.

[Studio](studio.md) explains launch, session reuse, displayed information, Source writeback and
project Companions. [Timestamped Comments](studio.md#revise-from-timestamped-comments) connects user
feedback to the owning production facts. [Builds and Results](builds.md) explains retrieval and explicit Output reuse.

For a collaborative review, [show the editable work before export](studio.md#review-before-export)
and introduce both views: Comments for time-located direction, Studio for the timeline and exposed
parameters. Browser playback makes both available without first encoding a complete video. When a final file is requested,
render and inspect that encoded deliverable as a separate step.

## Make the composition work

Watch the selected performance and its assembled picture and sound. In pure A-roll, judge whether
speech, action, reactions, camera changes and pauses carry the intended passage. In a mixed work,
judge the additional Caption, evidence and graphic relationships together with that performance.
Watch their actual arrangement in Studio or a rendered Result: is the comparison clear, is the
Caption readable, does the B-roll cover the intended explanation, and do entries and exits land on
the right words or actions? Does a persistent object retain its identity and state through the
handoff, and does moving a video viewport keep its intended playback? Adjust the layout, timing or
component behavior that will make the passage work better. Judge a local change in the surrounding
composition.

Work from the authored Script and the production's existing semantic timing when locating a word,
reveal or handoff. Those relationships identify the passages whose composition needs attention;
Studio and rendered frames show how the chosen assets work there. Carry the same produced media
and semantic Outputs through layout and component revisions.

## Review the work the Run actually selects

Use the Run that selects the production's actual material. It binds the Author Source, Targets,
files and earlier Results. Preserve the produced media and semantic Outputs as the composition
changes. Studio opens the selected work for playback and editing; snapshot captures its current
compiled picture directly. A focused Run serves a requested encoded interval.

Judge the relationship that the evidence can establish. A component's own example can show its
style and behavior. The actual production image establishes its framing and color; the produced
video shows how moving faces and gestures interact with Caption and MG. Inspect those interactions
with the material that will appear in the deliverable.

## Show what the current work establishes

`hypit check` can establish that the Source and graph are legal. Studio can establish what the
configured composition displays. A completed Build can establish what the selected Endpoints actually
produced. Creative review asks a different question: does this composition perform the
Treatment and the useful relationships learned from the reference?

Present intermediate work with its purpose, what it already realizes and the important work still
needed for the Brief. A storyboard can settle framing; the produced performance establishes how
a person actually moves and speaks. A working preview can support either discussion. Make its
current scope clear so the user can give useful direction, and continue the remaining work within
the agreed commission. [Service selection](../environment/model-and-provider.md#choose-the-practical-capability-path-with-the-user) owns unresolved service choices.

Read missing behavior through its material and use together. For intended speech, listen to
the selected Film: an available audio file establishes material, while admission and the chosen
Audio contribution establish whether that material reaches the Film. For intended physical
action, examine the footage itself as well as the viewport animation. Use
[media admission](media.md), [Audio Clips](audio-clips.md) and [Film assembly](rendering.md)
to complete those relationships. Silence or stillness can equally be intentional when they serve the Brief.

Look at the complete Film at its intended delivery size as well as the components inside it. A component that looks
attractive in isolation may still cover a face, compete with a Hook, arrive on the wrong word, or
break the piece's rhythm.

## Choose evidence that exists

The useful frame or interval is not known merely because a component has been authored. It becomes
known from something visible or time-locatable: an authored Segment or clock relation, the Studio
playhead, an encoded Result, or timing produced elsewhere in the graph. Until then, its exact
location remains an open question.

Use whichever view can answer the current question:

- Once frame positions are known, use [snapshot](snapshots.md) to inspect the existing `HtmlProgram`
  directly. Select individual states or continuous frames; keep the surrounding handoffs visible.
  The locations can come from semantic events, the playhead or authored clock time.
- On an encoded Result, focused media operations such as frames, cut, and tile can expose exact
  pixels, adjacent frames, or a short passage.
- Open Studio when interactive playback, parameter editing or a component's Companion helps the
  current work. Seek projected domain evidence or select Track Items to inspect their place in the composition.
- Use a [range render](rendering.md#choose-a-render-interval-in-frames) when the question requires
  an encoded clip with sound, such as testing an export setting or delivering a passage.
- Watch the whole deliverable when the question concerns Hook clarity, story movement, payoff,
  CTA, or how A-roll, B-roll, Caption, MG and Effects work together.

Choose and combine these views according to the current question. A component name alone does not
prove that a particular state is stable or that a change occurs at a guessed time; Studio or actual
media supplies that evidence.

Inspect the relationships that make the composition work:

- **performance** — the selected footage actually contains the intended speech, action and reaction;
  Clip or component motion does not substitute for missing action in the material;
- **picture and coverage** — B-roll supports the passage and its display window carries the intended
  explanation or handoff;
- **semantic timing and motion** — cuts, Caption Cues, MG states and Effects occur on the
  intended word, phrase, pause, or clock event; inspect important internal events as well as the
  outer interval. A scene that starts on the correct phrase can still reveal its result on the
  wrong word. Entry, settling, active behavior and exit should make the intended handoff perceptible;
- **shared layout** — a layout established for a passage remains coherent while its individual
  contents change; inspect the handoffs as well as the populated states, so replacing a card or
  ending a Selection does not accidentally release space the passage still needs;
- **Caption** — every meaningfully different speaker, position, color, emphasis, Cue shape, and motion
  configuration remains readable, belongs to the speech, and preserves the intended face and action;
- **Typography and UI** — independent writing has the correct hierarchy, content, persistence, and
  relationship to the picture;
- **composition** — each element has enough room and the full frame preserves the intended visual
  hierarchy.

For geometry, read three nested relationships: Canvas, outer Frame or background, and inner content.
Check containment and capacity at each boundary, then judge optical alignment. Intentional crop,
bleed, overlap, and asymmetric balance are part of the design when they help the work; measurements
describe what happened and the picture decides whether it succeeds.

At a visual handoff, inspect what is actually visible before, during and after the change. A return
to the speaker may be intended; a one-frame flash of that picture between other views may not be.
If the exposure is unintended, locate the owning cause: the active Window, source playback,
transition opacity, component background lifetime or spatial crop. Several Frames or a designed
background can form the intended picture without one full-frame source.

Repeated appearances of one observed visual configuration can share a judgment. A visibly changed
speaker, placement, Style, content shape, behavior, or surrounding composition supplies different
evidence.

## Compare a reconstruction by function

Use the reference Analysis and Timeline as a question map. Compare the spans that reveal an important
relationship: an accumulation on a board, a switch from A-roll to B-roll, a Caption system changing
speaker, an MG reveal, or a payoff returning to the Hook. A short clip or dense adjacent frames can
establish motion and order; a full-resolution frame can establish text and geometry.

The target may intentionally change person, product, brand, language, or visual world. Compare
whether the transformed element performs the same useful role, not whether its pixels match. When the
target's Treatment deliberately changes the role too, the Treatment is the authority.

For a supplied person or product, compare the new appearances with those actual references as well
as the intended camera image. Judge recognizable identity, appeal, and how naturally the new subject
inhabits the piece; check that dialogue, demonstrations, and graphic details make sense for this target.

Inspect the detailed realization of each relationship: the entry catches attention, the hold gives
enough reading time, the motion explains a change, and the exit clears the next idea. Compare source
and target at their corresponding words or actions; the target's new speech can place that event at
a different second. A reference gives precise design evidence, while Brief and Treatment determine
which of those choices belong in this piece.

## Repair the owning fact

| What the review reveals | Where the correction belongs |
| --- | --- |
| The intended story, shot logic, or visual system is wrong | `TREATMENT.md` |
| Words, speakers, Cue membership, Selections, or Moments are wrong | the Author Source's Script |
| Composition, authored parameters, or semantic/clock relation is wrong | Author Source or Recipe |
| The wrong file or earlier Output is selected | Run Source |
| A reusable visual role cannot express or render its intended design | the project Author Package |

Before changing the work, connect the composition problem to its consequence and the intended
improvement. For instance, extending a hold can make a comparison readable; delaying an exit can keep
proof visible through the claim it supports. Correct the owning fact and preserve existing work
around it. Watch the affected interval and its handoffs after the change, then judge it in the whole
Film. If the result did not improve, revisit the explanation before making another adjustment.

A request for different paid media is a production decision whose additional calls must be visible
in `hypit plan`. Reuse the accepted Outputs for composition changes.

The composition is ready when its layout, readability and timing carry the Brief and Treatment
clearly and compellingly. Continue when a change will improve that expression; deliver when it works,
with the important choices and any material limitations explained.
