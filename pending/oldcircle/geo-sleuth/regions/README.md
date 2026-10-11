# Region packs

Everything that only works inside one country lives here, one folder per country: `regions/<cc>/`, where `cc` is the ISO 3166-1 alpha-2 code in lower case (`cn`, `jp`, `in`). The core (SKILL.md, `references/`, `scripts/`) holds the methods and the cross-country clues, and reads packs through their manifest. Adding or removing a pack never changes the core.

## How the agent uses a pack

1. Country still open: cross-country clues (`references/clues/global.md`), calling codes, driving side. Lookups without `--country` search every pack and return matches from all countries that fit.
2. A country is a candidate: `regions.py show <cc>` prints the pack's card (lookups, preferred services, tips) and a one-line index of its clue entries with line numbers. Read only the entries you need.
3. Country settled: `board.py country <cc>`; from then on `board.py apply` uses only that pack, and `board.py next` uses its tips.
4. No pack for the country: global tools and references only. Lookups for it answer `unsupported`; they never fall back to another country's table.

## What a pack contains

```
regions/<cc>/
  region.json    manifest (required)
  clues.md       clue entries (required; more docs can be listed in region.json "docs")
  data/*.json    lookup tables and an admin table (optional)
  tests.json     lookup cases (required when the pack has lookups)
```

**Packs hold data and documents only: `.json` and `.md`.** The skill runs on users' machines, and a pack is reviewed as data. If a table needs logic the formats below can't express, propose a change to the core format in a separate PR.

### region.json

```json
{
 "code": "JP",
 "name": "Japan",
 "names": ["Japan", "日本", "Nippon"],
 "status": "community",
 "maintainers": ["@your-github-handle"],
 "docs": ["clues.md"],
 "admin_levels": {"4": "admin1", "7": "admin2"},
 "level_names": {"admin1": "prefecture", "admin2": "municipality"},
 "name_suffixes": [],
 "admin_table": "data/admin.json",
 "lookups": {"area-code": {"file": "data/area_codes.json"}},
 "services": {"poi": {"sources": "osm", "country": "jp"}, "street_view": "gsv.py"},
 "tips": {"livery": "…", "municipal": "…"}
}
```

| Field | Meaning |
|---|---|
| `code`, `name`, `names` | ISO code, display name, every name or alias a user or table might use (`--country` matches any of them) |
| `status` | `maintained` (core maintainers keep it current), `community` (a named maintainer does), `stub` (a few clues, no maintainer) |
| `docs` | Markdown files the card indexes |
| `admin_levels` | admin table `level` → board level: `admin1`, `admin2`, `city`, `district` |
| `level_names` | what the levels are called locally, for the card |
| `name_suffixes` | generic suffixes ignored when matching names across sources (CN: 市, 省, 区, 县) |
| `admin_table` | optional; lets `board.py children` check OSM's list and gives candidates stable ids |
| `lookups` | lookup kind → prefix table. Use an existing kind name when it means the same thing: `plate`, `area-code`, `postal-code` |
| `services` | `poi` (sources and Nominatim country for `poi.py --region`), `street_view` (a core script), `datum` (local map datum, if any) |
| `tips` | replaces the matching line of `board.py next`'s cheap tests (`livery`, `municipal`, …) |

### Prefix tables (`data/*.json` named in `lookups`)

```json
{
 "_meta": {
  "kind": "area-code",
  "source": ["https://…"],
  "fetched": "2026-10-08",
  "license": "CC BY-SA 4.0 (derived from Wikipedia)",
  "count": 2,
  "normalize": {"digits_only": true, "ensure_prefix": "0"},
  "key_pattern": null,
  "usage": "one line shown on the card: what to type",
  "miss_note": "what a miss usually means"
 },
 "entries": {
  "020": [{"admin1": "Maharashtra", "admin2": "Pune"}],
  "0120": [{"admin1": "Uttar Pradesh", "admin2": "Ghaziabad"}, {"admin1": "Uttar Pradesh", "admin2": "Gautam Buddh Nagar", "note": "Noida"}]
 }
}
```

- Lookup = normalize the value (`normalize`: `strip` characters, `digits_only`, `upper`, `ensure_prefix`), cut it with `key_pattern` if given (a value that doesn't fit is "not this country's format"), then take the **longest key that is a prefix** of it.
- Each key maps to a **list**. A key that covers several places lists every one of them; never merge two places into one name, and never pick one. The board keeps them all as hypotheses.
- A match names admin levels explicitly (`admin1` … `district`) with the names as the admin table or OSM spells them, plus optional `note` and `unverified: true` for rows not backed by the source.
- A key that covers only part of an area (part of a state, part of a district) names the larger area and says what part in `note`.
- `_meta.source`, `fetched` and `license` are required. Hand-compiled data says so in `source` and gives the references it was compiled from.

### Admin table (`admin_table`)

`{"_meta": {source, fetched, license, count}, "items": [{"name", "code", "level", "parent"}]}` — `parent` is the parent's `name`; top-level items have `"parent": ""`. Every `level` needs an entry in `admin_levels`.

### clues.md

Entries in the shared format (`references/clues/README.md`): Look for / Points to / Strength / Counterexamples / Sources, grouped under `##` topics. An entry belongs here when its "Points to" stays inside this country; clues that separate countries go into `references/clues/global.md`.

### tests.json

```json
[{"kind": "area-code", "value": "0120-4567890", "expect": [{"admin1": "Uttar Pradesh", "admin2": "Ghaziabad"}, {"admin1": "Uttar Pradesh", "admin2": "Gautam Buddh Nagar"}]}]
```

At least one case per lookup kind; include a key that covers several places and a value that should miss (`"expect": []`). Only the level fields are compared.

## Contributing a pack

| Tier | What | Review |
|---|---|---|
| 1 | Clue entries only (`region.json` + `clues.md`) | Entry format, sources, counterexamples |
| 2 | Lookup tables (+ `tests.json`, optionally an admin table) | Tier 1 + data sources, licenses, multi-place keys, tests |
| 3 | Anything that needs code: a new service adapter, OCR language support, a new table format | Open an issue first; core change in its own PR |

A pack PR touches only `regions/<cc>/`. Start from `regions/_template/`, then run:

```bash
uv run scripts/regions.py lint <cc>     # manifest, sources, entry fields, no code files, tests
uv run scripts/regions.py show <cc>     # what the agent will see
uv run scripts/clues.py lookup <kind> <value> --country <cc>
```

`lint` must print `ok`. It rejects code files, tables without source/date/license, keys that map to a merged name like "A / B" instead of a list, entries missing a field, and failing tests.
