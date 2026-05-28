# Common Bioinformatics Workflows using Pysam

## Overview

This document provides practical examples of common bioinformatics workflows using pysam, demonstrating how to combine different file types and operations.

## Quality Control Workflows

### Calculating BAM Statistics

```python
import pysam

def calculate_bam_stats(bam_file):
    """Calculate basic statistics for a BAM file."""
    samfile = pysam.AlignmentFile(bam_file, "rb")

    stats = {
        "total_reads": 0,
        "mapped_reads": 0,
        "unmapped_reads": 0,
        "paired_reads": 0,
        "proper_pairs": 0,
        "duplicates": 0,
        "total_bases": 0,
        "mapped_bases": 0
    }

    for read in samfile.fetch(until_eof=True):
        stats["total_reads"] += 1

        if read.is_unmapped:
            stats["unmapped_reads"] += 1
        else:
            stats["mapped_reads"] += 1
            stats["mapped_bases"] += read.query_alignment_length

        if read.is_paired:
            stats["paired_reads"] += 1
            if read.is_proper_pair:
                stats["proper_pairs"] += 1

        if read.is_duplicate:
            stats["duplicates"] += 1

        stats["total_bases"] += read.query_length

    samfile.close()

    stats["mapping_rate"] = stats["mapped_reads"] / stats["total_reads"] if stats["total_reads"] > 0 else 0
    stats["duplication_rate"] = stats["duplicates"] / stats["total_reads"] if stats["total_reads"] > 0 else 0

    return stats
```

### Checking Reference Genome Consistency

```python
def check_bam_reference_consistency(bam_file, fasta_file):
    """Verify that BAM alignments match the reference genome."""
    samfile = pysam.AlignmentFile(bam_file, "rb")
    fasta = pysam.FastaFile(fasta_file)

    mismatches = 0
    total_checked = 0

    for read in samfile.fetch():
        if read.is_unmapped:
            continue

        ref_seq = fasta.fetch(
            read.reference_name,
            read.reference_start,
            read.reference_end
        )

        aligned_pairs = read.get_aligned_pairs(with_seq=True)

        for query_pos, ref_pos, ref_base in aligned_pairs:
            if query_pos is not None and ref_pos is not None and ref_base is not None:
                read_base = read.query_sequence[query_pos]
                if read_base.upper() != ref_base.upper():
                    mismatches += 1
                total_checked += 1

        if total_checked >= 10000:
            break

    samfile.close()
    fasta.close()

    error_rate = mismatches / total_checked if total_checked > 0 else 0
    return {
        "positions_checked": total_checked,
        "mismatches": mismatches,
        "error_rate": error_rate
    }
```

## Coverage Analysis

### Calculating Per-Base Coverage

```python
def calculate_coverage(bam_file, chrom, start, end):
    """Calculate coverage at each position in a region."""
    samfile = pysam.AlignmentFile(bam_file, "rb")

    length = end - start
    coverage = [0] * length

    for pileupcolumn in samfile.pileup(chrom, start, end):
        if start <= pileupcolumn.pos < end:
            coverage[pileupcolumn.pos - start] = pileupcolumn.nsegments

    samfile.close()

    return coverage
```

### Identifying Low Coverage Regions

```python
def find_low_coverage_regions(bam_file, chrom, start, end, min_coverage=10):
    """Find regions with coverage below threshold."""
    samfile = pysam.AlignmentFile(bam_file, "rb")

    low_coverage_regions = []
    in_low_region = False
    region_start = None

    for pileupcolumn in samfile.pileup(chrom, start, end):
        pos = pileupcolumn.pos
        if pos < start or pos >= end:
            continue

        coverage = pileupcolumn.nsegments

        if coverage < min_coverage:
            if not in_low_region:
                region_start = pos
                in_low_region = True
        else:
            if in_low_region:
                low_coverage_regions.append((region_start, pos))
                in_low_region = False

    if in_low_region:
        low_coverage_regions.append((region_start, end))

    samfile.close()

    return low_coverage_regions
```

### Calculating Coverage Statistics

```python
def coverage_statistics(bam_file, chrom, start, end):
    """Calculate coverage statistics for a region."""
    samfile = pysam.AlignmentFile(bam_file, "rb")

    coverages = []

    for pileupcolumn in samfile.pileup(chrom, start, end):
        if start <= pileupcolumn.pos < end:
            coverages.append(pileupcolumn.nsegments)

    samfile.close()

    if not coverages:
        return None

    coverages.sort()
    n = len(coverages)

    return {
        "mean": sum(coverages) / n,
        "median": coverages[n // 2],
        "min": coverages[0],
        "max": coverages[-1],
        "positions": n
    }
```

