# 控制流、宏与 Raw OOXML —— `if` / `foreach` / `try` / `define-macro` / `use-macro` / `patch-ooxml`

> 这五个控制/宏 op + 一个 raw OOXML 逃生口都是 patch envelope 内的"元 op"。
> `foreach` 和宏负责结构展开；`if` 与 `try` 保留在顺序解释器中，在执行到该位置时
> 观察当前 candidate state。
> 它们让单份 patch.json 能表达"按状态分支"、"对一组数据循环"、"局部 try-catch"、
> "命名宏复用"，以及在极少数边角场景下走 OOXML 直改逃生口。

## §1 控制流 / 宏 op 总览

| op             | 必填                | 可选                   | 何时用                                           |
| -------------- | ------------------- | ---------------------- | ------------------------------------------------ |
| `if`           | `condition`, `then` | `else`                 | 按 candidate 当前状态决定分支                    |
| `foreach`      | `items`, `do`       | `as`(默认 `"item"`)    | 对 JSON 数组循环展开（KPI 卡 / 表格行 / 时间线） |
| `try`          | `body`              | `catch`, `recoverable` | 事务式尝试；失败时丢弃 body candidate 后回退     |
| `define-macro` | `name`, `body`      | （无）                 | 注册一个命名宏 — 把可复用的 op 块抽出来          |
| `use-macro`    | `name`              | `args`                 | 展开命名宏，用 `args` 传 `{{args.*}}` 参数       |

**解释顺序**：patch 按数组顺序执行。宏与 `foreach` 可递归产生子 op；执行器到达
`if` 时才求值条件，到达 `try` 时在 branch-local candidate 上执行 `body`。结果会反映在
`dry-run` 报告的 `opResults[]` 里（含 `expandedOps[]`，元 op 展开出的底层 op 名列表），
方便你审计。带 `--explain` 还会在
`explanations[<i>].expandedOps` 里给出"该元 op 展开成哪些底层 op"。
`opResults[].expandedOps[]` 是 `{op}` 名称摘要，不包含完整参数，不能作为 patch 重放。

> canonical v1 schema 只接受上表字段；不要使用旧版控制流或宏字段别名。

源快照保护有独立执行边界：带 `sourceText` / `sourceHash` / `unitId` 的 `set-run`
和任何 `replace-paragraph-text` 只能放在顶层 `ops[]`。嵌套形式仅在实际执行到它时
返回 `invalid_argument`，包括 foreach 替换、已调用宏和 recipe 展开；未选分支与未调用
宏不报错。`try` 可按普通错误策略恢复且不提交失败 body。需要批量保护型编辑时，
由生成器显式产出顶层 ops，保留完整 guard；详见 `inspect-and-edit.md`。

## §2 `if` —— 按状态分支

```json
{
  "op": "if",
  "condition": {
    "kind": "slide-count",
    "op": "eq",
    "value": 0
  },
  "then": [
    {
      "op": "add-slide",
      "recipe": { "kind": "title", "title": "新建 deck" }
    }
  ],
  "else": [
    {
      "op": "set-text-frame",
      "slide": 0,
      "shape": { "placeholder": "title" },
      "text": "已存在的 deck"
    }
  ]
}
```

`condition.kind` 取值：

| kind               | 含义                                                          |
| ------------------ | ------------------------------------------------------------- |
| `slide-count`      | 当前 candidate state 的 slide 数                              |
| `selector-match`   | 配合 `shape` 字段，判断 selector 是否命中当前 candidate state |
| `property-compare` | 配合 `slide` + `shape` + `property`，比对该属性的当前值       |

操作符按条件类型选择，省略时默认 `eq`：

| 条件                  | 值和操作符                                                  | 必填与边界                                                                             |
| --------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `slide-count`         | integer；`eq/ne/gt/gte/lt/lte`                              | 必填 `value`，读取执行到此处的候选页数                                                 |
| `selector-match` 计数 | 非负 integer；`eq/ne/gt/gte/lt/lte`                         | 必填 `slide/shape/value`                                                               |
| `selector-match` 存在 | 不提供 `value/op`                                           | 必填 `slide/shape`；至少命中一个即 true                                                |
| `property-compare`    | string；`eq/ne/contains/not-contains/starts-with/ends-with` | 必填 `slide/shape/property/value`，`property` 为 `name/text`；0 匹配 false，多匹配报错 |

`slide` 为 0-based，`shape` 沿用互斥 selector 契约。各分支拒绝不适用字段、旧别名和错误类型；
属性比较不会把数字或布尔转成字符串。模板在替换前检查符号结构，替换后仍按上述运行时条件校验。
独立 `xdoc pptx recipe` 只静态展开建页 recipe；条件应放在普通 patch 中执行。

