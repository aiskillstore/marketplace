# `nature-reviewer` 技能

`nature-reviewer` 用于从审稿人视角模拟 `Nature` 风格的预投稿评审包，而不是从作者 rebuttal 视角写回复。

该技能专门基于 `Nature` 官方 `Editorial criteria and processes` 页面中的审稿相关内容创建：

```text
https://www-nature-com/nature/for-authors/editorial-criteria-and-processes
```

它的动机非常明确：

- 提取该官方 `Nature` 来源中与审稿人相关的规则。
- 让模拟审稿行为尽可能保持在这些规则范围内。
- 避免滑向泛化的同行评审习惯或虚构审稿人设定。
- 形成一个可复用的 `nature-reviewer` 技能，并尽量贴合仓库的技能格式。

因此，该技能刻意保持保守。它以 `references/editorial criteria and processes.md` 中的本地来源副本为依据，并转换成稳定输出约定：`3 reviewer reports + 1 cross-review synthesis`。三个报告只在关注重点上不同，因为来源支持审稿功能和报告内容，但不支持虚构具体审稿人身份或专业人设。

## 功能

- 将手稿草稿、摘要、选定章节、图表或作者说明作为审稿输入包读取。
- 按来源约束的 `Nature` 风格维度评估工作：`originality`、`scientific importance`、`interdisciplinary readership`、`technical soundness` 和 `readability for nonspecialists`。
- 生成 `3` 份 reviewer report；差异只体现在重点，不编造身份或专业背景。
- 说明哪些读者会对结果感兴趣，以及原因。
- 识别作者论证成立前必须解决的技术缺陷。
- 综合三份报告的共识与重点差异。
- 标记无支撑声称和无法从已提供证据判断的内容。

## 适用场景

- 投稿前模拟 `Nature` 审稿意见。
- 压力测试手稿是否具有可信的 broad-interest 叙事。
- 从审稿人视角评估 novelty、significance 或 technical soundness。
- 生成预投稿同行评审式批评。
- 判断手稿是否能被非本领域专家读懂。
- 获得有边界的 peer-review style response，而不是作者回复信。

如果用户要写逐点回复或返修信，请使用 `nature-response`。

## 默认返回内容

除非用户要求其他格式，技能会返回：

1. `Review setup`
2. `Reviewer 1`
3. `Reviewer 2`
4. `Reviewer 3`
5. `Cross-review synthesis`
6. `Risk / unsupported claims`

## 核心规则

- 评估只能基于本地 reviewer 来源和用户提供的手稿事实。
- 三位审稿人使用同一事实基础，只改变事实权重。
- 不得编造审稿人身份、细分专业角色、机构或隐藏知识。
- 必须明确回答 `who will be interested in the new results and why`。
- 必须明确识别阻碍作者论证成立的 `technical failings`。
- 区分技术有效性和 broad-interest 适配度；来源认为两者相关但并不等同。
- 对无法判断的地方使用 `AUTHOR_INPUT_NEEDED`、`Not assessable from provided material` 或类似不确定性标签，不能补造细节。

## 来源层级

- `references/editorial criteria and processes.md` 是首要权威本地来源。
- 用户提供的手稿事实和证据。
- `references/source-basis.md` 中总结的保守本地实现规则。

该技能不得静默扩展到泛化审稿人角色、虚构人设或期刊政策猜测。

## 文件结构

```text
nature-reviewer/
├── README.md
├── SKILL.md
└── references/
    ├── editorial criteria and processes.md
    ├── source-basis.md
    ├── reviewer-workflow.md
    ├── review-axes.md
    ├── report-structure.md
    ├── role-boundaries.md
    └── qa-checklist.md
```

## 状态

Draft。第一版由来源定义，并已结构化为有依据的审稿模拟，但尚未用真实匿名手稿-审稿示例库验证。
