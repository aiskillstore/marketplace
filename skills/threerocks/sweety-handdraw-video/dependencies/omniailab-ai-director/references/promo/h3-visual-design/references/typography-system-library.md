---
name: omniailab-promo-h3-visual-design-typography-system-library
description: 「动态字体系统库｜H3 可执行规则」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：生成最终 Prompt 时读取本文件。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 动态字体系统库｜H3 可执行规则

生成最终 Prompt 时读取本文件。它不是字体名称清单，而是视频模型可以看懂的“字体角色组 + 尺度层级 + 配色脚本 + 图形组件 + 空间关系 + 动作语法”。15 秒常规包装使用 2–4 个协调角色：字体之间必须有可见对比，但在不同构图状态中持续复用，不能每镜随机换字。

这套系统与主体类型无关：产品、人物、Logo、房地产、商业空间、电商实景、自然环境和口播都使用同一组字体层级。`preserve_source_space` 时，把墙/地/玻璃/货架/门窗/阴影/人物轮廓当作字体锚点；`rebuild_editorial_space` 时，把同一套字体角色延伸成新舞台与镜头通道；`hybrid_local_set` 时只在一个局部表面建立空间字体。画面处理只改变环境与相机权限，不删除 TYPE CAST、COLOR SCRIPT、GRAPHIC KIT、SPACE BINDING、构图状态或音乐 cue。

## 1. 先建立 TYPE CAST 与 DESIGN SCORE

```text
TYPE CAST:
- language: Mixed by default | English | Chinese
- Display A: [主 Hero 骨架、字宽、字重、端点/笔画、字腔、材质、颜色、尺度和空间角色]
- Display B: [与 A 形成粗细/宽窄/曲直/衬线/手写对比的第二 Hero；颜色、尺度和状态用途]
- Utility: [稳定中小字号骨架；字幕、真实标签、辅助标题或说明]
- Marks: [白名单字符的描边/重复/裁切纹理，或不含伪文字的边框、圆点、箭头、网点、涂鸦、短线]

DESIGN SCORE:
- scale_ladder: [full-frame 75–130%] + [mid 22–55%] + [small 6–18%]
- color_script: [背景、Display A、Display B、专色、辅助色] → [哪一状态反白/换位]
- graphic_kit: [2–4 个图形载体及用途]
- space_binding: [至少两种墙/地/主体/画框/字腔/镜头入口关系]
- composition_states: [3–5 个状态；每个状态的主次、景深、颜色和继承关系]
- motion_cue: [每个状态一个主 cue、一个最强运动焦点、一个回收/继承点]
```

H3 Prompt 不写“使用 Helvetica / Futura / Didot”等依赖安装的字体名；写清骨架、笔画、字宽、端点和字腔。Display A/B 是全片持续复用的两个主角，Utility 与 Marks 提供阅读和图形节奏。短于 6 秒可只用 Display A + Utility；口播字幕骨架始终统一，但观点词必须由一个对比明显的 Display 角色接管，不能把“统一”误解成全片一种粗黑体。

## 2. English 主字体系统

每项依次写 `骨架与角色；尺度/版式；动作；配色；适用/边界`，选择后必须把可见参数展开到 Prompt，不能只写编号。

