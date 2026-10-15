# Verify the rendered drawing

## Inspect at two distances

At delivery size, check that the object reads before the annotations. The main view should have a clear silhouette, and the secondary view should explain its assembled form.

Read every label at that size. If it requires zoom, enlarge the label, enlarge the output or remove lower-priority metadata.

At 3–4×, inspect every crowded junction and curved contour. Look for faceting, lines through solid faces, doubled edges, mismatched tangencies and leaders ending in empty space.

Check that a cylinder's rim arcs connect through both silhouette edges. A missing side can appear only at particular camera angles or tessellation counts.

Check the preview against the reference's visual grammar. Judge line density, paper use and annotation restraint separately from whether the subject itself matches.

## Trace every correspondence

| Drawing type | Evidence to check |
| --- | --- |
| Exploded assembly | Zero offsets reconstruct the assembled view; mating anchors remain on the same explosion path |
| Multiple views | Feature counts and shared coordinates agree across projections |
| Section | Every hatch region is solid material at the stated cut; openings remain clear |
| Dimensioned drawing | Every label comes from a model parameter with known units |
| Parameterized object | Minimum, default and maximum settings preserve mating features, quantities and corresponding views |
| Isolated part | Previously occluded geometry reappears and the export contains only the selected component |
| Adjustable explosion | Zero reconstructs the assembly; intermediate and maximum spacing preserve insertion axes |
| Numbered assembly | Each balloon resolves to one item; every listed item is represented; quantities match the assembly |

An intentionally omitted item needs a note. A parts list cannot quietly count hardware that the drawing never represents.

Follow each leader from balloon to part in the final image. Confirm that crossings and hidden endpoints cannot make it identify a neighboring component.

For a real object, compare distinctive features against the source images. Remove invented certainty even when it makes the sheet look more official.

## Check the artifact mechanically

Parse the SVG as XML. Check for duplicate IDs, unresolved `url(#...)` references, invalid numbers and external assets.

Check rendered text, leaders and strokes against sheet margins and reserved table rectangles. Inspect the corners of rotated labels and the tips of arrowheads.

Ensure every supplied output opens without the original working environment. Check exported dimensions against the requested physical size or pixel size.

For numeric scales, verify a known model length against its exported paper length in a true-length view. Fit-to-page printing invalidates that check unless compensated.

Automate inventory, dimension and coordinate comparisons where the generator exposes them. Pixel inspection remains necessary for occlusion and readability.

## Make each revision answer a visible failure

Record the defect, change its source and render again. Inspect both the corrected region and the full sheet after any camera, scale or layout change.

Finish when geometry, correspondence, legibility and export checks pass. Report any remaining limitation by naming the affected view or feature, rather than claiming unqualified precision.
