---
id: "schema-validation"
title: "Schema validation at integration boundaries"
category: "backend"
summary: "Validate data received across trust and ownership boundaries before it changes state or reaches downstream code."
aliases: ["json schema","boundary validation","payload validation","strict decoding","schema evolution","gelen verinin şemasını doğrulama","mesaj alanları doğrulama","eski yeni veri biçimi"]
decisions: [{"when":"The input contract is versioned and intentionally extensible","use":"Validate required structure, bound sizes and validate business rules after safe parsing.","tradeoff":"Forward compatibility needs a consistent policy for unknown fields."},{"when":"Commands cross a closed or security-sensitive boundary","use":"Use strict allowed fields and explicit conversions, report stable validation codes.","tradeoff":"Changes require coordinated schema evolution."}]
checks: ["Test malformed, oversized and unexpected input without creating state.","Run representative old and new payloads across mixed deployments."]
sources: [{"title":"JSON Schema validation specification","url":"https://json-schema.org/draft/2020-12/json-schema-validation"},{"title":"OpenAPI 3.1 specification","url":"https://spec.openapis.org/oas/v3.1.0.html"}]
---

<!-- Generated record title. -->
# Schema validation at integration boundaries

## Scenario

Two teams exchange job messages through a broker. A producer can deploy ahead of the consumer and send a new optional field.

## Failure modes

A schema alone does not enforce domain invariants. Rejecting every new field can break compatible deployments, and unsafe coercion can turn malformed input into a valid-looking operation.

## Explain it simply

Check shape and values when a message enters the system, then check the business rules before acting.

## Implementation guidance

Validate size, framing and syntax before allocating work or coercing types. Validate the incoming DTO against its compatibility rules, then enforce domain invariants where the state change occurs. Keep a stable error code and targeted field location while omitting sensitive values. Include fixtures with an absent required field, an extra optional field from a newer producer, and a structurally valid command that violates the business rule.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The input contract is versioned and intentionally extensible** Validate required structure, bound sizes and validate business rules after safe parsing. Forward compatibility needs a consistent policy for unknown fields.
- **Commands cross a closed or security-sensitive boundary** Use strict allowed fields and explicit conversions, report stable validation codes. Changes require coordinated schema evolution.

## Verification

- Test malformed, oversized and unexpected input without creating state.
- Run representative old and new payloads across mixed deployments.

## Sources

- [JSON Schema validation specification](https://json-schema.org/draft/2020-12/json-schema-validation)
- [OpenAPI 3.1 specification](https://spec.openapis.org/oas/v3.1.0.html)

<!-- End generated record details. -->
