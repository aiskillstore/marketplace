# Drawing a component

Read this while implementing a project component's rendered output. [Track authoring](track-authoring.md)
owns its author interface, temporal inputs and state behavior. [Spatial layout](spatial.md) explains
the incoming geometry; [Studio](studio.md) explains an optional Companion.

## From program to visible Track

A component's drawing output describes what appears, where it appears and how it changes over its
visible lifetime. For a reveal card, those decisions become a box and text, a destination Frame,
an entrance animation and the interval for which the answer remains visible.

A component can first compute a domain program, such as a list of answers and their reveal times.
Its drawing Producer receives that program, Timeline, Frames, Style and explicit assets, then
returns a VisualTrack. A simple component can produce the Track directly when no separate program
would help its behavior or editing.

The public representation has these parts:

| Part | What it means |
| --- | --- |
| Track | Named picture contribution belonging to one Timeline |
| Present | An independently timed and stacked appearance |
| `span` | Program frames from `startFrame` through the frame before `endFrameExclusive` |
| `stacking` | Absolute paint order among Presents; higher order appears above lower order |
| Elements | One rooted tree of boxes, text, media, masks, compositable surfaces or renderer programs |
| Animation | Keyframes relative to the containing Present's start |

Use several Presents when items have separate lifetimes or stacking positions. A persistent board
can keep its settled rows visible while later rows enter. Its domain program decides those spans
and states; the drawing output makes them explicit.

Track grouping is an authoring boundary; each Present has its own paint order among the film's
appearances. Its element tree supplies local layout and compositing scope. Use that tree or a browser
program for content that moves, clips or changes layout together. The final DOM follows these owned
visual relationships rather than the nesting of tags in Source.

## A working drawing function

[visuals.ts](examples/visuals.ts) contains `renderCard`, a complete pure drawing function using
`sealVisualTrack` from `@hypit/composition`. It receives a projected span and a resolved Frame,
draws a colored box with exact-font text, and optionally fades in relative to the Present's start.
Its colors, size, padding, layer and entrance duration are supplied by the caller. These drawing-function
arguments need not all become Surface parameters: the owning component can supply its fixed design
and expose only the inputs the production needs.

The root uses Canvas coordinates. The text child uses the root's local coordinates, so padding is
added once. When a component computes child geometry in Canvas space, subtract the parent's origin
before writing child `left` and `top`.
Present `order` is local to its owning Visual Track, while `z` places that Present in the final Film
paint order. Element `order` is local again to the containing Present.

