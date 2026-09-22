# 约束图

[English](constraint-graph.md)

独立约束图或仓库级约束清单使用此流程。保留现有架构查看器。下述命令相对于已安装的技能目录，而不是目标仓库；需要 Node.js 和 Git。按照安装指南先在技能安装目录执行一次 `npm ci`；运行下述命令无需构建前端。

## 发现声明范围

```sh
node scripts/discover-constraints.mjs /path/to/repository /output/constraints.catalog.json "Project name"
node scripts/render-constraints.mjs /output/constraints.catalog.json /output/sources.html --sources
node scripts/compile-constraint-rules.mjs /output/constraints.catalog.json /output/reviewed-rules.json /output/constraints.reviewed.json
node scripts/render-constraints.mjs /output/constraints.reviewed.json /output/constraints.html
```

采集器读取已提交的 HEAD，不修改仓库。枚举受 Git 跟踪的 AGENTS.md、CLAUDE.md、GEMINI.md、SKILL.md、根 CONTRIBUTING.md、GitHub Copilot 指令和 Cursor 规则，再递归跟进本地 Markdown 链接及反引号中的 Markdown 路径。保留原文、标题层级、行号和文件历史。排除可识别的夹具、归档及重复中文翻译并记录原因。引用表示发现路径，不代表权威或自动生效。技能按任务触发，目录指令按宿主继承规则适用。已实施的决策笔记仍是引用证据，不自动视为当前规则。

检查 `coverage.entries`、`excluded`、`unresolved`、`uninspectedPaths` 和 `limitations`。解决重要的缺失引用，或明确保留缺口。默认 1000 个来源预算，未处理队列写入 `uninspectedPaths`，不得静默宣告完整。适用时另查未跟踪或修改中的指令、宿主/用户指令、外部引用和非标准指令位置。发布私有来源原文前确认输出受众。按仓库证据或用户上下文确认真实项目名称。

输出是**来源清单**，不是自动语义审计。章节可能含多条规则或说明文字。不得把节点/章节数量称作生效约束数量。完整性相对于指定版本、声明的入口约定和已解析引用，不代表项目整个生命周期。

## 审查规则

按请求范围阅读纳入的每份指令/技能及相关引用章节。把独立义务拆成稳定规则 ID，保留精确来源、适用条件、覆盖关系和未解决冲突。交叉引用或措辞相似不能证明权威相同。不得因来源不在初始示例中而舍弃。排除的夹具指令和历史笔记不得进入生效规则。

默认图要求已审查的 `rules` 和 `ruleReview.scope`，拒绝未提炼的来源清单。仅完成来源采集不算完成人类可读的约束图。每条规则必须回答做什么、何时适用、为什么重要、如何检查。原文放到详情。合并重复义务时保留条件和来源，不从标题直接推断生效规则。

编写 `reviewed-rules.json`，包含相同的 `revision`、准确的 `scope` 和 `groups`。每组包含 `sourcePath`、`category`、可选的 `topic: {id, name}` 和 `rules`。每条作者审查后的规则包含稳定 `id`、短 `name`、来源中唯一的原文 `anchor`、`explanation`、`condition`、`verification` 和可选的 `applicability`。编译器把锚点定位到段落/列表项，提取真实行号，拒绝缺失/歧义锚点和版本不匹配；它不代替语义审查。`examples/deepseek-constraints.rules.json` 展示格式，其中的项目规则不得复制到其他项目。

产出清单中必需的 `rules` 条目示例：

```json
{
  "id": "rule-model-visible-log",
  "category": "interfaces",
  "sourcePath": "AGENTS.md",
  "line": 111,
  "endLine": 111,
  "name": "模型可见输入必须记录",
  "explanation": "发送给模型的新输入需要持久化会话事件。",
  "condition": "新增模型可见输入时",
  "applicability": "conditional",
  "verification": "检查事件和重放路径，执行相关重放测试。"
}
```

