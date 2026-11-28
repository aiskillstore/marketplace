---
id: "consent-derived-preferences"
title: "Preference updates and deferred changes"
category: "product"
summary: "Apply user preference changes with understandable scope and durable enforcement across asynchronous consumers."
aliases: ["preference setting","notification toggle","preference consistency","unsubscribe","opt out","bildirim tercihini kapatma","abonelikten çıkanlara kuyruktaki epostayı gönderme","gönderim öncesi tercih kontrolü"]
decisions: [{"when":"A preference forbids a later external action","use":"Persist an authoritative version, acknowledge the save and recheck at dispatch.","tradeoff":"Each delivery may require a fresh read or a versioned revocation path."},{"when":"A preference only changes low-risk local presentation","use":"Use local state with eventual synchronization and a documented conflict rule.","tradeoff":"Devices may briefly show different views."}]
checks: ["Revoke consent after enqueue and before dispatch authorization, and verify the provider receives no send request.","Race revocation against an in-flight handoff and verify the reported outcome follows the documented boundary.","Race cross-device updates and verify the final saved value is visible."]
sources: [{"title":"RFC 8058 one-click unsubscribe","url":"https://www.rfc-editor.org/rfc/rfc8058"},{"title":"PostgreSQL transaction isolation","url":"https://www.postgresql.org/docs/current/transaction-iso.html"}]
---

<!-- Generated record title. -->
# Preference updates and deferred changes

## Scenario

A team digest worker schedules emails in advance. A user turns off the digest while messages are already queued.

## Failure modes

The settings screen can show the new value before queued notifications honor it. A settings cache can republish an older preference after concurrent updates.

## Explain it simply

Save the setting and recheck it immediately before sending anything it controls.

## Implementation guidance

Persist consent and its revision with the authoritative preference update, then check policy again at dispatch. A scheduled job can carry its original revision for diagnostics while eligibility depends on current consent and purpose. Define when a send is authorized relative to a revocation. For example, serialize the preference change and the dispatch claim on the same record, then skip previously queued work that has not been claimed. A provider call from a prior claim can still be in flight. Make the product promise match the handoff boundary and use provider cancellation only where it is supported.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **A preference forbids a later external action** Persist an authoritative version, acknowledge the save and recheck at dispatch. Each delivery may require a fresh read or a versioned revocation path.
- **A preference only changes low-risk local presentation** Use local state with eventual synchronization and a documented conflict rule. Devices may briefly show different views.

## Verification

- Revoke consent after enqueue and before dispatch authorization, and verify the provider receives no send request.
- Race revocation against an in-flight handoff and verify the reported outcome follows the documented boundary.
- Race cross-device updates and verify the final saved value is visible.

## Sources

- [RFC 8058 one-click unsubscribe](https://www.rfc-editor.org/rfc/rfc8058)
- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)

<!-- End generated record details. -->
