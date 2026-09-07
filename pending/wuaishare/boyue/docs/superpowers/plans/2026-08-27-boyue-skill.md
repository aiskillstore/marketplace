# Boyue Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a small, installable, vendor-neutral Boyue Agent Skill repository with bilingual documentation, practical references, templates, examples, attribution, and validation.

**Architecture:** Keep `SKILL.md` as the lean behavioral router and move detailed theory into `references/`. Keep reusable project artifacts in `templates/` and concrete usage walkthroughs in `examples/`. No runtime code is needed for v0.1; validation is structural and link-based.

**Tech Stack:** Markdown, YAML frontmatter, Git, GitHub, installed Desktop Commander skill validator.

---

## File Structure

Create:

- `SKILL.md` — installable core Agent Skill and trigger behavior.
- `README.md` — English-first public landing page with Chinese navigation.
- `README.zh-CN.md` — complete Simplified Chinese landing page.
- `LICENSE` — MIT License.
- `references/methodology.md` — compact conceptual foundation and terminology.
- `references/commitment-boundary.md` — Commit / Defer / Discard decision guidance.
- `references/ownership-boundary.md` — long-term ownership review guidance.
- `references/risk-adaptive-shaping.md` — reversibility/failure-cost shaping model.
- `references/delivery-patterns.md` — MCVS, Walking Skeleton, Tracer Bullet, Vertical Slice.
- `templates/option-map.md` — option exploration template.
- `templates/prfaq.md` — lightweight Working Backwards template.
- `templates/decision-record.md` — commitment decision record.
- `templates/non-goals.md` — scope exclusion template.
- `templates/risk-review.md` — reversibility and consequence review.
- `templates/ownership-review.md` — production ownership surface review.
- `templates/retirement-review.md` — removal/simplification review.
- `examples/new-ai-product.md` — Explore → Select example for a new AI product.
- `examples/feature-request.md` — low-risk vs scope-expanding feature example.
- `examples/architecture-change.md` — high-irreversibility architecture example.
- `examples/ai-spike.md` — disposable AI capability spike example.

Keep existing:

- `docs/superpowers/specs/2026-08-27-boyue-skill-design.md`
- `docs/superpowers/plans/2026-08-27-boyue-skill.md`

---

### Task 1: Create the installable core Skill

**Files:**
- Create: `SKILL.md`

- [ ] **Step 1: Write YAML frontmatter**

Use:

```yaml
---
name: boyue
description: "Decision and complexity governance for AI-assisted software development. This skill should be used when planning new products or features, evaluating scope expansion, making hard-to-reverse architecture decisions, validating uncertain AI capabilities, deciding whether experimental code belongs in production, or reviewing mature systems for simplification and retirement. It should not slow down low-risk reversible edits."
version: 0.1.0
---
```

- [ ] **Step 2: Add a lean workflow**

The body must explicitly:

1. classify work as Explore / Select / Shape / Deliver / Evidence;
2. bypass heavy governance for low-risk reversible changes;
3. apply Commitment Boundary for new scope and Ownership Boundary for durable complexity;
4. prefer Commit / Defer / Discard decisions;
5. recommend disposable Spike / PoC for uncertain AI capability;
6. deliver the smallest coherent change worth owning;
7. run Retirement Review when evidence no longer supports complexity;
8. link to references and templates using relative Markdown links.

- [ ] **Step 3: Verify token discipline**

Run:

```bash
wc -w SKILL.md
```

Expected: compact core guidance, preferably below roughly 1,500 words.

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat: 添加博约开发法核心 Skill"
```

---

### Task 2: Add conceptual references

**Files:**
- Create: `references/methodology.md`
- Create: `references/commitment-boundary.md`
- Create: `references/ownership-boundary.md`
- Create: `references/risk-adaptive-shaping.md`
- Create: `references/delivery-patterns.md`

- [ ] **Step 1: Write methodology reference**

Include:

- Implementation Abundance as a conceptual lens, not a proven law;
- `Option ≠ Commitment`;
- `Implementation ≠ Ownership`;
- “博观管理可能性，约取管理承诺；厚积管理不确定性，薄发管理复杂度。”;
- original-methodology attribution to `https://www.wuaishare.cn/12793.html`;
- explicit note that Double Diamond, Shape Up, YAGNI, Working Backwards, Walking Skeleton, Tracer Bullet, and Vertical Slice are existing practices rather than Boyue inventions.

- [ ] **Step 2: Write boundary references**

`commitment-boundary.md` must define:

```text
COMMIT — evidence supports investment now
DEFER — preserve option value without consuming current commitment capacity
DISCARD — evidence supports ending the option
```

`ownership-boundary.md` must review durable surfaces:

```text
public API
persistent schema/state
settings/configuration
new services
long-lived dependencies
security/permission boundaries
operational and compatibility obligations
```

- [ ] **Step 3: Write risk-adaptive shaping reference**

Use a 2×2 model of reversibility and failure consequence. Explicitly say that low-risk reversible work should move fast, while high-impact irreversible work deserves deeper evidence.

- [ ] **Step 4: Write delivery-pattern reference**

Differentiate:

```text
MCVS — what size of value to own
Vertical Slice — how to cut across layers
Walking Skeleton — minimal end-to-end system path
Tracer Bullet — early end-to-end probe through uncertain technical terrain
```

