# Record Observations And Referrals

Likes, reposts and follows are ambient observations, not milestones. Record them
with affectsBond:false. Like/follow/repost labels default to false across families;
explicit true opts in. Observations with significance <=2 also default to false.
They stay in journals but do not change affinity or meaningful-contact recency.
provenance.ambient:true also suppresses effects. Use explicit owner and other
participants, actor/recipient roles, and the correct directionality.
Unanswered owner_initiated evidence contributes much less and does not reset
radar recency. A relationship with only outbound activity gets no routine check-in
or drift prompt. other_initiated evidence counts fully. Observations and follow-like
milestones never derive breakthroughs; low-significance milestones derive no moment.

Primary tools:
- `record_event`
- `review_affinity`
- `inspect_affinity_item`

Goal:
- Add truthful third-party graph information while keeping observational evidence weaker than direct relationship evidence.

When to use:
- You learned that two people know each other, one person referred another, or you observed a third-party relationship pattern.
- You want the graph to reflect world truth without pretending you had the direct interaction yourself.

When not to use:
- The owner directly participated in the event and should record direct evidence instead.
- You merely suspect a relationship with no strong enough fact to justify recording it.

Step-by-step sequence:
1. Confirm the third-party contacts you are referring to.
2. Use `record_event` with `kind: "observation"` when the truth is observational rather than direct.
3. Keep significance modest unless the observed fact is genuinely consequential.
4. After recording, use `review_affinity` to inspect observed-link or graph views and verify the resulting topology.
5. If later direct evidence exists, record that separately rather than expecting the observation to do all the work.

Validation checks:
- The graph now reflects the third-party fact you meant to capture.
- Observed links stay appropriately weaker than direct links.
- No accidental owner-facing intimacy was invented.

Pitfalls:
- Do not use observations to fake deep trust or rank.
- Do not create a clique from vague group knowledge when the system only has justified pairwise facts.
- Do not promote a rumor to structure or direct evidence without better confirmation.

Tips and tricks:
- Referral chains are excellent observational facts because they help later review and graph interpretation.
- Use chart and observed-link review views together after batches of observation work.
- Observations are often better than silence, but they should remain humble.

Tool calls to prefer:
- `record_event` with `observation`
- `review_affinity` with observed-link and graph views
- `inspect_affinity_item` if you need exact follow-up on one target

Related skills:
- `record-direct-evidence-well`
- `review-radar-progression-and-graph`