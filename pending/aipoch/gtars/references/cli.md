# Command Line Interface (CLI)

Gtars provides a comprehensive set of command-line tools for genomic interval analysis directly in the terminal.

## Installation

```bash
# Install all features
cargo install gtars-cli --features "uniwig overlaprs igd bbcache scoring fragsplit"

# Install only specific features
cargo install gtars-cli --features "uniwig overlaprs"
```

## Global Options

```bash
# Display help information
gtars --help

# Display version number
gtars --version

# Verbose output mode
gtars --verbose <command>

# Quiet mode
gtars --quiet <command>
```

## IGD Commands

Build and query IGD indices for overlap detection:

```bash
# Build IGD index
gtars igd build --input regions.bed --output regions.igd

# Query a single region
gtars igd query --index regions.igd --region "chr1:1000-2000"

# Query from a file
gtars igd query --index regions.igd --query-file queries.bed --output results.bed

# Count overlap numbers
gtars igd count --index regions.igd --query-file queries.bed
```

## Overlap Commands

Calculate overlaps between sets of genomic regions:

```bash
# Find overlapping regions
gtars overlaprs overlap --set-a regions_a.bed --set-b regions_b.bed --output overlaps.bed

# Count overlap numbers
gtars overlaprs count --set-a regions_a.bed --set-b regions_b.bed

# Filter regions by overlap
gtars overlaprs filter --input regions.bed --filter overlapping.bed --output filtered.bed

# Region subtraction (difference set)
gtars overlaprs subtract --set-a regions_a.bed --set-b regions_b.bed --output difference.bed
```

## Uniwig Commands

Generate coverage tracks from genomic intervals:

```bash
# Generate coverage tracks
gtars uniwig generate --input fragments.bed --output coverage.wig

# Specify resolution
gtars uniwig generate --input fragments.bed --output coverage.wig --resolution 10

# Generate BigWig
gtars uniwig generate --input fragments.bed --output coverage.bw --format bigwig

# Strand-specific coverage
gtars uniwig generate --input fragments.bed --output forward.wig --strand +
```

## BBCache Commands

Cache and manage BED files from BEDbase.org:

```bash
# Fetch and cache BED file from bedbase
gtars bbcache fetch --id <bedbase_id> --output cached.bed

# List cached files
gtars bbcache list

# Clear cache
gtars bbcache clear

# Update cache
gtars bbcache update
```

## Scoring Commands

Score fragment overlaps based on reference datasets:

```bash
# Score fragments
gtars scoring score --fragments fragments.bed --reference reference.bed --output scores.txt

# Batch scoring
gtars scoring batch --fragments-dir ./fragments/ --reference reference.bed --output-dir ./scores/

# Scoring with weights
gtars scoring score --fragments fragments.bed --reference reference.bed --weights weights.txt --output scores.txt
```

## FragSplit Commands

Split fragment files by cell barcodes or clusters:

```bash
# Split by barcodes
gtars fragsplit split --input fragments.tsv --barcodes barcodes.txt --output-dir ./split/

# Split by clusters
gtars fragsplit cluster-split --input fragments.tsv --clusters clusters.txt --output-dir ./clustered/

# Filter fragments
gtars fragsplit filter --input fragments.tsv --min-fragments 100 --output filtered.tsv
```

## Common Workflows

### Workflow 1: Overlap Analysis Pipeline

```bash
# Step 1: Build IGD index for reference dataset
gtars igd build --input reference_regions.bed --output reference.igd

# Step 2: Query using experimental data
gtars igd query --index reference.igd --query-file experimental.bed --output overlaps.bed

# Step 3: Generate statistics
gtars overlaprs count --set-a experimental.bed --set-b reference_regions.bed
```

### Workflow 2: Coverage Track Generation

```bash
# Step 1: Generate coverage data
gtars uniwig generate --input fragments.bed --output coverage.wig --resolution 10

# Step 2: Convert to BigWig
gtars uniwig generate --input fragments.bed --output coverage.bw --format bigwig
```

### Workflow 3: Fragment Processing

```bash
# Step 1: Filter fragments
gtars fragsplit filter --input raw_fragments.tsv --min-fragments 100 --output filtered.tsv

# Step 2: Split by clusters
gtars fragsplit cluster-split --input filtered.tsv --clusters clusters.txt --output-dir ./by_cluster/

# Step 3: Score against reference dataset
gtars scoring batch --fragments-dir ./by_cluster/ --reference reference.bed --output-dir ./scores/
```

## Input/Output Formats

### BED Format
Standard 3-column or extended BED format:
```
chr1    1000    2000
chr1    3000    4000
chr2    5000    6000
```

### Fragment Format (TSV)
Tab-separated format for single-cell fragments:
```
chr1    1000    2000    BARCODE1
chr1    3000    4000    BARCODE2
chr2    5000    6000    BARCODE1
```

### WIG Format
Wiggle format for coverage tracks:
```
fixedStep chrom=chr1 start=1000 step=10
12
15
18
```

## Performance Options

```bash
# Set number of threads
gtars --threads 8 <command>

# Memory limit
gtars --memory-limit 4G <command>

# Buffer size
gtars --buffer-size 10000 <command>
```

## Error Handling

```bash
# Continue execution on error
gtars --continue-on-error <command>

# Strict mode (warnings as errors)
gtars --strict <command>

# Log output to file
gtars --log-file output.log <command>
```