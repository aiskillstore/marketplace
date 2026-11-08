# xdoc Schema 渐进式披露

xdoc 的 `schema` 子命令是机器可读的 JSON Schema 入口。完整输出包含操作、定义、示例和报告合同，
体积随版本与格式变化；按需获取投影，避免每次加载完整 schema。

## Focused Lookup and Output Flags

When unsure, first check exact capability truth, then the op index in `xdoc-capabilities.json`; use
`xdoc schema --mode index` only when the snapshot is missing or stale. Then use
`xdoc schema --mode ops --ops <name> --fields <needed-fields> --defs summary --minimal` when the snapshot discloses
both `--fields` and `--defs summary` and only a focused contract surface is needed; otherwise omit
`--defs` for the compatible full-definition projection. Summary projections are discovery views, not
complete validation schemas: switch to `--defs full` with the same `--fields` before constructing
nested selectors. Even a full-definition field projection remains incomplete; omit both `--fields`
and `--defs`, or use `apply --dry-run`, before treating a patch as valid. Read
theme/style/native DeckKit information from matching snapshot catalogs. Derive selectors from inspect, the
target op schema, then dry-run suggestions. For PPTX CLI syntax, use `xdoc pptx <action> --help`; this
schema-backed human synopsis is neither machine schema nor JSON.

For a `partial` feature, read its limits and `recommendation.operations` / `target`; an empty
`operations` list does not cancel that explicit recommendation. For example, existing model-host
geometry and semantic model authoring have different contracts. Probe `--require-feature` requires
the exact entry to be fully `supported`, so its strict failure for a `partial` entry is expected.
Use operation discovery plus the declared subset's dry-run/readback evidence for a bounded task;
do not relabel the feature as fully supported to satisfy that flag.

Do not append `--json` to top-level `xdoc convert` or `xdoc check` by default. For structured PPTX PNG
previews, prefer `xdoc pptx preview --json`; for structured single-file preflight results, prefer
`xdoc check ... -o check.json`. If the current `xdoc-capabilities.json#capabilities.commandFlags` or
`xdoc <command> --help` discloses `--report`, treat it only as a report/summary sidecar, not as a
replacement for `preview.json` or single-file `check.json`.

### CLI invocation and argument failures

For automation, prefer explicit commands such as `xdoc convert ...` and `xdoc pptx inspect ...`
over conversion shorthand. Pass an argument array to a process API instead of interpolating a shell
command. Use resolved absolute input paths, especially for filenames that resemble commands or
options. When using `--` to separate literal positional inputs, place the command, action and all
options before it. Absolute paths also avoid older runtimes' help/calendar token ambiguity.

Build options from the exact action contract, not just its parent command: a flag listed under
`pdf` or `pptx` may be invalid for a particular action. Omit absent optional values and disabled
`style: "flag"` booleans; do not emit empty values, `undefined`, `--flag=false`, or invented `--no-*`
options. Supply CLI `int` values as canonical decimal signed 32-bit integers without unnecessary
leading zeros, then respect the action's range constraints. Current runtimes reject malformed or
overflowing integers during parsing, including options that the selected action would otherwise
reject as inapplicable; they do not silently substitute defaults. Older parsers may do so; do not
rely on that behavior or use a parser failure to infer anything about the document.

