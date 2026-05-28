# BioServices: Complete Service Reference Manual

This document provides a comprehensive reference for all major services in BioServices, including core methods, parameters, and usage scenarios.

## Protein and Gene Resources

### UniProt

Protein sequence and functional information database.

**Initialization:**
```python
from bioservices import UniProt
u = UniProt(verbose=False)
```

**Core Methods:**

- `search(query, frmt="tab", columns=None, limit=None, sort=None, compress=False, include=False, **kwargs)`
  - Search UniProt using flexible query syntax.
  - `frmt`: "tab", "fasta", "xml", "rdf", "gff", "txt"
  - `columns`: Comma-separated list (e.g., "id,genes,organism,length")
  - Returns: String in the requested format.

- `retrieve(uniprot_id, frmt="txt")`
  - Retrieve specific UniProt entries.
  - `frmt`: "txt", "fasta", "xml", "rdf", "gff"
  - Returns: Entry data in the requested format.

- `mapping(fr="UniProtKB_AC-ID", to="KEGG", query="P43403")`
  - Convert identifiers between different databases.
  - `fr`/`to`: Database identifiers (see identifier_mapping.md)
  - `query`: Single ID or comma-separated list.
  - Returns: Dictionary mapping input IDs to output IDs.

- `searchUniProtId(pattern, columns="entry name,length,organism", limit=100)`
  - Convenient method for ID-based searches.
  - Returns: Tab-separated values (TSV).

**Common Column Names:** id, entry name, genes, organism, protein names, length, sequence, go-id, ec, pathway, interactor

**Usage Scenarios:**
- Retrieving protein sequences for BLAST.
- Querying functional annotations.
- Cross-database identifier mapping.
- Batch retrieval of protein information.

---

### KEGG (Kyoto Encyclopedia of Genes and Genomes)

Database for metabolic pathways, genes, and organisms.

**Initialization:**
```python
from bioservices import KEGG
k = KEGG()
k.organism = "hsa"  # Set default organism
```

**Core Methods:**

- `list(database)`
  - List entries in KEGG databases.
  - `database`: "organism", "pathway", "module", "disease", "drug", "compound"
  - Returns: Multi-line string containing entries.

- `find(database, query)`
  - Search databases by keywords.
  - Returns: List of matching entries and their IDs.

- `get(entry_id)`
  - Retrieve entries by ID.
  - Supports genes, pathways, compounds, etc.
  - Returns: Raw entry text.

- `parse(data)`
  - Parse KEGG entries into dictionaries.
  - Returns: Dictionary containing structured data.

- `lookfor_organism(name)`
  - Search for organisms by name pattern.
  - Returns: List of matching organism codes.

- `lookfor_pathway(name)`
  - Search for pathways by name.
  - Returns: List of pathway IDs.

- `get_pathway_by_gene(gene_id, organism)`
  - Find pathways containing a specific gene.
  - Returns: List of pathway IDs.

- `parse_kgml_pathway(pathway_id)`
  - Parse pathway KGML files for interaction information.
  - Returns: Dictionary containing "entries" and "relations".

- `pathway2sif(pathway_id)`
  - Extract Simple Interaction Format (SIF) data.
  - Filters for activation/inhibition.
  - Returns: List of interaction tuples.

