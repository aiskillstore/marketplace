# GWAS Catalog API Reference Guide

A comprehensive reference document for the GWAS Catalog REST API, including endpoint specifications, query parameters, response formats, and advanced usage patterns.

## Table of Contents

- [API Overview](#api-overview)
- [Authentication and Rate Limiting](#authentication-and-rate-limiting)
- [GWAS Catalog REST API](#gwas-catalog-rest-api)
- [Summary Statistics API](#summary-statistics-api)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Advanced Query Patterns](#advanced-query-patterns)
- [Integration Examples](#integration-examples)

## API Overview

The GWAS Catalog provides two complementary REST APIs:

1. **GWAS Catalog REST API**: Access curated SNP-trait associations, studies, and metadata.
2. **Summary Statistics API**: Access full GWAS summary statistics (all tested variants).

Both APIs follow RESTful design principles and return responses in JSON format with HAL (Hypertext Application Language), which includes `_links` for resource navigation.

### Base URLs

```
GWAS Catalog API:         https://www.ebi.ac.uk/gwas/rest/api
Summary Statistics API:   https://www.ebi.ac.uk/gwas/summary-statistics/api
```

### Version Information

GWAS Catalog REST API v2.0 was released in 2024 with significant improvements:
- New endpoints (publications, genes, genomic contexts, ancestries)
- Enhanced data exposure (cohorts, background traits, license agreements)
- Improved query capabilities
- Better performance and documentation

Previous API versions will be maintained until May 2026 to ensure backward compatibility.

## Authentication and Rate Limiting

### Authentication

**No authentication required** —— Both APIs are open access and do not require API keys or registration.

### Rate Limiting

While no explicit rate limits are documented, please follow these best practices:
- Set delays between consecutive requests (e.g., 0.1-0.5 seconds)
- Use pagination for large result sets
- Cache responses locally
- For genome-wide data, please use bulk downloads (FTP)
- Avoid hitting the API with extremely fast consecutive requests

**Example with rate limiting:**
```python
import requests
from time import sleep

def query_with_rate_limit(url, delay=0.1):
    response = requests.get(url)
    sleep(delay) # Implement delay to comply with best practices
    return response.json()
```

## GWAS Catalog REST API

The main API provides access to curated GWAS associations, studies, variants, and traits.

### Core Endpoints

#### 1. Studies

**Get all studies:**
```
GET /studies
```

**Get a specific study:**
```
GET /studies/{accessionId}
```

**Search studies:**
```
GET /studies/search/findByPublicationIdPubmedId?pubmedId={pmid}
GET /studies/search/findByDiseaseTrait?diseaseTrait={trait}
```

**Query Parameters:**
- `page`: Page number (starting from 0)
- `size`: Number of results per page (default: 20)
- `sort`: Sorting field (e.g., `publicationDate,desc`)

**Example:**
```python
import requests

# Get a specific study
url = "https://www.ebi.ac.uk/gwas/rest/api/studies/GCST001795"
response = requests.get(url, headers={"Content-Type": "application/json"})
study = response.json()

print(f"Title: {study.get('title')}")
print(f"PMID: {study.get('publicationInfo', {}).get('pubmedId')}")
print(f"Sample size: {study.get('initialSampleSize')}")
```

**Response Fields:**
- `accessionId`: Study identifier (GCST ID)
- `title`: Study title
- `publicationInfo`: Publication information, including PMID
- `initialSampleSize`: Discovery cohort description
- `replicationSampleSize`: Replication cohort description
- `ancestries`: Population ancestry information
- `genotypingTechnologies`: Genotyping chip or sequencing platform
- `_links`: Links to related resources

#### 2. Associations

**Get all associations:**
```
GET /associations
```

**Get a specific association:**
```
GET /associations/{associationId}
```

**Get associations for a trait:**
```
GET /efoTraits/{efoId}/associations
```

**Get associations for a variant:**
```
GET /singleNucleotidePolymorphisms/{rsId}/associations
```

**Query Parameters:**
- `projection`: Response projection (e.g., `associationBySnp`)
- `page`, `size`, `sort`: Pagination control

**Example:**
```python
import requests

# Find all associations for Type 2 Diabetes
trait_id = "EFO_0001360"
url = f"https://www.ebi.ac.uk/gwas/rest/api/efoTraits/{trait_id}/associations"
params = {"size": 100, "page": 0}
response = requests.get(url, params=params, headers={"Content-Type": "application/json"})
data = response.json()

associations = data.get('_embedded', {}).get('associations', [])
print(f"Found {len(associations)} associations")
```

**Response Fields:**
- `rsId`: Variant identifier
- `strongestAllele`: Risk or effect allele
- `pvalue`: Association p-value
- `pvalueText`: Reported p-value (may include inequality signs)
- `pvalueMantissa`: Mantissa of the p-value
- `pvalueExponent`: Exponent of the p-value
- `orPerCopyNum`: Odds Ratio (OR) per allele copy
- `betaNum`: Effect size (for quantitative traits)
- `betaUnit`: Unit of measurement
- `range`: Confidence interval
- `standardError`: Standard error
- `efoTrait`: Trait name
- `mappedLabel`: EFO standard term
- `studyId`: Accession number of the associated study

#### 3. Variants (Single Nucleotide Polymorphisms)

**Get variant details:**
```
GET /singleNucleotidePolymorphisms/{rsId}
```

**Search variants:**
```
GET /singleNucleotidePolymorphisms/search/findByRsId?rsId={rsId}
GET /singleNucleotidePolymorphisms/search/findByChromBpLocationRange?chrom={chr}&bpStart={start}&bpEnd={end}
GET /singleNucleotidePolymorphisms/search/findByGene?geneName={gene}
```

**Example:**
```python
import requests

# Get variant information
rs_id = "rs7903146"
url = f"https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/{rs_id}"
response = requests.get(url, headers={"Content-Type": "application/json"})
variant = response.json()

print(f"rsID: {variant.get('rsId')}")
print(f"Location: chr{variant.get('locations', [{}])[0].get('chromosomeName')}:{variant.get('locations', [{}])[0].get('chromosomePosition')}")
```

**Response Fields:**
- `rsId`: rs number
- `merged`: Indicates if the variant has been merged with another
- `functionalClass`: Variant consequence
- `locations`: Array of genomic locations
  - `chromosomeName`: Chromosome number
  - `chromosomePosition`: Base pair position
  - `region`: Genomic region information
- `genomicContexts`: Nearby genes
- `lastUpdateDate`: Last modification date

#### 4. Traits (EFO Terms)

**Get trait information:**
```
GET /efoTraits/{efoId}
```

**Search traits:**
```
GET /efoTraits/search/findByEfoUri?uri={efoUri}
GET /efoTraits/search/findByTraitIgnoreCase?trait={traitName}
```

**Example:**
```python
import requests

# Get trait details
trait_id = "EFO_0001360"
url = f"https://www.ebi.ac.uk/gwas/rest/api/efoTraits/{trait_id}"
response = requests.get(url, headers={"Content-Type": "application/json"})
trait = response.json()

print(f"Trait: {trait.get('trait')}")
print(f"EFO URI: {trait.get('uri')}")
```

#### 5. Publications

**Get publication information:**
```
GET /publications
GET /publications/{publicationId}
GET /publications/search/findByPubmedId?pubmedId={pmid}
```

#### 6. Genes

**Get gene information:**
```
GET /genes
GET /genes/{geneId}
GET /genes/search/findByGeneName?geneName={symbol}
```

### Pagination and Navigation

All list endpoints support pagination:

```python
import requests

def get_all_associations(trait_id):
    """Retrieve all associations for a trait via pagination"""
    base_url = "https://www.ebi.ac.uk/gwas/rest/api"
    url = f"{base_url}/efoTraits/{trait_id}/associations"
    all_associations = []
    page = 0

    while True:
        params = {"page": page, "size": 100}
        response = requests.get(url, params=params, headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            break

        data = response.json()
        associations = data.get('_embedded', {}).get('associations', [])

        if not associations:
            break

        all_associations.extend(associations)
        page += 1

    return all_associations
```

### HAL Links

Responses include `_links` for resource navigation:

```python
import requests

# Get a study and follow links to associations
response = requests.get("https://www.ebi.ac.uk/gwas/rest/api/studies/GCST001795")
study = response.json()

# Follow the associations link
associations_url = study['_links']['associations']['href']
associations_response = requests.get(associations_url)
associations = associations_response.json()
```

## Summary Statistics API

Access full GWAS summary statistics for studies that have submitted complete data.

### Base URL
```
https://www.ebi.ac.uk/gwas/summary-statistics/api
```

### Core Endpoints

#### 1. Studies

**Get all studies with summary statistics:**
```
GET /studies
```

**Get a specific study:**
```
GET /studies/{gcstId}
```

#### 2. Traits

**Get trait information:**
```
GET /traits/{efoId}
```

**Get associations for a trait:**
```
GET /traits/{efoId}/associations
```

**Query Parameters:**
- `p_lower`: Lower bound for p-value
- `p_upper`: Upper bound for p-value
- `size`: Number of results
- `page`: Page number

**Example:**
```python
import requests

# Find highly significant associations for a trait
trait_id = "EFO_0001360"
base_url = "https://www.ebi.ac.uk/gwas/summary-statistics/api"
url = f"{base_url}/traits/{trait_id}/associations"
params = {
    "p_upper": "0.000000001",  # p < 1e-9
    "size": 100
}
response = requests.get(url, params=params)
results = response.json()
```

#### 3. Chromosomes

**Get associations by chromosome:**
```
GET /chromosomes/{chromosome}/associations
```

**Query by genomic region:**
```
GET /chromosomes/{chromosome}/associations?start={start}&end={end}
```

**Example:**
```python
import requests

# Query variants in a specific region
chromosome = "10"
start_pos = 114000000
end_pos = 115000000

base_url = "https://www.ebi.ac.uk/gwas/summary-statistics/api"
url = f"{base_url}/chromosomes/{chromosome}/associations"
params = {
    "start": start_pos,
    "end": end_pos,
    "size": 1000
}
response = requests.get(url, params=params)
variants = response.json()
```

#### 4. Variants

**Get a specific variant across different studies:**
```
GET /variants/{variantId}
```

**Search associations by variant ID:**
```
GET /variants/{variantId}/associations
```

### Response Fields

**Association Fields:**
- `variant_id`: Variant identifier
- `chromosome`: Chromosome number
- `base_pair_location`: Position (bp)
- `effect_allele`: Effect allele
- `other_allele`: Reference/Other allele
- `effect_allele_frequency`: Allele frequency
- `beta`: Effect size
- `standard_error`: Standard error
- `p_value`: P-value
- `ci_lower`: Lower bound of confidence interval
- `ci_upper`: Upper bound of confidence interval
- `odds_ratio`: Odds ratio (for case-control studies)
- `study_accession`: GCST ID

## Response Formats

### Content Type

All API requests should include the header:
```
Content-Type: application/json
```

### HAL Format

Responses follow the HAL (Hypertext Application Language) specification:

```json
{
  "_embedded": {
    "associations": [
      {
        "rsId": "rs7903146",
        "pvalue": 1.2e-30,
        "efoTrait": "type 2 diabetes",
        "_links": {
          "self": {
            "href": "https://www.ebi.ac.uk/gwas/rest/api/associations/12345"
          }
        }
      }
    ]
  },
  "_links": {
    "self": {
      "href": "https://www.ebi.ac.uk/gwas/rest/api/efoTraits/EFO_0001360/associations?page=0"
    },
    "next": {
      "href": "https://www.ebi.ac.uk/gwas/rest/api/efoTraits/EFO_0001360/associations?page=1"
    }
  },
  "page": {
    "size": 20,
    "totalElements": 1523,
    "totalPages": 77,
    "number": 0
  }
}
```

### Page Metadata

Pagination responses include page information:
- `size`: Number of entries per page
- `totalElements`: Total number of results
- `totalPages`: Total number of pages
- `number`: Current page number (starting from 0)

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "timestamp": "2025-10-19T12:00:00.000+00:00",
  "status": 404,
  "error": "Not Found",
  "message": "No association found with id: 12345",
  "path": "/gwas/rest/api/associations/12345"
}
```

### Error Handling Example

```python
import requests

def safe_api_request(url, params=None):
    """Perform an API request with error handling"""
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text}")
        return None
    except requests.exceptions.ConnectionError:
        print("Connection error - check network")
        return None
    except requests.exceptions.Timeout:
        print("Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
```

## Advanced Query Patterns

### 1. Cross-referencing Variants and Traits

```python
import requests

def get_variant_pleiotropy(rs_id):
    """Get all traits associated with a specific variant"""
    base_url = "https://www.ebi.ac.uk/gwas/rest/api"
    url = f"{base_url}/singleNucleotidePolymorphisms/{rs_id}/associations"
    params = {"projection": "associationBySnp"}

    response = requests.get(url, params=params, headers={"Content-Type": "application/json"})
    data = response.json()

    traits = {}
    for assoc in data.get('_embedded', {}).get('associations', []):
        trait = assoc.get('efoTrait')
        pvalue = assoc.get('pvalue')
        if trait:
            # Update if trait doesn't exist or a more significant p-value is found
            if trait not in traits or float(pvalue) < float(traits[trait]):
                traits[trait] = pvalue

    return traits

# Usage example
pleiotropy = get_variant_pleiotropy('rs7903146')
for trait, pval in sorted(pleiotropy.items(), key=lambda x: float(x[1])):
    print(f"{trait}: p={pval}")
```

### 2. Filtering by P-value Threshold

```python
import requests

def get_significant_associations(trait_id, p_threshold=5e-8):
    """Get genome-wide significant associations"""
    base_url = "https://www.ebi.ac.uk/gwas/rest/api"
    url = f"{base_url}/efoTraits/{trait_id}/associations"

    results = []
    page = 0

    while True:
        params = {"page": page, "size": 100}
        response = requests.get(url, params=params, headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            break

        data = response.json()
        associations = data.get('_embedded', {}).get('associations', [])

        if not associations:
            break

        for assoc in associations:
            pvalue = assoc.get('pvalue')
            if pvalue and float(pvalue) <= p_threshold:
                results.append(assoc)

        page += 1

    return results
```

### 3. Combining Main API and Summary Statistics API

```python
import requests

def get_complete_variant_data(rs_id):
    """Retrieve variant data from both APIs"""
    main_url = f"https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/{rs_id}"

    # Get basic variant info
    response = requests.get(main_url, headers={"Content-Type": "application/json"})
    variant_info = response.json()

    # Get associations
    assoc_url = f"{main_url}/associations"
    response = requests.get(assoc_url, headers={"Content-Type": "application/json"})
    associations = response.json()

    # This variant can also be queried in the Summary Statistics API
    # to cover all studies with summary data

    return {
        "variant": variant_info,
        "associations": associations
    }
```

### 4. Genomic Region Query

```python
import requests

def query_region(chromosome, start, end, p_threshold=None):
    """Query variants within a genomic region"""
    # From Main API
    base_url = "https://www.ebi.ac.uk/gwas/rest/api"
    url = f"{base_url}/singleNucleotidePolymorphisms/search/findByChromBpLocationRange"
    params = {
        "chrom": chromosome,
        "bpStart": start,
        "bpEnd": end,
        "size": 1000
    }

    response = requests.get(url, params=params, headers={"Content-Type": "application/json"})
    variants = response.json()

    # Also query Summary Statistics API
    sumstats_url = f"https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/{chromosome}/associations"
    sumstats_params = {"start": start, "end": end, "size": 1000}
    if p_threshold:
        sumstats_params["p_upper"] = str(p_threshold)

    sumstats_response = requests.get(sumstats_url, params=sumstats_params)
    sumstats = sumstats_response.json()

    return {
        "catalog_variants": variants,
        "summary_stats": sumstats
    }
```

## Integration Examples

### Full Workflow: Disease Genetic Architecture Analysis

```python
import requests
import pandas as pd
from time import sleep

class GWASCatalogQuery:
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/gwas/rest/api"
        self.headers = {"Content-Type": "application/json"}

    def get_trait_associations(self, trait_id, p_threshold=5e-8):
        """Get all associations for a trait"""
        url = f"{self.base_url}/efoTraits/{trait_id}/associations"
        results = []
        page = 0

        while True:
            params = {"page": page, "size": 100}
            response = requests.get(url, params=params, headers=self.headers)

            if response.status_code != 200:
                break

            data = response.json()
            associations = data.get('_embedded', {}).get('associations', [])

            if not associations:
                break

            for assoc in associations:
                pvalue = assoc.get('pvalue')
                if pvalue and float(pvalue) <= p_threshold:
                    results.append({
                        'rs_id': assoc.get('rsId'),
                        'pvalue': float(pvalue),
                        'risk_allele': assoc.get('strongestAllele'),
                        'or_beta': assoc.get('orPerCopyNum') or assoc.get('betaNum'),
                        'study': assoc.get('studyId'),
                        'pubmed_id': assoc.get('pubmedId')
                    })

            page += 1
            sleep(0.1) # Comply with rate limiting suggestions

        return pd.DataFrame(results)

    def get_variant_details(self, rs_id):
        """Get detailed variant information"""
        url = f"{self.base_url}/singleNucleotidePolymorphisms/{rs_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

    def get_gene_associations(self, gene_name):
        """Get variants associated with a gene"""
        url = f"{self.base_url}/singleNucleotidePolymorphisms/search/findByGene"
        params = {"geneName": gene_name}
        response = requests.get(url, params=params, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        return None

# Usage example
gwas = GWASCatalogQuery()

# Query Type 2 Diabetes associations
df = gwas.get_trait_associations('EFO_0001360')
print(f"Found {len(df)} genome-wide significant associations")
print(f"Unique variants: {df['rs_id'].nunique()}")

# Get top significant variants
top_variants = df.nsmallest(10, 'pvalue')
print("\nTop 10 variants:")
print(top_variants[['rs_id', 'pvalue', 'risk_allele']])

# Get details for the top variant
if len(top_variants) > 0:
    top_rs = top_variants.iloc[0]['rs_id']
    variant_info = gwas.get_variant_details(top_rs)
    if variant_info:
        loc = variant_info.get('locations', [{}])[0]
        print(f"\n{top_rs} location: chr{loc.get('chromosomeName')}:{loc.get('chromosomePosition')}")
```

### FTP Download Integration

```python
import requests
from pathlib import Path

def download_summary_statistics(gcst_id, output_dir="."):
    """Download summary statistics from FTP"""
    # FTP URL pattern
    ftp_base = "http://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics"

    # Prefer harmonised files
    harmonised_url = f"{ftp_base}/{gcst_id}/harmonised/{gcst_id}-harmonised.tsv.gz"

    output_path = Path(output_dir) / f"{gcst_id}.tsv.gz"

    try:
        response = requests.get(harmonised_url, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Downloaded {gcst_id} to {output_path}")
        return output_path

    except requests.exceptions.HTTPError:
        print(f"Harmonised file not found for {gcst_id}")
        return None

# Usage example
download_summary_statistics("GCST001234", output_dir="./sumstats")
```

## Additional Resources

- **Interactive API Documentation**: https://www.ebi.ac.uk/gwas/rest/docs/api
- **Summary Statistics API Documentation**: https://www.ebi.ac.uk/gwas/summary-statistics/docs/
- **Workshop Materials**: https://github.com/EBISPOT/GWAS_Catalog-workshop
- **Blog Post on API v2**: https://ebispot.github.io/gwas-blog/rest-api-v2-release/
- **R Package (gwasrapidd)**: https://cran.r-project.org/package=gwasrapidd