[English](boyue-methodology.md) | 简体中文

# 从实现稀缺到实现丰裕：AI 软件工程中的决策边界与复杂度治理

## ——“博约开发法”的概念框架、实践机制与研究命题

**作者 / 发布方：** 吾爱分享网（Wuaishare）  
**项目：** Boyue · 博约开发法  
**原始方法论文章：** https://www.wuaishare.cn/12793.html  
**GitHub：** https://github.com/wuaishare/boyue  
**文档性质：** Conceptual Working Paper / 概念型工作论文

> **博观而约取，厚积而薄发。**  
> ——苏轼《稼说送张琥》

---

## 摘要

生成式人工智能与 Coding Agent 正在改变软件开发的成本结构。传统软件工程长期受到“实现稀缺”的约束：想法、需求和候选方案往往多于组织能够设计、编码、测试、部署和维护的数量，因此工程容量本身客观上构成了一道筛选机制。随着 Agentic Coding 能够阅读代码库、生成方案、修改文件、运行命令、执行测试并形成可审查的软件变更，候选方案、原型与候选实现的边际生成成本正在下降。

然而，候选实现更容易产生，并不意味着评估、验证、集成、安全、迁移、兼容、运维以及长期维护成本以同样速度下降。AIDev 数据集已收集 932,791 个由 Codex、Devin、GitHub Copilot、Cursor 与 Claude Code 等 Coding Agents 创建的 Agentic Pull Requests，覆盖 116,211 个 GitHub 仓库，表明 Agent 参与真实软件变更已形成相当规模。与此同时，METR 针对熟悉成熟开源代码库的资深开发者进行的 2025 年随机对照实验观察到，当时前沿 AI 工具使特定任务平均耗时增加 19%；到 2026 年，METR 又指出较新工具很可能已经带来更高加速，但研究遭遇显著选择偏差，难以可靠估计统一的 speedup。DORA 2025 则把 AI 描述为组织能力的“放大器”：成熟的工程体系能够放大收益，而薄弱的用户导向、平台和交付能力同样可能被 AI 放大。

本文据此提出 **Implementation Abundance（实现丰裕）** 作为分析 AI 软件开发的一种概念视角：当组织生成候选方案和候选实现的能力显著超过其判断、验证、整合以及长期拥有这些实现的能力时，软件开发的约束将部分从“能否实现”迁移到“什么值得承诺、什么值得长期拥有以及如何控制复杂度增长”。

本文进一步提出两道关键决策边界：**Commitment Boundary（承诺边界）**区分 `Could Build` 与 `Should Invest`；**Ownership Boundary（所有权边界）**区分 `Should Build` 与 `Should Own`。在 Double Diamond、Set-Based Concurrent Engineering、Shape Up、YAGNI、Working Backwards、小批量交付等既有思想基础上，本文借用“博观而约取，厚积而薄发”作为命名与启发式框架，形成 **BYHB Loop**：Explore（博观）、Select（约取）、Shape（厚积）、Deliver（薄发），并以 Evidence / Retirement 构成持续反馈。

其核心主张可以概括为：

> **博观管理可能性，约取管理承诺；厚积管理不确定性，薄发管理复杂度。**

本文不把 BYHB 视为新的线性项目管理流程，而将其定位为面向 AI 实现丰裕环境的轻量级决策与复杂度治理框架；并进一步给出 Commitment / Ownership 两道边界、风险自适应塑形、最小完整价值切片、退役审查等操作机制，以及四项可供后续实证研究检验的研究命题。

**关键词：** AI Coding Agent；Agentic Coding；软件工程；Implementation Abundance；产品开发；决策治理；复杂度治理；Commitment Boundary；Ownership Boundary

---

## 1. 引言

### 1.1 软件开发长期建立在“实现很贵”这一前提上

传统软件开发存在一个长期而稳定的经济约束：**从想法到生产系统的距离很长。**

一个功能通常需要经过问题理解、需求澄清、产品设计、交互设计、技术方案、编码、测试、代码审查、部署、监控与长期维护。即使组织拥有大量想法，也只有一部分能够真正获得工程资源并进入生产环境。

