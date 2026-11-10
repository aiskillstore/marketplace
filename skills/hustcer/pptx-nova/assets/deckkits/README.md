# DeckKits

经过验证矩阵通过后冻结的 DeckKit，用于 pptx-nova 的“DeckKit 模式”二次创作快路径。

套件版本、readiness、选型条件和验证记录以 `catalog.json` 为准。自动选型按用途、语言、
内容密度、页型覆盖范围和匹配度选择。

Teal Journal 1.0.0 为 default，可参与默认及自动交付选择：八类页面职责、十六种构图，以暖纸底、河蓝结构、
珊瑚强调、开放表格与时间派生路径表达编辑式手册。支持中文、英文及混排；图表和表格原生可编辑，
照片仅为明确标识的可编辑外壳，未注册图片输入。容量、同步边界与验收范围见
[使用说明](teal-journal/intent.md)。

Pink Script 1.0.0 为 production，可参与自动交付选择：九类页面职责、十八种构图，以暖黑、玫红、正体衬线、
巨大数字与开放细线表达夜间编辑叙事。支持中文、英文及混排，原生折线和矩阵可编辑；透明二维码
通过资产槽绑定。容量、字体、同步边界及机器/视觉/原生验收范围见
[使用说明](pink-script/intent.md)。

Paper Scholar 1.0.0 为 default，可参与默认及自动交付选择：八类研究课件职责、十六种构图，保留暖纸底、
橄榄绿／珊瑚层级、拱形等高线、十点比例图、半衰期机制图和开放分组表。支持中文、英文及
混排；文字、形状、柱图和表格原生可编辑，案例照片使用 shape 外壳。容量、字体、同步边界
及逐页／PowerPoint 验收范围见 [使用说明](paper-scholar/intent.md)。

## 目录结构

```text
assets/deckkits/
├── README.md
├── catalog.json                   # 所有路径相对本目录
├── validate-content.mjs            # content 校验 CLI
├── shared/                        # 共用运行时、校验和注册调度
│   ├── core-primitives.kit.mjs     # 几何安全与 op 生成
│   ├── icon-assets.kit.mjs         # 固定 Tabler bundle 的图片 helper
│   ├── deckkit-paths.mjs           # 与 cwd 无关的资源路径
│   ├── design-contract.mjs         # 合同断言与对象/数值回读
│   ├── design-family-registry.mjs  # 套件视觉族注册
│   ├── design-text.mjs             # 通用文字换行
│   ├── text-layout.mjs             # 跨套件文字容量计划
│   ├── evidence-components.mjs     # 原生数据证据组件
│   ├── native-evidence-plan.mjs    # 共用证据计划执行
│   ├── animation-corpus.mjs        # 动画语料检查
│   └── validate-deckkit.mjs        # 统一内容/语义校验
├── schemas/                       # 仅放公共 schema
│   ├── content.schema.json
│   └── design.schema.json
├── cartesian/                     # 每个套件采用同一组织方式
│   ├── cartesian.kit.mjs           # 对外薄入口
│   ├── design.json                # 设计合同事实源
│   ├── intent.md                  # 设计判断与编辑边界
│   ├── components.mjs             # 套件组件执行（需要时提供）
│   ├── layouts.mjs                # 构图选择与逐实例容量
│   ├── registry.mjs               # 视觉族注册（需要时提供）
│   ├── exhibit.mjs                # 额外套件模块（需要时提供）
│   ├── schemas/                   # 本套件各页型 schema
│   └── examples/
│       ├── content.json           # 主示例
│       ├── build.mjs              # 开发/benchmark 构建胶水
│       └── animation-content.json # 命名明确的补充示例
├── consulting-dark/
├── mckinsey-blue/
└── ...                            # 其他 catalog 注册套件
```

目录约定：

- 套件入口固定为 `<id>/<id>.kit.mjs`，设计合同固定为 `<id>/design.json`。
  套件内模块使用 `components.mjs`、`layouts.mjs`、`registry.mjs` 等职责名称，不再重复套件前缀。
- 每个套件的页型 schema 和开发示例分别归入 `<id>/schemas/` 与 `<id>/examples/`。
  `examples/build.mjs` 不传参数时读取同目录的 `content.json`，可从任意工作目录运行。
  catalog 的 `path`、`designContract`、`examples` 路径均相对 `assets/deckkits/`；
  benchmark index 的路径相对 `benchmarks/visual/`。
- 共用 helper 放在 `shared/`，套件不能直接导入另一个套件的实现。
  `shared/design-family-registry.mjs` 和统一合同/校验模块负责注册调度，可以导入各套件公开的注册或解析接口。
