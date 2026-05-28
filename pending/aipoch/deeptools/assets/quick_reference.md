# deepTools Quick Reference Guide

## Most Common Commands

### BAM to bigWig (Normalization)
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC --effectiveGenomeSize 2913022398 \
    --binSize 10 --numberOfProcessors 8
```

### Compare Two BAM Files
```bash
bamCompare -b1 treatment.bam -b2 control.bam -o ratio.bw \
    --operation log2 --scaleFactorsMethod readCount
```

### Correlation Heatmap
```bash
multiBamSummary bins --bamfiles *.bam -o counts.npz
plotCorrelation -in counts.npz --corMethod pearson \
    --whatToShow heatmap -o correlation.png
```

### TSS Heatmap Around TSS
```bash
computeMatrix reference-point -S signal.bw -R genes.bed \
    -b 3000 -a 3000 --referencePoint TSS -o matrix.gz

plotHeatmap -m matrix.gz -o heatmap.png
```

### ChIP Enrichment Check (Fingerprint Plot)
```bash
plotFingerprint -b input.bam chip.bam -o fingerprint.png \
    --extendReads 200 --ignoreDuplicates
```

## Effective Genome Sizes (Effective Genome Sizes)

| Species | Assembly | Size |
|----------|----------|------|
| Human | hg38 | 2913022398 |
| Mouse | mm10 | 2652783500 |
| Fly | dm6 | 142573017 |

## Common Normalization Methods

- **RPGC**: genome coverage (requires `--effectiveGenomeSize` ）
- **CPM**: Counts per million mapped reads (suitable for fixed windows/bins)
- **RPKM**: Reads per kilobase per million mapped reads (suitable for genes)

## Typical Workflow

1. Quality Control (QC): plotFingerprint, plotCorrelation

2. Coverage Calculation: Use bamCoverage for normalization

3. Comparative Analysis: Use bamCompare to compare treatment vs control

4. Visualization: computeMatrix → plotHeatmap/plotProfile