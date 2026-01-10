# SRAgent Metadata Fields Reference

## Overview

This document lists all metadata fields that SRAgent can extract from SRA/GEO databases.

## Accession-Level Fields

### Study Level (SRP / PRJNA)
```yaml
sra_study:        SRP######     # SRA study accession
bioproject:       PRJNA######   # BioProject accession  
study_title:      "..."         # Study title
study_abstract:   "..."         # Study abstract/description
experiments:      "SRX1,SRX2"   # Comma-separated experiment list
```

### Experiment Level (SRX / ERX)
```yaml
experiment:       SRX#######    # Experiment accession
sra_study:        SRP######     # Parent study
biosample:        SAMN########  # BioSample accession
library_name:     "1" or "Sample1"  # Library identifier
```

### Run Level (SRR / ERR)
```yaml
acc:              SRR#######    # Run accession (individual file)
experiment:       SRX#######    # Parent experiment
total_spots:      123456789     # Total number of reads
total_bases:      12345678900   # Total bases sequenced
size_MB:          1234          # File size in megabytes
```

## Library Information

### Library Strategy
```yaml
librarystrategy:
  - "RNA-Seq"              # Transcriptome sequencing
  - "WGS"                  # Whole genome sequencing
  - "WXS"                  # Whole exome sequencing
  - "ChIP-Seq"             # Chromatin immunoprecipitation
  - "ATAC-seq"             # Chromatin accessibility
  - "Bisulfite-Seq"        # DNA methylation
  - "DNase-Hypersensitivity"
  - "OTHER"
```

### Library Source
```yaml
librarysource:
  - "TRANSCRIPTOMIC"       # RNA from cells
  - "GENOMIC"              # DNA
  - "METAGENOMIC"          # Mixed community DNA
  - "METATRANSCRIPTOMIC"   # Mixed community RNA
  - "SYNTHETIC"
  - "VIRAL RNA"
  - "OTHER"
```

### Library Selection
```yaml
libraryselection:
  - "cDNA"                 # Reverse transcribed RNA
  - "RANDOM"               # Random priming
  - "PCR"                  # PCR amplified
  - "PolyA"                # Poly-A selected (mRNA)
  - "RANDOM PCR"
  - "Oligo-dT"             # Oligo-dT priming
  - "Inverse rRNA"         # Ribosomal RNA depletion
  - "size fractionation"
  - "OTHER"
```

### Library Layout
```yaml
librarylayout:
  - "SINGLE"               # Single-end reads
  - "PAIRED"               # Paired-end reads
  
# Additional paired-end info:
nominal_length:   300      # Insert size (bp)
nominal_sdev:     50       # Standard deviation
```

### Library Construction
```yaml
library_construction_protocol:
  "Detailed protocol description..."
  
# Examples:
  - "10x Genomics Chromium Single Cell 3' v3"
  - "Smart-seq2 protocol"
  - "Standard Illumina TruSeq RNA library prep"
```

## Platform & Instrument

### Platform
```yaml
platform:
  - "ILLUMINA"
  - "OXFORD_NANOPORE"
  - "PACBIO_SMRT"
  - "ION_TORRENT"
  - "BGISEQ"
  - "LS454"                # Legacy
```

### Instrument Models (Illumina)
```yaml
instrument:
  # Current platforms
  - "Illumina NovaSeq X"
  - "Illumina NovaSeq 6000"
  - "Illumina NextSeq 2000"
  - "Illumina NextSeq 1000"
  - "Illumina MiSeq"
  
  # Older platforms
  - "Illumina HiSeq 4000"
  - "Illumina HiSeq 2500"
  - "Illumina HiSeq 2000"
  - "NextSeq 500"
  - "NextSeq 550"
  
  # Very old
  - "Illumina Genome Analyzer II"
```

### Instrument Models (PacBio)
```yaml
instrument:
  - "PacBio Sequel II"
  - "PacBio Sequel IIe"
  - "PacBio Revio"
  - "PacBio Sequel"        # Older
  - "PacBio RS II"         # Legacy
```

### Instrument Models (ONT)
```yaml
instrument:
  - "PromethION"
  - "GridION"
  - "MinION"
  - "Flongle"
```

## Biological Sample Information

### Organism
```yaml
organism:                "Homo sapiens"
scientific_name:         "Homo sapiens"
taxon_id:                9606            # NCBI Taxonomy ID
common_name:             "human"

# Common organisms
  - Homo sapiens (9606)
  - Mus musculus (10090)
  - Rattus norvegicus (10116)
  - Danio rerio (7955)
  - Drosophila melanogaster (7227)
  - Caenorhabditis elegans (6239)
```

