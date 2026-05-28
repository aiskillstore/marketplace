# ClinPGx API Reference Documentation

Complete reference documentation for the ClinPGx REST API.

## Base URL

```
https://api.clinpgx.org/v1/
```

## Rate Limiting

- **Maximum Rate**: 2 requests per second
- **Enforcement**: Requests exceeding the limit will receive HTTP 429 (Too Many Requests)
- **Best Practice**: It is recommended to implement a 500 ms (0.5 second) delay between requests
- **Recommendation**: For high-volume API usage, please contact api@clinpgx.org

## Authentication

Basic API access does not require authentication. All endpoints are publicly accessible.

## Data License

All data accessed via the API is subject to the following agreements:
- Creative Commons Attribution-ShareAlike 4.0 International License
- ClinPGx Data Use Policy

## Response Format

All successful responses return JSON with the corresponding HTTP status code:
- `200 OK`: Request successful
- `404 Not Found`: Resource does not exist
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Core Endpoints

### 1. Gene Endpoint

Retrieve pharmacogenetic information, including functions, variants, and clinical significance.

#### Get Gene by Symbol

```http
GET /v1/gene/{gene_symbol}
```

**Parameters:**
- `gene_symbol` (path parameter, required): Gene symbol (e.g., CYP2D6, TPMT, DPYD)

**Example Request:**
```bash
curl "https://api.clinpgx.org/v1/gene/CYP2D6"
```

**Example Response:**
```json
{
  "id": "PA126",
  "symbol": "CYP2D6",
  "name": "cytochrome P450 family 2 subfamily D member 6",
  "chromosome": "22",
  "chromosomeLocation": "22q13.2",
  "function": "Drug metabolism",
  "description": "Highly polymorphic gene encoding enzyme...",
  "clinicalAnnotations": [...],
  "relatedDrugs": [...]
}
```

#### Search Genes

```http
GET /v1/gene?q={search_term}
```

**Parameters:**
- `q` (query parameter, optional): Search term for gene name or symbol

**Example:**
```bash
curl "https://api.clinpgx.org/v1/gene?q=CYP"
```

### 2. Chemical/Drug Endpoint

Access drug and chemical compound information, including pharmacogenomic annotations.

#### Get Drug by ID

```http
GET /v1/chemical/{drug_id}
```

**Parameters:**
- `drug_id` (path parameter, required): ClinPGx drug identifier (e.g., PA448515)

**Example Request:**
```bash
curl "https://api.clinpgx.org/v1/chemical/PA448515"
```

#### Search Drugs by Name

```http
GET /v1/chemical?name={drug_name}
```

**Parameters:**
- `name` (query parameter, optional): Drug name or alias

**Example:**
```bash
curl "https://api.clinpgx.org/v1/chemical?name=warfarin"
```

**Example Response:**
```json
[
  {
    "id": "PA448515",
    "name": "warfarin",
    "genericNames": ["warfarin sodium"],
    "tradeNames": ["Coumadin", "Jantoven"],
    "drugClasses": ["Anticoagulants"],
    "indication": "Prevention of thrombosis",
    "relatedGenes": ["CYP2C9", "VKORC1", "CYP4F2"]
  }
]
```

### 3. Gene-Drug Pair Endpoint

Query manually curated gene-drug interactions with clinical annotations.

#### Get Gene-Drug Pairs

```http
GET /v1/geneDrugPair?gene={gene}&drug={drug}
```

**Parameters:**
- `gene` (query parameter, optional): Gene symbol
- `drug` (query parameter, optional): Drug name
- `cpicLevel` (query parameter, optional): Filter by CPIC recommendation level (A, B, C, D)

**Example Request:**
```bash
# Get all pairs for a specific gene
curl "https://api.clinpgx.org/v1/geneDrugPair?gene=CYP2D6"

# Get a specific gene-drug pair
curl "https://api.clinpgx.org/v1/geneDrugPair?gene=CYP2D6&drug=codeine"

# Get all CPIC Level A pairs
curl "https://api.clinpgx.org/v1/geneDrugPair?cpicLevel=A"
```

**Example Response:**
```json
[
  {
    "gene": "CYP2D6",
    "drug": "codeine",
    "sources": ["CPIC", "FDA", "DPWG"],
    "cpicLevel": "A",
    "evidenceLevel": "1A",
    "clinicalAnnotationCount": 45,
    "hasGuideline": true,
    "guidelineUrl": "https://www.clinpgx.org/guideline/..."
  }
]
```

### 4. Guideline Endpoint

Access clinical practice guidelines from CPIC, DPWG, and other sources.

#### Get Guidelines

```http
GET /v1/guideline?source={source}&gene={gene}&drug={drug}
```