因此，有限的 Engineering Capacity 虽然并不是理想的产品决策机制，却客观上构成了一道天然过滤器。当一个功能需要数周工程投入时，团队通常不得不认真回答：

- 用户真的需要它吗？
- 它和核心产品方向一致吗？
- 是否存在更简单的方案？
- 现在值得做，还是应该延后？
- 新增的长期维护责任是否值得？

这一筛选并不总是高质量，但“昂贵的实现”至少制造了必要摩擦。

### 1.2 Agentic Coding 正在压缩从想法到候选实现的距离

新一代 Coding Agent 不再局限于单行补全。它们能够读取 Repository、规划任务、修改多个文件、调用工具、运行测试并形成 Pull Request。AIDev 对真实 GitHub 活动的研究已经识别出近百万个 Agentic Pull Requests，这意味着 AI 产生的软件变更已经不是边缘实验，而正在成为真实软件工程活动的一部分 [1]。

这会产生一种过去不常见的开发体验：

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

过去需要数天甚至数周才能获得的候选实现，现在可能在几个小时甚至更短时间内出现。

这种能力显然具有巨大价值，但也可能带来新的误判：

> “既然代码已经写出来了，为什么不顺便合进去？”

问题在于，**生成成本和所有权成本是两个完全不同的概念。**

### 1.3 Implementation Cost ≠ Ownership Cost

一个功能被 AI Agent 快速实现，并不意味着它在组织生命周期中是“便宜”的。

进入生产系统以后，它可能持续增加：

- 测试表面积；
- UI 与状态空间；
- Public API 与兼容义务；
- 数据与迁移责任；
- 权限、安全与审计边界；
- 监控与运维负担；
- 文档与用户支持；
- 第三方依赖与升级成本；
- 后续修改所需的认知上下文。

因此：

> **Implementation Cost ≠ Ownership Cost**

AI 首先大幅降低的是“产生一个候选实现”的边际成本，而不是自动消除“长期拥有这个实现”的成本。

本文的中心问题由此产生：

> **当低成本候选实现能够被大量、快速地产生时，软件团队如何防止这些可能性过早转化为昂贵的长期系统义务？**

---

## 2. 相关工作与理论基础

BYHB 并不主张发散、收敛、延迟决策、范围控制或小步交付是全新的思想。相反，它建立在多套成熟方法之上，其尝试贡献是：**在 AI Implementation Abundance 的情境下，以“承诺”和“长期所有权”为中心重新组织这些思想。**

### 2.1 Double Diamond：发散与收敛

Design Council 的 Double Diamond 将创新过程概括为 Discover、Define、Develop、Deliver，并以两个菱形表达发散与收敛的关系。其核心意义在于：不要过早假设问题和解决方案，而应先扩大理解，再逐渐聚焦 [2]。

Double Diamond 为 BYHB 的“博观—约取”提供了直接的设计思维基础。但 BYHB 进一步关心一个 AI 时代更突出的治理问题：**发散出来的候选方案能够被迅速转成代码时，如何防止 Option 自动膨胀成 Commitment 与 Ownership？**

### 2.2 Set-Based Concurrent Engineering：延迟承诺与方案集合

Sobek、Ward 与 Liker 对 Toyota 产品开发体系的研究指出，Set-Based Concurrent Engineering 并不要求团队很早锁定一个单点方案，而是广泛考虑多个可能解，并随着信息增加逐渐淘汰较弱方案，最终收敛 [3]。

这一思想直接支持 BYHB 的核心区分：

> **Option ≠ Commitment**

保留一个 Option 并不意味着现在就投入资源。`DEFER` 因而不是失败或优柔寡断，而可以是一种有意识的“保留期权”。

### 2.3 Shape Up：Shaping、Appetite、Rabbit Holes 与 No-Gos

Basecamp 的 Shape Up 明确区分 Raw Idea 与 Shaped Work。Shaping 的目标不是把所有细节提前设计完，而是让工作保持 rough、solved、bounded：关键问题被解决，边界被定义，同时仍给实施团队留下判断空间 [4]。Shape Up 还使用 Appetite 限制投入，通过 Rabbit Holes 与 No-Gos 暴露风险并主动排除不必要范围 [5]。