### Sample Attributes (variable)
```yaml
# These vary by study but common ones include:
tissue:                  "brain"
cell_type:               "neuron"
developmental_stage:     "adult"
age:                     "8 weeks"
sex:                     "female"
disease_state:           "healthy" or "diseased"
treatment:               "control" or "drug_name"
cell_line:               "HEK293"
source_name:             "peripheral blood"
biomaterial_provider:    "..."
```

## Single-Cell Specific Fields

### Library Prep Technology
```yaml
lib_prep:
  - "10x_Genomics"
  - "Smart-seq2"
  - "Smart-seq3"
  - "Drop-seq"
  - "inDrop"
  - "Seq-Well"
  - "CEL-Seq2"
  - "MARS-seq"
  - "unknown"
```

### 10X Genomics Specifics
```yaml
tenx_chemistry:
  - "Single Cell 3' v1"
  - "Single Cell 3' v2"
  - "Single Cell 3' v3"
  - "Single Cell 3' v3.1"
  - "Single Cell 3' v4"
  - "Single Cell 5'"
  - "Single Cell ATAC"
  - "Multiome"
  - "Visium"
  - "Fixed RNA Profiling"
```

### Cell Type
```yaml
single_cell_type:
  - "single cell"          # Dissociated cells
  - "single nucleus"       # Isolated nuclei
  - "spatial"              # Spatial transcriptomics
```

## Data Quality Metrics

### Read Statistics
```yaml
# From BigQuery
mbases:                  12345.6         # Megabases sequenced
avgspotlen:              150             # Average read length (bp)
total_spots:             123456789       # Total reads
total_bases:             12345678900     # Total bases

# Paired-end specific
insertsize:              300             # Mean insert size (bp)
```

### Data Availability
```yaml
# From sra-stat (when available)
read_count:              100000000
base_count:              15000000000
spot_count:              100000000
```

## Publication Links

### PubMed Information
```yaml
pubmed_id:               "31234567"
pmid:                    31234567        # Numeric format
pubmed_title:            "..."
pubmed_abstract:         "..."
publication_date:        "2020-05-15"
journal:                 "Nature"
authors:                 "Smith J, ..."
```

### DOI Information
```yaml
doi:                     "10.1038/s41586-020-1234-5"
doi_type:
  - "journal"            # Peer-reviewed publication
  - "preprint"           # bioRxiv, medRxiv, arXiv
  
preprint_server:
  - "biorxiv"
  - "medrxiv"
  - "arxiv"
```

## SRAgent-Generated Fields

### Classification Fields
```yaml
is_illumina:
  - "yes" / "no" / "unknown"

is_single_cell:
  - "yes" / "no" / "unknown"

is_paired_end:
  - "yes" / "no" / "unknown"

lib_prep:
  - "10x_Genomics"
  - "Smart-seq2"
  - "Drop-seq"
  - etc.
```

### Download Status (from papers agent)
```yaml
download_status:
  - "success"            # PDF downloaded
  - "failed"             # Download failed
  - "skipped"            # No DOI found
  - "not_found"          # DOI found but no open access

download_path:           "/path/to/file.pdf"
download_source:
  - "bioRxiv"
  - "CORE"
  - "Europe PMC"
  - "Unpaywall"
```

## BigQuery-Specific Output

### Study Metadata (get_study_metadata)
```json
{
  "sra_study": "SRP167700",
  "bioproject": "PRJNA498286",
  "experiments": "SRX4967527,SRX4967528,SRX4967529"
}
```

### Experiment Metadata (get_experiment_metadata)
```json
{
  "experiment": "SRX4967527",
  "sra_study": "SRP167700",
  "library_name": "1",
  "librarylayout": "PAIRED",
  "libraryselection": "cDNA",
  "librarysource": "TRANSCRIPTOMIC",
  "platform": "ILLUMINA",
  "instrument": "Illumina NovaSeq 6000",
  "acc": "SRR8124405,SRR8124406"
}
```

### Run Metadata (get_run_metadata)
```json
{
  "acc": "SRR8124405",
  "experiment": "SRX4967527",
  "biosample": "SAMN10123456",
  "organism": "Homo sapiens",
  "assay_type": "RNA-Seq",
  "mbases": 12345.6,
  "avgspotlen": 150,
  "insertsize": 300
}
```

