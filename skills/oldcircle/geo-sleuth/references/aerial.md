# Aerial branch: airplane-window photos, drone top-down shots

Ground-photo signs, license plates and street view are all useless here; what works is **aircraft registration → flight track**, or **landforms + hydrology → river section → line-to-point → 3D terrain comparison**.
Sources: v008 (large-river gorge from an airplane window), v012 (frozen lake through a cabin window + registration), v010-2 (gorge by drone).

## 1. Look for the aircraft registration first

The registration on the wing's upper and lower surfaces, engine nacelles and rear fuselage (Chinese civil aviation: `B-` plus 4 characters; seen from a cabin window it's often upside down, so check each character).

1. Look up this aircraft's flight history by registration on Flightradar24 or FlightAware (the free tier covers about 7 days; longer needs a paid tier; the paid tier can download KML/CSV tracks for single flights).
2. **Search the time window backward from the posting time**: casual photos were most likely taken the same day or a few days before (in v012 the correct flight was the one on the posting day, yet the creator went through all 114 flights over two months). If EXIF has a capture time, use it directly.
3. Filter the flight list layer by layer with conditions directly visible in the photo:
   - Day/night: takeoff and landing times against sunrise and sunset
   - Climate: the latitude band matching ice, snow cover, vegetation color
   - Terrain: whether the route passes over this kind of mountains/plains
   - Heading: the flight direction computed from the sun (see section 3)
4. Export the tracks of the remaining flights and look only at features on **the window side**, within visual range (tens of kilometers at cruising altitude).

Without a registration, cruising altitude, heading and common airways (which routes pass over this area) can serve as weak supporting evidence.

## 2. Which side you're sitting on, which way the nose points

- The wing's **trailing edge** has flap tracks and a row of fairings; the leading edge is smooth. Whichever side of the frame the trailing edge faces, the tail is on that side.
- Nose toward the left of the frame = right-side window; toward the right of the frame = left-side window.
- This determines which side of the flight track the ground features are on.

## 3. Infer heading from the sun (must be computed for the time)

- Whichever side the ridge shadows fall on, the sun is on the other side; lit slopes and reflections on water also work.
- **Don't assume "shadows point north"**: north of the Tropic of Cancer, shadows point due north only at noon; at 37° N at 10 a.m. in summer the shadow is already off by about 70°, and on winter mornings shadows are closer to northwest.
- With candidate flights, compute the sun azimuth at the time each one passes over the area (`sun.py pos --at … --time …`), then compare it with the lighting direction in the photo; this can tell right from wrong among several candidate flights (in v012 it could have been settled without asking the puzzle setter).
- When the time is completely unknown, direction is only a weak constraint and can't be used to exclude candidates.

## 4. No registration: landforms + hydrology

1. Identify the river (width, color, landforms on both banks) → list similar river sections → exclude by orientation and bank terrain → line-to-point (bridges, dams, ferries) → go through the candidate table one by one. Steps and commands are in `corridors.md` section 5.
2. For the **only man-made object** in the frame (a regular, light-colored patch on a ridge, a row of colored roofs, a tunnel portal), first describe its shape and position; don't label it "ordinary village" and discard it. It's often the anchor:
   - Crop it and search on short-video platforms and Baidu image search (v010-2 hit the scenic area's official account)
   - After locating it, check its name and size against map POIs + local news (v008)
3. Once the anchor is fixed, find a tangent line like "ridge — feature edge" in the photo and draw the same line on satellite imagery; the camera position is on that line (v010-2).

## 5. 3D terrain comparison (replaces street view)

On pure top-down satellite imagery, loess gullies and mountains all look alike; lower the view to near the photo's depression angle and the differences show.

```bash
# airplane window: give absolute altitude (cruise about 8000–11000 m, a few thousand meters during descent); negative pitch looks down
uv run scripts/terrain.py view --at <candidate lat,lon> --alt 9000 --heading 90 --pitch -35 --hfov 60 --range 40000 --zoom 11 --out a.png --photo puzzle.jpg
# drone: one or two hundred meters above ground
uv run scripts/terrain.py view --at <candidate lat,lon> --height 150 --heading 300 --pitch -20 --hfov 70 --range 15000 --out d.png --photo puzzle.jpg
```

- Compare ridgeline outlines, valley orientations and roads on ridges; for water bodies, compare bulges and inlets in the outline.
- High-altitude oblique views flatten shapes along the sight-line direction and skew them slightly; allow for perspective distortion when comparing; when needed, rotate and stretch the photo and overlay it on satellite imagery.
- Elevation data is about 30 m per cell: large mountain masses and river valleys are reliable; don't force comparisons of details smaller than a hundred meters.

## 6. Verify "what it is" with environmental data too

- Uniformly white water with no reflection, seen from high altitude, is most likely ice or snow on ice; after locating, confirm with the local historical daily temperatures (v012).
- Counterexamples: salt lakes, salt pans, dry lakebeds, turbid silty water, sun glint, thin cloud.

## Common mistakes

- Going through the entire flight list instead of checking "closest to the posting time first" (v012).
- Using "shadows point north" to infer heading or river orientation, and excluding candidates with it as a hard condition (v008, v012).
- Listing mountain ranges from memory and missing the one containing the answer (v012 didn't explain why the Lüliang Mountains were left out).
- Settling the final pick among a few by asking the puzzle setter, instead of using an independently doable test like sun azimuth (v012).
