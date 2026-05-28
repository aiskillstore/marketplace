# FDA Other Databases - Substances and NSDE

This reference guide covers FDA substance-related and other specialized API endpoints accessible via openFDA.

## Overview

FDA maintains additional databases that store substance information down to the molecular level. These databases support regulatory activities for drugs, biologics, medical devices, food, and cosmetics.

## Available Endpoints

### 1. Substance Data

**Endpoint**: `https://api.fda.gov/other/substance.json`

**Purpose**: Access molecular-level substance information for internal and external use. This includes information about active pharmaceutical ingredients, excipients, and other substances used in FDA-regulated products.

**Data Source**: FDA Global Substance Registration System (GSRS)

**Key Fields**:
- `uuid` - Unique Substance Identifier (UUID)
- `approvalID` - FDA Unique Ingredient Identifier (UNII)
- `approved` - Approval date
- `substanceClass` - Substance type (Chemical, Protein, Nucleic Acid, Polymer, etc.)
- `names` - Array of substance names
- `names.name` - Name text
- `names.type` - Name type (Systematic, Brand, Common, etc.)
- `names.preferred` - Whether it is the preferred name
- `codes` - Array of substance codes
- `codes.code` - Code value
- `codes.codeSystem` - Code system (CAS, ECHA, EINECS, etc.)
- `codes.type` - Code type
- `relationships` - Array of substance relationships
- `relationships.type` - Relationship type (ACTIVE MOIETY, METABOLITE, IMPURITY, etc.)
- `relationships.relatedSubstance` - Reference to related substance
- `moieties` - Molecular moieties
- `properties` - Array of physicochemical properties
- `properties.name` - Property name
- `properties.value` - Property value
- `properties.propertyType` - Property type
- `structure` - Chemical structure information
- `structure.smiles` - SMILES notation
- `structure.inchi` - InChI string
- `structure.inchiKey` - InChI key
- `structure.formula` - Molecular formula
- `structure.molecularWeight` - Molecular weight
- `modifications` - Structural modifications (for proteins, etc.)
- `protein` - Protein-specific information
- `protein.subunits` - Protein subunits
- `protein.sequenceType` - Sequence type
- `nucleicAcid` - Nucleic acid information
- `nucleicAcid.subunits` - Sequence subunits
- `polymer` - Polymer information
- `mixture` - Mixture components
- `mixture.components` - Component substances
- `tags` - Substance tags
- `references` - Literature references

**Substance Classes**:
- **Chemical** - Small molecules with defined chemical structures
- **Protein** - Proteins and peptides
- **Nucleic Acid** - DNA, RNA, oligonucleotides
- **Polymer** - Polymeric substances
- **Structurally Diverse** - Complex mixtures with diverse structures, botanical extracts
- **Mixture** - Well-defined mixtures
- **Concept** - Abstract concepts (e.g., classification groups)

**Common Scenarios**:
- Active ingredient identification
- Molecular structure queries
- UNII code resolution
- Chemical identifier mapping (e.g., CAS to UNII)
- Substance relationship analysis
- Excipient identification
- Botanical substance information
- Characterization of proteins and biologics

**Query Examples**:
```python
import requests

api_key = "YOUR_API_KEY"
url = "https://api.fda.gov/other/substance.json"

# Query substance by UNII code
params = {
    "api_key": api_key,
    "search": "approvalID:R16CO5Y76E",  # Aspirin UNII
    "limit": 1
}

response = requests.get(url, params=params)
data = response.json()
```

```python
# Search by substance name
params = {
    "api_key": api_key,
    "search": "names.name:acetaminophen",
    "limit": 5
}
```

```python
# Find substance by CAS number
params = {
    "api_key": api_key,
    "search": "codes.code:50-78-2",  # Aspirin CAS
    "limit": 1
}
```

```python
# Get only chemical class substances
params = {
    "api_key": api_key,
    "search": "substanceClass:chemical",
    "limit": 100
}
```

```python
# Search by molecular formula
params = {
    "api_key": api_key,
    "search": "structure.formula:C8H9NO2",  # Acetaminophen
    "limit": 10
}
```

```python
# Find protein class substances
params = {
    "api_key": api_key,
    "search": "substanceClass:protein",
    "limit": 50
}
```

