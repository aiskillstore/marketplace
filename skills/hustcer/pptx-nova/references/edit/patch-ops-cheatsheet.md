# Patch Ops Cheatsheet —— 59 个 op 按场景速查

下面按 **"我想做什么"** 归类 xdoc schema v1 的常用 op。当前契约包含 59 个 op，每条只列
关键字段；完整 schema 用 `xdoc schema --mode ops --ops <name>` 拉。旧版细粒度 shape / chart /
table setter 已全部并入对应的聚合 op
（`set-shape` / `set-chart` / `set-table` ...），本表只列 canonical 名字。

> 通用：所有 patch op 都嵌进 `{ "schemaVersion": "pptx-patch/v1", "ops": [ { "op": "...", ... } ] }`。
>
> 通用：`slide` 字段是 **0-based** 索引；`paragraph` / `run` / `row` / `column` 同样 0-based。
>
> 通用：schema 类型为 `length` 的几何字段只接受带单位的
> 字符串：`"1in"` / `"2cm"` / `"96px"` / `"72pt"` / `"914400emu"`。
> 裸 number 与无单位字符串会被拒收。字段名本身不能决定类型：例如 freeform
> 的 `path.width/height` 和路径点坐标使用整数 viewport，见 §2。

---

## 1. 演示文稿与 slide 级

| op                        | 用途                                                                                            |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| `add-slide`               | 加一页，`layout` 可按 `{ index }` / `{ name }` / `{ type }` 选                                  |
| `remove-slide`            | 删除指定 slide                                                                                  |
| `move-slide`              | 改 slide 顺序（`from` / `to` 都是 0-based）                                                     |
| `duplicate-slide`         | 复制 slide（保留全部内容，包括 notes）                                                          |
| `set-slide-size`          | 改 deck 尺寸（`slideSize` 字段）：`"wide"`(16:9) / `"standard"`(4:3) / `{ w, h }`               |
| `set-slide-background`    | 改某页背景：`{ fill: ..., followMaster: false }`                                                |
| `set-slide-transition`    | 设置/清理 schema 披露的基础、Morph、P14 转场与自动切页；参数和验证见 `../content/animations.md` |
| `set-slide-animations`    | 设置/清理安全子集动画，可 `mode: merge-safe / replace / clear`                                  |
| `set-slide-animations`    | 按 inspect 动画 id 修改安全子集 step（`animations: [{ id, ... }]`）                             |
| `set-slide-animations`    | 按 inspect 动画 id 删除安全子集 step（`remove: ["<id>"]`）                                      |
| `set-document-properties` | core props（`properties` map，键如 `title` / `author` / `subject` / `keywords`）                |

### Slide notes

| op                                | 用途                                   |
| --------------------------------- | -------------------------------------- |
| `set-slide-notes`（`text`）       | plain text 备注（覆盖）                |
| `append-slide-notes`              | 追加 plain text                        |
| `set-slide-notes`（`paragraphs`） | rich notes（paragraphs + runs + font） |
| `set-slide-notes` + `text: ""`    | 清空 notes 文本但保留 notes slide      |
| `remove-slide-notes`              | 整页 notes 删除（包括 part）           |

### Layout / Master / Theme

| op                             | 用途                                                               |
| ------------------------------ | ------------------------------------------------------------------ |
| `add-layout`                   | 新建 layout（`type` 可选 `title` / `obj` / `secHead` 等）          |
| `add-layout`（`source`）       | 复制既有 layout 到新 layout part（`source` 选源 layout）           |
| `set-layout`（`name`）         | 重命名 layout                                                      |
| `set-layout`（`type`）         | 改 layout type                                                     |
| `add-layout-placeholder`       | 给 layout 加 placeholder（type + idx）                             |
| `set-theme`（`colors`）        | 改主题色（`colors: { accent1: "1A73E8", ... }`）                   |
| `set-theme`（`fonts`）         | 改主题字体（`fonts: { major / minor: { typeface, eastAsian } }`）  |
| `set-master`（`background`）   | 改 master 背景（`background: <fill>`）                             |
| `set-master`（`placeholders`） | 改 master 占位符默认（`placeholders: [{ type, font, ... }]`）      |
| `set-default-text-style`       | 整个 deck 的默认文字样式（`levels: [{ level, font, ... }]`）       |
| `set-font`                     | 整包中文或东亚字体归一化；选择边界和复核见 `font-normalization.md` |

