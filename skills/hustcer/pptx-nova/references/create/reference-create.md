# Reference Create —— 参考 PPTX + 新大纲生成新 deck

当用户给一份 `.pptx` 作为参考，同时给新的大纲、主题或内容，并要求生成一份新的 `.pptx` 时使用。
目标是复用参考 deck 的视觉语言和可复用结构，但输出仍是新文件，源 PPTX 默认只读。

## 1. 先判定用户意图

| 用户意图                          | 路线                                                   |
| --------------------------------- | ------------------------------------------------------ |
| "严格套这个模板/保留原版式改内容" | Template Following，见 `../edit/template-following.md` |
| "按占位符填数据"                  | `template-fill`，见 `../content/data-driven.md`        |
| "风格像这份 PPT，内容按新大纲"    | `extract-style` + 新建 deck                            |
| "结构/版式也参考这份 PPT"         | `inspect` + `reference-map.json`                       |
| "美化/翻新这份 PPT，内容不变"     | Refurbish Existing Deck，见本文件第 6 节               |
| "直接在这份 PPT 上改成新内容"     | Edit 模式，见 `../edit/inspect-and-edit.md`            |
| "这份模板以后反复复用"            | `import-template`，见 `template-library.md`            |

不要把"参考风格生成新文件"误判成 Edit，也不要把"严格套模板"误判成普通 Reference Create：
严格套模板必须走 `../edit/template-following.md`，复制或填充源模板的 inherited objects，不能只重画一份
看起来相似的新 deck。Edit 是修改用户已有 deck；Reference Create 是读取参考 deck 后新建 deck。

## 2. Run 目录产物

除 `../common-workflow.md` 规定的通用产物外，Reference Create 还要把这些文件放在 run 目录：

- `reference-inspect.json`：`inspect` 输出，用来判断页面尺寸、layout、shape、文本密度和复杂对象。
- `reference-style.json`：`extract-style` 输出，包含主题色、字体、layout/slide 语义和 draft pack。
- `reference-map.json`：新大纲每页到参考页型/参考 slide 的映射。
- `review-policy.json`：仅在需要保留已确认的原始 finding 时创建；使用
  `pptx-nova-review-policy/v1`，绑定源 PPTX SHA-256，并从 `layout-final.json` 精确复制 actionable
  finding 的 `code` 与 `reviewIdentity.sha256`，同时记录原因。也可以把同样的 `bindings` /
  `reviewedFindings` 放入 `reference-map.json`；不要同时使用两个 policy 来源。
- `content-audit.json`：Refurbish Existing Deck 时逐页对账文本、表格、chart、SmartArt、图片/媒体、
  shape/group 和 notes 的保留状态。
- `content-audit-final.json`：Refurbish Existing Deck 时由 `xdoc pptx refurbish-audit`
  生成的最终内容保真门禁报告；用于交付前证明页数、文本、shape type、媒体、备注和外链未经批准减少。
- `vision-diff.json`：Refurbish Existing Deck 时由 `xdoc pptx vision-diff` 生成的 source/candidate
  视觉问题 delta 报告。
- `pptx-diff.json`：Refurbish Existing Deck 或需要 before/after 审计时由 `xdoc pptx diff`
  生成的 `pptx-diff/v1` 语义变更报告，用可靠变更核对源/候选的文本、几何、样式和对象摘要。
- `fidelity-gate.json`：Refurbish Existing Deck 时由 `cli/review/fidelity-gate.mjs`
  汇总 `vision-diff`、最终 `refurbish-audit` 和可用 `reference-map` 的保真门禁报告。
- `candidate-inspect.json` / `layout-final.json`：Refurbish Existing Deck 时对候选 PPTX
  做最终 inspect，并由 `cli/review/layout-snapshot.mjs` 生成对象 bbox、文本、字体、颜色、
  placeholder、frame 和 z-order 的结构化布局证据。
- `catalog-readiness.json`：每次 refurbish runner 都会持久化的 DeckKit catalog readiness
  与 benchmark 摘要；如显式请求 live benchmark readiness，则另存为 `delivery-readiness.json`。
- `contact-diff.png` / `contact-diff.json`：Refurbish Existing Deck 时由 `xdoc pptx contact-diff`
  生成的 source/candidate 并排 contact sheet 和状态报告。
- `refurbish-compare.png` / `refurbish-compare.json`：Refurbish Existing Deck 时由
  `xdoc pptx contact-diff --dpi 192` 生成的全量翻新前/后并排对比图和报告。
- `refurbish-compare-gate.json`：Refurbish Existing Deck 时由
  `<skill-root>/scripts/cli/review/compare-gate.mjs --kind refurbish --publish` 生成的同目录发布门禁报告；必须证明
  `status=pass`、`finalBinding.status=bound`，且最终 PPTX 与
  `<output-stem>-refurbish-compare-<MMDDhhmmss>.png` 已作为同一交付 bundle 发布。
- `chrome-detect.json` / `chrome-remove.json` / `chrome-apply.json`：Refurbish Existing Deck
  时由原生 chrome 命令生成的旧 chrome 识别、移除和目标 DeckKit chrome 应用报告。
- `remap-dry-run.json` / `remap-theme.json`：Refurbish Existing Deck 时由 `remap-theme`
  生成的对象级换肤预览和实际执行报告，重点检查 changed/skipped/unsupported/preserved。
- `outline.json`：用户大纲或标准化后的新大纲；用户已给大纲时直接采用。
- `template_fusion.json`：仅在多来源冲突、用户 override 或需要审计时记录完整段级融合结果。
- `deck_lock.json`：锁定参考 deck 可复用的风格/结构、模板融合、输出路径和每页页型/节奏。
- `assets_manifest.json`：仅在有被允许复用或新生成的 logo、图片、图标、数据截图等资源时创建。

