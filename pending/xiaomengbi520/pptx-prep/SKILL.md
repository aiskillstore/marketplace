---
name: pptx-prep
description: "Materials pre-check before any PPTX generation. ALWAYS run this skill FIRST when the user asks to create, generate, or make a presentation, slides, deck, or PPT. Analyzes requirements to identify human-dependent materials — names, photos, logos, data, statistics — that AI cannot invent. Collects all materials upfront or confirms skip decisions, eliminating rework. After completion, hands off directly to the available PPTX generation skill."
---

# PPTX Material Pre-Check

Run this skill **before** any PPTX generation. The goal: stop AI from inventing content that should come from a human.

## Core Principle

**Never guess what the user can provide. Never let the user discover problems only after the PPTX is generated.**

---

## Workflow

### Phase 1: 确认幻灯片结构

如果用户没有给出清晰的逐页大纲，问 3-5 个问题：

1. 几页 PPT？
2. 主题 / 场景是什么？
3. 关键模块有哪些？（封面 → 团队 → 里程碑 → 成果 → 总结）

输出骨架让用户确认：

```
## 幻灯片结构（请确认或调整）
1. 封面 — [标题]
2. 团队 — [成员]
3. 里程碑 — [时间线]
4. 成果 — [数据]
5. 总结 — [联系方式]
```

**未确认结构前不进入下一步。**

### Phase 2: 扫描人类依赖材料

逐页检查，对每项材料标记状态。使用以下图标：

| 图标 | 状态 | 含义 |
|------|------|------|
| ✅ | 可用 | 材料已就绪，无需用户操作 |
| ❌ | 需补充 | 必须由用户提供（照片、数据、Logo） |
| 🤖 | 待核实 | AI 可以生成初稿，但准确性需要用户确认 |

用以下格式输出：

```
## 材料扫描

| Slide | 材料 | 类型 | 状态 |
|-------|------|------|------|
| 1 封面 | 标题文案 | 文字 | ✅ 可用 |
| 1 封面 | 封面照片 | 照片 | ❌ 需补充 |
| 2 简介 | 人物基本信息 | 文字 | 🤖 待核实 |
| 3 数据 | Q2收入数字 | 数据 | ❌ 需补充 |
```

#### 5 大类检查依据

**类别 1：个人信息** — 姓名、职位、日期、联系方式
关键词: 团队介绍、成员、负责人、姓名、职位、联系方式、日期

**类别 2：视觉素材** — 照片、Logo、截图、图标
关键词: 照片、Logo、截图、头像、图标、海报

**类别 3：数据统计** — 收入、指标、调研结果、规格
关键词: 收入、数据、指标、增长、统计、营收

**类别 4：定制品牌** — 口号、品牌色、引用、术语
关键词: 口号、品牌色、愿景、标语、引用

**类别 5：外部引用** — 内网链接、参考文档、模板
关键词: 内网、参考文档、模板、链接、以往PPT

### Phase 3: 缺失阈值判断

统计材料总数。若 ❌ 需补充 占比 **> 50%**，警告用户：

> "⚠ 超过一半的材料缺失——AI 将被迫编造大量内容。建议先提供核心材料再继续，否则生成结果可能充满占位符。是否仍然继续？"

若 ❌ ≤ 50%，继续。剩余缺口逐项处理。

### Phase 4: 内容生成分层

| 层级 | 条件 | 标记 |
|------|------|------|
| 🤖 待核实 | AI 能起草但准确性重要（如公司介绍、市场分析） | `source: ai` `confidence: needs-review` |
| ✅ 可生成 | 通用知识，无需个性化（如 HTTP 原理、通用流程） | `source: ai` `confidence: verified` |
| ❌ 人类依赖 | 必须用户提供（如团队照、真实营收、Logo） | 进入 Phase 5 |

层级-1（可生成）直接放行。层级-2（待核实）生成但标记审核。层级-3（人类依赖）进入材料收集。

### Phase 5: 收集材料

**当用户说"我有照片/材料"时：**

先在项目目录创建材料文件夹，告知用户路径：

> "我在项目目录下创建了 `materials/` 文件夹。请将文件放入其中：
> - Slide 1: 封面照片
> - Slide 4: Q2收入数据
> - ..."

