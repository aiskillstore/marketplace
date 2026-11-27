# Changelog

本文件记录 `fuxin-office-suite`（福昕Office全家桶技能套件）的版本迭代、新增能力与修复内容。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

> **版本号口径**：采用**语义化版本 + 构建号**双轨。
>
> | 位置 | 字段 | 当前值 |
> |---|---|---|
> | `SKILL.md` | frontmatter `version` | `1.0.3` |
> | `manifest.json` | `version` | `1.0.3`（与 `SKILL.md` 对齐） |
> | `manifest.json` | `buildVersion`（新增） | `1.00.03.242` |
> | `CHANGELOG.md` / `README.md` | 条目 | `1.0.3 (build 1.00.03.242)` |
>
> 语义化版本用于对外沟通与技能市场识别，构建号用于追溯内部构建流水线，两者独立演进。

## [1.0.3 (build 1.00.03.242)] - 2026-11-16

对应工单 #24510（SKILL.md frontmatter `description_en` 含未转义英文冒号，YAML 严格解析失败导致 8 字段全部读不到）。`manifest.json` 的 `version` 保持 `1.0.3` 不变，仅 `buildVersion` 升至 `1.00.03.242`。

### Fixed

- **`SKILL.md` frontmatter 修复 YAML 严格解析失败**：`description_en` 的值含一个未转义的英文冒号（`... directly in Foxit Office: auto-compose ...`），`yaml.safe_load` 在第 8 行 182 列报 `ScannerError: mapping values are not allowed here`，整段 frontmatter 解析中断，`name` / `display_name` / `display_name_en` / `description` / `description_zh` / `description_en` / `version` / `author` 8 个字段全部读不到；此前逐行 `key: value` 的宽容解析可绕过该行，故「字段数量够不够」的校验无法发现本问题。现按「整值加双引号」写法修复：8 个字段值统一加双引号包裹（含冒号的 `description_en` 与含全角标点、破折号的 `description` / `description_zh` 一并处理），严格解析通过且 8 个键齐全、无重复键。不影响 Skill 运行时业务能力（预检与 Word / Excel / PPT 调用链路均正常）。

### Added

- **出包前置校验**：新增 YAML 严格解析校验步骤（`yaml.safe_load` 解析 frontmatter 必须成功且取出 8 个键、无重复键），作为发布前置检查替代人工目视字段数量，防止同类标点转义缺陷再次漏出。

## [1.0.3] - 2026-11-10

对应工单 #24154（「未安装下载引导改渠道包 + frontmatter 过审」）。目标：发布 V1.0.3，完成「未安装引导 → officeskill 渠道直链」与「frontmatter 七项补齐」。

### Changed

- **`SKILL.md` frontmatter 按平台必填校验补齐**：`name` / `display_name`（福昕Office助手）/ `display_name_en`（Foxit Office Assistant）/ `description` / `description_zh` / `description_en` / `version`（1.0.3）/ **`author`（福州福昕网络技术有限责任公司，本版新增）**。此前缺 `author` 且展示名、描述面向内部路由，WorkBuddy 开放平台校验不通过，线上包无法过审发布。
- **`manifest.json` 展示名同步为「福昕Office助手」**，与技能市场展示名对齐。

### Fixed

- **「未安装」引导文案统一改为渠道包直链**（`reference/bridge.md` 三处：就绪状态六档、未就绪明细、错误统一展示）：统一为「检测到您未安装福昕Office客户端，请复制下载链接到浏览器进行下载安装：https://file.foxitreader.cn/file/Channel/fuxinoffice_win/officeskill_FuxinOffice.exe」。此前文案只提示「请先安装」，无下载渠道，运营无法归因 Skill 带来的下载量（来源运营单 #22707）。**已安装 / 未运行 / 连接失败等其余场景文案不变。**

## [1.0.3 (build 1.00.03.241)] - 2026-11-16

对应工单 #23879（`extract_data_to_new_sheet` 缺少行筛选能力）、#24142（同工具的 `gt`/`lt` 误命中空单元格）与发布者主体信息整改（SkillHub 认证主体）。`manifest.json` 的 `version` 保持 `1.0.3` 不变，仅 `buildVersion` 升至 `1.00.03.241`。

