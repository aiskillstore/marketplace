# Deck Generator Workflow —— 创建/扩展 DeckKit 时的 JS 生成器工程化方法

> 本文档解决的问题：**当没有可用 DeckKit、需要新页型或需要改组件结构时**，如何用
> JS 生成器把视觉语言和页型抽取出来，再冻结成 DeckKit。普通交付 deck 应优先走
> `content manifest → DeckKit → patch`；不要把临时 generator 当作最终交付默认路径。
> 下面给一套 "用 JS 生成 patch.json" 的标准模板和工作流，把 deck 的"数据 + 模板"
> 显式拆开，让换主题色、换内容、换字号节奏各自 1 行修改解决。
>
> 出处：实战做 8 页 / 775 ops 橙色 deck 后沉淀。模板代码在
> `assets/examples/generator/deck-generator-template.mjs`，仅在创建/扩展 DeckKit 的探索阶段复制使用。

---

## 为什么手写 JSON 不可行（800+ 行 envelope 的真实代价）

| 痛点                              | 手写 JSON                   | JS 生成器               |
| --------------------------------- | --------------------------- | ----------------------- |
| 换主题色（hex 散落 N 处）         | grep + 全文 replace，易遗漏 | 改 `C.primary` 一行     |
| 字号节奏微调（page H1 32pt→28pt） | 找所有 page header 改       | 改 `F.pageH1` 一行      |
| 加新 KPI 卡片                     | 复制 50 行 JSON 改坐标      | 改 `kpis` 数组多一项    |
| 4 张 KPI 卡 x 坐标对齐            | 手算 + 数像素               | `startX + i*(w+gap)`    |
| selector 命中率                   | shape name 散落，拼写易漂移 | `nm(s, "X")` 统一命名   |
| 维护性                            | 800 行 JSON 难审查          | 250 行 JS 可循环 / 函数 |

**判断：deck 超过 ~100 ops 且没有可用 DeckKit 时，先上生成器抽取/扩展 DeckKit**。
规模越大收益越大；冻结后后续交付回到 DeckKit/content 路径。

---

## 探索生成器起手三步

先确认 `assets/deckkits/catalog.json` 里没有满足场景、语言、密度和页型覆盖的
production/default DeckKit。若有可用 DeckKit，直接回到 `deckkit-mode.md` 的
`content.json → validate-content → createDeck → xdoc → vision-check → PNG review` 生产路径。
只有确实需要新 DeckKit 或新页型时，才进入下面的探索生成器流程。

```bash
# 1. 复制模板
cp <skill-root>/assets/examples/generator/deck-generator-template.mjs <run-dir>/generate.mjs
cp <skill-root>/assets/examples/generator/theme-packs.generated.mjs <run-dir>/theme-packs.generated.mjs

# 2. 选择 themePack/stylePack；要新增风格时先改 assets/themes/catalog.json
#    并在发布前同步生成的 theme catalogs
#    然后只改各 slide 函数里的文字/数据

# 3. 生成探索 patch + 丰富度自检 + dry-run gate + 落盘
node <run-dir>/generate.mjs --theme corporate-blue --style consulting --layout executive-grid > patch.json
jq '.ops | length' patch.json   # 仅记录构建规模；质量由内容、结构和真实渲染证明，不设操作数下限
# 这里没有 --input，是从空白新建；不会复用已有 deck session。
# 编辑同一已有输入时可加 --daemon 复用解析；严格要求该 transport 时用 --daemon-strict。
xdoc pptx apply -p patch.json -o out.pptx --dry-run --json | tee dry-run.json
# 检查 dry-run.json 里没有阻塞性 visualRisks，并在 apply 后用 vision-check 清零 high/medium
xdoc pptx apply -p patch.json -o out.pptx --overwrite
xdoc pptx vision-check out.pptx --json | tee vision.json
# 创建型 deck 必须 high=0 且 medium=0；medium 也要改 generator/layout 后重跑
xdoc convert out.pptx --to png -o previews --overwrite --contact-sheet
# 先 Read previews/contact-sheet.png 总览图扫跨页一致性（配色/页码/节奏/构图）、定位可疑页，
# 再逐页 Read previews/slide-00*.png 抠单页细节：字符重叠/换行压字/截断、
# 小字号、连接线/箭头、中轴居中和对称平衡
```

