# Sky clues: sun, shadows, satellite dishes

Scripts: `scripts/sun.py` (`pos` / `ratio` / `locate` / `when` / `street` / `facing` / `compass` / `dish`). Compared with NREL SPA, the algorithm's error is ≤0.02°.
When there are no landmarks and text only gets you to a province or country, this is the main way to shrink hundreds of kilometers to tens of kilometers (v001: from hundreds of kilometers down to tens).

## When to take this branch

| Condition | What you get |
|---|---|
| Clear shadows + known capture time (puzzle setter's hint, EXIF, screenshot status bar, chat log timestamps) | Sun elevation angle → a band on the map; plus direction → a segment of the band |
| Clear shadows + location already fixed | Capture time and date (two candidate sets) |
| Satellite TV dishes in the frame | Photo heading (use them as a compass); dish azimuth → longitude range |
| The sun itself in the frame (sunrise/sunset, backlight) | Lens heading and the true bearings of objects in the frame (`sun.py compass`); given a clock time, you can also exclude countries with the wrong time zone |
| Overcast, night, indoors | Not usable; don't force a calculation |

Be clear about the capture time: posting time and IP location are not the capture time and place; treat them only as hypotheses to verify.

**Without a time, don't infer road direction, river direction or course from the sun's direction**. The sun at the side of the frame only says the lens is roughly perpendicular to the sun's azimuth; morning, noon and afternoon correspond to completely different directions (the creators in v002, v008 and v012 all reasoned this way and happened to be right; the method doesn't hold).

## 1. Determine the photo heading first

In order of reliability:
1. **Satellite dishes**: dishes in the same area point the same way. China's Hu Hu Tong (direct-to-home) small dishes point at ChinaSat 9; in eastern cities they face southwest (about 215°–227°), in the west south or even southeast (see the table in section 5). In Europe dishes generally face south, slightly east.
2. **Shadows or lit faces + time**: north of the Tropic of Cancer, the noon shadow points due north, northwest in the morning and northeast in the afternoon, turning clockwise through the day. With a date and time, compute it; don't estimate:
   `uv run scripts/sun.py pos --at <approx. location> --time 2025-01-26T08:53 --tz Asia/Shanghai`
   On winter mornings before 9 a.m. the sun's azimuth is about 120°, not due east (v006 took the sun as due east; the river direction could be off by 30°). Whichever face of a building is brightest faces roughly toward the sun.