- **E1 Extra-condensed Impact Grotesk｜高冲击压屏**：extra-bold condensed sans，字宽 55%–72%、字重 850–950、直端点/紧字距/清楚字腔；Hero 60%–130%、Keyword 20%–35%，堆叠/跨边/竖排/主体后景；画边 0.12–0.24s 压入 → 可读 0.55–1.0s → 纵压 82% 两帧 → 复位硬切；黑/暖白＋红/酸绿/电蓝；用于炫酷、黑场 Hero、动作撞击。
- **E2 Wide Geometric Sans｜明亮未来感**：宽几何 sans，圆 O、开放 C/G、可选单层 a/g、字重 650–820；Hero 35%–70%、Keyword 12%–26%，水平长标题/中心轴/台面透视；统一基线扩字距 → 0.35s 落位 → 光带扫一次 → 正常字距稳定退出；冷白/深海军蓝＋电青或奶油白/薄荷＋深墨；用于科技粒子、极简产品空间。
- **E3 Neutral Neo-grotesk｜口播与说明**：中性 sans，字重 550–800、正常字宽、开放字腔、清楚标点，同家族 Regular 作 Annotation；Spoken Hero 18%–45%、Annotation 7%–14%，肩外/下三分之一/边缘标签；重音前 0.05–0.12s 滑入 → 发音期稳定 → 底板放大 6%–10% 一次 → 停顿淡出；原画黑白高对比＋珊瑚/黄/电蓝；用于口播、说明、功能指向。
- **E4 High-contrast Editorial Serif｜高级编辑感**：高对比衬线，细横粗竖、尖锐衬线、高字面，Hero 650–750、辅助 400–500，配窄 sans 标签；Hero 45%–95%、辅助 8%–16%，首字跨屏/两行错位；细笔画描出 → 粗笔画填充 → 可读 0.8s → 纵拉 112% 一次 → 光擦除；纸白/墨黑＋酒红/群青/暖金属灰；用于艺术产品、拼贴、玻璃空间。
- **E5 Slab Serif Block｜机械块面**：等粗粗衬线、矩形脚、字重 750–900；Hero 45%–100%、Keyword 15%–30%，建筑构件式落台/横竖模块；各行整体滑入 → 同网格吸附 → 2–3 帧短震 → 完整保持 → 反向拆出；氧化红/象牙白/炭黑或钴蓝/纸白/黑；用于工业、拼贴、机械空间。
- **E6 Monospaced Technical｜精密标注**：中等字重等宽/半等宽 sans、略宽字距，只承载真实白名单标签，配 E2/E1 Hero；Annotation 6%–15%，沿真实部件边、连线终点或微距角落；细线从真实部件增长 → 到点整词显现 → 扫描一次 → 线字同收；冷白＋电青/酸绿、深灰蓝底；用于科技粒子和产品细节。
- **E7 Rounded Soft Grotesk｜清新玩具感**：高字重圆角 sans、宽字面/开放字腔/圆端点、字重 700–850，配轻手写或同家族 Regular；Hero 30%–62%、Keyword 14%–28%，圆台上方/侧边负空间/短弧；86% 弧线滑入 → 106% → 100% 稳定 → 原弧回收；奶油白＋深可可＋薄荷/杏橙/珊瑚粉；用于清新可爱和生活产品。
- **E8 Modular Stencil Sans｜字体模块切槽**：模块几何 sans、6%–12% 安全断口、字重 700–900；Hero 40%–90%，借产品轴线建立外部独立网格并留至少一个主笔画宽度间距；保护层外节点展开 → 负空间装完整词 → 断口亮一次 → 回外部网格，不进接缝/贴本体/拆产品；黑白＋单一高饱和专色；用于科技、炫酷，不用于长句。
- **E9 Chunky Playful Display｜怪趣块面**：超粗不等宽、圆角＋局部尖角、高宽差 8%–16%、字腔清楚，配 E7 与中性圆体 Utility；两行错位/首尾放大/圆角框/2×3 阵列；整词落基线 → 最大字 0.18s 横拉 115% → 回基线 → 圆角框接管；紫黄或钴蓝/奶油白/珊瑚、也可素材主色＋互补色；用于趣味标题、年轻人物和生活内容。
- **E10 Casual Marker / Brush｜手写情绪层**：不等粗记号笔/短笔刷、明显起收笔、倾斜 2°–8°，只作语义不同的 Display B/Marks，配 E1/E3/E7；跨负空间短词/批注/同源下划线；单向写出 → 保持 0.7–1.0s → 笔触延成框/下划线 → 擦入下一状态；用于可爱、拼贴、口播重音，不承担长字幕、小字或随机签名。

## 3. 中文主字体系统

