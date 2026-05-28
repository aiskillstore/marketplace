---
name: reference-search
description: Multi-database literature search and search-strategy design that outputs structured, reproducible result lists; use when you need reference retrieval, systematic searching, review topic selection, or to construct a traceable search strategy.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Reference Search

## When to Use

- Use this skill when you need multi-database literature search and search-strategy design that outputs structured, reproducible result lists; use when you need reference retrieval, systematic searching, review topic selection, or to construct a traceable search strategy in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/pubmed_search.py` is the most direct path to complete the request.
- Use this skill when you need the `reference-search` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Multi-database literature search and search-strategy design that outputs structured, reproducible result lists; use when you need reference retrieval, systematic searching, review topic selection, or to construct a traceable search strategy.
- Packaged executable path(s): `scripts/pubmed_search.py`.
- Reference material available in `references/` for task-specific guidance.
- Reusable packaged asset(s), including `assets/search_log_template.csv`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/reference-search"
python -m py_compile scripts/pubmed_search.py
python scripts/pubmed_search.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/pubmed_search.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/pubmed_search.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Packaged assets: reusable files are available under `assets/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill in the following scenarios:

1. **Systematic or scoping reviews** where you must document a reproducible search strategy and export structured results.
2. **Rapid evidence retrieval** for a research question, with quick export to CSV/JSON for screening.
3. **Search strategy construction** (keywords, synonyms, Boolean logic, field restrictions) before running searches at scale.
4. **Review topic selection** by exploring the volume and distribution of literature for candidate topics.
5. **Traceable search logging** when you need to record search date, query string, and result counts for auditability.

## 2. Key Features

- **Multi-database search framework** (currently implemented for **PubMed**).
- **Automatic keyword extraction** and **search strategy construction** (Boolean logic + field constraints).
- **Structured outputs**:
  - Machine-readable **JSON**
  - Spreadsheet-friendly **CSV**
- **Reproducible search records** (query string, keywords, counts, and record list).
- **Compliance-oriented network access** restricted to official PubMed E-utilities endpoints.

## 3. Dependencies

| Dependency | Version | Notes |
|---|---:|---|
| Python | 3.10+ | Uses Python standard library only (no third-party packages). |

## 4. Example Usage

### Run the PubMed search script

```bash
cd skills/reference-search
python scripts/pubmed_search.py
```

### Configure the script

Edit the `CONFIG` section in `scripts/pubmed_search.py`:

```python
from pathlib import Path

CONFIG = {
    "EMAIL": "your_email@example.com",          # Required (must be provided by the user)
    "API_KEY": "",                               # Optional (can increase rate limits)
    "RETMAX": 20,                                # Max number of records to return
    "OUTPUT_DIR": Path("outputs/pubmed_search"), # Allowed output directory
}
```

### Example output (JSON)

```json
{
  "query": "\"Cancer cachexia\"[Title] AND cachexia[Title/Abstract] AND pancreatic[Title/Abstract]",
  "keywords": ["cachexia", "pancreatic", "cancer", "weight", "muscle", "atrophy", "mortality", "treatment"],
  "count": 20,
  "records": [
    {
      "pmid": "36280389",
      "title": "Role of noncoding RNAs in pancreatic ductal adenocarcinoma associated cachexia.",
      "journal": "Journal of Cachexia, Sarcopenia and Muscle",
      "pubdate": "2022",
      "authors": "Wang X, Li Y, Zhang S"
    }
  ]
}
```

## 5. Implementation Details

### Supported databases and endpoints

- **PubMed (NCBI E-utilities)** only.
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` (search)
  - `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi` (record summaries)

### Search workflow (recommended)

1. **Define requirements and scope**
   - Confirm research question and core concepts.
   - Set inclusion/exclusion criteria (time window, language, publication type).
2. **Design the search strategy**
   - Expand keywords with synonyms.
   - Combine with Boolean operators (AND/OR) and apply field restrictions (e.g., Title/Abstract/MeSH).
3. **Execute and export**
   - Run the script and export results to JSON/CSV.
   - If combining multiple sources, merge and deduplicate externally while preserving source labels.
4. **Record for reproducibility**
   - Save the final query string, search date, and result counts.

### Configuration parameters

- `EMAIL` (required): Must be provided by the user; **must not** be hard-coded as a real credential.
- `API_KEY` (optional): If provided, can improve throughput under NCBI policies.
- `RETMAX`: Limits the number of returned records.
- `OUTPUT_DIR`: Must point to an `outputs/` subdirectory.

### Security, compliance, and access constraints

- **Network access**: restricted to the official NCBI host `eutils.ncbi.nlm.nih.gov` only.
- **Prohibited**: any third-party URLs.
- **File read constraints**: do not read files outside the skill directory.
- **File write constraints**: write outputs only under `outputs/` (ensure the directory exists or is created by the script).
- **Timeout**: 20 seconds per API request.
- **Rate limiting**: 0.35 seconds between requests.
- **Error handling**: return semantic, user-facing error messages without exposing sensitive technical details.

### Included assets and references (in-repo)

- Templates:
  - `assets/search_log_template.csv`
  - `assets/search_results_template.csv`
- Additional guidance and checklists:
  - `references/guide.md`
  - `references/evaluation-checklist.md`
- Tests:
  - `tests/test_pubmed_search.py`
- External documentation:
  - PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25504/
