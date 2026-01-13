---
name: extend-signal-schema
description: >
  Safely extend or refine AFI signal schemas and closely-related validators
  in afi-core, while preserving determinism, respecting PoI/PoInsight design,
  and obeying the AFI Droid Charter and AFI Core AGENTS.md boundaries.
---

# Skill: extend-signal-schema (afi-core)

## Purpose

Use this skill when you need to **extend or refine signal schemas** in afi-core,
adding new fields or validation rules to the Raw, Enriched, Analyzed, or Scored
signal schemas.

This skill ensures changes are:

- **Safe**: Backwards compatible where possible, with clear migration paths
- **Governed**: Aligned with AFI Droid Charter, AFI Droid Playbook, and afi-core/AGENTS.md
- **Correct**: PoI/PoInsight remain validator-level traits, NOT signal fields
- **Tested**: Schema changes include minimal test coverage

This skill is primarily used by `schema-validator-droid` and any future afi-core
droids that work on signal schemas and validators.

---

## Preconditions

Before changing anything, you MUST:

1. Read:
   - `afi-core/AGENTS.md`
   - AFI Droid Charter
   - AFI Droid Playbook
   - Target schema file(s) in `schemas/`

2. Confirm:
   - The requested change belongs in **afi-core** (signal language/validation),
     not in `afi-reactor` (orchestration) or `afi-token` (economics).
   - The change does **not** introduce PoI/PoInsight as signal fields.
   - The change does **not** require editing smart contracts, Eliza configs, or
     deployment/infra repos.

If any requirement is unclear or appears to violate AGENTS.md or Charter,
STOP and ask for human clarification instead of trying to be clever.

---

## Inputs Expected

The caller should provide, in natural language or structured form:

- **Target lifecycle stage**: Raw, Enriched, Analyzed, or Scored
- **Field name(s)**: The field(s) to add or refine
- **Type/shape**: e.g., `string`, `number`, `enum`, `object`, `array`
- **Optionality**: Required or optional? If optional, what's the default?
- **Description**: Brief explanation of field meaning and usage
- **Backwards compatibility**: Any migration concerns or breaking changes?

If any of this information is missing, ask clarifying questions or produce a
minimal, clearly-labeled stub with TODOs and conservative defaults.

---

## Step-by-Step Instructions

When this skill is invoked, follow this sequence:

### 1. Restate the requested change

In your own words, summarize:

- Which lifecycle stage (Raw/Enriched/Analyzed/Scored) is being modified
- Which field(s) are being added or changed
- The type, optionality, and purpose of each field
- Any backwards compatibility or migration concerns

This summary should be short and precise, so humans can quickly confirm the
intent.

---

### 2. Locate the schema files

Identify the relevant schema file(s), typically:

- `schemas/universal_signal_schema.ts` — Main signal schema (may cover all stages)
- `schemas/pipeline_config_schema.ts` — Pipeline configuration schema
- `schemas/signal_finalization_request_schema.ts` — Finalization request schema
- `schemas/validator_metadata_schema.ts` — Validator metadata schema

Or, if schemas are split by stage:

- `schemas/raw_signal_schema.ts`
- `schemas/enriched_signal_schema.ts`
- `schemas/analyzed_signal_schema.ts`
- `schemas/scored_signal_schema.ts`

Do **not** modify these yet; just understand the current structure.

---

### 3. Update the Zod schema

In the target schema file:

1. **Add new fields** with appropriate Zod types:
   - Use `.optional()` for optional fields
   - Use `.default(value)` for fields with defaults
   - Use `.enum([...])` for enumerated values
   - Use `.min()`, `.max()`, `.regex()` for validation rules

2. **Add clear comments** explaining:
   - Field purpose and usage
   - When the field is populated (which lifecycle stage)
   - Any constraints or validation rules

3. **Preserve existing fields**:
   - Do NOT silently rename or remove existing fields
   - If deprecating a field, mark it clearly and provide migration guidance

4. **Example**:

```typescript
// schemas/universal_signal_schema.ts

export const SignalSchema = z.object({
  // ... existing fields ...

  // ✨ NEW: Macro regime classification (Enriched stage)
  // Values: "risk_on" (bullish sentiment), "risk_off" (defensive), "neutral"
  macro_regime: z.enum(["risk_on", "risk_off", "neutral"]).optional(),

  // ... rest of schema ...
});
```

---

### 4. Update related type exports

If the schema has corresponding TypeScript types:

1. **Export the inferred type**:

```typescript
export type Signal = z.infer<typeof SignalSchema>;
```

2. **Update any registry interfaces** that reference the schema:
   - Check `runtime/types.ts` or `schemas/index.ts`
   - Ensure exported types match the updated schema

---

### 5. Update validators (if needed)

If the new field requires validation logic:

1. **Locate the relevant validator** in `validators/`:
   - `validators/SignalScorer.ts` — Signal scoring logic
   - `validators/index.ts` — Validator registry

2. **Add validation logic** if needed:
   - Check for required fields
   - Validate field values against business rules
   - Document any non-deterministic behavior

3. **Keep validators deterministic** where possible:
   - Avoid random values, timestamps, or external API calls
   - If non-deterministic, document clearly

---

### 6. Add or update tests

Where test patterns exist:

1. **Add unit tests** for the new field:
   - Test valid values
   - Test invalid values (should fail validation)
   - Test optional vs required behavior

2. **Update existing tests** if schema changed:
   - Fix tests that expect old schema shape
   - Add new test cases for new fields

3. **Example test locations**:
   - `tests/` — Vitest unit tests
   - `signal_schema_test/` — Schema-specific test suites

