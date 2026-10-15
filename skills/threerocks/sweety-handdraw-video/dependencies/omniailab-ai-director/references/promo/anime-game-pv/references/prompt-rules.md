---
name: omniailab-promo-anime-game-pv-prompt-rules
description: 「PV Prompt 编译规则」—— 二次元漫画 ／ 游戏 PV 方向细则：最终 Prompt 是一份 Markdown 文档，不是聊天摘要、分镜概述或单段自然语言。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

# PV Prompt 编译规则

## 编译单位

`final_video_prompt` 对应一条 Master Timeline。Panel 是语义分镜中的中间状态，用于聚合连续动作；Logical Shot 是 Prompt 内的时间章节；Render Attempt 才对应一次完整视频生成。不得把 Panel 或九宫格逐格机械复制为 Prompt 章节或独立生成任务；存在已批准九宫格时，必须把其中与语义分镜一致的构图、动作阶段、景别和镜头承接转译为文字化“分镜序列约束”。

最终 Prompt 是一份 Markdown 文档，不是聊天摘要、分镜概述或单段自然语言。编译完成后的标题、分节、时间码和换行属于交付合同，写入画布和交给 执行层 时必须原样保留。

## 语言合同

文档标题、章节标题、Logical Shot 叙事名称、规格说明和全部生成指令统一使用运行时注入的 `working_language`。不得因为本文件、Skill 示例或模型术语使用中文或英文，就改变用户当前语言。`default_editorial_active`、Editorial、内部视觉系统名称和其它内部路由字段不得出现在最终 Prompt；只能转译成用户已确认的实际画风、主题色、强调色和人物配色规则。模型 ID、模式名、素材标签、文件路径、参数名以及用户提供的精确标题、角色名、对白和画面文字保持原文；只有当前模型硬约束明确要求其它语言时才允许切换，并先向用户说明。

每个 Logical Shot 至少写明：时间范围、叙事职责、开始状态、主体动作与反应、摄影机路径、重要背景运动、声音事件、结束状态和下一段承接。只有揭示新的空间关系、动作进展、主体反应或环境反馈时才进入下一 Shot；不能只为换景别重复同一动作。

## 模式与参考绑定

- 没有可直接使用的有效图片素材时，必须先生成并确认与当前 `visual_artifact_type` 一致的视觉权威图，不能把纯文字直出作为默认捷径。
- 只有用户原文明示精确开场画面且 Render Contract 已选择对应模式时，才明确参考图对应 0 秒，并描述画面如何从该状态向后发展。
- 只有用户原文明示精确开场与收束画面且 Render Contract 已选择对应模式时，才明确两张图的时间角色，重点描述两者之间连续发生的动作、光影、材质、环境和声音变化。
- 多模态参考模式保持素材 slot 顺序，用一致标签逐一声明 `subject / scene / style / layout / action / audio` 的正向贡献。内部 `ignore` 判断不写进最终 Prompt。

素材已经清楚表达的外观和场景不重复长篇复述，把 Prompt 预算用于动作、摄影机、状态变化、转场和声音。不得主动引导时间锚定模式，也不得把普通参考视频、三视图或九宫格分镜预览误写成时间关键帧或普通视频参考。

## 画风权威合同

开始编译前必须已经完成 Style Authority Gate、适用的配色与参考处理确认、必要视觉权威图确认和 Render Contract 锁定，并得到一个可追溯的 `style_source → style_authority`、唯一 `style_authority`、`style_authority_kind`、`palette_authority`、`saturation_policy` 和 `reference_processing`。`generated_asset` 路径必须存在已批准的 `visual_authority_revision` 和具体 `visual_artifact_type`；`existing_asset` 路径必须使用 `visual_artifact_type=not_applicable`。内部默认视觉路径还必须锁定 `dominant_theme_color`、可空 `accent_color`、`accent_policy` 和 `character_palette_policy`；其它画风不得继承这些单色预算。用户文字、固定 IP、人物图、完整插画、场景图、排版图、动作视频和独立风格图在确认前都只是候选。