详见 `../content/styles-and-themes.md`。

### Animation / Transition 速查

动画编辑先读 `../content/animations.md`。不要在未 inspect 的情况下覆盖 `<p:timing>`。

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "mode": "merge-safe",
  "animations": [
    {
      "shape": { "name": "KPI Card" },
      "effect": "fade",
      "trigger": "on-click",
      "duration": 450,
      "delay": 0
    }
  ]
}
```

局部合并既有动画：

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "mode": "merge-safe",
  "animations": [
    {
      "shape": { "name": "KPI Card" },
      "phase": "exit",
      "effect": "fade",
      "trigger": "after-previous",
      "duration": 650
    }
  ]
}
```

逐条 bullet / paragraph：

```json
{
  "op": "set-slide-animations",
  "slide": 1,
  "mode": "merge-safe",
  "animations": [
    {
      "target": { "shape": { "name": "Body" }, "paragraph": 0 },
      "build": "by-paragraph",
      "effect": "appear",
      "trigger": "on-click"
    }
  ]
}
```

复杂 timing、motion path、emphasis、media timing、interactive trigger、chart/SmartArt build
默认 preserve-only；只有用户明确接受 `replace` / `clear` 语义损失时才重建整棵 timing tree。

---

## 2. Shape 创建

| op                | 用途                                                                                                                       |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `add-shape`       | 加预设形状（`kind` 必填：182 个 catalog 名/别名，或任意 canonical OOXML ST_ShapeType prst；`preset` 已删除）               |
| `add-text-box`    | 纯文本框                                                                                                                   |
| `add-placeholder` | 加 placeholder shape（`type` 取 placeholderType enum：title/body/ctrTitle/subTitle/obj/pic/chart/tbl/...，没有 `content`） |
| `add-image`       | 加图片（`assetSource.path` 或 `bytesBase64`）                                                                              |
| `add-equation`    | 加数学公式 SVG（`latex` fallback 或 `assetSource.path` 渲染资产）                                                          |
| `add-video`       | 加视频，含 poster frame                                                                                                    |
| `add-ole-object`  | 嵌入 OLE 对象（Excel/Word/PDF 等），含 ProgID 与 icon                                                                      |
| `add-group`       | 创建空 group shape，可后续填子 shape                                                                                       |
| `add-connector`   | 加连接线（`kind: straight / elbow / curve`）                                                                               |
| `add-freeform`    | 显式形状框与整数 viewport；`path.commands` 使用 move / line / cubic / close，以运行时 schema 为准。                        |
| `add-table`       | 加表 `rows x columns`，可选 `data: [[...]]` 初始化                                                                         |
| `add-chart`       | 加图表，详见 `../content/charts.md`                                                                                        |

### add-freeform 坐标与曲线

先读取当前 `xdoc schema` 的 `add-freeform` operation，确认运行时支持 `path`
合同。`x/y/w/h` 使用带单位的 slide 坐标；`path.width/height` 是正整数局部
viewport，映射到形状框。控制点与端点均为局部绝对整数，不使用英寸字符串。

每个 contour 用 `move` 开始，至少有一段 `line` 或 `cubic`；`cubic` 的
`x1/y1`、`x2/y2` 是两个控制点，`x/y` 是终点。需要闭合时显式追加 `close`，
其后只能开始新的 `move` 或结束。开放曲线通过 `set-shape` 设置无填充和线条。

```json
{
  "op": "add-freeform",
  "slide": 0,
  "name": "CubicWave",
  "x": "2in",
  "y": "2in",
  "w": "4in",
  "h": "2in",
  "path": {
    "width": 1000,
    "height": 1000,
    "commands": [
      { "type": "move", "x": 0, "y": 500 },
      { "type": "cubic", "x1": 250, "y1": -500, "x2": 750, "y2": 1500, "x": 1000, "y": 500 }
    ]
  }
}
```

