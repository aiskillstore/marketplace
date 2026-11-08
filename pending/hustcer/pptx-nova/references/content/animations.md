# PPTX 动画与转场

读取本文件的场景：用户要求新增、修改或删除 PPTX 动画/转场，或提到点击顺序、自动播放、
`with previous` / `after previous`、逐条 bullet、退出动画、motion path、emphasis、timing tree。

仅当任务涉及 Web 放映、play/pause、自动切页或键盘/焦点异常时，再读
[Viewer 播放诊断](viewer-playback.md)。普通 PPTX 导出无需启动浏览器。

## 能力发现

动画能力变化较快，先用运行时 schema 和 dry-run 证据，不靠记忆：

```bash
xdoc schema --mode ops --ops set-slide-animations --minimal > <run-dir>/schema-set-slide-animations.json
```

当前运行时 schema 暴露的安全子集包括：

- 创建/替换/清理：`set-slide-animations`，字段 `mode: "merge-safe" | "replace" | "clear"`。
- 局部安全编辑：`set-slide-animations`，用 `inspect.animations[].id` 定位。
- 局部安全删除：`set-slide-animations`，用 `remove: ["<inspect.animations[].id>"]` 定位。
- 支持的创建效果：入口 `appear/fade/wipe/fly`；退出安全子集 `disappear/fade-out/wipe-out/fly-out`
  或 `phase: "exit"`。
- 若 schema 披露 `box` / `dissolve`，可创建固定变体的整 shape 进入/退出；见下方专节，
  不把同名整页转场或可播放的既有复杂效果当作创建契约。
- 若当前 schema 披露 `grow-shrink` / `spin` 及其参数，可创建有限的整 shape 强调；详见下方幅度契约。
- 若当前 schema 同时披露 `motion-path` 和 `offset`，可创建有限的整 shape 直线路径；详见下方路径契约。
- 支持的 trigger：`on-click`、`with-previous`、`after-previous`。
- 支持的 timing modifier：`repeat`、`autoReverse`、`restart`、
  `easing.accelerate/decelerate`。
- 支持的文本 build：`target: { shape, paragraph?, level? }` 配合
  `build: "all-at-once" | "by-paragraph" | "by-level"`。

未在 schema 中披露的能力按 `undisclosed` 处理，不直接当成 `unsupported`；但交付前必须以 dry-run、
inspect 回读、PNG/播放复核和 clean-open gate 证明。

## Inspect First

既有 dissolve 转场的 Web 显示或速度异常，先核对加载的 Viewer build、原始转场
metadata、显式 Office duration（包括零）与 fallback。Web dissolve 采用有预算的
整页场景遮罩；不可用时的降级不表示源转场丢失。静态 PDF/PNG 不验证时长、seek、
清理或播放保真；保留原声明，在实际播放环境复核，不因 Viewer 新增显示支持就
假设 `set-slide-transition` 扩大了可写范围。字体 refit 后的段落动画还应检查反射与
Text 3D 是否随同一 target 运动、退出及复位，见 `../review/fidelity-diagnosis.md`。

动画编辑必须从 inspect 开始：

```bash
xdoc pptx inspect input.pptx --daemon --json > <run-dir>/inspect.json
```

看每页：

- `timingSummary`: timing 是否存在、media/interactive/unsupported timing、editable 与
  preserve-only **逻辑效果**数量、`unattributedTimingCount` 和独立安全判定 `mergeSafe`。
- `animations[]`: 稳定 `id`、`kind`、全部 `targets[]`、`source`、`behaviors[]`、`effect`、`direction`、`scale`、`degrees`、`offset`、`phase`、`trigger`、`durationMs`、`delayMs`、
  `repeat`、`autoReverse`、`restart`、`easing`、`editable` 和 preserve-only reason（`unsupportedReason`）。
- `animationCapabilities`: `editable`、`preserveOnly`、`unsupportedCreate`。

`kind: "effect"` 按明确的 effect `cTn` 聚合行为；`kind: "unattributed"` 是无可靠归属的
timing 诊断，不计入逻辑效果数量。相同 `grpId` 不合并不同效果，嵌套效果分别保留归属。
`source` / `behaviors[]` 保留 `tag`、`namespaceUri` 和原始 `attributes`，仅供诊断。
未知效果的 `durationMs` / `delayMs` 可为 `null`，不能当零或从第一个 behavior 猜时长。
不要再读取旧的 `animations[].target`；`targets[]` 可以为空或含多个对象，不能自动取首项当 selector。
旧 CLI 未披露这些字段时保留旧报告，按其实际 schema 和 dry-run 处理，不伪造逻辑计数或 `mergeSafe`。

只有 `kind: "effect"` 且 `editable: true` 的既有 step 才能尝试稳定 ID 编辑或删除；
它不是任意修改都成功的保证。`mergeSafe` 独立判断能否安全合并整棵 timing，计数变少不扩大权限。
`preserveOnly` 命中的 timing 不要 raw XML 猜改；仅在用户已明确授权丢弃/重建相应动画语义时
使用 `mode: "replace"` 或 `mode: "clear"`，否则先说明影响并取得授权。
`mergeSafe:false` 拒绝的是默认安全合并，不是禁止同页所有编辑：不相关文字/几何编辑
应保留未触达 timing；明确授权的 replace/clear 会整体替换/移除 timing。先保留原始
inspect/timing 证据，再回读最终 timing；不要仅为通过 merge-safe 而切换 mode。

