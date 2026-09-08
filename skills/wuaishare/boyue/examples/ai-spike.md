# Example: AI Capability Spike

## Scenario

A team wants an AI feature that extracts structured findings from long technical documents.

The key uncertainty is not UI design. It is whether the model can produce reliable, affordable structured output on realistic inputs.

## Hypothesis

> A selected model can extract the required fields with sufficient reliability and acceptable latency/cost for the intended workflow.

## Disposable Spike

Build the smallest test harness needed to evaluate the capability. Do not reuse the spike as production architecture by default.

## Test data

Use a representative set containing:

- short and long documents;
- incomplete documents;
- noisy formatting;
- examples with missing target fields;
- examples containing ambiguous language.

## Evidence to collect

### Task success

Does the output contain the required information when present?

### Failure modes

Record unsupported claims, missed fields, invalid structure, and unstable behavior.

### Structured-output stability

How often does output conform to the required schema?

### Latency

Measure typical and slow-case response time.

### Cost

Estimate cost per real user task, not per isolated prompt.

### Context sensitivity

Does performance materially change with document length or irrelevant surrounding text?

### Non-AI alternative

Could deterministic parsing, search, rules, or a hybrid pipeline solve the task more reliably or cheaply?

## Decision

Choose one:

- **COMMIT** — evidence supports integrating the capability and proceeding to Ownership Review.
- **DEFER** — capability is promising but does not yet meet a named requirement; define a revisit trigger.
- **DISCARD** — evidence shows the AI approach is not justified for the current problem.

## Key lesson

A successful demo proves that the capability can work under tested conditions. It does not prove that the organization should own the prototype architecture or that the AI approach is the best production solution.
