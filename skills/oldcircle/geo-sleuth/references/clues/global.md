# Cross-country clues

Clues that tell countries and continents apart, or that work the same way in many countries. Clues that only narrow things down inside one country live in that country's region pack (`regions/<cc>/clues.md`; `regions.py list` shows which exist).

General order when the country is still open: driving side and plate shape to exclude continents → script and language of the text, phone calling codes → plate style to the state/province → infrastructure and municipal fixtures → architecture and vegetation.

## General

### Driving side, driver's seat
- Look for: whether the driver's seat is on the left or the right; which side of the road traffic keeps to; which way cars parked at the roadside face
- Points to: right-hand traffic excludes the UK, Ireland, Japan, Australia, New Zealand, South Africa, India, some Southeast Asian countries, and Hong Kong/Macau; and vice versa
- Strength: strong (exclusion type; one clue excludes a batch of countries)
- Counterexamples: left-hand-traffic countries have a few imported left-hand-drive cars; **the photo or video may be mirrored**, first check for reversed text
- Sources: v009 v010-4

### Plate aspect ratio
- Look for: the plate's shape; no need to read the characters
- Points to: long narrow strip → Europe; rectangle close to 2:1 → North America; refine further by background color and graphics
- Strength: medium
- Counterexamples: Japanese plates are also close to 2:1 (exclude them with the driver's seat side); some European vehicles carry square plates; motorcycle plates are generally squarish
- Sources: v009

### Plate background and graphics in countries that issue plates by state/province
- Look for: when the characters can't be read: the plate's overall background color, color bands, central graphic (state or provincial flag), border color
- Points to: state/province level (US, Mexico, Canada, Brazil's old format, Australia, etc.)
- Strength: medium (filter to a few states against a chart of state plate designs; narrows by an order of magnitude in one step)
- Counterexamples: out-of-state vehicles crossing state lines (especially common on freight corridors and in border cities); old and new formats coexist, and reference charts go out of date; overexposure in strong light renders light-colored graphics as white
- Sources: v002 v009

### Official bilingual or multilingual signs
- Look for: two languages with the same content on one official traffic sign or street-name sign
- Points to: an officially multilingual admin area, not "near a country that speaks that language" (e.g., German-Italian bilingual signs in Italy → Province of Bolzano/South Tyrol)
- Strength: strong
- Counterexamples: bilingual private shop signs don't count; foreign-language signs added for tourists in tourist areas don't count
- Sources: v001

### Sub-brands and business lines of chain brands
- Look for: small marks on the sign besides the parent brand (truck tire retreading, commercial vehicle service, etc.)
- Points to: sub-brands have far fewer stores, so listing all their stores nationwide gives a candidate point list; also suggests a freight corridor or the outskirts of an industrial zone
- Strength: weak (alone); medium together with a store search
- Counterexamples: store data on maps is incomplete
- Sources: v002

### Ads for regional consumer goods
- Look for: drink and snack brand ads on vehicles and along the street
- Points to: the country or region where the brand mainly sells
- Strength: weak
- Counterexamples: multinational brands, imported brands
- Sources: v007

### Bus operator abbreviation + route number
- Look for: the operator abbreviation and route number at the top of the bus front and rear
- Points to: city; route number → look up the route corridor with `osm.py route` and search along it
- Strength: strong (to the city); with a route map, to one line
- Counterexamples: second-hand imported buses keep text from the country of origin on the body, so it can't be used to judge the country; route numbers get changed
- Sources: v007

## Europe

### Roof color: red terracotta tile vs gray pitched roofs (northern Italy, etc.)
- Look for: the color of roofs across an area in distant views of the photo or in satellite imagery
- Points to: Italian-speaking areas are mostly red terracotta; many gray or dark pitched roofs → towns in the German-speaking cultural area (Austria, Germany, South Tyrol)
- Strength: weak (meaningful only as a statistic over a whole area)
- Counterexamples: new apartment buildings often use flat roofs or gray metal roofs
- Sources: v001

### Arch form: round or pointed
- Look for: whether door and window arches are round or pointed; biforate windows (two small arches inside one large arch)
- Points to: round arch → Romanesque or Renaissance; pointed arch → Gothic. If sources say a city has few medieval remains but the photo shows an intact "medieval courtyard" → prefer 19th-century-or-later replicas (exposition pavilions, mock-historic streets, film studio sets)
- Strength: weak (narrows the building type, helps choose search terms)
- Counterexamples: there are many replicas; reverse image search in a Chinese-language interface mixes in large numbers of modern-era Chinese red-brick buildings
- Sources: v004

### Uniform streetlight design within an area
- Look for: streetlight pole color, lamp head shape
- Points to: procured uniformly by one city or area; use it for spot-check confirmation between candidate towns
- Strength: weak (for verifying, not for finding)
- Counterexamples: one manufacturer's lights are sold to many cities
- Sources: v001 v009

## Inherited standards (overseas territories, former colonies)

When you recognize infrastructure built to "country X's standard", the candidates are the home country + overseas territories that keep the home country's standards + some former colonies. Intersect that with the IP location and the continent the puzzle setter named, and often only one place remains.

### Arched crossarms on the French distribution grid
- Look for: a crossarm arching upward on top of a concrete or metal pole, three conductors hanging from suspension insulators (the "arched" layout of medium-voltage lines); identical poles lined up into the distance
- Points to: the French grid system: metropolitan France and the overseas departments that keep its standards; some former North African colonies have similar pole types
- Strength: medium (narrows the whole world to a few regions in the French system; then use IP, continent, and climate to fix one)
- Counterexamples: border areas of neighboring countries have similar styles; former colonies later changed pole types; in small distant images an ordinary straight crossarm is easily seen as arched, so zoom in to verify
- Sources: v013

## South Asia

### Sinhala script on official signs (Sri Lanka)
- Look for: Sinhala script (rounded, looping letters with no line along the top, unlike Hindi script) on road signs, street-name boards and government signs; official signs often repeat the same text in Sinhala, Tamil and English, but many carry only one or two of the three
- Points to: Sri Lanka; Sinhala is an official language there and is written almost nowhere else
- Strength: medium
- Counterexamples: Sinhala on temples, shops or embassies outside Sri Lanka; Malayalam (Kerala, India) is also rounded and can pass for Sinhala at low resolution; when only Tamil and English are visible (Sinhala cropped, blurred or absent from that sign), the sign can be mistaken for Tamil Nadu, India, so Tamil alone does not exclude Sri Lanka; private shop signs follow no official layout
- Sources: Constitution of Sri Lanka, Articles 18–19 (https://www.constituteproject.org/constitution/Sri_Lanka_2015.pdf?lang=en); Wikipedia "Sinhala script" (https://en.wikipedia.org/wiki/Sinhala_script)