局部坐标范围为 -2147483648～2147483647；viewport 范围为 1～2147483647。
控制点可以在 viewport 外，既不会被裁剪，也不会自动扩张形状框。实际曲线可能
伸出形状框，必须检查 PNG。首批只支持三次 Bézier C，不接受 Q/A、公式或 SVG
path 字符串；旧 `points/originX/xScale` 协议不能与新合同混用。

用 `inspect` 的 `freeform.path` 回读完整路径；遇到 `status: "preserve-only"`
时保留原形状，不把空路径或部分几何重建成替代品。样式继续使用普通
`set-shape.fill/line`，控制点变化应出现在 semantic diff 中。

### add-shape 示例

```json
{
  "op": "add-shape",
  "slide": 0,
  "kind": "rounded-rectangle",
  "x": "1in",
  "y": "1in",
  "w": "3in",
  "h": "1.2in",
  "name": "KPI Card"
}
```

用 `xdoc pptx catalog shapes --json` 看完整 182 个预设；常用别名：
`rounded-rectangle / right-arrow / star-5 / smiley-face / pentagon / cube /
cloud-callout`。

---

## 3. Shape 几何 / 样式

| op                             | 用途                                                                        |
| ------------------------------ | --------------------------------------------------------------------------- |
| `set-shape`（`position`）      | 移动（`position: { x, y }`）                                                |
| `set-shape`（`size`）          | 缩放（`size: { w, h }`）                                                    |
| `set-shape`（`rotation`）      | 旋转（`rotation: <度数>`）                                                  |
| `set-shape`（`flip`）          | 水平/垂直翻转（`flip: { horizontal, vertical }`）                           |
| `set-shape`（`name`）          | 改 shape name（修改时定位用）                                               |
| `set-shape`（`fill`）          | 改 fill：solid / gradient / pattern / picture / none                        |
| `set-shape`（`line`）          | 改边框（`line: { width, color, dash }`；`line: { noLine: true }` = 无边框） |
| `set-shape`（`effect`）        | 阴影 / 发光 / 反射 / 柔化（`effect: { shadow / glow / ... }`）              |
| `set-shape`（`clickAction`）   | 点击跳转（链接 / 跳页 / 运行宏）                                            |
| `set-shape`（`accessibility`） | 写标题、描述、装饰性标记                                                    |
| `remove-shape`                 | 删除                                                                        |

同一个 `set-shape` 可同时给多个字段（如 `position` + `size` + `fill` 一次改完）。
连接线原生 site、精确 ungroup、OLE/model preview 几何和复制身份边界见
`native-shape-editing.md`；不要把 `site` 当四边枚举，也不要绕过不可表示变换的拒绝。

Group target 是明确例外：只支持 `name`、`accessibility`、`position`、`size`、
`rotation`、`flip` 和 `effect`。`fill`、`line`、`clickAction` 会在任何 mutation 前返回
`invalid_operation`；先 inspect/select 组内子形状，再分别对这些子形状设置对应字段。以当前
`xdoc schema --mode ops --ops set-shape --minimal` 中的 `target-field-compatibility` constraint
和 dry-run 结果为准。

### Fill 示例

```json
{
  "op": "set-shape",
  "slide": 0,
  "shape": { "name": "KPI Card" },
  "fill": { "type": "solid", "color": "1A73E8" }
}
```

支持 `solid` / `gradient` / `pattern` / `picture` / `none`；24 个 preset gradients；
gradient stop 可用 `schemeClr` 引用主题色。`picture` 是 shape 专用 fill，可用
`assetSource`（或 `bytesBase64` + `mimeType`）、`mode: "stretch" | "tile"`、`crop`、
`alpha`、`rotateWithShape` 和 tile 参数。内置 preview/PDF 对 picture fill 目前只
可靠呈现 stretch 与 alpha，crop/tile 交付以 PowerPoint 复核为准。详见
`../content/styles-and-themes.md`。

### Accessibility 示例

```json
{
  "op": "set-shape",
  "slide": 0,
  "shape": { "name": "Revenue chart" },
  "accessibility": {
    "title": "Quarterly revenue",
    "description": "Columns compare actual and target revenue for four quarters.",
    "decorative": false
  }
}
```

