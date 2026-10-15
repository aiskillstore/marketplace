---
name: omniailab-promo-h3-visual-design-style-poster-collage
description: 「海报大字拼贴风｜H3 执行规则」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：只在用户选择“海报大字拼贴风”，或需要纸张、油墨、撕纸、套印、网点和版面分栏时读取本文件。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 海报大字拼贴风｜H3 执行规则

只在用户选择“海报大字拼贴风”，或需要纸张、油墨、撕纸、套印、网点和版面分栏时读取本文件。它是把文字当成画面构成层，不是生成一张虚构杂志或品牌海报。

## 1. 视觉参数

### 色盘

固定为“纸白 + 油墨黑 + 一个专色”：

- 纸面：旧纸白 `#F2EBDD`、暖灰白 `#F7F5EF` 或继承原片亮部。
- 油墨黑：`#101010`。
- 专色三选一：砖红 `#D94A3A`、群青 `#2457D6`、酸黄 `#E7C83A`。
- 若原片本身色彩丰富，文字层只保留黑 + 纸白 + 一个专色，不新增第二个彩色系统。

### 字体骨架

- Display A：超粗黑体/窄体 grotesk/粗宋体，承担全屏印刷 Hero、跨缝大字和重复字阵。
- Display B：现代宋体/高对比衬线、粗笔刷手写、线框黑体三选一，与 Display A 形成粗细、衬线或手工感对比；承担第二 Hero 和字形变图形。
- Utility：小号中性无衬线、人文黑体或现代手写细字，只写白名单中的真实短词。
- Marks：纸面分栏、粗边框、套印色边、网点、裁切字阵、裁切角标和无文字圆点；不使用伪期号、作者、价格或栏目小字。
- 纹理：纸张纤维、轻微油墨不均、网点、套印偏移中选两种，分配到不同状态。

### 层级与版面

- `Full-frame Hero`：Display A/B 占 75%–130%，允许跨主体、纸缝和画框；至少一次成为整张动态海报的骨架。
- `Mid Hero`：占 24%–60%，放在色块、纸条或分栏中，与主 Hero 形成宽窄/粗细对比。
- `Utility`：占 6%–18%，锁到框角、纸条或真实内容边缘。
- 用 2–4 个纸面分区、色块或粗框建立完整状态；一个状态可有 Hero、Mid Hero、Utility、Marks，但只有一个层承担最强运动。

## 1A. 复古拼贴剪纸增强路由

仅当用户说“拼贴剪纸、复古剪纸、手工拼贴”，或参考明显包含分层撕纸、主体剪纸贴片、信息卡和装配动作时启用；综艺参考只提供装配手法，不把风格变成可爱综艺。普通“海报大字拼贴”仍走上面的纸白/油墨编辑路线。

- `PALETTE`: 纸白/黑为底，再从主体或参考中选 1–2 个低饱和专色，最多保留一个高饱和亮点；不要做彩虹色、糖果色或可爱贴纸色场。
- `CUTOUT SUBJECT`: 主体作为完整剪纸贴片，外沿只用克制的纸白边或深色接触影；可加入最多两张同一主体的完整局部卡/重复贴片，但不能复制成结构错误的多个产品。
- `GRAPHIC KIT`: 3–5 块不规则纸片、1 条胶带角、粗框、套印边、网点和 1 张信息卡；气泡、箭头、星芒、手绘线默认留给清新可爱风，复古拼贴只在有真实来源时取其中一个作辅助。每个可读标签都必须来自白名单。至少三块纸片写出 `进入方向→旋转/滑行→吸附→停留→退出`。
- `TYPE CAST`: Display A 用粗黑/粗宋/窄体 grotesk 的复古印刷骨架，带纸边或专色套印，承担 55%–100% 的主 Hero；Display B 用现代宋体、高对比衬线或线框几何字，放进斜纸条、分栏或独立信息卡；Utility 只放真实短标签，不能把 FRAME/WHEEL/CHAIN 一类结构词铺满画面。
- `STATE CHOREOGRAPHY`: `clean editorial stage → paper assembly → type/subject depth exchange → detail/card insert → dense final board`。每个状态更换主载体、专色或景别；禁止连续两段使用同一条横向色带和同一张终版海报。
- `MOTION`: 纸片必须有可见的滑入、翻转、硬切吸附、撕开、叠放或被主体推开的动作；15 秒至少 3 次动作组变化、2 次景别/视角变化和 1 次主体完整局部卡。静态版面只在最终 0.8–1.2 秒稳定，禁止全程使用弹跳。
- `DEPTH`: 主体贴片、文字贴片、卡片和背景纸面分成前/中/后景；主字可以压住纸片边，但不遮挡主体关键结构。先完整读字，再由贴片遮挡/揭示，不能从头到尾把字压在产品上。