这里的行号仅作示例，须检查目标快照。适用性支持 `applicable`、`conditional`、`superseded`、`conflict`、`uncertain`。覆盖或冲突的原因写入 `explanation`。渲染器从来源提取原文，不编造引用。审查覆盖声明范围前保持 `coverage.semanticReview: pending`，未审查部分记录到 limitations 和 `ruleReview.scope`。部分审查结果必须明确标明范围才能交付，不得称作完整生效规则集。架构/变更任务需要使用这些规则时，转换为现有[约束契约](constraints.zh.md)，保留来源证据和适用性，不把图上分类直接作为模块所有权。

## 历史与验证

区分三个标识：稳定的 `rule.id`（显示的 R 编号只是展示序号）、规则原文历史 `vN`、完整仓库快照提交号。需要生成历史时，将仓库作为编译器第四个参数：

```sh
node scripts/compile-constraint-rules.mjs catalog.json reviewed-rules.json versioned.json /path/to/repository
node scripts/render-constraints.mjs versioned.json constraints.html
```

编译器对照固定快照检查来源文本，再逐条查询引用段落/列表项的 Git 行历史。记录 `history`，包含 `status: tracked`、`method: git-line-history`、`snapshot`、`sourcePath`、`line`、`endLine`、`version`、`lastEdited` 和真实 `{commit,date}` 数组 `commits`。这是原文行段的历史条目数，不是语义发布版本或 AI 解释的修订次数。移动、格式修改或多条义务共用一个段落会影响计数。不得手工编造这些字段，也不能用整份文件历史代替。渲染器校验来源一致性，不证明手写 Git 证据真实，须使用采集器。重新编译作者输入时丢弃旧历史，防止复用过期数据。

卡片展示 R 编号、`vN` 和角色；详情展示计算方法和完整提交证据，图例显示仓库快照。没有历史、浅克隆或无法查询行历史时显示“版本未追踪”，不填 v1。采集器不自动拉取历史。渲染器拒绝属于其他快照或来源行段的已追踪历史。分类节点不编造版本。交给其他 AI 生成时，要求一起交付审查选择文件、带版本清单和 HTML，保留可检查的来源依据。

来源文件节点的 vN 表示该**文件当前路径**的 Git 历史条目数量，不是某条规则的语义版本，不追溯重命名前历史；日期也属于文件。浅历史不显示版本计数并明确披露；不得静默拉取或把浅历史数量称作完整。原文章节不编造独立版本。即使来源已提交，未知合规结果仍保持 pending。

代码漂移需要已检查的实现关联和有依据的基准。文件变化使用架构契约与 `constraint-freshness.mjs` 检查。不得从标题推断所有权、把后续提交一概视为违规，或编造彩色状态徽标。此前 DeepSeek 六条规则原型使用另一种明确受限的行历史启发式；它不是通用扫描器，不能提供全局合规统计。测试和代码审查证据放在 `constraintReviews`，与来源时间及适用性分开。

## 集成到架构页面

保留架构页原有的横向工具栏和画布布局。原生约束视图包含规则目录、树形画布和按需阅读面板，不使用应用图标栏、底部状态栏或 iframe。不要给架构页添加模块目录侧栏。


用户要求组合页面时，复用现有架构 JSON，一次渲染两个视图：

```sh
node scripts/render.mjs architecture.json project.html --constraints versioned.json
```

活动 JSONL 与 `--repo` 仍为可选参数。CLI 写出 `project.html` 和辅助索引 `project.sources.html`，两者一起交付。不传 `--constraints` 时原架构输出不变。渲染器 API 的第三个参数支持 `constraintCatalog` 和可选的 `constraintSourceHref`；API 调用方自行生成辅助来源索引。

切换视图时保留各自画布状态。页头保留项目名称、语言控件和共享明暗主题；角色颜色含义一致。架构版本与约束快照是不同标识。控件使用主页面语言；已撰写规则和来源引文保持原语言。来源索引是辅助页面，不是第二张主图。