省略字段表示保留，`null` 表示清除。纯装饰对象设 `decorative: true`；不要同时
用误导性的描述把它当作信息对象。

### Effect 示例

```json
{
  "op": "set-shape",
  "slide": 0,
  "shape": { "id": 2 },
  "effect": {
    "shadow": { "blur": "6pt", "distance": "4pt", "angle": 90, "color": "000000", "alpha": 0.25 }
  }
}
```

`effect` 的子对象：`shadow`（`inner: true` = 内阴影，默认外阴影）/ `glow`
（`color` + `radius`）/ `reflection`（`alpha` / `blur` / `distance` / `size`）/
`softEdge`（`radius`）。`alpha` 是 0-1 小数；`color` 可用 hex 字符串或
`{ "scheme": "accent1" }` 引用主题色。

---

## 4. 文本编辑

文本写入有两条路径：**简单文本** 用 `set-text-frame`；**段落 / 段落格式 / run 字体**
用 `set-paragraph` / `set-run` / `add-paragraph` / `add-run`。

`set-text-frame` 写入含 `\n` 的字符串时会生成多个 paragraph。后续 `set-run` 只会修改指定
`paragraph/run`，不会自动把第 0 段的字体复制到其它段。凡是卡片、badge、diagram
节点、说明框里使用多行文本，都要逐段设置 `set-run` 和 `set-paragraph`，或把
标题/正文拆成独立 text box。否则 PNG 渲染时常见问题是第二行以后回到默认大字号，
导致文本越界、卡片拥挤或版式失衡。

| op                             | 用途                                                        |
| ------------------------------ | ----------------------------------------------------------- |
| `set-text-frame`               | 整个 text frame 覆盖 plain text                             |
| `add-paragraph`                | 在 text frame 末尾加段（可带 `text`）                       |
| `set-paragraph`（`text`）      | 改某段的文字                                                |
| `set-paragraph`（`format`）    | 改对齐 / 缩进 / 行距 / 段前段后 / RTL / level               |
| `set-paragraph`（`bullet`）    | 改 bullet（`type: none / character / auto-number / image`） |
| `add-run`                      | 给段加 run                                                  |
| `set-run`                      | 改某 run 文字与字体                                         |
| `set-run`（`hyperlink`）       | run 加超链接                                                |
| `set-run`（`hyperlink: null`） | run 清超链接                                                |

### set-paragraph 关键字段

格式字段全部包在 `format` 对象里（顶层只有 `op` / `slide` / `shape` /
`paragraph` / `text` / `format` / `bullet`）：

```json
{
  "op": "set-paragraph",
  "slide": 0,
  "shape": { "name": "Title 1" },
  "paragraph": 0,
  "format": {
    "level": 0,
    "alignment": "center",
    "lineSpacing": 1.2,
    "spaceBefore": "6pt",
    "spaceAfter": "6pt",
    "indent": "0.25in"
  }
}
```

`alignment`: `left / center / right / justify / justify-low / distribute / thai-distribute`。
`lineSpacing`: 数字 = 倍数；字符串 `"24pt"` = 固定行高。
把 `format` 中的字段设为 `null` 可清掉该属性（如 `"indent": null`）。

### Run 字体

```json
{
  "op": "set-run",
  "slide": 0,
  "shape": { "id": 2 },
  "paragraph": 0,
  "run": 0,
  "text": "Q2 2026",
  "font": {
    "name": "Inter",
    "eastAsian": "Noto Sans CJK SC",
    "complexScript": "Noto Sans Arabic",
    "letterSpacing": "0.2pt",
    "size": "32pt",
    "bold": true,
    "italic": false,
    "underline": "sng",
    "color": "1F1F1F",
    "fill": { "type": "solid", "color": "1F1F1F" }
  }
}
```

带 `sourceText` / `sourceHash` / `unitId` 的 `set-run` 必须使用输入的 numeric shape ID，
并放在顶层 `ops[]`；guard 对应整个源段落。`replace-paragraph-text` 也只允许顶层执行。
具体 selector、快照和错误处理见 `inspect-and-edit.md` 的源段落保护章节。

### Text frame 行为

