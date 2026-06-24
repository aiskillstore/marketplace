# `nature-data` 技能

`nature-data` 用于为 Nature / Springer Nature 风格投稿准备或审查 Data Availability statement、数据仓储方案、数据集引用和 FAIR 元数据检查。

该技能支持中文作者笔记。用户可以用中文描述“数据可向通讯作者索取”“原始数据”“受限数据”“公共数据库”等情况；技能会转化为可投稿的英文表述，并在需要时给出中文确认项。

## 功能

- 起草可直接粘贴到稿件中的 Data Availability statement。
- 在投稿前审查薄弱或不完整的数据可用性表述。
- 将每个支撑结果的数据集映射到仓储、accession、DOI 或访问路径。
- 区分公开数据、受控访问数据、第三方数据、补充材料数据和不适用场景。
- 准备 FAIR 元数据和 DataCite 风格的数据集引用检查。
- 标记缺失的仓储记录、许可证、来源、embargo 细节和访问条件。
- 将中文作者意图对齐为 Nature 风格英文数据可用性措辞。

## 来源层级

- Nature Portfolio 与 Springer Nature 的研究数据政策。
- Nature Portfolio 关于数据、代码、材料和实验方案可用性的报告标准。
- Scientific Data 关于仓储、原始性、长期保存和数据引用的实践。
- FAIR Guiding Principles 与 DataCite 元数据规范。

## 文件结构

该技能采用 router/static-dynamic 结构：`SKILL.md` 负责短路由，`manifest.yaml` 加载常驻 core 和按需 references。`nature-data` 是线性工作流，没有内容轴。

```text
nature-data/
├── SKILL.md                     # 短路由
├── manifest.yaml                # always_load core + 按需 references
├── README.md
├── agents/
│   └── openai.yaml
├── static/
│   └── core/                    # 始终加载
│       ├── stance.md            # 默认立场与来源层级
│       ├── chinese-mode.md      # 中文用户模式
│       └── workflow.md          # 8 步工作流与输出格式
└── references/
    ├── fair-metadata-checklist.md
    ├── chinese-author-alignment.md
    ├── policy-principles.md
    ├── repository-and-identifiers.md
    ├── source-basis.md
    └── statement-patterns.md
```

## 适用场景

- 为 Nature 系列或 Springer Nature 期刊准备 Data Availability statement。
- 投稿前决定数据应存放在哪个仓储。
- 修改含糊的 “available on request” 表述。
- 处理受控访问、人类参与者、商业专有或第三方数据。
- 引用带 DOI、accession number、Handle、ARK 或仓储记录的数据集。
- 检查数据存储是否达到投稿所需的 FAIR 程度。
- 将中文数据可用性说明转成准确的英文投稿文本。

## 设计意图

该技能要求每个支撑论文结论的数据集都有明确可追踪的访问路径。它不会编造 accession、许可证、限制条件或仓储元数据。信息缺失时，应给出可用草稿，并列出作者必须确认的短清单；如果用户从中文草稿开始，应优先给出中文确认说明。