探索样例通过后，应把视觉 token、组件和页型函数抽取到
`assets/deckkits/<id>/<id>.kit.mjs`，把布局、组件、schema 和示例归入同一 `<id>/`，补 catalog、benchmark 和 review。最终交付 deck
仍从 content manifest 调用 DeckKit 生成，不直接交付这份临时 generator 的输出。

---

## 耗时基准

以下为早期探索任务的历史人工计时，不代表当前运行时或其他机器的性能保证。

### 从零探索样本(10 页 / 1105 ops)

| 阶段                         | 耗时   | 占比    | 优化抓手                                    |
| ---------------------------- | ------ | ------- | ------------------------------------------- |
| 内容大纲提炼                 | ~3 min | 15%     | 先列每页主题再下笔                          |
| **JS 生成器编写**            | ~9 min | **45%** | **`grid()` / `_txH()` helper 压缩坐标手算** |
| dry-run gate + 修 schema bug | ~3 min | 15%     | 核对 remediation 目标，再校验完整请求       |
| 落盘 + PNG 视觉验证          | ~5 min | 25%     | 逐页 Read,不要批量浏览                      |

总计 ~20 min。这个样本代表从零探索主题、布局和生成器结构的场景。

### 模板熟练样本(8 页 / 893 ops / 橙色 roadmap deck)

| 阶段                   | 耗时         | 占比       | 备注                                                         |
| ---------------------- | ------------ | ---------- | ------------------------------------------------------------ |
| 内容大纲提炼           | ~1.0 min     | 15-20%     | 从当时的规划文档提炼（未随本仓库发布：`agent-pptx-plan.md`） |
| **JS 生成器编写**      | ~3.0-3.3 min | **45-50%** | 复用本模板模式,仍是最大耗时项                                |
| dry-run gate + 小修    | ~0.7-1.0 min | 10-15%     | 本次只修了 1 处长文本 overflow risk                          |
| apply + PNG + 结构验证 | ~1.3-1.6 min | 20-25%     | 包含 sidecar、PNG 导出、MD/zip/check 验证                    |

总计 ~6.6 min。这个样本代表已经熟悉 skill、复用生成器模式和避坑规则的快路径；
绝对时间比从零样本低很多，但占比仍显示"JS 生成器编写 / 坐标排版"最耗时。

模板里 `grid()` 把网格对齐从手算变 1 行,`_txH()` 把字号→高度的人脑表查变函数
调用,这两个是压缩"JS 生成器编写"耗时的关键。新建生成器还必须把**可读字号下限**
写进 helper，而不是靠每个 slide 函数自觉：核心正文不低于 `10.5pt`，label / badge /
chart / table 和页脚 / 来源不低于当前 canonical 门禁（默认 `10pt`），套件合同更严格时
采用更严格下限。如果文字放不下，重组内容、换布局、扩容器或拆页；不要静默删字段或缩字通过。

> **已有输入可用 `--daemon` 复用 session**：带同一 `--input` 的 inspect、dry-run 和 apply
> 可以复用解析状态；无输入的新建 patch 不会获得这项收益。PNG 转换仍走独立命令，
> 不复用该 PPTX session。实际收益须按输入、缓存状态和当前机器测量，不按 op 数推算。

---

## 模板的 4 个关键设计

### 1. 全局调色板 `C` 对象（来自 themePack，按角色命名）

```js
const C = {
  primary: 'F57C00', // 主品牌色
  primaryDk: 'E65100', // hero 收尾页深底色
  secondary: 'FF9800', // 副色（chart 第二系列）
  cardBg: 'FFF3E0', // 卡片底
  textPri: '1F1F1F', // 文字主
  textSec: '5F6368', // 文字次
  textMut: '9AA0A6', // 文字弱
  posBg: 'E6F4EA',
  posTxt: '188038', // 正增长 pill
  negBg: 'FCE8E6',
  negTxt: 'C5221F', // 负增长 pill
}
```

模板里的 `C` 由 `themePack.generator.colors` 派生。**所有 hex 字面量都必须走 `C.*`**，
整个文件里不应该出现第二个 `"F57C00"`。换主题优先传 `--theme` 或新增/修改
`assets/themes/catalog.json` 后同步生成的 theme catalogs，不要在复制出的 generator 里维护一份
完整主题色。

### 2. 字号节奏 `F` 对象（来自 themePack + stylePack）

