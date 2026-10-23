# Inspect the current picture

Use `hypit snapshot` first when the question concerns an existing production's visible state,
layout or motion sequence. It captures selected frames of the current picture through the
Profile's `rasterize-frames` Endpoint. Studio playback supplies motion with sound; an encoded video
supplies evidence about the delivered file. Choose the view that establishes the relationship.

## Capture the work already open in Studio

Open the actual Run using [Studio](studio.md). After its current preview is ready:

```bash
hypit snapshot --studio http://localhost:5191 \
  --at-frame 240 --to evidence/comparison-detail

hypit snapshot --studio http://localhost:5191 \
  --at-frame 240,255,269 --grid 3x1 --cell 480 --to evidence/comparison-states

hypit snapshot --studio http://localhost:5191 \
  --start-frame 240 --end-frame-exclusive 270 --step-frames 1 \
  --grid 4x3 --cell 480 --to evidence/comparison-motion
```

Use the address of the existing Studio session and frames located in its current `HtmlProgram`. The examples
demonstrate the options. Locate meaningful events through Script, Timeline or the Studio playhead;
pass their resulting frame positions to the observation command. Frame selection does not change
the authored timing relationship.

Studio supplies its already compiled `HtmlProgram` and the material selected by the Run.
This preserves declared fonts, images, video sampling, transparent Surfaces and resources used
inside a component's HTML visual. The command sends one immediate request, keeping the original
`HtmlProgram` clock and component-local clocks. It writes images directly into the chosen directory.
There is no new Build, material generation or video encoding in this call.

Use `--runtime <profile>` and `--project <project>` when the invocation needs an explicit selection;
otherwise run in the project that already selected its Profile. The command names the selected
Endpoint before execution. If several Endpoints offer frame capture, select one with the Profile's
`@hypit/html-program@1#rasterize-frames` binding. Browser preparation remains with that Provider:
[local tools](../environment/local-tools.md#prepare-the-local-rendering-browser).

## Read frames at the scale the question needs

- `--at-frame` chooses one frame or a strictly increasing list of frames.
- A range includes `--start-frame` and excludes `--end-frame-exclusive`. `--step-frames 1` retains
  every frame. Frame indices start at zero on that `HtmlProgram` clock.
- Every selected frame is saved as a full-size PNG. Open one for typography, edges and geometry.
- `--grid columnsxrows` adds paginated contact sheets. `--cell` chooses the width of each picture;
  labels sit below it and give its original frame index and time. The full-size PNGs remain available.
- `--json` reports the output paths and frame positions for subsequent inspection.

Widen the interval to understand a handoff, follow every frame to understand a movement, and enlarge
the image to judge small detail. Compare the corresponding event in reference and production;
different performances can put that event at different seconds. Revisit the whole passage in Studio
to hear and feel how the observed states work together.

## Existing HTML and source video

An already materialized HTML renderer HTML file can also be the input:

```bash
hypit snapshot ./picture/index.html --at-frame 240 --to evidence/html-detail
```

The HTML carries its compiled frame clock and frame-sampling declarations. Its directly referenced
media and fonts travel with the request; scripts and styles are inline. An HTML URL is accepted too.
For a current Studio work, prefer `--studio`: its compiled document also retains resource declarations
inside JavaScript data and the full typed Surface input. Snapshot is an `HtmlProgram` frame operation;
[browser capture](browser-capture.md) owns screenshots of ordinary websites and applications.

For an existing source video or encoded Result, use the media commands. Native-frame extraction
decodes each chosen interval once and retains the source's actual timestamps, including variable
frame rates:

```bash
hypit media tiles reference.mp4 --start 8 --end 9 --every-frame \
  --columns 4 --rows 3 --cell 480 --to evidence/reference-motion
```

`media frames --every-frame` saves individual images; `media tiles --ranges ranges.json
--every-frame` follows several selected intervals. `--transcript` adds the words around each
actual frame. [Reference understanding](../creation/reference-video.md) connects these views to
coarse and fine observation.

## After a composition change

Keep accepted material selected in the Run, let Studio compile the updated Source, then capture the
affected states and their handoffs. Carry discoveries back to the owning Source, component or
Treatment. This is the preferred picture-review path. Use a
[range render](rendering.md#choose-a-render-interval-in-frames) when a short encoded video with sound
is the evidence or deliverable needed; render and inspect the full file for final export.