## 3. 标准流程

```bash
xdoc pptx inspect reference.pptx --json > reference-inspect.json
xdoc pptx extract-style reference.pptx --output reference-style.json --json
```

然后创建 `reference-map.json`，最小结构如下：

```json
{
  "source": "reference.pptx",
  "strategy": "style-and-layout",
  "slides": [
    {
      "outlineIndex": 0,
      "outlineKind": "title",
      "referenceSlide": 0,
      "reuse": "style",
      "notes": "Use cover typography and chrome; create new text/content."
    }
  ]
}
```

`reuse` 建议值：

- `style`：只复用色彩、字体、chrome、密度，不复制整页。
- `layout`：复用版式结构和对象关系，用新内容重建。
- `copy-slide`：用 `slide-copy` 复制整页骨架后替换内容；只在参考页结构很难重建、且不是严格模板跟随
  的普通 Reference Create 中使用。严格模板跟随改走 `../edit/template-following.md`。
- `template`：已有占位符模板，改走 `template-fill`。

如果用户同时给了精确 brand/layout/deck catalog id 或显式模板路径，先按
`template-library.md` 的段级融合规则写入 `deck_lock.json.templateFusion`：

- brand 只覆盖 identity（颜色、字体、logo、图标风格、品牌口径）。
- layout 只覆盖 structure（画布、网格、页型结构、密度和 page rhythm）。
- deck 作为完整起点；显式 brand/layout 可分别覆盖它的 identity/structure。

融合结果进入 `deck_lock.json.templateFusion`。参考 PPTX 自身也是一个输入源，但它默认只提供
style/layout evidence；除非用户明确允许复用素材，不把参考 deck 的旧图片、logo 或图标复制进新文件。

生成路径：

1. 根据 `reference-style.json` 选择已有 theme/style，或临时使用抽取出的 draft pack。
2. 写 `deck_lock.json`：记录参考来源、template fusion、DeckKit/theme/style、每页
   `referenceSlide` / `reuse` / `slideType` / `rhythm` / `layoutIntent` /
   `visualDensity`，以及所有假设。
3. 只有允许复用或必须补齐图片/logo/图标/数据截图时才写 `assets_manifest.json`；未授权参考素材标为
   `needs-review` / `needs-user` / `forbidden`，不要在 patch 中偷偷引用。无外部资源时不要创建空 manifest。
4. 根据 `reference-map.json` 和 `deck_lock.json` 把 `outline.json` 转为 `content.json`
   或 generator 输入。
5. 优先用 DeckKit / generator 新建页面；只有 `reuse: copy-slide` 时才用 `slide-copy`。
6. 生成 patch 后跑
   `node <skill-root>/scripts/cli/create/check-lock.mjs --lock deck_lock.json --content content.json --patch patch.json --json`；
   有 `assets_manifest.json` 时加 `--assets assets_manifest.json`。
7. 跑 dry-run，确认 selector、layout 和 visualRisks。
8. apply 到 run 目录中间 `.pptx`。
9. 跑 `vision-check`，创建型 deck 的 high/medium 必须清零。
10. 对最终 PPTX 保存 `final-inspect.json`，运行
    `<skill-root>/scripts/cli/review/finalize-evidence.mjs --mode reference-create`，生成
    `layout-final.json` 和 `evidence-summary.json`。
11. 转 PNG/contact sheet，逐页检查参考风格是否一致、文字是否溢出、页面是否像新内容而不是旧页残留。

## 4. 复制整页时的规则

`slide-copy` 适合保留复杂整页结构：

```bash
xdoc pptx slide-copy -i target.pptx --source reference.pptx \
  --slides 1,3,5-8 --output out.pptx --dry-run --json > dry-run.json
xdoc pptx slide-copy -i target.pptx --source reference.pptx \
  --slides 1,3,5-8 --output out.pptx --json > slide-copy.json
```

`--slides` 是 1-based selector；省略所有 selector 时复制 source 第一页；`--all`
复制 source 全部页。两者互斥。需要多页时必须优先
一次事务复制，避免逐页调用、重复打开/序列化和中间候选分叉。`pptx-slide-copy/v1` 会返回
每页 `copied[]`、聚合 `dependencyMappings[]` / `changedParts[]`，以及只读 `preflight`。
执行前必须确认 `status: "success"` 且 `outcome: "passed"`、target/donor 指纹仍匹配、`blockers[]` 为空，并人工处理
`risks[]`；结构 Edit Contract 直接消费该报告，不伪造 patch `opResults[]`。

复制后必须立刻用 patch 替换旧文本、图表数据、表格数据和图片；不要交付带有参考 deck 旧内容的页面。
如果只是学习风格，不要整页复制，因为这会把旧内容、旧媒体和潜在授权风险一起带进新 deck。
复制后也不能用 overlay 遮住旧内容来伪装替换；必须改写、替换或删除 inherited 对象本身。
如果复制页中有空 title/body/date/footer/slide-number placeholder，必须显式填充或删除。

## 5. 质量和边界

- 用户给的新大纲是内容真源；参考 deck 是视觉和结构输入。不要为了贴近参考 deck 改写用户核心观点。
- `extract-style` 当前不会全量细抽 card radius、shadow、chart-specific style；这些需要用
  `inspect`、PNG 观察、generator token 和显式 patch ops 补齐。
- 如果参考 deck 含 logo、照片、插画、产品截图、客户 mark、App icon 或第三方图标，只有用户明确允许复用
  或来源可验证时才复制素材；否则抽象成布局和风格，不复制资产，不生成伪官方替代物。允许复用的素材必须
  登记到 `assets_manifest.json`。