```js
const F = {
  hero: '54pt', // hero 收尾页大标题
  cover: '44pt', // 封面主标题
  pageH1: '32pt', // 内容页主标题
  kpiNum: '40pt', // KPI 大数字
  body: '14pt', // 正文
  pill: '11pt', // delta pill
  eyebrow: '10pt', // eyebrow 小标
  foot: '10.5pt', // 页脚 / 注脚；按当前合同和 canonical 门禁复核
}
```

`F` 由基础兼容值、`themePack.generator.sizes` 和 `stylePack.generator.sizes` 合并得出。
consulting/minimal/product 的完整字号 token 属于 `assets/themes/catalog.json`；生成器模板只保留
外部 hand-written pack 的最小 fallback。

### 2b. Layout variant（同一 theme/style 跑不同版式系统）

模板支持三套内置 generator layout variant：

| Variant           | 适用场景                                              | 结构特征                                                 |
| ----------------- | ----------------------------------------------------- | -------------------------------------------------------- |
| `executive-grid`  | board readout、KPI evidence、咨询式 executive summary | 标题 band、KPI 卡片网格、chart + callout、三列行动支柱   |
| `narrative-split` | thesis-led recommendation、客户决策 memo              | 左侧叙事 rail、右侧证据堆叠、cohort bar、结论 panel      |
| `data-room`       | appendix、due diligence、action register              | 紧凑命令头、dashboard metrics、原生 table、行动 register |

探索用单 deck 生成：

```bash
node <skill-root>/assets/examples/generator/deck-generator-template.mjs \
  --theme consulting-grey \
  --style consulting \
  --layout narrative-split > .tmp-narrative.patch.json
```

DeckKit 视觉回归使用 benchmark 工具，而不是旧 showcase 产物矩阵：

```bash
node <skill-root>/scripts/cli/deckkits/benchmark.mjs \
  --deckkit consulting-dark \
  --all \
  --repeat 3 \
  --clean
```

benchmark 输出和 `scripts/cli/deckkits/readiness.mjs` 共同决定 DeckKit 是否能进入
delivery/default 路径。需要验证 theme/style 是否跨版式稳定时，把对应 fixture 收敛到
`<skill-root>/benchmarks/visual/`。

### 3. `nm()` 命名规范（双向必经）

```js
const nm = (slide, base) => `S${slide}_${base}`
//   生成： shape(s, nm(s, "KpiBg"), ...)        → "S2_KpiBg"
//   引用： fill(s, nm(s, "KpiBg"), C.primary)   → "S2_KpiBg" ✓
//   反例： fill(s, "KpiBg", ...)                → 命不中（真实名带前缀）
```

**严格规则：所有 shape name 进出都走 `nm(slide, base)`**。这是 selector
命中失败的常见根因 —— 创建时传入了带前缀的名称，引用时直接写裸名。
`shape()`、`textbox()`、`fill()` 等 helper 使用传入的名称，不会自动补前缀。

### 4. 复合 helpers 减少重复

模板提供以下常用 helper：

```js
shape(s, name, kind, x, y, w, h) // add-shape
box(s, name, kind, x, y, w, h, color) // add-shape + fill + noLine
textbox(s, name, x, y, w, h) // add-text-box
tx(s, name, x, y, w, h, text, font) // textbox + setText + setRun
grid(cols, gap, startX, contentW) // 自动算 N 列等距网格 → [{x, w}, ...]
_txH(sizePt, lines) // lines 默认 1；估算 textbox 高度，仍需检查溢出
```

`box` 是装饰元素的 one-liner，`tx` 是文字元素的 one-liner，`grid` 把"4 张 KPI
对齐"这类问题从手算变成一行,`_txH` 把"高度给字号几倍"的人脑表查变成函数调用。

对于对比页、流程图和架构图，再补两个几何 helper 思路：

```js
const centerX = (box) => box.x + box.w / 2
const centerY = (box) => box.y + box.h / 2
const gapCenterX = (left, right) => (left.x + left.w + right.x) / 2
const centeredAt = (center, size) => center - size / 2
```

VS 圆、中心节点、行内编号圆都用这些 helper 推导。连接线端点从 bbox 边缘和中心线算，
例如水平线 `y = centerY(target)`，`x1 = source.x + source.w`，`x2 = target.x`。
不要用目测的 `x=6.2` / `y=2.3`，也不要用未旋转的 `triangle` 假装水平箭头头。

**用 `grid()` 写 4-across KPI**：

