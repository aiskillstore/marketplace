---
name: omniailab-promo-h3-visual-design-style-dark-pop-glitch
description: 「暗黑胶片故障风｜Dark Pop Glitch」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：只在用户选择“暗黑胶片故障风”，或明确要求 dark-pop、cyber-grunge、rap MV、黑红高反差、地下音乐杂志、zine 拼
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 暗黑胶片故障风｜Dark Pop Glitch

只在用户选择“暗黑胶片故障风”，或明确要求 dark-pop、cyber-grunge、rap MV、黑红高反差、地下音乐杂志、zine 拼贴、胶片扫描、复印纸故障、Logo/字标发布片、模型发布视觉时读取。本风格适合人物、Logo、字标、模型名和强封面感视觉；不是廉价霓虹赛博，也不是把主体做成怪物。

核心目标：用写实高时装广告的主体质感，加地下音乐杂志的印刷破坏感，做一条压迫、冷酷、可读、能落成封面的 H3 字体包装片。

## 1. 固定视觉 DNA

生成 Prompt 前写：

```text
DARK_POP_GLITCH_DNA = {
  mood: cold_controlled_danger + fashion_ad + underground_music_zine,
  palette: deep_black + saturated_blood_red + dirty_white + charcoal_gray,
  texture: 16mm_grain + photocopy_halftone + scan_misalignment + ink_bleed + exposure_burn,
  cut_language: hard_cut + jump_cut + single_frame_insert,
  glitch_rule: impact_only_then_restore,
  final_form: high_contrast_magazine_cover_lockup
}
```

- 黑色不是空背景，而是深灰黑摄影棚、炭灰纸面、扫描阴影和印刷墨层；红色只承担品牌字标、裂纹光、套色偏移和最终封面重点。
- 故障效果只作为 1–6 帧的视觉冲击；每次故障之后必须恢复主体身份、Logo/字标拼写和画面主构图。
- 全片使用硬切、跳切、单帧插入和短促闪光，不使用淡入淡出、柔和叠化、梦幻光晕或连续 RGB glitch bed。
- 参考美学来自 90s/00s 独立音乐杂志、复印纸、胶片扫描、rap MV 封面和 zine 拼贴；不要生成赛博城市、彩虹霓虹、游戏 UI 或伪代码界面。

## 2. 主体与 Logo/字标保护

本风格常用于 `subject_mode=logo_motion_stage`、人物封面、模型发布视觉或人物 + 大字标组合。先建立：

```text
IDENTITY LOCK:
- logo_layout_type: pure_logo | logo_with_cover_anchor | not_logo
- protected subject: [face/product/logo/name/scene facts]
- protected wordmark: [exact spelling/case if provided]
- readable moments: [time ranges where subject and wordmark are fully clear]
- permitted damage: packaging layer, shadow, background, scan layer, printed carrier
- forbidden damage: facial structure, logo geometry, letter order, product parts, scene identity
```

- Logo、品牌名、模型名和背景标题至少一次完整、清晰、正确拼写；可做拖影、套印、扫描错位，但不能改字母结构或生成乱码。
- 先从参考图判断 `logo_layout_type`：纯 Logo 走字形轮廓、字腔、扫描、材料和重组；Logo + 人物/物件走“字标主导 + 封面锚点保护”。不要让用户额外选择。
- 人物保持五官、发型、正面/侧面身份和表情克制；不得变骷髅、怪物、机器人，不夸张张嘴，不改变年龄、性别或面部结构。
- 产品/Logo 不做本体碎裂、融化、透明化或部件散架；裂纹、粒子、墨迹和扫描只作用在光影、背景、包装面或反射层。
- 如果用户提供首帧/参考图，首帧构图、主体轮廓、主色和关键字标必须延续；镜头运动从这张图的空间里生长，不另起一个背景。
- `logo_motion_stage` 遇到清晰人物、雕塑、动物、产品或物件时，按“字标主导 + 封面锚点”处理：Logo/模型名决定字体系统和版式节奏，主体决定封面压迫感、景深和最终定格；不得把主体挤成边角贴图，也不得让大字持续覆盖主体脸、轮廓或关键材质。

## 3. 字体与版式系统

