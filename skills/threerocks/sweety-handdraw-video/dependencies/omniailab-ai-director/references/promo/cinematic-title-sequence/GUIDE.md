---
name: omniailab-promo-cinematic-title-sequence
description: 电影与剧集片头（标题序列） —— 宣传片线方向之一：15 秒电影或剧集片头、标题序列、卡司序列与概念预告。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

> **在本 skill 中的位置**：15 秒电影或剧集片头、标题序列、卡司序列与概念预告。由**宣传片线总调度** `references/PROMO GUIDE.md` 在判定为该方向后接入。
> **生成口径**：提示词编译完成后，统一在 **OmniAiLab 画布** 中选择 **MiniMax H3** 生成视频；图像与资产类提示词仍按主线层级执行（`references/LIRA GUIDE.md`／`references/STYLE GUIDE.md`／`references/ASSET-SYSTEM GUIDE.md`／`references/PROMPT-DOCTRINE GUIDE.md`）。
> **与主干的关系**：本文件是宣传片线的方向细则，**不改变 P0→P6 主干与确认门禁**；涉及资产、表演、情绪、站位与光学时照常调用主线对应层。
> **暂停点**：素材与文字确认 → 方向与风格确认 → 提示词确认 → 生成 → 验收；每一步都等创作者确认后再继续，**不得一次跑完**。
> **触发词**：影视片头／标题序列／开场字幕／卡司序列／电影预告／剧集预告／概念预告

# 电影与剧集片头（标题序列）

把用户确认的影片方案、准确文字、字体系统、镜头、转场、可见特效和完整 15 秒音乐编译成一个可直接提交给 MiniMax H3 的中文 Prompt。默认设置：`MiniMax H3｜15 秒｜16:9｜2K｜24fps｜同步音乐与环境声｜中英双语屏幕文字`。

素材可选。无素材时可以提出原创虚构人物、世界、卡司和片名，但所有原创内容必须先进入文本方案让用户确认；不影射现实明星、现有电影、现有角色或受保护品牌。

## 1. 强制流程状态

每个新任务都必须遵循以下状态机；未经用户决定的事项不能跨级：

```text
TRAILER_FLOW_STATE=awaiting_scope
→ returned_to_main_agent（用户选择 15 秒以上）
或 → awaiting_design（用户选择单条 15 秒）
→ awaiting_reference_scope（存在参考图时）
→ awaiting_reference_scope_custom（仅选择自定义范围且尚未补充时）
→ awaiting_proposal_confirmation
→ ready_to_compile
→ ready_to_dispatch
```

先从用户当前需求判断范围，再决定是否询问 Gate 1：单条 15 秒成片直接记录 `scope_confirmed=true` 并进入 `awaiting_design`；15 秒以上或多片段完整预告直接返回主 Agent；范围缺失、含糊或互相冲突时进入 Gate 1。主风格、参考图用途和影片方案仍按各自 Gate 处理。同一任务的重做、改风格或修订可以复用已经明确确认的范围、语言、文字模式和素材用途。

确认卡 被拒绝、取消、报错、无返回值或返回值无法解析时，保持当前 `awaiting_*` 状态并停止。不得猜默认值、不得继续写最终 Prompt、不得使用 `视频生成`。

## 2. Gate 1：范围分流

`TRAILER_FLOW_STATE=awaiting_scope` 时，先按第 1 节使用当前需求中已明确的范围。只有范围仍然缺失、含糊或互相冲突时，才逐字使用下面这张只问范围的确认卡：

```text
header: 成片范围
确认卡： 这次先做一条 15 秒成片体验，还是制作 15 秒以上、由多个片段组成的完整预告？
options:
- 单条 15 秒体验（推荐）｜一次 H3 生成，内部包含多个镜头、准确文字和完整配乐，直接交付一条成片。
- 15 秒以上 / 多片段完整预告｜退出本 Skill，返回主 Agent 规划多段生成、剪辑和组装。
```

