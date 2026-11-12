---
name: json-contract-tester
description: Guide validation of batches of JSON API or AI-agent outputs against a documented subset of JSON Schema, with explicit limitations and safe handling of sample data.
---

# JSON Contract Tester

## Purpose
Help developers check whether multiple JSON outputs conform to one declared contract before using them in an API or AI-agent workflow.

## Workflow
1. Ask for a JSON Schema and one or more representative JSON outputs. Remind the user to redact secrets, personal data, and confidential production payloads.
2. Explain the supported subset before interpreting a PASS/FAIL result.
3. Use the public browser tool for local validation when appropriate: https://falconprojectai-arch.github.io/falcon-ai-decision-engine/products/json-contract-tester/
4. Interpret validation errors using the reported JSON Pointer paths. Separate syntax errors from contract mismatches.
5. Suggest a minimal correction to the schema or payload only when the intended contract is clear.
6. For CI integration, explain that the browser tool exports JUnit XML locally; it does not run CI jobs or upload artifacts.

## Supported subset
type, required, properties, additionalProperties=false, items, enum, const, minimum, maximum, minLength, maxLength, pattern, minItems, and maxItems.

## Important limitations
- One JSON value per non-empty line; object/array schema nodes only.
- No $ref/$defs, allOf/anyOf/oneOf/not, format checks, boolean schemas, or additionalProperties schemas.
- Pattern uses the browser's JavaScript regular-expression engine; unknown keywords are ignored.
- A PASS means only that the value matches the supported rules, not the complete JSON Schema specification.
- Use a full validator for production or security-critical contracts.
- The companion browser tool runs locally and does not upload inputs.