- [ ] **Step 5: Commit**

```bash
git add references
git commit -m "docs: 添加博约方法论与边界参考"
```

---

### Task 3: Add reusable governance templates

**Files:**
- Create: `templates/option-map.md`
- Create: `templates/prfaq.md`
- Create: `templates/decision-record.md`
- Create: `templates/non-goals.md`
- Create: `templates/risk-review.md`
- Create: `templates/ownership-review.md`
- Create: `templates/retirement-review.md`

- [ ] **Step 1: Create Option Map template**

Sections:

```text
Problem / opportunity
Evidence
Candidate options
Unknowns
Constraints
Experiments
Options explicitly not committed
```

- [ ] **Step 2: Create lightweight PRFAQ template**

Sections:

```text
User
Problem
Outcome
Why now
Why existing alternatives are insufficient
FAQ
Non-goals
```

- [ ] **Step 3: Create commitment Decision Record**

Require one decision:

```text
COMMIT / DEFER / DISCARD
```

For DEFER require a revisit trigger.

- [ ] **Step 4: Create risk and ownership reviews**

`risk-review.md` must ask reversibility, blast radius, failure consequence, evidence, rollback, and required shaping depth.

`ownership-review.md` must ask:

> If this must be maintained for three years, is it still worth adding?

and enumerate new ownership surfaces.

- [ ] **Step 5: Create Retirement Review template**

Review features, settings, feature flags, dependencies, APIs, services, and documentation for maintain / simplify / retire decisions.

- [ ] **Step 6: Commit**

```bash
git add templates
git commit -m "feat: 添加博约治理模板"
```

---

### Task 4: Add four concrete usage examples

**Files:**
- Create: `examples/new-ai-product.md`
- Create: `examples/feature-request.md`
- Create: `examples/architecture-change.md`
- Create: `examples/ai-spike.md`

- [ ] **Step 1: New AI product example**

Show a broad option set becoming a narrow commitment set. Include at least one COMMIT, one DEFER, and one DISCARD decision.

- [ ] **Step 2: Feature request example**

Contrast a small reversible UI adjustment that proceeds directly with a “while we are here” scope expansion that triggers Commitment Boundary.

- [ ] **Step 3: Architecture change example**

Use a public API/auth/core-data type change. Show Risk-Adaptive Shaping, ADR evidence, rollback constraints, and Ownership Gate.

- [ ] **Step 4: AI Spike example**

Test model reliability, structured-output stability, latency, cost, failure modes, and a deterministic non-AI alternative. End in COMMIT / DEFER / DISCARD.

- [ ] **Step 5: Commit**

```bash
git add examples
git commit -m "docs: 添加博约开发法使用案例"
```

---

### Task 5: Publish bilingual public documentation and license

**Files:**
- Create: `README.md`
- Create: `README.zh-CN.md`
- Create: `LICENSE`

- [ ] **Step 1: Write English README**

Open with:

> AI makes it easier to build the wrong thing faster.

Include:

- Boyue positioning;
- mental model;
- two boundaries;
- five operating modes;
- install guidance that is vendor-neutral and clearly states host-tool compatibility varies;
- usage examples;
- repository structure;
- links to templates/references/examples;
- methodology origin attribution to 吾爱分享网;
- MIT license note.

- [ ] **Step 2: Write complete Chinese README**

Open with:

> AI 可以让错误的东西更快被做出来。

Cover the same content and depth as the English README.

- [ ] **Step 3: Add MIT License**

Use the standard MIT license with copyright:

```text
Copyright (c) 2026 wuaishare
```

- [ ] **Step 4: Commit**

```bash
git add README.md README.zh-CN.md LICENSE
git commit -m "docs: 完善中英文说明与开源许可"
```

---

### Task 6: Validate and publish v0.1

**Files:**
- Validate all created files.

- [ ] **Step 1: Validate Skill**

Run:

```bash
node ~/.agents/skills/skill-creator/scripts/validate-skill.mjs "$PWD"
```

Expected output contains:

```text
✅ Skill is valid!
```

- [ ] **Step 2: Check links and placeholders**

Run:

```bash
rg -n "TODO|TBD|PLACEHOLDER" . --glob '!docs/superpowers/plans/*'
```

Expected: no unintended placeholders.

Run a local Markdown-link check over relative repository links; every referenced file must exist.

- [ ] **Step 3: Inspect repository state**

Run:

```bash
git status --short
git log --oneline --decorate -8
```

Expected: only intentional uncommitted plan tracking changes, or a clean working tree after final plan update.

- [ ] **Step 4: Tag and push**

After all validation passes:

```bash
git tag -a v0.1.0 -m "博约开发法 Skill v0.1.0"
git push -u origin main
git push origin v0.1.0
```

- [ ] **Step 5: Verify GitHub publication**

Run:

```bash
gh repo view wuaishare/boyue --json name,url,description,visibility,defaultBranchRef
gh release create v0.1.0 --title "Boyue v0.1.0" --notes "首个公开版本：可安装的博约开发法 Agent Skill，包含中英文文档、方法论参考、治理模板和真实使用案例。"
```

Expected: public repository on `main` with a `v0.1.0` GitHub Release.