### Changed

- **发布者主体信息统一为认证主体全称**（`manifest.json`、`LICENSE.md`、`README.md`）：SkillHub 平台认证发布者为「福昕网络技术有限责任公司」，包内按其全称统一——`manifest.json` 的 `author.name` 由 `Fuxin` 改为 `福州福昕网络技术有限责任公司`，`author.url` 补为福昕Office产品页官网 `https://www.fuxinoffice.com`；`LICENSE.md` 第 3 行版权声明与第 19 行商业授权联系行改为全称；`README.md` 第 163 行 © 行改为全称。品牌词「Fuxin」保留（`FuxinAiService`、`FuxinOffice` 等产品/服务名不变）。
- **`extract_data_to_new_sheet` 的编排口径明确为改用 `filter`**（`reference/excel.md` 缺参/歧义段）：此前用户说「抽取包含 X 的行」时，文档未给出对应参数，Agent 只能退回「全量抽取 → `get_cell_values` 读全表 → 本地筛选 → 逐格写回」的冗长链路。现明确此类请求直接用 `filter`，不得先整表复制再删行，也不得自行读全表再写回。
- **路由触发词补充「筛选抽取」**（`SKILL.md` Excel 路由表、`README.md` 能力概览）：使「抽取包含…的行」「只要…的数据」一类说法能稳定路由到本场景。

### Added

- **`extract_data_to_new_sheet` 支持行筛选参数 `filter`**（`reference/excel.md`）：数组形式，多项之间为 AND。每项 `{column, operator, value}`——`column` 取**源表**列字母或 0 基索引（不是 `columns` 之后的输出列位置）；`operator` 取 `contains`（默认）/ `startsWith` / `equals` / `notEquals` / `gt` / `lt`，文本类不区分大小写，`gt`/`lt` 两侧均为数字时按数值比较；`value` 为字符串或数字。不传则不筛选；无命中时返回 `ok:true` 且 `matchedRows:0`（目标表只有表头），**不算失败**。参数表新增该行，调用示例补充筛选写法。

### Fixed

- **`extract_data_to_new_sheet` 的 `gt`/`lt` 不再把空单元格判为命中**（#24142，`reference/excel.md` 参数表）：此前内部比较函数对「一侧数字、一侧非数字」遵循「数字优先」规则（本为排序让数字排前），导致空单元格对数字阈值恒定返回 1——`gt` 于是把所有空值行都判为满足（`lt` 因同样返回 1 反而不命中，故缺陷只在 `gt` 暴露）。现 `gt`/`lt` 比较前先判空：**单元格为空、或阈值本身为空时一律不命中**。工单复现用例 `A/99, B/100, C/100.5, D/(空), E/101` 配 `{"column":"B","operator":"gt","value":100}`，由 `matchedRows=3`（含 `["D",""]` 空值行）修正为 `2`（100.5、101）。`equals`/`notEquals`/`contains`/`startsWith` 语义不变，排序行为不变。

## [1.0.1 (build 1.00.03.239)] - 2026-10-28

对应技能文档工单 #23878（工具名单/双下划线不一致、`get_document_info` 与 `save_document_as` 名称错误）与 #23884（`ppt.md` 未提示新建演示稿自带空白页）。

### Fixed

