# Camera geometry: recovering bearing, distance and height from the frame

Scripts: `scripts/geo.py` (`range` / `bearing` / `dest` / `fov` / `line` / `intersect` / `frame`), `scripts/pose.py` (solving the camera position from multiple points, scoring candidate camera positions), `scripts/terrain.py` (skyline rendering).
All results are estimates. When you write a conclusion, write out the assumptions you used (lens zoom, object size) with it.

## 1. Determine the field of view first

The main camera (35mm-equivalent about 24–26mm) is the most common phone lens, but **without EXIF, never lock the focal to it**. Distant mountains, compressed layers and a far object filling the frame are often shot at 2–3x or more. Any search that solves for focal must cover ultra-wide to telephoto (`terrain.py fit` does 13–135mm by default when the focal is assumed); a main-camera-only search simply cannot reach a 52mm photo, and its best fit lands somewhere wrong.

| Equivalent focal length | 4:3 long-side FOV | 4:3 short-side FOV |
|---|---|---|
| 13mm (0.5x ultra-wide) | ≈107° | ≈88° |
| 24mm | ≈71° | ≈57° |
| 26mm (common 1x) | ≈67° | ≈53° |
| 48–52mm (2x) | ≈38° | ≈29° |
| 77mm (3x) | ≈26° | ≈19° |

- In portrait orientation, the photo width corresponds to the short-side FOV; in landscape, to the long-side FOV.
- Judging zoom: obvious stretching at the frame edges, nearby objects very large → ultra-wide; small size difference between near and far, background looks "pressed in" → telephoto. Use this to choose where to look first, not to narrow the search range.
- Screenshots and cropped photos have a smaller FOV; use a conservative range.

**Video screenshots are narrower**: phone video is 16:9; the frame width of a vertical video corresponds to the short side of 16:9, and stabilization crops off another margin.

| Zoom | Landscape video horizontal FOV | Vertical video horizontal FOV |
|---|---|---|
| 0.5x | ≈95–106° | ≈65–73° |
| 1x | ≈58–67° | ≈35–41° |
| 2x | ≈32–37° | ≈18–21° |
| 3x | ≈22–25° | ≈12–14° |
| 5x | ≈14–16° | ≈8–9° |

When you can't tell the zoom, don't guess a single value: `geo.py range --real <object size> --pixels <pixels> --image-width <width> --hfov 8:70` gives the whole distance range; search for candidates over that range. Then use section 11 to check whether "landmark X is not in the frame" can exclude anything.
The zoom can be backed out: identify two or more landmarks with known positions; the angle spanned by their horizontal pixel spacing in the frame can be computed from the candidate camera position; comparing the two gives the focal length (with 4 or more points, use `pose.py` from section 10 directly, with hfov not fixed).

Focal length (pixels): `f = (image width in px / 2) / tan(FOV / 2)`

## 2. Find the horizon

**When shooting down from a tall building, shooting up, or holding the phone tilted, the horizon is not at the middle of the frame** (one calculation using that default got the ridge height difference wrong by 2–3×). In that case:
- Estimate pitch from the convergence of vertical building edges: edges converging downward = shooting down, converging upward = shooting up; asymmetric tilt of the left and right building edges = roll.
- When you can identify ≥4 points with known positions, use `pose.py` from section 10 to solve pitch, roll and height together.

When the phone is held level, the horizon is at the vertical middle of the frame. To verify:
- Vertical building edges are basically parallel, with no obvious upward convergence → phone is level
- The row on which a distant object at the photographer's height lands (e.g., the roof of a distant building a few floors high, when the photographer is also a few floors up) is the horizon

## 3. Estimate distance from a known size

`distance ≈ real size × f / size in pixels`

Common reference sizes:

| Object | Size |
|---|---|
| Residential floor height | 2.9–3.0 m |
| Office/factory floor height | 3.3–4.5 m |
| Car width / length | 1.8 m / 4.7 m; MPV length about 5 m |
| Urban lane width | 3.5 m |
| Standard parking space | 2.5 × 5.3 m |
| Balcony railing baluster spacing | about 0.11 m |
| Chinese high-speed and intercity rail simply supported box girder span (pier spacing) | mostly 32 m, also 24 m and 40 m; when you can count the piers, a row of piers is a ruler |
| Supertall tower width | look it up; if you can't find it, measure the roof on satellite imagery |