这一路由借鉴的是“纸片装配和综艺信息图”的机制，不复制参考中的人物、台词、品牌、地图或具体图形。

### 21:9 横向适配

超宽画幅不能只把同一张海报拉长：把画面分成左/中/右三个纵向区域，让主体、纸片和文字在横向路径上依次接力；至少一次主体偏左或偏右、一次局部卡片占据侧区、一次大字从画外横向切入。禁止连续两状态都“主体居中 + 同一主标题 + 同一色带”。

## 2. 语言分支

### English

- Hero 优先 ALL CAPS，1–4 个词；可用堆叠、竖排、切栏和基线错位。
- 保留字母完整形状；套印偏移只影响颜色边缘，不制造重影乱码。

### Chinese

- Hero 优先 2–8 个汉字，可用横排、竖排或两行错位。
- 粗黑体或粗宋体保持字面方正；撕纸/网点作用于整字表面，不拆散偏旁。
- 长句分语义块；不要把超过 8 个字压成一行窄条。

### Mixed

- 每个状态由一种语言做 Hero，另一种语言使用语义不同的次级文案或 1–2 个真实编辑标签；全片在不同纸面状态中交换主次以完成 `COPY_DECK`，不限制为一条注释。
- 不自动增加期号、作者、栏目名或逐字译文，也不用同一句跨纸条/字体角色复用。
- 两种语言放在不同纸条/色块中，保持独立基线和清晰阅读路径。

## 3. 空间、景深与遮挡

- 纸面层可放在前景，主体可压在纸面上或从纸面撕口穿出；保留主体脸、嘴和关键动作。
- Hero 可跨接两块纸面或穿过一条缝，跨接点要稳定至少 0.5 秒。
- 文字与画面主体可形成前/中/后景，但纸张纹理不能覆盖人物眼睛和已有字幕。
- 色块和纸条边缘必须有明确起点和终点；不要无限延伸到全屏。
- 文字主体不要依赖真实 Logo、品牌标识或虚构出版信息来成立。

## 4. 字体运动语法

### 拼贴纸条进入

```text
在[切镜/主体动作]时，一块宽度[占画面 20%–60%]的[纸白/专色色块]从[具体方向]滑入并停在[位置]。准确文字“[TEXT]”预先印在纸条上，纸条停止后文字完整、清楚、无透视变形可读至少 0.8 秒。下一次[真实触发]时，纸条沿同一方向滑出或被主体边缘压住；不要凭空出现第二张纸。
```

### 跨缝 Hero

```text
先显示完整文字“[TEXT]”。随后一条不规则撕纸缝从[起点]延伸至[终点]，Hero 跨在缝两侧，缝的两边只产生 2%–4% 的套印偏移。文字仍能逐字读取。缝合或硬切时，字块回到一个平整版面。
```

### 套印偏移

```text
准确文字“[TEXT]”完整可读后，在[单次重音]上只把专色轮廓向[方向]偏移 3–6 像素，持续 2–3 帧，再与黑色主字重合。黑色字形、字距和拼写不变化。
```