**Parameters:**
- `source` (query parameter, optional): Guideline source (CPIC, DPWG, FDA)
- `gene` (query parameter, optional): Gene symbol
- `drug` (query parameter, optional): Drug name

**Example Request:**
```bash
# Get all CPIC guidelines
curl "https://api.clinpgx.org/v1/guideline?source=CPIC"

# Get guidelines for a specific gene-drug pair
curl "https://api.clinpgx.org/v1/guideline?gene=CYP2C19&drug=clopidogrel"
```

#### Get Guideline by ID

```http
GET /v1/guideline/{guideline_id}
```

**Example:**
```bash
curl "https://api.clinpgx.org/v1/guideline/PA166104939"
```

**Example Response:**
```json
{
  "id": "PA166104939",
  "name": "CPIC Guideline for CYP2C19 and Clopidogrel",
  "source": "CPIC",
  "genes": ["CYP2C19"],
  "drugs": ["clopidogrel"],
  "recommendationLevel": "A",
  "lastUpdated": "2023-08-01",
  "summary": "Alternative antiplatelet therapy recommended for...",
  "recommendations": [...],
  "pdfUrl": "https://www.clinpgx.org/...",
  "pmid": "23400754"
}
```

### 5. Allele Endpoint

Query allele definitions, functions, and population frequencies.

#### Get All Alleles for a Gene

```http
GET /v1/allele?gene={gene_symbol}
```

**Parameters:**
- `gene` (query parameter, required): Gene symbol

**Example Request:**
```bash
curl "https://api.clinpgx.org/v1/allele?gene=CYP2D6"
```

**Example Response:**
```json
[
  {
    "name": "CYP2D6*1",
    "gene": "CYP2D6",
    "function": "Normal function",
    "activityScore": 1.0,
    "frequencies": {
      "European": 0.42,
      "African": 0.37,
      "East Asian": 0.50,
      "Latino": 0.44
    },
    "definingVariants": ["Reference allele"],
    "pharmVarId": "PV00001"
  },
  {
    "name": "CYP2D6*4",
    "gene": "CYP2D6",
    "function": "No function",
    "activityScore": 0.0,
    "frequencies": {
      "European": 0.20,
      "African": 0.05,
      "East Asian": 0.01,
      "Latino": 0.10
    },
    "definingVariants": ["rs3892097"],
    "pharmVarId": "PV00004"
  }
]
```

#### Get Specific Allele

```http
GET /v1/allele/{allele_name}
```

**Parameters:**
- `allele_name` (path parameter, required): Allele name in star nomenclature (e.g., CYP2D6*4)

**Example:**
```bash
curl "https://api.clinpgx.org/v1/allele/CYP2D6*4"
```

### 6. Variant Endpoint

Search genetic variants and their pharmacogenomic annotations.

#### Get Variant by rsID

```http
GET /v1/variant/{rsid}
```

**Parameters:**
- `rsid` (path parameter, required): dbSNP reference SNP ID

**Example Request:**
```bash
curl "https://api.clinpgx.org/v1/variant/rs4244285"
```

**Example Response:**
```json
{
  "rsid": "rs4244285",
  "chromosome": "10",
  "position": 94781859,
  "gene": "CYP2C19",
  "alleles": ["CYP2C19*2"],
  "consequence": "Splice site variant",
  "clinicalSignificance": "Pathogenic - reduced enzyme activity",
  "frequencies": {
    "European": 0.15,
    "African": 0.18,
    "East Asian": 0.29,
    "Latino": 0.12
  },
  "references": [...]
}
```

#### Search Variants by Position

```http
GET /v1/variant?chromosome={chr}&position={pos}
```

**Parameters:**
- `chromosome` (query parameter, optional): Chromosome number (1-22, X, Y)
- `position` (query parameter, optional): Genomic position (GRCh38)

**Example:**
```bash
curl "https://api.clinpgx.org/v1/variant?chromosome=10&position=94781859"
```

### 7. Clinical Annotation Endpoint

Access curated literature annotations regarding gene-drug-phenotype relationships.

#### Get Clinical Annotations

```http
GET /v1/clinicalAnnotation?gene={gene}&drug={drug}&evidenceLevel={level}
```

**Parameters:**
- `gene` (query parameter, optional): Gene symbol
- `drug` (query parameter, optional): Drug name
- `evidenceLevel` (query parameter, optional): Evidence level (1A, 1B, 2A, 2B, 3, 4)
- `phenotype` (query parameter, optional): Phenotype or outcome

**Example Request:**
```bash
# Get all annotations for a gene
curl "https://api.clinpgx.org/v1/clinicalAnnotation?gene=CYP2D6"

# Get high-quality evidence only
curl "https://api.clinpgx.org/v1/clinicalAnnotation?evidenceLevel=1A"

# Get annotations for a specific gene-drug pair
curl "https://api.clinpgx.org/v1/clinicalAnnotation?gene=TPMT&drug=azathioprine"
```

