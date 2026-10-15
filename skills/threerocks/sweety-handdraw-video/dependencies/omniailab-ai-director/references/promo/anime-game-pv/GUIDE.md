---
name: omniailab-promo-anime-game-pv
description: 二次元漫画 ／ 游戏 PV —— 宣传片线方向之一：15 秒以内的动漫、漫画或游戏 PV：角色宣传、觉醒、战斗、世界观与抽卡活动。
version: 2.3.0
author: OmniAiLab
developer: Mochiball
agent_created: true
开源仓库: https://github.com/tomatoparkdao/omniailab-ai-director
操作手册: https://zcn03zgas1zl.feishu.cn/wiki/P2fhwADXvil24UkNkDCcw1x2nbA
---

> **在本 skill 中的位置**：15 秒以内的动漫、漫画或游戏 PV：角色宣传、觉醒、战斗、世界观与抽卡活动。由**宣传片线总调度** `references/PROMO GUIDE.md` 在判定为该方向后接入。
> **生成口径**：提示词编译完成后，统一在 **OmniAiLab 画布** 中选择 **MiniMax H3** 生成视频；图像与资产类提示词仍按主线层级执行（`references/LIRA GUIDE.md`／`references/STYLE GUIDE.md`／`references/ASSET-SYSTEM GUIDE.md`／`references/PROMPT-DOCTRINE GUIDE.md`）。
> **与主干的关系**：本文件是宣传片线的方向细则，**不改变 P0→P6 主干与确认门禁**；涉及资产、表演、情绪、站位与光学时照常调用主线对应层。
> **暂停点**：素材与文字确认 → 方向与风格确认 → 提示词确认 → 生成 → 验收；每一步都等创作者确认后再继续，**不得一次跑完**。
> **触发词**：动漫PV／游戏PV／漫画PV／角色PV／剧情预告／战斗预告／抽卡宣传／活动PV

# 二次元漫画 ／ 游戏 PV

交付一条统一、可观看的二次元漫画或游戏 PV，而不是只交付分析、分镜或提示词。主 Agent 负责素材判断、视觉收敛、分镜、Prompt 编译、执行合同和最终验收；实际视频生成只通过一个 一次视频执行批次 执行。不创建 阶段执行计划，也不派 downstream workers 或下游 Agent 改写已确认的视频提示词。

## Production Model

| 实体 | 定义 |
| --- | --- |
| `Candidate Ref Capsule` | 媒体分析产生的候选素材贡献；只描述可能角色，不具有最终画风或执行权限。 |
| `Style Source` | Style Authority Gate 中由用户确认的原素材、文字方向、独立风格参考或 Agent 新方向，用于决定后续视觉制作。 |
| `Style Authority` | 真正进入视频 Prompt 的唯一画风权威，类型只允许 `existing_asset` 或 `generated_asset`。用户文字方向和内部视觉系统可以成为 `style_source`，但在需要生成视觉权威图的路径中不能直接冒充最终 `style_authority`。 |
| `Palette Authority` | 最终进入视觉权威图与视频 Prompt 的色彩合同。内部默认视觉路径由黑白结构、一个高纯度主题色和可选极少量强调色组成；其它画风按用户或权威风格来源锁定，不强制单色化。 |
| `Visual Artifact Type` | 新生成视觉权威图的实际画面形式。只有 `style_authority_kind=generated_asset` 时才使用具体类型；直接复用现有素材时必须为 `not_applicable`。 |
| `Render Ref Capsule` | 实际进入视频生成的素材合同，包含非空 `roles`、正向贡献边界和真实路径。 |
| `Panel` | 语义分镜中某个时间点或状态的制作单元，用于确认构图、动作进度和连续性。 |
| `Logical Shot` | Master Timeline 内的一段连续叙事，包含一个或多个 Panel；它是提示词章节，不是独立视频资产。 |
| `Master Timeline` | 包含全部 Logical Shot 的唯一完整生成计划。 |
| `Storyboard Preview` | 从当前语义分镜派生的可选九宫格。存在时作为构图、动作阶段和镜头承接的辅助 Prompt 输入；它不是人物或画风权威，也不进入视频参考槽位。 |
| `Storyboard Package` | 一次可供用户审阅的完整分镜版本，由 `storyboard_review.md`、全部 Panel、Logical Shot、Master Timeline，以及用户选择查看时生成的 Storyboard Preview 共同组成。 |
| `Storyboard Approval` | 用户通过真实 确认卡 对当前 Storyboard Package 给出的批准回执；必须绑定 `storyboard_revision`，存在九宫格时同时绑定 `preview_revision`。该批准同时授权系统编译 Prompt，并在 Preflight 通过后直接生成。 |
| `Render Contract` | 一次完整生成的可执行合同；draft 先锁定能力与计划，locked 再锁定身份、唯一画风与色彩权威、实际参考槽位、当前模型参数、Prompt 预算和最终文件数量。 |
| `Render Attempt` | 一份已确认的 Render Contract、一份通过 Preflight 的完整 Prompt、一次 一次视频执行批次 和一条完整候选视频。 |
| `Final Video` | 通过检查并被选中的 Render Attempt；它替代先前候选，而不是与候选片段拼接。 |

