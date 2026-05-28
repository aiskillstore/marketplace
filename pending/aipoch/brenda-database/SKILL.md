---
name: brenda-database
description: Programmatic access to the BRENDA enzyme database via the SOAP API; use when you need kinetic constants (Km, kcat, Vmax), reaction equations, enzyme properties (pH/temperature optima, stability), or enzyme discovery by EC/substrate/product.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need **kinetic parameters** (e.g., Km, kcat, Vmax) for a specific enzyme, organism, or EC number.
- You want **reaction equations/stoichiometry** associated with an enzyme (by EC number or enzyme name).
- You need **enzyme property data** such as optimal pH/temperature, stability, inhibitors, or activators.
- You want to **discover enzymes** by searching for a substrate, product, or EC number.
- You need to **automate retrieval** of BRENDA data in a Python pipeline (e.g., for modeling, annotation, or curation).

## Key Features

- SOAP-based programmatic access to the BRENDA database.
- Retrieval of:
  - Kinetic data: Km, kcat, Vmax
  - Reaction information: reaction equations and related metadata
  - Enzyme discovery: search by substrate/product/EC number
  - Enzyme properties: pH/temperature optima, stability, inhibitors/activators
- Built-in handling of BRENDA SOAP responses that are returned as **complex delimited strings**, with parsing performed by the provided script.
- Credential-based authentication via environment variables or a `.env` file.

## Dependencies

- Python `3.x`
- `zeep` (SOAP client)
- `requests`

Install (example):

```bash
uv pip install zeep requests
```

## Example Usage

1) Set credentials (either in your shell or a `.env` file loaded by your environment):

```bash
export BRENDA_EMAIL="your_email@example.com"
export BRENDA_PASSWORD="your_password"
```

2) Run the query script:

```bash
python scripts/brenda_queries.py
```

3) Minimal Python example (calling the script functions; adjust function names to match `scripts/brenda_queries.py`):

```python
import os
from scripts.brenda_queries import BrendaClient

email = os.environ["BRENDA_EMAIL"]
password = os.environ["BRENDA_PASSWORD"]

client = BrendaClient(email=email, password=password)

# Example: retrieve Km values for an EC number
km_records = client.get_km_values(ec_number="1.1.1.1")
for r in km_records:
    print(r)

# Example: retrieve reactions for an EC number
reactions = client.get_reactions(ec_number="1.1.1.1")
for rxn in reactions:
    print(rxn)
```

For a complete list of available API methods and parameters, see: `references/api_reference.md`.

## Implementation Details

- **Authentication / Connection**
  - The skill initializes a SOAP client (via `zeep`) using BRENDA credentials (email/password).
  - Credentials are read from environment variables or a `.env`-backed environment setup.

- **Query Execution**
  - The script calls SOAP methods such as `get_km_values` and `get_reactions` (and other supported endpoints for properties and discovery).

- **Response Parsing**
  - BRENDA SOAP responses are often returned as **single strings** containing multiple records and fields, using delimiters (e.g., patterns like `organism*E. coli#value*...`).
  - `scripts/brenda_queries.py` is responsible for:
    - Splitting records into entries
    - Extracting key/value fields
    - Normalizing parsed results into Python-friendly structures (e.g., dicts/lists)

- **Output Structure**
  - Parsed results are returned as structured Python objects suitable for downstream filtering (by organism, literature reference, conditions, etc.), depending on the endpoint and available fields.

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
- If a file is produced, prefer a deterministic output name such as `brenda_database_result.md` unless the skill documentation defines a better convention.
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
python scripts/brenda_queries.py --help
```

Expected output format:

```text
Result file: brenda_database_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
