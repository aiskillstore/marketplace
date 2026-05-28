---
name: arxiv-database
description: Search and retrieve scientific preprints from arXiv; use it when you need to find papers by keyword/author/category, fetch metadata (abstract, DOI, PDF URL), or download PDFs for offline reading.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# ArXiv Database Skill

## When to Use

- Use this skill when you need search and retrieve scientific preprints from arxiv; use it when you need to find papers by keyword/author/category, fetch metadata (abstract, doi, pdf url), or download pdfs for offline reading in a reproducible workflow.
- Use this skill when a evidence insight task needs a packaged method instead of ad-hoc freeform output.
- Use this skill when the user expects a concrete deliverable, validation step, or file-based result.
- Use this skill when `scripts/arxiv_search.py` is the most direct path to complete the request.
- Use this skill when you need the `arxiv-database` package behavior rather than a generic answer.

## Key Features

- Scope-focused workflow aligned to: Search and retrieve scientific preprints from arXiv; use it when you need to find papers by keyword/author/category, fetch metadata (abstract, DOI, PDF URL), or download PDFs for offline reading.
- Packaged executable path(s): `scripts/arxiv_search.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Evidence Insight/arxiv-database"
python -m py_compile scripts/arxiv_search.py
python scripts/arxiv_search.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/arxiv_search.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/arxiv_search.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

- You need to quickly find arXiv preprints by keyword, phrase, author, or category (e.g., `cs.AI`, `cs.CL`).
- You want to collect paper metadata (title, authors, publication date, abstract/summary, PDF link) for review or indexing.
- You need the latest submissions in a topic area (sorted by submission date or last updated date).
- You want to download one or more PDFs from search results for offline reading or batch processing.
- You have a known arXiv identifier and want to retrieve the corresponding paper directly.

## 2. Key Features

- arXiv query-based search (supports category filters, author filters, phrases, and ID lookups).
- Configurable result limits (`--max-results`).
- Sort control (`--sort-by`: `Relevance`, `LastUpdatedDate`, `SubmittedDate`).
- Metadata output per result (title, authors, published date, abstract/summary, PDF URL; DOI when available via arXiv metadata).
- Optional PDF download for returned results (`--download`) with configurable output directory (`--dir`).

## 3. Dependencies

- Python 3.8+
- `arxiv` (Python package) — version depends on your environment; install a recent release (e.g., `arxiv>=1.4.0`)

## 4. Example Usage

### Install dependencies

```bash
pip install "arxiv>=1.4.0"
```

### Run searches and downloads

**Search for papers in `cs.AI` about reinforcement learning (top 5 results):**
```bash
python scripts/arxiv_search.py --query "cat:cs.AI AND reinforcement learning" --max-results 5
```

**Search for “Large Language Models” in `cs.CL`:**
```bash
python scripts/arxiv_search.py --query "cat:cs.CL AND \"Large Language Models\""
```

**Get the latest 5 papers on “quantum computing” (sorted by submission date):**
```bash
python scripts/arxiv_search.py --query "quantum computing" --sort-by SubmittedDate --max-results 5
```

**Download a specific paper by arXiv ID:**
```bash
python scripts/arxiv_search.py --query "id:2101.12345" --download
```

**Download results into a specific directory:**
```bash
python scripts/arxiv_search.py --query "cat:cs.LG AND diffusion" --max-results 3 --download --dir ./papers
```

## 5. Implementation Details

- **Entry point:** `scripts/arxiv_search.py` wraps the `arxiv` Python API to execute queries against the arXiv search endpoint.
- **Query syntax:** The `--query` string is passed to arXiv search and can include:
  - Category filters (e.g., `cat:cs.AI`)
  - Author filters (e.g., `au:Smith`)
  - Exact phrases using quotes (e.g., `"Large Language Models"`)
  - ID lookup (e.g., `id:2101.12345`)
  - Boolean operators such as `AND`
- **Result limiting:** `--max-results` controls how many entries are returned (default: `10`).
- **Sorting:** `--sort-by` selects the ordering of results:
  - `Relevance` (default)
  - `LastUpdatedDate`
  - `SubmittedDate`
- **Downloads:** When `--download` is set, the script downloads the PDF for each returned result using the provided PDF URL and saves it to `--dir` (default: current working directory).
- **Metadata fields:** Each result includes core arXiv metadata (title, authors, published date, summary/abstract, PDF URL). DOI is included when present in arXiv’s metadata for that record.
