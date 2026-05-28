# Coverage Analysis with Uniwig

The `uniwig` module is used to generate coverage tracks from sequencing data, providing the functionality to efficiently convert genomic intervals into coverage profiles.

## Coverage Track Generation

Create coverage tracks from BED files:

```python
import gtars

# Generate coverage from BED file
coverage = gtars.uniwig.coverage_from_bed("fragments.bed")

# Generate coverage with specified resolution
coverage = gtars.uniwig.coverage_from_bed("fragments.bed", resolution=10)

# Generate strand-specific coverage
fwd_coverage = gtars.uniwig.coverage_from_bed("fragments.bed", strand="+")
rev_coverage = gtars.uniwig.coverage_from_bed("fragments.bed", strand="-")
```

## CLI Usage

Generate coverage tracks via the command line:

```bash
# Generate coverage track
gtars uniwig generate --input fragments.bed --output coverage.wig

# Specify resolution
gtars uniwig generate --input fragments.bed --output coverage.wig --resolution 10

# Generate BigWig format
gtars uniwig generate --input fragments.bed --output coverage.bw --format bigwig

# Strand-specific coverage
gtars uniwig generate --input fragments.bed --output forward.wig --strand +
gtars uniwig generate --input fragments.bed --output reverse.wig --strand -
```

## Processing Coverage Data

### Accessing Coverage Values

Query coverage at specific locations:

```python
# Get coverage at a specific position
cov = coverage.get_coverage("chr1", 1000)

# Get coverage for a specific range
cov_array = coverage.get_coverage_range("chr1", 1000, 2000)

# Get coverage statistics
mean_cov = coverage.mean_coverage("chr1", 1000, 2000)
max_cov = coverage.max_coverage("chr1", 1000, 2000)
```

### Coverage Operations

Perform operations on coverage tracks:

```python
# Normalize coverage
normalized = coverage.normalize()

# Smooth coverage
smoothed = coverage.smooth(window_size=10)

# Merge coverage tracks
combined = coverage1.add(coverage2)

# Calculate coverage difference
diff = coverage1.subtract(coverage2)
```

## Output Formats

Uniwig supports multiple output formats:

### WIG Format

Standard Wiggle format:
```
fixedStep chrom=chr1 start=1000 step=1
12
15
18
22
...
```

### BigWig Format

Binary format for efficient storage and access:
```bash
# Generate BigWig
gtars uniwig generate --input fragments.bed --output coverage.bw --format bigwig
```

### BedGraph Format

Flexible format suitable for variable coverage:
```
chr1    1000    1001    12
chr1    1001    1002    15
chr1    1002    1003    18
```

## Application Cases

### ATAC-seq Analysis

Generate chromatin accessibility profiles:

```python
# Generate ATAC-seq coverage
atac_fragments = gtars.RegionSet.from_bed("atac_fragments.bed")
coverage = gtars.uniwig.coverage_from_bed("atac_fragments.bed", resolution=1)

# Identify open regions (peaks)
peaks = coverage.call_peaks(threshold=10)
```

### ChIP-seq Peak Visualization

Create coverage tracks for ChIP-seq data:

```bash
# Generate coverage file for visualization
gtars uniwig generate --input chip_seq_fragments.bed \
                      --output chip_coverage.bw \
                      --format bigwig
```

### RNA-seq Coverage

Calculate read coverage for RNA-seq:

```python
# Generate strand-specific RNA-seq coverage
fwd = gtars.uniwig.coverage_from_bed("rnaseq.bed", strand="+")
rev = gtars.uniwig.coverage_from_bed("rnaseq.bed", strand="-")

# Export files for IGV viewing
fwd.to_bigwig("rnaseq_fwd.bw")
rev.to_bigwig("rnaseq_rev.bw")
```

### Differential Coverage Analysis

Compare coverage between samples:

```python
# Generate coverage for two samples
control = gtars.uniwig.coverage_from_bed("control.bed")
treatment = gtars.uniwig.coverage_from_bed("treatment.bed")

# Calculate fold change
fold_change = treatment.divide(control)

# Find differential regions
diff_regions = fold_change.find_regions(threshold=2.0)
```

## Performance Optimization

- Choose appropriate resolution based on data scale
- BigWig format is recommended for large datasets
- Supports parallel processing across multiple chromosomes
- Memory-efficient streaming for large files