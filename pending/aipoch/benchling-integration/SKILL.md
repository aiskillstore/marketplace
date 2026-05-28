---
name: benchling-integration
description: Integrate with the Benchling R&D platform when you need to programmatically manage registry entities, inventory, ELN entries, workflows, events, or data warehouse analytics via API/SDK.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Benchling Integration

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: Integrate with the Benchling R&D platform when you need to programmatically manage registry entities, inventory, ELN entries, workflows, events, or data warehouse analytics via API/SDK.
- Documentation-first workflow with no packaged script requirement.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```text
Skill directory: 20260316/scientific-skills/Others/benchling-integration
No packaged executable script was detected.
Use the documented workflow in SKILL.md together with the references/assets in this folder.
```

Example run plan:
1. Read the skill instructions and collect the required inputs.
2. Follow the documented workflow exactly.
3. Use packaged references/assets from this folder when the task needs templates or rules.
4. Return a structured result tied to the requested deliverable.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: instruction-only workflow in `SKILL.md`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## 1. When to Use

Use this skill when you need to:

- Create, read, update, archive, or search Benchling Registry entities (DNA/RNA/AA sequences, custom entities, mixtures) from code.
- Automate Inventory operations (containers, boxes, locations, transfers, check-in/out) across lab storage.
- Create or update ELN entries and link entities/results to notebook documentation.
- Orchestrate Benchling Workflows (create tasks, update statuses/assignees, monitor async jobs).
- Build integrations that sync Benchling data with external systems, including event-driven pipelines (e.g., AWS EventBridge) and analytics via the Benchling Data Warehouse.

## 2. Key Features

- **Authentication support**: API key for scripts; OAuth client credentials for apps.
- **Registry management**: typed create/update models, partial updates, pagination helpers.
- **Inventory automation**: create containers/boxes, move/transfer items, bulk-style operations.
- **ELN operations**: create entries, manage schema fields, link entities to entries.
- **Workflow automation**: create/update tasks, handle asynchronous operations and polling.
- **Event-driven integration**: consume Benchling events (via AWS EventBridge) to trigger downstream actions.
- **Analytics enablement**: query the Benchling Data Warehouse using SQL for reporting and trends.

> Additional reference docs may exist in `references/` (e.g., `references/authentication.md`, `references/sdk_reference.md`, `references/api_endpoints.md`) for deeper guidance.

## 3. Dependencies

- `benchling-sdk` (Python) — version: *not specified in source document*  
- Python — version: *not specified in source document*
- Optional (for FASTA import example): `biopython` — version: *not specified in source document*
- Optional (for event-driven integrations): AWS EventBridge — version: N/A (managed service)
- Optional (for Data Warehouse access): a SQL client/driver — version: *not specified in source document*

## 4. Example Usage

A minimal, runnable example that authenticates with an API key, creates a DNA sequence, lists sequences (paginated), and creates an ELN entry.

```python
import os

from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth
from benchling_sdk.models import DnaSequenceCreate, EntryCreate

def main():
    tenant_url = os.environ["BENCHLING_TENANT_URL"]  # e.g. https://your-tenant.benchling.com
    api_key = os.environ["BENCHLING_API_KEY"]
    folder_id = os.environ["BENCHLING_FOLDER_ID"]    # e.g. fld_abc123

    benchling = Benchling(
        url=tenant_url,
        auth_method=ApiKeyAuth(api_key),
    )

    # 1) Create a DNA sequence in the Registry (unregistered unless entity_registry_id is provided)
    created_seq = benchling.dna_sequences.create(
        DnaSequenceCreate(
            name="Example Plasmid",
            bases="ATCGATCG",
            is_circular=True,
            folder_id=folder_id,
        )
    )
    print("Created DNA sequence:", created_seq.id, created_seq.name)

    # 2) List DNA sequences (generator yields pages)
    print("\nListing DNA sequences (first page):")
    pages = benchling.dna_sequences.list()
    first_page = next(iter(pages))
    for seq in first_page:
        print("-", seq.id, seq.name)

    # 3) Create an ELN entry
    entry = benchling.entries.create(
        EntryCreate(
            name="Example Experiment Entry",
            folder_id=folder_id,
        )
    )
    print("\nCreated ELN entry:", entry.id, entry.name)

if __name__ == "__main__":
    main()
```

Run:

```bash
export BENCHLING_TENANT_URL="https://your-tenant.benchling.com"
export BENCHLING_API_KEY="your_api_key"
export BENCHLING_FOLDER_ID="fld_abc123"

python benchling_example.py
```

