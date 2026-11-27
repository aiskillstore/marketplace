---
id: "api-versioning"
title: "Evolving public API contracts"
category: "backend"
summary: "Preserve real client expectations as response schemas, validation and semantics evolve."
aliases: ["api versioning","backward compatibility","deprecation","api evolution","versioned endpoint","API sürümleme","eski istemci uyumluluğu","API alanını kullanımdan kaldırma"]
decisions: [{"when":"The change can be additive under current semantics","use":"Use a compatible optional field and verify service behavior with existing clients.","tradeoff":"Old fields need maintenance until deprecation criteria are met."},{"when":"Semantics must change incompatibly","use":"Publish an explicit version or new endpoint, migration guide and observed usage timeline.","tradeoff":"Running versions in parallel increases maintenance and verification."}]
checks: ["Use prior published clients to exercise the new API.","Test new capabilities and deprecation paths against the published compatibility contract."]
sources: [{"title":"Google AIP-180 backward compatibility","url":"https://google.aip.dev/180"},{"title":"OpenAPI 3.1 specification","url":"https://spec.openapis.org/oas/v3.1.0.html"}]
---

<!-- Generated record title. -->
# Evolving public API contracts

## Scenario

A calendar API moves from one host field to several participants. Several third-party clients may keep existing binaries installed.

## Failure modes

Changing the type of an existing field, changing default behavior or narrowing accepted inputs can break deployed clients. A new optional field can still matter to strict decoders.

## Explain it simply

Add new capabilities while keeping existing clients working, then give users time and guidance before retiring an old contract.

## Implementation guidance

Keep the established response field and its semantics while existing consumers move to the replacement. Take inventory of strict decoders, persisted payloads and clients you cannot upgrade before setting a retirement date. Exercise a representative old binary or consumer contract against the revised endpoint. A compatible new field may still need a rollout plan when the old field and new field can disagree.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **The change can be additive under current semantics** Use a compatible optional field and verify service behavior with existing clients. Old fields need maintenance until deprecation criteria are met.
- **Semantics must change incompatibly** Publish an explicit version or new endpoint, migration guide and observed usage timeline. Running versions in parallel increases maintenance and verification.

## Verification

- Use prior published clients to exercise the new API.
- Test new capabilities and deprecation paths against the published compatibility contract.

## Sources

- [Google AIP-180 backward compatibility](https://google.aip.dev/180)
- [OpenAPI 3.1 specification](https://spec.openapis.org/oas/v3.1.0.html)

<!-- End generated record details. -->