- 用户可见的 PPTX showcase 继续位于 `assets/examples/deckkits/<id>/`；
  视觉回归 fixture、基线与验收记录继续位于 `benchmarks/visual/cases/<id>/`。
- 根目录只保留 README、catalog 和校验 CLI。`node tools/pptx-nova-audit-public.mjs --strict`
  同时检查目录归属、标准模块名、catalog 路径、schema/示例存在性和套件间直接依赖。
  新增 DeckKit 时也须通过 `node --test tools/tests/maintenance/deckkit-layout.test.mjs`。

Biennale Yellow 2.0 保留九个页型名称，全部经注册合同执行；数据页改用数值、单位、来源，
不再分发旧固定页型渲染器。字段迁移与构图说明见 [intent.md](biennale-yellow/intent.md)。

Cartesian 2.0 保留十个编辑式页型，另提供五个原生展示页型，共二十八个注册布局，
全部经注册组件计划执行。编辑式图表必须提供单位、来源；展示页须提供来源，并在说明中标明适用的单位。
图片槽位和原生段落动画 target 保留。旧页型生成器及旧版 showcase 已替换，
不提供双执行路径。见 [设计与迁移说明](cartesian/intent.md)。

Broadside 2.0 保留十六类职责，提供二十八个注册构图；黑橙色域、超重标题、斜线列表、
衰减文字与闭环结构经合同执行。柱图、横条图和环图保留原生数据对象，要求数值、单位、
来源和系列名；独立环图图例需从 content 重新生成以同步手工数据编辑。
字体采用相近的常用替代，图壳仍为占位形状。见 [设计与迁移说明](broadside/intent.md)。
普通英文标题默认 sentence case；封面、章节和短宣言可有意采用全小写。专名、缩写与用户指定
写法保留，渲染器不自动转换大小写；换行也不重新大写。

Long Table 2.0 保留八个页型入口，十五个注册布局支持封面、信札、索引、特写、节目单、引文、
日程与收束。奶油纸底、锈红单墨、重标题、衬线正文、徽章与胶囊由合同约束；原生日程表格逐格回读。
Arial Black / Georgia 和正体 Arial Unicode MS 为明确替代字体，不随套件打包。
手工调整表格行高或列宽不会同步独立状态轮廓，须从 content 重新生成；不提供图表或图片输入。
见 [设计与迁移说明](long-table/intent.md)。

Swiss Grid 2.0 保留十五个页型入口，以二十四个注册布局表达非对称排版、开放名录、字体样张、
网格示意、时间线与原生表格。封面/收束不显示灰色施工网格；原稿图标、字重差异和列末注释已补齐。
计量示意的几何与标注来自同一数值模型，手工编辑后须重新生成才能同步；Tabler SVG 是矢量图片。
Helvetica / Arial Black / Arial Unicode MS 是不嵌入的替代字体。见 [设计与迁移说明](swiss-grid/intent.md)。

McKinsey Blue 2.0 保留八个页型入口，十六个注册布局覆盖观点标题、直接数值、面积优先矩阵、
渐进蓝色支柱、五项排序与四阶段路线。补回原稿图标、责任/成本明细和治理栏；图表与表格为原生对象，
cohort 宽度和圆面积来自数值。Arial / Arial Unicode MS 不嵌入；SVG 图标的路径节点不承诺原生编辑。
手工改图表、派生形状或旁注不会自动同步，须从 content 重新生成。较长内容应改用合法变体、重组或拆页。
见 [设计与迁移说明](mckinsey-blue/intent.md)。

Clear Impact 提供十二类开放式证据报告职责及二十四个注册构图，支持白底深绿层级、指标带、
原生柱图、稀疏表格、处理链、数值派生达成条和差异桥。中文、英文与混排使用正体无衬线字体。
当前为 production，可参与自动交付选择；派生形状与旁注编辑后须从 content 重新生成。详见 [设计与边界](clear-impact/intent.md)。

Warm Clay 提供八类暖陶土报告职责与十五个有界构图，使用奶油底、墨棕衬线标题、
陶土证据、粉色编号和角落圆环。柱图与表格为原生对象；中文、英文及混排有实际渲染覆盖。
封面竖幅仅为原生占位外壳，不接受图片输入；字体不嵌入，当前为 production，可参与自动交付选择。
详见 [设计意图与编辑边界](warm-clay/intent.md) 及 [验收摘要](../../benchmarks/visual/cases/warm-clay/golden-workshop/review.md)。