## Variant Analysis

### Extracting Variants in Specific Regions

```python
def extract_variants_in_genes(vcf_file, bed_file):
    """Extract variants overlapping gene regions."""
    vcf = pysam.VariantFile(vcf_file)
    bed = pysam.TabixFile(bed_file)

    variants_by_gene = {}

    for gene in bed.fetch(parser=pysam.asBed()):
        gene_name = gene.name
        variants_by_gene[gene_name] = []

        for variant in vcf.fetch(gene.contig, gene.start, gene.end):
            variant_info = {
                "chrom": variant.chrom,
                "pos": variant.pos,
                "ref": variant.ref,
                "alt": variant.alts,
                "qual": variant.qual
            }
            variants_by_gene[gene_name].append(variant_info)

    vcf.close()
    bed.close()

    return variants_by_gene
```

### Annotating Variants with Coverage

```python
def annotate_variants_with_coverage(vcf_file, bam_file, output_file):
    """Add coverage information to variants."""
    vcf = pysam.VariantFile(vcf_file)
    samfile = pysam.AlignmentFile(bam_file, "rb")

    if "DP" not in vcf.header.info:
        vcf.header.info.add("DP", "1", "Integer", "Total Depth from BAM")

    outvcf = pysam.VariantFile(output_file, "w", header=vcf.header)

    for variant in vcf:
        coverage = samfile.count(
            variant.chrom,
            variant.pos - 1,
            variant.pos
        )

        variant.info["DP"] = coverage

        outvcf.write(variant)

    vcf.close()
    samfile.close()
    outvcf.close()
```

### Filtering Variants by Read Support

```python
def filter_variants_by_support(vcf_file, bam_file, output_file, min_alt_reads=3):
    """Filter variants requiring minimum alt allele support."""
    vcf = pysam.VariantFile(vcf_file)
    samfile = pysam.AlignmentFile(bam_file, "rb")
    outvcf = pysam.VariantFile(output_file, "w", header=vcf.header)

    for variant in vcf:
        allele_counts = {variant.ref: 0}
        for alt in variant.alts:
            allele_counts[alt] = 0

        for pileupcolumn in samfile.pileup(
            variant.chrom,
            variant.pos - 1,
            variant.pos
        ):
            if pileupcolumn.pos == variant.pos - 1:
                for pileupread in pileupcolumn.pileups:
                    if not pileupread.is_del and not pileupread.is_refskip:
                        base = pileupread.alignment.query_sequence[
                            pileupread.query_position
                        ]
                        if base in allele_counts:
                            allele_counts[base] += 1

        has_support = any(
            allele_counts.get(alt, 0) >= min_alt_reads
            for alt in variant.alts
        )

        if has_support:
            outvcf.write(variant)

    vcf.close()
    samfile.close()
    outvcf.close()
```

## Sequence Extraction

### Extracting Sequences Around Variants

```python
def extract_variant_contexts(vcf_file, fasta_file, output_file, window=50):
    """Extract reference sequence context around variants."""
    vcf = pysam.VariantFile(vcf_file)
    fasta = pysam.FastaFile(fasta_file)

    with open(output_file, 'w') as out:
        for variant in vcf:
            start = max(0, variant.pos - window - 1)
            end = variant.pos + window

            context = fasta.fetch(variant.chrom, start, end)

            var_pos_in_context = variant.pos - 1 - start

            out.write(f">{variant.chrom}:{variant.pos} {variant.ref}>{variant.alts}\n")
            out.write(context[:var_pos_in_context].lower())
            out.write(context[var_pos_in_context:var_pos_in_context+len(variant.ref)].upper())
            out.write(context[var_pos_in_context+len(variant.ref):].lower())
            out.write("\n")

    vcf.close()
    fasta.close()
```

### Extracting Gene Sequences

```python
def extract_gene_sequences(bed_file, fasta_file, output_fasta):
    """Extract gene sequences from BED file."""
    bed = pysam.TabixFile(bed_file)
    fasta = pysam.FastaFile(fasta_file)

    with open(output_fasta, 'w') as out:
        for gene in bed.fetch(parser=pysam.asBed()):
            sequence = fasta.fetch(gene.contig, gene.start, gene.end)

            if hasattr(gene, 'strand') and gene.strand == '-':
                complement = str.maketrans("ATGCatgcNn", "TACGtacgNn")
                sequence = sequence.translate(complement)[::-1]

            out.write(f">{gene.name} {gene.contig}:{gene.start}-{gene.end}\n")

            for i in range(0, len(sequence), 60):
                out.write(sequence[i:i+60] + "\n")

    bed.close()
    fasta.close()
```

