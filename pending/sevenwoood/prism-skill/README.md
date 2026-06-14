<!--
语言切换导航（页面内锚点跳转）
-->

<div align="center">
  <a href="#简介">简介</a> | <a href="#主要特性">特性</a> | <a href="#安装">安装</a> | <a href="#快速开始">快速开始</a> | <a href="#文件结构">结构</a> | <a href="#许可证">许可证</a>
</div>

<div align="center">
  <a href="README.md">中文</a> | <a href="README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.ko.md">한국어</a> | <a href="README.es.md">Español</a>
</div>

<br>

<div align="center">
  <img src="assets/prism-skill.svg" alt="Prism Skill Banner" width="600">
</div>

# 🔮 Prism Skill · 棱镜

**多学科动态适配分析引擎** —— 对任意事件、观点或片段进行结构化、真实可信的专业解析。支持真实性核查、片段补全、表格/流程图/列表输出，并可一键生成交互式 HTML 报告。

---

## <a id="简介"></a>📖 简介

Prism Skill（棱镜）是一个遵循 Agent Skills 协议的分析型技能。它能够：

- 从**动态适配的学科**（自然科学、社会科学、人文学科等）和**主体视角**（个人、国家、国际、企业等）解析问题；
- **优先保证信息真实**，可应要求执行事实核查，并标注权威来源；
- **自动补全事件片段**，对模糊问题智能追问（最多3轮）；
- **输出柔和、易读**的结构化内容（表格、文本流程图、列表），告别机械的“一句话概述”；
- 支持 **Markdown 导出** 和 **可交互 HTML 报告**（折叠/展开、深色模式、一键复制）。

---

## <a id="主要特性"></a>✨ 主要特性

| 特性           | 说明                                                 |
| -------------- | ---------------------------------------------------- |
| 🌍 多语言自适应 | 自动使用用户输入的语言回复（中/英/日/韩/西最佳）     |
| 🔍 真实性优先   | 触发“真实案例”等关键词时强制事实核查，不编造         |
| 🧩 动态学科适配 | 根据问题自动选择最相关的1-3个学科，不限于固定列表    |
| 👥 多主体视角   | 从微观（个人）到宏观（国际），自由适配               |
| 💬 柔和交互     | 避免刻板标题，使用“简单来说”“咱们拆开看看”等自然表达 |
| 📊 丰富输出     | 表格、列表、文本流程图、Markdown、交互式HTML         |
| ⚙️ 环境降级     | CLI 环境中自动转为纯文本/简单列表                    |
| 🛡️ 伦理边界     | 不提供专业建议、不教唆暴力、尊重隐私、反对歧视       |

---

## <a id="安装"></a>📦 安装

### 方式一：GitHub CLI（推荐）

```bash
gh skill install sevenwooodname/prism-skill prism-skill
```

### **方式二：通用 Skills CLI**

```bash
npx skills add sevenwoood/prism-skill --skill prism-skill
```

### **方式三：手动安装**

```bash
git clone https://github.com/sevenwoood/prism-skill.git
# 将 prism-skill 文件夹复制到以下目录之一：
# - ~/.cursor/skills/
# - ~/.claude/skills/
# - ~/.codex/skills/
```

## <a id="快速开始"></a>🚀 快速开始

**输入示例**：

> “美联储最近加息了，对普通人有影响吗？我想知道真实情况。”

**技能输出**（柔和化示例）：

```text
简单来说：加息会直接增加浮动利率贷款的月供，同时可能抑制物价上涨。

咱们拆开看看：
| 生活领域 | 影响 |
|----------|------|
| 房贷 | 100万贷款每月多还约140元 |
| 存款 | 利息小幅上升 |
| 就业 | 出口相关行业可能承压 |

小结一下：最直接的感受在贷款成本，其他方面影响不大。

如果你还想聊，可以聊聊你的具体贷款情况，或者其他国家的人会怎样？
```

**生成 HTML 报告**：
在任意分析后输入“输出html”，即可获得一个交互式网页报告。

## <a id="文件结构"></a>📁 文件结构

```text
prism-skill/
├── SKILL.md                  # 核心技能定义
├── README.md                 # 本文件（中文）
├── README.en.md              # 英文
├── README.ja.md              # 日文
├── README.ko.md              # 韩文
├── README.es.md              # 西班牙文
├── references/               # 方法论与约束
│   ├── analysis-framework.md
│   ├── source-priority.md
│   └── ethics-boundaries.md
├── examples/                 # 示例对话
│   ├── economic-example.md
│   ├── health-example.md
│   └── social-example.md
└── assets/                   # 静态资源
    └── prism-skill.svg       # Banner 图片
```

## <a id="许可证"></a>📄 许可证

MIT © 2026 Prism Skill Contributors

------

## ⚠️ 语言兼容性注意事项

- **最佳支持语言**：中文、英文（事实核查最准确，输出最流畅）。
- **其他语言**：日语、韩语、西班牙语可正常使用，但复杂语境下的深度分析能力略弱。
- **建议**：对重要分析，可要求技能“先用英文/中文分析，再翻译成当前语言”。
- **事实核查**：不同语言会优先检索对应语言的权威来源；若事件跨境，可明确指定侧重地区（如“请优先使用中国官方数据”）。
