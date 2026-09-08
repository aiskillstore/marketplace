English | [简体中文](boyue-methodology.zh-CN.md)

# From Implementation Scarcity to Implementation Abundance

## Decision Boundaries and Complexity Governance for AI-Assisted Software Engineering

### A Conceptual Framework for the Boyue Method

- **Author / Publisher:** Wuaishare
- **Project:** Boyue Method
- **GitHub:** https://github.com/wuaishare/boyue
- **Document type:** Conceptual Working Paper

> **博观而约取，厚积而薄发。**  
> Broadly observe and selectively take; accumulate deeply and release with restraint.  
> — Su Shi, *Jia Shuo Song Zhang Hu*

---

## Abstract

Generative AI and coding agents are changing the cost structure of software development. Traditional software engineering has long operated under implementation scarcity: ideas, requirements, and candidate solutions typically exceed the amount of work that a team can design, implement, test, deploy, and maintain. Engineering capacity therefore acts, imperfectly but materially, as a filtering mechanism.

Agentic coding weakens that natural filter. Modern coding agents can inspect repositories, propose solutions, modify multiple files, invoke tools, execute tests, and produce reviewable pull requests. The AIDev dataset identifies 932,791 agent-authored pull requests across 116,211 GitHub repositories, showing that agent-generated software changes have become a substantial real-world phenomenon. Yet cheaper candidate implementation does not imply equally cheaper evaluation, verification, integration, migration, security, compatibility, operations, or long-term maintenance.

Empirical evidence on overall AI developer productivity remains heterogeneous and fast-moving. METR’s 2025 randomized controlled trial of experienced open-source developers observed a 19% average slowdown for the early-2025 tools and tasks studied. In 2026, METR reported that newer tools likely produce more positive acceleration, while severe selection effects make a single reliable speedup estimate difficult. DORA’s 2025 research frames AI primarily as an amplifier of existing organizational strengths and weaknesses, and warns that teams without strong user-centricity can accelerate into a feature-factory mode rather than better outcomes.

This paper therefore proposes **Implementation Abundance** as a conceptual lens for AI-assisted software development: a condition in which an organization’s marginal capacity to generate candidate solutions and implementations materially exceeds its capacity to judge, verify, integrate, and sustainably own them.

The paper introduces two decision boundaries. The **Commitment Boundary** separates `Could Build` from `Should Invest`; the **Ownership Boundary** separates `Should Build` from `Should Own`. Building on Double Diamond, Set-Based Concurrent Engineering, Shape Up, YAGNI, Working Backwards, and small-batch delivery, the paper frames the Boyue method as four operating modes—**Explore, Select, Shape, Deliver**—with a recurring **Evidence / Retirement** loop.

The central proposition is:

> **Explore manages possibility, Select manages commitment, Shape manages uncertainty, and Deliver manages complexity.**

Boyue is not presented as a new waterfall process or a validated universal best practice. It is a lightweight conceptual governance framework for environments where AI makes exploration and candidate generation abundant. The paper operationalizes the framework through Commit / Defer / Discard decisions, risk-adaptive shaping, Minimum Coherent Value Slices, disposable spikes, ownership review, and retirement review, and concludes with four falsifiable research propositions for future empirical study.

**Keywords:** AI coding agents; agentic coding; software engineering; implementation abundance; product development; commitment governance; ownership governance; complexity governance

---

## 1. Introduction

### 1.1 Software development has historically assumed implementation is expensive

A feature that becomes part of a production system usually passes through problem discovery, requirements work, product and interaction design, architecture, implementation, testing, code review, deployment, monitoring, and long-term maintenance.

Because engineering capacity is finite, most product organizations have traditionally faced a basic inequality:

```text
Ideas and requirements
        >
Available engineering capacity
```

This scarcity is not a high-quality prioritization system by itself, but it creates friction. When a feature costs several engineer-weeks, teams are more likely to ask whether the user problem is real, whether the timing is right, whether a simpler solution exists, and whether the long-term maintenance burden is justified.

### 1.2 Agentic coding compresses the distance from idea to candidate implementation

Contemporary coding agents can traverse repositories, propose plans, modify several files, run commands and tests, and produce pull requests. AIDev’s large-scale dataset of agent-authored pull requests indicates that these workflows are now visible in real GitHub development at substantial scale [1].

