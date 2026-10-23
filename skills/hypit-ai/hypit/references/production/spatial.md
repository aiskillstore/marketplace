# Spatial layout

Read this when positioning or fitting media, text or a project component. Timing is explained in
[Timing](timing.md); it is independent of these coordinates. Read
[component design](component-design.md) when deciding which content shares layout or motion;
[image direction](../playbooks/craft/image-direction.md) owns the source camera view. This page owns
the destination geometry for Visual Clips and project scenes alike.

## Canvas, extent and destination

The Canvas gives the final image's pixel dimensions. The shared `@1` picture-plane convention gives
the coordinate basis. Introduce Frames and
component scopes where they help organize the picture; they need not tile the canvas or remain
separate rectangles. Components can overlap, share motion and own local trees. Each visual
contribution publishes Presents with its own paint order.

An IntrinsicExtent gives a source image's actual dimensions. A Frame gives the destination rectangle
a consumer should occupy. A landscape image can retain its real extent while appearing in a portrait
composition. An A-roll source has no prescribed Frame or crop. For performance remaining mostly
full-screen, its intended final aspect can guide source direction; later insets or splits remain
visual placement choices. Translate required source framing into visible camera facts before generation.

```svml
<import as="space" from="@hypit/spatial@1"/>

<space:Canvas id="canvas" width="1080" height="1920"/>
<space:Extent id="photo-size" width="1600" height="1200"/>
<space:Frame id="content" within={canvas.bounds}
  left="6%" top="8%" right="94%" bottom="90%"/>
```

Coordinates start at the top left; x increases rightward and y downward. Frame edges are positions
from the parent's left/top, so `right="94%"` is the right edge at 94% of parent width. It leaves a
6% margin. A percentage on the x axis uses the parent width; on y it uses parent height. Nesting
changes that reference rectangle. Pixel lengths use `px`.

## Anchor an object or preserve its aspect

```svml
<space:AnchoredFrame id="label" within={content}
  x="50%" y="85%" width="80%" height="12%" anchor="center"/>
<space:AspectFrame id="photo-frame" within={content}
  x="100%" y="0%" width="45%" aspect={photo-size} anchor="top-right"/>
```

AnchoredFrame pins the named point of a sized rectangle to x/y in the parent. AspectFrame derives
one dimension from the other: specify width or height, plus an Extent or a ratio such as `4/3`.
An `offset-x` or `offset-y` is an additional pixel nudge. An anchored frame can extend beyond its
parent when that is the intended composition.

For text, `space:Point` supplies a pixel position and `space:Path` supplies authored Move/Line/curve
commands. [Fonts and text](fonts-and-text.md) shows which Typography placement consumes each.

## Map a source plane and treat its Frame

Visual Clips keep three different spatial facts separate:

- The source's **IntrinsicExtent** bounds its own local pixel plane.
- A **SpatialMap2D** maps positions from that local plane into the program picture plane.
- The destination **Frame** owns the Clip's outer treatment and clipping boundary.

Ordinary `fit` controls derive the SpatialMap2D after the source Extent and Clip Frame are both
known. The resolved Visual Program keeps
that mapping, not a parallel fitted rectangle. A still image therefore needs an Extent; prepared
moving media and compositable Surfaces already carry their dimensions. Border and padding produce a
deterministic inset used by the fit calculation, rather than another independently authored Frame.

For example, with no border or padding, a `1600 × 900` image fitted into a `600 × 600` Frame becomes
`600 × 337.5` under `contain`, leaving room above and below when centered. Under `cover`, it becomes
about `1066.7 × 600`; a frame clip shows the middle square. Moving the destination moves the whole
Clip; changing content alignment changes which part of that image occupies the square.

Choose ordinary fitting directly on the Clip:

- **contain** keeps the complete image visible and may leave space around it;
- **cover** fills the destination and may crop the image;
- **stretch** changes the source proportions to occupy the destination.

The Visual Track vocabulary also exposes `fit-width`, `fit-height`, `native` and `scale-down` when one
dimension or the source's own pixel size should determine the scale. The default is centered
`contain`. `fit: stretch` changes only spatial sizing. Timed-source sampling is the independent
partial relation documented in [Visual Clips](visual-clips.md); it is never inferred from spatial fit.

When fit vocabulary is too narrow, author the mapping itself and pass it with `mapping`. This is the
open spatial escape hatch; it can rotate, skew, reflect or place a source outside its Clip Frame.
The matrix maps source-local pixels directly into program-picture pixels:

```svml
<space:Map id="turned" xx="0" xy="-0.5" yx="0.5" yy="0" tx="920" ty="180"/>

<visual:Track id="graphic" timeline={program.timeline}>
  <visual:Clip image={poster} extent={poster-size} during={program.title}
    frame={layout.full} z="20" mapping={turned}/>
</visual:Track>
```

The equations are `x' = xx*x + xy*y + tx` and `y' = yx*x + yy*y + ty`. An explicit mapping is
already in program coordinates, so it is mutually exclusive with the fit and alignment attributes.
The Frame still owns clipping, border, padding, shadow and whole-Clip motion; it does not rewrite the
mapping. Project components may construct the same `SpatialMap2D` through the public package API.

