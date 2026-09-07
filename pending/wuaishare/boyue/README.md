English | [简体中文](README.zh-CN.md)

# Boyue Method

> **AI makes it easier to build the wrong thing faster.**

Boyue is a lightweight **AI development governance method and Agent Skill** for software teams and coding agents.

It helps teams explore broadly, commit selectively, validate expensive decisions, deliver coherent small changes, and retire complexity that no longer earns its maintenance cost.

[![Boyue Method — AI software development method](assets/boyue-cover-en.webp)](paper/boyue-methodology.md)

*Click the cover to read the full English methodology paper.*

## Project resources

The English project path is intentionally focused on English-language resources:

- **Full methodology paper:** [From Implementation Scarcity to Implementation Abundance](paper/boyue-methodology.md)
- **Installable Agent Skill (canonical execution source):** [SKILL.md](SKILL.md)
- **Methodology references:** [references/](references/)
- **Practical templates:** [templates/](templates/)
- **Usage examples:** [examples/](examples/)

The GitHub repository is the canonical home for the methodology paper, Agent Skill, templates, references, and examples.

## The idea in one sentence

> **Explore broadly. Prototype freely. Commit carefully. Own selectively.**

The name “Boyue” comes from a classical principle commonly rendered as: **study broadly, take selectively; accumulate deeply, release with restraint.**

In software-development terms:

> **Manage possibilities broadly, commitments selectively, uncertainty with evidence, and complexity with restraint.**

## Why Boyue exists

AI coding systems can generate ideas, prototypes, code changes, tests, and pull requests at a speed that was previously impossible for many teams.

That is valuable—but it creates a new failure mode:

```text
Cheap candidate generation
        ↓
More ideas and prototypes
        ↓
More accidental commitments
        ↓
More production ownership
        ↓
More maintenance, verification, migration, and compatibility cost
```

Boyue keeps two boundaries explicit:

### 1. Commitment Boundary

**Could Build ≠ Should Invest**

An idea, competitor feature, prototype, or working patch is still only an option until evidence justifies investment.

Choose:

- **COMMIT** — invest now;
- **DEFER** — preserve the option and define a revisit trigger;
- **DISCARD** — stop spending attention on it.

### 2. Ownership Boundary

**Should Build ≠ Should Own**

Working code is not automatically worth maintaining for years.

Before durable complexity enters production, ask:

> **If this must be maintained for three years, is it still worth adding?**

## Operating modes

Boyue is not a waterfall process. A real project may use multiple modes at the same time.

| Mode | Purpose | Typical practices |
|---|---|---|
| **Explore** | Expand the option space and reduce blind spots | user research, competitor research, Option Map, AI Spike |
| **Select** | Prevent options from becoming accidental commitments | PRFAQ, Non-goals, Commit / Defer / Discard |
| **Shape** | Reduce uncertainty according to the cost of being wrong | PoC, prototype, ADR, benchmark, rehearsal |
| **Deliver** | Ship the smallest coherent change worth owning | MCVS, Vertical Slice, Walking Skeleton |
| **Evidence / Retirement** | Decide whether existing complexity still deserves ownership | usage evidence, simplification, Retirement Review |

## The five rules

1. **Explore broadly without committing broadly.**
2. **Prototype freely; own selectively.**
3. **Options are cheap; commitments are expensive.**
4. **Shape according to the cost of being wrong.**
5. **Deliver the smallest coherent change worth owning.**

## What the Skill does

The installable [SKILL.md](SKILL.md) teaches an AI coding agent to:

- classify the current work as Explore / Select / Shape / Deliver / Evidence;
- avoid heavy process for small reversible edits;
- detect when new scope should cross a Commitment Boundary;
- detect when durable complexity should cross an Ownership Boundary;
- use disposable Spike / PoC work to validate uncertain AI capabilities;
- avoid silently promoting prototypes into production architecture;
- prefer the smallest coherent vertical slice for delivery;
- periodically consider simplification and retirement.

The Skill intentionally avoids arbitrary rules such as “AI must be 10× better” or “delete 80% of ideas”. Evidence and project context should drive decisions.

## Quick examples

### Small reversible edit

> “Change this label and adjust card spacing.”

Boyue should **not** add process overhead. Make the smallest safe change and verify it.

