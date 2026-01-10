# SRAgent Quick Reference

## Accession Format Patterns

### GEO (Gene Expression Omnibus)
```
GSE######  - Series (study-level)
           Example: GSE121737
           
GSM######  - Sample (individual sample)
           Example: GSM3457845
           
GPL####    - Platform (sequencing platform)
           Example: GPL24676
```

### SRA (Sequence Read Archive)
```
SRP######  - Study (project-level)
           Example: SRP167700
           
SRX#######  - Experiment (library/sample)
            Example: SRX4967527
            
SRR#######  - Run (actual sequence file)
            Example: SRR8124405
```

### BioProject / BioSample
```
PRJNA######  - BioProject (equivalent to SRA Study)
             Example: PRJNA498286
             
PRJEB######  - ENA Project (European equivalent)
             Example: PRJEB12345
             
SAMN########  - BioSample
              Example: SAMN10123456
```

### ENA (European Nucleotide Archive)
```
ERP######  - Study
           Example: ERP012345
           
ERX#######  - Experiment (equivalent to SRX)
            Example: ERX11887200
            
ERR#######  - Run (equivalent to SRR)
            Example: ERR5678901
```

## Hierarchy Diagram

```
GEO Series (GSE######)
    ↓
    Links to
    ↓
BioProject (PRJNA######) = SRA Study (SRP######)
    ↓
    Contains
    ↓
BioSample (SAMN########) → SRA Experiment (SRX#######)
    ↓                              ↓
    Sequenced as                Links to
    ↓                              ↓
SRA Run (SRR#######)          Publications
    ↓                          (PubMed ID → DOI)
Actual FASTQ files
```

## Command Selection Guide

| Need | Use Command | Example |
|------|-------------|---------|
| Simple conversion | `SRAgent entrez` | Convert GSE to SRX |
| Quick summary | `SRAgent entrez` | Summarize dataset |
| Technology ID | `SRAgent sragent` | Which 10X chemistry? |
| Verify single-cell | `SRAgent sragent` | Is this scRNA-seq? |
| Complete metadata | `SRAgent sragent` | Full experiment details |
| Download papers | `SRAgent papers` | Get PDFs |
| Batch processing | `SRAgent papers` + CSV | Multiple datasets |

## Common Metadata Fields

### Platform Information
```
platform:
  - "Illumina HiSeq 2500"
  - "Illumina NovaSeq 6000"
  - "PacBio Sequel II"
  - "Oxford Nanopore MinION"

instrument:
  - HiSeq, NovaSeq, MiSeq, NextSeq
  - Sequel, Sequel II
  - GridION, MinION, PromethION
```

### Library Layout
```
librarylayout:
  - "single"    (single-end reads)
  - "paired"    (paired-end reads)
```

### Library Source
```
librarysource:
  - "transcriptomic"  (RNA-seq)
  - "genomic"         (DNA-seq)
  - "metagenomic"     (Microbiome)
  - "metatranscriptomic"
```

### Library Selection
```
libraryselection:
  - "cDNA"
  - "PCR"
  - "PolyA"
  - "random"
  - "RANDOM PCR"
```

## Single-Cell Technologies

### 10X Genomics Products
```
Chromium Single Cell 3' (v1, v2, v3, v3.1, v4)
Chromium Single Cell 5'
Chromium Single Cell ATAC
Chromium Single Cell Multiome (GEX + ATAC)
Visium Spatial Gene Expression
CytAssist Spatial (FFPE)
Chromium Fixed RNA Profiling (FREP)
```

### Other scRNA-seq Platforms
```
Smart-seq / Smart-seq2 / Smart-seq3
Drop-seq
inDrop
Seq-Well / Seq-Well S3
CEL-Seq / CEL-Seq2
MARS-seq
STRT-seq
Quartz-Seq / Quartz-Seq2
sci-RNA-seq
SPLiT-seq
```

### Detection Keywords
Look for these in metadata:
- "single cell", "single-cell", "scRNA-seq"
- "10x", "10X", "Chromium"
- "droplet", "microfluidic"
- Technology names from above

## Organism Format

### Common Organisms
```
Scientific Name         Common Name
------------------     --------------
Homo sapiens           Human
Mus musculus           Mouse
Rattus norvegicus      Rat
Danio rerio            Zebrafish
Drosophila melanogaster  Fruit fly
Caenorhabditis elegans   C. elegans (worm)
Saccharomyces cerevisiae Yeast
Arabidopsis thaliana     Thale cress
```

### NCBI Taxonomy ID
Sometimes given as `taxon_id: 9606` (human)

## File Formats

### Sequence Data
```
.fastq / .fq         - Raw sequence reads
.fastq.gz / .fq.gz   - Compressed FASTQ
.sra                 - SRA native format
.bam / .sam          - Aligned reads
```

