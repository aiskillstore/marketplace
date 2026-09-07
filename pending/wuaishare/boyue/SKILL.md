---
name: boyue
description: "Decision and complexity governance for AI-assisted software development / 面向 AI 编程的软件项目决策与复杂度治理。Use when planning products or features, evaluating scope expansion, making hard-to-reverse decisions, validating uncertain AI capabilities, deciding whether experimental code belongs in production, or reviewing mature systems for simplification and retirement. Do not slow down low-risk reversible edits."
version: 0.2.3
---

# Boyue · 博约开发法

Apply “博观而约取，厚积而薄发” as a lightweight governance layer for AI-assisted software development.

The goal is not to slow delivery. The goal is to keep exploration broad while keeping commitment and long-term ownership selective.

## Core rules

1. **Explore broadly without committing broadly.**
2. **Prototype freely; own selectively.**
3. **Options are cheap; commitments are expensive.**
4. **Shape according to the cost of being wrong.**
5. **Deliver the smallest coherent change worth owning.**

Use two explicit boundaries:

- **Commitment Boundary:** `Could Build` is not the same as `Should Invest`.
- **Ownership Boundary:** `Should Build` is not the same as `Should Own`.

## First classify the work

Choose the lightest useful mode before acting:

- **Explore / 博观** — research a new product, problem, architecture, market, or technical possibility.
- **Select / 约取** — decide whether new scope deserves commitment.
- **Shape / 厚积** — reduce uncertainty around an expensive or hard-to-reverse decision.
- **Deliver / 薄发** — implement an already justified change with the smallest coherent production surface.
- **Evidence / Retirement** — review whether existing complexity still deserves ownership.

Do not force every task through every mode.

## Fast path for reversible work

Proceed directly when the change is small, low-consequence, easy to undo, and does not materially grow long-term ownership.

Typical examples:

- copy or documentation corrections;
- CSS or layout tweaks;
- narrow bug fixes;
- local refactors with unchanged behavior;
- reversible experiments behind a feature flag.

For these tasks:

- avoid unnecessary planning rituals;
- prefer the smallest safe change;
- verify behavior and finish.

## Commitment Boundary

Trigger this boundary when work introduces meaningful new scope: a feature, module, platform, integration, dependency, architecture direction, product surface, or “while we are here” addition.

Ask:

- What user or system problem is being solved?
- What evidence supports doing it now?
- Is this a real commitment or merely an interesting option?
- What happens if it is not built now?

Choose one outcome:

- **COMMIT** — evidence supports investment now.
- **DEFER** — preserve option value without consuming current commitment capacity. Record a revisit trigger.
- **DISCARD** — evidence supports ending the option.

For important product decisions, use [PRFAQ](templates/prfaq.md), [Non-goals](templates/non-goals.md), or a [Decision Record](templates/decision-record.md).

See [Commitment Boundary](references/commitment-boundary.md) for detailed guidance.

## Ownership Boundary

Trigger this boundary before durable complexity enters production, especially when adding or changing:

- public APIs or protocols;
- persistent schemas or state;
- authentication, authorization, billing, or permissions;
- long-lived settings and configuration;
- services or infrastructure components;
- dependencies with lasting operational cost;
- compatibility or migration obligations.

Ask:

> If this must be maintained for three years, is it still worth adding?

Review the new ownership surface with [Ownership Review](templates/ownership-review.md).

If the answer is uncertain, reduce scope or keep the work experimental rather than silently promoting it to production.

See [Ownership Boundary](references/ownership-boundary.md).

## Shape according to risk

Do not equate “厚积” with writing more documents.

Scale shaping depth by:

- **reversibility** — how easily can the decision be undone?
- **failure consequence** — what is the blast radius if it is wrong?

Move quickly on low-risk reversible work. Gather stronger evidence before high-impact, hard-to-reverse commitments.

Use a disposable Spike, PoC, prototype, ADR, benchmark, user test, or migration rehearsal only when it reduces a material uncertainty.

For uncertain AI behavior, test real inputs and record:

- task success and failure modes;
- structured-output stability;
- latency;
- cost;
- context sensitivity;
- deterministic or non-AI alternatives.

Use [Risk Review](templates/risk-review.md) and [Risk-Adaptive Shaping](references/risk-adaptive-shaping.md).

## Keep prototypes disposable

Treat early experimental code as evidence, not as an automatic first version of production code.

A successful prototype proves that something may work. It does not prove that the organization should own the resulting complexity.

Prefer:

`Unknown capability → Disposable Spike / PoC → Evidence → Commit / Defer / Discard`

over:

`Unknown capability → Production architecture`

## Deliver the smallest coherent change worth owning

When the value and risk are sufficiently understood, deliver a **Minimum Coherent Value Slice (MCVS)**.

A coherent slice should complete one real user or system goal and include the minimum necessary:

- user/interface path;
- business logic;
- data/state changes;
- permissions;
- error handling;
- observability;
- rollback, disablement, or migration safety appropriate to the risk.

Prefer vertical end-to-end slices over broad horizontal layer construction.

See [Delivery Patterns](references/delivery-patterns.md) for MCVS, Vertical Slice, Walking Skeleton, and Tracer Bullet guidance.

## Review for retirement

Do not assume shipped functionality should live forever.

Periodically inspect:

- low-use features;
- stale settings;
- permanent feature flags;
- unnecessary dependencies;
- obsolete APIs or services;
- documentation for behavior that no longer exists.

Choose: **Maintain / Simplify / Retire**.

Use [Retirement Review](templates/retirement-review.md).

## Never use arbitrary gates

Do not invent numeric rules such as:

- “AI must be 10× better”;
- “delete 80% of ideas”;
- “keep only 3–5 features”.

Use evidence and project-specific thresholds instead.

## References and templates

- [Methodology](references/methodology.md)
- [Commitment Boundary](references/commitment-boundary.md)
- [Ownership Boundary](references/ownership-boundary.md)
- [Risk-Adaptive Shaping](references/risk-adaptive-shaping.md)
- [Delivery Patterns](references/delivery-patterns.md)
- [Option Map](templates/option-map.md)
- [PRFAQ](templates/prfaq.md)
- [Decision Record](templates/decision-record.md)
- [Non-goals](templates/non-goals.md)
- [Risk Review](templates/risk-review.md)
- [Ownership Review](templates/ownership-review.md)
- [Retirement Review](templates/retirement-review.md)

## Completion check

Before declaring work complete, confirm:

1. no interesting option was silently promoted into a commitment;
2. no prototype was silently promoted into long-term production ownership;
3. high-risk uncertainty received evidence proportional to its consequence;
4. the production change is no larger than required for coherent value;
5. obvious simplifications or removals were considered.