生产拓扑固定为：静默 Intake → 制作路线与身份确认 → Style Authority Gate → 色彩方向与参考处理 → 视觉权威决策 → Render Contract draft → 必要视觉权威图与唯一 `style_authority` → locked Render Contract → Panel → Logical Shot → Master Timeline → 可选九宫格 → 完整 Storyboard Package 确认 → `final_video_prompt` 编译与 Preflight → 生成一个完整 Render Attempt。`production_route` 记录用户选择且后续不改写；是否需要先生成视觉权威图由 `requires_visual_authority_asset` 独立派生。每个 Render Attempt 始终生成一条完整候选视频；多个独立最终成片、时长超过 15 秒或跨视频连续性才升级到 workflow。

## Interaction Contract

先从用户原文、真实附件和画布资产建立 `intake_state`，再询问缺失决策。至少记录 `production_route / identity_source / has_valid_image_asset / style_candidates / style_source / style_authority / style_authority_kind / visual_policy / default_editorial_active / dominant_theme_color / accent_color / accent_policy / character_palette_policy / palette_authority / saturation_policy / reference_processing / requires_visual_authority_asset / visual_artifact_type / visual_authority_revision / visual_authority_status / narrative_focus / duration / aspect_ratio / audio_plan / audio_drive / storyboard_revision / preview_revision / storyboard_status / prompt_status`。用户已经明确或素材可以直接证明的身份、规格和声音信息必须继承，不得重复询问；画风方向属于强制确认项，不能仅凭文字或附件静默锁定。

`visual_authority_status` 只允许 `not_applicable | pending | approved`；`storyboard_status` 与 `prompt_status` 只允许 `empty | pending | approved`。新生成视觉权威图或 Storyboard Package 首次创建或内容变化时为 `pending`。从获批 Storyboard Package 编译 Prompt 后设置 `prompt_status=pending`，Preflight 通过后设置为 `approved` 并直接生成指令。后续产物不能反向替代前一状态的批准。

执行顺序固定为：静默 Intake → 有素材时完成媒体分析与候选 Ref Capsule → Style Authority Gate 确认 `style_source` → 解析色彩合同 → 内部默认视觉路径依次确认主题色、可选强调色和适用的参考图处理 → 根据视觉决策矩阵派生 `style_authority_kind / requires_visual_authority_asset / visual_artifact_type` → 确认其余规格 → 按路径生成并确认必要视觉权威图 → 锁定唯一 `style_authority` 和 Render Contract → 完成并确认 Storyboard Package → 编译并 Preflight Prompt → 直接生成。任何阶段都不得提前把候选来源当作最终画风权威，也不得越过前一产物的批准状态。

下游失效关系固定如下：

1. `style_source` 或 `visual_policy` 变化：使配色、参考处理、视觉权威、Render Contract 和 Storyboard Approval 全部失效，并将 `prompt_status` 设为 `pending`。
2. 配色、强调色职责或 `reference_processing` 变化：如果使用生成型权威图，使当前 `visual_authority_revision` 失效；无论权威类型如何，都使 Render Contract 和 Storyboard Approval 失效，并将 `prompt_status` 设为 `pending`。
3. 视觉权威资产、类型或实际绑定变化：使 Render Contract 和 Storyboard Approval 失效，并将 `prompt_status` 设为 `pending`。
4. Panel、Logical Shot 或 Master Timeline 变化：形成新的 `storyboard_revision`；九宫格预览变化：形成新的 `preview_revision`。任一变化都使 Storyboard Approval 失效，并将 `prompt_status` 设为 `pending`。
5. 只修改不改变分镜语义的模型、合法参数、参考槽位或 Prompt 措辞：只更新 Render Contract 或将 `prompt_status` 设为 `pending`，不回退视觉与分镜。

任何需要用户选择、确认或批准生成的步骤都必须调用真实 确认卡。普通文本只能解释结论、说明影响或请求上传已选素材；不得在普通回复中列编号选项、用“请回复 1/2/3”“如无修改我就继续”代替 Question Window，也不得在未获得对应确认时继续生成。问题标题、选项、说明和推荐表达必须统一遵循运行时注入的 `working_language`；推荐项只在有明确判断依据时标记，并使用该语言的自然表达。`default_editorial_active`、Editorial、内部视觉系统名称、内部路径、Skill 名称和转交过程不得向用户显示。分镜确认是执行前最后一道确认门禁；用户确认后，系统编译 Prompt、完成 Preflight 并直接生成指令。用户后续修改分镜、画风或参考处理时返回对应已有确认；其它明确修改更新后继续执行。必需的 确认卡 取消、报错或无有效结果时停在当前门禁。

### 静默 Intake

在首次提问前，自动判断：交付意图、人物/场景/风格/排版/动作或参考视频、音频、固定 IP 与指定角色、时长、画幅、平台、用户描述中的视觉方向，以及同类参考之间的冲突。只有真实存在、可读取且与任务有关的图片附件或画布图片资产才能令 `has_valid_image_asset=true`；文字描述、视频、音频、失败占位或尚未生成的计划图片均不能替代。分析结果只能形成 `subject | scene | style | layout | action | audio` 候选贡献：人物图、立绘和三视图默认是 `subject` 候选，独立风格图默认是 `style` 候选，其它素材按可观察内容建立候选角色；任何素材在用户确认前都不得成为最终 `style_authority`。

