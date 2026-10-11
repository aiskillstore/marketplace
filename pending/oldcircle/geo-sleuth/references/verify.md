# Confirmation and falsification

Used in steps 6–8. In the videos, the creators' most common problem isn't failing to find the place but **confirming too loosely**: declaring after checking only two items (v007), claiming a "two-meter error" from one alignment line (v006), dropping a pin and calling it found (v005).
AI's problem is worse: saying it "measured on the map" when it didn't (v010). The rules in this file are mandatory.

## 1. Write falsification conditions before looking at candidates

Before opening satellite imagery or street view, first write 2–3 "if this appears, give up" conditions, for example:
- "The road should be on the left of the building; if it's on the right, exclude"
- "The distant mountain should be on the far bank of the river; if it's on the same side, exclude"
- "Sunset has to be visible from here, so the camera heading must lean west"

If it appears, give up; don't look for reasons to explain it away. Confirmation bias is the number-one failure mode of this craft: you find a place that "looks right" and start making excuses for the differences.

**Falsification conditions themselves must also be verified**, otherwise they backfire and kill the correct answer:
- "From here, the landmark must be in the frame" → first compute it with `geo.py frame` (field-of-view range, occlusion, pixel size); see `geometry.md` section 11.
- Details inferred from a distant view, like "the line should turn at the tower" or "the building should have 8 floors" → if not verified, only rank; don't exclude.
- Record the candidates excluded by falsification conditions; when no candidate matches, first go back and recheck these conditions.

## 2. What to compare, what not to

| Compare (invariant features) | Don't compare (things that change) |
|---|---|
| Building outline, number of floors, window positions and spacing, balcony shape | Parked cars, pedestrians |
| Positions and number of utility poles and streetlights | Signs, ads, awnings (often replaced) |
| Curbs, wall corners, steps, manhole cover positions | How much foliage, whether flowers are in bloom |
| Ridgelines, riverbank lines, bridge positions | Construction hoarding, temporary structures |

- Only **independent** items count: the same sign photographed three times is one item, not three.
- To road level: ≥2 unique features; to building level: ≥3, plus two independent camera-position constraints.
- Common features like "factory buildings all faced with yellow tiles" don't count as unique features.

## 3. Bearing self-check (required before output)

Draw a top-down sketch on satellite imagery: camera position → foreground object → midground object → distant landmark, plus the direction of the sun or shadows. Check each item:
1. **Left-right order**: if A is left of B in the photo, it must also be so as seen from the candidate camera position.
2. **Near-far relationship**: if A blocks B in the photo, the candidate camera position, A and B must be roughly collinear, with A nearer.
3. **Heading and sun**: for a sunset photo the camera must face west; if, from the candidate point, getting the image's elements into one frame requires facing southeast, it can't be a sunset (v010-7: the point the AI chose could only shoot sunrise; off by 850 km).
4. **Sight line ahead along the road**: a tower straight ahead in a photo taken from inside a car must actually be in that road's direction of travel (v010-4 corrected a misidentified building with this one check).
5. **Compute the bearing first, then identify the structure**: which block on the satellite image corresponds to the tower, chimney or building corner in the photo is an unverified interpretation. When the sun is in the frame, use `sun.py compass --x <structure pixel>` to compute its true bearing, and search the satellite image along that bearing from the candidate camera position; don't first decide on the satellite image that "this is the tower" and then reason about left and right, and don't judge which block is tall from how the OSM building outlines are cut — for tall structures, look at shadow length and side walls on the satellite image. A misidentification makes the bearing self-check kill the correct candidate.
   Identifying tall structures on satellite imagery: first find a tall building that is certainly vertical and see which of its walls is visible — the satellite is on that side, and the tops of all tall objects lean the opposite way; only blocks with a visible side wall are tall, and the foot of a tower is at the bottom edge of the side wall, where the shadow starts, not at the center of the roof's projection; shadow direction is set by the sun and is not the same thing as lean direction. When both identifications are plausible, draw both sets of camera positions and check each against the bearing computed by `sun.py compass --x`.
