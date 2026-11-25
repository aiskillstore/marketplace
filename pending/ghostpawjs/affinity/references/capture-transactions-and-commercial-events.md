# Capture Transactions And Commercial Events

Primary tools:
- `record_event`
- `inspect_affinity_item`
- `review_affinity`

Goal:
- Represent deals, placements, closings, sponsorships, and operationally meaningful exchanges as transactions instead of flattening them into generic social notes.

When to use:
- Money, deliverables, placements, closings, or other commercially meaningful exchanges just occurred.
- The relationship is service-oriented, professional, or business-critical.

When not to use:
- The main truth is a personal conversation or ordinary activity.
- The important action is really a promise or agreement that still needs later resolution.

Step-by-step sequence:
1. Confirm the right counterparties first.
2. Use `record_event` with `kind: "transaction"` for the commercial event itself.
3. Keep the summary concrete enough that future review explains what was exchanged and why it mattered.
4. Use significance according to the real business weight, not just enthusiasm.
5. Review the affected relationship if the commercial event should meaningfully change trust, cadence, or graph visibility.

Validation checks:
- The transaction now appears in the relevant timeline or journal views.
- The resulting relationship effect matches the commercial importance of the event.
- Later maintenance views now have the right recency signal.

Pitfalls:
- Do not bury closings, placements, or sponsorship deliveries inside generic conversations.
- Do not record a transaction when the truth is still only a pending agreement.
- Do not expect transactions to create the same kind of affinity movement as rich direct social evidence.

Tips and tricks:
- A relationship can be commercially strong and emotionally shallow. That is normal.
- Use transactions to preserve crisp operational history for later portfolio review.
- Follow major transactions with review views to confirm the graph and maintenance surfaces updated as expected.

Tool calls to prefer:
- `record_event` with `transaction`
- `inspect_affinity_item` for exact relationship read-back
- `review_affinity` for owner-link portfolio review

Related skills:
- `manage-promises-and-agreements`
- `review-radar-progression-and-graph`