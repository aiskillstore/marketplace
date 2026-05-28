---
name: gtars
description: A high-performance Rust toolkit (with Python bindings and a CLI) for genomic interval analysis; use it when you need fast overlap queries, coverage track generation, genomic tokenization for ML, reference sequence verification, or fragment processing.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- **Overlap and set operations on genomic intervals** (e.g., peak/promoter overlap, variant annotation, shared-feature detection).
- **Coverage track generation** from interval-like inputs (e.g., ATAC-seq/ChIP-seq/RNA-seq coverage for visualization in genome browsers).
- **Machine-learning preprocessing** where genomic regions must be converted into discrete **tokens** (e.g., Transformer-style models, geniml-style pipelines).
- **Reference sequence management and verification** (e.g., subsequence retrieval, digest calculation aligned with GA4GH refget concepts).
- **Single-cell fragment workflows** (e.g., splitting fragments by barcode/cluster, scoring fragments against reference region sets).

## Key Features

- **Rust performance** with low overhead; designed for large genomic datasets.
- **Python bindings** for integration into analysis notebooks/pipelines.
- **CLI tooling** for batch processing and shell workflows.
- **Fast overlap detection** via IGD-style indexing and interval operations.
- **Coverage track generation** (WIG/BigWig workflows via the `uniwig` functionality).
- **Genomic tokenizers** for ML-ready representations of genomic regions.
- **Reference sequence utilities** (FASTA-backed stores, subsequence retrieval, digesting).
- **Fragment processing and scoring** for common single-cell genomics tasks.

> Additional module-specific guidance may be available in: `references/overlap.md`, `references/coverage.md`, `references/tokenizers.md`, `references/refget.md`, `references/python-api.md`, and `references/cli.md`.

## Dependencies

- **Python package**: `gtars` (version not specified in the source document)
- **Rust toolchain** (for CLI install): `cargo` (version not specified)
- **Rust crate**: `gtars = "0.1"` (as shown in the example)

## Example Usage

### Python: overlap analysis workflow (runnable)

```python
import gtars

# Load two region sets
peaks = gtars.RegionSet.from_bed("chip_peaks.bed")
promoters = gtars.RegionSet.from_bed("promoters.bed")

# Find overlaps (peaks that overlap promoters)
overlapping_peaks = peaks.filter_overlapping(promoters)

# Export results
overlapping_peaks.to_bed("peaks_in_promoters.bed")
```

### CLI: generate coverage tracks (runnable)

```bash
# Generate WIG coverage at a given resolution
gtars uniwig generate --input atac_fragments.bed --output coverage.wig --resolution 10

# Generate BigWig coverage for genome browser visualization
gtars uniwig generate --input atac_fragments.bed --output coverage.bw --format bigwig
```

### Python: ML tokenization (runnable)

```python
import gtars
from gtars.tokenizers import TreeTokenizer

# Load regions and build a tokenizer from BED
regions = gtars.RegionSet.from_bed("training_peaks.bed")
tokenizer = TreeTokenizer.from_bed_file("training_peaks.bed")

# Tokenize each region into a discrete representation
tokens = [tokenizer.tokenize(r.chromosome, r.start, r.end) for r in regions]

print(tokens[:5])
```

## Implementation Details

- **Interval overlap & indexing**: Overlap queries are designed around an IGD-like index to accelerate repeated interval queries (build once, query many). Typical parameters are chromosome, start, end; results are overlapping intervals or derived set operations.
- **Coverage generation (`uniwig`)**: Produces coverage tracks from interval/fragments input. Common knobs include output format (e.g., WIG vs BigWig) and resolution/binning for track granularity.
- **Tokenization**: Tokenizers (e.g., `TreeTokenizer`) map genomic coordinates to discrete tokens suitable for ML pipelines. Token vocabularies are commonly derived from a BED-defined training region universe.
- **Reference sequence store**: FASTA-backed reference access supports subsequence retrieval and digesting/verification workflows aligned with refget-style usage.
- **Fragment workflows**: Fragment splitting and scoring operate on fragment-like inputs (often TSV/BED-style) and can be used for barcode/cluster partitioning and enrichment-style scoring against reference region sets.