The function is the drawing part of a package. Connect it to a Producer with matching typed inputs,
then publish the Track through the Fragment and Surface as described in
[Track authoring](track-authoring.md#connect-the-implementation-at-its-real-boundaries). Surface outputs
map the Fragment's export name to a public Source name such as `answers.track`.

Use `timelineFrameCount` from `@hypit/timeline` for the full Timeline's frame count and
`assertVisualTrackIdentity(track, timeline)` to check a produced Track against it. Direct seeking
and range rendering evaluate the same declared keyframes at the requested frame.

## Elements, fonts and other assets

`box` provides a container or painted shape. `text`, `text-flow` and `path-text` carry text and exact
font resources. `image` and `video` reference their media artifacts. A `mask` names owned mask and
content children in the same Present. The installed vocabulary queries expose their value shapes:

```bash
hypit vocabulary --visual visual-track
hypit vocabulary --visual text
```

Visual styles and Motion use the installed CSS-shaped property vocabulary; query the relevant visual
shapes above for their supported values. Motion uses frame-indexed keyframes. Media sampling separately
describes which source frame to show at each part of a Present; it is needed for timed video playback,
trims, loops and holds. A Visual Clip is useful when that is the whole role.

Carry asset and font references through declared inputs. Source assets can be resolved at the
Surface's asset boundary; generated media remains a graph reference until its Producer runs.
The drawing function receives those values. For a visual preparation that reads bytes or invokes an
external tool, use its preparation capability and pass the resulting material into drawing.

## Compose externally prepared pixels

A `surface` element accepts a CompositableSurfaceRef: prepared pixels with explicit extent, color,
alpha and, for animation, frame information. This is useful when the component uses a raster or
animated asset produced by another tool. Its preparation determines the pixels; the Track determines
placement, sampling and lifetime.

For an effect that transforms an image, pass that image as an explicit input to the effect's
preparation. For a local mask, own the mask and content in the same element tree. These relationships
make the required materials available both in Studio and in a render of any selected interval.

## Compose video and graphics in one HTML visual

When a scene's video viewport and graphics share motion or layout, one component can draw them
together. `htmlVisual` from `@hypit/html-program` creates a `program` element's payload. Its HTML
owns the local structure; CSS supplies layout, stacking, masks, filters and blending; optional
`setup(root, data)` code returns `render(localFrame)`. This function sets the complete state at that
frame synchronously. A range render may start in the middle, so compute state from the frame and authored inputs.

Prepare stable structure in `setup`: locate elements, construct geometry and retain reusable drawing
objects there. Paint static procedural textures once their resources are ready.
Let `render(localFrame)` update the state that changes with time. This supports both
fast repeated capture and direct seeking. An HTML visual is sampled within its Present's lifetime;
outside it, the renderer may retain the boundary pose. Re-entry and repeated active seeks must
produce the complete requested state, including when an image became ready since the last call.

Repeated `HtmlVisual` instances share one document's HTML/SVG ID space even though their CSS
is scoped. For SVG masks, gradients or filters, derive each required ID from `root.id` in `setup`
and update its references together. The installed `@hypit/html-program` README owns the `HtmlVisual`
API and resource-loading behavior.

For a depth or material effect, choose the representation that carries its visible behavior:
CSS can tilt a panel, while a deforming textured surface may warrant mesh geometry and Canvas or
WebGL drawing. Keep that implementation inside the project component; give Source the useful
material, amplitude or timing choices rather than the renderer's internal construction.

For shared opacity or a filter, put the affected content under the element that owns the treatment.
A translucent panel can use backdrop filtering; its painted position and browser compositing scope
determine which background it affects. A transition can own both participating pictures and their
handoff. Choose the scope from the visible relationship, keeping independently useful contributions
as peer Presents. These are ordinary composition choices within the same rendering path.

Use ordinary typed children for prepared video, images and exact-font text. A `{{child-id}}` slot in
the HTML places each direct child exactly once. These children retain their declared resources,
video sampling and font handling while participating in the program's HTML layout. Extra artifacts
used by the program belong in its `artifacts` list; `htmlProgramResourceUri` supplies their resource
URLs. The rendering environment materializes those references.

For time-bearing footage, give the component ordinary normalized media, the absolute Window it needs
and an explicit sampling choice. Intersect that Window with the containing Present, then derive the
matching source-frame span from the authored sampling relation. Subtract the Present's start to obtain
Present-local video sampling intervals. Moving or reframing a video does not itself choose or restart
playback. The same media can independently feed a peer Audio Clip when the Film should retain its sound.

Project each independently meaningful event before rendering. Convert its program frame to the
containing Present's local frame once, then animate relative to that event. Keep source sampling
based on the returned source span; neither the event's local offset nor the viewport's movement
replaces it. [Component design](component-design.md#let-meaning-drive-the-behavior) distinguishes these
inputs from internal motion details.

A reusable scene might expose `during={explanation}` for its lifetime and
`reveal={demonstrate}` for its layout change. An upstream Narrative projector publishes
these independently; the Producer receives a Window and an Instant. The installed Distribution's
`examples/semantic-composition/packages/responsive-explainer` shows this complete package: video
moves from full screen to a side viewport while a diagram enters, with Caption available as a peer.

The HTML visual format belongs to the renderer package. `hypit.html-visual@1` runs in the
HTML renderer browser; another renderer implements the formats it supports.