- **工具全名统一为 `{产品ID}__{工具名}`（双下划线）**（`SKILL.md`、`reference/word.md`、`reference/excel.md`、`reference/ppt.md`、`reference/bridge.md`、`reference/doc-qa.md`、`reference/batch-undo.md`、`README.md`）：此前文档把产品 ID 与工具名之间的分隔符写成单下划线（如 `Word_get_path`），而网关对外注册的是双下划线（`Word__get_path`）。Agent 严格按文档拼名会直接收到 `tool not found` 错误。现已把全部可调用位置修正为双下划线，涉及预检章节、使用方式各步骤、只读工具表、批次原语与产品 ID 说明。
- **「取文档信息」按产品分别改名，不采用统一替换**：Word 实际工具是 `get_doc_info`，此前文档多处按 `get_document_info` 调用（Word 下不存在）；Excel 两者皆无，探活改用真实存在的 `get_sheet_summary` / `get_path`；PowerPoint 保持 `get_document_info`（本就不是 `get_doc_info`）。工单中「Excel / PowerPoint 同理」仅对**分隔符**成立、对**工具名本身**不成立，故未做机械替换，避免把 PowerPoint 唯一的正确名字改错。
- **`save_document_as` 改为 `save_document` + `path`**（`SKILL.md` 4.2、`reference/bridge.md` 保存例外、`reference/word.md`、`reference/excel.md`、`reference/ppt.md`、`README.md`）：网关三产品均未提供 `save_document_as`，但「另存为」需求真实存在——由 `save_document` 传 `path`（绝对路径）+ 可选 `format`（缺省从扩展名推断）实现。文档已改为该写法并标注同为不可逆保存、需预确认，既消除不存在的工具名，也保留能力。
- **`ppt.md` 补充全新演示稿的空白页处理**（对应 #23884）：新建演示文稿自带 1 页空白占位页，而 `generate_deck` 的 `startPosition` 默认 `-1`＝末尾追加、不清理既有页，用户要 5 页会得到 6 页（`created:5` + `totalSlides:6`）。新增「全新演示稿的空白页」小节，给出 A（先 `organize_deck` 传 `deleteSlides:[0]` 删空白页再生成）/ B（`startPosition:0` 原位插入后删末页）两种方案，并明确两条防错规则：`startPosition` 不是总页数控制；向用户报页数必须用 `get_ppt_outline` 的实际总页数，不得直接报 `created` 数。
- **`ppt.md` 修正空白页两方案的推荐顺序，并补充「演示文稿至少保留 1 页」**（对应 #23884 回归反馈）：原文档把「先删空白页再生成」（方案 A）列为推荐，实测无效——PowerPoint **强制保留至少 1 页**，文稿仅剩 1 页时删除会返回成功（`deleted:1` / `successCount:1`）但页数不变，产品自动补回一页空白页；全新演示稿恰好只有 1 页，故方案 A 在该场景下必然失败。现调整为：**方案 B（`startPosition:0` 原位插入后删末页）为推荐且是全新演示稿唯一可行路径**，方案 A 标注「**仅适用当前 ≥2 页**」；新增「PowerPoint 强制保留至少 1 页」前置说明，并给出方案 B 实测链路（1 页 → `startPosition:0` 生成 5 页得 6 页 → `delete_slides` 传 `slideIndexes:[5]` 得 5 页）与方案 A 反例（返回 `deleted:1` 但页数仍为 1），提示「看到 `deleted:1` 不等于删成功，必须用 `get_ppt_outline` 复核页数」。`organize_deck` 参数表的 `deleteSlides` 行同步补该约束（网关 `delete_slides` 的工具描述未包含此行为，文档是唯一说明来源）。
- **`ppt.md` / `doc-qa.md` 移除 `get_slide_count`、`get_slide_layouts` 引用，改用 `get_ppt_outline`**：两者均不在 Level 1 白名单内，文档却把 `get_slide_count` 写成「核对页数的唯一手段」，Agent 依此拼名会偏离白名单。现改为统一用 `get_ppt_outline`（条目数＝总页数，末条 `slideNumber` 即总页数），空演示稿判定也简化为「页数 1 且该页仅占位文字」；并补充两条使用约束——默认 `maxSlides=0` 走全量、传了上限则条目数只是扫描上限不是总页数；`applyTemplates` 的 (masterIndex, layoutIndex) 优先省略、确需换版式时先按 Level 2 检索布局枚举工具，禁止硬编码索引。

### Added

