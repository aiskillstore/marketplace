# `nature-response` 技能

`nature-response` 用于起草、审查和修改逐点回复审稿人的 response letter，适用于 Nature 系列和其他高影响力期刊的返修场景。

该技能支持中英文输入。它可以接收中文或英文审稿意见、编辑决定信、作者修改说明和 rebuttal 草稿，并生成英文回复包；需要作者确认的信息会用中文提示。

## 功能

- 将审稿意见拆分为稳定编号，例如 `R1.1`、`R1.2`、`R2.1`。
- 按类型、严重程度、所需行动、证据需求和风险对每条意见分类。
- 在正式起草前生成 response strategy summary。
- 根据任务需要路由到起草、审查、修改、只做分诊或类似 appeal 的处理。
- 如果决定信包含编辑要求，先生成 `E.1` 等 editor instruction ID，再处理 reviewer ID。
- 起草编辑可读的逐点回复信。
- 将每条回复映射到手稿修改动作、修改位置或缺失信息标记。
- 把防御性或含糊的作者笔记改写成专业回复语言。
- 处理困难情况，例如超出范围的实验、审稿人事实错误、审稿人意见冲突、统计质疑和合规问题。
- 标记缺失实验、分析、行号、引用、图版和手稿改动，不能编造这些内容。

## 适用场景

- 准备 Nature、Nature Portfolio、Springer Nature 或类似高影响力期刊返修。
- 回复大修或小修意见。
- 将审稿意见转化为手稿修改清单。
- 审查 rebuttal 草稿中遗漏回复、语气问题或无支撑声称。
- 将中文作者笔记转成可提交的英文逐点回复。
- 判断如何礼貌反驳审稿人，或解释研究范围边界。

## 默认返回内容

除非用户要求其他格式，技能会返回：

1. response strategy summary
2. comment-response tracker
3. draft point-by-point response letter
4. manuscript change checklist
5. missing information / risk flags
6. 用户使用中文时的中文确认说明

## 核心规则

- 回复前必须忠实保留审稿意见。
- 每条意见都要得到回应、交叉引用或标记为未解决。
- 每条回复必须映射到具体动作，例如 `ACCEPT_TEXT`、`ACCEPT_ANALYSIS`、`SOFTEN_CLAIM`、`DISAGREE` 或 `AUTHOR_INPUT_NEEDED`。
- 不得编造实验、分析、引用、行号、图版、补充材料、审稿人身份、编辑要求或手稿修改。
- 使用合作、证据优先、非防御性的语言。
- 将 response letter 视为给编辑核查的验证文件，而不只是礼貌文本。

## 来源层级

- 目标期刊说明与决定信要求。
- Nature / Nature Portfolio / Springer Nature 返修和同行评审流程说明。
- Springer Nature 关于 rebuttal letter 的编辑建议。
- 作者提供的本地手稿事实。

来源依据汇总在 `references/source-basis.md` 中，包含 URL、规则摘要和来源类型标签。

## 文件结构

该技能采用 router/static-dynamic 结构：`SKILL.md` 负责短路由，`manifest.yaml` 加载常驻 core 和按需 references。`nature-response` 是线性工作流，没有内容轴。

```text
nature-response/
├── README.md
├── SKILL.md                     # 短路由
├── manifest.yaml                # always_load core + 按需 references
├── static/
│   └── core/                    # 始终加载
│       ├── stance.md            # 目的、默认立场、红线、来源层级
│       └── workflow.md          # 输入类型、10 步工作流、输出格式
├── references/
│   ├── source-basis.md
│   ├── response-structure.md
│   ├── comment-taxonomy.md
│   ├── action-mapping.md
│   ├── tone-and-stance.md
│   ├── chinese-author-alignment.md
│   ├── difficult-cases.md
│   ├── intake-and-routing.md
│   └── qa-checklist.md
├── tests/
    ├── conflicting-reviewers.md
    ├── defensive-draft-audit.md
    ├── evaluation-summary.md
    ├── minor-revision.md
    ├── major-revision-missing-evidence.md
    ├── impossible-experiment.md
    └── rubric.md
└── examples/
    ├── conflicting-reviewers.md
    ├── major-revision-with-missing-evidence.md
    └── minor-revision.md
```

## 状态

Beta。当前行为由合成 Markdown fixtures 和示例定义。只有在经过真实匿名返修包、且获得作者许可的验证后，才应提升到 Stable。
