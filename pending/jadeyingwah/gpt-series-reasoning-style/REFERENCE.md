# gpt-series-reasoning-style · 完整说明书

> **交付验收与多智能体协作纪律层。**
> A delivery-discipline layer for agent skills — Chinese-primary.

<img src="social-preview.svg" alt="GPT-Series Reasoning Style — 交付验收纪律层" width="640">

> 图：`social-preview.svg`（1280×640）——三张卡片（规划 / 执行 / 审查）上以**盾牌图标的两种状态**表达纪律开关：虚线盾+斜杠 = **RULES OFF**（规则退场），实线盾+勾 = **RULES ON**（规则从文件读入）；底部图例同步释义。

| 项 | 值 |
|---|---|
| 名称 / 版本 | `gpt-series-reasoning-style` · **1.5.0**（以 `VERSION` 文件为准） |
| 许可 | MIT |
| 主导语言 | 中文（关键术语保留英文） |
| 运行时形态 | **纯文本**——不改代码、不联网、不上报 |
| 加载成本 | `SKILL.md` 仅 **1834 字节 / 29 行**（约 0.5k token）；规则文件**按阶段**才读 |

---

## 1. 来源与适用范围 / Origin and Scope

**中文**

本 skill 不是凭空设计的规则集，而是从一系列 **GPT 系列大模型**（包括 **GPT-5.6 Sol** 与 **GPT-6 Astra**）在真实交付任务中的长期使用过程里**观察、提炼**出来的。

我们把这些模型在规划与验收环节反复表现出的有益特点——**先想清楚再动手、交付时给出可复现的验证、没验过的地方主动标注**——保留并固化成一份纪律文本。

因此，它**不是**某个模型的专用配件：提炼的是**行为特征**，不是模型能力。任何具备指令遵循能力的大模型都可以加载它。名字里的 "GPT-Series" 记录的是它的**来源**，不是它的**适用范围**。

**English**

This skill is not an invented rule set. It was **observed and distilled** from long-term, hands-on use of a series of **GPT-series models** — including **GPT-5.6 Sol** and **GPT-6 Astra** — on real delivery tasks.

We kept and froze the habits these models showed at their best during planning and acceptance: **think it through before acting, ship reproducible verification, and flag what you could not verify**.

It is therefore **not** a model-specific add-on. What is distilled is **behavioral patterns**, not model capabilities — any instruction-following LLM can load it. "GPT-Series" in the name records its **origin**, not its **scope**.

---

## 2. 为什么不是"把 GPT 的行为规则全搬过来" / Why Not Copy Every Rule

**中文**

大量 A/B 对照实验反复证明了一件事：**把 GPT 自身的行为特点写成规则、塞进使用者的执行过程，结果适得其反**。你无法靠堆砌规则，让使用者复现 GPT 那样的产出质量。

实测中规则越多并不等于越好：把纪律硬指标化后，评分**并未提升**（与原则引导的差异落在判分误差内，判定为等效）；更极端的 v1.2.5 重版本（179 行、77 条自检）则被实验直接证伪并废弃。执行者记不住繁复步骤、模板填不满，最后流于形式应付。

> **版本注**：上述对比来自 **v1.2.x 旧版本**（v1.2.2 / v1.2.3-draft / v1.2.5）。v1.4.x 极简版起已删除硬指标化与繁复条款，现行 **1.5.0 不再适用该对比**。

所以我们只做两件事：

1. **抽取少数真正可遵守的特性**（真打开看一眼、未验证标注、全绿不算证据等）；
2. 配上**独特的遗忘机制**（即文件级渐进加载：执行阶段规则不在上下文，交付时从文件读入；任务结束后主动遗忘规则内容）。

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

> **Version note**: the comparison above comes from **older v1.2.x builds**. Hard metrics and bulky clauses were removed in the v1.4.x minimal line, so it **no longer applies to the current 1.5.0**.

So we do only two things:

1. **Extract a few traits that can actually be followed** (really open it, mark what is unverified, all-green is not evidence, etc.);
2. Pair them with a **distinctive forgetting mechanism** (file-level progressive loading: the rules are absent from context during execution, loaded from file at delivery, and actively forgotten after the task ends).

Users therefore **get the upside only** — more trustworthy deliveries, defects caught by actually opening the artifact, counter-example verification rising from roughly one-third to near-full coverage, unverified items listed one by one — **while avoiding the downside**: no ever-present discipline taxing attention, interrupting thought, or burning context; no regression from rule pile-up; no slide into checkbox-theatre.

