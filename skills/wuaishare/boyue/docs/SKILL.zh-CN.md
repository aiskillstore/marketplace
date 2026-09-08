# Boyue · 博约开发法 Skill 中文阅读版

> 本文件是根目录 [`SKILL.md`](../SKILL.md) 的**官方中文阅读版**，用于中文用户理解、审阅和传播。
>
> **唯一执行真源仍是根目录 `SKILL.md`。** 为避免双份规则长期漂移，本文件不会作为第二套独立执行入口维护；当规则发生变化时，应先更新 `SKILL.md`，再同步本中文说明。

## 目标

把“博观而约取，厚积而薄发”转化为一层轻量的软件项目治理机制，用于 AI 编程、Coding Agent 和 Agentic Software Development。

它不是为了降低开发速度，而是为了做到：

- 探索可以足够广；
- 承诺必须足够慎；
- 高风险决策获得与错误代价相匹配的验证；
- 进入生产系统的长期复杂度保持克制。

## 五条核心规则

1. **广泛探索，但不要广泛承诺。**
2. **大胆原型，谨慎拥有。**
3. **候选可以便宜，承诺从来不便宜。**
4. **按照“判断错误的代价”决定塑形深度。**
5. **只交付最小、完整且值得长期拥有的变化。**

始终区分两道边界：

- **Commitment Boundary · 承诺边界：** `Could Build ≠ Should Invest`，能做不等于值得投入。
- **Ownership Boundary · 所有权边界：** `Should Build ≠ Should Own`，值得实现不等于值得长期维护。

## 第一步：先判断当前工作属于什么模式

在行动前选择**最轻但足够有效**的模式：

- **Explore / 博观**：研究新的产品、用户问题、市场、架构或技术可能性。
- **Select / 约取**：判断新 Scope 是否值得正式承诺。
- **Shape / 厚积**：降低昂贵或难以逆转决策中的关键不确定性。
- **Deliver / 薄发**：对已经获得合理证据的变化，以最小完整生产面进行实现。
- **Evidence / Retirement / 反馈与退役**：重新判断现有复杂度是否仍然值得拥有。

**不要强迫每个任务完整走完所有模式。**

## 低风险、可逆工作走快速路径

当变化范围小、后果低、容易撤销，而且不会显著增加长期 Ownership 时，直接执行。

典型场景：

- 文案和文档修正；
- CSS、间距和布局微调；
- 范围明确的小 Bug；
- 不改变行为的局部重构；
- Feature Flag 后面的可逆实验。

对这类任务：

- 不增加无必要的规划仪式；
- 优先最小安全改动；
- 验证行为后完成任务。

博约开发法不应该把一个 CSS 小改动变成产品委员会。

## Commitment Boundary · 承诺边界

当工作开始引入明显的新 Scope 时触发，包括：

- 新 Feature；
- 新模块或新平台；
- 新集成；
- 新依赖；
- 新架构方向；
- 新的产品 Surface；
- “既然都做到这里了，顺便再加……”之类的扩张。

先问：

- 它究竟解决什么用户或系统问题？
- 为什么应该现在做？有哪些证据？
- 这是一个已经值得投入的承诺，还是一个有意思的 Option？
- 如果现在不做，会发生什么？

只给出三类结果：

- **COMMIT**：证据支持现在投入。
- **DEFER**：保留未来可能性，但不消耗当前承诺能力；同时记录重新评估触发条件。
- **DISCARD**：已有足够理由结束这个候选项。

重要产品决策可以使用：

- [`PRFAQ`](../templates/prfaq.md)
- [`Non-goals`](../templates/non-goals.md)
- [`Decision Record`](../templates/decision-record.md)

详细说明见 [`Commitment Boundary`](../references/commitment-boundary.md)。

## Ownership Boundary · 所有权边界

当长期复杂度准备进入生产系统时触发，尤其包括：

- Public API 或协议；
- 持久化 Schema 或状态；
- Auth、Authorization、Billing、Permissions；
- 长期存在的设置和配置；
- 新服务或基础设施组件；
- 带有持续运维成本的依赖；
- 兼容性与迁移义务。

问：

> **如果未来三年都必须维护它，我们今天仍然愿意把它加入产品吗？**

使用 [`Ownership Review`](../templates/ownership-review.md) 检查新增加的 Ownership Surface。

如果答案并不确定，优先缩小 Scope，或者继续把它保持为实验，而不是因为“代码已经能跑”就自动升级为生产能力。

详细说明见 [`Ownership Boundary`](../references/ownership-boundary.md)。

## 厚积：按照风险而不是文档数量塑形

不要把“厚积”理解成写更多 PRD、架构文档和会议纪要。

Shaping 深度主要取决于：

- **可逆性**：判断错了以后多容易撤销？
- **失败后果**：判断错了以后影响面有多大？

低风险、高可逆变化应保持高速；高影响、难以逆转的承诺需要更强的证据。

只有在确实能降低关键不确定性时，才使用：

