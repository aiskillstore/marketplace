# Preparing media for a production

Read this when admitting files, connecting generated media, choosing streams, or editing a clip
before using it in a component or a model reference. [Visual Clips](visual-clips.md)
owns independent picture placement and playback; [Tracks](tracks.md) routes other content relationships.
For a source video at a link, read [video download](video-downloads.md).
For acquiring website screenshots, page recordings or local HTML graphics, read
[browser capture](browser-capture.md).

## Choose preparation from the intended use

Keep source facts, preparation and use distinct:

| Material or use | What the next consumer needs |
| --- | --- |
| Still image, including a transparent cutout | Bytes and its real dimensions for independent placement; the component supplies its display Window. |
| Video, with or without audio or transparency | Selected streams, local duration and a frame clock when entering prepared-media composition inputs. |
| Audio | The selected audio stream and prepared local time; its role can be a Script performance, music, narration or an effect. |
| Compositable surface | Its declared pixels, extent and any animation information; use the producing package's output directly. |
| Code-authored text, shapes or a scene | The component's data and resources; it can draw directly without an intermediate media file. |
| A model reference | The exact image, video or audio input accepted by that model's Surface; normalization is not a universal prerequisite. |

Files, generated Outputs and earlier Results are sources of these values. A reference need not
appear in the film. A video containing a person is not automatically semantic; the author establishes
that relation by aligning one Script Segment to its local domain. [Runs](runs.md) owns explicit Result
reuse. [Image operations](image-operations.md) owns still-image preparation.

Normalization establishes moving media's frame clock, local domain and selected picture/audio
streams. `NarrativeAlignment` separately adds one Script Segment's local word/boundary positions.
[Timeline construction](timeline.md) may consume the prepared Extent. A domain projector may consume
the local domain with an equal-length Timeline Window. Neither operation changes the media value.

## Files and generated Outputs

File declarations publish a **Blob**, a reference to the file's bytes, under their own id:

```svml
<import as="asset" from="@hypit/media@1"/>

<asset:Image id="product" src="./assets/product.png"/>
<asset:Video id="performance" src="./assets/performance.mp4"/>
<asset:Audio id="music" src="./assets/music.wav"/>
```

