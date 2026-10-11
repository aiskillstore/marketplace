# Search: reverse image search, keyword image search, social media search

Use at step 3, in parallel with lookup-table clues. In 5 of the 20 puzzles in the videos this step was the breakthrough, yet it costs the least.

## 1. Reverse image search

```bash
# Make variants first: tight crop of a distinctive object / horizontal flip / grayscale enhancement / color-cast removal; rectify rephotographed material first
uv run scripts/imgprep.py variants photo.jpg --box 300,120,900,760 --out-dir v/
uv run scripts/imgprep.py variants photo.jpg --persp 312,140,880,95,905,770,290,720 --box ... --out-dir v/
# Baidu image search + Yandex; each image gets a result screenshot and JSON
uv run scripts/revimg.py photo.jpg v/*.jpg --out-dir rev/
```

**Always open the result screenshots and look**: extracted text is only an aid; the scenes in similar images and the titles of source posts matter more. Baidu's similar images are also saved as a numbered contact sheet `<name>_baidu_similar.jpg` (the top-left cell is the query image; number i corresponds to the source page of JSON `similar[i]`). Look at it first: for near-duplicate photos of the same object or scene, the source page (Dianping, Douyin, Xiaohongshu) often gives the shop name or location tag directly.

**How to use place-name labels**: Baidu image search's "图中可能是…" ("the image may show…"), Yandex labels and the Lens AI overview are all candidates; count votes separately by level:
- City level: count which city each crop and each engine named. The same city named by two different crops is more credible than "two contradictory specific places"; specific places that don't agree don't cancel the city they jointly point to.
- Place level: when a label is the name of a residential compound, housing development, hotel or organization, get its coordinates with `poi.py` and check; this often gets you to the area in one step:

```bash
uv run scripts/poi.py "<compound name>" --city <city> --region <cc> --out pois.json   # every same-name point in the city (sources from the region pack, WGS84)
uv run scripts/poi.py "<compound name>" --region <cc>                                  # no city: which cities in the country have a same-name point
uv run scripts/tiles.py sheet --points pois.json --zoom 18 --out pois_sheet.jpg
```

- When a label is the specific name of a common facility such as a school or residential compound, first open the "图片来源" ("image source") thumbnails to see whether it's the same place (one call): names on images of playgrounds or housing are mostly assembled by voting over similar images; if it isn't the same place, downgrade it to weak and don't bother getting coordinates.
- **Facility-type words** in generic labels ("grain drying complex", "cement plant", "greenhouse") are useful: use them to look up where that industry is concentrated, for category inference and candidate areas.
- When the label is generic ("blocks of housing", "city street", "school playground"), treat it only as weak evidence; if the whole image + one tight crop, one round in each of two engines, give only generic labels, stop; don't keep trying variants.

| Situation | What to do | Source |
|---|---|---|
| The whole image finds nothing | Box only the most distinctive object (statue, building, ornament); remove the sky and background buildings | v010-5, v010-6 |
| Stock photos may have been taken from the other side | Flip horizontally and search again | v010-5 (hit only after flipping) |
| Rephotographed material, oblique shots | Perspective-rectify, remove glare | v004 |
| Old photos with a yellow or purple cast | Remove the color cast or convert to grayscale | v010-6 |
| One engine has no results | Switch engines: Baidu is best for Chinese web pages, Weibo, Baijiahao and scenic-area content; Yandex fills in building and street scenes and foreign content | v009 (Yandex found nothing, Baidu hit) |
| The search UI language biases results | Google Lens with a Chinese UI favors similar buildings on Chinese sites; for foreign scenes switch to English or the local language | v004 |

