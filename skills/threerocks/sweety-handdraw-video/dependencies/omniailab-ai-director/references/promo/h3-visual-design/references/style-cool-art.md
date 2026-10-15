---
name: omniailab-promo-h3-visual-design-style-cool-art
description: 「炫酷艺术风｜H3 融合执行规则」—— 动态视觉设计（字体包装／追踪视觉／手绘融合） 方向细则：只在用户选择“炫酷艺术风”，或参考明确要求折射塑料、像素故障、主体驱动变形字体、高密度赛事海报、暗黑扫描裂变时读取。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 炫酷艺术风｜H3 融合执行规则

只在用户选择“炫酷艺术风”，或参考明确要求折射塑料、像素故障、主体驱动变形字体、高密度赛事海报、暗黑扫描裂变时读取。本风格固定把四类机制融合成同一套视觉 DNA；13–15 秒按顺序完整呈现五个连续状态，不提供风格底盘分支选择。

融合不是同时堆四套滤镜。让同一组材质、字体、信号线和主体关系连续变形：`透明折痕 → 字体拼贴格/弧形场 → 3D 字块与事件海报 → 暗黑扫描裂变 → 融合终版海报`。

## 导航

- 第 1–2 节：锁定全片共用的材质、色盘、字体与图形角色。
- 第 3–4 节：统一变形主线和 15 秒固定状态。
- 第 5–7 节：时长适配、原片权限、声音与最终 Prompt 锁定块。
- 第 8–9 节：生成指令检查与用户参考转译。

## 1. 固定融合 DNA

生成 Prompt 前写：

```text
COOL_ART_FUSION = {
  persistent_material: clear_crumpled_plastic + frosted_glass + chrome_reflection,
  palette: mist_white / silver / graphite_black / signal_red_orange / micro_acid_green,
  core_type_family: modular_geometric_display + neo_grotesk_width_italic_variants + semi_mono_utility,
  shared_signal: one red_orange line,
  density_curve: sparse_refractive_interface → subject_responsive_type_morph → event_poster_density → dark_scan_climax → fused_poster_resolve,
  transformation_spine: fold → tile → arc/tape → 3D type block → scan line/fracture → fold
}
```

### 材质锚点

- 全片持续保留透明皱褶塑料、磨砂玻璃或银色/虹彩金属中的可见联系；即使进入黑场，折痕高光、透明边缘或 chrome 反射仍要证明它们是同一世界。
- 折射只让材质后方的字/背景局部位移 1%–3%；不融化主体，不改变 Logo 几何，不破坏中文偏旁和英文拼写。
- 所有塑料折痕沿 2–4 条固定折线运动；所有金属高光沿同一个主体轮廓或 3D 字块边缘运动，不随机闪烁。

### 产品主体适配

当 `subject_type=product`，先把 `PRODUCT_PROTECTED_LAYER` 当作内部渲染检查，再把本风格映射到保护层之外。它不是故事主题、屏幕文案或视觉事件；最终 Prompt 只需一句轻量身份锁，不要反复解释“结构完整”。

- 透明塑料、磨砂玻璃和折射面只在产品前后景、背景面板或独立载体中显影；不得覆盖成产品材质，也不得改变产品任一分区的透明度。
- 文字不默认贴在产品旁边：至少建立两块独立空间平面（地面/后墙、玻璃/前景板或海报分栏），让主字沿真实消失点跨平面、形成通道或前后景交换；只有一条辅助字带可以沿产品外轮廓的外侧偏移，始终留出清楚间距。字体与产品保持独立景深，不黏连、不共享轮廓、不互相生成。
- 3D 字块是由白名单文字构成的独立图形载体，不由产品折叠、切片或拆件形成，也不使用产品结构或负形作为镜头入口。
- 扫描线、裂隙和颗粒从产品背后、投影、倒影或相邻包装面经过；产品本体只接受源材质允许的光照响应，不出现结构裂变或部件剥离。
- 建立态与终版保留清楚的主体识别；局部微距只能由镜头裁切画面，不能裁断或重组产品。最多一次短暂遮挡非关键外轮廓，随后产品和文字各自恢复。不要把“结构完整、组件关系、透明度”等保护术语写进文案或标签。

### 统一色盘

- 高键阶段：雾白/浅银灰 `#ECEDEE–#F7F7F5` + 石墨黑 `#202124`。
- 主专色：信号红橙 `#EB3C24–#FF4A16`，承担基线、主标题、扫描和事件海报色场，占新增包装 8%–30%。
- 微专色：荧光黄绿 `#C7FF2E`，只承担一个真实日期/数字/标签或 2–4 个小标记，占比不超过 5%；没有真实信息时不用。
- 暗场阶段：黑/炭灰 `#050607–#17191C` + 同一信号红橙；全片只允许一次 0.10–0.25 秒高键反白。