## Align the picture inside its destination

The fit shorthand aligns a point on the scaled source with a point in the fitting area:

| Direct Clip control | Meaning |
| --- | --- |
| `frame-x`, `frame-y` | The destination alignment point, from `0` to `1` across the fitting area's width and height |
| `content-x`, `content-y` | The point on the scaled source that meets it, also from `0` to `1` |
| `fit-offset-x`, `fit-offset-y` | Additional source displacement in pixels, positive right and down |
| `fit-constraint` | `bounded` keeps the fitted rectangle within the available placement range; `free` preserves the authored alignment and offsets |

The four point coordinates default to `0.5`; offsets default to zero. To keep a cover crop aligned
to the top, use `frame-y: 0; content-y: 0;`. `frame-x` and `frame-y` are alignment fractions inside
this fitting area. Position the whole card or inset with its spatial Frame.

With `bounded`, a source larger than the fitting area keeps it covered on that axis; a smaller
source stays inside it. An offset can therefore be limited, including to zero when the dimensions
match. Use `free` when exposing space through an offset is part of the design. Choose alignment from
the actual subject and composition; these coordinates express your crop choice.

## Shape the outer frame

Clipping, border, padding, shadow and frame paint belong to the outer Frame. The optional treatment
Recipe uses `clip: frame` for a rectangular clip, `clip: rounded` with a pixel `radius` for rounded
corners, or `clip: none` to show overflow. A radius takes effect with the rounded clip.

Here is a circular presenter inset; the normalized media, local domain and imported namespaces are
already available:

```svml
<space:AnchoredFrame id="presenter-frame" within={canvas.bounds}
  x="94%" y="94%" width="320px" height="320px" anchor="bottom-right"/>
<time:Clock id="clock" frame-rate="30"/>
<time:Timeline id="speech" clock={clock} end="opening.end">
  <time:Window id="opening" from="start" for={opening-media.extent}/>
</time:Timeline>
<visual:Track id="presenter" timeline={speech.timeline}>
  <visual:Clip id="opening" media={opening-media.media} during={speech.opening}
    frame={presenter-frame} z="20" fit="cover" treatment={look.presenter}/>
</visual:Track>
```

```svs
look.presenter {
  clip: rounded;
  radius: 160;
  border-width: 3;
  border-color: #D8C7A8;
}
```

A square Frame with radius half its side makes a circle. This crops the source geometrically;
subject-shaped transparency comes from the prepared media. For a rounded card, choose a radius
appropriate to its size. Rounded clipping follows the Frame: a smaller `contain` picture sitting
away from its corners can still have square picture corners. For rounded edges that follow the
picture itself, make the Frame match its displayed aspect and place the content flush inside it.

`padding` uses quoted pixel values: `"12"` for all sides, `"8 12"` for vertical/horizontal, or
`"8 12 16 12"` for top/right/bottom/left. Border and padding both reduce the fitting area while the
outer Frame keeps its size. Padding changes where fitting happens; the clip still follows the outer
Frame. `frame-paint` colors the space behind the source, including space left by fitting. Borders
outline the Frame and `shadows` sit behind it. Sample `opacity` and filters affect the picture;
the frame's paint and decoration have their own appearance.

## Move the frame or move its contents

A typed `Motion` moves or fades the complete framed occurrence, including its border and paint.
`Sampling` children pan, zoom or rotate the mapped picture under that frame. Use Sampling
for a moving crop or a slow push-in while a card's outline stays still:

```svml
<visual:Clip media={prepared.media} during={detail}
  frame={detail-frame} z="20" fit="cover" treatment={look.detail}>
  <visual:Sampling at="start" zoom="1"/>
  <visual:Sampling at="end" zoom="1.08" y="-18"/>
</visual:Clip>
```

This excerpt belongs inside a Visual Track, with prepared media, a resolved Window, Frame and Recipe already
available. Sampling fields apply to the Clip's sampled source.
`x` and `y` are pixel offsets, `rotate` is in
degrees, and `at` follows the source unit's active span from `start` to `end`, with percentages for
intermediate keys. Sampling acts after the resolved static mapping; its movement can expose space inside the
Frame. Choose the crop and motion together for the intended coverage.

[Visual Track](visual-clips.md) places explicit footage through Clips and owns their source-time
inputs. Read its installed vocabulary for complete appearance and motion fields. A scene that
coordinates the viewport with surrounding graphics can own the shared motion in its
[component program](component-visuals.md#compose-video-and-graphics-in-one-html-visual).

## Carry measured regions through explicit peer evidence

Region Evidence contains already prepared boxes indexed by Timeline Frame. It is not part of static
Spatial geometry. Its Recipe uses normalized `[x, y, width, height]` boxes and `null` for absent
measurements, resolved inside an explicit Frame. Source-local measurements need their actual time
placement and the source-to-picture mapping used by the actual visual occurrence before they can
position text correctly.

[Caption tracking](../playbooks/craft/caption-tracking.md) explains producing and applying head
regions. In a new component's visual element tree, child positions are relative to their parent;
[component visuals](component-visuals.md) shows that final layout boundary.