---

## 3. 核心机制：文件级渐进加载实现「纪律—心流五阶段时序隔离」

**首创性**：据我们所知，这是首个在**单一 Skill 内**、通过**文件级渐进加载**实现"纪律—心流五阶段时序隔离"的设计。

### 3.1 物理布局：规则与流程是分开的文件

规则**不是**提示词里的一段话，而是**独立的物理文件**：

| 文件 | 字节 | 内容 | 何时进入上下文 |
|---|---|---|---|
| `SKILL.md` | 1834 | 只有五阶段流程表 + 各阶段指针 + 边界 + 加载说明 | **始终在场**（常驻层） |
| `references/plan-rules.md` | 2321 | 阶段2 规划规则 | **仅阶段2** |
| `references/review-rules.md` | 2547 | 阶段5 八条纪律 | **仅阶段5** |
| `references/multi-agent.md` | 2273 | 形态二三细则 | **仅叠加形态二三时** |

常驻层里**没有任何规则条文**——只有"有五个阶段，到哪个阶段读哪个文件"。

### 3.2 五阶段时序

| # | 阶段 | 规则状态 | 做什么 | 退出条件 |
|---|---|---|---|---|
| 1 | **自由构想** | 规则缺席 | 凭自己的判断力想清楚要做什么 | 能一句话说清接下来做什么 |
| 2 | **规则规划** | **读 `plan-rules.md`** | 把构想落成计划，**完整保留**阶段1构想 | 方案已确认、风险已分级、无需再问 |
| 3 | **执行** | 规则退场 | 凭自己的能力去做，不打断思路 | 觉得可以了，没有正在调的问题 |
| 4 | **直觉检查** | 规则缺席 | 凭常识快速扫一遍交付物 | 没有"等等，这里好像有问题"的卡住感 |
| 5 | **纪律检查** | **读 `review-rules.md`** | 严格逐条过纪律 | 见 §5.2 退出条件 |

状态序列：**无规则 → 有规则 → 无规则 → 无规则 → 有规则**

**任务结束后**：彻底忘记三个规则文件的具体内容，只记住"有五个阶段，到哪个阶段读哪个文件"——下次需要时再读。

**设计意图**两条：

1. **创作时没有纪律**——阶段1与整个执行阶段规则缺席，不污染思路、不打断心流；
2. **检查有两道**——直觉抓规则**没覆盖到**的问题，纪律确保规则**覆盖到**的都做到，互不替代。

**两头吃**：**阶段3** 既不丢失原本的创作能力，又已获得 skill 给予的规划能力（阶段2 成果在手、规则文本退场）——零副作用；**阶段4** 不加载纪律规则，使用者自己的找问题能力不被清单框住，而前一阶段注入的审查能力仍在发挥作用——直觉的广度与纪律的敏感度同时在线。

**结果是两个「零」**：**执行期零干扰**（规则退场，心流不断）+ **验收期零妥协**（八条逐条过，一条不少）→ **交付可信度显著提升**。

---

## 4. 触发条件 / Triggers

| 类型 | 信号 |
|---|---|
| **自动触发**（`description`） | 任务涉及**数字验算、代码交付、多 Agent 协作、需要防假完成**；用户说"**做完了帮我查 / 看看对不对 / 验收**"、**派发子任务或多个 AI 分工** |
| **显式触发** | "使用 gpt-series-reasoning-style 执行本次任务。" |
| **不触发** | 一句话问答、纯聊天、小且可逆的改动——纪律不该出现在不需要它的地方 |

---

## 5. 阶段规则详解

### 5.1 阶段2：规划规则（`plan-rules.md`）

| 动作 | 内容 |
|---|---|
| **保留阶段1构想** | 阶段1想到的一切——方案思路、技术选型、可能的坑——**全部带入阶段2，不清空重来** |
| **形态判断** | 心里做，**不输出思考过程**，直接干活 |
| **协作形态叠加** | 形态一/二/三可分部分叠加（见 §5.3）；**形态三命中后先与用户确认** |
| **轻量档** | 只做方案、不实际派发时，不建 `_agents/` 目录、不写任务包文件 |
| **小任务直通** | 小且可逆 = 指令即授权。只有**不可逆、对外发布、删东西**才事前确认 |
| **风险分级** | 轻任务只做审查 3 条（★）；重任务做全 **8** 条 |
| **动手前调研** | 重任务先花几分钟上网查做法、坑、最佳实践 |
| **确认档位** | **A 档（默认）**：一次性列推荐方案。**B 档**：用户主动要求时才用，一次只问一个最高影响问题。**不需要专门问"你要 A 还是 B"** |
| **退出条件** | 方案已确认 + 风险已分级 + 无需再问任何问题 |