安全修改还取决于 carrier、调度和引用：

- 可写 carrier 必须是唯一、直接的 PresentationML timing；包装在 `AlternateContent`、外来
  namespace 或多个 timing 中的内容保持只读。合法 namespace 别名/默认 namespace 本身不是风险。
- 重复或非法 time ID、不完整的 click/automatic 调度容器、未知 wrapper 属性会阻止安全合并。
  根 group 的 `grpId` 省略或数值零可合法，不能自行补为别的值或“修好”容器来绕过拒绝。
- 删除/替换效果可能移除内部 behavior ID；若幸存节点仍引用它们，即使该效果 `editable:true`
  也会拒绝。纯时长编辑可有不同结果，必须验证用户实际请求，不自动切换到 replace/clear。
- 删除 shape 同时清理完整所属效果，并检查所有 target、build 与包内相关扩展元数据中的引用；
  归属不明、会误删嵌套效果或留下引用时原子拒绝。无关扩展 metadata 保留，不是可写动画树；
  不能因为 metadata 中也有 timing/id 就改它，也不能忽略它对被删 shape 的引用。
- 幸存容器的 `stCondLst/endCondLst/prevCondLst/nextCondLst` 若仍引用被删 shape，必须原子拒绝，
  即使列表还有其他条件也不能删掉这一项来绕过拒绝。条件只随被完整删除的所属效果/行为一起移除。
  新空的 timing 子列表只可在封闭、安全的结构内清理；属性、注释或其他 metadata 不能随容器丢弃。

失败后保留输入、patch 和报告，按真实拒绝原因缩小操作或重新规划；不要靠计数、preset ID
或名字推断权限。apply 后重新 inspect，核对稳定 ID、所有 targets、未触达效果及 metadata。

## 新增动画

新增动画仍是用户显式要求时才做；不要给普通商务 deck 自动加动效。

最小 patch：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
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
  ]
}
```

`merge-safe` 是默认思路：如果现有 timing 含 media timing、interactive trigger、unsupported timing、
未建模的 motion path / emphasis 或复杂 build，dry-run 应拒绝覆盖。不要为通过门禁而改成 `replace`，除非用户明确
接受丢弃/重建既有动画树。

## 基础动画 timing modifier

四个 modifier 用于当前 schema 披露的安全效果；box/dissolve/grow-shrink/spin/motion-path 额外要求有限 repeat。
它们不会解锁任意 emphasis、motion path、sequence/parallel、chart build、media timing 或 shape-trigger：

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "mode": "merge-safe",
  "animations": [
    {
      "shape": { "name": "KPI Card" },
      "effect": "fade",
      "duration": 400,
      "repeat": 2,
      "autoReverse": true,
      "restart": "when-not-active",
      "easing": {
        "accelerate": 0.25,
        "decelerate": 0.5
      }
    }
  ]
}
```

严格语义：

- `repeat` 是非负整数或字符串 `"indefinite"`。有限整数表示总播放次数；显式 `0` 会被保留，
  不会偷偷归一成 `1`。xdoc 会按 OOXML 要求将次数编码为千分之一单位，Agent 不应直接传 wire 值。
- `autoReverse` 是 boolean，对应每个有限循环先正向、再反向播放；因此 `repeat: 1` 也包含一正一反
  两段。它不会让 Viewer 获得完整 PowerPoint restart 激活状态机。
- `restart` 只接受 `always`、`when-not-active`、`never`。
- `easing.accelerate` / `easing.decelerate` 都是闭区间 `[0, 1]` 的比例；对象至少提供一侧。
- 有限 repeat 会扩展 `after-previous` 的调度总时长；启用 autoReverse 时每个循环按两倍基础 duration
  计时。Viewer 支持有限 repeat、autoReverse 和 easing；
  `repeat: 0`、`repeat: "indefinite"` 当前不播放，`restart` 只作为结构化 metadata 保留。
- 同一个 direct timing group 若混入 preserve-only 节点，或存在无法完成的 indefinite 前驱，整组按
  preserve-only 处理；不要尝试按稳定 ID 局部改写或删除其中某个 leaf。创建/更新形成同 click group 的
  `indefinite -> after-previous` 会被拒绝，应改成新的 on-click group 或移除 indefinite。
- `ext:repeatCount`、`ext:childTnLst` 等带扩展 namespace 的同名 QName 不属于标准 timing 字段；inspect
  会保留并把相关 leaf 降为 preserve-only，Agent 不应通过 raw XML 把它们改写为无前缀属性。
- PDF/PNG 仍是静态结果，不能用来证明 modifier 的播放语义。

