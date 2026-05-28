# KEGG Database Reference Guide

## Overview

KEGG (Kyoto Encyclopedia of Genes and Genomes) is a comprehensive bioinformatics resource that maintains manually curated pathway maps and molecular interaction networks. It provides "molecular wiring diagrams of interaction, reaction and relation networks" for understanding biological systems.

**Base URL**: https://rest.kegg.jp
**Official Documentation**: https://www.kegg.jp/kegg/rest/keggapi.html
**Access Restrictions**: The KEGG API is provided for academic use by academic users only.

## KEGG Databases

KEGG integrates 16 main databases categorized into four groups: Systems Information, Genomic Information, Chemical Information, and Health Information:

### Systems Information
- **PATHWAY**: Manually drawn pathway maps covering metabolism, genetic information processing, environmental information processing, cellular processes, organismal systems, human diseases, and drug development
- **MODULE**: Functional units and building blocks of pathways
- **BRITE**: Hierarchical classifications and ontologies

### Genomic Information
- **GENOME**: Complete genomes with annotations
- **GENES**: Catalog of genes from all organisms
- **ORTHOLOGY**: Ortholog groups (KO: KEGG Orthology)
- **SSDB**: Sequence Similarity Database

### Chemical Information
- **COMPOUND**: Metabolites and other chemical substances
- **GLYCAN**: Glycan structures
- **REACTION**: Chemical reactions
- **RCLASS**: Reaction classes (chemical structure transformation patterns)
- **ENZYME**: Enzyme nomenclature
- **NETWORK**: Network variants

### Health Information
- **DISEASE**: Human diseases including genetic and environmental factors
- **DRUG**: Approved drugs with chemical structures and target information
- **DGROUP**: Drug groups

### External Database Links
KEGG maintains cross-references with the following external databases:
- **PubMed**: Literature citations
- **NCBI Gene**: Gene database
- **UniProt**: Protein sequences
- **PubChem**: Chemical compounds
- **ChEBI**: Chemical Entities of Biological Interest

## REST API Operations

### 1. INFO - Database Metadata

**Syntax**: `/info/<database>`

Retrieves release information and statistics for a database.

**Examples**:
- `/info/kegg` - KEGG system information
- `/info/pathway` - Pathway database information
- `/info/hsa` - Human species information

### 2. LIST - Entry List

**Syntax**: `/list/<database>[/<organism>]`

Lists entry identifiers and associated names.

**Parameters**:
- `database` - Database name (pathway, enzyme, genes, etc.) or entry (hsa:10458)
- `organism` - Optional organism code (e.g., hsa for human, eco for E. coli)

**Examples**:
- `/list/pathway` - All reference pathways
- `/list/pathway/hsa` - Human-specific pathways
- `/list/hsa:10458+ece:Z5100` - Specific gene entries (up to 10)

**Organism Codes**: Three or four-letter codes
- `hsa` - Homo sapiens (human)
- `mmu` - Mus musculus (mouse)
- `dme` - Drosophila melanogaster (fruit fly)
- `sce` - Saccharomyces cerevisiae (yeast)
- `eco` - Escherichia coli K-12 MG1655

### 3. FIND - Search Entries

**Syntax**: `/find/<database>/<query>[/<option>]`

Searches for entries by keywords or molecular properties.

**Parameters**:
- `database` - Database to search
- `query` - Search term or molecular property
- `option` - Optional: `formula` (molecular formula), `exact_mass` (exact mass), `mol_weight` (molecular weight)

**Search Fields** (depending on database):
- ENTRY, NAME, SYMBOL, GENE_NAME, DESCRIPTION, DEFINITION
- ORGANISM, TAXONOMY, ORTHOLOGY, PATHWAY, etc.

**Examples**:
- `/find/genes/shiga toxin` - Keyword search in genes
- `/find/compound/C7H10N4O2/formula` - Exact match for molecular formula
- `/find/drug/300-310/exact_mass` - Mass range search (300-310 Da)
- `/find/compound/300-310/mol_weight` - Molecular weight range search

