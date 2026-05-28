# deepTools complete tools reference guide

This document provides a categorized reference for the deepTools command-line utilities.

## BAM and bigWig processing tools

### multiBamSummary

Compute read coverages for multiple BAM files over genomic regions and output a compressed numpy array suitable for downstream correlation and PCA analyses.

Modes:
- bins: Genome-wide analysis using contiguous equal-sized windows (default 10kb)
- BED-file: Analyze only user-specified genomic regions

Key parameters:
- `--bamfiles, -b`: Indexed BAM files (space-separated, required)
- `--outFileName, -o`: Output coverage matrix file (required)
- `--BED`: Region file (BED-file mode only)
- `--binSize`: Window size in bases (default: 10,000)
- `--labels`: Custom sample labels
- `--minMappingQuality`: Minimum mapping quality for reads to include
- `--numberOfProcessors, -p`: Number of parallel cores
- `--extendReads`: Extend reads to fragment length
- `--ignoreDuplicates`: Remove PCR duplicates
- `--outRawCounts`: Export tab-separated raw counts with coordinates and sample columns

Output: Compressed numpy array (.npz) for use with `plotCorrelation` and `plotPCA`.

Common usage:
```bash
# Genome-wide comparison
multiBamSummary bins --bamfiles sample1.bam sample2.bam -o results.npz

# Compare peak regions
multiBamSummary BED-file --BED peaks.bed --bamfiles sample1.bam sample2.bam -o results.npz
```

---

### multiBigwigSummary

Similar to `multiBamSummary` but operates on bigWig files instead of BAMs. Use it to compare coverage tracks across samples.

Modes:
- bins: Genome-wide analysis
- BED-file: Region-specific analysis

Key parameters: Similar to `multiBamSummary` but accepts bigWig inputs.

---

### bamCoverage

Convert BAM alignment files into normalized coverage tracks in bigWig or bedGraph format. Computes read counts per bin as coverage.

Key parameters:
- `--bam, -b`: Input BAM file (required)
- `--outFileName, -o`: Output file name (required)
- `--outFileFormat, -of`: Output type (bigwig or bedgraph)
- `--normalizeUsing`: Normalization method
  - RPKM: Reads per kilobase per million mapped reads
  - CPM: Counts per million mapped reads
  - BPM: Bins per million mapped reads
  - RPGC: Reads per genomic content (requires `--effectiveGenomeSize`)
  - None: No normalization (default)
- `--effectiveGenomeSize`: Effective genome size (required for RPGC)
- `--binSize`: Resolution in bases (default: 50)
- `--extendReads, -e`: Extend reads to fragment length (recommended for ChIP-seq; NOT for RNA-seq)
- `--centerReads`: Center reads to fragment midpoint to sharpen signal
- `--ignoreDuplicates`: Count duplicate reads only once
- `--minMappingQuality`: Filter out reads below this quality
- `--minFragmentLength / --maxFragmentLength`: Fragment length filtering
- `--smoothLength`: Window for smoothing to denoise signal
- `--MNase`: Options for MNase-seq and nucleosome positioning
- `--Offset`: Shift reads for specialized assays (RiboSeq, GRO-seq)
- `--filterRNAstrand`: Separate forward/reverse strand RNA reads
- `--ignoreForNormalization`: Exclude chromosomes from normalization (e.g., sex chromosomes)
- `--numberOfProcessors, -p`: Parallelize processing

Important notes:
- For RNA-seq: do NOT use `--extendReads` (it will extend across splice junctions)
- For ChIP-seq: use `--extendReads` with smaller `--binSize` for sharper peaks
- Never apply `--ignoreDuplicates` after GC bias correction

Common usage:
```bash
# Basic coverage with RPKM normalization
bamCoverage --bam input.bam --outFileName coverage.bw --normalizeUsing RPKM

# ChIP-seq with extension
bamCoverage --bam chip.bam --outFileName chip_coverage.bw \
    --binSize 10 --extendReads 200 --ignoreDuplicates

# Strand-specific RNA-seq
bamCoverage --bam rnaseq.bam --outFileName forward.bw \
    --filterRNAstrand forward
```

