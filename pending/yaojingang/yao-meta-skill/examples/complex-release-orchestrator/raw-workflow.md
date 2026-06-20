# Raw Workflow

Every release we have to pull information from too many places and rebuild the same release packet by hand.

Current inputs are scattered across:

- merged PR summaries from the current milestone
- dependency update notes
- migration docs from backend and data teams
- rollout sequencing notes from on-call
- rollback conditions kept in an old runbook
- stakeholder announcements drafted in chat

What usually goes wrong:

- a migration note is missing when we think the release is ready
- rollback criteria are vague
- stakeholder communication is written too late
- someone says "ship it" before the packet has a clear go/no-go decision

What we want from the skill:

- ask for the minimum required release inputs
- produce one consistent release packet
- force a go/no-go summary
- call out missing release-critical details before approval
- keep deterministic artifacts separate from judgment calls
