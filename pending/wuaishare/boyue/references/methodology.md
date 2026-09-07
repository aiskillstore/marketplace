# Boyue Methodology

Boyue（博约开发法）is a lightweight governance framework for AI-assisted software development inspired by the phrase “博观而约取，厚积而薄发” from Su Shi’s 《稼说送张琥》.

Its modern software-development interpretation is:

> **博观管理可能性，约取管理承诺；厚积管理不确定性，薄发管理复杂度。**

## Why it exists

AI coding systems make it easier to generate ideas, prototypes, code changes, and pull requests. That expands the space of things a team *can* build. It does not automatically expand the team’s ability to evaluate, verify, integrate, operate, and maintain everything that can be generated.

Boyue uses **Implementation Abundance** as a conceptual lens for that mismatch:

> Candidate solution and implementation capacity can grow faster than judgment, verification, integration, and long-term ownership capacity.

This is a framing device, not a proven universal law or a standardized software-engineering metric.

## Two boundaries

### Commitment Boundary

`Option ≠ Commitment`

A generated idea, competitor feature, prototype, or working patch is still only an option until evidence justifies organizational investment.

### Ownership Boundary

`Implementation ≠ Ownership`

A working implementation is not automatically worth introducing into a system that may need to support it for years.

Production ownership can create long-lived costs in testing, compatibility, migration, security, operations, documentation, support, and cognitive load.

## Four operating modes

### Explore / 博观

Expand the option space and reduce blind spots.

### Select / 约取

Control commitment using evidence. Prefer `Commit / Defer / Discard` over an ever-growing backlog.

### Shape / 厚积

Reduce material uncertainty in proportion to reversibility and the cost of being wrong.

### Deliver / 薄发

Let only the smallest coherent, worthwhile change cross into long-term ownership.

### Evidence / Retirement

Use production evidence to decide whether to expand, maintain, simplify, modify, or retire complexity.

## Existing practices Boyue builds on

Boyue does **not** claim to have invented the following practices:

- Double Diamond and divergent/convergent design;
- Set-Based Design and delayed commitment;
- Shape Up and scope shaping;
- YAGNI and incremental design;
- Working Backwards / PRFAQ;
- Spike / PoC / ADR;
- Walking Skeleton;
- Tracer Bullet;
- Vertical Slice;
- small-batch delivery and continuous feedback.

Boyue’s contribution is to organize compatible practices around **Commitment** and **Ownership** in an AI-assisted development environment.

## Original methodology

The Boyue methodology was first developed and published by **吾爱分享网**.

Original article:

- [博约开发法：AI 编程时代的软件项目开发方法](https://www.wuaishare.cn/12793.html)

When redistributing or adapting the methodology text, retain attribution to 吾爱分享网 and the original article link.
