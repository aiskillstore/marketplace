---
name: fulltext-fetcher
description: Fetch and save the original HTML of scientific literature webpages when given a URL, DOI, or PubMed PMID (triggered when you need archival-grade page HTML for downstream parsing or review).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Fetch and save the original HTML of scientific literature webpages when given a URL, DOI, or PubMed PMID (triggered when you need archival-grade page HTML for downstream parsing or review).
- Packaged executable path(s): `scripts/fulltext_fetcher.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/fulltext-fetcher"
python -m py_compile scripts/fulltext_fetcher.py
python scripts/fulltext_fetcher.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/fulltext_fetcher.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/fulltext_fetcher.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/fulltext_fetcher.py --help
```

# fulltext-fetcher

## 1. When to Use
- You need to archive the **original HTML** of a scientific literature webpage for later parsing, auditing, or offline review.
- You have a **DOI** and need to quickly resolve it to the landing page and save the resulting HTML.
- You have a **PubMed PMID** and need to fetch the PubMed record page HTML (or resolve onward) for extraction workflows.
- You need to **batch fetch** multiple public literature pages (URLs/DOIs/PMIDs) into a consistent output directory.
- You want a safer crawl mode that **restricts requests to a whitelist** unless explicitly overridden.

## 2. Key Features
- Accepts three input types: **URL**, **DOI**, and **PubMed PMID**.
- Writes **one `.html` file per input** and preserves the **original HTML**.
- Supports **multiple repeated inputs** (e.g., multiple `--url` / `--doi` / `--pmid` flags).
- Default **domain whitelist** for safer operation; optional override via `--allow-all`.
- Built-in **timeout and retry** behavior to reduce long blocking on network issues.

## 3. Dependencies
- Python **3.x**
- Python Standard Library only (no third-party packages)

## 4. Example Usage
> The following commands are intended to be runnable as-is from the repository root.

### Fetch a single URL
```bash
python scripts/fulltext_fetcher.py --url "https://example.org/page"
```

### Fetch by DOI
```bash
python scripts/fulltext_fetcher.py --doi "10.1038/s41586-020-2649-2"
```

### Fetch by PubMed PMID
```bash
python scripts/fulltext_fetcher.py --pmid "23273568"
```

### Batch fetch and customize output directory
```bash
python scripts/fulltext_fetcher.py \
  --url "https://example.org/page1" \
  --url "https://example.org/page2" \
  --doi "10.1038/s41586-020-2649-2" \
  --pmid "23273568" \
  --out-dir "outputs"
```

### Allow crawling non-whitelisted public domains (explicit opt-in)
```bash
python scripts/fulltext_fetcher.py \
  --doi "10.1038/s41586-020-2649-2" \
  --allow-all
```

## 5. Implementation Details

### Inputs
- `--url` (repeatable): Direct webpage URL(s) to fetch.
- `--doi` (repeatable): DOI(s) to resolve (typically via `doi.org`) and fetch.
- `--pmid` (repeatable): PubMed PMID(s) to fetch (typically via `pubmed.ncbi.nlm.nih.gov` / `ncbi.nlm.nih.gov`).

At least one of `--url`, `--doi`, or `--pmid` must be provided.

### Output
- Produces **one HTML file per input**.
- Default output directory: `outputs/`
- Output directory can be changed with:
  - `--out-dir <path>`

### Domain access control
- Default allowed domains:
  - `doi.org`
  - `pubmed.ncbi.nlm.nih.gov`
  - `ncbi.nlm.nih.gov`
- To fetch from other public domains, you must explicitly enable:
  - `--allow-all`

### Network behavior
- Uses timeout and retry logic to avoid long-running hangs and to improve robustness against transient network failures.
- Only targets **publicly accessible** webpages; it is not intended for restricted or authenticated content.

### Verification checklist
- After running, confirm:
  - The output directory exists.
  - Generated `.html` files exist and are **non-empty**.
- For parallel/coexistence runs, ensure output paths do not collide (use distinct `--out-dir` values if needed).

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `fulltext_fetcher_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/fulltext_fetcher.py --help
```

Expected output format:

```text
Result file: fulltext_fetcher_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
