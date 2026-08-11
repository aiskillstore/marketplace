---
name: gjalla-spec
description: Create a well-thought-out plan covering problem statement, goals, technical approach, and verification criteria. Use while planning / before implementing any non-trivial feature.
---

# Goal

The best, most elegant and effective software systems are ones that are well-informed, well-planned, and verifiable. 
The final output is a plan/spec that can act as a reference doc, covering the problem/motivation, technical approach, deltas (what properties of the system will change once implemented), and verification criteria.
The first step is always understanding the current state. Use gjalla (CLI or MCP) to fetch the relevant parts of the master spec, including the architecture, capabilities, data flows, etc that are relevant to this problem/solution space. Also fetch the gjalla rules so you know what boundaries there are on your final solution.
Once you undersatnd the relevant properties and constraints, identify any specific details that you need from the source code and gather them.
Now you have everything you can find yourself. Are there any outstanding questions that will affect the specifics of the solution you propose? If so, ask the user for input.

When you have everything you need, go ahead and use `gjalla spec new` which will scaffold a change spec for you to edit. This is necessary for workflows where specs are artifacts are canonical, and the gjalla platform will facilitate verifying and merging changes into the master spec once implementation is complete.
The user may prefer that you present the plan as a Claude Plan or a Cursor Plan (or another alternative based on your identity as an agent)... that's fine. Once the plan is approved for implementation, write the approved information into a gjalla spec and continue on.

The information needed for a production-grade spec / reference doc includes the following:
- **Problem Statement**: What user or system problem does this solve?
- **Goals**: What must be true when this is done?
- **Non-Goals**: What is explicitly out of scope?
- **Behavioral Requirements**: Observable behaviors the feature must exhibit, in other words, new capability properties that will be present within the system.
- **Technical Approach**: How will this be built? How will this affect architecture, data flows, surace area, and other gjalla primitives?
- **Verification Strategy**: Unit, integration, and acceptance test plan.
- **Dependencies**: What must exist or be deployed first?
- **Rollback Plan**: How to safely revert if something goes wrong.

## Guidelines
- Specs and plans are not novels. Background information and context is totally acceptable (in fact its preferred) as long as the information is clear, salient, and not overly verbose.
- The goal is to get ahead of unintended consequences (use second order thinking) and to make sure there are no surprises for the humans
