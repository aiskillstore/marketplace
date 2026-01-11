# External API Validation Reference

## Overview

Step 5 validates and enriches extracted data using external scientific databases. This ensures taxonomic names are standardized, locations are geocoded, and chemical/gene identifiers are canonical.

## Available APIs

### Biological Taxonomy

#### GBIF (Global Biodiversity Information Facility)

**Use for:** General biological taxonomy (animals, plants, fungi, etc.)

**Function:** `validate_gbif_taxonomy(scientific_name)`

**Returns:**
- Matched canonical name
- Full scientific name with authority
- Taxonomic hierarchy (kingdom, phylum, class, order, family, genus)
- GBIF ID
- Match confidence and type
- Taxonomic status

**Example:**
```python
validate_gbif_taxonomy("Apis melifera")
# Returns:
{
  "matched_name": "Apis mellifera",
  "scientific_name": "Apis mellifera Linnaeus, 1758",
  "rank": "SPECIES",
  "kingdom": "Animalia",
  "phylum": "Arthropoda",
  "class": "Insecta",
  "order": "Hymenoptera",
  "family": "Apidae",
  "genus": "Apis",
  "gbif_id": 1340278,
  "confidence": 100,
  "match_type": "EXACT"
}
```

**No API key required** - Free and unlimited

**Documentation:** https://www.gbif.org/developer/species

#### World Flora Online (WFO)

**Use for:** Plant taxonomy specifically

**Function:** `validate_wfo_plant(scientific_name)`

**Returns:**
- Matched name
- Scientific name with authors
- Family
- WFO ID
- Taxonomic status

**Example:**
```python
validate_wfo_plant("Magnolia grandiflora")
# Returns:
{
  "matched_name": "Magnolia grandiflora",
  "scientific_name": "Magnolia grandiflora L.",
  "authors": "L.",
  "family": "Magnoliaceae",
  "wfo_id": "wfo-0000988234",
  "status": "Accepted"
}
```

**No API key required** - Free

**Documentation:** http://www.worldfloraonline.org/

### Geography

#### GeoNames

**Use for:** Location validation and standardization

**Function:** `validate_geonames(location, country=None)`

**Returns:**
- Matched place name
- Country name and code
- Administrative divisions (state, province)
- Latitude/longitude
- GeoNames ID

**Example:**
```python
validate_geonames("São Paulo", country="BR")
# Returns:
{
  "matched_name": "São Paulo",
  "country": "Brazil",
  "country_code": "BR",
  "admin1": "São Paulo",
  "admin2": None,
  "latitude": "-23.5475",
  "longitude": "-46.63611",
  "geonames_id": 3448439
}
```

**Requires free account:** Register at https://www.geonames.org/login

**Setup:**
1. Create account
2. Enable web services in account settings
3. Set environment variable: `export GEONAMES_USERNAME='your-username'`

**Rate limit:** Free tier allows reasonable usage

**Documentation:** https://www.geonames.org/export/web-services.html

#### OpenStreetMap Nominatim

**Use for:** Geocoding addresses to coordinates

**Function:** `geocode_location(address)`

**Returns:**
- Display name (formatted address)
- Latitude/longitude
- OSM type and ID
- Place rank

**Example:**
```python
geocode_location("Field Museum, Chicago, IL")
# Returns:
{
  "display_name": "Field Museum, 1400, South Lake Shore Drive, Chicago, Illinois, 60605, United States",
  "latitude": "41.8662",
  "longitude": "-87.6169",
  "osm_type": "way",
  "osm_id": 54856789,
  "place_rank": 30
}
```

**No API key required** - Free

**Important:** Add 1-second delays between requests (implemented in script)

**Documentation:** https://nominatim.org/release-docs/latest/api/Overview/

### Chemistry

#### PubChem

**Use for:** Chemical compound validation

**Function:** `validate_pubchem_compound(compound_name)`

**Returns:**
- PubChem CID (compound ID)
- Molecular formula
- PubChem URL

**Example:**
```python
validate_pubchem_compound("aspirin")
# Returns:
{
  "cid": 2244,
  "molecular_formula": "C9H8O4",
  "pubchem_url": "https://pubchem.ncbi.nlm.nih.gov/compound/2244"
}
```

**No API key required** - Free

**Documentation:** https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest

### Genetics

#### NCBI Gene

**Use for:** Gene validation

**Function:** `validate_ncbi_gene(gene_symbol, organism=None)`

**Returns:**
- NCBI Gene ID
- NCBI URL

