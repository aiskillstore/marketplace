# Reuse construction helpers

Use [assets/geometry.js](assets/geometry.js) for small illustrative objects with repeated mechanical features. Copy it beside the generator so delivered sources remain independent of the skill installation.

The helpers run in Node through `require()` and in a browser or worker through `TechnicalGeometry`. They use caller-defined model units and have no package dependencies.

## Compose parts from profiles

`part(id, name, explosion)` creates a mesh with vertices, triangles and feature lines. Give `explosion` as an `[x, y, z]` translation from its assembled placement.

| Helper | Inputs and result |
| --- | --- |
| `lathe(part, profile, options)` | Revolves a closed `[x, radius]` profile around X; inner profile segments form actual bores, and a third value of `'h'` makes that point hexagonal |
| `ring(part, x, radius, role, kind)` | Adds a circular feature line perpendicular to X, or a hexagonal one with `kind` set to `'h'` |
| `helix(part, options)` | Adds a thread line from `x0` to `x1` with `radius`, `pitch` and optional handedness |
| `spring(part, options)` | Builds closed wire around X from `radius`, `wire`, `turns`, `x0` and `x1` |
| `knurl(part, options)` | Adds crossing helices using `starts`, `pitch`, `radius`, `x0` and `x1` |
| `screw(part, options)` | Combines a cylindrical head, shank, thread lines and a slot indication |
| `ringPoints(center, radius, u, v, options)` | Samples a circular arc in orthonormal plane axes to a model-space chord tolerance |
| `roundedRectangle(width, height, radius, options)` | Returns a rounded profile centered on X, with its bottom at Y zero |
| `extrude(part, profile, options)` | Gives a simple XY polygon a positive Z `depth`; supports concave outlines without holes |
| `transform(part, frame)` | Places mesh vertices, feature lines and explosion directions in one rigid frame |
| `merge(target, source)` | Copies a positioned construction piece into one complete part, preserving the target's identity and explosion |

```js
const G = require('./geometry.js');
const sleeve = G.part('sleeve', 'Knurled sleeve', [25, 0, 0]);
G.lathe(sleeve, [[0, 5], [30, 5], [30, 3], [0, 3]]);
G.knurl(sleeve, {x0: 2, x1: 28, radius: 5.01, starts: 12, pitch: 40});
```

Surface thread and knurl lines describe appearance, not cut thread solids. The screw's slot is an indication, not a machined recess.

Use CAD for boolean intersections, manufacturing threads, arbitrary section cuts or complex curved housings. These helpers do not infer those constructions.

Full lathe profiles may contain concave radial boundaries. Partial lathe sectors use convex end caps and require a convex radial profile.

## Build prismatic parts without custom triangulation

Pass `extrude` an ordered polygon without self-intersections. Clockwise and counterclockwise inputs work; a repeated closing point is optional.

```js
const bracket = G.part('bracket', 'Angle bracket', [0, 0, 20]);
G.extrude(bracket, [[0, 0], [24, 0], [24, 4], [4, 4], [4, 30], [0, 30]], {depth: 12});
G.transform(bracket, {origin: [10, 0, 0]});
```

Cap triangulation preserves concave notches. Curved profiles need sampled points; `creaseAngle` controls which corners receive longitudinal feature lines, defaulting to 25°.

`transform` mutates the part and accepts `origin`, `xAxis`, `yAxis` and `zAxis`. Axes must form a right-handed orthonormal frame; omitted values use the world frame.

Explosion vectors rotate with that frame but do not receive its origin translation. Place each complete part once, after constructing its local features.

Use CAD or a verified custom mesh for profiles with holes, intersecting contours or boolean subtraction. An outlined hole on a solid extrusion does not create an opening.

## Describe custom surfaces explicitly

Use this mesh contract when a verified construction needs surfaces beyond the helpers:

| Field | Representation |
| --- | --- |
| `vertices` | Finite `[x, y, z]` positions in assembled model coordinates |
| `triangles` | Three zero-based vertex indices per face, consistently wound toward the surface's outside |
| `lines` | Feature segments with `a` and `b` endpoints and a line `role` |
| `explosion` | A translation applied to the complete part, independent of its assembled position |

Add feature lines through `line(part, a, b, role)`. The role is `outline`, `edge`, `detail` or `texture` and defaults to `edge`. Helpers that add lines take the same `role` option.

Share vertex indices across adjacent faces so silhouette detection can compare their normals. Triangulation diagonals belong only in the mesh, never in feature lines.

Build positioned submeshes with zero explosion and combine them through `merge`. Set the complete part's explosion separately; merging copies geometry and leaves the source unchanged.

Merging does not union intersecting solids or erase their authored feature lines. Remove internal faces and seams explicitly, or move that construction to CAD.

## Project visible ink from the mesh

[assets/projection.js](assets/projection.js) supplies parallel cameras and sampled hidden-line removal for these meshes.

```js
const {render} = require('./projection.js');
const {markup} = render([sleeve], {explosion: 0.6, isolated: null});
```

For upright objects, set `camera: {azimuth: -135, elevation: 20, roll: 0}` in the render options. Angles use degrees, with world Z up and positive elevation above the object.

Zero roll keeps vertical edges vertical. The default camera retains the original isometric elevation and 16° roll; choose a view that reveals the object's important surfaces.

`project(point, camera)` accepts the same angles for feature anchors. For many anchors, build the camera once with `createCamera(camera)` and call its `project`. Keep camera changes out of model coordinates so geometry and explosion vectors remain in one physical frame.

The render result includes `scale` and `offset` for paper placement. Map an anchor with `project(anchor, camera).slice(0, 2).map((n, i) => n * result.scale + result.offset[i])`.

Add its part's current explosion translation before projecting the anchor. This keeps requested leaders and insertion axes attached after the view refits.

The result contains named part groups and paths carrying `data-line-role`. Roles are `outline`, `edge`, `detail` and `texture`; the viewer supplies their ink styles.

Coordinates fit a landscape A3 page with a 28 mm margin, which is the paper space the viewer expects. `explosion` accepts 0–2, while `isolated` accepts one part ID or `null` for the complete assembly.

The renderer samples visibility at 0.045 mm on paper by default. Its depth tolerance tracks 0.01 mm on paper, so inspect shallow recesses and nearly touching faces closely.

Move to CAD when sampled clipping cannot resolve the construction reliably.

Regenerate visibility after changing geometry, spacing or isolation. Previously hidden segments cannot be recovered by moving or hiding already-clipped SVG groups.

## Keep parameter changes coherent

Expose only meaningful parameters with validated minima, maxima, defaults and units. Use integer steps for counts and label fictional dimensions as concept values.

Derive mating features and repeated instances from shared parameters. Length changes must move attached components without stretching their independent details.

Share angular samples between touching curved surfaces, including segment counts and start angles. Equal radii alone can leave dotted contact lines when differently tessellated meshes intersect.

Retain stable part IDs across every parameter value. Confirm minimum, default and maximum settings reconstruct a credible assembly at zero explosion.

Run the helper checks with `node scripts/test-geometry.cjs` from this skill's directory. Render representative primitives and inspect their outlines after changing a construction helper.
