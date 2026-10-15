---
name: omniailab-promo-anime-game-pv-visual-inputs
description: 「视频模式、视觉权威与分镜预览」—— 二次元漫画 ／ 游戏 PV 方向细则：所有图片、视频和用户文字先形成视觉候选，不直接形成最终画风。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# 视频模式、视觉权威与分镜预览

## 视觉权威决策矩阵

所有图片、视频和用户文字先形成视觉候选，不直接形成最终画风。Style Authority Gate 在 `GUIDE.md` 中负责取得用户确认；本文件只负责把已确认的 `style_source / visual_policy / reference_processing` 转换为唯一执行结果，不重复维护问题选项。

`style_authority_kind` 只允许 `existing_asset | generated_asset`。`visual_artifact_type` 只描述新生成视觉权威图的形式；直接复用素材时固定为 `not_applicable`。

| 已确认条件 | `style_authority_kind` | `requires_visual_authority_asset` | `visual_artifact_type` | 最终权威 |
| --- | --- | --- | --- | --- |
| 忠实继承人物或角色素材，素材可直接用于视频且无需清理载体 | `existing_asset` | `false` | `not_applicable` | 用户确认的原素材 |
| 忠实继承原素材，但需要清理背景、排版、UI、边框、裁切或载体污染 | `generated_asset` | `true` | `faithful_reference_frame` | 确认后的清理参考帧 |
| 用户文字给出新的视觉方向，或身份素材需要按该方向转换 | `generated_asset` | `true` | `directed_style_reference_frame` | 确认后的指定方向参考帧 |
| 人物身份需要与独立风格素材融合 | `generated_asset` | `true` | `style_fusion_reference_frame` | 确认后的融合参考帧 |
| 独立风格素材可直接进入当前视频模式，且不需要与人物身份融合 | `existing_asset` | `false` | `not_applicable` | 用户确认的独立风格素材 |
| 用户允许调整角色设定且未启用内部默认视觉路径 | `generated_asset` | `true` | `redesigned_character_reference_frame` | 确认后的角色重设计参考帧 |
| 启用内部默认视觉路径，包括允许角色重设计的情况 | `generated_asset` | `true` | `editorial_screencap_reference` | 确认后的动画截图参考 |
| 没有可直接进入视频参考的有效图片 | `generated_asset` | `true` | 按已确认视觉来源选择对应生成类型 | 确认后的视觉权威图 |

发生条件重叠时按以下优先级唯一确定结果：内部默认视觉路径 → 角色重设计 → 人物身份与独立风格融合 → 用户文字视觉方向 → 忠实素材清理 → 现有素材直接复用。没有有效图片时，根据最高优先级的已确认视觉来源选择对应生成类型。不得因为用户选择“直接制作”而跳过必要视觉权威图，也不得改写已经确认的 `production_route`。

人物图、立绘和三视图默认只锁定身份。只有用户明确选择保留其原画风时，原人物素材才可以兼任 `style`；不得因为图片自身具有韩漫画线、网点、水彩、赛璐璐或其它可识别媒介，就自动继承这些风格。场景、排版、动作或参考视频也只能在用户明确选为风格来源后贡献画风，否则只承担各自原始职责。

## 公共 Visual Authority Contract

“主视觉”表示后续视频使用的视觉权威角色，不表示固定画面形式。需要生成视觉权威图时，先确定 `visual_artifact_type`，再编译生图 Prompt；不能先写一份通用海报 Prompt，再用少量补充词适配不同路径。

每份生图 Prompt 必须以运行时 `working_language` 自然表达以下语义章节：

```text
参考职责
- 每份人物、风格、场景和排版素材分别承担什么，不允许职责漂移

身份边界
- 必须保留的身份特征
- visual_policy 允许改变的角色设定范围

画风与配色权威
- style_source、palette_authority、saturation_policy
- 内部默认视觉路径额外写入主题色、强调色预算和 character_palette_policy

载体排除
- 不继承原图中未获授权的背景、构图、裁切、文字、UI、边框、遮罩、水印或品牌

视觉产物形式
- 当前 visual_artifact_type 的构图、背景信息量、媒介和画面职责
- 明确该图不负责的内容，避免它锁死最终视频
```

缺少任一语义章节都不能提交生成。不得使用“生成高级主视觉”“做成宣传海报”“优化原图”或“保持原构图”等不区分路径的泛化指令。

## 内部默认视觉系统

仅当 `default_editorial_active=true` 时启用。`default_editorial_active`、Editorial 和系统名称均为内部字段，不得进入 Question Window、用户可见摘要、Prompt 标题或最终回复。用户只看到实际视觉方向、主题色、强调色和人物配色处理。

该系统的稳定身份是纯二维赛璐璐/手书动画加抽象编辑式 MG：纯黑、纯白、可选中性灰和一个高纯度高饱和主题色；可选极少量强调色；强剪影、平面纯色块、正负反转、分层剪纸或原画切片、网点或墨迹纹理、图形化空间和受控冲击帧。它不是普通彩色动漫插画，也不是暗黑霓虹、多色赛博或精致宣传海报。

