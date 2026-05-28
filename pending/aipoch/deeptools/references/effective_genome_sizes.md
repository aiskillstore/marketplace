# Effective Genome Sizes

## Definition

Effective genome size refers to the length of the genome that is "mappable"—that is, the regions where sequencing reads can be uniquely mapped. This metric is crucial for proper normalization in many deepTools commands.

## Why It Matters

- Essential parameter for RPGC normalization (--normalizeUsing RPGC)
- Affects accuracy of coverage calculations
- Must match your data processing methods (filtered reads vs. unfiltered reads)

## Calculation Methods

1. **Non-N Base Method**：Count the number of non-N nucleotides in the genome sequence
2. **Unique Mappability Method**：Regions where sequences of a specific length can be uniquely mapped (may consider edit distance)

## Common Species Values

### Using Non-N Base Method

| Species      | Assembly Version | Effective Size | Full Command Parameter             |
| ------------ | ---------------- | -------------- | ---------------------------------- |
| Human        | GRCh38/hg38      | 2,913,022,398  | `--effectiveGenomeSize 2913022398` |
| Human        | GRCh37/hg19      | 2,864,785,220  | `--effectiveGenomeSize 2864785220` |
| Mouse        | GRCm39/mm39      | 2,654,621,837  | `--effectiveGenomeSize 2654621837` |
| Mouse        | GRCm38/mm10      | 2,652,783,500  | `--effectiveGenomeSize 2652783500` |
| Zebrafish    | GRCz11           | 1,368,780,147  | `--effectiveGenomeSize 1368780147` |
| *Drosophila* | dm6              | 142,573,017    | `--effectiveGenomeSize 142573017`  |
| *C. elegans* | WBcel235/ce11    | 100,286,401    | `--effectiveGenomeSize 100286401`  |
| *C. elegans* | ce10             | 100,258,171    | `--effectiveGenomeSize 100258171`  |



### Human (GRCh38) by Read Length

For quality-filtered reads, values vary by read length:

| Read Length | Effective Size |
| ----------- | -------------- |
| 50bp        | ~2.7 billion   |
| 75bp        | ~2.8 billion   |
| 100bp       | ~2.8 billion   |
| 150bp       | ~2.9 billion   |
| 250bp       | ~2.9 billion   |


### Mouse (GRCm38) by Read Length

| Read Length | Effective Size |
| ----------- | -------------- |
| 50bp        | ~2.3 billion   |
| 75bp        | ~2.5 billion   |
| 100bp       | ~2.6 billion   |


## Usage in deepTools

Effective genome size is most commonly used in the following commands:

### bamCoverage with RPGC Normalization
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398
```

### bamCompare with RPGC Normalization
```bash
bamCompare -b1 treatment.bam -b2 control.bam \
    --outFileName comparison.bw \
    --scaleFactorsMethod RPGC \
    --effectiveGenomeSize 2913022398
```

### computeGCBias / correctGCBias
```bash
computeGCBias --bamfile input.bam \
    --effectiveGenomeSize 2913022398 \
    --genome genome.2bit \
    --fragmentLength 200 \
    --biasPlot bias.png
```


## How to Choose the Right Value

**For most analyses** Use the "non-N base method" value for your selected reference genome.

**For filtered data** If you apply strict quality filtering or remove multimapping reads, consider using read-length-specific values.

**When uncertain** Use the conservative "non-N base" value—it is more broadly applicable.

## Common Abbreviations

deepTools also accepts the following shorthand values in certain contexts:

- `mm` or `GRCm38`: 2652783500
- `dm` or `dm6`: 142573017
- `ce` or `ce10`: 100286401

Please consult the documentation for your specific deepTools version to confirm supported abbreviations.

## Calculating Custom Values

For custom genomes or assembly versions, you can calculate the number of non-N bases using:

```bash
# Using faCount (UCSC utilities)
faCount genome.fa | grep "total" | awk '{print $2-$7}'

# Using seqtk
seqtk comp genome.fa | awk '{x+=$2}END{print x}'
```

## References
- For more information on the latest effective genome sizes and detailed calculation methods, please refer to:
- deepTools Official Documentation: https://deeptools.readthedocs.io/en/latest/content/feature/effectiveGenomeSize.html
ENCODE Documentation for reference genome details