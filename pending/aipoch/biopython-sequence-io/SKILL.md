---
name: biopython-sequence-io
description: Use Biopython to read/write/convert biological sequence files (FASTA/GenBank/FASTQ, etc.) and perform basic sequence operations; use when you need reliable sequence I/O, lightweight sequence manipulation, or scalable processing of large sequence datasets.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# biopython-sequence-io

## When to Use

- Converting between common sequence formats (e.g., FASTA ↔ GenBank, FASTQ → FASTA) while preserving identifiers and annotations.
- Reading and writing sequence datasets for downstream pipelines (alignment, assembly, annotation) with consistent parsing and output.
- Performing basic sequence operations (reverse complement, translation, slicing) without implementing custom parsers.
- Processing large sequence files efficiently via streaming iteration or indexed access instead of loading everything into memory.
- Computing simple sequence statistics and filtering records (length, GC content, ambiguous bases) during ingestion.

## Key Features

- **Sequence objects and basic operations** using `Bio.Seq.Seq` (slicing, reverse complement, transcription/translation).
- **Robust sequence I/O** via `Bio.SeqIO` for parsing and writing FASTA/GenBank/FASTQ and other supported formats.
- **Format conversion** by reading records in one format and writing them in another.
- **Scalable processing** with iterator-based parsing and optional indexed access (`SeqIO.index`) for large files.
- **Common filtering/statistics** patterns (length thresholds, GC%, quality-aware handling for FASTQ).

## Dependencies

- `biopython>=1.80`
- `numpy>=1.21`

## Example Usage

Create `config/task_config.json`:

```json
{
  "input_path": "data/input.fasta",
  "input_format": "fasta",
  "output_path": "data/output.gb",
  "output_format": "genbank",
  "min_length": 200,
  "max_ambiguous": 0,
  "index_db_path": "data/index.sqlite"
}
```

Run:

```bash
python scripts/sequence_io.py
```

`scripts/sequence_io.py` (runnable end-to-end):

```python
import json
from pathlib import Path

import numpy as np
from Bio import SeqIO

def gc_fraction(seq: str) -> float:
    s = seq.upper()
    if not s:
        return 0.0
    return float((s.count("G") + s.count("C")) / len(s))

def ambiguous_count(seq: str) -> int:
    # Treat anything outside A/C/G/T/U as ambiguous for simple filtering.
    allowed = set("ACGTU")
    return sum(1 for ch in seq.upper() if ch not in allowed)

def main() -> None:
    config_path = Path("config/task_config.json")
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    input_path = Path(cfg["input_path"])
    input_format = cfg["input_format"]
    output_path = Path(cfg["output_path"])
    output_format = cfg["output_format"]

    min_length = int(cfg.get("min_length", 0))
    max_ambiguous = int(cfg.get("max_ambiguous", 10**9))

    output_path.parent.mkdir(parents=True, exist_ok=True)

    kept = 0
    lengths = []

    # Stream records to avoid loading the entire file into memory.
    with output_path.open("w", encoding="utf-8") as out_handle:
        for record in SeqIO.parse(str(input_path), input_format):
            seq_str = str(record.seq)

            if len(seq_str) < min_length:
                continue
            if ambiguous_count(seq_str) > max_ambiguous:
                continue

            # Example: attach simple stats as annotations (useful for GenBank output).
            record.annotations["gc_fraction"] = gc_fraction(seq_str)

            SeqIO.write(record, out_handle, output_format)
            kept += 1
            lengths.append(len(seq_str))

    summary = {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "kept_records": kept,
        "length_min": int(np.min(lengths)) if lengths else 0,
        "length_max": int(np.max(lengths)) if lengths else 0,
        "length_mean": float(np.mean(lengths)) if lengths else 0.0,
    }

    Path("config").mkdir(parents=True, exist_ok=True)
    with Path("config/summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
```

## Implementation Details

- **Configuration convention**
  - Store runtime configuration in `config/task_config.json` as an intermediate artifact.
  - Invoke scripts uniformly with `python scripts/<task_name>.py`.
  - Avoid stacking many CLI `--` parameters; prefer config files for reproducibility.
  - All file I/O must specify `encoding="utf-8"`. JSON output must use `ensure_ascii=False`.

- **Parsing and writing**
  - Use `SeqIO.parse(path, format)` for streaming iteration over records.
  - Use `SeqIO.write(records_or_record, handle, format)` to serialize records.
  - For format conversion, parse in the source format and write in the target format; ensure the target format supports the fields you expect (e.g., GenBank requires richer metadata than FASTA).

- **Large-file strategies**
  - Prefer iterator-based parsing for one-pass processing.
  - For random access by record ID, use `SeqIO.index(input_path, format)` (creates an on-disk index depending on backend); this avoids loading all sequences into memory.

- **Filtering/statistics**
  - Typical filters include `min_length`, maximum ambiguous characters, and quality-based criteria for FASTQ.
  - GC fraction is computed as `(count(G)+count(C))/length` on an uppercased sequence string; handle empty sequences safely.

- **Reference**
  - See `references/sequence_io.md` for additional notes and format-specific behaviors.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `biopython_sequence_io_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: biopython_sequence_io_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