- 选择 `15 秒以上 / 多片段完整预告`：设置 `TRAILER_FLOW_STATE=returned_to_main_agent`，明确告诉用户将由主 Agent 继续规划，然后退出本 Skill；不得继续问风格、语言、文字或启动 H3 生成。
- 选择 `单条 15 秒体验`：记录 `scope_confirmed=true`，设置 `TRAILER_FLOW_STATE=awaiting_design`，进入 Gate 2。

## 3. Gate 2：三个固定设计问题

`TRAILER_FLOW_STATE=awaiting_design` 时，在同一个 确认卡流程中同时提交以下三个问题；不得改名、增删一级风格或临时改写选项含义。

用户输入已经包含四类之外的明确美术风格、媒介或时代视觉时，不把它新增为第五种风格，也不新增 Reference。先按主要画面如何构成，选择四类中制作机制最接近的一类；在 Gate 2 前用一段普通文本提醒并推荐：

```text
你描述的「[保留用户原词]」目前没有独立风格入口，最接近现有的「[四类之一]」。建议沿用它的[镜头/二维或空间组织/文字落版/音乐结构]，再把画面适配成你要求的[美术特质]；请在下面确认是否采用这个主风格。
```

如果没有高度相似项，明确说“没有完全对应项”，仍只推荐一个最适合作为结构模板的现有风格，不列多个备选。此推荐不替用户作答，Gate 2 仍必须出现。四个主风格的名称、顺序和说明保持固定，只把 `（推荐）` 标在当前推荐项：无额外风格要求时推荐电影叙事；有明确风格时标在最近似项。

```text
question 1
header: 主风格
确认卡： 这支 15 秒片头或预告希望采用哪种主视觉载体？
options（顺序固定，只把“推荐”标记放在当前推荐项）:
- 电影叙事｜真人或写实电影世界由人物行动推动；文字进入天空、墙面、道路、车窗等真实留白。
- 实拍动态图形合成｜保留真实人物与城市/建筑；多窗口、动态字体、玻璃折射、线条粒子和空间字幕承担主要节奏。
- 架空世界特效｜不可能物理法则、微缩模型或抽象空间成为主角；巨型异象、粒子介质和史诗文字构成奇观。
- 编辑拼贴包装｜纸张、照片、剪纸、杂志、日记、地图或胶片构成高密度动态版面，最终形成电影海报。

question 2
header: 屏幕语言
确认卡： 片名、角色卡和署名使用哪种语言？
options:
- 中英双语（推荐）｜中文为主信息，英文为副层；两套字形分别设计并共享版式关系。
- 纯英语｜所有可读片名、角色卡和署名只使用英文。

question 3
header: 文字内容
确认卡： 这条 15 秒成片希望出现哪些准确文字？
options:
- 基础电影卡司（推荐）｜片名、导演卡、2–3 位主要角色姓名卡；每张姓名卡包含主标题和身份/英文名/STARRING 等副标题。
- 基础卡司＋一句剧情钩子｜在基础电影卡司之外增加一句与可见剧情直接对应的短句。
- 用户自定义准确文字｜由用户提供片名、姓名、身份、署名或短句；未提供齐全前只做方案，不生成指令。
```

三个结果都有效后记录：

```text
design_confirmed=true
PRIMARY_STYLE=[四选一]
SCREEN_LANGUAGE=bilingual_cn_en | english_only
TEXT_CONTENT_MODE=basic_cast | basic_cast_plus_hook | user_exact
```

若用户确认的需求包含现有 Reference 未覆盖的美术风格，立即生成一份仅服务当前任务的 `AD_HOC_STYLE_SUMMARY`，不得把它保存为新风格或新 Reference：