用户放入文件后告知你，你扫描 `materials/` 目录，**自动匹配**文件到对应槽位：
- 分析文件内容（看图/读数据）
- 文件名信号
- manifest 中的 `description` 字段

匹配后，**给出完整对照表**：

> "自动匹配结果：
> | 材料槽位 | ← 文件 | 依据 |
> |----------|--------|------|
> | Slide 1 封面照 | ✅ materials/photo.jpg | 人物肖像，竖版 |
> | Slide 4 Q2收入 | ✅ materials/数据.xlsx | 表格含数字 |
> | Slide 1 Logo | ✅ materials/logo.png | Logo图形 |
>
> 全部匹配成功。有需要调整的吗？"

**若用户纠正了匹配（如"R.png是颁奖现场不是工作照"）：** 必须重新输出完整对照表，不能只说"已更新"。

### Phase 6: 照片宽高比检查 + 即时选项

当用户照片宽高比与幻灯片槽位偏差 >10%，**立刻给出 A/B/C 选项**，不等：

> "⚠ Slide 6 的照片槽位是 16:9 横版，但 R.png 是 1:1 方形。如何处理？
>  **A)** contain — 完整显示照片，左右留白
>  **B)** cover — 铺满画面，上下被裁切
>  **C)** 我换一张照片"

**不要只标记风险而不给选项。** 每个不匹配的照片都要立刻问。

若用户选择 A 或 B，记录为 `fill_mode`。若选 C，等新照片后重新检查。

### Phase 7: 质量门禁

检查每份材料，不达标则拒绝 + 解释 + 给选项：

- 照片任意维度 < 200px → "照片太小（200×150px），放大后会模糊。请换更大的，或接受继续。"
- 内容类型明显错误（如 Logo 位传了一张猫的照片）→ 指出，确认是否更换。

**永远不阻塞——始终给"接受并继续"的选项。**

### Phase 8: 内容溢出检查

文本/数据量 vs 槽位容量估算：
- 标题页: ~20 字
- 正文块: ~150 中文字
- 数据表格: ~5 行 × 5 列

内容超过容量 × 1.5：

> "⚠ Slide 3 的文字约 320 字，槽位设计约 150 字。AI 会自动缩小字号，可能显得拥挤。建议：
>  - 精简到 150 字以内
>  - 拆成 2 页（⚠ 不推荐——新增页可能与模板风格不一致）
>  - 继续，让 AI 处理"

超过容量 × 3 时，"拆页"选项必须附带"不推荐"警告。

### Phase 9: 缺失项处理

对于用户没有的材料：

> "Slide 7: 获奖照片 — 你没有。怎么处理？
>  **A)** AI 搜索图片 — 我帮你找合适的真实图片
>  **B)** AI 生成图片 — 创建一张插画/卡通风格图片
>  **C)** 保留占位符 — 留空，以后自己补
>  **D)** 我上传 — 稍后提供照片"

- **A → prep 立即搜索。** 使用可用工具搜索真实图片，下载到 `materials/`，展示结果让用户确认。确认后 manifest 中改为 `status: ready` + `source: ai-search` + `confidence: needs-review`。
- **B → prep 立即生成。** 使用图像生成工具创建插画风格图片，下载到 `materials/`，展示结果让用户确认。确认后 manifest 中改为 `status: ready` + `source: ai-generated` + `confidence: needs-review`。
- C → `status: placeholder`
- D → 等待用户上传，然后回到 Phase 5 收集材料

**A/B 选项的关键约束：**
- 搜索/生成必须在 Phase 9 内完成，不能标记 `ai-fill` 然后留给下游
- 结果下载到 `materials/` 目录
- 展示结果让用户确认
- 移交 pptx 前，manifest 中不应存在任何 `ai-fill` 状态的项。

**必须保留 D 选项。** 用户可能一开始说没有，随后又找到了。

### Phase 10: 输出 manifest

在项目目录写入 `manifest.yml`。结构：

