---
name: omniailab-promo-h3-visual-design-td-cv-tracking
description: 「实时视觉与追踪 追踪表现」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：把"AI 看见的世界"（计算机视觉检测/追踪的可视化结果）做成短视频。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 实时视觉与追踪 追踪表现

把"AI 看见的世界"（计算机视觉检测/追踪的可视化结果）做成短视频。

---

## 何时使用

用户要做 **TD 风格 / 动态追踪 / CV 调试风 / "AI 看见的世界"** 风格的视频时。

**典型说法**：做个 TD 追踪视频、动态追踪、AI 看见的世界、CV 可视化、TD lab 风、像 sample 里那种。

---

## 工作流

### 1. 收集 3 个 Question（独立条目，一次调用）

编写制作计划时，按 Q1 → Q2 → Q3 判断缺失项；命中的项目合并到一次 confirmation card 流程中，但每项仍是独立问题，不能合并成一个问题：

- 用户未亲自明确提供的信息必须问，禁止根据平台、附件或推荐项静默补默认值。
- 用户已明确提供的项不再问；只提交仍缺失的问题。
- 每题把推荐项放第一位，但“推荐”不等于默认，必须等用户选择后才能继续。

#### Q1 — 比例 & 时长

**问题**：请选择视频比例和时长。

- A. **9:16 / 10s（推荐）** — 适合竖屏短视频
- B. **16:9 / 15s** — 适合横屏与宽屏平台
- C. **1:1 / 10s** — 适合正方形画面

用户可以自定义其他组合。比例或时长只明确了一项时，保留已给值，并针对另一项继续提问；不得自动补齐。

#### Q2 — 素材 / 风格提供方式

**问题**：这次用哪种方式提供素材/风格？

- A. **直接生成（推荐）**
  → AI 用基线风格直接出视频，你只需描述场景。
- B. **上传风格参考图片**
  → 你给图片或视频作为风格参考，AI 参考它的视觉方向生成新视频；参考素材只用于风格参考，不作为视频底片、叠加层或音轨。
- C. **试试描述**
  → 你自己写：场景 + 风格 + 颜色。
  例：
  - 一个舞者 + 末日废土 + 红框
  - 鸟群 + 黑白 + 纯蓝框 + HUD
  - 手部特写 + 赛博朋克 + 绿框 + 中心准星

**选择 C 后的普通对话补充**：

- **是否追问只根据 C 的自定义输入判断，不使用用户发起任务时的原始输入作这一判断。**
- C 的自定义输入包含风格词或视觉方向（如末日废土、赛博朋克、黑白、复古胶片、极简、低饱和、霓虹、HUD 等）时直接继续，不再询问。
- C 的自定义输入为空，或只有主体、场景、动作而没有风格描述时，Agent 在普通对话中只问一句：`你想要什么画面风格？`
- 这句话必须作为普通聊天消息发送，**禁止调用 confirmation card，禁止弹出 Question 卡片，也不要提供 A/B/C 选项**。
- 普通对话补充最多问一次。用户没有回答、跳过，或下一条回复仍未提供风格时，使用默认 visual reference 继续，禁止再次追问。
- 该普通对话补充不计入开始时的 3 个 Question，也不改变 Q1 → Q2 → Q3 的卡片顺序。

仅有图片或视频附件但未明确其用途时，不能静默视为 B；仍需提问确认。

#### Q3 — 节奏模式

**问题**：请选择视频镜头节奏模式。

- A. **一镜到底（推荐）** — 最终只输出一条完整视频；全程保持同一个连续镜头，不主动切镜
- B. **多段切镜** — 最终仍只输出一条完整视频；在所选总时长内出现清晰的镜头切换。这里的“多段”只表示一条成片内部有切镜，**不是**分开生成多个视频再拼接；不规定切镜数量、每段时长或固定时间点

### 2. 判定主体类型

