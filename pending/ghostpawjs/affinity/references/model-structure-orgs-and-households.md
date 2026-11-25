# Model Structure, Orgs, And Households

Primary tools:
- `manage_contact`
- `manage_relationship`
- `inspect_affinity_item`
- `review_affinity`

Goal:
- Capture the stable factual skeleton of the world: who belongs where, who reports to whom, and what entities are structurally connected.

When to use:
- You need to represent employment, family structure, team membership, households, or service affiliation.
- The fact should exist even if no emotional or operational relationship score is implied.

When not to use:
- You want to express how strong, strained, warm, or active a relationship feels.
- You are recording something that happened in time.

Step-by-step sequence:
1. Create or locate the entities involved.
2. Decide whether the fact is structural rather than relational. If the answer survives even with zero interaction history, it is usually structural.
3. Use `manage_relationship` with `action: "set_structural_tie"` to record the factual tie.
4. Include a role when the role clarifies the structure, such as job title or household role.
5. Inspect relevant profiles or review lists after large structural batches to confirm the world model is clean.
6. Remove or replace outdated ties when the world changes, such as a job move or team change.

Validation checks:
- The structural tie is visible and stable.
- No fake progression fields were introduced just to represent a factual tie.
- The chart and review surfaces now reflect the world structure you expect.

Pitfalls:
- Do not use structural ties to stand in for closeness, trust, or cadence.
- Do not seed social links just because a structural tie exists; only do that if a live relational track also matters.
- Do not leave outdated structural ties hanging after the factual world changes.

Tips and tricks:
- Structural and relational links can coexist. Use both when both truths matter.
- Groups, households, companies, teams, and services often deserve their own contacts.
- If you are unsure, ask whether the statement is about belonging or about lived relationship quality.

Tool calls to prefer:
- `manage_relationship` with `set_structural_tie`
- `inspect_affinity_item` to verify exact targets
- `review_affinity` for broader structural review

Related skills:
- `identify-and-locate-contacts`
- `record-direct-evidence-well`