固定 IP 只直接影响身份判断，不自动决定最终画风：

1. 已有固定 IP 但没有指定角色时，只用允许自由输入的单选 确认卡 询问具体角色或是否制作群像。
2. 已指定角色、群像或原创人物时，先锁定 `identity_source`，但仍必须通过下方 Style Authority Gate 确认是否继承原作、附件或其它视觉方向。
3. 用户明确允许大幅改造角色设定时，记录为 `reinterpret` 候选；最终仍通过 Style Authority Gate 确认实际视觉来源。

### 制作路线与画风来源决策

制作方式不明确时，询问“这次希望从哪种方式开始？”：

| 单选项 | 用户说明 | 内部路径 |
| --- | --- | --- |
| 使用现有素材制作 | 根据已有角色和参考素材直接制作 PV | `direct_pv` |
| 先确定主视觉 | 先完成角色与画面设计，确认后制作 PV | `visual_first` |
| 参考视频复刻 | 上传参考视频，复刻其镜头、动作与节奏 | 停止本 Skill，转交 `video-deconstruct` |

问题窗口只显示选项和用户说明，不显示内部路径、Skill 名称或转交过程。用户已明确逐镜复刻参考视频时直接转交，不再显示本问题；参考视频仅用于节奏、运镜、转场或媒介参考时继续留在本 Skill。所选路径缺少必要素材时，说明需要的素材并等待上传；素材到达后自动分析，不重复询问制作方式。`production_route` 一经确认保持不变，后续即使需要先生成视觉权威图，也只说明这是当前路线的必要准备，不改写用户选择。

素材分析完成后，每个任务都必须执行一次单选 Style Authority Gate。即使用户已经描述风格，也要把该描述作为推荐候选供用户确认；不得因为固定 IP、人物图、完整插画、风格图或明确风格词而跳过。问题与选项根据实际素材动态生成：

| 可用条件 | 单选项示例 | 内部结果 |
| --- | --- | --- |
| 存在人物或角色素材 | 同时参考角色与原画风 | 用户选中的素材成为 `style_source`，`visual_policy=faithful`。 |
| 存在人物或角色素材 | 只保留角色身份，重新建立视觉表现 | 使用用户后续方向或内部系统作为 `style_source`，原素材只锁身份，`visual_policy=identity_locked_restyle`，先生成并确认主视觉。 |
| 用户已描述视觉方向 | 按当前视觉方向继续 | 用户描述成为已确认的 `style_source`；如有角色素材，只锁身份。 |
| 存在独立风格素材 | 以风格参考控制视觉 | 用户选中的独立素材成为 `style_source`。 |
| 没有可用风格来源 | 由 Agent 提出新的视觉方向 | 内部视觉系统成为 `style_source`；有身份素材时保持角色身份。 |
| 任意情况 | 使用或补充其他风格参考 | 等待用户指定或上传素材，确认前不继续。 |
| 任意情况 | 基于现有设定重新设计 | 仅在用户明确允许调整角色造型时显示，`visual_policy=reinterpret`。 |

每次只显示当前真实可执行的 2–4 个选项，不为凑数量展示无素材支撑的路径。存在多份候选风格时，选项必须说明具体来源或允许自由输入；用户确认前只保留 `style_candidates`，回答只确立一个 `style_source`。只有用户选择由 Agent 提出新方向，或选择重新建立视觉表现但没有给出其它文字/图片风格来源时，内部设置 `default_editorial_active=true`；该内部名称和固定语法不作为“唯一内置画风”外显。忠实原画风、用户文字方向和独立风格参考均设置为 false。

Style Authority Gate 的答案决定后续路径：选择原作或原素材视觉时为 `faithful`；选择文字方向、独立风格素材或 Agent 新方向且已有身份素材时为 `identity_locked_restyle`；没有身份素材时为 `original_direction`；允许改变角色设定时为 `reinterpret`。随后读取 `references/visual-inputs.md` 的唯一视觉决策矩阵，派生 `style_authority_kind / requires_visual_authority_asset / visual_artifact_type`。直接复用现有生产可用素材时使用 `style_authority_kind=existing_asset / requires_visual_authority_asset=false / visual_artifact_type=not_applicable`；需要清理载体、风格转换、身份融合、角色重设计或没有可直接使用的图片时，使用 `generated_asset / true / 对应具体类型`。

角色揭示、觉醒、战斗、世界观或抽卡目标优先从用户描述推断，只有宣传重点确实不明确时才用单选 确认卡 询问“角色魅力与情绪 / 技能、动作与战斗 / 剧情、关系与世界观”。同一流程最多包含三个相互独立且尚未明确的问题，每题必须单选并禁止 `multiple: true`；内部默认视觉路径的主题色、强调色和参考图处理依赖已确认画风，必须在 Style Authority Gate 返回后顺序询问。

### 色彩方向、参考处理与视频规格

Style Authority Gate 返回后，先判断是否启用内部默认视觉路径。以下问题只展示实际颜色和处理结果，不显示 Editorial 或任何内部风格名称：

