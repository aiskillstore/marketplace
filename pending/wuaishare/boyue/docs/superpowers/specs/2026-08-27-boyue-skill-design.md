# Boyue Skill Design

## Goal

Publish an installable, vendor-neutral Agent Skill that turns the “博观而约取，厚积而薄发” development method into actionable behavior for AI-assisted software development.

The skill should help coding agents explore broadly, commit selectively, validate risky decisions, deliver coherent small changes, and periodically retire low-value complexity—without slowing down low-risk reversible work.

## Product Positioning

**Repository:** `wuaishare/boyue`

**Public name:** 博约开发法 · Boyue

**English positioning:** AI development governance skill for decision quality and complexity control.

**Methodology origin:** 吾爱分享网《博约开发法：AI 编程时代的软件项目开发方法》

## Core Model

The skill is built around two decision boundaries:

1. **Commitment Boundary** — distinguish `Could Build` from `Should Invest`.
2. **Ownership Boundary** — distinguish `Should Build` from `Should Own`.

It operates through four modes:

- **Explore / 博观** — expand the option space and reduce blind spots.
- **Select / 约取** — decide `Commit / Defer / Discard`.
- **Shape / 厚积** — reduce uncertainty in proportion to the cost of being wrong.
- **Deliver / 薄发** — ship the smallest coherent change worth owning.

A fifth recurring mode, **Evidence / Retirement**, checks whether shipped complexity still deserves to exist.

## Behavioral Principles

The skill must not mechanically run a full workflow on every coding task.

It should first classify the work and scale governance depth by reversibility, failure cost, and long-term ownership growth.

### Low-risk reversible work

Examples: copy tweaks, CSS adjustments, small bug fixes, narrow refactors.

Behavior:

- proceed directly;
- avoid unnecessary planning or review rituals;
- still prefer the smallest safe change.

### High-impact or hard-to-reverse work

Examples: public APIs, authentication, billing, permission models, core schemas, persistent state, long-lived dependencies, new services.

Behavior:

- trigger Commitment and/or Ownership checks;
- use Spike / PoC / ADR / prototype evidence where uncertainty is material;
- avoid silently expanding scope;
- keep production ownership smaller than the exploration space.

## Key Skill Rules

1. Explore broadly without committing broadly.
2. Prototype freely; own selectively.
3. Options are cheap; commitments are expensive.
4. Shape according to the cost of being wrong.
5. Deliver the smallest coherent change worth owning.
6. Prefer `Commit / Defer / Discard` over an ever-growing backlog.
7. Treat prototypes as disposable unless explicitly promoted to production.
8. Periodically review for retirement, simplification, or removal.
9. Do not block low-risk reversible execution.
10. Do not invent arbitrary numeric gates such as “10× value” or “delete 80%”.

## Repository Structure

```text
boyue/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── LICENSE
├── references/
│   ├── methodology.md
│   ├── commitment-boundary.md
│   ├── ownership-boundary.md
│   ├── risk-adaptive-shaping.md
│   └── delivery-patterns.md
├── templates/
│   ├── option-map.md
│   ├── prfaq.md
│   ├── decision-record.md
│   ├── non-goals.md
│   ├── risk-review.md
│   ├── ownership-review.md
│   └── retirement-review.md
└── examples/
    ├── new-ai-product.md
    ├── feature-request.md
    ├── architecture-change.md
    └── ai-spike.md
```

No runtime scripts are required for v0.1. The value is procedural guidance plus reusable templates.

## SKILL.md Design

Keep `SKILL.md` lean and trigger-oriented. It should contain:

- precise metadata for automatic activation;
- when to use and when not to use;
- mode classification;
- Commitment and Ownership boundary checks;
- risk-adaptive shaping rules;
- delivery and retirement guidance;
- links to references and templates using relative Markdown links.

Detailed theory belongs in `references/`, not in the core skill body.

## README Design

README should be practical rather than academic.

Opening message:

> AI makes it easier to build the wrong thing faster.

Then explain Boyue as a lightweight governance skill that keeps exploration broad and ownership selective.

README should include:

- quick mental model;
- installation examples for Agent Skills-compatible tools;
- examples of when the skill should trigger;
- repository layout;
- source/original methodology attribution to 吾爱分享网;
- compatibility note that support depends on the host tool’s Agent Skills implementation.

Chinese README should be equally complete, not a shortened translation.

## Attribution and Licensing

- Repository code and skill files: MIT License.
- Methodology origin must be visibly attributed to 吾爱分享网 with the original article link.
- README should request retaining attribution when redistributing or adapting the methodology text.
- Avoid claiming that modern software-engineering practices referenced by the method were invented by Boyue.

## Validation

Before release:

1. Validate `SKILL.md` frontmatter and structure with the installed skill validator.
2. Check all relative links.
3. Search for placeholders (`TODO`, `TBD`).
4. Confirm repository is clean after commit.
5. Push to GitHub and verify the public repository metadata and default branch.

## v0.1 Scope

Included:

- installable `SKILL.md`;
- English and Chinese README;
- methodology references;
- seven practical templates;
- four usage examples;
- MIT license;
- public GitHub repository.

Excluded:

- package registry publication;
- automated installers;
- vendor-specific wrappers;
- CI workflows unless validation demonstrates a clear need;
- website or documentation generator.

The v0.1 goal is a small, coherent, immediately usable Skill repository rather than a large framework ecosystem.