Estimate the same object two ways (e.g., building width and floor height). A large gap means the zoom or size assumption is wrong.

## 4. Recover the shooting direction from two landmarks (most useful)

Conditions: the positions of two landmarks are known (measured on satellite imagery), and in the photo you can tell which is nearer/farther and which is left/right.

1. On satellite imagery, determine the direction of the line connecting the two landmarks.
2. For objects of equal height, the one whose top sits lower in the frame is farther. With a known width, use section 3 to compute each distance.
3. Only a few directions satisfy "near one on the left, far one on the right": looking obliquely from one side of the connecting line.
   Example: two towers lie east–west, near tower on the left, far tower on the right → the photographer is west-southwest or east-northeast;
   from due south/north the two towers are equally far; from the southeast/northwest the left/right near/far relation reverses.
4. The horizontal angle between the two towers in the frame, combined with their actual spacing, further gives the angle between the sight line and the connecting line.
5. Usually two candidate directions remain; use satellite imagery to see which side's building layout looks like the photo, and exclude the other.

## 5. Road direction

- Find the street's vanishing point (the intersection of the extended eave lines of buildings on both sides and the road edges).
- Horizontal pixel difference between a landmark and the vanishing point in the frame → angle: `angle = atan((x_landmark − x_center) / f) − atan((x_vanishing − x_center) / f)`
- Road bearing = landmark bearing − angle. Look for a road with this direction on satellite imagery.

## 6. Camera height

- A certain floor of a building in the frame lies on the horizon → the photographer is at the same height as that floor.
- Or: the ratio of the pixel distances from an object's top edge and bottom edge to the horizon = part above the photographer : part below the photographer.
  Example: a glass curtain wall's top edge is 283 px above the horizon and its bottom edge 157 px below; the wall spans 4–20 m above ground → the photographer is about 10 m above ground.
- Looking down at nearby objects on the ground: `depression angle = atan(pixel distance to the center line / f)`; with a known horizontal distance you can get the height.
- Cross-check with at least two references and give a floor range (e.g., "floors 3–6"), not a single number.

## 7. Sight-line geometry: fixing the camera position without focal length or sizes

This section is the main way humans beat the AI in the videos (v006, v010-1/2/3/7). Do it after identifying an anchor and before street view comparison.

### 7.1 Alignment line (extend the line through two points)