项目名称必须匹配。可选模块关联要求清单明确声明 `architectureBinding: {mapId, mapRevision, sourceRevision}`，与架构和清单的完整提交一致，并在已审查规则上声明 `modules: ["module-id"]`。编译时在审查选择中携带此绑定；重新编译会丢弃旧清单绑定。撰写关联前检查源码依据。渲染器拒绝过期绑定和未知模块 ID。角色相似绝不是模块关联。没有绑定时，完整图仍可用，模块详情提示尚未记录关联；有绑定时，模块按钮仅打开关联规则及其祖先，“查看全部规则”恢复完整图。改变筛选会初始化新的约束布局；仅切换架构/约束会保留布局。筛选不改变版本与核验证据。

检查两个视图、切换保留状态、主题变化、中英文导航、窄屏、模块筛选和页内来源阅读。保留原架构布局。即使配套约束来自真实源码历史，概念演示架构仍须注明是概念图。

## 渲染与交付

`render-constraints.mjs` 接受 `birdview.constraint-catalog/v1`，默认生成**规则图**：项目 → 类别 → 可选的人类语义主题 → 规则。六种类别为 `lifecycle`、`interfaces`、`configuration`、`security`、`testing`、`delivery`。主题使用编号和文字；颜色按架构角色统一：frontend 蓝、backend 青绿、cache 青、database 紫、queue 琥珀、security 玫瑰、generic 灰蓝。规则可填 targetRole；非通用角色必须给 roleReason 来源依据。跨角色或不明确时保持 generic，不根据主题名猜测角色。同角色分组沿用该色，混合分组为通用色。工具栏角色图例显示规则数量；卡片同时显示规则编号和角色文字。适用性和核验结果在详情独立显示，颜色不表达通过或失败。标题应简洁并表达可执行要求；卡片最多显示两行，悬停提示和阅读面板保留完整标题。通过主题分组控制每层阅读量，通常不超过八个子节点。文件时间/版本和采集数量不占规则卡片，不把成千上万个统一待定的来源节点作为主视图。

渲染器使用 Birdview 自有 HTML 卡片、SVG 连线和子树布局，不依赖第三方图运行时。`constraint-canvas.js` 在独立和集成页面挂载同一组件；`constraint-page.html` 提供独立页面外壳；`constraint-canvas.css` 将样式限定在约束视图。`buildConstraintGraph()` 准备 `birdview.constraint-view/v1` 展示数据，不改变输入清单契约。详情先呈现适用条件、解释和验证计划，再展示来源依据与规则历史。文档按安全文本和基础标题、引文渲染，不执行任意 HTML 或嵌入图表。全部已采集来源（包括未审查的 skills 与引用文档）显示在“按目录”；双击来源文件阅读原文和审查状态。覆盖情况仍在“阅读范围”。工具栏不再跳转其他页面。CLI 为兼容保留相邻 `.sources.html` 导出；`--sources` 仅渲染此辅助导出。

打开 HTML，在桌面和窄屏检查展开、原文阅读、长内容及覆盖披露。报告实际采集数量、未解决/排除范围、语义审查状态和执行过的测试。来源采集完整不等于生效规则审查完整，分别说明。页面离线只读，不是实时监控或执行拦截器。生成的原生页面包含 Birdview 许可；保留实际分发依赖的许可证。


目录与画布同步展开和选择；搜索匹配规则名称、解释和原文，并保留祖先路径。超过 100 项搜索结果时只显示前 100 项并明确提示，避免把整份来源清单铺满画布。提供拖动平移、Ctrl/Command + 滚轮缩放、触摸双指缩放、加减按钮和适配全图。画布获得焦点后方向键平移，加减键缩放、0 适配；卡片支持 Enter 选择和左右键导航，Escape 关闭浮层。窄屏默认收起目录，选择后收起，并以抽屉展示详情。展开、搜索和缩放只影响展示，不改变规则版本或验证状态。

## 目录与主题视图

已审查规则图提供“按主题”和“按目录”，共用规则 ID、版本与正文。分组前发现根目录和嵌套指令文件。目录节点依据已记录来源作用域列出本目录来源和上级指令候选；仅凭存放路径不能证明适用性、覆盖或冲突解决。Skills 与引用文档需审查调用和引用关系。已采集但未提炼规则的指令文件也应显示，明确提炼缺口。目录位置表达来源，不代表模块所有权。切换视图时保留模块筛选。双击节点或 Shift+Enter 打开共享详情弹窗。
