# Reference Sequence Management

The `refget` module is responsible for the retrieval and digest calculation of reference sequences, following the refget protocol for sequence identification.

## RefgetStore

`RefgetStore` is used to manage reference sequences and their digests:

```python
import gtars

# Create RefgetStore
store = gtars.RefgetStore()

# Add sequence
store.add_sequence("chr1", sequence_data)

# Retrieve sequence
seq = store.get_sequence("chr1")

# Get sequence digest
digest = store.get_digest("chr1")
```

## Sequence Digests

Calculate and verify sequence digests:

```python
# Calculate sequence digest
from gtars.refget import compute_digest

digest = compute_digest(sequence_data)

# Verify if digest matches
is_valid = store.verify_digest("chr1", expected_digest)
```

## Integration with Reference Genomes

Handling standard reference genomes:

```python
# Load reference genome
store = gtars.RefgetStore.from_fasta("hg38.fa")

# Get chromosome sequences
chr1 = store.get_sequence("chr1")
chr2 = store.get_sequence("chr2")

# Get subsequence
region_seq = store.get_subsequence("chr1", 1000, 2000)
```

## Command Line Interface (CLI) Usage

Manage reference sequences from the command line:

```bash
# Calculate digests for FASTA file
gtars refget digest --input genome.fa --output digests.txt

# Verify sequence digest
gtars refget verify --sequence sequence.fa --digest expected_digest
```

## Refget Protocol Compliance

The `refget` module follows the GA4GH refget protocol:

### Digest Calculation

Digests are calculated using SHA-512 truncated to 48 bytes:

```python
# Calculate refget-compliant digest
digest = gtars.refget.compute_digest(sequence)
# Returns: "SQ.abc123..."
```

### Sequence Retrieval

Retrieve sequences by digest:

```python
# Get sequence by refget digest
seq = store.get_sequence_by_digest("SQ.abc123...")
```

## Use Cases

### Reference Sequence Validation

Verify the integrity of reference genomes:

```python
# Calculate digests for reference sequences
store = gtars.RefgetStore.from_fasta("reference.fa")
digests = {chrom: store.get_digest(chrom) for chrom in store.chromosomes}

# Compare with expected digests
for chrom, expected in expected_digests.items():
    actual = digests[chrom]
    if actual != expected:
        print(f"Mismatch for {chrom}: {actual} != {expected}")
```

### Sequence Extraction

Extract specific genomic regions:

```python
# Extract regions of interest
store = gtars.RefgetStore.from_fasta("hg38.fa")

regions = [
    ("chr1", 1000, 2000),
    ("chr2", 5000, 6000),
    ("chr3", 10000, 11000)
]

sequences = [store.get_subsequence(c, s, e) for c, s, e in regions]
```

### Cross-Reference Comparison

Compare sequences between different reference versions:

```python
# Load two reference versions
hg19 = gtars.RefgetStore.from_fasta("hg19.fa")
hg38 = gtars.RefgetStore.from_fasta("hg38.fa")

# Compare digests
for chrom in hg19.chromosomes:
    digest_19 = hg19.get_digest(chrom)
    digest_38 = hg38.get_digest(chrom)
    if digest_19 != digest_38:
        print(f"{chrom} differs between hg19 and hg38")
```

## Performance Notes

- Sequences are loaded on demand
- Calculated digests are cached
- Efficient subsequence extraction
- Support for memory-mapped files for large genomes