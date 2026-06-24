# Article Anatomy — a reading aid (Nat Commun 2025 CS/AI corpus)

Use this file as a **reading aid** while building the bilingual reader, to label
the *argumentative function* of each block so the reader can locate the gap, the
contribution, the decisive result, and the self-contained figure legends. It is
distilled from a 2025 set of 20 open-access *Nature Communications* computer
science / AI papers across genres.

> This is an aid for **locating structure**, not a license to summarise. The
> `core/principles.md` contract still holds: translate every block for meaning,
> keep the bilingual side-by-side, and never degrade to a summary-only output.
> Use the function labels to help a reader navigate, e.g. in a short orientation
> note, not to replace the full translation.

## Where each function lives

- **Abstract = a funnel.** Read it as five moves: field value → gap (almost
  always after **However**) → hinge `Here we show/present X` → one quantified
  result → significance. The hinge sentence is the fastest way to state what the
  paper actually contributes.
- **Introduction = hook → gap → contribution.** Gap signal words to spot:
  **However / remains / Unfortunately / underexplored / the scarcity of … /
  Without X, Y cannot be …**. The contribution is the explicit `Here we… / In
  this work, we…` sentence, often with a `(Fig. 1)` pointer.
- **Results = conclusion-first.** Each paragraph opens with the judgement; the
  figure call (`Fig. Xa`, or `Figure X shows…`) and the numbers follow.
  Subheadings are often conclusions or method names, so the subheading list
  alone sketches the evidence ladder.
- **Figure/Table legends are self-contained.** `Fig. N | bold noun title`, then
  `a/b/c` panels, with `n=`, error type, and test written in. A legend's last
  sentence sometimes advances a claim (*"…indicating that the models are not
  predicting poses based on physics…"*) — flag it; it is interpretation, not
  description.
- **Discussion = restate contribution → why credible → wider meaning → limits
  (`Another limitation…` / `remains to be tested`) → future work.** The limits
  sentence is where the paper bounds its own claim.

## Genre tells (so the reader frames the paper correctly)

- **Research article**: own data, IMRaD, `we` + passive.
- **Review**: chapters by topic/modality synthesising others' citations, little
  own data, closes with `Conclusions and outlook`.
- **Perspective**: history/era hook, numbered argument, normative `X should…`,
  roadmap close.
- **Comment**: first-person `I`, rhetorical-question opening, analogy/history,
  no IMRaD, no figures.
- **Benchmark/framework**: the gap is "the field lacks an agreed standard";
  tables dominate; stresses community / reproducibility / versioning.

## 中文阅读提示

- 给读者的导航可标注每段功能(背景/空白/贡献/结果/局限),帮助快速抓论证骨架;
  但**不得**因此省略逐段对照翻译或退化为摘要。
- "然而 / 仍是挑战 / 鲜有研究 / 缺乏 / 没有 X 就无法 Y"是空白信号词;`Here we / 本文`
  之后是作者自述贡献。
- 图注通常自足(含 n、误差、检验);若图注末句给出推断结论,标注为"解读"而非"描述"。
- 先判定体裁(研究论文/综述/观点/评论/基准),再据此理解其组织方式与语气。