- **C1 超粗方黑｜全屏压字**：方形重心、等粗笔画、紧字面、清楚偏旁、字重 850–950；2–4 字横/竖排，55%–120%；整组压入 → 完整可读 → 3–5 条水平切片一次并在 2–4 帧复位；黑/暖白＋红/蓝/酸黄；用于炫酷和海报大字。
- **C2 几何圆黑｜清新可爱**：圆角等粗、方字面、开放字腔，2–6 字；一/两行错位、单字角度差 2°–4° 但基线清楚；按语义组弹入并在 0.4s 内成完整词，全词只回弹一次；奶油白、深可可/墨绿、薄荷/杏橙/粉；用于生活、亲子、食品、日用品。
- **C3 现代宋体｜编辑与艺术**：横细竖粗、三角/楔形收笔、疏朗字面，配 25%–35% 高度中性黑体；2–6 字竖排/两行错位/跨纸缝并保护偏旁；细笔画显现 → 粗笔画填充 → 稳定 0.8s → 纸面/玻璃擦除；纸白/墨黑＋酒红/群青/金属灰；用于拼贴和炫酷安静段。
- **C4 窄体黑｜科技与纵向空间**：中文黑体横压最多 12%–15%、字重 700–850，保持偏旁比例；2–8 字沿两侧竖排/窄列；扫描线按整字揭示 → 完整后轮廓脉冲一次，不逐笔闪烁；深底＋冷白＋电青/冰蓝；用于科技粒子和 9:16 产品侧标题。
- **C5 粗宋/方黑混搭｜海报标题**：主字只在超粗方黑/粗宋中选一，另一骨架只作 1–3 字辅助，禁止逐字换字体；主标题 60%–110%、标签 12%–22% 落纸条/色块；主字吸附网格 → 标签下节点滑入 → 专色轮廓套印偏移 2–3 帧；用于拼贴和实验海报。
- **C6 人文黑体｜口播与解释**：自然笔画、开放字腔、中高字重、小尺寸可读且不书法化；基础字幕随语速一条一条推进，单次只呈现一个完整意群/一句话，短句一行、长句可折成 1–2 行；重点短句在肩外/标签区，随真实重音整体进入并稳定，只让底板/下划线响应一次；原画黑白高对比＋一个强调色；用于口播和功能解释。
- **C7 怪趣粗黑｜不等宽趣味标题**：粗细略不均、圆角＋短尖角、偏旁夸张 6%–12% 但笔画/重心完整，Display A/B 皆可，配 C2/C6；2–6 字两行高低错位，一个字放大 130%–170%＋短手写标注；0.35s 依次落位 → 最大字回弹一次 → 涂鸦长出 → 统一回收；用于食品、日用品、萌宠、旅行、轻松口播。
- **C8 粗笔刷手写｜情绪 Hero**：粗笔刷、不等粗、起收笔/局部飞白可见但不破坏偏旁，倾斜≤8°；Display B 或 2–5 字单字 Hero，配 C1/C2/C6；跨屏/两侧错位/顺动作方向＋手写圆圈短线；同笔势显形 → 可读 → 延成框/下划线 → 擦除/变下一切边；用于可爱、拼贴、口播重音和人物情绪。
- **C9 几何线框黑体｜空间科技辅助**：方形几何黑体单/双线描边、内部留白清楚，只作 Display B/背景重复/Marks，Display A 保持实心；贴墙落地透视/四边裁切/3×2 阵列/与实心字错开 4%–8%；真实边缘长线 → 完整空心字 → 局部填实 → 字体入口或回线框；用于科技、炫酷和 Logo 几何场。
- **C10 现代手写细字｜注释呼吸层**：中细笔画、自然书写、疏字距、轻倾斜且不草书连写，只作 Utility/Annotation，配 C1/C2/C3/C7/C8；肩外/产品边缘/纸条上方/Hero 短批注＋同源线；线先到 → 短词整体淡入/写入 → 稳定 0.8–1.2s → 线字同收；用于可爱、编辑拼贴、生活和口播。

## 4. Mixed 中英混排系统

非口播默认中英混排。指定主语言与编辑语言，让它们分别承担 Display A、Display B 或 Utility；两种语言共享同一内容角度但分别增加不同信息，不逐条互译，也不用孤立英文名词填版：

```text
Mixed hierarchy: Display A [main language] height = 100%; Display B or Utility [secondary language] height = 22–45%. Keep separate baselines and one shared alignment edge. A later composition state may promote the secondary language to a 55–85% Display B while the main language becomes Utility. Do not fuse two scripts into one unreadable glyph block.
```

推荐组合：

- 中文超粗方黑 Display A + English condensed sans Display B + 中性黑体 Utility：高冲击、炫酷艺术。
- English heavy condensed Display A + 中文超粗方黑/窄黑 Display B + 半等宽 Utility：暗黑胶片故障、Logo/模型发布封面。
- English high-contrast serif Display A + 中文现代宋/中性黑体 Display B + 窄体 Utility：编辑拼贴。
- English wide geometric Display A + 中文窄体黑 Display B + 等宽 Utility：科技产品。
- 中文怪趣粗黑或圆黑 Display A + English chunky/rounded Display B + 手写 Utility：清新可爱。
- English neutral grotesk / 中文人文黑体稳定字幕 + 一个怪趣或手写关键词 Display B：口播。

## 5. 字体与颜色搭配库

每套色盘都指定角色，不写“缤纷多彩”：

