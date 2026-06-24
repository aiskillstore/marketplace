# `nature-paper-to-patent` 技能

`nature-paper-to-patent` 是一个有证据约束的工作流，用于把科研论文、学位论文、技术报告、源代码、图表和发明人笔记转换为结构化中国发明专利草稿。

该技能面向研究生、高校科研人员和技术团队。它生成中文正式专利文档，同时让面向 agent 的分析和路由说明保持可跨 AI agent 迁移。

## 功能

- 将论文正文、公式、图表、代码和补充证据映射到稳定 source ID。
- 提取技术问题、协同技术手段、实施链条和具体技术输出。
- 在起草权利要求前建立 evidence ledger。
- 将每个实质性权利要求特征映射到来源证据。
- 支持完整草案、仅权利要求、技术交底分析和 paper-patent comparison。
- 处理可选中文本 PDF、扫描 PDF、粘贴文本和混合项目文件夹。
- 将算法/软件、装置/系统、工艺/材料和混合型发明路由到不同起草规则。
- 保留来源支持的核心公式，并在 DOCX 中渲染为可编辑 Office Math。
- 生成与权利要求对齐的黑白流程图 SVG 和 PNG。
- 复用主权利要求流程图作为摘要附图和说明书附图。
- 分别生成中文 DOCX：权利要求书、说明书、说明书摘要、摘要附图和完整审阅稿。
- 校验权利要求结构、证据可追溯性、公式覆盖、附图对齐、术语一致性和质量阈值。

## 文件结构

```text
nature-paper-to-patent/
├── README.md
├── SKILL.md
├── manifest.yaml
├── requirements.txt
├── static/
│   ├── core/
│   │   ├── principles.md
│   │   ├── workflow.md
│   │   └── output-contract.md
│   └── fragments/
│       ├── source/
│       ├── task/
│       └── invention/
├── references/
│   ├── cn-patent-drafting-guide.md
│   ├── corpus-derived-patterns.md
│   ├── corpus-pair-audit.md
│   ├── draft-schema.md
│   └── patent-figure-guide.md
├── scripts/
│   ├── audit_claims.py
│   ├── build_patent_package.py
│   ├── extract_pdf_text.py
│   ├── init_patent_project.py
│   ├── math_to_omml.py
│   ├── render_flowchart_svg.py
│   ├── render_patent_docx.py
│   └── validate_patent_draft.py
├── evals/
│   └── evals.json
└── tests/
    └── test_validation.py
```

## 路由模型

短 `SKILL.md` 作为路由器。`manifest.yaml` 只选择当前请求需要的片段：

- `source_format`：`pdf-text`、`scanned-pdf`、`pasted-text` 或 `mixed-project`
- `task_mode`：`full-draft`、`claim-set`、`disclosure-analysis` 或 `paper-patent-audit`
- `invention_type`：`algorithm-software`、`apparatus-system`、`process-material` 或 `mixed`

始终加载的 core 定义证据纪律、分阶段起草工作流和输出契约。

## 默认工作流

1. 记录输入、发表状态、发明人问题和权属问题。
2. 建立全文 source map。
3. 建立术语、公式、图表和输入-操作-输出清单。
4. 建立 evidence ledger。
5. 形成发明构思和权利要求策略。
6. 起草并审查权利要求。
7. 对齐说明书、公式、附图、实施例和摘要。
8. 校验并生成完整申请文件包。

每个阶段都有明确 gate。无支撑特征会被排除在正式权利要求之外，未解决事实会保留为发明人问题，而不会被编造。

## 安装

安装完整目录，而不是只安装 `SKILL.md`，因为路由器依赖 `manifest.yaml`、`static/`、`references/` 和 `scripts/`。

安装依赖：

```bash
python -m pip install -r requirements.txt
```

运行自动检查：

```bash
python -m unittest discover -s tests -v
```

## 示例请求

```text
请读取并遵循 nature-paper-to-patent 技能。
分析 paper/paper.pdf，并生成中国发明专利草稿。
请分别创建中文权利要求书、说明书、说明书摘要和摘要附图 DOCX 文件。
保留来源支持的核心公式，并以可编辑 Office Math 呈现；
生成与权利要求对齐的主流程图和方法附图；
将每个实质性权利要求特征映射到来源证据。
```

## 默认交付物

```text
outputs/
├── patent-权利要求书.docx
├── patent-说明书.docx
├── patent-说明书摘要.docx
├── patent-摘要附图.docx
├── patent-完整审阅稿.docx
├── patent-结构化草稿.json
├── patent-权利要求检查.txt
├── patent-草稿验证报告.txt
└── patent-figures/
    ├── figure-1.svg
    └── figure-1.png
```

## 状态与边界

状态：**Beta**。

确定性校验脚本和合成测试覆盖权利要求映射、核心公式要求、附图生成、可编辑 Office Math 和 DOCX 打包。输出仍是起草辅助材料，不构成专利性、新颖性、发明人资格、权属、侵权或可提交性意见；正式使用前需要发明人确认，并由合格中国专利专业人员审阅。

贡献者：[`snipp-zha`](https://github.com/snipp-zha)。

独立开发仓库：[`snipp-zha/Paper-to-patent-Skill`](https://github.com/snipp-zha/Paper-to-patent-Skill)。