### 网点放大

```text
从文字左下角的真实印刷网点开始，网点按同一圆心放大到[文字外沿]，短暂形成一层半色调纹理，随后缩回文字表面；不把网点扩散到全屏。
```

## 5. 小特效连续性

小特效只能是纸张、油墨或版面行为：

```text
The torn paper edge begins at the lower-left corner of the exact word "[TEXT]", travels diagonally to the upper-right corner, briefly exposes the [spot-color] layer underneath, then folds back along the same edge and settles flat. No paper appears from empty space.
```

```text
Two visible ink registration marks start beside the existing printed edge of "[TEXT]", slide 4–6 pixels in the same direction as the color misregistration, align back to the black letterforms, and disappear into the paper grain.
```

```text
A real hand/object crossing the frame pushes the paper strip by one strip width; the strip bends at the contact point, reveals the exact word for a clear moment, then returns to its original plane. The hand/object remains unchanged.
```

禁止无来源的彩纸爆炸、飘满全屏的纸屑、无穷套娃小海报或虚构报刊小字。

## 6. 两种视频模式

### 锁定原片，只做包装

- 原片人物、场景、镜头、动作、声音和光线保持不变。
- 纸条、色块和 Hero 只在负空间或已有平面上叠加；不把原片背景改成纸张。
- 撕纸缝、套印偏移和网点必须由文字层自身产生，不能改变主体纹理。
- 不添加品牌片尾、广告标题页、价格或产品功能清单。

### 二创原片

- 保留主体、关键动作和内容语义。
- 可把背景局部处理成 2–4 块纸面版区，或让 Hero 跨一个真实空间边界。
- 版面变化只服务于当前文字和动作节点；不新增虚构品牌出版物。

## 6B. 保留原环境的多图层分支

当 `space_mode=preserve_source_space` 时，视频保持原镜头和色彩，图片保持原构图和空间骨架；新增字体像一套与真实环境贴合的印刷版面：

```text
Utility: exact phrase, if required, in a small ink-black/cream line placed on one existing baseline or frame edge.
Display A: exact bold printed Hero at 55–125% width, crossing one real frame boundary, shadow edge or visible plane; hold it complete before any tear, crop or registration shift.
Display B: exact short word in a contrasting heavy serif/modern Song/brush skeleton at 24–68% width, placed on one paper strip or spot-color block that follows a visible hand/object/architectural direction.
Marks/Carrier: one thick frame, 2–4 aligned paper/color panels, one repetition field and one localized halftone/registration system reuse the source perspective.
Type camera: Hero makes one paper-plane slide or crop reveal; Keyword rotates 3–6° and snaps to the same grid. The original footage camera remains untouched.
Overlay/depth: use one paper-white plane, ink-black plane or spot-color block in front/behind the footage; real subject may push/occlude the strip, but the subject is never cut out or changed.
Texture/light: localized paper grain, halftone or registration edge starts at the printed boundary, travels to the exact text edge, creates one 3–6px color offset for 2–3 frames, and settles back into the same paper surface.
```

不要给原片铺满纸纹，也不要虚构期号、作者、杂志小字；每段只选择纸条装配、跨缝撕纸或套印偏移之一作为主机制。

## 6A. 产品架空展示分支

当 `visual_treatment_mode=product_hero_stage` 时，把产品从普通背景中“剪出”，放进一套可移动的纸面/油墨展示台；产品不是被一张海报覆盖，而是作为真实物体在纸面空间中旋转和被版面装配。