| 配色系统 | 背景 | Hero | 专色 | 辅助字 | 适合 |
|---|---|---|---|---|---|
| Ink Signal | `#050505` | `#F4F2EC` | `#FF2B2B` | `#9A9A9A` | 炫酷艺术 |
| Blood Zine | `#050607` | `#F4F1EA` | `#E82018` | `#77706B` | 暗黑胶片故障 / Logo 发布 |
| Acid Night | `#07090D` | `#F6F5EE` | `#C7FF2E` | `#8D96A3` | 科技/艺术 |
| Electric Lab | `#071726` | `#EAF6FF` | `#22D3EE` | `#6F91A6` | 科技粒子 |
| Cobalt Paper | `#F2EBDD` | `#101010` | `#2457D6` | `#6D665B` | 海报拼贴 |
| Brick Print | `#F7F5EF` | `#111111` | `#D94A3A` | `#81796F` | 编辑海报 |
| Mint Cream | `#FFF6E8` | `#173F36` | `#78DCC6` | `#FFAA73` | 清新可爱 |
| Coral Milk | `#F7FBFA` | `#3A2C2A` | `#FF7F96` | `#FFD86B` | 清新可爱 |
| White Gallery | `#F4F4F0` | `#151515` | `#275DFF` | `#777777` | 极简产品/口播 |

主体或原环境已有高饱和主色时，专色优先从素材取样，其他新增包装色使用中性黑/白/灰；主体为白色时，用周围图形层的专色建立轮廓，不重染主体或原环境。

15 秒不必从头到尾只用同一种字色关系。保持同一套 3–5 色，但写出 2–3 个状态变化：

```text
COLOR SCRIPT:
- State 1: background=[base], Display A=[light], Display B=[accent], Utility=[neutral].
- State 2: background becomes [accent]; Display A reverses to [dark/light]; Display B becomes [base]; subject color stays unchanged.
- State 3: return to [base] with one [accent] frame/underline; all roles settle to the final palette.
```

颜色变化通过色块接管、纸面翻转、灯光擦入、全屏 Hero 或遮挡切镜完成；不是随机换滤镜。

## 6. AE 级文字版式机制库

每支 15 秒片从下列机制选 2–4 个，并安排先后关系；不要全部叠加在同一时刻。

### M1. Full-frame Hero takeover

```text
"[TEXT]" expands from 30% to 110% frame width over 0.25 seconds, becomes a full-screen foreground plane, remains complete for 0.55 seconds, then the product passes in front through a real silhouette mask. The word moves behind the product and settles at 65% width in the background.
```

### M2. Subject/type depth exchange

```text
Start with the real subject or architectural edge in the foreground and "[TEXT]" in the background. In rebuild mode, use a controlled camera orbit; in preserve mode, keep the source camera fixed and move only the type layer with matched parallax. The word crosses an independent carrier or architectural negative-space opening into the foreground; product structure and product negative space never become the portal. The subject briefly occludes no more than 30% of the word. End with the complete word in front and the subject readable.
```

### M3. Scale ladder

```text
Show the same whitelist word only once at a time: 18% Keyword → hard cut to 65% Hero → hard cut to 115% cropped Hero. Each size holds complete for at least 0.35 seconds. The previous size exits before the next enters; no echo copies remain.
```

### M4. Split-stack assembly

```text
Divide the exact phrase into 2–3 semantic lines. Line 1 slides from the left, line 2 from the right, and both snap to one shared grid. After the complete phrase is readable, the two lines move together as one block and exit along the product motion direction.
```

### M5. Contour wrap

```text
Place "[TEXT]" on one independent flat plane beside the product. Keep at least one main-stem width of visible clearance from the complete product silhouette. A thin baseline follows no more than one-quarter of the outer contour on an offset path; the letters remain front-facing, stay on their own depth layer, and do not attach to the product or wrap into unreadable 3D. The baseline detaches from the contour and straightens before exit.
```

### M6. Counter-rotation

```text
The product rotates clockwise by 90° while the Hero block rotates counter-clockwise by only 6° around its own center. The Hero remains front-facing and readable; when the product stops, the type returns to 0° and locks to the stage grid.
```

### M7. Material transition

```text
The solid word "[TEXT]" is readable first. A product-generated light/airflow/paper edge crosses the word once, changing only the passed area into [outline/particle/ink/transparent glass]. The effect stops at the far edge, and the entire word returns to one solid material before exit.
```

### M8. Typographic portal cut

```text
The counter of a real letter in "[TEXT]" grows to fill the frame while the word remains readable for the first half of the move. The camera passes through that opening and cuts to the next product angle. The same word does not reappear immediately after the cut.
```

### M9. Baseline as motion trail

```text
The product movement leaves one light/ink trail. The trail straightens into a baseline, the exact word grows upward from it, holds complete, then collapses back into the baseline and returns to the product's motion endpoint.
```

### M10. Annotation choreography

