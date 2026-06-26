# `nature-citation` 技能

`nature-citation` 用于把论文段落、手稿片段或单条科研判断转化为可审查的 Nature / CNS 系列参考文献候选，并导出可被文献管理器直接导入的文件。

这个技能支持中文输入。用户可以直接提出“分段引用”“Nature 系列引用”“CNS 及子刊”“补引用”“支撑文献”“导出 Zotero”等需求；技能会用英文科学概念检索文献，同时默认返回中文审查说明。

## 功能

- 将手稿拆分为可引用的 claim 单元，并生成稳定编号，例如 `S001`、`S002`、`S003`。
- 为每个片段生成面向 Crossref 等结构化元数据源的检索式。
- 将结果限制在 Nature Portfolio、AAAS Science family、Cell Press，或只保留旗舰刊范围。
- 为每个片段匹配候选文献，并给出建议的正文插入位置。
- 导出一个 `ENW`、`RIS` 或 Zotero `RDF` 文献管理文件。
- 可选生成 JSON、TSV、Markdown 和 HTML 审查材料，便于人工筛选。
- 支持长文批处理、部分检查点、失败重试和局部段落运行。
- 支持 DOI-only 导出，适合用户已经确认文献列表的场景。

## 来源层级

- Crossref 结构化元数据与 DOI 记录。
- 相关时使用 PubMed / NCBI E-utilities 做生物医学交叉核对。
- Nature Portfolio、AAAS Science、Cell Press 的官方出版商页面。
- 二级学术索引只作为发现线索，不能作为唯一支撑依据。

## 文件结构

该技能采用 router/static-dynamic 结构：`SKILL.md` 负责短路由，`manifest.yaml` 决定常驻内容和按需参考文件。`nature-citation` 是线性工作流，没有内容轴，因此主要由 core 常驻内容和按需 references 组成。

```text
nature-citation/
├── SKILL.md                     # 短路由
├── manifest.yaml                # always_load core + 按需 references
├── README.md
├── static/
│   └── core/                    # 始终加载
│       ├── principles.md        # 产物、期刊范围、来源层级、检索规则
│       ├── chinese-mode.md      # 中文用户模式
│       └── workflow.md          # 7 步工作流与报告格式
├── references/                  # 按需打开
│   ├── script-usage.md          # nature_citation.py 参数与长文批处理
│   ├── journal-scope.md
│   ├── ris-endnote.md
│   └── search-strategy.md
└── scripts/
    └── nature_citation.py
```

## 适用场景

- 给摘要、引言、结果、讨论或单段文字补充引用。
- 将长文本拆成“片段-候选文献”对应表。
- 限定只检索 `Nature系列`、`CNS`、`CNS及其子刊` 或 `只看正刊`。
- 为 EndNote、Zotero 或其他文献管理器导出记录。
- 判断一句话获得的是直接支撑、部分支撑，还是背景性支撑。
- 生成 HTML 审查页，让用户按年份筛选、选择文献并下载所需记录。

## 长文本处理

短输入会采用普通的一次性检索流程。较长输入可以分批处理，每批完成后写入部分导出检查点，避免后续批次失败导致前面进度丢失。Crossref 临时失败会自动重试。

经验规则：

- 1-10 个片段：普通运行。
- 11-25 个片段：优先使用 batch mode。
- 26 个以上片段：优先按小节分开运行。

## 设计意图

该技能优先追求可辩护性，而不是候选文献数量。它的目标是帮助用户发现范围内的潜在支撑文献，而不是把元数据当成证据本身。每条导出记录都应保留真实元数据，不补造字段，并明确提示仍需人工阅读全文或摘要来确认支撑强度。

对长手稿而言，设计目标还包括运行稳定性：更小批次、更少中断、更清晰的检查点轨迹。

## 参考文件

- `search-strategy.md`：claim 拆解、支撑等级和常见检索失败模式。
- `journal-scope.md`：Nature / Science / Cell 家族边界与旗舰刊解释。
- `ris-endnote.md`：`ENW`、`RIS`、Zotero `RDF` 导出说明。
- `scripts/nature_citation.py`：本地 CLI，用于分段、Crossref 检索、导出和 HTML 审查页生成。

## 常用 CLI 参数

- `--batch-size 2`：将长文本拆成更小批次处理。
- `--max-segments 12`：限制一次运行处理的片段数。
- `--max-retries 2`：重试临时 Crossref 失败。
- `--sleep 0.3`：缩短请求间默认等待。
- `--with-artifacts`：生成 HTML、TSV、JSON 和 Markdown 审查文件。

## 注意事项

- 默认产物是单个文献管理文件；其他审查材料需显式开启。
- `metadata-only candidate` 表示仍需人工查看摘要或全文后才能引用。
- HTML 审查页可将用户选中的记录导出为 `ENW`、`RIS` 或 Zotero `RDF`。
- 长文本建议开启 `--with-artifacts`，因为 HTML 页面最方便人工筛选。
- Batch mode 会在最终导出前持续写入 `.partial.enw`、`.partial.ris` 或 `.partial.rdf` 检查点。
