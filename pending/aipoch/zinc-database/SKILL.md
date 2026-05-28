---
name: zinc-database
description: Access the ZINC (230M+ purchasable compounds) database when you need to look up compounds by ZINC ID/SMILES, run similarity/analog searches, or download 3D ready-to-dock structures for virtual screening and drug discovery.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. **Build a virtual screening library** by sampling purchasable compounds (e.g., fragment/lead-like/drug-like subsets).
2. **Retrieve compounds by identifier** (ZINC ID) for follow-up analysis, procurement, or reporting.
3. **Search by structure (SMILES)** to find exact matches or **analogs** via similarity thresholds.
4. **Validate supplier availability** by querying supplier/catalog identifiers and mapping them to ZINC entries.
5. **Download docking-ready 3D structures** (e.g., MOL2/SDF/DB2) organized by ZINC tranches for docking pipelines.

## Key Features

- **ZINC22 access** (CartBlanche22 web + API) for large-scale purchasable chemical space.
- **Lookup by ZINC ID** (single or batch).
- **SMILES search** with optional similarity/analog expansion via distance parameters.
- **Supplier/catalog queries** to cross-reference vendor codes and catalogs.
- **Random sampling** for benchmarking, diversity sampling, and screening set generation.
- **Property-aware filtering** using **tranche codes** (H-bond donors, LogP, MW, reactivity phase).
- **3D structure downloads** from the ZINC22 files library (tranche-organized).

## Dependencies

- `curl` (tested with 7.70+)
- Python `>=3.9`
- `pandas>=2.0.0` (parsing tabular API output)
- (optional) `requests>=2.31.0` (if replacing `curl` with native HTTP)
- (optional) `rdkit>=2023.09.1` (structure validation, fingerprints, downstream cheminformatics)

## Example Usage

The following example is a complete runnable script that:
1) queries by ZINC ID, 2) runs a SMILES similarity search, 3) samples random compounds, and 4) parses tranche properties.

```python
#!/usr/bin/env python3
import subprocess
from io import StringIO
import re
import pandas as pd

BASE = "https://cartblanche22.docking.org"

def curl_get(url: str) -> str:
    r = subprocess.run(["curl", "-sS", url], capture_output=True, text=True)
    r.check_returncode()
    return r.stdout

def query_by_zinc_id(zinc_id: str, output_fields="zinc_id,smiles,catalogs,tranche") -> pd.DataFrame:
    # Common pattern used by CartBlanche22: <endpoint>.txt:<field>=<value>&output_fields=...
    url = f"{BASE}/substances.txt:zinc_id={zinc_id}&output_fields={output_fields}"
    txt = curl_get(url)
    return pd.read_csv(StringIO(txt), sep="\t")

def search_by_smiles(smiles: str, dist: int = 0, adist: int = 0,
                     output_fields="zinc_id,smiles,tranche") -> pd.DataFrame:
    url = (
        f"{BASE}/smiles.txt:smiles={smiles}"
        f"&dist={dist}&adist={adist}&output_fields={output_fields}"
    )
    txt = curl_get(url)
    return pd.read_csv(StringIO(txt), sep="\t")

def random_compounds(count: int = 100, subset: str | None = None,
                     output_fields="zinc_id,smiles,tranche") -> pd.DataFrame:
    url = f"{BASE}/substance/random.txt:count={count}&output_fields={output_fields}"
    if subset:
        url += f"&subset={subset}"
    txt = curl_get(url)
    return pd.read_csv(StringIO(txt), sep="\t")

def parse_tranche(tranche: str):
    """
    Tranche format: H##P###M###-phase
      H##   = H-bond donors
      P###  = LogP * 10
      M###  = molecular weight (Da)
      phase = reactivity classification
    Example: H05P035M400-0
    """
    m = re.match(r"H(\d+)P(\d+)M(\d+)-(\d+)", str(tranche))
    if not m:
        return None
    return {
        "h_donors": int(m.group(1)),
        "logP": int(m.group(2)) / 10.0,
        "mw": int(m.group(3)),
        "phase": int(m.group(4)),
    }

def main():
    # 1) Lookup by ZINC ID
    df_id = query_by_zinc_id("ZINC000000000001")
    print("By ZINC ID:")
    print(df_id.head(), "\n")

    # 2) SMILES exact / similarity search (example: benzene)
    df_smiles = search_by_smiles("c1ccccc1", dist=3, output_fields="zinc_id,smiles,tranche")
    print("SMILES similarity search (dist=3):")
    print(df_smiles.head(), "\n")

    # 3) Random sampling (lead-like)
    df_rand = random_compounds(count=50, subset="lead-like", output_fields="zinc_id,smiles,tranche")
    df_rand["tranche_props"] = df_rand["tranche"].apply(parse_tranche)
    print("Random lead-like sample with parsed tranche:")
    print(df_rand.head(), "\n")

    # 4) Simple tranche-based filtering example
    # Keep compounds with MW <= 350 and logP <= 3.5 when tranche parsing is available
    props = df_rand["tranche_props"].dropna().apply(pd.Series)
    filtered = df_rand.loc[props.index].copy()
    filtered = filtered.join(props)
    filtered = filtered[(filtered["mw"] <= 350) & (filtered["logP"] <= 3.5)]
    print(f"Filtered (mw<=350, logP<=3.5): {len(filtered)} rows")
    print(filtered[["zinc_id", "smiles", "tranche", "mw", "logP"]].head())

if __name__ == "__main__":
    main()
```

