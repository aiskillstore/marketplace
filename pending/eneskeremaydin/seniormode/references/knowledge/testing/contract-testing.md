---
id: "contract-testing"
title: "Consumer contracts for API compatibility"
category: "testing"
summary: "Catch provider changes that break a real consumer's expectations before independent deployment."
aliases: ["consumer driven contract","pact","api compatibility test","provider verification","contract testing","tüketici sözleşme testi","eski istemci alanı kaldırılınca bozuluyor","sağlayıcı uyumluluğu"]
decisions: [{"when":"Consumers and providers deploy independently","use":"Publish consumer expectations and verify them in provider CI with controlled states.","tradeoff":"Contracts need stale-consumer retirement and representative provider fixtures."},{"when":"The entire call graph ships together","use":"Use a small number of integration tests through public boundaries and schema checks.","tradeoff":"Integration checks are more expensive but require less cross-team infrastructure."}]
checks: ["Enforce a consumer dependency with a failing compatibility change.","Verify adding irrelevant fields does not fail an existing contract."]
sources: [{"title":"Pact consumer-driven contract testing","url":"https://docs.pact.io/"},{"title":"OpenAPI 3.1 specification","url":"https://spec.openapis.org/oas/v3.1.0.html"}]
---

<!-- Generated record title. -->
# Consumer contracts for API compatibility

## Scenario

A billing provider removes a field that one older invoice client still requires. Both repositories' unit tests passed independently.

## Failure modes

Overly strict full-response snapshots freeze incidental fields. Provider mocks can drift if the provider never verifies consumer expectations.

## Explain it simply

Test the parts of the response each client actually relies on against the real provider.

## Implementation guidance

Write focused expectations from a real consumer and verify them in provider CI with controlled provider states. Include semantic constraints and deliberate nullability differences that a broad type schema can hide. Keep a representative end-to-end flow. Run the unchanged consumer’s verification before and after removing the required field and check that only the breaking behavior fails.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Consumers and providers deploy independently** Publish consumer expectations and verify them in provider CI with controlled states. Contracts need stale-consumer retirement and representative provider fixtures.
- **The entire call graph ships together** Use a small number of integration tests through public boundaries and schema checks. Integration checks are more expensive but require less cross-team infrastructure.

## Verification

- Enforce a consumer dependency with a failing compatibility change.
- Verify adding irrelevant fields does not fail an existing contract.

## Sources

- [Pact consumer-driven contract testing](https://docs.pact.io/)
- [OpenAPI 3.1 specification](https://spec.openapis.org/oas/v3.1.0.html)

<!-- End generated record details. -->