**Google Lens**: from the server's egress it demands a CAPTCHA, so the script doesn't do it. If you have a browser tool (such as Claude in Chrome, which uses the user's own browser), use it directly: Google Images home → search by image → upload. In tests it is often stronger than Baidu and Yandex, but keep its two result blocks apart:
- "Exact matches / pages that include this image": provenance evidence; usable.
- "AI Overview": forces a place name out of similar-looking photos; a different crop of the same image can yield two places a dozen or so km apart. Treat it only as a candidate; it must be verified back at steps 6 and 7.

Without a browser tool, when Baidu and Yandex both have no results and the frame shows a foreign landmark or object, ask the user to try Lens once in their own browser.

### Keyword search in the local language

Write queries in the local language as well as English. `revimg.py --query "<words>"` runs keyword search on Chinese engines only (Bing China, Baidu Images, Sogou Images); elsewhere use your general web and image search tools. Region packs describe which local engines and platforms work and how to phrase queries (`regions.py show <cc>`).

### After a hit

- **Look at the rest of the set**: the hit post is often a set of images, and the others may show plates, road signs or shop names (v009: the plate was in the 5th image of the set). First use shared fixed objects (streetlights, walls, chimneys) to confirm that the photos in the set and the puzzle image are the same place.
- **The candidate's background doesn't match**: it may be a replica, an identical installation, or another branch of the same chain. Once you have the proper name, search another round for "<proper name> 复制品 / replica / 同款" (复制品 = replica, 同款 = same model); the official introduction where the original stands often says where the replicas are (v004).
- **The hit is only a "similar scene"**: use it as a clue (city, scenic-area name), not as a conclusion; go back to steps 6 and 7 to verify.
- **For news images, first judge whether it's a real photo**: many news sites illustrate articles with stock images, illustrations or even generated images; before comparing facades, check whether it is this place.

## 2. Choose where to search by object type

Region packs add local platforms per object type (`regions.py show <cc>`).

| Object | Where to search | Source |
|---|---|---|
| Scenic-area buildings, viral check-in spots | The local short-video and photo-sharing platforms (the region pack names them); official scenic-area accounts post videos from the same angle | v010-2, v009 |
| Statues, small park features, foreign attractions | User photos on travel review sites (Tripadvisor and local equivalents); Google Lens | v010-6 |
| New residential developments, commercial complexes | Development albums and listing photos on local property sites; page all the way to the signboard | v010-5 |
| Old buildings, historic sites | Local culture-and-tourism and protected-heritage-site pages; stock image sites (Getty, Alamy and local agencies), whose captions carry place names and years | v004 |
| Ordinary streets and residential areas | Image search adds little; prioritize geometry and infrastructure; when even the city isn't fixed, sample one page of arterial-road street view per candidate city and compare municipal fixtures (the street-view script the region pack names) | — |
| Sub-brand stores of chain brands (truck service, refurbishment, specialty stores) | **Search opening press releases first** ("开业 / inaugura / abre / opens + sub-brand + state or city"; 开业 = opens), trade media often give the street address; treat the official store locator only as a candidate pool: it doesn't tag sub-brands, and its coordinates may be off by several km | blind test |
| Nameless facilities found on satellite imagery (plants, warehouses, farms, mines) | Search the web and news for the facility-type word in the local language + nearby place names, and compare the accompanying photos with the facade; once you find the name, search images another round | v013 |
| Vehicle livery (bus, taxi, school bus) | `revimg.py --query "<city> <color description> bus"` in the local language, and read route signs and company names from the result images; first resolve any place name you read to a district with `poi.py` before using it; don't treat a vehicle from district A as a clue for district B | v014 |

## 3. Descriptive keyword image search

Suits objects that "you can't name, but have a rare shape" (the v004 fountain).

1. Write the object as a "shape + components + position" phrase: `顶上有金色球形装饰的白色钟楼` (white clock tower with a golden ball ornament on top), `蓝色拱形顶棚的人行天桥` (pedestrian bridge with a blue arched canopy).
2. Prepare both a version **with place names** and one **without**, one set each in the local language and in English, and search them together. Finding nothing with place names is normal: replicas and obscure places have few photos online, while there is more material on the original and on similar objects.
3. If you can't count the shapes, use broad words; don't write a wrong count.
4. Use style words (Romanesque, Gothic, Hui-style) only after checking the form: if the arches are pointed, it isn't Romanesque.

## 4. Social media and check-in spot search

- Viral scenery (cherry-blossom streets, ginkgo avenues, influencer walls, check-in cafés): search `<city> + <scenery>` on the local platforms, **in both the local language and English** (English posts about popular foreign streets often include the street name).
- Other posts from the same place give more angles (houses, steps, chimneys) and even location tags.
- Locals' photos of the same mountains or the same river: look in the candidate town's local feed or its place page on those platforms (the v010-1 creator spoofed the device location to the candidate township to browse local content).
- A city usually has only a dozen or so popular check-in streets; find the list first, then check them one by one.

## 5. Open data (use when clearly effective)

- **City street-tree data** (species, trunk diameter, height class, address number, coordinates): many cities abroad have open datasets (e.g., Vancouver's `public-trees` on `opendata.vancouver.ca`, about 180,000 trees citywide, `exports/csv` takes about 20 s in one request). Suited to puzzles with "a row of some kind of tree + residential street, no text": it narrows the whole city to a few dozen street segments, with the ground truth among them (proposed in the v009 breakdown, used in one real case). Method:
  1. **Pull all species**, not just the target species: later you need to judge "are there trees across the street", and pulling only Prunus would make an opposite side planted with other trees look empty.
  2. **Use cultivar and trunk diameter only to sort, never to filter**: the cultivar in the municipal inventory may not match the actual tree (pale pink Somei-Yoshino-type blossoms in the photo; the inventory lists a white-flowered cultivar), and the trunk diameter may have been measured years ago. Cultivars of the same genus with similar flower color all go in as candidates; exclusion can only rely on invariant features in street view.
  3. **Use odd/even address numbers to fix which side of the street the trees are on**: comparing the coordinates of odd- and even-numbered trees on the same street tells you (in Vancouver, odd numbers are on the north side of east–west Avenues and the west side of north–south Streets; east–west Streets follow the Avenue rule). Then filter with "which side you're standing on, which way you're facing" from the shadows.
  4. **Compute the across-the-street constraint from the field of view**: a portrait phone's horizontal FOV is about 50°, so the grass strip across the street (10–20 m sideways) enters the frame only beyond about 25 m ahead; "no trees across the street" constrains only about 25–50 m ahead, not close by.
  5. Add the filtered street segments to the board in one go with `board.py add --from <street-segment JSON> --level road`; when you drop one, write `evidence --against` with a comparison image (SKILL hard rule 9).
  6. For street view, first pick historical captures from the same season as the photo (`gsv.py near` to see the history, `sheet --date <year>`) and compare facades, retaining walls and lamp-post positions; in summer captures tree crowns and bloom differ a lot, so don't skip a segment because "the trees look small".
- Local government and media reports: after locating, look up the name, size and year built of unusual man-made objects in the frame (scenic spots, towers, statues) (v008).

## Common mistakes

- Using only one engine and searching only the whole image; after a failure, not changing the image or the engine.
- Turning the "object category" from an AI or image recognition directly into a location ("boat-shaped sculpture → tourist city"); this jump counts only as weak evidence (v005).
- Getting carried off by the "most famous similar place" the search turns up and forgetting to come back and check bearings and details (the main way the AI failed in v010).
- Two engines each point at a different city, and you draw a big circle around the midpoint of the two and call it done: instead run a discriminating test and pick one as the main answer (SKILL hard rule 8).
- Image search gave a residential compound or housing-development name, and you didn't get its coordinates.