| op                                         | 用途                                                                                                                     |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `set-text-frame`（`frame.autofit`）        | `none` 固定框；`shape` 请求原生字体测量与框几何 reflow；`text` 缩小溢出文字，可加 `fontScale` 1-100；`null` 清本层设置   |
| `set-text-frame`（`frame.direction`）      | 竖排文本方向（`"vertical"` / `"vertical-270"` / `"east-asian-vertical"` 等；`"horizontal"` 或 `null` 恢复横排）          |
| `set-text-frame`（`frame.margin*`）        | 设置四边内边距；单位值或 `null`（清掉显式属性，恢复继承/默认）                                                           |
| `set-text-frame`（`frame.verticalAnchor`） | `top` / `middle` / `bottom`；`null` 清除                                                                                 |
| `set-text-frame`（`frame.wordWrap`）       | 布尔值控制换行；`null` 清除                                                                                              |
| `fit-text`                                 | 给 text frame 算合适字号（`maxFontSize` / `minFontSize`，可选 `strategy: "estimate" / "font-metrics"`，默认 `estimate`） |

`fit-text` 直接计算并写死字号。`shape` autofit 的原生测量边界、锚点、失败条件与
回读验证见 `inspect-and-edit.md`；不要把它描述为只写属性后等待 PowerPoint 调整。

---

## 5. 表格

| op                                | 用途                                                                                               |
| --------------------------------- | -------------------------------------------------------------------------------------------------- |
| `add-table`                       | 加表（详见 `../content/tables.md`）                                                                |
| `set-table`（`cells[].text`）     | 改单元格文字（`cells: [{ row, column, text }]`）                                                   |
| `set-table`（`cells[].style`）    | 单元格 fill/font/border/margin/对齐（`cells: [{ row, column, style: {...} }]`）                    |
| `set-table`（`cells[].formula`）  | 静态公式 SUM/AVG/COUNT/MIN/MAX（`cells: [{ row, column, formula: "SUM(B2:B4)" }]`）                |
| `set-table`（`rows` / `columns`） | 改行高 / 列宽（`rows: [{ row, height }]`，`columns: [{ column, width }]`）                         |
| `set-table`（`style`）            | 表格 `firstRow` / `horizontalBanding` / `verticalBanding` / `styleId`                              |
| `set-table`（`borders`）          | 区域批量加边框（`borders: [{ range: {...}, value: {...} }]`，outline / insideH / insideV / cross） |
| `set-table-data`                  | 整表数据覆盖，`resize: true` 自动改行列数                                                          |
| `set-table-data`（`format`）      | 从 CSV / JSON 导入：`data: { format: "csv", text }` 或 `{ format: "json", values / text }`         |
| `merge-table-cells`               | 合并                                                                                               |

`set-table-data` 的 `data` 是严格 union：`{ format: "matrix", values: [[...]] }` /
`{ format: "csv", text: "..." }` / `{ format: "json", values: [[...]] 或 text }`。
同一个 `set-table` 可同时带 `style` / `rows` / `columns` / `cells` / `borders`。

完整示例见 `../content/tables.md`。

---

## 6. 图表

| op                                | 用途                                                                                              |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| `add-chart`                       | 创建（27 个 kind, 详见 `../content/charts.md`）                                                   |
| `set-chart-data`                  | 替换数据                                                                                          |
| `set-chart-text`                  | 改标题 / 系列名 / 分类名等文本                                                                    |
| `set-chart`（`style`）            | PowerPoint 内置 chartStyle 1-48                                                                   |
| `set-chart`（`title`）            | 标题样式 font/fill/line（改标题文本用 `set-chart-text`）                                          |
| `set-chart`（`legend`）           | 图例（`position` / `includeInLayout` / `horizontalOffset` / `font`）                              |
| `set-chart`（`axes[].scale`）     | 轴刻度 min/max/unit/crosses（`axes: [{ axis: "category" / "value" / "x" / "y", scale: {...} }]`） |
| `set-chart`（`axes[].line`）      | 轴线样式                                                                                          |
| `set-chart`（`axes[].ticks`）     | 刻度 / 标签位置 / number format                                                                   |
| `set-chart`（`axes[].gridlines`） | 网格线                                                                                            |
| `set-chart`（`plot`）             | gapWidth / overlap / varyByCategories / bubbleScale                                               |
| `set-chart`（`series[]`）         | 系列 fill/line/marker/smooth/invertIfNegative（`series: [{ series: N, ... }]`）                   |
| `set-chart`（`series[].marker`）  | 系列 marker                                                                                       |
| `set-chart`（`series[].points`）  | 单点样式（`series: [{ series: N, points: [{ point: M, ... }] }]`）                                |
| `set-chart`（`dataLabels`）       | 数据标签（`scope` / `showValue` / `position` / `numberFormat`）                                   |
| `set-chart`（`view3D`）           | 3D 视角（`rotX` / `rotY` / `rightAngleAxes` / `perspective` / `depthPercent` / `heightPercent`）  |

