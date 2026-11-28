---
id: "eventual-consistency-feedback"
title: "User feedback during asynchronous workflows"
category: "product"
summary: "Communicate the uncertainty of accepted-but-unfinished work without encouraging duplicate actions."
aliases: ["eventual consistency ux","pending state","asynchronous confirmation","progress feedback","delayed status","süreç devam ediyor durum göstergesi","iş gecikince kullanıcıya geri bildirim","gönderim işleniyor durumu"]
decisions: [{"when":"Completion is delayed but progress is observable","use":"Show a durable operation ID and stable pending, complete and failed states with bounded polling or notifications.","tradeoff":"Clients need consistent status and clear retry affordances."},{"when":"The user needs a final confirmation before proceeding","use":"Wait within a clear deadline and present pending or recoverable failure when the result is not yet known.","tradeoff":"The interaction can be slower, but uncertainty stays explicit."}]
checks: ["Leave and reopen the screen while the job is pending and verify consistent status.","Test repeated clicks, long-running jobs and an actionable failed state."]
sources: [{"title":"Azure asynchronous request-reply pattern","url":"https://learn.microsoft.com/en-us/azure/architecture/patterns/async-request-reply"},{"title":"W3C Web Content Accessibility Guidelines 2.2","url":"https://www.w3.org/TR/WCAG22/"}]
---

<!-- Generated record title. -->
# User feedback during asynchronous workflows

## Scenario

A document upload is accepted immediately but malware scanning and indexing finish later. The user can navigate away and return to the same job.

## Failure modes

Showing success before required checks finish creates a false promise. Polling aggressively can overload the service and a stuck job can leave users without recovery.

## Explain it simply

Tell users the work was received, show what is still pending and give them a way to recover if it stalls.

## Implementation guidance

Return an operation reference on acceptance and persist a status available after reload or reconnect. Distinguish pending, completed, failed and expired and expose a next action for each. Bound polling with a server hint or backoff. Test losing the initial response and reopening or safely retrying a stalled job from another tab.

<!-- Generated record details. Edit the YAML above and run npm run catalog. -->

## Decision rules

- **Completion is delayed but progress is observable** Show a durable operation ID and stable pending, complete and failed states with bounded polling or notifications. Clients need consistent status and clear retry affordances.
- **The user needs a final confirmation before proceeding** Wait within a clear deadline and present pending or recoverable failure when the result is not yet known. The interaction can be slower, but uncertainty stays explicit.

## Verification

- Leave and reopen the screen while the job is pending and verify consistent status.
- Test repeated clicks, long-running jobs and an actionable failed state.

## Sources

- [Azure asynchronous request-reply pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/async-request-reply)
- [W3C Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)

<!-- End generated record details. -->
