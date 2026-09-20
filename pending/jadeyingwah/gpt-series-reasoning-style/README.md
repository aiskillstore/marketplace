<div align="center">

# GPT-Series Reasoning Style

**把"Agent 说做完了"变成"Agent 证明做完了"。**  
**Turn "the agent says it's done" into "the agent proves it's done".**

<img src="assets/social-preview.svg" alt="GPT-Series Reasoning Style · 交付纪律层" width="100%">

![Version](https://img.shields.io/badge/version-1.6.0-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Size](https://img.shields.io/badge/SKILL.md-3594%E5%AD%97%E8%8A%82%C2%B735%E8%A1%8C%E9%97%A8%E7%A6%81-orange)
![Experiments](https://img.shields.io/badge/A%2FB%20%E4%B8%8E%E5%AE%9E%E6%B5%8B-300%2B%20%E8%87%82%E6%AC%A1-success)
![Runtime](https://img.shields.io/badge/按需加载-纯文本-blueviolet)
![CI](https://github.com/JadeYingWah/gpt-series-reasoning-style/actions/workflows/ci.yml/badge.svg)

</div>

---

# 📖 目录 / Table of Contents

## 🇨🇳 中文版

- [来源与适用范围](#来源与适用范围)
- [为什么不是"把 GPT 的行为规则全搬过来"](#为什么不是把-gpt-的行为规则全搬过来)
- [与其他skill共存](#与其他skill共存)
- [首创性设计](#首创性设计)
- [它治的是什么病](#它治的是什么病)
- [它凭什么不一样](#它凭什么不一样)
- [它怎么工作](#它怎么工作)
- [交付长什么样](#交付长什么样)
- [怎么知道它生效了](#怎么知道它生效了)
- [八条纪律](#八条纪律)
- [多智能体协作](#多智能体协作)
- [实测与证据](#实测与证据)
- [诚实边界](#诚实边界)
- [设计哲学](#设计哲学)
- [安装](#安装)
- [触发方式](#触发方式)
- [成本](#成本)
- [仓库结构](#仓库结构)
- [版本](#版本)

## 🇬🇧 English

- [Origin and Scope](#origin-and-scope)
- [Why Not Copy Every Rule](#why-not-copy-every-rule)
- [Coexists with Other Skills](#coexists-with-other-skills)
- [A First of Its Kind](#a-first-of-its-kind)
- [The Actual Problem](#the-actual-problem)
- [One Divergence](#one-divergence)
- [How It Works](#how-it-works)
- [What Delivery Looks Like](#what-delivery-looks-like)
- [How To Know It's Working](#how-to-know-its-working)
- [The Rules](#the-rules)
- [Multi-Agent](#multi-agent)
- [Field Tests](#field-tests)
- [What It Is Not](#what-it-is-not)
- [Philosophy](#philosophy)
- [Install](#install)
- [Usage](#usage)
- [Cost](#cost)
- [What's Inside](#whats-inside)
- [Version](#version)

## 📄 Common

- [License](#license)

---

# 🇨🇳 中文版说明书

## 来源与适用范围

本 skill 不是凭空设计的规则集，而是从一系列 **GPT 系列大模型**（包括 **GPT-5.6 Sol** 与 **GPT-6 Astra**）在真实交付任务中的长期使用过程里**观察、提炼**出来的。

我们把这些模型在规划与验收环节反复表现出的有益特点——**先想清楚再动手、交付时给出可复现的验证、没验过的地方主动标注**——保留并固化成一份纪律文本。

因此，它**不是**某个模型的专用配件：提炼的是**行为特征**，不是模型能力。任何具备指令遵循能力的大模型都可以加载它。名字里的 "GPT-Series" 记录的是它的**来源**，不是它的**适用范围**。

**它不挑场景。** 执行阶段规则文件根本不加载——挂着它的边际成本在执行期趋近于零：不打断思路、不占上下文、不把流程塞给你。小且可逆的任务自动降级为"直接做、做完扫一眼"，不触发调研和方案确认。在**历史 A/B（233 轮：任务×臂×轮）**与后续实测（experiments 脚本口径 ≥286 臂次/53 批至 09-17 素材，另加 09-17 八组床与 09-18 四场 v1.6.0 单臂包）中，**没有任何一类任务测出"带 skill 比不带更差"**；稳定的正向收益集中在交付可信度（敢不敢直接用、有没有假完成），而不是逼你走流程。

代码、写作、设计、分析、日常问答——都可以挂着它。它唯一的"代价"是交付前多看一眼；如果你明确要最快出活，说一声"别管验收"即可。


## 为什么不是"把 GPT 的行为规则全搬过来"

大量 A/B 对照实验反复证明了一件事：**把 GPT 自身的行为特点写成规则、塞进使用者的执行过程，结果适得其反**。你无法靠堆砌规则，让使用者复现 GPT 那样的产出质量。

实测中规则越多并不等于越好：把纪律硬指标化后，评分**并未提升**（与原则引导的差异落在判分误差内，判定为等效）；更极端的 v1.2.5 重版本（179 行、77 条自检）则被实验直接证伪并废弃。执行者记不住繁复步骤、模板填不满，最后流于形式应付。

> **版本注**：上述"规则越多越差"的对比来自 **v1.2.x 旧版本**（v1.2.2 / v1.2.3-draft / v1.2.5）。v1.4.x 极简版起已删除硬指标化与繁复条款，现行 **1.6.0 不再适用该对比**。

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


## 与其他skill共存

> **不抢流程，只做验收。** 我们专门设计了共存机制：本skill只在**阶段2（规划）**和**阶段5（验收）**介入，阶段1/3/4完全开放——其他任何类型skill（实现型/设计型/视觉型等）的方法和流程照常执行，互不干扰。流程冲突时以宿主和用户指令为准。
>
> 这意味着你可以同时挂着 frontend-design、imagegen、xlsx 等任何其他类型skill，再加上本skill做交付门禁——各管各的，不会打架。


## 首创性设计

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

---

## 它治的是什么病

AI agent 最贵的失败，从来不是"不会做"，而是**没验过就说做完了**：

- 测试没真跑，宣布"全部通过"；
- HTML 没在浏览器里打开过，宣布"页面没问题"；
- 关键数字没重算，照抄第一遍的结果；
- 交付说明里写着"音效已实现"——产物里连一行音频代码都没有。

在**四轮独立复现、共 14 个实验臂**的对照实验里，AI **无一例外**自报"测试全过、验证有效"——而独立复查（机械判定台）仍判出大量真实缺陷。

2026-09-17 的同题双臂实测（4 个小游戏，两组各自独立完成）再现了这一切：**不带纪律的裸平台**交付后宣布"实测可玩、全链路断言全部通过"——逐文件核验发现其宣称的验证与产物对不上。同一天，带纪律的对照臂交付了**可复现的验证脚本与逐项断言记录**。

所以真正决定价值的不是"它做得多快"，而是——

> **你敢不敢直接用它的产出。**

这个 skill 只干一件事：**把"我觉得行"变成"验过了，证据在这儿"。**

## 它凭什么不一样

主流 skill 的默认形态是「**加载后全程在场**」；而多智能体框架常把治理规则发给**每一个**参与角色——执行者手里也拿着指挥官的职权条款，角色越位由此发生。

本 skill 把隔离做到**两层物理级**：

1. **执行者与审查者窗口不加载本 skill**——他们的全部行为规范来自身份文件与任务包（自包含），指挥官职权条款（五阶段、形态判断、配置确认）**物理上不在他们的上下文里**；
2. **指挥官自己的 SKILL.md 也只是一道门禁**（3594 字节 / 35 行）——纪律全文（DISCIPLINE.md，3862 字节 / 33 行）在**动手做事的前一刻**才被放行。

常驻上下文里**只有一句门禁**——你看不到 skill 常见的那些负作用，只收下它的益处。

> **为什么这样设计**：多数 skill 一旦加载便全程在场——规则持续占用注意力、打断思路、消耗上下文。本 skill 把自己拆成**规划**与**验收**两端，中间漫长的执行阶段让纪律退场；只在自判"我做完了"的那一刻重新加载审查规则。所以你可以**只收下它的益处，不必承受纪律常驻的代价**。

## 它怎么工作

装上后**无需任何特殊指令**。当 agent 接到交付型任务（写代码、算数据、做页面、多 Agent 分工），SKILL.md 的纯门禁会在**动手前一刻**放行纪律全文，然后进入**五阶段时序**：

```text
┌─ 门禁（SKILL.md · 35 行纯门禁）——「前一刻」= 写交付物/施工确认/产线命令/宣布交付 中最早者
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
             ＋ 完成档位 C1/C2 标明 ＋ 无未处理的"这里好像有问题"
```

**完成档位（1.6.0）**：阶段5通过 = **C1 可验收**（须写清产品档是否拉满）；「产品做好了」= **C2**，只能来自你确认或外部 scorecard，禁止 Agent 自封。执行面无规则——纪律只在门禁时点、阶段2、阶段5出现。

**任务交付之后**：彻底忘记 `plan-rules.md` / `review-rules.md` / `multi-agent.md` 的具体内容——只记"有五个阶段、到哪个阶段读哪个文件"。规则长什么样，下次需要时再读。

规则文件只在阶段 2 与阶段 5 被读进来，**执行期它们根本不在上下文里**；纪律全文（DISCIPLINE.md）也只在动手前一刻才被放行。

设计意图就两句话：

- **创作时没有纪律**——阶段 1 与整个执行阶段，规则不污染思路；
- **检查有两道**——直觉抓规则**没覆盖到**的问题，纪律确保规则**覆盖到**的都做到，互不替代。

---

## 交付长什么样

同一种任务，装上前后的两副面孔：

**没有纪律层：**

> 做完了。功能都实现了，测试也全过了。

**有纪律层：**

> **做了什么**：重写导出功能，新增 3 个边界用例。  
> **怎么验的**：浏览器实测渲染（截图见附件）；`pytest tests/test_export.py -q` → 12 passed。  
> **哪些没验**：① Safari 兼容性——本机无 Safari，建议你打开自验；② 10 万行以上大数据量性能——没有现成数据集。

差别不在格式好看——是你**一眼就知道哪些话能信、哪些还得自己再验**。

## 怎么知道它生效了

- 交付消息开始自带三件套：做了什么 / 怎么验的（可复现命令）/ 哪些没验；
- 没验过的地方**主动认**，而不是含糊带过；
- 环境不支持真打开时，给你自验步骤，而不是装作验过；
- 连续失败两次后换路径，而不是硬刚；
- 轻任务上它几乎隐身——**这是设计，不是失灵**。

---


## 八条纪律

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

## 多智能体协作

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



## 实测与证据

**最新实测（2026-09-18 · v1.6.0）——交付型 + 创意型单臂（无 B 臂，只记行为与完成档位）：**

| 实验 | 条件 | 结果 |
|---|---|---|
| **鸣潮伤害验算表**（数字/交付） | skill v1.6.0 · 引擎 `damage_calc.py` 1:1 | 页内 21/21 + Python 15 项交叉 + 变异 `792→793` 红；**完成档位 C1**（实机对账待用户） |
| **星光接取**（创意小游戏） | v1.6.0 · A 档方向卡 · 质量预算 ≤2 轮 | 逻辑 24/24（含变异）+ Chrome/点击开局；**C1**，产品档未拉满 |
| **3D 钓鱼 / Neon Void**（创意游戏） | v1.5.5–1.6.0 讨论前后 | 口供与 artifacts 显示 C1 式标注 + 自动化证据；**C2 须用户试玩**；完整钓鱼源码未入仓（口供级） |

> **1.6.0 口径**：阶段5通过 = **C1 可验收**；「产品做好了」= **C2**（用户或外部 scorecard）。执行面无规则；创意段可不挂 skill，验收再挂。证据在 [`experiments` 分支](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments) `raw-materials/*2026-09-18/`。

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
  - **2026-09-18**：4 场 v1.6.0 实测包（鸣潮验算表、星光接取、3D 钓鱼口供、Neon Void 证据层）。
- 结论沉淀：规则越少越好，但核心那几条不能少；**C1/C2 把诚信完成与产品满意拆开**。
- Harness 本机另有 ab-* 目录若干，**未全部入 experiments 分支**，不计入上述公开数字。
- 可引用硬数字（v1.2.x 时代对照实验）：软维度提升 **+20~24**（P1-5）；反例验证执行率 **带 skill 100% vs 无 skill 33%**（P1-1）；自我校准缺口 **100% → 33%**（P1-2）。
- 实验原始数据（约 70 MB / 3066+ 文件）在 [`experiments` 分支](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments)；主仓库只含 skill 本体。

</details>

---

## 诚实边界

这一节写的是**我们自己测出来的局限**——不是谦虚，是口径。

> **版本适用性**：标注「**旧版**」的条目测于 **v1.2.x 时代**。v1.4.x 极简版起已删除硬指标化与繁复条款，**这些旧版结论在现行 1.6.0 上不再适用**。

- **不提升推理能力**，也不是 GPT 专用——从 GPT 系列（含 GPT-5.6 Sol、GPT-6 Astra）提炼而来，但适用于所有具备指令遵循能力的大模型。
- **不提升代码质量**——实验一致显示：代码本体差别不大，变好的是**交付可信度**。
- **不是加速器**——验证习惯会占去约三到四成的时间预算，换来的是"敢直接用"的交付。
- **不是流程绑架**——执行阶段规则文件根本不加载，创作不被打断；问答场景双臂实测零打扰。轻任务几乎无感。
- **裸平台的模型能力已经很强**——信息型问答双臂满分无差异；三游戏裸平台也能做出来（虽然丢了主题、两个打不开）。skill 的价值不是让模型变强，是把质量从碰运气变成有保证：任务核心词不被丢掉（菲比秋比对照）、交付形态先问你（exe 双击直启）、未验证项如实标注并自我闭环。

<details>
<summary><b>历史实验边界档案</b>（v1.2.x 时代，现行不适用，点开备查）</summary>

不兜底〔旧版 v1.2.2 / v1.2.5〕——n=2 对照：致命缺陷率维度带 skill 与不带没有拉开可辨差距，held-out 略差。反向结果也放进仓库。防线靠证据与独立复验，不靠条款。

加条款不等于更好〔旧版 v1.2.2 / v1.2.3-draft〕——硬指标化后评分未提升（58.17 vs 57.00，等效）；更重的 v1.2.5（179 行/77 条自检）被证伪废弃。

</details>

---

## 设计哲学

- **规则越少越好，但核心那几条不能少**——历史 A/B（233 轮）+ 后续实测的最终结论；
- **创作是创作，检查是检查**——忘/想交替的全部理由；
- **证据高于声称**——全绿不算证据，断言红过才算验过；
- **责任不随委派转移**——子智能体交回后，主 Agent 仍是 DRI。

---

## 安装

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

验证装好了：新开会话问 agent「**你的版本号是多少？加载证明需要哪几个文件？五阶段是什么？**」——应答 `1.6.0`，说得出门禁链路（`SKILL.md` 门禁 → **前一刻**读 `DISCIPLINE.md`；前一刻=写交付物/施工确认/产线命令/宣布交付中最早者）与五阶段时序，并能逐字引用纪律第 1 条；提及完成档位 **C1 可验收 / C2 产品满意**（C2 须用户或外部认定）。

## 触发方式

- **自动触发**（由 `SKILL.md` 的 description 决定）：涉及数字验算、代码交付、多 Agent 协作、需要防假完成的任务；或用户说"做完了帮我查 / 看看对不对 / 验收"；或派发子任务、多个 AI 分工。约束交付是否真实，**不单独设定创意质量满意标准**（见 DISCIPLINE 完成档位）。
- **显式点名**：`使用 gpt-series-reasoning-style 执行本次任务。`
- **不加载**：一句话问答、纯聊天、小且可逆的改动——纪律不该出现在不需要它的地方。
- **创意任务用法**：要抬产品上限时，**创意/实现段可不挂本 skill**，收工后再挂验收（真打开 + C1/C2）；门禁与打磨预算不在创意场里，才谈得上零压榨。

## 成本

| 项目         | 实测值                                                          |
| ---------- | ------------------------------------------------------------ |
| `SKILL.md` | **3594 字节 / 35 行**（常驻约 0.6k token）——**纯门禁**，纪律全文在 `DISCIPLINE.md`（3862 字节/33 行，动手前一刻才读） |
| 阶段 2 按需   | `references/plan-rules.md`（6162 字节）——仅在规则规划阶段读入        |
| 阶段 5 按需   | `references/review-rules.md`（5041 字节）——仅在纪律检查阶段读入      |
| 多智能体按需  | `references/multi-agent.md`（5718 字节）——仅叠加形态二三时读入       |
| 加载路径      | 平时只读 `SKILL.md`（35 行门禁）+ `VERSION`；**动手/回答前一刻**读 `DISCIPLINE.md`（纪律全文）；阶段 2 读 plan-rules、阶段 5 读 review-rules、多智能体场景另读 `multi-agent.md`；**任务结束后规则内容全部遗忘** |
| 峰值常驻文本   | 任一时刻上下文里的规则文本不超过一份（规划或审查，二者不同时在场）              |

**对比 v1.2.5 重版本**：38.7 KB / 179 行 / ~12k token —— 已由实验证明是更差的选择（见「实测与证据」）。


## 仓库结构

| 文件                               | 角色                                                     |
| -------------------------------- | ------------------------------------------------------ |
| `SKILL.md`                       | **门禁**（35 行）。不含纪律正文；「前一刻」动作化 + 创意构想例外            |
| `DISCIPLINE.md`                  | **纪律全文**（33 行）。五阶段 + **完成档位 C1/C2** + 任务后遗忘 + 边界 + 加载规则 |
| `references/plan-rules.md`       | **阶段 2 专用**：规划规则（构想实质保留、形态裁定、A档不锁质量上限、创意质量预算） |
| `references/review-rules.md`     | **阶段 5 专用**：8 条纪律（★三条轻任务必做）+ **第9条完成档位** + 退出条件    |
| `references/multi-agent.md`      | 形态二三细则：命中信号、派发规范、六步操作、红线                             |
| `AGENTS.md`                      | 跨运行时入口路由（Codex / Gemini CLI 等），仅指路，无规则               |
| `templates/`                     | 指挥官 / 执行者 / 审查者三张角色卡 + 任务包七要素                        |
| `scripts/selfcheck.py`           | 仓库一致性自检（**38 项**，纯只读，已适配文件级渐进加载结构）                  |
| `SECURITY.md`                    | 安全模型说明                                                 |
| `assets/social-preview.svg / .png`      | 仓库横幅图（1280×640）                                       |

## 版本

当前版本：**1.6.0**

- **v1.6.0**：重写说明书（REFERENCE.md）；与其他skill共存规则完善；文档一致性对齐；.gitattributes调整（Python/YAML计入Languages）；
- **v1.5.8**：创作类任务可直接跳过阶段2（陌生专名先搜再问用户确认）；
- **v1.5.7**：与其他skill共存规则（只在阶段2/5介入）；B档硬上限（未主动说逐项问时最多1题专名确认）；竖切优先（A档后立刻出可玩切片）；修复SKILL.md编码乱码；
- **v1.5.5**：SKILL.md 门禁化，纪律全文移入 DISCIPLINE.md（物理隔离）；
- **v1.4.x 极简线**：五阶段时序、文件级渐进加载——主线前身；
- **v1.2.x 重版线**：179 行、模块矩阵、self-test 冻结 77 条——**已被实验证伪**，该线已废弃。

**用法原则（1.6.0）**：执行面无规则；创意段若要零压榨，验收前可不挂本 skill；大版本（≥1.6）须总指挥主动提起。

## License

MIT

---

# 🇬🇧 English Documentation

## Origin and Scope

This skill is not an invented rule set. It was **observed and distilled** from long-term, hands-on use of a series of **GPT-series models** — including **GPT-5.6 Sol** and **GPT-6 Astra** — on real delivery tasks.

We kept and froze the habits these models showed at their best during planning and acceptance: **think it through before acting, ship reproducible verification, and flag what you could not verify**.

It is therefore **not** a model-specific add-on. What is distilled is **behavioral patterns**, not model capabilities — any instruction-following LLM can load it. "GPT-Series" in the name records its **origin**, not its **scope**.

**It does not pick its battles.** During execution the rule files are not loaded at all — the marginal cost of keeping it on is effectively zero at execution time: no thought interruption, no context tax, no workflow shoved in your face. Small and reversible tasks auto-degrade to "just do it, glance at the end" — no research, no plan approval. Across the **historical A/B line (233 task×arm×round)** plus later beds (script count ≥286 arms / 53 batches through 09-17 materials, plus 09-17 eight desktop beds and 09-18 four v1.6.0 single-arm field packs), **no task category showed the skill making things worse**; the consistent gain is in delivery trustworthiness, not in forcing a pipeline.

Code, writing, design, analysis, everyday Q&A — keep it on. Its only "cost" is one extra look before you ship; if you want raw speed, just say so.


## Why Not Copy Every Rule

Extensive A/B testing keeps showing one thing: **turning GPT's own behavioral traits into rules and injecting them into the user's execution process backfires.** You cannot make a user reproduce GPT-grade output quality by piling on rules.

In our tests, more rules did not mean better results: turning the discipline into hard metrics brought **no gain** (the gap versus principle-based guidance fell within scoring error and was judged equivalent), and the far heavier v1.2.5 build — 179 lines with 77 self-checks — was directly falsified and retired. Executors could not remember elaborate steps, templates were never fully filled, and compliance became theatre.

> **Version note**: the "more rules, worse results" comparison comes from **older v1.2.x builds** (v1.2.2 / v1.2.3-draft / v1.2.5). Hard metrics and bulky clauses were removed in the v1.4.x minimal line, so the comparison **no longer applies to the current 1.6.0**.

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


## Coexists with Other Skills

> **No process hijack, only acceptance.** We designed the coexistence mechanism deliberately: this skill only intervenes at **stage 2 (planning)** and **stage 5 (acceptance)**. Stages 1/3/4 are completely open — any other type of skill (implementation/design/visual, etc.) runs its methods and workflows as usual, no interference. When workflows conflict, the host and user instructions take precedence.
>
> This means you can run frontend-design, imagegen, xlsx, or any other skill alongside this one as a delivery gate — each does its own job, no fighting.


## A First of Its Kind

To our knowledge, this is the first design to achieve **discipline/flow isolation across a five-stage timeline** — inside a **single skill**, via **file-level progressive loading**.

Five stages unfold in sequence:

| # | Stage | Rule state | What happens |
| - | ----- | ---------- | ------------ |
| 1 | **Unconstrained ideation** | absent | think it through on judgment alone |
| 2 | **Progressive rule loading for planning** | loading | turn the vision into a plan, **fully preserving** the stage-1 vision rather than overwriting it |
| 3 | **Execution** | withdrawn | focused work; rules simply do not exist |
| 4 | **Unruled check** | absent | intuition-driven, catching what the rules **do not** cover |
| 5 | **Progressive rule loading for discipline check** | reloaded | enforce every rule, one by one |

The result is two **zeros**:

- **Zero interruption while executing** — the rules are absent during execution, so flow is never broken;
- **Zero compromise at acceptance** — the rules reload in full at delivery, and nothing on the list is skipped.

And with that: **delivery trustworthiness rises markedly** (skill-armed runs score clearly higher on quality/discipline).

---

## The Actual Problem

The most expensive failure of an AI agent is never "it doesn't know how" — it's **declaring done without verifying**:

- Tests never actually ran, yet "all pass" is claimed;
- The HTML never opened in a browser, yet "page works" is claimed;
- Key numbers were never recalculated, yet the first-pass result is copied;
- The delivery says "audio implemented" — but there isn't a single line of audio code in the artifact.

In **four independent reproductions, 14 experimental arms total**, the AI **invariably** self-reported "all tests pass, verified working" — while independent review (mechanical adjudication) still found numerous real defects.

The 2026-09-17 same-task dual-arm test (4 mini-games, two independent teams) reproduced all of this: **the discipline-free arm** delivered and announced "playable end-to-end, all assertions pass" — file-by-file review showed the claimed verification didn't match the artifact. The same day, the disciplined control arm delivered **reproducible verification scripts with itemized assertion records**.

So what really matters isn't "how fast it works" — it's:

> **Do you dare use its output directly.**

This skill does one thing only: **turn "I think it's fine" into "it's verified, here's the evidence."**

## One Divergence

The default shape of mainstream skills is "**always present once loaded**"; multi-agent frameworks often push governance rules to **every** participant — the executor holds the commander's authority clauses, and role creep begins there.

This skill isolates to **two physical layers**:

1. **Executors and reviewers don't load this skill** — their behavioral norms come entirely from their identity files and task packages (self-contained). The commander's authority clauses (five stages, form judgment, config confirmation) are **physically not in their context**;
2. **The commander's own SKILL.md is also just a gate** (3594 bytes / 35 lines) — the full discipline (DISCIPLINE.md, 3862 bytes / 33 lines) is only released **the moment before action begins**.

Only one gate sentence lives in persistent context — you don't see the usual downsides of skills, you only get the benefits.

> **Why it's built this way**: most skills stay present once loaded. This skill splits into **planning** and **acceptance**, and goes further: even the commander's own SKILL.md is a pure gate — the discipline file is released the moment before action. You get the benefits **without paying the costs** of an ever-present discipline.

## How It Works

Once installed, **no special instructions needed**. When the agent receives a delivery task (write code, compute data, build a page, multi-agent orchestration), the SKILL.md pure gate releases the full discipline **the moment before action**, then enters the **five-stage timeline**:

```text
┌─ Gate (SKILL.md · 35-line pure gate) — "the moment before" = earliest of: write deliverable / construction confirm / build command / announce delivery
│         Creative tasks get one round of direction ideation without reading DISCIPLINE; unknown proper nouns still require ask/search first
│
┌─ Stage 1 · Free ideation (don't read plan/review/multi-agent, don't create governance dirs) — figure out what you're doing on your own
│      Exit: ideation points listed, about to enter planning or implementation
┌─ Stage 2 · Rule planning (read references/plan-rules.md) — turn plan into reality per rules, respond to each ideation item
│      Exit: plan confirmed (structured option cards) ＋ risk graded ＋ form decided
│             ＋ creative quality budget written (A-tier doesn't cap quality ceiling) ＋ no more questions to ask
┌─ Stage 3 · Execution (rules completely absent) — work with your abilities, flow uninterrupted
│      Exit: no unresolved bugs; creative/visual tasks additionally require "openable complete path"
┌─ Stage 4 · Intuitive check (no rules) — scan the deliverable on common sense
│      Exit: no new doubts found (doubts confirmed or fixed on the spot, not carried into stage 5)
└─ Stage 5 · Discipline check (read references/review-rules.md) — items 1–8 + item 9 completion tier
       Exit: rules passed (light tasks ★3 items + item 9 / heavy tasks full + item 9) ＋ three-piece set
             ＋ completion tier C1/C2 marked ＋ no unresolved "something looks off here"
```

**Completion tiers (1.6.0)**: Stage 5 pass = **C1 acceptable for acceptance** (must state whether product tier is maxed); "product is good" = **C2**, which can only come from your confirmation or an external scorecard — agents are forbidden from self-declaring. Execution side has no rules — discipline only appears at gate timing, stage 2, and stage 5.

**After task delivery**: completely forget the specific content of `plan-rules.md` / `review-rules.md` / `multi-agent.md` — only remember "there are five stages, read the right file at the right stage". What the rules actually say, read again next time.

Rule files are only read in at stage 2 and stage 5 — **during execution they're not in context at all**; the full discipline (DISCIPLINE.md) is also only released the moment before action.

The design intent is two sentences:

- **No discipline while creating** — stage 1 and the entire execution phase, rules don't pollute thought;
- **Two checks** — intuition catches what rules **don't cover**, discipline ensures what rules **do cover** is all done, neither replaces the other.

---

## What Delivery Looks Like

Same task, two faces before and after installation:

**Without the discipline layer:**

> Done. All features implemented, tests all pass.

**With the discipline layer:**

> **What was done**: rewrote export functionality, added 3 edge cases.  
> **How it was verified**: real browser render (screenshots attached); `pytest tests/test_export.py -q` → 12 passed.  
> **What wasn't verified**: ① Safari compatibility — no Safari on this machine, please open and verify yourself; ② performance on 100k+ row datasets — no existing dataset.

The difference isn't pretty formatting — it's that you **know at a glance which claims to trust and which to verify yourself**.

## How To Know It's Working

- Delivery messages start including the three-piece set: what was done / how it was verified (reproducible commands) / what wasn't verified;
- What wasn't verified is **admitted** up front, not glossed over;
- When the environment can't really open something, you get self-verification steps, not fake verification;
- After two consecutive failures on the same action, it switches paths instead of stubbornly retrying;
- On light tasks it's nearly invisible — **that's by design, not malfunction**.

---


## The Rules

Stage 5 (discipline check) strictly passes these **8 items** (★ = 3 items that light tasks must also do):

| #  | Rule | Key point |
| -- | ---- | --------- |
| 1★ | **Really open it** | Open and actually use the artifact in a real environment — HTML needs browser rendering, API needs frontend calls, running scripts doesn't count. Other types: games go through a full core gameplay loop, reports check every number against the source, SVG is really rendered and zoomed in on. When the environment doesn't support it: honestly mark "unverified: browser render" + give the user self-verification steps |
| 2★ | **Mark what's unverified** | Delivery says three things only: what was done / how it was verified (reproducible commands) / what wasn't verified. List each unverified item with its reason, don't just write "partially unverified"; unverified items must be **prominently marked** with asterisks or bold, not hidden in the middle of paragraphs |
| 3  | **Delivery claims match** | You say "did X" — is there actually X in the artifact? One last read-back of your own delivery claims before delivery, find each item in the artifact; if you can't find it, either do it or change it to "not done + reason" |
| 4  | **Switch paths after two failures** | On the 2nd consecutive failure of the same action, don't try the same method a 3rd time; first judge whether it's equivalent to a verified path, don't get stuck |
| 5  | **All-green isn't evidence** | Deliberately introduce the error you're guarding against, assertions going red counts as verification; if everything still passes after mutation = mutation didn't work. Minimal recipe: null/too long/invalid type/missing key. **Non-code artifacts**: click every link, cross-check numbers, really render visuals and record verification |
| 6  | **Recalculate key numbers** | Key numbers in data/research deliveries, independently recalculate or cross-source; if they don't match, recalculation wins |
| 7  | **Isolate temp files** | Temp files don't go in the delivery directory, clean up at the end; cleanup only touches this task's own directory, no global process killing |
| 8★ | **Anti-infinite-loop** | Read the same file 3 times with no new info = stop; same action 3 times in a row with identical output = switch approach |

---

## Multi-Agent

Details in `references/multi-agent.md` (read only when triggered), role card templates in `templates/`.

### Form 2 · Sub-agents (open proactively when there's clear benefit, don't wait for user to ask)

**Open when any of these hit**: completely independent subtasks / need to run two things in parallel / need independent critical perspective / worried intermediate process pollutes main context.  
When dispatching, make three things clear: **goal, completion criteria, who to report back to**. Iron rule: after sub-agent reports back, **the main agent is still the DRI**, must verify it yourself; sub-agents don't report directly to the user; if one person can do it coherently, don't open a second.

### Form 3 · Multi-agent (confirm with user first / cross-model / large task division)

Six steps: commander identity declaration → build character profiles → break subtasks and write task packages → user relays dispatch → verify against original goal (check for drift first, then have the critic pick apart) → report three-piece set to user.

**Task package seven elements**: background / decided decisions / open gaps / completion criteria / allowed and prohibited scope / unique DRI / who to report back to.

**Three role cards** (`templates/`): **Commander** defaults to DRI, delegation doesn't transfer final responsibility; **Executor** only says "done per spec, please review"; **Critic** independently picks apart, doesn't do the work themselves.

**Red lines**: Executor saying "I'm done" isn't acceptance; Critic doesn't modify work; doesn't bypass the commander to report directly.

---



## Field Tests

**Latest tests (2026-09-18 · v1.6.0) — delivery + creative single-arm (no B arm, only records behavior and completion tier):**

| Experiment | Conditions | Results |
|---|---|---|
| **Wuthering Waves damage calculator table** (data/delivery) | skill v1.6.0 · engine `damage_calc.py` 1:1 | in-page 21/21 + Python 15-item cross-check + mutation `792→793` red; **completion tier C1** (real-device reconciliation pending user) |
| **Star Catch** (creative mini-game) | v1.6.0 · A-tier direction card · quality budget ≤2 rounds | logic 24/24 (including mutation) + Chrome/click to start; **C1**, product tier not maxed |
| **3D Fishing / Neon Void** (creative game) | v1.5.5–1.6.0 discussion period | transcripts and artifacts show C1-style annotation + automated evidence; **C2 requires user playtest**; complete fishing source not in repo (transcript-level) |

> **1.6.0 framing**: Stage 5 pass = **C1 acceptable for acceptance**; "product is done" = **C2** (user or external scorecard). Execution side has no rules; creative segments can skip the skill, then attach acceptance. Evidence in the [`experiments` branch](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments) `raw-materials/*2026-09-18/`.

**Controlled experiments (2026-09-17) — dual-arm, disk evidence + post-interview transcripts:**

| Experiment | With skill | Without skill | Who's better |
|---|---|---|---|
| **v1.5.1 · Phoebe retest** (unknown proper noun + from-scratch 2D game) | two rounds of search found "Phoebe" source → three questions to confirm → protagonist made it into the product | core word **silently dropped**, generic fishing game | **With skill clearly better** |
| **v1.5.2 · Q&A dual-arm** | search-verified + read VERSION + cited sources | same questions both arms got right | **Tie** → removed Q&A forced research |
| **v1.5.1 · Three-game collection** | A-tier confirmation → **exe direct-launch 3/3 playable** + unverified item automated closure | bat dependencies **2/3 don't open**, zero annotation | **With skill comprehensively better** |

> **One sentence**: clauses exist only for measured gaps; **C1/C2 separates "no fake completion" from "product is done well"**.

<details>
<summary><b>Historical experiment archive</b> (framing and old numbers, click for reference)</summary>

- Historical cumulative framing (don't mix):
  - **Narrative A/B rounds 233** (= heavy version line 207 + minimal line 26; one "task × arm × round" counts as one);
  - **experiments branch script count**: ≥ **286 arms / 53 batches** (regex-covered arm dirs, lower bound; ~3250 files total, including v1.2.x and pre-09-17 materials);
  - **2026-09-17**: 8 groups of desktop comparison/form beds (Phoebe / three-games×2 / 4399×2 / pomodoro / finance suite / three txts);
  - **2026-09-18**: 4 v1.6.0 test packs (WUWA calculator table, Star Catch, 3D fishing transcript, Neon Void evidence layer).
- Conclusion distilled: fewer rules is better, but the core few can't be missing; **C1/C2 separates honest completion from product satisfaction**.
- Harness has several local ab-* dirs, **not all in the experiments branch**, not counted in the public numbers above.
- Citable hard numbers (v1.2.x era controlled experiments): soft-dimension improvement **+20~24** (P1-5); counter-example verification execution rate **with skill 100% vs without skill 33%** (P1-1); self-calibration gap **100% → 33%** (P1-2).
- Raw experimental data (~70 MB / 3066+ files) is in the [`experiments` branch](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments); the main repo only contains the skill itself.

</details>

---

## What It Is Not

This section lists **the limitations we've measured ourselves** — not modesty, but framing.

> **Version applicability**: items marked "**old**" were measured in the **v1.2.x era**. Hard metrics and bulky clauses were removed in the v1.4.x minimal line, so **these old conclusions no longer apply to the current 1.6.0**.

- **Doesn't improve reasoning ability**, and isn't GPT-specific — distilled from GPT series (including GPT-5.6 Sol, GPT-6 Astra), but applies to all instruction-following LLMs.
- **Doesn't improve code quality** — experiments consistently show: code itself barely differs, what improves is **delivery trustworthiness**.
- **Not an accelerator** — verification habits eat up about 30-40% of the time budget, in exchange for "dare to use directly" deliveries.
- **Not workflow kidnapping** — during execution the rule files aren't loaded at all, creation isn't interrupted; Q&A scenarios showed zero disruption in dual-arm tests. Light tasks are nearly invisible.
- **The base platform's model is already strong** — information Q&A both arms got full marks with no difference; three games the base platform could also make (though it lost the theme and two didn't open). The skill's value isn't making the model stronger, it's turning quality from luck into a guarantee: task core words aren't dropped (Phoebe comparison), delivery form is asked first (exe double-click direct launch), unverified items are honestly annotated and self-closed.

<details>
<summary><b>Historical experiment boundary archive</b> (v1.2.x era, doesn't apply now, click for reference)</summary>

Doesn't catch critical defects [old v1.2.2 / v1.2.5] — n=2 comparison: critical defect dimension showed no distinguishable gap between with and without skill, held-out slightly worse. Reverse results are also kept in the repo. The defense relies on evidence and independent re-verification, not clauses.

Adding clauses ≠ better [old v1.2.2 / v1.2.3-draft] — hard metrics brought no score improvement (58.17 vs 57.00, equivalent); the heavier v1.2.5 (179 lines/77 self-checks) was falsified and retired.

</details>

---

## Philosophy

- **Fewer rules is better, but the core few can't be missing** — historical A/B (233 rounds) + later measurements' final conclusion;
- **Creation is creation, review is review** — the entire reason for the remember/forget alternation;
- **Evidence over claims** — all-green isn't evidence, assertions going red is what counts as verified;
- **Responsibility doesn't transfer with delegation** — after sub-agent reports back, the main agent is still the DRI.

---

## Install

Two installation methods, corresponding to two loading modes (use multiple clients, install each separately, no conflicts):

- **Method 1 · Native Skill (recommended)**: put the folder in the client's skills directory, auto-discovered on startup via `SKILL.md` description and triggered by context.
- **Method 2 · AGENTS.md project instructions**: for clients that don't support skill auto-discovery but read project-root `AGENTS.md`, `cd` into the repo and AGENTS.md points to the loading.

### Method 1: Native Skill (auto-discovery)

Skills directories for each client (`<name>` = `gpt-series-reasoning-style`):

| Client | Personal (global, all projects) | Project-level (shared with team via repo) |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Cursor (2.4+) | `~/.cursor/skills/` | `.cursor/skills/` |
| Codex CLI | `~/.codex/skills/` | `.codex/skills/` (or `.agents/skills/`) |
| WorkBuddy | `~/.workbuddy/skills/` | — |
| Other SKILL.md-supporting clients | check their docs for skills directory | same |

> **One location feeds two clients**: Cursor will also load `.claude/skills/` and `~/.claude/skills/` (same for Codex dir). If using both Claude Code and Cursor, install into `~/.claude/skills/` and both work.

**macOS / Linux (bash)** — Claude Code personal level example:

```bash
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
mkdir -p ~/.claude/skills && cp -r gpt-series-reasoning-style ~/.claude/skills/
# Cursor: change target to ~/.cursor/skills/; Codex: ~/.codex/skills/; WorkBuddy: ~/.workbuddy/skills/
```

**Windows (PowerShell)**:

```powershell
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force gpt-series-reasoning-style "$HOME\.claude\skills\"
# Cursor target "$HOME\.cursor\skills"; Codex "$HOME\.codex\skills"; WorkBuddy "$HOME\.workbuddy\skills"
```

**Project-level / team share**: put the folder in the project repo's `.claude/skills/` (or the corresponding client dir) and commit — teammates clone the repo and automatically get it, no separate install.

After install, **start a new session** (or restart the client) to discover the new skill.

### Method 2: AGENTS.md project instructions (cd-type)

For clients that don't do skill auto-discovery but read project-root `AGENTS.md` (Codex / Gemini CLI / Copilot CLI / Windsurf / Zed, etc.):

```bash
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
cd gpt-series-reasoning-style    # start the agent inside the repo dir, AGENTS.md entry point auto-applies
```

This isn't skill registration, it's the agent treating `AGENTS.md` as project instructions and following its lead to `SKILL.md` (gate) → `DISCIPLINE.md` (five stages) → read references as needed. If your client only reads specific filenames, add a symlink at the repo root pointing to `AGENTS.md` (e.g., `ln -s AGENTS.md CLAUDE.md`, `ln -s AGENTS.md GEMINI.md`; on Windows use `mklink` or just copy a file).

### Installation notes

- **Copy the whole folder, don't just copy `SKILL.md`** — `DISCIPLINE.md`, `references/`, `templates/`, `scripts/` are all loaded on demand; missing them breaks multi-agent scenarios.
- **The directory name must be `gpt-series-reasoning-style`**: downloaded ZIP extracts with `-main` / `-master` suffixes, rename it or some clients' discovery and slash invocation will break.
- **Zero dependencies, no network, no telemetry**: the whole thing is plain Markdown; only `scripts/selfcheck.py` repo self-check needs Python 3 (optional, skill works fine without Python).

### Update and verify

```bash
cd <skills dir>/gpt-series-reasoning-style && git pull    # version in VERSION file
python scripts/selfcheck.py    # optional: 38 static self-check items, exit code 0 = all pass
```

Verify it's installed: in a new session ask the agent "**What's your version? What files prove you're loaded? What are the five stages?**" — should answer `1.6.0`, state the gate chain (`SKILL.md` gate → **moment before** reading `DISCIPLINE.md`; moment before = earliest of writing deliverable / construction confirm / build command / announcing delivery) and five-stage timeline, and quote rule 1 verbatim; mention completion tiers **C1 acceptable / C2 product satisfaction** (C2 requires user or external recognition).

## Usage

- **Auto-trigger** (determined by `SKILL.md` description): tasks involving numeric verification, code delivery, multi-agent collaboration, need to prevent fake completion; or user says "done, help me check / see if it's right / accept it"; or dispatching subtasks, multiple AI division of labor. Constrains whether delivery is real, **doesn't set creative quality satisfaction standards on its own** (see DISCIPLINE completion tiers).
- **Explicitly named**: `Use gpt-series-reasoning-style for this task.`
- **Don't load**: one-sentence Q&A, pure chat, small and reversible changes — discipline doesn't belong where it's not needed.
- **Creative task usage**: to raise the product ceiling, **creative/implementation segments can skip this skill**, attach acceptance after finishing (really open + C1/C2); gates and polishing budgets stay out of the creative space, that's how zero-friction works.

## Cost

| Item | Measured value |
| ---- | -------------- |
| `SKILL.md` | **3594 bytes / 35 lines** (~0.6k token resident) — **pure gate**, full discipline in `DISCIPLINE.md` (3862 bytes / 33 lines, read only the moment before action) |
| Stage 2 on-demand | `references/plan-rules.md` (6162 bytes) — only read in the planning stage |
| Stage 5 on-demand | `references/review-rules.md` (5041 bytes) — only read in the discipline check stage |
| Multi-agent on-demand | `references/multi-agent.md` (5718 bytes) — only loaded when adding form 2/3 |
| Loading path | normally only reads `SKILL.md` (35-line gate) + `VERSION`; **moment before action/answer** reads `DISCIPLINE.md` (full discipline); stage 2 reads plan-rules, stage 5 reads review-rules, multi-agent scenarios additionally read `multi-agent.md`; **rule content all forgotten after task ends** |
| Peak resident text | at any moment, rule text in context is at most one copy (planning or review, never both present) |

**Compared to v1.2.5 heavy version**: 38.7 KB / 179 lines / ~12k token — experimentally proven to be the worse choice (see "Field Tests").


## What's Inside

| File | Role |
| ---- | ---- |
| `SKILL.md` | **Gate** (35 lines). No discipline text; "moment before" actionized + creative ideation exception |
| `DISCIPLINE.md` | **Full discipline** (33 lines). Five stages + **completion tiers C1/C2** + post-task forgetting + boundaries + loading rules |
| `references/plan-rules.md` | **Stage 2 only**: planning rules (ideation substantive preservation, form judgment, A-tier doesn't cap quality, creative quality budget) |
| `references/review-rules.md` | **Stage 5 only**: 8 rules (★ three light-task-mandatory) + **item 9 completion tier** + exit conditions |
| `references/multi-agent.md` | Form 2/3 details: trigger signals, dispatch norms, six-step operations, red lines |
| `AGENTS.md` | Cross-runtime entry routing (Codex / Gemini CLI etc.), pointer only, no rules |
| `templates/` | Commander / Executor / Critic three role cards + task package seven elements |
| `scripts/selfcheck.py` | Repo consistency self-check (**38 items**, read-only, adapted to file-level progressive loading) |
| `SECURITY.md` | Security model explanation |
| `assets/social-preview.svg / .png` | Repo banner (1280×640) |

## Version

Current version: **1.6.0**

- **v1.6.0**: rewritten manual (REFERENCE.md); coexistence rules refined; document consistency aligned; .gitattributes adjusted (Python/YAML counted in Languages);
- **v1.5.8**: creative tasks can skip stage 2 directly (unknown proper nouns searched first then ask user to confirm);
- **v1.5.7**: coexistence rules (only intervenes at stage 2/5); B-tier hard cap (max 1 proper-noun question unless user asks for item-by-item); vertical slice priority (playable slice immediately after A-tier); fixed SKILL.md encoding garble;
- **v1.5.5**: SKILL.md gated, full discipline moved into DISCIPLINE.md (physical isolation);
- **v1.4.x minimal line**: five-stage timeline, file-level progressive loading — the mainline predecessor;
- **v1.2.x heavy line**: 179 lines, module matrix, self-test frozen 77 items — **experimentally falsified**, this line is retired.

**Usage principle (1.6.0)**: no rules on execution side; creative segments can skip the skill before acceptance if zero-friction is desired; major versions (≥1.6) require commander to proactively bring it up.

## License

MIT