```js
// 居中:cells 总宽 = 4*cardW + 3*gap;startX = (13.333 - totalW) / 2
const startX = 0.6
const cells = grid(4, 0.27, startX, 13.333 - startX * 2)
cells.forEach((c, i) => {
  box(s, nm(s, `K${i + 1}Bg`), 'rounded-rectangle', c.x, 2.4, c.w, 4.0, C.white)
  // 顶部色条用同一个 c.x / c.w,自动对齐
  box(s, nm(s, `K${i + 1}Top`), 'rectangle', c.x, 2.4, c.w, 0.1, C.primary)
})
```

**用 `_txH()` 写 textbox**：

```js
tx(s, nm(s, 'Title'), 0.85, 0.95, 11, Number.parseFloat(_txH(32)), 'Page H1', {
  // 32pt 单行
  name: FONT_LATIN,
  size: F.pageH1,
  bold: true,
  color: C.textPri,
})
tx(s, nm(s, 'Body'), 0.85, 3.0, 6, Number.parseFloat(_txH(14, 4)), longBody, {
  // 14pt 4 行
  name: FONT_LATIN,
  size: F.body,
  color: C.textSec,
})
```

---

## textbox 高度规则（防 text-overflow-estimate）

**模板中的估算 helper 名为 `_txH(sizePt, lines)`**，返回带 `in` 的字符串，可用于
patch 长度字段。`tx()` 的几何参数使用数值英寸，传入时须如上调用 `Number.parseFloat()`：

```js
_txH(54) // → "1.13in"  (单行 54pt)
_txH(44, 2) // → "1.83in"  (2 行 44pt)
_txH(14, 4) // → "1.17in"  (4 行 14pt body)
```

公式：`(sizePt / 72) * 1.5 * lines` —— 中文环境给 1.5 倍系数(西文可以 1.4)。

`text-overflow-estimate` 是 dry-run 和 `vision-check` 共用的静态估算信号。
它会基于最终 shape 文本、字号、inset 和 autofit 判断可用空间；创建型 deck 里出现
medium 时优先加高、重组内容、拆页或选择合法布局。**单行最小给字号的 1.4 倍,中文给
1.5 倍**;多行按行数线性放大。

| 字号 | 单行高度（in） | 2 行高度（in） | 4 行高度（in） |
| ---- | -------------- | -------------- | -------------- |
| 54pt | 1.13in         | 2.25in         | 4.50in         |
| 44pt | 0.92in         | 1.83in         | 3.67in         |
| 32pt | 0.67in         | 1.33in         | 2.67in         |
| 24pt | 0.50in         | 1.00in         | 2.00in         |
| 16pt | 0.33in         | 0.67in         | 1.33in         |
| 14pt | 0.29in         | 0.58in         | 1.17in         |
| 12pt | 0.25in         | 0.50in         | 1.00in         |
| 9pt  | 0.19in         | 0.38in         | 0.75in         |

---

## 装饰元素布局规则（封面页特别注意）

13.333in × 7.5in 幕布上，**主标题 textbox 通常吃 11in 宽**（x=0.95 → x=11.95），
装饰元素**不能放右上 (10+, 2-4) 区域**，必然碰撞。

### 安全区图（封面页）

```
┌──────────────────────────────────────────┐
│ 顶部品牌条 (0-13.333, 0-0.12)             │
├──────────────────────────────────────────┤
│                                          │ ← 0.6-2.4 通常空（留给 spacing）
├──────────────────────────────────────────┤
│ ▌ eyebrow                                │ ← 2.4-2.8
│ ▌ 主标题（占 0.95 → 11.95 宽）           │ ← 2.85-4.4
│ ▌ 副标题                                 │ ← 4.4-4.9
│ ▌ tagline                                │ ← 4.95-5.35
│                              ┌──┐┌──┐    │ ← 装饰安全区 (10+, 5.4-6.8)
│                              │  ││  │    │
│                              └──┘└──┘    │
├──────────────────────────────────────────┤
│ Hero strip (0-13.333, 6.95-7.5)          │
└──────────────────────────────────────────┘
```

- 装饰放 **右下 (10+, 5.4-6.8)** —— 主标题、副标题、tagline 都不会延伸到这里
- 不要放右上 (10+, 2-4) —— 主标题 textbox 必然覆盖
- 不要放底部 strip (6.95+) —— 会被 hero strip 盖住

