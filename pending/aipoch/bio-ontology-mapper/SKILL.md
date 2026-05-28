---
name: bio-ontology-mapper
description: Map unstructured biomedical text to standardized ontologies (SNOMED CT.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Bio-Ontology Mapper

## When to Use

- Use this skill when the task is to Map unstructured biomedical text to standardized ontologies (SNOMED CT.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Map unstructured biomedical text to standardized ontologies (SNOMED CT.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `difflib`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Evidence Insight/bio-ontology-mapper"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

Biomedical terminology normalization tool that maps free-text clinical and scientific concepts to standardized ontologies for semantic interoperability and data harmonization.

**Key Capabilities:**
- **Multi-Ontology Support**: SNOMED CT, MeSH, ICD-10, LOINC, RxNorm
- **Entity Extraction**: NER for diseases, symptoms, procedures, drugs
- **Fuzzy Matching**: Handle typos, abbreviations, and synonyms
- **Confidence Scoring**: Reliability metrics for each mapping
- **Batch Processing**: Normalize large datasets efficiently
- **Cross-Mapping**: Translate between ontology systems

## Core Capabilities

### 1. Entity Recognition and Mapping

Extract and map biomedical entities to ontologies:

```python
from scripts.mapper import BioOntologyMapper

mapper = BioOntologyMapper()

# Map clinical text
result = mapper.map_text(
    text="Patient has diabetes and hypertension, taking metformin",
    ontologies=["snomed", "mesh", "rxnorm"],
    confidence_threshold=0.7
)

for entity in result.entities:
    print(f"{entity.text} → {entity.concept_id} ({entity.ontology})")
    print(f"  Preferred: {entity.preferred_term}")
    print(f"  Confidence: {entity.confidence:.2f}")
```

**Supported Ontologies:**
| Ontology | Domain | Use Case |
|----------|--------|----------|
| **SNOMED CT** | Clinical | EHR interoperability |
| **MeSH** | Literature | PubMed indexing |
| **ICD-10** | Billing | Diagnosis codes |
| **LOINC** | Labs | Test result standardization |
| **RxNorm** | Drugs | Medication normalization |
| **HGNC** | Genes | Gene name standardization |

### 2. Cross-Ontology Translation

Map concepts between different ontologies:

```python

# Cross-map SNOMED to ICD-10
translation = mapper.cross_map(
    source_id="22298006",  # SNOMED: Myocardial infarction
    source_ontology="snomed",
    target_ontology="icd10"
)

print(f"ICD-10: {translation.target_id} - {translation.target_term}")

# Output: I21.9 - Acute myocardial infarction, unspecified
```

**Cross-Mapping Coverage:**
- SNOMED CT ↔ ICD-10-CM (clinical modifications)
- MeSH ↔ SNOMED CT (literature to clinical)
- RxNorm ↔ ATC (drug classifications)
- LOINC ↔ SNOMED (lab to clinical)

### 3. Batch Normalization

Process large datasets:

```python

# Batch process CSV
results = mapper.batch_map(
    input_file="clinical_terms.csv",
    text_column="diagnosis_description",
    ontologies=["snomed", "icd10"],
    output_format="csv",
    max_workers=4
)

# Results include:

# - Original term

# - Mapped concept ID

# - Confidence score

# - Alternative mappings (if ambiguous)
```

**Performance:**
- ~100 terms/second (with caching)
- ~20 terms/second (API lookup)
- Parallel processing for large datasets

### 4. Confidence Scoring and Validation

Assess mapping reliability:

```python
scoring = mapper.score_mapping(
    term="heart attack",
    candidate="22298006",  # Myocardial infarction
    factors=["string_similarity", "context_match", "frequency"]
)

print(f"Overall confidence: {scoring.confidence:.2f}")
print(f"Breakdown: {scoring.factors}")
```

**Scoring Factors:**
- **String similarity**: Levenshtein distance, n-grams
- **Context match**: Surrounding words alignment
- **Frequency**: Common usage in corpus
- **Semantic similarity**: Vector embeddings

## Quality Checklist

**Pre-Mapping:**
- [ ] Text preprocessed (lowercase, punctuation handled)
- [ ] Abbreviations expanded where possible
- [ ] Language identified (multilingual support)

**During Mapping:**
- [ ] Confidence threshold appropriate (>0.7 for clinical)
- [ ] Multiple candidates considered for ambiguous terms
- [ ] Context used for disambiguation

**Post-Mapping:**
- [ ] Low-confidence mappings flagged for review
- [ ] Unmapped terms logged
- [ ] **CRITICAL**: Clinical expert validation for high-stakes use

**Before Production:**
- [ ] Mapping accuracy validated on gold standard
- [ ] False positive rate acceptable (<5%)
- [ ] Recall acceptable for use case (>90%)
- [ ] API rate limits respected

## Common Pitfalls

**Mapping Errors:**
- ❌ **Abbreviation ambiguity** → "MI" = Myocardial infarction OR Michigan
  - ✅ Use context; flag for manual review

- ❌ **Outdated terms** → Old terminology not in current ontology
  - ✅ Use historical mappings; update terminology

- ❌ **False confidence** → High score for wrong concept
  - ✅ Always review top-3 candidates

**Technical Issues:**
- ❌ **API failures** → No local fallback
  - ✅ Implement caching; use local reference files

- ❌ **Version mismatches** → Different ontology versions
  - ✅ Track ontology version used

- ❌ **PHI exposure** → Sending patient data to external APIs
  - ✅ De-identify before API calls; use local processing when possible

## References

Available in `references/` directory:

- `snomed_ct_guide.md` - SNOMED CT hierarchy and relationships
- `mesh_structure.md` - MeSH tree structure and qualifiers
- `ontology_mappings.md` - Crosswalks between systems
- `nlp_best_practices.md` - Biomedical text processing
- `api_documentation.md` - External service integration
- `validation_datasets.md` - Gold standard test sets

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for mapping
- `mapper.py` - Core ontology mapping engine
- `extractor.py` - Named entity recognition
- `cross_mapper.py` - Ontology-to-ontology translation
- `scorer.py` - Confidence calculation
- `batch_processor.py` - Large dataset handling
- `validator.py` - Mapping quality checks
- `caching.py` - Local storage for frequent lookups

## Limitations

- **Ambiguity**: Many-to-many mappings common; context required
- **Coverage**: Rare diseases and new concepts may not be in ontologies
- **Versioning**: Ontology updates can change mappings over time
- **Language**: Best support for English; other languages limited
- **Real-time**: Not suitable for time-critical clinical applications
- **API Dependency**: Requires internet for most lookups (caching helps)

---

**⚠️ Critical: Ontology mapping is for research and data integration, not clinical decision-making. Always validate mappings with domain experts before use in patient care contexts. Never process PHI without appropriate de-identification and compliance measures.**

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--term` | str | Required | Single term to map |
| `--input` | str | Required | Input file path |
| `--output` | str | Required | Output file path |
| `--ontology` | str | 'both' |  |
| `--threshold` | float | 0.7 |  |
| `--format` | str | 'json' |  |
| `--use-api` | str | Required | Use UMLS/MeSH APIs |
| `--api-key` | str | Required |  |

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `bio-ontology-mapper` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `bio-ontology-mapper` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