主题色承担环境主场、核心道具/母题、UI/文字强调和转场载体，可在同一色相家族中改变明度。正常画面遵循 `dominant_theme_color ≈ black > white > accent`，不平均分色。强调色可为空；存在时只能承担一个 `accent_role`，单帧不超过 5%、全片平均不超过 3%，只能局限在小型物体、轮廓、眼睛、液体、裂缝或短促边缘，不能成为背景、整套服装、大型道具、城市灯光系统或持续轮廓光。

有角色图片时必须先锁定 `reference_processing`：

- `preserve_original_palette`：角色脸、发型、服装和原配色保持稳定；主题色只控制环境与 MG。角色额外颜色局限在角色自身，不扩散到其它图层。
- `flattened_palette`：保留角色原配色逻辑，但降低饱和度、取消柔和渐变并转为平面纯色块。
- `strict_single_hue`：角色转为黑、白、可选中性灰和主题色；仅保留用户明确指定的局部颜色，并限制在指定部位。

不得静默选择处理方式。人物身份始终保留脸型、眼型、发型轮廓与刘海分区、体型、服装结构、配饰、标志物、武器和人数关系；`reinterpret` 只保留用户确认必须继承的核心概念，其余按批准范围重建。

没有人物图片时跳过参考处理问题，设置 `reference_processing=not_applicable`。内部默认视觉路径的 `character_palette_policy` 使用 `strict_single_hue`；用户文字已明确角色必须保留的局部颜色时，将这些颜色记录为身份局部色并限制在指定部位。默认 `saturation_policy` 只表示主题色高纯度高饱和，不能被解释为整张图、肤色或角色全部颜色统一增艳。

内部默认视觉路径的视觉权威图固定为 `editorial_screencap_reference`，而不是宣传海报：生成与最终视频画幅一致的 TV 动画/独立手书 PV 截图感画面，使用特写或中近景、边缘裁切、轻微倾斜或仰视、停帧感，以及纯色、城市剪影、电线杆、电线、几何形或留白构成的低信息大色块背景。纯白或近白肤色、硬边纯黑赛璐璐阴影、干净锐利二维线稿；不使用自然肤色渐变、腮红、柔光、皮肤高光、玻璃质感眼睛、写实光照、复杂渐变或过度细节背景。

该截图只锁角色身份、配色纪律、线条质量和手书 PV 截图感，不规定最终视频的精确布局、完整故事、镜头路线、文字版式或 MG 节奏。若结果只是原图换色、仍由原背景/构图主导，或生成成精致海报、三视图、角色站桩图、最终分镜，则标记为 `invalid_visual_artifact`，不能成为 `style_authority`。

## 其它视觉权威图形式

| `visual_artifact_type` | 使用路径 | 画面职责 |
| --- | --- | --- |
| `not_applicable` | 直接复用已确认且生产可用的现有素材 | 不生成视觉权威图；实际素材本身承担 `style_authority`。 |
| `faithful_reference_frame` | 忠实原画风并需要先确认视觉，或需要清理原图载体 | 保持原角色、原画风和原配色，只调整为适合视频引用的姿态、裁切、简化背景和构图；不是海报。 |
| `directed_style_reference_frame` | 用户已给明确文字视觉方向 | 保持批准的身份边界，严格按用户方向生成；形式服从该方向，不追加 editorial。 |
| `style_fusion_reference_frame` | 人物身份与独立风格素材融合 | 人物图只锁身份，风格素材控制媒介、线条、色彩和质感；不得复制风格图角色、文字或品牌。 |
| `redesigned_character_reference_frame` | 用户允许重新设计角色 | 确认新版角色身份与所选画风，只改变批准范围；没有选择 editorial 时不自动单色化。 |

这些图与 `editorial_screencap_reference` 共享公共 Visual Authority Contract，但不共享具体画风、配色预算和构图模板。所有视觉权威图都不能被当作最终 Storyboard、首帧、尾帧或逐 Shot 参考，除非用户原文明示相应时间角色。

生成型 `visual_artifact_type` 按决策矩阵唯一确定：`default_editorial_active=true` 始终使用 `editorial_screencap_reference`，即使同时为 `reinterpret`；否则根据清理、文字方向、身份融合或角色重设计选择对应类型。忠实素材可直接复用、或独立风格素材无需身份融合时使用 `not_applicable`。不能同时选择多个类型，也不能在生成失败后静默换类型。

## 选择模式

以当前能力摘要为唯一能力来源。优先使用可用的默认视频模型路径；参考方式、文件限制和音频能力必须与摘要一致。

| 输入状态 | 模式意图 | 参考规则 |
| --- | --- | --- |
| 没有可直接进入视频参考的有效图片素材 | 视觉权威图路径 | 按当前 `visual_artifact_type` 生成并确认一张参考图，再用它承担可见画风权威。 |
| 已有一份或多份有效角色、场景、风格、动作、视频或音频参考 | 多模态参考路径 | 保持用户附件顺序，逐一声明每份素材贡献；视觉权威图与其它合法用户素材按最终 roles 进入槽位。 |
| 用户原文明示精确开场画面 | 时间锚定路径 | 仅在模型能力支持时把已确认图片绑定为开场状态，并描述后续连续发展。 |
| 用户原文明示精确开场与收束画面 | 双时间锚定路径 | 仅在模型能力支持时绑定两张时间图片，并描述中间连续变化。 |

