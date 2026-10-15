---
name: omniailab-promo-h3-visual-design-style-tech-particle
description: 「科技粒子风｜H3 执行规则」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：只在用户选择“科技粒子风”，或内容需要精密、数字化、扫描、能量聚合与轻量界面感时读取本文件。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 科技粒子风｜H3 执行规则

只在用户选择“科技粒子风”，或内容需要精密、数字化、扫描、能量聚合与轻量界面感时读取本文件。科技感必须来自有因果的粒子、光线、扫描和几何字形，不来自随机 HUD、乱码或伪代码。

## 1. 视觉参数

### 色盘

采用“深底 + 冷白文字 + 一个能量色”：

- 深底：近黑 `#05090F`、深海军蓝 `#071726` 或继承原片暗部。
- 主文字：冷白 `#EAF6FF` 或浅灰蓝 `#C9DFEA`。
- 能量色：电青 `#22D3EE`、冰蓝 `#4CA6FF` 或酸性绿 `#9CFF57` 三选一。
- 警示色仅在语义真实需要时使用橙红 `#FF5C45`，占比不超过 8%。

原片为明亮场景时，不强制压暗全片；改用深色几何文字 + 单一电青描边。禁止把所有画面覆盖成蓝黑“科技滤镜”。

### 字体骨架

- Display A：宽几何无衬线或高字重窄体 grotesk，字面清楚、直线端点，承担全屏实心 Hero 与空间墙面字。
- Display B：模块化断口字或几何线框黑体，承担第二 Hero、轮廓字阵和字腔/框架转场；断口不破坏识别。
- Utility：中等字重等宽/半等宽或中性黑体，只显示真实白名单标签、字幕和部件名。
- Marks：透明网格板、轮廓框、扫描线、粒子轨迹、真实连接线；不生成编号、坐标、百分比或代码，除非用户提供。
- 材质：Display A 以实心为主；Display B 可用单层 1%–2% 发光轮廓/透明板；Utility 保持平面高对比。

### 层级

- `Full-frame Hero`：Display A/B 占 75%–115%，至少一次成为全屏色场、墙面字或镜头入口。
- `Spatial Hero`：占 30%–70%，位于后墙、地面、透明板或产品后景。
- `Utility`：占 6%–18%，连接真实主体或动作节点。
- 一个状态可同时有一个 Hero、一个 Utility、一个透明框/网格和一条粒子轨迹；只有粒子聚合、扫描或镜头穿越之一承担最强运动。

## 2. 语言分支

### English

- Hero 优先 1–3 个 ALL CAPS 单词。
- 可用窄体、斜切端点或局部断线，但断线不得改变字母识别。
- 等宽辅助文字只显示白名单内容；不生成 `SYSTEM 01`、`LOADING`、`DATA` 等伪科技词。

### Chinese

- 使用高字重几何黑体；保留方形字面、偏旁比例和清晰笔画交叉。
- 粒子可以沿外轮廓和笔画顺序聚合，但不能把汉字打散成不可识别的英文式碎片。
- 扫描揭示按整字或语义词组进行；不要逐笔随机闪烁。

### Mixed

- 每个状态由一种语言承担 Hero，另一种语言使用语义不同的次级文案或 1–2 个具体标签；全片在不同状态中交换主次并完成 `COPY_DECK`，不把辅助语言限制成全片只有一个词。
- 英文等宽标签与中文 Hero 分开基线，尺寸比为 1:2.8–1:4。
- 不自动补充序号、坐标、单位、日期或逐字翻译，也不用 `FLOW / GRID / LINK` 等孤立技术词填版。

## 3. 空间、景深与遮挡

- 粒子文字优先从主体高光、屏幕反光、物体边缘、地面光带或现有运动轨迹产生。
- Hero 可置于中景，允许主体轮廓短暂从字前穿过；人脸和嘴必须保持前景清楚。
- Annotation 用一条细线连接到真实物体边缘，线端必须触达目标；不画向空气。
- 所有发光半径不超过字高的 8%；不能形成覆盖整片的雾状 bloom。
- 文字与背景对比不足时先加 40%–65% 不透明度的局部深色底片，不改变全片曝光。

## 4. 字体运动语法

### 粒子聚字

```text
在[真实高光/物体边缘/文字轮廓]产生 60–120 个细小发光粒子。粒子沿可见的[直线/弧线/主体运动轨迹]移动，在 0.45–0.80 秒内聚合成准确文字“[TEXT]”。聚合结束后，粒子停止移动并形成完整实心字；保持拼写准确、稳定可读至少 0.8 秒。下一次[动作/声音触发]只让外轮廓发出一次扫描脉冲。退出时，文字从进入方向的反向边缘开始拆成粒子，并回到原高光/物体边缘；不要随机散满画面。
```

### 扫描揭示

```text
一条宽度为字高 4% 的电青扫描线从左到右穿过“[TEXT]”，扫描线经过的区域才显示完整实心字。0.35 秒完成揭示，随后移除扫描线，保持文字稳定可读。退出时同一条扫描线反向扫回，文字在其后消失。
```