```text
A line starts at a visible product component, reaches the label position, then the exact label appears. The line and label hold together for 0.8–1.2 seconds. The label disappears first; the line retracts to the same component. No additional UI is generated.
```

### M11. Spatial type corridor｜字体空间通道

```text
Place the exact Display A word across the floor and back wall as two connected flat planes sharing one vanishing point. The camera starts above the first full readable word, travels forward between its enlarged strokes or counters, then reveals the same word complete on the rear wall. Display B remains on a side plane; one frame edge from the floor becomes the next state's border.
```

### M12. Multi-panel poster state｜多分栏动态海报

```text
Build one full-frame composition from 2–4 panels: one subject panel, one Display A panel, one Display B/Utility panel and one color/texture panel. All panels snap to one grid over 0.25–0.45 seconds. Hold the complete poster state, then let one panel expand to full frame and become the next scene's wall or background.
```

### M13. Repetition field｜重复字阵/图案场

```text
Repeat only one whitelist word or one verified Logo/name in a 2×3 or 3×4 grid. Use outline or low-contrast copies as Marks and keep one solid copy as the reading focus. The grid follows one plane and vanishing direction. A subject or color block wipes through the grid, leaving one enlarged solid word for the next state.
```

### M14. Glyph-to-graphic transformation｜字形变图形

```text
Show the exact Chinese character/English word complete first. Enlarge one real stroke, counter or outer contour until it becomes a frame, divider, floor line or mask; keep enough of the word visible to preserve identity during the move. The enlarged shape carries the camera into a new poster state, where the complete word returns in a different scale or color role.
```

### M15. Frame ecology｜边框与标记系统

```text
Generate one thick frame, one partial corner frame and 2–5 short marks from a visible subject edge, baseline or paper seam. Display A may cross one frame edge; Utility locks to a corner; Marks follow the subject motion direction. The full frame closes once, then one side becomes the wipe boundary for the next state.
```

### M16. Playful doodle dialogue｜趣味涂鸦响应

```text
Use 2–5 content-related non-text doodles such as citrus wedges, airflow arcs, stars, dots, eyes or short arrows. Each doodle starts from a visible object/action edge, responds to Display B or a hand-drawn Hero, and joins one border/baseline before exit. Pair a stable rounded or bold Display A with one irregular hand-drawn Display B and one small handwritten Utility.
```

### M17. Talking-head evidence card｜口播素材/证据卡

```text
Keep the speaker visible in one protected panel or a corner mini-head inset. When a source video exists, build at least one editorial popup card from a source-derived crop/PiP or a real frame detail; otherwise use an uploaded image/chart, exact quote, verified number, real step or comparison. State which spoken phrase it proves. Match card form to meaning: quote/definition card, large-number card, numbered-step stack, split comparison, process connector, or verified location/architecture detail. Use a 1:1 or 4:3 card with one Display keyword, one Utility line and one shared border/accent color. The card enters on a paper flick, restrained UI click or hand-gesture cue, holds 0.8–1.4 seconds, then one edge becomes the next layout divider. Never invent data, names, screenshots, logos or stock B-roll.
```

### M18. Talking-head layout swap｜口播版式换位

```text
REVEAL: one caption unit appears by a directional mask in 0.12–0.24 seconds, carrying only one spoken sentence or one complete semantic beat; short units stay on one line and long units may wrap to two lines, never stacking multiple spoken sentences at once. EMPHASIS: one real stressed phrase becomes a contrasting Display role and performs one 106%–112% pulse, width stretch or foreground step with a tactile cue. SWAP: the Display phrase takes a full-frame/side-column/behind-speaker position while the caption clears; a source-derived popup card or divider inherits the old baseline, and the speaker may shrink into a 12%–22% top-left/top-right mini-head inset while remaining lip-readable. SETTLE: all roles return to a shared grid and hold complete for 0.55–1.0 seconds. For every swap, specify outgoing action → transition type and 0.12–0.35 second duration → semantic relationship → incoming composition and viewer focus. Do not animate every character independently, keep one rounded box throughout, or write only “smooth transition”.
```

### M19. Architectural axis transfer｜建筑轴线跨镜继承

```text
For each preserved-space clip, identify one real axis or edge and one attach plane. Choose one shared geometric motif across the sequence. Reveal the master title from clip 1's real axis, lock it to the plane and track the original camera with matched perspective and parallax. Let one real foreground object occlude part of the title, then transfer only the axis/edge/light path—not a floating sticker—through a 0.12–0.35 second match cut into clip 2's corresponding structure. Repeat the same motion spine once, then settle the title into clip 3's architectural grid. Use one master title, one medium label and one Utility role; no independent bounce routine per room.
```

