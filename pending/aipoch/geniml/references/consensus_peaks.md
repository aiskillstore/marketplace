# Consensus Peaks: Building a Universe

## Overview

Geniml provides tools for building genomic "universes" — standardized consensus peak reference sets derived from collections of BED files. These universes represent genomic regions with significant coverage overlap across the analyzed datasets and serve as a reference vocabulary for tokenization and analysis.

## When to Use

Use consensus peak construction in the following scenarios:
- Building reference peak sets from multiple experiments
- Creating universe files for Region2Vec or BEDspace tokenization
- Normalizing genomic regions across a series of datasets
- Defining target regions with statistical significance

## Workflow

### Step 1: Merge BED Files

Merge all BED files into a single file:

```bash
cat /path/to/bed/files/*.bed > combined_files.bed
```

### Step 2: Generate Coverage Tracks

Use uniwig combined with a smoothing window to create bigWig coverage tracks:

```bash
uniwig -m 25 combined_files.bed chrom.sizes coverage/
```

**Parameter Descriptions:**
- `-m 25`: Smoothing window size (typically 25bp for chromatin accessibility analysis)
- `chrom.sizes`: Chromosome sizes file for the corresponding genome
- `coverage/`: Output directory for bigWig files

Smoothing windows help reduce noise and create more robust peak boundaries.

### Step 3: Build Universe

Use one of the following four methods to build consensus peaks:

## Universe Construction Methods

### 1. Coverage Cutoff (CC)

The simplest method using a fixed coverage threshold:

```bash
geniml universe build cc \
  --coverage-folder coverage/ \
  --output-file universe_cc.bed \
  --cutoff 5 \
  --merge 100 \
  --filter-size 50
```

**Parameter Descriptions:**
- `--cutoff`: Coverage threshold (1 = union; total number of files = intersection)
- `--merge`: Distance to merge adjacent peaks (bp)
- `--filter-size`: Minimum peak size to include in statistics (bp)

**Applicable Scenario:** When simple threshold-based selection is sufficient.

### 2. Flexible Coverage Cutoff (CCF)

Creates confidence intervals around likelihood split points for boundaries and region cores:

```bash
geniml universe build ccf \
  --coverage-folder coverage/ \
  --output-file universe_ccf.bed \
  --cutoff 5 \
  --confidence 0.95 \
  --merge 100 \
  --filter-size 50
```

**Extra Parameters:**
- `--confidence`: Confidence level for flexible boundaries (0-1)

**Applicable Scenario:** When capturing uncertainty in peak boundaries is required.

### 3. Maximum Likelihood (ML)

Builds a probabilistic model considering region start/end positions:

```bash
geniml universe build ml \
  --coverage-folder coverage/ \
  --output-file universe_ml.bed \
  --merge 100 \
  --filter-size 50 \
  --model-type gaussian
```

**Parameter Descriptions:**
- `--model-type`: Distribution type for likelihood estimation (gaussian, poisson)

**Applicable Scenario:** When statistical modeling of peak positions is crucial.

### 4. Hidden Markov Model (HMM)

Models genomic regions as hidden states, with coverage as observed emissions:

```bash
geniml universe build hmm \
  --coverage-folder coverage/ \
  --output-file universe_hmm.bed \
  --states 3 \
  --merge 100 \
  --filter-size 50
```

**Parameter Descriptions:**
- `--states`: Number of HMM hidden states (typically 2-5)

**Applicable Scenario:** When capturing complex genomic state patterns is necessary.

## Python API

```python
from geniml.universe import build_universe

# Build using the Coverage Cutoff method
universe = build_universe(
    coverage_folder='coverage/',
    method='cc',
    cutoff=5,
    merge_distance=100,
    min_size=50,
    output_file='universe.bed'
)
```

## Method Comparison

| Method | Complexity | Flexibility | Computational Cost | Best For |
|------|--------|--------|----------|--------|
| CC | Low | Low | Low | Quick reference set construction |
| CCF | Medium | Medium | Medium | Handling boundary uncertainty |
| ML | High | High | High | Rigorous statistical analysis |
| HMM | High | High | Very High | Complex pattern recognition |

## Best Practices

### Choosing a Method

1. **Start with CC**: Simple and easy to interpret for preliminary exploration.
2. **Use CCF**: When peak boundaries are uncertain or noisy.
3. **Apply ML**: For publication-level statistical analysis.
4. **Deploy HMM**: When modeling complex chromatin states.

### Parameter Selection

**Coverage cutoff:**
- `cutoff = 1`: Union of all peaks (most permissive)
- `cutoff = n_files`: Intersection (most restrictive)
- `cutoff = 0.5 * n_files`: Moderate consensus (typical choice)

**Merge distance:**
- ATAC-seq: 100-200bp
- ChIP-seq (narrow peaks): 50-100bp
- ChIP-seq (broad peaks): 500-1000bp

**Filter size:**
- Minimum 30bp to avoid artifacts
- Typical values are 50-100bp for most experiments
- Use larger values for broad histone marks

### Quality Control

After construction, evaluate the universe quality:

```python
from geniml.evaluation import assess_universe

metrics = assess_universe(
    universe_file='universe.bed',
    coverage_folder='coverage/',
    bed_files='bed_files/'
)

print(f"Number of regions: {metrics['n_regions']}")
print(f"Mean region size: {metrics['mean_size']:.1f}bp")
print(f"Input peak coverage: {metrics['coverage']:.1%}")
```

**Key Metrics:**
- **Region count**: Should capture main features without over-fragmentation.
- **Size distribution**: Should align with expected biological characteristics (e.g., ~500bp for ATAC-seq).
- **Input coverage**: The proportion of original peaks represented (typically should be >80%).

## Output Format

Consensus peaks are saved as a BED file with three required columns:

```
chr1    1000    1500
chr1    2000    2800
chr2    500     1000
```

Depending on the chosen method, additional columns may include confidence scores or state annotations.

## Common Workflows

### For Region2Vec

1. Build a universe using your preferred method
2. Use the universe as a reference for tokenization
3. Tokenize BED files
4. Train the Region2Vec model

### For BEDspace

1. Build a universe from all datasets
2. Use the universe in the preprocessing step
3. Train BEDspace using metadata
4. Query across regions and labels

### For scEmbed

1. Create a universe from bulk or aggregated scATAC-seq
2. Use for cell tokenization
3. Train the scEmbed model
4. Generate cell embeddings

## Troubleshooting

**Too few regions:** Lower the `cutoff` threshold or decrease the `filter-size`.

**Too many regions:** Increase the `cutoff` threshold, increase the `merge-distance`, or increase the `filter-size`.

**Noisy boundaries:** Use CCF or ML methods instead of CC.

**Computation taking too long:** Use the CC method to get quick results first, then refine with ML/HMM if necessary.