```text
AD_HOC_STYLE_SUMMARY
user_style_exact=[用户原词]
template_style=[用户确认的四类之一]
visual_traits=[画布/材料；线条/造型；颜色/光影；构图/空间]
motion_traits=[主体怎么动；镜头怎么动；转场如何继承]
title_traits=[片名的字形、材质、位置和揭示方式]
audio_traits=[音乐气质、2–4 个音色锚、环境/动作声]
avoid=[最容易误生成且与用户要求冲突的画风、材料、滤镜或技术效果]
```

总结必须把风格名转成 H3 可看见、可听见的具体特质，不能只重复“国风、复古、高级、艺术感”。现有 Reference 继续提供提示词结构、节奏、镜头、转场、字体层级和音乐完整性；`AD_HOC_STYLE_SUMMARY` 只负责当前项目的画面表面与排除项。用户改选主风格时按新模板重新总结。

- 存在一张或多张参考图：设置 `TRAILER_FLOW_STATE=awaiting_reference_scope`，进入 Gate 3。
- 没有参考图：记录 `REFERENCE_SCOPE_MODE=not_used / reference_scope_confirmed=true / SEQUENCE_MODE=multi_scene`，设置 `TRAILER_FLOW_STATE=awaiting_proposal_confirmation`。

## 3A. Gate 3：参考图用途

只要当前任务存在参考图，`TRAILER_FLOW_STATE=awaiting_reference_scope` 时必须单独使用一次 确认卡；不得根据图片内容、用户说“参考一下”或历史默认值替用户选择。逐字使用：

```text
header: 参考图用途
确认卡： 这次希望参考图约束到什么程度？
options:
- 参考人物与影调（推荐）｜锁定人物身份、服装、颜色、光线和电影质感；原图环境只作为全片其中一个场景，其他场景在同一世界观内主动发散。
- 严格参考原景与人物｜全片只使用参考图中的人物和同一地点，不新增地点；允许变化景别、机位、动作、光线和特效。
- 自定义参考范围｜由你指定人物、服装、道具、场景、色彩、构图中哪些必须保持，哪些允许发散。
```

- 选择 `参考人物与影调`：记录 `REFERENCE_SCOPE_MODE=identity_grade_one_scene / reference_scope_confirmed=true / SEQUENCE_MODE=multi_scene`。人物身份、服装主特征和颜色影调可贯穿；原图环境必须映射为一个明确场景且全片只使用一次，另外至少发散两个不同地点/行动条件；原图站位和构图不自动锁定。
- 选择 `严格参考原景与人物`：记录 `REFERENCE_SCOPE_MODE=strict_same_scene_people / reference_scope_confirmed=true / SEQUENCE_MODE=single_scene_locked_reference / single_scene_user_confirmed=true`。不得新增地点或替换人物，但必须通过不同动作阶段、景别、机位、前中后景、光线和有来源效果形成至少三个可区分状态，不能把静态图只做十五秒慢推。
- 选择 `自定义参考范围`：记录 `REFERENCE_SCOPE_MODE=user_defined`，设置 `TRAILER_FLOW_STATE=awaiting_reference_scope_custom`，用普通文本请用户逐项说明人物、服装、道具、场景、色彩、构图的 `锁定 / 可发散` 范围并停止。收到明确范围后先复述映射，记录 `reference_scope_confirmed=true`，再根据是否允许新地点设置 `SEQUENCE_MODE=multi_scene | single_scene_locked_reference`。

参考图在 Gate 2 之后才上传、替换或新增时，必须进入或退回 Gate 3；参考范围变化后必须重做剧情确认稿。Gate 3 通过后设置 `TRAILER_FLOW_STATE=awaiting_proposal_confirmation`。

## 4. 先给方案，后生成

只有 `reference_scope_confirmed=true` 后才能进入 `awaiting_proposal_confirmation`。此时不调用 确认卡，也不生成最终 H3 Prompt。写确认稿之前必须先按第 5 节判定 `OUTPUT_MODE` 和主路由，并立即读取：

1. [case-calibration-matrix.md](references/case-calibration-matrix.md)
2. 已选主风格的一份 Reference
3. [cinematography-and-transitions.md](references/cinematography-and-transitions.md)

