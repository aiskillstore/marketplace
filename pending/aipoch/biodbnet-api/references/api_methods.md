# bioDBnet API Methods

Base URL: `https://biodbnet-abcc.ncifcrf.gov/webServices/rest.php/biodbnetRestApi.json`

## Methods

### `getInputs`
- Description: Gets all input nodes.
- Params: None

### `getOutputsForInput`
- Description: Gets all possible output nodes for a given input node.
- Params:
  - `input`: The input node name (e.g., `genesymbol`)

### `getDirectOutptsForInput`
- Description: Gets direct output nodes for a given input node.
- Params:
  - `input`: The input node name
  - `directOutput`: Set to `1`

### `getPathways`
- Description: Get available pathways.
- Params:
  - `pathways`: `1` (all) or comma-separated list (e.g., `ncipid,kegg`)
  - `taxonId`: Taxon ID (e.g., `9606` for human)

### `db2db`
- Description: Database to Database conversion.
- Params:
  - `input`: Input type (e.g., `geneid`)
  - `inputValues`: Comma-separated values (e.g., `1,3`)
  - `outputs`: Comma-separated output types (e.g., `genesymbol,affyid`)
  - `taxonId`: Taxon ID
  - `format`: `row` or `col` (optional)

### `dbReport`
- Description: Like db2db but returns all possible outputs.
- Params:
  - `input`: Input type
  - `inputValues`: Values
  - `taxonId`: Taxon ID
  - `format`: `row` or `col`

### `dbWalk`
- Description: Graph walk.
- Params:
  - `inputValues`: Values
  - `dbPath`: Path (e.g., `genesymbol->geneid->affyid`)
  - `taxonId`: Taxon ID
  - `format`: `row` or `col`

### `dbFind`
- Description: Find intermediate nodes.
- Params:
  - `inputValues`: Values
  - `output`: Output node
  - `taxonId`: Taxon ID
  - `format`: `row` or `col`

### `dbOrtho`
- Description: Ortholog mapping.
- Params:
  - `input`: Input type
  - `inputValues`: Values
  - `inputTaxon`: Input Taxon ID
  - `outputTaxon`: Output Taxon ID
  - `output`: Output type
  - `format`: `row` or `col`

### `dbAnnot`
- Description: Annotations (Genes, Drugs, Diseases, GO Terms, Pathways, Protein Interactors).
- Params:
  - `inputValues`: Values
  - `taxonId`: Taxon ID
  - `annotations`: Comma-separated types (e.g., `Genes,Pathways`)
  - `format`: `row` or `col`