| 画面主体 | 追踪策略 |
|---|---|
| 单体植物 / 动物 | 整体外轮廓 |
| 身体局部特写（手 / 脚 / 关节） | 局部精细 |
| 面部 | 五官关键点（眼/鼻/嘴/轮廓） |
| **群组**（人群 / 鸟群 / 鱼群 / 动物群） | **多目标统一追踪，每个个体都锁定并跟随移动** |

### 3. 组装 prompt

1. 取下面的"基线 prompt"
2. 把"主体描述段"（开头的 `[A single dancer in a black leotard ...]`）替换为用户场景展开后的描述
3. 把"技术参数段"（末尾的 `[Technical] 10 seconds, 9:16 vertical, ...`）替换为 Q1 的比例/时长
4. Q2 = A：使用基线 prompt，根据用户场景描述展开主体描述。
5. Q2 = B：读取参考图片或视频的视觉方向（构图、色彩、光线、材质、镜头感），将其作为风格参考；最终仍由 video model 从头生成一条新视频，不使用参考素材的画面、动作或音轨作为底层内容。
6. Q2 = C：按“选择 C 后的普通对话补充”判断是否追问。组装 prompt 时仍以用户发起任务时的原始输入为主体与场景基础，再叠加 C 的自定义输入；如果发生过风格追问，再叠加用户的风格回答。没有获得风格回答时使用默认 visual reference，同时保留基线 prompt 的追踪框、负片、音画同步和硬负面规则。

**主体描述展开规则**：把场景描述展开成 1-2 句的视觉化描述，必须包含“画面构图 + 相机视角 + 主体动作”。Q2 = A 由基线 prompt 定义 TD 风格；Q2 = B/C 可将参考或用户明确写出的风格、颜色要求加入 prompt，但不能覆盖基线硬性规则。

### 3.1 底层画面视觉 reference

读取 [td-visual-attributes.md](td-visual-attributes.md)，把它作为**底层 AI 生成画面**的默认视觉处理参考，不把它当成主体、场景或 overlay 规则：

- 默认应用：低饱和、冷暖分离（冷阴影 / 暖高光）、中高对比、抬黑但保留高光细节、中高强度胶片颗粒、电影感单点/侧逆光、浅景深、轻微暗角和自然锐度。
- 可选应用：轻微划痕、灰尘、褪色、偏色、眩光、漏光或高光 bloom；不要堆成满屏瑕疵。
- 适用范围：只处理生成视频的主体画面、色调、质感、灯光和镜头观感；不得给描边框、连线、数字 ID 或局部负片遮罩增加填充、染色或颗粒。
- 优先级：用户明确写出的场景 / 风格 / 颜色，以及 Q2 的图片或视频风格参考优先；本 reference 只补充未指定的画面属性；本路线的框、负片、同步和硬负面规则始终最高优先级。
- 单色例外：用户明确要求黑白或单色底层画面时，停用本 reference 的彩色冷暖分离和主导色相，只保留不冲突的对比度、颗粒、灯光、景深和暗角；遵守“强制单色写法”。

| 用户输入 | 展开后 |
|---|---|
| "跳舞的女孩" | "A single dancer in a black leotard performs sharp contemporary dance moves in a minimalist concrete dance studio. The camera holds a steady medium shot; the dancer fills the center of the frame..." |
| "海鸥飞" | "A flock of dozens of seagulls flying dynamically against a pale overcast sky, shot from below on a windy coastline. The camera tracks the flock as it twists, expands, and contracts..." |
| "郁金香开花" | "A single tulip slowly opening and blooming in time-lapse, against a soft warm gradient background. The camera holds a steady close-up shot..." |
| "手部特写" | "A hand reaches and grabs an object in close-up, fingers extending and curling. The camera holds a tight macro shot, shallow depth of field..." |
| "人群俯视" | "A crowd of people walking in a busy public square, shot from above in a high-angle perspective. The camera is static, the crowd moves organically..." |