**典型用法**：

- "如果输入 deck 没标题占位符,就先 add-placeholder"
- "已有 ≥ 10 页,就跳过封面页直接进内容"
- "shape 名包含 'Logo' 才走 set-image"

## §3 `foreach` —— 数据驱动的循环展开

```json
{
  "op": "foreach",
  "items": [
    { "name": "KPI-Revenue", "label": "营收", "value": "¥42M", "delta": "+21.9%" },
    { "name": "KPI-Margin", "label": "毛利率", "value": "38%", "delta": "+3pp" },
    { "name": "KPI-NewUsers", "label": "新增用户", "value": "1.2K", "delta": "+18%" },
    { "name": "KPI-Churn", "label": "流失率", "value": "2.1%", "delta": "-0.4pp" }
  ],
  "as": "kpi",
  "do": [
    {
      "op": "add-text-box",
      "slide": 0,
      "name": "{{kpi.name}}",
      "x": "0.5in",
      "y": "3in",
      "w": "2.8in",
      "h": "1.4in",
      "text": "{{kpi.label}}\n{{kpi.value}}\n{{kpi.delta}}"
    }
  ]
}
```

关键点：

- `items` 必须是 JSON 数组；每个元素被赋给 `as` 变量（默认 `"item"`）
- 在 `do[]` 内部用 `{{kpi}}` 或 `{{kpi.field}}` 插值当前元素或其直接字段；
  字段名不加 `$`，不承诺递归路径解析
- `{"$var":"kpi"}` 将整个变量作为 JSON 值替换，必须是只有 `$var` 一个键的对象。
  例如循环 `items:[0]` 时可用 `"slide":{"$var":"item"}` 保持 integer 类型
- 不支持索引变量（无 `{{$index}}`）。要带序号请在 `items` 数组里预先填好
- 同一个 `foreach` 内可以嵌 `if` / 另一个 `foreach`,变量作用域逐层叠加

**典型用法**：

- 用单个 foreach 生成 4-across KPI 卡(代替手写 4 份重复的 add-shape/add-text-box)
- 时间线节点 / 议程编号卡 / 章节扉页批量化
- 把 CSV / JSON 数据源转成 deck 内容,**不必落地一个 template.pptx**(对比 `template-fill`)

> ⚠️ `foreach` 仍然不能脱离 patch op 自身的字段约束 — `add-text-box` 必须有
> `slide` / `x` / `y` / `w` / `h`。字符串插值的结果始终是 string，integer 字段
> 需要 JSON 变量或数字字面量。复杂坐标计算应该用
> JS 生成器(`assets/examples/generator/deck-generator-template.mjs`)在生成 items 时
> 算好,再交给 foreach 展开。

## §4 `try` —— 容错执行

```json
{
  "op": "try",
  "body": [
    {
      "op": "set-text-frame",
      "slide": 0,
      "shape": { "query": { "nameRegex": ".*-callout$" } },
      "text": "替换文字"
    }
  ],
  "recoverable": ["invalid_operation"],
  "catch": [
    {
      "op": "add-text-box",
      "slide": 0,
      "x": "0.5in",
      "y": "6in",
      "w": "12in",
      "h": "0.4in",
      "name": "fallback-callout",
      "text": "替换文字"
    }
  ]
}
```

- `recoverable` 列出可被 catch 接住的错误 `kind`：取值就是 dry-run 错误报告里的
  `error.code`（`invalid_operation` / `invalid_argument` / `missing_part` / `unsupported_feature` 等，
  见 `references/runtime/troubleshooting.md` 的 errorCatalog），`"*"` 匹配全部；其它错误仍然冒出。
  selector 找不到 / 多命中都是 `invalid_operation`；`missing-shape`、`ambiguous-selector`
  是 errorCatalog 的 scenario 名，不是 kind，写进 `recoverable` 不会生效
- 不给 `recoverable` 时所有错误都会被 catch（强烈不建议 — 容易掩盖 bug）
- `body` 在独立 candidate 上顺序执行；其中任一可恢复执行错误都会丢弃整个 body 的
  修改，再从进入 `try` 前的 candidate 执行 `catch`；`warnings[]` 里会出现
  `try recovered from <kind>: <message>`

**典型用法**：

- 给同一份 patch 在"修改已有 deck"和"从零创建"两种场景共用：先 try set-text-frame，
  catch 内 add-text-box
