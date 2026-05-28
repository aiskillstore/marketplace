# Overlap Detection and IGD

The `overlaprs` module utilizes the Integrated Genome Database (IGD) data structure to provide efficient genomic interval overlap detection.

## IGD Index

IGD (Integrated Genome Database) is a data structure specifically designed for fast genomic interval queries and overlap detection.

### Building an IGD Index

Create an index from genomic region files:

```python
import gtars

# Build IGD index from a BED file
igd = gtars.igd.build_index("regions.bed")

# Save index for reuse
igd.save("regions.igd")

# Load an existing index
igd = gtars.igd.load_index("regions.igd")
```

### Querying Overlaps

Efficiently find overlapping regions:

```python
# Query a single region
overlaps = igd.query("chr1", 1000, 2000)

# Query multiple regions
results = []
for chrom, start, end in query_regions:
    overlaps = igd.query(chrom, start, end)
    results.append(overlaps)

# Get overlap count only
count = igd.count_overlaps("chr1", 1000, 2000)
```

## CLI Usage

The `overlaprs` command-line tool provides overlap detection functionality:

```bash
# Find overlaps between two BED files
gtars overlaprs query --index regions.bed --query query_regions.bed

# Count the number of overlaps
gtars overlaprs count --index regions.bed --query query_regions.bed

# Output overlapping regions
gtars overlaprs overlap --index regions.bed --query query_regions.bed --output overlaps.bed
```

### IGD CLI Commands

Build and query IGD indices:

```bash
# Build an IGD index
gtars igd build --input regions.bed --output regions.igd

# Query an IGD index
gtars igd query --index regions.igd --region "chr1:1000-2000"

# Batch query from a file
gtars igd query --index regions.igd --query-file queries.bed --output results.bed
```

## Python API

### Overlap Detection

Calculate overlaps between sets of regions:

```python
import gtars

# Load two region sets
set_a = gtars.RegionSet.from_bed("regions_a.bed")
set_b = gtars.RegionSet.from_bed("regions_b.bed")

# Find overlaps
overlaps = set_a.overlap(set_b)

# Get regions in A that overlap with B
overlapping_a = set_a.filter_overlapping(set_b)

# Get regions in A that do not overlap with B
non_overlapping_a = set_a.filter_non_overlapping(set_b)
```

### Overlap Statistics

Calculate overlap metrics:

```python
# Count the number of overlaps
overlap_count = set_a.count_overlaps(set_b)

# Calculate overlap fraction
overlap_fraction = set_a.overlap_fraction(set_b)

# Get overlap coverage
coverage = set_a.overlap_coverage(set_b)
```

## Performance Characteristics

IGD provides efficient querying capabilities:
- **Index Building**: O(n log n), where n is the number of regions
- **Query Time**: O(k + log n), where k is the number of overlaps
- **Memory Efficient**: Uses a compact representation of genomic intervals

## Use Cases

### Regulatory Element Analysis

Identify overlaps between genomic features:

```python
# Find Transcription Factor Binding Sites (TFBS) overlapping with promoters
tfbs = gtars.RegionSet.from_bed("chip_seq_peaks.bed")
promoters = gtars.RegionSet.from_bed("promoters.bed")

overlapping_tfbs = tfbs.filter_overlapping(promoters)
print(f"Found {len(overlapping_tfbs)} TFBS in promoters")
```

### Variant Annotation

Annotate variants using overlapping features:

```python
# Check which variants overlap with coding sequences
variants = gtars.RegionSet.from_bed("variants.bed")
cds = gtars.RegionSet.from_bed("coding_sequences.bed")

coding_variants = variants.filter_overlapping(cds)
```

### Chromatin State Analysis

Compare chromatin states between different samples:

```python
# Find regions with consistent chromatin states
sample1 = gtars.RegionSet.from_bed("sample1_peaks.bed")
sample2 = gtars.RegionSet.from_bed("sample2_peaks.bed")

consistent_regions = sample1.overlap(sample2)
```