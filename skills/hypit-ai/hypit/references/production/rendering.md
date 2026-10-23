# Composition and rendering

Read this when assembling the deliverable or rendering a frame interval for review. [Tracks](tracks.md)
explains the contributing layers; [Runs](runs.md) explains selecting existing media for this execution.

Components author the picture and sound contributions. Film assembles the selected contributions
with Timeline and Canvas into a Composition. Rendering evaluates that composition over a frame
interval and produces the encoded media. The
same composition can therefore be inspected in Studio, rendered in part, or rendered as a whole.

## Assemble the picture and sound

With the named inputs already declared:

```svml
<import as="film" from="@hypit/film@1"/>
<import as="html" from="@hypit/html-video@1"/>

<film:Film id="main" canvas={canvas.canvas} timeline={speech.timeline}
  appearance={look.film.main}>
  <film:Track source={picture.visual}/>
  <film:Track source={mix.audio}/>
  <film:Track source={coverage.visual}/>
  <film:Track source={captions.visual}/>
  <film:Track source={music.audio}/>
</film:Film>
<html:Video id="final" composition={main.composition} timeline={speech.timeline}/>
```

An example Film Recipe is `film.main { background: #18212A; }`. Canvas supplies the picture dimensions;
the Timeline supplies program time. `picture.visual` is a Visual Track output and `mix.audio` is an
Audio Track output. Include every wanted output explicitly: placing the same normalized media in a
Visual Clip and an Audio Clip is what makes both its picture and its audio present.
Layer order is authored in the Visual Tracks' Presents, so moving these Film children does not
reorder the picture.

`main.composition` is the assembled work, usable in Studio. `final.video` asks for an encoded video.
A compatible Composition from another component can also feed the HTML Video Surface. Pure A-roll may
need only one Visual Clip and one Audio Clip, with Caption when wanted. Additional coverage
and graphics in this excerpt illustrate optional independent contributions.

## Compose an authored animation

A Film needs a time axis, whether or not it contains speech or prepared media. For a speech-led piece,
continue to pass `timeline={speech.timeline}`: it provides both the complete film time and the
context in which Tracks resolve Script references. For a pure MG piece, author a Timeline with an
explicit end and pass it to the components, Film and HTML Video:

```svml
<import as="time" from="@hypit/timeline-author@1"/>
<time:Clock id="animation-clock" frame-rate="30"/>
<time:Timeline id="animation" clock={animation-clock} end="8s">
  <time:Instant id="question" at="0.5s"/>
  <time:Instant id="answer" at="2s"/>
</time:Timeline>

<!-- conversation is the project's own visual component. -->
<chat:Scene id="conversation" timeline={animation.timeline} within={canvas.bounds} font={font}
  during={animation.window} title="Launch crew">
  <chat:Message id="question" sender="Maya" side="left" at={animation.question} text="Ready?"/>
  <chat:Message id="answer" sender="Leo" side="right" at={animation.answer} text="Let's go."/>
</chat:Scene>
<film:Film id="main" canvas={canvas.canvas} timeline={animation.timeline} appearance={look.film.main}>
  <film:Track source={conversation.visual}/>
</film:Film>
<html:Video id="final" composition={main.composition} timeline={animation.timeline}/>
```

The example assumes the Canvas, font, Film Recipe and project package are declared. Timeline's `end`
accepts seconds, milliseconds or frames and must end on a frame boundary. `Clock` remains the
separate duration-free input for normalizing real media. Drawing code produces the picture at each
requested frame; the Film's background supplies the canvas color. With no AudioTrack, the delivered
video is silent. Render ranges and worker settings apply in the same way as for spoken work.

Media, Typography, Audio and the graphic Tracks accept this same Timeline. Visual and Audio Clips
receive ordinary media and Windows explicitly; the Timeline does not contain or discover media. Caption
uses its speech-linked document; authored chat text belongs to the chat scene. The working example
`examples/semantic-composition/chat.svml` and its `@example/chat-scene` package show the complete
code-only composition, including scrolling and arbitrary message arrivals.

## Choose a render interval in frames

```svml
<html:Video id="detail" composition={main.composition} timeline={speech.timeline}
  start-frame="240" end-frame-exclusive="360"/>
```

Both bounds refer to the original program's frame clock. The interval includes frame 240 and ends
before 360: 120 frames, or seconds 8–12 at 30 fps. Omit both bounds for the whole program. For a
rational frame rate, compute seconds from its numerator and denominator rather than rounding the
rate first.

The original animation time remains intact, and picture and sound use the same interval. A short
Run can target `detail.video` while the normal Run continues to target `final.video`.
For this example, the renderer evaluates the original page at seconds 8–12 and encodes those frames
as a four-second clip starting at zero. An animation already in progress at second 8 keeps that state.

**The range limits final rendering. Upstream generation still follows the selected graph.** Keep
the Run Candidates for usable normalized media and alignment evidence when inspecting a Caption or MG revision.
Inspect `hypit plan` for the work that remains before submission. [Authoring](authoring.md#reuse-produced-work-explicitly)
explains choosing the reuse boundary.

## Execution and capacity

The HTML program compiler lowers the selected Composition, and the selected rasterization Provider produces its picture. Timeline audio is prepared
from the included AudioTracks, then picture and sound are muxed into the delivered file. A Runtime
can bind these capabilities to different compatible Endpoints.

Before the first local render, or when browser startup reports a missing executable, follow
[browser preparation](../environment/local-tools.md#prepare-the-local-rendering-browser).
That selected Provider owns browser installation and download configuration.

The local HTML Provider supports range requests and can capture different parts of one
program with several browser workers. Browser selection, download settings and worker capacity
belong to that Provider's Profile configuration. [Runtime profiles](../environment/profile.md)
and the selected Provider's README own those choices; the Source retains the same render declaration.
Another Provider declares the request forms its deployment supports.

A short interval reduces frame capture and source-frame extraction, but still prepares the document's
declared assets and validates typed Surfaces. Extra browsers help only while the machine can use them;
preparation and final encoding contribute separately. Reusing media through the Run avoids generation work; it does
not preserve a previous render's temporary preparation.

For a local composition change, use [snapshot](snapshots.md) first to inspect the changed
relationship and its handoffs in Studio's current `HtmlProgram`. Keep accepted material selected in
the Run. Range rendering supplies an encoded clip when that is needed; render the complete
deliverable when the composition is ready.
While rendering, communicate the current phase and meaningful progress. The Provider reports
decoding, browser startup, capture, encoding and storage; `hypit logs <build-id>` preserves their
timings and execution details when a slow or failed stage needs investigation.

Image decode and declared-font loading failures stop capture with an error. Repair the named
resource in its owning Source or component, then retry with accepted media retained in the Run.

A local render timeout ends that execution attempt and releases capacity after its work has stopped.
Its failure and already completed Outputs belong to the Build Result. Continue through a new Run
and Build that explicitly reuse the available media, as described in [Runs](runs.md).

Use [Builds and Results](builds.md) to submit, follow and retrieve `final.video` or `detail.video`.
Use [Review](review.md) to judge the observed interval or complete deliverable against the intended work.