**Example:**
```python
validate_ncbi_gene("BRCA1", organism="Homo sapiens")
# Returns:
{
  "gene_id": "672",
  "ncbi_url": "https://www.ncbi.nlm.nih.gov/gene/672"
}
```

**No API key required** - Free

**Rate limit:** Max 3 requests/second

**Documentation:** https://www.ncbi.nlm.nih.gov/books/NBK25500/

## Configuration

### API Config File Structure

Create `my_api_config.json` based on `assets/api_config_template.json`:

```json
{
  "field_mappings": {
    "species": {
      "api": "gbif_taxonomy",
      "output_field": "validated_species",
      "description": "Validate species names against GBIF"
    },
    "location": {
      "api": "geocode",
      "output_field": "coordinates"
    }
  },

  "nested_field_mappings": {
    "records.plant_species": {
      "api": "wfo_plants",
      "output_field": "validated_plant_taxonomy"
    },
    "records.location": {
      "api": "geocode",
      "output_field": "coordinates"
    }
  }
}
```

### Field Mapping Parameters

**Required:**
- `api` - API name (see list above)
- `output_field` - Name for validated data

**Optional:**
- `description` - Documentation
- `extra_params` - Additional API-specific parameters

## Adding Custom APIs

To add a new validation API:

1. **Create validator function** in `scripts/05_validate_with_apis.py`:

```python
def validate_custom_api(value: str, extra_param: str = None) -> Optional[Dict]:
    """
    Validate value using custom API.

    Args:
        value: The value to validate
        extra_param: Optional additional parameter

    Returns:
        Dictionary with validated data or None if not found
    """
    try:
        # Make API request
        response = requests.get(f"https://api.example.com/{value}")
        if response.status_code == 200:
            data = response.json()
            return {
                'validated_value': data.get('canonical_name'),
                'api_id': data.get('id'),
                'additional_info': data.get('info')
            }
    except Exception as e:
        print(f"Custom API error: {e}")

    return None
```

2. **Register in API_VALIDATORS** dictionary:

```python
API_VALIDATORS = {
    'gbif_taxonomy': validate_gbif_taxonomy,
    'wfo_plants': validate_wfo_plant,
    # ... existing validators ...
    'custom_api': validate_custom_api,  # Add here
}
```

3. **Use in config file:**

```json
{
  "field_mappings": {
    "your_field": {
      "api": "custom_api",
      "output_field": "validated_field",
      "extra_params": {
        "extra_param": "value"
      }
    }
  }
}
```

## Rate Limiting

The script implements rate limiting to respect API usage policies:

**Default delays (built into script):**
- GeoNames: 0.5 seconds
- Nominatim: 1.0 second (required)
- WFO: 1.0 second
- Others: 0.5 seconds

**Modify delays if needed** in `scripts/05_validate_with_apis.py`:

```python
# In main() function
if not args.skip_validation:
    time.sleep(0.5)  # Adjust this value
```

## Error Handling

APIs may fail for various reasons:

**Common errors:**
- Connection timeout
- Rate limit exceeded
- Invalid API key
- Malformed query
- No match found

**Script behavior:**
- Continues processing on error
- Logs error to console
- Sets validated field to None
- Original extracted value preserved

**Retry logic:**
- 3 retries with exponential backoff
- Implemented for network errors
- Not for "no match found" errors

## Best Practices

1. **Start with test run:**
   ```bash
   python scripts/05_validate_with_apis.py \
     --input cleaned_data.json \
     --apis my_api_config.json \
     --skip-validation \
     --output test_structure.json
   ```

2. **Validate subset first:**
   - Test on 10 papers before full run
   - Verify API connections work
   - Check output structure

3. **Monitor API usage:**
   - Track request counts for paid APIs
   - Respect rate limits
   - Consider caching results

4. **Handle failures gracefully:**
   - Original data is never lost
   - Can re-run validation separately
   - Manually fix failed validations if needed

5. **Optimize API calls:**
   - Only validate fields that need standardization
   - Use cached results when re-running
   - Batch similar queries when possible

## Troubleshooting

### GeoNames "Service disabled" error
- Check account email is verified
- Enable web services in account settings
- Wait up to 1 hour after enabling

### Nominatim rate limit errors
- Script includes 1-second delays
- Don't run multiple instances
- Consider using local Nominatim instance

### NCBI errors
- Reduce request frequency
- Add longer delays
- Use E-utilities API key (optional, increases limit)

### No matches found
- Check spelling and formatting
- Try variations of name
- Some names may not be in database
- Consider manual curation for important cases