更多布局模式（KPI 网格 / chart + callout / hero 收尾）见
[rich-deck-patterns.md](rich-deck-patterns.md)。

---

## 完整工作流（推荐顺序）

```
┌─ 1. 写 generate.mjs (从模板起步) ─────────┐
│   - 改 C 调色板                          │
│   - 改各 slide 函数文字/数据              │
│   - 必要时加新 slide 函数                 │
└───────────────────────┬───────────────────┘
                        │
                        v
┌─ 2. node generate.mjs > patch.json ───────┐
│   产物：patch.json (200-800 ops 的 envelope)
└───────────────────────┬───────────────────┘
                        │
                        v
┌─ 3. dry-run gate ─────────────────────────┐
│   xdoc pptx apply -p patch.json \         │
│     -o out.pptx --daemon --dry-run --json\│
│     | tee dry-run.json                    │
│                                           │
│   检查项：                                 │
│   - opResults[*].status == "success"      │
│   - visualRisks[] 无阻塞风险               │
│   - 没有 ambiguous selector               │
└───────────────────────┬───────────────────┘
                        │
                        v
                 dry-run 阻塞风险？
                  ┌─────┴─────┐
              yes │           │ no
                  v           v
        ┌─修 generate.mjs┐  ┌─ 4. apply 落盘 ─────────────┐
        │  re-loop      │  │ xdoc pptx apply -p patch.json│
        └───────────────┘  │   -o out.pptx --daemon       │
                           │   --overwrite                │
                           │ 产物：out.pptx + sidecar       │
                           └─────────────┬─────────────────┘
                                         │
                                         v
                           ┌─ 5. vision-check 几何门 ─────┐
                           │ xdoc pptx vision-check out.pptx│
                           │   --json | tee vision.json    │
                           │ high / medium 必须为 0         │
                           └─────────────┬─────────────────┘
                                         │
                                         v
                           ┌─ 6. PNG 视觉验证 ───────────┐
                           │ xdoc convert out.pptx \      │
                           │   --to png -o previews \     │
                           │   --overwrite --contact-sheet│
                           │                              │
                           │ 先 Read contact-sheet.png    │
                           │ 总览扫跨页 → 再逐页 Read PNG，│
                           │ 对照 §视觉验证盲点清单        │
                           └─────────────┬───────────────┘
                                         │
                                         v
                                  视觉问题？
                              ┌─────┴─────┐
                          yes │           │ no
                              v           v
                    ┌─修 generate.mjs┐  ┌─ 完成 ─┐
                    │  re-loop ↑    │  └────────┘
                    └───────────────┘
```

---

## 视觉验证盲点（静态检查抓不到的）

dry-run 做 schema / selector / op-level 语义校验，并用和 `vision-check` 相同的
文本溢出估算器提前报告 `text-overflow-estimate`。`vision-check` 继续负责几何重叠、
边界、字号和预期单行文本的 `text-unexpected-wrap` 等静态风险。下面这些仍必须靠 PNG
人工 Read 才能发现：

1. **字符重叠 / 换行压字 / 截断** —— 字体、theme/style、平台渲染差异会改变实际
   换行和字高；dry-run / vision-check 的 medium 风险要处理，PNG 里还要人工确认没有撞字。
   subtitle、eyebrow、badge、label 这类单行角色如果出现孤行，先处理
   `text-unexpected-wrap`，再看 PNG。
2. **小字号可读性** —— `font-too-small` 可能只是 low，甚至手写生成器可能没触发；
   PNG 上如果圆形编号、badge、risk 标签、灰色说明、chart/table label 需要凑近看，就必须返工。
3. **装饰元素遮挡主标题** —— textbox 在 dry-run 看来高度合法，但坐标和装饰
   shape 的 bounding box 重叠。
4. **卡片 x 坐标视觉不对齐** —— 4 张 KPI 卡 x 是 0.6 / 3.5 / 6.4 / 9.3，dry-run
   认为合法，但视觉上若 startX 没居中（应 `(13.333 - total) / 2`）会偏左/右。
5. **对称中心偏移** —— VS 圆、中心框、矩阵列头、流程主节点如果没有用 bbox 中心推导，
   只偏 0.1-0.2in 用户也会觉得“不对称、不专业”。
6. **连接线 / 箭头语义错误** —— 线没有接到目标 shape、箭头头方向不对、水平线实际倾斜；
   这是生成器几何问题，不是 PPTX 渲染 bug。