See [Feature Request](examples/feature-request.md).

### Scope expansion

> “While adding export, let’s also add scheduling, cloud sync, templates, and a public API.”

Boyue treats the new ideas as **Options**, then applies Commit / Defer / Discard rather than silently expanding scope.

### Hard-to-reverse architecture decision

> “Expose our internal extension mechanism as a public API.”

Boyue increases shaping depth because compatibility and migration obligations can last for years.

See [Architecture Change](examples/architecture-change.md).

### Uncertain AI capability

> “Can the model reliably extract structured findings from long documents?”

Boyue recommends a disposable capability Spike before production ownership.

See [AI Capability Spike](examples/ai-spike.md).

## Practical toolkit

### References

- [Methodology](references/methodology.md)
- [Commitment Boundary](references/commitment-boundary.md)
- [Ownership Boundary](references/ownership-boundary.md)
- [Risk-Adaptive Shaping](references/risk-adaptive-shaping.md)
- [Delivery Patterns](references/delivery-patterns.md)

### Templates

- [Option Map](templates/option-map.md)
- [Lightweight PRFAQ](templates/prfaq.md)
- [Commitment Decision Record](templates/decision-record.md)
- [Non-goals](templates/non-goals.md)
- [Risk Review](templates/risk-review.md)
- [Ownership Review](templates/ownership-review.md)
- [Retirement Review](templates/retirement-review.md)

### Examples

- [New AI Product](examples/new-ai-product.md)
- [Feature Request](examples/feature-request.md)
- [Architecture Change](examples/architecture-change.md)
- [AI Capability Spike](examples/ai-spike.md)

## Installation

Boyue is packaged as an Agent Skill with a root `SKILL.md` and supporting Markdown resources.

For Agent Skills-compatible CLI installers, the repository can be installed directly:

```bash
npx skills add wuaishare/boyue
```

See [DISTRIBUTION.md](DISTRIBUTION.md) for marketplace/registry status and licensing boundaries.

OpenAI Skills follow the Agent Skills open standard, and Skills are supported across ChatGPT, Codex, and the API, although installation and workspace management differ by host product.

### ChatGPT

Use the Skills interface to create/upload a skill from your computer or workspace. See OpenAI’s official documentation:

- https://help.openai.com/en/articles/20001066-skills-in-chatgpt

### Hosts that scan `~/.agents/skills`

For environments such as Desktop Commander setups that load skills from `~/.agents/skills/`:

```bash
git clone https://github.com/wuaishare/boyue.git ~/.agents/skills/boyue
```

Then start a new session or let the host refresh its skill registry.

### Other Agent Skills-compatible tools

Clone or copy the repository into the skill directory expected by the host. The host must support the Agent Skills layout and `SKILL.md` discovery.

## Suggested prompts

Boyue should normally activate automatically when relevant, but it can also be invoked explicitly:

```text
Use Boyue to evaluate whether this new feature belongs in the roadmap.
```

```text
Apply the Commitment and Ownership boundaries before implementing this architecture change.
```

```text
Use Boyue to design a disposable AI Spike for this uncertain model capability.
```

```text
Run a Retirement Review on this mature module and identify complexity we can safely remove.
```

## Design philosophy

Boyue is deliberately lightweight.

It should **not** turn a CSS change into a product committee meeting. Governance depth should rise only when reversibility decreases, failure cost rises, or long-term ownership materially grows.

> **Prototype can be disposable. Production should be deliberate.**

## Methodology origin and attribution

The Boyue methodology was originally developed and published by **Wuaishare**.

Canonical English resources:

- [Full methodology paper](paper/boyue-methodology.md)
- [Installable Agent Skill](SKILL.md)
- [Original illustrated article on Wuaishare (Chinese)](https://www.wuaishare.cn/12793.html)

When redistributing or adapting the methodology text, please retain attribution to **Wuaishare** and the original article link.

Boyue builds on and references existing software and product practices such as Double Diamond, Set-Based Design, Shape Up, YAGNI, Working Backwards, Spike / PoC, Walking Skeleton, Tracer Bullet, and Vertical Slice. This project does not claim to have invented those practices.

## License

Repository code and Skill files are released under the [MIT License](LICENSE).

The methodology attribution request above applies to redistribution or adaptation of the Boyue methodology text.
