# deepTools normalization methods

This document explains the various normalization methods available in deepTools and when to use them.

## Why normalize?

Normalization is essential to:
1. Compare samples with different sequencing depths
2. Correct for library size differences
3. Make coverage values interpretable across experiments
4. Ensure fair comparisons between conditions

Without normalization, a sample with 100 million reads will appear to have higher coverage than a sample with 50 million reads even if the underlying biological signal is identical.

---

## Available normalization methods

### 1. RPKM (Reads Per Kilobase per Million mapped reads)

Formula: (read count) / (region length in kb × total mapped reads in millions)

When to use:
- Compare different genomic regions within the same sample
- Correct for both sequencing depth and region length
- RNA-seq gene expression analysis

Tool: `bamCoverage`

Example:
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPKM
```

Interpretation: RPKM = 10 means 10 reads per kb per million mapped reads in that feature.

Pros:
- Accounts for region length and library size
- Widely used and understood in genomics

Cons:
- Not ideal for between-sample comparisons when total RNA content differs
- Can be misleading when sample composition differs greatly

---

### 2. CPM (Counts Per Million mapped reads)

Formula: (read count) / (total mapped reads in millions)

Also called RPM (Reads Per Million)

When to use:
- Compare the same genomic regions across samples
- When region length is fixed or irrelevant
- ChIP-seq, ATAC-seq, DNase-seq analyses

Tools: `bamCoverage`, `bamCompare`

Example:
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing CPM
```

Interpretation: CPM = 5 means 5 reads per million mapped reads in that bin.

Pros:
- Simple and intuitive
- Good for comparing samples with different sequencing depths
- Suitable for fixed-size bins

Cons:
- Does not account for region length
- Sensitive to very high abundance regions (e.g., rRNA in RNA-seq)

---

### 3. BPM (Bins Per Million mapped reads)

Formula: (reads in bin) / (total reads in all analyzed bins in millions)

Difference from CPM: BPM only considers reads falling in the analysis bins, not all mapped reads.

When to use:
- Similar to CPM but when you want to exclude reads outside the analyzed regions
- Compare specific genomic regions while ignoring background

Tools: `bamCoverage`, `bamCompare`

Example:
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing BPM
```

Interpretation: BPM normalizes using only reads within the bins of interest.

Pros:
- Focuses normalization on analyzed regions
- Less influenced by reads outside the regions of interest

Cons:
- Less commonly used; may be hard to compare with published data

---

### 4. RPGC (Reads Per Genomic Content)

Formula: (read count × scaling factor) / effective genome size

Scaling factor: chosen so that values correspond to 1× genome coverage (one read per base)

When to use:
- Obtain comparable coverage values across samples
- Provide interpretable absolute coverage values
- Compare samples with very different total read counts
- ChIP-seq experiments with spike-in normalization

Tools: `bamCoverage`, `bamCompare`

Required parameter: `--effectiveGenomeSize`

Example:
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398
```

Interpretation: values approximate coverage depth (e.g., 2 ≈ 2× coverage).

Pros:
- Produces 1× normalized coverage
- Coverage values are interpretable in genome-wide terms
- Good for comparing samples with different sequencing depths

Cons:
- Requires a known effective genome size
- Assumes uniform coverage (which may not hold for peak-based ChIP-seq)

---

### 5. None (no normalization)

Formula: raw read counts

When to use:
- Preliminary inspections
- When samples have identical library sizes (rare)
- When downstream tools will perform normalization
- Debugging or QC

Tool: All tools (usually the default)

Example:
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing None
```

Interpretation: raw read counts per bin.

Pros:
- Makes no assumptions
- Useful to inspect raw data
- Fastest to compute

Cons:
- Not appropriate for fair comparison across samples with different depths
- Not suitable for publication-quality figures

---

### 6. SES (Selective Enrichment Statistics)

Method: Signal Extraction Scaling — a more sophisticated scaling method for comparing ChIP to control.

When to use:
- Use with `bamCompare` for ChIP-seq analyses
- When you need more sophisticated background correction
- As an alternative to simple readCount scaling

Tool: `bamCompare` only

Example:
```bash
bamCompare -b1 chip.bam -b2 input.bam -o output.bw \
    --scaleFactorsMethod SES
```

Note: SES is designed for ChIP-seq and may outperform simple scaling in noisy datasets.

---

### 7. readCount (read count scaling)

Method: Scale by the ratio of total read counts between samples.

When to use:
- Default method for `bamCompare`
- Compensate for sequencing depth differences in comparisons
- When you trust total read count as a proxy for library size

Tool: `bamCompare`

Example:
```bash
bamCompare -b1 treatment.bam -b2 control.bam -o output.bw \
    --scaleFactorsMethod readCount
```

How it works: If sample A has 100M reads and sample B has 50M reads, sample B is scaled by 2 before comparison.

---

## Choosing a normalization method

### For ChIP-seq coverage tracks

Recommended: RPGC or CPM

```bash
bamCoverage --bam chip.bam --outFileName chip.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --extendReads 200 \
    --ignoreDuplicates
