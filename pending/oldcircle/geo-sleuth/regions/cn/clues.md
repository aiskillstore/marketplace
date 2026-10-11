# Mainland China clues

Entries use the shared format (`references/clues/README.md`); lookups: `clues.py lookup plate|area-code|admin --country cn`. Ordered by the layers in `references/observe.md`: platform metadata → text and plates → vehicles and traffic → infrastructure → climate and phenology → terrain and water → urban form.

## Platform and metadata (all of it is a hypothesis to verify)

### IP location label on comments/posts
- Look for: the province shown next to comments and posts on Douyin, Xiaohongshu, and Weibo (a country for users abroad), together with the posting date
- Points to: which province the poster was in at the moment of posting, not where the photo is
- Strength: weak; raise to medium when the stated story is "shot today, posted today" and the watermark time matches the posting time
- Counterexamples: posting while traveling, old photos, going online through a proxy (v006: the photo was in a province neighboring the IP province); the puzzle setter's "not in X" is itself a hypothesis to verify. When it conflicts with the image, keep "matching areas in this province + neighboring provinces"; don't exclude a whole province
- Sources: v004 v006 v010 v011

### Photo timestamp watermark / EXIF time
- Look for: a date-time watermark in a corner of the frame; DateTimeOriginal as read by `exif.py`
- Points to: month and time of capture → phenology judgments, sun calculations
- Strength: medium (the watermark can be wrong because of camera settings; EXIF can be edited)
- Counterexamples: rephotographed images, metadata stripped after reposting; camera time zone not set
- Sources: v006 v010-3

## Text and plates

### Shop signs, street signs, organization names
- Look for: place names on shop signs, company plaques, and street-name signs; search the original text
- Points to: province / city / street
- Strength: street-name signs and organization names strong; place names in shop signs medium (chain stores and out-of-town companies mislead)
- Counterexamples: chain brands; shops named after somewhere else ("重庆火锅" Chongqing hotpot, "沙县小吃" Shaxian snacks)
- Sources: general; case001

### Issuing authority at the bottom of signs
- Look for: small print in the corner of traffic signs, prohibition signs, public notices, and construction signs: 〇〇市公安局交警支队 (〇〇 city public security bureau, traffic police detachment), 〇〇区城管 (〇〇 district urban management), 〇〇街道办 (〇〇 subdistrict office)
- Points to: city, district (county); often names the admin division directly
- Strength: medium (if legible, it reaches the district; the name of an agency with cross-district jurisdiction is not the district you are in)
- Counterexamples: blurry small print is easy to misread; it needs a second instance to confirm
- Sources: v003 (the same technique used abroad; applies equally to signs in China)

