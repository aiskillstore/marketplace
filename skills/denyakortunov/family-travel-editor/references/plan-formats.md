# Narrative scene → technical shot plan

`project.py init` creates `scene.json`: a narrative worksheet. It has the scene's purpose, confirmed context, open questions, setup, action, result and ending. It is **not input to the XML/preview helpers**. Do not invent timings to make an empty template render.

After watching candidate ranges and confirming the scene, create a separate `shot-plan-v1.json`. Resolve each narrative shot to a real file and measured frame range. The current helper schema is:

```json
{
  "name": "First scene v1",
  "fps": 25,
  "width": 640,
  "height": 360,
  "shots": [
    {"path": "shot-1.mp4", "in": 0, "out": 100, "source_frames": 100, "role": "setup"}
  ]
}
```

- `fps`: integer 24, 25 or 30; sources must share that constant rate. No 23.976, 29.97, variable-rate, speed changes or mixed-rate conform here.
- `width`, `height`: positive integer dimensions shared by the sources.
- `shots`: nonempty ordered list. `path` is relative to the supplied media root and must remain inside it.
- `in` is inclusive, `out` exclusive; both are source frame numbers, not seconds or SMPTE timecodes. `source_frames` is the measured total number of source video frames.
- Optional `role` explains the editorial purpose; helpers do not interpret it.

At 25 fps, source `[25, 75)` contains 50 frames = 2 seconds. Output positions are consecutive sums of selected lengths. The first example contains three 100-frame shots (12 seconds); shortening only the middle to 50 produces 250 frames (10 seconds).

The XML helper validates plan structure, ranges and paths, but **does not probe source media**. The preview renderer probes and counts actual video frames and rejects incompatible dimensions/rates/counts, rotation or pixel aspect. Averages alone cannot fully certify constant frame rate; inspect/normalize questionable phone footage into separate copies before using either helper. Never modify source files to satisfy a template.

Audio is absent from both outputs. Preserve dialogue and audio separately before any real editorial use; a silent picture preview is not a complete scene or a native project.