从已验证案例中选择唯一 `primary_calibration`，再把素材职责、场景扩展、人物行动和转场落点写进方案。禁止先根据一张参考图拟出单场景方案、等用户确认后才读取案例和转场库。参考图如何进入全片只服从 Gate 3：默认作为一个场景使用一次，不自动放在开头、结尾或贯穿全片；严格原景模式才允许整条停留在同一地点。

存在 `AD_HOC_STYLE_SUMMARY` 时，在确认稿最前增加一项 `风格适配`：说明推荐使用哪个现有模板、临时总结出的核心可见特质，以及明确不采用哪些冲突效果。用户确认的是“现有模板结构 + 当前任务风格摘要”的组合，不是新增风格。

然后用普通聊天文本给用户一份短而具体的确认稿，必须包含：

1. `素材用途`：逐张写明 Gate 3 选择、需要保持的可见锚点和允许扩展范围；默认模式必须指明原图环境落在哪一个且仅一个场景、另外发散哪些地点，严格模式必须明确不新增地点，自定义模式逐项复述用户边界。
2. `15 秒剧情/片头方案`：按时间顺序写清主体、触发或人物任务、行动、升级、结尾落点；Opening Title 也要写人物通过什么动作被认识。
3. `全部准确上屏文字`：逐卡列出中文、英文、大小写、换行和出现顺序；没有剧情钩子时不硬编短句。
4. `文字层级`：逐卡说明主标题、副标题和 Utility；角色卡默认以姓名为主层，以英文名、角色身份或 `STARRING` 为副层。
5. `字体方向`：说明 Display A、Display B、Utility 的骨架对比和主要材质，不只写“高级、电影感、现代”。
6. `场景扩展与转场落点`：`multi_scene` 至少列出 3 个一眼可区分的地点/版面与行动/效果条件，其中默认参考图环境只占一个场景，另有至少两个新地点；列出至少 2 条“前镜可见来源 → 切点 → 继承项 → 后镜新落点”。`single_scene_locked_reference` 则列出同一地点内至少 3 个动作/尺度/光线状态和 2 次内部转场。这是行动条件数量，不是强制镜头数。
7. `运镜与转场母题`：列出 2–4 个会贯穿全片的确定手法，如横向跟拍、动作匹配、前景遮挡、形状匹配、声音桥；不列备选项。

确认稿中的每个“新场景”必须同时改变地点/版面与人物任务、行动结果、世界尺度或效果状态中的至少一项。同一海边步道换景别、继续走路、继续对视、只改天空颜色，不算多场景扩展；它们只在用户明确选择严格原景时作为同一场景内部状态使用。

Agent 提出的片名、人物名、导演名、身份、剧情和短句都标注为“原创提案”。用户可修改任意一项。用户在同一条消息中给出一处准确文字替换，并明确要求“继续”“开始”“生成”或“生成指令”时，把新文字同步更新到整份确认稿、`TITLE_BIBLE` 和 `TEXT LEDGER`，记录 `proposal_confirmed=true`，直接进入 `ready_to_compile`。改动影响剧情、主风格、参考图用途或整体文字版式时，展示更新后的确认稿并继续保持 `awaiting_proposal_confirmation`。

其它方案修改在用户明确表达“确认”“可以，开始生成”“按这个生成”或“开始生成指令”后，记录 `proposal_confirmed=true`，设置 `TRAILER_FLOW_STATE=ready_to_compile`。沉默、问句、局部认可、确认卡失败或“先看看”继续保持方案待确认。

## 5. 成片模式与四类路由

只选一个 `OUTPUT_MODE`：

| 模式 | 触发 | 核心目标 |
| --- | --- | --- |
| `opening_title` | 片头、卡司、Opening Title、Opening Credits、Title Sequence、演员名字 PV | 影片世界和视觉识别优先；卡司、字体、空间关系与最终片名构成完整标题序列 |
| `single_clip_trailer` | 预告、概念预告、先导预告、teaser、trailer | 因果故事和卖点优先；观众能看懂主体、变化、行动、升级与未解决问题 |

