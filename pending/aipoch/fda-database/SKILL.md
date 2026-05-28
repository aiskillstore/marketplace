---
name: fda-database
description: Query the openFDA API to retrieve FDA regulatory datasets (drugs, devices, adverse events, recalls, submissions, UNII) when you need programmatic safety/regulatory evidence for analysis or research.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

1. **Pharmacovigilance / safety signal screening** when you need adverse event counts, common reactions, or serious-event rates for a drug.
2. **Medical device regulatory research** when you need 510(k)/PMA context, device classification, UDI lookups, or device adverse events/recalls.
3. **Recall and enforcement monitoring** when you need to track Class I/II/III recalls across drugs, devices, or foods.
4. **Substance identity resolution** when you need UNII/CAS/name-based lookups and basic substance relationship/structure retrieval.
5. **Veterinary safety analysis** when you need animal adverse events filtered by species/breed and product.

## Key Features

- Unified Python interface (`FDAQuery`) for multiple openFDA domains (drug, device, food, animalandveterinary, other).
- Convenience helpers for common tasks:
  - Drug events, labels, recalls, shortages
  - Device events, classification, 510(k), PMA, UDI
  - Food events and recalls
  - Animal/veterinary adverse events
  - Substance (UNII/name) lookups
- Supports openFDA query patterns:
  - Fielded search strings, date ranges, wildcards
  - Aggregations via `count_by_field(...)` (with `.exact` support)
  - Pagination via `skip/limit` and bulk retrieval via `query_all(...)`
- Operational safeguards:
  - Optional API key support for higher daily limits
  - Built-in caching (TTL) and rate limiting (as implemented in `scripts/fda_query.py`)
  - Basic error handling patterns

> Additional endpoint notes and query syntax are typically documented in:
> `references/api_basics.md`, `references/drugs.md`, `references/devices.md`, `references/foods.md`, `references/animal_veterinary.md`, `references/other.md`.

## Dependencies

- Python **3.9+**
- openFDA API access (public)
- Optional: openFDA API key (recommended for higher daily quota)

> Package-level dependencies (e.g., `requests`) are defined by the repository implementation in `scripts/fda_query.py`. If you maintain this skill, pin them in `requirements.txt` (for example, `requests==2.31.0`) to ensure reproducibility.

## Example Usage

The following example is designed to be runnable in a repository that contains `scripts/fda_query.py` and the `FDAQuery` class.

### 1) Set an API key (optional, recommended)

```bash
export FDA_API_KEY="your_key_here"
```

### 2) Run a complete script

