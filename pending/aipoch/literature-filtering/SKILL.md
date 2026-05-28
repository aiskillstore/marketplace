---
name: literature-filtering
description: Filter literature by publication year, journal, and predefined screening rules to produce inclusion/exclusion lists; use when conducting preliminary screening or systematic review screening to narrow the literature scope.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to quickly narrow a large bibliography by **publication year range** (e.g., 2015–2024).
- You must restrict results to a **target journal set** (e.g., a whitelist/blacklist of journals).
- You are running **preliminary screening** before full-text review and need traceable inclusion/exclusion decisions.
- You are conducting **systematic review screening** and must record consistent reasons for exclusion.
- You need standardized outputs (lists + logs) for collaboration, auditing, or downstream analysis.

## Key Features

- Rule-based filtering by **year**, **journal**, and **literature type/criteria**.
- **Journal name normalization** to match abbreviations and full names consistently.
- Structured recording of **exclusion reasons** for transparency and reproducibility.
- Support for **borderline/controversial item review** to improve consistency.
- Standardized outputs: **inclusion list**, **exclusion list**, and **screening statistics/summary**.

## Dependencies

- None (documentation-driven workflow).
- Optional template file:
  - `assets/screening_log_template.csv`

## Example Usage

The following example is a complete, runnable Python script that:
1) normalizes journal names, 2) filters by year and journal whitelist, 3) applies simple inclusion/exclusion rules, and 4) outputs inclusion/exclusion CSV files plus a screening log.

```python
#!/usr/bin/env python3
import csv
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

# ----------------------------
# Configuration (edit as needed)
# ----------------------------
YEAR_MIN = 2018
YEAR_MAX = 2024

# Journal whitelist after normalization
JOURNAL_WHITELIST = {
    "journal of finance",
    "journal of financial economics",
    "review of financial studies",
}

# Abbreviation/full-name mapping (extend as needed)
JOURNAL_ALIASES = {
    "j. finan.": "journal of finance",
    "j finan": "journal of finance",
    "jfe": "journal of financial economics",
    "rev. financ. stud.": "review of financial studies",
    "rfs": "review of financial studies",
}

# Simple keyword-based screening rules (example)
INCLUDE_KEYWORDS = {"asset pricing", "corporate finance", "risk premium"}
EXCLUDE_KEYWORDS = {"editorial", "book review", "erratum"}

# ----------------------------
# Data model
# ----------------------------
@dataclass
class Record:
    id: str
    title: str
    year: int
    journal: str
    abstract: str

# ----------------------------
# Helpers
# ----------------------------
def normalize_journal(name: str, aliases: Dict[str, str]) -> str:
    """
    Normalize journal names:
    - lowercase
    - strip punctuation
    - collapse whitespace
    - map abbreviations to canonical full names
    """
    if not name:
        return ""
    raw = name.strip().lower()
    raw = re.sub(r"[^\w\s\.]", " ", raw)  # keep dots for alias keys like "j. finan."
    raw = re.sub(r"\s+", " ", raw).strip()

    # Try alias mapping on the dot-preserved version
    if raw in aliases:
        return aliases[raw]

    # Also try a dot-stripped variant
    nodot = raw.replace(".", "")
    if nodot in aliases:
        return aliases[nodot]

    # Canonicalize by removing dots and extra spaces
    canonical = re.sub(r"[\.]", "", raw)
    canonical = re.sub(r"\s+", " ", canonical).strip()
    return canonical

def contains_any(text: str, keywords: set) -> bool:
    t = (text or "").lower()
    return any(k in t for k in keywords)

def screen_record(r: Record) -> Tuple[bool, str]:
    """
    Returns (included, reason).
    Reasons are designed to be human-auditable.
    """
    if r.year < YEAR_MIN or r.year > YEAR_MAX:
        return False, f"Excluded: year out of range ({r.year})"

    norm_journal = normalize_journal(r.journal, JOURNAL_ALIASES)
    if norm_journal not in JOURNAL_WHITELIST:
        return False, f"Excluded: journal not in whitelist ({norm_journal})"

    text = f"{r.title}\n{r.abstract}"
    if contains_any(text, EXCLUDE_KEYWORDS):
        return False, "Excluded: matches exclusion keywords"

    if not contains_any(text, INCLUDE_KEYWORDS):
        return False, "Excluded: does not match inclusion keywords"

    return True, "Included: meets all criteria"

# ----------------------------
# I/O
# ----------------------------
def read_input_csv(path: str) -> List[Record]:
    """
    Expected columns: id,title,year,journal,abstract
    """
    out = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.append(
                Record(
                    id=row.get("id", "").strip(),
                    title=row.get("title", "").strip(),
                    year=int(row.get("year", "0")),
                    journal=row.get("journal", "").strip(),
                    abstract=row.get("abstract", "").strip(),
                )
            )
    return out

def write_csv(path: str, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    input_path = "input_literature.csv"
    records = read_input_csv(input_path)

    included, excluded, log = [], [], []
    for r in records:
        norm_journal = normalize_journal(r.journal, JOURNAL_ALIASES)
        ok, reason = screen_record(r)

        log.append({
            "id": r.id,
            "title": r.title,
            "year": str(r.year),
            "journal_raw": r.journal,
            "journal_normalized": norm_journal,
            "decision": "include" if ok else "exclude",
            "reason": reason,
        })

        base = {
            "id": r.id,
            "title": r.title,
            "year": str(r.year),
            "journal": norm_journal,
        }
        (included if ok else excluded).append(base)

    write_csv("included.csv", included, ["id", "title", "year", "journal"])
    write_csv("excluded.csv", excluded, ["id", "title", "year", "journal"])
    write_csv(
        "screening_log.csv",
        log,
        ["id", "title", "year", "journal_raw", "journal_normalized", "decision", "reason"],
    )

    # Simple screening statistics
    stats = {
        "total": len(records),
        "included": len(included),
        "excluded": len(excluded),
    }
    print("Screening complete:", stats)
    print("Outputs: included.csv, excluded.csv, screening_log.csv")

if __name__ == "__main__":
    main()
```

