# CTD Batch Query API Documentation

Based on CTD API documentation.

## Base URL
`https://ctdbase.org/tools/batchQuery.go`

## Parameters

### 1. inputType (Required)
The category of your input data.
* `chem`: chemicals
* `disease`: diseases
* `gene`: genes
* `go`: Gene Ontology (GO) terms
* `pathway`: pathways
* `phenotype`: phenotype
* `reference`: references

### 2. inputTerms (Required)
List of query terms (names or IDs).

### 3. report (Required)
The data to return. Valid combinations with `inputType`:

| Report Parameter | Valid Input Types | Description |
| :--- | :--- | :--- |
| `cgixns` | chem, gene, disease, phenotype | Curated chemical–gene interactions. Requires `actionTypes`. |
| `chems` | disease | All chemical associations. |
| `chems_curated` | disease, gene, phenotype, reference | Curated chemical associations. |
| `chems_inferred` | disease | Inferred chemical associations. |
| `genes` | disease | All gene associations. |
| `genes_curated` | chem, disease, go, pathway, reference | Curated gene associations. |
| `genes_inferred` | disease | Inferred gene associations. |
| `diseases` | chem, gene | All disease associations. |
| `diseases_curated` | chem, gene, reference | Curated disease associations. |
| `diseases_inferred` | chem, gene, go, pathway, phenotype | Inferred disease associations. |
| `pathways_curated` | gene | Curated pathway associations. |
| `pathways_inferred` | chem, disease | Inferred pathway associations. |
| `pathways_enriched` | chem | Enriched pathway associations. |
| `phenotypes_curated` | chem, reference | Curated phenotype associations. |
| `phenotypes_inferred` | disease | Inferred phenotype associations. |
| `go` | chem, gene | All GO associations. Requires `ontology`. |
| `go_enriched` | chem | Enriched GO associations. Requires `ontology`. |
| `exposure` | chem, disease, gene, phenotype | All exposure details data. |

### 4. format (Optional)
* `tsv` (tab-separated values)
* `csv` (comma-separated values)
* `json` (JavaScript Object Notation) - **Default in Skill**
* `xml`

### 5. Other Parameters (Optional)
* `actionTypes`: Filter for `cgixns`. `ANY` or specific types.
* `ontology`: Filter for `go` or `go_enriched`.
    * `go_bp`: Biological Process
    * `go_cc`: Cellular Component
    * `go_mf`: Molecular Function
