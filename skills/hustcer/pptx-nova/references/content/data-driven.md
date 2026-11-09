# 数据驱动 Deck —— template-fill + bind-data

数据驱动场景的核心思路：**模板与数据分离**。Deck 里写占位符 `{{path}}`，数据塞在
JSON 里，xdoc 渲染时把占位符替换成真值。

适用：

- 季度报告，每季度数据变但版式不变
- 产品 catalog（同一模板 × N 个 SKU）
- 客户提案（同一框架 × N 个客户）
- 销售/运营 dashboard

## 两条路径

```
路径 1：template-fill (有模板文件)
  template.pptx  +  data.json  +  bindings.json
        │              │              │
        └──────────────┴──────────────┘
                       ▼
                  out.pptx

路径 2：bind-data (模板与数据同 patch)
  patch.json (内含 add-slide + add-shape + bind-data op)
        │
        ▼
  out.pptx
```

## 路径 1：`template-fill`（推荐：模板复用率高）

### 1.1 准备模板

用 PowerPoint 或 xdoc 提前做一份 `template.pptx`，在文本里写占位符：

```
标题占位:   "{{title}}"
副标题:     "{{subtitle}}"
KPI 营收:   "{{kpi.revenue.value}}"
KPI 变化:   "{{kpi.revenue.delta}}"
```

占位符语法：

| 语法                          | 含义                                                       |
| ----------------------------- | ---------------------------------------------------------- |
| `{{path}}`                    | 取 `data.path`，可路径 dot 嵌套（`{{kpi.revenue.value}}`） |
| `{{.}}`                       | 取当前 scope 值（在 `{{#each}}` 里指当前元素）             |
| `{{$.path}}`                  | 从根 data 取（在 nested scope 里逃出）                     |
| `{{#each items}}...{{/each}}` | 列表循环                                                   |
| `{{#if path}}...{{/if}}`      | 条件渲染                                                   |

### 1.2 准备 data.json

```json
{
  "title": "Q2 2026 业务回顾",
  "subtitle": "Aug 2026 · 业务部",
  "kpi": {
    "revenue": { "value": "$42M", "delta": "+12%" },
    "nps": { "value": "62", "delta": "+4" }
  },
  "rows": [
    ["指标", "Q1", "Q2"],
    ["营收", "10", "12"]
  ],
  "quarters": ["Q1", "Q2", "Q3", "Q4"],
  "series": [{ "name": "Revenue", "values": [10, 12, 14, 16] }]
}
```

### 1.3 准备 bindings.json（必填）

`bindings.json` 列出全部绑定目标：文本 shape 用 `text`，table / chart 用整体绑定；没有出现在
bindings 里的 shape 不会被触碰：

```json
[
  {
    "type": "text",
    "slide": 0,
    "shape": { "name": "Title" }
  },
  {
    "type": "table",
    "slide": 0,
    "shape": { "name": "Metrics" },
    "data": "{{rows}}",
    "resize": true
  },
  {
    "type": "chart",
    "slide": 0,
    "shape": { "name": "Revenue Chart" },
    "data": {
      "categories": "{{quarters}}",
      "series": "{{series}}"
    }
  }
]
```

| binding.type | 行为                                                                                     |
| ------------ | ---------------------------------------------------------------------------------------- |
| `text`       | shape 内所有 text run 中的 `{{path}}` 都做替换                                           |
| `table`      | 整张表用 `data` 里的二维数组覆盖（可 `resize: true`）                                    |
| `chart`      | 用 `data.categories` + `data.series` 替换 chart 数据                                     |
| `layout`     | 用 `layout` + `content` 填充内置 layout contract（可选 `contract: "strict" \| "loose"`） |

> `--bindings` 是必填项（缺省报 `xdoc pptx template-fill requires --bindings`，退出码 2）；
> xdoc 不会自动扫描所有 shape，只替换 bindings 里列出的 `text` shape。

### 1.4 执行

```bash
xdoc pptx template-fill data.json \
     --template template.pptx \
     --bindings bindings.json \
     -o out.pptx
```

`--bindings` 不可省；`-o` 已存在时需要 `--overwrite`。

## 路径 2：`bind-data` op（推荐：临时一次性 deck）