### 数据切片响应

```text
在[重音/物体接触]时，把“[TEXT]”水平分成 3 个等高切片；中间切片向右错位不超过字宽 4%，持续 2–3 帧后立即复位。完整字形、拼写和基线不变；只触发一次。
```

禁止持续故障、整句乱码、字符滚动、无限加载动画或粒子永远悬浮。

## 5. 小特效连续性

粒子和光线使用同一条因果链：

```text
[visible source] emits [countable particles/light line] → follows [specific path] → forms or touches [exact text] → produces [one response] → returns to [source] or is absorbed by [text/object]
```

可执行示例：

```text
Eighty cyan particles detach from the moving metallic highlight on the object's right edge, travel along that same edge path, converge into the exact word "[TEXT]" in the upper-right negative space, become a solid readable word for 1.0 second, then reverse along the same path and merge back into the metallic highlight.
```

```text
A thin cyan line grows from the subject's visible contact point to the lower-left corner of "[TEXT]". When it touches the word, one outline pulse travels clockwise around the letters and stops at the contact point. The line retracts to the original contact point; no extra interface appears.
```

## 6. 两种视频模式

### 锁定原片，只做包装

- 不改变原片亮度、调色、场景或镜头来“制造科技感”。
- 从原片真实高光、边缘、动作路径或声音重音中选择触发点。
- 粒子只出现在文字与触发源之间的局部区域。
- 不覆盖原有屏幕内容，不伪造按钮、数据和扫描界面。

### 二创原片

- 保持核心主体、动作和语义。
- 可调整主体与负空间比例，增加一条实际可见的边缘光或反射作为粒子来源。
- 可使用一次短推镜或横向 truck 配合粒子聚合；不把全片改成太空舱、赛博城市或 UI 演示。
- 每个状态只选择粒子聚字、扫描揭示、轮廓填充或字体通道穿越之一作为主运动；Display A/B、Utility、透明板和连接线可以同步落位。

## 6B. 保留原环境的多图层分支

当 `space_mode=preserve_source_space` 时，不给源素材套蓝黑滤镜；视频不改变原片相机，图片不改变原构图和空间骨架。新增字体层模拟一个精密的标题/扫描系统：

```text
Utility: exact, stable, cold-white caption or context label in the existing lower/side safe area; no random numbers or code.
Display A: one exact solid geometric Hero binds to an existing wall, floor, glass or rear plane at 45–105% width. It becomes fully readable before any particle or scan response.
Display B: one exact outline/modular keyword follows a visible object edge or real highlight at 22–58% width; it enters with a thin connection line and may form one repetition field or type portal.
Marks/Carrier: one translucent plate, one perspective frame and a restrained line/particle path reuse the source scene's vanishing direction.
Type camera: Hero makes one slow type lateral truck or 4° counter-orbit; Keyword uses one 0.35s scan reveal. The footage camera and original screen remain unchanged.
Overlay/depth: a translucent grid plate or outline can sit between the original footage and the new Hero for 0.5–1.0s; the real subject may occlude up to 25% of the Hero once.
Light/effect: 60–120 particles or one cyan contour line must originate from a real highlight/edge in the footage, form/touch the exact text, make one outline pulse, then return to the source.
```

全片保持一种粒子运动规律和一种扫描规律；3–5 个状态轮换实心字、线框字、重复字阵和透明板，保留原环境但不降低字体层级，任何可读标签都来自 `TEXT_WHITELIST`。

## 6A. 产品架空展示分支

当 `visual_treatment_mode=product_hero_stage` 时，科技粒子风必须把产品送入一个精密、可见深度的展示空间，而不是给原图套蓝黑滤镜：

```text
Stage: reflective dark laboratory or translucent acrylic chamber; use a near-black/blue floor, one rear plane, one transparent depth plate and a narrow light strip. Remove the ordinary source background and preserve the product's exact silhouette, material and visible components.
Camera: start on a 35mm front 3/4 medium shot → robotic-arm orbit 90° around the product while the camera height rises 10% of product height → hard cut to a macro push-in on one real edge, grille, control or surface reflection → end on a stable 3/4 hero angle.
Lighting: fixed cool-white key from upper-right, thin cyan rim from rear-left, one moving highlight sliding along the real contour. The highlight is the only particle source; it does not jump between surfaces.
Product motion: slow axial rotation 10–20°/s or a controlled turntable 180°; every new angle exposes a real structure or material response. No random disassembly.
Effect chain: 60–120 cyan particles detach from the moving rim highlight → follow the same contour arc → converge in the negative space into the exact Hero word → become a solid cold-white readable word for 0.8–1.2s → one outline scan pulse → particles reverse and merge back into the rim.
Typography depth: Display A begins as a midground wall/floor title during the orbit, then one real counter or frame becomes a camera portal. Display B appears as an outline/repetition field on one transparent plane; Utility connects to one visible detail. The final state returns to one solid full word and the product.
```

