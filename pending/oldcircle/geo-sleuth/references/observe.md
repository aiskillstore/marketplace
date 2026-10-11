# Image-reading checklist

Used in step 1. Don't guess a location until the checklist is written. Number every item, write the original text or the shape, and mark anything you can't make out as "illegible".
Ordered top to bottom by "how much area it can exclude": one clue higher up outweighs twenty below it.

## 0. First scan the whole frame

```bash
uv run scripts/imgprep.py edges photo.jpg --out-dir edges/        # one zoomed crop per edge and per corner
uv run scripts/imgprep.py zoom photo.jpg --box x0,y0,x1,y1 --scale 4 --out z1.png
```

- Go through the four corners, the bottom edge, and the top edge one by one: cables, boat bows, car window frames, aircraft wings, fingers, watermarks, screenshot UI.
- Zoom into every distant sign and every vehicle once. The eye is pulled first to the most prominent landmark; small street signs are often more useful.

## 1. Shooting conditions (decide which branch to take)

| Item | What to record | Used for |
|---|---|---|
| Shooting platform | ground / upper floor of a building / in a vehicle / on a boat or pontoon / cable car / train / airplane / drone | boat bow → at a dock or the waterside; car window → on a road, record the direction of travel; aircraft wing → aerial branch. **Tell apart top-down from a building vs an expressway service area vs inside a vehicle on an elevated road**: from a building the camera position is steady, you can look down on car roofs and building roofs, and window frames or sills are common; at a service area look at the orientation of rows of parking spaces, slope-protection retaining walls, trash bins, and gas station facilities; inside a vehicle there are window frames, windshield reflections, guardrails rushing past. Get the platform wrong and you pick the wrong co-occurrence conditions later |
| Camera height | eye level or looking down; how many stories' rooftops you can look down on | filter buildings by height; test claims like "shot from the road" |
| Focal length | EXIF equivalent focal length; if absent, judge from distortion and near/far compression | field of view, distance estimates |
| Image processing | rephotographed (reflections, print edges, perspective distortion), screenshot, cropped, mirrored (reversed text, driver's seat on the unexpected side; with no text, look at hand gestures and clocks; reposted videos are often flipped horizontally); **video screenshot** (vertical 9:16, platform watermark, subtitle bar) with unknown zoom | correct before searching; flip mirrored images back before reading; compute the field of view of a video screenshot as a range (`geometry.md` section 1) |
| Time | watermark, EXIF, shadow length and direction, daylight, season | sky branch; phenology judgments |

## 2. Layer 1: text, phone numbers, language

- Shop signs, street-name signs, organization names, construction notices, public notices: copy the original text and search the original, not a translation.
- **Issuing authority at the bottom of signs** (〇〇交警支队 traffic police detachment, 〇〇城管 urban management, 〇〇警察署 police station, 〇〇土木事務所 civil engineering office): often gives the district (county) directly.
- **Destinations and terrain words mentioned in notices** ("no way through to the coast ahead", "to such-and-such scenic area").
- **Phone numbers**: record the area-code part and the digit grouping (first work out how many digits the area code has).
- Language and script: simplified/traditional characters, dialect characters; for foreign text, identify the writing system before reading the characters.
- **Official multilingual signs**: two languages on one official sign → an officially multilingual area (not "near a country that speaks that language").
- Chain brands: note sub-brands and business lines (only sub-brands with few stores have locating value).

## 3. Layer 2: vehicles and roads

- **Plates**: characters (province/city code) → if unreadable, background color, color bands, graphics, border → failing that, aspect ratio (Europe long and narrow, North America about 2:1). Note where the vehicle is parked (plates in a parking lot count only as weak).
- **Driving side**: which side traffic keeps to, which side the driver's seat is on, which way cars parked at the roadside face.
- **Public transport**: bus operator abbreviation, route number, rear ads; taxi color; bus roof color (clearest in top-down shots).
- Road marking color and style, guardrails, curb paint (alternating red and white, etc.), streetlight design and color, gutters, whether there is a grass strip between sidewalk and roadway.
- Overhead gantry direction signs: when the text is illegible, count the destination lines and note the background color.

## 4. Layer 3: infrastructure specs (can be looked up in data)

- **Railways**: catenary or not; masts on one side (usually single-track) or on both sides or with portal frames (double-track); how many parallel tracks at a level crossing; viaduct or embankment; railway company name on crossing signs.
- **Power lines**: tower type (single tubular steel pole / angle-steel lattice tower); how many conductors per bundle per phase (common in China: 4 per bundle = 500 kV); angle relative to railways, rivers, roads.
- **Special transport facilities**: cross-river cableways, road/rail-transit bridges, light rail through a building, high-speed rail bridges, long urban escalators, cable cars.
- **Classify cables at the frame edges**: high-voltage lines (tall towers, insulators, separate phases, nearly horizontal over crossing spans) / passenger cableways (two or three closely parallel track ropes + a haul rope, steeply slanting and sagging) / cable-stayed bridge stays (fanning from the tower top) / ordinary wires (thin, messy, hung on utility poles).
- Solar water heaters, density of AC outdoor units, security window grilles, rooftop water tanks.

## 5. Layer 4: sky

- Shadows: direction (relative to the frame, relative to the road), ratio of length to object height, whether they are parallel to each other.
- Satellite TV dishes: heading, size (small Hu Hu Tong dish / large dish).
- Lit face: which face of a building is bright.
- The sun itself, sunrise and sunset, backlit silhouettes.

Details in `sky.md`. Without a time of day, shadow direction is only a weak constraint.

## 6. Layer 5: architecture and vegetation

- Roof color and material (red terracotta / gray tile / flat roof / blue sheet metal), facade material (tile color, paint, stone).
- For building elements, check the basic shape before using style words: round or pointed arches, number of window panes, columns.
- Skyline: whether there are office clusters or supertall towers (weak: judges the city's tier).
- Vegetation: evergreen or deciduous, flowering stage (first bloom / full bloom / petal fall), palms, bamboo groves, rice paddy color. **It must be paired with the month of capture to mean anything.**
- Fog, cloud, snow, ice: only weak supporting evidence.

## 7. Layer 6: terrain and water

- Plain or mountains; how far beyond the far bank the mountains rise; whether buildings are stacked up the slopes.
- Rivers: width (use houses, lanes, terraces as a ruler), water color (sediment load), landforms on both banks, river islands, confluences, bridge positions.
- Distant mountain outlines; towers, statues, pylons on peaks (skyline fingerprint).
- Coastlines; mountain silhouettes across a bay.

## 8. Negative clues

Write down what is absent: no utility poles, no snow, no palms, no motorcycles, no Chinese-character signs, no office towers. Negative clues can exclude regions just like positive ones.
**Negative clues depend on visibility**: not seeing mountains or a river in the distance in haze, backlight, or dusk doesn't mean they aren't there; to use one, first compute from the distance whether it should be visible (`terrain.py view`, `geo.py frame`); otherwise use it only for ranking.

## Rules for writing the checklist

- For anything unclear, describe only its shape, color, and position ("a light-colored patch with clean edges on the ridge"); **don't rush to name it**. A wrong name gets it discarded as something ordinary.
- If you can't count it, write a broad word ("polygon"), not a wrong exact number.
- Text that is only "read" after zooming in to the level of compression noise is a hypothesis.
- When two clues conflict, write it down: it may be mirroring, an imported vehicle, a border area, a composite image.
