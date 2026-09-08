[English](README.md) | 简体中文

# 博约开发法 · Boyue

> **AI 可以让错误的东西更快被做出来。**

博约开发法（Boyue）是一套面向 **AI 编程 / Coding Agent** 的轻量级软件项目决策与复杂度治理 Skill。

它帮助 AI 编程 Agent 在项目开发中做到：**大胆探索、谨慎承诺、按风险验证、克制拥有，并主动清理已经不再值得维护的复杂度。**

[![博约开发法：从广泛探索到谨慎拥有](assets/boyue-cover-zh-CN.webp)](https://www.wuaishare.cn/12793.html)

*点击主图可前往吾爱分享网图文阅读版，通过配图与博客排版更直观地理解方法论。*

## 项目资源

Boyue 同时维护为一套**完整方法论论文**和一个**可安装的 Agent Skill**。中文版导航只保留中文读者实际需要的资源：

- **中文完整版论文：** [从实现稀缺到实现丰裕：AI 软件工程中的决策边界与复杂度治理](paper/boyue-methodology.zh-CN.md)
- **可安装 Skill（唯一执行真源）：** [SKILL.md](SKILL.md)
- **Skill 中文阅读版：** [docs/SKILL.zh-CN.md](docs/SKILL.zh-CN.md)
- **实践模板：** [templates/](templates/)
- **使用案例：** [examples/](examples/)
- **图文阅读版：** [吾爱分享网《博约开发法：AI 编程时代的软件项目开发方法》](https://www.wuaishare.cn/12793.html)

GitHub 仓库作为完整论文、Skill、模板和案例的长期主仓；吾爱分享网文章则通过配图与博客排版提供更适合普通读者阅读理解的图文版本。两者保持双向链接。

## 一句话理解

> **大胆探索，大量试验，谨慎承诺，克制拥有。**

“博约开发法”取意于苏轼《稼说送张琥》中的：

> **博观而约取，厚积而薄发。**

放到 AI 软件开发中，可以解释为：

> **博观管理可能性，约取管理承诺；厚积管理不确定性，薄发管理复杂度。**

## 为什么需要它？

AI Coding Agent 正在显著降低想法、原型、代码修改、测试和 Pull Request 的生成成本。

这当然提高了开发能力，但也会产生一种新的风险：

```text
候选方案越来越容易生成
        ↓
想法、原型、代码越来越多
        ↓
越来越多“顺便做一下”
        ↓
更多复杂度进入生产系统
        ↓
测试 / 验证 / 迁移 / 兼容 / 运维成本不断增加
```

过去开发很贵，本身就是一道天然过滤器。

AI 时代这道过滤器正在变弱，因此需要人为重新建立两道边界。

## 两道关键边界

### 1. Commitment Boundary · 承诺边界

**Could Build ≠ Should Invest**

“我们能做”不等于“现在值得投入”。

AI 给出的新想法、竞品已有的功能、一个跑通的 Demo、甚至已经写完的代码，首先都只是 **Option（候选项）**，而不是 Roadmap。

对重要候选项只做三种判断：

- **COMMIT**：证据充分，现在值得投入；
- **DEFER**：方向可能有价值，但现在不投入，并记录重新评估条件；
- **DISCARD**：已有足够理由放弃。

### 2. Ownership Boundary · 所有权边界

**Should Build ≠ Should Own**

“值得验证和实现”不等于“值得未来几年一直维护”。

一个功能进入生产以后，不只是多了几百行代码，还可能同时增加：

- API 与兼容责任；
- 数据结构与迁移责任；
- 设置项和 UI 状态；
- 权限、安全边界；
- 新服务与基础设施；
- 监控、文档和用户支持；
- 长期依赖升级成本。

所以在长期复杂度进入生产以前，可以问一个简单的问题：

> **如果未来三年都必须维护它，我们今天还愿意把它加入产品吗？**

## 五种工作模式

博约开发法不是新的瀑布式流程。一个真实项目可以同时处于多个模式。

| 模式 | 作用 | 常用实践 |
|---|---|---|
| **博观 Explore** | 扩大可能性空间，减少认知盲区 | 用户研究、竞品调研、Option Map、AI Spike |
| **约取 Select** | 防止候选项自动变成承诺 | PRFAQ、Non-goals、Commit / Defer / Discard |
| **厚积 Shape** | 按错误代价降低关键不确定性 | PoC、Prototype、ADR、Benchmark、演练 |
| **薄发 Deliver** | 只让最小完整价值进入长期系统 | MCVS、Vertical Slice、Walking Skeleton |
| **反馈 / 退役** | 判断已有复杂度是否仍值得拥有 | 使用证据、简化、Retirement Review |

## 五条核心原则

1. **Explore broadly without committing broadly.**  
   广泛探索，但不要广泛承诺。

2. **Prototype freely; own selectively.**  
   大胆原型，谨慎拥有。

3. **Options are cheap; commitments are expensive.**  
   候选可以丰富，承诺必须珍贵。

4. **Shape according to the cost of being wrong.**  
   错误越昂贵、越难逆转，越应该充分塑形。

5. **Deliver the smallest coherent change worth owning.**  
   只让最小、完整且值得长期维护的变化进入系统。

## 这个 Skill 会做什么？

可安装的 [SKILL.md](SKILL.md) 会让 AI 编程 Agent 在适当的时候自动：

- 判断当前任务属于 Explore / Select / Shape / Deliver / Evidence 哪一种模式；
- 对低风险、容易回滚的小改动直接执行，不制造额外流程；
- 当任务突然扩大 Scope 时触发 Commitment Boundary；
- 当 Public API、核心数据、权限、长期配置、服务和依赖进入生产时触发 Ownership Boundary；
- 面对不确定的 AI 能力时优先做 Disposable Spike / PoC，而不是直接造生产架构；
- 避免把成功的 Prototype 自动升级成长期 Production Ownership；
- 用最小完整价值切片和 Vertical Slice 交付；
- 在成熟项目中主动寻找可以简化或退役的复杂度。

它不会使用“AI 必须强 10 倍”“必须删掉 80% 想法”这类没有依据的固定数字规则。

## 快速例子

### 小而可逆的修改

> “把这个按钮文字改短一点，卡片间距加 4px。”

博约开发法不会要求写 PRFAQ 或 ADR。

判断：低风险、可逆、不增加长期 Ownership → **直接修改并验证。**

参见：[Feature Request](examples/feature-request.md)

### 开发过程中突然膨胀 Scope

原任务：

> “增加报告导出。”

Agent 又提出：

> “既然做导出，要不要顺便做定时导出、云盘同步、模板市场和公开 Export API？”

这些都只是 Option。

博约开发法会先执行：

**COMMIT / DEFER / DISCARD**

而不是把 AI 生成出来的所有想法都变成开发任务。

### 高不可逆架构决策

> “把内部扩展接口正式开放成第三方 Public API。”

一旦外部开发者依赖，兼容与迁移义务可能持续很多年。

博约开发法会提高 Shaping 深度，先验证契约边界、版本策略和长期 Ownership，再决定 Production Surface。

参见：[Architecture Change](examples/architecture-change.md)

### AI 能力不确定

> “模型能不能稳定从几十页技术文档里抽取结构化结果？”

不要先设计整套生产架构。

先做 Disposable AI Spike，验证：

- 成功率；
- 失败类型；
- 结构化输出稳定性；
- 延迟；
- 成本；
- 长上下文表现；
- 非 AI 替代方案。

参见：[AI Capability Spike](examples/ai-spike.md)

## 实践工具箱

### 方法论参考

- [方法论总览](references/methodology.md)
- [Commitment Boundary](references/commitment-boundary.md)
- [Ownership Boundary](references/ownership-boundary.md)
- [Risk-Adaptive Shaping](references/risk-adaptive-shaping.md)
- [Delivery Patterns](references/delivery-patterns.md)

### 模板

- [Option Map](templates/option-map.md)
- [轻量 PRFAQ](templates/prfaq.md)
- [Commitment Decision Record](templates/decision-record.md)
- [Non-goals](templates/non-goals.md)
- [Risk Review](templates/risk-review.md)
- [Ownership Review](templates/ownership-review.md)
- [Retirement Review](templates/retirement-review.md)

### 案例

- [新 AI 产品](examples/new-ai-product.md)
- [普通 Feature Request](examples/feature-request.md)
- [高风险架构变化](examples/architecture-change.md)
- [AI Capability Spike](examples/ai-spike.md)

## 安装

Boyue 按 Agent Skills 结构组织，仓库根目录包含 `SKILL.md`，其余资料通过相对路径按需加载。

兼容 Agent Skills 的 CLI 安装器可以直接安装仓库：

```bash
npx skills add wuaishare/boyue
```

各技能市场的同步状态与许可证边界统一记录在 [DISTRIBUTION.md](DISTRIBUTION.md)。

OpenAI 官方说明目前 Skills 遵循 Agent Skills 开放标准，并支持 ChatGPT、Codex 与 API；不同宿主产品的安装和工作空间管理方式会有所不同。

### ChatGPT

可以在 ChatGPT 的 Skills 页面通过创建/上传方式添加 Skill。官方说明：

- https://help.openai.com/zh-hans-cn/articles/20001066

### 使用 `~/.agents/skills` 的环境

例如部分 Desktop Commander / Agent Skills 本地环境可以直接：

```bash
git clone https://github.com/wuaishare/boyue.git ~/.agents/skills/boyue
```

之后开启新会话，或等待宿主刷新 Skill 列表。

### 其他兼容 Agent Skills 的工具

把仓库 Clone / Copy 到对应宿主要求的 Skill 目录即可。具体安装路径以宿主产品说明为准。

## 可以这样直接调用

通常 Skill 应在合适上下文中自动触发，也可以显式要求：

```text
使用博约开发法判断这个新功能是否应该进入 Roadmap。
```

```text
在实现这个架构变化以前，先用 Commitment Boundary 和 Ownership Boundary 做一次判断。
```

```text
用博约开发法设计一个 Disposable AI Spike，先验证这个模型能力。
```

```text
对这个成熟模块执行 Retirement Review，找出可以安全删除或简化的复杂度。
```

## 设计哲学

Boyue 必须保持轻量。

它不应该把一个 CSS 小改动变成产品委员会。

流程和治理深度只应该在以下情况增加：

- 决策越来越难回滚；
- 错误后果越来越高；
- 长期 Ownership Surface 明显扩大。

> **Prototype 可以是 Disposable，Production 必须是 Deliberate。**

## 方法论原创与出处

“博约开发法”方法论由 **吾爱分享网** 原创提出并持续完善。

完整资源：

- [中文完整方法论论文](paper/boyue-methodology.zh-CN.md)
- [吾爱分享网图文阅读版](https://www.wuaishare.cn/12793.html)
- [可安装 Agent Skill](SKILL.md)
- [Skill 中文阅读版](docs/SKILL.zh-CN.md)

转载、引用或改编该方法论文字时，请保留 **吾爱分享网** 与原文链接作为出处。

本项目同时借鉴和引用 Double Diamond、Set-Based Design、Shape Up、YAGNI、Working Backwards、Spike / PoC、Walking Skeleton、Tracer Bullet、Vertical Slice 等已有产品设计与软件工程实践；Boyue 不声称这些成熟实践由本项目发明。

## 开源许可

仓库代码与 Skill 文件采用 [MIT License](LICENSE)。

关于“博约开发法”方法论文字的转载与改编，请同时遵守上述出处与署名说明。
