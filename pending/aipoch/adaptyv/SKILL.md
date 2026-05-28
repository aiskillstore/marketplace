---
name: adaptyv
description: Cloud laboratory platform for automated protein testing and validation; use when you have designed protein sequences and need wet-lab experimental validation (e.g., binding, expression, thermostability, enzyme activity) and API-based submission/status/result retrieval.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Cloud laboratory platform for automated protein testing and validation; use when you have designed protein sequences and need wet-lab experimental validation (e.g., binding, expression, thermostability, enzyme activity) and API-based submission/status/result retrieval.
- Packaged executable path(s): `scripts/validate_skill.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260316/scientific-skills/Others/adaptyv"
python -m py_compile scripts/validate_skill.py
python scripts/validate_skill.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/validate_skill.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/validate_skill.py`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# Adaptyv

Adaptyv is a cloud laboratory platform for automated protein testing and validation. You can submit protein sequences via API (or web UI), track experiment status, and download results (typically delivered in ~21 days).

For additional details, see:
- `reference/experiments.md` (assay types and workflows)
- `reference/protein_optimization.md` (sequence optimization workflows)
- `reference/api_reference.md` (endpoints, schemas, auth)
- `reference/examples.md` (more code examples)

## 1. When to Use

Use this skill when you need to:
- Validate newly designed protein sequences with wet-lab assays (e.g., binding, expression, thermostability, enzyme activity).
- Run high-throughput protein design → test cycles and want programmatic experiment submission and tracking via API.
- Compare multiple variants (e.g., mutants, redesigns) under the same assay conditions and retrieve results in a standardized way.
- Optimize sequences for expression/solubility before ordering experiments (e.g., filter or redesign candidates using NetSolP/SoluProt/SolubleMPNN/ESM).
- Integrate experimental validation into an automated workflow (e.g., trigger downstream analysis via a webhook when results are ready).

## 2. Key Features

- **API authentication** using a bearer token (`ADAPTYV_API_KEY`).
- **Experiment submission** by providing sequences and an `experiment_type`.
- **Supported assay categories** (see `reference/experiments.md`):
  - Binding assays (e.g., BLI)
  - Expression testing
  - Thermostability measurements
  - Enzyme activity assays
- **Asynchronous workflow support** via `webhook_url` callbacks.
- **Status tracking and results retrieval** (see `reference/api_reference.md` and `reference/examples.md`).
- **Pre-submission sequence optimization guidance** (see `reference/protein_optimization.md`).

## 3. Dependencies

- `python>=3.9`
- `requests>=2.31.0`
- `python-dotenv>=1.0.0`

## 4. Example Usage

The following example is a minimal, runnable workflow to (1) submit an experiment and (2) poll for completion, then (3) download results. Adjust endpoint paths/fields to match `reference/api_reference.md`.

### 4.1 Set credentials

Request API access and a token from `support@adaptyvbio.com`, then set:

```bash
export ADAPTYV_API_KEY="your_api_key_here"
```

Or create a `.env` file:

```dotenv
ADAPTYV_API_KEY=your_api_key_here
```

### 4.2 Install dependencies

```bash
python -m pip install "requests>=2.31.0" "python-dotenv>=1.0.0"
```

### 4.3 Submit, poll, and fetch results

```python
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ADAPTYV_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing ADAPTYV_API_KEY. Set it in your environment or .env file.")

BASE_URL = "https://kq5jp7qj7wdqklhsxmovkzn4l40obksv.lambda-url.eu-central-1.on.aws"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# 1) Submit an experiment
submit_payload = {
    "sequences": ">protein1\nMKVLWALLGLLGAA...",  # FASTA-like string as shown in the original docs
    "experiment_type": "binding",                # e.g., binding | expression | thermostability | enzyme_activity
    "webhook_url": "https://your-webhook.com/callback",  # optional but recommended for async workflows
}

submit_resp = requests.post(f"{BASE_URL}/experiments", headers=HEADERS, json=submit_payload, timeout=60)
submit_resp.raise_for_status()
experiment_id = submit_resp.json()["experiment_id"]
print("Submitted experiment:", experiment_id)

# 2) Poll status until completion (use webhook in production to avoid polling)
status = None
for _ in range(120):  # e.g., poll up to ~20 minutes at 10s intervals (adjust as needed)
    status_resp = requests.get(f"{BASE_URL}/experiments/{experiment_id}", headers=HEADERS, timeout=60)
    status_resp.raise_for_status()
    data = status_resp.json()
    status = data.get("status")
    print("Status:", status)

    if status in {"completed", "failed", "canceled"}:
        break

    time.sleep(10)

if status != "completed":
    raise RuntimeError(f"Experiment did not complete successfully (status={status}).")

# 3) Download results (endpoint/format may vary; confirm in reference/api_reference.md)
results_resp = requests.get(f"{BASE_URL}/experiments/{experiment_id}/results", headers=HEADERS, timeout=60)
results_resp.raise_for_status()

# Save results (could be JSON, CSV, or a file bundle depending on the API)
with open(f"{experiment_id}_results.json", "wb") as f:
    f.write(results_resp.content)

print("Results saved to:", f"{experiment_id}_results.json")
```

## 5. Implementation Details

### Authentication
- Uses a bearer token provided via `ADAPTYV_API_KEY`.
- Requests include header: `Authorization: Bearer <token>`.

### Core request parameters
- `sequences`: Provided as a FASTA-like string (e.g., `>name\nSEQUENCE...`). For batch submissions, follow the exact multi-sequence format described in `reference/api_reference.md`.
- `experiment_type`: Select the assay category (binding, expression, thermostability, enzyme activity). Exact allowed values and any assay-specific parameters are defined in `reference/experiments.md` and `reference/api_reference.md`.
- `webhook_url` (optional): A callback URL to receive asynchronous notifications when experiment state changes or results are ready.

### Workflow timing and execution model
- Experiments are **asynchronous**; results are typically delivered in **~21 days**.
- Prefer **webhooks** for production workflows; polling is suitable for demos/tests.

### Sequence optimization guidance (pre-submission)
Common pre-checks before ordering wet-lab validation (see `reference/protein_optimization.md`):
- Identify **unpaired cysteines** that may form unintended disulfides.
- Reduce **excess hydrophobicity** that can drive aggregation.
- Screen for **low predicted solubility** and redesign candidates.

Commonly referenced tools in the workflow documentation:
- **NetSolP / SoluProt**: solubility prediction and filtering
- **SolubleMPNN**: redesign for improved solubility/expression
- **ESM**: sequence likelihood scoring
- **ipTM**: interface stability assessment
- **pSAE**: hydrophobic exposure quantification

### Notes and constraints
- The platform may be in **alpha/beta**; endpoints and capabilities can change.
- Not all platform features may be exposed via API; consult `reference/api_reference.md` for the authoritative list.

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
- If a file is produced, prefer a deterministic output name such as `adaptyv_result.md` unless the skill documentation defines a better convention.
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

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: adaptyv_result.md
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