When a near object and a far object in the frame are vertically aligned or one hides the other (a spire right above a house, a court's diagonal pointing straight at the lens), the camera position is on the extension of the line "far object → near object", beyond the near object.

```bash
uv run scripts/geo.py line --near <near object lat,lon> --far <far object lat,lon> --range 50:2000 --step 100 --out line.json
uv run scripts/tiles.py mark area.jpg --points line.json --out area_line.jpg
```

Then cut the camera position out of the line with a third constraint: riverbank, road, a tall-enough building, camera height.

### 7.2 Sight-line intersection (two lines fix a point)

```bash
uv run scripts/geo.py intersect --align1 <near1>:<far1> --align2 <near2>:<far2> --sigma 1
uv run scripts/geo.py intersect --sight1 <landmark lat,lon>@<bearing to it from the camera position> --sight2 ... --sigma 2
```

- Outputs the intersection, the angle between the two lines, and the error radius (the maximum distance the intersection moves when each line's bearing is off by ±sigma).
- When the angle is <15°, the intersection is extremely sensitive to error; find another line at a large angle.
- The error radius is the radius to write in the conclusion; don't make up decimal places.

### 7.3 Tangent line

A ridge or cliff edge is exactly tangent in the frame to the edge of a nearby feature (field edge, riverbank line, eave) → draw the same tangent line on satellite imagery; the camera position is on that line (v010-2).

### 7.4 A skyline gives only one sight line

Moving the camera position a few hundred meters forward or back along the sight line barely changes the outline of a distant ridge. So "the mountain shape matches" only says the camera position is near some sight line; **it can't fix a point, much less give meter-level precision** (v010-1: the AI reported ±7 m from the mountain outline alone and landed in the wrong town).

```bash
uv run scripts/terrain.py view --at <candidate camera position> --heading <heading> --hfov 60 --range 25000 --out v.png --photo photo.jpg
```

Use it to screen candidate camera positions and fix the sight-line bearing; to fix a point, add another independent constraint (another near–far alignment, a road or riverbank, camera height).
When rendering, the FOV must match the photo: portrait phone main camera horizontal FOV about 50°, landscape about 65°; for telephoto shrink it by the zoom (2x roughly halves it).

- `--overlay` outputs an extra image that draws the synthetic skyline directly on the photo by pinhole projection; easier to match than stacking them top and bottom. When it doesn't match, adjust `--heading / --pitch / --hfov / --roll` first, before doubting the camera position. `--pitch` is positive looking up: horizon below the photo's middle → positive, above → negative.
- When spiky false ridges appear close by (elevation sampling artifacts), set `--near` to 150–300 m.
- When the ridges around a city are gentle, the skyline only helps you fix heading and FOV; it can't separate camera positions within a few hundred meters.

**When there are many candidate camera positions, score them in batch, then look at overlays of the top few** (single source; one real case). Two steps: first `terrain.py ridge` reads the photo's ridge into a sequence of pixel points, then `terrain.py fit` places grids of camera positions around the candidate points and searches heading × focal length × horizon row.

```bash
# 1) Read the photo ridge: per column, find the brightness drop from sky to mountain
uv run ${CLAUDE_SKILL_DIR}/scripts/terrain.py ridge photo.jpg [--x0 X0 --x1 X1 | --points "x,y;x,y;..."] --out ridge.json \
  [--step 20] [--flat x0:x1] [--hrow ROW] [--f0 px] [--f35 26.0] [--ymin 0] [--ymax IMAGE_HEIGHT] \
  [--near "x,y;x,y;..."] [--near-clear x0:x1@ROW ...] \
  [--drop 30] [--k 4] [--hold 12] [--halfw 1] [--png check.png]

# 2) Batch scoring (fine search = the same command with --radius 800 --grid 100 --zoom 13 --az-step 0.25 --nsamp 400)
uv run ${CLAUDE_SKILL_DIR}/scripts/terrain.py fit (--hits hits.json | --at lat,lon) --ridge ridge.json --out fit.json \
  [--select 11,87,...] [--radius 2000] [--grid 250] [--zoom 11] [--focal-scales auto | --f35-range LO:HI] [--az-step 0.5] \
  [--near 150] [--range 15000] [--nsamp 260] [--eye 1.6] [--cam-flat 8] [--cam-flat-radius 300] \
  [--min-peak 6] [--cc-max 0.7] [--roll-max 1.0] [--flat-clear 1.0] [--flat-w 1.5] [--flat-step 20] \
  [--line lines.geojson --line-dist L0-L1:C0-C1:R0-R1 [--line-win -27:-21,-3:3,18:27] [--line-scale 200,200,300] \
   [--line-order none|asc|desc] [--line-w 0.3] [--line-min 150] [--line-sample 50] [--line-reach 3000] [--skip-tag electrified=no ...]] \
  [--near-dist 3000,5000,8000,12000] [--near-clear-w 1.5] [--perp-line lines.geojson [--perp-tol 35] [--perp-reach 1500]] \
  [--top 20] [--keep 5000] [--sheet top.jpg] [--overlay|--photo photo.jpg] [--sheet-cols 4] [--sheet-width 360]
```

- `ridge`: `--x0/--x1` is the column range of the ridge, `--step` the spacing between sampled points, `--flat x0:x1` the column range of the flat horizon (the stretch with no mountains), `--hrow` the horizon row (if omitted, estimated from the middle of the frame). `--drop/--k/--hold/--halfw` are the thresholds for finding the brightness drop (drop size, multiple, consecutive rows, horizontal smoothing half-width). Outputs `{size, ridge:[[x,y]...], flat:[x0,x1], hrow, f0, f0_source}`; when the photo has no EXIF focal length, `f0` is estimated from the `--f35` equivalent focal length and the image dimensions and marked `f0_source=assumed`. `--png` outputs a check image. `--points` replaces detection with hand-picked skyline points: use it when cloud sits on the peaks or snow meets a pale sky, because detection then follows the cloud edge and the residual never comes down.
- `fit`: candidates come from `--hits` (the scan results of `corridors.md` 4.3; `--select` takes only the given cluster numbers) or a single point via `--at`. Around each candidate point, camera positions are placed on a `--grid`-meter grid within `--radius` meters; heading is scanned in `--az-step` steps, focal length is tried at the `--focal-scales` multipliers, and the horizon row is searched too — **don't hard-code "portrait 50°, horizon at the middle"**. The camera position itself must be flat close by (relief of at most `--cam-flat` m within `--cam-flat-radius` m), and the mountains must be high enough (`--min-peak`). Score = ridge elevation-angle RMS + a penalty for the flat-horizon stretch being blocked by mountains (`--flat-clear` tolerance, `--flat-w` weight). `rms_px` in the output is the RMS converted to pixels; compare it with the point-picking error of the photo ridge: when the top few all have `rms_px` about as large as the picking error (a few to a dozen or so pixels), the skyline can't separate these camera positions and you need a second constraint. Focal search is automatic (`--focal-scales auto`): ×0.9/1/1.12 around an EXIF or `--f0` focal (pass `--focal-scales 1` to pin it), a 13–135mm-equivalent ladder (~18% steps) when ridge.json's focal is assumed. On the ladder, scores are compared in pixels (`--focal-metric auto`): in degrees the same pixel mismatch shrinks as the focal grows, and on a real photo every candidate ran to the longest rung. `f35` in each record is the equivalent focal in mm.
- **A focal on the edge of the range is a signal, not noise.** When the leading results sit on one end of the ladder, fit prints a WARNING and writes `focal_edge`. Most often the photo is more zoomed (or wider) than the range: rerun with `--f35-range` extended past that end (the warning suggests one) before trusting the ranking, heading or focal. A search that keeps everything on the long end is telling you the photo was zoomed; ignoring that and ranking anyway sends you to a place where a shorter lens happens to fit. In the real case: with a 20–40mm range all 10 leading results sat on the long end and the true area ranked 97th; with 13–135mm the edge cleared, the focal settled inside the range and the true area ranked 1st of about 1,800. Only when the focal runs to the new end again, or the focal is known from EXIF and still hits ×0.9/×1.12, is it absorbing another error: check cloud on the ridge points (`ridge --png`), `hrow`, and whether the place is wrong.
- **Distant ranges**: the default `--range 15000` only sees terrain within 15 km. For a range 20–40 km away use `--range 45000`; z10 flattens peaks, so lower `--min-peak` to about half the photo estimate (corridors.md 4.3).
- **Two-layer photos** (a lower near range in front of a higher far range, and the near range ends mid-frame so the far range's foot or plain shows beyond it). `fit` on the outermost skyline alone can match the far outline at a wrong heading with a wrong focal; in one real case the far-only fit at the true camera position chose a heading 50° off and a near-maximal focal, while the two-layer fit got the heading within 0.5°. In `ridge`, add `--near` (points on the near range's top edge, where it stands in front of the far range) and `--near-clear x0:x1@ROW` (columns past the near range's end, where nothing near may rise above ROW, usually the far range's foot). `fit` then computes a near layer = highest terrain within D1 m (D1 tried from `--near-dist`), scores the near points with the far ones (one `cc` and roll for both), and adds `--near-clear-w` × `nclearpen`. The record gains `D1` (how far the near range reaches) and `rms_near_px`; the sheet draws the near layer in orange. Pick near points by hand and check them on `ridge --png`: the near/far boundary is where detection fails.
- **Wires crossing the frame almost level** (high-voltage lines overhead): `--perp-line lines.geojson` keeps only headings within `--perp-tol` (default 35°) of perpendicular to the nearest line; camera positions more than `--perp-reach` m from any line are skipped. In the real case this, plus the near layer, was what separated the right region from look-alike ranges elsewhere.
- **Solve roll too** (`--roll-max`, default 1.0°; 0 gives the old behavior): a 1° handheld tilt makes the ridge at the two ends of the frame differ by a dozen or so pixels; if roll isn't solved, the ground truth gets crowded into the same RMS tier as a pile of wrong candidates. For each heading, a least-squares fit of "terrain elevation angle − photo elevation angle" against horizontal azimuth gives the horizon offset `cc` as the intercept and tan(roll) as the slope; the result is written into the camera-position record's `roll`. Keep the cap tight: in both synthetic tests and real photos ±1° works better than ±2.5° (when loosened, wrong candidates can also absorb noise through tilt, and the gap between the ground truth and second place is flattened). A solved `roll` that hits the cap means this degree of freedom is compensating for other errors (wrong camera position, wrong focal length); don't treat it as real tilt in the shot.
- The facility-distance constraint is optional: `--line` gives the line data, `--line-dist` gives distance ranges (meters) at three places, left/center/right, `--line-win` the frame bearing windows for those three places (degrees, relative to heading), and `--line-order` requires the three distances to be monotonic (asc/desc). Falling outside a window is penalized by `--line-scale` and `--line-w`.
- Output `fit.json`: `{params, n_clusters, n_cams, n_skipped:{not_flat, no_peak, no_line, dup}, clusters:[{hit, name, hit_ll, n, max_ang, n_cams, rank, best}...], cams:[{hit, name, hit_ll, cam:[lat,lon], d, brg, g, H, fs, f, cc, roll, rms, rms_px, flatpen, score, (dL/dC/dR/line_pen), total}...]}`; `--sheet` outputs thumbnails of the top N; with `--photo` they are the photo overlaid with the synthetic skyline (the red line is drawn with the `roll` solved for that camera position; otherwise the two ends would be off by a dozen or so pixels).
- `ridge` / `fit` both use `terrain.py`'s `--cache` parameter (default `.geo-cache/dem`).
- When spiky false ridges appear close by (elevation sampling artifacts), set `--near` to 150–300 m.
- **Fine search (z13) is not guaranteed to be more accurate than coarse search**: in reruns, fine search on the same chain ended up farther from the ground truth than coarse search. The z13 flatness filter removes points near the ground truth, and the skyline itself gives only one sight line. Fine search exists to give 7.7's evenly spaced structures a reliable `--center`, not to push the error down by itself.
- `H` and `f` in the `fit` output have a systematic bias that comes from `hrow` in `ridge.json`: in the same coarse search, hrow set by hand to 935 gave H 80.5 / f 1436, while the auto-estimated 909 gave H 79.0 / f 1282. Cluster ranking is unaffected (the ground-truth cluster ranked 1st both times); if you want to make claims from heading and focal length, first pin down the blue line on `ridge --png`.
- **Skyline alone can't separate them**: in a real case with 171 candidates the ground truth ranked 2nd, but the top 20 all had RMS crowded into 0.10–0.20°. Rank together with a second numeric constraint (e.g., how far the facility is from the left, center and right of the frame, `corridors.md` 4.3).
- The stretch of ridge hidden by the foreground (people, cars, trees, nearby objects) doesn't enter the score, yet where the mountain foot starts to rise is often what best separates candidates. **Always `--overlay` the top 3–5 and look**: in a real case, the candidate ranked 1st overall had its ridge bulge in the occluded stretch and its mountain foot didn't match; the 2nd was the ground truth.

### 7.6 A nearby cable close to vertical in the frame

If a cable, wire or stay very close to the lens looks almost vertical in the frame, the camera position is near the vertical plane of that line (looking from directly below or straight from the side).
The bearing difference Δ (degrees) by which the line departs from vertical and spans horizontally in the frame, and the distance s from the line to the camera position, satisfy: lateral offset d ≈ s · tan(Δ). Get the line's position with `osm.py find '["aerialway"]'` or `'["power"="line"]'`.
In a blind test, this alone once brought the lateral error down to a dozen or so meters.

### 7.5 Verify bearings with a top-down sketch

Draw "camera position → foreground → midground → background → sun" as a top-down sketch with bearings; the candidate point must reproduce the same left/right, near/far and heading on the map. Rules in `verify.md` section 3. A sunset only says the lens faces west, not that the coast faces west (v010-7).

### 7.7 Evenly spaced structures: distance to the line and oblique angle

When a row of evenly spaced things in the frame (viaduct piers, utility poles, streetlights, guardrail posts) lies on a line known on the map, you can solve for how far the camera position is from that line and at how many degrees it looks across it obliquely. Single source (one real case).

1. `imgprep.py piers` reads the pixel column of each structure (it takes a brightness profile along the rows where the structures are and finds peaks); ≥6 of them, and it's fine if the foreground breaks them into several segments.

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/imgprep.py piers <image> --rows R0:R1 --out cols.json \
  [--cols X0:X1] [--min-gap 20] [--min-prominence 12] [--baseline 61] [--polarity auto|bright|dark] [--sheet piers.jpg]
```

`--rows` is the row range for the profile (the rows the structures are in), `--cols` limits the column range, `--min-gap` is the minimum spacing in pixels between adjacent peaks, `--min-prominence` the minimum peak prominence, `--baseline` the sliding-window width (odd) used to estimate the background, and `--polarity` says whether the structures are brighter or darker than the background. Outputs `{image, size, rows:[r0,r1], cols:[x0,x1] (the column search range, not the structure columns), polarity, params, count, piers:[{col, prominence, dev, level}...]}`; the structure columns are in `piers`, and `geo.py spacing --cols @cols.json` reads that field directly. **You must eyeball the check image from `--sheet`**: bright patches of grass and the edges of foreground pipes produce false peaks; delete them before the next step.

2. `geo.py spacing`: for each candidate camera position, heading and focal length, convert the pixel columns into bearing rays and intersect them with the OSM polyline to get each structure's along-line distance; at the correct camera position the differences between adjacent along-line distances are constant and equal the standard spacing.

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/geo.py spacing --cols '39,133,219,296,369;745,788,...,1148' \
  --line rail.geojson [--line-name <line name>] [--line-index 0] --span 32 --center lat,lon \
  [--radius 1500] [--grid 50] [--headings 0:360] [--heading-step 0.25] \
  --focals 1200,1281,1350,1430,1500|1200:1500[:step] [--focal-step 50] [--cx 640] \
  [--min-dist 100] [--pier-max 0.08] [--mono-penalty 1.0] [--top 25] [--progress 10] [--out spacing.json] \
  [--ridge ridge.json] [--hrow 935] [--flat 0:280] [--flat-step 20] [--flat-margin 1.0] [--flat-weight 1.5] \
  [--ridge-weight/--pier-weight 2.0] [--cc-max 0.8] [--eye 1.6] [--dem-zoom 13] [--dem-range 18000] \
  [--sky-range 16000] [--sky-near 100] [--sky-samples 400] [--az-step 0.1] [--cache .geo-cache/dem]
```

- `--cols` are pixel columns; when the foreground breaks them into segments, group them with `;` (adjacent along-line differences are compared only within a group); at least 3. `--cx` is the center column of the frame.
- When `--line` contains several lines, pick one with `--line-name` or `--line-index` (a name that doesn't exist lists the available names). `--span` is the standard spacing (meters).
- Camera positions are searched on a `--grid`-meter grid within `--radius` meters of `--center`; heading is scanned by `--headings a:b` + `--heading-step`, and focal length is tried from the `--focals` list or `low:high[:step]`. Score = spacing dispersion (CV) + |log(mean spacing / standard spacing)|; `--pier-max` is the cutoff for inclusion, and `--mono-penalty` penalizes solutions whose along-line distances aren't monotonic.
- Passing `--ridge` scores jointly with the 7.4 skyline (DEM fetched per `--dem-zoom`/`--dem-range`, weight `--ridge-weight`, flat-horizon stretch via `--flat*`). Outputs `{line, params, n_fit, best, candidates:[{tot, rms, pier, cam:[lat,lon], f, H, cc, span_m, d_first, d_last}...]}`.
- With this alone, the solution is a band along the line (spread over about 800 m in a real case); scoring jointly with the skyline narrows it to about 300 m. Suited to fixing the camera position at the end, not to choosing a city.
- The standard spacing is an assumption: a solved mean spacing equal to the standard value is forced by the scoring and doesn't count as verification; the real signal is low dispersion (CV 2–7% in a real case). When unsure of the spacing, run once with each of a few standard values.

## 8. Estimate object height

Back-computing the time from the sun and estimating distance by proportion both need object height. Cross-check with at least two rulers:

| Ruler | Size |
|---|---|
| Adult | about 1.7 m (posture and shoes add a few cm of error) |
| Interior door / entrance door | about 2.0–2.1 m |
| Residential floor height | 2.9–3.0 m; commercial buildings 4–5 m; factories 3.3–4.5 m |
| Standard shipping container | 2.59 m; high cube 2.90 m |
| Mounting height of traffic signs and signals | look up that country's standard; don't guess |

When you have the building name, look up its floor count and floor height directly; that is more reliable than estimating from pedestrian proportions.

## 9. Screen buildings by camera height

- Can look down on the roofs of surrounding 20–30-story residential towers → the camera position is in the city's tallest tier of buildings, often only a few candidates; not seeing the city's tallest building in the frame may be precisely because the photographer is standing on it (v006).
- In a tourist's photo, a steady elevated downward shot from a building is most likely from their hotel (v011): within the candidate area, look first at hotels with parking lots.
- Estimate the floor by cross-checking two references (section 6); give a range.

## 10. Solving the camera position from multiple points (pose.py)

Window views, downward shots from tall buildings, views across a river: as long as you can identify ≥4 points on satellite imagery (bridgeheads, spires, building corners, intersections, sports-field corners), you can solve the camera position's lat/lon, height, heading, pitch, roll and FOV in one go. It uses height information that a two-sight-line intersection doesn't, and can compute the floor directly.

```bash
# spec.json: {"image_size":[W,H], "points":[{"name":…,"px":[x,y],"ll":[lat,lon],"h":<elevation ASL>}...],
#             "init":{"at":[lat,lon],"height":<elevation ASL>,"heading":…,"pitch":…,"hfov":65}, "fix":["hfov"]}
uv run scripts/pose.py solve spec.json --photo photo.jpg --out pose_check.jpg --search-radius 500
uv run scripts/pose.py project --pose pose.json --points river_bank.json --photo photo.jpg --out bank_check.jpg
```

- The heights of the points and of the camera position must use the same datum; always use elevation above sea level: ground points via `terrain.py elev`, rooftop = ground elevation + building height.
- Spread the points across different directions and distances in the frame; if they all lie on one line the solution is unstable (the script warns).
- Check `rms_px` in the output (reprojection error; >15 px means a point is misidentified or the height datums are inconsistent) and `radius_m` (95% error radius; use it directly as the radius in the conclusion).
- **`--pt-sigma` must be set to match reality** (default 5 m): how many meters of error the control points you clicked on satellite imagery carry. Sharp-edged ones like building corners and bridgeheads 3–5 m; a tower in a cluster of trees or a round building whose center you can only estimate 10–15 m. Control-point coordinate error doesn't propagate into the reprojection residual (if all points shift the same way, the camera shifts with them and the residual stays the same), so it can only be propagated by the `--pt-sigma` Monte Carlo; you can't see it from rms alone. Set it too small and the reported radius is too small: in synthetic tests with a true 15 m but 5 m entered, coverage dropped from 95% to 53%.
- `radius_px_only_m` in the output is the old measure (3σ of pixel noise only), kept for comparison; **don't use it as the conclusion's radius**: with coordinate noise ≥5 m it covers the ground truth only about 70% of the time.
- After solving, use `project` to project riverbanks, roads and building corners back onto the photo and check them item by item; this is an independent second verification step.
- Check on synthetic data: 8 points, 1.5 px noise, position error about 30 m (600 m height, points several km away); heading and pitch error <0.1°.
- **Works for level shots too**: standing on the ground shooting distant towers, bridges or piers, add `height` to `fix` and give the eye height as `init.height` (same datum as the points). Accuracy depends on how widely the points spread in bearing: in synthetic tests (4 px pixel noise, 5–15 m coordinate noise) with the points all crowded within 10°, the median error is about 50 m and bad ones reach 200 m; spread to 40°, about 25 m. When they're crowded, report the conclusion's radius from `radius_m`; don't shrink it because "it matches".
- **The main source of error is misidentified points, not the solver**: one misidentified point (wrong feature, a courtyard outline taken as a building corner, a tower of the same kind on the map that isn't the one in the frame) can pull the camera position off by tens of meters to over a hundred. `leave_one_out` in the `solve` output re-solves with each point removed in turn: `pred_err_px` is how far off this point is when predicted from the other points; `suspect` flags one only when "the remaining points fit clearly better without it" (the threshold is conservative; synthetic tests: downward shots with 7 points, false alarms about 1/20, detection about 12/20; level shots with 6 points unstable, detection 6–17/20; not possible when there is no redundancy after removing a point); `most_improved` lists "which point's removal improves things most" whether or not it passes the threshold — in a real case the mislabeled point was right there but didn't pass the threshold. Nothing flagged doesn't mean no point is misidentified.

When several candidate camera positions all make sense and you need to pick one (a viewing platform marked on the map vs another stretch of shore on satellite imagery, several buildings on the same alignment line), use `check`:

```bash
# cands.json: {"candA": [lat, lon], "candB": [lat, lon, <eye elevation ASL>]}; without a height, init.height is used
uv run scripts/pose.py check spec.json --cands cands.json
```

- Each candidate camera position is held fixed; only heading, pitch, roll (and the focal length if not fixed) are solved, and reprojection errors are compared; then it re-scores with each point removed in turn, and `robust_delta_chi2` takes the minimum over all removals. **Only `robust_delta_chi2` > 9 counts as not matching the photo**, and then it can be the file for `board.py exclude --computed`; looking only at `delta_chi2` over all points can be flipped by one misidentified point (synthetic tests: with one misidentified point mixed in, the ground truth ranked first dropped from 15/15 to 1/15).
- Measured on synthetic tests (90 runs, including ones with a misidentified point mixed in): the true camera position was never robustly judged a mismatch; with all points correct, decoys 120 m away were excluded 10–15/15, and 60 m away 6–8/15.
- **It is for removing clear mismatches, not for picking out the ground truth**: in 160 synthetic tests it wrongly eliminated the ground truth only once (excluding by `solve`'s camera position + radius would wrongly eliminate it 35 times, so exclude with `check`, not with the radius); but in scenarios where `solve` itself breaks down (points all crowded within 10–12°, coarse point marking), it ranks the ground truth first only about half the time. Ranking first isn't final; still go back to street view/satellite imagery and check invariant features.
- One more thing: few points isn't fatal (4 well-spread points still solve to a dozen or so meters); **what's fatal is all the points crowded in one bearing** — better to use fewer points and look for them on both sides.
- When two candidates differ only on one point (`robust_by` is the same "drop X"), the geometry can't separate them; first go back and check X. If they still can't be separated, rely on the scene (is the foreground an open lawn, can you see water), and state in the conclusion that the scene decided it.

## 11. Compute the view before excluding: out of frame, occluded or too small ≠ absent

Before you use "X is not in the frame" to exclude a camera position or a whole direction, you must compute it first. Common mistakes: a landmark sits right at the frame edge, so you assume "that famous building next to it would be visible if it were there"; imagining how wide a video screenshot's frame is using the main camera's FOV; a distant tower is only a few pixels, and you say "not seen".

```bash
# Identified landmark A is at x=1000 in the frame (width 1080), FOV unknown; check whether B and C should appear from the candidate camera position
uv run scripts/geo.py frame --at <camera position lat,lon> --anchor A:<lat,lon>:px=1000:h=<height>:w=<width> \
    --width 1080 --hfov 8:70 --pt B:<lat,lon>:h=<height>:w=<width> --pt C:<lat,lon>:h=<height>:w=<width> --cam-h <camera height>
# Place candidate camera positions in rings around A (radius 1–13 km, every 15°) and compute in one go which directions "no B" can exclude
uv run scripts/geo.py frame --ring <A's lat,lon>:1000:13000:1000:15 --anchor A:<lat,lon>:px=1000:h=<height>:w=<width> \
    --width 1080 --hfov 8:70 --pt B:... --out ring.json
uv run scripts/tiles.py mark area.jpg --points ring_keep.json --geojson ... --out ring_keep.jpg
```

- `--anchor` makes the heading change with the FOV: the narrower the FOV, the narrower the frame, and the more easily landmarks next to A fall out of frame.
- Each landmark gets a verdict: "in frame over the whole field-of-view range" / "in frame at field of view a–b°, out of frame otherwise" / "not in frame over the whole field-of-view range"; plus "may be blocked" (the height and width of a nearer landmark can block a farther one) and "may not be visible" when it is too small (`--min-px`, default 12 px).
- **Only a landmark that is "in frame over the whole field-of-view range, large enough and not blocked" can exclude this camera position by its absence**. Nearby buildings the script doesn't know about also occlude; a direction with tall buildings in the foreground still can't be excluded.
- Look up the landmarks' h and w or measure them on satellite imagery; h and `--cam-h` use the same datum.

## Common sources of error

- Computing a 2x or 3x photo as 1x underestimates distance by half to two-thirds.
- On satellite imagery the roof of a tall building is offset from its base, so you measure the wrong point.
- When shooting through window glass, reflections and window frames are easily taken as scene content.
- Declaring building level with only one alignment line (v006); reporting meter-level precision from the skyline outline alone (v010-1).
- Treating "out of frame", "hidden by a nearby building" or "so far away it's only a few pixels" as "not there", and excluding the correct direction (section 11).
- Computing video screenshots with the FOV of a phone photo: vertical video at 1x is only about 40°; add zoom and distances can be off several-fold.
- In SunCalc-style tools, pinning the shadow tip at the base of the wall when what actually casts it is the eave or canopy edge; a few meters off shifts the time by several minutes (v007).