按 Gate 2 的固定风格选择唯一主路由：

| 主风格 | 路由 | 必读 |
| --- | --- | --- |
| 电影叙事 | `cinematic_narrative` | [cinematic-narrative.md](references/cinematic-narrative.md) |
| 实拍动态图形合成 | `live_action_graphics` | [live-action-graphics.md](references/live-action-graphics.md) |
| 架空世界特效 | `constructed_world_vfx` | [constructed-world-vfx.md](references/constructed-world-vfx.md) |
| 编辑拼贴包装 | `editorial_collage` | [editorial-collage.md](references/editorial-collage.md) |

题材词不能改写主路由。换风格时只硬锁用户真实提供的命题、`user_exact` 文字、上传身份/品牌素材和权利边界；Agent 自创的场景、色盘、字体、镜头、转场和音乐按新路由重建，并重新发送方案等待确认。

## 6. 素材与已确认事实

检测到附件后先用 `媒体分析步骤` 只读分析内容、镜头、文字、色彩与声音。媒体分析请求必须只提取可验证事实：人物身份与服装、地点元素、色盘、光线、现有文字、构图层级和可见动作；不得让分析器决定参考范围、替整支成片设计慢推/侧移/同一场景延展，也不得把它给出的创意建议当成已确认事实。参考范围只由 Gate 3 决定。

参考图按 Gate 3 预设绑定职责，不再用模糊的“参考全部”：默认模式允许 `人物身份/服装 + 颜色影调 + 一个场景` 三项贡献，但禁止锁定全片构图；严格模式锁定人物与同一地点；自定义模式只使用用户白名单。视频和音频仍只指定一个 `primary_role`：`motion` 或 `audio_rhythm`，可记录一个次要贡献。Prompt 使用 `@图片1/@视频1/@音频1`，不写本地路径。

`identity_grade_one_scene` 下，无论静态图是否像完整海报，人物身份、服装主特征、色盘和光线质感可以贯穿，但原图环境、站位和构图只落入剧情方案指定的一个场景；其他场景必须保持同一人物与影调，同时更换地点和行动条件。`strict_same_scene_people` 下才把原景与人物锁定全片；`user_defined` 严格按用户逐项白名单执行。

内部登记产出模式、素材、参考范围、已确认命题、身份锚点、风格证据、准确文字、屏幕语言和音频参考；同时记录参考模式、锁定锚点、允许扩展范围、参考场景及其使用方式，以及构图是否锁定。

无素材时只能使用用户已确认的原创方案。不得在确认后临时增加人物、爱情关系、离别、旧信、秘密、灾难、时间跨度、地名、数字或沉重背景。

## 7. 文字内容按选择执行

- `basic_cast`：片名 1、导演卡 1、主要角色姓名卡 2–3；不设必须出现多少剧情短句。
- `basic_cast_plus_hook`：在 `basic_cast` 之外只增加 1 句已确认、且能由画面验证的剧情钩子。
- `user_exact`：只使用用户确认的准确文字；若不足以形成用户要求的卡司结构，回到方案阶段补齐，不猜写。

每张姓名卡使用主副标题：主层为姓名；副层从英文名、角色身份、`STARRING` 中选择已确认的一项或两项。导演卡同样区分姓名主层与 `DIRECTED BY / 导演` 副层。最终片名不再新增角色姓名。

内部建立 `TITLE_BIBLE` 与 `TEXT LEDGER`，逐字锁定中文、英文、大小写、换行、角色、出现顺序和来源。默认中英双语是同一语义组中的中文主层+英文副层；纯英语只保留英文。任何未出现在确认稿中的可读文字都不得进入 Prompt。

## 8. Reference 读取纪律

在 `awaiting_proposal_confirmation`、写方案之前读取：

