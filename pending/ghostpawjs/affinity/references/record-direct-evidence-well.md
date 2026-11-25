# Record Direct Evidence Well

CLI and MCP share epoch ms, ISO with Z/offset, YYYY-MM-DD, DD.MM.YYYY,
today/yesterday/tomorrow and signed day offsets (+3d/-2d). Date-only inputs
preserve the calendar day at UTC midnight (UTC end of day for dueAt).
Keywords use the process local date. Read occurredOn/dueOn and review occursOn
for calendar dates; *Iso fields remain UTC. Future events carry future_event
warnings and do not count for recency, cadence or drift until their time and day
arrive. Commitments and resolutions never reset contact recency or cadence.

Imported text and event maintenance:
- Use externalRef: {source, id} for idempotent intake; retries return no_op and the existing id.
- Store verbatim text in content (up to 1,048,576 UTF-8 bytes, empty allowed). Summary is optional when content exists; its derived label is at most 140 characters.
- Use channel for the medium, parentRef or parentEventId for replies, and threadRef for the root. Event attributes use target {kind: "event", eventId} or {kind: "event", ref: {source, id}}. Unchanged values return no_op.
- Inspect kind "event" by eventId or ref. Search scope "events" or "all" discovers event ids; default scope remains contacts.
- Review journals/timelines with includeContent: true only when needed; CLI uses --with-content. Filter with channel. Review events.thread by ref for chronological context.
- Use manage_event revise with patch: summary, content, occurredAt, significance, channel, type within the same kind, or externalRef only when absent. Unknown keys fail validation.
- Use manage_event delete with confirm: true to remove incorrect evidence and recompute affected relationship scores.
- Send large payloads through whole-payload stdin or @file rather than argv. For example, affinity event record < payload.json or affinity call record_event - < payload.json.

Primary tools:
- `record_event`
- `inspect_affinity_item`
- `review_affinity`
- `manage_relationship`

Goal:
- Capture what really happened between the owner and other contacts so Affinity can derive progression, trust, cadence, and moments cleanly.

When to use:
- A conversation, activity, support exchange, conflict, correction, milestone, or direct operational interaction just happened.
- You want future radar, progression, journal, and chart views to reflect the event truthfully.

When not to use:
- You are importing pre-system history.
- You only observed third parties and were not directly part of the relationship evidence.

Step-by-step sequence:
1. Confirm the participants first. Use exact contacts whenever possible.
2. Use `record_event` with the smallest honest event family: `interaction` for ordinary direct evidence, `milestone` when the event is truly milestone-shaped, or another event family only when it better matches reality.
3. Set significance conservatively. Use high significance only when the event genuinely changed the relationship.
4. Let the system auto-create owner-facing links when appropriate instead of manually seeding a link just because a direct event happened.
5. Review the receipt or inspect the resulting profile when you need to understand the effect.
6. Use `review_affinity` on journal, timeline, moments, or readiness views when you need context after a sequence of events.

Validation checks:
- The right contacts were involved.
- The event family matches what really happened.
- The resulting mechanics feel plausible when reviewed.

Pitfalls:
- Do not inflate significance to force a rank-up.
- Do not turn ordinary direct evidence into a milestone just to get a dramatic moment.
- Do not use bond text as evidence. If the bond changed but no event happened, revise the bond separately.
- Do not guess through ambiguity; clarify the target first.

Tips and tricks:
- Conflict and correction are both first-class direct evidence. Use them honestly rather than hiding them inside generic summaries.
- Multi-participant owner events can refresh multiple links at once. That is a feature, not a bug.
- If you need to label the current narrative reading without changing mechanics, use `manage_relationship` with `revise_bond` after the evidence is recorded.

Tool calls to prefer:
- `record_event` for the evidence itself
- `inspect_affinity_item` for exact read-back
- `review_affinity` for journals, timelines, moments, and readiness
- `manage_relationship` only for bond interpretation after the fact

Related skills:
- `record-observations-and-referrals`
- `review-radar-progression-and-graph`