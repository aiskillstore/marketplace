---
name: variant-annotation
description: Query and annotate gene variants from ClinVar and dbSNP databases. \n\.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Variant Annotation

Query and interpret gene variant clinical significance from ClinVar and dbSNP databases with ACMG guideline support.

## When to Use

- Use this skill when the task needs Query and annotate gene variants from ClinVar and dbSNP databases. 
\.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Query and annotate gene variants from ClinVar and dbSNP databases. \n\.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/variant-annotation"
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

## Purpose

Provide comprehensive variant annotation including:
- Clinical significance classification (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign)
- ACMG guideline-based pathogenicity assessment
- Population allele frequencies (gnomAD, ExAC, 1000 Genomes)
- Disease and phenotype associations
- Functional predictions (SIFT, PolyPhen, CADD)

## Supported Input Formats

| Format | Example | Description |
|--------|---------|-------------|
| **rsID** | `rs80357410` | dbSNP reference SNP ID |
| **HGVS cDNA** | `NM_007294.3:c.5096G>A` | Coding DNA change |
| **HGVS Protein** | `NP_009225.1:p.Arg1699Gln` | Protein change |
| **HGVS Genomic** | `NC_000017.11:g.43094692G>A` | Genomic coordinate |
| **VCF-style** | `chr17:43094692:G>A` | Chromosome:position:ref>alt |
| **Gene:AA** | `BRCA1:R1699Q` | Gene with amino acid change |

## Usage

### Python API

```python
from scripts.main import VariantAnnotator

# Initialize annotator
annotator = VariantAnnotator()

# Query by rsID
result = annotator.query_variant("rs80357410")

# Query by HGVS notation
result = annotator.query_variant("NM_007294.3:c.5096G>A")

# Query by genomic coordinate
result = annotator.query_variant("chr17:43094692:G>A")

# Batch query
results = annotator.batch_query(["rs80357410", "rs28897696", "rs11571658"])
```

### Command Line

```text

# Single variant query
python scripts/main.py --variant rs80357410

# HGVS notation
python scripts/main.py --variant "NM_007294.3:c.5096G>A"

# Genomic coordinate
python scripts/main.py --variant "chr17:43094692:G>A"

# Batch from file
python scripts/main.py --file variants.txt --output results.json

# With output format
python scripts/main.py --variant rs80357410 --format json
```

## Output Format

```json
{
  "variant_id": "rs80357410",
  "gene": "BRCA1",
  "chromosome": "17",
  "position": 43094692,
  "ref_allele": "G",
  "alt_allele": "A",
  "hgvs_genomic": "NC_000017.11:g.43094692G>A",
  "hgvs_cdna": "NM_007294.3:c.5096G>A",
  "hgvs_protein": "NP_009225.1:p.Arg1699Gln",
  
  "clinical_significance": {
    "clinvar": "Pathogenic",
    "acmg_classification": "Pathogenic",
    "acmg_criteria": ["PS4", "PM1", "PM2", "PP2", "PP3", "PP5"],
    "acmg_score": 13.0,
    "review_status": "criteria provided, multiple submitters, no conflicts"
  },
  
  "disease_associations": [
    {
      "disease": "Breast-ovarian cancer, familial 1",
      "medgen_id": "C2676676",
      "significance": "Pathogenic"
    }
  ],
  
  "population_frequencies": {
    "gnomAD_genome_all": 0.000008,
    "gnomAD_exome_all": 0.000012,
    "1000G_all": 0.0
  },
  
  "functional_predictions": {
    "sift": "deleterious",
    "polyphen2": "probably_damaging",
    "cadd_score": 24.5,
    "mutation_taster": "disease_causing"
  },
  
  "literature_count": 42,
  "last_evaluated": "2023-12-15",
  
  "interpretation_summary": "This variant (BRCA1 p.Arg1699Gln) is classified as Pathogenic based on ACMG guidelines. It shows strong evidence of pathogenicity including population data (extremely rare), computational predictions (deleterious), and strong clinical significance (established association with hereditary breast-ovarian cancer)."
}
```

## ACMG Classification Criteria

