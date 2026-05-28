# FDA Animal & Veterinary Database

This reference document covers the FDA Animal & Veterinary drug API endpoints accessible via openFDA.

## Overview

The FDA Animal & Veterinary database provides information on adverse drug events related to animal drugs and veterinary medical products. These databases help monitor the safety of products used in pets, livestock, and other animals.

## Available Endpoints

### Animal Drug Adverse Events

**Endpoint**: `https://api.fda.gov/animalandveterinary/event.json`

**Purpose**: Access reports of side effects, product use errors, product quality issues, and therapeutic failures related to animal drugs.

**Data Source**: FDA Center for Veterinary Medicine (CVM) Adverse Event Reporting System

**Key Fields**:
- `unique_aer_id_number` - Unique adverse event report identifier
- `report_id` - Report ID number
- `receiver.organization` - Organization receiving the report
- `receiver.street_address` - Receiver street address
- `receiver.city` - Receiver city
- `receiver.state` - Receiver state/province
- `receiver.postal_code` - Receiver postal code
- `receiver.country` - Receiver country
- `primary_reporter` - Primary reporter type (e.g., veterinarian, examiner)
- `onset_date` - Adverse event onset date
- `animal.species` - Affected animal species
- `animal.gender` - Animal gender
- `animal.age.min` - Minimum age
- `animal.age.max` - Maximum age
- `animal.age.unit` - Age unit (days, months, years)
- `animal.age.qualifier` - Age qualifier
- `animal.breed.is_crossbred` - Whether crossbred/hybrid
- `animal.breed.breed_component` - Breed component
- `animal.weight.min` - Minimum weight
- `animal.weight.max` - Maximum weight
- `animal.weight.unit` - Weight unit
- `animal.female_animal_physiological_status` - Physiological status
- `animal.reproductive_status` - Reproductive status (neutered/spayed)
- `drug` - Array of drugs involved
- `drug.active_ingredients` - Active ingredients
- `drug.active_ingredients.name` - Ingredient name
- `drug.active_ingredients.dose` - Dosage information
- `drug.brand_name` - Brand name
- `drug.manufacturer.name` - Manufacturer
- `drug.administered_by` - Who administered the drug
- `drug.route` - Route of administration
- `drug.dosage_form` - Dosage form
- `drug.atc_vet_code` - ATCvet code
- `reaction` - Array of adverse reactions
- `reaction.veddra_version` - VeDDRA dictionary version
- `reaction.veddra_term_code` - VeDDRA term code
- `reaction.veddra_term_name` - VeDDRA term name
- `reaction.accuracy` - Diagnostic accuracy
- `reaction.number_of_animals_affected` - Number of animals affected
- `reaction.number_of_animals_treated` - Number of animals treated
- `outcome.medical_status` - Medical outcome
- `outcome.number_of_animals_affected` - Number of animals affected by this outcome
- `serious_ae` - Whether it is a serious adverse event
- `health_assessment_prior_to_exposure.assessed_by` - Person assessing health status prior to exposure
- `health_assessment_prior_to_exposure.condition` - Health condition
- `treated_for_ae` - Whether treated for the adverse event
- `time_between_exposure_and_onset` - Time between exposure and onset
- `duration.unit` - Duration unit
- `duration.value` - Duration value

**Common Animal Species**:
- Dog (Canis lupus familiaris)
- Cat (Felis catus)
- Horse (Equus caballus)
- Cattle (Bos taurus)
- Pig (Sus scrofa domesticus)
- Chicken (Gallus gallus domesticus)
- Sheep (Ovis aries)
- Goat (Capra aegagrus hircus)
- And many other species

**Common Use Cases**:
- Pharmacovigilance
- Product safety monitoring
- Adverse event trend analysis
- Drug safety comparison
- Species-specific safety studies
- Breed predisposition studies

**Query Examples**:
```python
import requests

api_key = "YOUR_API_KEY"
url = "https://api.fda.gov/animalandveterinary/event.json"

# Find adverse events for dogs
params = {
    "api_key": api_key,
    "search": "animal.species:Dog",
    "limit": 10
}

response = requests.get(url, params=params)
data = response.json()
```

```python
# Search for adverse events for a specific drug
params = {
    "api_key": api_key,
    "search": "drug.brand_name:*flea+collar*",
    "limit": 20
}
```

```python
# Count most common reactions by species
params = {
    "api_key": api_key,
    "search": "animal.species:Cat",
    "count": "reaction.veddra_term_name.exact"
}
```

```python
# Find serious adverse events
params = {
    "api_key": api_key,
    "search": "serious_ae:true+AND+outcome.medical_status:Died",
    "limit": 50,
    "sort": "onset_date:desc"
}
```

```python
# Search by active ingredient
params = {
    "api_key": api_key,
    "search": "drug.active_ingredients.name:*ivermectin*",
    "limit": 25
}
```

```python
# Find events for a specific breed
params = {
    "api_key": api_key,
    "search": "animal.breed.breed_component:*Labrador*",
    "limit": 30
}
```

```python
# Get events by route of administration
params = {
    "api_key": api_key,
    "search": "drug.route:*topical*",
    "limit": 40
}
```

## VeDDRA - Veterinary Dictionary for Drug Related Affairs

The Veterinary Dictionary for Drug Related Affairs (VeDDRA) is a standardized international veterinary terminology used for adverse event reporting. It provides:

- Standardized veterinary adverse reaction terms
- Hierarchical organization of terms
- Species-specific terminology
- International harmonization

**VeDDRA Term Structure**:
- Terms are organized by hierarchy
- Each term has a unique code
- Terms are applicable to corresponding species
- Multiple versions exist (please check the `veddra_version` field)