若当前模型不支持目标模式或某类参考，先说明影响并用 confirmation card 确认切换模型、减少约束或调整模式；不得静默丢弃素材。

时间锚定路径只用于响应用户原文中的明确要求。用户未主动提出时，不介绍、不推荐、不询问首帧、尾帧、首尾帧或关键帧锁定，也不为了使用这些模式改变既定制作路径。

## 视觉参考生成

- 已有完成度高的角色/KV 图只有在 Style Authority Gate 已确认其最终职责、载体风险可接受且与所选模式一致时才能直接复用；需要清理背景、排版、裁切或 UI 污染时生成对应 `faithful_reference_frame`，不能把原载体直接传给视频。
- 没有可直接进入视频参考的有效图片素材时必须令 `requires_visual_authority_asset=true`，先完成当前路径的配色与 Visual Authority Contract，再生成对应视觉权威图；不得因为已有文字方向就跳过视觉确认直接生成视频。
- `default_editorial_active=true` 时只使用 `editorial_screencap_reference`；人物素材按 `reference_processing` 约束角色配色，不因图像相似度高而恢复未经确认的 `style` 权限。
- 用户文字方向、独立风格素材、忠实原画风和角色重设计分别使用其对应 `visual_artifact_type`；不得为了复用一份生图 Prompt，把它们统一转换成 editorial、海报或 KV。
- 确认后的视觉权威图成为唯一 `style_authority`；原人物素材继续承担其批准的身份角色，已被新图吸收的风格素材不再作为第二个视频画风权威重复传入。
- 用户明确要求时间锚定时，只生成模型模式真正缺少的时间图片，不扩展为逐 Shot 参考，也不将普通风格图、三视图、视觉权威图或分镜预览误作时间锚点。
- 三视图只用于身份锁定，不是三个时间关键帧，也不要求最终视频逐个展示。

## 九宫格分镜预览

九宫格只在用户于 Storyboard Approval 门禁主动选择“查看九宫格分镜预览”后，从当前 `storyboard_review.md`、Panel、Logical Shot 和 Master Timeline 派生。节点统一命名为 `《项目名》九宫格分镜预览`，并向用户说明：“九宫格用于确认镜头顺序、动作节点和构图方向；确认后其中可执行的信息会转译进视频提示词，但九宫格图片本身不会作为视频参考。成片的角色与画风由已确认视觉权威保持一致，动态与镜头过渡按照主时间线生成。”

Storyboard Preview 不是视频参考资产：内部标记为 `roles=none / render_reference=false / reference_slot=none`，不得规范化为 Render Ref Capsule，不得写入 `reference_slots`，也不得因其存在而切换视频模型或模式。存在并获批时，它作为 `storyboard_prompt_input` 进入 Prompt 编译；主 Agent 读取九宫格，将与语义分镜一致的构图、动作阶段、景别和镜头承接转译成文字，不把图片路径或图片槽位交给视频模型。

预览只派生自语义分镜，是第二级构图与动作规划输入，不反向成为人物、画风或叙事权威。用户要求修改预览内容时，先修改对应 Panel、Logical Shot 或 Master Timeline 并形成新的 `storyboard_revision`，再重新派生预览；不得只编辑预览图。每次生成或重新生成九宫格都创建新的 `preview_revision`；Storyboard Approval 必须绑定当前语义 revision 和当前 preview revision。不得主动引导用户裁切其中一格、选择某格作为视频参考，或转入首帧、尾帧、首尾帧路径。

## 排版参考

角色海报、抽卡界面、活动 KV、字体海报或 UI 图默认作为 `layout`，贡献文字层级、图文遮挡、网格、切片、信息面板和定版逻辑，不自动贡献角色身份或世界。

| 排版结构 | 可迁移动态 |
| --- | --- |
| 异形轮廓网格拼贴 | 网格逐格亮起、局部破框、大标题沿侧边进入。 |
| 斜切角色展示 / 活动 KV | 斜向色块切入、角色依次揭示、标签过冲后稳定。 |
| 巨型字体穿插 / 角色破框 | 巨字作为遮罩，角色从笔画缝隙揭示，切片错位后对齐。 |
| 中轴角色海报 / 切片详情 | 主体从中心建立，局部框和指示线依次出现并锁定。 |
| 游戏 UI / 抽卡 KV | 标题、卡片和前景 UI 分层视差进入，最终收束为活动定版。 |

用户没有提供精确文字时，只迁移字体形状、色块、留白和版式运动，不虚构价格、活动规则、产品事实或官方宣称。版式层服务角色和叙事，不让 HUD、信息卡或字幕墙覆盖主体。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
