# 表格（Table）创建与编辑

xdoc 的表格支持完整的对象模型：创建、改单元格、改样式、改宽高、合并、边框、
导入 CSV/JSON、静态公式。

## 专项语义验证

在 Studio、data-driven、结构编辑、模板跟随或手工 refurbish 路线中，只要 patch 含
add-table / set-table-data，apply 后保存 final-inspect.json，并运行
<skill-root>/scripts/cli/review/semantic-audit.mjs 输出 semantic-audit.json。该审计只做轻量语义门禁：
行列维度、header/source/unit 或时间范围披露，以及最终原生 table 对象存在性；它不是完整
table XML 等价检查。semantic-audit.json 若为 fail，最终 evidence-summary 必须阻塞；warn
可以披露后继续视觉复核。

table 页优先保留 PowerPoint 原生 table 语义；只有 inspect 证明源 deck 是视觉表格时，才按
普通 shape 编辑。写 table 前先在 `deck_lock.slides[].table` 记录数据来源、表格角色和验证点；
生成 `patch.json` 后由 `cli/create/check-lock.mjs` 检查明显行列错误，再交给 dry-run /
vision-check / PNG 复核。

在已有 deck 美化 / 翻新场景中，源表格若是 `shapeType == "table"` 且用户要求内容或样式不变，
默认处理方式是 `preserved`：复制或保留原生 table 对象，只在页级添加新风格 chrome。不要用
DeckKit 的视觉表格页型、文本框网格或重新 `add-table` 来替代，除非已逐项重建并验证这些语义：
单元格 fill、run 样式、字号、颜色、加粗/斜体/下划线/删除线、对齐、边框、合并、表格 styleId、
行高和列宽。无法验证等价时，`content-audit.json.tables.status` 必须保持 `preserved` 或
`blocked`，不能写成已完成的 `rebuilt-editable`。

若同一任务还要求明显翻新页面，保留 table 不代表整页保持原样。正确处理是：保留原生 table 的 XML /
对象语义，同时重做页眉、标题层级、网格、留白、说明和页脚节奏；表格可以在新网格内重新定位或缩放，
但不能丢失 PowerPoint 原生 table。最终必须重新 `inspect` 输出 PPTX，并把对应页记录为
`shapeType == "table"`；只看 PNG 像表格不算通过。
当前 xdoc 的 `remap-theme --scope tables` 已能对 table fill、border 和字体做 MVP 换肤。
翻新时先用 dry-run 报告确认 table 对象是 `changed`、`preserved` 还是 `skipped`；如果跳过后仍明显
带着旧主题色，再用 table ops 做最小补丁，不要直接把原生 table 重画成文本框网格。

最小检查清单：

- `add-table` 必须有正数 `rows` / `columns`。
- `data` 每一行列数一致；不一致是数据错误，不靠视觉裁切掩盖。
- `data` 行列数和声明表格尺寸不一致时，显式写 `resize: true`，否则修正尺寸或数据。
- header、单位、时间范围、来源说明必须随表格进入 content/patch，不能只在备注里解释。
- 单元格字号和边距要满足 deck 的可读性红线；PNG 复核仍要看截断、贴边、合并区域和网格线。
- 翻新后重新 `inspect` 输出 PPTX，确认需要保真的表格仍然是 `shapeType == "table"`，而不是一组
  `textBox` / `autoShape`。

## 先分辨：真表格还是视觉表格

### 共享边框的渲染诊断

当前 Web/PDF 将每条物理网格边画一次，合并区域使用 anchor cell 的边框，忽略 continuation
cell 的边框格式，并隐藏合并内部边。共享水平边优先取列坐标更靠右的锚点，列相同取上方格的
bottom；共享垂直边优先取行坐标更靠下的锚点，行相同取左方格的 right。优先边缺失时再取
另一侧，显式 `noFill` 仍是有效选择；不是粗线、直接格式或 CSS 冲突胜出。
表格外框回退按合并跨度是否到达周界判断，不只看 anchor 所在的物理格。
比较横向、纵向、二维合并的 dash、空边与实际行高，勿为恢复旧预览而复制边框、
加分割线 shape 或取消合并。缺失边与显式 noFill 不等价；写入字段仍以当前 table schema
为准，渲染改进不授予任意原始边框 XML 的编辑能力。升级诊断参见 `../review/fidelity-diagnosis.md`。