Use `{product}`, `{performance}` and `{music}` as inputs that accept these Blobs. A model
Surface can publish the same kind of value under an output path, such as `{portrait.image}` or
`{opening.video}`. The package vocabulary gives that path. File paths are relative to their Source;
[project setup](../creation/project-files.md#establish-the-project-boundary) explains the declared project boundaries.

A supplied recording can be a reference for new work, an independent picture or sound, or material
the finished work retains. When the intended passage keeps its actual recorded delivery, that
recording can carry the Script without regenerating it. If only part of the file belongs in the
work, prepare a new file locally with `hypit media cut`:

```bash
hypit media probe assets/recording.mp4
hypit media cut assets/recording.mp4 --start 12.4 --end 19.8 --to assets/opening.mp4
hypit media cut assets/recording.mp4 --keep 12.4:15.7 --keep 16.2:19.8 --to assets/opening-edited.mp4
hypit media cut assets/voice.wav --keep 0.3:4.1 --keep 4.6:9.2 --to assets/narration-edited.wav
```

The first form retains one interval; repeated `--keep` joins selected parts of the *same* recording.
The command keeps existing audio and picture together and can write an ordinary MP4 or audio-only
WAV. Import that output as `asset:Video` or `asset:Audio` for its intended use. If the edited
delivery is a Script performance, normalize it; align its local domain when another contribution
needs positions inside that performance, as described below.
Independent footage can instead enter a Visual Clip or another visual component, with source sound included
when the work needs it. A file cut does not choose Script or Segment boundaries. The installed Video
CLI README owns exact options and output behavior. `hypit transcribe` accepts either audio or video
when a transcript helps inspect the recording; its word times refer to that input file, while a
retained edited performance receives its own semantic alignment in the Build when the composition
consumes that timing.

An image reference can enter a model directly. A still placed as a Visual Clip needs its actual
IntrinsicExtent as well. Inspect its dimensions with `hypit media probe <file>` and declare them
with `space:Extent`; [spatial layout](spatial.md) explains extent versus destination Frame.

## Prepare moving media on the program clock

Clips can arrive with different frame rates, several streams or picture and sound of different
lengths. Normalize selects the intended streams and expresses them on the program's frame clock,
so their lengths and later playback can be combined precisely.

The following excerpt prepares a performance and an independent soundtrack:

```svml
<import as="mediaop" from="@hypit/media-operations@1"/>

<time:Clock id="clock" frame-rate="30"/>
<mediaop:Normalize id="performance-media" source={performance} clock={clock}
  video="primary-moving" audio="default" span-authority="video"/>
<mediaop:Normalize id="music-media" source={music} clock={clock}
  video="none" audio="default" span-authority="audio"/>
```

The Clock is an authored rate; the prepared media supplies the resulting length. Share the Clock
across media that will join one program.

- `video` selects the moving-picture stream, or `none` for audio-only material.
- `audio` selects the embedded audio, or `none` when the material should carry no sound.
- `span-authority` chooses which stream determines the prepared duration when stream lengths differ.

`primary-moving` excludes attached cover art. The default audio selection uses the default or
unambiguous audio stream; select an explicit stream when the container has several intended choices.
`hypit vocabulary @hypit/media-operations --tag Normalize` gives the supported selectors.

Normalization inspects the bytes and produces `{performance-media.media}`: a SynchronizedMedia value
with an exact local frame count, optional picture and optional audio on the chosen Clock. Audio is
prepared as a 48 kHz render stem with its level preserved. Balance, fades and music ducking remain
mix decisions in [Audio Track and sound mix](../playbooks/craft/sound-mix.md).

## Associate a performance with Script when its timing is consumed

Script preserves wording and meaningful events for performance-led work. When Caption, semantic
picture changes, sound events or another consumer needs their actual positions, alignment locates
them on the accepted media's local domain:

```svml
<import as="whisperx" from="@hypit/whisperx@1"/>

<whisperx:Alignment id="opening-semantic" narrative={story}
  segment={story.segment.opening} media={performance-media.media}
  domain={performance-media.domain} language="en"/>
```

Set `language` to the performed language supported by the selected WhisperX Endpoint. WhisperX
supplies timed evidence; deterministic alignment associates it with Script. The result
`opening-semantic.alignment` is `NarrativeAlignment`: Segment and Token boundaries on the named local
domain. It carries no media and no Timeline position.

Combine the alignment, its complete local domain and the equal-length Window in one explicit
semantic projection:

```svml
<time:Timeline id="program" clock={clock} end="opening.end">
  <time:Window id="opening" from="start" for={performance-media.extent}/>
</time:Timeline>
<semantic:Projection id="story-time" narrative={story} timeline={program.timeline}>
  <semantic:Map alignment={opening-semantic.alignment}
    domain={performance-media.domain} window={program.opening}/>
</semantic:Projection>
```

After projection, picture and sound use the ordinary normalized media with explicit absolute Windows.
They do not retain or inspect this semantic relation. Audio-only A-roll uses the same projection chain
without a dummy picture.

## Project a wordless Segment when its identity is consumed

A wordless Segment can align directly to its complete local domain without transcription when a
consumer needs that Segment's boundaries. The alignment contributes the real Segment start/end
identities and no Tokens; the media Extent can construct Timeline without it. A silent action inside
that passage needs its own authored or measured event if another component must respond to it.

## Give a still a duration when that is its role

A still B-roll Clip already occupies an authored Window. To make one or several images into a
time-bearing clip, use StillVideo:

```svml
<import as="mediaop" from="@hypit/media-operations@1"/>

<mediaop:StillVideo id="opening-still" source={product} duration="6s" clock={clock}/>
<mediaop:Normalize id="opening-media" source={opening-still.video}
  video="primary-moving" audio="none" span-authority="video" clock={clock}/>
```

StillVideo produces a video-only Blob. Multiple `media:Still` children divide the authored
duration by their optional weights. Normalization then makes that clip usable as prepared moving
media. Choose it when one or more held images need to become a time-bearing video Artifact; its role
is assigned by the downstream Source relationships just like any other video.

## Edit bytes at an explicit point in the graph

```svml
<mediaop:Transform id="edited" source={performance-media.media}>
  <mediaop:Trim tail="0.25s"/>
  <mediaop:Retime rate="1.05"/>
</mediaop:Transform>
<mediaop:ExtractAudio id="voice-reference" source={edited.video} audio="default"/>
<mediaop:ExtractFrame id="frame-reference" source={edited.video}
  video="primary-moving" at="last"/>
```

Transform applies its operations in order. These Outputs are Blobs; normalize an edited
clip again when feeding it into a prepared-media input, and realign the edited performance when its
timing changed and downstream consumers use that alignment. Extracted audio or a frame can directly
feed a compatible model reference port.
`ExtractFrame` also accepts `first`, `frame:<index>` and `time:<seconds>`.

Use graph operations for repeatable preparation belonging to the production. `hypit media` commands
are useful for inspection and deliberately exported evidence. Image geometry changes and compositing
have one installed vocabulary in `@hypit/image-operations`; select
the operation that matches the asset's intended use.

## Keep original and processed material explicit

A crop, background removal or flattened composite produces a selected asset. Normalization prepares
that output; retain the original whenever the production may still need its pixels. A transparent
video enters the same normalization and Visual Clip path as opaque video. A circular Clip or
rounded Frame instead masks Clip geometry; it does not remove the source background.

When original and processed pictures both appear, retain both and connect each as an explicit media
input. If a picture-only transformation preserves the same frame correspondence, a project
preparation component may reuse the accepted local domain and alignment while publishing a new
visual source. This is an authored relation, never automatic variant inheritance.

For a moving portrait, the installed `@hypit/volcengine-matting` package exposes `Portrait` with
`source={performance.video}` and publishes `cutout.video`; query its vocabulary and README for
transparent formats and current Provider support. Existing transparent material can enter Normalize
directly. Removing a still reference's background does not establish transparency in generated video.

Choose an operation for the material it actually accepts: a moving silhouette needs a video matte
or suitable keying operation; deterministic Image Operations do not silently turn it into one.
[Video direction](../playbooks/craft/video-direction.md#prepare-footage-for-subject-isolation) explains
preparing and judging footage for that use. A fixed flattened arrangement of still images can use
[Image Compose](image-operations.md#flatten-a-fixed-still-image-arrangement) when that is the desired output.

Operation order matters to the selected implementation. The current local Media Provider's Normalize
preserves input alpha, while its Transform emits opaque MP4. When using that Transform for trimming
or retiming a cutout performance, perform it before matting. Read the selected operation's output
behavior rather than assuming every video operation preserves transparency.

Trimming, retiming or replacing the performance changes its local temporal relation and requires a
new local domain. Prepare new semantic timing as well when downstream consumers use it.
[Reuse boundaries](authoring.md#reuse-produced-work-explicitly) explain which completed Output can
remain selected.

Choose source proportions and framing for the actual footage the work needs. A full-frame spoken
piece can start from the final aspect ratio; a later inset or split does not dictate the generated
source shape. [Spatial layout](spatial.md) owns destination geometry. Image and video direction own
the camera view; pass those requests visible, performable facts rather than unconverted MG instructions.