7. **文字颜色对比度不足** —— 浅灰文字（`9AA0A6`）放在浅灰背景（`F8F9FA`）上
   看不清；dry-run 不验对比度。
8. **chart 数据标签重叠 / 截断** —— `chart-label-density-unknown` 是 low
   severity advisory，不阻塞 apply，但确实可能渲染挤压。
9. **页脚和正文 textbox 边界相撞** —— 正文 textbox 给到 y=6.8 + h=0.5
   = 7.3，页脚 y=7.1，会重叠；dry-run 不报。
10. **hero 页深底白字遗漏改色** —— 复制白底页代码到 hero 时忘记把 textPri
    改成 white；dry-run 看到的只是合法 hex。
11. **freeform 尺寸或曲率不对** —— `add-freeform` 的 `x/y/w/h` 使用带单位的
    slide 坐标，`path.width/height` 与 command 坐标使用局部整数。先通过 runtime
    schema 确认该合同；显式设置 viewport 和形状框，逐个检查 cubic 的两个控制点。
    控制点不会自动扩张形状框，apply 后仍须用 PNG 检查真实轮廓与尺寸。
12. **页码连续性** —— `01 / 08` 跳到 `03 / 08` 因为漏调函数；dry-run 不知道
    你期望的页序。

**先 Read `previews/contact-sheet.png` 总览图**一屏扫跨页/全局问题（尤其上面第 4 条卡片对齐、
第 5 条对称中心、第 11 条页码连续，以及全 deck 配色 / 节奏一致性），快速定位可疑页；再逐页
Read PNG 时按 [rich-deck-patterns.md §9 视觉验证清单](rich-deck-patterns.md) 对照。

---

## 常见返工原因（生成器特有）

| 现象                                                         | 根因                                                                                                                                     |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 第一发 dry-run 报 `set-paragraph` 字段错误                   | `pAlign` helper 必须用 `op: 'set-paragraph'` 且把 `alignment` 放进嵌套 `format` 对象(模板已修,自己写新 helper 时别把 `alignment` 放顶层) |
| fill / line op 命不中（resolvedSelectors 报 not-found）      | shape name 引用裸名，应用 `nm(s, "...")`                                                                                                 |
| 主题色没换干净（部分 shape 还是旧色）                        | 某处 hex 字面量没走 `C.*`，grep `[0-9A-F]{6}` 找漏的                                                                                     |
| KPI 4 卡片不等距                                             | 手算 `startX + i*(cardW+gap)` 易错;统一用 `grid(4, gap, startX, contentW)`                                                               |
| textbox 大量 text-overflow-estimate warning                  | 核对字号、inset 和真实换行；用 `_txH(sizePt, lines)` 估算高度，传给 `tx()` 时转成数值，仍须验证。                                        |
| freeform / donut / polygon 在 PNG 中看不见                   | 核对 `add-freeform` 的带单位 `x/y/w/h` 与整数 `path` viewport，按运行时 schema 使用 move/line/cubic/close，并检查填充和线条。            |
| 同页左下 footer 写"BRAND·X"右上 watermark 写"structurify.io" | 旧版模板把 watermark 字串硬编码;新版 `pageChrome(s, total, footerLeft, watermark='')` 已参数化                                           |
| 第二次跑 `apply` 报 `output_exists`                          | 加 `--overwrite`，或 `xdoc pptx rollback --from-sidecar`                                                                                 |
| 第二次跑 `convert` 报 PNG 已存在                             | `convert` 也需要 `--overwrite`                                                                                                           |
| `xdoc -t png` 返回 help                                      | 错误命令格式，正确是 `xdoc convert <pptx> --to png -o <dir>`                                                                             |
| `legend: "b"` / `position: "outEnd"` 被拒                    | enum 必须使用 canonical 值 `"bottom"` / `"outside-end"`，shorthand 拒                                                                    |
| `titleStyle.bold` 被拒                                       | 放进 `font: { bold: true }` 子对象                                                                                                       |

---

## 升级路径：从模板到完整 deck

模板的 `executive-grid` 使用 8 个 slide 函数（cover / agenda / KPI / chart / table /
pillars / workflow / hero）。模板还包含 `narrative-split` 和 `data-room` 的专用函数。

按需 **复制函数 + 改函数名** 即可生成第 9、10 页：