```

Reason: Accounts for sequencing depth differences; RPGC yields interpretable coverage values.

---

### For ChIP-seq comparisons (treatment vs control)

Recommended: log2 ratio with readCount or SES scaling

```bash
bamCompare -b1 chip.bam -b2 input.bam -o ratio.bw \
    --operation log2 \
    --scaleFactorsMethod readCount \
    --extendReads 200 \
    --ignoreDuplicates
```

Reason: Log2 ratios show enrichment (positive) and depletion (negative); readCount adjusts depth.

---

### For RNA-seq coverage tracks

Recommended: CPM or RPKM

```bash
# strand-specific forward
bamCoverage --bam rnaseq.bam --outFileName forward.bw \
    --normalizeUsing CPM \
    --filterRNAstrand forward

# gene-level: RPKM accounts for gene length
bamCoverage --bam rnaseq.bam --outFileName output.bw \
    --normalizeUsing RPKM
```

Reason: CPM for fixed-width bins; RPKM for gene-level coverage where length matters.

---

### For ATAC-seq

Recommended: RPGC or CPM

```bash
bamCoverage --bam atac_shifted.bam --outFileName atac.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398
```

Reason: Similar to ChIP-seq — aiming for comparable coverage across samples.

---

### For sample correlation analyses

Recommended: CPM or RPGC

```bash
multiBamSummary bins \
    --bamfiles sample1.bam sample2.bam sample3.bam \
    -o readCounts.npz

plotCorrelation -in readCounts.npz \
    --corMethod pearson \
    --whatToShow heatmap \
    -o correlation.png
```

Note: `multiBamSummary` does not explicitly normalize, but correlation analyses are relatively robust to scaling. For large library-size differences consider normalizing BAMs first or use `multiBigwigSummary` on CPM-normalized bigWig files.

---

## Advanced normalization considerations

### Spike-in normalization

For experiments with spike-in controls (e.g., Drosophila chromatin spike-ins for ChIP):

1. Calculate a scaling factor from spike-in reads
2. Apply the custom scaling factor with `--scaleFactor`

```bash
# compute spike-in factor (e.g., 0.8)
SCALE_FACTOR=0.8

bamCoverage --bam chip.bam --outFileName chip_spikenorm.bw \
    --scaleFactor ${SCALE_FACTOR} \
    --extendReads 200
```

---

### Manual scale factors

You can apply a custom scale factor:

```bash
# apply 2x scaling
bamCoverage --bam input.bam --outFileName output.bw \
    --scaleFactor 2.0
```

---

### Excluding chromosomes

Exclude specific chromosomes from normalization calculations:

```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --ignoreForNormalization chrX chrY chrM
```

When to use: sex chromosomes in mixed-sex samples, mitochondrial DNA, or chromosomes with abnormal coverage.

---

## Common pitfalls

### 1. Using RPKM on bin-based data
Problem: RPKM accounts for region length but bins are all the same size.
Fix: Use CPM or RPGC instead.

### 2. Comparing unnormalized samples
Problem: A sample with 2× sequencing depth will look like it has 2× signal.
Fix: Always normalize before comparing samples.

### 3. Wrong effective genome size
Problem: Using hg19 genome size on hg38 data.
Fix: Verify the genome assembly and use the correct effective genome size.

### 4. Ignoring duplicates after GC correction
Problem: May introduce bias.
Fix: Do not use `--ignoreDuplicates` after `correctGCBias`.

### 5. Using RPGC without specifying effective genome size
Problem: Command will fail.
Fix: Always specify `--effectiveGenomeSize` with RPGC.

---

## Normalization strategies for comparison scenarios

### Within-sample comparisons (different regions)
Use: RPKM (accounts for region length)

### Between-sample comparisons (same regions)
Use: CPM, RPGC, or BPM (account for library size)

### Treatment vs control comparisons
Use: `bamCompare` with log2 ratios and readCount/SES scaling

### Multi-sample correlation
Use: CPM- or RPGC-normalized bigWig files and `multiBigwigSummary`

---

## Quick reference table

| Method | Accounts for depth | Accounts for length | Best for | Flag |
|--------|-------------------:|--------------------:|---------|------|
| RPKM   | ✓                  | ✓                   | RNA-seq gene-level | `--normalizeUsing RPKM` |
| CPM    | ✓                  | ✗                   | Fixed-size bins     | `--normalizeUsing CPM` |
| BPM    | ✓                  | ✗                   | Specific regions    | `--normalizeUsing BPM` |
| RPGC   | ✓                  | ✗                   | Interpretable coverage | `--normalizeUsing RPGC --effectiveGenomeSize X` |
| None   | ✗                  | ✗                   | Raw inspection      | `--normalizeUsing None` |
| SES    | ✓                  | ✗                   | ChIP comparisons    | `bamCompare --scaleFactorsMethod SES` |
| readCount | ✓               | ✗                   | ChIP comparisons    | `bamCompare --scaleFactorsMethod readCount` |

---

## Further reading

For more detail on normalization theory and best practices:
- deepTools documentation: https://deeptools.readthedocs.io/
- ENCODE ChIP-seq guidelines
- RNA-seq normalization literature (DESeq2, TMM methods)