Web 边框 overlay 依赖挂载后的实际 cell 几何；内容撑高、行/列重新分配、隐藏页重新显示
或缩放后，应等字体与布局稳定再截图，并比较网格线与真实 cell 边界。初始声明尺寸不一定
等于最终浏览器尺寸；过早或隐藏状态的截图不能证明源表格行高错误。若稳定后仍偏移，
记录加载的 Viewer build、显示比例和复现步骤，不先向 PPTX 加补偿线或修改行高。

### 对象类型

编辑已有 deck 前先看 inspect。只有 `shapeType == "table"` 的对象才使用
`set-table`、`set-table-data`、`merge-table-cells` 等 table ops。

很多高设计感 deck 会用文本框 + 细矩形/连接线模拟表格。这类对象在 inspect 中通常表现为：

- 多个 `textBox` 单元格文字
- 多个 `autoShape` / `connector` / `freeform` 分割线
- shape name 常含 `TableCell`、`TableRowRule`、`TableColRule`、`Rule`、`Divider`
- 没有任何 `shapeType == "table"` 对象

遇到这种视觉表格时，不要强行使用 table ops；按普通 shape 编辑：

```nu
^xdoc pptx inspect input.pptx --json | from json
  | get slides.4.shapes
  | where shapeType in ["autoShape" "connector" "freeform"]
  | where ($it.name =~ "Table|Rule|Divider") or ($it.fillColor? != null) or ($it.lineColor? != null)
  | select --optional id name shapeType fillColor lineColor lineWidthEmu bbox
```

改视觉表格分割线颜色时，优先用这些 line/rule shape 的 `id` 或唯一 `name` 写
`set-shape`（线条属性放在嵌套的 `line` 对象里），再 dry-run 检查 `resolvedSelectors[]`。若分割线是
细矩形，通常要改 `fill`；若是 connector/freeform 线，通常要改 `line`。

## 创建

```json
{
  "op": "add-table",
  "slide": 0,
  "rows": 4,
  "columns": 3,
  "x": "1in",
  "y": "1.5in",
  "w": "8in",
  "h": "3in",
  "name": "Metrics Table",
  "data": [
    ["指标", "Q1", "Q2"],
    ["营收", "$10M", "$12M"],
    ["毛利", "$5M", "$6M"],
    ["NPS", "60", "62"]
  ]
}
```

`data` 可选 — 不写就是空表，后续用 `set-table` 的 `cells` 一格一格填，或 `set-table-data`
整表覆盖。

## 写数据

