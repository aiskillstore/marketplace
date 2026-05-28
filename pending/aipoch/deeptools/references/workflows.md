# deepTools workflow

This document provides complete workflow examples for common scenarios in deepTools analysis.

## ChIP-seq Quality Control Workflow

A comprehensive quality control evaluation for ChIP-seq experiments.

### Step 1: Initial Correlation Assessment

Compare replicates and different samples to validate experimental quality:

# deepTools common workflows

This document provides complete example workflows for common deepTools analysis scenarios.

## ChIP-seq quality-control workflow

Complete QC assessment for ChIP-seq experiments.

### Step 1: Initial correlation checks

Compare replicates and different samples to validate experiment quality:

```bash
# Generate a genome-wide coverage matrix
multiBamSummary bins \
    --bamfiles Input1.bam Input2.bam ChIP1.bam ChIP2.bam \
    --labels Input_rep1 Input_rep2 ChIP_rep1 ChIP_rep2 \
    -o readCounts.npz \
    --numberOfProcessors 8

# Create a correlation heatmap
plotCorrelation \
    -in readCounts.npz \
    --corMethod pearson \
    --whatToShow heatmap \
    --plotFile correlation_heatmap.png \
    --plotNumbers

# Generate a PCA plot
plotPCA \
    -in readCounts.npz \
    -o PCA_plot.png \
    -T "PCA of ChIP-seq samples"
```

Expected results:
- Replicates should cluster together
- Input samples should be clearly separated from ChIP samples

---

### Step 2: Coverage and depth assessment

```bash
# Check sequencing depth and coverage
plotCoverage \
    --bamfiles Input1.bam ChIP1.bam ChIP2.bam \
    --labels Input ChIP_rep1 ChIP_rep2 \
    --plotFile coverage.png \
    --ignoreDuplicates \
    --numberOfProcessors 8
```

Interpretation: Assess whether sequencing depth is sufficient for downstream analysis.

---

### Step 3: Fragment size validation (paired-end)

```bash
# Validate expected fragment size distribution
bamPEFragmentSize \
    --bamfiles Input1.bam ChIP1.bam ChIP2.bam \
    --histogram fragmentSizes.png \
    --plotTitle "Fragment Size Distribution"
```

Expected result: Fragment sizes should match library prep expectations (ChIP-seq typically 200–600 bp).

---

### Step 4: GC bias detection and correction

```bash
# Compute GC bias
computeGCBias \
    --bamfile ChIP1.bam \
    --effectiveGenomeSize 2913022398 \
    --genome genome.2bit \
    --fragmentLength 200 \
    --biasPlot GCbias.png \
    --frequenciesFile freq.txt

# If bias is detected, correct it
correctGCBias \
    --bamfile ChIP1.bam \
    --effectiveGenomeSize 2913022398 \
    --genome genome.2bit \
    --GCbiasFrequenciesFile freq.txt \
    --correctedFile ChIP1_GCcorrected.bam
```

Note: Only correct when substantial bias is observed. Do NOT use `--ignoreDuplicates` on GC-corrected files.

---

### Step 5: ChIP enrichment assessment

```bash
# Assess ChIP enrichment
plotFingerprint \
    --bamfiles Input1.bam ChIP1.bam ChIP2.bam \
    --labels Input ChIP_rep1 ChIP_rep2 \
    --plotFile fingerprint.png \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8 \
    --outQualityMetrics fingerprint_metrics.txt
```

Interpretation:
- Strong ChIP: cumulative curve rises sharply at top ranks
- Weak enrichment: curve close to the diagonal (similar to Input)

---

## ChIP-seq analysis workflow

From BAM files to publication-ready visualizations.

### Step 1: Generate normalized coverage tracks

```bash
# Input control
bamCoverage \
    --bam Input.bam \
    --outFileName Input_coverage.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 10 \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8

# ChIP sample
bamCoverage \
    --bam ChIP.bam \
    --outFileName ChIP_coverage.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 10 \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8
```

---

### Step 2: Create a log2 ratio track