---

### bamCompare

Compare two BAM files by producing a bigWig or bedGraph result and apply normalization for sequencing depth differences. The genome is processed in equal-sized bins and a per-bin computation is performed.

Comparison methods:
- log2 (default): Log2 ratio of sample signals
- ratio: Direct ratio
- subtract: Difference between files
- add: Sum of signals
- mean: Mean of signals
- reciprocal_ratio: Negative reciprocal for ratios < 0
- first/second: Output scaled signal from a single file

Normalization methods:
- readCount (default): Compensate for sequencing depth
- SES: Selective Enrichment Statistics
- RPKM, CPM, BPM, RPGC (RPGC requires `--effectiveGenomeSize`)

Key parameters:
- `--bamfile1, -b1`: First BAM file (required)
- `--bamfile2, -b2`: Second BAM file (required)
- `--outFileName, -o`: Output file name (required)
- `--outFileFormat`: bigwig or bedgraph
- `--operation`: Comparison operation
- `--scaleFactorsMethod`: Normalization method
- `--binSize`: Bin width for output (default: 50 bp)
- `--pseudocount`: Avoid division by zero (default: 1)
- `--extendReads`: Extend reads to fragment length
- `--ignoreDuplicates`: Count duplicates once
- `--minMappingQuality`: Minimum mapping quality
- `--numberOfProcessors, -p`: Parallel processing

Common usage:
```bash
# Log2 ratio (treatment vs control)
bamCompare -b1 treatment.bam -b2 control.bam -o log2ratio.bw

# Subtract control from treatment with readCount scaling
bamCompare -b1 treatment.bam -b2 control.bam -o difference.bw \
    --operation subtract --scaleFactorsMethod readCount
```

---

### correctGCBias / computeGCBias

`computeGCBias`: Identify GC bias introduced by sequencing and PCR amplification.

`correctGCBias`: Correct BAM file GC bias using frequencies detected by `computeGCBias`.

Key parameters (`computeGCBias`):
- `--bamfile, -b`: Input BAM file
- `--effectiveGenomeSize`: Effective mappable genome size
- `--genome, -g`: Reference genome in 2bit format
- `--fragmentLength, -l`: Fragment length for single-end data
- `--biasPlot`: Output diagnostic plot

Key parameters (`correctGCBias`):
- `--bamfile, -b`: Input BAM file
- `--effectiveGenomeSize`: Effective mappable genome size
- `--genome, -g`: Reference genome in 2bit format
- `--GCbiasFrequenciesFile`: Frequency file from `computeGCBias`
- `--correctedFile, -o`: Output corrected BAM

Important note: Do not use `--ignoreDuplicates` after GC bias correction.

---

### alignmentSieve

Filter a BAM file on the fly according to multiple quality metrics. Useful to create a filtered BAM for specific analyses.

Key parameters:
- `--bam, -b`: Input BAM
- `--outFile, -o`: Output BAM
- `--minMappingQuality`: Minimum mapping quality
- `--ignoreDuplicates`: Remove duplicates
- `--minFragmentLength / --maxFragmentLength`: Fragment length filters
- `--samFlagInclude / --samFlagExclude`: SAM flag filters
- `--shift`: Shift reads (e.g., ATAC-seq Tn5 correction)
- `--ATACshift`: Automatic ATAC-seq shift

---

### computeMatrix

Compute scores for genomic regions and prepare a matrix for `plotHeatmap` and `plotProfile`. It consumes bigWig score files and BED/GTF region files.

Modes:
- reference-point: Signal around a specific point (TSS, TES, or center)
- scale-regions: Signal scaled across region bodies to a uniform length

