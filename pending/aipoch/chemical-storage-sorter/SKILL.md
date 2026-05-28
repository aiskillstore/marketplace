---
name: chemical-storage-sorter
description: Sort laboratory chemicals into safe storage groups by hazard classification (acids, bases, oxidizers, flammables, toxics). Identifies incompatible pairs, generates storage plans with warnings, and supports OSHA/NFPA compliance for lab safety.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Chemical Storage Sorter

Organize laboratory chemicals into safe storage groups based on chemical compatibility and hazard classification. Prevents dangerous reactions by identifying incompatible pairs and providing segregation guidelines compliant with OSHA, NFPA, and institutional safety standards.

**Key Capabilities:**
- **Automatic Chemical Classification**: Categorize chemicals into hazard groups
- **Compatibility Checking**: Identify incompatible pairs that could react dangerously
- **Storage Grouping**: Sort chemical inventories into safe storage arrangements
- **Safety Warnings**: Generate warnings for incompatible combinations
- **Regulatory Compliance**: Follow OSHA and NFPA segregation rules

---

## Input Validation

This skill accepts: a list of chemical names (comma-separated or one per line), or a single chemical name for compatibility checking. Chemical names should be standard IUPAC or common names; CAS numbers are also accepted.

If the request does not involve sorting or checking laboratory chemicals for safe storage — for example, asking to synthesize chemicals, interpret SDS documents, or provide medical advice about chemical exposure — do not proceed. Instead respond:
> "Chemical Storage Sorter is designed to classify and sort laboratory chemicals for safe storage. Please provide a list of chemical names. For other chemical safety tasks, use a more appropriate tool."

---

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the chemical list, required inputs, and any special constraints (custom classifications, lab-specific rules).
2. Validate that the request matches the documented scope; stop if the task requires unsupported assumptions.
3. Run the script or apply the documented classification path with only the inputs available.
4. Return a structured result separating assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

**Fallback:** If no chemicals are provided, respond: "No chemical list provided. Please supply chemical names via `--chemicals` or as a text list. Cannot sort without input chemicals."

---

## Core Capabilities

### 1. Chemical Classification

```python
from scripts.main import ChemicalStorageSorter
sorter = ChemicalStorageSorter()
group = sorter.classify_chemical("Hydrochloric acid")  # → "acids"
```

| Group | Examples | Storage Requirements |
|-------|----------|---------------------|
| **Acids** | HCl, H₂SO₄, HNO₃ | Acid cabinet, secondary containment |
| **Bases** | NaOH, KOH, ammonia | Base cabinet, separate from acids |
| **Oxidizers** | H₂O₂, KMnO₄, nitrates | Cool, dry, away from organics |
| **Flammables** | Ethanol, acetone, hexane | Flammable storage cabinet |
| **Toxics** | Cyanides, mercury, arsenic | Locked cabinet, limited access |
| **General** | NaCl, PBS, sucrose | Standard storage |

### 2. Compatibility Checking

```python
compatible, message = sorter.check_compatibility("Hydrochloric acid", "Sodium hydroxide")
# → False, "INCOMPATIBLE: acids cannot be stored with bases"
```

| Chemical Group | Incompatible With | Reaction Risk |
|----------------|------------------|---------------|
| **Acids** | Bases, oxidizers, cyanides | Violent neutralization, toxic gas |
| **Oxidizers** | Flammables, acids, bases | Fire, explosion |
| **Flammables** | Oxidizers, acids | Fire, combustion |

### 3. Storage Plan Generation

```python
groups = sorter.sort_chemicals(inventory)
sorter.print_storage_plan(groups)
```

---

## CLI Usage

```text
# Sort list of chemicals
python scripts/main.py --chemicals "HCl,NaOH,ethanol,H2O2"

# Check compatibility between two chemicals
python scripts/main.py --chemicals "HCl" --check "NaOH"

# List all storage groups
python scripts/main.py --list-groups
```

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--chemicals`, `-c` | string | No | Comma-separated chemical list |
| `--check` | string | No | Check compatibility with another chemical |
| `--list-groups`, `-l` | flag | No | List all storage groups |

---

## Output Requirements

Every final response must make these explicit:

- Objective or requested deliverable
- Inputs used (chemical list) and assumptions introduced
- Classification method and any manual overrides applied
- Core result: storage groups with chemicals assigned, incompatibility warnings
- Constraints and risks (tool is first-check only; always verify with SDS)
- Unresolved items and next-step checks

---

## Error Handling

- If no chemicals are provided, list the required input format and request it.
- If a chemical cannot be classified, assign to "general" and flag for manual review. Suggest: (1) provide the CAS number for lookup, (2) consult the SDS for GHS hazard classification, (3) contact the institutional safety officer.
- If `scripts/main.py` fails, report the failure point and provide manual classification fallback using the hazard group table above.
- Do not fabricate classifications or compatibility results.

---

## Common Pitfalls

- **Assuming dilute = safe**: Even dilute acids/bases need proper storage
- **Storing by alphabetical order**: Acetic acid next to acetone — always prioritize compatibility
- **Inadequate separation**: Use physical barriers (cabinets), not just distance
- **Outdated storage plans**: Update documentation whenever chemicals are relocated
- **Ignoring multi-hazard chemicals**: Concentrated HNO₃ is both acid and oxidizer — store in most restrictive group; multi-hazard chemicals are automatically assigned to the most restrictive applicable group

---

## Storage Requirements by Group

| Group | Cabinet Type | Special Requirements |
|-------|-------------|---------------------|
| **Acids** | Acid cabinet | Secondary containment, corrosion-resistant |
| **Bases** | Base cabinet | Minimum 3 feet from acids |
| **Oxidizers** | Standard/oxidizer | Away from ignition sources |
| **Flammables** | Flammable cabinet | Bonding/grounding for dispensing |
| **Toxics** | Locked cabinet | Access log, limited quantities |

---

## References

- OSHA Chemical Storage Guidelines: https://www.osha.gov/chemical-storage
- NFPA 45: Fire Protection for Laboratories Using Chemicals
- Prudent Practices in the Laboratory (National Research Council)