- 渐进迁移老版 deck 的 placeholder 名字（先按新名 set，catch 内按旧名 set）

> ⚠️ **try 块内的 `define-macro` 在失败时会被丢弃**：try 主分支失败、走 catch 分支
> 时，try 内部 `define-macro` 的宏会被清理（避免半成品宏污染后续 op）。如果你需要
> "尝试 + 失败回退" 同时定义一个宏，把 `define-macro` 放到 try 外面或 catch 外面。

## §5 `define-macro` / `use-macro` —— 命名宏 / 参数化 op 块

`define-macro` / `use-macro` 让你把"反复写"的一组 ops 抽出来命名复用，参数通过
`args` 注入、模板里用 `{{args.<field>}}` 引用，dry-run 报告里 `use-macro` 的
`expandedOps[]` 会列出展开成的底层 op。

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "define-macro",
      "name": "metricBox",
      "body": [
        {
          "op": "add-text-box",
          "slide": 0,
          "x": "{{args.x}}",
          "y": "{{args.y}}",
          "w": "2in",
          "h": "0.6in",
          "name": "{{args.name}}",
          "text": "{{args.label}}\n{{args.value}}"
        }
      ]
    },

    { "op": "add-slide" },

    {
      "op": "use-macro",
      "name": "metricBox",
      "args": {
        "x": "0.5in",
        "y": "3.2in",
        "name": "kpi-revenue",
        "label": "营收",
        "value": "¥42M"
      }
    },
    {
      "op": "use-macro",
      "name": "metricBox",
      "args": {
        "x": "3.5in",
        "y": "3.2in",
        "name": "kpi-margin",
        "label": "毛利率",
        "value": "38%"
      }
    }
  ]
}
```

### 5.1 字段约束

| op             | 字段   | 类型             | 说明                                                              |
| -------------- | ------ | ---------------- | ----------------------------------------------------------------- |
| `define-macro` | `name` | 非空字符串       | 宏名；同一份 patch 内**不能重复定义**（重定义直接报错）           |
| `define-macro` | `body` | array            | 任意 patch op；可以嵌 `if` / `foreach` / `try` / 甚至 `use-macro` |
| `use-macro`    | `name` | 非空字符串       | 要引用的宏；**必须先 `define-macro`** 后才能 `use-macro`          |
| `use-macro`    | `args` | object（可省略） | 暴露给宏体内的 `{{args.*}}` 占位符；省略 = 空对象                 |

`{{args.field}}` 在 `use-macro` 展开时做**字符串插值**（与 `foreach` 的 `{{item.x}}`
同机制），访问 `args` 的直接字段。`{"$var":"args"}` 可替换整个 JSON 对象，
例如把宏的 `condition` 写成该对象、通过 `args` 传入完整条件。插值后的 op
仍进入 schema 校验，所以坐标、枚举和数值字段必须保持各自的合法类型。

### 5.2 嵌套与递归

- `use-macro` 之间可以串调用：宏 A 内部可以 `{ "op": "use-macro", "name": "B" }`
- **递归深度上限 16 层**：超过会报 `macro expansion exceeded depth limit 16`，
  自递归 / 互相递归两种死循环都会被这个限制兜住
- 宏注册表是 **全局共享** 的：从第一次 `define-macro` 开始一直存活到 patch 结束；
  顺序上 `define-macro` 必须排在它的 `use-macro` 前面

### 5.3 何时用宏 vs. `foreach` vs. JS 生成器

| 你想做                          | 选什么                                        |
| ------------------------------- | --------------------------------------------- |
| 4 张相同形状 KPI 卡（数据不同） | `foreach` —— 一份 items + 一份 do             |
| 同一页里 2-3 处样式一致的小组件 | `define-macro` + 2-3 次 `use-macro`（更可读） |
| 多页都要用的"标准 callout 卡片" | `define-macro` 一次，每页 `use-macro`         |
| 100+ ops、跨页/复杂坐标计算     | JS 生成器（`define-macro` 解决不了坐标计算）  |

**宏的边界**：

- `{{args.*}}` 只做字符串插值，**不做算术**（要算坐标用 JS 生成器在外面算好）
- 宏体内引用的 selector / id 仍然要遵守 `nm()` 命名规范，否则 resolvedSelectors
  会报 not-found（见 `../create/deck-generator-workflow.md` 的命名 helper 规范）
- 宏 **不会被持久化**到生成的 PPTX 里 — 它纯粹是 patch JSON 的"复用快捷方式"

### 5.4 常见错误

| 错误                                         | 原因                                               | 修复                                               |
| -------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| `use-macro references undefined macro 'foo'` | `use-macro` 在 `define-macro` 之前出现，或宏名拼错 | 把 `define-macro` 移到 `use-macro` 前面 / 校对名字 |
| `define-macro macro 'foo' already exists`    | 同一份 patch 里 `define-macro` 了两次同名宏        | 用唯一名字，或拆成不同 patch                       |
| `macro expansion exceeded depth limit 16`    | 宏自递归或互相递归                                 | 拆开递归边界，或在宏体内用 `if` 加终止条件         |
| `try recovered from ...`（warnings 里）      | try 内 `define-macro` 被 catch 接住，宏被丢弃      | 把 `define-macro` 移出 try 块                      |

## §6 `patch-ooxml` —— 逃生口（默认禁用）

```bash
xdoc pptx apply -p patch.json -o out.pptx --allow-raw-xml --dry-run --json
```

```json
{
  "op": "patch-ooxml",
  "target": "ppt/slides/slide1.xml",
  "xpath": "//a:hlinkClick/@tooltip",
  "action": "set",
  "value": "Open the product demo"
}
```

字段：

| 字段     | 说明                                                                                                                                                                                                                                                       |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `target` | OPC 部件路径（`.xml` / `.rels` 结尾，禁止 `..` 路径穿越）                                                                                                                                                                                                  |
| `xpath`  | 受限 XPath；支持 `/`、`//`、元素名路径和最终 `/@attribute`，不支持 predicate/filter                                                                                                                                                                        |
| `action` | `set`(替换文本) / `add`(追加子元素) / `remove`(删除节点) / `replace`(整节点换)；守卫 action `repair-child-order` / `repair-preset-adjustments` 用 `expectedPartSha256`+`repairs`，`repair-relationships` 用 `relationshipRepairs`，三者 `xpath` 均固定 `/` |
| `value`  | 文本或 raw XML 片段；`set/add/replace` 必填，`remove` 与所有 repair action **不能带**                                                                                                                                                                      |

