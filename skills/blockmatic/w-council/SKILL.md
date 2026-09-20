---
name: w-council
description: Explore a codebase with parallel agents, then hand off findings.
disable-model-invocation: true
---

Gather architecture and keywords for the requested area, then spawn a small set of varied explorers. This playbook inspects. It does not commit, push, or open a PR. Implementation continues only when the user already asked for it.

1. Inspect the area yourself first: owning packages, README/scripts, and current behavior. Record keywords and the architecture sketch the agents will use.
2. Spawn explorers only as needed. Default to 2–3 with distinct angles, including one out-of-the-box probe. Split larger investigations into separate bounded runs.
3. Reconcile reports against the tree. Prefer file evidence over agent summaries. If the working tree changed underfoot, re-verify before using a finding.
4. If the user asked only to investigate or plan, hand off. Follow [build](../w-build/SKILL.md) only if they already asked to implement — do not publish. For plans, include References, 3–5 assumptions, and deferrals per [plan](../w-plan/SKILL.md).