### 4. 生成 + 自检 + 交付

1. 使用视频生成一次完成所选总时长的完整单条视频：一镜到底保持单镜头连续动作；多段切镜只需在同一条视频内部产生清晰的镜头切换。禁止把段落拆成多个独立视频，禁止交付多个视频文件
2. 生成完成后只走一次 §自检清单。全部通过 → 用 `<media>` 标签交付**单个视频**并结束
3. 任一项不通过 → **禁止自动重新生成**，只使用一次独立 confirmation card：
   - **问题**：要不要重新生成？
   - A. **重新生成（推荐）** — 生成一个新版本
   - B. **不重新生成** — 保留当前结果并结束
4. 发出 Question 卡片前后都不要告诉用户哪一项不合格，也不要展示检查结论、失败原因或改进说明；卡片只保留上面的简短问题和两个选项
5. 只有用户明确选择 A 后才能重新调用 video model；选择 B、关闭卡片、未回答或没有明确确认时都不得重新生成
6. 每次用户确认只授权重新生成一次。新结果仍只检查一次；若仍不通过，必须重新询问同一个 Question，禁止沿用上一次确认连续重跑

---

## 5 要素（必出 + 必齐）

> 缺一个都算风格缺失；进入“要不要重新生成？”确认流程，禁止自动重跑。

| # | 要素 | 形态 |
|---|---|---|
| 1 | **描边框** | 空心方形，1-2px 描边，**无填充**。同屏 **12-20 个**，固定保持大 / 中 / 小 / 微型四级尺寸，且最大/最小面积差 ≥32x；框的位置和尺寸随重拍快速轮换 |
| 2 | **连接线** | 细直线，星型/网状结构，框角/中心互相牵引 |
| 3 | **数字 ID** | 4 位数字（或 `[x, y]` 坐标），等宽字体，**每帧随机变化** |
| 4 | **颜色反转** | 对小框/微型框做**局部矩形遮罩合成**：只把遮罩内的底层像素做 RGB 反转，框外逐帧保持不变；每次重拍轮换负片窗口，不能整条视频总是同几个框在闪 |
| 5 | **音画同步** | 视觉节奏跟随 AI 生成的音轨；负片在每个重音/底鼓点正↔负切换；BGM 使用无歌词纯音乐 |

### 描边框的硬性规则

✅ **空心方形**：仅 axis-aligned 矩形，**不画人物轮廓形、五边形、星形等异形**
✅ **多框并存**：同一目标范围内始终保持 **12-20 个**描边框；稳定画面不得少于 12 个
✅ **四级尺寸分桶**：每个稳定画面同时具备四级框，数量固定在：**大框 2-4 个、中框 3-5 个、小框 3-5 个、微型框 4-6 个**，合计 12-20 个；相邻框不能属于同一尺寸档
✅ **尺寸必须拉开**：以画面宽度为参照，大框约 15-25%、中框约 8-14%、小框约 4-7%、微型框约 1-3%；允许宽扁或高窄，但微型框必须肉眼明显小于小框
✅ **最大框只取局部**：最大框面积不得超过可见主体包围区域的 **1/4**，不得完整框住整个人、整个头部或整个主体
✅ **最小框必须足够小**：微型框面积不得超过最大框的 **1/32**；每个画面至少有 4 个微型框，形成清晰的针孔 / 局部采样感
✅ **重拍轮换**：每个可感知的重拍触发框的出现、消失、跳位或缩放；每次轮换约 30%-50% 的框，保留其余框短暂跟随，不能整片只重复同一批框
❌ **严格禁止同心框**：任意两个框都不得共享或近似共享中心点，每个框的中心必须明显错开并追踪不同局部。小框可以部分或完整落在大框内部，只要两者不同心
❌ **禁止异形**：不是人物轮廓、不规则多边形、五角星等
❌ **禁止实心**：框内不能有填充色块
❌ **禁止全包框**：任何框都不能覆盖或包住完整主体