**安全约束**：

- `set/add/remove/replace` 必须显式加 `--allow-raw-xml` 旗标（否则报
  `patch-ooxml requires xdoc pptx apply --allow-raw-xml`）；守卫 action
  `repair-child-order` / `repair-preset-adjustments` / `repair-relationships` 不需要。
  preset 修复必须显式采纳报告建议，不能自动重试；其精确 part hash 不允许退回
  element-only guard。完整流程见 `../runtime/troubleshooting.md`，不要手写这些 guard。
- 普通 `set/add/remove/replace` **不接受** `expectedPartSha256`，也没有运行时源摘要
  guard。记录输入文件 SHA-256，在 apply 前确认仍是 dry-run 的原始字节；有变化就重新
  inspect/dry-run。不要给普通 action 填 repair 字段来制造“已防陈旧”的保证。
- `repair-relationships` 要区分现有与缺失 `.rels`：现有 part 的 add/retarget 都要求
  `expectedPartSha256`，retarget 还要求每项 `expectedTarget`；新建缺失 part 只允许 add，
  且禁止 `expectedPartSha256`。按当前 action schema 和已审阅修复建议构造；owner、
  target/type 校验仍执行，不能把新建规则套到已有 part 或省略 retarget 的旧目标。
  retarget 只修复当前目标 part 已缺失的关系，不是任意重定向已有有效关系的工具。
- `target` 只接受 OPC 包内部部件路径,会拒绝任意路径穿越
- 普通 raw mutation 会 emit `semanticChanges[]`(category=`rawOoxml`)和 `visualRisks[]`
  (code=`patch-ooxml`, severity=`high`, "raw OOXML patch bypasses the schema-v1 semantic contract")
- raw XML 内容不受 typed op 的完整字段约束；dry-run/apply 仍执行全包语义前后差分，
  可能发现子元素顺序、关系和 preset adjustment 等问题。没有新增 issue 也不证明
  Office 保真；最终补全量 semantic/compat、渲染和适用的 PowerPoint clean-open。

**XPath 能力边界**：

| 写法                             | 支持 | 说明                                           |
| -------------------------------- | ---- | ---------------------------------------------- |
| `/p:sld/p:cSld/p:spTree`         | ✅   | 绝对元素路径；命名空间前缀会按 local-name 匹配 |
| `//a:t`                          | ✅   | 递归选择所有同名元素                           |
| `//a:hlinkClick/@tooltip`        | ✅   | 最后一段可以是 attribute，用于批量设/删属性    |
| `//a:hlinkClick[@tooltip=x]`     | ❌   | 不支持 predicate 或按属性值筛选                |
| `//p:sp[1]`                      | ❌   | 不支持索引筛选                                 |
| `//*[@id]` / `//a:*`             | ❌   | 不支持 wildcard                                |
| `contains(...)` / `text()`       | ❌   | 不支持函数                                     |
| <code>//a:t &#124; //p:ph</code> | ❌   | 不支持 union                                   |