参考绑定严格消费用户确认后的最终 `roles`：

- 人物图、角色立绘和三视图默认只写为 `subject`，只描述脸、发型、体型、服装、配饰、武器、人数和关系。
- 只有用户明确选择同时参考角色与原画风时，被选中的人物素材才可写为 `[subject, style]`。
- `style_authority_kind=generated_asset` 时必须已有用户确认且类型正确的视觉权威图，并由该图承担唯一 `style_authority`；原人物素材继续只承担其确认后的身份角色。
- 内部默认视觉路径中的原人物素材只能写为 `subject`。角色颜色按 `character_palette_policy` 处理：保留原配色时只能局限在角色自身；降饱和纯色化时使用平面色块；全面单主题色化时只允许黑白、中性灰、主题色和用户明确保留的局部颜色。原图背景、构图、排版和载体伪影永远不得恢复。
- 用户选择独立风格素材时，人物素材继续锁身份，只有被选中的风格素材贡献媒介、材质、色彩和运动语言。
- 用户确认文字视觉方向时，把该方向作为全局风格合同；不得再从未选中的附件追加竞争风格。
- 用户允许重新设计角色时，只有确认后的新版角色视觉权威图进入 Prompt，旧素材只保留用户允许继承的核心概念。
- Storyboard Preview 永远不进入视频参考绑定；即使九宫格位于画布，也不得为其分配 `roles`、视频参考路径标签或参考槽位。它只在下方分镜编译阶段贡献文字化镜头约束。

全局基准只写一次最终画风，不并列多个“同时遵循”的视觉系统。内部默认视觉路径必须完整消费 `visual-inputs.md` 已锁定的 `palette_authority / accent_policy / character_palette_policy / saturation_policy`，并用自然视觉语言写入 Prompt，不重复维护另一份颜色比例或视觉语法。其它画风按已确认来源编译，不添加内部默认路径的单色规则。

## Render Contract 与执行预算

Prompt 不是脱离执行能力的创作文档。开始编译前必须已有唯一 Render Contract，并锁定批准状态、身份与画风权威、配色策略、参考素材角色、时长、画幅、声音、提示词预算和最终文件数量。不适用项要明确标记，不能停留在待定。Prompt 只描述模型需要看见、听见和执行的内容；执行设置和文件数量由合同承载，二者共同构成生成前确认对象。

`prompt_budget` 使用同一解析器确定：

1. 优先读取当前能力摘要明示的 Prompt 限制；
2. 若未提供，读取本 Skill 对应模型的能力说明；
3. 两者均未提供时，使用本 Skill 声明的保守 fallback；没有对应 fallback 时停止并补充能力证据，不猜测预算。

能力摘要与能力说明均未暴露字符上限时，停止编译并补充能力证据；不得猜测预算，也不得把某一模型的历史上限套用到其它模型，更不能等生成报错后才临时压缩。

执行设置必须逐项来自当前能力摘要。公共交付约束与执行设置分别保留；任何未被能力说明覆盖的设置都说明 Render Contract 尚未成立，不能靠执行层猜测、增删或搬移。

## 已批准 Storyboard Package 是编译输入

`final_video_prompt.md` 是 Storyboard Package 的编译结果，不是新的创作阶段。开始编译前必须同时满足：画布中完整 `storyboard_review.md` 已经可见；`storyboard_status=approved`；Storyboard Approval 绑定的 `storyboard_revision` 与当前 Panel、Logical Shot 和 Master Timeline 完全一致；存在 Storyboard Preview 时，Approval 绑定的 `preview_revision` 与画布当前九宫格完全一致。

