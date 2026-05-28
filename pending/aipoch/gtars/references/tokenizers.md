# Genomic Tokenizers

Tokenizers convert genomic regions into discrete tokens for use in machine learning applications, particularly for training genomic deep learning models.

## Python API

### Creating a Tokenizer

Tokenizer configurations can be loaded from various sources:

```python
import gtars

# Load from a BED file
tokenizer = gtars.tokenizers.TreeTokenizer.from_bed_file("regions.bed")

# Load from a configuration file
tokenizer = gtars.tokenizers.TreeTokenizer.from_config("tokenizer_config.yaml")

# Load from a region string
tokenizer = gtars.tokenizers.TreeTokenizer.from_region_string("chr1:1000-2000")
```

### Tokenizing Genomic Regions

Convert genomic coordinates into tokens:

```python
# Tokenize a single region
token = tokenizer.tokenize("chr1", 1000, 2000)

# Tokenize multiple regions
tokens = []
for chrom, start, end in regions:
    token = tokenizer.tokenize(chrom, start, end)
    tokens.append(token)
```

### Token Properties

Access token information:

```python
# Get Token ID
token_id = token.id

# Get genomic coordinates
chrom = token.chromosome
start = token.start
end = token.end

# Get token metadata
metadata = token.metadata
```

## Use Cases

### Machine Learning Preprocessing

Tokenizers are essential for preparing genomic data for machine learning models:

1. **Sequence Modeling**: Convert genomic intervals into discrete tokens for use in Transformer models.
2. **Positional Encoding**: Create consistent positional encodings across different datasets.
3. **Data Augmentation**: Generate alternative tokenization schemes for training.

### Integration with geniml

The tokenizer module integrates seamlessly with the geniml library for genomic machine learning:

```python
# Tokenize regions for geniml
from gtars.tokenizers import TreeTokenizer
import geniml

tokenizer = TreeTokenizer.from_bed_file("training_regions.bed")
tokens = [tokenizer.tokenize(r.chrom, r.start, r.end) for r in regions]

# Use tokens in a geniml model
model = geniml.Model(vocab_size=tokenizer.vocab_size)
```

## Configuration Format

Tokenizer configuration files support YAML format:

```yaml
# tokenizer_config.yaml
type: tree
resolution: 1000  # Token resolution (in base pairs)
chromosomes:
  - chr1
  - chr2
  - chr3
options:
  overlap_handling: merge
  gap_threshold: 100
```

## Performance Considerations

- `TreeTokenizer` uses efficient data structures for fast tokenization.
- For large datasets, batch tokenization is recommended.
- Pre-loading the tokenizer reduces overhead from repeated operations.