Key parameters:
- `-R`: Regions file in BED/GTF format (required)
- `-S`: BigWig score files (required)
- `-o`: Output matrix file (required)
- `-b`: Upstream distance from reference point
- `-a`: Downstream distance from reference point
- `-m`: Region body length (scale-regions only)
- `-bs, --binSize`: Bin size for averaging scores
- `--skipZeros`: Skip regions with all zeros
- `--minThreshold / --maxThreshold`: Filter by signal intensity
- `--sortRegions`: ascending, descending, keep, no
- `--sortUsing`: mean, median, max, min, sum, region length
- `-p, --numberOfProcessors`: Parallel processing
- `--averageTypeBins`: Statistical method (mean, median, min, max, sum, std)

Output options:
- `--outFileNameMatrix`: Export tab-delimited numeric matrix
- `--outFileSortedRegions`: Save filtered/sorted BED file

Common usage:
```bash
# TSS matrix
computeMatrix reference-point -S signal.bw -R genes.bed \
    -o matrix.gz -b 2000 -a 2000 --referencePoint TSS

# Scaled gene body matrix
computeMatrix scale-regions -S signal.bw -R genes.bed \
    -o matrix.gz -b 1000 -a 1000 -m 3000
```

---

## Quality control tools (QC)

### plotFingerprint

A QC tool primarily for ChIP-seq to assess antibody enrichment. Generates cumulative read coverage plots to separate signal from background.

Key parameters:
- `--bamfiles, -b`: Indexed BAM files (required)
- `--plotFile, -plot, -o`: Output image file (required)
- `--extendReads, -e`: Extend reads to fragment length
- `--ignoreDuplicates`: Count duplicates once
- `--minMappingQuality`: Mapping quality filter
- `--centerReads`: Center reads to fragment midpoint
- `--minFragmentLength / --maxFragmentLength`: Fragment filters
- `--outRawCounts`: Save per-bin read counts
- `--outQualityMetrics`: Output QC metrics (Jensen-Shannon distance)
- `--labels`: Custom sample labels
- `--numberOfProcessors, -p`: Parallel processing

Interpreting results:
- Ideal input: a diagonal straight line
- Well-enriched ChIP: sharp rise at high ranks (reads concentrated in few bins)
- Weak enrichment: curve closer to diagonal

Common usage:
```bash
plotFingerprint -b input.bam chip1.bam chip2.bam \
    --labels Input ChIP1 ChIP2 -o fingerprint.png \
    --extendReads 200 --ignoreDuplicates
```

---

### plotCoverage

Visualize the average read distribution genome-wide. Useful to assess coverage and whether sequencing depth is sufficient.

Key parameters:
- `--bamfiles, -b`: BAM files to analyze (required)
- `--plotFile, -o`: Output plot file (required)
- `--ignoreDuplicates`: Remove PCR duplicates
- `--minMappingQuality`: Mapping quality threshold
- `--outRawCounts`: Save raw data
- `--labels`: Sample names
- `--numberOfSamples`: Number of sampling positions (default: 1,000,000)

---

### bamPEFragmentSize

Determine fragment size distribution for paired-end data — a key QC step to verify library construction.

Key parameters:
- `--bamfiles, -b`: BAM files (required)
- `--histogram, -hist`: Output histogram file (required)
- `--plotTitle, -T`: Plot title
- `--maxFragmentLength`: Maximum fragment length to consider (default: 1000)
- `--logScale`: Use log scale for Y-axis
- `--outRawFragmentLengths`: Save raw fragment lengths

---

### plotCorrelation

Analyze sample correlations from `multiBamSummary` or `multiBigwigSummary` outputs. Visualize similarity between samples.

Correlation methods:
- Pearson: Measures linear relationships; sensitive to outliers; suited for normally distributed data
- Spearman: Rank-based; less sensitive to outliers; suitable for non-normal data

Visualization options:
- heatmap: Heatmap with hierarchical clustering (complete linkage)
- scatterplot: Pairwise scatterplots with correlation coefficients

Key parameters:
- `--corData, -in`: Input matrix from `multiBamSummary`/`multiBigwigSummary` (required)
- `--corMethod`: pearson or spearman (required)
- `--whatToShow`: heatmap or scatterplot (required)
- `--plotFile, -o`: Output file (required)
- `--skipZeros`: Exclude regions with all zeros
- `--removeOutliers`: Filter outliers using median absolute deviation (MAD)
- `--outFileCorMatrix`: Export correlation matrix
- `--labels`: Custom sample names
- `--plotTitle`: Plot title
- `--colorMap`: Color map (50+ options)
- `--plotNumbers`: Display correlation coefficients on heatmap