```text
TYPE CAST:
- Display A: [exact brand/model/title]；粗窄无衬线、压缩 grotesk、模块方黑或厚重中文黑体；承担巨大后景字标、全屏 Hero、封面主标题。
- Display B: [different exact phrase]；黑白红杂志副标题、竖排短语、侧栏标题或高对比编辑字；承担冲击状态和局部微距。
- Utility: [real short labels]；半等宽/中性窄体小字，只写真实或用户允许的短标签、编号、边缘扫描标记。
- Marks: 裁切线、扫描编号、半色调网点、套印十字、边缘印刷标记、黑色墨迹、胶片划痕；Marks 不伪造数据。
```

- Display A 必须先完整可读，再进入切片、套印、拖影或遮挡；不要从一开始就把字打散。
- 中英文混排时，中文负责主信息或情绪钉子，英文负责独立编辑标签；不逐条翻译同一句话，也不用孤立英文词填版。
- 最终封面只叠少量信息：如用户提供的模型名、真实编号、发布标签或 `NEW VIDEO MODEL` 这类被需求允许的短标签；不能编造价格、日期、奖项、媒体名或 CTA。
- 如果白名单只有 Logo/模型名等极少文字，不要把同一词在 Display A/B/Utility 中反复堆满画面；Display B 可改为同一字标的局部字腔、轮廓、低对比重复场或非可读图形化切片，Utility 可省略，密度由 Marks 和镜头切换承担。

## 4. 故障艺术动作库

每个状态只选 1–2 个故障动作，并写清触发、持续时间和复位：

- `Negative flash`：插入 1 帧黑白高反差负片，立刻硬切回主画面。
- `Scan tear`：把人物/字标的包装层分成极薄水平切片，错开 2–4 帧后复位；主体结构不变。
- `Registration offset`：红/黑/白套印偏移一次，偏移量小，下一帧或下一个鼓点恢复清晰。
- `Photocopy rip`：复印纸撕裂边、扫描条或墨层作为转场，只撕开包装面，不撕裂脸、Logo 或产品。
- `Halftone macro`：硬切 2–4 帧到眼睛、字标边缘、材质纹理或印刷网点微距，再切回主构图。
- `Exposure burn`：局部红/白曝光灼烧 0.10–0.25 秒，只扫过高光边或标题边，不吞掉主体。
- `Particle recoil`：黑色颗粒或红色发光粉尘从阴影、裂纹、背景字边喷出后反向吸回；主体最终完整。

禁止连续整片故障、满屏乱码、随机 HUD、RGB 彩虹重影、长时间频闪、血液内脏、卡通渲染和主体身份漂移。

## 5. 15 秒状态结构

```text
STATE 1｜0.0–3.0s｜STILL PRESSURE
延续首帧/主构图建立 0.6–1.2 秒，随后进入一次 logo-only 或字标局部抽象状态：字腔、横向扫描、红色能量线或反相字标成为主画面。主体/封面锚点可暂时退入阴影或被硬切离开，但身份不改。2.0–2.8s 可插入 1 帧黑白负片。

STATE 2｜3.0–6.0s｜SCAN TEAR / WORDMARK SHOCK
第一次重拍触发扫描撕裂：包装层水平切片错位后迅速复位。硬切到主体局部、Logo 边缘或字标微距，红色裂纹/套印偏移在鼓点上出现一次，随后回到中近景。若 Display A 变成 75%–110% Hero，只持续 0.55–0.8 秒并完整可读，立刻退回后景或边界，不长期压住封面锚点。

STATE 3｜6.0–10.0s｜ZINE COLLAGE ATTACK
用 2–4 个极短硬切插入半色调微距、复印纸撕裂、黑白闪光照片、字标局部和材质纹理；每个 2–4 帧。复印纸和网点只能是插入或局部载体，不把整段变成明亮拼贴海报。主镜头可小幅绕拍或轻推近，形成真实空间视差；主体仍是封面锚点，主字标仍能找回。

STATE 4｜10.0–13.0s｜RED IMPACT
音乐最强拍点让红色裂纹、标题拖影、颗粒喷射或曝光灼烧同时爆发一次。Display A 被冲击波短暂拉伸但保持可辨；主体/封面锚点必须回到中心或稳定主景深，形成“字标事件击中主体”的因果关系。可加入一句用户确认的短口播或屏幕标题，动作极小、语气冷静。

STATE 5｜13.0–15.0s｜MAGAZINE COVER FREEZE
所有颗粒悬停或回收，音乐抽空，只保留低频余震。镜头拉回接近首帧/主封面构图；主体、Logo/字标、Display A、少量 Utility 和印刷标记锁成高反差杂志封面，稳定 1.0–1.4 秒，最后一拍落板。
```