Request help in a separate, clean invocation such as `xdoc pdf render --help`; do not append it to
an incomplete command with a missing string value. Newer runtimes distinguish help from literal
`--help` input operands and show root help for a bare `xdoc` invocation. Help success only proves
discovery worked. On exit 2, preserve stderr and correct the invocation using action help/schema;
there may be no JSON report. See [argument failure recovery](troubleshooting.md#cli-argument-failures).
Put the action before `--help`: `xdoc pdf render --help` selects action help, while
`xdoc pdf --help render` selects PDF command help. After `--`, help-looking tokens remain literal
operands. Even an invalid integer may coexist with a successful help request; validate the actual
invocation separately and never infer numeric acceptance or task authorization from help output.

### Optional shell completion

When the current snapshot discloses `completions`, read `xdoc schema --command completions` for
accepted shells. `xdoc completions bash`, `xdoc completions zsh`, or `xdoc completions fish` prints
a shell script, not JSON. Generation does not install it or edit shell configuration. Generate or
reload it after a CLI upgrade when the user wants interactive completion; it is not a prerequisite
for Agent workflows. Completion candidates do not prove capability support or task authorization.

### Apply report detail

When `xdoc schema --command pptx.apply` discloses `detailModes`, `apply --detail summary`
(including `--dry-run`) reduces long semantic before/after strings in stdout; the default is
`full`, unlike `pptx diff`'s default summary. Strings over 1024 UTF-8 bytes are omitted and
represented in `valueSummaries[]` by JSON Pointer `path`, `utf8Bytes`, SHA-256 and a preview of
at most 128 Unicode scalars. This also applies to completed `opResults` in error reports.
Authored patches, candidate validation and sidecars keep complete values; omission is not null,
deletion or proof of an unchanged value. Keep `full` for runners/gates requiring exact values.
Use summary for interactive inspection only when the consumer can handle omissions, retain its
report, and inspect the complete patch/sidecar or a full dry-run when the exact value matters.
Unlike `diff --output`, apply summary does not promise a retained full-report sidecar.

## 拉法

```bash
xdoc schema                          # 完整 schema（贵）
xdoc schema --mode capabilities      # 工作流能力清单，不含完整校验树
xdoc schema --command auth.status    # 单命令合同及其报告引用闭包
xdoc schema --command pptx.preview   # 渲染参数与报告合同
xdoc schema --report pptx-diff/v1     # 按 schemaVersion 取报告合同
xdoc schema --mode index                  # 只 op 名 + summary + required/optional 字段 + constraints
xdoc schema --mode ops --ops add-text-box         # 单个 op 完整 jsonSchema
xdoc schema --mode ops --ops add-slide,add-chart   # 多个 op
xdoc schema --mode ops --ops set-shape --fields name,shape,slide --defs summary --minimal # 字段 + 紧凑定义摘要
xdoc schema --mode ops --ops set-shape --fields name,shape,slide --defs full --minimal # 字段 + 完整定义闭包
xdoc schema --mode examples               # 当前运行时的 patch 示例
xdoc schema --minimal                # 删 verbose 字段（与上面任一组合用）
```

约束：视图由 `--mode` 明说，不靠优先级推断——`--ops`/`--fields` 只属于 `--mode ops`，
用在别的 mode 上直接报错。`--fields` 的 required 字段会自动保留，未知字段直接报错；
`--defs` 只用于字段投影，因此也要求 `--fields`，默认值为 `full`。
`--command` 与 `--report` 互斥，也不能与 `--mode`、`--ops`、`--fields`、`--defs`
混用；两者都支持 `--minimal`。命令名使用点分路径，报告名使用确切的 `schemaVersion`。
只有不带任何选择器时，省略 `--mode` 才回退完整 schema；传 `--command` / `--report`
时不要由包装器自动补 `--mode full`。定向报告闭包还会跟随命名 `*SchemaRef` 引用，
保留其原始 JSON Pointer 路径；不要只处理 `$ref` 或拼接旧 snapshot 来补定义。

能力探测同时读取 `schemaDisclosure.modes` 和 `schemaDisclosure.refinements`；
新版将 `--fields` / `--defs` 放在 refinements，旧版可能放在 modes。
`commands.schema.disclosure` 也可提供这份合同。以当前 snapshot 的
`fieldsAvailable` / `summaryDefsAvailable` 选路，不因 mode 列表里没有字段 flag
而退回完整 schema；未披露时仍用当前 help/schema 确认。

## Action 级 CLI 帮助

只需要确认某个 PPTX action 的调用方式时，先用低成本的 action help，无需拉完整 schema：

```bash
xdoc help                         # 根帮助
xdoc help pptx                    # PPTX action 总览
xdoc pptx apply --help            # apply 的 usage / options / examples
xdoc help pptx visual-audit      # 等价的 help verb 形式
```

每个 `xdoc pptx <action> --help` 都由运行时
`commands.pptx.subcommands.<action>` 合同生成；其中 option 定义投影自同一 PPTX 父命令，
因此适合发现 CLI flag、默认值和示例。它不是 patch operation JSON Schema：需要字段类型、
selector、enum 或完整校验合同，仍按下文使用 `xdoc schema --mode ops --ops ...`。help 是人类文本，
不要附加 `--json` 或把输出当 JSON 解析。

从 help 探测参数时只认 `Options` 中的声明行（如 `  -o, --output <path>`），
不要把描述、续行或示例里提到的其他命令参数当成当前命令的能力。
`cli/runtime/probe.mjs` 的 `commandFlags` 使用同样规则；例如正文建议
`pptx preview --json`，并不表示顶层 `convert` 支持 `--json`。

## 典型 Agent 用法

### Command / report 合同不在 op 投影里

用户要求安装、续期或诊断 Runtime 授权时，先读[授权安装与诊断](licensing.md)的执行流程；
本节负责命令参数和报告引用的精确发现。

`--mode index` / `--mode ops` 和 skill 的 capability snapshot 用于渐进发现，不包含完整
auth、渲染参数或报告校验合同。需要这些内容时，将 `xdoc schema --command <command.action>`
或 `xdoc schema --report <schemaVersion>` 保存到 run 目录，再读取原位置的参数和
`ioContract.stdout.schemaRef`。按 JSON Pointer 解引用到同一份 schema；`~1` 表示 `/`，
`~0` 表示 `~`。不要从报告名称猜引用位置：diff 指向 `commands.pptx.diffReportSchema`，
auth 的各动作指向根 `reports`。

定向视图保留原始路径和可达的报告合同，不需要再下载完整 schema。
`disclosure.schemaDigest` 标识同一运行时的完整合同；不要拼接来自不同 digest 的片段。
`--mode capabilities` 仅供工作流能力发现，`validationSchema=false` 明确禁止将其当成
完整参数校验树。probe 优先使用此视图；定向查询应按实际任务读取。

auth 通过 `commands.auth.subcommands.<action>` 披露 `usage`、`options`、`positionals`、
`acceptsInputPositional`、`argumentsSchema` 和 `ioContract`；旧的
`commands.auth.reportSchema` / `commands.auth.reports` 已移除。CLI 调用方式没有因此改变：

| action        | 输入                                | I/O 与结果边界                                                                                   |
| ------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------ |
| `verify`      | `xdoc auth verify --license <file>` | 只读指定文件，做诊断校验，不完成任务授权或本地安装准入。                                         |
| `install`     | `xdoc auth install <file>`          | 恰好一个位置文件，禁止 `--license`；可写本地配置和 Clock 状态。                                  |
| `status`      | `xdoc auth status`                  | 无文件参数；准入可能更新 Clock 状态，不是纯只读查询。退出 0 不代表 Credential 健康或任务获授权。 |
| `uninstall`   | `xdoc auth uninstall`               | 无文件参数；只删除已安装 License。                                                               |
| `reset-clock` | `xdoc auth reset-clock`             | 无文件参数；只删除固定 Clock anchor，保留锁文件；按实际恢复指引执行。                            |

这些动作的 stdout 本身是 JSON report，不追加 `--json`。参数或进程失败可能只有 stderr，
不能假设每次失败都有 JSON。认证维护不是普通 PPTX 任务的自动准备步骤；仅在任务需要时
使用相应动作。测试这些写操作时用新建的 `XDOC_CONFIG_PATH` **目录**隔离本机配置。

### 1. 初次进 deck → 取 op 索引

```bash
xdoc schema --mode index > schema-index.json
```

得到当前 op 名、summary、required / optional 字段名与 constraints —— 用来
决定 "我要 `add-chart` 还是 `add-text-box`"。index 视图没有 `level` 字段（`--mode ops`
里所有 op 的 `level` 都是 `patch`）；18 种 recipe kind 不是独立 op，而是
`add-slide.recipe.kind`，清单在完整 schema 的 `commands.pptx.recipeOps[]`。

### 2. 选定 op → 先拉所需字段

只确认 selector、name 等少量字段时，优先使用字段投影：

```bash
xdoc schema --mode ops --ops set-shape --fields name,shape,slide --defs summary --minimal \
  > schema-set-shape-name.json
```

`--defs summary` 只保留投影字段直接引用的定义，并在 `$defs.*.x-xdoc-summary` 中披露类型、
属性名、required 组合、引用和顶层枚举/分支数量；它用于低 token 成本的字段与定义发现。
输出中的 `disclosure.completeValidation=false` 表示它不是完整校验合同。开始构造嵌套 selector、
需要传递引用时，应改用 `--defs full`。即使如此，字段投影仍不是完整校验合同；需要检查全部
可选字段或执行完整离线验证时，应同时省略 `--fields` 和 `--defs`（也可用 `apply --dry-run` 校验最终 patch）：

```bash
xdoc schema --mode ops --ops set-shape --fields name,shape,slide --defs full --minimal \
  > schema-set-shape-name-full.json
xdoc schema --mode ops --ops add-chart --minimal > schema-add-chart.json
```

`--defs full` 保留投影字段可达的完整 `$defs` 闭包；省略 `--defs` 与显式 `full` 等价。

拿到完整 jsonSchema，里面有：

- 每个字段的 type / enum / pattern
- `$ref` 指向的 `$defs`（如 `length` / `color` / `chartKind`）
- required vs optional 列表

### 2b. 动画 op 必须按需拉 schema

动画字段和安全边界更新频繁，涉及动画时先拉对应 op：

```bash
xdoc schema --mode ops --ops set-slide-animations --minimal > schema-set-slide-animations.json
```

重点看 `mode`、`effect`、`phase`、`target`、`build`、`trigger` 的 enum。不要把旧版本
`set-slide-animations` 只能做入口动画的记忆当成当前事实；也不要把 schema 未披露的高级动画
当作已支持。

### 3. 想抄个例子 → 拉 examples

```bash
xdoc schema --mode examples > examples.json
```

示例覆盖 populate-slide / bind-data / rich notes / charts / tables /
shape effects / hyperlinks 等。对照修改最快。

已选定操作时，优先 `xdoc schema --mode ops --ops set-shape`：完整单操作视图同时返回
匹配的 `examples[]`，无需再取全量 examples。`--minimal` 和带 `--fields` 的投影有意省略
示例；缺少示例不表示操作不可用。示例可能含准备步骤，复用时只保留当前任务需要的操作，
仍按 inspect selector、完整合同与 dry-run 核实。

## Schema 关键 `$defs` 速记

`convert` / `extract` / `check` 的页码参数统一为 `--slides`（短参数 `-s`），
从 1 开始，支持逗号与范围；省略表示全部。不要使用已移除的 `--slide`。
此规则不改名 skill 自有 helper 的参数；helper 仍以自身 `--help` 为准。
所有 FontPatch 的 `letterSpacing` 使用显式 `pt` 字符串或 `null`，包括 chart、
table、notes 的 run；裸数字会被拒绝，notes 的非法 font 不再可当作忽略样式继续执行。

### `length`

```
"^-?[0-9]+(\\.[0-9]+)?(emu|in|cm|mm|pt|px)$"
```

必须带单位后缀的字符串：`"1in"` / `"2.54cm"` / `"96px"` / `"914400emu"` 等；
裸 number 与无单位字符串会被拒收（EMU 用 `"…emu"` 显式表达）。

### `color`

```
"^#?[0-9A-Fa-f]{6}$"
```

6 位十六进制，可选 `#` 前缀；大小写不敏感。

### `themeColorScheme`

```
lt1 / dk1 / lt2 / dk2 / accent1..6 / hlink / folHlink
```

### Theme fonts

整包中文/东亚字体归一化是独立的 top-level `set-font`，不是 `set-theme` 的别名，
也没有 shape selector。先检查 `text/font-family-normalization`，再读
[字体归一化](../edit/font-normalization.md) 的选择报告与文档级 Edit Contract。

`set-theme.fonts` 使用 `major` / `minor` 两个槽位；每个槽位是字体对象，例如
`{ "typeface": "Inter", "eastAsian": "Source Han Sans SC" }`。不要使用已删除的
`themeFontKind` / `majorFont` / `minorFont` 别名。

### 严格写入枚举与保留身份

对下列字段读取目标 op 的完整定义；lookup/preserve 域不等于 create/edit 域：

- 字体 `underline` 使用 DrawingML token，例如 `sng`、`dbl`、`none`，不接受
  `single` / `double`。省略保留本地值，`none` 显式关闭；规则适用于 run、notes、
  table、chart 等共享 font surface。保留的陌生源值不等于可再次写入。
- 普通 slide/layout placeholder 创建用 `slidePlaceholderType`；例如 `dt`、
  `ctrTitle`、`subTitle`、`obj`，不用 `date`、`centerTitle`、`subtitle`、`object`。
  `hdr` / `sldImg` 属于 notes/handout，不可在此创建；lookup 的 `placeholderType`
  仍可描述这些保留身份。`set-master` 的共享文字样式槽不创建 placeholder shape。
- `add-layout` / `set-layout` 显式 `type` 使用 `slideLayoutType`，如 `cust`，不是
  `custom`。省略时新建默认 blank，复制/更新保留源身份；改 type 只改元数据，
  不生成对应占位符或布局。selector 可以匹配既有不透明类型，不据此放宽 authoring。

无效值先修正 patch，再 dry-run；不要通过 raw XML 写入被 typed writer 拒绝的别名。

### `chartKind`

```
column / column-3d / bar / bar-3d / line / line-3d / area / area-3d /
pie / pie-3d / doughnut / radar / surface / surface-3d / stock /
scatter / bubble / bubble-3d / combo / waterfall / funnel / histogram /
pareto / treemap / sunburst / box-whisker / region-map
```

### `chartVariant`

```
standard / clustered / stacked / percent-stacked / markers /
lines / lines-no-markers / smooth / smooth-no-markers / exploded / wireframe
```

（kind/variant 合法组合详见 `../content/charts.md`）

### `chartData`

- 直角坐标系（column/bar/line/area/radar/doughnut/pie）：
  ```json
  { "categories": ["Q1", "Q2"], "series": [{ "name": "Sales", "values": [10, 20] }] }
  ```
- scatter：
  ```json
  { "series": [{ "name": "A", "points": [{ "x": 1, "y": 2 }] }] }
  ```
- bubble：
  ```json
  { "series": [{ "name": "A", "points": [{ "x": 1, "y": 2, "size": 0.5 }] }] }
  ```
- stock：
  ```json
  {
    "categories": ["d1", "d2"],
    "high": [12, 15],
    "low": [8, 9],
    "close": [11, 14],
    "open": [9, 10]
  }
  ```

### `fill`

- solid: `{ "type": "solid", "color": "RRGGBB" }`
- gradient: `{ "type": "gradient", "stops": [{ "position": 0, "color": "..." }, ...], "angle": 45 }`
- radial gradient: `{ "type": "gradient", "path": "circle", "stops": [...] }`
- pattern: `{ "type": "pattern", "pattern": "wdDnDiag", "foregroundColor": "...", "backgroundColor": "..." }`
- preset gradient: `{ "type": "gradient", "preset": "daybreak" }`
- none: `{ "type": "none" }`

### `legendPosition`

```
right / left / top / bottom / top-right
```

### `alignment`

```
left / center / right / justify / justify-low / distribute / thai-distribute
```

### `effect`

`set-shape.effect` 使用 `shadow` / `glow` / `reflection` / `softEdge` 子对象；不要使用
`effect.kind`。只查询 effect 时优先使用
`xdoc schema --mode ops --ops set-shape --fields effect,shape,slide --defs summary --minimal`；构造 effect
对象时保持 `--fields` 并切换到 `--defs full`，完整合同再同时省略 `--fields` 和 `--defs`。

## Catalog 命令

| Catalog               | 拉法                                                        |
| --------------------- | ----------------------------------------------------------- |
| 182 个 preset shape   | `xdoc pptx catalog shapes --json`                           |
| 103 个 XlChartType    | 在 `schema` 输出的 `commands.pptx.catalogs.xlChartTypeMap`  |
| 24 个 preset gradient | 在 `schema` 输出的 `commands.pptx.catalogs.presetGradients` |
| Layout 契约           | 在 `schema` 输出的 `commands.pptx.catalogs.layouts`         |
| Brand profile         | 在 `schema` 输出的 `commands.pptx.catalogs.brands`          |
| Chart styles 1-48     | 在 `schema` 输出的 `commands.pptx.catalogs.chartStyles`     |

## Select 查询 schema

`xdoc pptx select` 用于只读定位 shape 候选。完整 schema 中相关入口：

- `commands.pptx.subcommands.select`：CLI 用法、IO contract、`--slides` 范围规则。
- `commands.pptx.selectReportSchema`：`pptx-select/v1` 输出结构。
- `commands.pptx.patchSchema.jsonSchema.$defs.shapeQuery`：query 字段定义。

典型查询：

```bash
xdoc pptx select input.pptx --query '{"textRegex":"Revenue"}' --json
xdoc pptx select input.pptx --query '{"nameRegex":"^KPI","slideIndex":0}' --json
xdoc pptx select input.pptx --query query.json --slides 1,3-5 --json
```

`select` 是定位工具，不能替代 `apply --dry-run` 的 `resolvedSelectors[]` 校验。

## Schema 检索的 nushell 高效模式

```nu
# 找 "做表" 相关的 op
xdoc schema --mode index --minimal | from json | get operations | where op =~ 'table' | select op summary required

# 看 add-chart 必填 / 可选字段
xdoc schema --mode ops --ops add-chart --minimal | from json | get operations.0 | { required: $in.required, optional: $in.optional }

# 把所有 recipe kind 列出来（recipe 不是独立 op，index 视图没有 level 字段）
xdoc schema | from json | get commands.pptx.recipeOps | select recipeKind description
```

## 何时不查 schema

简单常见任务（加封面、改标题文字、改颜色）按 cheatsheet / recipes 写就行，不必每次
都拉 schema。schema 主要在：

- 拿不准字段名 / 类型
- 想看 `enum` 全集（如 `chartKind` / `placeholder.type`）
- 写完 patch 想离线 validate

这种时候才花一次 schema 拉取的 token。

## `--explain`：dry-run 报告里直接拿"该 op 的 schema 摘要"

当你只想了解"**当前 patch 里这个 op** 的字段约束 / 该 op 做什么"，而不需要
schema 全集时，可以在 `apply --dry-run` 上加 `--explain`：

```bash
xdoc pptx apply -p patch.json -i in.pptx --dry-run --explain --json > dry.json
```

报告顶层会新增 `explanations[]`，与 `opResults[]` / `traces[]` 一一对应，每项形如
（`expandedOps` 只在 `if` / `foreach` / `try` / `use-macro` / recipe 等会展开的元 op 上出现）：

```json
{
  "opIndex": 1,
  "op": "add-text-box",
  "status": "success",
  "summary": "Create a text box shape on a slide.",
  "reason": "Create a text box shape on a slide. Its arguments are validated against the published patch schema metadata before the bridge applies the concrete operation.",
  "schema": {
    "level": "patch",
    "requiredFields": ["slide", "x", "y", "w", "h"],
    "optionalFields": ["marginBottom", "marginLeft", "marginRight", "marginTop", "name", "text"],
    "fieldNotes": [
      {
        "name": "slide",
        "required": true,
        "type": "integer",
        "schemaRef": "",
        "description": "0-based slide index.",
        "strict": false
      },
      {
        "name": "x",
        "required": true,
        "type": "string",
        "schemaRef": "#/$defs/length",
        "description": "Length value: a unit suffix is required, ...",
        "strict": false
      },
      {
        "name": "text",
        "required": false,
        "type": "string",
        "schemaRef": "",
        "description": "",
        "strict": false
      }
    ]
  }
}
```

适用场景：

- **Agent 不读源码也能用**：拿到 dry-run 错误时，比 grep schema 更直接 —
  `explanations[opIndex].schema.{required,optional,fieldNotes}` 直接告诉你这条
  op 还缺什么字段、字段类型是什么 `$ref`
- **元 op 展开审计**：对 `if` / `foreach` / `try` / `use-macro` / recipe 等会展开的
  元 op，`explanations[i].expandedOps[]` 列出展开后实际执行的底层 op 名，比
  自己读 `opResults[].controlExpansion` 更直观
- **token 友好**：与 `xdoc schema` 一次性几万 token 不同，`--explain` 只在
  dry-run 时按需附带、且只覆盖当前 patch 里**真正用到**的 op
- **rename 可自证**：对 `set-shape` rename，检查对应 `semanticChanges[]` 的
  `before` / `after`；`explanations[].reason` 会明确说明名称从旧值变为新值。

### 约束

- **只对 `pptx apply --dry-run` 生效**：在 `inspect` / 真正 apply 上加 `--explain`
  会被 CLI 拒绝（`--explain is only valid with apply --dry-run`）
- 报告 schema 版本仍是 `pptx-dry-run/v1`，新字段 `explanations` 是向后兼容追加
- 出错时同样会附 explanations（与 op_results 一一对应），方便你看错的 op 本来
  期望什么字段
