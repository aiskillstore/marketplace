# `nature-writing` 技能

`nature-writing` 用于根据作者提供的 claims、图表、结果、笔记或中文草稿，起草或重建 Nature 风格手稿章节。

## 功能

`nature-writing` 可帮助撰写：

- 标题
- 摘要
- 引言
- 结果叙事
- 讨论
- 结论
- significance paragraph
- 手稿大纲

该技能用于论证构建和章节起草。如果已有英文草稿只需要句子级润色，应使用 `nature-polishing`。

## 来源基础

该技能来自对材料、能源系统、建筑脱碳和机器学习等领域 Nature 与 Nature Communications 研究论文的细读，并结合仓库中已有的 writing-strategy 规则。

章节级写作和面向审稿人的自审规则也参考了彭思达老师公开的科研写作笔记：

- https://pengsida.notion.site/c1a22465a0fa4b15a12985223916048e
- https://github.com/pengsida/learning_research

## 文件结构

```text
nature-writing/
├── README.md
├── SKILL.md
└── references/
    ├── abstract.md
    ├── article-architecture.md
    ├── chinese-author-workflow.md
    ├── conclusion.md
    ├── experiments.md
    ├── introduction.md
    ├── method.md
    ├── nature-summary-paragraph.md
    ├── paper-review.md
    ├── paragraph-flow.md
    ├── related-work.md
    └── examples/
```

## 核心规则

| 领域 | 规则 |
|---|---|
| 证据优先 | 不编造数据、机制、统计量、样本量或创新性 |
| 摘要 | 背景、缺口、方法、关键结果、意义、边界 |
| 引言 | 领域尺度、瓶颈、已有尝试、未解决缺口、本文工作；面向 `Nature` 时使用分阶段 summary-paragraph funnel |
| 方法 | 解释模块动机、设计、正向流程和技术优势 |
| 结果 | 构建证据阶梯，而不是按实验流水账写作 |
| 实验 | 每个主要 claim 都要对应比较、消融、指标或压力测试证据 |
| 讨论 | 解释意义、与既有工作的关系、约束和未来使用 |
| 自审 | 投稿前做 adversarial self-review |
| 中文笔记 | 翻译意图和论证，不照搬中文句序 |