同一个 `set-chart` 可同时带 `style` / `plot` / `title` / `legend` / `axes` /
`series` / `dataLabels` / `view3D`。`view3D` 只接受原生 3D chart group，普通
2D 图表会在写入前 fail closed；PDF/Viewer 的 3D 投影仍是 partial，交付时以
PowerPoint 原生渲染复核为准。

详见 `../content/charts.md`。

---

## 7. 图片 / 媒体

| op               | 用途                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| `add-image`      | 加图片                                                                                         |
| `set-image`      | 更新已有图片的 `crop` 和/或 `maskPreset`；各裁剪边为 `[0,1)`，`null` 清裁剪/把 mask 恢复为矩形 |
| `add-video`      | 加视频                                                                                         |
| `add-ole-object` | 嵌入 OLE 对象（如 Excel）                                                                      |

资产推荐用 `assetSource.path` + `--asset-root`：

```json
{
  "op": "add-image",
  "slide": 0,
  "x": "1in",
  "y": "1in",
  "w": "4in",
  "h": "3in",
  "assetSource": { "path": "images/hero.png", "mimeType": "image/png" }
}
```

```json
{
  "op": "set-image",
  "slide": 0,
  "shape": { "name": "Hero" },
  "crop": { "left": 0.08, "right": 0.08 },
  "maskPreset": "round-rect"
}
```

---

## 8. 高层 / Recipe / 数据驱动 / 控制流

`add-slide.recipe` 的 diagram kinds（`process-flow` / `cycle` / `hub-spoke` /
`funnel` / `pyramid` / `roadmap` 等）生成的是原生可编辑形状、文本框和连接线，
适合做 SmartArt 等价表达。当前没有通用 `add-smartart` op；已有真实
SmartArt diagram parts 主要走 inspect/report/preserve。需要展示或生成 SmartArt
风格内容时，优先使用这些 recipe diagram ops 或显式 shape/connector patch；不要假设
可以直接创建或编辑 OOXML SmartArt。