### 2. NSDE (National Substance Data Index)

**Endpoint**: `https://api.fda.gov/other/nsde.json`

**Purpose**: Access historical substance data from legacy National Drug Code (NDC) Directory entries. This endpoint provides substance information as it appeared in historical drug listing records.

**Note**: This database is primarily for historical reference. For current substance information, use the Substance Data endpoint.

**Key Fields**:
- `proprietary_name` - Product proprietary name (Brand name)
- `nonproprietary_name` - Non-proprietary name (Generic name)
- `dosage_form` - Dosage form
- `route` - Route of administration
- `company_name` - Company name
- `substance_name` - Substance name
- `active_numerator_strength` - Active ingredient strength (numerator)
- `active_ingred_unit` - Active ingredient unit
- `pharm_classes` - Pharmacologic classes
- `dea_schedule` - DEA controlled substance schedule

**Common Scenarios**:
- Historical drug formulation research
- Legacy system integration
- Historical substance name mapping
- Pharmacy history research

**Query Examples**:
```python
# Search by substance name
params = {
    "api_key": api_key,
    "search": "substance_name:ibuprofen",
    "limit": 20
}

response = requests.get("https://api.fda.gov/other/nsde.json", params=params)
```

```python
# Find controlled substances by DEA schedule
params = {
    "api_key": api_key,
    "search": "dea_schedule:CII",
    "limit": 50
}
```

## Integration Tips

### UNII to CAS Mapping

```python
def get_substance_identifiers(unii, api_key):
    """
    Given a UNII code, retrieve all identifiers for that substance.

    Parameters:
        unii: FDA Unique Ingredient Identifier
        api_key: FDA API Key

    Returns:
        Dictionary containing substance identifiers
    """
    import requests

    url = "https://api.fda.gov/other/substance.json"
    params = {
        "api_key": api_key,
        "search": f"approvalID:{unii}",
        "limit": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    substance = data["results"][0]

    identifiers = {
        "unii": substance.get("approvalID"),
        "uuid": substance.get("uuid"),
        "preferred_name": None,
        "cas_numbers": [],
        "other_codes": {}
    }

    # Extract names
    if "names" in substance:
        for name in substance["names"]:
            if name.get("preferred"):
                identifiers["preferred_name"] = name.get("name")
                break
        if not identifiers["preferred_name"] and len(substance["names"]) > 0:
            identifiers["preferred_name"] = substance["names"][0].get("name")

    # Extract codes
    if "codes" in substance:
        for code in substance["codes"]:
            code_system = code.get("codeSystem", "").upper()
            code_value = code.get("code")

            if "CAS" in code_system:
                identifiers["cas_numbers"].append(code_value)
            else:
                if code_system not in identifiers["other_codes"]:
                    identifiers["other_codes"][code_system] = []
                identifiers["other_codes"][code_system].append(code_value)

    return identifiers
```

### Chemical Structure Query

```python
def get_chemical_structure(substance_name, api_key):
    """
    Retrieve chemical structure information for a substance.

    Parameters:
        substance_name: Substance name
        api_key: FDA API Key

    Returns:
        Dictionary containing structure information
    """
    import requests

    url = "https://api.fda.gov/other/substance.json"
    params = {
        "api_key": api_key,
        "search": f"names.name:{substance_name}",
        "limit": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    substance = data["results"][0]

    if "structure" not in substance:
        return None

    structure = substance["structure"]

    return {
        "smiles": structure.get("smiles"),
        "inchi": structure.get("inchi"),
        "inchi_key": structure.get("inchiKey"),
        "formula": structure.get("formula"),
        "molecular_weight": structure.get("molecularWeight"),
        "substance_class": substance.get("substanceClass")
    }
```

### Substance Relationship Mapping