这与 BYHB 的“厚积”高度一致，但 BYHB 进一步采用 **Risk-Adaptive Shaping**：并非所有任务都需要同等深度的前置塑形，塑形强度应与错误后果和不可逆性相匹配。

### 2.4 YAGNI：不要为假想未来提前增加复杂度

Martin Fowler 对 YAGNI 的总结强调：未来“可能需要”的能力，不应该仅仅因为这种可能性就被现在实现；否则会为当前软件增加尚未产生价值的复杂度 [6]。

AI Coding 使 YAGNI 的意义更加突出。过去提前实现一个假想需求可能需要数天，因此成本会自然抑制冲动；当 Agent 能在很短时间内完成时，“顺便做掉”变得更有诱惑力，但长期所有权成本并未因此消失。

### 2.5 Working Backwards / PRFAQ：先回答用户价值，再回答如何实现

AWS 的 DevOps 与产品开发指导将 Amazon Working Backwards 描述为从客户价值与理想用户体验出发，通过 Press Release / FAQ 明确范围、客户价值和业务结果，再反推实现路径 [7][8]。

这可以直接映射到 Commitment Boundary：在 AI 非常擅长回答“怎么实现”的时代，团队更需要在承诺前先回答“为什么它应该存在”。

### 2.6 AI 软件开发生产率研究：结果正在快速变化

关于 AI 是否整体提高开发生产率，现有研究并没有一个可以简单外推到所有场景的统一数字。

METR 在 2025 年对 16 名熟悉自身成熟开源项目的开发者进行随机对照实验，共涉及 246 个真实任务，观察到当时前沿 AI 工具使任务平均耗时增加 19% [9]。到 2026 年，METR 又指出新实验受到严重选择偏差：开发者越来越不愿执行“禁止使用 AI”的任务，并可能主动避开 AI 特别擅长的任务；研究者认为更晚期工具很可能带来更明显的正向加速，但现有数据不足以可靠量化统一幅度 [10]。

DORA 2025 则从组织层面提出更结构化的解释：AI 的主要作用是“放大器”，放大高绩效组织的优势，也放大薄弱组织的混乱 [11]。其 User-Centric Focus 研究进一步指出，在缺乏用户价值导向时，AI 的代码生成能力可能让团队更快进入 Feature Factory——产出更多功能，但没有对应的用户价值 [12]。

这些研究共同支持本文采取一种更谨慎的研究问题：与其假设“AI 使整个软件工程统一变便宜”，不如研究**AI 是否首先创造了候选生成能力与组织治理能力之间的新不对称。**

---

## 3. 实现丰裕：一个概念性分析视角

### 3.1 定义

本文将 **Implementation Abundance（实现丰裕）** 定义为：

> **软件组织生成候选方案与候选实现的边际能力，显著超过其评估、验证、整合以及可持续长期拥有这些实现的组织能力的一种开发状态。**

这里有三个限定。

第一，讨论的是 **candidate implementations**，而不是断言 production software 已经廉价。

第二，实现丰裕是相对状态，而非一个固定阈值。不同团队、代码库、产品与风险等级可能表现完全不同。

第三，实现丰裕不等于生产率必然提高。候选生成能力扩大以后，Review、Verification、Integration 和 Ownership 可能成为新的瓶颈。

### 3.2 从实现稀缺到实现丰裕

传统环境可以粗略描述为：

```text
Ideas / Requirements
        >
Engineering Capacity
```

大量想法因为资源不足而从未成为正式实现。

AI 环境则越来越可能出现：

```text
Candidate Generation Capacity
        >
Judgment + Verification + Integration + Ownership Capacity
```

问题从“做不完所有想法”，逐渐增加了另一层：

> **能做出来的东西，比真正值得长期拥有的东西更多。**

### 3.3 Boundary Compression

本文把 Option、Commitment 与 Implementation 之间原本由时间和工程成本形成的距离缩短称为 **Boundary Compression（边界压缩）**。