按 inspect 返回的稳定 `id` 更新 timing modifier 时使用三态契约：字段省略表示保留，`null` 表示清除，合法值表示写入。
`easing` 对象是完整替换：只提供 `accelerate` 会清除旧的 `decelerate`，反之亦然；`easing: null`
清除两侧。创建新 step 时不要传 modifier `null`，因为没有既有值可清除。

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "animations": [
    {
      "id": "animation-id-from-inspect",
      "repeat": null,
      "autoReverse": false,
      "restart": null,
      "easing": { "accelerate": 0 }
    }
  ]
}
```

apply 后必须重新 inspect，确认 omitted/null/value 语义、stable id 和目标对象都保持预期；不要只看
patch 成功状态。

## 固定 Box / Dissolve

先核对 effect 枚举与 `slide-animation/basic-shape-and-text-builds` 各能力轴。
这两个效果均只接受整 shape、`phase: "entrance" | "exit"` 和有限整数 repeat；
默认 entrance、on-click、500ms、delay 0。省略 repeat 使用默认播放次数。
不传 `direction`、`build`、paragraph/level，也不与同一 shape 的段落 build 混用；
`repeat: "indefinite"` 被拒绝。有限 repeat、autoReverse、restart、easing 沿用上文契约。

| effect     | 固定源语义                                                           | Web 预览边界                                                              |
| ---------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `box`      | preset 4 / subtype 16 / filter `box(in)`；退出由 `phase:"exit"` 表达 | 矩形裁剪近似，不承诺 Office 逐帧一致                                      |
| `dissolve` | preset 9 / subtype 0 / filter `dissolve`                             | 确定性散点单元遮罩；支持有限 repeat/reverse，不承诺 Office 粒子或逐帧一致 |

不发明 `box-out`、`dissolve-out`、`box(out)` 等 wire 值。入口/出口可共用同一 effect：

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "animations": [
    { "shape": { "name": "KPI Card" }, "effect": "box", "duration": 400 },
    {
      "shape": { "name": "KPI Card" },
      "effect": "dissolve",
      "phase": "exit",
      "trigger": "after-previous",
      "duration": 600,
      "repeat": 1
    }
  ]
}
```

稳定 ID 更新可改时序/target、替换效果或删除，但完整 profile 不匹配（preset、filter、
phase、目标、行为顺序、时长、可见性边界或额外 metadata）仍 preserve-only。
只改时长时省略 `effect`，由运行时维护原 profile 与 visibility boundary；零时长也要回读。
进入边界设 visible，退出末尾设 hidden。不要手写额外 visibility op 修补预览。

检查当前 Web dissolve 时，原始效果与实际播放计划均应保留 `dissolve` 身份，不再要求
`kind:"effect-fallback"` 或 `previewFallback:"fade"`。升级后重新解析原始 PPTX，不能将
旧播放计划、旧诊断或缓存的 fade fallback 当作当前事实；旧 Viewer 则按其实际加载的实现记录降级。
只有精确 filter 与有效、一致的 phase/transition（含显式 preset class）才允许播放；
`animEffect/@transition` 省略时按 OOXML 默认入口解释，非法值和相互冲突的声明不等于省略。
`dissolve(fade)`、大小写变体或 unknown 效果不能套用通用 fade，旧诊断也不授权播放。
`text-granularity` 与 `timing-fill` 仍是不同诊断；移除旧效果降级字段不代表所有动画均完整支持。

实播检查进入/退出、有限 repeat、autoReverse、延迟开始、同一 shape 的混合效果与 reset/replay。
初始遮罩以首次出现的 click segment 为边界，后续未激活的 click 不可提前隐藏或显示对象。
保留显式 visibility 和原始 opacity；粒子遮罩不是将作者的不透明度重置为 1。

此处是对象动画；前述 dissolve **整页转场**的场景遮罩走不同管道。
静态 PNG/PDF、结构校验和 clean-open 都不能证明上述动画动态等价或 Office 回存无损。

## 有限 grow-shrink / spin

先检查当前运行时 schema 同时披露 effect 和参数，随后 dry-run。两者只面向整 shape，
不接受 paragraph/level/build/direction，也不能与同一目标的段落 build 混用。

- `grow-shrink` 必须显式提供 `scale: { "x": 1.1, "y": 1.1 }`。这是相对倍数：1 为原尺寸，
  1.1 为 110%；两个分量均在 `[0.00001, 1000]`，按十万分之一量化。
- `spin` 必须显式提供有符号 `degrees`，范围 `[-3600, 3600]`，正数顺时针，0 合法；精度为 1/60000 度。
- 两者默认 `phase: "emphasis"`、`trigger: "on-click"`、`duration: 500`、`delay: 0`。
  `repeat` 只接受 `[0, 2147483]` 的整数；`"indefinite"` 被拒绝。轻微强调可用一次有限播放加 `autoReverse: true`。
- 按 ID 更新省略 `effect` 时保留幅度；显式提供 `effect` 时必须再次提供完整 `scale` 或 `degrees`。
  幅度、effect、direction、phase 不接受 `null`；只有上面的 timing modifier 支持清除。
- 改幅度保持对象静态位置、尺寸和旋转不变；apply 后检查 shape、稳定动画 ID 和后继 `after-previous` 延迟。
  最终保持态或反向返回态需要实际播放证据，不能从静态预览推定。