### 颜色反转的硬性规则

- **合成方式**：先保留完整的 AI 生成帧作为 base layer，再复制同一帧；只在小框/微型框的矩形遮罩内替换为反转像素。遮罩外（包括大框、中框内部）每一帧都必须保持生成画面，不得闪烁、变黑或变白。
- **像素定义**：对遮罩内每个彩色像素执行 RGB 通道反转 `R'=255-R, G'=255-G, B'=255-B`。彩色素材必须保留反转后的彩色（如红变青、蓝变黄），不能把整帧或遮罩强制降成黑白；黑白素材只在对应小框内做局部黑↔白反转。
- **负片窗口**：把小框和微型框当作悬浮在主体上的小窗、小孔或取景器，透过窗口看到同一位置、同一时刻主体的负片版本；主体动作、轮廓和纹理必须连续不变。
- **边界与对照**：负片精确裁切在小框内侧边界内，不能越过描边或向外扩散。框外和未反转区域始终保持 normal positive color，形成清晰的局部正片/负片对照。
- **节拍切换**：音乐重音或底鼓点触发小框遮罩内 positive ↔ negative 切换，每个重音触发一次；视觉变化跟随音乐自然发生，不使用固定 BPM 或固定秒数间隔。
- **窗口轮换**：不要让固定的几个小框/微型框贯穿全片反复闪负片。保留多个可用的小框，在连续重拍之间轮换不同的位置、尺寸和框身份，让负片窗口在一条视频内持续变化；每次被选中的窗口仍只在对应重拍切换。
- **关键观感**：画面必须像“透过几个小窗口看到同一主体的负片版本”，而不是全屏黑白闪、全局负片、曝光闪烁或在主体上叠加色块。

### BGM 与音画同步规则

- **所有 Q2 方式都生成新视频和新音轨**：根据用户提示词中的场景、情绪、主体动作、风格、颜色和节奏模式决定 BGM 的曲风、音色、乐器、BPM 与节奏密度；用户明确指定音乐要求时优先遵循。
- **禁止写死音乐参数**：不得默认电子乐、固定 kick、`120 BPM`、每 `0.5s` 一次重拍或任何统一节拍模板。
- **禁止人声和歌词**：生成的 BGM 必须为纯音乐，不得出现演唱、念白或可辨识歌词。
- **同步要求**：音轨由 video model 与画面同步生成。框的出现、跳动、缩放和小框负片切换都跟随音乐节拍；负片在每个可感知的重音/底鼓点正↔负翻转，不在非重音位置单独闪烁。

### 严禁的元素（HARD NEGATIVES）

- ❌ **实心色块**糊在主体上
- ❌ **飘字**（`Hah, c'mon` 这类英文 subtitle drift）
- ❌ **logo / 水印 / 角标**
- ❌ **全局黑白 / 全局降饱和 / 全局负片**
- ❌ **全屏黑↔白闪烁、全屏曝光闪、全屏颜色脉冲或 strobe**
- ❌ **把彩色素材整体降成黑白来模拟负片**
- ❌ **大框或中框内部出现负片**
- ❌ **用实心色块、单色染色或半透明蒙版冒充 photographic negative**
- ❌ **负片越过小框内侧边界或扩散到框外**
- ❌ **框数量不足 12 个**，或缺少大 / 中 / 小 / 微型任一尺寸档
- ❌ **所有框集中在相近尺寸**，或没有至少 4 个肉眼可见的微型框
- ❌ **全身框 / 全主体框 / 整头框**
- ❌ **同心框 / 近似同心框**（共享中心或视觉上中心过近都禁止；中心明显错开的嵌套框允许出现）
- ❌ **同尺寸框**（"all the same size"——必须有明显尺寸差）
- ❌ **静态数字 ID**（必须每帧变）
- ❌ **人物轮廓形 / 异形** BBox

---

## 自检清单

