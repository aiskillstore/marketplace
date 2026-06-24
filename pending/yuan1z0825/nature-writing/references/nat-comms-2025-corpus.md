# Nature Communications 2025 — Empirical Drafting Patterns (CS/AI corpus)

Use this file when drafting or restructuring a manuscript and you want
**genre-aware, evidence-backed structure calibration** beyond the generic
section fragments. The patterns below are distilled from a 2025 reading set of
20 open-access *Nature Communications* articles in computer science / AI
(research articles plus Perspective, Comment, Review, and benchmark/framework
papers). **Do not copy their wording.** Use the patterns to decide structure,
move order, and signal words; the short quoted fragments are pattern markers,
not text to reuse.

> Companion of `references/article-architecture.md` (generic move orders) and
> `nature-polishing/references/published-article-patterns.md`. This file adds
> the 2025 CS/AI evidence layer, quantified word preferences, and genre splits.

## 0. Decide the genre first — it picks the skeleton

| Genre | Skeleton |
|---|---|
| Research article | Abstract funnel → Intro (hook→gap→`Here we`) → Results (conclusion-first) → Discussion → Methods |
| Benchmark / framework | Same, but the *gap is "the field has no agreed standard"*; tables dominate; stress community / reproducibility / versioning |
| Review | Trend declaration → `This Perspective/Review explores…` → topic/modality chapters synthesising others' work → `Conclusions and outlook` |
| Perspective | History/era hook → numbered argument points → normative `X should…` advice → roadmap close |
| Comment | First-person singular, rhetorical question opening, analogy/history, no IMRaD, no abstract/figures |

State the detected genre before drafting; the rest of this file assumes a
research article unless noted.

## 1. Title

- Four recurring shapes, chosen by intent:
  - Noun phrase, method-led (most common): *AlphaFold prediction of structural ensembles of disordered proteins*
  - Declarative claim (the selling point is a finding): *Dendrites endow artificial neural networks with accurate, robust and parameter-efficient learning*
  - `System name: function` colon form (brands a tool/model): *CodonTransformer: a multispecies codon optimizer…*
  - Gerund/question for benchmark or Perspective: *Benchmarking large language models for…*; *Does provable absence of barren plateaus imply classical simulability?*
- An evaluative adjective often pre-loads the claim: *robust*, *generalizable*, *data-driven*.
- Almost never contains a number or a result; keep digits for the abstract.
- Prepositional chain carries "what + how + where": *…discovery and engineering **with** deep learning **using** CataPro*.

## 2. Abstract — the funnel

Five moves, one paragraph, 4–11 sentences (research longer, benchmark/active-learning tighter):

1. Field value / why-it-matters (present tense, often subject-less assertion)
2. Gap, almost always opened by **However** + a nominalised pain point
3. Hinge sentence: `Here we show/present/introduce X (FULL NAME, abbr.), a … that …`
4. One hard quantified result (a factor, %, or accuracy), past tense
5. Significance + optional resource link (GitHub)

Pattern markers: gap *"However, DE can be inefficient when mutations exhibit … epistatic behavior."*; hinge *"Here, we show that traditional fine-tuning outperforms zero- or few-shot LLMs in most tasks."*; close *"Our findings suggest…"* / *"These results indicate…"*.

## 3. Introduction

- **Hook**, three forms: importance declaration (*"The biological brain is remarkable in its ability to…"*); definition framing (*"Protein engineering is an optimization problem, where…"*); domain-then-obstacle (benchmark default: broad use → *"Despite its promises, progress … is impeded due to the absence of … benchmarks."*).
- **Gap** signal words cluster tightly: **However / remains / Unfortunately / underexplored / the scarcity of … hinder / Without X, Y cannot be …**. High-end move: quantify the scarcity — *"merely 124 (3.0%) have … structures in the PDB."*
- **Contribution**: `Here we…` / `In this work, we…`, usually with a `(Fig. 1)` pointer; multiple contributions as `First… Second… Finally…`.
- Make the **choice of system/problem explicit** — *"We chose this model system because…"* — this satisfies the "科学问题要科学" expectation: the question must be motivated, not assumed.

## 4. Results narrative

- **Subheadings** are either a conclusion sentence or a noun/gerund phrase naming the method — *"CodonTransformer generates DNA sequences with natural-like distributions"*, *"Exploring the biocatalytic synthesis landscape of McbA"*. Avoid neutral *Experiment 1 / Dataset* labels.
- **Conclusion-first**: the paragraph opens with the judgement, evidence and figure call follow — *"Interestingly, wt-McbA displayed a tolerance to multiple 'unprotected' functional groups…"*
- **Figure callouts**, two shapes: figure-led (*"Figure 3 (a) depicts the action distributions…"*) and trailing parenthetical (*"…synthesize 11 pharmaceutical compounds (Fig. 2C)"*).
- **Numbers** come as absolute + relative + direction — *"from 323.4 to 297.3 … representing an improvement of 8.8%"*; closing roll-up *"These findings collectively affirm that…"*.
- Paragraph-advance engine: `With [previous result], we next …` / `To <goal>, we <did> (Fig. X).`

## 5. Transitions (observed frequencies, 5-article subset)

`However` 51 ≫ `Furthermore` 22 · `Therefore` 19 · `Overall`/`Notably` 16 · `In addition` 13 · `In contrast` 6 · `Moreover` 4.
- **However** is the workhorse for turning, gap-opening, and surprise.
- Prefer **Furthermore** over **Moreover** for addition (22 vs 4).
- `Notably / Importantly / Interestingly / Surprisingly` flag the key finding; `Overall / In summary` close a block.

## 6. Syntax & register

- Tense: background/properties = present; what-we-did = past; current meaning/figure description = present.
- Voice: active **we** for narrative and claims; passive for apparatus/method (*"The optical convolutional layer is implemented by integrating…"*).
- Hedge (`may / suggest / likely / potential`) only in meaning sentences; boosters are rationed to the key finding.

## 7. Genre-difference cheatsheet

| Axis | Research | Review | Perspective | Comment |
|---|---|---|---|---|
| Data | own figures/numbers | synthesis of others' citations | argument, no experiments | none |
| Person | `we` + passive | `we` + survey | `we/our` throughout | first-person `I` |
| Stance | assert findings | weigh + outlook | argue + normative `should` | rhetorical, value-driven |
| Close | Discussion + limits | `Conclusions and outlook` + governance call | roadmap / conditions | call to action |

## 8. 中文迁移要点

- 保留信息链:`现象（现在时）→ 然而/目前仍/尚不清楚 → 本文提出 X → 带一个硬核数字的结果 → 意义升华`。
- 标题按体裁切模板:方法文用名词短语、卖点文用陈述句、工具用"系统名:功能"、论辩文可用疑问句;**标题不放数字与结论**。
- gap 必带信号词(然而/不幸的是/仍是挑战/鲜有研究/缺乏);高级写法用数字量化稀缺。
- 贡献句显式给出选题理由("之所以选该体系,是因为…"),呼应"科学问题要科学"。
- 对冲词(可能/提示/很可能)只用于意义句;少用"显著"——对应英文 `significantly` 在本语料 0 次,改用"明显/大幅/相当"(notably/substantially/considerably)。