- 如果参考 deck 有动画、转场、SmartArt、复杂 chartEx，`inspect` 发现后在摘要中说明保真风险；
  必要时改用普通可编辑 shape/table/chart 重建。
- 完成摘要必须列出参考 deck 路径、`reference-style.json`、`reference-map.json`、
  `template_fusion.json`（如有）、`deck_lock.json`、`assets_manifest.json`（如有）、最终 PPTX 路径、
  check-lock、vision-check、`evidence-summary.json`、`layout-final.json` 和 PNG 复核结果。

## 6. Refurbish Existing Deck —— 保持内容的已有 deck 翻新

当用户要求"美化/翻新/重写这份 PPTX"并明确说"保持内容不变"时，源 PPTX 是内容真源，
目标是输出一个新的、可编辑的、更高质量 deck。默认路线是先复制或保留源 slide/object，再
安全换成目标 DeckKit 视觉系统；不要把这个场景等同于普通 Edit，也不要把它默认理解成
从零重建。普通 Edit 是在原结构上改少量对象；Refurbish 是在内容保真前提下做系统性换肤、
清旧 chrome、批量 remap 和必要的局部版式重排。

### 视觉目标硬定义

"保持内容不变"不等于"视觉上尽量不动"。当用户说美化、翻新、换风格、按某个 DeckKit
完成时，交付物必须在 contact sheet 上明显区别于源稿：页面网格、标题层级、内容重排、
留白、规则线、色彩节奏和证明对象摆放都应体现新风格。只做这些事情不算完成翻新：

翻新换肤的目标是"源内容不变 + 目标 DeckKit 风格一致"。目标 DeckKit 的 palette、字体层级、
header/footer、页码、背景、规则线、图标语言、表格/图表外观和 page chrome 都是视觉合同。
可以复制原 slide 或原对象作为保真起点，但复制后必须编辑对象本身并重新主题化，而不是把源页
截图化、overlay 化，或保留原 deck 的色系、页眉、页脚和 chrome。`deck_lock.visualTarget`
应记录目标 DeckKit 的 palette/chrome/typography 规则；`content-audit.json` 可把这类处理记录为
`preserved object + restyled` 的说明，但状态仍应落在 `preserved` 或 `rebuilt-editable` 等合法枚举。

- 在源页上加页码、kicker、细红线、淡背景或轻量边框。
- 保留原版式和原对象位置，只微调颜色或字体。
- 用源 slide 渲染截图、整页图片或大面积透明 overlay 掩盖旧版式。
- 为了保真把绝大多数页退回源稿样貌，却声称通过了检查。

如果用户先要求预览前几页并认可其中某一版，全量输出必须把该预览版写入
`deck_lock.visualTarget`，并以它作为视觉合同。后续全量生成前，先打开预览 contact sheet
和源 contact sheet，明确记录哪些视觉特征要扩展到全 deck。不能因为遇到表格、chart 或
SmartArt 保真要求，就退回"源页 + chrome"的保守方案；正确策略是"对象保留 + 页面重排"。

### 内容不变的硬定义

除非用户明确允许，"内容不变"默认包含：

- 所有可见文本、标题、副标题、脚注、页码、备注和 speaker notes。
- 表格的行列、单元格文本、合并关系、数据含义和表头层级。
- chart 的图表类型、系列、类目、数值、标签、legend、轴含义和标题。
- SmartArt / diagram / 流程图 / 组织结构图的节点文本、层级、连线关系和顺序。
- 图片、logo、图标、截图、媒体、OLE、公式、形状组合和其它用户可见对象的语义存在。
- 每页的内容归属关系：源 slide N 的内容必须能在输出中被明确追溯到相同 slide，或用户确认过的拆分/合并 slide。

禁止把"保持内容"降级理解为"只保留可见文本"，也禁止把源 slide 渲染 PNG 当作内容保真捷径。
如果 DeckKit、xdoc 或当前工具链不能保真复制某类对象，默认处理是阻塞并说明能力缺口；优先选项只能是
复制原对象、用可编辑 shape/table/chart/picture 重建、或调整页型后重建。只有用户明确批准降低可编辑性时，
才可讨论截图保留、只保留文本或放弃该翻新。不能静默丢弃 chart、SmartArt、shape、图片、媒体或备注，
也不能用 `deck_lock.assumptions[]` 把未经确认的内容损失合理化。

目标 DeckKit 只是视觉和组件工具，不是内容裁剪器。如果现有页型、slot 数量、表格/图表组件或密度预算
无法完整承载源 slide 的内容，必须先扩展目标 DeckKit 的页型、组件或 slot contract，再重新生成；
不能为了塞进现有页型而改写标题、删减 bullet、合并表格列、丢弃图片/连接线/备注、降低对象可编辑性，
或把源页内容改成摘要。扩展 DeckKit 是翻新流程的正常步骤，不是最后手段。

必做步骤：

标准路线优先使用一键 runner；它会把下述 plan、inspect、native/fallback、dry-run/apply、
vision-diff、refurbish-audit、semantic diff、preview、`refurbish-compare` 和同目录发布门禁阶段写入同一个 run 目录：

```bash
node <skill-root>/scripts/cli/refurbish/run.mjs \
  --deckkit <id> \
  --source source.pptx \
  --output candidate.pptx \
  --json
```

机器门禁通过后 runner 返回 `status: "needs-human-review"`，而不是伪造视觉复核通过。runner
会在最终 PPTX 发布后生成 `refurbish-compare.png`，并把同一张 PNG 复制到最终 PPTX 同目录，
命名为 `<output-stem>-refurbish-compare-<MMDDhhmmss>.png`。
下面的分步命令仍是 runner 的行为合同，也是局部修复和故障排查入口。