```bash
# Compare ChIP vs Input
bamCompare \
    --bamfile1 ChIP.bam \
    --bamfile2 Input.bam \
    --outFileName ChIP_vs_Input_log2ratio.bw \
    --operation log2 \
    --scaleFactorsMethod readCount \
    --binSize 10 \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8
```

Result: A log2 ratio track showing enrichment (positive) and depletion (negative).

---

### Step 3: Compute matrix around TSS

```bash
# Prepare matrix for TSS-centered heatmaps/profiles
computeMatrix reference-point \
    --referencePoint TSS \
    --scoreFileName ChIP_coverage.bw \
    --regionsFileName genes.bed \
    --beforeRegionStartLength 3000 \
    --afterRegionStartLength 3000 \
    --binSize 10 \
    --sortRegions descend \
    --sortUsing mean \
    --outFileName matrix_TSS.gz \
    --outFileNameMatrix matrix_TSS.tab \
    --numberOfProcessors 8
```

---

### Step 4: Plot heatmap

```bash
# Create heatmap around TSS
plotHeatmap \
    --matrixFile matrix_TSS.gz \
    --outFileName heatmap_TSS.png \
    --colorMap RdBu \
    --whatToShow 'plot, heatmap and colorbar' \
    --zMin -3 --zMax 3 \
    --yAxisLabel "Genes" \
    --xAxisLabel "Distance from TSS (bp)" \
    --refPointLabel "TSS" \
    --heatmapHeight 15 \
    --kmeans 3
```

---

### Step 5: Plot profile

```bash
# Create meta-profile around TSS
plotProfile \
    --matrixFile matrix_TSS.gz \
    --outFileName profile_TSS.png \
    --plotType lines \
    --perGroup \
    --colors blue \
    --plotTitle "ChIP-seq signal around TSS" \
    --yAxisLabel "Average signal" \
    --xAxisLabel "Distance from TSS (bp)" \
    --refPointLabel "TSS"
```

---

### Step 6: Enrichment analysis for peaks

```bash
# Calculate enrichment over peak regions
plotEnrichment \
    --bamfiles Input.bam ChIP.bam \
    --BED peaks.bed \
    --labels Input ChIP \
    --plotFile enrichment.png \
    --outRawCounts enrichment_counts.tab \
    --extendReads 200 \
    --ignoreDuplicates
```

---

## RNA-seq coverage workflow

Generate strand-specific coverage tracks for RNA-seq data.

### Forward strand

```bash
bamCoverage \
    --bam rnaseq.bam \
    --outFileName forward_coverage.bw \
    --filterRNAstrand forward \
    --normalizeUsing CPM \
    --binSize 1 \
    --numberOfProcessors 8
```

### Reverse strand

```bash
bamCoverage \
    --bam rnaseq.bam \
    --outFileName reverse_coverage.bw \
    --filterRNAstrand reverse \
    --normalizeUsing CPM \
    --binSize 1 \
    --numberOfProcessors 8
```

Important: Do NOT use `--extendReads` for RNA-seq (it will extend across splice junctions).

---

## Multi-sample comparison workflow

Compare multiple ChIP-seq samples (e.g., different conditions or time points).

### Step 1: Generate coverage files

```bash
# Iterate over samples
for sample in Control_ChIP Treated_ChIP; do
    bamCoverage \
        --bam ${sample}.bam \
        --outFileName ${sample}.bw \
        --normalizeUsing RPGC \
        --effectiveGenomeSize 2913022398 \
        --binSize 10 \
        --extendReads 200 \
        --ignoreDuplicates \
        --numberOfProcessors 8
done
```

---

### Step 2: Compute multi-sample matrix

```bash
computeMatrix scale-regions \
    --scoreFileName Control_ChIP.bw Treated_ChIP.bw \
    --regionsFileName genes.bed \
    --beforeRegionStartLength 1000 \
    --afterRegionStartLength 1000 \
    --regionBodyLength 3000 \
    --binSize 10 \
    --sortRegions descend \
    --sortUsing mean \
    --outFileName matrix_multi.gz \
    --numberOfProcessors 8
```

---

### Step 3: Multi-sample heatmap