## Read Filtering and Subset Extraction

### Filtering BAM by Region and Quality

```python
def filter_bam(input_bam, output_bam, chrom, start, end, min_mapq=20):
    """Filter BAM file by region and alignment quality."""
    infile = pysam.AlignmentFile(input_bam, "rb")
    outfile = pysam.AlignmentFile(output_bam, "wb", template=infile)

    for read in infile.fetch(chrom, start, end):
        if read.mapping_quality >= min_mapq and not read.is_duplicate:
            outfile.write(read)

    infile.close()
    outfile.close()

    pysam.index(output_bam)
```

### Extracting Reads at Specific Variants

```python
def extract_reads_at_variants(bam_file, vcf_file, output_bam, window=100):
    """Extract reads overlapping variant positions."""
    samfile = pysam.AlignmentFile(bam_file, "rb")
    vcf = pysam.VariantFile(vcf_file)
    outfile = pysam.AlignmentFile(output_bam, "wb", template=samfile)

    reads_to_keep = set()

    for variant in vcf:
        start = max(0, variant.pos - window - 1)
        end = variant.pos + window

        for read in samfile.fetch(variant.chrom, start, end):
            reads_to_keep.add(read.query_name)

    samfile.close()
    samfile = pysam.AlignmentFile(bam_file, "rb")

    for read in samfile.fetch(until_eof=True):
        if read.query_name in reads_to_keep:
            outfile.write(read)

    samfile.close()
    vcf.close()
    outfile.close()

    pysam.index(output_bam)
```

## Integrated Workflows

### Creating Coverage Track from BAM

```python
def create_coverage_bedgraph(bam_file, output_file, chrom=None):
    """Create bedGraph coverage track from BAM."""
    samfile = pysam.AlignmentFile(bam_file, "rb")

    chroms = [chrom] if chrom else samfile.references

    with open(output_file, 'w') as out:
        out.write("track type=bedGraph name=\"Coverage\"\n")

        for chrom in chroms:
            current_cov = None
            region_start = None

            for pileupcolumn in samfile.pileup(chrom):
                pos = pileupcolumn.pos
                cov = pileupcolumn.nsegments

                if cov != current_cov:
                    if current_cov is not None:
                        out.write(f"{chrom}\t{region_start}\t{pos}\t{current_cov}\n")

                    current_cov = cov
                    region_start = pos

            if current_cov is not None:
                out.write(f"{chrom}\t{region_start}\t{pos+1}\t{current_cov}\n")

    samfile.close()
```

### Merging Multiple VCF Files

```python
def merge_vcf_samples(vcf_files, output_file):
    """Merge multiple single-sample VCF files."""
    vcf_readers = [pysam.VariantFile(f) for f in vcf_files]

    merged_header = vcf_readers[0].header.copy()
    for vcf in vcf_readers[1:]:
        for sample in vcf.header.samples:
            merged_header.samples.add(sample)

    outvcf = pysam.VariantFile(output_file, "w", header=merged_header)

    all_variants = {}
    for vcf in vcf_readers:
        for variant in vcf:
            key = (variant.chrom, variant.pos, variant.ref, variant.alts)
            if key not in all_variants:
                all_variants[key] = []
            all_variants[key].append(variant)

    for key, variants in sorted(all_variants.items()):
        merged = outvcf.new_record(
            contig=variants[0].chrom,
            start=variants[0].start,
            stop=variants[0].stop,
            alleles=variants[0].alleles
        )

        for variant in variants:
            for sample in variant.samples:
                merged.samples[sample].update(variant.samples[sample])

        outvcf.write(merged)

    for vcf in vcf_readers:
        vcf.close()
    outvcf.close()
```

## Workflow Performance Tips

1. **Use index files for all random access operations**.
2. **Parallelize region processing** when analyzing multiple independent regions.
3. **Stream data whenever possible** - avoid loading entire files into memory.
4. **Explicitly close files** to release resources.
5. **Use `until_eof=True`** for sequential processing of entire files.
6. **Batch operations on the same file** to minimize I/O.
7. **Be aware of memory consumption** in pileup operations for high-coverage regions.
8. **Use count() instead of pileup()** when only counting is needed.

## Common Integration Patterns

1. **BAM + Reference**: Verify alignments, extract aligned sequences.
2. **BAM + VCF**: Verify variants, calculate allele frequencies.
3. **VCF + BED**: Annotate variants with gene/region information.
4. **BAM + BED**: Calculate coverage statistics for specific regions.
5. **FASTA + VCF**: Extract variant context sequences.
6. **Multiple BAM files**: Compare coverage or variants across samples.
7. **BAM + FASTQ**: Extract unmapped reads for realignment.