The path from concept to candidate code can increasingly look like:

```text
Idea
  ↓
Prompt / Agent
  ↓
Prototype
  ↓
Working Patch
  ↓
Pull Request
```

This creates a powerful capability: teams can explore more solutions, compare alternatives, and test hypotheses faster.

It also creates a new temptation:

> “The agent already built it, so why not keep it?”

That reasoning conflates generation cost with ownership cost.

### 1.3 Implementation Cost ≠ Ownership Cost

A feature that enters production may create persistent obligations in:

- testing surface;
- UI and state space;
- public API compatibility;
- data migration;
- permissions and security;
- monitoring and operations;
- documentation and support;
- dependencies and upgrade paths;
- cognitive context required for future changes.

An agent may generate the initial implementation in minutes or hours. The organization may own the resulting complexity for years.

The central research question of this paper is therefore:

> **When candidate implementations become cheap to generate at scale, how can software teams prevent low-cost possibilities from prematurely becoming expensive long-term system obligations?**

---

## 2. Related Work

Boyue does not claim to invent divergence, convergence, delayed commitment, shaping, scope control, or incremental delivery. Its contribution is to reorganize these existing ideas around commitment and ownership under conditions of AI-driven candidate abundance.

### 2.1 Double Diamond

The Design Council’s Double Diamond models innovation as Discover, Define, Develop, and Deliver, with divergence and convergence across both problem and solution spaces [2]. Boyue inherits the value of broad exploration followed by deliberate convergence, but asks an additional AI-era question: when divergent solutions can be converted into working code almost immediately, what prevents options from becoming accidental commitments?

### 2.2 Set-Based Concurrent Engineering

Set-Based Concurrent Engineering, as documented in studies of Toyota product development, starts with sets of possible solutions and narrows them as evidence accumulates [3]. This supports Boyue’s distinction between preserving an option and committing resources to it.

Boyue therefore prefers a three-state decision:

- **COMMIT** — invest now;
- **DEFER** — preserve option value and define a revisit trigger;
- **DISCARD** — stop spending attention.

### 2.3 Shape Up

Shape Up distinguishes raw ideas from shaped work and describes shaped work as rough, solved, and bounded. It uses appetite, rabbit holes, and no-gos to reduce risk while avoiding excessive up-front detail [4][5].

Boyue adapts this insight into **Risk-Adaptive Shaping**: shaping depth should increase with the cost and irreversibility of being wrong, rather than applying the same design burden to every change.

### 2.4 YAGNI

Fowler’s discussion of YAGNI argues against adding software capability solely because it may be needed in the future [6]. AI coding increases the relevance of this discipline because speculative implementation becomes cheaper to generate while still adding present-day complexity.

### 2.5 Working Backwards and PRFAQ

AWS guidance describes Amazon’s Working Backwards approach as starting from intended customer value and using a press release and FAQ to clarify scope, assumptions, and outcomes before deriving implementation [7][8].

This maps naturally to Boyue’s Commitment Boundary: before asking AI how to build something, clarify why it should exist.

### 2.6 AI developer productivity research

METR’s 2025 randomized controlled trial observed a 19% slowdown for experienced developers working in mature repositories with early-2025 frontier tools [9]. In 2026, METR reported evidence consistent with newer tools providing more speedup, while selection effects made the magnitude difficult to estimate reliably [10].

DORA’s 2025 research describes AI as an amplifier of organizational capabilities and dysfunctions [11]. Its user-centricity guidance warns that code-generation acceleration without a strong outcome orientation can accelerate low-value feature production [12].

Together, these findings motivate a narrower claim than “AI makes software development cheap”: AI clearly expands the amount of candidate work teams can generate and attempt, while end-to-end productivity and organizational value depend on downstream judgment and system quality.

---

## 3. Implementation Abundance

### 3.1 Definition

This paper defines **Implementation Abundance** as:

> **A software-development condition in which an organization’s marginal capacity to generate candidate solutions and implementations materially exceeds its capacity to evaluate, verify, integrate, and sustainably own them.**

Three qualifications matter.

First, the claim concerns candidate implementations, not all production software.