1. 先生成 `refurbish-plan.json`，再执行任何 `xdoc` 换肤命令：

```bash
node <skill-root>/scripts/cli/refurbish/plan.mjs \
  --deckkit <id> \
  --source source.pptx \
  --output candidate.pptx \
  --json > refurbish-plan.json
```

如果用户显式指定 experimental/candidate DeckKit，加 `--explicit`。`status: blocked`
时停止并说明缺口；`status: explicit-only`、`manual-fallback` 或
`explicit-manual-fallback` 时继续但必须逐项执行 `requiredGates[]`。`manual-fallback`
不是自由发挥路线：先用 `cli/refurbish/fallback-patch.mjs` 从 inspect 和 catalog
生成可审计 patch，再 dry-run/apply。

2. 同时生成 `reference-inspect.json`、`source_extract.md`（或等价文本提取）和源 deck PNG/contact sheet。
3. 以 `reference-inspect.json.presentation.slideCount` 和 `slides[]` 作为源页清单权威。
   Markdown/文本提取可能漏掉无文本页、SmartArt-only 页、纯图页或 preserve-only 页；必须对账并在
   `content-audit.json` 中标出补齐方式。
4. 建立 `content-audit.json`，逐页记录 `text`、`tables`、`charts`、`smartArtOrDiagrams`、
   `imagesAndMedia`、`groupsAndShapes`、`notes`、`unsupportedObjects` 的数量、摘要、输出处理方式和状态。
   每项状态只能是 `preserved`、`rebuilt-editable`、`user-approved-raster`、`user-approved-drop` 或 `blocked`。
   skin-first 中大多数复杂对象应先标为 `preserved`，后续通过 `remap-theme` 和局部 patch 改视觉；
   默认交付不得存在 `blocked`，也不得出现未经用户确认的 `user-approved-raster` / `user-approved-drop`。
   `user-approved-raster` 只能用于用户明确批准的降级；不能由 Agent 为了省事自行选择。
5. 写 `reference-map.json`，记录每个源 slide 映射到哪些输出 slide。默认 `1:1` 保持页数；
   任何 `1:N` 拆页、`N:1` 合页、重排序或 appendix 化都必须先让用户确认，并写入 `approvedChanges[]`。
   不要为了保持原页数而让文字小到不可读或触发 text overflow；但也不能擅自改变页数。
   `approvedChanges[]` 描述真实内容/结构变化，不能用于忽略诊断。如果源 deck 有意保留空 placeholder，
   应保持该对象不变，并写 hash-bound reviewed finding；不得删除对象来消除 layout warning，也不得使用
   `allowEmptyPlaceholder` 或全局 ignore。

   `layout-final.json.risks[]` 中每个 actionable finding 都带稳定的 `reviewIdentity.sha256`。
   最小 reviewed finding 结构如下，可作为独立 `review-policy.json`，也可把 `bindings` 和
   `reviewedFindings` 嵌入 `reference-map.json`：

```json
{
  "schemaVersion": "pptx-nova-review-policy/v1",
  "bindings": {
    "sourceSha256": "<64-hex-source-sha256>"
  },
  "reviewedFindings": [
    {
      "id": "slide-8-intentional-empty-sldnum",
      "code": "empty-placeholder",
      "disposition": "accepted",
      "findingSha256": "<layout-final-risk-review-identity-sha256>",
      "reason": "该页用于验证 viewer 未自动填充页码占位符的行为"
    }
  ]
}
```

`findingSha256` 绑定 finding 的语义证据，不绑定提示文案或 severity；证据变化会使规则失配并
fail closed。已有 `empty-placeholder` policy 的 `target` + `expected.textEmpty=true` 精确匹配格式
仍兼容，但新规则应使用 fingerprint 模式，且任意 policy 都不得匹配 informational finding。

6. 复制源 deck 到 run 目录作为 skin-first 工作文件；输入 deck 保持只读。默认先运行一等编排命令：

```bash
xdoc pptx refurbish-skin \
  --source source.pptx \
  --deckkit mckinsey-blue \
  --output candidate.pptx \
  --json > refurbish-skin.json
```

`refurbish-skin` 会复制保留源 deck，检测/删除高置信旧 chrome，应用 DeckKit 背景和 page chrome，
对 text/shapes/tables/charts 做批量 remap，并运行 `vision-diff` 与原生 `refurbish-audit` gate。
读取 `refurbish-skin.json`：`status` 必须为 `success` 且 `outcome` 为 `passed`，`gate.passed` 必须为 `true`，且
`gate.newHighIssues` / `gate.newMediumIssues` 必须为 0。`artifacts.contactDiff.status` 默认为
`skipped`；标准 runner 最终会生成完整 `refurbish-compare`，不要为全量人工复核额外运行一次
`xdoc pptx contact-diff`。只有局部修复预览才单独使用带 `--slides` 的 contact-diff。

如果 `refurbish-skin` 返回 `unsupported_complexity` 错误码，不要重试同一条命令，也不要让用户等待长流程；
改用下方低层命令对 deck 分段处理，或先做 inspect/audit 后向用户说明当前 MVP 的大 deck 限制。
如果返回 unsupported DeckKit/native skinning 错误，记录 JSON，并改用目标 DeckKit 对应的 brand profile
或 inspect 驱动 patch；不得静默切换到其它 DeckKit。若 `refurbish-plan.json` 已返回
`manual-fallback` / `explicit-manual-fallback`，不要先试 `refurbish-skin`，直接运行：

