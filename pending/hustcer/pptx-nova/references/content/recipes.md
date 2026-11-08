# Recipes —— 高层意图 → 自动 patch

Recipe 是 xdoc 在 `add-slide.recipe` 中暴露的 **18 个严格页面意图**。相比手堆
`add-text-box`/`add-shape`，
recipe 预设了字体、间距与几何，适合页面原型或显式 patch 的组成部分；输入和展开结果仍须
校验、dry-run 及渲染复核。普通交付新建 deck 优先走本 skill 的 DeckKit 与标准 Create runner。

每个 recipe 都作为 `add-slide` 的 `recipe` 字段放进 patch JSON，并在执行时展开成底层
patch。先用 `xdoc schema --mode ops --ops add-slide --minimal` 获取当前严格字段，再通过 dry-run
审查 `expandedOps[]` 与 `createdObjects[]`。
`opResults[].expandedOps[]` 每项只含操作名 `{op}`，不能直接执行。
需要完整展开请求时，对 recipe envelope 执行
`xdoc pptx recipe --recipe recipe.json --compile --json`，读取返回的 `patch`
并按正常 patch 流程校验和 dry-run。该 CLI 输入使用 `schemaVersion: "pptx-recipe/v1"`，
与下面用于 `apply` 的 `pptx-patch/v1` envelope 不同；`recipeResults[].expandedOps[]` 仍是名称摘要。

## 通用 envelope

所有 recipe 都嵌进同一种 patch envelope：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    { "op": "add-slide", "recipe": { "kind": "title", "title": "..." } },
    {
      "op": "add-slide",
      "recipe": { "kind": "kpi-grid", "title": "...", "items": [...] }
    }
  ]
}
```

recipe 与底层 patch op 可以混用：一份 patch 可同时包含 `add-slide.recipe` 与
`set-theme`，按数组顺序观察并修改同一个 candidate state。`layout` 与 `recipe`
互斥，不能在同一个 `add-slide` 中同时提供。

## Recipe 速览

| 类型        | `add-slide.recipe.kind`                                                |
| ----------- | ---------------------------------------------------------------------- |
| 页面骨架    | `title`, `section`, `two-column`, `image-caption`                      |
| 指标 / 表格 | `kpi-grid`, `comparison-table`, `scorecard-table`, `comparison-cards`  |
| 商务图示    | `timeline`, `roadmap`, `matrix-2x2`, `process-flow`, `funnel`, `cycle` |
| 结构图示    | `swot`, `pyramid`, `hub-spoke`, `gantt`                                |

本文件展开核心页面 recipe。品牌改装使用 `set-theme` / `remap-theme`，详见
`styles-and-themes.md`。native diagram/table preset 的完整输入示例
放在 `references/content/charts.md` 的 "Native diagram/table presets"。

## 通用 `theme` 字段

所有页面 / KPI / table / diagram recipe 都接受可选 `theme`，会覆盖该页的样式：

```json
"theme": {
  "accent": "#1A73E8",
  "background": "#FFFFFF",
  "text": "#1F1F1F"
}
```

颜色支持 `#RRGGBB` / `RRGGBB`（大小写不敏感）。省略 `theme` 使用 recipe 内置默认值：
accent `3366CC`、background `FFFFFF`、text `111827`、muted `667085`。
它不会自动读取 deck 当前主题色；需要品牌配色时显式传入相应字段。

---

## 1. `recipe.kind: "title"` —— 封面 / 章节扉页

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "title",
    "title": "S8FY 季度业务回顾",
    "subtitle": "2026 Q2 · 业务部门"
  }
}
```

| 字段       | 必填 | 说明                             |
| ---------- | ---- | -------------------------------- |
| `title`    | ✅   | 主标题（非空字符串）             |
| `subtitle` |      | 副标题                           |
| `theme`    |      | 可选样式覆盖                     |
| `kind`     | ✅   | 固定 `"title"`，位于 `recipe` 内 |

适用：封面、章节扉页、模块引导页。

---

## 2. `recipe.kind: "section"` —— 大章节分割页

比 `title` 多一个 `eyebrow`（眉标），适合 PART 01 / 章节序号那种风格。

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "section",
    "title": "财务表现",
    "subtitle": "营收、利润率、现金流",
    "eyebrow": "PART 01"
  }
}
```

---