## Implementation Details

### Data Sources and Access Points

- **ZINC main site**: https://zinc.docking.org/
- **CartBlanche22 interactive search**: https://cartblanche22.docking.org/
- **CartBlanche22 API base**: `https://cartblanche22.docking.org/`
- **ZINC22 files library (3D structures)**: https://files.docking.org/zinc22/
- **Documentation/wiki**: https://wiki.docking.org/

### Core Query Patterns

CartBlanche22 commonly exposes endpoints in the form:

- `.../substances.txt:zinc_id=<ID1,ID2,...>&output_fields=...`
- `.../smiles.txt:smiles=<SMILES>&dist=<n>&adist=<n>&output_fields=...`
- `.../catitems.txt:catitem_id=<SUPPLIER_CODE>`
- `.../substance/random.txt:count=<N>&subset=<subset>&output_fields=...`

Returned data is typically **tab-separated** text; request only needed columns via `output_fields` to reduce payload.

### Similarity Parameters (`dist`, `adist`)

- `dist`: similarity/analog expansion control (often used as a threshold-like knob; smaller values yield closer analogs).
- `adist`: alternative distance parameter for broader expansion.
- Practical guidance:
  - Start with **exact match** (`dist=0`, `adist=0`).
  - Expand gradually (e.g., `dist=1..3` for close analogs; higher values for broader exploration).

### Output Fields

Commonly useful fields (availability depends on endpoint/data):

- `zinc_id`: ZINC identifier
- `smiles`: SMILES representation
- `sub_id`: internal substance identifier
- `supplier_code`: vendor catalog number
- `catalogs`: supplier/catalog list
- `tranche`: encoded property bin (H donors, LogP, MW, phase)

Example:

```bash
curl "https://cartblanche22.docking.org/substances.txt:zinc_id=ZINC000000000001&output_fields=zinc_id,smiles,catalogs,tranche"
```

### Tranche Encoding (Property Binning)

ZINC tranches encode coarse physicochemical properties:

- Format: `H##P###M###-phase`
  - `H##`: H-bond donors
  - `P###`: LogP × 10
  - `M###`: molecular weight (Da)
  - `phase`: reactivity classification

Use tranche parsing to implement fast, server-side-friendly filtering workflows (e.g., lead-like/drug-like constraints) before downloading 3D structures.

### 3D Structure Downloads (Docking-Ready)

For docking workflows, use the ZINC22 files library:

- https://files.docking.org/zinc22/

Files are organized by tranche and provided in formats such as **MOL2**, **SDF**, and **DB2.GZ** (for DOCK). For large batch downloads, prefer tranche-based retrieval and parallel download tools (e.g., `wget`, `aria2c`) while respecting server load.