| op / kind                                  | 等级   | 用途                                                                                                                                                                                                             |
| ------------------------------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `add-slide.recipe.kind="title"`            | recipe | 封面                                                                                                                                                                                                             |
| `add-slide.recipe.kind="section"`          | recipe | 章节扉页                                                                                                                                                                                                         |
| `add-slide.recipe.kind="two-column"`       | recipe | 左右对照                                                                                                                                                                                                         |
| `add-slide.recipe.kind="image-caption"`    | recipe | 大图 + 说明                                                                                                                                                                                                      |
| `add-slide.recipe.kind="kpi-grid"`         | recipe | KPI 网格                                                                                                                                                                                                         |
| `add-slide.recipe.kind="comparison-table"` | recipe | 对比表                                                                                                                                                                                                           |
| `add-slide.recipe.kind="timeline"`         | recipe | 时间线 / 里程碑                                                                                                                                                                                                  |
| `add-slide.recipe.kind="roadmap"`          | recipe | 产品路线图 / 阶段计划                                                                                                                                                                                            |
| `add-slide.recipe.kind="matrix-2x2"`       | recipe | 2x2 矩阵                                                                                                                                                                                                         |
| `add-slide.recipe.kind="process-flow"`     | recipe | 流程图                                                                                                                                                                                                           |
| `add-slide.recipe.kind="funnel"`           | recipe | 漏斗 / pipeline                                                                                                                                                                                                  |
| `add-slide.recipe.kind="swot"`             | recipe | SWOT 四象限                                                                                                                                                                                                      |
| `add-slide.recipe.kind="pyramid"`          | recipe | 金字塔 / 层级模型                                                                                                                                                                                                |
| `add-slide.recipe.kind="hub-spoke"`        | recipe | 中心辐射 / 能力地图                                                                                                                                                                                              |
| `add-slide.recipe.kind="cycle"`            | recipe | 闭环 / 复盘循环                                                                                                                                                                                                  |
| `add-slide.recipe.kind="gantt"`            | recipe | 甘特 / 项目排期                                                                                                                                                                                                  |
| `add-slide.recipe.kind="scorecard-table"`  | recipe | 评分卡表格                                                                                                                                                                                                       |
| `add-slide.recipe.kind="comparison-cards"` | recipe | 方案比较卡片                                                                                                                                                                                                     |
| `set-theme` / `remap-theme`                | patch  | 品牌改装                                                                                                                                                                                                         |
| `populate-slide`                           | patch  | 填 layout 契约（title-and-content/two-column/...），`mode: "strict" / "loose"`                                                                                                                                   |
| `bind-data`                                | patch  | JSON 数据绑定 text / table / chart                                                                                                                                                                               |
| `if`                                       | patch  | 控制流：按状态分支（slide-count / selector-match / ...）                                                                                                                                                         |
| `foreach`                                  | patch  | 控制流：对 `items[]` 数组循环展开 `do[]` 子 ops                                                                                                                                                                  |
| `try`                                      | patch  | 控制流：高风险 op 失败时退到 `catch[]` 分支                                                                                                                                                                      |
| `define-macro`                             | patch  | 宏：注册一个命名 op 块（`{{args.*}}` 占位符）                                                                                                                                                                    |
| `use-macro`                                | patch  | 宏：展开已 `define-macro` 的命名宏，用 `args` 传参                                                                                                                                                               |
| `patch-ooxml`                              | patch  | 直接 XPath 改 OOXML；`set/add/remove/replace` 需 raw XML 权限。守卫修复 `repair-child-order` / `repair-preset-adjustments` / `repair-relationships` 必须按报告绑定与权限执行，见 `../runtime/troubleshooting.md` |

详见 `../content/recipes.md` / `../content/data-driven.md` / `control-flow-and-raw-xml.md`。

---

## 9. 常见模式片段

### 9.1 加封面 + 加 KPI 页 + 设置主题色

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    { "op": "set-theme", "colors": { "accent1": "1A73E8" } },
    {
      "op": "add-slide",
      "recipe": { "kind": "title", "title": "Q2 2026 Review", "subtitle": "Aug 2026" }
    },
    {
      "op": "add-slide",
      "recipe": {
        "kind": "kpi-grid",
        "title": "Key Metrics",
        "items": [{ "label": "Revenue", "value": "$42M", "delta": "+12%" }]
      }
    }
  ]
}
```

### 9.2 改某页标题颜色 + 加粗

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-run",
      "slide": 2,
      "shape": { "placeholder": "title" },
      "paragraph": 0,
      "run": 0,
      "font": { "bold": true, "color": "1A73E8" }
    }
  ]
}
```

### 9.3 替换某图表数据

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-chart-data",
      "slide": 1,
      "shape": { "name": "Revenue Chart" },
      "data": {
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series": [
          { "name": "2025", "values": [10, 12, 14, 16] },
          { "name": "2026", "values": [15, 18, 21, 24] }
        ]
      }
    }
  ]
}
```

### 9.4 给页面加水印形状

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "add-shape",
      "slide": 0,
      "kind": "rectangle",
      "x": "0in",
      "y": "7in",
      "w": "13.333in",
      "h": "0.5in",
      "name": "Watermark"
    },
    {
      "op": "set-shape",
      "slide": 0,
      "shape": { "name": "Watermark" },
      "fill": { "type": "solid", "color": "1A73E8" }
    },
    {
      "op": "set-text-frame",
      "slide": 0,
      "shape": { "name": "Watermark" },
      "text": "CONFIDENTIAL · 内部资料"
    }
  ]
}
```