Amber Ledger 提供八类年度报告职责与十六个注册构图，以暖象牙底、炭黑观点、鼠尾草证据、
正体衬线解释及蜂蜜琥珀焦点组织开放版面。常规柱图、点线、环图和表格为原生对象；极小量图、
差异桥、进度为数值派生形状，编辑后须从 content 重建同步。当前为 production，可参与自动交付选择，字体不嵌入。
详见 [设计意图、验证范围与编辑边界](amber-ledger/intent.md)。

Sky Compass 提供十二类运营复盘职责与二十四个注册构图，以白底、天空蓝观点、海军蓝重点、
浅冰蓝解释栏及开放式原生表格组织证据。封面采用开放式罗盘弧线，保留蓝点页眉、短下划线、基准刻线、
流程虚线及日期刻度；原生环图、趋势柱图、表格和数值派生形状支持编辑，独立标签须从 content 重建同步。
当前为 default，可参与自动交付选择，字体不嵌入。详见 [设计与边界](sky-compass/intent.md) 及 [验收记录](../../benchmarks/visual/cases/sky-compass/golden-operations/review.md)。

## Midnight Pulse

Midnight Pulse 提供深黑蓝运营报告、叠层深蓝／深青薄雾、青蓝仪表、开放式衬线诊断表、
差异汇聚、比较、状态治理与路线决策。背景薄雾是原生可编辑路径，不可为通用极简而删除。
当前为 production，可参与自动交付选择；派生形状和独立标签在手工数据编辑后须从 content 重建。
详见 [设计与编辑边界](midnight-pulse/intent.md) 及 [验收摘要](../../benchmarks/visual/cases/midnight-pulse/golden-operations/review.md)。

## core-primitives 职责边界

| 属于 core-primitives（几何安全 + op 生成）             | 不属于 core-primitives（视觉语言）         |
| ------------------------------------------------------ | ------------------------------------------ |
| `nm()`, `assertWithinSlide()`, `grid()`                | 调色板 `C`、具体颜色选择                   |
| `shape()`, `fill()`, `noLine()`, `thinLine()`          | 间距节奏（marginX, gridGap 的具体数值）    |
| `textbox()`, `setText()`, `runFont()`, `tx()`, `box()` | chrome 结构（topBar, footer 的高度/位置）  |
| `withFontFloor()`, `parseFontPt()`, `fontSizeValue()`  | 页型函数（heroSlide, kpiRowSlide 等）      |
| `contrastRatio()`, `readableTextOn()`, `isDarkColor()` | 组件外观（卡片圆角、accent bar 高度）      |
| `icon()`, `addTablerIconPicture()`                     | 具体图标语义选择（哪个 icon 表示某概念）   |
| `cardBox()`, `panelBox()`（结构骨架）                  | 组件内容布局（KPI 圆的位置、编号框的偏移） |
| content schema 校验引擎、fit diagnostics 框架          | 具体页型的 soft/hard limit 数值            |
| `assertWithinSlide` bounds check                       | stylePack/themePack 的选择和解析           |

**判断原则**：如果某段代码换了主题色/间距后仍然正确，它属于 primitives；如果它依赖具体的视觉决策，它属于 DeckKit。

## 校验合同

`validate-content.mjs`、DeckKit build 胶水和 benchmark CLI 调用
`shared/validate-deckkit.mjs` 的 `validateDeckkitContent(content, { deckkit, mode })`。
它先运行 core 的 `validateContent`；只有 catalog 注册了 `designContract` 的套件才增加
合同与语义检查、逐实例的文字容量估计。未迁移套件保持原有行为。直接调用 core 校验
不包含这些额外检查。

`validateContent` 返回：

- `errors`：阻塞性 schema、catalog 或 fit 问题。
- `warnings`：非阻塞 density / fit / catalog 风险。
- `fitDiagnostics`：结构化容量诊断，包含 `slideIndex`、`slideType`、`severity`、`code`、
  `path`、`value`、`limit`、`blocking` 和 `suggestedActions`。
- `normalizedContent`：当前与输入一致，保留给后续规范化。

当前页型级 fit diagnostics 已覆盖 `heroSlide`、`kpiRowSlide`、`multiCardSlide`、
`benchmarkSlide`、`timelineSlide` 和 `askSlide`，并包含长 Latin token 风险检查。

`catalog.json` 可声明以下交付与选型合同：

- `layoutContract`：按 DeckKit / 页型声明必填数据槽位、任一满足槽位组、允许的
  `layoutId`、`customOps` 策略和 `assetSlots`。draft 默认给 warning，delivery 可通过
  `deliverySeverity` 升级为 error。