```bash
xdoc pptx chrome-detect source.pptx --json > chrome-detect.json

node <skill-root>/scripts/cli/refurbish/fallback-patch.mjs \
  --deckkit <id> \
  --source source.pptx \
  --inspect reference-inspect.json \
  --chrome-detect chrome-detect.json \
  --output candidate.pptx \
  --patch patch.json \
  --lock deck_lock.json \
  --audit content-audit.json \
  --map reference-map.json \
  --json > fallback-patch-report.json

xdoc pptx apply -p patch.json -i source.pptx -o candidate.pptx --overwrite --dry-run --json > dry-run.json
xdoc pptx apply -p patch.json -i source.pptx -o candidate.pptx --overwrite --json > apply.json
```

该脚本优先读取 `refurbishProfile.fallback`；若 DeckKit 没有专用 fallback，则从
`visualGrammar.colorSystem` / `visualGrammar.typography` 合成通用 palette、字体和对象保留策略。
这条路线服务所有 DeckKit，不能在脚本里对单个 DeckKit id 做硬编码特判。`content-audit.json`
是 apply 前的保留基线和操作计划，最终交付仍必须由 `content-audit-final.json` 证明。

只有需要定制删除策略或排查中间报告时，才先判断 `chrome-remove`
是否会误删真实内容：feature-test deck、模板验收页、页脚/页码/日期能力演示页、placeholder
验证页、或任何把 header/footer/page number/rule 当作内容展示的 slide，不能机械执行
`chrome-remove`。这类 deck 应跳过删除旧 chrome，直接从源 deck 或源 deck 的 `apply-brand`
副本开始，用 inspect 驱动的批量 patch 重设背景、fill、line、字体和目标 DeckKit chrome。
手工 fallback 命令链如下：

```bash
xdoc pptx chrome-detect source.pptx --json > chrome-detect.json
xdoc pptx chrome-remove source.pptx --roles header,footer,page-number,rule --output 01-clean.pptx --json > chrome-remove.json
xdoc pptx remap-theme 01-clean.pptx --theme corporate-blue --scope text,shapes,tables,charts --output 02-remapped.pptx --dry-run --json > remap-dry-run.json
xdoc pptx remap-theme 01-clean.pptx --theme corporate-blue --scope text,shapes,tables,charts --output 02-remapped.pptx --json > remap-theme.json
xdoc pptx chrome-apply 02-remapped.pptx --deckkit mckinsey-blue --output 03-styled.pptx --json > chrome-apply.json
```

`remap-theme` 当前使用 `--theme <themePack id>`（不接受 stylePack id，也没有 `--style`）；用目标
DeckKit 对应的 themePack alias（例如 `corporate-blue`）替代示例值。始终显式传
`--scope text,shapes,tables,charts`，因为默认 scope 只覆盖 `text,shapes`。不要假设所有 DeckKit id 都能传给 `chrome-apply`：
先运行命令并读取 JSON 报告。若报告 `unknown DeckKit`、目标 DeckKit 是 `candidate` 但用户显式指定，
或缺少匹配 theme/style alias，必须记录限制并 fallback 到 `apply-brand` + patch 实现目标视觉合同；
不要静默改用其它 DeckKit 或只做轻量 chrome。

Fallback 的最小可交付动作是硬规则：

- `refurbish-plan.json` 必须说明 route、native skinning、fallback strategy、duplicate chrome policy
  和 `requiredGates[]`；不要边试命令边决定路线。
- `fallback-patch-report.json` 必须说明 fallback 来源、chrome-detect 状态、slide count 和 patch op 数；生成的
  `deck_lock.json`、`content-audit.json`、`reference-map.json` 必须与当前候选同步。
- 必须保存 `chrome-detect.json`。对已有 header/footer/page/rule，逐类选择
  `replace`、`restyle-existing`、`skip-duplicate` 或 `add`，并在报告或 patch 备注中体现；发现重复
  chrome 时优先移除新增重复项或复用源对象，不能只移动到别处。
- 主题/字体/颜色 fallback 必须用目标 DeckKit 的 theme/style/profile 驱动。整 text frame
  换字体、字号、颜色时用 `set-text-frame`（字体字段放 `font` 对象）；只有 inspect 或 smoke test
  证明段落/run 索引存在时才使用 `set-run`。
- 必须有 dry-run/apply、`vision-diff.json`、`fidelity-gate.json`、PNG/contact-sheet
  复核和最终 `refurbish-audit`/supplemental audit。缺任一项就不能交付。
- fallback 输出必须能在 PNG/contact sheet 上看出目标 DeckKit 的 palette、typography、background、
  rules、page number chrome 和空间节奏；只改几条线、页码或局部字体不算完成。

7. 如果走 fallback，读取 `chrome-detect.json`、`chrome-remove.json`、`remap-dry-run.json` 和 `chrome-apply.json`。
   `remap-theme` 的 `opResults[].analysis` 会给出 visited/changed/skipped/unsupported/preserved
   统计和对象级原因；跳过项可能是合理语义保留，也可能是旧风格残留，必须在
   `content-audit.json` 或修复 patch 中处理。如果走 `apply-brand` + patch fallback，仍要保存
   brand profile、生成 patch、dry-run/apply 报告和 inspect 色彩统计，证明它确实实现了目标
   DeckKit 的 palette、typography、background、rules 和 page number chrome。