Prompt 首先从获批 `storyboard_review.md` 中的 Brief、素材贡献、Panel、Logical Shot 和 Master Timeline 编译模型可执行语言。存在获批九宫格时，再分析其可观察构图、动作阶段、景别和镜头承接，将与语义分镜一致的内容写入“分镜序列约束”。九宫格不得新增、删除、合并或改写镜头职责、时间范围、动作因果、转场、声音事件、人物身份、画风或结尾状态；发生冲突时以语义分镜为第一权威，停止编译并回到 Storyboard Package 修订，不能在 Prompt 中自行取舍。

“分镜序列约束”只包含视频模型可执行的文字描述，不包含九宫格图片路径、素材标签或引用指令。它可以补充同一 Logical Shot 内的构图发展和动作阶段，但不能把九格强制转换为九个镜头或九段生成任务。

分镜确认问题必须发生在完整 Storyboard Package 落画布之后。对分镜摘要、制作计划或尚未写入的 Master Timeline 提前取得的回答，不构成有效 Storyboard Approval，也不能解锁 Prompt 编译。九宫格不是强制前置条件；用户选择生成后，它成为当前 Storyboard Package 和 Prompt 编译输入的一部分。

## 预算化编译与 Preflight

先在预算内组织信息密度，再写入 `final_video_prompt.md`。不得先生成超长完整版、提交失败后再临时删减。优先级从高到低为：身份与画风权威、时间线完整性、可观察动作与摄影机、状态承接、真实素材绑定、声音事件、项目特定失败预防、装饰性形容。

每次候选 Prompt 写入或覆盖同一个画布文档后，按最终字符串的实际字符数做精确校验。超预算时按以下顺序确定性收敛，并重新覆盖同一文档直至通过：

1. 合并重复的人物身份、世界和画风描述，只保留全局基准中的权威版本；
2. 删除各 Shot 重复继承的色彩、材质、连续性和通用质量词；
3. 合并重复否定词，只保留与当前项目真实风险相关的约束；
4. 删除没有新增空间关系、动作进展、主体反应或环境反馈的镜头表达；
5. 压缩句式而不删除时间码、动作因果、开始/结束状态、素材贡献和声音事件。

长度通过后，在完全相同的 Prompt 与 Render Contract 上执行一次统一 Preflight：

- 最终提示词字符数不超过 `prompt_budget`；
- 当前存在有效 Storyboard Approval，且其 `storyboard_revision` 与画布中的 `storyboard_review.md`、Panel、Logical Shot 和 Prompt 所使用的 Master Timeline 完全一致；存在九宫格时，`preview_revision` 与 Prompt 使用的预览一致；
- Render Contract 为 `status=locked` 且不存在 pending 字段；Style Authority Gate 已有有效答案，`style_authority_kind`、`requires_visual_authority_asset` 与实际资产一致，`style_source` 到唯一 `style_authority` 的转换可追溯，适用的配色与参考处理字段已锁定；
- 模型选择、生成路线、时长、画幅、分辨率和声音配置均在能力范围内；
- 执行设置的每个键和值都在能力说明范围内，公共字段没有错放；
- 参考素材类型、顺序、数量、单项/总时长、路径和最终 `roles` 与 `reference_slots` 一致；原始人物素材只有获得用户确认时才可拥有 `[subject, style]`；
- `style_authority_kind=generated_asset` 时已经生成并确认类型正确的视觉权威图，`visual_authority_status=approved` 且 revision 一致；`existing_asset` 时 `visual_artifact_type=not_applicable / visual_authority_status=not_applicable`；
- `default_editorial_active=true` 时已确认的主题色、强调色预算、角色配色策略和黑白面积层级均以自然视觉语言进入全局基准，Prompt 中不存在 Editorial 或内部系统名称；false 时 Prompt 中不存在该内部路径的专属规则；
- 九宫格存在时，Prompt 已包含“分镜序列约束”，但 `reference_slots` 中不存在九宫格，且没有将九格拆为九个 Logical Shot 或生成任务；
- 用户音频的实际传入方式与 Prompt 声明一致；
- `final_output_count=1`，Logical Shot 没有被编译成多个生成任务；
- 时间线覆盖完整时长且无空档或重叠，所有引用真实存在；
- 文档不存在尖括号、临时说明、伪路径或其它未解析占位符。