## Entrez XML Fields

### Common XML Paths
```xml
<!-- Study information -->
<STUDY>
  <DESCRIPTOR>
    <STUDY_TITLE>...</STUDY_TITLE>
    <STUDY_ABSTRACT>...</STUDY_ABSTRACT>
  </DESCRIPTOR>
</STUDY>

<!-- Experiment information -->
<EXPERIMENT>
  <DESIGN>
    <LIBRARY_DESCRIPTOR>
      <LIBRARY_STRATEGY>RNA-Seq</LIBRARY_STRATEGY>
      <LIBRARY_SOURCE>TRANSCRIPTOMIC</LIBRARY_SOURCE>
      <LIBRARY_SELECTION>cDNA</LIBRARY_SELECTION>
      <LIBRARY_LAYOUT>
        <PAIRED NOMINAL_LENGTH="300" NOMINAL_SDEV="50"/>
      </LIBRARY_LAYOUT>
    </LIBRARY_DESCRIPTOR>
  </DESIGN>
  <PLATFORM>
    <ILLUMINA>
      <INSTRUMENT_MODEL>Illumina NovaSeq 6000</INSTRUMENT_MODEL>
    </ILLUMINA>
  </PLATFORM>
</EXPERIMENT>

<!-- Sample information -->
<SAMPLE>
  <SAMPLE_NAME>
    <SCIENTIFIC_NAME>Homo sapiens</SCIENTIFIC_NAME>
  </SAMPLE_NAME>
  <SAMPLE_ATTRIBUTES>
    <SAMPLE_ATTRIBUTE>
      <TAG>tissue</TAG>
      <VALUE>brain</VALUE>
    </SAMPLE_ATTRIBUTE>
  </SAMPLE_ATTRIBUTES>
</SAMPLE>
```

## Field Availability by Source

| Field | Entrez | BigQuery | Web Scraping | sra-stat |
|-------|--------|----------|--------------|----------|
| Accessions | ✅ | ✅ | ✅ | ❌ |
| Platform | ✅ | ✅ | ✅ | ❌ |
| Library layout | ✅ | ✅ | ✅ | ❌ |
| Organism | ✅ | ✅ | ✅ | ❌ |
| Read counts | ⚠️  | ✅ | ❌ | ✅ |
| Sample attrs | ✅ | ❌ | ⚠️ | ❌ |
| Protocols | ✅ | ❌ | ⚠️ | ❌ |
| Publications | ✅ | ❌ | ✅ | ❌ |
| File sizes | ⚠️ | ✅ | ❌ | ✅ |

Legend:
- ✅ Fully available
- ⚠️ Partially available
- ❌ Not available

## Query Field Examples

### Technology Identification Query
```bash
SRAgent sragent "For SRX4967527, tell me: lib_prep, tenx_chemistry, is_single_cell"
```

Returns:
```json
{
  "srx_accession": "SRX4967527",
  "lib_prep": "10x_Genomics",
  "tenx_chemistry": "Single Cell 3' v3",
  "is_single_cell": "yes"
}
```

### Platform Verification Query
```bash
SRAgent sragent "For SRX4967527: platform, instrument, is_paired_end"
```

Returns:
```json
{
  "platform": "ILLUMINA",
  "instrument": "Illumina NovaSeq 6000",
  "is_paired_end": "yes"
}
```

### Biological Sample Query
```bash
SRAgent sragent "For SRX4967527: organism, tissue, cell_type"
```

Returns:
```json
{
  "organism": "Homo sapiens",
  "tissue": "brain",
  "cell_type": "mixed"
}
```

## Tips for Extracting Metadata

1. **Start broad, then specific:**
   ```bash
   # First: Get basic info
   SRAgent entrez "Summarize SRX4967527"
   
   # Then: Get specific details
   SRAgent sragent "Which 10X chemistry for SRX4967527?"
   ```

2. **Use appropriate command:**
   - Simple fields (accession, platform) → `entrez`
   - Complex fields (technology, cell type) → `sragent`

3. **Check multiple sources:**
   - Entrez has most metadata
   - BigQuery has aggregated stats
   - Web scraping fills gaps
   - sra-stat validates actual files

4. **Parse structured output:**
   ```python
   # SRAgent often returns JSON
   import json
   result = json.loads(output)
   organism = result.get("organism", "unknown")
   ```

5. **Handle missing data:**
   - Not all fields available for all accessions
   - Older datasets may lack detailed metadata
   - Single-cell detection requires multiple signals