The annotator implements the ACMG/AMP guidelines for variant interpretation:

### Pathogenic Evidence (Score)
- **PVS1** (8.0): Null variant in a gene where LOF is known mechanism
- **PS1** (4.0): Same amino acid change as known pathogenic
- **PS2** (4.0): De novo with confirmed paternity/maternity
- **PS3** (4.0): Well-established functional studies show damaging effect
- **PS4** (4.0): Prevalence in affected > controls
- **PM1** (2.0): Located in critical functional domain
- **PM2** (2.0): Absent from controls (MAF <0.0001)
- **PM3** (2.0): AR disorder, detected in trans with pathogenic
- **PM4** (2.0): Protein length changing
- **PM5** (2.0): Novel missense at same position as known pathogenic
- **PM6** (2.0): Assumed de novo without confirmation
- **PP1** (1.0): Cosegregation with disease
- **PP2** (1.0): Missense in gene with low benign rate
- **PP3** (1.0): Multiple computational evidence support
- **PP4** (1.0): Phenotype/patient history matches gene
- **PP5** (1.0): Reputable source reports pathogenic

### Benign Evidence
- **BA1** (-8.0): MAF >5% in population
- **BS1** (-4.0): MAF >expected for disorder
- **BS2** (-4.0): Observed in healthy adult
- **BS3** (-4.0): Functional studies show no damage
- **BS4** (-4.0): Lack of cosegregation
- **BP1** (-1.0): Missense in gene where truncating are pathogenic
- **BP2** (-1.0): Observed in trans with pathogenic
- **BP3** (-1.0): In-frame indel in repetitive region
- **BP4** (-1.0): Multiple computational evidence benign
- **BP5** (-1.0): Alternate cause found
- **BP6** (-1.0): Reputable source reports benign
- **BP7** (-1.0): Synonymous with no splicing impact

### Classification Thresholds
| Classification | Score Range |
|----------------|-------------|
| Pathogenic | ≥ 10 |
| Likely Pathogenic | 6-9 |
| Uncertain Significance | 0-5 |
| Likely Benign | -5 to -1 |
| Benign | ≤ -6 |

## Technical Difficulty: **HIGH**

⚠️ **AI independent acceptance status**: manual inspection required
This skill requires:
- NCBI E-utilities API integration (ClinVar, dbSNP)
- HGVS notation parsing and validation
- VCF format handling
- ACMG guideline implementation
- Multiple prediction algorithm integration
- Complex data transformation and scoring

## Data Sources

| Database | Data Type | API/Access |
|----------|-----------|------------|
| **ClinVar** | Clinical significance, disease associations | NCBI E-utilities |
| **dbSNP** | SNP data, allele frequencies | NCBI E-utilities |
| **gnomAD** | Population frequencies | gnomAD API |
| **Ensembl VEP** | Functional predictions | REST API |
| **CADD** | Deleteriousness scores | REST API |

## Limitations

- Requires internet connection for database queries
- NCBI API rate limits: 3 requests/second (API key increases to 10/sec)
- Some variants may not be present in ClinVar (VUS without clinical data)
- HGVS notation parsing may fail for complex variants
- Population frequencies not available for all variants
- Functional predictions are computational estimates only

## References

See `references/` for:
- ACMG guidelines publication (Richards et al. 2015)
- ClinVar documentation
- HGVS nomenclature guide
- dbSNP data dictionary
- Example variant outputs

## Safety & Disclaimer

⚠️ **IMPORTANT**: This tool is for research and educational purposes only. Variant interpretations are computational predictions and should not be used as the sole basis for clinical decisions. Always consult certified genetic counselors and clinical laboratories for diagnostic purposes. ACMG classifications in this tool are algorithmic estimates and may differ from expert panel reviews.

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--variant` | str | Required |  |
| `--file` | str | Required |  |
| `--output` | str | Required |  |
| `--format` | str | "json" |  |
| `--api-key` | str | Required | NCBI API key for increased rate limits |
| `--delay` | float | 0.34 |  |

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

This skill accepts requests that match the documented purpose of `variant-annotation` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `variant-annotation` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
