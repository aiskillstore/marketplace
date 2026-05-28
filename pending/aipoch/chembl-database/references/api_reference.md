# API Reference for ChEMBL Skill

## Resources
The `chembl_webresource_client` supports the following resources:
- `molecule`
- `target`
- `activity`
- `drug`
- `mechanism`
- `target_component`
- `drug_indication`

## Filter Syntax
Filters follow Django-style syntax:

- `exact`: Exact match
- `iexact`: Case-insensitive exact match
- `contains`: Case-sensitive containment test
- `icontains`: Case-insensitive containment test
- `gt` / `gte`: Greater than / Greater than or equal
- `lt` / `lte`: Less than / Less than or equal
- `in`: In a given list
- `isnull`: Is null (True/False)

### Examples
- `pref_name__icontains='aspirin'`
- `molecular_weight__gte=200`
- `molecular_weight__lte=500`

## Caching
The client includes built-in caching for 24 hours to reduce load on the ChEMBL API.