本分支覆盖通用“必须颜色反转”的最低交付：高键折射界面进入黑橙赛事海报与暗黑扫描，再回收成高键/暗色并存的终版海报，原片锁定模式只切换新增包装层，不重调原素材。

## 2. 固定字体与信息层级

读取主 Skill 的 `COPY_BRIEF / COPY_DECK / TEXT_WHITELIST`。Display A/B/Utility 必须使用不同文字与语义；同一文字只在自己的角色内跨状态变形。

```text
TYPE CAST:
- Display A: [master id]；宽体/高字重模块化几何无衬线或自定义模块方黑；6%–12% 水平切槽；承担折射后景大字、3D 字块六面、黑橙赛事主标题与暗场扫描 Hero。
- Display B: [不同 secondary id]；同一 neo-grotesk 家族的 Regular / Bold / Condensed / Italic 变化；承担人物穿字、弧形/环形基线、透明信息带和第二海报标题。
- Utility: [不同 editorial_label ids]；稳定中性无衬线/半等宽；承担磨砂卡、真实功能/日期/参数/队伍/地点/Ticker。
- Marks: 无文字细网格、红线、3×4/4×4 点阵、折痕高光、像素竖带、真实 Logo 轮廓和少量定位十字。
```

- 不再默认“超窄粗体 + 编辑衬线/现代宋 + 笔刷手写”。风格统一性来自模块几何主字与 neo-grotesk 宽窄/正斜变化。
- 中文主标题的水平切槽只发生在笔画内部安全区；完整字先可读，切槽后仍保持偏旁、交叉点和方形重心。
- 弧形/环形文字使用 Display B 的另一条准确文案，不把 Display A 原句换排版冒充新层级。
- 微小信息必须真实。没有用户/台词/素材提供的日期、比分、队名、参数、Logo、编号或赛事信息时，删除该槽位，用无文字网格和点阵保持密度；禁止 Lorem ipsum、伪坐标和假 Ticker。

### 字体进入空间，而不是粘在主体旁边

炫酷艺术风必须把字体当成可被镜头经过的空间平面，学习音乐短片里“字面就是舞台”的关系：

- 先让主标题在后墙或地面完整出现，再把同一平面沿一个消失点延伸到另一平面；相机可沿字面、字腔或两块字板之间穿行，字形保持一次完整可读停留。
- Display B 进入玻璃、透明膜、前景框或侧向海报板，和 Display A 分开基线、尺度与景深；至少一次由后景转前景或由前景退到后景，形成视差和遮挡，不把所有文字贴到产品轮廓线上。
- 产品只作为空间锚点，文字可以从主体运动方向获得 cue，但不能从产品组件、空洞或负形生成；主体与字块之间保留可见空气层。
- 文字先读懂再变形：进入 → 完整可读 → 透视/折叠/套印响应 → 回到稳定版面。一个状态只设一个最强运动焦点，其他文字停稳。

## 3. 同一元素的连续变形合同

### 折痕 → 拼贴格

透明塑料先从真实画边铺开，折线交点成为 4×4 或 6×4 网格。人物/场景可使用主体真实局部裁切、Display A/B 的完整字母/汉字和无文字银灰面；不得复制五官或制造多张脸。产品模式的网格只切分文字、背景、反射或独立包装面，并围绕完整产品合并，不切分产品保护层。

### 拼贴格 → 字母弧线/景深交换

网格沿一个方向合并成完整主体和完整 Display B。Display B 字母/字组随后整体脱离基线，沿人物手势、主体运动方向或完整外轮廓的外侧偏移路径形成 180°–300° 弧形场；字符保持完整。人物可与字体做一次受控前后景交换；产品只与独立字体层交换景深并保持清楚间距，不穿入字形、不与文字黏连，随后字体形成透明信息带。

### 信息带 → 3D 字块/赛事海报

同一透明信息带收紧成独立 3D 字块的一条边；Display A 的真实笔画与不同白名单短句折成可读六面体。字块旋转 90°–180°，一个面扩张成硬切边，进入黑橙高密度海报。3D 字块与塑料折射共享包装层光路；主体只匹配同一主光方向并保持自己的源材质，不变成金属、玻璃或字块。

### 赛事色带 → 扫描裂变

环绕主体的信息带在一侧收窄成唯一红橙扫描线；事件海报的主标题退到后景黑场。扫描线经过 Display A 后，让 20–40 条短线沿真实笔画向内聚合；局部红色裂隙/颗粒只出现在主体背后的影子、倒影或相邻包装面，触碰文字时只触发一次 2–4 帧水平像素拉伸，不覆盖或切开主体本体。