下面是 operation 片段，置入 `pptx-patch/v1` 的 `ops` 后使用：

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "animations": [
    {
      "shape": { "name": "KPI Card" },
      "effect": "grow-shrink",
      "scale": { "x": 1.08, "y": 1.08 },
      "duration": 250,
      "repeat": 1,
      "autoReverse": true
    },
    {
      "shape": { "name": "Arrow" },
      "effect": "spin",
      "degrees": -45,
      "trigger": "after-previous",
      "duration": 400
    }
  ]
}
```

## 有限直线路径

只有当前运行时 schema 同时披露 `effect: "motion-path"` 和 `offset` 时才使用。`offset: { "x": 0.25, "y": -0.1 }`
表示向右移动幻灯片宽度的 25%、向上移动幻灯片高度的 10%。两个分量均为 `[-1000, 1000]` 内的有限数，
量化至六位小数，零位移合法。默认 `phase: "path"`、`trigger: "on-click"`、`duration: 500`、`delay: 0`。

每条路径从对象原始布局位置出发，终点保持；`autoReverse: true` 返回本条路径的起点。
连续路径分别从原始位置开始，不累加上条路径的位移。路径保留对象旋转和缩放，不自动朝向路径。
仅支持整 shape 和有限 repeat，不接受 paragraph/level/build/direction；不允许任意路径字符串。

按稳定 ID 修改时，省略 `effect` 保留原路径；显式提供 `motion-path` 必须同时提供完整 `offset`。
`effect`、`phase`、`offset` 不接受 null。复杂路径、未知组合模式、额外 behavior 或复杂 target 仍按 inspect 的
`editable` 与 `unsupportedReason` 处理。apply 后核对偏移、稳定 ID、目标和后继 `after-previous` 延迟，
实际播放检查中间位置、保持态及反向返回态。生成与 Viewer 播放通过不能代替 PowerPoint 回存、播放认证。

## 原生 fly 的有限边界

若当前运行时披露原生 fly，新建 `fly` / `fly-out` 使用两个固定端点的 `ppt_x` / `ppt_y` 行为；
inspect 把它们归为一个逻辑动画，不应按两个属性重复计算 duration。
`direction: "from-left" | "from-right" | "from-top" | "from-bottom"` 始终命名屏幕外侧边缘：
进入时是起点，退出时是终点。因此退出到右侧仍写 `"from-right"`，不要自行发明 `"to-right"`。

```json
{
  "op": "set-slide-animations",
  "slide": 0,
  "animations": [
    {
      "shape": { "name": "KPI Card" },
      "effect": "fly",
      "phase": "exit",
      "direction": "from-right",
      "duration": 600
    }
  ]
}
```

时长编辑应保留坐标公式、并行目标和稳定 ID，并重算退出末尾的短暂隐藏行为。旧 `slide(...)` filter
形态仍可安全编辑；只有显式替换效果时才可能切换形态，不批量改写未触达效果。wipe 的方向映射不随 fly 改变。
陌生公式、额外 keyframe、混合目标、额外属性动画、背景/chart target 或复杂共享 wrapper 都应保留；
以 inspect 的 `editable` 为准，不能仅凭 `effect: "fly"` 推断可编辑。

这些是生成和安全编辑能力。新效果的 Viewer 渲染、PowerPoint 重存及播放必须分别验证，
不能用 create/edit 成功、结构校验或 clean-open 推定这些结果。

## 六轴 capability truth

probe snapshot 中若 capability entry 的 `axes` 非 null，不能只看 entry-level `status`。逐轴读取
`status`、`limits`、`officeTarget` 和 `evidenceIds`：

- `pptx-capability-truth/v3` 的六轴 contract 无效时，整份 truth 不可用；不能退回 entry-level status。
- contract 的 `requiredFor` 条目若缺失完整 axes 或任一轴畸形，该 feature/subset 视为
  `undisclosed`，不能因为 operation 已披露就推断为 supported。

- `slide-animation/basic-shape-and-text-builds`：create/edit/inspect 为 `supported`，preserve/render
  为 `partial`，verify 为 `inconclusive`。
- `slide-transition/morph-authoring`：create/edit/inspect/preserve 为 `supported`，render 为
  `unsupported`，verify 为 `inconclusive`，直到引用到受控 Windows PowerPoint evidence。

`verify` 的 `supported` 必须来自该轴引用的目标 Office evidence。结构 round-trip、Viewer 测试、
静态 PDF/PNG 和 Morph fade fallback 都不能替代 PowerPoint clean-open/resave/playback 证据；环境不可用时
保持 `skipped` 或 `inconclusive`。

## 安全合并既有动画

使用 `set-slide-animations` 的 `merge-safe` 模式提交局部更新；复杂 timing 会拒绝覆盖：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-slide-animations",
      "slide": 0,
      "mode": "merge-safe",
      "animations": [
        {
          "shape": { "name": "KPI Card" },
          "effect": "fade",
          "trigger": "after-previous",
          "duration": 650,
          "delay": 120
        }
      ]
    }
  ]
}
```

dry-run 重点看：

- `opResults[]` 成功且没有 preserve-only 拒绝。
- `semanticChanges[]` / diff 中只有预期的 animation 变化。
- 更新 target 时目标 shape 解析唯一；歧义时先 `select` 或改用 inspect 的 shape id/name。
- 若目的 shape 在同一动画组已有 build 元数据，retarget 会拒绝；不要强行合并两个组的构建语义。

