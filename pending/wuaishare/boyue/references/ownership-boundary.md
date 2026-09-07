# Ownership Boundary

The Ownership Boundary separates **what is worth implementing** from **what is worth maintaining as part of the long-term system**.

> **Implementation ≠ Ownership**

A prototype, PoC, or even a tested patch can be useful evidence without belonging in production.

## Trigger conditions

Run an Ownership check before introducing durable complexity, especially:

- public APIs, protocols, or extension contracts;
- persistent schemas, storage formats, or state;
- authentication, authorization, billing, or permission rules;
- settings and configuration that users will depend on;
- new services, queues, workers, or infrastructure components;
- long-lived dependencies with upgrade or supply-chain cost;
- migrations or compatibility obligations;
- workflows that users or third parties will integrate into their own processes.

## Core question

> **If this must be maintained for three years, is it still worth adding?**

This question deliberately shifts attention from creation cost to ownership cost.

## Review the ownership surface

For each proposed production change, identify whether it adds:

- API surface;
- persisted data or migration duties;
- UI states and settings;
- security boundaries;
- operational components;
- monitoring and alerting duties;
- compatibility promises;
- new documentation or support obligations;
- third-party dependency risk.

Then ask:

1. Can the scope be smaller?
2. Can it remain experimental?
3. Can it be made reversible?
4. Can an existing component solve the problem?
5. Is a new setting, service, API, or dependency truly necessary?

## Possible outcomes

### OWN

Accept the long-term responsibility intentionally.

### REDUCE

Keep the value while shrinking the ownership surface.

Examples:

- keep the capability internal instead of exposing a public API;
- avoid a new setting by choosing a strong default;
- reuse an existing service instead of creating another one;
- gate the feature behind an experimental interface.

### REJECT

Keep the prototype or evidence, but do not move the complexity into production.

## Useful artifact

Use [Ownership Review](../templates/ownership-review.md) before high-impact production commitments.
