# Operate Agent Relationships

Primary tools:
- `manage_contact`
- `manage_identity`
- `manage_relationship`
- `record_event`
- `manage_commitment`
- `inspect_affinity_item`
- `review_affinity`

Goal:
- Keep an operator's relationships with many non-human agents accountable and reviewable.

When to use:
- An operator coaches multiple agents through regular individual slots.

When not to use:
- Scheduling or dispatching work; the schedule itself lives in a task tool, not in Affinity.

Step-by-step sequence:
1. Locate or create the operator's owner-side contact and each agent with `manage_contact`, kind `agent`.
2. Attach an identity with `manage_identity`: type `custom:<system>-agent`, value `<id>`. This represents `custom:<system>-agent=<id>` and keeps names separate from stable routing keys.
3. Seed a professional relationship with `manage_relationship` action `seed_social_link`; set input.cadenceDays to a positive number for a fixed rhythm. Existing links use action `revise`, patch.cadenceDays; null unpins and returns to derived cadence.
4. Record each 1:1 as an interaction event with `record_event`, kind `interaction`, type `conversation`, and the agent as a participant. Record what happened, with conservative significance.
5. Record every agreed change with `manage_commitment`, action `record`, commitmentType `promise`, the agent as actor, and dueAt at its next slot. The owner is the recipient; the tool adds the owner when omitted.
6. At verification, resolve each promise as `kept` or `broken` according to the result, so trust reflects the track record. For kept outcomes, include options.resolvingEvent with type promise, summary, significance and occurredAt to record verification evidence and its trust effect. Broken outcomes create resolution evidence automatically. Do not resolve before verification.
7. Record the owner's open decisions as commitments on the owner-side contact without a due date. Review these alongside agent promises; resolve when the decision is made.
8. Inspect `contact_profile` for inline open commitments and use `review_affinity` for commitments.open and links.radar. Keep future slots and reminders in the task tool.

Validation checks:
- Each agent has kind agent and a unique system identity.
- Every agreed change has an actor, a promise and a verification outcome.
- Fixed rhythms show cadencePinned true; open decisions have no due date.

Pitfalls:
- A conversation summary alone does not represent an obligation.
- A missed promise is broken, not cancelled merely to avoid a trust consequence.
- Scheduled slots are not evidence that a 1:1 occurred.

Tips and tricks:
- Search identities before creating contacts to avoid duplicates.
- Inspect open commitments before each slot and verify outcomes afterward.

Related skills:
- `manage-promises-and-agreements`
- `review-radar-progression-and-graph`