Second, abundance is relative rather than universal. A team can be abundant in prototype generation while constrained in security review, migration, or platform integration.

Third, abundance does not imply higher total productivity. It can reallocate the bottleneck from generation to evaluation and ownership.

### 3.2 From scarcity to abundance

A traditional constraint can be represented as:

```text
Idea supply > implementation capacity
```

An AI-assisted constraint may increasingly become:

```text
Candidate generation capacity
        >
Judgment + Verification + Integration + Ownership capacity
```

The practical shift is subtle but important:

> **What can be built quickly can exceed what is worth owning.**

### 3.3 Boundary Compression

This paper uses **Boundary Compression** to describe the shrinking time and cost distance among Options, Commitments, and Implementations.

```text
Traditional:
Idea ─── Research ─── Design ─── Engineering ─── Production

AI-assisted:
Idea ─ Agent ─ Prototype ─ PR
```

Compression is valuable. It enables cheaper learning.

Risk appears when decision governance remains calibrated for the old scarcity regime. Two failure modes then become more likely:

- **Premature Commitment** — a prototype or patch is treated as proof that a roadmap commitment is warranted;
- **Premature Ownership** — generated code is promoted into the production system without sufficient consideration of durable ownership cost.

---

## 4. Two Decision Boundaries

### 4.1 Commitment Boundary: Could Build → Should Invest

The Commitment Boundary asks whether an option deserves organizational investment.

Ideas, competitor features, fashionable architectures, successful demos, and agent-generated patches remain Options until evidence supports a commitment.

The governing principle is:

> **Option ≠ Commitment**

The default decision vocabulary is:

- **COMMIT** — evidence supports investment now;
- **DEFER** — option value remains, but timing or evidence is insufficient;
- **DISCARD** — stop investing attention.

A DEFER decision should ideally include a revisit trigger, such as a usage threshold, repeated customer demand, a technical prerequisite, or a specific review date.

### 4.2 Ownership Boundary: Should Build → Should Own

A committed idea may still be better handled as a prototype, experiment, or temporary implementation rather than production architecture.

The Ownership Boundary asks:

> **Is this complexity worth maintaining as a durable part of the system?**

The governing principle is:

> **Implementation ≠ Ownership**

A useful review question is:

> **If we had to maintain this capability for the next three years, would we still choose to add it today?**

The “three years” is a heuristic for adopting a long-term ownership perspective, not a literal product-lifetime requirement.

---

## 5. The BYHB Loop

The phrase “博观而约取，厚积而薄发” serves as the naming metaphor for four operating modes rather than four sequential stages.

| Mode | Governance target | Objective | Typical practices |
|---|---|---|---|
| **Explore / 博观** | Option Space | reduce blind spots | research, comparison, spikes, alternative prototypes |
| **Select / 约取** | Commitment | reduce wrong commitments | PRFAQ, Non-goals, Commit / Defer / Discard |
| **Shape / 厚积** | Uncertainty | reduce expensive uncertainty | PoC, prototype, ADR, benchmark, rehearsal |
| **Deliver / 薄发** | Ownership Growth | control durable complexity | MCVS, vertical slice, feature flag |
| **Evidence / Retirement** | Existing Ownership | decide whether complexity still earns its cost | usage evidence, simplification, retirement review |

A project can use several modes simultaneously. A public API may be in Shape while a small feature is in Deliver and a future product direction remains in Explore.

### 5.1 Explore: broaden knowledge, not the roadmap

AI can be used aggressively in exploration: generate alternatives, test hypotheses, inspect competitors, build prototypes, and challenge assumptions.

The important distinction is that generated ideas are hypotheses, not obligations.

Exploration should stop when additional evidence has low marginal impact on the problem model, risk map, option categories, or likely decision.

### 5.2 Select: manage commitment quality

Selection is not successful because a high percentage of ideas is deleted. The objective is **Commitment Quality**.

Important options may use customer-value framing, evidence logs, PRFAQs, and explicit Non-goals. Small, low-risk work should not require heavyweight artifacts.

### 5.3 Shape: according to the cost of being wrong

Boyue rejects the idea that every change should receive a large up-front specification.

Instead:

> **Shape according to the cost of being wrong.**