6. **When bearings don't match, check for mirroring and sunrise first**: screenshots of reposted videos are often horizontally flipped. Without text, look at gestures (usually right-handed), clocks, the driver's side of vehicles; when the candidate facility is unique and only left-right doesn't match, build two templates each for "original / mirrored" and "sunset / sunrise" and check each one, then decide whether to downgrade or widen the search.

If any item fails, exclude, or downgrade and write down why.

## 4. How to confirm without street view

| Situation | Alternative |
|---|---|
| Mountains, outskirts, looking across a river from afar | `terrain.py view --photo` renders the candidate camera position; compare ridgeline outlines; remember the outline only proves "on this sight line", you still need a second constraint. With many candidates, batch-score first, then overlay (`geometry.md` 7.4) |
| Suburban hotels, factory compounds, scenic areas | Map POI photos, real photos of the hotel/scenic area online, tourist photos; compare the type, number and spacing of the pylons on the skyline (v011) |
| New housing developments, commercial complexes | Development photo albums on real-estate sites (v010-5) |
| Outside China | `gsv.py near / sheet --headings / render` (Google Street View, no key); when the puzzle image is a street view screenshot, use the watermark year with `sheet --date <year>` to get the same capture; clouds and season can also be compared |
| Rural areas, factory compounds, farms outside China, with no street view | **First find a name for the facility**: OSM name, nearby place name + the local-language word for the facility type (sawmill: scierie / aserradero and the like), search the web, and compare facade details in images from news, encyclopedias, company websites and blogs (v013's creator confirmed it this way); then try Wikimedia Commons image search by coordinates (no key, see `data-sources.md`); Mapillary needs a token, KartaView has little coverage |
| No ground photos of any kind | ≥3 top-down features uniquely matched on satellite imagery + bearing self-check passed: report area level as high, road as medium, building as low, and state that ground-level imagery is missing; don't fall back to district level overall just because there's no street view |

### Finding a storefront along a road

When you know the road name (address from a news article, the street given by reverse image search) but not the street number:

```bash
uv run scripts/osm.py along --bbox <s,w,n,e> --line '["highway"]["name"~"<road name fragment>"]' --step 120 --out pts.json
uv run scripts/gsv.py sheet --points pts.json --headings 30,90 --out road.jpg   # in China use baidu_pano.py instead
```

- Spacing ≤150 m: a storefront is only visible within a very narrow angle; at 400 m spacing you can easily miss every single one.
- Set headings from "direction of travel + which side the shop is on": in a right-hand-traffic country, shooting a shop on the right from inside a car while heading north, use 20–90°. To reproduce an upward shot of a storefront from inside a car, add `--pitch 15–20`.
- To find roadside factory buildings and fields, use satellite thumbnails: `--step 300–500 --side <north|south|east|west> --offset <meters from the road to the building>`, then `tiles.py sheet --zoom 16–17`.

### Picking street view points

- When there are many panorama points, group them by capture date and road, and render the ones with an open view first: waterside paths, bridges, intersections, older captures not blocked by street trees. Newer captures on main roads are often completely blocked by trees (the truly usable ones are often older-capture points on waterside paths and construction access roads).
- Look around from one point: `baidu_pano.py sheet --ids <id> --headings 0,60,120,180,240,300` (outside China use `gsv.py`).
- For farmland and countryside in China, first probe one or two points with `baidu_pano.py near <lat,lon>` to see whether there's a panorama, then decide whether to `scan`: in a real case a 1.5 km-radius `scan` over farmland ran for 5 minutes and found none.

## 5. Overlay comparison

When the two images have different perspectives, crop the sign, utility pole or window from the original, rotate and scale it, and paste it onto the corresponding position in the street view screenshot; whether it's the same object is visible at a glance (v002). Same for water and mountain outlines: rotate and stretch, then overlay onto satellite imagery and compare point by point (v012).

```bash
uv run scripts/imgprep.py zoom photo.jpg --box ... --scale 2 --out part.png
uv run scripts/baidu_pano.py render <panoid> --heading 47 --out sv.jpg
uv run scripts/evidence.py spec.json --out evidence.jpg      # satellite image + camera-position wedge + comparison panels
```

## 6. Historical imagery

- Street view taken many years before the photo: go by old buildings and permanent structures; new buildings may not exist yet, and signs may have changed (v003: the street view was 10 years older; the comparison used buildings and poles).
- New facilities (new schools, new factory buildings) aren't in old street view yet: first group by date and look at the newest capture; if it shows demolition, hoarding or tower cranes, that's ground evidence that "something was built here later", and it also gives the photo an earliest possible year.
- Conversely, you can date the photo: find slowly changing things (extent of climbing-plant cover, tree crown size, hoarding, whether a new building has gone up), compare them across street view or satellite imagery from different years, and you can bracket it to within a year or two (v004).
- Judge the season from the phenology in the photo, not from the month the reference street view was taken (v004's creator called it "winter" from the date of a December street view).

## 7. When there are many candidate cities or candidate points

- Make a candidate table: one row per candidate, one column per criterion, fill in "matches / doesn't match / can't tell", and in the last column write the reason for exclusion.
- Look at candidate points one page at a time: `tiles.py sheet --points cands.json --zoom 18`; each cell is centered and numbered, more accurate than finding points in a large mosaic (reading pixels off a large mosaic displayed scaled down is off by 50–100 px).
- Criteria use only things directly visible within the photo's field of view.
- Go through all of them once before looking closely at what remains; don't stop at the first one that "looks like it".
- When candidates come from OSM, first check each candidate area's data volume with `osm.py coverage`; an area with sparse data being absent from the candidate table doesn't mean it isn't the one — scan it separately with `tiles.py sheet --grid`.

### Finding a sports field (common in top-down shots from windows)

1. Read the sports-field template from the photo: the angle between the track's long axis and the camera direction (lying across the frame ≈ perpendicular to the camera direction), which side of the track the pitch and basketball courts are on, the shape of nearby buildings (L-shaped, enclosed square), adjacent open ground or slopes.
2. The camera direction comes from the sun (`sun.py compass`; without a date, compute over the whole year) or from roads or rivers in the frame; if two headings can't be separated, use two templates.
3. First look at the whole urban area in one z16 mosaic; bright new sports fields stand out at a glance; convert pixels to coordinates with `tiles.py px2ll`. When you need to find all fields, new and old, lay a grid over the candidate district's urban area: `tiles.py sheet --grid <urban area s,w,n,e> --zoom 17 --size 320 --cols 5` (one cell ≈ 330 m, 25 cells per page ≈ 1.5 km × 1.5 km), and look for red running tracks cell by cell (a track covered by building shadows shows only a section of arc).
4. Compare matched fields to the template, then work back from the field toward the camera to find the building the camera is in (which side of the teaching building is visible, which road lies between, how large the depression angle is).
5. Don't assume "track lying across the frame = long axis perpendicular to the sight line": see which end of the track's far edge is lower (closer); if it's slanted, it isn't perpendicular. After identifying ≥4 points (track curves, basketball court corners, building corners), solve heading and camera position with `pose.py solve`; don't compute by hand.

## 8. Final check before concluding

- [ ] Every "matched" and "measured" has a file actually produced in this session
- [ ] The error radius comes from intersection geometry or multi-item comparison, not made-up decimal places
- [ ] All four bearing self-check items passed
- [ ] After finding an anchor, you didn't go back to generic features to pick another place
- [ ] Category inference listed all candidates, with exclusion reasons written
- [ ] Conflicts between hints, IP, EXIF and the conclusion are explained (the image wins)
- [ ] The key step was redone with a different crop or keywords, with consistent results
- [ ] If you couldn't pin a point, you wrote "the level it's determined to + what information is still missing"
- [ ] Every exclusion reason was verified: exclusions by "X isn't in the image" had the frame and occlusion computed; unverified interpretations were used only for ranking
- [ ] When the candidates are a few discrete ones, you chose a main answer, not a midpoint with a big circle
