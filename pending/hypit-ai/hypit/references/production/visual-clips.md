# Place pictures through Visual Track

Read this when an image, normalized video or compositable Surface should appear in the finished
picture. [Media preparation](media.md) owns source facts, [spatial layout](spatial.md) owns destination
Frames, and [timing](timing.md) owns absolute and projected time.

## Place one ordinary Clip occurrence

```text
Visual Clip = picture source + absolute Window + Frame
            + z + spatial mapping + source-time + optional treatment + optional Motion
Visual Track = a set of Visual Clips
```

```svml
<visual:Motion id="photo-push">
  <visual:Pose at="start" scale="1.08" easing="ease-out"/>
  <visual:Pose at="end" scale="1"/>
</visual:Motion>

<visual:Track id="picture" timeline={program.timeline}>
  <visual:Clip id="speaker" media={speaker-media.media}
    during={program.speaker} frame={layout.full} z="10" fit="cover"/>
  <visual:Clip id="photo" image={product} extent={product-extent}
    during={example} frame={layout.detail} z="20" fit="contain"
    treatment={look.visual.still} motion={photo-push}/>
</visual:Track>
```

An A-roll picture, B-roll insert, generated shot and imported graphic use the same occurrence model.
The Clip explicitly chooses what becomes visible, even when the source earlier supplied Timeline
extent or semantic evidence.

A Clip takes one source form:

- `image` with its pixel `extent` for a still;
- normalized `media` for timed picture;
- a typed `surface` for compositable pixels.

`during` accepts a resolved Window, including the complete `timeline.window`. Declare any direct
clock range as a named Timeline child or standalone `time:Window` before using it here.

Ordinary fit and alignment attributes derive the source-to-picture SpatialMap2D. Supply an authored
`space:Map` through `mapping` when the production already owns the exact relation. The Clip Frame
remains the treatment and clipping boundary. [Spatial layout](spatial.md#map-a-source-plane-and-treat-its-frame)
explains the relation.

## Keep destination time and source sampling distinct

The Window states when the occurrence contributes. For moving media, omission uses bounded native
playback from source start; source that ends before the Window leaves the remaining picture empty.

Use `visual:Map` children for another relation. Target bounds select Clip-local time; source bounds
select source frames; paired anchors and an exact rate relate the two clocks. `wrap-from` and
`wrap-until` make a source interval periodic. Multiple non-overlapping Maps form one piecewise
relation and retain transparent gaps.

Use rate zero to hold a frame and a negative rate for reverse traversal. A Map with source and
target bounds but no rate, anchors or wrap fits the selected source interval across its target.

```svml
<visual:Clip media={shot.media} during={story.outro} frame={layout.full} z="10">
  <visual:Map target-at="end" source-at="end" rate="1"/>
</visual:Clip>
```

Stills have no source clock and therefore use no temporal Map. `space:Map` and `visual:Map` answer
different questions.

Use distinct `z` values when relative paint order matters. Equal-`z` Clips are legal and use stable
declaration and identity order. Sampling changes which source pixels appear; Pose or `motion` moves
the complete framed occurrence.

## Put shared behavior in a component

A continuing presenter, crossfade, slideshow or coordinated reveal owns behavior across several
occurrences. Implement that relationship as a project or reusable component, using Visual Track
builders where useful and publishing a VisualTrack for Film.

Components can define local author vocabularies that fit their shared content. Caption, for example,
uses a persistent document and timed Uses; a presenter component may similarly expose its own roles
and treatments. These are component relationships, not requirements for an ordinary Clip.

Visual Track publishes `.visual` for Film and `.program` for declared tooling. It emits picture only;
place desired sound independently through [Audio Track](audio-clips.md). [Track authoring](track-authoring.md)
explains how a component publishes a visual contribution.