Common usage:
```bash
# Heatmap with Pearson correlation
plotCorrelation -in readCounts.npz --corMethod pearson \
    --whatToShow heatmap -o correlation_heatmap.png --plotNumbers

# Scatterplot with Spearman correlation
plotCorrelation -in readCounts.npz --corMethod spearman \
    --whatToShow scatterplot -o correlation_scatter.png
```

---

### plotPCA

Generate PCA plots from `multiBamSummary` or `multiBigwigSummary` outputs to display sample relationships in reduced dimensions.

Key parameters:
- `--corData, -in`: Coverage file from `multiBamSummary`/`multiBigwigSummary` (required)
- `--plotFile, -o`: Output image (png, eps, pdf, svg) (required)
- `--outFileNameData`: Export PCA data (loadings and eigenvalues)
- `--labels, -l`: Custom sample labels
- `--plotTitle, -T`: Plot title
- `--plotHeight / --plotWidth`: Dimensions (cm)
- `--colors`: Custom symbol colors
- `--markers`: Marker shapes
- `--transpose`: Perform PCA on transposed matrix (rows = samples)
- `--ntop`: Use top N most variable rows (default: 1000)
- `--PCs`: Principal components to plot (default: 1 2)
- `--log2`: Apply log2 transform before analysis
- `--rowCenter`: Center each row to zero

Common usage:
```bash
plotPCA -in readCounts.npz -o PCA_plot.png \
    -T "PCA of read counts" --transpose
```

---

## Visualization tools

### plotHeatmap

Create genomic region heatmaps from `computeMatrix` output. Produces publication-quality visualizations.

Key parameters:
- `--matrixFile, -m`: Matrix from `computeMatrix` (required)
- `--outFileName, -o`: Output image (png, eps, pdf, svg) (required)
- `--outFileSortedRegions`: Save filtered regions
- `--outFileNameMatrix`: Export matrix values
- `--interpolationMethod`: auto, nearest, bilinear, bicubic, gaussian
  - default: nearest (≤1000 columns), bilinear (>1000 columns)
- `--dpi`: Image resolution

Clustering:
- `--kmeans`: k-means clustering
- `--hclust`: hierarchical clustering (slow for >1000 regions)
- `--silhouette`: Compute clustering quality metric

Visual customization:
- `--heatmapHeight / --heatmapWidth`: Size (3–100 cm)
- `--whatToShow`: plot, heatmap, colorbar (combinable)
- `--alpha`: Transparency (0–1)
- `--colorMap`: 50+ color palettes
- `--colorList`: Custom gradient colors
- `--zMin / --zMax`: Intensity scale limits
- `--boxAroundHeatmaps`: Show border (default: yes)

Labels:
- `--xAxisLabel / --yAxisLabel`: Axis labels
- `--regionsLabel`: Region set identifier
- `--samplesLabel`: Sample names
- `--refPointLabel`: Reference point label
- `--startLabel / --endLabel`: Region boundary labels

Common usage:
```bash
# Basic heatmap
plotHeatmap -m matrix.gz -o heatmap.png

# Heatmap with clustering and custom colors
plotHeatmap -m matrix.gz -o heatmap.png \
    --kmeans 3 --colorMap RdBu --zMin -3 --zMax 3
```

---

### plotProfile

Create profile/summary plots of scores across genomic regions from `computeMatrix` output.

Key parameters:
- `--matrixFile, -m`: Matrix from `computeMatrix` (required)
- `--outFileName, -o`: Output image (png, eps, pdf, svg) (required)
- `--plotType`: lines, fill, se, std, overlapped_lines, heatmap
- `--colors`: Palette (names or hex codes)
- `--plotHeight / --plotWidth`: Dimensions (cm)
- `--yMin / --yMax`: Y-axis range
- `--averageType`: mean, median, min, max, std, sum