如果需要"按属性值定位某个节点后再改"，不要在 raw XPath 中反复试 predicate；
优先使用已有 patch op、先用 inspect 定位稳定 selector，或拆成更具体的常规编辑能力。
raw 逃生口只适合你已经确认目标路径足够窄、批量命中也可接受的场景。

**何时用**:

- 标准 patch op 表达不了的 OOXML 边角场景(e.g. 直接调字符级 `<a:rPr lang="zh-CN">`,
  改 `<p:transition>` 子节点的高级属性等)
- 给已有 deck 做"批量正则替换" — 比常规 `set-text-frame` 更直接但风险更高
- **不要用来做** recipe / patch op 已经覆盖的事(字体颜色、对齐、placeholder 等);
  那等于自废 schema 校验、走老路。

## §7 与 `bind-data` / `template-fill` 的关系

| 路线            | 模板需要存在?        | 数据源                | 适合场景                                    |
| --------------- | -------------------- | --------------------- | ------------------------------------------- |
| `template-fill` | ✅ `.pptx` 文件      | JSON / 命令行         | 同一份品牌模板 + 多份数据反复出 deck        |
| `bind-data`     | ❌ 在同一 patch 创建 | 内联 / 外部 JSON      | 一次性 deck,数据与样板同源                  |
| `foreach` op    | ❌                   | patch 内 `items` 字段 | 单页内重复结构(KPI 卡 / 议程项 / 行)        |
| `if` op         | ❌                   | 输入 deck 状态        | 同一份 patch 在"新建"和"修改"两种入口下复用 |

**配方**:中大型 deck 推荐 JS 生成器 + `foreach` 混用 — 生成器算 items 数组 +
统一坐标,foreach 展开重复结构,patch 体积小、可维护性高。

## §8 调试技巧

- dry-run 报告的 `opResults[]` 里,展开过的元 op 会在 `expandedOps[]` 列出子 op 名;
  有歧义时顶层 `error.suggestions[]` 会带修复建议
- `recoverable` 写错 kind 名（例如写成 scenario 名 `missing-shape`）→ try 块照样冒错;
  kind 取 dry-run 报告 `error.code` 的值(`invalid_operation` 等),对照 `references/runtime/troubleshooting.md` 的错误名
- `foreach` / `use-macro` 模板占位符都**不带 `$`**:`{{item.x}}` / `{{kpi.label}}` /
  `{{args.x}}`。写成 `{{$item.x}}` 不会报错 — schema 把它当成普通字面量字符串原样写入。
  看 dry-run `semanticChanges[]` 里的 text 字段(或 `--explain` 的 `expandedOps`)确认占位符是否被替换;
  `{"$var": "name"}` 是唯一带 `$` 的写法,用于整值 JSON 替换
- 排查宏展开:`xdoc pptx apply -p patch.json -i in.pptx --dry-run --explain --json`
  会在 `explanations[<i>].expandedOps` 列出每个 `use-macro` 展开成哪些底层 op

## §9 不要做的事

- 不要用 `patch-ooxml` 修改 `[Content_Types].xml` 或 `.rels` 关系图谱以外
  的元数据 — 几乎一定会破坏 OPC 包结构
- 不要发明 `if.condition.kind` —— 只有 `slide-count` / `selector-match` / `property-compare`
  三种，没有 `count` 之类的 expand 期累加器;要检验 deck 状态(slide 数 / shape 命中数)
  就用这三种
- 不要把 `foreach` 当 SQL —— 不支持 `where` / `sort` / `groupBy`。需要时在
  JS 生成器里预处理 `items` 数组
- 不要把所有错误都丢进 `try.catch[]` —— 没有 `recoverable` 列表时,真正的字段
  错误也会被 catch 掉,debug 极痛苦
- 不要把 `define-macro` 放进 `try.body` 期望失败时还能 `use-macro` —— catch 分支会清掉 try
  里注册的宏,后续 `use-macro` 直接报 `undefined macro`
- 不要在 `{{args.*}}` 里塞表达式(`{{args.x + 1in}}` 不工作);坐标算式放到 JS
  生成器里算好,再用计算结果调 `use-macro`
