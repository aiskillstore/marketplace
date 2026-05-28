---
name: matchms
description: Process, clean, and compare mass spectrometry (MS/MS) spectra with Matchms; use when you need reproducible spectral filtering and similarity scoring for metabolomics workflows.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Matchms Skill

## When to Use

- Use this skill when you need process, clean, and compare mass spectrometry (ms/ms) spectra with matchms; use when you need reproducible spectral filtering and similarity scoring for metabolomics workflows in a reproducible workflow.
- Use this skill when a data analytics task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/similarity_pipeline.py` is the most direct path to complete the request.
- Use this skill when you need the `matchms` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Process, clean, and compare mass spectrometry (MS/MS) spectra with Matchms; use when you need reproducible spectral filtering and similarity scoring for metabolomics workflows.
- Packaged executable path(s): `scripts/similarity_pipeline.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Data Analytics/matchms"
python -m py_compile scripts/similarity_pipeline.py
python scripts/similarity_pipeline.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/similarity_pipeline.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/similarity_pipeline.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need to:

- Import and harmonize MS/MS spectra from common community formats (e.g., MGF/MSP) before analysis.
- Clean spectra (peak filtering, intensity normalization) to improve downstream similarity scoring and identification.
- Compute spectral similarity (Cosine/Modified Cosine/Fingerprint-based) for library matching or clustering.
- Build reproducible, configurable processing pipelines for metabolomics projects.
- Compare many spectra efficiently (all-vs-all or query-vs-library) and store/inspect score outputs.

## 2. Key Features

- **Import/Export support**: Read spectra from mzML, mzXML, MGF, MSP, and JSON (depending on installed readers).
- **Filtering & harmonization**: Metadata standardization, peak cleaning, intensity normalization, and other reusable filters.
- **Similarity scoring**:
  - Cosine similarity (Greedy/Hungarian variants)
  - Modified Cosine (accounts for precursor mass shifts)
  - Fingerprint-based similarities (when molecular fingerprints are available)
- **Pipeline composition**: Chain filters and scoring steps into repeatable workflows.

Additional reference material (if present in the repository):
- Filters: `references/filtering.md`
- Similarity: `references/similarity.md`
- Workflows: `references/workflows.md`

## 3. Dependencies

- `matchms` (version depends on your environment; pin in your project, e.g., `matchms>=0.20,<1.0`)
- `numpy` (e.g., `numpy>=1.20`)
- `scipy` (e.g., `scipy>=1.7`)
- `rdkit` (optional; required for chemistry/fingerprint-related functionality, version varies by distribution)

## 4. Example Usage

A minimal, runnable example that loads spectra from an MGF file and computes pairwise cosine scores:

```python
from matchms.importing import load_from_mgf
from matchms import calculate_scores
from matchms.similarity import CosineGreedy

def main():
    # Load spectra from an MGF file
    spectra = list(load_from_mgf("data.mgf"))

    # Compute similarity scores (all-vs-all)
    scores = calculate_scores(
        references=spectra,
        queries=spectra,
        similarity_function=CosineGreedy()
    )

    # Iterate over computed scores
    for (reference_idx, query_idx, score, n_matches) in scores:
        print(
            f"ref={reference_idx:>3} query={query_idx:>3} "
            f"cosine={score:.4f} matches={n_matches}"
        )

if __name__ == "__main__":
    main()
```

## 5. Implementation Details

- **Data model**: Matchms operates on `Spectrum` objects containing peak m/z and intensity arrays plus metadata (e.g., precursor m/z, charge, compound name/identifier).
- **Filtering stage**: Typical pipelines apply filters to:
  - standardize/repair metadata fields,
  - remove noise peaks (e.g., by intensity threshold or m/z window rules),
  - normalize intensities (commonly to a maximum of 1.0 or to unit norm).
  See `references/filtering.md` for filter patterns and recommended sequences.
- **Cosine similarity (Greedy/Hungarian)**:
  - Peaks are matched within an m/z tolerance (implementation-specific defaults; configure via the similarity class parameters).
  - **Greedy** matching selects best available peak matches iteratively.
  - **Hungarian** matching solves an assignment problem to maximize total match score under one-to-one constraints.
- **Modified Cosine**:
  - Extends cosine matching by allowing peak alignment with a precursor mass shift, improving matching for related compounds/adducts.
  - Typically requires precursor m/z metadata to be present and consistent.
- **Fingerprint similarity (optional)**:
  - Requires molecular fingerprints (often derived via RDKit) and compares spectra/compounds using fingerprint similarity metrics.
  - Use when you have structure annotations or can compute fingerprints reliably.
- **Workflow reproducibility**:
  - Prefer explicit, ordered filter chains and pinned dependency versions.
  - Store configuration (tolerances, normalization choices, filters used) alongside results for traceability.
  See `references/workflows.md` for pipeline organization guidance.