### Metadata
```
.xml                 - SRA XML metadata
.json                - JSON formatted data
.csv / .tsv          - Tabular metadata
```

### Papers
```
.pdf                 - Downloaded manuscripts
.xml                 - PubMed XML records
```

## Common Query Patterns

### Pattern 1: "Is it X?"
```bash
SRAgent sragent "Is [accession] [criteria]?"

Examples:
- "Is SRX4967527 single-cell RNA-seq?"
- "Is SRX4967527 paired-end Illumina data?"
- "Is SRX4967527 from human samples?"
```

### Pattern 2: "What is X?"
```bash
SRAgent sragent "What [field] for [accession]?"

Examples:
- "What organism for SRX4967527?"
- "What 10X technology for ERX11887200?"
- "What sequencing platform for SRR8124405?"
```

### Pattern 3: "Convert A to B"
```bash
SRAgent entrez "Convert [accession] to [format]"

Examples:
- "Convert GSE121737 to SRX accessions"
- "Convert SRX4967527 to SRR accessions"
- "Convert PRJNA498286 to SRX accessions"
```

### Pattern 4: "Summarize"
```bash
SRAgent entrez "Summarize [accession]"
# or
SRAgent sragent "Summarize [accession]"

Examples:
- "Summarize SRX4967527"
- "Summarize study PRJNA498286"
```

## Environment Variables Quick Check

```bash
# Check if required variables are set
echo "ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:+SET}" 
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}"
echo "EMAIL: ${EMAIL:+SET}"
echo "NCBI_API_KEY: ${NCBI_API_KEY:+SET}"
echo "DYNACONF: ${DYNACONF:-prod}"

# Minimum required (choose one):
# - ANTHROPIC_API_KEY or OPENAI_API_KEY
# Highly recommended:
# - EMAIL
```

## Output Parsing Tips

### JSON Detection
```python
import json
import re

def extract_json(text: str):
    """Extract first JSON object from text"""
    # Look for {...} pattern
    match = re.search(r'\{[^}]+\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return None
```

### Accession Extraction
```python
import re

def extract_accessions(text: str, acc_type: str = "SRX"):
    """Extract accessions from text"""
    patterns = {
        "GSE": r'GSE\d{5,7}',
        "SRP": r'SRP\d{6}',
        "PRJNA": r'PRJNA\d{6}',
        "SRX": r'SRX\d{7,8}',
        "ERX": r'ERX\d{7,8}',
        "SRR": r'SRR\d{7,8}',
    }
    pattern = patterns.get(acc_type, patterns["SRX"])
    return re.findall(pattern, text)
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| No API key | Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` |
| Email error | Set `EMAIL` environment variable |
| Rate limited | Set `NCBI_API_KEY` or reduce concurrency |
| BigQuery error | Optional - skip or set up GCP credentials |
| Paper not found | Normal - not all datasets have papers |
| Download failed | Paper may be paywalled (no open access) |
| Wrong accession | Check format (GSE vs SRP vs SRX vs SRR) |

## Performance Benchmarks

| Operation | Time (approx) | Notes |
|-----------|---------------|-------|
| Entrez query | 1-2 sec | Per accession |
| BigQuery batch | 3-5 sec | Per 100 accessions |
| Metadata extraction | 2-5 sec | Depends on complexity |
| Paper download | 5-15 sec | Per paper, varies by source |
| CSV batch (10 items) | 30-60 sec | With --max-concurrency=5 |

## Batch Processing Guidelines

```bash
# Small batch (< 10 items)
SRAgent papers accessions.csv --max-concurrency 5

# Medium batch (10-50 items)  
SRAgent papers accessions.csv --max-concurrency 3

# Large batch (> 50 items)
SRAgent papers accessions.csv --max-concurrency 2

# Be respectful of NCBI rate limits
# Use NCBI_API_KEY for better limits
```

## Quick Troubleshooting

```bash
# 1. Check SRAgent is installed
which SRAgent

# 2. Check environment
env | grep -E "API_KEY|EMAIL|DYNACONF"

# 3. Test simple query
SRAgent entrez "Convert GSE121737 to SRX accessions"

# 4. Check settings
python -c "from SRAgent.agents.utils import load_settings; print(load_settings()['models']['default'])"

# 5. Verify .env file
cat .env
```

## Success Criteria

Query was successful if:
- ✅ SRAgent returns structured data (JSON, table, list)
- ✅ No error messages about missing API keys
- ✅ Accessions are in correct format
- ✅ Paper downloads report success/failure status
- ✅ Metadata includes expected fields

Query needs retry if:
- ❌ "API key not found" errors
- ❌ "Email parameter not set" 
- ❌ Timeout errors (increase --recursion-limit)
- ❌ Rate limit errors (reduce concurrency)