### 5.2 阶段5：八条纪律（`review-rules.md`）

| # | 纪律 | 具体要求 | 轻任务 |
|---|---|---|---|
| 1★ | **真打开看一眼** | 产物在真实环境打开、真用一遍。HTML 要在浏览器渲染、API 要用前端调、文档要在阅读器打开——**跑脚本不算真打开**。环境不支持时：如实标"未验证：浏览器渲染"+ 给用户自验步骤 | 必做 |
| 2★ | **未验证标注** | 未验过的结论标「未验证」，写明哪步没法验。交付只说三件：做了什么 / 怎么验的（给可复现命令）/ 哪些没验。未验项逐条写 ①XX——原因是XX；**不许只写"部分未验证"**；且必须在交付物里用**星号或加粗醒目标出**，不许藏在段落中间 | 必做 |
| 3 | **交付声明对得上** | 你说"做了 X 功能"，产物里就**真的有 X**。交付前最后一次**回读自己的交付声明**，逐项在产物里找位置；指不到的，要么补做，要么改成"未完成 + 原因" | — |
| 4 | **失败两次换路** | 同一动作连续失败第 2 次，禁止同法第 3 次；先判断是否与已验路径等价，等价就改代码审查，别死磕 | — |
| 5 | **全绿不算证据** | 交付前把要防的错误**故意做一次**，断言变红才算验过。变异后仍全绿 = 变异没生效。最小菜谱：每个写入口至少打 **空值 / 超长 / 非法类型 / 缺键** | — |
| 6 | **关键数字重算** | 数据/研究类交付的关键数字，用独立方法重算或双源交叉验证；对不上以**重算为准** | — |
| 7 | **临时物隔离** | 临时文件不进交付目录、收尾清掉；清理只动本任务自己的目录，**禁全局杀进程** | — |
| 8★ | **防死循环** | 同一文件连续读 3 次无新信息就停；同一动作连续做 3 次输出相同就换思路 | 必做 |

**阶段5 退出条件**：①该风险等级对应的规则都过一遍（轻 3 / 重 8）；②能说出三件套；③没有未处理的"这里好像有问题"。

### 5.3 三形态协作（可叠加，非三选一）

| 形态 | 何时使用 | 关键约束 |
|---|---|---|
| **形态一 · 单智能体** | **默认** | — |
| **形态二 · 子智能体** | **明显增益就自觉开**：独立子活 / 并行两件以上 / 独立挑刺视角 / 怕污染主上下文 | 用 `create_agent` 派，给清三样：**目标 / 完成标准 / 交回给谁**。交回后**主 Agent 仍是 DRI**；子智能体不直接对用户；一个人能干完的不开二 |
| **形态三 · 多智能体** | **命中任一就考虑，先与用户确认**：用户指名 / 让另一个 AI 干 / 任务大到分工 / 跨模型——因要建 `_agents/`、写任务包，有外部副作用 | 六步：指挥官声明 → 建角色档案 → 写任务包 → **用户转述**派发 → 对照原始目标验收 → 汇报三件套。**任务包七要素**：背景 / 已定决策 / 未定缺口 / 完成标准 / 允许与禁止范围 / 唯一 DRI / 交回给谁。三张角色卡在 `templates/` |

**红线**：执行者说「我做完了」不算验收；审查者不亲自改；不绕开指挥官直接汇报。

### 5.4 加载证明协议

被要求证明已加载时，输出：①版本号；②五阶段时序（自由构想 → 规则规划 → 执行 → 直觉检查 → 纪律检查）；③**逐字引用**纪律第 1 条；④协作形态说明；⑤实际读过的文件清单。读不到 `SKILL.md` 或 `VERSION` 时**不伪造**，停止并请求只读权限。

### 5.5 交付物格式（"三件套"）

```text
做了什么：……
怎么验的：……（可复现命令）
哪些没验：①XX——原因是XX；②XX——原因是XX
```

一眼就知道哪些话能信、哪些还得自己再验。

---

## 6. 运行限制与边界

