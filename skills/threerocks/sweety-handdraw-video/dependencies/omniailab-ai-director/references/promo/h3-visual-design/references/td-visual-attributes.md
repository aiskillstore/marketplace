---
name: omniailab-promo-h3-visual-design-td-visual-attributes
description: 「视觉风格参考库 / Visual Style Attributes Reference」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：[Visual style]
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 视觉风格参考库 / Visual Style Attributes Reference

> **用途**：从 17 张参考图里提取的**可量化视觉属性**，作为 AI 视频生成的 prompt 风格层参考。
> **不含**内容共性（人物/场景/主题）——只沉淀**视觉处理方式**。
> **由 `td-cv-tracking` 路线通过 Prompt 片段按需引用**。

---

## 1. 色彩 / Color

### 1.1 整体饱和度
- **状态**：低饱和（饱和度约 30-50%）
- **prompt 描述**：`low saturation palette`, `desaturated tones`, `muted colors`, `faded color`
- **不要**：❌ 高饱和鲜艳色（纯红/纯蓝/纯黄），❌ 平面化色彩

### 1.2 冷暖分离 / Color Temperature Split（teal/orange grading）
- **状态**：必有——**这是参考库最一致的色彩特征**
- **机制**：阴影偏冷（cyan / 蓝 / 冷绿）+ 高光偏暖（橙 / 粉 / 黄）
- **强度**：中等（不是极端 teal/orange，而是"自然倾向"）
- **prompt 描述**：`teal-and-orange color grading`, `cinematic color split with cool shadows and warm highlights`, `split toning with cool shadows / warm highlights`

### 1.3 主导色相
- **状态**：单色相主导
- **常见**：蓝 / cyan / 灰蓝
- **机制**：画面有一个统一色调倾向，**不是多色相混战**
- **prompt 描述**：`blue-dominant color palette`, `monochromatic-leaning with cool tone`

### 1.4 暗部 / Black Point
- **状态**：压实但不死黑
- **数值**：black point 提到 5-15（vs 纯 0）
- **prompt 描述**：`lifted blacks`, `crushed but not pure black`, `shadows hold a touch of color`
- **不要**：❌ 死黑（pure black everywhere）

### 1.5 高光 / Highlight
- **状态**：偏柔、不爆
- **prompt 描述**：`rolled-off highlights`, `preserved highlight detail`, `no blown-out whites`
- **不要**：❌ HDR 感（过曝 + 高光全亮）

---

## 2. 对比度 / Contrast

### 2.1 整体对比
- **状态**：中-高对比
- **数值范围**：对比度 +20 到 +40（vs 默认 0）
- **prompt 描述**：`high contrast`, `deep blacks with preserved highlights`, `strong contrast but not crushed`

### 2.2 阴影 / Shadow Density
- **状态**：暗部细节少、大量区域直接黑掉
- **作用**：作为构图元素（剪影感）
- **prompt 描述**：`dark shadows with little detail`, `silhouette composition`, `subjects as shapes in shadow`

---

## 3. 画面质感 / Texture

### 3.1 胶片颗粒 / Film Grain ⭐⭐⭐
- **状态**：**必有** —— 17 张图最一致的属性
- **强度**：中-高
- **prompt 描述**：`heavy film grain`, `analog texture`, `35mm film grain`, `high ISO noise`, `grainy photographic look`
- **重要性**：这是这个参考库的**核心标志**，比色彩还重要

### 3.2 复古瑕疵 / Vintage Artifacts
- **状态**：50% 概率出现
- **类型**：划痕、网点、暗角、褪色、偏色
- **prompt 描述**（可选）：`subtle vintage artifacts`, `light scratches and dust`, `slight color shift, aged film look`, `risograph print texture`
- **不要过度**：❌ 满屏划痕、❌ 强烈斑点

### 3.3 边缘处理 / Edge Treatment
- **状态**：常见
- **类型**：轻微暗角（vignette）、边缘柔化（lens diffusion）
- **prompt 描述**：`subtle vignette`, `soft lens diffusion at edges`, `slight falloff at frame edges`

### 3.4 锐度 / Sharpness
- **状态**：中等（不追求极锐）
- **prompt 描述**：`natural sharpness`, `not over-sharpened`, `organic detail`
- **机制**：颗粒 + 复古瑕疵自然降低锐度感

---

## 4. 灯光 / Lighting

### 4.1 风格
- **状态**：电影感打光
- **机制**：单点强光源 / 侧光 / 逆光
- **prompt 描述**：`cinematic lighting`, `single key light`, `side-lit or backlit subject`, `moody dramatic lighting`

### 4.2 剪影 / Silhouette
- **状态**：常见
- **机制**：主体作为剪影、暗部细节少
- **prompt 描述**：`silhouette composition`, `subject against bright background`, `subjects as dark shapes`