```text
传统：Idea ───── Research ───── Design ───── Engineering ───── Production

AI：  Idea ─ Agent ─ Prototype ─ PR
```

Boundary Compression 本身是效率提升，并非风险。风险产生于：**当生成速度改变，而承诺与所有权治理机制没有改变时。**

这种情况下可能出现：

- **Premature Commitment**：因为原型已经存在，就过早把候选项当作 Roadmap 承诺；
- **Premature Ownership**：因为代码已经存在，就过早把它纳入长期生产系统。

---

## 4. 两道关键边界

### 4.1 Commitment Boundary：从 Could Build 到 Should Invest

Commitment Boundary 回答的是：

> **这个 Option 是否值得组织投入更多注意力、时间和资源？**

在 AI 环境中，以下内容首先都只是 Option：

- 一次 Brainstorm 产生的 Feature；
- 竞品已有的能力；
- GitHub 上流行的新架构；
- Agent 自动写出的 Prototype；
- 一次能跑通的 Demo；
- 一段已经通过测试的 Patch。

它们并不因为“已经能做”而自动获得产品优先级。

因此，BYHB 使用三态 Commitment Decision：

- **COMMIT**：已有足够证据，现在值得进一步投入；
- **DEFER**：仍具有 Option Value，但当前证据、时机或前置条件不足；
- **DISCARD**：已有足够证据表明不值得继续投入。

对 `DEFER`，应尽量记录 **Revisit Trigger**，例如：

> 当三个独立付费客户主动提出相同工作流需求时重新评估。

这样可以避免“以后再说”演变为无限膨胀的 Backlog。

### 4.2 Ownership Boundary：从 Should Build 到 Should Own

通过 Commitment Boundary 并不意味着必须进入 Production。

Ownership Boundary 回答：

> **如果这项能力未来需要长期维护，我们仍然愿意让它成为系统永久表面积的一部分吗？**

这是 BYHB 最关键的区分之一：

> **Implementation ≠ Ownership**

进入生产环境意味着组织开始拥有：

- API 兼容责任；
- 数据迁移责任；
- 安全与权限责任；
- 用户工作流与学习成本；
- 配置状态与测试矩阵；
- 服务、依赖与运维拓扑；
- 文档和支持承诺。

因此，一个非常实用的 Ownership Gate 是：

> **如果未来三年都必须维护它，我们今天仍然会选择加入吗？**

这不是字面要求所有产品存在三年，而是用长期视角迫使团队把一次性生成成本与持续所有权成本分离。

---

## 5. BYHB Loop：四种工作模式，而非四个线性阶段

BYHB 将“博观、约取、厚积、薄发”解释为四种可并行存在的 Operating Modes，而不是新的 Waterfall。

| 模式 | 管理对象 | 目标 | 典型行为 |
|---|---|---|---|
| **Explore / 博观** | Option Space | 降低认知盲区 | 用户研究、竞品研究、技术探索、Spike |
| **Select / 约取** | Commitment | 降低错误承诺 | Commit / Defer / Discard、PRFAQ、Non-goals |
| **Shape / 厚积** | Uncertainty | 降低高代价不确定性 | PoC、Prototype、ADR、Benchmark、Rehearsal |
| **Deliver / 薄发** | Ownership Growth | 控制新增长期复杂度 | MCVS、Vertical Slice、Feature Flag |
| **Evidence / Retirement** | Existing Ownership | 重新验证复杂度是否值得存在 | Usage Evidence、Simplification、Retirement Review |

真实项目可以同时存在多个 Mode：一个 Feature 正在 Deliver，一个 Public API 正在 Shape，未来方向仍在 Explore，而旧模块正在 Retirement Review。

### 5.1 博观：扩大认知，不扩大承诺

博观允许积极利用 AI 的生成能力。团队可以一次产生多个设计、多个技术路线甚至多个 Prototype。

但需要明确：

> **AI 产生的候选项是 hypotheses，不是 backlog obligations。**

博观的停止条件不是“看完所有资料”，而是当新增信息已经很少改变用户问题、核心风险、候选类别与主要决策时，应停止继续发散。

### 5.2 约取：管理 Commitment，而不是追求删除数量

