# `nature-paper2ppt` 技能

`nature-paper2ppt` 用于把科研论文转换为简洁中文 PowerPoint，用于文献汇报、组会、实验室会议或论文分享，并以 Nature 风格证据叙事组织内容。

该技能可以接收论文 PDF、预印本、文章文本、摘要加图注，或结构化阅读笔记。它会识别论文类型、提取科学论证、只选择支撑论证的关键图表，撰写中文幻灯片内容和演讲备注，生成真实 `.pptx`，并做轻量级包体 QA。

## 功能

- 将科研论文转换为 10-16 页中文演示文稿。
- 使用论文的科学论证作为幻灯片主线，而不是照搬章节顺序。
- 先判断论文类型，再选择叙事逻辑。
- 把关键图、表或面板作为证据，而不是装饰。
- 当完整大图难以阅读时，对密集图版进行裁剪或拆分。
- 撰写中文标题、精简 bullet、图注、takeaway 和 speaker notes。
- 生成可编辑的 `.pptx` 作为主交付物。
- 提取图表时记录 asset manifest。
- 对页数、嵌入媒体、speaker notes 和 PPTX 包结构做轻量 QA。

## 来源与设计层级

- Nature 风格科学叙事：问题、缺口、claim、证据、验证、复用价值、局限和讨论。
- 学术 journal club 实践：面向现场报告的短幻灯片，而不是密集读书笔记。
- 证据优先的幻灯片设计：结果页尽量以一个主图或主表为核心。
- 低开销生产：只有在实质提升成稿质量时，才做耗时的 OCR、图像提取和渲染。

## 文件结构

该技能采用 router/static-dynamic 结构：短 `SKILL.md` 路由配合 `manifest.yaml`，只加载当前任务需要的片段。

```text
nature-paper2ppt/
├── SKILL.md                     # 短路由：识别 paper_type，加载 fragments
├── manifest.yaml                # always_load core + paper_type axis + 按需 references
├── README.md
├── static/
│   ├── core/                    # 始终加载
│   │   ├── principles.md        # 目的、核心原则、lean mode、输入、语言
│   │   ├── toolchain.md         # 跨平台 Python 栈与默认快速路径
│   │   ├── workflow.md          # 9 步主线
│   │   └── output-and-quality.md# 输出包、引用、质量、fallback 规则
│   └── fragments/
│       └── paper_type/          # 每类论文一条汇报弧线
│           ├── discovery.md     # question-to-evidence
│           ├── methods.md       # problem-to-solution
│           ├── resource.md      # workflow-to-validation
│           ├── clinical.md      # design-to-inference
│           ├── materials.md     # property-to-mechanism / design-to-performance
│           └── review.md        # evidence-map
└── references/                  # 按需打开
    ├── design-and-layout.md     # 构图、版式、字体、反模板、页面原型
    ├── figure-assets.md         # 图表选择、提取、裁剪自查
    └── self-review.md           # 自审循环、严重程度、程序检查、验证
```

共享术语表 `../_shared/core/terminology-ledger.md` 会在每次任务中加载，以保证幻灯片中的技术术语一致。

## 适用场景

- 根据研究论文 PDF 制作 PPT 或 PPTX。
- 准备 journal club、组会、实验室会议、论文分享或学位汇报。
- 将 Nature 系列论文总结成中文幻灯片。
- 把文章文本、图注或阅读笔记转成演示文稿。
- 需要图文结合的 deck，而不只是大纲或摘要。
- 需要 speaker notes、来源标签和 QA 报告。

## 默认输出包

默认输出是一个小型工作目录：

```text
output/
├── final_presentation_cn.pptx
├── qa_report.md
├── asset_manifest.md          # 提取源图表时生成
└── assets/
    └── figures/
```

如果有助于审阅或调试，可以额外生成大纲或讲稿文件，但 `.pptx` 始终是主交付物。

## 汇报逻辑

默认叙事弧线帮助听众回答：

1. 这个问题为什么重要？
2. 论文解决了什么缺口或瓶颈？
3. 作者做了什么？
4. 关键证据是什么？
5. 为什么结果可信？
6. 新意、可复用价值或广泛意义在哪里？
7. 边界和开放问题是什么？

技能会按论文类型调整这条弧线。Discovery paper 使用 question-to-evidence 逻辑；methods、AI 和工具论文使用 problem-to-solution；resource 和 atlas 论文使用 workflow-to-validation；review 使用 evidence-map 结构。

## 设计意图

该技能应创建可直接用于学术口头报告的 deck。它应简洁、图表主导、证据敏感，不能编造源论文没有支持的数值、方法、机制、数据集或图像解释。

密集结果图应裁剪、拆分或单独成页，不能压缩进不可读的对称双栏版式。幻灯片正文要短，深入解释放进 speaker notes。

## 注意事项

- 默认语言为简体中文，同时保留重要技术术语、缩写、基因名、模型名、公式和统计术语的英文。
- 该技能适用于多个研究领域，不限于生物医学论文。
- 如果没有可靠的 headless renderer，技能会进行结构 QA，并记录跳过渲染预览 QA 的原因。