### 单元格

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": { "name": "Metrics Table" },
  "cells": [{ "row": 1, "column": 1, "text": "$12M" }]
}
```

`row` / `column` 都是 0-based。`cells` 数组一次可以写多格；同一格的 `text` 与
`formula` 互斥，同一 op 里同一格只能出现一次。

### 整表覆盖

```json
{
  "op": "set-table-data",
  "slide": 0,
  "shape": { "name": "Metrics Table" },
  "data": { "format": "matrix", "values": [["..."], ["..."]] },
  "resize": true
}
```

`data` 是对象，`format` 取值 `matrix / csv / json`；`matrix` 的 `values` 必须是
字符串二维数组。`resize: true` 会按 `data` 解析出的行列数**自动加减行列**（保留
grid widths / row heights / style flags / 合并属性）；`resize: false`（默认）则
数据维度必须与现有表一致，否则报错。

> 注意：`resize: true` 不会"打断"已有 merge —— 如果新尺寸会切到 merge 中间，
> 会结构化拒绝（不会强行截断）。

### 导入 CSV / JSON

```json
{
  "op": "set-table-data",
  "slide": 0,
  "shape": { "name": "Metrics Table" },
  "data": {
    "format": "csv",
    "text": "指标,Q1,Q2\n营收,$10M,$12M\n毛利,$5M,$6M\n"
  },
  "resize": true
}
```

JSON 形式：

```json
{
  "op": "set-table-data",
  "slide": 0,
  "shape": {...},
  "data": {
    "format": "json",
    "values": [
      ["指标", "Q1", "Q2"],
      ["营收", "$10M", "$12M"],
      ["毛利", "$5M", "$6M"]
    ]
  },
  "resize": true
}
```

`json` 格式的 `values` / `text` 二选一：`values` 直接给标量二维数组（数字、布尔、
null 会转成文本），`text` 给 JSON 字符串（解析后同样必须是标量二维数组）。header
不会自动推导，需要显式写成第一行。

## 样式

### 单元格样式

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": {...},
  "cells": [
    {
      "row": 0,
      "column": 0,
      "style": {
        "fill": { "type": "solid", "color": "1A73E8" },
        "font": { "name": "Inter", "size": "14pt", "bold": true, "color": "FFFFFF" },
        "alignment": "center",
        "verticalAnchor": "middle",
        "marginLeft": "6pt",
        "marginRight": "6pt",
        "marginTop": "4pt",
        "marginBottom": "4pt"
      }
    }
  ]
}
```

`alignment` 取值与段落对齐相同；`verticalAnchor` = `top / middle / bottom`。

### 边框（单格）

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": {...},
  "cells": [
    {
      "row": 0,
      "column": 0,
      "style": {
        "borders": {
          "top":    { "width": "1pt", "color": "1A73E8" },
          "bottom": { "width": "1pt", "color": "1A73E8" },
          "left":   { "width": "1pt", "color": "BFBFBF" },
          "right":  { "width": "1pt", "color": "BFBFBF" }
        }
      }
    }
  ]
}
```

每条边是 line 对象（`width` / `color` / `dash`；`noLine: true` = 去线，`dash: "none"` 或
`clearDash: true` 只清掉继承的虚线）。边不能写成 `"none"` 字符串（会报
`borders.top must be object`）。单格
`borders` 只支持 `top / right / bottom / left / cross`；`insideH` / `insideV`
属于区域边框（见下节）。style 里也可以写 `line` 一次性给四边同样式。

### 区域边框（批量加边框）

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": {...},
  "borders": [
    {
      "range": { "startRow": 0, "startColumn": 0, "endRow": 3, "endColumn": 2 },
      "value": {
        "top":     { "width": "1.5pt", "color": "1F1F1F" },
        "bottom":  { "width": "1.5pt", "color": "1F1F1F" },
        "left":    { "width": "1.5pt", "color": "1F1F1F" },
        "right":   { "width": "1.5pt", "color": "1F1F1F" },
        "insideH": { "width": "0.5pt", "color": "BFBFBF" },
        "insideV": { "width": "0.5pt", "color": "BFBFBF" },
        "cross":   { "width": "1pt",   "color": "1A73E8" }
      }
    }
  ]
}
```

- `top / bottom / left / right` 只作用于区域外缘（首行的上边、末行的下边、
  首列的左边、末列的右边），四条合起来就是外框
- `insideH` 内部横线
- `insideV` 内部竖线
- `cross` 对角线（不常用）

### 表格整体样式

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": {...},
  "style": {
    "firstRow": true,
    "lastRow": false,
    "firstColumn": false,
    "lastColumn": false,
    "horizontalBanding": true,
    "verticalBanding": false,
    "styleId": "{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"
  }
}
```

`styleId` 是 PowerPoint 内置表格样式 GUID — 不需要硬记，从 deck 里 inspect 一个
现有 styled table 抄一下就行。常用的"firstRow + banding" 组合就够 95% 场景。

## 列宽 / 行高

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": {...},
  "columns": [{ "column": 0, "width": "2in" }],
  "rows": [{ "row": 0, "height": "0.5in" }]
}
```