- **主题色问题**。先单独确认 `dominant_theme_color`，提供 3 个高纯度、高饱和且叙事情绪明显不同的主题色方向，并允许自由输入。主题色控制环境主场、MG 图形、核心道具/母题、文字/UI 强调和转场载体；人物原图颜色不自动决定该答案。
- **强调色问题**。取得主题色后再单独询问 `accent_color`，必须包含“无强调色”选项，并可提供 2–3 个只承担单一语义职责的候选，例如危险、超自然裂变、目标锁定、身份差异或冲击火花。选择强调色时同时锁定唯一 `accent_role`；允许自由输入，用户只给颜色但用途不明确时再补问用途。
- **内部色彩预算**。建立 `palette_authority={ black, white, optional_neutral_gray, dominant_theme_color, accent_color|null }`。主题色保持同一色相家族，可改变明度但不能漂移为邻近彩虹色；强调色单帧不超过 5%、全片平均不超过 3%，不能成为背景、整套服装、大型道具、城市灯光系统或持续轮廓光，并应长时间消失后再在唯一语义节点出现。
- **其它画风路径**。忠实原画风、用户文字方向或独立风格参考按其已确认色盘建立 `palette_authority`；只有来源冲突、用户要求改色或色盘无法判断时才补问，不套用黑白单主题色预算。

内部默认视觉路径且存在人物图片时，在配色确认后再用单选 确认卡 询问参考图处理方式：

- **保留角色原配色**：角色身份和原配色保持稳定，主题色只控制环境与 MG；必要时生成清理载体后的动画截图参考，不把原图背景、排版或构图传给视频。
- **降低饱和度纯色化保留**：保持角色原有配色逻辑，但降低饱和度并改为平面纯色块，再生成动画截图参考。
- **全面黑白主题色化**：将角色转入黑、白、可选中性灰和已确认主题色；仅保留用户明确指定的局部颜色，并把它限制在指定部位。

记录 `reference_processing=preserve_original_palette | flattened_palette | strict_single_hue` 和对应 `character_palette_policy`。用户已明确处理方式时直接继承；不得静默重着色。完成配色和参考处理后，只询问尚未明确的视频规格：

- **时长**：`15 秒（推荐） / 10 秒 / 6 秒 / 其他`。用户已给时长时直接继承；未给时默认推荐 15 秒。
- **画幅**：根据平台或用户原文推断；无法推断时询问 `9:16 竖屏 / 16:9 横屏 / 1:1 方形`，并按发布场景动态排列推荐项。
- **声音**：已上传音频但用户未说明用途时，询问“这段音频主要如何参与制作？”，提供 `参考音乐节奏 / 参考台词或人声 / 只分析节奏与情绪 / 不使用这段音频`。前两项把真实音频交给选定的视频模型，第三项只使用分析结果并生成模型原生声音，第四项回到无用户音频路径；用户已经明确卡点、口型或情绪用途时直接继承。没有音频且用户未说明时，询问 `视频模型原生声音（推荐） / 静音视频 / 预留后期配乐空间`；预留后期配乐空间表示不生成 BGM，但允许环境声和动作声维持节奏。

主题色问题、强调色问题和参考图处理问题必须按依赖顺序调用，不能与彼此或视频规格合并；没有人物图片时跳过参考处理问题。同一次规格 确认卡 仍最多包含三个独立问题；配色与参考处理锁定后再询问时长、画幅和声音，不把这些决策拼成组合选项。

时长超过 15 秒时单独使用条件窗口，只提供“压缩到 15 秒以内”和“切换到长视频/完整分镜流程”。不得在本 Skill 内拆成多个视频后拼接。用户要求屏幕文字但未给准确原文时，再单独请求准确文字，不询问已经明确的“是否需要文字”。

### 视觉确认与生成授权

1. `style_authority_kind=generated_asset` 时，视觉权威图生成并检查后设置 `visual_authority_status=pending`，用真实 确认卡 提供：使用当前视觉参考继续、调整画风表现、调整配色、调整参考图处理、调整角色一致性。确认后记录 `visual_authority_revision` 并设置为 approved；existing_asset 路径设置 `visual_authority_status=not_applicable / visual_authority_revision=not_applicable`。
2. 完成全部 Panel、Logical Shot、Master Timeline 和 `storyboard_review.md` 后，设置 `storyboard_status=pending` 并显示分镜确认卡：确认分镜并生成；查看九宫格分镜预览；调整叙事与节奏；调整人物与动作；调整视觉与声音。用户选择查看预览时，从当前语义分镜生成九宫格并返回同一道门禁；最终确认绑定语义分镜、当前 locked Render Contract 和存在时的 `preview_revision`。
3. 当前 `storyboard_status=approved` 且批准回执绑定当前 Storyboard Package 与 Render Contract 时，编译完整 Markdown Prompt。编译只把已确认内容转成可执行 Prompt，不新增创意决定。Prompt 和 Render Contract 通过 Preflight 后，设置 `prompt_status=approved` 并直接生成指令。

每次只修改用户所选范围，并按统一失效关系重新展示受影响内容。用户选择调整画风、色彩或参考绑定时，回到对应决策阶段，按需重新生成视觉权威图，再更新 Render Contract 和 Storyboard Package。Panel、Logical Shot、Master Timeline、分镜文字或已生成九宫格发生变化时，形成新的 Storyboard Package revision，并重新显示分镜确认卡；其它执行信息按用户的新要求更新，重新 Preflight 后继续生成指令。