| 限制 | 说明 |
|---|---|
| **"想清楚了"无判据** | 阶段1 的出口条件无法机械判定，可被形式化应付 |
| **意图引导不可外部验证** | 阶段1 / 阶段4 的效果只能靠软维度盲评或使用体感判断；但**规则不在场**本身是可验证的物理事实（规则在独立文件里，按需读入） |
| **规则只覆盖已知失败模式** | 有限文本无法穷举无限缺陷——结构性上限，非缺陷 |
| **边界条款** | 只改完成任务必须改的地方；发现会让交付物坏着交的问题顺手修掉，**其余不碰** |

---

## 7. 外部依赖与安全模型

| 项 | 要求 |
|---|---|
| 宿主 | 目录型（Claude Code / WorkBuddy 等，读 `SKILL.md`）或 `AGENTS.md` 型（Codex / Gemini CLI / Copilot CLI 等） |
| 网络 | **不需要**（唯一例外：阶段2"动手前调研"建议联网，非强制） |
| 代码执行 | **不需要**（skill 本体零代码） |
| 第三方库 | **无** |

安全模型：运行时面**纯文本**，加载全程不运行代码、不发起网络请求、不上报数据；唯一脚本 `selfcheck.py` 只读仓库内文件、无网络、无 `shell=True`。详见 `SECURITY.md`。

---

## 8. 安装与验证

```bash
# 目录型运行时（Claude Code / WorkBuddy 等）
git clone https://github.com/JadeYingWah/gpt-series-reasoning-style
cp -r gpt-series-reasoning-style ~/.claude/skills/     # WorkBuddy 用 ~/.workbuddy/skills/

# AGENTS.md 型运行时（Codex / Gemini CLI / Copilot CLI 等）
cd gpt-series-reasoning-style    # 仓库目录内启动，入口路由自动生效
```

**功能验证**：问 agent「你的版本号是多少？加载证明需要哪几个文件？」——应答 `1.5.0`，说得出五阶段时序，并能逐字引用纪律第 1 条。

**仓库自检**：

```bash
python scripts/selfcheck.py    # 24 项静态检查；退出码 0=全过 / 1=有失败
```

---

## 9. 文件清单

| 文件 | 字节 | 角色 |
|---|---|---|
| `SKILL.md` | 1834 | **规则权威与五阶段流程表**（29 行）。运行时只加载它 + `VERSION` |
| `VERSION` | 5 | 版本号（`1.5.0`） |
| `references/plan-rules.md` | 2321 | 阶段2 规划规则（保留构想 / 形态叠加 / 风险分级 / 档位 / 退出条件） |
| `references/review-rules.md` | 2547 | 阶段5 审查规则：**八条纪律** + 退出条件 |
| `references/multi-agent.md` | 2273 | 形态二三细则：命中信号、派发规范、六步操作、红线 |
| `AGENTS.md` | 2697 | 跨运行时入口路由（Codex / Gemini CLI 等），仅指路无规则 |
| `templates/commander.md` | 1034 | 指挥官角色卡 |
| `templates/executor.md` | 810 | 执行者角色卡 |
| `templates/reviewer.md` | 795 | 审查者角色卡 |
| `scripts/selfcheck.py` | 4045 | 仓库一致性自检（24 项，纯只读，已适配文件级渐进加载结构） |
| `README.md` | 28633 | 面向使用者的介绍（中英双语） |
| `REFERENCE.md` | 21845 | **本说明书**（完整版） |
| `SECURITY.md` | 2488 | 安全模型说明 |
| `social-preview.svg` / `.png` | 7868 / 361993 | 仓库横幅（1280×640）：三阶段卡片 + RULES OFF/ON 盾牌图标 |
| `LICENSE` | 1068 | MIT |
| `.gitattributes` / `.gitignore` | 257 / 351 | 仓库配置 |

---

## 10. 实测证据