- **工具命名规范章节**（`SKILL.md`「三·通用约定」第 10 条）：明确 `{产品ID}__{工具名}` 双下划线规范、产品 ID 只有 `Word` / `Excel` / `PowerPoint` 三个，并用对照表列出四种写法的结果（双下划线正确、单下划线错误、缺前缀错误、应用名 `FuxinOffice*` 作前缀错误），另附三产品「取信息/取路径/取状态/保存/另存为」工具名对照表，标注 Excel 与 PowerPoint 缺失的工具，防止跨产品套用。
- **实际工具清单快照**（`SKILL.md`「三·通用约定」第 11 条）：按产品列出 Level 1 工具白名单（Word 14 / Excel 13 / PowerPoint 20，共 47 个），分「写场景工具」与「只读 / 原子接口」两栏，逐条核验均存在于网关 `resources/products/*/tools.json`（0 缺失、0 重复、0 臆造）。未列入白名单的工具（如 Word 的 `insert_text` / `replace_text` / `batch_find_replace`、PowerPoint 的 `get_slide_count` / `get_slide_layouts`）明确标注属 Level 2、不在 Level 1 能力声明内，避免把「网关有这个工具」误读为「它属于 Level 1 预置」。
- **`ppt.md` 只读工具列表补齐并改以 `get_ppt_outline` 取页数**：原列表未列页数相关工具，会导致 Agent 只能看 `generate_deck` 的 `created` 而误报页数；现明确 `get_ppt_outline` 为取页数的唯一手段（条目数＝总页数），不再依赖白名单外的页数工具。

## [1.00.03.238] - 2026-10-28

对应数据统计工单 #23449「agent_product 无法识别到 workbuddy」。

### Added

- **埋点新增必填字段 `agent_product`（平台标识）**（`SKILL.md`、`reference/bridge.md`、`reference/word.md`、`reference/excel.md`、`reference/ppt.md`、`reference/doc-qa.md`）：此前 telemetry 只上报 `skill_id` / `scenario_id`，服务端只能靠 MCP 客户端上报的 `clientInfo.name` 反推 Agent 产品，而该名称常是 `probe`、`mcp-inspector` 之类的客户端标识，无法稳定映射到具体产品。现要求每次 `tools/call` 在同一个 `com.foxit.office/telemetry` 对象内一并传入 `agent_product`，值为当前实际运行本 Agent 的平台标识，服务端据此直接识别产品，不再依赖名称推断。
- **平台枚举与取值规则**（`SKILL.md`「三·通用约定」第 8 条）：新增枚举表 `workbuddy` / `vscode` / `cursor` / `claude-desktop` / `mcp-inspector` / 其它宿主稳定小写标识，并规定无法确证时填 `unknown`；同时明确四条约束——必须真实不得猜测、`unknown` 优于错误值（填错会把调用量污染成另一平台）、同一会话内恒定不随工具或场景变化、字段名用下划线 `agent_product`（服务端落库映射为指标字段 `agentProduct`）。
- **取值优先级说明**（`SKILL.md`、`reference/bridge.md`）：网关侧按 telemetry `agent_product` > `X-MCP-Agent-Product` 请求头 > `clientInfo.name` 取值；文档同时注明请求头由 MCP 客户端注入、**Skill 提示词无法设置 HTTP 头**，因此 Skill 侧只需保证 telemetry 字段，若客户端同时支持请求头则两处取值应一致、不得冲突，避免把无法实现的要求写成 Skill 义务。

### Changed

- **埋点表述由双字段统一扩为三字段**（`SKILL.md` 第 68、109、162、163、166、169、171、190 行及相关段落，`reference/word.md` 第 61、189、194 行，`reference/excel.md` 第 60、167、172 行，`reference/ppt.md` 第 62、201、206 行，`reference/bridge.md` 第 203、265 行，`reference/doc-qa.md` 第 58、64、88 行）：「两个字段」「该组字段」等旧表述一并改写，只读工具埋点映射章节补一句说明 `agent_product` 不参与场景判定、全表沿用同一值，防止只读路径漏带。
- **请求格式示例同步**（`SKILL.md` UC-E2E-01 示例、`reference/bridge.md` 独立预检示例）：示例 telemetry 对象内补 `agent_product`，并加注示例值仅为结构示意、实际须填当前真实平台、不得照抄。

