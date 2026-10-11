# Lookup data

Global lookup tables. `clues.py lookup` reads the JSON in this directory; country tables (plates, area codes, admin divisions) live in region packs (`regions/<cc>/data/`, format in `regions/README.md`). Each file's `_meta` records the source URL, fetch date, and entry count; maintainers refetch with `refresh.py` (global tables and the China pack).

| File | Content | Source | Fetched | Entries | License |
|---|---|---|---|---|---|
| `calling_codes.json` | Country calling codes for countries and regions | [en.wikipedia.org/wiki/List_of_telephone_country_codes](https://en.wikipedia.org/wiki/List_of_telephone_country_codes) | 2026-09-14 | 281 | Derived from Wikipedia, CC BY-SA 4.0 |
| `driving_side.json` | Driving side by country | [en.wikipedia.org/wiki/Left-_and_right-hand_traffic](https://en.wikipedia.org/wiki/Left-_and_right-hand_traffic) | 2026-10-08 | 241 | Derived from Wikipedia, CC BY-SA 4.0 |
| `territories.json` | Overseas territories and dependencies | [en.wikipedia.org/wiki/List_of_dependent_territories](https://en.wikipedia.org/wiki/List_of_dependent_territories) | 2026-09-14 | 60 | Derived from Wikipedia, CC BY-SA 4.0 |
| `country_names.json` | Chinese–English country and region name mapping, with aliases | Hand-compiled | 2026-09-14 | 300 | MIT (with this repository) |

Notes:

- The Wikipedia-sourced tables are factual data scraped and compiled from the tables in the corresponding articles. Wikipedia text is licensed under CC BY-SA 4.0; these tables are released under the same license, with attribution to Wikipedia and its editors.
- `country_names.json` is a hand-compiled mapping table; the keys of `en2zh` match the English spellings used in the other tables, and `aliases` maps short names, traditional-character names, former names, and English abbreviations to `en2zh` keys.
- This directory contains no OpenStreetMap data; `gazetteer.py` and `osm.py` query Overpass live.

Source names and quoted source notes stay in their original language. Maintained annotations (including curated driving-side notes and unverified municipality hints) are in English; the agent explains source evidence in the user's language.