视频出片后**只逐项核对一次**。任一不通过视为生成失败，但不得自动重跑；按 §生成 + 自检 + 交付 发起“要不要重新生成？”Question，等待用户明确确认。

- [ ] 5 要素全部出现（框/线/数字/反转/同步）
- [ ] 框是空心方形，不是异形
- [ ] **没有任何"全包框"**（最大框面积 ≤ 可见主体包围区域的 1/4，且只框局部）
- [ ] 稳定画面同时有 12-20 个框，不能只出现少数几个
- [ ] 四级尺寸数量齐全：大框 2-4 个、中框 3-5 个、小框 3-5 个、微型框 4-6 个
- [ ] 大 / 中 / 小 / 微型四档尺寸肉眼明显拉开；微型框宽度约为画面宽度 1-3%
- [ ] 最小框面积 ≤ 最大框的 1/32，最大/最小面积差 ≥ 32x
- [ ] 任意两个框的中心都明显错开，没有同心或近似同心框
- [ ] 小框落在大框内部时，两者中心仍明显错开，没有形成同心套环
- [ ] 小框遮罩切到 negative 状态时，所有可见小框/微型框内都能清楚看到同一底层画面的真实 photographic negative，不是色块或染色蒙版
- [ ] 大框、中框和所有小框之外的画面保持正常正片颜色
- [ ] 负片精确裁切在小框内侧，没有越过描边或向外扩散
- [ ] positive ↔ negative 切换肉眼清晰可见
- [ ] 连续重拍之间负片窗口会轮换到不同的小框/微型框，整条视频不是固定同几个框反复闪
- [ ] 没有全屏黑白闪、曝光闪、strobe 或彩色素材整体降黑白
- [ ] 负片切换与音乐重音/底鼓点对齐，每个重音触发一次，没有非重音位置的随机闪烁
- [ ] AI 生成的 BGM 无人声、无歌词，且曲风、BPM 与节奏密度匹配用户提示词
- [ ] 最终视频和音轨均由 AI 生成；没有把参考素材的画面、动作或音轨直接叠加进成片
- [ ] 底层 AI 画面应用了 visual reference 的必要电影属性，且调色、颗粒和瑕疵没有污染 overlay 或局部负片遮罩
- [ ] 数字肉眼可见在跳（前后帧数字不同）
- [ ] 没有实心色块、飘字、logo、HUD 误入
- [ ] （如强制单色）只有目标颜色出现，没有第三色

---

## 基线 Prompt（10s / 9:16 / 单人舞蹈）

> 这是用户测试 OK 的版本，是所有 Q2 方式共用的**唯一基线**；无论素材/风格如何提供，最终都由 AI 从头生成一条新视频。
> 主体描述和技术参数按 §Step 3 规则替换。

