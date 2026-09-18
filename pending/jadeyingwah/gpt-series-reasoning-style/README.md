<div align="center">

# GPT-Series Reasoning Style

**把"Agent 说做完了"变成"Agent 证明做完了"。**  
**Turn "the agent says it's done" into "the agent proves it's done".**


<img src="assets/social-preview.svg" alt="GPT-Series Reasoning Style · 交付纪律层" width="100%">

![Version](https://img.shields.io/badge/version-1.5.6-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Size](https://img.shields.io/badge/SKILL.md-3180%E5%AD%97%E8%8A%82%C2%B733%E8%A1%8C%E9%97%A8%E7%A6%81-orange)
![Experiments](https://img.shields.io/badge/A%2FB%20%E4%B8%8E%E5%AE%9E%E6%B5%8B-300%2B%20%E8%87%82%E6%AC%A1-success)
![Runtime](https://img.shields.io/badge/按需加载-纯文本-blueviolet)
![CI](https://github.com/JadeYingWah/gpt-series-reasoning-style/actions/workflows/ci.yml/badge.svg)


</div>


## 来源与适用范围 / Origin and Scope

**中文**

本 skill 不是凭空设计的规则集，而是从一系列 **GPT 系列大模型**（包括 **GPT-5.6 Sol** 与 **GPT-6 Astra**）在真实交付任务中的长期使用过程里**观察、提炼**出来的。

我们把这些模型在规划与验收环节反复表现出的有益特点——**先想清楚再动手、交付时给出可复现的验证、没验过的地方主动标注**——保留并固化成一份纪律文本。

因此，它**不是**某个模型的专用配件：提炼的是**行为特征**，不是模型能力。任何具备指令遵循能力的大模型都可以加载它。名字里的 "GPT-Series" 记录的是它的**来源**，不是它的**适用范围**。

**English**

This skill is not an invented rule set. It was **observed and distilled** from long-term, hands-on use of a series of **GPT-series models** — including **GPT-5.6 Sol** and **GPT-6 Astra** — on real delivery tasks.

We kept and froze the habits these models showed at their best during planning and acceptance: **think it through before acting, ship reproducible verification, and flag what you could not verify**.

It is therefore **not** a model-specific add-on. What is distilled is **behavioral patterns**, not model capabilities — any instruction-following LLM can load it. "GPT-Series" in the name records its **origin**, not its **scope**.

**通用性 / It is safe to keep on, in any task**

> **它不挑场景。** 执行阶段规则文件根本不加载——挂着它的边际成本在执行期趋近于零：不打断思路、不占上下文、不把流程塞给你。小且可逆的任务自动降级为"直接做、做完扫一眼"，不触发调研和方案确认。在**历史 A/B（233 轮：任务×臂×轮）**与后续实测（experiments 脚本口径 ≥286 臂次/53 批至 09-17 素材，另加 09-17 八组床与 09-18 四场 v1.5.6 单臂包）中，**没有任何一类任务测出"带 skill 比不带更差"**；稳定的正向收益集中在交付可信度（敢不敢直接用、有没有假完成），而不是逼你走流程。
>
> 代码、写作、设计、分析、日常问答——都可以挂着它。它唯一的"代价"是交付前多看一眼；如果你明确要最快出活，说一声"别管验收"即可。

> **It does not pick its battles.** During execution the rule files are not loaded at all — the marginal cost of keeping it on is effectively zero at execution time: no thought interruption, no context tax, no workflow shoved in your face. Small and reversible tasks auto-degrade to "just do it, glance at the end" — no research, no plan approval. Across the **historical A/B line (233 task×arm×round)** plus later beds (script count ≥286 arms / 53 batches through 09-17 materials, plus 09-17 eight desktop beds and 09-18 four v1.5.6 single-arm field packs), **no task category showed the skill making things worse**; the consistent gain is in delivery trustworthiness, not in forcing a pipeline.
>
> Code, writing, design, analysis, everyday Q\&A — keep it on. Its only "cost" is one extra look before you ship; if you want raw speed, just say so.


## 为什么不是"把 GPT 的行为规则全搬过来" / Why Not Copy Every Rule

**中文**

大量 A/B 对照实验反复证明了一件事：**把 GPT 自身的行为特点写成规则、塞进使用者的执行过程，结果适得其反**。你无法靠堆砌规则，让使用者复现 GPT 那样的产出质量。

实测中规则越多并不等于越好：把纪律硬指标化后，评分**并未提升**（与原则引导的差异落在判分误差内，判定为等效）；更极端的 v1.2.5 重版本（179 行、77 条自检）则被实验直接证伪并废弃。执行者记不住繁复步骤、模板填不满，最后流于形式应付。

> **版本注**：上述"规则越多越差"的对比来自 **v1.2.x 旧版本**（v1.2.2 / v1.2.3-draft / v1.2.5）。v1.4.x 极简版起已删除硬指标化与繁复条款，现行 **1.5.6 不再适用该对比**。

所以我们只做两件事：

1. **抽取少数真正可遵守的特性**（真打开看一眼、未验证标注、全绿不算证据等）；
2. 配上**独特的遗忘机制**——执行阶段规则不在上下文，交付时从文件读入。

这让使用者**只享受正面增益**：

- 交付可信度提升（带 skill 的臂在质量/纪律评分上明显更高）；
- "真打开看一眼"能抓到代码审查抓不到的视觉与运行缺陷；
- 反例验证执行率从约三分之一提升到接近全部覆盖；
- 未验项被逐条标注，一眼知道哪些结论能直接信、哪些还要自己再验。

同时**避免负面影响**：

- 不必让纪律全程在场——不挤占注意力、不打断创作思路、不烧上下文；
- 不会因规则堆砌而效果倒退；
- 不会滑向"填模板、走过场"的形式化应付。

**English**

Extensive A/B testing keeps showing one thing: **turning GPT's own behavioral traits into rules and injecting them into the user's execution process backfires.** You cannot make a user reproduce GPT-grade output quality by piling on rules.

In our tests, more rules did not mean better results: turning the discipline into hard metrics brought **no gain** (the gap versus principle-based guidance fell within scoring error and was judged equivalent), and the far heavier v1.2.5 build — 179 lines with 77 self-checks — was directly falsified and retired. Executors could not remember elaborate steps, templates were never fully filled, and compliance became theatre.

> **Version note**: the "more rules, worse results" comparison comes from **older v1.2.x builds** (v1.2.2 / v1.2.3-draft / v1.2.5). Hard metrics and bulky clauses were removed in the v1.4.x minimal line, so the comparison **no longer applies to the current 1.5.6**.

So we do only two things:

1. **Extract a few traits that can actually be followed** (really open it, mark what is unverified, all-green is not evidence, etc.);
2. Pair them with a **distinctive forgetting mechanism** — the discipline steps aside during execution and is reloaded at delivery time.

Users therefore **get the upside only**:

- more trustworthy deliveries (skill-armed runs score markedly higher on quality/discipline);
- "really open it" catches visual and runtime defects that code review misses;
- counter-example verification rises from roughly one-third to near-full coverage;
- unverified items are listed one by one, so you can tell at a glance what to trust and what to re-check.

while **avoiding the downside**:

- no ever-present discipline taxing attention, interrupting thought, or burning context;
- no regression from rule pile-up;
- no slide into checkbox-theatre.


## 首创性设计 / A First of Its Kind

**中文**

据我们所知，这是首个在**单一 Skill 内**、通过**文件级渐进加载**实现「**纪律—心流五阶段时序隔离**」的设计。

五个阶段依次展开：

| # | 阶段                            | 规则状态    | 做什么                            |
| - | ----------------------------- | ------- | ------------------------------ |
| 1 | **无规则约束构想**（阶段1 · 自由构想）       | 规则缺席    | 纯凭判断力想清楚要做什么                   |
| 2 | **渐进式加载规则进行规划**（阶段2 · 规则规划）   | 规则载入    | 把构想落成计划，**完整保留**第一阶段的构想，不被规则覆盖 |
| 3 | **执行**（阶段3 · 执行）              | 规则退场    | 专心干活，规则完全不存在                   |
| 4 | **无规则检查**（阶段4 · 直觉检查）         | 规则缺席    | 凭直觉挑刺，抓规则**没覆盖到**的问题           |
| 5 | **渐进式加载规则进行纪律检查**（阶段5 · 纪律检查） | 规则从文件读入 | 严格逐条过纪律，规则覆盖到的必须都做到            |

结果是两个「**零**」：

- **执行期零干扰**——规则在执行阶段完全不存在，心流不被打断；
- **验收期零妥协**——规则在交付那一刻从文件完整读入，该守的一条不少。

由此带来：**交付可信度显著提升**（带 skill 的臂在质量/纪律评分上明显更高）。

**English**

To our knowledge, this is the first design to achieve **discipline/flow isolation across a five-stage timeline** — inside a **single skill**, via **file-level progressive loading**.

| # | Stage                                                        | Rule state | What happens                                                                                    |
| - | ------------------------------------------------------------ | ---------- | ----------------------------------------------------------------------------------------------- |
| 1 | **Unconstrained ideation** (plan-1)                          | absent     | think it through on judgment alone                                                              |
| 2 | **Progressive rule loading for planning** (plan-2)           | loading    | turn the vision into a plan, **fully preserving** the stage-1 vision rather than overwriting it |
| 3 | **Execution**                                                | withdrawn  | focused work; rules simply do not exist                                                         |
| 4 | **Unruled check** (review-1)                                 | absent     | intuition-driven, catching what the rules **do not** cover                                      |
| 5 | **Progressive rule loading for discipline check** (review-2) | reloaded   | enforce every rule, one by one                                                                  |

The result is two **zeros**:

- **Zero interruption while executing** — the rules are absent during execution, so flow is never broken;
- **Zero compromise at acceptance** — the rules reload in full at delivery, and nothing on the list is skipped.

And with that: **delivery trustworthiness rises markedly** (skill-armed runs score clearly higher on quality/discipline).

---

## 它治的是什么病 / The Actual Problem

AI agent 最贵的失败，从来不是“不会做”，而是**没验过就说做完了**：

- 测试没真跑，宣布“全部通过”；
- HTML 没在浏览器里打开过，宣布“页面没问题”；
- 关键数字没重算，照抄第一遍的结果；
- 交付说明里写着“音效已实现”——产物里连一行音频代码都没有。

在**四轮独立复现、共 14 个实验臂**的对照实验里，AI **无一例外**自报“测试全过、验证有效”——而独立复查（机械判定台）仍判出大量真实缺陷。

2026-09-17 的同题双臂实测（4 个小游戏，两组各自独立完成）再现了这一切：**不带纪律的裸平台**交付后宣布“实测可玩、全链路断言全部通过”——逐文件核验发现其宣称的验证与产物对不上。同一天，带纪律的对照臂交付了**可复现的验证脚本与逐项断言记录**。

所以真正决定价值的不是“它做得多快”，而是——

> **你敢不敢直接用它的产出。**

这个 skill 只干一件事：**把“我觉得行”变成“验过了，证据在这儿”。**

## 它凭什么不一样 / One Divergence

主流 skill 的默认形态是「**加载后全程在场**」；而多智能体框架常把治理规则发给**每一个**参与角色——执行者手里也拿着指挥官的职权条款，角色越位由此发生。

本 skill 把隔离做到**两层物理级**：

1. **执行者与审查者窗口不加载本 skill**——他们的全部行为规范来自身份文件与任务包（自包含），指挥官职权条款（五阶段、形态判断、配置确认）**物理上不在他们的上下文里**；
2. **指挥官自己的 SKILL.md 也只是一道门禁**（3180 字节 / 33 行）——纪律全文（DISCIPLINE.md，3185 字节 / 33 行）在**动手做事的前一刻**才被放行。



常驻上下文里**只有一句门禁**——你看不到 skill 常见的那些负作用，只收下它的益处。

> **为什么这样设计**：多数 skill 一旦加载便全程在场——规则持续占用注意力、打断思路、消耗上下文。本 skill 把自己拆成**规划**与**验收**两端，中间漫长的执行阶段让纪律退场；只在自判“我做完了”的那一刻重新加载审查规则。所以你可以**只收下它的益处，不必承受纪律常驻的代价**。
>
> **Why it's built this way**: most skills stay present once loaded. This skill splits into **planning** and **acceptance**, and goes further: even the commander's own SKILL.md is a pure gate — the discipline file is released the moment before action. You get the benefits **without paying the costs** of an ever-present discipline.

## 它怎么工作 / How It Works

装上后**无需任何特殊指令**。当 agent 接到交付型任务（写代码、算数据、做页面、多 Agent 分工），SKILL.md 的纯门禁会在**动手前一刻**放行纪律全文，然后进入**五阶段时序**：

```text
┌─ 门禁（SKILL.md · 33 行纯门禁）——「前一刻」= 写交付物/施工确认/产线命令/宣布交付 中最早者
│         创意类可有一轮不读 DISCIPLINE 的方向构想；陌生专名仍先问/搜
│
┌─ 阶段1 · 自由构想（不读 plan/review/multi-agent，不建治理目录）——凭你自己想清楚要做什么
│      退出：构想要点已列出，即将进入规划或实现之前
┌─ 阶段2 · 规则规划（读 references/plan-rules.md）——按规则落成计划，逐条回应构想清单
│      退出：方案已确认（结构化选项卡片）＋ 风险已分级 ＋ 形态已裁定
│             ＋ 创意类质量预算已写明（A档不锁质量上限）＋ 没有要再问的问题
┌─ 阶段3 · 执行（规则完全不存在）——凭你的能力干活，心流不被打断
│      退出：无未调试问题；创意/视觉类另有「可打开完整路径」
┌─ 阶段4 · 直觉检查（无规则）——凭常识快速扫一遍交付物
│      退出：没有再发现新的疑点（疑点当场确认或修掉，不带进阶段5）
└─ 阶段5 · 纪律检查（读 references/review-rules.md）——1–8条 + 第9条完成档位
       退出：规则过完（轻任务★3条+第9条 / 重任务全量+第9条）＋ 三件套
             ＋ 完成档位 C1/C2 标明 ＋ 无未处理的“这里好像有问题”
```

**完成档位（1.5.6）**：阶段5通过 = **C1 可验收**（须写清产品档是否拉满）；「产品做好了」= **C2**，只能来自你确认或外部 scorecard，禁止 Agent 自封。执行面无规则——纪律只在门禁时点、阶段2、阶段5出现。

**任务交付之后**：彻底忘记 `plan-rules.md` / `review-rules.md` / `multi-agent.md` 的具体内容——只记“有五个阶段、到哪个阶段读哪个文件”。规则长什么样，下次需要时再读。

规则文件只在阶段 2 与阶段 5 被读进来，**执行期它们根本不在上下文里**；纪律全文（DISCIPLINE.md）也只在动手前一刻才被放行。

设计意图就两句话：

- **创作时没有纪律**——阶段 1 与整个执行阶段，规则不污染思路；
- **检查有两道**——直觉抓规则**没覆盖到**的问题，纪律确保规则**覆盖到**的都做到，互不替代。

---

## 交付长什么样 / What Delivery Looks Like

同一种任务，装上前后的两副面孔：

**没有纪律层：**

> 做完了。功能都实现了，测试也全过了。

**有纪律层：**

> **做了什么**：重写导出功能，新增 3 个边界用例。  
> **怎么验的**：浏览器实测渲染（截图见附件）；`pytest tests/test_export.py -q` → 12 passed。  
> **哪些没验**：① Safari 兼容性——本机无 Safari，建议你打开自验；② 10 万行以上大数据量性能——没有现成数据集。

差别不在格式好看——是你**一眼就知道哪些话能信、哪些还得自己再验**。

## 怎么知道它生效了 / How To Know It's Working

- 交付消息开始自带三件套：做了什么 / 怎么验的（可复现命令）/ 哪些没验；
- 没验过的地方**主动认**，而不是含糊带过；
- 环境不支持真打开时，给你自验步骤，而不是装作验过；
- 连续失败两次后换路径，而不是硬刚；
- 轻任务上它几乎隐身——**这是设计，不是失灵**。

---


## 八条纪律 / The Rules

阶段 5（纪律检查）严格过这 **8 条**（★ = 轻任务也必须做的 3 条）：

| #  | 纪律         | 要点                                                                        |
| -- | ---------- | ------------------------------------------------------------------------- |
| 1★ | **真打开看一眼** | 产物在真实环境打开、真用一遍——HTML 要浏览器渲染、API 要前端调，跑脚本不算。其他类型：游戏走一轮核心玩法、报告逐数字对源、SVG 真渲染放大看。环境不支持时：如实标"未验证：浏览器渲染"+ 给用户自验步骤 |
| 2★ | **未验证标注**  | 交付只说三件：做了什么 / 怎么验的（可复现命令）/ 哪些没验。没验的逐条列原因，不许只写"部分未验证"；未验项必须用星号或加粗**醒目标出**，不许藏在段落中间                     |
| 3  | **交付声明对得上** | 你说"做了 X"，产物里真的有 X 吗？交付前最后一次回读自己的交付声明，逐项在产物里找位置；指不到的，要么补做，要么改成"未完成 + 原因"   |
| 4  | **失败两次换路** | 同一动作连续失败第 2 次，禁止同法第 3 次；先判断是否与已验路径等价，别死磕                                  |
| 5  | **全绿不算证据** | 把要防的错误故意做一次，断言红才算验过；变异后照样全绿 = 变异没生效。最小菜谱：空值/超长/非法类型/缺键。**非代码产物**：链接逐个点、数字对源、效果真渲染并列查证记录 |
| 6  | **关键数字重算** | 数据/研究类交付的关键数字，独立方法重算或双源交叉；对不上以重算为准                                        |
| 7  | **临时物隔离**  | 临时文件不进交付目录、收尾清掉；清理只动本任务自己的目录，禁全局杀进程                                       |
| 8★ | **防死循环**   | 同一文件连读 3 次无新信息就停；同一动作连续 3 次输出相同就换思路                                       |

---

## 多智能体协作 / Multi-Agent

细则在 `references/multi-agent.md`（命中才读），角色卡模板在 `templates/`。

### 形态二 · 子智能体（有明显增益就自觉开，不等用户说）

**命中任一就开**：完全独立的子活 / 要并行跑两件事 / 要独立挑刺视角 / 中间过程怕污染主上下文。  
派发给清三样：**目标、完成标准、交回给谁**。铁律：子智能体交回后**主 Agent 仍是 DRI**，必须自己验收；子智能体不直接对用户；一个人能连贯干完的事不开二。

### 形态三 · 多智能体（命中后先与用户确认 / 跨模型 / 大任务分工）

六步：指挥官身份声明 → 建立角色档案 → 拆子任务写任务包 → 用户转述派发 → 对照原始目标验收（先查跑偏，再交审查者挑刺）→ 向用户汇报三件套。

**任务包七要素**：背景 / 已定决策 / 未定缺口 / 完成标准 / 允许与禁止范围 / 唯一 DRI / 交回给谁。

**三个角色卡**（`templates/`）：**指挥官**默认 DRI，委派不转移最终责任；**执行者**只说"按标准做完了，请验收"；**审查者**独立挑刺、不亲自改活。

**红线**：执行者说「我做完了」不算验收；审查者不亲自改；不绕开指挥官直接汇报。

---



## 实测与证据 / Field Tests

**最新实测（2026-09-18 · v1.5.6）——交付型 + 创意型单臂（无 B 臂，只记行为与完成档位）：**

| 实验 | 条件 | 结果 |
|---|---|---|
| **鸣潮伤害验算表**（数字/交付） | skill v1.5.6 · 引擎 `damage_calc.py` 1:1 | 页内 21/21 + Python 15 项交叉 + 变异 `792→793` 红；**完成档位 C1**（实机对账待用户） |
| **星光接取**（创意小游戏） | v1.5.6 · A 档方向卡 · 质量预算 ≤2 轮 | 逻辑 24/24（含变异）+ Chrome/点击开局；**C1**，产品档未拉满 |
| **3D 钓鱼 / Neon Void**（创意游戏） | v1.5.5–1.5.6 讨论前后 | 口供与 artifacts 显示 C1 式标注 + 自动化证据；**C2 须用户试玩**；完整钓鱼源码未入仓（口供级） |

> **1.5.6 口径**：阶段5通过 = **C1 可验收**；「产品做好了」= **C2**（用户或外部 scorecard）。执行面无规则；创意段可不挂 skill，验收再挂。证据在 [`experiments` 分支](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments) `raw-materials/*2026-09-18/`。

**对照实验（2026-09-17）——双臂，磁盘证据 + 回访口供：**

| 实验 | 有skill | 无skill | 有skill和无skill谁更好 |
|---|---|---|---|
| **v1.5.1 · 菲比秋比复测**（陌生专名 + 从零新建 2D 游戏） | 两轮搜索查到「菲比啾比」出处 → 三问确认 → 主角进产物 | 核心词被**静默丢弃**，通用钓鱼游戏 | **有 skill 明显更好** |
| **v1.5.2 · 问答双臂** | 搜索核实 + 读 VERSION + 标来源 | 同样双问全对 | **平手**→撤销问答强制调研 |
| **v1.5.1 · 三游戏合集** | A 档确认 → **exe 直启 3/3 可玩** + 未验项自动化闭环 | bat 依赖环境 **2/3 打不开**，零标注 | **有 skill 全面更好** |

> **一句话**：条款只为实测缺口而设；**C1/C2 把「没假完成」和「产品做好了」拆开**。

<details>
<summary><b>历史实验档案</b>（口径与旧数字，点开备查）</summary>

- 历史累计口径（勿混用）：
  - **叙事 A/B 轮次 233**（= 重版本线 207 + 极简线 26；一次「任务 × 臂 × 轮」计一次）；
  - **experiments 分支脚本口径**：≥ **286 臂次 / 53 批**（正则覆盖臂目录，下限值；素材约 3250 文件，含 v1.2.x 与 09-17 前素材）；
  - **2026-09-17**：8 组桌面对照/形态床（菲比/三游戏×2/4399×2/番茄钟/财务套件/三txt）；
  - **2026-09-18**：4 场 v1.5.6 实测包（鸣潮验算表、星光接取、3D 钓鱼口供、Neon Void 证据层）。
- 结论沉淀：规则越少越好，但核心那几条不能少；**C1/C2 把诚信完成与产品满意拆开**。
- Harness 本机另有 ab-* 目录若干，**未全部入 experiments 分支**，不计入上述公开数字。
- 可引用硬数字（v1.2.x 时代对照实验）：软维度提升 **+20~24**（P1-5）；反例验证执行率 **带 skill 100% vs 无 skill 33%**（P1-1）；自我校准缺口 **100% → 33%**（P1-2）。
- 实验原始数据（约 70 MB / 3066+ 文件）在 [`experiments` 分支](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments)；主仓库只含 skill 本体。

</details>

---

## 诚实边界 / What It Is Not

这一节写的是**我们自己测出来的局限**——不是谦虚，是口径。

> **版本适用性**：标注「**旧版**」的条目测于 **v1.2.x 时代**。v1.4.x 极简版起已删除硬指标化与繁复条款，**这些旧版结论在现行 1.5.6 上不再适用**。

- **不提升推理能力**，也不是 GPT 专用——从 GPT 系列（含 GPT-5.6 Sol、GPT-6 Astra）提炼而来，但适用于所有具备指令遵循能力的大模型。
- **不提升代码质量**——实验一致显示：代码本体差别不大，变好的是**交付可信度**。
- **不是加速器**——验证习惯会占去约三到四成的时间预算，换来的是“敢直接用”的交付。
- **不是流程绑架**——执行阶段规则文件根本不加载，创作不被打断；问答场景双臂实测零打扰。轻任务几乎无感。
- **裸平台的模型能力已经很强**——信息型问答双臂满分无差异；三游戏裸平台也能做出来（虽然丢了主题、两个打不开）。skill 的价值不是让模型变强，是把质量从碰运气变成有保证：任务核心词不被丢掉（菲比秋比对照）、交付形态先问你（exe 双击直启）、未验证项如实标注并自我闭环。

<details>
<summary><b>历史实验边界档案</b>（v1.2.x 时代，现行不适用，点开备查）</summary>

不兜底〔旧版 v1.2.2 / v1.2.5〕——n=2 对照：致命缺陷率维度带 skill 与不带没有拉开可辨差距，held-out 略差。反向结果也放进仓库。防线靠证据与独立复验，不靠条款。

加条款不等于更好〔旧版 v1.2.2 / v1.2.3-draft〕——硬指标化后评分未提升（58.17 vs 57.00，等效）；更重的 v1.2.5（179 行/77 条自检）被证伪废弃。

</details>

---

## 设计哲学 / Philosophy



- **规则越少越好，但核心那几条不能少**——历史 A/B（233 轮）+ 后续实测的最终结论；
- **创作是创作，检查是检查**——忘/想交替的全部理由；
- **证据高于声称**——全绿不算证据，断言红过才算验过；
- **责任不随委派转移**——子智能体交回后，主 Agent 仍是 DRI。

---

## 安装 / Install

两种装法，对应两类加载方式（用多个客户端就各装各的，互不冲突）：

- **方式一·原生 Skill（推荐）**：把文件夹放进客户端的 skills 目录，启动时按 `SKILL.md` 的 description **自动发现、按上下文触发**。
- **方式二·AGENTS.md 项目指令**：不支持 skill 自动发现、但会读项目根 `AGENTS.md` 的客户端，`cd` 进仓库即可，由 AGENTS.md 指路加载。

### 方式一：原生 Skill（自动发现）

各客户端的 skills 目录（`<name>` = `gpt-series-reasoning-style`）：

| 客户端 | 个人级（全局，所有项目） | 项目级（随仓库共享给团队） |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor（2.4+） | `~/.cursor/skills/` | `.cursor/skills/` |
| Codex CLI | `~/.codex/skills/` | `.codex/skills/`（或 `.agents/skills/`） |
| WorkBuddy | `~/.workbuddy/skills/` | — |
| 其他支持 SKILL.md 的客户端 | 对号入座查其文档的 skills 目录 | 同左 |

> **一个位置喂两个客户端**：Cursor 会兼容加载 `.claude/skills/` 与 `~/.claude/skills/`（Codex 目录同理）。同时用 Claude Code 和 Cursor 时，装进 `~/.claude/skills/` 即可两边生效。

**macOS / Linux（bash）**——以 Claude Code 个人级为例：

```bash
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
mkdir -p ~/.claude/skills && cp -r gpt-series-reasoning-style ~/.claude/skills/
# Cursor 改目标为 ~/.cursor/skills/ ；Codex 改 ~/.codex/skills/ ；WorkBuddy 改 ~/.workbuddy/skills/
```

**Windows（PowerShell）**：

```powershell
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force gpt-series-reasoning-style "$HOME\.claude\skills\"
# Cursor 目标 "$HOME\.cursor\skills"；Codex "$HOME\.codex\skills"；WorkBuddy "$HOME\.workbuddy\skills"
```

**项目级 / 团队共享**：把文件夹放进项目仓库的 `.claude/skills/`（或对应客户端目录）并提交——队友 clone 仓库即自动获得，无需各自安装。

装完**新开一个会话**（或重启客户端）让其发现新 skill。

### 方式二：AGENTS.md 项目指令（cd 型）

适用于不做 skill 自动发现、但会读项目根 `AGENTS.md` 的客户端（Codex / Gemini CLI / Copilot CLI / Windsurf / Zed 等）：

```bash
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
cd gpt-series-reasoning-style    # 在仓库目录内启动 agent，AGENTS.md 入口指路自动生效
```

这不是 skill 注册，而是 agent 把 `AGENTS.md` 当项目指令、按其指路走 `SKILL.md`（门禁）→ `DISCIPLINE.md`（五阶段）→ 按需读 references。若你的客户端只读特定文件名，可在仓库根加一个软链指向 `AGENTS.md`（如 `ln -s AGENTS.md CLAUDE.md`、`ln -s AGENTS.md GEMINI.md`；Windows 用 `mklink` 或直接复制一份）。

### 安装注意

- **拷整个文件夹，不要只拷 `SKILL.md`**——`DISCIPLINE.md`、`references/`、`templates/`、`scripts/` 都是按需加载的，缺了多智能体等场景会失效。
- **目录名必须是 `gpt-series-reasoning-style`**：下载 ZIP 解压后常带 `-main` / `-master` 后缀，需改名，否则部分客户端的发现与斜杠调用会异常。
- **零依赖、不联网、不上报**：本体全是 Markdown 纯文本；仅 `scripts/selfcheck.py` 仓库自检需要 Python 3（可选，不装 Python 不影响 skill 工作）。

### 更新与验证

```bash
cd <skills 目录>/gpt-series-reasoning-style && git pull    # 版本号见 VERSION 文件
python scripts/selfcheck.py    # 可选：38 项静态自检，退出码 0=全过
```

验证装好了：新开会话问 agent「**你的版本号是多少？加载证明需要哪几个文件？五阶段是什么？**」——应答 `1.5.6`，说得出门禁链路（`SKILL.md` 门禁 → **前一刻**读 `DISCIPLINE.md`；前一刻=写交付物/施工确认/产线命令/宣布交付中最早者）与五阶段时序，并能逐字引用纪律第 1 条；提及完成档位 **C1 可验收 / C2 产品满意**（C2 须用户或外部认定）。

## 触发方式 / Usage

- **自动触发**（由 `SKILL.md` 的 description 决定）：涉及数字验算、代码交付、多 Agent 协作、需要防假完成的任务；或用户说"做完了帮我查 / 看看对不对 / 验收"；或派发子任务、多个 AI 分工。约束交付是否真实，**不单独设定创意质量满意标准**（见 DISCIPLINE 完成档位）。
- **显式点名**：`使用 gpt-series-reasoning-style 执行本次任务。`
- **不加载**：一句话问答、纯聊天、小且可逆的改动——纪律不该出现在不需要它的地方。
- **创意任务用法**：要抬产品上限时，**创意/实现段可不挂本 skill**，收工后再挂验收（真打开 + C1/C2）；门禁与打磨预算不在创意场里，才谈得上零压榨。

## 成本 / Cost

| 项目         | 实测值                                                          |
| ---------- | ------------------------------------------------------------ |
| `SKILL.md` | **3180 字节 / 33 行**（常驻约 0.6k token）——**纯门禁**，纪律全文在 `DISCIPLINE.md`（3185 字节/33 行，动手前一刻才读） |
| 阶段 2 按需   | `references/plan-rules.md`（5442 字节）——仅在规则规划阶段读入        |
| 阶段 5 按需   | `references/review-rules.md`（5041 字节）——仅在纪律检查阶段读入      |
| 多智能体按需  | `references/multi-agent.md`（5718 字节）——仅叠加形态二三时读入       |
| 加载路径      | 平时只读 `SKILL.md`（33 行门禁）+ `VERSION`；**动手/回答前一刻**读 `DISCIPLINE.md`（纪律全文）；阶段 2 读 plan-rules、阶段 5 读 review-rules、多智能体场景另读 `multi-agent.md`；**任务结束后规则内容全部遗忘** |
| 峰值常驻文本   | 任一时刻上下文里的规则文本不超过一份（规划或审查，二者不同时在场）              |

**对比 v1.2.5 重版本**：38.7 KB / 179 行 / ~12k token —— 已由实验证明是更差的选择（见「实测与证据」）。


## 仓库结构 / What's Inside

| 文件                               | 角色                                                     |
| -------------------------------- | ------------------------------------------------------ |
| `SKILL.md`                       | **门禁**（33 行）。不含纪律正文；「前一刻」动作化 + 创意构想例外            |
| `DISCIPLINE.md`                  | **纪律全文**（31 行）。五阶段 + **完成档位 C1/C2** + 任务后遗忘 + 边界 + 加载规则 |
| `references/plan-rules.md`       | **阶段 2 专用**：规划规则（构想实质保留、形态裁定、A档不锁质量上限、创意质量预算） |
| `references/review-rules.md`     | **阶段 5 专用**：8 条纪律（★三条轻任务必做）+ **第9条完成档位** + 退出条件    |
| `references/multi-agent.md`      | 形态二三细则：命中信号、派发规范、六步操作、红线                             |
| `AGENTS.md`                      | 跨运行时入口路由（Codex / Gemini CLI 等），仅指路，无规则               |
| `templates/`                     | 指挥官 / 执行者 / 审查者三张角色卡 + 任务包七要素                        |
| `scripts/selfcheck.py`           | 仓库一致性自检（**38 项**，纯只读，已适配文件级渐进加载结构）                  |
| `SECURITY.md`                    | 安全模型说明                                                 |
| `assets/social-preview.svg / .png`      | 仓库横幅图（1280×640）                                       |

## 版本 / Versioning

当前版本：**1.5.6**

- **v1.5.6**：门禁「前一刻」动作化；阶段1禁读规则文件；A档不锁质量上限 + 创意打磨预算；完成档位 C1/C2（阶段5过完≠产品做好了）；
- **v1.5.5**：SKILL.md 门禁化，纪律全文移入 DISCIPLINE.md（物理隔离）；
- **v1.4.x 极简线**：五阶段时序、文件级渐进加载——主线前身；
- **v1.2.x 重版线**：179 行、模块矩阵、self-test 冻结 77 条——**已被实验证伪**，该线已废弃。

**用法原则（1.5.6）**：执行面无规则；创意段若要零压榨，验收前可不挂本 skill；大版本（≥1.6）须总指挥主动提起。

## License / 许可证

MIT