Preflight 未通过时返回 Render Contract 或 Prompt 编译阶段，不创建 Render Attempt。任何修正都先覆盖同一文档并重新 Preflight；修正后的合同和 Prompt 必须重新获得生成前确认，不能静默删参数、压缩、换模型或重试。

## 全局视觉与连续性

Prompt 开头只建立一次全局基准：人物身份、场景、唯一 `style_authority`、适用时的视觉产物形式、`palette_authority`、`saturation_policy`、媒介纹理、文字原文和最终视频目标。内部默认视觉路径按 `visual-inputs.md` 中已确认的合同写入实际主题色职责、强调色预算、角色配色策略、肤色、阴影、平面色块和环境信息量，不显示内部名称；不得重新引用原人物素材的背景、构图、排版或载体伪影。其它视觉路径只继承其已确认方向，不被单色化。后续 Logical Shot 继承该基准，不逐段重复相同形容词和负面约束。

优先使用可读的二维手绘运动、2.5D 图层视差、剪纸/原画切片、拖影帧、冲击线、墨迹或实体遮挡转场和受控形变。每次转场说明进入来源、遮挡对象和下一状态；复杂全身动作不能以随机快切掩盖失败。

用户提供精确标题、角色名、Logo 或 UI 文案时按原文处理。未提供精确文案时，只使用字体形状、图形层、色块和版式运动，不虚构具体价格、活动规则、产品事实或官方宣称。

## Prompt 骨架

以下是固定语义顺序，不是固定英文标题。每个尖括号标题都必须替换为 `working_language` 中自然、明确的对应表达，最终文档不得保留尖括号或双语占位：

```markdown
# <最终视频提示词>

## <制作规格>

- <时长>: <duration>
- <画幅>: <aspect ratio>
- <视频模式>: <selected video mode>
- <最终输出>: <一条完整统一的二次元漫画或游戏 PV>

## <全局基准>

<人物身份、世界、唯一画风权威、视觉产物形式、配色权威、饱和度策略、参考处理、媒介、精确文字和连续性锁>

## <参考素材绑定>

<每份真实图片、视频和音频参考的最终 roles、正向贡献与槽位绑定；没有外部参考时使用 working_language 表达“无”>

## <声音方案>

<实际传入的用户音频、视频模型原生声音、无 BGM 或静音，以及全局声音连续性>

## <分镜序列约束>

<仅在存在已批准九宫格时写入；把与语义分镜一致的构图、动作阶段、景别和镜头承接转译成文字，并明确九宫格图片不作为视频参考。没有九宫格时省略整个章节>

## <主时间线>

### <逻辑镜头 1> | <时间范围> | <叙事职责>

<开始状态、景别、摄影机路径、主体动作与反应、重要背景运动、图形或文字事件、声音、结束状态和下一镜头承接>

### <逻辑镜头 2> | <时间范围> | <叙事职责>

<新增叙事信息、继承状态、转场依据、动作发展、声音、结束状态和下一镜头承接>

## <最终状态>

<收束构图、用户提供时的精确标题处理、声音收束和稳定停留>

## <负面约束>

<只写项目特定的失败预防，不重复通用形容词列表>
```

写入 `final_video_prompt.md` 前检查：全部语义章节都已用 `working_language` 写出自然标题；时间线覆盖完整时长且无空档或重叠；每个 Logical Shot 都有开始状态、动作、摄影机、背景变化、声音、结束状态和承接；存在已批准九宫格时包含“分镜序列约束”，不存在时省略该章节；九宫格未进入参考素材绑定；所有真实引用均有绑定；精确文字保持原文；没有未解析占位符。任一项缺失时先补全，不得用一个长段落替代结构。

Prompt 长度服从 Render Contract，不设凑字数目标。复杂度来自可观察的时间变化与明确素材贡献，而不是重复形容词、重复锁定或无叙事增量的镜头数量。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