```js
function slideKPI2(total) {
  // 复制 slideKPI，改名
  const s = 8 // 改 slide index
  // ... 内容部分照搬模板，改 kpis 数组
}

// 把 TOTAL 改为 9，在 main 的 JSON 输出前追加调用
slideKPI2(TOTAL)
```

不要把 8 个函数拆到 8 个文件 —— 单文件 250-400 行 deck 完全 OK，超过 600 行
再考虑按 slide 拆模块。

---

## 与 recipe 的关系

模板**几乎全用 patch op**（`add-shape` / `add-text-box` / `add-chart` /
`add-table`），以便在探索阶段直接控制对象、布局和样式。

Recipe 同样展开为原生 patch operations。对 `schemaVersion: "pptx-recipe/v1"` 的 recipe envelope 执行
`xdoc pptx recipe --recipe recipe.json --compile --json`，可从返回的 `patch`
获取完整展开请求，继续按普通 patch 流程修改、校验和 dry-run。一份 patch 也可
混用 `add-slide.recipe` 与底层操作，给生成页补充或调整原生形状、文字和样式。
部分 recipe 已提供 `section.eyebrow`、`kpi-grid.items[].delta` 等内容字段；
具体布局由 recipe 实现和输入决定，需要自定义几何时检查编译结果或改用 DeckKit。

操作数量不决定 recipe 的适用性或交付质量。普通客户演示级交付仍按本 skill 的
production/default DeckKit 路线执行；模板用于抽取或扩展 DeckKit，recipe 可作为
页面原型或显式 patch 的组成部分。完整字段和编译边界见 [recipes.md](../content/recipes.md)。

---

## 二次创作快路径（DeckKit 模式）

当目标场景已经有冻结的 DeckKit（`assets/deckkits/<id>/<id>.kit.mjs`），可以跳过从头写
generator 的全流程，直接走 **content manifest → DeckKit → patch** 的快路径：

```bash
# 1. 只写内容清单（~200 行 JSON，不含坐标/配色/组件逻辑）
cp assets/deckkits/consulting-dark/examples/content.json ./content.json
#    参照 assets/deckkits/consulting-dark/schemas/<slideType>.schema.json 改内容
#    或运行 node <skill-root>/scripts/cli/deckkits/slots.mjs --deckkit <id> 查看槽位速查

# 2. 校验 content（schema + density limit，几何错误 apply 前拦截）
node assets/deckkits/validate-content.mjs content.json --deckkit consulting-dark

# 3. 生成 patch（默认使用通用 driver；只有开发 DeckKit 时才写临时 build.mjs）
node <skill-root>/scripts/cli/create/build.mjs \
  --deckkit consulting-dark \
  content.json \
  -o patch.json \
  --quality-json quality.json

# 4. apply + 质量门
xdoc pptx apply -p patch.json -o out.pptx --daemon --dry-run --json
xdoc pptx apply -p patch.json -o out.pptx --daemon --overwrite
xdoc pptx vision-check out.pptx --json
xdoc convert out.pptx --to png -o previews --overwrite --contact-sheet
```

**与从头写 generator 对比**：

| 维度       | 从头写 generator                     | DeckKit 快路径                              |
| ---------- | ------------------------------------ | ------------------------------------------- |
| 输入       | 250-400 行 JS（坐标+配色+组件+数据） | ~200 行 content.json（纯数据）              |
| 需要理解   | op API + 坐标计算 + 视觉节奏         | schema 字段（有 description）               |
| token 开销 | 全量                                 | 首次引用 DeckKit 后缓存，二次创作仅 content |
| 适用场景   | 新 theme / 深度定制布局              | 同 theme 的内容变体                         |

**何时不适合直接复用现有 DeckKit**：目标场景尚无 production/default DeckKit、需要修改布局/
组件结构、需要新页型。这些场景仍应走创建/扩展 DeckKit workflow，并在冻结和 benchmark
通过后回到 content manifest → DeckKit → patch 生产路径。

---

## 也参考

- [rich-deck-patterns.md](rich-deck-patterns.md) — 视觉元素清单与 7 页 deck 起手势
- [patch-ops-cheatsheet.md](../edit/patch-ops-cheatsheet.md) — patch op 的 schema 速查
- [charts.md](../content/charts.md) — 27 种 chart kind 与 enum 全名表
- [troubleshooting.md](../runtime/troubleshooting.md) — `errorCatalog` 错误自修复
