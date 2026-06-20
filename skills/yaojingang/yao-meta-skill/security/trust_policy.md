# Trust Policy

Yao Meta Skill treats scripts and distributed skill packages as supply-chain surfaces.

Governed or team-distributed skills should produce a trust report before release. The report must identify:

- secret exposure risk
- scripts that lack a visible CLI/help surface
- execution-level CLI `--help` smoke failures
- interactive or network-capable scripts
- bounded host policy for each network-capable script
- reviewer approval for each high-permission capability
- dependency pinning status
- runtime trust metadata
- package integrity hash

High-risk secrets or unrestricted remote inline execution block governed release.

Network-capable scripts without a matching `security/network_policy.json` entry remain reviewer-visible warnings until the host boundary is declared.

High-permission capabilities without valid `security/permission_policy.json` approvals block governed mode. Required approvals must name the reviewer, scope, reason, expiry, evidence, and target-enforcement mapping.