8. 对复制或保留的 chart、table、shape、icon、SmartArt 和图片对象，尽量把 fill、line、text、
   gridline、label 和 accent colors 映射到目标 DeckKit palette，并统一目标字体层级、header/footer
   和页级 chrome。`remap-theme` 已覆盖 text、普通 shape、table 和 chart 的 MVP；SmartArt/diagram
   仍按 preserve/report-only 思路处理。只有当原颜色本身承载内容语义（例如风险红、品牌色、图例颜色、
   截图真实像素）时才保留，并在 `content-audit.json` 或 `deck_lock.assumptions[]` 中记录理由。
   不得留下大面积原主题色导致输出与目标 DeckKit 风格割裂。新增 page chrome 后必须运行
   `vision-diff` 并修掉由本轮新增页码、规则线、背景色、文字颜色造成的 high/medium；常见问题是
   页码贴边、页码压住源底部标签、深色按钮文字仍保持旧 hyperlink 颜色、以及浅黄背景降低链接对比度。

9. 对换肤后仍显得拥挤、旧版式痕迹重、标题层级混乱或目标风格不足的页面，做 selective layout polish：
   用 patch 调整可编辑对象位置、尺寸、标题区、说明层级、留白和背景，不要先进入全页重建。
   源 slide 含原生 styled table、chart 或富样式图形时，优先复制/保留源对象本身；不要为了套
   DeckKit 表格/卡片页型而把源原生表格降级成视觉表格或纯文本重画。确实需要重建时，必须在
   `content-audit.json` 中把该项标为 `rebuilt-editable`，并逐项验证样式等价。
10. 只有以下情况才切到 DeckKit rebuild fallback：源页本身不可读，skin-first 后仍无法达到目标风格，
    用户明确要求重排/拆页/合页，或 xdoc 无法安全复制/保留对象且用户同意可编辑重建。fallback 前按
    DeckKit slot budget 粗分块；若目标 DeckKit 没有匹配源页内容结构的页型，先扩展 DeckKit（新增
    可复用页型、组件、slot schema 和 catalog/layout contract），再写 `content.json` 或 `patch.json`。
    不得先把源内容裁剪成现有页型能容纳的形状。
11. `deck_lock.assumptions[]` 只能披露事实性不确定性和用户已接受的 tradeoff；不能记录未经确认的内容损失。
    如果图片、图表、SmartArt、媒体、备注或复杂对象不能复制或可编辑重建，状态必须是 `blocked`，先询问用户。
12. 生成全量候选后使用标准 runner 的最终 `refurbish-compare` 做视觉差异复核；局部修复阶段才按需
    运行带 `--slides` 的 contact-diff。必要时再对照已认可预览 contact sheet。若候选的多数页面不像已认可预览方向，或用户一眼会觉得"基本没变"，
    回到 chrome/remap/layout polish 或 DeckKit 页型映射重做，不能只解释为"保真优先"。
    最终交付前还必须生成全量逐页 `refurbish-compare.png`：源稿在左、最终交付稿在右，
    默认 192dpi，不能用局部 `--slides` 版本替代交付证据。
13. 生成后必须刷新 `outline.json`、`reference-map.json`、`content-audit.json`，确保它们反映最终输出页数，
    不能停留在第一次生成的旧映射。
14. 候选 PPTX apply、inspect 和 PNG 复核后，运行原生最终 refurbish audit；默认不得有 `error`：

```bash
xdoc pptx refurbish-audit \
  --source source.pptx \
  --final candidate.pptx \
  --map reference-map.json \
  --json > content-audit-final.json

xdoc pptx inspect candidate.pptx --json > candidate-inspect.json

node <skill-root>/scripts/cli/review/layout-snapshot.mjs \
  --inspect candidate-inspect.json \
  --output layout-final.json \
  --json

node <skill-root>/scripts/cli/review/fidelity-gate.mjs \
  --mode refurbish \
  --source-inspect reference-inspect.json \
  --source-pptx source.pptx \
  --candidate-pptx candidate.pptx \
  --reference-map reference-map.json \
  --content-audit content-audit.json \
  --final-audit content-audit-final.json \
  --vision-diff vision-diff.json \
  --layout-snapshot layout-final.json \
  --json > fidelity-gate.json

xdoc pptx contact-diff \
  --source source.pptx \
  --candidate <run-dir>/candidate.pptx \
  --output <run-dir>/refurbish-compare.png \
  --dpi 192 \
  --json > <run-dir>/refurbish-compare.json

node <skill-root>/scripts/cli/review/compare-gate.mjs \
  --run-dir <run-dir> \
  --final-pptx final-output.pptx \
  --final-pptx-source <run-dir>/candidate.pptx \
  --kind refurbish \
  --publish \
  --overwrite \
  --json > <run-dir>/refurbish-compare-gate.json
```

如果 reviewed findings 位于独立 `review-policy.json`，给 fidelity gate 和标准 refurbish runner
增加 `--review-policy review-policy.json`；如果它们已嵌入 `reference-map.json`，不要重复传入独立 policy。

如果没有拆页、合页或重排，可用 `--assume-one-to-one` 省略 `--map`，但仍必须在
`reference-map.json` 或最终摘要中说明采用默认 1:1 映射。

如果任务还需要检查 OOXML 可见文本泄漏，或需要禁止某类遗留 shape name，可额外运行 legacy supplemental audit：

```bash
node <skill-root>/scripts/cli/refurbish/audit.mjs \
  --source-pptx source.pptx \
  --final-pptx candidate.pptx \
  --source-inspect reference-inspect.json \
  --final-inspect candidate-inspect.json \
  --reference-map reference-map.json \
  --forbidden-shape-name-regex '<pattern>' \
  --output content-audit-legacy.json \
  --json
```

该脚本只是原生命令尚未覆盖检查的补充，不再是默认 gate；它只使用 Node 内置模块，并通过系统
`unzip` 读取 PPTX XML，不要为 skill 用户路径引入额外 npm 依赖。

翻新 run 的实操 guardrail：