Copy, styling, and reversible experiments can move quickly. Public APIs, authentication, billing, permission models, core schemas, and irreversible migrations deserve deeper evidence because mistakes create durable obligations.

### 5.4 Deliver: the smallest coherent change worth owning

Boyue uses **Minimum Coherent Value Slice (MCVS)** to describe a delivery unit that completes a real user-value loop while minimizing new durable system surface.

“Minimum” does not mean incomplete. “Coherent” means the slice includes the behavior, data, permissions, failure handling, observability, and rollback controls appropriate to its risk.

> **Thin scope is not thin quality.**

Vertical Slice, Walking Skeleton, Tracer Bullet, feature flags, and small-batch delivery can all be implementation techniques for achieving this principle.

---

## 6. Prototype Freely; Own Selectively

One of AI coding’s strongest advantages is cheap experimentation. Boyue should not suppress it.

The framework therefore explicitly separates experimental code from production ownership:

```text
Unknown capability
      ↓
Disposable Spike / PoC
      ↓
Evidence
      ↓
Commit / Defer / Discard
```

rather than:

```text
Unknown capability
      ↓
Production architecture
```

For AI-specific features, a disposable spike can test:

- capability on realistic inputs;
- structured-output reliability;
- long-context degradation;
- retrieval quality;
- latency and inference cost;
- failure modes;
- whether a deterministic non-AI alternative is simpler.

The operational principle is:

> **Prototype freely; own selectively.**

or, more strongly:

> **Generation may be aggressive; ownership should be conservative.**

---

## 7. Five Decision Gates

Boyue can be operationalized through five lightweight questions. They are not mandatory meetings or approvals.

### G1 — Exploration Gate

**Will more research or experimentation materially change the decision?**

### G2 — Commitment Gate

**Is there enough evidence to justify further investment?**

Outcome: `COMMIT / DEFER / DISCARD`.

### G3 — Risk Gate

**If this decision is wrong, how severe are the consequences and how difficult is reversal?**

This determines shaping depth.

### G4 — Ownership Gate

**Is this complexity worth owning over time?**

Outcome: `OWN / REDUCE / REJECT`.

### G5 — Evidence Gate

**Does real-world evidence still support the original decision?**

Outcome: `EXPAND / MAINTAIN / MODIFY / RETIRE`.

The meta-rule is:

> **Governance cost should scale with the cost of being wrong.**

---

## 8. Retirement as a First-Class Capability

Software complexity has a ratchet effect: adding features is easier than removing them.

Once shipped, a feature can accumulate users, data, integrations, documentation, compatibility obligations, and internal expectations. AI lowers the immediate cost of adding software more than it lowers the social and technical cost of removing it.

Boyue therefore treats **Retirement Review** as a normal lifecycle activity.

Questions include:

- Which features have persistently low usage?
- Which settings create state complexity without corresponding value?
- Which feature flags became permanent debris?
- Which dependencies are no longer justified?
- Which public interfaces or workflows should be simplified or removed?

If ownership cost exceeds sustained value, removing complexity is not failure—it is value creation.

---

## 9. Risk-Adaptive Governance

Any governance framework can become bureaucracy. Boyue therefore scales process by:

1. **Reversibility**
2. **Consequence of error**

| | Low consequence | High consequence |
|---|---|---|
| **Easy to reverse** | execute directly | validate with a small experiment |
| **Hard to reverse** | shape carefully | deep shaping + ownership review |

Examples:

- copy or CSS: direct execution;
- feature-flagged experiment: quick prototype;
- normal durable feature: lightweight commitment review + vertical slice;
- public API, auth, billing, core data: stronger commitment and ownership review.

Boyue is therefore not a method for slowing teams down. It is a method for keeping reversible work fast while allocating more reasoning to expensive mistakes.

---

## 10. Proposed Mechanism

The framework proposes the following causal mechanism for future validation:

```text
AI Candidate Generation ↑
          ↓
Options / Prototypes / Patches ↑
          ↓
Boundary Compression
          ↓
Premature Commitment / Ownership ↑
          ↓
Owned Complexity ↑
          ↓
Review / Verification / Integration / Maintenance ↑
          ↓
Context and coordination cost ↑
          ↓
Rework / instability risk ↑
```