## 3. `recipe.kind: "two-column"` —— 左右对照页

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "two-column",
    "title": "新旧方案对比",
    "left": {
      "heading": "旧方案",
      "text": "依赖 python-pptx，需要本地运行环境",
      "bullets": ["运行慢", "无 dry-run", "错误不结构化"]
    },
    "right": {
      "heading": "新方案",
      "text": "xdoc CLI，单命令调用",
      "bullets": ["原生可编辑", "结构化错误", "可回放审计"]
    }
  }
}
```

`left` / `right` 都是 `{ heading?, text?, bullets?[], image?, caption? }` 对象，每侧至少给
一个字段（空对象会报 `add-slide.recipe.left requires field 'heading'` 之类的 union-no-match）；
`image` 结构同 `image-caption.image`（`bytesBase64` + `mimeType` + 可选 `objectFit`）。

---

## 4. `recipe.kind: "image-caption"` —— 大图 + 标题 + 说明

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "image-caption",
    "title": "新产品包装外观",
    "caption": "采用环保再生纸，符合 ESG 战略",
    "image": { "bytesBase64": "...", "mimeType": "image/png", "objectFit": "cover" }
  }
}
```

canonical v1 的 `image-caption.image` 严格接受 `bytesBase64`、`mimeType` 和可选
`objectFit`；本地文件先由生成器读取并编码，不要把 `assetSource` 塞进该 recipe。

---

## 5. `recipe.kind: "kpi-grid"` —— KPI 卡片网格（最适合季度报告）

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "kpi-grid",
    "title": "Q2 2026 关键指标",
    "items": [
      { "label": "营收", "value": "$42M", "delta": "+12% YoY" },
      { "label": "毛利率", "value": "58%", "delta": "+1.2pp" },
      { "label": "NPS", "value": "62", "delta": "+4" },
      { "label": "用户", "value": "1.2M", "delta": "+18%" }
    ]
  }
}
```

每个 `item` 形如 `{ label, value, delta? }`，3 字段都是字符串。可选 `delta`
作为标签文字输出，不自动计算涨跌，也不按正负号推导趋势颜色。

适合：仪表盘、季度报告、招股书指标页。

---

## 6. `recipe.kind: "comparison-table"` —— 比较表格

```json
{
  "op": "add-slide",
  "recipe": {
    "kind": "comparison-table",
    "title": "三家供应商对比",
    "headers": ["维度", "供应商 A", "供应商 B", "供应商 C"],
    "rows": [
      ["报价", "$1.2M", "$1.5M", "$0.9M"],
      ["交付", "8 周", "6 周", "10 周"],
      ["质保", "12 个月", "24 个月", "6 个月"]
    ]
  }
}
```

`headers` / `rows` 都是字符串数组；每一行 `rows[i].length` 必须等于 `headers.length`，
不一致时 dry-run 直接报错（`rows[0] must have N cells`），不会降级渲染。

---

## 品牌改装使用 `set-theme` / `remap-theme`

```json
{
  "op": "set-theme",
  "colors": {
    "accent1": "#1A73E8",
    "accent2": "#34A853",
    "accent3": "#FBBC04",
    "accent4": "#EA4335",
    "dk1": "#1F1F1F",
    "lt1": "#FFFFFF"
  },
  "fonts": {
    "major": { "typeface": "Inter" },
    "minor": { "typeface": "Inter" }
  }
}
```

`set-theme` 负责主题色与主题字体；需要把既有文本、形状、表格、图表映射到某个
theme pack 时使用 `remap-theme`。背景、母版 placeholder 和默认文本样式分别使用
当前 schema 披露的 `set-master` / `set-slide-background` / 文本样式 op，不再使用已删除
的高层 rebrand alias。

---

## Recipe 与 patch op 混用模式

下面这份 patch **同时**做 "一键改主题 + 加 KPI 页 + 加对比表"：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-theme",
      "colors": { "accent1": "#1A73E8" },
      "fonts": {
        "major": { "typeface": "Inter" },
        "minor": { "typeface": "Inter" }
      }
    },
    {
      "op": "add-slide",
      "recipe": { "kind": "title", "title": "Q2 2026 业务回顾" }
    },
    {
      "op": "add-slide",
      "recipe": {
        "kind": "kpi-grid",
        "title": "关键指标",
        "items": [
          { "label": "营收", "value": "$42M", "delta": "+12%" },
          { "label": "NPS", "value": "62", "delta": "+4" }
        ]
      }
    },
    {
      "op": "add-slide",
      "recipe": {
        "kind": "comparison-table",
        "title": "新旧方案",
        "headers": ["维度", "旧", "新"],
        "rows": [
          ["速度", "慢", "快"],
          ["可审计", "❌", "✅"]
        ]
      }
    }
  ]
}
```

执行：`xdoc pptx apply -p patch.json -o out.pptx --dry-run --json` 看
`expandedOps[]`。

## 何时降级到底层 patch op

- 自定义形状（不是 layout placeholder）
- 自定义图表样式 / 坐标精确控制
- 已有 deck 的局部修改（recipe 主要面向"加新页"）
- 需要 `set-shape` / `set-chart` 等细粒度 aggregate mutation

降级方法：去 `references/edit/patch-ops-cheatsheet.md` 找对应 op。