```text
A single dancer in a black leotard performs sharp contemporary dance moves in a minimalist concrete dance studio. The camera holds a steady medium shot; the dancer fills the center of the frame and her arms sweep wide through the negative space.

[Style — 实时视觉工具-style real-time computer vision tracking visualization]
Overlay ALL of the following on top of the AI-generated footage, densely and continuously, throughout the entire clip:

1. Multiple HOLLOW axis-aligned rectangle bounding boxes only. Thin 1-2px stroke, NO fill, NO semi-transparent fill, NO solid color blocks. Keep **12-20 boxes visible simultaneously** throughout the clip, never just a few. At every stable moment, show four unmistakable size tiers with these counts: **2-4 LARGE local boxes**, **3-5 MEDIUM boxes**, **3-5 SMALL boxes**, and **4-6 TINY MICRO boxes**. Approximate width tiers relative to the frame: LARGE 15-25%, MEDIUM 8-14%, SMALL 4-7%, MICRO 1-3%; use varied wide and tall rectangles, not identical squares. Every box tracks a LOCAL FRAGMENT of the subject; NO box may enclose the whole subject, the whole body, or the whole head. Even the largest box must cover no more than ONE QUARTER of the visible subject's bounding-region area. Each micro box must be visibly tiny and its area at most 1/32 of the largest box. The box sizes can vary within their tier, but must not collapse into one similar size. STRICT SPATIAL RULE — ABSOLUTELY NO CONCENTRIC OR NEAR-CONCENTRIC BOXES. No two boxes may share the same or nearly the same center point. Give every box a visibly displaced center and a separate local tracking region. A smaller box MAY sit partly or fully inside a larger box, but their center points must remain clearly offset; non-concentric nesting is allowed. Never create layered rectangle rings that share or nearly share one center. On every audible downbeat or strong accent, replace or resize roughly 30-50% of the boxes and move them to new local fragments, while keeping the total count and all four tiers; do not use fixed-time, fixed-BPM, or unsynced changes. NO silhouettes, NO star shapes, NO irregular polygons, NO masks shaped like the dancer.

2. Thin topological connection lines — straight lines linking box corners and centers into a star / network graph that flexes with the dancer's motion.

3. Numeric IDs as 4-digit numbers and small [x, y] coordinate labels next to each box, in a clean monospace font. The numbers MUST randomize / change rapidly on every frame, like a live CV debug console where the IDs are constantly updating. Make the labels small and compact, not large.

4. Color inversion effect, ONLY inside the SMALL and MICRO bounding boxes: the pixels covered by the currently selected small boxes show a photographic negative (color-inverted) version of the underlying AI-generated frame, while everything OUTSIDE those boxes — including large and medium box interiors — stays in normal positive color. Keep several small/micro boxes available and ROTATE WHICH BOXES ARE NEGATIVE across successive music downbeats: different box identities, positions, and sizes must take turns throughout the single clip. Do not let the same fixed few boxes flash for the entire video. Each selected window changes negative ↔ positive on its beat while unselected windows remain positive. Think of each selected box as a tiny "window," "viewport," or "aperture" that shows the negative of the same moving subject while the rest of the frame remains normal. Preserve the subject's motion and detail inside the window. Clip the effect to the selected small-box interiors. This is the key visual hook — beat-synced, rotating "negative-film peeks" through changing small boxes, NOT a global black-and-white flash, strobe, or full-frame negative.

5. The entire visual rhythm — box appearance, jumping, resize, and color inversion timing — is tightly synced to the audio beat.

Optional subtle layers (free to add or omit): small center crosshair, sparse floating pixel sample blocks, faint particle dust.

HARD NEGATIVES — do NOT include any of these:
- solid-fill colored blocks covering the subject (no red blocks, no cyan blocks)
- global black-and-white or desaturation filter on the whole frame
- global photographic negative applied to the entire image
- the same fixed small/micro boxes remaining the only negative windows throughout the whole clip
- fewer than 12 visible boxes, missing any of the four size tiers, or no clearly visible micro boxes
- boxes collapsing into one similar size instead of the required large/medium/small/micro hierarchy
- full-screen black ↔ white flashing, exposure pulsing, color strobing, or any frame-wide brightness/color toggle
- converting color footage to monochrome to fake the negative effect
- inversion inside large or medium boxes, or negative pixels bleeding beyond a small box's inner edges
- solid fills, flat color tints, or translucent masks used instead of a true photographic negative of the underlying pixels
- any box enclosing the whole subject, whole body, or whole head; the largest box must stay below one quarter of the visible subject area
- floating English subtitle text drifting across the screen
- logo watermarks or corner brand marks
- concentric or near-concentric rectangles with shared/near-shared centers, including layered rectangle rings; a smaller box fully inside a larger box is allowed when their centers are clearly offset
- boxes that are all the same size (the smallest micro box must be at most 1/32 the area of the largest box)
- static, unchanging numeric IDs (the 4-digit numbers must keep randomizing rapidly)

[Audio — generated by the video model in sync]
Generate an instrumental BGM whose genre, sound palette, instrumentation, tempo/BPM, rhythmic density, and intensity are inferred from the user's scene prompt, mood, subject motion, and pacing mode. Follow any explicit music direction from the user. Do NOT default to electronic music, 120 BPM, a fixed kick pattern, half-second downbeats, or any other universal rhythm template. No vocals, no spoken voice, and no lyrics. Make the musical beat and downbeats clear enough for the box motion and local color inversions to follow naturally.

[Technical]
10 seconds, 9:16 vertical, cinematic, sharp focus on the dancer, shallow depth of field; lighting follows the visual reference's cinematic single-key or side/back setup.

[Visual style — generated footage only]
Apply the visual attributes from `td-visual-attributes.md` to the underlying AI-generated footage: low-saturation palette, natural teal/cyan shadows with warm orange/pink highlights, medium-high contrast with lifted blacks and preserved highlight detail, strong 35mm film grain, cinematic single-key or side/back lighting, shallow depth of field, subtle vignette, and natural rather than over-sharpened detail. Optional vintage scratches, dust, color shift, lens flare, light leak, or highlight bloom must stay subtle. Do not apply this grading, grain, or artifacts to the tracking overlay, box outlines, connection lines, numeric IDs, or the local negative masks. If the user explicitly requests monochrome or a different palette, follow that request and keep only compatible texture, lighting, contrast, and optical attributes.
```