## 7. 文字节奏与密度

- 13–15 秒建立 3–5 个完整 `COMPOSITION STATE`，而不是 3–5 个孤立单词。每个状态使用主体 + Display A/B + Utility/Marks + Carrier 中的 3–6 层。
- Hero 不是片尾标题：在前 20%–40% 时长处至少一次全屏/近全屏接管；后续可变为背景墙、地面字、遮罩或重复字阵，结尾回到稳定版面。
- Display A/B 在不同状态间轮换主次：例如窄粗大字 → 高对比衬线/手写情绪字 → Utility/Marks 接管过渡 → Display A 回收。
- 同一状态最多一个最强运动焦点，但可以同时存在一个 Hero、一个中尺度辅助标题、一个稳定 Utility 和 1–3 个无文字图形组件。
- 强冲击后留 0.35–1.0 秒完整可读；呼吸来自稳定构图，不是把包装全部清空。
- 每个状态写 `cue → carrier enter → type cast locks → readable hold → focal response → depth/layout change → inherited transition`。
- 4–5 秒使用 1–2 个状态、1–2 个字体角色；6–8 秒使用 2–3 个状态、2–3 个角色；9–12 秒使用 3–4 个状态；13–15 秒使用 3–5 个状态、2–4 个角色。
- 口播 13–15 秒至少使用 `单句字幕底座 → 观点 Hero 状态 → 素材弹窗/证据卡状态 → 小头窗/人物与字体共存终态` 中的三种以上，不得只在同一个黑色圆角框内更换文字。稳定字幕使用 E3/C6；Display 依内容从 E4/E9/E10/C1/C3/C7/C8 选一个；卡片 Utility 使用 E3/C6/C10，并共用同一对齐边和专色。
- 建筑/室内原片优先 `E2/E4/C3/C6 + E3/C10 Utility`：一个中等字重几何/人文无衬线负责空间标题，一个现代宋体/高对比编辑衬线负责对比，一个稳定小字负责真实标签。正常状态主字 20%–55%，全片唯一 Hero 55%–85%。不要使用厚黑白描边、短硬阴影、泡泡贴纸字或每段一个超粗圆黑 Hero；明亮背景用局部半透明建筑面、单色实心字、微弱软阴影和真实遮挡解决对比。

## 8. 生成指令前选择器

```text
Select typography system by content:
- real-estate / architecture with preserved environment → Display A E2/E4/C3/C6 + one contrasting E4/C3 role + Utility E3/C10; use M2/M10/M15/M19 on real walls, floors, glass, axes and vanishing lines. One master title, one motion spine, at most one 55–85% Hero; no thick outline, sticker shadow or generic room labels
- e-commerce / retail / lived-in scene with preserved environment → Display A E1/E7/C1/C2 + Display B E4/E10/C3/C8 + Utility E3/C10; use M2/M3/M12/M13/M15 without replacing the scene
- general image/video creative rework → choose roles from content mood; keep M1/M11/M12/M14/M15, then select preserve, hybrid or rebuild camera permissions
- cool art → first read `style-cool-art.md` and use one fused type family across all states: Display A combines E2/E8/C1/C4 modular geometric structure; Display B uses E1/E3/C6 width/italic/curved neo-grotesk variants; Utility uses E6/C6. The same roles flow through plastic refraction, subject type morph, 3D event poster and dark scan fracture; use M11/M12/M14/M15 so type occupies floor/wall/glass/foreground planes and camera perspective, not a side label; do not select separate chassis or return to “condensed + serif/brush + generic glitch”.
- dark-pop glitch / logo launch → first read `style-dark-pop-glitch.md`; infer `logo_layout_type` from the reference. Display A is the verified Logo/model/title in E1/E8/C1/C4 heavy condensed or modular black type, Display B uses a different editorial phrase only when provided or semantically grounded; otherwise use glyph counters, outline crops, scan slits and low-contrast repetition as non-readable Marks. For `pure_logo`, design from glyph geometry and reassembly. For `logo_with_cover_anchor`, keep the anchor protected and central while the Logo remains the typographic owner. Use M1/M11/M12/M13/M14/M15 as hard-cut magazine-cover states; include one logo-only/abstract scan state before final cover, allow 1-frame negative flash, 2–4-frame scan tear and red/black registration offset, but restore exact wordmark spelling and anchor visibility immediately. No RGB neon, random letters, fake issue data, persistent giant text pasted over the anchor, or body/logo deformation.
- precise technology product → Display A E2/C4 + Display B E8/C9 + Utility E6/C6; M5/M9/M11/M13
- editorial / art object → Display A E4/C3 + Display B E1/C8 + Utility E3/C10; M2/M12/M14/M15
- industrial / mechanical → Display A E5/E8/C1 + Display B E1/C9 + Utility E6/C6; M4/M6/M9/M15
- friendly lifestyle product → Display A E7/C2/C7 + Display B E9/E10/C8 + Utility E3/C10; M3/M12/M15/M16
- talking-head / explanation → stable E3/C6 single-sentence caption base + one contrasting E4/E9/E10/C1/C3/C7/C8 keyword role + Utility E3/C10; M10/M15/M16/M17/M18. Require two keyword packaging hits with tactile SFX, one verified popup card/PiP, one speaker mini-head corner inset, two layout states and reveal → emphasis → swap → settle; never default to one black rounded caption box.
- poster collage → 普通编辑路线使用 Display A E1/E4/E5/C1/C3/C5 + Display B E10/C8/C9 + Utility E3/C10；复古拼贴剪纸增强路线改用 Display A E1/E5/C1/C3 + Display B E4/C5/C9 + Utility E3/C10，并把 M4/M7/M12/M13/M15 落到纸片吸附、跨缝、重复字阵和信息卡，不退回单一黑白红大字海报，也不引入可爱综艺的气泡/星芒默认装饰
- logo packaging → first infer `logo_layout_type`; verified Logo/name as Display A + outline/repetition/glyph-crop Display B + stable Utility only when semantically grounded. `pure_logo` uses real glyph contour/counters/spacing as the motion skeleton; `logo_with_cover_anchor` keeps Logo as typographic owner and the anchor as protected cover center; M11/M12/M13/M14/M15
```