```bash
plotHeatmap \
    --matrixFile matrix_multi.gz \
    --outFileName heatmap_comparison.png \
    --colorMap Blues \
    --whatToShow 'plot, heatmap and colorbar' \
    --samplesLabel Control Treated \
    --yAxisLabel "Genes" \
    --heatmapHeight 15 \
    --kmeans 4
```

---

### Step 4: Multi-sample profile

```bash
plotProfile \
    --matrixFile matrix_multi.gz \
    --outFileName profile_comparison.png \
    --plotType lines \
    --perGroup \
    --colors blue red \
    --samplesLabel Control Treated \
    --plotTitle "ChIP-seq signal comparison" \
    --startLabel "TSS" \
    --endLabel "TES"
```

---

## ATAC-seq workflow

Specialized workflow for ATAC-seq with Tn5 shift correction.

### Step 1: Shift reads for Tn5 correction

```bash
alignmentSieve \
    --bam atacseq.bam \
    --outFile atacseq_shifted.bam \
    --ATACshift \
    --minFragmentLength 38 \
    --maxFragmentLength 2000 \
    --ignoreDuplicates
```

---

### Step 2: Generate coverage track

```bash
bamCoverage \
    --bam atacseq_shifted.bam \
    --outFileName atacseq_coverage.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 1 \
    --numberOfProcessors 8
```

---

### Step 3: Fragment size analysis

```bash
bamPEFragmentSize \
    --bamfiles atacseq.bam \
    --histogram fragmentSizes_atac.png \
    --maxFragmentLength 1000
```

Expected pattern: nucleosome ladder with peaks at ~50 bp (nucleosome-free), ~200 bp (mononucleosome), ~400 bp (dinucleosome).

---

## Peak-region analysis workflow

Focused analysis of signal at called peaks.

### Step 1: Matrix at peaks

```bash
computeMatrix reference-point \
    --referencePoint center \
    --scoreFileName ChIP_coverage.bw \
    --regionsFileName peaks.bed \
    --beforeRegionStartLength 2000 \
    --afterRegionStartLength 2000 \
    --binSize 10 \
    --outFileName matrix_peaks.gz \
    --numberOfProcessors 8
```

---

### Step 2: Heatmap at peaks

```bash
plotHeatmap \
    --matrixFile matrix_peaks.gz \
    --outFileName heatmap_peaks.png \
    --colorMap YlOrRd \
    --refPointLabel "Peak Center" \
    --heatmapHeight 15 \
    --sortUsing max
```

---

## Troubleshooting

### Problem: Out of memory
Solution: Process one chromosome at a time using `--region`:
```bash
bamCoverage --bam input.bam -o chr1.bw --region chr1
```

### Problem: Missing BAM index
Solution: Index BAM files before running deepTools:
```bash
samtools index input.bam
```

### Problem: Slow processing
Solution: Increase `--numberOfProcessors`:
```bash
# Use 8 cores instead of the default
--numberOfProcessors 8
```

### Problem: bigWig files too large
Solution: Increase bin size:
```bash
--binSize 50  # or larger (defaults are often 10–50)
```

---

## Performance tips

1. Use multiple processors: always set `--numberOfProcessors` to available CPU cores.
2. Regional processing: use `--region` for tests or memory-limited environments.
3. Adjust bin size: larger bins speed up processing and reduce file size.
4. Pre-filter BAMs: create filtered BAMs once with `alignmentSieve` and reuse them.
5. Prefer bigWig over bedGraph: bigWig is compressed and faster to handle.

---

## Best practices

1. Always run QC first: correlation, coverage and fingerprint analyses before downstream steps.
2. Record parameters: save command-line scripts for reproducibility.
3. Use consistent normalization: apply the same normalization across samples in a comparison.
4. Verify reference genome consistency: ensure BAMs and region files use the same assembly.
5. Check strand orientation: verify forward/reverse strands for RNA-seq.
6. Test on a small region first: use `--region chr1:1-1000000` to quickly validate settings.
7. Keep intermediate files: save matrix files to regenerate plots with different settings later.