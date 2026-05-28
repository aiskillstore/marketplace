# Sequence Processing with Bio.Seq and Bio.SeqIO

## Overview

The `Bio.Seq` module provides `Seq` objects with specialized methods for biological sequences, while `Bio.SeqIO` provides a unified interface for reading, writing, and converting sequence files across multiple formats.

## Seq Objects

### Creating Sequences

```python
from Bio.Seq import Seq

# Create a basic sequence
my_seq = Seq("AGTACACTGGT")

# Sequences support string-like operations
print(len(my_seq))  # Length
print(my_seq[0:5])  # Slicing
```

### Core Sequence Operations

```python
# Complement and reverse complement
complement = my_seq.complement()
rev_comp = my_seq.reverse_complement()

# Transcription (DNA to RNA)
rna = my_seq.transcribe()

# Translation (to protein)
protein = my_seq.translate()

# Back transcription (RNA to DNA)
dna = rna_seq.back_transcribe()
```

### Sequence Methods

- `complement()` - Returns the complementary strand
- `reverse_complement()` - Returns the reverse complement strand
- `transcribe()` - DNA to RNA transcription
- `back_transcribe()` - RNA to DNA conversion
- `translate()` - Translate to protein sequence
- `translate(table=N)` - Use a specific genetic code table
- `translate(to_stop=True)` - Stop at the first stop codon

## Bio.SeqIO: Sequence File I/O

### Core Functions

**Bio.SeqIO.parse()**: The primary tool for reading sequence files, returning an iterator of `SeqRecord` objects.

```python
from Bio import SeqIO

# Parse a FASTA file
for record in SeqIO.parse("sequences.fasta", "fasta"):
    print(record.id)
    print(record.seq)
    print(len(record))
```

**Bio.SeqIO.read()**: Used for single-record files (validates that the file contains exactly one record).

```python
record = SeqIO.read("single.fasta", "fasta")
```

**Bio.SeqIO.write()**: Outputs SeqRecord objects to a file.

```python
# Write records to a file
count = SeqIO.write(seq_records, "output.fasta", "fasta")
print(f"Wrote {count} records")
```

**Bio.SeqIO.convert()**: Streamlined format conversion.

```python
# Convert between formats
count = SeqIO.convert("input.gbk", "genbank", "output.fasta", "fasta")
```

### Supported File Formats

Common formats include:
- **fasta** - FASTA format
- **fastq** - FASTQ format (with quality scores)
- **genbank** or **gb** - GenBank format
- **embl** - EMBL format
- **swiss** - SwissProt format
- **fasta-2line** - FASTA format with sequences on a single line
- **tab** - Simple tab-separated format

### SeqRecord Objects

The `SeqRecord` object combines sequence data with annotations:

```python
record.id          # Primary identifier
record.name        # Short name
record.description # Description line
record.seq         # Actual sequence (Seq object)
record.annotations # Dictionary of additional information
record.features    # List of SeqFeature objects
record.letter_annotations  # Per-letter annotations (e.g., quality scores)
```

### Modifying Records

```python
# Modify record attributes
record.id = "new_id"
record.description = "New description"

# Extract subsequence
sub_record = record[10:30]  # Slicing operations preserve annotations

# Modify sequence
record.seq = record.seq.reverse_complement()
```

## Handling Large Files

### Memory-Efficient Parsing

Use iterators to avoid loading the entire file into memory:

```python
# Suitable for large files
for record in SeqIO.parse("large_file.fasta", "fasta"):
    if len(record.seq) > 1000:
        print(record.id)
```

### Dictionary-Based Access

Three random access methods:

**1. Bio.SeqIO.to_dict()** - Loads all records into memory:

```python
seq_dict = SeqIO.to_dict(SeqIO.parse("sequences.fasta", "fasta"))
record = seq_dict["sequence_id"]
```

**2. Bio.SeqIO.index()** - Lazy-loading dictionary (memory-efficient):