### 4.3 混合色温 / Mixed Color Temperature
- **状态**：常见
- **机制**：冷暖光源同时存在（舞台灯 / 室内灯 / 霓虹）
- **prompt 描述**：`mixed color temperature lighting`, `cool ambient + warm practical light`, `multiple light sources of different temperatures`

---

## 5. 镜头/光学 / Lens & Optics

### 5.1 景深 / Depth of Field
- **状态**：浅景深
- **prompt 描述**：`shallow depth of field`, `subject in focus, background bokeh`, `cinematic portrait lens feel`

### 5.2 镜头瑕疵 / Lens Imperfections
- **状态**：40% 概率
- **类型**：眩光（flare）、光晕（light leak）、轻微过曝（highlight bloom）
- **prompt 描述**（可选）：`subtle lens flare`, `light leak`, `highlight bloom from bright light source`

---

## 6. 后期处理总览 / Post-Processing Summary

| 维度 | 状态 |
|---|---|
| 色调曲线 | lift blacks, roll-off highlights |
| 饱和度 | 降低 30-50% |
| 颗粒 | 中-高强度（必有） |
| 暗角 | 轻微 |
| 锐化 | 不锐化或轻微 |
| 冷暖分离 | teal shadows / orange highlights（必有） |
| 复古瑕疵 | 可选 50% |
| 暗部 | 压实 + 大量黑区（剪影感） |
| 高光 | 偏柔、保留细节 |

---

## 7. 风格关键词 / Style Keywords（直接放进 prompt）

`filmic` / `lo-fi` / `indie` / `retro` / `cinematic` / `35mm film` / `analog photography` / `magazine editorial` / `fashion editorial` / `Kodak Portra`-like / `Fuji 400H`-like

---

## 8. 反面（要避免的）

- ❌ 高饱和鲜艳色
- ❌ 干净数字感（无颗粒）
- ❌ 平面化打光（无阴影对比）
- ❌ 均匀色温（无冷暖分离）
- ❌ 过度锐化
- ❌ HDR 感（过曝 + 高光全亮）
- ❌ 死黑暗部
- ❌ 完美无瑕（要保留"不完美"的质感）

---

## 9. 怎么用这个库

### 9.1 在 prompt 里直接引用（精简版）

```text
[Visual style]
- Low saturation, desaturated palette
- Teal/orange split tone color grading (cool shadows, warm highlights)
- Strong film grain (35mm analog feel)
- High contrast with lifted blacks, preserved highlights
- Cinematic single-key lighting, mixed color temperature
- Shallow depth of field, subtle vignette
- Style keywords: filmic, lo-fi, cinematic, indie
```

### 9.2 跟 实时视觉与追踪 追踪表现叠加

实时视觉与追踪 路线的 5 要素（框/线/数字/反转/同步）**保持不变**；
底层视频的"颜色/对比度/质感"按这个 reference 走；
最终效果 = "TD 追踪可视化 + filmic 调色"。

在 实时视觉与追踪 路线的基线 Prompt 的 `[Technical]` 段之后，**追加**：
```text
[Visual style — pull from `td-visual-attributes.md`]
Apply the visual style reference: desaturated palette, teal/orange split tone, strong film grain, cinematic single-key lighting, shallow depth of field, lifted blacks, subtle vignette.
```

### 9.3 用户输入映射

当用户在 Q2 说风格关键词时，按这个 reference 库映射到具体参数：

| 用户说法 | 映射参数 |
|---|---|
| 末日风 / 废土 | 高对比 + 深暗部 + 蓝绿冷调 + 强颗粒 |
| 赛博朋克 | 强霓虹 + 紫粉 + 高对比 + 高光 bloom |
| 极简 | 干净 + 高调 + 留白 + 弱颗粒（甚至不要） |
| 复古胶片 | 重颗粒 + 偏色 + 暗角 + 划痕 |
| 黑白 | 完全去饱和 + 强对比 + 暗部压实 |
| 港风 / 复古 | 橙黄暖调 + 中颗粒 + 复古偏色 |
| cyber / 数字冷感 | 蓝绿 + 高对比 + 干净（少颗粒）+ neon |

### 9.4 自由组合

这套库是**可拼装的**：
- "末日 + 黑白" → 黑白 + 末日（高对比深暗）
- "复古 + 赛博朋克" → 强颗粒 + 紫粉霓虹
- "极简 + 黑白" → 黑白 + 弱对比 + 干净

用户能想到的组合基本都能拼出来。

---

## 10. 元信息

- **参考样本数**：17 张
- **来源**：用户提供（"我喜欢的风格.zip"）
- **属性提取方式**：目视观察 + 风格摄影/调色行业通用描述
- **不包含**：内容/题材/情绪分析——那是另一类问题
- **维护**：v1，可根据用户反馈持续补充/调整

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
