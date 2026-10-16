# Compose the sheet in paper units

## Start from the reproduction size

Use one SVG user unit per millimeter of paper. A landscape A3 sheet starts with `width="420mm" height="297mm" viewBox="0 0 420 297"`.

For that sheet, begin with 12 mm margins and a 24 mm title band. Size the object before placing a border or table.

Use plain white paper and near-black ink, such as `#202020`, for a clean assembly print. Follow an explicit color reference when provided.

Treat these values as a starting recipe, not a drafting standard:

| Mark | Paper size |
| --- | --- |
| Outer silhouettes and cut boundaries | 0.35 mm stroke |
| Visible component edges | 0.22 mm stroke |
| Fine details, leaders and dimensions | 0.16 mm stroke |
| Hatching, centerlines and trails | 0.13 mm stroke |
| Main title | 5 mm text |
| Item numbers and ordinary labels | 3 mm text |
| Secondary metadata | 2.5 mm text |

Keep fine strokes dark enough to survive export. Achieve hierarchy through width before reducing opacity.

Use the project's fonts when the sheet belongs to a product. Otherwise choose an available neutral sans serif and verify its actual rendering.

Keep annotations in sheet coordinates so changing the drawing scale does not change their size. Font sizes above describe the em size, not guaranteed capital height.

Use square-ended technical strokes for edges and dashes. Inspect acute joins for unwanted spikes.

## Make line roles distinguishable

Use continuous lines for visible edges. Hidden edges use short, uniform dashes; centerlines and assembly trails use a long-short pattern.

Start with `stroke-dasharray="2 1"` for hidden edges and `stroke-dasharray="6 1 1 1"` for centerlines. Preserve those lengths in paper coordinates.

Place centerlines slightly beyond the feature they identify. Terminate trails at meaningful assembly anchors, and use solid leaders for item identification.

White space around a part is useful. Add sheet grids, zone labels or decorative rules only when the user's template needs them.

## Keep the exported SVG self-contained

Use named groups for views, parts, annotations and sheet furniture. Prefix IDs when embedding multiple drawings in one document.

Keep styles, patterns and markers inside the SVG. Avoid remote fonts, linked images and runtime dependencies in the standalone artifact.

Set `fill="none"` on open paths and polylines, including leaders. SVG's default fill otherwise closes a bent leader into a black triangle.

Include an SVG `title` and `desc` summarizing the subject and views. When embedding in a product, hand accessible naming and the parts-list alternative to `better-accessibility`.

This shell establishes physical units and line roles without prescribing the sheet's composition:

```svg
<svg xmlns="http://www.w3.org/2000/svg"
     width="420mm" height="297mm" viewBox="0 0 420 297"
     role="img" aria-labelledby="drawing-title drawing-desc">
  <title id="drawing-title">Assembly drawing</title>
  <desc id="drawing-desc">Assembled and exploded views with a parts list.</desc>
  <defs>
    <style>
      .edge, .outline, .fine, .axis {
        fill: none;
        stroke: #202020;
        stroke-linecap: butt;
        stroke-linejoin: round;
      }
      .outline { stroke-width: .35; }
      .edge { stroke-width: .22; }
      .fine { stroke-width: .16; }
      .axis { stroke-width: .13; stroke-dasharray: 6 1 1 1; }
      text { fill: #202020; font-family: Arial, sans-serif; font-size: 3px; }
    </style>
  </defs>
  <rect width="420" height="297" fill="white"/>
  <g id="views"/>
  <g id="annotations"/>
  <g id="sheet"/>
</svg>
```

Replace the placeholder title, description and empty groups with the actual drawing. Here SVG font pixels are user units and inherit the root's millimeter mapping.

Generate projected coordinates directly in sheet space when possible. Nested scale transforms otherwise multiply stroke widths along with geometry.

`vector-effect="non-scaling-stroke"` preserves viewport stroke thickness, not a universal physical pen size. Use it only with a deliberate export policy and verify both preview and print output.

The [SVG coordinate specification](https://www.w3.org/TR/SVG2/coords.html) defines the relationship between user coordinates, viewports and vector effects.

## Export from the same source

Rasterize the actual SVG with a browser or installed SVG renderer. For A3, a preview around 2000 pixels wide is a useful first inspection.

For a print PNG, compute pixels as `millimeters / 25.4 * dpi`. At 300 dpi, landscape A3 rounds to 4961 by 3508 pixels.

For PDF, retain vector geometry through a suitable exporter. Set the page size explicitly, disable browser headers and margins, then inspect the exported page.

Open SVG and PDF independently after export. Check that fonts, markers, clipping and hatch patterns survived, especially around holes and small labels.

Keep any generator beside the deliverables with its invocation and required dependencies. Resolve imports locally so regenerating the drawing does not depend on a temporary skill-installation path.
