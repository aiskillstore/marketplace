---
name: mindmap-helper
description: Organize requirements into Markdown/JSON mind map structures; use when you need a hierarchical outline for mind map tools (e.g., XMind, ProcessOn, FreeMind) or for documentation planning.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Converting product requirements into a clear multi-level outline for review and alignment.
- Preparing a mind map document to import into tools like XMind, ProcessOn, or FreeMind.
- Drafting an information architecture (IA) for documentation, onboarding guides, or knowledge bases.
- Summarizing a complex topic into balanced branches with consistent granularity.
- Producing a machine-readable hierarchy (JSON) for downstream processing or automation.

## Key Features

- Builds a hierarchical mind map structure from a topic, requirements, or notes.
- Supports two output formats:
  - **Markdown** (default): readable and easy to edit manually.
  - **JSON**: suitable for programmatic processing and tool import.
- Provides a **structure-first workflow**: draft the tree, then refine naming and granularity.
- Enforces naming and structure rules:
  - short phrases / noun phrases (avoid full sentences)
  - consistent granularity at the same level
  - recommended **5-9** sibling branches per parent (split if exceeded)
  - avoid duplicates/synonyms; merge when appropriate
- Handles missing information by producing a usable draft and marking items as "TBD/Optional/To confirm".

> Reference templates and examples: `references/mindmap_formats.md`

## Dependencies

- None

## Example Usage

### Input (prompt)

Create a mind map for "Mobile App Subscription System".  
Audience: product + engineering.  
Scope: subscription purchase, renewal, cancellation, and entitlement.  
Output: Markdown. Depth: 4-5 levels.

### Output (Markdown mind map)

- Mobile App Subscription System
  - Goals
    - Increase conversion
    - Reduce churn
    - Ensure entitlement accuracy
  - User Journeys
    - Purchase
      - Plan selection
      - Price display
      - Payment confirmation
      - Receipt / invoice
    - Renewal
      - Auto-renew rules
      - Renewal notification
      - Payment failure handling
    - Cancellation
      - Cancel entry points
      - Effective date rules
      - Win-back offers (Optional)
    - Restore Purchases
      - Platform restore flow
      - Cross-device sync
  - Product Rules
    - Plans
      - Monthly / yearly
      - Trial eligibility
      - Regional pricing
    - Entitlements
      - Feature gating
      - Grace period
      - Refund impact
    - Promotions
      - Intro offers
      - Coupons (TBD)
  - Platform & Integrations
    - iOS (StoreKit)
      - Product IDs
      - Receipt validation
      - Server notifications
    - Android (Google Play Billing)
      - Product IDs
      - Purchase tokens
      - RTDN notifications
    - Backend
      - Subscription state machine
      - Webhooks ingestion
      - Idempotency keys
  - Risks & Edge Cases
    - Payment failures
      - Retry policy
      - Dunning messaging
    - Refunds / chargebacks
      - Entitlement revocation timing
    - Account changes
      - Email change
      - Device migration
  - Metrics
    - Conversion funnel
    - Renewal rate
    - Churn reasons
  - Open Questions (To confirm)
    - Supported countries and currencies
    - Trial rules per platform
    - Tax/VAT invoice requirements

## Implementation Details

- **Workflow**
  1. Confirm topic, audience, scope boundaries, and desired depth (default **4-5 levels**).
  2. Produce a **structural draft first**, then refine branch names and granularity.
  3. Choose output format: **Markdown (default)** or **JSON**.
  4. Validate consistency: balanced hierarchy, consistent granularity at the same level, and short/clear naming.

- **Output rules**
  - **Markdown**: represent hierarchy using unordered list indentation.
  - **JSON**: root node contains `title` and `children` (each child follows the same structure).
  - If depth/format is not specified: default to **Markdown** with **4-5 levels**.

- **Naming rules**
  - Use phrases or noun phrases; avoid full sentences.
  - Keep sibling nodes at the same conceptual granularity.
  - Target **5-9** children per parent; split into sub-levels if exceeded.
  - Avoid repetition and synonyms; merge when necessary.
  - Default to English node names; preserve established technical terms when appropriate.

- **Missing information handling**
  - If topic/scope is unclear, still output a usable structure.
  - Mark uncertain branches/items explicitly (e.g., **TBD**, **Optional**, **To confirm**) so they can be validated later.

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

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `mindmap_helper_result.md` unless the skill documentation defines a better convention.
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

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: mindmap_helper_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Organize requirements into Markdown/JSON mind map structures; use when you need a hierarchical outline for mind map tools (e.g., XMind, ProcessOn, FreeMind) or for documentation planning.