3. **Lit faces** (when there's no measurable shadow): a wall is lit if and only if the angle between the sun's azimuth and the wall's normal is less than 90°. Intersect the lit/shaded state of several walls and you get a range for the lens heading:
   `uv run scripts/sun.py facing --at <approx. location> --time <time> --tz <time zone> --lit left --shaded camera`
   Describe walls by which way they face in the frame: `camera` faces the lens, `left` faces frame left, `right` faces frame right. At the range boundaries the wall is nearly parallel to the sunlight; don't treat them as hard boundaries.
   **When shadow direction conflicts with wall brightness or the lit side of tree trunks, trust the shadow** (in two cases, reading wall brightness put the sun on the wrong side): white walls and pale bark also look bright in diffuse light. The easiest thing to read is a car parked at the roadside: use the car length of about 4.5 m as a ruler; how far the shadow extends beyond the front of the car and which side of the car it falls toward directly tell you whether the sun is in front or behind, left or right, and roughly how low its elevation angle is. Tree-shadow stripes on sidewalks come from trees outside the frame and their direction is hard to judge; use them only as a reference.
4. **The sun itself in the frame**: it is the compass. Compute the lens heading from the sun's pixel position; you can also compute the true bearing of any object in the frame (tower, chimney, building corner), to judge "which block is the tower in the photo" within a candidate factory site and which side of the building the camera position is on:
   `uv run scripts/sun.py compass --at <candidate area> --time <clock time> --dates <possible date range> --tz <time zone> --sun-x <pixels> --width <image width> --hfov <FOV range> --x <object pixels>`
   - Only a time given, no date: compute over the possible date range, and the bearings become ranges; then add `--elev lo:hi` from how high the sun is above the horizon in the frame; dates whose elevation doesn't match are dropped automatically and the range narrows.
   - Neither time nor date: `compass` defaults to the whole year, split into a sunrise set and a sunset set. Around 30°N, the sunset azimuth swings between about 240° and 300° over a year; the difference is enough to make a top-down template not match. **Posting time is not capture time**; don't use the posting month to narrow the date.
   - Telling sunrise from sunset: what the poster says, sky color, shadow changes, road traffic and streetlights. Don't use reasons like "nobody at the school → after school", which holidays and weekends overturn (v014). If you can't tell, build templates for both headings.
5. **Roads on satellite imagery**: once you have location candidates, match the directions of roads, walls and riverbanks in the frame against satellite imagery.
6. Claims like moss or tree crowns leaning one way are unreliable; don't use them.

## 2. Measure the shadow length ratio

`sun elevation angle = atan(object height / shadow length)`. Only the ratio is needed, not real sizes.

- Pick **vertical** objects (wall corners, utility poles, lamp posts, vertical wall edges) and their shadows on **flat** ground.
- Prefer shadows parallel to the image plane (spread sideways); a shadow pointing toward or away from the lens is heavily foreshortened, so pick another object.
- For wide-angle photos, first correct barrel distortion, then draw guide lines along the perspective direction to measure (the v001 creator corrected first, then measured).
- In the same image, the shadows of vertical objects on flat ground must be parallel to each other. Not parallel = uneven ground, a non-vertical object, an artificial light source or a composite image.
- Measure with at least two objects and take a range. A 20% shadow-length error gives a 6–8° elevation-angle error near 45°.

```bash
uv run scripts/sun.py ratio --shadow 1.2           # 1:1.2 → 39.8°
```

## 3. Known time → a band on the map

The points where the sun's elevation angle is the same at the same moment form a large circle centered on the subsolar point; adding tolerance makes it a band. Intersect it with the existing candidate areas.

```bash
# Beijing time 2023-08-15 16:20, shadow ratio 1.2, ±1°, candidate area in North China
uv run scripts/sun.py locate --time 2023-08-15T16:20 --tz Asia/Shanghai --ratio 1.2 --tol 1 \
        --bbox 34,110,42,122 --step 0.05 --mosaic north.jpg --out band.jpg
# Add the shadow bearing (northeast, 60°±10°) and the band shrinks to a segment
uv run scripts/sun.py locate ... --shadow-bearing 60 --az-tol 10
```

- When the time is uncertain, add `--time-tol 30` (±30 minutes).
- `--mosaic` draws the band directly on a low-zoom base map from `tiles.py fetch` (zoom 7–9), for the evidence image.
- Verified: plugging in a video puzzle's known answer point and the time the puzzle setter gave, the computed shadow ratio matched the creator's measurement.

### China-specific: a single Beijing time = a longitude clue

The whole country uses UTC+8, yet spans 73°E–135°E. Beijing time of solar noon (shadow pointing due north): Shanghai about 11:56, Lanzhou about 13:06, Lhasa about 13:57, Urumqi about 14:11 (June; it shifts by about another ±15 minutes over the year).
So **knowing the clock time + being able to see the shadow direction** directly constrains longitude: if the shadow still points due north at 2 p.m., it can't be in the east.

## 4. Known location → capture time and date

```bash
uv run scripts/sun.py when --at 30.25,120.16 --date 2024-10-01 --tz Asia/Shanghai --ratio 1.2 --shadow-bearing 30
uv run scripts/sun.py when --at 30.25,120.16 --dates 2024-01-01:2024-12-31 --tz Asia/Shanghai --elev 40 --shadow-bearing 330
```

- The same sun position occurs twice a year (symmetric about the summer or winter solstice), so results always come in two sets of dates; pick one using vegetation (fallen leaves, flowering, rice-paddy color) and clothing.
- Date resolution is high around the equinoxes; for several weeks around the solstices dates are nearly indistinguishable; say so when reporting.
- The same elevation angle occurs at two times in a day, morning and afternoon; separate them by shadow **direction** (v007: 08:39 shadow to the northwest, 15:03 shadow to the northeast).
- **Report the sensitivity before the time**: `when` prints "1° off ≈ N minutes". Write out how many minutes a 1 m error in object height and a 1 m error in shadow length each correspond to (v007: each 1 m of object-height error shifted the time by about 13 minutes; the creator's ±5 minutes was luck).
- Align the shadow tip with the edge that actually casts it (eave, canopy, railing top), not with the base of the wall.

### Known city and date → street orientation

Only the angle of the shadow's **direction** relative to the street lets you infer the street orientation; shadow length doesn't (v009 inferred the orientation from shadow length; the reasoning doesn't hold).

```bash
# In the top-down view, turning clockwise from the street direction to the shadow direction is 90° (shadow perpendicular to the street); if you can't tell clockwise from counterclockwise, add --both
uv run scripts/sun.py street --at 49.25,-123.10 --date 2025-04-01 --tz America/Vancouver --ratio 1.5 --tol 4 --shadow-rel 90
```

Outputs two sets of directions, morning and afternoon. In a grid city one direction cuts out half the streets; when the date is uncertain, try several days and see how much the direction changes.

## 5. Satellite TV dishes

Dishes point at geostationary satellites above the equator; the azimuth is determined by "the difference between the local longitude and the satellite's longitude".

China's Hu Hu Tong / Cun Cun Tong (direct-to-home / village coverage) small dishes (35–60 cm diameter, common on rooftops in rural areas and urban villages) almost all point at ChinaSat 9 (92.2°E):

| City | Azimuth | Elevation |
|---|---|---|
| Harbin | 224° | 27° |
| Beijing | 215° | 38° |
| Shanghai | 227° | 42° |
| Guangzhou | 225° | 54° |
| Lanzhou | 199° | 46° |
| Chengdu | 202° | 52° |
| Kunming | 204° | 59° |
| Lhasa | 178° | 55° |
| Urumqi | 173° | 39° |
| Kashgar | 156° | 41° |

```bash
uv run scripts/sun.py dish --at 31.2,121.5 --sat 92.2               # forward
uv run scripts/sun.py dish --lat 31.2 --sat 92.2 --azimuth 213       # dish faces 213° → longitude about 109°–113°
```

- Azimuth readings are more reliable than elevation. Small dishes are mostly offset-feed; the dish face looks more "upright" than its actual pointing (offset angle 20°–25°), so don't take the dish face tilt as the elevation angle.
- Large dishes (1.5 m and up) at institutions and cable TV stations may point at ChinaSat 6B (115.5°) or an AsiaSat satellite; you can't apply the Hu Hu Tong table to them.
- Common in Europe: Astra 1 (19.2°E, Germany/Austria), Hot Bird (13°E, Italy), Astra 2 (28.2°E, UK). There's a list in `sun.py`.

## Common mistakes

- Wrong time zone or DST: use an IANA name for `--tz` (`Europe/Berlin` handles DST automatically); don't hand-write +1/+2.
- Taking posting time as capture time.
- Measuring shadow length on slopes or steps; taking a slanted shadow (from a non-vertical object) as the shadow of a vertical object.
- Computing a band and looking only at its center line: the whole band within tolerance must be checked; prioritize the parts that intersect other clues.