### 裂变颗粒 → 终版折痕

裂隙颗粒只沿主体投影或相邻包装面的一侧剥离，随后变成透明塑料膜的银色折痕高光；主体自身始终完整。黑场与雾白面板重新拼成同一张终版海报。最初的红线回到版面基线，3D 字块的一个面变成终版磨砂信息卡。

## 4. 15 秒固定融合状态

```text
STATE 1｜0.0–2.6s｜REFRACTIVE REVEAL
雾白银灰留白；Display A 以柔焦超大后景字出现；透明皱褶塑料在中景显影；磨砂卡与 Utility 在前景锐利建立。唯一红橙细线横穿一次，折痕让后景字局部折射 1%–3%，随后稳定。

STATE 2｜2.6–6.0s｜SUBJECT-RESPONSIVE TYPE MORPH
折痕交点形成 4×4/6×4 网格，人物/场景真实局部或产品外部包装面与不同 Display B 字组组成拼贴；网格合并恢复完整主体和完整文案。红线转为弧形运动轨道，Display B 沿主体动作或完整外轮廓的外侧偏移路径形成 180°–300° 字体弧线；人物可受控穿字一次，产品只做保持间距的景深交换。

STATE 3｜6.0–9.2s｜TYPE BLOCK / EVENT POSTER
弧形线带收紧为透明信息带并折成 3D 字块边缘；Display A 笔画与白名单短句形成可读六面体，旋转 90°–180°。一个面扩张硬切为黑橙赛事/事件式海报：模块化主标题、中心主体、透明环绕带、真实 Utility 和底部非伪造信息层同时落位，稳定 0.8–1.0 秒。

STATE 4｜9.2–12.1s｜DARK SCAN FRACTURE
信息带收成一条红橙扫描线，新增包装层进入炭黑；Display A 由径向短线聚成完整扫描 Hero。短暂高键反白 0.10–0.25 秒后插入一个真实局部微距；主体背后的影子、倒影或相邻包装面出现单侧裂隙光/颗粒并触碰字边，引发一次 2–4 帧像素拉伸后完全复位，主体本体不裂变。

STATE 5｜12.1–15.0s｜FUSED POSTER RESOLVE
裂隙颗粒转成银色塑料折痕；雾白磨砂面板与黑橙事件面板在同一网格中锁定。中心主体、模块 Display A、弧形/透明带 Display B、真实 Utility、红橙基线和 chrome/塑料材质共同组成终版海报；荧光黄绿只点亮一个真实信息。完整稳定 1.0–1.4 秒后收尾。
```

五个状态必须继承元素：红线贯穿五段；塑料折痕变网格/字块/终版材质；Display A 始终使用同一骨架；主体身份和主光方向不变。不得把每个状态写成独立模板。

## 5. 时长适配

- `13–15 秒`：完整执行五个状态。
- `9–12 秒`：把 STATE 1+2 压成 3 秒，保留 3D 字块/事件海报、扫描裂变和终版，共 4 个状态。
- `6–8 秒`：折射网格与主体/字体景深交换合并；3D 字块硬切事件海报；扫描裂变直接回到终版，共 3 个状态。
- `4–5 秒`：前半以折痕网格组出主体/主字，后半让同一字块旋转硬切为带扫描裂隙的融合终版；仍需同时看见塑料/主体字/事件层级/暗红扫描四个 DNA，不逐项展开长段落。

## 6. 原片权限

### 锁定原片，只做包装

- 保持原片镜头、动作、剪辑、色彩、光线和声音；高键/暗场切换只作用新增面板、文字、塑料膜和局部覆盖层。
- 人物/场景网格只裁切原片同一时刻的真实局部，不复制人物；产品网格不裁切产品保护层。人物穿字只改变字体景深；产品与字体保持间距。裂隙只作用新增包装面、影子或倒影，不改变脸、Logo 或产品结构。
- 原片没有可用的动作弧线、表面或切点时，用真实画边/剪辑边继承红线与折痕，不重拍主体。

### 根据视频二创 / 架空重建

- 可建立统一摄影棚、折射界面、事件海报和暗场，但保持人物、产品、Logo 与事件身份。
- 相机只做一次低角度/穿字、一次围绕 3D 字块或一次塑料膜前后轻推近；不自动变成 MV 快切。

## 7. 融合声音合同

读取 `music-direction-library.md` 的炫酷艺术分支。声音也走同一条顺序，不把四套声效同时叠加：

