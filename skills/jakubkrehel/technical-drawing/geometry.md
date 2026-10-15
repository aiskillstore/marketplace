# Build geometry once for every view

## Separate the object from its arrangement on paper

Keep dimensions, local profiles, assembled transforms, explosion vectors and item IDs in plain data. Define holes and their fasteners from shared centers.

Keep annotation anchors in the same coordinate system as their features. Sheet positions belong to the view, never to the part definition.

For a simple assembly, a small script generating SVG is sufficient. Complex curved intersections benefit from CAD hidden-line export rather than a new general-purpose renderer.

## Use one parallel projection

For an upright object, use world `x` across, `y` in depth and `z` up. The following is an isometric drawing with equal scale along its axes:

```js
const project = ([x, y, z], { ox, oy, scale }) => [
  ox + scale * Math.sqrt(3) / 2 * (x - y),
  oy + scale * (0.5 * (x + y) - z)
];

const displace = (point, offset) =>
  point.map((value, axis) => value + offset[axis]);
```

Here `scale` is paper units per model unit along the principal axes. This pictorial convention differs from a physically foreshortened orthographic isometric projection.

A different parallel camera is appropriate when the reference shows more of one face. Apply the same camera to every feature, including circles, slots and fasteners.

Fit bounds after explosion, reserving the annotation lanes. Compute a uniform view scale from the available width and height. Never stretch horizontal and vertical coordinates independently.

## Project circular features from their own plane

A circle on a sloping face becomes an ellipse with that plane's projected orientation. Arbitrary axis-aligned SVG ellipses break that relationship.

For a center `c`, radius `r` and orthonormal plane axes `u` and `v`, project points from this parameterization:

```js
function ringPoint(c, u, v, r, t) {
  return c.map((n, i) =>
    n + r * (u[i] * Math.cos(t) + v[i] * Math.sin(t))
  );
}
```

An affine SVG matrix can transform a local circle exactly. Its columns are the projected unit vectors `u` and `v`, and its translation is the projected center.

That matrix also transforms stroke widths. Use transformed paths with sheet-space strokes, or compensate the stroke deliberately and verify its rendered thickness.

When sampling curves, subdivide until the projected chord error is below 0.05 mm on paper. Fixed coarse polygons become visibly faceted in close-ups.

For a cylinder, draw the visible rim arcs and tangent side edges. Hide rear arcs according to the chosen view, using hidden lines only when requested by its grammar.

## Give parts real boundaries

An enclosure has wall thickness, an inner cavity and mounting features. A grille has an outer frame and repeated openings, not stripes floating across a face.

A fastener has an axis, a head and a shank entering a matching hole. Simplify its threads at small scales while retaining enough shape to identify the connection.

A cable meets a connector or strain relief. A spring wraps around its axis with consistent radius and pitch, then terminates on a seat or attachment.

Choose only the features supported by the evidence record. Conceptual construction should fit together even when its geometry is invented.

## Resolve visibility before drawing edges

Paint opaque surfaces back to front and draw only their visible edges. Plain paper-colored faces provide occlusion without adding shaded rendering.

A center-depth sort is insufficient when parts overlap or wrap around each other. Split intersecting projections, clip hidden segments or use the CAD renderer.

For holes, subtract the opening from the front face using a compound path or clipping. Draw visible inner walls and whatever is actually behind the opening.

A white ellipse can suggest a shallow recess. It cannot represent a through-hole when another part should remain visible through it.

Avoid triangulation seams, duplicate coincident edges and tessellation lines on smooth surfaces. Keep only silhouette edges, actual boundaries and necessary feature lines.

## Prove the assembly before decorating it

Render with explosion offsets set to zero. Check each fastener's alignment and insertion depth against its hole. Check rims against their mating seats and covers against their enclosures.

Fastener heads should contact their seats, with shanks concealed where they enter solid material.

Restore the explosion offsets and verify that the same features stay aligned along their disassembly paths. Fix a misfit in the part data, never by nudging one view's ink.

For orthographic views, compare shared feature coordinates numerically. A hole's horizontal location must agree between front and top views when both display that coordinate.