## 合并

```json
{
  "op": "merge-table-cells",
  "slide": 0,
  "shape": {...},
  "startRow": 0,
  "startColumn": 0,
  "endRow": 0,
  "endColumn": 2
}
```

横/竖向合并都用同一个 op，靠 startRow/Col + endRow/Col 表达范围。

## 静态公式

```json
{
  "op": "set-table",
  "slide": 0,
  "shape": {...},
  "cells": [{ "row": 4, "column": 1, "formula": "SUM(B2:B4)" }]
}
```

支持的公式：`SUM / AVG / AVERAGE / COUNT / MIN / MAX`。
**注意：** 这是**静态**公式 — xdoc 在生成时计算结果存入单元格，公式本身不写入
PowerPoint（PPTX 表格不像 Excel 那样有计算引擎）。再次改数据时需要手动重写公式或
用 `bind-data` 重新算。

## 表格 + `bind-data` 数据绑定

如果数据来自 JSON：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "add-table",
      "slide": 0,
      "rows": 1,
      "columns": 1,
      "x": "1in",
      "y": "1.5in",
      "w": "8in",
      "h": "3in",
      "name": "Metrics"
    },
    {
      "op": "bind-data",
      "data": {
        "rows": [
          ["指标", "Q1", "Q2"],
          ["营收", "$10M", "$12M"]
        ]
      },
      "bindings": [
        {
          "type": "table",
          "slide": 0,
          "shape": { "name": "Metrics" },
          "data": "{{rows}}",
          "resize": true
        }
      ]
    }
  ]
}
```

详见 `data-driven.md`。

## 完整示例：KPI 表

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    { "op": "add-slide" },
    {
      "op": "add-text-box",
      "slide": 0,
      "name": "Title",
      "x": "1in",
      "y": "0.5in",
      "w": "11in",
      "h": "0.8in",
      "text": "关键指标"
    },
    {
      "op": "add-table",
      "slide": 0,
      "rows": 4,
      "columns": 3,
      "x": "1in",
      "y": "2in",
      "w": "11in",
      "h": "3in",
      "name": "KPI",
      "data": [
        ["指标", "Q1 2026", "Q2 2026"],
        ["营收", "$10M", "$12M"],
        ["毛利率", "55%", "58%"],
        ["NPS", "58", "62"]
      ]
    },
    {
      "op": "set-table",
      "slide": 0,
      "shape": { "name": "KPI" },
      "style": { "firstRow": true, "horizontalBanding": true },
      "borders": [
        {
          "range": { "startRow": 0, "startColumn": 0, "endRow": 3, "endColumn": 2 },
          "value": {
            "top": { "width": "1pt", "color": "1F1F1F" },
            "bottom": { "width": "1pt", "color": "1F1F1F" },
            "left": { "width": "1pt", "color": "1F1F1F" },
            "right": { "width": "1pt", "color": "1F1F1F" },
            "insideH": { "width": "0.5pt", "color": "BFBFBF" }
          }
        }
      ],
      "cells": [
        {
          "row": 0,
          "column": 0,
          "style": {
            "fill": { "type": "solid", "color": "1A73E8" },
            "font": { "color": "FFFFFF", "bold": true }
          }
        }
      ]
    }
  ]
}
```

## 不要做的事

- ❌ 不要在 `set-table-data` 时假定 `resize: false` 会自动加减行列 — 不写 `resize: true`
  时维度必须严格匹配
- ❌ 不要对 table shape 用 `set-paragraph` / `add-paragraph` / `set-run`（会报
  `shape does not contain a text frame`）— 单元格内换行直接在 `set-table` 的
  `cells[].text` 里写 `\n`，每个 `\n` 会生成一个新段落
- ❌ 不要给已合并区域再次 merge（会冲突）
- ❌ 不要忘了 `set-table` 的 `cells[].formula` 是**静态**的 — 改基础数据后公式不会自动重算