## 1. 判断路由与交付范围

“韩漫 PV、漫画 PV、二次元剧情 PV、角色/群像 PV”属于本 Skill 的明确正向信号。不得因为用户同时使用“影视 PV、预告、teaser、trailer”等泛称，就覆盖二维漫画/动漫主体并转入电影片头 Skill。

建立 Brief：目标属于角色/群像剧情揭示、角色觉醒、战斗预告、世界观展示或抽卡/活动宣传；记录时长、画幅、精确标题文字、辅助资产及 `production_route / identity_source / has_valid_image_asset / style_candidates / style_source / style_authority / style_authority_kind / visual_policy / default_editorial_active / dominant_theme_color / accent_color / accent_policy / character_palette_policy / palette_authority / saturation_policy / reference_processing / requires_visual_authority_asset / visual_artifact_type / visual_authority_revision / visual_authority_status / narrative_focus / audio_plan / audio_drive`。所有字段按 Interaction Contract 推断或确认，不得重新拼成一张综合多选表。

以下意图离开本 Skill：

| 用户意图 | 去向 |
| --- | --- |
| 片名、卡司、Opening Title、Opening Credits 或标题特效是主体 | `cinematic-title-sequence` |
| 静止系 MAD、歌词文字或动态字体是主体 | `h3-visual-design` 或对应 Skill |
| 音乐、说唱、时尚表演或 MV 是主叙事 | `cool-music-video` |
| 通用动态设计 MG | `h3-visual-design` 或对应 Skill |
| 品牌科技蒙太奇或系统视觉是主体 | `brand-ad` |
| 逐镜拆解并复刻参考视频 | `video-deconstruct` |
| 真人广告、3D 动漫、长剧情、多个独立成片或跨视频连续性 | 对应 workflow |

参考视频若只用于原创二次元 PV 的节奏、运镜、转场或媒介参考，继续留在本 Skill，不继承其角色、世界、品牌或文字。

## 2. 建立素材、身份、画风来源与色彩策略

1. 用 `媒体分析步骤` 分析相关图片、视频和音频，并先为每份素材建立候选 Ref Capsule：`{ id, candidate_roles, contributes, take }`。`candidate_roles` 是 `subject | scene | style | layout | action | audio` 的集合；分析结果不能替代 Style Authority Gate。
2. 角色立绘、人物图和三视图默认只作为高权重身份参考：锁定脸、发型、体型、服装、配饰、武器、标记、人数和关系；不要求最终视频展示所有视角，也不因其自身线条、上色或构图自动获得 `style` 权限。
3. 场景候选只锁定空间与世界；风格候选只贡献媒介、材质、色彩和运动语言；排版候选只贡献层级、网格、遮挡、切片和定版逻辑；动作候选只贡献动作与摄影机关系。只有用户在 Style Authority Gate 中明确选择后，素材才从候选贡献转为最终 `style` 角色。
4. Style Authority Gate 只确立 `style_source`、`visual_policy` 和 `default_editorial_active`，不提前决定最终素材角色或主视觉形式。配色和参考处理完成后，统一通过 `references/visual-inputs.md` 的决策矩阵派生 `style_authority_kind / requires_visual_authority_asset / visual_artifact_type`；需要生成视觉权威图时，不能把未转换的人物素材与新产物一起当作多个视频画风权威。

`style_source` 确认后按路径建立色彩权威：

1. `default_editorial_active=true` 时严格按 `dominant_theme_color → accent_color|null → accent_policy → palette_authority` 完成门禁。强调色不是第二主色；默认推荐无强调色，只有叙事需要单一语义差异时才启用。用户界面只展示实际颜色方向和用途，不显示内部系统名称。
2. `faithful`、用户文字方向或独立风格参考按已确认来源锁定色盘；用户原文已经明确改色时才覆盖来源，不强制黑白单主题色。
3. 人物原配色与全片 editorial 色盘分开管理。`character_palette_policy` 由参考处理答案决定；角色多余颜色只能局限在角色身份区域，不能扩散到背景、MG、UI 或转场。

内部默认视觉路径的具体画面语法、颜色预算、人物配色处理和视觉产物验收只以 `references/visual-inputs.md` 为真相源；本文件只负责决定何时进入该路径以及哪些用户确认必须完成，不重复维护视觉细节。

## 3. 锁定 Render Contract 与视觉参考

先查看当前能力摘要，优先选择可用的默认视频模型路径。确定模型路线后，建立人类可读的 Render Contract 草稿，覆盖批准状态、身份与画风权威、配色、参考素材角色、时长、画幅、声音、提示词预算和最终文件数量，不把私有实现字段复制进文档。

