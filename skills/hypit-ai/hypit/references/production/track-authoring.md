# Writing a project Track

Read this when a production needs new visual or audible structure, state or rendering behavior,
including a scene that coordinates existing footage with independent content. Begin from
what the viewer should perceive and what should follow a changed performance.
[Component design](component-design.md) develops that idea into a useful author interface and a
coherent treatment in the actual composition.
[Composing Tracks](tracks.md) covers existing Track roles; [vocabulary](vocabulary.md) covers discovery
and project package ownership. [Caption authoring](caption-authoring.md) covers the speech-text case.

## Start with the author-visible behavior

Prefer domain-produced time when the component responds to words or performance. A Narrative
projector can turn a comparison Selection into a Window, a verdict Moment into an Instant, and a
Segment into a board lifetime. Expose ordinary absolute values on the component Surface and pass
them to the implementation. This keeps the component useful when a new performance changes the
pace without coupling it to Narrative. Expose separately meaningful
internal events as well as the outer lifetime. The [event-versus-animation boundary](component-design.md#let-meaning-drive-the-behavior)
explains why a single semantic Window cannot replace several word-linked triggers. In an authored animation,
content events carry their own reading rhythm. Their Instants and Windows enter the same component
inputs; durations and frame offsets direct how a change unfolds.

Write a small intended Source use before implementing it. A new score strip might have one Style,
an outer Window, preset scores and score-changing Moments. Decide whether its items appear briefly,
remain after activation, replace a previous state, or rearrange the layout. Those differences define
the component more usefully than a long list of decorative parameters.

This existing answer-strip vocabulary illustrates a concrete choice:

```svml
<emoji:EmojiReveal id="answers" timeline={speech.timeline} within={canvas.bounds}
  style={answer-style} placeholder={question-icon} during={speech.window}>
  <emoji:Item id="known" icon={known-icon} preset="true"/>
  <emoji:Item id="surprise" icon={answer-icon} at={reveal}/>
</emoji:EmojiReveal>
```

Its outer Window owns visibility; source order owns slots; preset answers exist at the beginning;
each activation Instant changes only its slot and the answer persists. A chart or scoreboard can instead own
repeated updates or simultaneous events.

## Keep selection projection and consumption distinct

Script names Narrative meaning: a Selection, Segment or Moment. `@hypit/narrative-temporal`
combines Alignment, its local domain and an equal-length Window and publishes requested absolute Instants or Windows. The
component's Surface accepts those values, and its Fragment and
Producers decide what to do with them.

```text
Narrative relationship + Alignment + LocalDomain + Window
                         ↓ Narrative projector
                Timeline + Window / Instant
                         ↓ generic component consumption
              media occupancy, graphic state, sound or effect
```

This separation lets one projected Instant drive an answer reveal, a short sound and a flash.
Consumers can share that one value. Changed speech moves the upstream event without asking each
component to search for a word, carry a projector or inspect the Script parser.

Use `resolveTemporalContext` from `@hypit/temporal/markup` to resolve the component's
`timeline` input. Pass that same Timeline to its Fragment and Producers, alongside projected
Instants/Windows. A component can combine directly authored and domain-produced named values without switching
time models. The installed `examples/semantic-composition/packages/chat-scene` demonstrates repeated
content children with their own events and a picture drawn entirely in code.

For a Window consumer, `during={example}` reuses a projected interval. To start a short
effect at an Instant, first declare a named Window from that Instant, then pass it through `during`.
An Instant consumer may accept `at={answer}` because it owns a state transition. Read the
actual Surface: Window and Instant consumers deliberately expose different reference vocabulary.
[Timing](timing.md) describes the shared forms.

## Separate lifetime, activation and persistent state

For a board that stays on screen, author its outer Window independently of individual reveals.
Then decide what its children mean:

- an Item window may mean “draw only during this interval,” as with an ordinary Clip;
- an activation window may stage an item's entrance and movement, after which it remains in a board;
- a Moment may replace a question mark with an answer that persists until the outer Window ends;
- a preset item may already occupy the initial state and need no reveal trigger.

Document that meaning in the component. `preset` is the answer strip's package-owned initial-state
concept. An answer strip consumes an Instant for a reveal that persists, while Media consumes a
Window for occupancy. Expose timing inputs whose consumption matches the behavior.

The interview's project emoji strip illustrates this design: one outer Window, ordered answer
items, a placeholder asset and one icon per answer. Each Moment changes its own slot. The Track does
not decide when the spoken answer occurred; it consumes the already projected event.

## Use absolute time with explicit media inputs

The [Timeline](timeline.md) resolves Instants and Windows from literal or typed Extents. A domain
projector may translate a complete local domain through an equal-length Window, then publish ordinary
absolute values and discard that relation. Media is not bound to this projection; a Visual or Audio
Clip declares its own ordinary media occurrence with an absolute Window. Sequential ranges,
head/interior/tail space and simultaneous branches remain temporal relationships. A project scene
consumes the Timeline, media and the Instants or Windows its behavior actually needs.

A different material operation, such as trimming or retiming a performance, changes the local media
and its preparation. A display operation, such as crossfading two available sources, belongs to the
visual scope owning them. Keep these decisions distinct so a layout change preserves source timing
and a material change establishes truthful local evidence.

## Make spatial decisions equally explicit

Canvas identifies the final raster viewport. SpatialFrame, anchors, extents and fitting describe
where content goes and how its intrinsic shape occupies that place. Region Evidence supplies authored
per-frame regions already resolved in the program picture plane. These are distinct from Timeline,
which owns the complete time range.

Keep image dimensions, placement and crop transformations visible so a measured head or a reserved
MG area maps into the actual composition. Take the production's Canvas and the placement inputs the
role needs. Derive related internal geometry from their common owner. A project scene may keep a fixed layout and speaker arrangement;
a reusable behavior exposes the variation its real uses require. Keep renderer viewport selection
and any detector in their own execution or measurement boundary.

## Write the smallest component that expresses the role

Declare the new package in the project's `packages/` and ordinary package configuration. Read the
installed `@hypit/hypit/author`, `producer`, `admission` and `markup` READMEs for the public package boundaries and inspect a close installed sibling for
the relevant implementation, rather than depending on a monorepo example directory being present.
When already selected by a project, `@hypit/interview-emoji-reveal` demonstrates persistent
Moment-driven state and `@hypit/ranking` demonstrates reveal Windows and settled rows.
`@hypit/visual-track` is the default example for ordinary Clip occurrences with independent Window,
Frame, fit and source-time relations. Optional examples are evidence, not prerequisites.

Ranking's repository README links its implementation: `surface.ts` resolves authored time references,
`fragment.ts` connects typed inputs, `schedule.ts` computes reveal and settled spans, `render.ts`
draws them, and `studio.ts` turns the same program into editor Items. Read it only when that
example is relevant and available; a new project component may use fewer operations or different state.

The Surface exposes author intent and resolves absolute temporal inputs through
`resolveTemporalWindowReference` or `resolveTemporalInstantReference`. The Fragment wires the
completed value, the shared Timeline, explicit placement Frames and authored values into the
component's Producers. Timeline authoring, Narrative, beat or other domain packages publish those
values upstream; the component does not construct an anonymous value or inspect its origin. The
Producer owns the visual/state behavior, while Studio follows the graph back to the value's actual
declaration for editing.

Wire supplied media, Script content and event references through Source. Expose other content or
treatment in Source or Recipe where the work needs those choices. A one-off component can own fixed
illustrative labels, dimensions and animation alongside its state and visual structure; its boundary
does not require every detail to become a parameter. [Component design](component-design.md#separate-responsibility-parameters-and-reuse)
explains that distinction. A new Caption family consumes the common Caption document and timing.

## Connect the implementation at its real boundaries

The useful pieces of a project package are:

| Piece | Responsibility |
| --- | --- |
| Manifest | Module identity, nominal Types, Producer input/output ports and dependencies |
| Surface | Validate authored attributes and children, resolve typed references, emit inert Records, Components and Fragments |
| Fragment | Wire the finite computation graph and publish outputs |
| Producer | Compute the immutable state or render program from declared inputs |
| Activation | Register the Manifest, deterministic handlers and Markup facets with their matching Facet ABI |
| Vocabulary and preview | Explain the role and show a recognizable, configured example |
| Optional Studio Companion | Project meaningful editor Items, real parameter bindings and temporal lineage without changing video rendering |

Resolve the Track's `timeline` through `resolveTemporalContext` and wire `context.timeline.ref`
directly to its Timeline input. Source footage is supplied explicitly through media inputs. The
visual Producer consumes Timeline, explicit media and absolute time values.

For each Window input, call `resolveTemporalWindowReference`; for an event, use
`resolveTemporalInstantReference`. Pass the child element and `resolveReference`, then wire the
returned `ref` into the domain Fragment. Window consumers use `during`; Instant consumers use `at`.
Both attributes reference completed temporal values. Timeline-authoring and domain packages own
declarations; a Narrative package must publish its selected boundary first.

Keep each child's `subjectId` meaningful for inspection while qualifying graph ids by its owning
Track, so multiple instances can coexist. Do not use it to reject a deliberately shared Window. A
finite create/append/finalize graph supports any authored number of messages or cards with ordinary
fixed Producer ports. The exact helpers and vocabulary
live in `@hypit/temporal/markup`; the `@example/chat-scene` package demonstrates authored and semantic events on one Timeline.

A scene may publish computed event times when another component needs them, just as it publishes a
Track. This shares pre-render data. When the author already specifies a common trigger, consumers
can share that input directly. Expose additional outputs for a real composition relationship.

For persistent state, reason about a requested frame directly. For example: outside the outer Window,
draw nothing; inside it, each slot shows its preset/activated answer or its placeholder. Apply an
entrance motion relative to that slot's activation frame. Deriving state directly from declared inputs
and the requested frame keeps Studio scrubbing and partial or concurrent rendering deterministic.

Emit the public VisualTrack representation through `@hypit/composition`.
[Component visuals](component-visuals.md) explains Presents, element trees, local animation,
prepared surfaces and a complete drawing function. [Spatial layout](spatial.md) explains incoming
Frames, and [Fonts and text](fonts-and-text.md) explains font resources.
Pass asset references and exact font data through declared inputs. A visual Producer does not open
files, call GVI, run ffmpeg or choose a Provider. If an external preparation operation is needed,
represent it separately through its capability; its result becomes another input.

A component-owned sound can be a peer Audio Track output; alternatively the Source can place a sound
on the same Moment. Neither choice requires a Track to inspect another Track's private state.
Document which Outputs are public, including useful deterministic program values for inspection.

## Verify the behavior the component introduced

When the new role needs its own timeline Items or Inspector, read
[Companion authoring](studio-companions.md). Expose the domain
schedule and temporal identities at their actual boundaries so the editor consumes them directly
instead of reconstructing them from pixels.

Give the component a concise README, public vocabulary, a meaningful visual example and a preview
showing the state change. State each exposed event's meaning and which state persists after it.
When several actions follow different phrases, check their separate anchors through a delivery with
uneven spacing; stretching only the outer Window would conceal a wrongly fixed internal trigger.
Verify the actual intended transition: an answer appears on its Moment,
previous answers persist, future ones remain hidden, and the whole strip respects its outer Window.
A designed still alone cannot establish that behavior. For stateful MG, a few meaningful frame
checks around activation and exit are more useful than snapshots of every implementation detail.
Also check a second instance, a differently sized Frame and direct seeking into the middle when
those exercise the new behavior.

## A reusable relation spanning Clips

When behavior spans several source occurrences, make that relation the component's own vocabulary.
A continuing Presenter may own explicit Source and Use children; a crossfade may own outgoing and
incoming roles; a slideshow may own its replacement policy. The component receives Timeline, Frames,
media and events through normal typed inputs and publishes an ordinary VisualTrack. Its package owns
the local grammar for that relation, while a larger scene coordinating footage and graphics can remain
one project component. Both paths use the same rendering capabilities.