实验素材与统计脚本在 [`experiments` 分支](https://github.com/JadeYingWah/gpt-series-reasoning-style/tree/experiments)。

### 10.1 素材规模（口径见 §10.2）

| 来源 | 实验批次 | 臂次 | 文件 |
|---|---|---|---|
| v1.2.x（历史） | 32 | 225 | 2880 |
| desktop-beds-2026-09 | 8 | 35 | 127 |
| test-bed1~4 | 13 | 26 | 163 |
| collected-from-workbuddy | — | — | 47 |
| **合计** | **53** | **286** | **3217** |

复跑：`python experiments/stats-experiments.py`

**局限**：臂目录命名跨批次不统一（`arm-A-skill` / `Skills_Yes` / `A-skill`），正则尽力覆盖，**「臂次」是下限值，不会高估**；按"臂/子目录数（含嵌套）"的更宽口径约 328——两种口径都对，引用须注明。

### 10.2 可引用的硬数字

| 结论 | 数字 | 来源 | 适用版本 |
|---|---|---|---|
| 软维度（质量/纪律评分）提升 | **+20~24** | P1-5 | v1.2.x 历史 |
| 反例验证执行率 | **带 skill 100% vs 无 skill 33%** | P1-1 终报 | v1.2.x 历史 |
| 自我校准缺口率 | **无 skill 100% → 带 skill 约 33%** | P1-2 | v1.2.x 历史 |
| 交付可信度（非代码质量）提升 | 所有实验一致 | Test-Bed 1 | **现行有效** |
| "真打开看一眼"抓到代码审查抓不到的缺陷 | 视觉类缺陷 | Test-Bed 3 / 4 | **现行有效** |
| 判定台可信度 | T6/T7/T8 三套通过"变异全灭 + GOLD 零误杀 + 反向自查" | P1-7 终报 | v1.2.x 历史 |
| 自检可信度 | **24/24** 通过；3 个注入变异**全部被杀** | 2026-09-17 实测 | **现行有效** |

> **1.5.0 的评分实验尚未进行**——上表数字均为历史实验（v1.2.x / v1.4.x 时代）所得，待最新评分实验完成后更新。

---

## 11. 已知边界

> **版本适用性**：标〔**旧版**〕的条目测于 v1.2.x（v1.2.2 / v1.2.3-draft / v1.2.5），v1.4.x 极简版起已删除硬指标化与繁复条款，**现行 1.5.0 不再适用**；未标注者为现行版本仍需知悉的边界。

- **不兜底**〔**旧版** v1.2.2 / v1.2.5〕——n=2 对照实验显示：致命缺陷率维度上带 skill 与不带 skill 未拉开可辨差距，held-out 上甚至略差。反向结果也放在仓库里。**v1.4.x 起不再适用**。防线靠证据与独立复验，不靠条款。
- **不提升代码质量**——代码本体差别不大，变好的是**交付可信度**。
- **不是加速器**——验证习惯占约三到四成时间预算，换"敢直接用"的交付。**要最快出活，这个 skill 不适合你。**
- **对创意产物部分条款偏重**——七条时代实测有 2–3 条对纯视觉/创意产物没有落点（如变异测试、数字重算）；现行八条未重新实测，建议仍走轻量档。
- **加条款不等于更好**〔**旧版** v1.2.2 / v1.2.3-draft〕——受控对照显示硬指标化后评分**并未提升**（原则引导 58.17 vs 硬指标 57.00，+1.17 落在判分误差内，判定**等效**），故不实施；更重的 v1.2.5 被实验证伪并废弃。
- **Test-Bed 4 设计有污染**——B 臂执行者此前加载过旧版 skill，其结论不作为有效性证据。
- **自报 ≠ 验证**——14 个实验臂全部自报"全过"，oracle 仍判出大量 fatal。这个 gap 既是本 skill 存在的理由，也是它的天花板：**它降低"假完成"，不能保证"真完成"**。

---

## 12. 设计哲学

- **规则越少越好，但核心那几条不能少**；
- **创作是创作，检查是检查**——文件级渐进加载的全部理由；
- **证据高于声称**——全绿不算证据，断言红过才算验过；
- **责任不随委派转移**——子智能体交回后，主 Agent 仍是 DRI。

---

## 附：快速上手

```text
1. 装好（§8：目录型拷文件夹 / AGENTS.md 型 cd 进目录）
2. 验证生效：问「你的版本号是多少？加载证明需要哪几个文件？」
3. 正常派活——无需特殊指令，交付型任务自动进入五阶段时序
4. 检查交付消息是否自带三件套：做了什么 / 怎么验的 / 哪些没验
5. 创意/纯视觉任务留意轻量档（§5.1）
```

**版本策略**：

- **v1.4.x 极简线 → v1.5.0 文件级渐进加载**——五阶段时序、规则与流程物理分离、按阶段读入。**当前主线**。
- **v1.2.x 重版线**——179 行、模块矩阵、self-test 冻结 77 条。**已被实验证伪，该线已废弃**。

---

*MIT License · 本说明书对应版本 1.5.0*