## 文本逐条出现

优先表达成 paragraph/bullet build，不拆 word/character：

```json
{
  "op": "set-slide-animations",
  "slide": 2,
  "mode": "merge-safe",
  "animations": [
    {
      "target": {
        "shape": { "name": "Body" },
        "paragraph": 0
      },
      "build": "by-paragraph",
      "effect": "appear",
      "trigger": "on-click"
    }
  ]
}
```

`paragraph` 和 `level` 是 0-based。不要为了 word/character 动画给文本额外包大量 shape 或 span；
当前创建 schema 不暴露 word/character，遇到这类需求说明会降级到 paragraph/shape 或要求 PowerPoint 手工处理。

## Slide Transition

基础转场继续用 `set-slide-transition`，它与 shape animation 是不同层：

```json
{
  "op": "set-slide-transition",
  "slide": 0,
  "kind": "fade",
  "speed": "medium",
  "advanceOnClick": true,
  "advanceAfter": 5000
}
```

以下是基础转场的参数规则；P14 扩展使用下方单独的运行时契约。
`speed` 仅接受 `slow/medium/fast`，默认 `fast`。`dir` 在 `push/wipe` 上接受
`left/up/right/down`，`cover` 还接受 `left-up/right-up/left-down/right-down`（默认 `left`），在
`split/zoom` 上接受 `in/out`（默认 `out`）；其他 kind 禁止 `dir`。
`orient` 仅用于 `split`，取 `horizontal/vertical`，默认 `horizontal`；
`throughBlack` 仅用于 `fade/cut`。`clear:true` 禁止同时提供转场参数。

如果 inspect 已有未披露的 p14/p15 扩展转场、声音或复杂 timing，默认 preserve-only。
不要将 schema 已披露的基础 `zoom` 与未披露的高级导航功能混为一谈。
Morph 使用下面的专用流程，不要把它归入普通转场或 shape animation。

### P14 转场与时间回读

先读取当前 `slide-transition/p14-authoring` 的各能力轴，再查询完整
`set-slide-transition` schema。条目总体 `partial` 不会否定其已披露的 create/edit 支持，
也不会把 `render: partial` 或 `verify: inconclusive` 升级为 Office 播放已验证。
标准 Create 可通过 `--choreography` 传入这些原生操作；无需绕过 DeckKit 或改写包 XML。

当前披露的 P14 类型为 `honeycomb/flash/vortex/pan/switch/flip/ferris/gallery/conveyor/doors/window/
warp/ripple/glitter/shred/flythrough/reveal/prism/wheel-reverse`。此清单用于发现，实际以当前 schema 为准。
参数按 kind 分别校验，不沿用基础转场的限制，也不把一种效果的参数复制到另一种效果：

| 类型                                                 | 专用参数                                            |
| ---------------------------------------------------- | --------------------------------------------------- |
| vortex / pan / glitter / prism                       | `dir: left/up/right/down`                           |
| switch / flip / ferris / gallery / conveyor / reveal | `dir: left/right`                                   |
| doors / window                                       | `orient: horizontal/vertical`                       |
| warp / shred / flythrough                            | `dir: in/out`（默认值按 schema）                    |
| ripple                                               | `dir: left-up/right-up/left-down/right-down/center` |
| glitter / shred                                      | `pattern: diamond/hexagon` / `strip/rectangle`      |
| flythrough / reveal                                  | `hasBounce` / `throughBlack` 布尔值                 |
| prism                                                | `isContent`、`isInverted` 布尔值                    |
| wheel-reverse                                        | `spokes` 为 UInt32；可写范围不等于 Web 可播放范围   |

例如对已有第 2 页设置转场，先 dry-run，再 apply 到新候选并 inspect：

```json
{
  "op": "set-slide-transition",
  "slide": 1,
  "kind": "prism",
  "dir": "left",
  "isContent": false,
  "isInverted": false,
  "duration": 750,
  "advanceAfter": 2000,
  "advanceOnClick": false
}
```

- `slide` 为 0-based 目标页。`duration` 和 `advanceAfter` 的写入单位都是毫秒，当前接受
  0–2147483647 的整数。`duration` 是效果时长，`advanceAfter` 是自动换页时间，不相互替代。
- inspect 的 `transition.durationMs` 可含小数，`advanceAfterMs` 可读完整 UInt32。
  保留 `durationRaw`、`parameters[].raw/value/source` 和 `diagnostics`；省略、显式 false、
  implied、unspecified 与 invalid 不能混同。`editable:true` 不保证所有读到的值均可无损回写。
  不改转场时保留原 XML；确需替换时只写 schema 可表达且符合用户意图的值，不自动取整或截断。
- `set-slide-transition` 是整体替换，不是参数合并。核对目标 kind、所需参数、时间、
  `extensionWrapped`、`fallbackKind` 和 `fallbackTiming`；P14 新建会写基本 fade fallback。
  source 与 fallback 的时间事实分别解释，不要求二者拥有完全相同的精确 duration。
  纯转场 carrier 可替换/清除，混有其他 payload 的 carrier 被拒绝时保留输入，不强行 raw XML 覆盖。