- 对源 deck 和候选运行 `xdoc pptx vision-diff --source source.pptx --candidate candidate.pptx --json`
  并保存为 `vision-diff.json`。已有源稿问题要和新增问题分开记录；候选不得新增 high severity，
  新增 medium 必须能用 PNG/contact sheet 解释并尽量修掉。
- 候选稳定后运行一次 `xdoc pptx diff --source source.pptx --candidate candidate.pptx --detail summary --json`
  并保存为 `pptx-diff.json`。不要在每次 skin/remap 局部尝试后重复运行；只有 `summary` 指向可疑页或需要
  字段级证据时才追加 `--detail full`。用 `agentGate.semanticStatus`、`summary.reliableChanges`、
  `summary.byCategory`、`styleChangeSummary` 和 `slides[]` 检查可靠变更是否符合预期：翻新通常会有可靠的几何/样式变化，
  但不应出现未经批准的文本删除、slide 删除或对象类别大幅减少。`uncertainChanges` /
  `unsupportedRegions` 只表示需要人工、`refurbish-audit` 或专项审计补证，不能当作通过。
- 不要通过把旧 header、footer、页码或标题移到画布外来隐藏它们；这会制造 `shape-out-of-bounds`
  并污染后续自动修复。优先把已经镜像到新 header 的旧标题文本设为空，或在原位置把旧装饰 fill/line
  改成目标背景色并保留在画布内。
- 不要把编号、quote、URL、template 文案、diagram 节点或 proof label 误判为可丢弃 chrome。
  任何被清空的源文本都必须已经以等价可见文本重建；否则最终 refurbish audit 应视为阻塞。
- 不要跨一组 slide 硬编码 shape id。很多导入 deck 在中段会换 layout 或对象顺序；优先用
  `xdoc pptx chrome-detect` 的 role/confidence/evidence 识别旧 header/footer/page number/rule，
  再用 `name`、`textPreview`、bbox、fill/line、pageType 和 contact sheet 做人工复核。无法确认
  是 chrome 的对象不要删除。
- 异构 deck 中的导入模板页、整页 quote/cover、mismatched-canvas 页面和复杂图示页，不应机械套用普通
  header/rule。`chrome-apply` 后要检查目标 chrome 是否压住源内容；必要时按页删除或移动目标 chrome，
  或扩展 DeckKit 页型。
- 对 xdoc op 或 selector schema 不确定时，先用 `xdoc schema --mode ops --ops <op>` 和一页最小 dry-run smoke
  验证。若主题级 op 在当前版本不稳定，优先对新增 textbox 使用显式 `set-run` 字体和颜色。

对象保留但版式重排的推荐策略：

- 表格、chart、SmartArt、媒体等复杂对象优先保留为原生对象；围绕它们重做标题区、网格、留白和说明层级。
- 图片页可以保留源图片对象，但应按新 DeckKit 的网格位置重新摆放，而不是保留原图坐标。
- 对 feature-test、组件验收、产品截图走查这类 proof object 本身就是内容的页面，保真不等于铺满画布。
  保留源对象语义后，按目标网格把图片、圆角 shape、pattern tile、clip 示例等居中缩进到单元格内部；
  通常应给对象四周留下 15-25% 的单元内呼吸空间，并确保标签与对象之间有稳定间距。若 contact sheet
  里一页显得"太满"，优先批量审计同类页面的大图、圆角矩形、图案填充和裁剪示例，而不是只修单页。
- 装饰性 registration rule、底部横线、空 footer line 只有在它们锚定了真实内容、来源或分组语义时才保留。
  如果横线下方或旁边没有内容，删除该 rule；不要为了维持 DeckKit chrome 而留下无意义的空线。
- 图示页若源对象可编辑且语义简单，可用 DeckKit 原生 shape 重建；若复杂对象不能等价重建，应保留源对象并显著调整页面框架。
- 复制原 slide 后，不要把它当成最终页；先移除或替换原 header/footer、页码、母版残留、背景和旧品牌
  chrome，再套目标 DeckKit 的 page chrome、色系和字体层级。
- 对 feature-test、组件验收、产品截图走查这类“视觉效果本身就是内容”的 deck，也必须逐元素重建为
  可编辑对象：图片使用源图片对象或重新插入图片并设置可编辑 crop/line/effect；连接线用 connector；
  图案、形状、裁剪、文本和表格用原生 shape/table/text 重建。源页 PNG/contact sheet 只能作为视觉对照，
  不能嵌入输出页。若当前 patch 层不能逐对象表达 filter、clip、line、transition、hyperlink tooltip 等属性，
  该项标为 `blocked`，不要用“源页视觉证据面板 + 可编辑语义卡片”冒充内容保留。
- 如果当前 xdoc patch 缺少单对象复制能力，可在 run 目录中用包级 XML 方式作为保真逃生口，但必须重新 inspect
  输出，确认 `shapeType`、table/chart 数量和对象名称符合 `content-audit.json`，并在最终摘要列为风险/技术债。

DeckKit 选择注意事项：

- 如果用户显式指定某个 DeckKit，即使该 DeckKit 不是 delivery-ready，也可以继续，但必须在
  `deck_lock.assumptions[]` 和最终摘要中记录 readiness 例外，并用 `vision-check` 与 PNG 复核补足风险。
- 若指定 DeckKit 缺少适合源内容的页型，不要硬塞到表格/菜单/卡片槽位。优先判断是否需要扩展 DeckKit；
  只有用户确认可拆页时才拆页，且拆页不能改变内容归属或遗漏任何对象。若仍不稳，应扩展 DeckKit 增加
  dense-text / ledger / comparison / diagram / media-grid / object-preserve 等可复用页型，再重新生成。
  不能把“DeckKit 没有合适页型”当作删减、摘要化或降低保真的理由。