Minimal input file example (`input_literature.csv`):

```csv
id,title,year,journal,abstract
1,Asset Pricing with Risk Premiums,2020,J. Finan.,We study asset pricing and the risk premium...
2,An Editorial Note,2021,Journal of Finance,This editorial summarizes...
3,Corporate Finance Evidence,2017,JFE,Empirical corporate finance results...
```

## Implementation Details

### 1. Rule Setting

- **Year rules**: define an inclusive range `[YEAR_MIN, YEAR_MAX]`.
- **Journal rules**:
  - Use a **whitelist** (or blacklist) of canonical journal names.
  - Apply **normalization** before matching to avoid false mismatches.
- **Screening criteria**:
  - Define explicit inclusion/exclusion criteria (e.g., topic, study type, population, method).
  - Ensure each exclusion has a **single primary reason** (or a controlled multi-reason scheme).

### 2. Journal Name Normalization

Recommended normalization steps (in order):

1. Convert to lowercase.
2. Remove/standardize punctuation and collapse whitespace.
3. Apply **abbreviation/full-name mapping** (e.g., `J. Finan.` → `Journal of Finance`).
4. Output a canonical form used for matching and reporting.

Key parameters:
- `JOURNAL_ALIASES`: dictionary for abbreviation/full-name mapping.
- Normalization policy choices:
  - Case sensitivity (typically disabled by lowercasing).
  - Punctuation handling (strip most punctuation; optionally preserve dots for alias keys).
  - Whitespace collapsing.

### 3. Execution of Screening

- Apply filters in a stable order to keep decisions consistent and auditable:
  1. Year range
  2. Journal match (after normalization)
  3. Inclusion/exclusion criteria
- Record a **decision** and **reason** for every record in a screening log.

### 4. Review and Consistency

- Flag borderline items (e.g., unclear abstracts, ambiguous journal names) for manual review.
- Keep a shared, versioned rule set (year range, journal list, alias map, criteria) to ensure consistent application across reviewers.

### 5. Output Organization

Produce at minimum:
- `included.csv`: records that pass all rules.
- `excluded.csv`: records that fail at least one rule.
- `screening_log.csv`: full trace with normalized journal and exclusion reason.
- Optional: screening statistics and a reason summary (counts by reason).

Reference formats and checkpoints can be aligned with `references/guide.md` if available.