This is not a claim that AI inherently produces technical debt. DORA’s amplifier framing suggests the opposite is also possible: strong systems and user focus can be amplified into better performance [11][12].

Boyue’s goal is to decouple **fast candidate generation** from **automatic production ownership**.

---

## 11. Research Propositions

Boyue is currently a conceptual framework. The following propositions are intentionally falsifiable.

### P1 — Abundance–Rework Proposition

Holding other factors approximately constant, if AI candidate-generation capacity grows faster than review and verification capacity while commitment and ownership governance remain unchanged, the proportion of reworked, abandoned, or rejected candidate implementations will increase.

### P2 — Commitment Governance Proposition

Teams using explicit Commit / Defer / Discard decisions should exhibit a lower Premature Implementation Rate than teams that convert AI-generated options directly into backlog commitments.

### P3 — Risk-Adaptive Shaping Proposition

Risk-adaptive shaping should reduce downstream rework for high-consequence, hard-to-reverse decisions, while over-application to low-risk reversible changes should increase lead time without equivalent benefit.

### P4 — Ownership Governance Proposition

At similar levels of delivered user value, teams using explicit Ownership Gates and Retirement Reviews should exhibit slower long-term growth in low-usage features, configuration surface, deprecated APIs, and unnecessary dependencies than teams optimizing primarily for feature throughput.

---

## 12. Operationalization and Future Research

### 12.1 Repository studies

Datasets such as AIDev make it possible to study agent-authored changes at scale [1]. Future work could track merge, close, revert, follow-up fixes, review duration, abandonment, and large subsequent rewrites.

Crucially, research should distinguish:

1. implementation failure;
2. product-value or priority failure.

The second category maps more directly to commitment quality.

### 12.2 Team-level controlled studies

A control process might be:

```text
Idea → Backlog → Agent → PR → Review
```

A Boyue-informed process might be:

```text
Option
  ↓
Commit / Defer / Discard
  ↓
Risk-Adaptive Shaping
  ↓
Ownership Gate
  ↓
MCVS
  ↓
Evidence / Retirement
```

Possible outcomes include lead time, review time, rework, change failure, adoption, feature removal, and durable ownership surface.

### 12.3 High-irreversibility case studies

Public APIs, authentication, billing, permission systems, plugin architectures, and database schemas provide useful settings for retrospective studies of premature commitment and ownership.

---

## 13. Practical Implications

If Implementation Abundance is a useful description of AI-assisted work, output metrics such as commits, pull requests, lines of code, feature counts, or agent-completed tasks become increasingly insufficient proxies for product progress.

DORA’s user-centricity research already warns that AI can accelerate feature-factory behavior when teams optimize output instead of outcomes [12].

More useful governance questions include:

- How many options are correctly deferred or discarded before production commitment?
- How much rework comes from “this should never have been built yet” rather than ordinary defects?
- How much long-term ownership surface does each shipped capability add?
- Are shipped capabilities actually used?
- Can the organization retire low-value complexity?

A strong AI engineering team may therefore be defined less by how much code its agents generate and more by its ability to explore broadly while keeping durable ownership selective.

---

## 14. Relation to “博观而约取，厚积而薄发”

This paper does not claim that Su Shi anticipated modern software engineering. The classical phrase functions as a naming metaphor and heuristic frame, not as technical evidence.

In the Boyue interpretation:

- **博观 / Explore** expands the option space without expanding the roadmap;
- **约取 / Select** governs commitments without eliminating optionality;
- **厚积 / Shape** reduces uncertainty in proportion to the cost of error;
- **薄发 / Deliver** limits durable complexity rather than product quality.

The compact formulation is:

> **Explore manages possibility; Select manages commitment; Shape manages uncertainty; Deliver manages complexity.**

For AI-assisted development:

> **Explore boldly, experiment widely, commit carefully, own selectively.**

---

## 15. Limitations

### 15.1 Implementation Abundance is not yet an established empirical construct

It is proposed here as a conceptual lens. Teams may differ dramatically in candidate-generation capacity, review capacity, operational constraints, and risk profile.

### 15.2 AI capability changes rapidly

The contrast between METR’s 2025 and 2026 findings illustrates how quickly tool capability and participant behavior can alter experimental interpretation [9][10].