- `diversityGate`：按页型分组检查长 deck 的版式多样性、必需叙事组和连续重复组上限，
  避免整套 deck 退化成同一种卡片页。触发时的 `fitDiagnostics` 会同时给出
  `usedGroups`、`missingGroups`、`groupMembers` 和 `slideGroups`，因此 Agent 可以直接
  选择替代页型，不必另查 catalog。
- `visualGrammar`：声明 DeckKit 的视觉语言合同，包含定位、气质、布局原则、
  signature elements、字体/色彩节奏、composition rules 和 avoid 清单。它让 Agent 在
  选择 DeckKit 后知道"这套页面应该长什么样"，并在 readiness audit 中阻止缺少风格合同的
  production/default DeckKit 进入交付。

这些 gate 属于 DeckKit 元数据，不属于单个 deck 的临时 patch。设计合同规则放在合同模块，
不要把特定风格下沉到 core。通用入口共享校验；构建和标准 create runner 还会保存设计计划、
检查应用后的对象和原生数值。详见 `../../references/create/design-contracts.md`。

合同路线包括 Consulting Dark、Biennale、Cartesian、Broadside、Long Table、Swiss Grid、McKinsey Blue、Black Gold、Green Slate 与 Clear Value 等风格；完整套件列表以 catalog 为准。Consulting Dark 2.1 保留深蓝首尾与大小不同的圆形装饰，
所有内容页统一深蓝底，以暖白正文、暖铜数字、浅青输出关系和开放台账、比较栏、共享时间轴替换重复切角面板，提供十类职责、二十个注册布局及英文完整示例；支持中文和混排，
原生条形图保留负数、零与极小值，表格逐格回读。字段迁移和编辑同步边界见 `consulting-dark/intent.md`。
Black Gold 增加原生表格逐格回读、单焦点与
期刊图表/表格规则；Green Slate 增加深色策略报告构图、带底色标签、形状内编号、按时长分配的
阶段路线图和独立说明区。Clear Value 增加白底衬线研究报告、多图证据板、可变列矩阵、原生环图、
预测柱虚线边界和面积成比例的可编辑圆。candidate 状态不等于 production/default 交付资格。开发者从设计规范和
参考图迁入新风格时，使用仓库内 deckkit-maker 的 design-source 路线，保持运行时自包含。

`layoutContract.slideTypes.<slideType>.assetSlots` 是页型的图片槽位合同。它是一个以语义
slot id 为键的对象，每项至少说明 `kind`、`acceptsAsset` 和
`placeholderBehavior`，还可以给出 `labelSlot` / `captionSlot` 与 `note`。槽位参考会把
这些信息输出为单独的 Asset slots 表；当 `acceptsAsset` 为 `false` 时，该页型只会渲染
占位框，`content.json` 的 `imageSlots` 不能注入真实图片，校验器会在 delivery 模式阻止
这种误用。`acceptsAsset: true` 的页型通过 `assets_manifest.json` 解析 asset id；build
生成短的 `assetSource.path`，runner 再把 manifest 所在目录作为 `--asset-root` 传给 xdoc。
没有绑定时是否保留占位框由该页型自己的 `placeholderBehavior` 决定。

`visualGrammar` 不是运行时代码，也不替代页型函数、schema、layout contract 或 diversity gate。
它只约束 DeckKit 使用方式和内容创作方向：选中 DeckKit 后，把 `positioning` 用作风格判断，
用 `signatureElements` 和 `compositionRules` 指导页面构成，用 `avoid` 拦截不匹配的视觉选择。
不要因为有 visual grammar 就在 content 里塞 `customOps` 或临时坐标。

## 使用方式

```bash
node <skill-root>/scripts/cli/deckkits/slots.mjs \
  --deckkit consulting-dark \
  > deckkit-slots.md

node <skill-root>/assets/deckkits/validate-content.mjs \
  content.json \
  --deckkit consulting-dark \
  --mode delivery

node <skill-root>/scripts/cli/create/build.mjs \
  --deckkit consulting-dark \
  content.json \
  -o patch.json \
  --quality-json quality.json
```

不要为普通交付手写每次一份的 `build.mjs`。只有在开发或调试 DeckKit 本身时，才临时导入
`.kit.mjs` 调用 `createDeck(content)`。

## 图标使用

DeckKit 需要 Tabler 图标时，使用 `createOps()` 返回的 `icon()` 或直接使用
`shared/icon-assets.kit.mjs`。它通过 skill 内的图标入口读取 `assets/icons/tabler-icons.pack.br`，并把 SVG
内联为 `add-image` 的 `bytesBase64 + mimeType`，不依赖网络、临时 SVG 文件或 Tabler
源码目录：

