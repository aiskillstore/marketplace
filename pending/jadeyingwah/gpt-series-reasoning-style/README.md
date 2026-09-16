<div align="center">

# GPT-Series Reasoning Style

**把"Agent 说做完了"变成"Agent 证明做完了"。**  
**Turn "the agent says it's done" into "the agent proves it's done".**

![GPT-Series Reasoning Style — 交付验收纪律层](social-preview.svg)

[![Version](https://img.shields.io/badge/version-1.5.0-blue)](#版本--versioning)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](#license--许可证)
[![Size](https://img.shields.io/badge/SKILL.md-1.8KB·23行-orange)](#成本--cost)
[![Experiments](https://img.shields.io/badge/A%2FB_实验-233_次-success)](#实测与证据--field-tests)
[![Runtime](https://img.shields.io/badge/按需加载-18_files-blueviolet)](#成本--cost)

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


## 为什么不是"把 GPT 的行为规则全搬过来" / Why Not Copy Every Rule

**中文**

大量 A/B 对照实验反复证明了一件事：**把 GPT 自身的行为特点写成规则、塞进使用者的执行过程，结果适得其反**。你无法靠堆砌规则，让使用者复现 GPT 那样的产出质量。

实测中规则越多并不等于越好：把纪律硬指标化后，评分**并未提升**（与原则引导的差异落在判分误差内，判定为等效）；更极端的 v1.2.5 重版本（179 行、77 条自检）则被实验直接证伪并废弃。执行者记不住繁复步骤、模板填不满，最后流于形式应付。

> **版本注**：上述"规则越多越差"的对比来自 **v1.2.x 旧版本**（v1.2.2 / v1.2.3-draft / v1.2.5）。v1.4.x 极简版起已删除硬指标化与繁复条款，现行 **1.5.0 不再适用该对比**。

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

> **Version note**: the "more rules, worse results" comparison comes from **older v1.2.x builds** (v1.2.2 / v1.2.3-draft / v1.2.5). Hard metrics and bulky clauses were removed in the v1.4.x minimal line, so the comparison **no longer applies to the current 1.5.0**.

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

| # | 阶段 | 规则状态 | 做什么 |
|---|---|---|---|
| 1 | **无规则约束构想**（阶段1 · 自由构想） | 规则缺席 | 纯凭判断力想清楚要做什么 |
| 2 | **渐进式加载规则进行规划**（阶段2 · 规则规划） | 规则载入 | 把构想落成计划，**完整保留**第一阶段的构想，不被规则覆盖 |
| 3 | **执行**（阶段3 · 执行） | 规则退场 | 专心干活，规则完全不存在 |
| 4 | **无规则检查**（阶段4 · 直觉检查） | 规则缺席 | 凭直觉挑刺，抓规则**没覆盖到**的问题 |
| 5 | **渐进式加载规则进行纪律检查**（阶段5 · 纪律检查） | 规则从文件读入 | 严格逐条过纪律，规则覆盖到的必须都做到 |

结果是两个「**零**」：

- **执行期零干扰**——规则在执行阶段完全不存在，心流不被打断；
- **验收期零妥协**——规则在交付那一刻从文件完整读入，该守的一条不少。

由此带来：**交付可信度显著提升**（带 skill 的臂在质量/纪律评分上明显更高）。

**English**

To our knowledge, this is the first design to achieve **discipline/flow isolation across a five-stage timeline** — inside a **single skill**, via **file-level progressive loading**.

| # | Stage | Rule state | What happens |
|---|---|---|---|
| 1 | **Unconstrained ideation** (plan-1) | absent | think it through on judgment alone |
| 2 | **Progressive rule loading for planning** (plan-2) | loading | turn the vision into a plan, **fully preserving** the stage-1 vision rather than overwriting it |
| 3 | **Execution** | withdrawn | focused work; rules simply do not exist |
| 4 | **Unruled check** (review-1) | absent | intuition-driven, catching what the rules **do not** cover |
| 5 | **Progressive rule loading for discipline check** (review-2) | reloaded | enforce every rule, one by one |

The result is two **zeros**:

- **Zero interruption while executing** — the rules are absent during execution, so flow is never broken;
- **Zero compromise at acceptance** — the rules reload in full at delivery, and nothing on the list is skipped.

And with that: **delivery trustworthiness rises markedly** (skill-armed runs score clearly higher on quality/discipline).

---

## 它治的是什么病 / The Actual Problem

AI agent 最贵的失败，从来不是"不会做"，而是**没验过就说做完了**：

- 测试没真跑，宣布"全部通过"；
- HTML 没在浏览器里打开过，宣布"页面没问题"；
- 关键数字没重算，照抄第一遍的结果。

在**四轮独立复现、共 14 个实验臂**的对照实验里，AI **无一例外**自报"测试全过、验证有效"——而独立复查（机械判定台）仍然判出大量真实缺陷。

所以真正决定价值的不是"它做得多快"，而是——

> **你敢不敢直接用它的产出。**

这个 skill 只干一件事：**把"我觉得行"变成"验过了，证据在这儿"。**

## 它凭什么不一样 / One Divergence

主流 skill 的默认形态是「**加载后全程在场**」：规则一直压着，挤占注意力、打断思路、烧上下文。事后审查则通常另起一个独立 agent，或在同一上下文里再跑一遍 checklist。

本 skill 的差异只有一个动作：**在同一段上下文内，执行阶段让模型显式脱离纪律、进入心流，只在它自判完成的那一刻，重新加载审查规则。**

```text
忘  →  想  →  忘  →  忘  →  想
```

**你看不到 skill 常见的那些负作用，只收下它的益处。**

> **为什么这样设计**：多数 skill 一旦加载便全程在场——规则持续占用注意力、打断思路、消耗上下文。本 skill 把自己拆成**规划**与**验收**两端，中间漫长的执行阶段让纪律退场；只在自判"我做完了"的那一刻重新加载审查规则。所以你可以**只收下它的益处，不必承受纪律常驻的代价**。
>
> **Why it's built this way**: most skills stay present once loaded — taxing attention, interrupting thought, burning context. This skill splits into **planning** and **acceptance**, letting the discipline step aside during the long execution phase, and reloading it only when the model declares "I'm done." You get the benefits **without paying the costs** of an ever-present discipline.

---


## 它怎么工作 / How It Works

装上后**无需任何特殊指令**。当 agent 接到交付型任务（写代码、算数据、做页面、多 Agent 分工），它会自动进入**五阶段时序**——核心是"规则在需要时才被加载，不需要时根本不存在"：

```text
┌─ 阶段1 · 自由构想（无规则）——凭你自己想清楚要做什么
│      退出：能一句话说清楚接下来做什么
┌─ 阶段2 · 规则规划（去读 references/plan-rules.md）——按规则落成计划，完整保留阶段1的构想
│      退出：方案用户已确认（A档同意 / B档问完）＋ 风险已分级（轻/重）＋ 没有要再问用户的问题
┌─ 阶段3 · 执行（规则完全不存在）——凭你的能力干活，心流不被打断
│      退出：觉得可以了，没有正在调试的问题
┌─ 阶段4 · 直觉检查（无规则）——凭常识快速扫一遍交付物
│      退出：没有"等等，这里好像有问题"的卡住感
└─ 阶段5 · 纪律检查（去读 references/review-rules.md）——严格过 8 条纪律
       退出：规则全部过一遍（轻任务3条 / 重任务8条）＋ 能说出三件套 ＋ 没有未处理的"这里好像有问题"
```

**任务交付之后**：彻底忘记 `plan-rules.md` / `review-rules.md` / `multi-agent.md` 的具体内容——只记"有五个阶段、到哪个阶段读哪个文件"。规则长什么样，下次需要时再读。

规则文件只在阶段 2 与阶段 5 被读进来，**执行期它们根本不在上下文里**。

设计意图就两句话：

- **创作时没有纪律**——阶段 1 与整个执行阶段，规则不污染思路；
- **检查有两道**——直觉抓规则**没覆盖到**的问题，纪律确保规则**覆盖到**的都做到，互不替代。

### 阶段 3 / 阶段 4：两头吃，零副作用

**阶段 3 · 执行**——既不丢失使用者原本的**创作能力**，又已获得 skill 给予的**规划能力**：阶段 2 的规划成果（方案、风险分级、验收标准）全部在手，规则文本却完全退场。两头吃，且没有任何"纪律常驻"的副作用。

**阶段 4 · 直觉检查**——**不加载纪律检查规则**，使用者自己的找问题能力不被任何清单框住、不被替代；同时 skill 在前一阶段注入的**审查能力**（真验证、交付声明对得上的意识）仍在发挥作用。直觉的广度 + 纪律的敏感度，同时在线、互不挤占。

**English**

- **Stage 3 · Execution** — the user's original **creative ability** stays fully intact while the **planning capability** the skill granted is already in hand: the plan, the risk tier and the acceptance criteria are all there, with the rule text completely out of the way. Both worlds, zero side effects.
- **Stage 4 · Intuition check** — the discipline rules are **not loaded**, so the user's own problem-finding instinct is neither boxed in nor replaced; meanwhile the **review capability** the skill instilled in the earlier stage (really verify, delivery claims must match) still works. The breadth of intuition and the sensitivity of discipline, online at the same time.

<details>

<summary><b>轻任务与重任务怎么自动分级？（规划时自过的七件事）</b></summary>

1. **形态判断自己心里做**——不输出决策过程，不跟用户汇报"我选择了什么形态"，直接干活。
2. **协作形态可叠加**——同一任务可以自己干一部分（形态一）、派子 Agent 干一部分（形态二）、协调外部模型干一部分（形态三）；默认形态一起步，哪里需要并行/独立/跨模型就叠加哪里。
3. **轻量档**——只做分工方案、不实际派发时，不建 `_agents/` 目录、不写任务包文件；方案获批准后再展开。
4. **小且可逆 = 指令即授权**——直接做、别请示；只有不可逆、对外发布、删东西才事前确认。
5. **按风险分级**——轻任务只做 3 条纪律（真打开看一眼 / 未验证标注 / 防死循环）；数据/代码/多 Agent 类重任务做全 8 条。
6. **动手前先调研**——重任务先花几分钟查网上怎么做、有什么坑、有没有最佳实践，不凭感觉瞎写。
7. **最后确认档位**——跟用户确认沟通方式：**A 档**一次性确认（推荐方案列出，同意就开干）或 **B 档**逐项问答（一次一个最高影响问题）；用户没说默认 A 档。

</details>

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
| 1★ | **真打开看一眼** | 产物在真实环境打开、真用一遍——HTML 要浏览器渲染、API 要前端调，跑脚本不算。环境不支持时：如实标"未验证：浏览器渲染"+ 给用户自验步骤 |
| 2★ | **未验证标注**  | 交付只说三件：做了什么 / 怎么验的（可复现命令）/ 哪些没验。没验的逐条列原因，不许只写"部分未验证"；未验项必须用星号或加粗**醒目标出**，不许藏在段落中间                     |
| 3  | **交付声明对得上** | 你说"做了 X"，产物里真的有 X 吗？交付前最后一次回读自己的交付声明，逐项在产物里找位置；指不到的，要么补做，要么改成"未完成 + 原因"   |
| 4  | **失败两次换路** | 同一动作连续失败第 2 次，禁止同法第 3 次；先判断是否与已验路径等价，别死磕                                  |
| 5  | **全绿不算证据** | 把要防的错误故意做一次，断言红才算验过；变异后照样全绿 = 变异没生效。最小菜谱：每个写入口至少打 空值/超长/非法类型/缺键           |
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

这个 skill 的每一次删减与保留，都是 A/B 实验投出来的票。**累计 233 次**（= 重版本线 207 次 + 极简线 26 次；口径：一次「任务 × 臂 × 轮」计一次）：

| 阶段          | 版本形态             | 实验次数      | 结论           |
| ----------- | ---------------- | --------- | ------------ |
| v1.2.x 重版本线 | 3043 个文件 / 179 行 | **207 次** | **规则越多效果越差** |
| v1.4.x 极简线  | 6 个文件 / 59 行     | **26 次**  | 核心条款被反复验证有效  |

**233 次实验最终证明的四件事：**

1. **重版本是错的**——规则越多效果越差，207 次实验证明了。
2. **极简是对的**——59 行承载核心纪律，比 179 行更有效；被砍掉的多是"仪式成本"。
3. **核心价值是真的**——「真打开看一眼」「未验证标注」，这几条反复被验证有用。
4. **轻任务上价值小**——所以做了风险分级，轻任务只常驻 3 条。

> **233 次实验测出来的不是"规则越多越好"，而是"规则越少越好，但核心那几条不能少"。**

**四个 test-bed 的实测定性结论：**

| 测试场        | 设计         | 任务类型 | 定性结论                       |
| ---------- | ---------- | ---- | -------------------------- |
| Test-Bed 1 | 单臂 ×6      | 轻任务  | 轻任务上价值小                    |
| Test-Bed 2 | 单臂 ×5      | 中等任务 | 不提升代码质量，提升交付可信度（评估记录整理中）   |
| Test-Bed 3 | **A/B 双臂** | 创意任务 | 「真打开看一眼」抓到 5 处视觉问题，结构校验抓不到 |
| Test-Bed 4 | **A/B 双臂** | 复杂创意 | 判分未定稿；已记录的观察见下方「诚实边界」      |

**几条可引用的硬数字：**

| 结论               | 数字                                         | 来源          |
| ---------------- | ------------------------------------------ | ----------- |
| 软维度（质量 / 纪律评分）提升 | **+20~24**                                 | P1-5        |
| 反例验证执行率          | **带 skill 100% vs 无 skill 33%**            | P1-1 终报     |
| 自我校准缺口率          | **无 skill 100% → 带 skill 约 33%**           | P1-2 自我校准分析 |
| 判定台可信度           | T6/T7/T8 三套，均通过"变异全灭 + GOLD 零误杀 + 判定门反向自查" | P1-7 终报     |

> **实验原始数据（约 70 MB / 3066 文件）在 [`experiments` 分支](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments)。** 主仓库（main）只含 skill 本体，agent clone 时不会拉取实验数据；想复现或审查过程，切到 experiments 分支即可。

---

## 诚实边界 / What It Is Not

这一节写的是**我们自己测出来的局限**——不是谦虚，是口径。

> **版本适用性**：标注「**旧版**」的条目测于 **v1.2.x 时代**（v1.2.2 / v1.2.5）。v1.4.x 极简版起已删除硬指标化与繁复条款，改为"少量特性 + 遗忘机制"，**这些旧版结论在现行 1.5.0 上不再适用**。

- **不提升推理能力**，也不是 GPT 专用——从 GPT 系列（含 GPT-5.6 Sol、GPT-6 Astra）提炼而来，但适用于所有具备指令遵循能力的大模型。
- **不兜底**〔**旧版** v1.2.2 / v1.2.5〕——2026-09 的 n=2 对照实验（三个机械判定任务）显示：在**致命缺陷率**这个维度上，带 skill 的臂与不带 skill 的臂**没有拉开可辨的差距**，held-out 上甚至略差。这个反向结果我们**也放进了仓库**。**该结论测于 v1.2.x 旧版本，v1.4.x 起不再适用。** 防线靠证据与独立复验，不靠条款。
- **不提升代码质量**——实验一致显示：代码本体差别不大，变好的是**交付可信度**。
- **不是加速器**——验证习惯会占去约三到四成的时间预算，换来的是"敢直接用"的交付。**要最快出活，这个 skill 不适合你。**
- **对创意产物部分条款偏重**——实测反馈：七条纪律里有 2–3 条对纯视觉/创意产物没有落点（如变异测试、数字重算）。这类任务建议走轻量档。
- **加条款不等于更好**〔**旧版** v1.2.2 / v1.2.3-draft〕——受控对照显示：纪律硬指标化后评分**并未提升**（原则引导 58.17 vs 硬指标 57.00，差 +1.17 落在判分误差内，判定为**等效**），故最终不实施硬指标化；更重的 v1.2.5（179 行 / 77 条自检）被实验证伪并废弃。
- **不是流程绑架**——执行阶段纪律完全退场，创作不被打断；轻任务几乎无感。

---

## 设计哲学 / Philosophy

- **规则越少越好，但核心那几条不能少**——233 次实验的最终结论；
- **创作是创作，检查是检查**——忘/想交替的全部理由；
- **证据高于声称**——全绿不算证据，断言红过才算验过；
- **责任不随委派转移**——子智能体交回后，主 Agent 仍是 DRI。

---

## 安装 / Install

两种装法，对应两类运行时（用多个就各装各的）：

### 目录型运行时：Claude Code / WorkBuddy 等

```bash
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
cp -r gpt-series-reasoning-style ~/.claude/skills/    # WorkBuddy 用 ~/.workbuddy/skills/
```

> **拷整个文件夹，不要只拷 `SKILL.md`**——`references/` 与 `templates/` 是按需加载的，缺了它们，多智能体场景会失效。

### AGENTS.md 运行时：Codex / Gemini CLI / Copilot CLI 等

```bash
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
cd gpt-series-reasoning-style    # 在仓库目录内启动 agent，AGENTS.md 入口路由自动生效
```

路由只做一件事：让 agent 读 `SKILL.md` + `VERSION` 完成加载，其余文件按需读取。

### 更新与验证

```bash
git pull    # 更新；版本号见 VERSION 文件
```

验证装好了：问 agent「**你的版本号是多少？加载证明需要哪几个文件？**」——应答 `1.5.0`，说得出五阶段时序，并能逐字引用第 1 条纪律。

## 触发方式 / Usage

- **自动触发**（由 `SKILL.md` 的 description 决定）：涉及数字验算、代码交付、多 Agent 协作、需要防假完成的任务；或用户说"做完了帮我查 / 看看对不对 / 验收"；或派发子任务、多个 AI 分工。
- **显式点名**：`使用 gpt-series-reasoning-style 执行本次任务。`
- **不加载**：一句话问答、纯聊天、小且可逆的改动——纪律不该出现在不需要它的地方。

## 成本 / Cost

| 项目         | 实测值                                                          |
| ---------- | ------------------------------------------------------------ |
| `SKILL.md` | **1834 字节 / 29 行**（常驻约 0.6k token）——只有五阶段流程表，规则不在其中 |
| 阶段 2 按需   | `references/plan-rules.md`（2321 字节）——仅在规则规划阶段读入        |
| 阶段 5 按需   | `references/review-rules.md`（2547 字节）——仅在纪律检查阶段读入      |
| 加载路径      | 平时只读 `SKILL.md` + `VERSION`；阶段 2 读 plan-rules、阶段 5 读 review-rules、多智能体场景另读 `multi-agent.md`；**任务结束后规则内容全部遗忘** |
| 峰值常驻文本   | 任一时刻上下文里的规则文本不超过一份（规划或审查，二者不同时在场）              |

**对比 v1.2.5 重版本**：38.7 KB / 179 行 / ~12k token —— 已由实验证明是更差的选择（见「实测与证据」）。

## 仓库结构 / What's Inside

| 文件                               | 角色                                                     |
| -------------------------------- | ------------------------------------------------------ |
| `SKILL.md`                       | **流程权威**（29 行）。只有五阶段流程 + 退出条件，不含规则条文               |
| `references/plan-rules.md`       | **阶段 2 专用**：规划规则（含"保留阶段1构想"、形态叠加、轻量档、退出条件）         |
| `references/review-rules.md`     | **阶段 5 专用**：8 条纪律（★ 三条为轻任务必做）+ 退出条件                 |
| `references/multi-agent.md`      | 形态二三细则：命中信号、派发规范、六步操作、红线                             |
| `AGENTS.md`                      | 跨运行时入口路由（Codex / Gemini CLI 等），仅指路，无规则               |
| `templates/`                     | 指挥官 / 执行者 / 审查者三张角色卡 + 任务包七要素                        |
| `scripts/selfcheck.py`           | 仓库一致性自检（**24 项**，纯只读，已适配文件级渐进加载结构）                  |
| `SECURITY.md`                    | 安全模型说明                                                 |
| `social-preview.svg / .png`      | 仓库横幅图（1280×640）                                       |

## 版本 / Versioning

当前版本：**1.5.0**

- **v1.4.x 极简线**：五阶段时序、文件级渐进加载、协作形态叠加——当前主线；
- **v1.2.x 重版线**：179 行、模块矩阵、self-test 冻结 77 条——**已被实验证伪**，该线已废弃。

## License / 许可证

MIT