- draft 中锁定 `style_source`、`visual_policy`、`default_editorial_active`、`reference_processing`、`style_authority_kind`、`requires_visual_authority_asset`、`visual_artifact_type` 和模型能力。`generated_asset` 路径必须标记 `style_authority=pending / visual_authority_status=pending`，用户确认对应 revision 后才能写入实际资产并设置 approved；`existing_asset` 路径直接写入已确认素材，设置 `visual_authority_status=not_applicable / visual_artifact_type=not_applicable`。locked Render Contract 不允许任何 pending 字段。
- 内部默认视觉路径必须锁定 `dominant_theme_color`、可空 `accent_color`、`accent_policy`、`character_palette_policy`、`palette_authority` 和 `saturation_policy`；选择无强调色时使用显式 `accent_color=none / accent_policy=none`，不是 pending。其它画风将不适用字段标记为 `not_applicable`，并锁定其来源色盘。所有实际适用字段必须在视觉权威图和最终 Prompt 中保持不变，但内部字段名不得进入用户可见问题、摘要或 Prompt 标题。
- 执行设置必须在当前能力摘要声明的范围内；公共交付约束与执行设置分别保留。
- draft 的 `reference_slots` 只记录计划使用的素材类型、顺序、数量、时长限制、已有身份素材路径和待生成锚点；主视觉/锚点确认后再写入 Render Ref Capsule 的最终 `roles` 与实际路径。进入 Prompt 编译前，所有槽位必须完整锁定；候选角色、未确认风格和没有合法槽位的素材不得伪装成已参与生成。
- `prompt_budget` 按统一优先级解析：当前能力摘要 → 本 Skill 对应模型的能力说明 → `references/prompt-rules.md` 的保守 fallback。前两者均未暴露提示词上限时，必须在编译前停下并补充能力证据；不得猜测预算，也不得等生成失败后才临时压缩。
- `final_output_count` 在本 Skill 中固定为 `1`；内部允许多个 Panel 和 Logical Shot，但它们不增加最终文件数量。
- Render Contract 只锁定生成执行条件，不代替 Storyboard Approval。即使合同已经 locked，只要当前 Storyboard Package 尚未落盘并获批，就不得编译 `final_video_prompt`。

读取 `references/visual-inputs.md`，按唯一决策矩阵确定是直接复用现有权威素材，还是生成某种视觉权威图，再在 Render Contract draft 允许的模式与槽位内选择实际视频参考；不得为了使用某个模式静默丢弃素材。`generated_asset` 路径必须完成视觉权威确认后，才能补齐唯一 `style_authority`、Render Ref Capsule、实际路径和参考槽位；`existing_asset` 路径不得伪造生成型 `visual_artifact_type`。只有 locked Render Contract 可以进入 Prompt 编译；如需更换画风来源、视觉形式、配色、参考处理、模型、模式、声音、素材绑定或参数，按统一失效关系返回对应阶段。

没有可直接进入视频参考的有效图片素材时，必须生成与当前风格路径一致的视觉权威图，不走无图直出。`requires_visual_authority_asset=false` 时只复用已经确认且生产可用的素材，并保持唯一 `style_authority`。
- 只有用户原文明示需要精确开场、精确收束或指定时间画面时，才被动校验并使用模型支持的时间锚定模式；不得主动介绍、推荐或询问首帧、尾帧、首尾帧或关键帧锁定，也不得引导用户从分镜预览中裁切 Panel 作为视频参考。

需要生成视觉权威图时，先查询 image 能力，再按 `references/visual-inputs.md` 的公共 Visual Authority Contract 与当前 `visual_artifact_type` 编译生图 Prompt，并用 `图像生成步骤` 落实权威身份贡献、`style_source`、适用的配色字段、`reference_processing` 和画面形式。生图 Prompt 必须区分必须保留的身份、允许适配的表现和禁止继承的载体信息；不得使用“优化原图”“保持原构图”或不区分路径的“生成宣传海报/KV”等泛化表达。生成或覆盖资产时创建新的 `visual_authority_revision` 并设置 `visual_authority_status=pending`。

生成后先用 `媒体分析步骤` 按当前 `visual_artifact_type` 检查。所有路径都要保持身份边界并移除不应继承的载体污染；指定方向和风格融合路径要命中所选风格；角色重设计要符合允许变化范围；内部默认视觉路径必须通过单主题色预算、强调色预算、纯白/近白肤色、硬边黑影、平面色块、低信息背景和动画截图感检查，同时不能只是原图换色，也不能生成精致宣传海报、三视图或最终分镜。未通过时不得提升为 `style_authority`，应在同一视觉阶段修正对应合同后重新生成。

通过检查后落到画布，并用 确认卡 提供“使用当前视觉参考继续 / 调整画风表现 / 调整配色 / 调整参考图处理 / 调整角色一致性”。用户确认当前 revision 后设置 `visual_authority_status=approved`；选择调整时回到对应生产层，不把所有问题统一回退成重做海报。不得为每个 Logical Shot 分别生成视觉参考。

主视觉和锚点确认后，把所有实际进入视频生成的素材规范化为 Render Ref Capsule：`{ id, roles, contributes, take }`。`roles` 是 `subject | scene | style | layout | action | audio` 的非空子集。`faithful` 且不生成新主视觉时，被确认的原人物素材可获得 `[subject, style]`；生成新主视觉时，原人物素材只保留 `[subject]`，确认后的主视觉获得 `[style]`；独立风格素材若已被主视觉吸收，不再作为第二个视频画风权威重复传入。其它素材分别承担已确认的场景、排版、动作或声音角色，最终只保留一个 `style_authority`。完成这些转换并补齐实际路径后，才能把 Render Contract 设置为 locked。

## 4. 制作 Panel、Logical Shot 与 Master Timeline