**Example Response:**
```json
[
  {
    "id": "PA166153683",
    "gene": "CYP2D6",
    "drug": "codeine",
    "phenotype": "Reduced analgesic effect",
    "evidenceLevel": "1A",
    "annotation": "Poor metabolizers have reduced conversion...",
    "pmid": "24618998",
    "studyType": "Clinical trial",
    "population": "European",
    "sources": ["CPIC"]
  }
]
```

**Evidence Levels:**
- **1A**: High-quality evidence from guidelines (CPIC, FDA, DPWG)
- **1B**: High-quality evidence not yet included in guidelines
- **2A**: Moderate evidence from well-designed studies
- **2B**: Moderate evidence with some limitations
- **3**: Limited or conflicting evidence
- **4**: Case reports or weak evidence

### 8. Drug Label Endpoint

Retrieve regulatory drug label information containing pharmacogenomic content.

#### Get Drug Labels

```http
GET /v1/drugLabel?drug={drug_name}&source={source}
```

**Parameters:**
- `drug` (query parameter, required): Drug name
- `source` (query parameter, optional): Regulatory source (FDA, EMA, PMDA, Health Canada)

**Example Request:**
```bash
# Get all labels for warfarin
curl "https://api.clinpgx.org/v1/drugLabel?drug=warfarin"

# Get FDA labels only
curl "https://api.clinpgx.org/v1/drugLabel?drug=warfarin&source=FDA"
```

**Example Response:**
```json
[
  {
    "id": "DL001234",
    "drug": "warfarin",
    "source": "FDA",
    "sections": {
      "testing": "Consider CYP2C9 and VKORC1 genotyping...",
      "dosing": "Dose adjustment based on genotype...",
      "warnings": "Risk of bleeding in certain genotypes"
    },
    "biomarkers": ["CYP2C9", "VKORC1"],
    "testingRecommended": true,
    "labelUrl": "https://dailymed.nlm.nih.gov/...",
    "lastUpdated": "2024-01-15"
  }
]
```

### 9. Pathway Endpoint

Access pharmacokinetic and pharmacodynamic pathway diagrams and related information.

#### Get Pathway by ID

```http
GET /v1/pathway/{pathway_id}
```

**Parameters:**
- `pathway_id` (path parameter, required): ClinPGx pathway identifier

**Example:**
```bash
curl "https://api.clinpgx.org/v1/pathway/PA146123006"
```

#### Search Pathways

```http
GET /v1/pathway?drug={drug_name}&gene={gene}
```

**Parameters:**
- `drug` (query parameter, optional): Drug name
- `gene` (query parameter, optional): Gene symbol

**Example:**
```bash
curl "https://api.clinpgx.org/v1/pathway?drug=warfarin"
```

**Example Response:**
```json
{
  "id": "PA146123006",
  "name": "Warfarin Pharmacokinetics and Pharmacodynamics",
  "drugs": ["warfarin"],
  "genes": ["CYP2C9", "VKORC1", "CYP4F2", "GGCX"],
  "description": "Warfarin is metabolized primarily by CYP2C9...",
  "diagramUrl": "https://www.clinpgx.org/pathway/...",
  "steps": [
    {
      "step": 1,
      "process": "Absorption",
      "genes": []
    },
    {
      "step": 2,
      "process": "Metabolism",
      "genes": ["CYP2C9", "CYP2C19"]
    },
    {
      "step": 3,
      "process": "Target interaction",
      "genes": ["VKORC1"]
    }
  ]
}
```

## Query Patterns and Examples

### Common Query Patterns

#### 1. Patient Medication Review

Query all gene-drug pairs for medications a patient is using:

```python
import requests

patient_meds = ["clopidogrel", "simvastatin", "codeine"]
patient_genes = {"CYP2C19": "*1/*2", "CYP2D6": "*1/*1", "SLCO1B1": "*1/*5"}

for med in patient_meds:
    for gene in patient_genes:
        response = requests.get(
            "https://api.clinpgx.org/v1/geneDrugPair",
            params={"gene": gene, "drug": med}
        )
        pairs = response.json()
        # Check for interactions
```

#### 2. Actionable Gene Panel

Find all genes with CPIC Level A recommendations:

```python
response = requests.get(
    "https://api.clinpgx.org/v1/geneDrugPair",
    params={"cpicLevel": "A"}
)
actionable_pairs = response.json()

genes = set(pair['gene'] for pair in actionable_pairs)
print(f"Panel should include: {sorted(genes)}")
```

#### 3. Population Frequency Analysis

Compare allele frequencies across different populations:

```python
alleles = requests.get(
    "https://api.clinpgx.org/v1/allele",
    params={"gene": "CYP2D6"}
).json()

# Calculate phenotype frequency
pm_freq = {}  # Poor metabolizer frequency
for allele in alleles:
    if allele['function'] == 'No function':
        for pop, freq in allele['frequencies'].items():
            pm_freq[pop] = pm_freq.get(pop, 0) + freq
```

#### 4. Drug Safety Screening

Check for high-risk gene-drug associations:

```python
# Screen for HLA-B*57:01 before using abacavir
response = requests.get(
    "https://api.clinpgx.org/v1/geneDrugPair",
    params={"gene": "HLA-B", "drug": "abacavir"}
)
pair = response.json()[0]

if pair['cpicLevel'] == 'A':
    print("CRITICAL: Do not use if HLA-B*57:01 positive")
```

## Error Handling

### Common Error Responses

#### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "Gene 'INVALID' does not exist"
}
```

#### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded",
  "message": "Maximum 2 requests per second allowed"
}
```

### Recommended Error Handling Patterns

```python
import requests
import time

def safe_query(url, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                time.sleep(0.5)  # Rate limiting
                return response.json()
            elif response.status_code == 429:
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            elif response.status_code == 404:
                print("Resource not found")
                return None
            else:
                response.raise_for_status()

        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise

    return None
```

## Best Practices

### Rate Limiting
- Implement a 500 ms delay between requests (max 2 requests per second)
- Use exponential backoff for rate limit errors
- Consider caching results for frequently accessed data
- For batch operations, please contact api@clinpgx.org

### Caching Strategy
```python
import json
from pathlib import Path

def cached_query(cache_file, query_func, *args, **kwargs):
    cache_path = Path(cache_file)

    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)

    result = query_func(*args, **kwargs)

    if result:
        with open(cache_path, 'w') as f:
            json.dump(result, f)

    return result
```

### Batch Processing
```python
import time

def batch_gene_query(genes, delay=0.5):
    results = {}
    for gene in genes:
        response = requests.get(f"https://api.clinpgx.org/v1/gene/{gene}")
        if response.status_code == 200:
            results[gene] = response.json()
        time.sleep(delay)
    return results
```

## Data Schema Definitions

### Gene Object
```typescript
{
  id: string;              // ClinPGx Gene ID
  symbol: string;          // HGNC Gene Symbol
  name: string;            // Full Gene Name
  chromosome: string;      // Chromosome Location
  function: string;        // Pharmacogenomic Function
  clinicalAnnotations: number;  // Annotation Count
  relatedDrugs: string[];  // Related Drugs
}
```

### Drug Object
```typescript
{
  id: string;              // ClinPGx Drug ID
  name: string;            // Generic Name
  tradeNames: string[];    // Trade Names
  drugClasses: string[];   // Therapeutic Classes
  indication: string;      // Primary Indication
  relatedGenes: string[];  // Pharmacogenes
}
```

### Gene-Drug Pair Object
```typescript
{
  gene: string;            // Gene Symbol
  drug: string;            // Drug Name
  sources: string[];       // CPIC, FDA, DPWG, etc.
  cpicLevel: string;       // A, B, C, D
  evidenceLevel: string;   // 1A, 1B, 2A, 2B, 3, 4
  hasGuideline: boolean;   // Whether a clinical guideline exists
}
```

### Allele Object
```typescript
{
  name: string;            // Allele Name (e.g., CYP2D6*4)
  gene: string;            // Gene Symbol
  function: string;        // Normal/Decreased/No/Increased/Uncertain
  activityScore: number;   // 0.0 to 2.0+
  frequencies: {           // Population Frequencies
    [population: string]: number;
  };
  definingVariants: string[];  // rsIDs or descriptions
}
```

## API Stability and Versioning

### Current Status
- API Version: v1
- Stability: Beta - Endpoints are stable, parameters may change
- Update Monitoring: https://blog.clinpgx.org/

### Migrating from PharmGKB
Starting July 2025, PharmGKB URLs will redirect to ClinPGx. Please update references:
- Old: `https://api.pharmgkb.org/`
- New: `https://api.clinpgx.org/`

### Future Changes
- Watch for API v2 announcements
- Breaking changes will be announced on the ClinPGx blog
- Production applications are advised to lock versions

## Support and Contact

- **API Issues**: api@clinpgx.org
- **Documentation Address**: https://api.clinpgx.org/
- **FAQ**: https://www.clinpgx.org/page/faqs
- **Blog**: https://blog.clinpgx.org/
- **CPIC Guidelines**: https://cpicpgx.org/

## Related Resources

- **PharmCAT**: Pharmacogenomics Clinical Annotation Tool
- **PharmVar**: Pharmacogene Variation Consortium
- **CPIC**: Clinical Pharmacogenetics Implementation Consortium
- **DPWG**: Dutch Pharmacogenetics Working Group
- **ClinGen**: Clinical Genome Resource