- 图片、图表、SmartArt 和复杂媒体属于内容资产。若用户要求内容完全不变，优先复用源对象或重建等价
  可编辑对象；不能复制或重建时必须阻塞确认。不要默认只保留可见文本、源页标记或 preserve-only 说明，
  也不要生成伪截图、源页截图或 overlay。对第三方品牌/授权不明资产，先在 `assets_manifest.json` 标风险并请求确认。
- 对表格页尤其要区分 "DeckKit table look" 和 "source table fidelity"。如果用户强调表格内容和样式不变，
  DeckKit 只能提供页级网格、标题、规则线或背景，不能替换源表格对象。
- 翻新类 DeckKit 若需要新增 evidence / gallery / table / feature 页型，不能只改 `.kit.mjs`：
  同步更新 `catalog.json` 的 `coverage.slideTypes`、`supportedSlideTypes`、`visualGrammar.slideRhythm`、
  `layoutContract.slideTypes`、`diversityGate.groups`，并更新 `schemas/content.schema.json` 的枚举。
  否则 `validate-content` 会报 unknown slide type，或 diversity gate 会把 1:1 翻新误判为缺少 roadshow 的
  anchor / close。
- 图片、截图和其它资源路径不要把长 run 目录路径直接写进 `content.json` 的文本字段；优先使用相对
  `assetRoot` 的短路径，并在 `xdoc pptx apply` 时传 `--asset-root <run-dir>`。这里的截图指用户提供、
  源 deck 内已有的截图对象或经用户批准的新截图资产，不包括源 slide 渲染 PNG。当前文本 fit 检查会扫描
  content 中的长 Latin token，长绝对路径容易被误判为显示文本溢出。

验证侧重点：

- `content-validation` 除用户显式接受的 DeckKit readiness 例外外，不应有文本 fit warning。
- `check-lock` 应为 valid，最好 warnings=0；如果资料型翻新导致连续相同节奏，可把资料页标为
  `appendix`，但必须用 contact sheet 复核整体节奏。
- `vision-check` 默认要求 high/medium 为 0；如果源 deck baseline 已有 high/medium，则候选必须用
  `vision-diff.json` 做 delta 判断：不得新增 high，新增 medium 需要修复或在最终摘要中列为源内容保真导致的已复核风险。
  low 需要人工判断。
- `pptx-diff.json` 是语义审计，不是视觉判断，也不替代 `refurbish-audit`。可靠 diff 应与
  `reference-map.json` 和 `content-audit-final.json` 一致；可靠的文本/slide/object 删除必须有
  `approvedChanges[]` 或用户确认。`uncertain` / `unsupported` 区域要在最终摘要中披露，并说明用
  哪个人工或专项 gate 覆盖。
- PNG/contact-sheet 复核使用最终 `refurbish-compare` 抽查封面、密集文本拆分页、表格页、
  SmartArt/无文本补齐页和最后一页。局部修复复核可运行带 `--slides` 的 contact-diff，但不要在
  最终全量 compare 之外再次渲染同一组 source/candidate/slide range/DPI。
  对翻新任务还必须做视觉差异判断：候选是否明显沿用了目标风格，是否避免了"原稿基本不变"。
  同时检查 proof object 是否过满、圆角/图片/图案示例是否压住标签、空内容区域是否残留无意义横线。
- `refurbish-compare.png` 是交付物，不只是内部 QA 图。它必须覆盖全 deck，报告中的
  `status` 必须为 `success`，`agentGate.status` 必须为 `pass`，`summary.scopeMode` 必须为
  `all-slides`，`summary.pairCount` 必须匹配源/输出页数，且 render 尺寸必须非零。交付前运行
  `<skill-root>/scripts/cli/review/compare-gate.mjs --kind refurbish --publish`，并要求
  `refurbish-compare-gate.json.status=pass` 且 `finalBinding.status=bound`；gate
  是唯一最终 PPTX 发布者，之后不得再次复制候选文件；最终回复列出同目录 PNG 路径。
- 最终必须对比源 deck 和输出 deck：slide count、每页文本摘要、表格数量、chart 数量、SmartArt/diagram
  数量、图片/媒体数量、备注存在性和 `reference-map.json` 覆盖率。任何减少、缺页、未映射对象或未经批准的
  页数变化都是交付阻塞项。
- 对富文本、tab stops、表格和 connector-heavy 页面，再做文本泄漏审计：候选可见文本中不得出现 `<a:`、
  `<p:`、`xmlns` 等 OOXML 片段；逐页 shape type 数量不得少于源页，除非已在 `content-audit.json`
  中记录为用户批准的删除或降级。
  常规内容保真检查应优先由 `xdoc pptx refurbish-audit` 生成 `content-audit-final.json`。如果
  原生命令非零退出、被系统 kill、崩溃、或写出空 JSON，不要把文件存在当作通过；保存
  `*.exit` / `*.stderr`，单独重试一次，并立刻运行
  `scripts/cli/refurbish/audit.mjs`。若 legacy audit 也不足以覆盖当前风险，再用
  `inspect` 生成 supplemental audit，对比 slide count、可见文本、picture/table/chart/connector/
  graphicFrame/placeholder 数量、notes、links 和 `reference-map.json` 覆盖率。最终摘要必须明确
  native audit 的工具失败和 supplemental audit 的结论。
  `fidelity-gate.json` 应作为最终保真结论入口；`layout-final.json` 应作为最终布局结构证据。
  两者都不替代人工 PNG/contact-sheet 视觉判断。
  OOXML 文本泄漏和 forbidden shape name 暂时由 legacy supplemental audit 补充。Agent 仍需人工复核机器无法判断的视觉差异、
  留白和 DeckKit 风格一致性。