短时长压缩：6–8 秒保留 `Still pressure → Scan tear → Red impact → Cover freeze`；9–12 秒保留四段；13–15 秒完整执行五段。

## 6. 原片 / 图生视频权限

### 锁定原片，只做包装

- 保持原片镜头、剪辑、速度、人物、Logo、调色和声音；新增黑红标题、半色调、扫描层、印刷标记和短故障只覆盖包装层。
- 不改原片背景文字，不把原片内容重拍成另一个 MV；所有故障必须在 2–6 帧内复位。

### 根据视频二创 / 架空重建 / 图生视频

- 可以建立黑灰摄影棚、地下杂志纸面、巨大后景字标、微绕拍和最终封面，但必须继承主体身份、首帧构图、字标拼写和主色关系。
- 图生视频把参考图当准确起始帧；0 秒画面先像参考图，后续运动是微推进、硬切、扫描、颗粒和封面落板，不突然换场景。
- 架空重建不是 15 秒重复同一张完整封面。必须在前半段至少一次离开完整封面，进入字标局部、抽象扫描、能量线、微距或负片状态；再把它们回收成最终封面。

## 7. 声音与画面同步

读取 `music-direction-library.md` 的暗黑胶片故障分支。声音必须像剪辑里的触发器：

```text
0.0–3.0s: low synth descent + tape hiss + close breath / room pressure.
3.0–6.0s: distorted 808 hit + scan zap + short reverse inhale, tied to scan tear.
6.0–10.0s: dry industrial metal hit + film projector rattle, tied to hard-cut inserts.
10.0–13.0s: strongest sub impact + exposure burn + particle blast, then immediate space.
13.0–15.0s: low-frequency aftershock + one final dry flash/camera hit for the cover freeze.
```

如果原片有对白或指定声音，保持原声在前；新增音效只在故障、硬切、封面落板处短促出现，不盖住人声和品牌名。

## 8. 可直接写入 H3 Prompt 的锁定块

```text
DARK POP GLITCH LOCK:
Build a realistic dark-pop / cyber-grunge editorial packaging video, combining high-fashion subject lighting with underground music zine print damage.
PALETTE: deep black / charcoal gray / saturated blood red / dirty white. No rainbow neon and no cheap RGB glitch.
TYPE: Display A is the exact Logo/model/title in heavy condensed sans or modular bold black type; Display B is a different editorial phrase; Utility contains only verified short labels.
SPARSE TEXT RULE: if the text whitelist contains only Logo/name/model text, do not duplicate it as multiple large readable layers in every state; use glyph counters, crop fields, scan slits, silhouettes and non-readable print marks for density.
ANCHOR RULE: when a visible person/object cover anchor exists, keep it as the protected center of pressure and depth; type may briefly pass foreground but must restore clear anchor visibility.
GLITCH: use hard cuts, jump cuts, 1-frame negative flash, 2–4-frame scan tear, red/black registration offset, halftone macro, photocopy rip and short exposure burn. Every glitch restores subject identity and exact wordmark spelling immediately.
IDENTITY: preserve face/product/logo geometry, first-frame composition, hair/silhouette/material/color and all exact text. Do not mutate into skull, monster, robot, random letters or new background words.
FINAL: resolve into a high-contrast magazine cover freeze with readable subject, readable wordmark, small print marks and one clean final beat.
```

## 9. 生成指令前检查

- 是否明确使用黑/炭灰/血红/脏白，而不是霓虹彩色赛博？
- Logo、模型名、背景字标和所有必现文字是否至少一次完整可读且拼写正确？
- 人物/产品/Logo 是否保持身份，没有怪物化、机器人化、融化、散架或改结构？
- 若存在人物/物件封面锚点，它是否始终承担压迫中心或最终封面中心，而不是被大字长期挤出画面？
- 前半段是否至少一次进入字标局部/抽象扫描/能量/微距状态，而不是 15 秒重复完整封面？
- 稀少文字是否没有被反复复制成满屏大字，密度是否由非可读 Marks、字腔、裁切、扫描和镜头状态承担？
- 故障是否短促、可计数并复位，而不是连续噪声或乱码？
- 是否使用硬切、跳切、单帧插入和微距，而不是柔和转场？
- 是否有 13–15 秒的封面定格、少量真实 Utility 和最后落板？
- 图生视频是否从参考图准确起步，并把参考图的构图、主体和字标作为全片锚点？

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