```text
Stage: paper-white plane, one ink-black rear plane, one [brick-red/cobalt-blue/acid-yellow] block, two irregular cut edges and short hard shadows. Remove the ordinary source background. Preserve the product's exact silhouette, components, material and color; do not print a fake logo or issue number.
Camera: start top-down on the empty paper stage → a product cut-out drops onto the real printed contact shadow → camera tilts to a 3/4 view and trucks laterally 20% for parallax → macro cut on one real texture or control → return to a flat poster-like hero composition.
Lighting: broad soft daylight from upper-left for paper texture, one hard side light for the product cut-out, and a localized ink shadow that moves only when the product turns. Registration color does not recolor the product.
Product motion: one top-down drop with a single elastic settle, then a 30–60° product turn showing a real side component; no paper puppet deformation of the product.
Effect chain: a torn edge begins at an existing paper seam → travels to the lower-left of the exact Hero → reveals the [spot-color] layer → the printed word becomes readable across the seam → the torn edge folds back and settles flat; no floating paper debris.
Typography depth: Display A is a 75–120% printed block crossing one seam and briefly occluded by the product. Display B becomes a contrasting serif/brush/outline state on another paper plane; Utility rides one strip or frame corner. One enlarged stroke/letter counter or paper panel expands to full frame and becomes the next state's wall or mask.
```

建议 9–12 秒节奏：`纸面与产品落台 0.0–2.0s → 3/4 角度与横向视差 2.0–4.8s → 跨缝 Hero 4.8–6.4s → 真实部件微距 6.4–8.0s → 套印偏移一次 8.0–8.4s → 纸条回收、产品与版面稳定 8.4–10.5s`。纸张、网点、套印最多选择两种。

## 7. 4–15 秒密度

- `4–5 秒`：1–2 个状态；Display A + Utility + 一块纸条/色块。
- `6–8 秒`：2–3 个状态；Display A/B 对比一次，加入跨缝或套印。
- `9–12 秒`：3–4 个状态；全屏 Hero、重复字阵、多分栏海报各至少一次。
- `13–15 秒`：3–5 个完整状态；普通编辑路线使用 Display A/B/Utility、2–4 个纸面分区、边框/网点持续复用；复古拼贴剪纸路线必须完成 `clean stage → paper assembly → type/subject exchange → detail/card → final board`，且最终稳定版面只占最后 0.8–1.2 秒。

## 8. 可直接写入 H3 Prompt 的执行块

```text
Typography packaging style: moving editorial poster collage built from paper-white planes, ink-black type and one [brick-red/cobalt-blue/acid-yellow] spot color. Display A is [bold condensed/heavy square/heavy serif]; Display B is [modern serif/brush/outline] with a visible contrasting skeleton; Utility is [neutral sans/humanist/modern handwritten]. Reuse one thick frame, 2–4 paper panels, one repetition field and one localized halftone/registration system.

Layout: Display A "[HERO]" occupies [75–130%] in one full-frame poster state and [45–100%] across a seam/subject layer. Display B "[SECOND]" occupies [24–70%] on a contrasting paper/color plane. Utility "[UTILITY]" sits at [6–18%] on one frame corner or strip. One panel expands into the next state's background; one repetition field resolves into a single solid word.

Choreography: on [real cut or action trigger], one [paper strip/spot-color block] slides from [direction] over [0.20–0.40] seconds and stops. The printed exact text "[TEXT]" is fully readable from [time] to [time]. On [single later trigger], shift only the spot-color registration layer by 3–6 pixels for 2–3 frames, then align it back to the black type. Exit by folding or sliding the same strip along its entry path.

Localized effect: a torn edge or halftone pattern begins at [visible printed edge], travels to [specific endpoint], reveals [one existing layer], then folds back or shrinks into the paper surface. No floating paper debris and no full-screen texture wash.
```

## 9. 风格专属反向约束

```text
反向：不要虚构杂志、期号、作者、价格、Logo、品牌名、CTA 或广告片尾；不要伪造小字填版；不要无限纸张套叠、满屏纸屑或无来源彩纸爆炸；不要把拼贴剪纸路线压成黑白红单一海报；不要改变锁定原片的背景、人物和动作；不要遮住脸、嘴、手和已有字幕；不要加入与文字无关的镜头。
```