```text
0.0–2.6s: filtered air + one foil/plastic flex + thin glass tick。
2.6–6.0s: clean beat + one short tile-click cluster + restrained air swipe。
6.0–9.2s: one metallic tape snap + one deep 3D block hit。
9.2–12.1s: 0.10–0.20s silence → one narrow scan zap → one dry fracture crack。
12.1–15.0s: low sub tail + one glass settle tick；all distortion decays before the final hold。
```

每个状态遵循：`MATERIAL / SUBJECT CAUSE → TYPE RESPONSE → DEPTH EXCHANGE → FULLY READABLE HOLD → TRANSFER`。主文字稳定可读 0.55–1.2 秒；速度线、纸裂、持续震动、无限切片、连续 glitch bed 和全屏频闪不再是默认动作。

## 8. 可直接写入 H3 Prompt 的锁定块

```text
COOL ART FUSION LOCK:
Use one fused system, not four selectable styles: transparent plastic refraction → subject-responsive packaging mosaic/curved type → 3D type block and dense event poster → dark scan fracture → fused final poster.
PERSISTENT MATERIAL: clear crumpled plastic + frosted glass + chrome reflection, sharing one highlight path across all states.
PERSISTENT SIGNAL: one red-orange line transforms into baseline → arc path → transparent information tape → scan line → final baseline.
TYPE CAST: Display A=[master id + modular geometric skeleton]；Display B=[different secondary id + neo-grotesk width/italic/curved role]；Utility=[different verified labels]；no serif/brush default and no fake microcopy.
STATE INHERITANCE: fold→tile→3D face→scan streak→fold；subject identity, type skeleton, palette roles and light direction remain continuous.
PRODUCT IDENTITY CHECK (internal, not on-screen): when subject_type=product, retain source-visible silhouette, key component relationships, material/transparent regions, controls and Logo; all plastic, fracture, scan, 3D type and portal effects stay on independent packaging layers. Never turn this check into a title, label or visual event.
SPACE TYPE RELATION: use at least two independent planes (floor→wall, glass→foreground board or poster panels) sharing one vanishing point; let the main title cross planes or become a camera corridor, while the product remains a separate depth anchor with visible air around it.
BOUNDARY: exact readable text before/after every deformation; no random data, continuous glitch, generic speed lines, paper tear, full-frame strobe or unrelated effect stack.
```

## 9. 生成指令前检查

- 13–15 秒是否完整包含折射塑料、主体变形字、3D 字块/事件海报、暗黑扫描裂变和融合终版？
- 四类机制是否通过同一红线、同一折痕、同一 Display A 骨架和同一主体连续变形，而不是四段模板拼接？
- 字体是否统一为模块几何主字 + neo-grotesk 宽窄/正斜变化 + 半等宽 Utility，没有退回衬线/手写乱配？
- Display A/B/Utility 是否使用不同白名单文案；日期、比分、Logo、参数、编号和 Ticker 是否全部真实？
- 故障是否为一次可计数的折射/竖带/扫描/像素拉伸，并在 2–4 帧内复位？
- 人物/场景是否通过受控网格与景深交换参与；产品是否只是独立空间锚点，字体是否进入墙/地/玻璃/前景板而不是粘在产品旁边？
- 产品身份检查是否通过且没有被写成画面主题、屏幕文案或标签；是否没有切产品、拆组件、产品透明化、产品充当镜头入口或与字体融合？
- 最终融合海报是否稳定 1.0–1.4 秒，所有材质、文字、主体和信息层都有清楚主次？
- 锁定原片时是否没有改变原镜头、调色、人物、产品和声音？

## 10. 用户参考锚点：只内化机制

- [Ctrend｜科技像素故障塑料折痕反光反射](https://www.xiaohongshu.com/discovery/item/69d59e9c00000000230114ec)：内化雾白银灰底、透明皱褶塑料、磨砂卡、柔焦大字、细网格、红线/红点与短暂竖带错位。
- [乍见一隅｜字幕用得好，小导变大佬，第二弹](https://www.xiaohongshu.com/discovery/item/66ee76b50000000012010025)：内化网格拼贴合并、完整词拆成字母场、环形/弧形/透视排版、人物层景深交换，以及产品外轮廓保持间距的字体弧线。
- [高兴品牌｜英雄联盟 LPL 赛事包装](https://www.xiaohongshu.com/discovery/item/68932eb10000000005005822)：内化模块化中文主标题、2D 标题转 3D 字块、金属主体、透明环绕带与高密度真实信息层级。

从用户上传的暗黑 H3 参考中内化径向红线聚字、横向扫描条、中心人物与后景大字、一次黑白反相、局部微距、裂隙光与单侧粒子剥离。所有参考只提供机制和审美校准，不复制其中品牌、人物、Logo、广告卖点、水印或原文案。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