约取的质量不能通过“删掉多少百分比”衡量。

真正目标是：

> **让更多错误的东西在成为正式承诺之前消失或延后。**

PRFAQ、Non-goals、Evidence Log 与 Decision Record 都可以作为 Select 的工具，但它们不是强制仪式。简单、低风险任务不应产生不必要流程负担。

### 5.3 厚积：Shape according to the cost of being wrong

厚积不是“大设计在前”。它的原则是：

> **错误越昂贵、越难逆转，越值得在 Ownership 前投入更多验证。**

按钮间距和文案高度可逆，不值得长时间讨论；Public API、Auth、Billing、Permission Model、Core Schema、不可逆数据迁移则不同。

因此，厚积的产物不以“文档数量”衡量，而以关键不确定性是否被证据降低来衡量。

### 5.4 薄发：Deliver the smallest coherent change worth owning

薄发不是“做得残缺”，而是控制一次进入长期系统的变更面。

本文使用 **Minimum Coherent Value Slice（MCVS，最小完整价值切片）**：

> 一个能够完成真实用户价值闭环，同时将新增长期系统表面积控制在最小合理范围内的交付单元。

一个 MCVS 应具备与其风险匹配的必要 UI、数据、权限、错误处理、可观测性以及回滚或禁用能力。

> **薄，是变更面薄，不是质量薄。**

工程上，Vertical Slice、Walking Skeleton、Tracer Bullet 与 small batches 都可以成为实现 MCVS 的具体手段，而 MCVS 本身并不试图替代这些既有实践。

---

## 6. 原型与所有权：AI 时代最重要的分离之一

AI Coding 的一个巨大优势是：**试验代码变得非常便宜。**

BYHB 并不主张因为担心复杂度而减少实验。恰恰相反：

> **Prototype freely; own selectively.**

一个高度不确定的 AI 能力，可以尽早通过 Disposable Spike 验证：

```text
Unknown capability
        ↓
Disposable Spike / PoC
        ↓
Evidence
        ↓
Commit / Defer / Discard
```

而不是：

```text
Unknown capability
        ↓
Production architecture
```

这解决了“厚积会不会导致 Analysis Paralysis”的核心矛盾：

> **鼓励尽早实验，反对过早拥有。**

对 AI 功能而言，Spike 可以验证：

- 任务能力是否稳定；
- 结构化输出失败率；
- 长上下文退化；
- RAG 召回与噪声；
- 延迟与推理成本；
- Failure Modes；
- 传统规则系统是否反而更简单可靠。

AI 本身也只是一个 Option，而不是用户价值。

---

## 7. 五道 Decision Gates

为了避免 BYHB 退化为抽象口号，可以将其压缩成五个问题。它们不是五场审批会议，而是按风险轻量使用的判断点。

### G1 — Exploration Gate

> **继续增加研究或实验，还会显著改变当前判断吗？**

若会，则继续 Explore；若新增信息的边际决策价值已经很低，则停止发散。

### G2 — Commitment Gate

> **当前证据是否足以让这个 Option 获得进一步投入？**

结果：`COMMIT / DEFER / DISCARD`。

### G3 — Risk Gate

> **如果这个判断错了，后果有多严重？有多难撤销？**

这一问题决定 Shaping 深度。

### G4 — Ownership Gate

> **这项复杂度值得我们长期拥有吗？**

结果可以是：`OWN / REDUCE / REJECT`。

### G5 — Evidence Gate

> **上线后的真实证据仍然支持原始判断吗？**

结果可以是：`EXPAND / MAINTAIN / MODIFY / RETIRE`。

这五个 Gate 应遵循同一个元原则：

> **治理成本必须与错误成本匹配。**

---

## 8. Retirement：删除是一种正式的开发能力

软件系统具有天然的 Complexity Ratchet：增加容易，删除困难。

功能上线以后很快会形成用户依赖、历史数据、文档、API 调用和组织预期。AI 进一步降低“Add”的即时成本，却不会同步降低“Remove”的社会与技术成本。

因此 BYHB 把 **Retirement Review（退役审查）** 纳入正式反馈环，而不是默认所有已发布能力永久存在。