```python
import os
from datetime import datetime, timedelta

from scripts.fda_query import FDAQuery


def drug_safety_profile(fda: FDAQuery, drug_name: str):
    # Total adverse events (meta.total)
    events = fda.query_drug_events(drug_name, limit=1)
    total = events.get("meta", {}).get("results", {}).get("total", 0)

    # Top reactions (aggregation)
    reactions = fda.count_by_field(
        "drug",
        "event",
        search=f"patient.drug.medicinalproduct:*{drug_name}*",
        field="patient.reaction.reactionmeddrapt",
        exact=True,
    )
    top_reactions = reactions.get("results", [])[:10]

    # Serious events
    serious = fda.query(
        "drug",
        "event",
        search=f"patient.drug.medicinalproduct:*{drug_name}*+AND+serious:1",
        limit=1,
    )
    serious_total = serious.get("meta", {}).get("results", {}).get("total", 0)

    # Recent recalls
    recalls = fda.query_drug_recalls(drug_name=drug_name)
    recall_results = recalls.get("results", [])

    return {
        "drug": drug_name,
        "total_events": total,
        "serious_events": serious_total,
        "serious_rate_pct": (serious_total / total * 100.0) if total else 0.0,
        "top_reactions": top_reactions,
        "recalls_sample": recall_results[:5],
    }


def monthly_event_trend(fda: FDAQuery, drug_name: str, months: int = 6):
    trends = []
    for i in range(months):
        end = datetime.now() - timedelta(days=30 * i)
        start = end - timedelta(days=30)
        date_range = f"[{start.strftime('%Y%m%d')}+TO+{end.strftime('%Y%m%d')}]"

        search = (
            f"patient.drug.medicinalproduct:*{drug_name}*"
            f"+AND+receivedate:{date_range}"
        )
        result = fda.query("drug", "event", search=search, limit=1)
        count = result.get("meta", {}).get("results", {}).get("total", 0)

        trends.append({"month": start.strftime("%Y-%m"), "events": count})

    return list(reversed(trends))


def main():
    fda = FDAQuery(api_key=os.getenv("FDA_API_KEY"))

    # Drug: safety profile + trend
    profile = drug_safety_profile(fda, "aspirin")
    trend = monthly_event_trend(fda, "aspirin", months=6)

    # Device: quick cross-database lookup
    device_lookup = {
        "adverse_events": fda.query_device_events("pacemaker", limit=10),
        "classification": fda.query_device_classification("DQY"),
        "510k": fda.query_device_510k(applicant="Medtronic"),
        "udi": fda.query("device", "udi", search="brand_name:*pacemaker*", limit=5),
    }

    # Food: recall monitoring
    food_recalls = fda.query_food_recalls(reason="undeclared peanut", limit=10)

    # Substance: UNII lookup
    substance = fda.query_substance_by_unii("R16CO5Y76E")

    print({"drug_profile": profile, "drug_trend": trend})
    print({"device_lookup_keys": list(device_lookup.keys())})
    print({"food_recalls_count": len(food_recalls.get("results", []))})
    print({"substance_keys": list(substance.keys())})


if __name__ == "__main__":
    main()
```

### 3) Run the repository examples (if provided)

```bash
python scripts/fda_examples.py
```

## Implementation Details

### API domains and endpoints

This skill is a thin client over openFDA endpoints, typically accessed as:

- **Drugs**: `drug/event`, `drug/label`, `drug/ndc`, `drug/enforcement`, `drug/drugsfda`, `drug/drugshortages`
- **Devices**: `device/event`, `device/510k`, `device/classification`, `device/enforcement`, `device/recall`, `device/pma`, `device/registrationlisting`, `device/udi`, `device/covid19serology`
- **Foods**: `food/event`, `food/enforcement`
- **Animal/Veterinary**: `animalandveterinary/event`
- **Other/Substances**: `other/substance`, `other/nsde`

Exact helper method names (e.g., `query_drug_events`, `query_device_510k`) are implemented in `scripts/fda_query.py`.

### Query construction

- Searches are passed as openFDA query strings (Lucene-like), e.g.:
  - Field match: `patient.drug.medicinalproduct:aspirin`
  - Wildcards: `*aspirin*` (use sparingly)
  - Boolean: `A+AND+B`
  - Date range: `receivedate:[20240101+TO+20241231]`
- Pagination uses:
  - `limit` (page size)
  - `skip` (offset)
- Aggregations use `count_by_field(domain, endpoint, search, field, exact=True)`:
  - When `exact=True`, the implementation typically appends `.exact` to the aggregation field to avoid tokenization issues.

### Rate limits and authentication

- openFDA supports unauthenticated access with lower daily quotas; an API key increases the daily request limit.
- The client is expected to:
  - Attach the API key when provided
  - Apply rate limiting and retries (per `FDAQuery` implementation)

### Result handling and robustness

- Responses generally follow:

```json
{
  "meta": { "results": { "skip": 0, "limit": 100, "total": 12345 } },
  "results": []
}
```

- Always guard for:
  - Missing `results`
  - Empty result sets
  - `error` objects returned by the API

### Caching

- If enabled in `FDAQuery`, caching reduces repeated calls for identical queries.
- Typical parameters (implementation-dependent):
  - `use_cache=True`
  - `cache_ttl=<seconds>`