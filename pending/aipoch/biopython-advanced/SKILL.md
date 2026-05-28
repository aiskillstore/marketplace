---
name: biopython-advanced
description: Advanced Biopython modules for motifs, population genetics, sequence utilities, restriction analysis, clustering, and GenomeDiagram visualization; use when you need extended bioinformatics analysis beyond basic sequence I/O and alignment.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# biopython-advanced

## When to Use

- You need **motif discovery/statistics** (e.g., PWM/consensus, motif counts across multiple sequences).
- You want **restriction enzyme site analysis** (e.g., find cut sites for specific enzymes in a DNA sequence).
- You need **codon usage / sequence utility calculations** (e.g., codon frequency from CDS, GC content, basic sequence stats).
- You are working with **population genetics (PopGen)** utilities for advanced analyses.
- You need **advanced visualization** such as **GenomeDiagram**-style plots for genomic features.

## Key Features

- **Motif analysis** using Biopython’s `Bio.motifs` (counts, consensus, simple statistics).
- **Restriction analysis** using `Bio.Restriction` (enzyme lookup, cut site detection).
- **Sequence utilities** via `Bio.SeqUtils` (codon usage and related helpers).
- Access to additional advanced tools such as **CodonTable**, **SeqFeature**, and **IUPACData** when needed.
- Standardized workflow conventions:
  - Write configuration to `config/task_config.json` as an intermediate artifact.
  - Run tasks uniformly via `python scripts/<task_name>.py`.
  - Avoid stacking many CLI flags; keep parameters in config files.
  - Always use `encoding="utf-8"` for file I/O; JSON output uses `ensure_ascii=False`.

## Dependencies

Required:

- biopython (>=1.80)
- numpy (>=1.21)

Optional (for reporting/plotting):

- reportlab (>=3.6)
- matplotlib (>=3.5)

## Example Usage

The following examples are complete runnable scripts that follow the conventions:
- configuration stored in `config/task_config.json`
- invoked as `python scripts/<task_name>.py`
- explicit UTF-8 encoding and `ensure_ascii=False` for JSON output

### 1) Motif Statistics

**config/task_config.json**
```json
{
  "task": "motif_stats",
  "sequences": ["ATGCATGCATGC", "ATGCGTGCATGC", "ATGCATGTATGC"]
}
```

**scripts/motif_stats.py**
```python
import json
from Bio import motifs
from Bio.Seq import Seq

def main():
    with open("config/task_config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    seqs = [Seq(s) for s in cfg["sequences"]]
    m = motifs.create(seqs)

    result = {
        "alphabet": str(m.alphabet),
        "length": m.length,
        "counts": {k: dict(v) for k, v in m.counts.items()},
        "consensus": str(m.consensus),
        "degenerate_consensus": str(m.degenerate_consensus),
    }

    with open("outputs/motif_stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
```

Run:
```bash
python scripts/motif_stats.py
```

### 2) Restriction Enzyme Cleavage Sites

**config/task_config.json**
```json
{
  "task": "restriction_sites",
  "sequence": "GAATTCGCGGAATTC",
  "enzymes": ["EcoRI", "BamHI"]
}
```

**scripts/restriction_sites.py**
```python
import json
from Bio.Seq import Seq
from Bio.Restriction import RestrictionBatch

def main():
    with open("config/task_config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    seq = Seq(cfg["sequence"])
    batch = RestrictionBatch(cfg["enzymes"])
    analysis = batch.search(seq)

    # Convert enzyme keys to strings for JSON serialization
    result = {str(enzyme): positions for enzyme, positions in analysis.items()}

    with open("outputs/restriction_sites.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
```

Run:
```bash
python scripts/restriction_sites.py
```

### 3) Codon Usage Frequency (CDS)

**config/task_config.json**
```json
{
  "task": "codon_usage",
  "cds": "ATGGCTGCTGCTGCTTAA"
}
```

**scripts/codon_usage.py**
```python
import json
from collections import Counter

def main():
    with open("config/task_config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    cds = cfg["cds"].upper().replace(" ", "").replace("\n", "")
    codons = [cds[i:i+3] for i in range(0, len(cds) - (len(cds) % 3), 3)]
    counts = Counter(codons)
    total = sum(counts.values()) or 1

    result = {
        "total_codons": total,
        "codon_counts": dict(sorted(counts.items())),
        "codon_frequencies": {k: v / total for k, v in sorted(counts.items())},
        "note": "This example computes raw codon frequencies from the provided CDS. Validate CDS frame and stop codons for your use case."
    }

    with open("outputs/codon_usage.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
```

Run:
```bash
python scripts/codon_usage.py
```

## Implementation Details

- **Configuration-first execution**
  - All task parameters are stored in `config/task_config.json` to keep CLI invocation stable and reproducible.
  - Scripts read the config as the single source of truth and write results to `outputs/*.json`.

- **Motif statistics (`Bio.motifs`)**
  - A motif is created from aligned sequences of equal length.
  - Outputs typically include:
    - `counts`: per-position nucleotide counts
    - `consensus` and `degenerate_consensus`: derived consensus sequences
  - If sequences differ in length, you must align/trim/pad them before motif creation.

- **Restriction analysis (`Bio.Restriction`)**
  - `RestrictionBatch(enzymes).search(seq)` returns cut positions per enzyme.
  - Enzyme objects are converted to strings for JSON serialization.

- **Codon usage**
  - The example computes codon frequencies by splitting the CDS into triplets in-frame.
  - Practical considerations:
    - Ensure the CDS length is a multiple of 3 (or decide how to handle remainder bases).
    - Confirm the correct reading frame and whether to include terminal stop codons.
    - For organism-specific codon usage tables, integrate `Bio.Data.CodonTable` as needed.

- **I/O requirements**
  - Always open files with `encoding="utf-8"`.
  - Use `json.dump(..., ensure_ascii=False)` to preserve non-ASCII characters in outputs.

- **Further reference**
  - See `references/advanced.md` for additional notes and module coverage (motifs/PopGen/SeqUtils/Restriction/Cluster, GenomeDiagram, CodonTable/SeqFeature/IUPACData).