- 当前 Web 源效果仅启用 flash/reveal/flip/prism/doors/window/pan/wheel-reverse；prism 要求
  `isContent=false` 且 `isInverted=false`，wheel-reverse 仅支持 1–16 spokes。
  不支持的变体或缺少场景能力时可回退，其他 P14 效果使用 MC 选中的 fallback。
  动画开关、reduced-motion、前一页是否存在也会影响播放。Web 是近似实现，PDF/PNG 是静态证据。
- Office 的 clean-open、播放、resave 分别记录候选 SHA、应用版本和观察结果。
  不以 Web fallback 正常或静态 PNG 通过宣称 P14 Office 播放认证；没有原生播放证据就明确未验证。

## Morph 专用流程

需要安排对象移动/聚焦、KPI 卡片放大或主体退场时，继续读取
[Morph 编排与三个最小示例](morph-choreography.md)。该指南复用复制页、形状编辑和本节转场契约。

先从当前运行时确认 Morph 契约，不能仅凭 xdoc 版本号推断：

```bash
xdoc schema --mode ops --ops set-slide-transition --minimal > <run-dir>/schema-set-slide-transition.json
xdoc pptx inspect input.pptx --daemon --json > <run-dir>/inspect-before.json
```

只有 schema 同时披露 `kind: "morph"`、`morphMode` 和需要的 mode 时才创建。Morph 目标是相邻的
source/destination slide pair；`set-slide-transition.slide` 是 **0-based destination slide index**。
对象配对是显式契约：在两页上给对应 shape 设置完全相同、区分大小写的 `!!` 前缀名称，例如
`!!Hero`。不要宣称 xdoc 会按文本、位置或普通 shape name 自动推断配对。

最小 patch：

```json
{
  "schemaVersion": "pptx-patch/v1",
  "ops": [
    {
      "op": "set-slide-transition",
      "slide": 1,
      "kind": "morph",
      "morphMode": "by-object",
      "duration": 900
    }
  ]
}
```

`morphMode` 只使用 schema 披露的严格枚举：`by-object`、`by-word`、`by-char`。在 apply 前后都对
确切相邻页运行诊断，并保存 `pptx-morph-check/v1` 报告：

```bash
xdoc pptx morph-check input.pptx --from-slide 1 --to-slide 2 --json \
  > <run-dir>/morph-check-before.json
xdoc pptx apply -i input.pptx --patch <run-dir>/patch.json --dry-run --json \
  > <run-dir>/dry-run.json
xdoc pptx apply -i input.pptx --patch <run-dir>/patch.json -o <run-dir>/candidate.pptx --json \
  > <run-dir>/apply.json
xdoc pptx inspect <run-dir>/candidate.pptx --daemon --json \
  > <run-dir>/inspect-after.json
xdoc pptx morph-check <run-dir>/candidate.pptx --from-slide 1 --to-slide 2 --json \
  > <run-dir>/morph-check-after.json
```

交付前要求 `morph-check-after.json` 中预期显式配对成功且没有 blocking finding，并确认 inspect 回读
到 `kind: morph`、正确的 mode/duration、extension wrapper 以及 fade fallback。若两页本来没有 `!!`
名称，先通过普通 inspect/select 和受支持的重命名操作建立显式配对；不要通过 raw XML 绕过诊断。

`clean-open.mjs` 在可用时按主流程运行。下面的 Nushell 播放探针是可选的、能力门控的
PowerPoint-native 证据，仅在 macOS + PowerPoint + Nushell 都可用时运行：

```bash
node <skill-root>/scripts/cli/runtime/clean-open.mjs \
  --pptx <run-dir>/candidate.pptx --output <run-dir>/clean-open.json --json
nu <skill-root>/scripts/cli/office/morph-playback.nu <run-dir>/candidate.pptx \
  --from-slide 1 --to-slide 2 --mode by-object --duration-ms 900 \
  --output <run-dir>/morph-playback.json --json
```

缺少 Nushell 或其他可选前置不阻断基线 Morph 流程，但必须把 PowerPoint 播放证据标为
unverified，不能声称已经验证；若用户或交付策略明确要求 PowerPoint-native Morph 证明，
则该证明门禁保持阻塞，直到可选前置可用。

`--duration-ms` 是通过门禁的必填预期值，必须来自 patch 或 inspect，不能省略后仍宣称时长已验证。
需要验证 PowerPoint 保存往返时，再加 `--resave-output <run-dir>/powerpoint-resaved.pptx`，随后对该文件
重复 inspect 和 morph-check，并对 destination slide 的关键 XML 做可归因 diff。下面以 destination index
1 对应 `slide2.xml` 为例；其他页按实际 part 调整：

```bash
unzip -p <run-dir>/candidate.pptx ppt/slides/slide2.xml \
  | xmllint --format - > <run-dir>/slide2-before.xml
unzip -p <run-dir>/powerpoint-resaved.pptx ppt/slides/slide2.xml \
  | xmllint --format - > <run-dir>/slide2-after.xml
diff -u <run-dir>/slide2-before.xml <run-dir>/slide2-after.xml \
  > <run-dir>/slide2-powerpoint.diff || true
```

