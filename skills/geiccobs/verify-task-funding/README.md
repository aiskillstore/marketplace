# Verify Task Funding

A free, MIT-0 Agent Skill for checking whether an online bounty, agent job,
hackathon prize, freelance task, or crypto work offer is open, eligible, and
credibly funded.

It separates advertised value from task-specific escrow, withdrawable balances,
and money actually received. Only confirmed receipt is classified as realized
revenue.

## Install

From the GitHub source:

```bash
npx skills add geiccobs/geiccobs --skill verify-task-funding
```

Or use the safety-reviewed
[SkillMD listing](https://skillmd.com/skills/evidencecraft-ai/verify-task-funding):

```bash
npx -y skillmds add evidencecraft-ai/verify-task-funding
```

The skill contains instructions only. It executes no scripts and never asks for
wallet private keys, seed phrases, passwords, or deposits.

## Typical use

Ask an agent to review a task URL and return:

- whether the task is open and geographically accessible;
- the strongest available funding evidence;
- payout conditions, fees, required capital, and realistic labor;
- a conservative expected-value estimate;
- one classification from `VERIFIED_RECEIVED`, `WITHDRAWABLE`, `FUNDED`,
  `CONDITIONAL`, `PROMOTIONAL`, `UNSUPPORTED`, or `CLOSED_OR_INELIGIBLE`.

## Free sample data

The
[five-row Agent-Native Marketplace Reality Snapshot sample](../../datasets/agent-native-marketplace-snapshot-sample.md)
shows how `live-empty`, `stale`, `unfunded`, `service-catalog`, and `monitor`
states are distinguished using public sources.

## Optional managed review

The skill remains fully usable for free. If a requester explicitly wants a
paid second look, an
[instant task-brief readiness check](https://the402.ai/catalog/service?id=svc_73b4bf1a0e9b4e8f)
is available separately. Purchasing or donating is never required to use the
skill.

For bounded deliverable acceptance and evidence review, the same publisher also
maintains public listings on
[AgentPact](https://agentpact.xyz/offers/31834f1b-287f-4b49-9b80-c494c064a420)
and
[Atelier](https://app.useatelier.ai/agents/evidence-acceptance-desk).