### 比例/时长替换表

修改最后一段 `[Technical]`：

| 比例 / 时长 | 替换为 |
|---|---|
| 9:16 / 10s（推荐） | `10 seconds, 9:16 vertical, ...` |
| 9:16 / 6s | `6 seconds, 9:16 vertical, ...` |
| 9:16 / 15s | `15 seconds, 9:16 vertical, ...` |
| 16:9 / 15s | `15 seconds, 16:9 horizontal, ...` |
| 16:9 / 10s | `10 seconds, 16:9 horizontal, ...` |
| 16:9 / 20s | `20 seconds, 16:9 horizontal, ...` |
| 1:1 / 10s | `10 seconds, 1:1 square, ...` |
| 1:1 / 6s | `6 seconds, 1:1 square, ...` |
| 1:1 / 15s | `15 seconds, 1:1 square, ...` |

### Q2 选择后的 prompt 处理

- **A. 直接生成**：使用基线 prompt，并将用户的场景描述展开为主体描述。
- **B. 上传风格参考图片**：从图片或视频中提取构图、色彩、光线、材质和镜头感等视觉方向，作为新视频的风格参考。参考素材不能作为底片、叠加层、动作来源或音轨。
- **C. 试试描述**：是否追问只检查 C 的自定义输入；组装 prompt 时保留原始输入，并叠加 C 的自定义输入和后续风格回答。具体追问方式按 §选择 C 后的普通对话补充执行；基线 prompt 的框、连线、数字 ID、局部负片和音画同步规则始终保留。

无论选择哪一项，最终都只使用一次 video model 生成一条完整的新视频，并生成匹配的无歌词纯音乐音轨。

---

## 配色规则

| 场景 | Overlay 默认色 |
|---|---|
| 默认（彩色主体） | 模型自选（参考样本多为红/青/紫） |
| 主体黑白 + 蓝 overlay | 强制 RGB 蓝（`#0000FF` 或类似纯蓝） |
| 主体黑白 + 任意单色 overlay | 用户在 Q2 答完后补充指定 |

**强制单色写法**（在主体描述后追加）：

```text
COLOR DISCIPLINE — STRICT: The underlying AI-generated footage is ENTIRELY MONOCHROME BLACK AND WHITE. The ONLY color allowed in the entire video is pure RGB blue (around #0000FF) used for ALL overlay elements — bounding boxes, connection lines, numeric IDs, coordinate labels. No other colors anywhere.
```

并在所有 overlay 段（§1 / §2 / §3）的描述里加 "in pure RGB blue"。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