Retirement Review 可以问：

- 哪些功能长期低使用率？
- 哪些 Setting 增加了大量状态却很少产生价值？
- 哪些 Feature Flag 已成为永久垃圾？
- 哪些 Dependency 不再必要？
- 哪些 Public API、页面、工作流已不值得维护？
- 哪些实现可以被更简单的方案替代？

删除并不等于失败。如果一项复杂度的持续成本已经超过它产生的价值：

> **删除本身就是价值创造。**

---

## 9. 风险自适应：避免把方法论变成官僚主义

任何治理框架最大的风险之一，是自己成为新的复杂度。

BYHB 因而拒绝“所有任务一律跑完整流程”。其重量应按两类变量调节：

1. **Reversibility：可逆性**
2. **Consequence：判断错误的后果**

| | 错误后果低 | 错误后果高 |
|---|---|---|
| **容易逆转** | 直接执行 / 快速实验 | 小规模验证后执行 |
| **难以逆转** | 谨慎设计 | 深度 Shaping + Ownership Review |

典型示例：

- 文案、CSS、可回滚的小 Bug Fix：直接处理；
- Feature Flag 后的实验能力：快速 Prototype；
- 普通长期 Feature：轻量 Commitment + Vertical Slice；
- Public API、Auth、Billing、Core Data：严格 Commitment + 深度 Shaping + 强 Ownership Gate。

因此 BYHB 的原则不是“慢下来”，而是：

> **让低风险可逆工作保持高速，让真正昂贵的错误获得足够思考。**

---

## 10. 理论机制：从生成丰裕到复杂度累积

本文提出一个需要后续实证研究验证的因果机制：

```text
AI Candidate Generation ↑
          ↓
Options / Prototypes / Patches ↑
          ↓
Boundary Compression
          ↓
Premature Commitment / Premature Ownership ↑
          ↓
Owned Complexity ↑
          ↓
Review / Verification / Integration / Maintenance ↑
          ↓
Context and coordination cost ↑
          ↓
Rework / instability risk ↑
```

这并不意味着 AI 必然制造技术债。相反，DORA 的“Amplifier”结论提示：如果组织拥有强用户导向、平台能力、测试与小批量交付，AI 可以放大优点；如果基础薄弱，AI 也可能放大问题 [11][12]。

BYHB 的作用因此不是抑制 AI 生产力，而是让“候选生成的加速”与“Commitment / Ownership 治理”解耦：

> **前端探索可以极度开放，后端 Ownership 必须保持选择性。**

---

## 11. 研究命题

本文当前属于 Conceptual Framework，而不是已经得到充分实证验证的工程定律。为使其可证伪，提出以下研究命题。

### P1 — Abundance–Rework Proposition

在其他条件近似时，当 AI 候选实现生成能力相对于团队 Review / Verification 能力持续提高，而 Commitment / Ownership 治理机制保持不变时，候选实现的返工、废弃或拒绝比例将提高。

### P2 — Commitment Governance Proposition

显式使用 `Commit / Defer / Discard` 的团队，相比将 AI 产生的候选项直接转化为 Backlog 的团队，应具有更低的 Premature Implementation Rate，即更少出现“实现后才发现产品价值或优先级本身错误”的工作。

### P3 — Risk-Adaptive Shaping Proposition

Risk-Adaptive Shaping 对高不可逆性、高错误代价的决策应能降低后期返工成本；但如果过度应用于低风险、易撤销决策，则会增加不必要的 Lead Time。

这一命题特别重要，因为它意味着 BYHB **使用过度同样会降低效率**。

### P4 — Ownership Governance Proposition

在相近用户价值输出下，使用显式 Ownership Gate 与 Retirement Review 的团队，其低使用率功能、公共配置面、废弃 API 与不必要依赖的长期增长速度应低于只优化 Feature Throughput 的团队。

---

## 12. 操作化与未来研究设计

### 12.1 Repository 纵向研究

可以利用 AIDev 一类 Agentic PR 数据，追踪：