1. [case-calibration-matrix.md](references/case-calibration-matrix.md)
2. 已选主风格的一份 Reference
3. [cinematography-and-transitions.md](references/cinematography-and-transitions.md)

在用户确认、进入 `ready_to_compile` 后再读取：

1. [h3-prompt-contract.md](references/h3-prompt-contract.md)
2. [typography-and-credits.md](references/typography-and-credits.md)

同一任务、文件未变化时复用已读内容。用户改风格或方案后只补读发生变化的风格 Reference，但必须重新完成方案确认。

## 9. 字体与运镜编译硬门

最终 Prompt 必须完整展开 `TYPE PROGRAM`，不能只出现“高级、清爽、现代、电影感字体”：

```text
Display A / Display B / Utility / Marks
→ 各自的骨架、字宽、字重、字距、端点/笔画、字腔、材质、颜色、尺度、空间位置、动态过程
→ 每张准确文字卡映射到唯一字体角色
→ scale ladder / COLOR SCRIPT / GRAPHIC KIT / SPACE BINDING / motion cue
```

每张文字卡都写清 `触发 → 构建/揭示 → 完整 → 阅读停留 → 一次响应 → 退出或继承`。Display A、Display B、Utility 至少在两项可见特征上形成对比；Utility 不是 Display A 的等比缩小。

每个主要镜头必须在内部补齐并在最终 Prompt 转为自然中文：

```text
camera_origin | size_and_lens | path_axis | foreground_pass | subject_action | endpoint | story_gain | transition_source | cut_point | inherited_item | next_landing
```

每镜只选一个主运动。最终 Prompt 中出现“横移或慢推、可以使用、可选、建议、例如、等方式”这类未决镜头方案时，`camera_plan_complete=false`，禁止生成指令。全片至少覆盖建立揭示、行动跟随、证据靠近、尺度释放中的三种摄影功能，并从动作匹配、形状匹配、前景遮挡、声音桥中确定使用 2–3 类。

运镜编译时同步完成 `TRANSITION SCORE`，不另起校验轮次。只有全片已经实际写入 2–3 类确定转场，并且至少两次跨镜转场都明确 `可见来源 → 覆盖/动作切点 → 后镜继承项 → 新地点/新行动条件/新主体/新片名空间`，才设置 `transition_plan_complete=true`。只在同一背景改变景别、继续走路或继续对视，不算完成一次有效转场；只列“前景遮挡、动作匹配”等手法名也不算。

## 10. 编译、校验与生成指令锁

1. 根据最新能力摘要确认 MiniMax H3 的合法时长、画幅、音频和参考素材范围。
2. 复用确认稿之前已锁定的素材 `reference_scope`、唯一 `primary_calibration`、`SEQUENCE_MODE` 和唯一母体；继承对应案例已验证的提示词结构、摄影、字体关系、效果链、转场种子与音乐完整性。若存在 `AD_HOC_STYLE_SUMMARY`，把其中的可见特质与排除项填入同一模板，不另起 Prompt、不新增 Reference，也不得让案例默认表面风格覆盖用户原词。不得在用户确认后才首次选择校准或把多场景方案缩回参考图单场景。
3. 按 [h3-prompt-contract.md](references/h3-prompt-contract.md) 写出中文 `final_h3_prompt`。最终 Prompt 只保留 H3 能直接看见、听见和执行的自然语言。
4. 硬范围 `5000–7000` 字符，目标 `5600–6500`。首次成稿后计数一次；越界时只允许一次确定性修整并再计数一次。不得第三次试算、来回重写或向用户直播计数。
5. 生成指令前必须显式得到以下内部结果：

```text
scope_confirmed=true
design_confirmed=true
reference_scope_confirmed=true
proposal_confirmed=true
prompt_length=5000..7000
type_program_complete=true
camera_plan_complete=true
transition_plan_complete=true
TRAILER_FLOW_STATE=ready_to_dispatch
```