If no test patterns exist yet, leave a clearly marked TODO and surface this
in your summary.

---

### 7. Validate and build

Run at least:

- `npm run build` in `afi-core`

If relevant tests exist and are safe to run:

- `npm test` or `npm run test:run` (Vitest)

Do not mark the skill as "successful" if the build fails. Instead, stop, gather
error output, and surface it with minimal, clear commentary.

---

## Hard Boundaries

When using this skill, you MUST NOT:

- **Modify orchestration logic** in afi-reactor:
  - Do NOT edit DAG wiring, pipeline execution, or orchestration code.
  - Schema changes belong in afi-core; DAG wiring belongs in afi-reactor.

- **Introduce PoI/PoInsight as signal fields**:
  - Do NOT add `poi`, `poinsight`, `proof_of_intelligence`, or similar fields.
  - PoI/PoInsight are validator-level traits, NOT signal-level fields.
  - If a request asks for this, STOP and escalate.

- **Touch token/economics**:
  - Do NOT modify smart contracts, emissions, or tokenomics in afi-token.

- **Modify Eliza agents or gateways**:
  - Do NOT edit Eliza agent configs, character specs, or runtime behavior.
  - Do NOT modify afi-gateway.

- **Touch infra/ops**:
  - Do NOT modify deployment configs, Terraform, K8s, or CI/CD.

- **Perform large sweeping refactors**:
  - Do NOT restructure the entire schema architecture without explicit approval.
  - Do NOT rename or remove existing fields without a migration strategy.

- **Break backwards compatibility**:
  - Do NOT remove required fields without a deprecation path.
  - Do NOT change field types in breaking ways without human approval.

If a request forces you towards any of the above, STOP and escalate.

---

## Output / Summary Format

At the end of a successful `extend-signal-schema` operation, produce a short
summary that includes:

- **Lifecycle stage(s) modified**: Raw, Enriched, Analyzed, or Scored
- **Fields added/changed**: List each field with:
  - Field name
  - Type (string, number, enum, object, etc.)
  - Optionality (required or optional)
  - Brief description
- **Files created/modified**:
  - Schema file(s)
  - Validator file(s) (if any)
  - Type export file(s)
  - Test file(s)
- **Build/test results**: Pass or fail
- **Backwards compatibility**: Any breaking changes or migration notes
- **TODOs or open questions**: Any human decision points

Aim for something a human maintainer can read in under a minute to understand
exactly what changed and why.

---

## Example Usage Patterns

### Use This Skill For

- "Add an optional `macro_regime` field to Enriched signals with enum values
  `risk_on`, `risk_off`, `neutral`."

- "Extend the Scored schema to include a `risk_breakdown` object with sub-scores
  for `market_risk`, `liquidity_risk`, and `execution_risk`."

- "Add a `derivative_underlier` string field to Analyzed signals for
  options/futures-only signals."

- "Add a required `content` field to all signals (already exists, but make it
  required with a migration strategy)."

- "Refine the `action` field to include new enum values: `buy`, `sell`, `hold`,
  `close`, `reduce`."

### Do NOT Use This Skill For

- "Wire the new schema into the DAG pipeline."
  → Use `add-dag-node` skill in afi-reactor instead.

- "Add PoInsight as a field on Scored signals."
  → Violates PoI/PoInsight design (escalate to human).

- "Modify token emissions based on signal scores."
  → Belongs in afi-token (escalate to human).

- "Update Eliza agent character specs to use the new field."
  → Belongs in afi-gateway (escalate to human).

- "Add a new validator that calls an external API."
  → Requires explicit approval (escalate to human).

---

## Migration Strategy Guidance

When adding fields that may break backwards compatibility:

### For Optional Fields (Safe)

- Add field with `.optional()`
- No migration needed
- Document when the field is populated

### For Required Fields (Breaking)

- **Option 1**: Add as optional first, then require in a future version
- **Option 2**: Add with `.default(value)` to provide backwards compatibility
- **Option 3**: Provide explicit migration script or guidance

Always document the migration strategy in your summary.

---

## Example: Adding an Optional Field

**Request**: "Add an optional `macro_regime` field to Enriched signals."

**Summary**:

- **Stage modified**: Enriched (via `universal_signal_schema.ts`)
- **Field added**: `macro_regime`
  - Type: `enum(["risk_on", "risk_off", "neutral"])`
  - Optionality: Optional
  - Description: Macro regime classification for market sentiment
- **Files modified**:
  - `schemas/universal_signal_schema.ts` (added field)
  - `schemas/index.ts` (re-exported type)
- **Build/test results**: ✅ Pass
- **Backwards compatibility**: ✅ Safe (optional field)
- **TODOs**: None

---

## Example: Adding a Required Field with Default

**Request**: "Make `content` field required for all signals."

**Summary**:

- **Stage modified**: All stages (via `universal_signal_schema.ts`)
- **Field changed**: `content`
  - Type: `string` (min 1, max 280)
  - Optionality: Required (was optional)
  - Migration: Added `.default("")` for backwards compatibility
- **Files modified**:
  - `schemas/universal_signal_schema.ts` (changed optionality)
  - `tests/signal_schema.test.ts` (updated tests)
- **Build/test results**: ✅ Pass
- **Backwards compatibility**: ⚠️ Breaking change mitigated with default value
- **TODOs**: Consider removing default in v2.0 after migration period

---

**Last Updated**: 2025-11-27
**Maintainers**: AFI Core Team
**Charter**: `afi-config/codex/governance/droids/AFI_DROID_CHARTER.v0.1.md`