## [1.00.03.237] - 2026-10-28

对应技能测试工单 #23868（版本号三处不一致）与 #23866（撤销提示文案空格不一致）。

### Fixed

- **版本号统一为单一构建号**（`manifest.json`、`SKILL.md`、`README.md`、本文件）：`SKILL.md` frontmatter 此前为语义化版本 `1.0.1`，与 `manifest.json` / 本文件的 `1.00.03.236` 不一致，按 `SKILL.md` 判断会误认为技能停留在早期版本。现四处统一为 `1.00.03.237`，并在本文件顶部补充版本号口径说明。**（注：该「单一构建号」口径已于 `1.0.1` 起调整为双轨，见本文件顶部说明；本条仅作历史记录保留）**
- **品牌名统一为不带空格的形式**（`SKILL.md`、`README.md`、`CHANGELOG.md`、`LICENSE.md`、`manifest.json`、`schema/input_schema.json`、`examples/sample_case.json`、`reference/*.md`）：本套件内品牌名此前存在带空格与不带空格两种写法混用，导致用户可见文案（`user_message`）与「逐字一致」要求冲突。现统一为不带空格的形式，共修正 165 处——其中 94 处为品牌名内部的空格（`reference/bridge.md` 45 处、`examples/sample_case.json` 12 处、`SKILL.md` 9 处、本文件 8 处、`README.md` 4 处、`reference/word.md` 4 处、`LICENSE.md` 3 处、`reference/excel.md` 3 处、`manifest.json` 2 处、`reference/ppt.md` 2 处、`schema/input_schema.json` 1 处、`reference/batch-undo.md` 1 处），另 71 处为品牌名与后接中文/英文之间多余的空格。仅保留 Markdown 表格分隔所需的 2 处空格。
- **写后撤销提示三处逐字对齐**：`SKILL.md` 汇总层与 `reference/bridge.md`、`reference/word.md`、`reference/excel.md` 的撤销提示统一为 `改好了。要撤回改动：回复「撤销」，或在福昕Office按 Ctrl+Z。`

## [1.00.03.236] - 2026-10-12

对应 SdkAdapter 侧 PPT 页数计数问题单 #22382「AI 修改文档后返回的页数会比正常 PPT 页数少一页」。

### Fixed

- **PPT 页码口径统一为 0 基**（`reference/ppt.md`、`reference/doc-qa.md`）：`get_slide_text`、`deleteSlides`、`startPosition`、`edits.slideIndex`、`duplicateSlides`/`moveSlides`/`applyTemplates` 的索引说明此前仍为 1 基（且 `edits.slideIndex` 用 `0=当前页`），与已发布的 0 基实现（`edits.slideIndex` 的 `-1`=当前选中页、`startPosition` 合法范围 `[0, 当前页数]`）不一致，会导致按文档传参改错页。
- **明确「报告页码用 slideNumber、调用工具用 slideIndex」**：`slideIndex` 为 0 基索引（入参），`slideNumber` 为 1 基页码（`get_ppt_outline` / `get_slide_text` 返回），禁止混用——此前把 0 基 slideIndex 当页码回复用户，会把第 N 页说成第 N-1 页。

## [1.00.03.235] - 2026-08-26

这是 `fuxin-office-suite`（福昕Office全家桶技能套件）的**首个对外发布版本**，对应 SKILL.md 版本号 `1.00.03.235`。

### Added

- 首次对外发布完整技能套件，对外暴露唯一入口技能 `fuxin-office`，覆盖：
  - 连接预检（`reference/bridge.md`）
  - Word 文档编排（`reference/word.md`）
  - Excel 表格编排（`reference/excel.md`）
  - PowerPoint 演示编排（`reference/ppt.md`）
  - 文档只读问答（`reference/doc-qa.md`）
  - 批次撤销（`reference/batch-undo.md`）
  - 企业自定义流程示例（`reference/custom-tool.md`）
- 补齐对外交付配套资源：`manifest.json`、`README.md`、`CHANGELOG.md`、`LICENSE.md`、`schema/input_schema.json`、`examples/sample_case.json`。