```js
const p = createOps()
p.addSlide(0, '0B1020')
p.icon(0, 'S0_StatusIcon', 'chart-line', 0.72, 0.72, 0.28, 0.28, {
  color: 'C8583A',
})
```

查找图标时使用 agent 入口，避免把全量 SVG 读入上下文：

```bash
node <skill-root>/scripts/cli/assets/icons.mjs search "analytics dashboard" --style outline --limit 12 --json
node <skill-root>/scripts/cli/assets/icons.mjs get chart-line users presentation --style outline --json
```

图标包覆盖 Tabler `outline` 和 `filled` 全量图标。刷新 pack 与 license 时运行
`node <skill-root>/scripts/cli/assets/icons.mjs generate --source-root <tabler-icons-checkout>` 和
`node <skill-root>/scripts/cli/assets/icons.mjs generate --source-root <tabler-icons-checkout> --check`（也可改用 `TABLER_ICONS_ROOT` 环境变量指定 checkout）。

## 版本规则（semver）

| 修改类型                                                      | 版本  |
| ------------------------------------------------------------- | ----- |
| 修复 DeckKit 逻辑 bug；放宽过严校验（不影响已验证样例）       | patch |
| 新增页型或可选字段；放宽验证（接受更多输入）                  | minor |
| 删除/重命名字段；收紧验证（拒绝原来合法的输入）；改变布局容量 | major |

## 冻结准入

1. `validate-content` 通过，只有可解释的非阻塞 warning
2. `cli/create/build.mjs` 可重复生成稳定 patch 和 `quality.json`
3. DeckKit benchmark 的 repo-indexed cases 全部通过；新 kit 至少要有 golden case，stress /
   mixed-language 可在 `.tmp` 做审查而不入库
4. `node <skill-root>/scripts/cli/deckkits/readiness.mjs --deckkit <id> --target candidate --benchmark-mode required-live` 通过
5. `xdoc pptx apply --dry-run --json` 通过
6. `xdoc pptx vision-check out.pptx --json` 的 high/medium 为 0
7. PNG contact sheet 和逐页检查通过
8. catalog 记录版本、visual grammar、验证命令、示例路径和已知限制

当前 readiness audit 会明确报告 candidate / delivery / default 三个结论。
benchmark CLI 已接入逐页 PNG 与 contact-sheet 机器 gate；新增 DeckKit 只有在人工视觉复核、
catalog 质量字段和已知限制满足晋级要求后，才能提升为 `production` 或 `default`。

## Catalog 质量元数据回写

benchmark 通过后，用 catalog update 工具把机器可证明的结果写回
`assets/deckkits/catalog.json`：

```bash
node <skill-root>/scripts/cli/deckkits/catalog-update.mjs \
  --deckkit consulting-dark \
  --write
```

该命令只更新 `quality.lastBenchmark`、`quality.vision` 和
`quality.benchmark`，默认不改变 `readiness`，也不会把人工 PNG review
结果假定为通过。人工复核完成后，再显式写入 hard defect 数：

```bash
node <skill-root>/scripts/cli/deckkits/catalog-update.mjs \
  --deckkit consulting-dark \
  --manual-hard-defects 0 \
  --write
```

只有逐页 PNG 和 contact sheet 人工检查完成、`manualHardDefects=0`、benchmark
和 vision gate 均通过后，才可以带 `--readiness production` 或
`--readiness default`，且必须同时带 `--confirm-manual-png-review`。否则工具会拒绝
promotion。

## 新增 DeckKit 流程

1. 从已验收的视觉基线提取身份与构图，集中放入 `<id>/design.json`、`intent.md` 和 `<id>.kit.mjs`。
2. 内容数据放入 `<id>/examples/content.json`，开发胶水为同目录 `build.mjs`。
3. 写 `<id>/schemas/<slideType>.schema.json` 和 slot budget；复用注册执行组件与共享校验。
4. 跑验证矩阵（文本长度 × 语言 × 密度 × 主题 × 页数 × 页型组合）
5. 在 `catalog.json` 注册，绑定最新 canonical 逐页审查、benchmark 和 readiness 结论。

`blue-research` 为白底海军蓝研究报告套件，提供 10 种职责、20 种注册构图；保留刊头、
指标椭圆链、蓝阶矩阵、差异桥、数值短条、时间节点、递升阶段与证据结论。当前为 production，
可参与自动交付选择；能力与同步边界见 [intent](blue-research/intent.md)，验收范围见
[benchmark review](../../benchmarks/visual/cases/blue-research/golden-learning/review.md)。