建议 9–12 秒节奏：`全貌舞台 0.0–1.0s → 90° 绕拍与粒子聚字 1.0–4.5s → Hero 稳定 4.5–5.5s → 真实细节微距 5.5–7.5s → 侧后 3/4 角度与一次扫描响应 7.5–10.5s → 粒子回收 10.5–11.5s`。全片只使用一种粒子运动规律和一种扫描规律。

## 7. 4–15 秒密度

- `4–5 秒`：1–2 个状态；Display A + Utility；粒子或扫描二选一。
- `6–8 秒`：2–3 个状态；Display A/B 一次实心/线框切换，加入一个透明框。
- `9–12 秒`：3–4 个状态；全屏 Hero、空间墙/地字、真实细节 Utility 各一次。
- `13–15 秒`：3–5 个状态；Display A/B/Utility + 网格/透明框/粒子轨迹；保持一种粒子规律和一种扫描规律。

## 8. 可直接写入 H3 Prompt 的执行块

```text
Typography packaging style: precise technical type cast with localized energy particles. Display A is [wide geometric/heavy condensed] solid type; Display B is [modular stencil/geometric outline] for repetition fields and portals; Utility is [monospaced/neutral] for exact whitelist labels. Use [deep base or inherited color], cold white and one [cyan/blue/acid-green] energy accent; apply one color reversal state without recoloring the product.

Text hierarchy and depth: Display A "[HERO]" appears once at [75–115%] full-frame scale and once at [30–70%] on a wall/floor/rear plane. Display B creates one outline/repetition field at [35–90%]. Utility sits at [6–18%] and every connection line terminates on a visible real object. One type counter/frame becomes the camera transition surface.

Particle choreography: [60–120] small [accent-color] particles detach from [visible highlight or object edge], follow [specific path], and converge into the exact text "[TEXT]" over [0.45–0.80] seconds. At [time], stop all particle motion and form a solid, correctly spelled, fully readable word. Hold it stable from [time] to [time]. On [real trigger], send one thin outline pulse around the word. Exit by reversing the same path and merge every particle back into [source].

Glitch limit: on [single trigger], split the solid word into three horizontal slices, offset only the middle slice by no more than 4% of one letter width for 2–3 frames, then restore the complete word. No continuous glitch and no random characters.
```

## 9. 风格专属反向约束

```text
反向：不要随机 HUD、伪代码、乱码、无来源编号、坐标、百分比、加载条或数据面板；不要整片蓝黑滤镜；不要覆盖原屏幕内容；不要全屏 bloom；不要持续 glitch；不要粒子从空气凭空出现或散满画面；不要改写白名单文字；不要遮住脸、嘴、手和已有字幕；不要 Logo、卖点、价格或 CTA。
```

## 10. 生成指令前检查

- 是否指定了粒子的真实来源、明确轨迹和最终归宿？
- 聚合结束后是否形成实心、准确、稳定可读的文字？
- 中文是否保持偏旁和笔画结构？
- 是否完全没有白名单外的数字、代码和 UI 文案？
- 发光和粒子是否只作用在局部，没有改变原片整体？
- 故障是否只触发一次并在 2–3 帧内复位？

## 11. 网页案例锚点：只借运动机制

以下网页用于校准粒子、扫描和数字化文字的因果关系，不复制源码中的界面、文字或 3D 场景：

- [Generative Kinetic Typography Engine](https://github.com/zfryrgnci/kinetic-typography)：把字体轮廓拆成大量粒子/顶点，用 physics、noise 和 shader 让字形发生波动、破碎与聚合，并把交互位置作为响应源。转译为 H3：把“物体高光/边缘/动作轨迹”设为粒子来源，先聚合成完整实心白名单文字，再只做一次局部脉冲；不要要求 H3 生成连续数学模拟。
- [TypeFlow Kinetic Typography Maker](https://www.typeflow.studio/kinetic-typography-maker)：提供 flip-board 逐字落位、wave/color surge、CRT scanline 和 spring/scale reveal 等明确模板。转译为 H3：每个 Shot 只挑一种揭示机制，例如一条扫描线从左到右揭示整词，或粒子逐字落位；写清起点、方向、完成时间和复位，不能把 flip、wave、CRT、glitch 全部叠加。
- [卡点文字快闪案例](https://www.xiaohongshu.com/discovery/item/680f6bf70000000009014498)：蓝色色场中，中文实心字、英文超大透明字、圆环、球体和波点网格在多个状态中重组。转译为 H3：Display A 使用实心几何字，Display B 使用低对比轮廓/透明大字，Utility 保持稳定；球体、波点网格和圆环属于 GRAPHIC KIT，每一状态只让一个组件承担主运动。

从案例提取的执行规则：`数字效果必须有来源和响应对象`；`Display A 实心、Display B 线框/模块、Utility 稳定`；`粒子最终回到来源或被文字吸收`；`扫描/翻牌/波浪是互斥的主揭示机制`；`没有来源的 HUD、编号和代码不属于科技感`。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