### 15.3 Ownership complexity is difficult to quantify

APIs, UI states, settings, services, dependencies, migrations, and cognitive load are all forms of complexity, but they cannot be reduced safely to one universal scalar.

### 15.4 Governance can create governance debt

If every low-risk change requires PRFAQs, ADRs, and multiple decision gates, the framework becomes the complexity it was designed to reduce.

Risk-adaptive application is therefore a necessary condition of the method.

### 15.5 Longitudinal case evidence is still missing

The framework should be treated as a Conceptual Working Paper until validated on real projects through longitudinal case studies, controlled comparisons, and repository data.

---

## 16. Conclusion

Software engineering has historically been shaped by implementation scarcity. Coding agents are changing that constraint by making ideas, prototypes, and candidate code much cheaper and faster to generate.

The product objective, however, is not to maximize candidate code. It is to maximize durable user value.

As the amount of software that can be generated quickly begins to exceed the amount of software worth owning, teams must separate three questions:

> **Can we build it?**

> **Should we invest in it?**

> **Should we own it?**

The Commitment Boundary separates the first two. The Ownership Boundary separates the latter two.

Boyue therefore does not ask teams to explore less. It encourages faster and broader experimentation while resisting the automatic conversion of generated options into durable production obligations.

The central governance proposition is:

> **The core challenge of AI-assisted software engineering is not merely generating implementations faster, but preventing cheaply generated candidate implementations from prematurely becoming expensive long-term system obligations.**

The long-term optimization target is not Code Generation Rate, but:

> **the conversion efficiency from possibility to durable user value.**

That is the modern software-engineering interpretation of:

> **博观而约取，厚积而薄发。**

---

## References

1. Li, H., Zhang, H., & Hassan, A. E. **AIDev: Studying AI Coding Agents on GitHub**. 2026. https://arxiv.org/abs/2602.09185
2. Design Council. **History of the Double Diamond**. https://www.designcouncil.org.uk/resources/the-double-diamond/history-of-the-double-diamond/
3. Sobek II, D. K., Ward, A. C., & Liker, J. K. **Toyota's Principles of Set-Based Concurrent Engineering**. MIT Sloan Management Review, 1999. https://shop.sloanreview.mit.edu/store/toyotas-principles-of-set-based-concurrent-engineering
4. Singer, R. **Shape Up: Principles of Shaping**. Basecamp. https://basecamp.com/shapeup/1.1-chapter-02
5. Singer, R. **Shape Up: Write the Pitch**. Basecamp. https://basecamp.com/shapeup/1.5-chapter-06
6. Fowler, M. **YAGNI**. 2015. https://martinfowler.com/bliki/Yagni.html
7. AWS Well-Architected. **Prioritize customer needs to deliver optimal business outcomes**. https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/oa.ti.6-prioritize-customer-needs-to-deliver-optimal-business-outcomes.html
8. AWS Prescriptive Guidance. **Developing product strategies that deliver measurable business value**. https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/start-with-why.html
9. Becker, J., Rush, N., Barnes, B., & Rein, D. **Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity**. METR, 2025. https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf
10. METR. **We are Changing our Developer Productivity Experiment Design**. 2026. https://metr.org/blog/2026-02-24-uplift-update/
11. DORA. **State of AI-assisted Software Development 2025**. https://dora.dev/research/2025/dora-report/
12. DORA. **User-centric Focus**. https://dora.dev/capabilities/user-centric-focus/
13. DORA. **AI Capabilities Model**. https://dora.dev/ai/capabilities-model/report/
14. Wuaishare. **博约开发法：AI 编程时代的软件项目开发方法**. https://www.wuaishare.cn/12793.html

---

## Attribution

The Boyue methodology is an original methodology developed and published by **Wuaishare (吾爱分享网)**. When redistributing, translating, or adapting the Boyue methodology text, please retain attribution and the original source links:

- https://www.wuaishare.cn/12793.html
- https://github.com/wuaishare/boyue

Double Diamond, Set-Based Concurrent Engineering, Shape Up, YAGNI, Working Backwards, Vertical Slice, and other referenced methods remain the work of their respective authors and communities. Boyue does not claim authorship of those existing practices.
