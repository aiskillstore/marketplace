# PPT 主题选择

此入口管理演示稿视觉偏好，不重新计算分析结果。旧模型PPT仍走旧校验；新版HTML模型通过独立章节演示投影生成PPT，完整主题支持范围见chapter-presentation.md。冻结模型不可为换主题而修改。

## 交互决策

- 首屏最多四方向：清晰商务 clean、沉稳管理 corporate、编辑叙事 editorial、温暖亲和 warm。目录见 `ppt-theme-directions.json`，颜色见 `themes.json`。
- 本轮明确要求优先，其次当前项目已确认偏好、标准版已确认方向。此前AI自动选择不能标成用户已确认。
- 用户明确说“你决定、直接生成”且无已确认偏好时，使用默认清晰商务；明确指定/确认沿用时，说明方向和理由后继续。
- 正常情况下若没有指定风格、也没有授权代选，先推荐一种、备选最多两种，每种实际导出封面和复杂图表两页，再渲染供用户选择；普通汇报也适用，无需用户先提出挑选。等待选择时可核对内容，但不能用超时或沉默代替选择。
- 用户一旦选定，记录为 explicit 再生成完整稿。美化版继承同一方向；需重新排版。输出目标和图表编辑需求分别记录：原生数据图表要求与矢量形状输出冲突时需取舍，不静默降级。
- 公司母版要求优先检查；仅提取颜色不能声称套用母版。本入口不支持任意模板复刻。额外SlideViber风格按需读取其当前CLI目录，不硬编码数量；额外预设需另行可读性核验，不绕过四方向注册表静默使用。
- 偏好仅写当前演示稿旁清单，不写全局记忆。

## 最小选择合同

宿主将已理解的意图写成JSON，调用 `python scripts/ppt_theme_selection.py --request intent.json --output selection.json`。无需用户填写JSON。已有output不会覆盖。

输入：`target` 为 standard/slideviber；`explicit: {id}`、`project_preference: {id, confirmed}`、`inherited: {id, confirmed}` 按上述优先级；`recommendation: {id}` 和未经确认的继承仅用于小样推荐，不构成选定。布尔 `direct / choose / template_required / template_supported / require_native_chart_data`；`direct` 仅在用户明确授权代选/直接生成时设置，没有明确偏好且 `direct` 为假默认 awaiting_choice。`choose` 与旧 `first_important` 保留兼容，不是触发正常选择的必要条件。`reason` 为简短实际依据，`source_model_sha256` 绑定源。

宿主需能够读取Skill、执行本地Python/Node依赖、生成PPT并展示其渲染预览。可视选择是交互协议，不保证所有Agent产品均支持这些能力；豆包、Workbuddy、千问办公等尚未逐一验证。若缺少执行或展示能力，明确说明缺口，不把色卡或网页示意当作真实PPT小样。

输出：`ppt-theme/1`、状态 ready/awaiting_choice/needs_decision、原因、选择来源、确认标志、主题参数及指纹、源模型指纹、编辑边界。`validate_selection` 在正式生成前再次核验状态与配置指纹，拒绝未知或漂移配置。小样须明确 `preview=True`，只能放行 awaiting_choice，不能绕过能力冲突。

`slideviber_theme` 从同一选择输出工作区theme.json。颜色按角色映射，不能机械把SlideViber第3强调色当成业务正向；正负方向与业务好坏分开。生成者保留标签、符号和图表尺度。配置可控制封面/标题构图，编辑叙事必须实际改变留白与构图，而不只是换色。

## 已有消费者与验证

- 原标准消费者 `build_pptx.py` 接受可选 `theme_selection`，先校验原报告合同，再覆盖仅用于渲染的主题；不改model。旧三个主题调用保持原状；旧布局未实现editorial时必须拒绝而不是冒充。
- `slideviber_handoff.py` 可接收相同可选清单并携带确认来源；未指定且未授权代选时等待两页小样选择，已确认偏好不重复审批。
- `ppt_theme_samples.mjs` 从绑定来源的两页内容规格生成标准PPT或SlideViber SVG，主题来自已验证selection；不接收原始Excel或绕过报告合同。它是主题展示消费者，非通用分析/PPT故事生成器。标准小样用公开python-pptx导出，SlideViber分支只输出SVG，不提前加载标准私有工具；运行前按所选目标进行环境预检。小样不得当作整稿，editorial两页可预览仍不代表其完整章节稿已验。
- 验证冻结图表数据、显示标签、顺序/尺度、负值、中文长标签、多系列、导出编辑性。全部方向两种路径的两页小样通过只说明受测主题可用，正式长稿仍须逐页检查。