最终 Prompt 必须把选择结果写成可见参数，而不是只写编号：模型不认识 `E1` 或 `M3`。

## 9. 案例来源到执行规则的转译

- [RCA Visual Communication](https://www.rca.ac.uk/study/programme-finder/visual-communication-ma/) 将 type design、sound、performance、moving image、VR 并置。转译：字体不仅是标签，它可作为前景平面、后景结构、遮挡物和镜头转场；每次改变景深时保留可读时刻。
- [RCA Typographic Abstraction](https://www.rca.ac.uk/news-and-events/news/in-session-typographic-abstraction-the-shift-from-semantics-to-spectacle/) 讨论 typography 从 semantics 到 spectacle。转译：允许 Hero 全屏、尺度跳变、字腔变成转场入口和材质转换，但白名单文字先完整出现。
- [RISD Graphic Design](https://www.risd.edu/academics/graphic-design) 的公开课程范围包括 offset typography、grid、3D display、projection、package design 与 title sequences。转译：先锁定共享网格和一个空间轴，再做套印、立体层级、投影和标题切换。
- [UAL MA Graphic Media Design](https://www.arts.ac.uk/subjects/communication-and-graphic-design/postgraduate/ma-graphic-media-design) 强调 research-led graphic practice，并将 print、photography、emerging technologies、3D production 与 sound 放进同一制作语境。转译：字体系统要同时定义平面印刷质感、摄影景深、空间/3D 层级与声音触发；不要只写“动态字体”，要写它落在什么平面、如何被产品/光线遮挡、如何回到版面。
- [Mat Voyce — Type in Motion](https://abduzeedo.com/type-motion-mat-voyce-animates-experimental-kinetic-typography-stickers/) 的模块网格、bounce/warp/stretch 与字形角色化。转译：圆润字体按统一基线落位，只回弹一次；小尺寸优先清晰字腔。
- [SVGator kinetic typography examples](https://www.svgator.com/blog/50-kinetic-typography-examples/) 的 snap、stack、pulse、hard cut、fluid type。转译：每个文字事件只选择一个主运动和一个短响应；hard cut 是节拍边界，fluid 变化保持整体词可读。
- [TechSmith Talking Head Video](https://www.techsmith.com/blog/talking-head-video/) 建议把口播与 annotations、images、lower thirds、simple graphics、B-roll、zoom 和 transitions 配合。转译：把台词与可视素材按同一时间点编排；H3 口播至少有稳定字幕、观点 Hero 和一张来源明确的素材/证据卡，锁定原片时只使用已上传素材或原片衍生 PiP，不虚构 B-roll。
- [FontsArena Kinetic Type](https://fontsarena.com/blog/kinetic-type-for-the-rest-of-us-a-practical-guide-for-designers/) 强调层级来自字重、尺度与 easing，并让动效落回稳定可读状态。转译：口播统一使用 `reveal → emphasis → swap → settle`，剪辑层 punch-in/parallax 控制在 2%–3%，不让文字持续漂浮。
- [SEGD — Wayfinding Is Where Place Meets Information Design](https://segd.org/resources/wayfinding-where-place-meets-information-design/) 强调建筑是人的第一空间线索，图形系统应在关键节点做渐进式信息披露，并与建筑保持支持、和谐关系。转译：先找原片主轴、转折、入口和出边，再放文字；每一状态只出现当下需要的信息，不让装饰抢过空间。
- [SEGD — The Field Guide to Supergraphics](https://segd.org/resources/field-guide-supergraphics-big-graphics-urban-landscape/) 将成功的大型环境图形归纳为强概念、与建筑/光/空间互动、与观看者建立关系。转译：多段空间先找一个共享母题和 motion spine；大字必须改变或解释空间关系，不能只是贴在墙上的巨大字幕。
- [Pentagram — Philadelphia Museum of Art](https://www.pentagram.com/work/philadelphia-museum-of-art-2/story) 与 [Bibliothèque nationale du Luxembourg](https://www.pentagram.com/work/bibliotheque-nationale-du-luxembourg/story) 使用克制、模块化、与柱列/石块/空间比例呼应的导视，并用三级字号覆盖不同观看距离。转译：室内包装保持三级字阶和建筑留白；载体尺寸、轴线和比例来自真实建筑构件，避免过度干预。
- [Adobe — Tracking 3D Camera Movement](https://helpx.adobe.com/after-effects/desktop/work-with-3d-composition/3d-camera-tracker-effect/tracking-3d-camera-movement.html) 通过提取相机运动与场景数据，让文字正确合成进二维实拍。转译：H3 Prompt 要逐段写 camera vector、attach plane、消失方向、透视缩短、视差和遮挡，缺一项就不是空间贴附。
- [TypeFlow kinetic typography](https://www.typeflow.studio/kinetic-typography-maker) 的 flip、wave、scanline、spring、scale、odometer reveal。转译：揭示机制互斥；写清方向、完成时间和复位，不把所有模板同时叠加。
- [MiniMax H3 动态海报案例](https://www.xiaohongshu.com/discovery/item/6a6b4b5e0000000008013c1b)：同一人物在纸白、黑红、网点、剪影和暖橙状态间转换；`MiniMax / H3 / 001` 不是旁边标签，而是全屏构图骨架，人物反复穿过字面。转译：15 秒写 3–5 个完整海报状态；字体、人物、色场和网点共同换位，至少一次让文字从后景变前景。
- [国风 H3 字形图形化案例](https://www.xiaohongshu.com/discovery/item/6a6d8add0000000021021369)：中文粗线字形先成为全屏抽象结构，再重组成红黑白模块版面。转译：使用 M14，把真实笔画放大成框、分栏或遮罩；完整汉字先出现并在下一状态返回。
- [空棚人物 + 字体空间运镜](https://www.xiaohongshu.com/discovery/item/69d9cce30000000022003dbc)：大字铺在地面与后墙，相机沿字面透视穿行后再揭示人物。转译：使用 M11，写同一消失点、地面/墙面连接、相机起终点和穿越后的完整文字，不把字贴在人物旁边。
- [趣味字体动效合集](https://www.xiaohongshu.com/discovery/item/67d189f3000000002803c611)：宽窄拉伸、立方体、重复字阵、弧形字、彩色底反转与多栏排版连续切换。转译：使用固定 TYPE CAST 和 COLOR SCRIPT，在多个状态中轮换 E7/E9/E10 或 C2/C7/C8，而不是只用一个圆体。
- [怪趣中文字体图集](https://www.xiaohongshu.com/discovery/item/69861f05000000001a01e9d4)：可见粗细不均、圆尖混合、偏旁夸张、手写笔刷、稳定黑体与小注释的组合。转译：清新可爱不等于单一圆体；优先 `C2/C7 Display A + C8 Display B + C10 Utility + M16 Marks`。
- [口播精剪，解锁时尚大片质感](https://www.xiaohongshu.com/discovery/item/6a1c285e000000003601daed)：公开标题把目标定义为淘汰常规口播、形成杂志封面式精剪。转译：口播包装不能退化成底部字幕；必须让大字、人物、卡片、分栏、轻推近和触感音效形成多状态编辑版面，同时保持真实台词和人物表演。

共同准则：`字体角色有对比且持续复用；每个状态是主体、字、图形、色彩和空间的完整组合；尺度和空间层级大胆；运动有触发、完成、继承和复位；复杂度不来自随机字体或伪小字。`

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