**Organism Codes:**
- hsa: Homo sapiens (Human)
- mmu: Mus musculus (Mouse)
- dme: Drosophila melanogaster (Fruit fly)
- sce: Saccharomyces cerevisiae (Baker's yeast)
- eco: Escherichia coli (E. coli)

**Usage Scenarios:**
- Pathway analysis and visualization.
- Gene functional annotation.
- Metabolic network reconstruction.
- Protein-protein interaction extraction.

---

### HGNC (HUGO Gene Nomenclature Committee)

Official human gene naming body.

**Initialization:**
```python
from bioservices import HGNC
h = HGNC()
```

**Core Methods:**
- `search(query)`: Search for gene symbols/names.
- `fetch(format, query)`: Retrieve gene information.

**Usage Scenarios:**
- Standardizing human gene names.
- Querying official gene symbols.

---

### MyGeneInfo

Gene annotation and query service.

**Initialization:**
```python
from bioservices import MyGeneInfo
m = MyGeneInfo()
```

**Core Methods:**
- `querymany(ids, scopes, fields, species)`: Batch gene queries.
- `getgene(geneid)`: Get gene annotations.

**Usage Scenarios:**
- Batch retrieval of gene annotations.
- Gene ID conversion.

---

## Compound Resources

### ChEBI (Chemical Entities of Biological Interest)

Dictionary of molecular entities.

**Initialization:**
```python
from bioservices import ChEBI
c = ChEBI()
```

**Core Methods:**
- `getCompleteEntity(chebi_id)`: Get complete compound information.
- `getLiteEntity(chebi_id)`: Get basic information.
- `getCompleteEntityByList(chebi_ids)`: Batch retrieval.

**Usage Scenarios:**
- Small molecule information queries.
- Chemical structure data.
- Compound property lookups.

---

### ChEMBL

Bioactive drug-like compound database.

**Initialization:**
```python
from bioservices import ChEMBL
c = ChEMBL()
```

**Core Methods:**
- `get_molecule_form(chembl_id)`: Compound details.
- `get_target(chembl_id)`: Target information.
- `get_similarity(chembl_id)`: Get compounds similar to a specified compound.
- `get_assays()`: Bioactivity assay data.

**Usage Scenarios:**
- Drug discovery data.
- Finding similar compounds.
- Bioactivity information.
- Target-compound relationship research.

---

### UniChem

Chemical identifier mapping service.

**Initialization:**
```python
from bioservices import UniChem
u = UniChem()
```

**Core Methods:**
- `get_compound_id_from_kegg(kegg_id)`: KEGG → ChEMBL conversion.
- `get_all_compound_ids(src_compound_id, src_id)`: Get all associated IDs.
- `get_src_compound_ids(src_compound_id, from_src_id, to_src_id)`: Convert IDs.

**Source IDs:**
- 1: ChEMBL
- 2: DrugBank
- 3: PDB
- 6: KEGG
- 7: ChEBI
- 22: PubChem

**Usage Scenarios:**
- Cross-database compound ID mapping.
- Linking chemical databases.

---

### PubChem

NIH compound database.

**Initialization:**
```python
from bioservices import PubChem
p = PubChem()
```

**Core Methods:**
- `get_compounds(identifier, namespace)`: Retrieve compounds.
- `get_properties(properties, identifier, namespace)`: Get properties.

**Usage Scenarios:**
- Chemical structure retrieval.
- Compound property information.

---

## Sequence Analysis Tools

### NCBIblast

Sequence similarity search.

**Initialization:**
```python
from bioservices import NCBIblast
s = NCBIblast(verbose=False)
```

**Core Methods:**
- `run(program, sequence, stype, database, email, **params)`
  - Submit BLAST jobs.
  - `program`: "blastp", "blastn", "blastx", "tblastn", "tblastx"
  - `stype`: "protein" or "dna"
  - `database`: "uniprotkb", "pdb", "refseq_protein", etc.
  - `email`: Required by NCBI.
  - Returns: Job ID.

- `getStatus(jobid)`
  - Check job status.
  - Returns: "RUNNING", "FINISHED", "ERROR"

- `getResult(jobid, result_type)`
  - Retrieve results.
  - `result_type`: "out" (default), "ids", "xml"

**Important Note:** BLAST jobs are asynchronous. Always check the status before retrieving results.

**Usage Scenarios:**
- Protein homology search.
- Sequence similarity analysis.
- Functional annotation via homology.

---

## Pathway and Interaction Resources

### Reactome

Pathway database.

**Initialization:**
```python
from bioservices import Reactome
r = Reactome()
```

**Core Methods:**
- `get_pathway_by_id(pathway_id)`: Pathway details.
- `search_pathway(query)`: Search for pathways.

**Usage Scenarios:**
- Human pathway analysis.
- Biological process annotation.

---

### PSICQUIC

Protein interaction query service (federating 30+ databases).

**Initialization:**
```python
from bioservices import PSICQUIC
s = PSICQUIC()
```

**Core Methods:**
- `query(database, query_string)`
  - Query specific interaction databases.
  - Returns: PSI-MI TAB format.

- `activeDBs`
  - List properties of available databases.
  - Returns: List of database names.

**Available Databases:** MINT, IntAct, BioGRID, DIP, InnateDB, MatrixDB, MPIDB, UniProt, and 30+ others.

**Query Syntax:** Supports AND, OR, and organism filtering.
- Example: "ZAP70 AND species:9606"

**Usage Scenarios:**
- Discovering protein-protein interactions.
- Network analysis.
- Interactome mapping.

---

### IntactComplex

Protein complex database.

**Initialization:**
```python
from bioservices import IntactComplex
i = IntactComplex()
```

**Core Methods:**
- `search(query)`: Search for complexes.
- `details(complex_ac)`: Complex details.

**Usage Scenarios:**
- Protein complex composition analysis.
- Multi-protein assembly analysis.

---

### OmniPath

Integrated signaling pathway database.

**Initialization:**
```python
from bioservices import OmniPath
o = OmniPath()
```

**Core Methods:**
- `interactions(datasets, organisms)`: Get interactions.
- `ptms(datasets, organisms)`: Post-translational modifications.

**Usage Scenarios:**
- Cell signaling analysis.
- Regulatory network mapping.

---

## Gene Ontology

### QuickGO

Gene Ontology annotation service.

**Initialization:**
```python
from bioservices import QuickGO
g = QuickGO()
```

**Core Methods:**
- `Term(go_id, frmt="obo")`
  - Retrieve GO term information.
  - Returns: Term definitions and metadata.

- `Annotation(protein=None, goid=None, format="tsv")`
  - Get GO annotations.
  - Returns: Annotation information in the requested format.

**GO Categories:**
- Biological Process (BP)
- Molecular Function (MF)
- Cellular Component (CC)

**Usage Scenarios:**
- Functional annotation.
- Enrichment analysis.
- GO term lookup.

---

## Genomic Resources

### BioMart

Data mining tool for genomic data.

**Initialization:**
```python
from bioservices import BioMart
b = BioMart()
```

**Core Methods:**
- `datasets(dataset)`: List available datasets.
- `attributes(dataset)`: List attributes.
- `query(query_xml)`: Execute BioMart queries.

**Usage Scenarios:**
- Batch retrieval of genomic data.
- Custom genomic annotation.
- SNP information queries.

---

### ArrayExpress

Gene expression database.

**Initialization:**
```python
from bioservices import ArrayExpress
a = ArrayExpress()
```

**Core Methods:**
- `queryExperiments(keywords)`: Search for experiments.
- `retrieveExperiment(accession)`: Get experiment data.

**Usage Scenarios:**
- Gene expression data acquisition.
- Microarray analysis.
- RNA-seq data retrieval.

---

### ENA (European Nucleotide Archive)

Nucleotide sequence database.

**Initialization:**
```python
from bioservices import ENA
e = ENA()
```

**Core Methods:**
- `search_data(query)`: Search for sequences.
- `retrieve_data(accession)`: Retrieve sequences.

**Usage Scenarios:**
- Nucleotide sequence retrieval.
- Accessing genome assemblies.

---

## Structural Biology

### PDB (Protein Data Bank)

3D protein structure database.

**Initialization:**
```python
from bioservices import PDB
p = PDB()
```

**Core Methods:**
- `get_file(pdb_id, file_format)`: Download structure files.
- `search(query)`: Search for structures.

**File Formats:** pdb, cif, xml

**Usage Scenarios:**
- 3D structure retrieval.
- Analysis-based structural studies.
- PyMOL visualization.

---

### Pfam

Protein family database.

**Initialization:**
```python
from bioservices import Pfam
p = Pfam()
```

**Core Methods:**
- `searchSequence(sequence)`: Find domains within a sequence.
- `getPfamEntry(pfam_id)`: Domain information.

**Usage Scenarios:**
- Protein domain identification.
- Family classification.
- Functional motif discovery.

---

## Specialized Resources

### BioModels

Repository of systems biology models.

**Initialization:**
```python
from bioservices import BioModels
b = BioModels()
```

**Core Methods:**
- `get_model_by_id(model_id)`: Retrieve SBML models.

**Usage Scenarios:**
- Systems biology modeling.
- SBML model retrieval.

---

### COG (Clusters of Orthologous Genes)

Orthologous gene classification.

**Initialization:**
```python
from bioservices import COG
c = COG()
```

**Usage Scenarios:**
- Homology analysis.
- Functional classification.

---

### BiGG Models

Metabolic network models.

**Initialization:**
```python
from bioservices import BiGG
b = BiGG()
```

**Core Methods:**
- `list_models()`: List available models.
- `get_model(model_id)`: Model details.

**Usage Scenarios:**
- Metabolic network analysis.
- Flux Balance Analysis (FBA).

---

## General Patterns

### Error Handling

All services may throw exceptions. It is recommended to wrap calls in try-except blocks:

```python
try:
    result = service.method(params)
    if result:
        # Process result
        pass
except Exception as e:
    print(f"Error: {e}")
```

### Logging Verbosity Control

Most services support the `verbose` parameter:
```python
service = Service(verbose=False)  # Suppress HTTP logs
```

### Rate Limiting

Services have timeouts and frequency limits:
```python
service.TIMEOUT = 30  # Adjust timeout
service.DELAY = 1     # Delay between requests (if supported)
```

### Output Formats

Common format parameters:
- `frmt`: "xml", "json", "tab", "txt", "fasta"
- `format`: Service-specific variants

### Caching

Some services cache results:
```python
service.CACHE = True  # Enable caching
service.clear_cache()  # Clear cache
```

## Other Resources

For detailed API documentation, please refer to:
- Official Documentation: https://bioservices.readthedocs.io/
- Individual service documentation linked on the homepage
- Source Code: https://github.com/cokelaer/bioservices