### 4. GET - Retrieve Entries

**Syntax**: `/get/<entry>[+<entry>...][/<option>]`

Retrieves full database entries or specific data formats.

**Parameters**:
- `entry` - Entry ID (up to 10, joined by +)
- `option` - Output format (optional)

**Output Options**:
- `aaseq` - Amino acid sequence (FASTA)
- `ntseq` - Nucleotide sequence (FASTA)
- `mol` - MOL format (compounds/drugs)
- `kcf` - KCF format (KEGG Chemical Function, compounds/drugs)
- `image` - PNG image (pathway maps only, single entry)
- `kgml` - KGML XML (pathway structure only, single entry)
- `json` - JSON format (pathways only, single entry)

**Examples**:
- `/get/hsa00010` - Glycolysis pathway (human)
- `/get/hsa:10458+ece:Z5100` - Multiple genes (up to 10)
- `/get/hsa:10458/aaseq` - Protein sequence
- `/get/cpd:C00002` - ATP compound entry
- `/get/hsa05130/json` - Cancer pathway in JSON format
- `/get/hsa05130/image` - Pathway map in PNG format

**Image Restriction**: Only one entry is allowed when using the image option.

### 5. CONV - ID Conversion

**Syntax**: `/conv/<target_db>/<source_db>`

Converts identifiers between KEGG and external databases.

**Supported Conversions**:
- `ncbi-geneid` ↔ KEGG genes
- `ncbi-proteinid` ↔ KEGG genes
- `uniprot` ↔ KEGG genes
- `pubchem` ↔ KEGG compounds/drugs
- `chebi` ↔ KEGG compounds/drugs

**Examples**:
- `/conv/ncbi-geneid/hsa` - Convert all human genes to NCBI Gene IDs
- `/conv/hsa/ncbi-geneid` - Convert NCBI Gene IDs to human genes (reverse)
- `/conv/uniprot/hsa:10458` - Convert specific gene to UniProt
- `/conv/pubchem/compound` - Convert all compounds to PubChem IDs

### 6. LINK - Cross-references

**Syntax**: `/link/<target_db>/<source_db>`

Finds related entries within or between KEGG databases.

**Common Links**:
- genes ↔ pathway
- pathway ↔ compound
- pathway ↔ enzyme
- genes ↔ orthology (KO)
- compound ↔ reaction

**Examples**:
- `/link/pathway/hsa` - All pathways associated with human genes
- `/link/genes/hsa00010` - Genes in the glycolysis pathway
- `/link/pathway/hsa:10458` - Pathways containing a specific gene
- `/link/compound/hsa00010` - Compounds in a pathway

### 7. DDI - Drug-Drug Interactions

**Syntax**: `/ddi/<drug>[+<drug>...]`

Retrieves drug-drug interaction information extracted from Japanese drug labels.

**Parameters**:
- `drug` - Drug entry ID (up to 10, joined by +)

**Examples**:
- `/ddi/D00001` - Interactions for a single drug
- `/ddi/D00001+D00002` - Interactions between multiple drugs

## Pathway Categories

KEGG organizes pathways into seven broad categories:

### 1. Metabolism
Carbohydrate, energy, lipid, nucleotide, amino acid, glycan biosynthesis and metabolism, metabolism of cofactors and vitamins, metabolism of terpenoids and polyketides, biosynthesis of secondary metabolites, xenobiotics biodegradation

**Pathway Examples**:
- `map00010` - Glycolysis / Gluconeogenesis
- `map00020` - Citrate cycle (TCA cycle)
- `map00190` - Oxidative phosphorylation

### 2. Genetic Information Processing
Transcription, translation, folding/sorting/degradation, replication and repair

**Pathway Examples**:
- `map03010` - Ribosome
- `map03020` - RNA polymerase
- `map03040` - Spliceosome

### 3. Environmental Information Processing
Membrane transport, signal transduction

**Pathway Examples**:
- `map02010` - ABC transporters
- `map04010` - MAPK signaling pathway

### 4. Cellular Processes
Transport and catabolism, cell growth and death, cellular community, cell motility

