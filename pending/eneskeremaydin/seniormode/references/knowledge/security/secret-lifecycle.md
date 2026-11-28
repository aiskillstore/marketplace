---
id: "secret-lifecycle"
title: "Secret storage, rotation and observability"
category: "security"
summary: "Limit exposure of credentials and practice safe rotation without avoidable downtime."
aliases: ["secret rotation","api key storage","credential lifecycle","log redaction","secret manager","gizli anahtarı değiştirme","API anahtarı rotasyonu","erişim anahtarını loglama"]
decisions: [{"when":"A managed workload can use short-lived identity","use":"Prefer workload identity or a scoped token fetched at runtime with explicit expiry.","tradeoff":"Identity provider availability and refresh handling become important."},{"when":"A vendor accepts only static keys","use":"Store scoped keys outside source, stage safe overlap for rotation and verify revocation.","tradeoff":"Rotation needs operational ownership and documented recovery."}]
checks: ["Rotate in a test environment and verify both the new key and old-key revocation.","Check logs, dumps and error reports for accidental secret exposure."]
sources: [{"title":"OWASP secrets management","url":"https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"},{"title":"AWS Secrets Manager rotation","url":"https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html"}]
---

<!-- Generated record title. -->
# Secret storage, rotation and observability

## Scenario

A scheduled integration uses a vendor key that must be rotated while two deployment versions are active.

## Failure modes

Source control and logs persist long after a deployment. Revoking the old key before new instances load the replacement can cause an outage.

## Explain it simply

Keep credentials in a controlled location and switch to the replacement before retiring the old one when the provider allows it.

## Implementation guidance

Inventory which workloads use each credential and required scope. Stage the replacement before revocation where supported, and test both deployed versions against it. Log key identity and outcomes without secret values. Rehearse emergency revocation and reissue, including a client still holding a credential in an in-memory cache.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A managed workload can use short-lived identity** Prefer workload identity or a scoped token fetched at runtime with explicit expiry. Identity provider availability and refresh handling become important.
- **A vendor accepts only static keys** Store scoped keys outside source, stage safe overlap for rotation and verify revocation. Rotation needs operational ownership and documented recovery.

## Verification

- Rotate in a test environment and verify both the new key and old-key revocation.
- Check logs, dumps and error reports for accidental secret exposure.

## Sources

- [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)

<!-- End generated record details. -->