## 10. 生成指令前检查

- 是否使用纸白、油墨黑和一个专色，且纹理局部可见？
- Display A/B/Utility 是否形成粗黑/衬线或手写/稳定小字的角色对比？
- 是否至少有一次全屏海报状态、一次多分栏状态和一次字形/纸面成为转场？
- 若启用拼贴剪纸子路由，是否保持纸白/黑 + 1–2 个专色、一个完整主体贴片、三次纸片装配动作、一次局部/卡片插入和三种不同版式；是否没有连续重复同一色带或终版，也没有变成糖果色可爱贴纸？
- Hero 是否跨越具体边界，而不是随机漂浮？
- 套印偏移是否只作用 2–3 帧并恢复？
- 每一条纸张/撕纸效果是否有起点、路径、终点？
- 是否删除了所有虚构期号、作者、Logo 和广告文案？
- 版面是否仍然让原片承担叙事？

## 11. 网页案例锚点：只借系统和装配动作

以下网页用于校准纸张、网点、边缘和装配的可见规则，不把活动广告或商业文案带入包装：

- [Advibly — AI Paper Collage Motion](https://advibly.com/templates/collage-motion-ad)：把 collage 先拆成共享 medium、palette、paper texture、halftone、edge treatment、shadow、typography、negative prompt，再让 cut-out pieces slide / rotate / snap into place；空色场和成品版面都保留，避免每个场景漂移成另一套设计。转译为 H3：先锁定“纸白 + 油墨黑 + 一个专色”的系统，再让同一纸条沿一条路径滑入、旋转或吸附；结束时停在一个稳定版面，不随机生成第二套纸张。
- [Paper Collage Motion（GitHub）](https://github.com/jasperdevs/paper-collage-motion)：将半色调纸拼贴拆成 medium、color field、halftone、cut edges、shadows、composition、label treatment 和 mood，并强调把 reference 解码成 editable specs 与 motion handoff。转译为 H3：把每块纸、字块和边缘写成明确字段；文字只使用白名单，纸张效果必须有起点、运动、吸附/回收点。
- [FontsArena — Kinetic Type for the Rest of Us](https://fontsarena.com/blog/kinetic-type-for-the-rest-of-us-a-practical-guide-for-designers/)：强调在动态缩放/字重变化中使用字形指标稳定、字腔清晰的字体。转译为 H3：拼贴 Hero 可大、可裁切，但关键字母/汉字必须保持清楚；不使用无法稳定渲染的装饰小字。
- [MiniMax H3 动态海报案例](https://www.xiaohongshu.com/discovery/item/6a6b4b5e0000000008013c1b)：人物、超大字、编号、红黑白/纸白色场、剪影与网点构成连续海报状态。转译为 H3：把主体面板、Display A、Display B/Utility 和纹理面板写成 2–4 栏；让一栏扩张为下一状态，不把小字散放成 tag。
- [国风 H3 字形模块案例](https://www.xiaohongshu.com/discovery/item/6a6d8add0000000021021369)：完整中文粗线字形被放大成红黑白模块。转译为 H3：Display A 先完整可读，再让真实笔画成为分栏、边框和遮罩，镜头越过后回到完整字形。
- [怪趣中文字体图集](https://www.xiaohongshu.com/discovery/item/69861f05000000001a01e9d4)：粗黑、笔刷手写、现代细字和小色块共同组成标题。转译为 H3：使用 `Display A 粗黑/粗宋 + Display B 手写/衬线 + Utility 稳定小字`，小色块和手写符号承担 Marks，不伪造刊物信息。

从案例提取的执行规则：`先锁 TYPE CAST、纸面网格和颜色角色，再做 3–5 个完整状态`；`slide / rotate / snap / panel-expand 是纸块的可观察动作`；`粗黑、衬线/手写和稳定小字共同组成版式`；`纹理、阴影和网点必须服务版面`。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
