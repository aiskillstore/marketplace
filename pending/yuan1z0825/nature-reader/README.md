# `nature-reader` 技能

`nature-reader` 是以 Markdown 为核心的全文论文阅读工作流。

## 功能

`nature-reader` 可以把 PDF、DOI、arXiv 链接、出版社 HTML 页面或粘贴的手稿文本转化为完整 Markdown 阅读材料，包含：

- 段落级原文与中文翻译，并以正文形式呈现。
- 提取出的图和表，放在首次实质性讨论它们的位置附近。
- 原始图注和中文图注翻译。
- 稳定的页码与文本块锚点，便于回溯来源。
- 紧凑图像裁剪和完整文档 source map。

## 主要产物

- `paper.md`
- `source_map.json`
- `translation_notes.md`
- `assets/`

`reader.html` 可以作为二级预览生成，但该技能默认以 Markdown 为中心，不默认生成交互式问答面板。

## 触发短语

当用户提出以下需求时使用该技能：

- 全文翻译
- 原文对照
- 中英文对照
- 图文对应
- 图表提取
- 翻译解读
- 全文 Markdown
- paper md
- source-grounded reading notes

## 注意事项

不要把该技能用于摘要、关键词列表或只做引用检索的任务。一旦触发，默认产物应是带有可见 `Original` / `中文` 对照和图表卡片的 `paper.md`，不能只输出中文摘要。