## Integration Tips

### Species-Specific Adverse Event Analysis

```python
def analyze_species_adverse_events(species, drug_name, api_key):
    """
    Analyzes adverse events for a specific drug in a specific species.

    Parameters:
        species: Animal species (e.g., "Dog", "Cat", "Horse")
        drug_name: Drug brand name or active ingredient
        api_key: FDA API key

    Returns:
        Dictionary containing analysis results
    """
    import requests
    from collections import Counter

    url = "https://api.fda.gov/animalandveterinary/event.json"
    params = {
        "api_key": api_key,
        "search": f"animal.species:{species}+AND+drug.brand_name:*{drug_name}*",
        "limit": 1000
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        return {"error": "No results found"}

    results = data["results"]

    # Collect reactions and outcomes
    reactions = []
    outcomes = []
    serious_count = 0

    for event in results:
        if "reaction" in event:
            for reaction in event["reaction"]:
                if "veddra_term_name" in reaction:
                    reactions.append(reaction["veddra_term_name"])

        if "outcome" in event:
            for outcome in event["outcome"]:
                if "medical_status" in outcome:
                    outcomes.append(outcome["medical_status"])

        if event.get("serious_ae") == "true":
            serious_count += 1

    reaction_counts = Counter(reactions)
    outcome_counts = Counter(outcomes)

    return {
        "total_events": len(results),
        "serious_events": serious_count,
        "most_common_reactions": reaction_counts.most_common(10),
        "outcome_distribution": dict(outcome_counts),
        "serious_percentage": round((serious_count / len(results)) * 100, 2) if len(results) > 0 else 0
    }
```

### Breed Predisposition Study

```python
def analyze_breed_predisposition(reaction_term, api_key, min_events=5):
    """
    Identifies breed predisposition for a specific adverse reaction.

    Parameters:
        reaction_term: VeDDRA reaction term to analyze
        api_key: FDA API key
        min_events: Minimum number of events required to include a breed

    Returns:
        List of breeds with event counts
    """
    import requests
    from collections import Counter

    url = "https://api.fda.gov/animalandveterinary/event.json"
    params = {
        "api_key": api_key,
        "search": f"reaction.veddra_term_name:*{reaction_term}*",
        "limit": 1000
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data:
        return []

    breeds = []
    for event in data["results"]:
        if "animal" in event and "breed" in event["animal"]:
            breed_info = event["animal"]["breed"]
            if "breed_component" in breed_info:
                if isinstance(breed_info["breed_component"], list):
                    breeds.extend(breed_info["breed_component"])
                else:
                    breeds.append(breed_info["breed_component"])

    breed_counts = Counter(breeds)

    # Filter by minimum event count
    filtered_breeds = [
        {"breed": breed, "count": count}
        for breed, count in breed_counts.most_common()
        if count >= min_events
    ]

    return filtered_breeds
```

### Drug Safety Comparative Analysis

```python
def compare_drug_safety(drug_list, species, api_key):
    """
    Compares the safety profiles of multiple drugs in a specific species.

    Parameters:
        drug_list: List of drug names to compare
        species: Animal species
        api_key: FDA API key

    Returns:
        Dictionary of drug comparisons
    """
    import requests

    url = "https://api.fda.gov/animalandveterinary/event.json"
    comparison = {}

    for drug in drug_list:
        params = {
            "api_key": api_key,
            "search": f"animal.species:{species}+AND+drug.brand_name:*{drug}*",
            "limit": 1000
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "results" in data:
            results = data["results"]
            serious = sum(1 for r in results if r.get("serious_ae") == "true")
            deaths = sum(
                1 for r in results
                if "outcome" in r
                and any(o.get("medical_status") == "Died" for o in r["outcome"])
            )

            comparison[drug] = {
                "total_events": len(results),
                "serious_events": serious,
                "deaths": deaths,
                "serious_rate": round((serious / len(results)) * 100, 2) if len(results) > 0 else 0,
                "death_rate": round((deaths / len(results)) * 100, 2) if len(results) > 0 else 0
            }

    return comparison
```

## Best Practices

1. **Use Standard Species Names** - Using full scientific names or common names works best.
2. **Consider Breed Variations** - Spelling and naming conventions may vary.
3. **Check VeDDRA Versions** - Terminology may change between different versions.
4. **Account for Reporter Bias** - Differences exist in how veterinarians versus pet owners report.
5. **Filter by Serious Events** - Focus on clinically significant reactions.
6. **Consider Animal Demographics** - Age, weight, and reproductive status are highly important.
7. **Track Temporal Patterns** - Seasonal fluctuations may exist.
8. **Cross-Reference Products** - The same active ingredient may correspond to multiple brands.
9. **Analyze by Route** - Topical vs. systemic administration has different safety implications.
10. **Consider Species Differences** - Drugs affect different species differently.

## Reporting Sources

Animal drug adverse event reports come from:
- **Veterinarians** - Professional medical observations
- **Animal Owners** - Direct observations and concerns
- **Pharmaceutical Companies** - Required post-marketing surveillance
- **FDA Field Personnel** - Official investigations
- **Research Institutions** - Clinical studies
- **Other Sources** - Various origins

Reporting thresholds and levels of detail may vary across different sources.

## Additional Resources

- OpenFDA Animal & Veterinary API: https://open.fda.gov/apis/animalandveterinary/
- FDA Center for Veterinary Medicine: https://www.fda.gov/animal-veterinary
- VeDDRA: https://www.veddra.org/
- API Basics: See `api_basics.md` in this reference directory
- Python Examples: See `scripts/fda_animal_query.py`