# `nature-polishing` 技能

`nature-polishing` 用于把学术手稿文本润色、重构或翻译成更接近 `Nature` 风格的简洁英文。

## 来源层级

- `Main strategy`：`Chapter1-Week1-7 full version.pdf` 中的写作课程笔记。
- `Published article patterns`：精选 Nature 与 Nature Communications 论文范式。
- `Reference support`：`Academic-Phrasebank-Navigable-PDF-2023.pdf`。

## 当前变化

- 主 `SKILL.md` 已按第一份 PDF 的架构重写：论文类型、读者工作流、沙漏结构、写作顺序、各部分职责、intellectual debt 以及 AI/ethics 边界。
- 全文级润色可以使用已发表论文范式，覆盖摘要、引言、结果、讨论、结论和标题。
- `references/` 现在承担更窄的职责：短语族、move template 和风格检查主要来自第二份 PDF。
- 技能会区分 `research papers` 与 `methods papers`。
- 技能把 `core argument ownership` 视为核心规则，而不是附带提醒。

## 文件结构

```text
nature-polishing/
├── SKILL.md
├── README.md
└── references/
    ├── published-article-patterns.md
    ├── phrasebank-playbook.md
    ├── section-moves.md
    ├── style-guardrails.md
    ├── writing-strategy.md
    └── latex-layout.md
```

## 适用场景

- 润色摘要、引言、结果、讨论、结论或标题。
- 润色 methods section，或处理强调公平比较逻辑的 methods paper。
- 将中文学术文本翻译成可投稿英文。
- 投稿前收紧章节逻辑。
- 降低过度声称，修正证据强度不匹配的措辞。
- 在不编造内容的前提下，让文本更像高水平期刊英文。
- 修复 LaTeX 排版问题：页面过松、标题孤立、图片未填满页面或跨页、`Float too large`、多面板图排列、Supplementary Information 页面稀疏等。

## 设计意图

该技能应当：

- 保留事实、引用意图和作者责任。
- 以第一份 PDF 作为主导写作策略。
- 改善段落层面的修辞顺序。
- 保持句子短、清楚、可读。
- 只把第二份 PDF 作为短语和参考层。
- 避免通用 AI 腔和无支撑声称。

## 参考文件

- `section-moves.md`：各章节顺序与 move pattern。
- `published-article-patterns.md`：精选 Nature 与 Nature Communications 论文写法。
- `phrasebank-playbook.md`：hedging、过渡、证据、局限和未来工作表达。
- `style-guardrails.md`：英式风格、冠词、缩写、单位、语域和过度声称控制。
- `writing-strategy.md`：段落与章节层面的论证逻辑。
- `latex-layout.md`：LaTeX 浮动体和页面排版，包括顶端对齐、`\clearpage` + `[H]` 标题-图片单元、`placeins` 注意点、源头重绘又宽又矮的图、多面板堆叠，以及渲染后生成 contact sheet 的诊断流程。

## 注意事项

- 该技能用于润色和结构重组，不用于编造科学内容。
- 主要策略规则位于 `SKILL.md`；参考文件不应覆盖这些规则。
- 参考文件有意保持选择性，用于辅助判断，而不是鼓励套话堆砌。