```python
def get_substance_relationships(unii, api_key):
    """
    Retrieve all related substances (metabolites, active moieties, etc.).

    Parameters:
        unii: FDA Unique Ingredient Identifier
        api_key: FDA API Key

    Returns:
        Dictionary of relationships organized by type
    """
    import requests

    url = "https://api.fda.gov/other/substance.json"
    params = {
        "api_key": api_key,
        "search": f"approvalID:{unii}",
        "limit": 1
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    substance = data["results"][0]

    relationships = {}

    if "relationships" in substance:
        for rel in substance["relationships"]:
            rel_type = rel.get("type")
            if rel_type not in relationships:
                relationships[rel_type] = []

            related = {
                "uuid": rel.get("relatedSubstance", {}).get("uuid"),
                "unii": rel.get("relatedSubstance", {}).get("approvalID"),
                "name": rel.get("relatedSubstance", {}).get("refPname")
            }
            relationships[rel_type].append(related)

    return relationships
```

### Active Ingredient Extraction

```python
def find_active_ingredients_by_product(product_name, api_key):
    """
    Find active ingredients in a drug product.

    Parameters:
        product_name: Drug product name
        api_key: FDA API Key

    Returns:
        List of active ingredient UNIIs and names
    """
    import requests

    # First search the drug label database
    label_url = "https://api.fda.gov/drug/label.json"
    label_params = {
        "api_key": api_key,
        "search": f"openfda.brand_name:{product_name}",
        "limit": 1
    }

    response = requests.get(label_url, params=label_params)
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    label = data["results"][0]

    # Extract UNII from the openfda section
    active_ingredients = []

    if "openfda" in label:
        openfda = label["openfda"]

        # Get UNII list
        unii_list = openfda.get("unii", [])
        generic_names = openfda.get("generic_name", [])

        for i, unii in enumerate(unii_list):
            ingredient = {"unii": unii}
            if i < len(generic_names):
                ingredient["name"] = generic_names[i]

            # Get additional substance information
            substance_info = get_substance_identifiers(unii, api_key)
            if substance_info:
                ingredient.update(substance_info)

            active_ingredients.append(ingredient)

    return active_ingredients
```

## Best Practices

1. **Use UNII as the primary identifier** - It is the most consistent identifier across FDA databases.
2. **Map between identifier systems** - Use CAS, UNII, and InChI Key for cross-referencing.
3. **Handle substance variants** - Different salt forms and hydrates have different UNIIs.
4. **Check substance classes** - Different classes have different data structures.
5. **Validate chemical structures** - SMILES and InChI should be verified.
6. **Consider substance relationships** - The distinction between Active Moiety and salt forms is important.
7. **Use preferred names** - These are more consistent than brand names.
8. **Cache substance data** - Substance information changes infrequently.
9. **Cross-reference with other endpoints** - Link substances to drugs/products.
10. **Handle mixture components** - Complex products contain multiple components.

## UNII System

The FDA Unique Ingredient Identifier (UNII) system provides:
- **Unique Identifier** - Each substance gets one UNII.
- **Substance Specificity** - Different forms (salts, hydrates) get different UNIIs.
- **Global Recognition** - Internationally used.
- **Stability** - UNIIs do not change once assigned.
- **Free Access** - No license required.

**UNII Format**: 10-character alphanumeric code (e.g., `R16CO5Y76E`)

## Substance Class Descriptions

### Chemical
- Traditional small molecule organic drugs.
- Defined molecular structure.
- Includes organic and inorganic compounds.
- Provides SMILES, InChI, and molecular formula.

### Protein
- Peptides and proteins.
- Provides sequence information.
- May have post-translational modifications.
- Includes antibodies, enzymes, and hormones.

### Nucleic Acid
- DNA and RNA sequences.
- Oligonucleotides.
- Antisense, siRNA, mRNA.
- Provides sequence data.

### Polymer
- Synthetic and natural polymers.
- Structural repeat units.
- Molecular weight distribution.
- Used as excipients and active ingredients.

### Structurally Diverse
- Complex natural products.
- Botanical extracts.
- Materials without a single molecular structure.
- Characterized by source and composition.

### Mixture
- Well-defined combinations of substances.
- Fixed or variable component ratios.
- Each component is traceable.

## Additional Resources

- FDA Substance Registration System: https://fdasis.nlm.nih.gov/srs/
- UNII Search: https://precision.fda.gov/uniisearch
- OpenFDA Other APIs: https://open.fda.gov/apis/other/
- API Basics: See `api_basics.md` in the reference directory
- Python Example: See `scripts/fda_substance_query.py`