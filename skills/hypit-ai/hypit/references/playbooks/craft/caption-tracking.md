# Caption above a moving head

Read this when the user's reference visibly uses Caption that follows a speaking person's moving
head, or the user asks for that treatment. Ordinary Caption uses its family's layout and Style
placement; the presence of a face does not by itself call for head boxes. The optional measured or
authored regions answer where this particular speaker's words should appear in the actual picture.

## Resolve who, where and when

Script Role identifies who says the Cue. The intended view of that person in the final composition
determines where the Cue follows them; GVI face-track ids do not establish identity. The speech and
the directed Caption treatment determine when it appears. In ordinary turn-taking, the previous
speaker's Caption hands off as the next speaker starts. Their face remaining visible is not a reason
to keep their earlier words on screen.

Measure whichever available picture lets those relationships be mapped accurately:

- A supplied or prepared clip gives source-local positions that must follow its placement,
  playback, crop and any moving view into the composition.
- A composed view already contains its camera framing and program time, provided graphics do not
  obscure the person being measured.

Retain the relation between the measured source and its use. A source timestamp can change meaning
after trim or retiming, and a face box can move after crop or reframing. A presenter shrinking into an
inset needs positions that follow that actual transformation. When the same person appears in
several views simultaneously, choose the view this Caption follows. Fine accepts one region per Role
per frame; several simultaneous text placements need an explicitly authored presentation.

Leave room for the complete Cue and nearby graphics. A correctly measured head can still be an
awkward place to put a long phrase; the work may instead use ordinary Caption placement there.

## Read face observations

The worked method used Google Video Intelligence. Its face feature can return bounding boxes when
`FACE_DETECTION` is requested with `includeBoundingBoxes` enabled; facial attributes are unnecessary
for this placement task. Use the installed tool or the provider's
[face-detection example](https://docs.cloud.google.com/video-intelligence/docs/samples/video-detect-faces)
for actual invocation and existing authorization for any paid request. Another suitable detector or
manual measurement can supply the same authored data. The stable Hypit input is the resulting
Region Evidence, so detector invocation can remain an external, project-side preparation step.

GVI's timestamped boxes are observations, not Script Roles or ready-to-use Hypit head tracks. Its
[response schema](https://docs.cloud.google.com/video-intelligence/docs/reference/rest/v1/AnnotateVideoResponse#TimestampedObject)
expresses `timeOffset` relative to the input video and the rectangle as `normalizedBoundingBox`.
Use all relevant observations, not just the first box printed by a sample program.

Treat the returned face tracks as candidate observations. Inspect representative frames from each
track and associate useful fragments with the intended Script Role. A detector track is not a global
person identity: a cut can split one guest across several tracks, and one shared shot can contain
several people. Combine the fragments that visibly belong to the Role in final program time. Selecting
the first or largest face alone can attach the guest's Caption to the interviewer.

## Map observations into the composition

Transform the useful observations into ordinary project data, with these decisions explicit:

- **Clock:** sample the observations on the Timeline's frame clock using the actual source playback
  mapping. For prepared media on the same clock at native speed, add its actual placement start,
  including any gap or overlap. Apply any source trim or rate change when measuring other footage.
  Final-video measurements already use that rendered program's clock.
- **Geometry:** convert detector edges to `[x, y, width, height]` using width `right - left` and height
  `bottom - top`. If measurement used another resolution, crop, inset or split-screen panel, map the
  box through that actual placement before normalizing it to the final Canvas. Update this mapping
  through a moving or resizing view; a single fixed rectangle cannot describe that movement.
- **Head extent:** expand the face region to include the relevant hair, hat and desired clearance.
  For face `(x,y,w,h)`, authored padding fractions can produce
  `(x - pL*w, y - pT*h, w*(1+pL+pR), h*(1+pT+pB))`. Choose those fractions from the visible head;
  there is no universal face-to-head multiplier. Keep the resulting region valid inside the Canvas.
- **Missing observations:** make any interpolation or smoothing an explicit external preparation
  choice within a continuous shot and the same person. Inspect it, stop at cuts and occlusion, and
  write `null` when no usable region exists. Fine does not invent a missing box.

Each Role track's final array has exactly one box or `null` per program frame. Keep the actual array
in a project Recipe such as `tracking.svs`. A project script can perform the transformations using
explicit source, clock and geometry inputs. Changing the camera use can require remapping positions.

## Place only the intended speaker's Caption

Script and Caption already connect a Role's words to their timed Cue; the region input supplies the
head position for the frames where this treatment follows them. A `null` region also hides that
Role's Cue on that frame. Use the Cue's presentation window or `null` regions to end its appearance
at the intended handoff, including when a Style's tail would otherwise leave the old words over the
next speaker. When the person is absent, obscured or in another camera view, choose whether the
Caption ends or uses an authored ordinary placement. Neither a detector track nor the mere presence
of a listening face extends someone's speech.

[Caption presentation](../../production/caption-presentation.md) owns Style coverage and hiding.
A Role with no region evidence keeps ordinary Style placement; a `null` inside an existing series hides
the Cue rather than switching placement automatically. A deliberate tracked-to-ordinary change can
use explicit Caption Uses or separate Tracks with the same Script and Timeline.

For example, this is a three-frame data-shape illustration, not a ready timeline for a real video:

```svs
heads.default {
  series: [
    {"id":"GUEST","regions":[[0.12,0.09,0.20,0.26],null,[0.13,0.10,0.20,0.26]]}
  ];
}
```

## Connect the placement to Caption

```svml
<import as="region" from="@hypit/region-evidence@1"/>
<region:Evidence id="heads" within={vertical.bounds} timeline={speech.timeline}
  recipe={tracking.heads.default}/>
<caption-fine:Caption id="captions" document={story.caption} timing={story-captions}
  timeline={speech.timeline} within={vertical.bounds} regions={heads}>
  <caption-fine:Use style={caption-style}/>
</caption-fine:Caption>
```

The Region Evidence series ids match Script Roles. Fine places a single-Role Cue at that region's top
center; `anchor-x: center` and `anchor-y: bottom` put the Cue above it. The Style still owns its width,
font and motion. Supplying `regions` requires every Cue on that Track to have one Script Role, even
when that particular Role uses fixed placement. Author the relevant Role Cues in Script. The
`@hypit/region-evidence` and `@hypit/caption-fine` READMEs own the exact data behavior.

## Inspect the actual placement

Use Studio or [snapshots](../../production/snapshots.md) to inspect the current picture around
camera changes and speaker handoffs. Check the first and last frames of each tracked Cue, the whole
Cue's clearance above hair or hats, top-edge clipping and collisions with graphics. Play the passage
with speech to judge jitter, wrong-person jumps and reading rhythm. When source timing or visual
presentation changes, remap the affected observations rather than carrying stale coordinates forward.