默认先制作语义分镜，不生成九宫格。每个 Panel 在 `storyboard_review.md` 中记录时间点或时间段、景别、主体与动作状态、前中后景、摄影机状态、文字/图形事件、转场依据、声音提示和从上一 Panel 继承的连续状态。Panel 是中间制作单元，不是独立视频资产，也不直接进入视频参考。

将完成的 Panel 聚合为 Logical Shot。每个 Logical Shot 记录：时间范围、叙事职责、包含的 Panel、开始状态、主要动作、结束状态、摄影机轴线、光线、环境、转场接口、文字状态和声音区间。多个相邻 Panel 可以共同描述一个 Logical Shot 的连续发展。

把全部 Logical Shot 排入同一条 Master Timeline。叙事可采用“钩子 → 主体/空间建立 → 动作或情绪发展 → 高潮 → 稳定定版”的弧线，但不套用预设类型模板；结构必须来自用户目标和素材。

按以下固定顺序完成 Storyboard Package：

1. 用 `画布写入` 创建或覆盖同一个 `storyboard_review.md`，写入完整 Brief、素材贡献、`style_source → style_authority`、`visual_artifact_type`、配色权威、饱和度策略、参考图处理、声音方案、全部 Panel、Logical Shot 分组和无空档的 Master Timeline。
2. 确认完整 `storyboard_review.md` 已在画布可见；不得用 `final_video_prompt.md` 充当分镜文档。
3. 以当前分镜文本节点及其语义内容组成新的 `storyboard_revision`，设置 `storyboard_status=pending`。尚未生成九宫格时记录 `preview_revision=none`。
4. 调用分镜 确认卡，提供“确认分镜并生成 / 查看九宫格分镜预览 / 调整叙事与节奏 / 调整人物与动作 / 调整视觉与声音”。Storyboard Approval 同时绑定当前 `storyboard_revision`、locked Render Contract 和存在时的 `preview_revision`；用户要求调整时覆盖分镜产物、生成新 revision 并再次等待确认。

用户选择“查看九宫格分镜预览”时，才从当前语义分镜派生一张九宫格，节点命名为 `《项目名》九宫格分镜预览`，并明确说明：“九宫格用于确认镜头顺序、动作节点和构图方向；确认后其中可执行的构图与动作信息会转译进视频提示词，但九宫格图片本身不会作为视频参考。成片的角色与画风由已确认视觉权威保持一致，动态与镜头过渡按照主时间线生成。”预览成功落到画布后记录新的 `preview_revision`，保持 `storyboard_status=pending` 并立即返回同一道分镜确认 确认卡。用户要求修改预览内容时，先修改对应 Panel、Logical Shot 或 Master Timeline，形成新 `storyboard_revision`，再从新语义分镜重新派生预览；不得只编辑预览图。重新生成九宫格会产生新的 `preview_revision`，使旧 Storyboard Approval 失效并将 `prompt_status` 设为 `pending`。

分镜 确认卡 是本阶段的终点。未得到绑定当前 revision 的有效确认前，不得进入 Prompt 编译阶段，不得创建或覆盖 `final_video_prompt.md`，也不得把“已生成分镜”“接下来编译 Prompt”等普通回复视为默认批准。

## 5. 从已批准 Storyboard Package 编译并 Preflight

进入本阶段前先验证：`storyboard_status=approved`、Storyboard Approval 绑定的 `storyboard_revision` 与画布当前语义分镜一致、存在九宫格时绑定的 `preview_revision` 与画布预览一致、Render Contract 为 locked。任一必要条件不成立都返回第 4 阶段，不创建 Prompt。验证通过后读取 `references/prompt-rules.md` 和 `references/audio-direction.md`，从获批 Storyboard Package 编译唯一 `final_video_prompt`，并从一开始遵守 Render Contract 的 `prompt_budget`；不得先写无限长度版本再等待生成失败后压缩。Prompt 按顺序包含：

1. 时长、画幅、模式和唯一最终视频目标；
2. 素材引用及 Ref Capsule 的正向贡献边界；
3. 人物、场景、唯一画风权威、视觉产物形式、配色权威、饱和度策略、参考处理和文字连续性锁；
4. 存在九宫格时，将其与语义分镜一致的构图、动作阶段、景别和镜头承接转译为“分镜序列约束”；不写入图片参考路径，不创建图片槽位；
5. Master Timeline 内全部 Logical Shot 的开始状态、动作、结束状态和下一段承接；
6. 用户原文、图形处理、原生声音或已确认音频的真实引用关系；
7. 最终定版和稳定停留。

Panel 不与 Prompt 章节一一对应，也不逐格机械复制进 Prompt；Logical Shot 才是 Prompt 内的时间章节。九宫格只补充与获批语义分镜一致的构图和动作阶段，不得新增、删除或改写镜头职责；发生冲突时停止编译并返回分镜阶段统一。动态必须写成可观察的摄影机路径、主体动作、图层变化、实体转场和声音事件，不能用“电影感、震撼、流畅”代替时间变化。

`final_video_prompt` 的文档标题、章节标题、Logical Shot 叙事名称和正文统一使用运行时注入的 `working_language`；模型 ID、模式名、素材标签、文件路径和用户精确文字保持原文。Prompt 必须保留 `references/prompt-rules.md` 规定的语义章节顺序和 Logical Shot 分节，不得压缩成一段普通文本或聊天摘要。