Clustering:
- `--kmeans`: k-means clustering
- `--hclust`: hierarchical clustering
- `--silhouette`: Clustering quality metric

Labels:
- `--plotTitle`: Main title
- `--regionsLabel`: Region set identifier
- `--samplesLabel`: Sample names
- `--startLabel / --endLabel`: Region boundary labels (scale-regions only)

Output options:
- `--outFileNameData`: Export data as TSV
- `--outFileSortedRegions`: Save filtered/sorted regions as BED

Common usage:
```bash
# Line profile
plotProfile -m matrix.gz -o profile.png --plotType lines

# Profile with standard error shading
plotProfile -m matrix.gz -o profile.png --plotType se \
    --colors blue red green
```

---

### plotEnrichment

Compute and visualize signal enrichment over genomic regions. Measures the proportion of alignments overlapping given region groups. Commonly used to compute FRiP (Fraction of Reads in Peaks) scores.

Key parameters:
- `--bamfiles, -b`: Indexed BAM files (required)
- `--BED`: BED/GTF regions file (required)
- `--plotFile, -o`: Output image (png, pdf, eps, svg)
- `--labels, -l`: Custom sample labels
- `--outRawCounts`: Export numeric counts
- `--perSample`: Group by sample rather than by feature (default)
- `--regionLabels`: Custom region names

Read handling:
- `--minFragmentLength / --maxFragmentLength`: Fragment filters
- `--minMappingQuality`: Mapping quality filter
- `--samFlagInclude / --samFlagExclude`: SAM flag filtering
- `--ignoreDuplicates`: Remove duplicates
- `--centerReads`: Center reads to fragment midpoint for clarity

Common usage:
```bash
plotEnrichment -b Input.bam H3K4me3.bam \
    --BED peaks_up.bed peaks_down.bed \
    --regionLabels "Up regulated" "Down regulated" \
    -o enrichment.png
```

---

## Other tools

### computeMatrixOperations

Advanced operations to merge or extract from `computeMatrix` matrices. Supports complex multi-sample and multi-region workflows.

Operations:
- `cbind`: Column-wise concatenate matrices
- `rbind`: Row-wise concatenate matrices
- `subset`: Extract specific samples or regions
- `filterStrand`: Keep regions only on a specific strand
- `filterValues`: Apply signal intensity filters
- `sort`: Sort regions by various criteria
- `dataRange`: Report min/max values

Common usage:
```bash
# Concatenate matrices by columns
computeMatrixOperations cbind -m matrix1.gz matrix2.gz -o combined.gz

# Extract specific samples
computeMatrixOperations subset -m matrix.gz --samples 0 2 -o subset.gz
```

---

### estimateReadFiltering

Estimate the impact of different filtering parameters without performing the full filtering. Useful to optimize filters before running complete analyses.

Key parameters:
- `--bamfiles, -b`: BAM files to analyze
- `--sampleSize`: Number of reads to sample (default: 100,000)
- `--binSize`: Bin size for analysis
- `--distanceBetweenBins`: Spacing between sampled bins

Filter options to test:
- `--minMappingQuality`: Test quality thresholds
- `--ignoreDuplicates`: Evaluate effect of duplicates
- `--minFragmentLength / --maxFragmentLength`: Test fragment filters

---

## Common cross-tool parameters

Many deepTools commands share filtering and performance options:

Read filtering:
- `--ignoreDuplicates`: Remove PCR duplicates
- `--minMappingQuality`: Filter by mapping confidence
- `--samFlagInclude / --samFlagExclude`: SAM format filtering
- `--minFragmentLength / --maxFragmentLength`: Fragment length bounds

Performance:
- `--numberOfProcessors, -p`: Enable parallel processing
- `--region`: Operate on a specific genomic region (chr:start-end)

Read handling:
- `--extendReads`: Extend reads to fragment length
- `--centerReads`: Center reads to fragment midpoint
- `--ignoreDuplicates`: Count unique reads only