- Merge / Close / Abandon；
- Review Duration；
- Follow-up Fix；
- Revert；
- 后续大幅重写；
- 任务为什么被拒绝；
- 功能是否最终产生真实使用。

特别需要区分：

1. 技术实现错误；
2. 产品价值、优先级或 Scope 判断错误。

第二类才直接对应 Commitment Quality。

### 12.2 团队级对照实验

使用相同 Coding Agent 的多个团队，可以比较：

**Control**

```text
Idea → Backlog → Agent → PR → Review
```

**BYHB**

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

观察 Lead Time、Review Time、Rework、Change Failure、Feature Adoption、Feature Removal 与 Ownership Surface 的变化。

### 12.3 高不可逆决策案例研究

Public API、Authentication、Billing、Permission Model、Plugin Architecture、Database Schema 等特别适合作为案例研究对象。

核心问题包括：

- 决策时掌握了哪些证据？
- 哪些不确定性被忽略？
- 是否出现 Premature Ownership？
- 返工成本来自实现错误，还是承诺过早？
- 如果延迟 Commitment，是否会显著降低成本？

---

## 13. 对 AI 软件团队的实践意义

如果 Implementation Abundance 假说成立，AI 团队的绩效对象需要发生变化。

仅仅观察：

- Commit 数量；
- PR 数量；
- LOC；
- Feature Count；
- Agent 完成任务数；

很容易把“更高活动量”误认为“更高产品价值”。DORA 对 User-Centric Focus 的研究已经明确指出，缺乏用户导向时，AI 可能加速 Feature Factory [12]。

更值得关注的问题是：

- 有多少候选项在承诺前被正确淘汰或 Defer？
- 有多少实现后来因为“本来就不值得做”而被大改或废弃？
- 一个新功能增加了多少长期 Ownership Surface？
- 上线功能是否真正被用户使用？
- 团队是否有能力主动 Retire 低价值复杂度？

未来高水平的 AI 开发团队可能并不是“让 Agent 写代码最多”的团队，而是：

> **既能用 AI 极大扩大探索空间，又能阻止绝大多数低价值探索结果进入长期系统的团队。**

---

## 14. 与“博观而约取，厚积而薄发”的关系

本文不主张苏轼预见了现代软件工程，也不把古典文本当作工程证据。

“博观而约取，厚积而薄发”在本文中承担的是 **Naming Metaphor + Heuristic Frame**：它为已经由现代产品设计、系统工程与 AI 软件开发现实重新论证出的结构提供一种高度凝练的中文表达。

其现代解释为：

### 博观

扩大 Option Space，而不是扩大 Roadmap。

### 约取

控制 Commitment，而不是消灭可能性。

### 厚积

根据错误代价与不可逆性，降低关键不确定性，而不是堆积文档。

### 薄发

限制穿过 Ownership Boundary 的长期复杂度，而不是降低质量。

因此可以概括为：

> **博观管理可能性，约取管理承诺；厚积管理不确定性，薄发管理复杂度。**

进一步浓缩成面向 AI Coding 的实践语言：

> **大胆探索，大量试验，谨慎承诺，克制拥有。**

---

## 15. 局限

### 15.1 Implementation Abundance 尚未被充分实证验证

这是本文提出的概念视角，而不是软件工程领域已经确立的标准理论。不同团队的 Candidate Generation、Review、Verification 与 Ownership Capacity 可能差异巨大。

### 15.2 AI Coding 能力快速变化

METR 2025 与 2026 的研究变化已经表明，工具能力和开发者使用模式在短时间内就可能改变实验结果及研究方法 [9][10]。因此任何基于当前 Agent 能力得出的结论都需要持续更新。

### 15.3 Ownership Complexity 难以统一量化

Public API、UI State、Settings、Services、Dependencies、Data Migration 与 Cognitive Load 都可能构成复杂度，但无法简单通过 LOC 相加。

### 15.4 治理框架可能产生治理债务

如果每一个低风险修改都需要 PRFAQ、ADR 和多级 Gate，BYHB 本身就会成为应该被“约取”的复杂度。

因此，风险自适应不是框架的可选附加项，而是其成立的必要条件。