```python
seq_index = SeqIO.index("sequences.fasta", "fasta")
record = seq_index["sequence_id"]
seq_index.close()
```

**3. Bio.SeqIO.index_db()** - SQLite-based indexing for extremely large files:

```python
seq_index = SeqIO.index_db("index.idx", "sequences.fasta", "fasta")
record = seq_index["sequence_id"]
seq_index.close()
```

### High-Performance Low-Level Parsers

For high-throughput sequencing data, use low-level parsers that return tuples instead of objects:

```python
from Bio.SeqIO.FastaIO import SimpleFastaParser

with open("sequences.fasta") as handle:
    for title, sequence in SimpleFastaParser(handle):
        # Print title and sequence length
        print(title, len(sequence))

from Bio.SeqIO.QualityIO import FastqGeneralIterator

with open("reads.fastq") as handle:
    for title, sequence, quality in FastqGeneralIterator(handle):
        print(title)
```

## Compressed Files

Bio.SeqIO handles compressed files automatically:

```python
# Supports gzip compression
for record in SeqIO.parse("sequences.fasta.gz", "fasta"):
    print(record.id)

# BGZF format for random access
from Bio import bgzf
with bgzf.open("sequences.fasta.bgz", "r") as handle:
    records = SeqIO.parse(handle, "fasta")
```

## Data Extraction Patterns

### Extracting Specific Information

```python
# Get all IDs
ids = [record.id for record in SeqIO.parse("file.fasta", "fasta")]

# Get sequences exceeding a length threshold
long_seqs = [record for record in SeqIO.parse("file.fasta", "fasta")
             if len(record.seq) > 500]

# Extract organism name from GenBank
for record in SeqIO.parse("file.gbk", "genbank"):
    organism = record.annotations.get("organism", "Unknown")
    print(f"{record.id}: {organism}")
```

### Filtering and Writing

```python
# Filter sequences by criteria
long_sequences = (record for record in SeqIO.parse("input.fasta", "fasta")
                  if len(record) > 500)
SeqIO.write(long_sequences, "filtered.fasta", "fasta")
```

## Best Practices

1. **Use iterators** when handling large files instead of loading them entirely into memory.
2. **Prefer index()** for repeated random access to large files.
3. **Use index_db()** for millions of records or multi-file scenarios.
4. **Use low-level parsers** for high-throughput data when speed is critical.
5. **Download once, reuse locally** to avoid repeated network access.
6. Explicitly **close index files** or use context managers.
7. **Validate input** before writing with `SeqIO.write()`.
8. **Use appropriate format strings** - always keep them lowercase (e.g., "fasta" instead of "FASTA").

## Common Use Cases

### Format Conversion

```python
# GenBank to FASTA
SeqIO.convert("input.gbk", "genbank", "output.fasta", "fasta")

# Multiple format conversions
for fmt in ["fasta", "genbank", "embl"]:
    SeqIO.convert("input.fasta", "fasta", f"output.{fmt}", fmt)
```

### Quality Filtering (FASTQ)

```python
from Bio import SeqIO

# Filter reads with a Phred quality score of at least 20
good_reads = (record for record in SeqIO.parse("reads.fastq", "fastq")
              if min(record.letter_annotations["phred_quality"]) >= 20)
count = SeqIO.write(good_reads, "filtered.fastq", "fastq")
```

### Sequence Statistics

```python
from Bio.SeqUtils import gc_fraction

for record in SeqIO.parse("sequences.fasta", "fasta"):
    gc = gc_fraction(record.seq)
    print(f"{record.id}: GC={gc:.2%}, Length={len(record)}")
```

### Creating Records Programmatically

```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Create a new record
new_record = SeqRecord(
    Seq("ATGCGATCGATCG"),
    id="seq001",
    name="MySequence",
    description="Test sequence"
)

# Write to file
SeqIO.write([new_record], "new.fasta", "fasta")
```