- Disposable Spike；
- PoC；
- Prototype；
- ADR；
- Benchmark；
- 用户测试；
- Migration Rehearsal。

面对不确定的 AI 能力，应尽量使用真实输入验证，并记录：

- 任务成功率与失败模式；
- 结构化输出稳定性；
- 延迟；
- 成本；
- 上下文敏感性；
- 确定性方案或非 AI 替代方案。

使用 [`Risk Review`](../templates/risk-review.md) 与 [`Risk-Adaptive Shaping`](../references/risk-adaptive-shaping.md)。

## Prototype 必须默认可丢弃

把早期实验代码视为**证据**，而不是天然的“生产第一版”。

Prototype 成功，只能证明“这条路可能工作”，不能证明团队应该长期拥有它产生的全部复杂度。

优先：

```text
未知能力
  ↓
Disposable Spike / PoC
  ↓
获得证据
  ↓
COMMIT / DEFER / DISCARD
```

而不是：

```text
未知能力
  ↓
直接搭建 Production Architecture
```

一句话：

> **Prototype 可以是 Disposable，Production 必须是 Deliberate。**

## 薄发：交付最小完整价值切片

当价值与风险已经得到足够理解后，交付 **Minimum Coherent Value Slice（MCVS，最小完整价值切片）**。

一个完整切片应完成一个真实用户目标或系统目标，同时只保留必要的：

- 用户 / 界面路径；
- 业务逻辑；
- 数据 / 状态变化；
- 权限；
- 错误处理；
- 可观测性；
- 与风险匹配的回滚、禁用或迁移保护。

优先采用纵向端到端切片，而不是先铺满数据库层、再铺后端、最后才连接 UI 的横向堆叠。

MCVS、Vertical Slice、Walking Skeleton 与 Tracer Bullet 的关系见 [`Delivery Patterns`](../references/delivery-patterns.md)。

> **“薄”是变更面薄，不是质量薄。**

## 退役审查：删除也是正式开发能力

不要假设上线后的功能应该永久存在。

定期检查：

- 长期低使用率 Feature；
- 过期设置；
- 已经永久化的 Feature Flag；
- 不再必要的依赖；
- 过时 API 或服务；
- 已经与真实行为不一致的文档和工作流。

选择：

- **Maintain**：继续保留；
- **Simplify**：缩小、合并或降低复杂度；
- **Retire**：正式退役。

使用 [`Retirement Review`](../templates/retirement-review.md)。

## 禁止凭空发明数字门槛

不要自行制造如下固定规则：

- “AI 必须比传统方案好 10 倍”；
- “必须删除 80% 的想法”；
- “只能留下 3–5 个功能”。

阈值必须来自项目证据、风险与实际约束，而不是方法论为了显得精确而人为编造。

## 方法论资料与模板

### 方法论参考

- [`Methodology`](../references/methodology.md)
- [`Commitment Boundary`](../references/commitment-boundary.md)
- [`Ownership Boundary`](../references/ownership-boundary.md)
- [`Risk-Adaptive Shaping`](../references/risk-adaptive-shaping.md)
- [`Delivery Patterns`](../references/delivery-patterns.md)

### 实践模板

- [`Option Map`](../templates/option-map.md)
- [`PRFAQ`](../templates/prfaq.md)
- [`Decision Record`](../templates/decision-record.md)
- [`Non-goals`](../templates/non-goals.md)
- [`Risk Review`](../templates/risk-review.md)
- [`Ownership Review`](../templates/ownership-review.md)
- [`Retirement Review`](../templates/retirement-review.md)

## 完成前检查

在声明项目或开发任务已经完成之前，至少确认：

1. 没有把一个“有意思的 Option”悄悄升级成正式承诺；
2. 没有把一个成功 Prototype 悄悄升级成长期 Production Ownership；
3. 高风险不确定性获得了与其错误后果相匹配的证据；
4. 生产变更没有大于实现完整价值真正需要的范围；
5. 已经考虑明显可以简化或删除的复杂度。

## 中文用户如何使用

正常情况下，兼容 Agent Skills 的宿主应根据根目录 [`SKILL.md`](../SKILL.md) 的 metadata 自动判断何时触发 Boyue；中文用户无需安装第二份 Skill。

也可以显式要求：

```text
使用博约开发法判断这个功能是否值得进入 Roadmap。
```

```text
在实现这个架构变化以前，先检查 Commitment Boundary 和 Ownership Boundary。
```

```text
先做一个 Disposable AI Spike，不要急着把未知能力做成生产架构。
```

```text
对这个成熟模块执行 Retirement Review，找出可以安全简化或删除的复杂度。
```

---

**方法论出处：**“博约开发法”由 [吾爱分享网](https://www.wuaishare.cn/) 原创提出并持续完善。推荐先阅读图文版文章：[《博约开发法：AI 编程时代的软件项目开发方法》](https://www.wuaishare.cn/12793.html)，完整中英文方法论论文见 [`paper/`](../paper/README.md)。