按以下顺序完成可执行编译：

1. 编译候选 Prompt，并用 `画布写入` 创建或覆盖同一个 `final_video_prompt.md` 文档节点；正文必须与准备生成指令的 Prompt 字符级一致。
2. 按最终 Prompt 的实际字符数与 Render Contract 的 `prompt_budget` 做精确校验。
3. 超预算时，按 `references/prompt-rules.md` 的确定性收敛顺序删除重复身份、重复画风、重复否定词和没有新增信息的镜头表达，覆盖同一文档并重新计数；不得牺牲时间线覆盖、动作因果、素材绑定或声音事件。
4. 在同一份 Prompt 和 Render Contract 上执行统一 Preflight：Style Authority Gate、唯一画风与色彩权威、Prompt 长度、当前模型参数白名单、模型与模式、素材最终角色、槽位/数量/时长、真实路径、音频方案、duration、画幅、分辨率、最终文件数量和未解析占位符。
5. 任一项失败都返回对应合同、分镜或 Prompt 编译阶段修正，不创建 Render Attempt。全部通过后设置 `prompt_status=approved` 并直接生成指令。

Prompt 编译后、生成指令前，如果用户主动要求修改，先判断是否改变获批分镜语义：镜头、时间范围、叙事职责、动作、转场、构图、声音事件或结尾状态变化回到第 4 阶段，生成新 `storyboard_revision` 并重新通过分镜门禁；不改变分镜语义的措辞压缩、合法参数、模型或参考槽位修正直接更新 Render Contract 或同一 `final_video_prompt.md`，重新 Preflight 后继续生成指令。

## 6. 创建、检查和修复 Render Attempt

只有 `storyboard_status=approved`、`prompt_status=approved`，且 Storyboard Approval 仍绑定当前产物时，才将确认后的 Render Contract 和 `final_video_prompt.md` 作为不可变执行简报，进入一次视频生成。执行层先确认简报仍满足合同，再提交字符级相同的 Prompt、素材顺序和设置；不得摘要、翻译、改写、压缩、增加设置、切换模型、改变素材绑定、压平 Markdown 结构或把 Logical Shot 拆成独立视频任务。

失败按生产阶段回流：

1. 提交前发现参数、长度、模式、素材或路径不合法：返回 Render Contract / Prompt 编译阶段，不创建 Render Attempt，也不发起生成。
2. 修复需要改变画风权威、视觉产物形式、配色、参考处理或饱和度：回到对应 Style Authority Gate、配色或参考处理确认，按需重新生成视觉权威图，再更新 Master Timeline、Render Contract、Prompt、Preflight 和受影响的生成门禁。
3. 修复改变镜头、时间线、动作、转场、构图、声音事件或结尾状态：回到 Storyboard Package，形成新 revision，重新通过分镜门禁后再编译 Prompt；只改变不影响分镜语义的措辞、参数、模型或参考槽位时，主 Agent 更新合同和同一 Prompt 文档，重新 Preflight 后继续执行。
4. 已成功生成但人物、画风、动作、节奏、声音或转场质量不合格，且不改变已确认权威：进入下方整条重生成流程。

任何失败都不得通过静默删除参数、临时压缩 Prompt、替换素材或切换模型后继续执行；也不得绕过重新确认自动重试。

生成后用 `媒体分析步骤` 检查人物身份、剪影、与已确认 `style_authority` 的一致性、`palette_authority` 与 `saturation_policy`、内部默认视觉路径的主题色/强调色预算和角色配色策略、动作可读性、文字、Shot 承接、转场、节奏、声音关系、最终停留和异常伪影。

默认修复策略是整条重生成：

1. 在 Master Timeline 中定位失败位置。
2. 修改对应 Panel、Logical Shot、连续性锁或时间线指令，并覆盖 Storyboard Package。
3. 形成新的 `storyboard_revision`，重新通过分镜门禁。
4. 从获批分镜重新编译完整 `final_video_prompt`；如执行条件变化，同时更新 Render Contract。
5. 重新执行统一 Preflight，通过后直接生成指令。
6. 创建新的完整 Render Attempt，重新检查完整视频，并用通过的候选替代旧候选。

不生成局部视频补丁，不把修复后的 Shot 拼接回旧视频，不原样重复失败调用，也不静默切换模型或丢弃参考素材。

## 7. 定稿与交付

核对时长、画幅、最终文件数量、人物连续性、唯一画风权威、视觉产物形式、配色权威与饱和度策略、内部默认视觉路径的颜色预算、文字准确度、动作完成度、Logical Shot 承接、声音来源和最终停留。除非用户明确要求，否则不制作字幕。

只导出一个最终视频。九宫格分镜预览、视觉权威图、标题卡或最终 Prompt 仅在用户请求时作为辅助资产交付。最终回复提供成片路径或画布产物、时长/画幅、参考素材贡献摘要、声音来源和一项可执行的下一轮优化建议。

---
> © OmniAiLab ｜ 开发者：Mochiball ｜ OmniAiLab AI导演完整版（omniailabx.com）— 未经授权禁止复制、传播或二次分发。
