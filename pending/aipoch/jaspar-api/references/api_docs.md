# JASPAR API Documentation

## Base URL
https://jaspar.elixir.no/api/v1/

## Endpoints

### 1. Collections

#### List Collections
`GET /api/v1/collections/`

Query Parameters:
- `search`: A search term.
- `order`: Which field to use when ordering the results.
- `release`: Access a specific release (2014, 2016, 2018, 2020, 2022). Default: latest.

#### Read Collection
`GET /api/v1/collections/{collection}/`

Path Parameters:
- `collection`: Collection name (required).

Query Parameters:
- `search`: A search term.
- `order`: Ordering field.
- `version`: If set to `latest`, return latest version.
- `release`: Release year.

### 2. Infer

#### Infer Matrix Profiles
`GET /api/v1/infer/{sequence}/`

Path Parameters:
- `sequence`: Protein sequence (required).

### 3. Matrix

#### List Matrices
`GET /api/v1/matrix/`

Query Parameters:
- `page`: Page number.
- `page_size`: Results per page.
- `search`: Search term.
- `order`: Ordering field.
- `collection`: JASPAR Collection name (e.g., CORE, CNE).
- `name`: TF name (case-sensitive, e.g., SMAD3).
- `tax_group`: Taxonomic group (e.g., Vertebrates).
- `tax_id`: Taxa ID (e.g., 9606). Comma-separated for multiple.
- `tf_class`: Transcription factor class (e.g., Zipper-Type).
- `tf_family`: Transcription factor family (e.g., SMAD factors).
- `data_type`: Data type (e.g., ChIP-seq, PBM, SELEX).
- `version`: `latest` or specific.
- `release`: Release year.

#### Read Matrix
`GET /api/v1/matrix/{matrix_id}/`

Path Parameters:
- `matrix_id`: Matrix ID (required).

#### List Matrix Versions
`GET /api/v1/matrix/{base_id}/versions/`

Path Parameters:
- `base_id`: Base Matrix ID (required).

### 4. Releases

#### List Releases
`GET /api/v1/releases/`

#### Read Release
`GET /api/v1/releases/{release_number}/`

### 5. Species

#### List Species
`GET /api/v1/species/`

#### Read Species
`GET /api/v1/species/{tax_id}/`

### 6. Taxon

#### List Taxons
`GET /api/v1/taxon/`

#### Read Taxon
`GET /api/v1/taxon/{tax_group}/`

Available groups: vertebrates, plants, insects, nematodes, fungi, urochordates.