**Pathway Examples**:
- `map04140` - Autophagy
- `map04210` - Apoptosis

### 5. Organismal Systems
Immune, endocrine, circulatory, digestive, nervous, sensory, development, environmental adaptation

**Pathway Examples**:
- `map04610` - Complement and coagulation cascades
- `map04910` - Insulin signaling pathway

### 6. Human Diseases
Cancer, immune diseases, neurodegenerative diseases, cardiovascular diseases, metabolic diseases, infectious diseases

**Pathway Examples**:
- `map05200` - Pathways in cancer
- `map05010` - Alzheimer disease

### 7. Drug Development
Chronological classification and target-based classification

## Common Identifiers and Naming

### Pathway IDs
- `map#####` - Reference pathway (generic)
- `hsa#####` - Human-specific pathway
- `mmu#####` - Mouse-specific pathway
- Format: Organism code + 5 digits

### Gene IDs
- `hsa:10458` - Human gene (organism:gene_id)
- Format: Organism code + colon + gene number

### Compound IDs
- `cpd:C00002` - ATP
- Format: cpd:C#####

### Drug IDs
- `dr:D00001` - Drug entry
- Format: dr:D#####

### Enzyme IDs
- `ec:1.1.1.1` - Alcohol dehydrogenase
- Format: ec:EC number

### KO (KEGG Orthology) ID
- `ko:K00001` - Ortholog group
- Format: ko:K#####

## API Limits & Best Practices

### Frequency Limits and Regulations
- Maximum 10 entries per operation (except image/kgml: 1 entry only)
- Academic use only—commercial use requires a separate license
- While frequency limits are not explicitly documented, high-frequency concurrent requests should be avoided

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (query syntax error)
- `404` - Not Found (entry or database does not exist)

### Best Practices
1. Always check the HTTP status code in the response.
2. For batch operations, use + to group entries (up to 10).
3. Cache results locally to reduce API calls.
4. Use specific organism codes whenever possible for faster queries.
5. For pathway visualization, use the web interface or KGML/JSON formats.
6. Parse tab-separated output carefully (format is consistent across operations).

## Integration with Other Tools

### Biopython Integration
Biopython provides the `Bio.KEGG.REST` module for easy Python integration:
```python
from Bio.KEGG import REST
# Read pathway list
result = REST.kegg_list("pathway").read()
```

### KEGGREST (R/Bioconductor)
R users can use the KEGGREST package:
```r
library(KEGGREST)
pathways <- keggList("pathway")
```

## Common Analysis Workflows

### Workflow 1: Gene to Pathway Mapping
1. Obtain gene IDs from your study organism.
2. Use `/link/pathway/<gene_id>` to find associated pathways.
3. Use `/get/<pathway_id>` to retrieve detailed pathway information.

### Workflow 2: Pathway Enrichment Analysis Background
1. Use `/list/pathway/<org>` to get all pathways for the organism.
2. Use `/link/genes/<pathway_id>` to get genes in each pathway.
3. Perform statistical enrichment analysis.

### Workflow 3: Compound to Reaction Mapping
1. Use `/find/compound/<name>` to find compound IDs.
2. Use `/link/reaction/<compound_id>` to find related reactions.
3. Use `/link/pathway/<reaction_id>` to find pathways containing these reactions.

### Workflow 4: ID Conversion for Integration
1. Use `/conv/uniprot/<org>` to map KEGG genes to UniProt.
2. Use `/conv/ncbi-geneid/<org>` to map to NCBI Gene IDs.
3. Use converted IDs for integration with other databases.

## Additional Resources

- **KEGG Mapper**: https://www.kegg.jp/kegg/mapper/ - Interactive pathway mapping
- **BlastKOALA**: Automatic annotation tool for sequenced genomes
- **GhostKOALA**: Annotation tool for metagenomes and metatranscriptomes
- **KEGG Modules**: https://www.kegg.jp/kegg/module.html
- **KEGG Brite**: https://www.kegg.jp/kegg/brite.html