一次 patch 同时定义模板 + 数据，不需要预先做 template.pptx：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    { "op": "add-slide" },
    {
      "op": "add-text-box",
      "slide": 0,
      "x": "0.5in",
      "y": "0.5in",
      "w": "4in",
      "h": "0.6in",
      "name": "Headline",
      "text": "{{title}} / {{kpi.revenue}}"
    },
    {
      "op": "add-table",
      "slide": 0,
      "rows": 1,
      "columns": 1,
      "x": "0.5in",
      "y": "1.3in",
      "w": "4in",
      "h": "1in",
      "name": "Metrics"
    },
    {
      "op": "add-chart",
      "slide": 0,
      "kind": "column",
      "x": "5in",
      "y": "1.3in",
      "w": "4in",
      "h": "3in",
      "name": "Sales",
      "data": {
        "categories": ["placeholder"],
        "series": [{ "name": "placeholder", "values": [0] }]
      }
    },
    {
      "op": "bind-data",
      "data": {
        "title": "QBR",
        "kpi": { "revenue": "$42M" },
        "rows": [
          ["Metric", "Value"],
          ["Revenue", "42"]
        ],
        "quarters": ["Q1", "Q2"],
        "series": [{ "name": "Revenue", "values": [10, 20] }]
      },
      "bindings": [
        { "type": "text", "slide": 0, "shape": { "name": "Headline" } },
        {
          "type": "table",
          "slide": 0,
          "shape": { "name": "Metrics" },
          "data": "{{rows}}",
          "resize": true
        },
        {
          "type": "chart",
          "slide": 0,
          "shape": { "name": "Sales" },
          "data": { "categories": "{{quarters}}", "series": "{{series}}" }
        }
      ]
    }
  ]
}
```

执行：

```bash
xdoc pptx apply -p patch.json -o out.pptx
```

`bind-data` op 也支持把 data 放外部文件：

```json
{
  "op": "bind-data",
  "source": { "path": "data/q2.json" },
  "bindings": [...]
}
```

配合 `--asset-root` 安全 materialize。

## 高级：列表与条件

### `{{#each items}}`

模板：

```
{{#each products}}
  {{name}} - {{price}}
{{/each}}
```

数据：

```json
{
  "products": [
    { "name": "A", "price": "$10" },
    { "name": "B", "price": "$20" }
  ]
}
```

输出：

```
A - $10
B - $20
```

### `{{#if path}}`

模板：

```
{{#if isPaid}}
  ✅ 已付款
{{/if}}
```

`isPaid` 为 truthy（非空字符串、非 0、非 false、非 null、非空数组/对象）时渲染块内内容。

### 嵌套（当前不支持）

当前运行时（xdoc 0.20.0）**不支持**嵌套 `{{#each}}`（报 `bind-data template has
unterminated each block`），也不支持 `{{../path}}`（报 `bind-data template path not
found: ../name`）。`{{#each}}` 块内只能用 `{{.}}`、当前元素字段和 `{{$.path}}`（根 data）；
多层数据请先在 data.json 里拍平成单层列表。

## 检验 binding 结果

写完 `template-fill` / `bind-data` patch 后：

```bash
xdoc pptx apply -p patch.json -o out.pptx --dry-run --json | jq '.opResults[] | select(.op == "bind-data")'
```

看 `status` / `semanticChanges` / `warnings`（bind-data 的 `analysis` 为 `null`）。data 里找不到的 path
不是 warning，而是整条 op 失败：`invalid_argument` / `bind-data template path not found: <path>`。

## 常见错误

| 现象                                  | 原因                               | 解决                                     |
| ------------------------------------- | ---------------------------------- | ---------------------------------------- |
| `{{title}}` 没替换，原样输出          | 该 shape 没有进入 bindings         | 补 `text` binding                        |
| `bind-data template path not found`   | data 里没 `title` 字段或 path 错   | 检查 data.json                           |
| `{{products}}` 直接输出 JSON 数组文本 | 想循环但漏了 `{{#each}}`           | 加 `{{#each}}`                           |
| Table binding 报维度不匹配            | 没加 `resize: true` 且行列数不同   | 加 `resize: true`                        |
| Chart 数据全是 0                      | binding path 错或 chart 模板未绑定 | 检查 bindings.json 的 path 与 chart name |
| 中文乱码                              | data.json 不是 UTF-8               | 转 UTF-8                                 |

## template-fill vs bind-data 选哪个

| 场景                                         | 选                                                                           |
| -------------------------------------------- | ---------------------------------------------------------------------------- |
| 模板会复用 N 次（每月报告等）                | `template-fill`                                                              |
| 一次性生成 deck，模板 / 数据都在 patch 里    | `bind-data`                                                                  |
| 模板由设计师在 PowerPoint 里维护             | `template-fill`                                                              |
| 模板需要程序化生成（每个 AI 请求都不同布局） | `bind-data`                                                                  |
| 数据量大 / 来源是外部 JSON 文件              | 都行，建议 `template-fill` 或 `bind-data + source.path`（配 `--asset-root`） |

## 不要做的事

- ❌ 不要把 `{{path}}` 写在 shape `name` 字段里 — 只支持文本内容
- ❌ 不要在 binding `data` 字段里写裸字符串（如 `"rows"`）— 必须 `"{{rows}}"`
- ❌ 不要假设 `template-fill` 会创建新页 — 它只填充模板里已有的 placeholder / shape
- ❌ 不要忘了 chart data 类型要匹配（column/line 用 `{categories, series}`，scatter 用 `{points}`）
- ❌ 不要用新增 overlay 文本框遮住模板占位符来完成填充；`template-fill` 应填充模板已有 placeholder /
  shape，无法填充时先修模板或改走 Template Following。
- ❌ 不要忽略空 placeholder。模板中未绑定的 title/body/date/footer/slide-number 占位符必须填充、
  删除或在交付摘要中列为阻塞风险。