逐项归因 namespace/attribute order 等 PowerPoint 规范化；`p159:morph` mode/duration、
`mc:AlternateContent` Choice 和 fade Fallback 的删除或语义变化必须阻断。播放探针证明 PowerPoint 识别
目标 Morph mode、启用动画并从 source 前进到 destination；它不捕获中间帧，也不证明视觉插值像素一致。
该技能脚本只提供 macOS PowerPoint 证据；不可用时输出结构化 `skipped`。如果交付目标明确要求 Windows
PowerPoint，必须在 Windows fixture 补证，否则该维度保持 `inconclusive`。

清除 Morph 时使用同一 canonical operation，不直接删 XML：

```json
{
  "op": "set-slide-transition",
  "slide": 1,
  "clear": true
}
```

若调用方要求保留兼容转场，则用同一 operation 将 `kind` 明确设为 `fade`（或 schema 披露的其他基础
转场），不要把它与 `clear: true` 混用。apply 后 inspect 必须回读为无 transition 或指定基础转场，且
目标 slide 不得残留 Morph namespace、extension wrapper 或失效 Choice。

当前 Viewer 已部分支持 object/group、word/character Morph 插值及播放生命周期；具体边界以
当前运行时 capability 的 `render` 轴为准。`create/edit/inspect/preserve/render/verify` 六轴分别
核对：能创建或在 Viewer 播放，不代表已通过目标 Office 验证。PDF/PNG 仍是静态结果。
PowerPoint 播放与保存往返提供原生兼容性证据；缺少目标平台证据时，`verify` 保持
`inconclusive`，不能以 Viewer 播放或 fade fallback 代替。

## Standard Create choreography

新建 DeckKit 演示时，在标准 Create 命令加 `--choreography <run-dir>/choreography.json`。
文件使用 `{"schemaVersion":"pptx-patch/v1","ops":[...]}`，只接受：

- `set-slide-animations`：非空 replacement 列表，组合时明确写入 `mode: "replace"`；用
  `shape.name` 或 `target.shape.name` 指向已生成对象。
- `set-slide-transition`：明确的 kind；Morph 的 slide 必须是有前一页的目标页。
- `set-shape`：仅允许把已有对象重命名为唯一的 `!!Name`，用于两页显式配对。

字段、效果与参数先读取当前 `xdoc schema --mode ops --ops <op> --minimal`；不猜枚举，也不提供 JS/shell
hook 或放开 `customOps`。组合发生在 build 后、check-lock 前；`deckkit.patch.json` 保留原始版式，
`patch.json` 是最终组合。两份 patch 和编排输入均进入最终摘要绑定；修改后必须重新生成和审查，
finalize 也须带原来的 `--choreography`。

Cartesian Agenda 可设置 `data.textLayout: "paragraphs"`，生成单一原生对象
`S{0-based slide index}_AgendaParagraphs`。每个 item 对应一个段落，可声明 `level: 0..8`，默认 0；
编号随段落播放，装饰线仅在整个框下方。省略该字段或使用 `rows` 保留逐行版式。
逐段动画用 `by-paragraph`，分层用 `target.level` + `by-level`；整框 grow-shrink/spin 不附带 build。

### Animation corpus

控制变量语料可同时声明 `content.meta.deckProfile: "animation-corpus"` 和
`deck_lock.deckProfile.primary: "animation-corpus"`，并在 `content.meta.animationCases` 写案例：

```json
{
  "id": "paragraph-fade",
  "kind": "animation",
  "effect": "fade",
  "feature": "逐段淡入",
  "expectedPlayback": "点击三次，观察段落依次淡入。",
  "slides": [0]
}
```

`feature` 与 `expectedPlayback` 必须在案例页的 data 文字中可见。animation 是单页；morph 与
transition 使用相邻的 `[source, destination]`（0-based）。morph 声明 `morphMode`，基础 transition
声明 `effect`。案例必须对应组合 patch 中的真实动画目标/转场，Morph 还须存在显式 `!!` 配对。
只有有效声明覆盖的页可重复布局并免于填充无关 evidence 页；未覆盖页继续按普通 diversity 规则检查。
所有溢出、语义和 canonical 视觉门禁保持有效，profile 名称本身不能放行。

完整可复用输入见 `assets/deckkits/cartesian/examples/animation-content.json` 和同目录的
`cartesian-animation-choreography.json`。这是标准 Create 的入口；编辑已有 PPTX 仍使用上述
inspect → patch → dry-run/apply → 回读和播放验证流程，共用同一原生 probe。

播放探针通过指定放映范围直接从源页开始，读取实际 slide index。`--navigation-timeout-seconds`
默认 60 秒控制源页启动/定位；原 `--timeout-seconds` 默认 10 秒用于目标页播放/重存，两者均有
1–600 秒边界。重用报告路径须显式 `--overwrite`，或选新路径；报告不会采集中间帧。
验证源码变化时确认测试加载当前源码或重新构建的产物，不能用旧 dist 证明新行为。

## Preserve-only 边界

