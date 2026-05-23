<p align="center">
  <h1 align="center">🧾 pptx-prep</h1>
  <p align="center"><strong>AI PPT 材料预检协议</strong><br>在 AI 生成 PPT 之前，先检查缺什么，避免返工。</p>
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Proprietary-red" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Claude%20Code-skill-orange" alt="Claude Code Skill"></a>
  <a href="./README.md"><img src="https://img.shields.io/badge/README-English-blue" alt="English"></a>
</p>

---

## 🤔 痛点

```
你: "帮我做一份 7 页的团队介绍 PPT"
AI: 生成完成。
你: 打开一看——
   ❌ 人名编的
   ❌ 照片是握手的通用素材
   ❌ 数据是猜的
   ❌ Logo 的位置是空白
   ...
你花了 30 分钟改本该提前发现的问题。
```

## 💡 pptx-prep 怎么解决

pptx-prep **在生成之前**扫描需求 → 列出你缺什么 → 你一次性提供材料 → AI 生成完整 PPT。一次到位，不返工。

```
你的需求
  → pptx-prep 确认幻灯片结构
  → pptx-prep 逐页扫描：哪些材料 AI 能生成？哪些必须你提供？
  → 你把照片、数据放进 materials/ 文件夹 (或让 AI 搜索)
  → pptx-prep 输出 manifest.yml + 汇总
  → pptx 技能一次性生成完整 PPTX
```

## ⚡ 快速开始

### Claude Code（推荐）

```bash
git clone https://github.com/xiaomengbi520/pptx-prep.git
cp -r pptx-prep ~/.claude/skills/pptx-prep
```

然后在新会话中说"帮我做一份XX PPT"，pptx-prep 自动激活。

### 其他 AI 工具

从 [`prompts/`](prompts/) 复制对应版本的 prompt，粘贴到对话开头。

| AI 工具 | 使用方式 | 文件 |
|---------|---------|------|
| Claude Code | Skill（自动触发） | [`SKILL.md`](SKILL.md) |
| ChatGPT / 聊天工具 | 粘贴到对话开头 | [`prompts/universal.md`](prompts/universal.md) |
| ChatGPT Custom GPT | 一次配置永久使用 | [`prompts/chatgpt.md`](prompts/chatgpt.md) |
| API 集成 | 设为 system prompt | [`prompts/system-prompt.md`](prompts/system-prompt.md) |

## 📋 检查什么

| 类别 | 检查项示例 | 关键词 |
|------|-----------|--------|
| 🧑 个人信息 | 姓名、职位、日期、联系方式 | 团队、成员、姓名、职位 |
| 🖼️ 视觉素材 | 照片、Logo、截图、图标 | 照片、Logo、截图、头像 |
| 📊 数据统计 | 收入、指标、调研结果 | 收入、数据、指标、增长 |
| 🎨 定制品牌 | 口号、品牌色、引用 | 口号、品牌色、愿景、引用 |
| 🔗 外部引用 | 内网链接、参考文档、模板 | 内网、参考文档、模板 |

每项材料标记为：**✅ 可用** / **📌 占位符** / **🤖 待核实**

## 🔄 缺失材料的 4 种处理

| 选项 | 做什么 | 执行时机 |
|------|--------|---------|
| **A) AI 搜索** | 找真实照片，下载到 materials/ | prep 立即执行 |
| **B) AI 生成** | 创建插画/卡通风格图片 | prep 立即执行 |
| **C) 占位符** | 留空，以后补 | 生成时渲染占位符 |
| **D) 我上传** | 用户自己提供 | Phase 5 收集 |

## 📦 输出什么

1. **对话内汇总** — 清晰区分 ✅你提供的 / 🤖AI 生成需审核 / 📌占位符
2. **manifest.yml** — 结构化清单。人类可读，机器可解析（见 [schema](manifest.schema.json)）
3. **materials/ 目录** — 所有收集的文件。A/B 选项的结果也自动放入

## 📁 示例

| 场景 | 演示 |
|------|------|
| 团队介绍 PPT（7 页） | [需求→bad output→manifest→结果](examples/scenario-team/) |
| 融资路演 PPT（10 页） | [需求→manifest](examples/scenario-pitch/) |

打开 `examples/scenario-team/` 看有 prep vs 没 prep 的落差。

## 🛠️ 工具

| 工具 | 用途 | 依赖 |
|------|------|------|
| `validate.py` | 校验 manifest.yml 结构 | **零依赖**（仅 Python stdlib） |
| `manifest.schema.json` | JSON Schema 结构合同 | 供 IDE / CI 使用 |

```bash
python validate.py manifest.yml
# → Validation PASSED — 12 materials, all checks passed.
```

## 📂 项目结构

```
pptx-prep/
├── SKILL.md                  # Claude Code skill（主推）
├── prompts/                  # 多平台 prompt 模板
│   ├── universal.md          #   粘贴版 — 所有聊天工具通用
│   ├── chatgpt.md            #   ChatGPT Custom GPT 配置
│   └── system-prompt.md      #   API system prompt
├── manifest.schema.json      # manifest 的结构合同
├── PLACEHOLDER_SPEC.md       # 占位符数据格式规范
├── validate.py               # 零依赖 manifest 校验器
├── examples/
│   ├── scenario-team/        #   团队介绍 — before/after 对比
│   └── scenario-pitch/       #   融资路演 — 完整 manifest
├── README.md                 # 英文版
└── README_CN.md              # 你在这里（中文版）
```

## ❓ 常见问题

**Q: pptx-prep 能生成 PPT 吗？**
不能。它只做材料预检。生成交给下游 PPTX 工具（pptx skill、python-pptx、PptxGenJS 等）。

**Q: 我不想用 Claude Code，能在 ChatGPT 上用吗？**
可以。复制 `prompts/universal.md` 的内容粘贴到 ChatGPT 对话开头，同样的效果

**Q: 一定要提供所有材料吗？**
不。缺失的照片选 A（AI 搜索）或 C（占位符）。缺失的文字 AI 自动生成，标记 `needs-review`。

**Q: manifest.yml 有什么用？**
给下游 PPTX 工具的结构化输入——哪些文件放哪页、宽高比怎么处理。也给用户一目了然的清单。

**Q: 怎么校验 manifest 写对了？**
运行 `python validate.py manifest.yml`，零依赖。

## 📄 协议

Proprietary. 详见 [LICENSE](LICENSE.txt)。

---

<p align="center">
  <sub>Built with ❤️ for AI + PPT workflows</sub>
</p>
