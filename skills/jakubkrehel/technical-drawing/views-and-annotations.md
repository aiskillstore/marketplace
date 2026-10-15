# Choose the view and its annotation grammar

## Explode along the assembly paths

Keep the assembled and exploded cameras identical unless a second angle reveals something necessary. Identify any camera change in the view label.

Choose a primary disassembly axis. Translate components along it, preserving their orientation, then separate secondary hardware along its own insertion axis.

Each offset begins at the component's assembled placement. Setting all explosion offsets to zero must reconstruct the assembly.

Choose gaps in paper space after projection. Start with 8–15 mm of clear space between silhouettes, increasing it where leaders or inner surfaces need room.

Keep stacks such as screw, washer, cover and boss coaxial. Show the real locating features at both ends of an assembly trail.

Use fine chain lines for necessary trails and omit redundant ones. Stop trails at their attachment features or conceal them behind opaque parts.

An explosion should reveal mating surfaces, not just spread silhouettes across the page. Preserve enough assembled context to explain where each group belongs.

These relationships follow [Autodesk's exploded-view model](https://help.autodesk.com/cloudhelp/2025/ENU/Inventor-Help/files/GUID-2569BBA6-816B-4656-9AC9-ABB9E1DC43C0.htm). Its item numbers connect the drawing to a parts list.

## Align orthographic views

Use a common scale and preserve corresponding widths, heights and hole positions between views.

Follow the supplied projection convention. Without one, select and label a convention explicitly. Third-angle places the top view above the front and the right-side view to its right.

First-angle places those views below and to the left. Never combine the two arrangements on one sheet.

Use hidden edges only where they explain features absent from the visible outlines. Draw centerlines through holes and axes rather than adding a background grid.

## Cut material, not empty space

Locate the cutting plane on a parent view, label both ends and show the viewing direction. Give the resulting section the same designation, such as `SECTION A-A`.

Hatch the solid regions intersected by the plane. Leave holes, passages and open cavities clear. Vary hatch direction or spacing between adjacent components.

For an illustrative section, start with 45° hatching at 2–3 mm spacing on paper. Enlarge narrow regions or adjust spacing before they become solid black.

For formal drafting, check the chosen standard's exceptions for ribs, shafts and fasteners. A visually plausible cutaway does not establish standards compliance.

The [MIT drawing handbook](https://ocw.mit.edu/courses/2-007-design-and-manufacturing-i-spring-2009/pages/related-resources/drawing_and_sketching/) explains section lining and view selection.

## Attach each balloon to one item

Use sequential item IDs from the inventory, without renumbering them when the layout changes. A parts list has `ITEM`, `DESCRIPTION` and `QTY` columns.

Quantities describe the complete depicted assembly. One balloon may identify repeated identical fasteners; the parts list gives their total count.

Place balloons in loose perimeter lanes, ordered to reduce leader crossings. Start with 7 mm diameter circles and center their numbers optically.

Route a leader from its feature to one elbow, then to the balloon edge. Use a small filled dot on a surface or an arrowhead at an edge.

Keep at least 2 mm between a leader and unrelated lettering. Prefer moving a balloon over adding another elbow.

Use stable feature anchors, such as `cover.fastener[0].center`, rather than guessing a nearby screen coordinate. Reproject anchors whenever the view changes.

## Dimension only what is established

Dimension model-space features in the view that shows their true shape. An exploded gap is a layout choice, never a product dimension.

Derive dimension labels from the same parameters as the geometry. Distinguish diameter `Ø` from radius `R`, and give units once for the sheet unless values use mixed units.

Prefer an orthographic view for dimensions, with extension lines outside the part. Start the first dimension 10 mm from the silhouette and successive dimensions 7 mm farther out.

Leave a 1 mm gap before each extension line and extend it 2 mm past the dimension line. Use filled arrowheads about 2.5 mm long.

These spacing values are an illustrative sheet recipe. A supplied drafting standard or established drawing template takes precedence.

Keep numbers readable from the sheet's chosen reading direction. Put radius leaders on the actual arc.

In circular views, place diameter lines through the circle's center. In axial views or sections, span the corresponding outside or inside surfaces and retain the `Ø` prefix.

Use `NTS` for fitted illustrations. Claim a numeric scale only when model units, projection and physical page output were all checked.
