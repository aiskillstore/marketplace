---
name: geo-sleuth
description: Geolocate or chronolocate a photo with tool-verified reasoning (where was this taken / when was it taken / photo geolocation / geo-guessing). Given one or more photos, one command does metadata, OCR and reverse image search (intake.py); clues and candidates go on a candidate board (board.py) that ranks them by script and gives the next step; lookup-table clues via clues.py (calling codes, driving side, territories; plates, area codes and other country tables from region packs); satellite imagery and street view are both "the machine ranks first, you look only at the top few" (CLIP-ranked satellite scan in sat_scan.py, DINOv2+SIFT-ranked street view in match.py); plus EXIF, reverse image search (Baidu/Yandex), sun and shadow math, OSM Overpass and DEM skyline rendering. Every conclusion is checked against real data; output is coordinates + error radius, evidence images and tiered confidence. Use when the user shares a photo and asks where was this taken / geolocate this / when was this taken / 这是哪 / 在哪拍的 / 帮我定位这张照片 / 网络迷踪 / 图寻 / 几点拍的.
---

# geo-sleuth (v2)

Goal: find a location that **holds up under checking**. Every conclusion must point to the clue it used, the command it ran and the file it produced.

> `${CLAUDE_SKILL_DIR}` in commands means the directory containing this SKILL.md (the same for commands in references). Claude Code substitutes it automatically; in other agents, first `export CLAUDE_SKILL_DIR=<absolute path of this directory>` before running (if the shell doesn't keep variables between commands, prefix every command with it), or replace it with that path directly.

The work is split into three layers. Remember this first, then read the flow:

| Layer | Who | Tools |
|---|---|---|
| Decision: which candidates exist, how evidence is scored, whether a candidate can be excluded, what to scan next | **Script** (candidate board) | `board.py` |
| Perception: reading text, table lookups, finding targets in satellite imagery, street-view matching | **Scripts compute and rank first; you look only at the top few** | `intake.py` `ocr.py` `clues.py` `sat_scan.py` `match.py` `geo.py bearings` |
| Judgment: pulling clues out of the image, proposing hypotheses when the tables have nothing, deciding among the machine's top few | **You** | — |

The method comes from breaking down 14 photo-geolocation (网络迷踪) creator videos and 22 puzzles, plus several rounds of blind-test comparisons; the breakdown notes are not published with the repo. The lesson of v1: rules written as prose don't get executed, and two runs of the same skill version gave very different results; so v2 puts every rule that can be written as code into `board.py`.

## Hard rules (always in force; ★ = enforced by board.py, just follow it)

0. If the user says the photo isn't theirs, or the image shows a private residence or minors, ask once what it's for before continuing; when the prompt already states the source or purpose (an evaluation puzzle, a puzzle setter's hint, the user says they took it), don't ask, and go to the finest level as usual.
1. **Don't fabricate verification.** "Measured on the map", "matched street view", "±10 m" must correspond to commands actually run and files actually produced in this session. If you didn't run it, write "unverified".
2. **Precision needs a source**: an error radius ≤100 m requires the intersection of two independent constraints, or a ground-level match on ≥3 invariant features. Before reporting a camera position, run a self-check: `pose.py project --horizon <sea-horizon row>` computes what the pitch should be and each feature's "expected row" for the current camera position; reconcile that with the photo (the depression angle to a target ≠ the camera's pitch; look up the camera position's elevation with `terrain.py elev` — if the height difference doesn't match the depression angles in the image, the camera position is wrong).
3. **Once you have a unique anchor, close the loop**: all later search and geometry starts from the anchor; don't go back to generic features like "blue-green lake water" or "tropical park" and pick the most famous place of that kind.
4. **Compute bearings first, then identify structures**: which block in satellite imagery is the tower or chimney in the photo is itself an interpretation. First compute its true bearing in the image with `sun.py compass` or a confirmed landmark, then use `geo.py bearings` to see which outline around the candidate camera position falls on that bearing; when nothing fits, first try both templates ("original/mirrored", "sunrise/sunset"); if not verified, only lower the tier, don't exclude.
5. ★ **List the whole category before inferring**: when inferring a region from "hill city", "tropical", "IP in a municipality", use `board.py children` to add all subordinate admin divisions as candidates, then rank them with evidence. Don't default to the main urban district, don't pick by population.
6. **Metadata and hints are hypotheses**: when EXIF, IP location, location tags or the puzzle setter's words conflict with the image, the image wins; don't invent a story to reconcile them. IP says country A but the hint or the regulation designs (plates, signs) point to another continent: intersect with `clues.py lookup territories <country A> --continent <continent>`.
7. **Self-consistency**: redo each key judgment once with a different crop or keyword set; if the two results differ by tens of kilometers or more, lower the tier.
8. ★ **If you can't pin a point, give a range + what information is missing**; when the candidates are a few discrete ones, don't take the midpoint: the main answer of `board.py report` is always the top-ranked candidate; the rest go into alternatives with discriminating tests.
9. ★ **Exclusion and confirmation use the same standard**: `board.py exclude` only accepts read/computed clues + a computed file (output of `geo.py frame`, `terrain.py`, etc.); observed and inferred clues can only down-weight via `evidence --against`, with the likelihood ratio clamped to 1/3–3 (inferred) or 1/5–5 (observed). Generating candidates from "there's an X nearby" is also filtering, and X must be something confirmed in the image. Fine-level candidates such as campuses, residential compounds and street segments must go on the board too: add a batch at once with `board.py add --from <poi.py --out / osm.py geom output> --level area/road`, don't hand-pick; when you drop one, write `evidence --against` with a comparison image, and `check` lists candidates without a single piece of evidence (meaning nobody looked at them); a finer candidate goes under the one that contains it (a point under its street segment: `--parent`, or `board.py move`), so its support counts in that level's ranking, and `check` fails when it skips a level; labels from third-party data (tree species in a municipal inventory, an exact school-name match) can only down-weight, never justify exclusion (in two cases the ground truth was skipped by hand exactly this way). **The excluded extent must be ≤ the evidence extent**: for candidates with extent, such as districts, areas and roads, `exclude` needs `--covers lat,lon[:lat,lon]` stating which stretch the evidence covers; the script rejects coverage below half (excluding a whole road after looking at one point on it failed in two cases).
10. ★ **Population and fame are not evidence**; scan order follows "share ÷ pages" (`board.py next`): finish the small districts first, put large districts last with a page cap.

## Flow

You don't have to go through every step: if reverse image search in step 1 hits directly, jump to steps 6 and 7 to confirm. Every step's output goes on the candidate board.

### Step 1: steps 0–3 in one command

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/intake.py photo.jpg --out-dir intake/ [--box x0,y0,x1,y1 ...]
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py init --photo photo.jpg
```

`intake.py` usually takes 1–2 minutes, longer on the first run because it installs dependencies: give the command a generous timeout (10+ minutes) or run it in the background. If a command timeout interrupts it, the reverse-image-search subprocesses may still be writing into `rev/`, but `intake.md` won't be generated; don't treat it as finished.

`intake.md` contains: metadata, OCR text (lines read from upscaled/tiled passes are marked pass=up/tile and are hypotheses), Baidu similar images (source-site counts + numbered contact sheet), reverse-image-search labels with tiered vote counts, likely residential compound/development names, the list of edge crops, and failed items. Then you do four things:

- **Look at the image**: go through every crop in `edges/` (four edges, four corners); run through the checklist in `references/observe.md`; log each clue with `board.py clue "<text>" --kind <kind> --status observed|read|inferred|computed --file <zoomed crop>`. Be honest about status: text you read is read; "the building is probably 8 floors", "the road goes uphill" are inferred.
- When a computed result actually tests an earlier clue, link it with `clue "<result>" --kind <kind> --status computed --file <output> --resolves K1` (repeat `--resolves` for multiple clues). An unrelated computation does not resolve a pending infrastructure clue; this link records the test, not support for a location.
- **Lookup tables**: calling codes, driving side, overseas territories are global; plates, area codes and other country tables come from region packs → `clues.py lookup <kind> <value> [--country <cc>]` (without `--country`, every pack is searched and matches from several countries are all returned). For those that resolve to an admin division, use `board.py apply --kind plate --value <plate prefix> --file <zoomed crop>` directly (adds candidates and evidence automatically; the other candidates at the same level are only down-weighted, not excluded).
- **Reverse-image-search results**: first open `rev/<name>_baidu_similar.jpg` (the top-left tile is the query image) and look for near-duplicates of the same object or the same scene; if there are any, go by number to `similar[i].from` in the JSON to see the source page; compound, development or hotel names in the labels → `poi.py "<name>" --city <city> --out pois.json` to get coordinates; for same-name hits (several campuses, several branches) put them all on the board with `board.py add --from pois.json --level area`, then check; always open the screenshots, and once a post hits, look through the rest of its photo set. Choose where to search by object type (`references/search.md`).
- **Hints and metadata**: log each as an inferred clue and state how credible it is; IP location only says where the person was when posting, and the posting time is not the capture time.
- **Country-specific material**: country-specific clues, tables, preferred services and tips are in region packs (`regions/<cc>/`). Once a country is a candidate, run `regions.py show <cc>`: it prints the pack's lookups, services and a one-line index of its clue entries with line numbers; read only the entries you need. When the country is settled, `board.py country <cc>`. `regions.py list` shows which packs exist; with no pack, use the global tools and `references/clues/global.md`.

### Step 2: list all candidates, score evidence, check the next step

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py children <parent admin area>          # municipality → all districts; country → first-level admin divisions (gazetteer.py queries OSM, with bbox)
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py evidence --clue K1 --for <candidate A>:5 --for <candidate B>:2 --against <candidate C>:0.3 --why "…" --file <comparison image>
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py rank
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py next
```

`next` only ever says one of two things:
- **Can't separate**: run discriminating tests from cheap to expensive, each one on all candidates at once — lookup tables → terrain (plain vs. hill city, `tiles.py fetch --zoom 13` or `terrain.py`) → vehicle livery (image search for "<city> <color> bus" in the local language; read route signs from the result images, compare the stripe along the bus rear by district) → street fixtures (street view per candidate built-up area) → river/road-network templates. Still can't separate after all of them: don't stop; scan in the "share ÷ pages" order it gives. `next` replaces these lines with the region pack's tips when the board's country is known.
- **Ready to narrow**: first narrow the extent to the built-up area with `board.py urban <candidate>` (or give it by hand with `scan-bbox`), then write a falsification condition with `board.py falsify <candidate> --text "…"`, then go to step 3.

The coarse environmental-location rules still apply: terrain before river width and building color; phenology must be paired with the month; take the intersection of rare facility combinations; recognizable species are only an exclusion tool; when all you have is a land type, first narrow to that type of land with a land-cover map (`references/clues/`).

### Step 3: pick a branch to narrow down

| What you have | Approach | Read |
|---|---|---|
| A unique anchor (building, statue, tower, scenic-area building) | Anchor geometry: sight-line intersection, alignment lines, tangent lines, filtering buildings by camera height | `geometry.md` |
| Distant mountains, skyline | Render candidate camera positions with `terrain.py view` and compare; this fixes only one sight line, then find a second constraint. No EXIF: don't assume the main camera (distant mountains are often zoomed); a best focal on the edge of the searched range means widen and rerun. Near range in front of a far one: score both layers | `geometry.md` |
| Clear shadows, lit faces, the sun in the frame | `sun.py locate / when / facing / compass`: latitude band, time, heading, true bearing of objects in the image | `sky.md` |
| Route numbers, railway or power-line specs, a large river | Linear corridor + line-to-point: `osm.py route / crossings / along` | `corridors.md` |
| Two or three kinds of infrastructure in one frame | `osm.py near --report`; crossings of two linear types `osm.py intersect` (bends are only annotated, not removed) | `corridors.md` |
| Linear infrastructure + unrecognized mountains, no text | Compute horizons from elevation along the infrastructure and filter a whole region → score skyline + distance to infrastructure numerically → overlay the top 3–5 → fix the camera position from evenly spaced structures: `terrain.py scan --lines … --out hits.json --clusters-out clusters.json` → `terrain.py ridge photo.jpg --x0 … --x1 … --out ridge.json` → `terrain.py fit --hits hits.json --ridge ridge.json [--line … --line-dist …] --sheet top.jpg --photo photo.jpg` (for the fine search switch to `--at lat,lon --radius 800 --grid 100 --zoom 13`) → `imgprep.py piers photo.jpg --rows … --out cols.json --sheet piers.jpg` → `geo.py spacing --cols … --line … --span … --center lat,lon --ridge ridge.json` | `corridors.md` 4.3, `geometry.md` 7.4 / 7.7 |
| Clear street layout, no anchor | `osm.py street-scan` to filter intersections → `tiles.py sheet` → street view | `corridors.md` |
| No near-duplicates from reverse image search, no text, only a set of scene elements (road spec + adjacent features + landform) | **Don't hand-pick spots first**: write the scene as one English query and let CLIP rank with `sat_scan.py grid --bbox <coastal strip/corridor> --zoom 17 --cell 360 --query … --neg …`; look only at the top 20–30 thumbnails; `grid` beats `points` because OSM features like `amenity=parking` may be incomplete | `search.md` |
| ≥4 points of known location in the frame (window views, looking down; also level shots of distant towers, bridges, piers — fix the height) | `pose.py solve` solves camera position, heading and height; when several candidate positions all fit, score them one by one with `pose.py check --cands`; only robust Δchi2 > 9 may go to `board.py exclude --computed` | `geometry.md` section 10 |
| Want to exclude by "there's no X in the frame" | `geo.py frame` first computes whether X should be inside the frame, large enough and not occluded; only what it says can exclude goes to `board.py exclude --computed` | `geometry.md` section 11 |
| Recognizable facility type (grain dryer tower, feed mill, sugar mill, concrete batching plant) | Look up the industry's distribution → enumerate large buildings with `osm.py buildings` → rank with `sat_scan.py points` | `search.md` |
| Stores of a chain's sub-brand | First search opening press releases for the address; use store locators only as a candidate pool → `osm.py along` + street-view sampling | `search.md` |
| Plane window, drone shots looking down | Aerial branch | `aerial.md` |

### Step 4: finding the spot in satellite imagery — the machine ranks first

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/sat_scan.py grid --bbox <scan_bbox> --zoom 17 --preset track --multi-scale --top 30 --out sat.json --sheet sat_top.jpg --heat heat.jpg
uv run ${CLAUDE_SKILL_DIR}/scripts/poi.py "<district> <school, in the local language>" --city <city> --region <cc> --out schools.json      # seeds: --seeds schools.json boosts nearby cells
uv run ${CLAUDE_SKILL_DIR}/scripts/sat_scan.py points --points big.json --preset factory --out r.json --sheet r.jpg   # rank candidate points from osm.py buildings / poi.py
```

- Presets: track (running tracks), stadium, factory, silo, dam, bridge, quarry, solar, greenhouse, port; custom `--query`. In tests: across 300-odd cells of an urban area, more than half of the OSM-mapped running tracks made the top 30; in an old town in China where OSM is blank, a school's sports field still ranked first. **It ranks, it doesn't decide**: look at the thumbnails of the top 20–30 cells, then check them against the bearing and shape in the photo.
- Translate the image description into top-down features before looking: curved buildings, octagonal pavilion roofs, sports courts, parking spaces perpendicular to a railway; for tall buildings look at the base; imagery has a date.
- With many candidates, make a candidate table: one row per point, one column per criterion directly visible in the photo.
- Nothing in the top 30 matches: first go back to the "candidates down-weighted by inference" listed by `board.py check` and to the falsification conditions, then switch preset or go to z18, and only then widen the area.

### Step 5: confirmation — street view is ranked first too

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/baidu_pano.py scan <lat,lon> --radius 300 --out panos.json                     # the street-view script the region card names (CN: baidu_pano.py); otherwise gsv.py
uv run ${CLAUDE_SKILL_DIR}/scripts/match.py rank --query photo.jpg --panos panos.json --toward <landmark lat,lon> --spread 15 --refine sift --top 10 --out m.json --sheet m.jpg
uv run ${CLAUDE_SKILL_DIR}/scripts/match.py rank --query photo.jpg --items around.index.json --render gsv --spread-headings -30,0,30 --out m.json --sheet m.jpg
```

- `match.py` coarse-ranks by DINOv2 global similarity and fine-ranks by SIFT inliers; in tests, ground-truth street views of the same place from different years all made the top 4. Open only the top 10 and compare **invariant features** (building outline, window positions, balconies, pole positions, curbs, ridgelines), not vehicles, signs or foliage. ≥2 features for road level, ≥3 for building level. Not a single image with ≥15 inliers **doesn't mean it's wrong**: with a change of season, an old capture, or the photo taken from the sidewalk while street view was shot from the middle of the road, the ground truth had only 5 and 0–8 inliers in tests (two cases); first open the top 10 and compare invariant features, and only if none fit change `--spread-headings` or widen `--within`. The global score gets dominated by season (a blossom-season capture ranks high wherever it is), so compare against a historical capture from the same season as the photo when you can (`gsv.py sheet --date`).
- With many panorama points, group by date and road; `sheet --road <road name> --spread 60` shows one road only; older captures have a more open view.
- No street view doesn't mean you can't confirm: compare ridgelines with `terrain.py view --photo`; find a name for the candidate facility (OSM name, nearby place name + the facility-type word in the local language) and search news, encyclopedias and official-site photos to compare facade details.
- When street view is many years older than the photo, go by old buildings and permanent structures.

### Step 6: fix the camera position and write the output

- Look back: at the matching street-view point, turn 180° and see what's on the photographer's side.
- A camera position needs two independent constraints (`geo.py intersect` sight-line intersection, `geo.py line` alignment line, `pose.py` multi-point solve, camera height, reverse street view); with only one, building-level confidence is at most "medium".
- When there's no measurable shadow, use lit faces for the heading: `sun.py facing --lit left --shaded camera`. For photos taken from a car, boat or train, state the direction of travel.

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py check                      # before concluding: do exclusions have files, does the main answer have verified evidence, which clues went unused
uv run ${CLAUDE_SKILL_DIR}/scripts/board.py report --merge result.json # main answer = top-ranked; alternatives, exclusions and unused clues are written into result.json automatically
uv run ${CLAUDE_SKILL_DIR}/scripts/evidence.py spec.json --out evidence.jpg
```

Show `evidence.jpg` to the user together with the answer, without waiting to be asked. A road-level claim from satellite imagery needs a ≥z18 crop, not a z17 glance.

Output:
1. One-sentence conclusion: place + camera position + heading (+ direction of travel and capture time, where applicable)
2. Coordinates: WGS84, plus the local datum when the region card names one (`geo.py convert`), **with error radius**
3. Evidence image (satellite image marking the camera position and heading wedge + comparison images)
4. Reasoning chain: clue → inference → **commands actually run and files produced** → extent
5. Tiered confidence (table below). **Rate each level separately; the tier you report is the finest level rated "medium" or above**: a low building level doesn't drag down a high area level
6. Excluded candidates and reasons, alternatives and discriminating tests, clues not used or not resolved (generated by `board.py report`)
7. When you can't pin a point: which level is settled + what information is still needed

Use English for tool messages, report headings and generated labels. Preserve source text (OCR, place names, service responses) verbatim as evidence; explain or translate it for the reader. Write the agent's final report in the user's language. In Chinese, use 高/中/低 for high/medium/low and 城市/片区/路/楼/楼层 for city/area/road/building/floor.

| Level | High | Medium | Low |
|---|---|---|---|
| City | Text, plates, area codes or a confirmed anchor | Several independent weak clues agree | A single weak clue, or only the hint |
| Area | A unique facility or landmark matches ≥3 top-down features in satellite imagery (whole candidate area checked, no second match) | The most similar spot in the candidate area, with candidates still unchecked | Inferred |
| Road | Ground-level match on ≥2 unique features | Layout consistent, 1 unique feature; **when there is no ground-level imagery at all**: area level high + bearing self-check passed | Satellite layout only |
| Building | Two independent constraints + ground-level match on ≥3 features | One of the two | Inferred |
| Floor | Two kinds of reference agree | A single reference | Don't give |

## Budget and stopping conditions

- `intake.py` counts as one call; if reverse image search with 3 different keyword sets finds nothing, stop and go back to the checklist for other clues.
- **While candidates still can't be separated, don't scan any point one by one** (when `board.py next` says "can't separate", do the discriminating tests first); if they still can't be separated after the cheap tests, scan in the order it gives, the first 3 pages of each candidate's built-up area first.
- Scanning and confirmation always rank first: look at the top 30 cells from `sat_scan.py` and the top 10 images from `match.py`; widen only when all of the top ones are wrong, instead of paging through.
- Run `osm.py coverage` before enumerating candidates with OSM: districts with sparse data get silently excluded; switch to `sat_scan.py grid` and say so in the conclusion.
- Scan panoramas in batches of at most 500 points per area. When a batch or several areas yield no match, review candidate generation, search coverage and down-weighted candidates; then change the approach or widen the justified search scope. A fixed number of unmatched areas is not a reason to end the investigation.
- A failed or unavailable service blocks that route, not the whole investigation. Consider other feasible sources or methods; do not repeat unchanged failing requests.
- Before stopping, `board.py check`: go back through the top 20 candidates, in ranking order, that were down-weighted by inference but not excluded.
- Conclude when evidence supports the requested location level, the user asks to stop or a user-set budget is reached, or no remaining feasible action is likely to distinguish the candidates. If unresolved, use `board.py report` to state the supported level, actual search coverage, attempted routes, blockers and missing evidence; do not invent a coordinate or precision to finish.

## Runtime environment

- Python 3.10+, `uv`, and `curl`. Always use `uv run ${CLAUDE_SKILL_DIR}/scripts/xxx.py`; each script declares its dependencies. `scripts/` in references is relative to this skill directory.
- On first setup or after a runtime failure, run `uv run ${CLAUDE_SKILL_DIR}/scripts/doctor.py`; add `--network` to check service reachability. Read the English checks and fixes before starting an expensive scan. It uploads no photos and does not load ML models.
- Reverse image search uses local Google Chrome, with automatic fallback to Playwright Chromium (`uvx playwright install chromium`). If neither starts, use `intake.py --no-rev` and report the skipped search. OCR prefers Apple Vision on macOS and uses RapidOCR elsewhere or as a fallback.
- `match.py` and `sat_scan.py` install ML dependencies and download model weights on first use. Allow extra time and disk space.
- Cache goes to `.geo-cache/` in the current directory; the candidate board is `board.json` in the current directory. Script list and data sources: `references/data-sources.md`.
- macOS has no `timeout` command; in zsh `$var` doesn't word-split, so use `bash -c` or `${=var}` in loops. A province-wide Overpass query can take several minutes; run it in the background.
