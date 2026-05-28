# NCBI Gene API Reference Documentation

This document provides detailed API instructions for programmatic access to the NCBI Gene database.

## Table of Contents

1. [E-utilities API](#e-utilities-api)
2. [NCBI Datasets API](#ncbi-datasets-api)
3. [Authentication and Rate Limits](#authentication-and-rate-limits)
4. [Error Handling](#error-handling)

---

## E-utilities API

E-utilities (Entrez Programming Utilities) provide a stable interface to NCBI's Entrez databases.

### Base URL

```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
```

### Common Parameters

- `db` - Database name (use `gene` for the Gene database)
- `api_key` - API key for higher rate limits
- `retmode` - Return format (json, xml, text)
- `retmax` - Maximum number of records returned

### ESearch - Searching the Database

Search for genes matching a text query.

**Endpoint:** `esearch.fcgi`

**Parameters:**
- `db=gene` (Required) - Database to search
- `term` (Required) - Search query term
- `retmax` - Maximum number of results (default: 20)
- `retmode` - json or xml (default: xml)
- `usehistory=y` - Store results on the history server, suitable for large result sets

**Query Syntax:**
- Gene symbol: `BRCA1[gene]` or `BRCA1[gene name]`
- Organism: `human[organism]` or `9606[taxid]`
- Combined terms: `BRCA1[gene] AND human[organism]`
- Disease: `muscular dystrophy[disease]`
- Chromosome: `17q21[chromosome]`
- GO terms: `GO:0006915[biological process]`

**Request Example:**

```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=BRCA1[gene]+AND+human[organism]&retmode=json"
```

**Response Format (JSON):**

```json
{
  "esearchresult": {
    "count": "1",
    "retmax": "1",
    "retstart": "0",
    "idlist": ["672"],
    "translationset": [],
    "querytranslation": "BRCA1[Gene Name] AND human[Organism]"
  }
}
```

### ESummary - Document Summary

Retrieve document summaries for Gene IDs.

**Endpoint:** `esummary.fcgi`

**Parameters:**
- `db=gene` (Required) - Database
- `id` (Required) - Comma-separated Gene IDs (up to 500)
- `retmode` - json or xml (default: xml)

**Request Example:**

```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=672&retmode=json"
```

**Response Format (JSON):**

```json
{
  "result": {
    "672": {
      "uid": "672",
      "name": "BRCA1",
      "description": "BRCA1 DNA repair associated",
      "organism": {
        "scientificname": "Homo sapiens",
        "commonname": "human",
        "taxid": 9606
      },
      "chromosome": "17",
      "geneticsource": "genomic",
      "maplocation": "17q21.31",
      "nomenclaturesymbol": "BRCA1",
      "nomenclaturename": "BRCA1 DNA repair associated"
    }
  }
}
```

### EFetch - Full Records

Fetch detailed gene records in various formats.

**Endpoint:** `efetch.fcgi`

**Parameters:**
- `db=gene` (Required) - Database
- `id` (Required) - Comma-separated Gene IDs
- `retmode` - xml, text, asn.1 (default: xml)
- `rettype` - gene_table, docsum

**Request Example:**

```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=672&retmode=xml"
```

**XML Response:** Contains detailed gene information, including:
- Gene nomenclature
- Sequence locations
- Transcript variants
- Protein products
- Gene Ontology (GO) annotations
- Cross-references
- Publications

### ELink - Related Records

Find related records in Gene or other databases.

**Endpoint:** `elink.fcgi`

**Parameters:**
- `dbfrom=gene` (Required) - Source database
- `db` (Required) - Target database (gene, nuccore, protein, pubmed, etc.)
- `id` (Required) - Gene ID

**Request Example:**

```bash
# Get related PubMed articles
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=gene&db=pubmed&id=672&retmode=json"
```

### EInfo - Database Information

Get information about the Gene database.

**Endpoint:** `einfo.fcgi`

**Parameters:**
- `db=gene` - Database to query

**Request Example:**

```bash
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gene&retmode=json"
```

---

## NCBI Datasets API

The Datasets API provides a streamlined way to access gene data with metadata and sequences.

### Base URL

```
https://api.ncbi.nlm.nih.gov/datasets/v2alpha/gene
```

### Authentication

Include the API key in the request header:

```
api-key: YOUR_API_KEY
```

### Get Gene by ID

Retrieve gene data by Gene ID.

**Endpoint:** `GET /gene/id/{gene_id}`

**Request Example:**

```bash
curl "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/gene/id/672"
```

**Response Format (JSON):**

```json
{
  "genes": [
    {
      "gene": {
        "gene_id": "672",
        "symbol": "BRCA1",
        "description": "BRCA1 DNA repair associated",
        "tax_name": "Homo sapiens",
        "taxid": 9606,
        "chromosomes": ["17"],
        "type": "protein-coding",
        "synonyms": ["BRCC1", "FANCS", "PNCA4", "RNF53"],
        "nomenclature_authority": {
          "authority": "HGNC",
          "identifier": "HGNC:1100"
        },
        "genomic_ranges": [
          {
            "accession_version": "NC_000017.11",
            "range": [
              {
                "begin": 43044295,
                "end": 43170245,
                "orientation": "minus"
              }
            ]
          }
        ],
        "transcripts": [
          {
            "accession_version": "NM_007294.4",
            "length": 7207
          }
        ]
      }
    }
  ]
}
```

### Get Gene by Symbol

Retrieve gene data by gene symbol and organism.

**Endpoint:** `GET /gene/symbol/{symbol}/taxon/{taxon}`

**Parameters:**
- `{symbol}` - Gene symbol (e.g., BRCA1)
- `{taxon}` - Taxon ID (e.g., 9606 for human)

**Request Example:**

```bash
curl "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/gene/symbol/BRCA1/taxon/9606"
```

### Get Multiple Genes

Retrieve data for multiple genes.

**Endpoint:** `POST /gene/id`

**Request Body:**

```json
{
  "gene_ids": ["672", "7157", "5594"]
}
```

**Request Example:**

```bash
curl -X POST "https://api.ncbi.nlm.nih.gov/datasets/v2alpha/gene/id" \
  -H "Content-Type: application/json" \
  -d '{"gene_ids": ["672", "7157", "5594"]}'
```

---

## Authentication and Rate Limits

### Obtaining an API Key

1. Create an NCBI account at https://www.ncbi.nlm.nih.gov/account/
2. Navigate to Settings → API Key Management
3. Generate a new API key
4. Include the key in your requests

### Rate Limits

**E-utilities:**
- Without API key: 3 requests/second
- With API key: 10 requests/second

**Datasets API:**
- Without API key: 5 requests/second
- With API key: 10 requests/second

### Usage Guidelines

1. **Include email in requests:** Add `&email=your@email.com` to E-utilities requests
2. **Implement rate limiting:** Set delays between requests
3. **Use POST for large queries:** When handling a large number of IDs
4. **Cache results:** Store frequently used data locally
5. **Handle errors gracefully:** Implement retry logic with exponential backoff

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid parameters or malformed query
- `404 Not Found` - Gene ID or symbol not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error (try retrying with exponential backoff)

### E-utilities Error Messages

E-utilities returns errors in the response body:

**XML Format:**
```xml
<ERROR>Empty id list - nothing to do</ERROR>
```

**JSON Format:**
```json
{
  "error": "Invalid db name"
}
```

### Common Errors

1. **Empty Result Set**
   - Cause: Gene symbol or ID not found
   - Resolution: Check spelling, check organism filters

2. **Rate Limit Exceeded**
   - Cause: Requests sent too frequently
   - Resolution: Increase delay, use an API key

3. **Invalid Query Syntax**
   - Cause: Malformed search term
   - Resolution: Use correct field tags (e.g., `[gene]`, `[organism]`)

4. **Timeout**
   - Cause: Result set too large or slow connection
   - Resolution: Use the history server, reduce result size

### Retry Strategy

Implement exponential backoff for failed requests:

```python
import time

def retry_request(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s respectively
                time.sleep(wait_time)
            else:
                raise
```

---

## Common Taxon IDs

| Species | Scientific Name | Taxon ID |
|----------|----------------|----------|
| Human | Homo sapiens | 9606 |
| Mouse | Mus musculus | 10090 |
| Rat | Rattus norvegicus | 10116 |
| Zebrafish | Danio rerio | 7955 |
| Fruit fly | Drosophila melanogaster | 7227 |
| C. elegans | Caenorhabditis elegans | 6239 |
| Yeast | Saccharomyces cerevisiae | 4932 |
| Arabidopsis | Arabidopsis thaliana | 3702 |
| E. coli | Escherichia coli | 562 |

---

## Further Resources

- **E-utilities Documentation:** https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **Datasets API Documentation:** https://www.ncbi.nlm.nih.gov/datasets/docs/v2/
- **Gene Database Help:** https://www.ncbi.nlm.nih.gov/gene/
- **API Key Registration:** https://www.ncbi.nlm.nih.gov/account/