任一项不成立：保持或退回对应状态，说明缺哪一项；不得进入视频生成。这条检查是视频生成的必要前置，不因用户催促、执行端可接受短 Prompt 或上一次生成成功而豁免。

6. 在本 Skill 内部保留一份生成指令检查记录：七项确认/编译状态必须为 true；写入唯一 `primary_calibration`、参考范围与序列模式、参考场景及其使用方式、确认稿中的可区分视觉条件和转场落点。默认模式若参考图环境未被明确映射为唯一场景、在全片重复出现，或少于两个发散新地点；严格原景模式若不是用户主动选择：均保持 `ready_to_compile` 并停止，不得进入生成指令。
7. 完整展示锁定后的唯一 Prompt，并在同一 assistant turn 直接进入视频生成；不得通过第二个写作者、摘要文件或临时文件翻译、压缩或二次改写。
8. 确认稿中的模型、时长、画幅、分辨率、原生声音选择和素材顺序在确认与执行之间保持不变。
9. 执行校验失败时只补齐缺失的能力信息，复用字符级相同的 Prompt、素材顺序与设置重发；不得删掉内部证明项、伪造成功或改用其它路线绕过。生成期间明确告诉用户“已经生成指令，正在生成”。
10. 完成后核对实际模型、分辨率、时长、画幅、音频和素材绑定，再交付成片。

## 11. 最终质量硬门

- 用户已经明确单条 15 秒或 15 秒以上时，是否直接采用该范围；范围缺失、含糊或冲突时 Gate 1 是否真实出现；选择 15 秒以上时是否立即回到主 Agent？
- Gate 2 是否一次同时出现固定四风格、双语/英语和三种文字内容？
- 用户提出四类之外风格时，是否先提醒并只推荐一个最近似现有风格；是否生成当前任务专用的具体风格摘要，再使用原有提示词模板，而没有新增风格或 Reference？
- 有参考图时 Gate 3 是否真实出现；默认、严格、自定义三种范围是否按用户选择执行？
- 剧情与全部准确文字确认稿是否通过原方案确认，或用户明确的“改单处文字并继续执行”指令得到确认？
- 默认参考图是否只锁人物/服装/影调并只占一个场景，同时明确发散至少两个新地点；严格模式是否确由用户选择；自定义边界是否逐项落实？
- 屏幕文字是否严格按 `TEXT_CONTENT_MODE`，没有为了密度硬编剧情句、数字、地名或关系？
- 角色卡是否都有姓名主层和身份/英文名/`STARRING` 副层？
- 电影叙事是否以完整表演和有意义的换景为准、不强制镜头数；另外三条路线是否至少有 5 个可区分环境/尺度/版面？是否有 4–6 个主效果和 8–14 个支撑效果？
- 是否完整展开 TYPE PROGRAM、三档尺度、颜色脚本、图形组件、空间绑定和每卡动态过程？
- 是否逐镜只有一个确定运镜，并写出起点、路径、前景、动作、终点、叙事增益和转场落点？
- 是否至少两次跨镜转场已写清来源、切点、继承项和新落点，且真正进入新地点、新行动条件、新主体或片名空间，而非同一背景换景别？
- 生成指令检查记录是否与确认稿逐项一致；不满足时是否确实停在 Skill 内而没有启动生成？
- 音乐是否只锁风格、情绪、2–4 个音色锚和完整能量弧，让 H3 自主作曲，同时有开场动机、推进、高潮和明确终止？
- `final_h3_prompt` 是否只计数最多两次、处于 5000–7000，并与实际执行为同一字符串？

## 12. 交付边界

本 Skill 只生成当前单条 15 秒成片，不创建 阶段执行计划，不进入 downstream workers，不自动生成更多版本，不自动剪辑长片，不自动重启 Electron。15 秒以上任务返回主 Agent，同一 15 秒任务重做时复用已确认 Gate。用户明确“改单处文字并继续”时可以直接执行；剧情、主风格、参考图用途或整体文字版式变化时回到方案确认。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
