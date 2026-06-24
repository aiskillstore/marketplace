# Nature Communications 2025 — Diction & Connector Calibration

Use this file during the sentence-level polish pass when you want **empirical,
quantified word-choice calibration** to back up `style-guardrails.md` and
`published-article-patterns.md`. The preferences below are measured from a 2025
reading set of 20 open-access *Nature Communications* computer-science / AI
articles. They are calibration data, not rules to apply blindly — a discipline
or a specific journal house style overrides them. **Do not copy source wording.**

## 1. Connectors — observed preference order

句首大写连接词词频(5 篇子集合计):
`However` **51** ≫ `Furthermore` 22 · `Therefore` 19 · `Overall`/`Notably` 16 · `In addition` 13 · `In contrast` 6 · `Moreover` 4 · `Importantly` 2.

- **However** carries turns, gap-opening, and surprises — do not scatter weaker
  alternatives where `However` is idiomatic.
- For addition, prefer **Furthermore** over **Moreover** (22 vs 4 here).
- Cause/close with **Therefore**; summarise a block with **Overall / In summary / In conclusion**.
- Reserve **Notably / Importantly / Interestingly / Surprisingly** for the
  paragraph's key finding, not as routine sentence openers.

## 2. Boosters — the `significantly` red line

- **`significantly` appears 0 times in the corpus.** When a draft leans on
  "significantly (better/higher/improved)", first check it is a *statistical*
  claim with a test behind it; otherwise replace with **notably /
  substantially / considerably / markedly**.
- This extends the `style-guardrails.md` overclaim list: treat blanket
  intensifiers as a smell, and attach every booster to a number or a test.

## 3. Hedges — concentrated, not sprinkled

- Primary hedges are **may** and **potential**; `might / could / likely` are
  secondary. They cluster in meaning/Discussion sentences, not in Results
  reporting. Pattern marker: *"Encoding these mechanisms **may** help further
  improve the performance."*
- Keep Results sentences assertive + numeric; move the hedge to the
  interpretation sentence.

## 4. Achievement verbs — the house vocabulary

Frequent, defensible when backed by data: **achieve · demonstrate · outperform
· superior · robust · generalizable · comparable**. When the result is *weaker*
than a baseline, state it honestly and reframe with **comparable** +
concession: *"**Despite the smaller scale** of our pre-training data …, the
**comparable** performance highlights the effectiveness."* Do not upgrade
`comparable` to `superior`.

## 5. Tense & voice (polish-pass checks)

- Background / property = present; specific operation = past; figure
  description = present. Flag accidental past-tense for a standing property
  (*"CataPro demonstrates…"* not *"demonstrated"* when stating a capability).
- Active **we** for narrative and claims; passive for apparatus/method only.
  Flag passive over-use that hides the agent in claim sentences.

## 6. Sentence-skeleton phrases (calibrated to 2025 corpus)

- Abstract hinge: `Here we show/present X (FULL NAME, abbr.), a … that …`
- Gap: `However, … remains a challenge` / `the scarcity of … hinders …` /
  `Without X, Y cannot be quantified`.
- Result close: `These findings collectively affirm/confirm that …`
- Significance (soft promise, not a guarantee): `promises to / offers
  potential / paves the way`.
- Title: no number, no result — keep digits for the abstract.

## 7. 中文润色要点

- 连接词:转折/制造空白优先"然而";递进偏"此外/进一步"(对应 Furthermore);
  因果用"因此";收束用"总体而言/综上"。
- 慎用"显著"——英文 `significantly` 在本语料 0 次。无统计检验支撑时改"明显/大幅/相当/尤为"。
- 对冲(可能/提示/有望)集中在意义句,结果句保持带数字的肯定陈述。
- 战绩措辞(实现/证明/优于/稳健/可泛化/相当)需有数据支撑;弱于对手时用"相当"+"尽管规模更小"客观化,不拔高为"优于"。