## 5. Implementation Details

### Authentication

- **API Key authentication** is recommended for scripts and automation:
  - API keys are obtained from Benchling profile/settings.
  - Permissions match the user/app permissions in the Benchling UI.
  - Store secrets in environment variables or a secrets manager; never commit keys.

```python
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=ApiKeyAuth("your_api_key"),
)
```

- **OAuth client credentials** is suitable for apps/services:

```python
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.client_credentials_oauth2 import ClientCredentialsOAuth2

auth_method = ClientCredentialsOAuth2(
    client_id="your_client_id",
    client_secret="your_client_secret",
)

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=auth_method,
)
```

### Registry entities and schema fields

- Registry entity creation uses typed models such as `DnaSequenceCreate`.
- Custom schema fields are passed via the SDK `fields()` helper.

```python
from benchling_sdk.models import DnaSequenceCreate

sequence = benchling.dna_sequences.create(
    DnaSequenceCreate(
        name="My Plasmid",
        bases="ATCGATCG",
        is_circular=True,
        folder_id="fld_abc123",
        schema_id="ts_abc123",  # optional
        fields=benchling.models.fields({"gene_name": "GFP"}),
    )
)
```

- **Registration behavior**: the source document notes that `entity_registry_id` and `naming_strategy` should not be used together.

```python
sequence = benchling.dna_sequences.create(
    DnaSequenceCreate(
        name="My Plasmid",
        bases="ATCGATCG",
        is_circular=True,
        folder_id="fld_abc123",
        entity_registry_id="src_abc123",
        naming_strategy="NEW_IDS",  # do not combine with entity_registry_id per source note
    )
)
```

### Partial updates

- Updates are partial: unspecified fields remain unchanged.

```python
from benchling_sdk.models import DnaSequenceUpdate

updated = benchling.dna_sequences.update(
    sequence_id="seq_abc123",
    dna_sequence=DnaSequenceUpdate(
        name="Updated Plasmid Name",
        fields=benchling.models.fields({"gene_name": "mCherry"}),
    ),
)
```

### Pagination

- Listing endpoints return generators of pages; iterate page-by-page for memory efficiency.
- Some list iterators provide `estimated_count()`.

```python
sequences = benchling.dna_sequences.list()
for page in sequences:
    for seq in page:
        print(seq.name, seq.id)

total = sequences.estimated_count()
```

### Inventory operations (containers/boxes/transfers)

- Inventory objects are created via typed models (e.g., `ContainerCreate`, `BoxCreate`).
- Transfers move items between storage locations.

```python
from benchling_sdk.models import ContainerCreate, BoxCreate

box = benchling.boxes.create(
    BoxCreate(
        name="Freezer Box A1",
        schema_id="box_schema_abc123",
        parent_storage_id="loc_abc123",
    )
)

container = benchling.containers.create(
    ContainerCreate(
        name="Sample Tube 001",
        schema_id="cont_schema_abc123",
        parent_storage_id=box.id,
        fields=benchling.models.fields({"concentration": "100 ng/μL"}),
    )
)

benchling.containers.transfer(
    container_id=container.id,
    destination_id="box_xyz789",
)
```

### Workflows and async tasks

- Some operations are asynchronous and return a task object; poll until completion.

```python
from benchling_sdk.helpers.tasks import wait_for_task

result = wait_for_task(
    benchling,
    task_id="task_abc123",
    interval_wait_seconds=2,
    max_wait_seconds=300,
)
```

### Retry strategy (error handling)

- The SDK can retry transient failures (e.g., rate limiting and gateway errors) with configurable strategy.

```python
from benchling_sdk.benchling import Benchling
from benchling_sdk.auth.api_key_auth import ApiKeyAuth
from benchling_sdk.retry import RetryStrategy

benchling = Benchling(
    url="https://your-tenant.benchling.com",
    auth_method=ApiKeyAuth("your_api_key"),
    retry_strategy=RetryStrategy(max_retries=3),
)
```

### Events and Data Warehouse

- **Events**: Benchling can emit events (e.g., entity updates, inventory transfers, workflow status changes) that can be routed via AWS EventBridge for near real-time integrations.
- **Data Warehouse**: Use SQL access for analytics/reporting (inventory trends, compliance reports, aggregations). Connection details and schemas are provided by Benchling.

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
- If a file is produced, prefer a deterministic output name such as `benchling_integration_result.md` unless the skill documentation defines a better convention.
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
Result file: benchling_integration_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
