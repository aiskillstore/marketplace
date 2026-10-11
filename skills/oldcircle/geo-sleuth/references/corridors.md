# Linear corridors and structured queries

Use when there are no landmarks and no text, but the image shows a **route number, railway, power line, large river or expressway**.
The core idea in two sentences: **first turn the area into a line, then look for discrete points on the line**; **when several kinds of infrastructure share the frame, use a query to enumerate every co-occurrence point in the whole province at once**; don't scan the whole map.
Sources: v002 v003 v007 v008 v010-3 v011.

Script: `scripts/osm.py` (find / near / crossings / route / along / intersect / street-scan / buildings / geom / raw). Output is `{name: [lat, lon]}`, which goes straight into `tiles.py mark` to plot the points and `tiles.py sheet` for numbered candidate thumbnails.
OSM data in China is incomplete: a hit is a candidate; a miss can't be used as grounds for exclusion.

Known gaps in OSM for China (measured in blind tests):
- `building` and `parking` are basically empty in counties and townships, and missing even in many urban areas of prefecture-level cities — **in China, don't use buildings or parking lots as co-occurrence conditions**.
- Many rivers have only a centerline and no water-area polygon; the riverbank shape can only come from satellite imagery.
- A whole-province query can take several minutes, and public servers also rate-limit; run it in the background, or run provinces separately.
- In mountain cities, curves, hairpin turns and retaining walls are everywhere; don't use them as co-occurrence conditions (in a blind test the core of the main urban area had nearly 700 hairpin turns; adding "school, arterial road" still left dozens, none of them right).
- **Check coverage before enumerating candidates**: `osm.py coverage --areas <district A>,<district B> --filter '<feature>'`. If one candidate district has noticeably fewer features, the co-occurrence query silently excludes all of it (common in China: almost none of a whole district's schools or running tracks are mapped).

## 1. Route number → corridor

The operator abbreviation + route number on top of a bus's rear, bus stop signs, metro line numbers, origin and destination on long-distance coach signs (v007: operator abbreviation + route number on the bus rear → one route corridor).

```bash
uv run scripts/osm.py route --bbox <s,w,n,e> --kind bus --ref <route number> --step 150 --out route.json
uv run scripts/tiles.py fetch <center of a segment along the route> --zoom 17 --radius 4 --out seg.jpg
uv run scripts/tiles.py mark seg.jpg --points route.json --out seg_route.jpg
```

- When OSM doesn't have the route, search "<city> <route number> 路 线路图 / bus route" (路 线路图 = bus route map), then on a map manually record the coordinates of a few stops and connect them.
- Before scanning along the route, combine what is "behind the buildings" and "behind the camera" in the photo into filter conditions: construction hoarding or tower cranes showing above the rooftops = a construction site behind; a glass curtain wall reflecting nothing but trees = green space across the street (v007).

## 2. Railways

| What you see | What it implies | How to query |
|---|---|---|
| Railway company name on a level-crossing sign (JR西日本 (JR West), private railway names) | Operating area or specific line | The company's operating area |
| Catenary masts on one side only | Usually a single-track electrified railway (a small share nationwide) | `["railway"="rail"]["electrified"="contact_line"]["tracks"="1"]` (tracks is often untagged in China) |
| Masts on both sides, or portal gantries spanning the tracks | Double track | — |
| 4 tracks side by side at the same level crossing | Quadruple track or several lines running in parallel; only a few sections nationwide | `osm.py crossings --kind level_crossing`: OSM has one crossing node per track, and the script estimates the track count from the node count |
| High-speed rail viaduct | Along a high-speed line | `["railway"="rail"]["highspeed"="yes"]["bridge"]` |

```bash
# All level crossings on a stretch of railway, by track count (each is labeled "~N tracks")
uv run scripts/osm.py crossings --bbox <s,w,n,e> --line '["railway"="rail"]' --kind level_crossing
```

Order for railway scenes: line (company name, track count, electrification) → station (terrain conditions such as by the sea, by a river) → compare each level crossing or bridge along the line against satellite imagery.
The web version of OpenRailwayMap (openrailwaymap.org) shows line class and single/double track very clearly; good for manual comparison.

## 3. Power lines

- Tower type only separates "transmission / distribution": tall steel-tube monopoles or angle-steel lattice towers with long insulator strings = transmission; short concrete poles or wooden poles = distribution.
- Read the voltage from bundled conductors (common in China): single conductor ≈ below 220 kV, bundles of 2 = 220–330 kV, **bundles of 4 = 500 kV**, bundles of 6 = 750 kV or ±800 kV DC, bundles of 8 = 1000 kV.
- When you can't count the conductors at a distance, look for small dark dots at intervals along the line (spacers): present → bundled conductors, treat as ≥220 kV; if you can't narrow it further, don't commit to a single voltage.
- The voltage can also be looked up in reverse: find the same type of tower in street view at any known location, click that line on OpenInfraMap (openinframap.org) to see its voltage, and you get "this tower type ≈ X kV" (v002).
- **Useless alone, useful only in intersection**: only crossing or parallel relationships with railways, rivers and expressways narrow things down. The angles between several linear features (power line perpendicular to the railway, parking spaces perpendicular to the railway) are a spatial signature visible at a glance on satellite imagery (v011).

OSM tags: `["power"="line"]["voltage"="500000"]`, `["power"="tower"]`.

## 4. Co-occurrence queries (several kinds of infrastructure in the same frame)

Write the features that appear together in the image and have OSM tags as "B within x m of A, C within y m of B", and enumerate over a whole province or city (v010-3: high-speed rail bridges within 700 m of a power tower, rivers within 100 m of the bridge → a few dozen sites in the province → filter by plain/mountain and distant mountain outline).

```bash
uv run scripts/osm.py near --area <full name of the province-level division> \
  --a '["railway"="rail"]["highspeed"="yes"]["bridge"]' --b '["power"="tower"]' --within 700 \
  --c '["waterway"="river"]' --within-c 100 --out cands.json
```

- **Loosen** distance thresholds to double your estimate from the image; better too many than missing one, then filter with terrain, distant mountain outline and satellite imagery.
- `--area` takes the full admin-division name used in OSM (e.g. "江苏省" (Jiangsu Province), "深圳市" (Shenzhen City)); if it isn't found, switch to `--bbox`.
- Over 200 results: add conditions; don't go through them one by one.
- Adding `--report near.json` writes each candidate's actual distance to B and C and its key tags (voltage, electrification, line name), for ranking.
- **Rank, then look**: distance to towns and roads (`--rank-near`), whether the voltage class matches the image, whether the actual distance is close to the image estimate, terrain (`terrain.py elev` to see whether the railway is on a slope).
- `--rank-near` is only a rough ranking: in China, OSM town nodes, hotels and residential land-use tagging are all uneven (residential land use even includes villages, so ranking by it is almost useless). Town nodes `'["place"~"^(city|town)$"]'` are relatively the most stable; for service areas use `'["highway"="services"]'`.
- **What actually narrows candidates is attributes you can verify in the image**: countable bundled conductors → voltage, visible catenary → electrification, the track count at a level crossing. One verified attribute often cuts 80% of candidates, more effective than any distance ranking; if you can't verify it, widen it to a range (e.g. 220–500 kV); don't guess a single value.
- **Stopping rule**: view thumbnails in rank order with `tiles.py sheet`; if there's still no match after 100, stop and report "province/city level + candidate areas + why they didn't match"; don't keep scanning by eye.

## 4.1 Crossings of two kinds of lines (railway × power line, river × road)

```bash
uv run scripts/osm.py intersect --area <full name of the province-level division> \
  --a '["railway"="rail"]["electrified"="contact_line"]' --b '["power"="line"]["voltage"~"^(220000|500000)$"]' \
  --bend-min 25 --bend-within 100:900 --rank-near '["place"~"^(city|town)$"]' \
  --cluster 600 --out crossings.json      # for voltage, write only the range you can verify in the image
uv run scripts/tiles.py sheet --points crossings.json --zoom 18 --out crossings_sheet.jpg
```

- `--bend-min`: marks crossings where B has a bend away from the crossing point (angle tower, river bend); by default it **only labels them and ranks them first; it doesn't delete**.
- Only `--bend-filter` actually deletes; deleted ones are written to `<out>_dropped.json`. Use it only when "the line turns at this tower, and which side of the crossing the tower is on" is a fact you confirmed with your own eyes in the image; a bend position inferred from a distant view doesn't count.
- `--ring lat,lon:min_m:max_m`: keep only crossings within this distance ring around a point (e.g. a distance computed from the landmark's pixel size and the field-of-view range).
- Put voltage and electrification into the filter only when you can count the bundled conductors or see the catenary in the image; otherwise loosen them into ranking.
- Labels carry the line name, voltage, electrification, bend, and distance to the reference feature; look first at the ones that match the image.

## 4.2 Street-view geometry template (no anchor, but a clear street layout)

The photo only narrows to town level, but the layout in the frame is clear: the camera looks down a street, with a large building on the right and a wall and garden on the left. Write the layout as a template and filter the whole town at once:

```bash
# camera heading (a range from sun.py facing or shadows) → street bearing 320°–80°; a building with a footprint ≥250 m² 4–22 m to the right; no building 3–10 m to the left
uv run scripts/osm.py street-scan --bbox <town s,w,n,e> --bearing 320:80 --right building --left empty \
  --band 4:22 --clear 3:10 --ahead 0:40 --min-area 250 --out cands.json
uv run scripts/tiles.py sheet --points cands.json --zoom 19 --out cands_sheet.jpg
```

- By default it assumes the camera stands at an intersection looking down the side street; if not at an intersection, add `--anywhere --every 30`.
- Regression check: on one video puzzle, a whole town's 2265 roads and 5132 buildings filtered down to 38 candidates; the correct intersection was 3 m from a candidate point.
- Only suitable where OSM building data is complete (Europe and North America, Japan, the cores of some large Chinese cities); don't use it in Chinese counties and townships.
- Common tags: `["railway"="level_crossing"]`, `["man_made"="water_tower"]`, `["aerialway"]` (aerial ropeways, cable cars), `["bridge"="yes"]`, `["waterway"="dam"]`, `["leisure"="pitch"]`, `["amenity"="fuel"]`, `["man_made"="communications_tower"]`, `["historic"]`, `["tourism"="attraction"]`.

## 4.3 Linear infrastructure × terrain: no text, only infrastructure and an unidentifiable mountain

Section 4's co-occurrence queries can only use OSM tags; "a steep mountain in the distance" can't be written into them. The method is to connect each point on the infrastructure to elevation data, compute the horizon, and filter a whole large region at once. This is the single source for the method (one real case: about 27,000 railway-bridge segments in one large region (about 25,000 of them electrified or untagged) → 171 clusters, ground truth among them).

1. `osm.py geom '<infrastructure filter>' --bbox <large region> --out lines.geojson` to get the lines.
2. `terrain.py scan` samples points along the lines, computes a 360° horizon at each point from Terrarium elevation, filters by shape conditions and clusters:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/terrain.py scan --lines lines.geojson --out hits.json \
  [--clusters-out clusters.json] [--bbox s,w,n,e] [--step 400] [--zoom 10] \
  [--near-flat 40] [--near-radius 1200] [--near-step 300] \
  [--min-peak 4.5] [--max-low 1.2] [--flat-run 20] [--min-low-deg default=--flat-run] [--flat-run-cap 100] \
  [--eye 1.5] [--az-step 5] [--dist 1500,2000,2500,3000,3500,4000,5000,6000,7000,8000,9000] \
  [--skip-tag electrified=no ...] [--cluster-km 3.5] [--threads 8] [--max-tiles 4000] [--allow-missing]
```

- `--step` is the sampling spacing along the line (meters); `--zoom` is the elevation tile level (at z10 one cell is about 150 m; good enough, with few tiles).
- Filter conditions use only shapes that don't depend on heading and are visible in the image: `--near-flat` = relief within `--near-radius` m is at most this many meters (flat nearby), `--min-peak` = within a few km there must be a mountain at elevation angle ≥X°, `--max-low` = how low counts as a flat horizon, `--flat-run` = how many continuous degrees the flat horizon must span. `--dist` is the distance ladder used to compute mountains.
- `--skip-tag` skips lines by tag (repeatable); `--cluster-km` is the clustering radius for hits. If the tile count exceeds `--max-tiles` it exits with an error; shrink `--bbox` or lower `--zoom` first.
- `--cache` uses the same elevation cache as `terrain.py` (default `.geo-cache/dem`).
- Output `hits.json`: `{params:{...}, n_samples, n_hits, n_clusters, hits:[{lat, lon, h0: ground elevation m, max_ang: highest horizon elevation angle °, az: its azimuth °, relief: max relative height difference in that azimuth m, flat_run_deg: length of the flat horizon right next to the mountain °, name/hs/elec/id: the line's OSM tags}...], clusters:[...]}`. Clusters are sorted by `max_ang` descending; a cluster's representative is its steepest point (same fields as `hits`, plus `n` = number of points in the cluster); `--clusters-out` writes a separate JSON with only the cluster list.
3. The resulting clusters go into the batch skyline scoring in `geometry.md` 7.4 (`terrain.py fit --hits`). Without EXIF it searches 13–135mm by default; if the leading clusters all want the longest (or shortest) focal, widen `--f35-range` and rerun before reading the ranking.

- **When the mountain is right in front of you** (its foot a few hundred meters from the camera position), the defaults miss it: within the 1200 m `--near-radius` you are sure to climb onto its slope, and `--dist` starting at 1.5 km can't measure this mountain either. Shrink `--near-radius` to a few hundred meters (`--near-step` must be smaller than it, otherwise only the camera position itself is sampled and the flat-nearby check does nothing), and start `--dist` at 400 m. In hilly areas, loosening like this gives many candidates; when the skyline can't separate them, you need a second constraint.
- **When mountains fill the whole frame** (no stretch of flat horizon anywhere), the flat-run condition rejects the ground truth: pass `--flat-run 0 --min-low-deg 0` to drop it and rely on `--near-flat` + `--min-peak`, then rank with `terrain.py fit`. If the skyline alone can't separate the top clusters (rms within a few px of each other), add the heading constraint from the line (view ≈ perpendicular to the line when the wires cross the frame nearly level): `terrain.py fit --perp-line lines.geojson`. When a lower near range stands in front of the far one, score both layers (`ridge --near/--near-clear`, `geometry.md` 7.4); the outermost skyline alone ranked look-alike ranges level with the right one.
- **Set thresholds at about half the photo estimate**. At z10 one cell is about 150 m, peaks get flattened, and computed elevation angles come out low. In a real case, with thresholds set to the photo estimate, not a single point near the ground truth was kept; it came in only after loosening. Better too many than missing one; leave the count to the next ranking step.
- How far the infrastructure is at the left edge, center and right edge of the frame is also an independent numeric constraint: use evenly spaced structures as a ruler (`geometry.md` section 3) to estimate the three distances, and pass them to `terrain.py fit` via `--line` / `--line-dist` for joint scoring.

## 5. Large rivers: identify the river → river section → line-to-point

1. **Three things to identify the river**: width (use houses, lanes, terraced fields on both banks as a ruler), color (sediment load), landforms on both banks (plain / high-mountain gorge / low, broken gullies). The three combined are more reliable than color alone (many rivers are yellow in flood season).
2. **Determining the orientation** needs a time: compute direction from the sun (`sky.md`); don't assume "the shaded slope faces north".
3. **Filter river sections by orientation + terrain on both banks**: list sections with the same orientation, the same width and the same landforms on both banks, and exclude them one by one.
4. **Line-to-point**: find discrete structures on the line in the image — bridges (when the bridge deck isn't clear, look for a long thin shadow on the water), dams, ferries, tunnel portals, interchanges, docks — and list all such structures on this stretch of river. v008: an 850 km stretch of a large river → 26 river-crossing structures → 7 → 2 → 1.

```bash
uv run scripts/osm.py crossings --bbox <s,w,n,e> --line '["waterway"="river"]["name"="<river name>"]' --kind bridge,dam,ferry --out crossings.json
```

5. **Go through the candidate table one by one**: for each point, ask only a few questions you can see directly in the photo (does the river bend within the view, is there a reservoir, are both banks mountains, is there a large settlement); go through all of them once, then compare in detail. **Criteria compare only the section within the photo's field of view** (v008 excluded a candidate using a bend outside the view and nearly filtered out the answer).
6. When a few remain, compare ridgelines and the roads on them with `terrain.py view` or Google Earth's tilted view.

## 6. Template comparison between cities

When there are several candidate cities (v006: three candidate cities with similar layouts), write the large-scale structures in the photo as a template and compare city by city:

- Water system: how many rivers, each one's orientation (combined with heading), confluence angle, whether there's a river island, river width, bridge positions, whether the far bank is urban.
- Mountains: which side the mountain is on, how far from the urban area, whether there's a tower or statue on the summit.
- Road network: positions of elevated roads, roundabouts and railways in the urban area.

Features like river islands, whether rivers meet, and river width exclude at a glance; compare them first. Mind the satellite imagery's year (shorelines and river islands change with water levels and engineering works).

## Common mistakes

- Treating a probability bet as a filter: "green taxis are most common in Sichuan" so you only search Sichuan; "the top 20 cities" (v002, v006). These can add to a score; they can't exclude.
- Treating co-occurrence in two samples as a rule: "both places with this kind of pole are next to a railway → there's a railway near the photo too" (v002).
- Stacking inferences on a false premise: "snowy mountains in the distance → must be in a certain province → search only that province's railways"; the premise wasn't verified, so everything after it is wrong.
- Using an unverified interpretation as a hard filter: "the angle tower must be on the outer side of the crossing" — the true point was in the batch that got filtered out. Interpretations only rank; when nothing matches, first go back to the filtered-out ones.
- Excluding because OSM has no result: missing lines are common in Chinese data.
- Declaring failure when no candidate matches, without going back to check the filter conditions (hard rule 9).