### Landline area codes
- Look for: landline numbers on signs, ads, and construction notices (mobile numbers don't map to a region)
- Points to: roughly blocked by first digit: 010 Beijing, 02X municipalities and megacities (020 Guangzhou, 021 Shanghai, 022 Tianjin, 023 Chongqing, 024 Shenyang, 025 Nanjing, 027 Wuhan, 028 Chengdu, 029 Xi'an); 03 North China and the Central Plains (Hebei, Shanxi, Henan); 04 Northeast and Inner Mongolia; 05 East China (Jiangsu, Shandong, Anhui, Zhejiang, Fujian); 07 Central and South China (Hubei, Hunan, Guangdong, Guangxi, Jiangxi); 08 Southwest (Sichuan, Guizhou, Yunnan, Tibet); 09 Northwest (Shaanxi, Gansu, Ningxia, Qinghai, Xinjiang). Look up the full area code in the table to get the prefecture-level city
- Strength: medium (a full area code reaches the city)
- Counterexamples: first judge how many digits the area code has from the digit grouping; 400/800 numbers and mobile numbers don't map to a region; a company headquarters number may be in another city; a few area-code blocks have exceptions (e.g., codes starting with 06 belong to parts of Shandong, Guangdong, and Yunnan); the lookup table is authoritative
- Sources: v003 (method); the block pattern is general knowledge, check the table before citing it

### License plates
- Look for: the first Chinese character is the provincial abbreviation, the second-position letter is the prefecture-level city code (A is usually the provincial capital; exceptions: Qingdao 鲁B, Shenzhen 粤B, Dalian 辽B, Xiamen 闽D, etc.; check the table); background color: blue for small vehicles, yellow for large vehicles, gradient green for new-energy small vehicles, yellow-green for new-energy large vehicles, black for foreign-related vehicles and Hong Kong/Macau cross-border vehicles (粤Z)
- Points to: province / prefecture-level city
- Strength: strong when several vehicles on the street agree; a single vehicle, or vehicles in parking lots, scenic areas, at hotel entrances, or in expressway service areas, count only as weak
- Counterexamples: out-of-town vehicles are common in big cities and tourist areas; freight corridors carry plates from everywhere; illegible out-of-town plates in hotel or scenic-area parking lots can't be used to place the location
- Sources: case001 v011

## Vehicles and traffic

### Taxi colors
- Look for: main body color (green, yellow, blue-and-white, red, etc.) and color scheme
- Points to: a city-level candidate list (e.g., green-family taxis are common in several Sichuan cities; look up the exact list live, it changes over the years)
- Strength: weak (single source); medium when combined with bus livery and terrain
- Counterexamples: one city often runs several colors at once, and they change generations often; Chongqing, Xi'an, Changzhi, and other places also have green-family taxis; ride-hailing cars don't count
- Sources: v006

### Bus roof and body livery (clear in top-down shots)
- Look for: bus roof color, main body color, waistline stripe, rear-end pattern (zoomed top-down shots often leave only color blocks, which is still enough)
- Points to: a fingerprint to compare city by city (first narrow down to a few cities with taxis etc., then separate them by bus livery); **inside a municipality or a large prefecture-level city it can separate districts (counties)**: the urban core and outlying districts/counties have different bus companies, with very different liveries
- How to check: first confirm the common livery in the urban core; if it doesn't match, search images for "<城市> <颜色描述> 公交" (query in Chinese: <city> <color description> bus), and take the district/county name from route signs and company names in the result images (pin it to a district/county before using it); finally compare bus photos from the candidate districts/counties one by one on rear end and waistline
- Strength: medium (two sources, v006 and v014; can narrow a whole city down to one or two districts/counties); strong when route signs or company names are visible
- Counterexamples: several liveries coexist in one city and change generations often; ad wraps cover the base colors; buses on cross-district routes run into other districts; not appearing in the first few pages of image results doesn't mean it doesn't exist
- Sources: v006 v014

## Infrastructure

### Electrified railway catenary masts: one side or both
- Look for: a row of poles beside the railway with triangular cantilever arms at the top, holding two or three non-parallel wires (messenger wire, contact wire). Only on one side of the track → usually single-track; on both sides, or with portal frames spanning the tracks → double-track
- Points to: an electrified railway; single-track electrified lines are a small share, so this can narrow down a lot (combine with regional clues, then list candidate lines with `osm.py` or a railway map)
- Strength: medium
- Counterexamples: seen from far away or from low down, masts on the other side may be hidden by trees or embankments; stations, bridges, and tunnels have different structures; "single-track = old line" does not hold
- Sources: v011

### Number of bundled conductors on transmission lines
- Look for: how many conductors form one bundle per phase under the tower crossarm (with spacers between them)
- Points to: voltage level. Common: single conductor ≈ below 220 kV, 2 → 220–330 kV, 4 → 500 kV, 6 → 750 kV or ±800 kV DC, 8 → 1000 kV
- Strength: weak (alone it only tells the grid level); medium after intersecting with railways, rivers, expressways
- Counterexamples: special designs; the count is easy to get wrong at a distance; several circuits in one corridor overlap
- Sources: v011 v010-3

### Combinations of special urban transport facilities
- Look for: cross-river passenger cableways (two or three closely parallel track ropes + a haul rope, slanting from a riverside station to the opposite bank), road/rail-transit bridges (double-deck truss, rail transit on the lower deck), light rail running through a building, long urban escalators, high-speed rail viaducts
- Points to: each facility maps to a set of cities; when two or three appear together, take the intersection (with a cross-river passenger cableway, a road/rail-transit bridge, and steep riverside mountains in one frame, usually only one or two mountain river cities nationwide remain); verify each item of the intersection with web search, not from memory
- Strength: medium (combined, it can reach the city)
- Counterexamples: high-voltage lines crossing a river (tall towers, insulators, nearly horizontal), cable-stayed bridge stays (fanning from the tower top), and dock crane cables get mistaken for cableways; road/railway bridges in Wuhan, Nanjing, and elsewhere are structurally similar but differ in color and terrain
- Sources: v005 v010-3

### Hu Hu Tong (户户通) small satellite dishes
- Look for: small dishes 35–60 cm in diameter on rooftops in rural areas and urban villages
- Points to: the heading corresponds to longitude: in eastern cities they face southwest (about 215°–227°), in the west they face south or southeast (table in `sky.md` section 5)
- Strength: medium (when the azimuth is read accurately it can bound the longitude range)
- Counterexamples: large dishes at institutions and cable TV stations point at other satellites; on offset-feed dishes the dish-face tilt is not the elevation angle
- Sources: derived in sky.md; v001 (using dishes as a compass)

## Climate and phenology (must be paired with the month)

### Extensive evergreen broadleaf trees in winter photos
- Look for: in photos from December–February, whether street trees, green belts, and hillsides at the city edge are broadly green (camphor, glossy privet, osmanthus, banyan and the like)
- Points to: the subtropical evergreen broadleaf forest zone, roughly south of the Qinling–Huaihe line
- Strength: medium with a reliable month (excludes half of China); weak without a month
- Counterexamples: northern cities also have evergreen plantings such as pines, cypresses, and Japanese spindle (mostly conifers or shrubs); **the parts of northern provinces south of the Qinling are also evergreen in winter: Longnan in Gansu, Hanzhong and Ankang in Shaanxi**; high-altitude mountains in the south lose their leaves and hold snow in winter
- Sources: v006

### Color of mountains in winter (distant views, aerial)
- Look for: in winter distant views or high-altitude photos, whether the mountains are uniformly gray-brown and bare or broadly green
- Points to: gray-brown → temperate mountains north of the Qinling–Huaihe line; evergreen → southern subtropical mountains
- Strength: medium (separates north from south; can't reach the province)
- Counterexamples: conifer forest areas such as the northern Greater Khingan and the Changbai Mountains stay dark green in winter; the arid northwest is brown in every season; high altitudes in the south also turn withered yellow in winter; doesn't apply to summer photos
- Sources: v012 v006

### White water bodies seen from altitude
- Look for: in aerial or airplane-window photos, water surfaces that are uniformly white with no reflection
- Points to: ice or snow on ice → regions where the daily mean temperature stays below 0 ℃ for long stretches in winter, roughly north of the Qinling–Huaihe line
- Strength: weak (pair with season and mountain color)
- Counterexamples: salt lakes, salt pans, dry lakebeds, turbid sediment-laden water, sun glint, thin cloud; during cold waves in the south, small water bodies also freeze briefly
- Sources: v012

### Palms, coconut trees → "tropical China"
- Look for: rows of coconut palms, palm-family plants, tropical landscaping
- Points to: you must list every candidate: Hainan, southern Guangdong (Leizhou Peninsula), southern Guangxi, **southern Yunnan (river valleys in Xishuangbanna, Dehong, Honghe, etc.)**, southern Taiwan; beyond that, Southeast Asia
- Strength: weak (only draws the candidate set)
- Counterexamples: parks in Fujian, Sichuan, Shanghai, and elsewhere also plant palms; in v010-6 the AI searched only Hainan and Guangdong, missed Yunnan, and ended up jumping to Vietnam
- Sources: v010-6 v002

### Weeping willows + calm artificial water, no other features
- Look for: weeping willows, mixed trees, water that looks like an irrigation canal or fish pond; no mountains, towers, road signs, or buildings
- Points to: mainly provinces of the Huang-Huai-Hai Plain (Henan, Hebei, Shandong, Anhui, Jiangsu)
- Strength: weak (only reaches a few provinces; photos like this can usually only give a range)
- Counterexamples: the Yangtze basin and irrigated oases in the northwest also commonly have weeping willows and canals
- Sources: v010-8

### Fog, low cloud
- Look for: low visibility, a gray-white sky, distant mountains reduced to outlines
- Points to: common in Sichuan Basin cities (Chongqing etc.) in the winter half of the year
- Strength: weak (only boosts; doesn't fix the city, let alone the solar term)
- Counterexamples: smoggy winter days in North China and the Yangtze River Delta look the same; phone filters and backlighting also make things gray
- Sources: v005

## Terrain and water

### Mountains rising straight from the far bank of a big river, buildings stacked up the slopes
- Look for: a very wide river with mountains several hundred meters high within one or two km of the far bank; houses climb the slope tier by tier
- Points to: mountain river cities (central Chongqing, Yibin, Luzhou, and other Sichuan–Chongqing and upper-Yangtze cities); excludes plains cities on the middle and lower Yangtze (Wuhan, Jiujiang, Nanjing, Wuhu)
- Strength: weak (excludes a large area; doesn't fix the city)
- Counterexamples: Yichang and other cities also have nearby mountains across the river; fog "pulls" distant mountains closer, so check whether the mountain foot meets the built-up area directly
- Sources: v005

### Mountain city at the confluence of two rivers
- Look for: the urban area straddles the confluence of two rivers, surrounded by mountains
- Points to: a common layout in Sichuan–Chongqing and the southwest (Chongqing, Yibin, Luzhou, etc.); separate specific cities by confluence angle, river islands, bridge positions, and river width (template comparison in `corridors.md` section 6)
- Strength: weak (common layout)
- Counterexamples: river islands and shorelines change with water level and construction; mind the date of the satellite imagery
- Sources: v006

### Wide, muddy yellow river + low, dense, fragmented gullies
- Look for: a river several hundred meters wide, earthy yellow; the hills on both banks are low but cut by gullies into branching patterns, sparse vegetation, terraces on the slopes
- Points to: the Loess Plateau reach of the middle Yellow River (around the Shanxi–Shaanxi Gorge) and its tributaries in northern Shaanxi, western Shanxi, and eastern Gansu
- Strength: medium (reaches Loess Plateau + Yellow River; pair with the river's direction and the terrain on both banks to get the reach)
- Counterexamples: in flood season the Yangtze and the Jinsha are also yellow, but their banks are plains and high mountain gorges respectively; tributaries such as the Wuding and Yan rivers are just as muddy but much narrower
- Sources: v008

### Blue-green Yellow River surface in a canyon
- Look for: a wide river surface, clear blue-green with no visible sediment, in a loess or red sandstone canyon
- Points to: reservoir areas of the cascade dams on the upper Yellow River (Liujiaxia, Yanguoxia, Bapanxia in Gansu; Lijiaxia in Qinghai; Qingtongxia in Ningxia; etc.)
- Strength: weak (only reaches the "upper-river reservoir" class of reach)
- Counterexamples: season, light, and drone filters all change the water color; in v010-2 the AI used this clue to pick the most famous reservoir and was off by 7 km
- Sources: v010-2

## To be filled: street-level fingerprints between similar cities

For several cities with similar layouts in the same basin or the same province, street-level distinguishing clues haven't been collected yet (guardrail color and style, bus shelters, curbs, traffic sign poles, streetlight design, residential facade colors). Until the library has them, when "several cities all look alike", sample and compare on the spot:

```bash
uv run scripts/baidu_pano.py sample --bbox <city A urban area s,w,n,e> --n 24 --out cityA.jpg
uv run scripts/baidu_pano.py sample --bbox <city B urban area s,w,n,e> --n 24 --out cityB.jpg
```

- Compare only things the city procures uniformly and that are consistent citywide (guardrails, shelters, sign poles); don't compare shop signs, trees, or cars.
- Baidu street view was mostly captured several years ago, and fixtures like guardrails get replaced; when the sample year and the photo year are far apart, drop one tier.
- A difference found by sampling must hold across three or more cities and two or more independent samples before it can be written into this section.

## Urban form

### No office clusters or supertall towers in the skyline
- Look for: the frame is all residential high-rises, with no glass-curtain-wall office clusters or supertall landmarks
- Points to: the old town of a prefecture-level city, or a county seat; not the core of a provincial capital
- Strength: weak
- Counterexamples: old districts of provincial capitals and suburban counties look like this too; the photo covers only one direction; the photographer may be standing on the tallest building in town
- Sources: v006

### Tile-clad factory buildings + rows of AC units, right next to new supertall towers (Pearl River Delta)
- Look for: six- to eight-story factory buildings clad in small square beige or yellow-green tiles, windows lined with AC outdoor units; new glass-curtain-wall towers beside or behind them
- Points to: "industrial-zone redevelopment" areas in Shenzhen, Dongguan, and similar places, where the old factories aren't demolished yet but new towers have gone up around them
- Strength: weak (suggests the Pearl River Delta; can't fix the city on its own)
- Counterexamples: old industrial areas in the Yangtze River Delta such as Suzhou and Ningbo also have similar factory buildings; tile color and AC unit density usually differ
- Sources: case001