### 15.5 尚缺乏真实项目的纵向案例

本文当前仍属于 Conceptual Working Paper。只有经过真实项目案例、对照实验和长期数据验证后，才能判断其究竟是一种有用的认知框架，还是仅仅一种具有启发性的理论整理。

---

## 16. 结论

软件工程过去长期建立在“实现能力有限”这一稀缺关系上。AI Coding Agent 正在改变这一基础：组织越来越能够快速生成想法、方案、原型和候选代码。

但软件产品的目标不是最大化候选代码数量，而是最大化长期用户价值。

当：

> **能够迅速实现的东西，开始多于真正值得长期拥有的东西，**

软件团队就需要重新区分三个问题：

> **Can we build it?**

> **Should we invest in it?**

> **Should we own it?**

Commitment Boundary 用来分离前两个问题，Ownership Boundary 用来分离后两个问题。

在此基础上，BYHB 不要求团队减少探索，反而鼓励使用 AI 更快、更广地研究与实验；它真正限制的是未经充分判断的 Commitment 与 Production Ownership。

因此，本文的中心命题可以表述为：

> **AI 软件工程的核心治理问题，不再只是如何更快地产生实现，而是如何防止廉价生成的候选实现过早转化为昂贵的长期系统义务。**

最终，真正值得优化的不是 Code Generation Rate，而是：

> **从可能性到长期用户价值的转化效率。**

这也是“博观而约取，厚积而薄发”在 AI 软件工程中的现代意义。

---

## 参考文献与资料

1. Li, H., Zhang, H., & Hassan, A. E. **AIDev: Studying AI Coding Agents on GitHub**. 2026. https://arxiv.org/abs/2602.09185
2. Design Council. **The Double Diamond / History of the Double Diamond**. https://www.designcouncil.org.uk/resources/the-double-diamond/history-of-the-double-diamond/
3. Sobek II, D. K., Ward, A. C., & Liker, J. K. **Toyota's Principles of Set-Based Concurrent Engineering**. MIT Sloan Management Review, 1999. https://shop.sloanreview.mit.edu/store/toyotas-principles-of-set-based-concurrent-engineering
4. Singer, R. **Shape Up: Principles of Shaping**. Basecamp. https://basecamp.com/shapeup/1.1-chapter-02
5. Singer, R. **Shape Up: Write the Pitch**. Basecamp. https://basecamp.com/shapeup/1.5-chapter-06
6. Fowler, M. **YAGNI**. 2015. https://martinfowler.com/bliki/Yagni.html
7. AWS Well-Architected. **DevOps Guidance: Prioritize customer needs to deliver optimal business outcomes**. https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/oa.ti.6-prioritize-customer-needs-to-deliver-optimal-business-outcomes.html
8. AWS Prescriptive Guidance. **Developing product strategies that deliver measurable business value**. https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-product-development/start-with-why.html
9. Becker, J., Rush, N., Barnes, B., & Rein, D. **Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity**. METR, 2025. https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf
10. METR. **We are Changing our Developer Productivity Experiment Design**. 2026. https://metr.org/blog/2026-02-24-uplift-update/
11. DORA. **State of AI-assisted Software Development 2025**. https://dora.dev/research/2025/dora-report/
12. DORA. **User-centric Focus**. https://dora.dev/capabilities/user-centric-focus/
13. DORA. **AI Capabilities Model**. https://dora.dev/ai/capabilities-model/report/
14. 吾爱分享网. **博约开发法：AI 编程时代的软件项目开发方法**. https://www.wuaishare.cn/12793.html

---

## 版权与引用说明

“博约开发法 / Boyue”方法论由 **吾爱分享网（Wuaishare）** 原创提出并持续完善。转载、改编或引用本文方法论内容时，请保留方法来源与原始文章链接：

- https://www.wuaishare.cn/12793.html
- https://github.com/wuaishare/boyue

本文引用的 Double Diamond、Set-Based Concurrent Engineering、Shape Up、YAGNI、Working Backwards、Vertical Slice 等既有方法与实践均归其原作者和来源所有；Boyue 不主张对这些既有实践拥有原创权。