既有 slide drawing group 的 appearance 动画可在当前 Web build 中以完整 leaf 集合播放，
保留嵌套 group 身份、原始叠放、非整数原点及链接。checkerboard 的 across/down、blinds 的
horizontal/vertical 使用共享 group mask；blinds 当前是六条带近似。visibility helper 归入
所属 click build，不应额外消耗点击。测试 wipe 尾部、描边/箭头、反射的 overflow paint，
以及布局刷新、暂停、重播和 reset；扩展绘制范围不能扩大链接命中区。
group-level motion/scale/spin 仍不受支持，旋转 group 内 leaf 的运动/旋转修正不改变此边界。
保留诊断与 timing，不能因 Web 会播放导入 pattern/group 效果，就把 checkerboard/blinds
或任意 group transform 当成新增 patch 可写效果，也不扩大 chart/SmartArt 子 build 支持。

这些场景默认不能用普通 patch 改：

- 未披露的 motion path / 任意 custom path 创建；已披露的有限直线路径按上文契约处理。
- 未披露的强调效果（例如 color）；grow-shrink/spin 超出上述整 shape、有限幅度与重复边界的变体。
- media/video timing、interactive trigger、点击某个 shape 触发。
- chart/SmartArt build。
- word/character 级文本动画。
- inspect 标记 `editable: false` 或 `animationCapabilities.preserveOnly` 的 timing。

Viewer 对已有 chart 子目标和 SmartArt 节点/连接线 build 的播放改善，不改变这里的
创建/编辑边界。保留原 timing/build 与对象身份，在实际 Viewer 或 PowerPoint 中验证
目标、顺序、重播与复位；静态 PNG/PDF 只反映静态内容，不能证明这些 build 已播放。
不要为得到新播放效果而把现有 build 重写成普通 shape 动画。

raw OOXML 不是常规 fallback。只有用户明确要求、你能写出最小 XPath 修改，并完成 OPC/XML/PowerPoint
clean-open 与播放验证时，才读 `../edit/control-flow-and-raw-xml.md` 评估风险。

## 验证

动画任务的收尾比普通编辑多几步：

```text
inspect -> patch -> dry-run --json -> apply -> inspect回读 -> pptx diff -> preview/contact sheet ->
PowerPoint clean-open -> 播放/点击复核(可用时) -> Morph 时运行 morph-check + PowerPoint 播放探针 -> final summary
```

结构证据：

- `unzip -t out.pptx`
- 按报告中的实际 slide `partName` 检查修改部件的 XML well-formed；不要由页码拼文件名。
- 对新增/编辑 timing，确认 `<p:timing>` 位于合法 slide 子元素顺序，`bldLst` 与目标 shape id 对齐。
- PowerPoint clean-open 不得出现 Repair。

视觉/播放证据：

- PNG/contact sheet 只能证明静态最终态可读，不能证明动画顺序正确。
- 报告分别注明结构校验、浏览器运行冒烟、离散时间点画面检查、PowerPoint 语义播放和逐帧视觉对照。
  时间轴无异常不等于轨迹正确；DOM 状态采样不等于看过画面；离散帧也不能证明整个过程视觉一致。
  JS/WASM 解析结果共用同一渲染器时，不能作为两个独立视觉基准。未实际录屏或逐帧比较，就不作相应声明。
- 若用户关心播放，必须用 PowerPoint 或 viewer 播放复核点击次数、触发顺序、delay/duration 和自动切页。
- 有 `with-previous` / `after-previous` 时，检查 dry-run/diff 是否报告 timing 改动符合预期，不要把 delay 累加成意外长等待。
- 对 Web 中同一 owner 的直接并行行为，若实际播放计划披露 `trigger.parallelGroup`，同组成员
  共享触发与 delay 原点，不应逐项增加点击或串行等待；后继 after 应等待组结束（含有限 repeat/
  autoReverse），不是只等第一个成员。该字段属于播放计划，不是 patch 字段，也不开放任意并行树创建。
  检查延迟 visibility、重叠 owner、reset/重播的真实初始/结束态；被拒绝的效果及其诊断不能在
  visibility 合并时消失。段落目标的播放改善不扩大 Box/Dissolve 的整 shape 创建边界。
- 播放计划若披露 `trigger.delayOrigin`，`segment` 的 `delayMs` 已是本段累计偏移，不能再次加上
  前一效果的等待；`trigger`（其他 step 的默认原点）则是相对触发的延迟：with 相对前一 owner
  开始，after 相对当前组结束，on-click/auto 相对段开始。不能按数值大小猜原点；这是播放计划
  字段，不是 patch 参数，也不能从祖先 delay 推断已包含前序 sibling duration。
- `p:set` 的显式 visibility 是属性赋值，不是 opacity tween。检查延迟赋值、`fill=remove`、held
  state 和相邻零时长 click；完成当前 click 不激活下一 click。退出边界、seek、reset/replay
  不应留下未来赋值，也不应重复累计相对 spin/scale。不要往源 PPTX 加额外 visibility 来修预览。

最终摘要列出动画能力审计：xdoc 版本、相关 op schema 是否披露、涉及的动画 id、哪些 step 被编辑/删除、
哪些 preserve-only 风险保留，以及 clean-open / 播放复核是否完成。