```yaml
manifest_version: "1.0"
project:
  title: "..."
  slide_count: N
materials:
  - field: unique_key
    type: photo | text | data | branding | reference
    description: "..."
    used_in: [slide-N]
    status: ready | placeholder
    source: ai | ai-search | ai-generated | user
    confidence: verified | needs-review | placeholder
    path: "materials/filename.jpg"    # if ready
    slot:                             # for photo type
      aspect_ratio: "16:9"
      fill_mode: cover
    warnings: []                      # optional
summary:
  total: N
  ready: N
  placeholder: N
  needs_review: N
```

### Phase 11: 输出汇总

用中文 + 图标清晰区分：

```
## 材料检查完成

### ✅ 你提供的 (3)：
- 封面照   ← materials/photo.jpg (Slide 1)
- 公司Logo ← materials/logo.png (Slide 1)
- Q2收入   ← materials/数据.xlsx (Slide 4)

### 🤖 AI 生成，请审核 (2)：
- 公司简介 (Slide 2) — AI 撰写，请核实数据准确性
- 里程碑描述 (Slide 3) — AI 编写了时间线文字

### 🔍 AI 将自动填充 (1)：
- 获奖照片 (Slide 7) — 用户选择让 AI 搜索

### 📌 占位符 (0)：
- 无
```

### Phase 12: 内部移交

**移交前自查：**
- manifest 中不应有 `status: ai-fill` 的项（已在 Phase 9 处理完毕）
- manifest 中不应有 `status: missing` 的项（已全部收集或标记 placeholder）
- 所有用户提供的文件已放入 `materials/` 目录

**动态检测可用的 PPTX 生成 skill：**

回顾可用 skills 列表，优先使用 `pptx`。若存在其他 PPTX 相关 skill，使用匹配的那个。找不到时：

> "材料已就绪。我未检测到可用的 PPTX 生成 skill。请确认你安装了哪个。"

检测到后：

> "材料就绪。开始生成 PPTX。"

调用该 skill。**不要求用户复制或开新对话。同会话内完成。**

---

## Key Rules

1. **不猜测。** 不在对话或项目文件中的，标记缺失。
2. **说具体。** "Slide 2 缺团队照" 而不是 "缺一些照片"。
3. **不过度标记。** 用户已提供的文字内容，不因"可能想改"而标记。
4. **先查项目目录。** 标记缺失前先确认项目里没有。
5. **尊重选择。** 用户说跳过就跳过，不反复追问。
6. **自动匹配优先。** 不过度要求用户改名，用内容分析匹配。
7. **警告不阻塞。** 质量问题给警告 + 提供继续选项。
8. **一对话完成。** prep → 收集 → 生成，从头到尾不换会话。
9. **Phase 6 即时选项。** 检出宽高比不匹配时，立刻给 A/B/C，不延后。
10. **纠正后重列。** 用户调整匹配后，重新输出完整对照表，不只回一句。
11. **动态发现下游工具。** 不硬编码 "pptx"，检测实际可用的生成 skill。

---

## Examples

### 示例 1：团队介绍 PPT（高缺失）

用户: "帮我们英语小组做 7 页介绍陆鸿的 PPT"

| 材料 | 状态 |
|------|------|
| 小组成员姓名 (Slide 1) | ❌ 需补充 |
| 陆鸿照片 (Slide 2-7) | ❌ 需补充 |
| 内容故事 (来自 tips.txt) | ✅ 可用 |
| 幻灯片结构 (7 页) | ✅ 可用 |

❌ > 50% → 警告用户，建议先提供核心材料。

### 示例 2：简单教程 PPT（零缺失）

用户: "做 3 页解释 HTTP 原理的 PPT"

| 材料 | 状态 |
|------|------|
| HTTP 内容 | ✅ 可生成 |

无人类依赖材料。直接移交 PPTX 生成。

### 示例 3：混合场景

用户: "做融资路演 PPT" + 提供了公司名、团队信息、产品截图

| 材料 | 状态 |
|------|------|
| 公司名、团队信息 | ✅ 可用 |
| 产品截图 | ✅ 可用 |
| Logo | ❌ 需补充 |
| 财务预测 | ❌ 需补充 |

❌ ≤ 50%。收集 Logo + 数据选择，然后生成。
