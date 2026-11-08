# 颜色、字体、主题、母版

PPTX 的视觉风格由四个层次决定：**theme（主题）→ master（母版）→ layout（版式）→ slide**。
xdoc 让这四层都能改。整 deck 的主题槽位更新可用 theme 层；局部修改应选择相应对象层，
避免把一次局部改色扩大成全包主题更新。

## 颜色

### 直接颜色

所有 `color` 字段都接受 6 位十六进制，可选 `#` 前缀：

```
"color": "1A73E8"      // 推荐
"color": "#1A73E8"     // 也行
"color": "1a73e8"      // 大小写不敏感
```

### 主题色引用

任何 fill 里都可以引用主题色（不写死 RGB，跟着主题走）：

```json
"fill": {
  "type": "solid",
  "color": { "schemeClr": "accent1", "alpha": 0.8 }
}
```

`schemeClr` 必须放在 `color` 对象里（fill 顶层直接写 `schemeClr` 会报 `unknown field`）；
取值：`lt1 / dk1 / lt2 / dk2 / accent1..6 / hlink / folHlink`（colorMap 层名字 `bg1/bg2/tx1/tx2` 不被接受，请先经 deck 的 clrMap 换算，默认 `tx1→dk1`、`bg1→lt1`）。
`alpha` 控制不透明度（0-1）；当前 patch schema 不接受 `lumMod` / `lumOff` 亮度变换字段。

## Fill（填充）

`set-shape` / `set-slide-background` 的 `fill` 与 `set-master` 的 `background`
共享 solid / gradient / pattern / none 基础定义。只有普通 shape 的 `set-shape.fill`
另外接受 picture fill；不要把它用于 slide background、table cell、chart 或 master。

### Solid

```json
{ "type": "solid", "color": "1A73E8" }
```

### Gradient

```json
{
  "type": "gradient",
  "angle": 45,
  "stops": [
    { "position": 0, "color": "1A73E8" },
    { "position": 0.5, "schemeClr": "accent2" },
    { "position": 1, "color": "FFFFFF" }
  ]
}
```

`position` 范围 `[0, 1]`；`angle` 为顺时针角度（0 = 左→右，90 = 上→下）。stop 可以混用 `color` 与 `schemeClr`。

### Radial gradient

需要径向光晕或 spotlight 时，优先用原生 radial gradient fill，而不是嵌入 SVG 或整页位图。
当前 patch 层用普通 gradient fill 加 `path: "circle"` 表达径向渐变，会写入 DrawingML path gradient，仍保持可编辑：

```json
{
  "type": "gradient",
  "path": "circle",
  "fillToRect": { "left": 0.5, "top": 0.5, "right": 0.5, "bottom": 0.5 },
  "stops": [
    { "position": 0, "color": "F1EE2E" },
    { "position": 0.72, "color": { "rgb": "F8F39B", "alpha": 0.42 } },
    { "position": 1, "color": { "rgb": "F0DA7C", "alpha": 0 } }
  ]
}
```

`fillToRect` 控制焦点/扩散区域；不确定当前 xdoc 版本的字段时先跑
`xdoc schema --mode ops --ops set-shape --minimal`。

### Preset Gradient（24 个内置）

```json
{ "type": "gradient", "preset": "daybreak" }
```

预设清单跑 `xdoc schema | jq '.commands.pptx.catalogs.presetGradients'` 取。常用：
`early-sunset / daybreak / horizon / ocean / chrome / silver / sapphire`。

### Pattern

```json
{
  "type": "pattern",
  "pattern": "wdDnDiag",
  "foregroundColor": "1A73E8",
  "backgroundColor": "FFFFFF"
}
```

`pattern` 是 OOXML pattern name（`pct5 / pct10 / dkHorizontal / wdDnDiag / cross / shingle` 等）。

### No fill

```json
{ "type": "none" }
```

这是显式无填充，不是“删除本地声明并恢复继承”。slide background 的 no-fill 会阻断
layout/master 背景继承；透明 solid 也仍是本地声明。需要恢复母版背景时，按当前
`set-slide-background` schema 使用 `followMaster:true`，不要以 no-fill 或透明色代替。
普通 shape 从主题继承 no-fill 时也应保持透明，直接 solid override 则可恢复填充；
不要为匹配旧预览给未声明 fill 的对象补实心背景。解析后的 deferred theme color
可能输出小写 hex；颜色比较按数值归一化，大小写变化不构成重新着色。

### Picture fill（仅普通 shape）

```json
{
  "op": "set-shape",
  "slide": 0,
  "shape": { "name": "Photo panel" },
  "fill": {
    "type": "picture",
    "assetSource": { "path": "images/texture.png", "mimeType": "image/png" },
    "mode": "stretch",
    "crop": { "left": 0.05, "right": 0.05 },
    "alpha": 0.9,
    "rotateWithShape": true
  }
}
```

`mode` 是 `stretch` 或 `tile`，tile 模式可另给 `tile` 参数。检查当前 preview/PDF 的
源裁剪、目标矩形、平铺比例/偏移与透明度映射，并用 PowerPoint 复核目标页面；不要因旧版
crop/tile 显示差异就删除这些设置。已有 picture shape 的裁剪或 preset mask 则用
`set-image`。既有背景/表格单元格 picture fill 的读取与渲染不代表上述 authoring op 已能写入。

## Line（边框）

```json
{
  "op": "set-shape",
  "slide": 0,
  "shape": { "id": 2 },
  "line": {
    "width": "1pt",
    "color": "1A73E8",
    "dash": "dash"
  }
}
```

`dash` 取值：`solid / dot / dash / lgDash / dashDot / lgDashDot / lgDashDotDot / sysDash / sysDot / sysDashDot / sysDashDotDot`。

清掉边框：

```json
{ "op": "set-shape", "slide": 0, "shape": {...}, "line": { "noLine": true } }
```

## 字体

整包统一中文或东亚字体时，先读 [字体归一化](../edit/font-normalization.md)，使用实时披露的
`set-font`。只改主题不会覆盖已有 run 字体，只改 Latin `name` 也不会统一东亚字形。
中文模式保留日文/韩文及通用 EA 默认值；全东亚模式需要对应范围的明确意图。
局部改字族继续使用下面的 run patch，不将单对象请求扩大到整个文档。

### 单个 run 字体

```json
{
  "op": "set-run",
  "slide": 0,
  "shape": { "id": 2 },
  "paragraph": 0,
  "run": 0,
  "font": {
    "name": "Inter",
    "eastAsian": "Source Han Sans SC",
    "complexScript": "Noto Sans Arabic",
    "letterSpacing": "0.1pt",
    "size": "16pt",
    "bold": true,
    "italic": false,
    "underline": "sng",
    "color": "1F1F1F"
  }
}
```

字段说明：

| 字段              | 含义                                                                                                     |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `name`            | 字体族名（如 `Inter` / `Microsoft YaHei` / `Source Han Sans SC`）                                        |
| `eastAsian`       | 东亚脚本字体；省略保留，`null` 清除并恢复继承                                                            |
| `complexScript`   | 阿拉伯文等复杂脚本字体；省略保留，`null` 清除并恢复继承                                                  |
| `letterSpacing`   | 字符间距；仅显式 `pt` 字符串，拒绝裸数字；省略保留，`null` 清除                                          |
| `kern`            | 字偶距调整的最小字号阈值；仅在当前 schema 披露时使用，规则见下文                                         |
| `size`            | 使用 `"<n>pt"` 等带单位的 length 字符串；裸数字会被拒绝                                                  |
| `bold` / `italic` | 布尔                                                                                                     |
| `underline`       | DrawingML token，如 `none / sng / dbl / wavy / heavy`；完整枚举读当前 schema，`single` / `double` 被拒绝 |
| `color`           | 字体颜色（6 位 hex）                                                                                     |
| `fill`            | 用 fill 对象（gradient/pattern）填字符                                                                   |

`name` / `eastAsian` / `complexScript` / `letterSpacing` 都是 sparse patch：省略不改，
`null` 清掉本地值使继承继续。不要只改 Latin `name` 就声称多语言字体已经统一；先从
inspect 的 `fontFacts[]` 检查各脚本 scope。

`letterSpacing` 的范围是 `-4000pt` 至 `4000pt`，支持任意小数位，直接舍入到 0.01pt，
恰好一半时远离零：`"0.005pt"` → 0.01pt，`"-0.005pt"` → -0.01pt，
`"0.004999pt"` → 0pt。保留原十进制字符串交给运行时，避免先转 EMU、用二进制浮点
预舍入或二次舍入；富文本 notes 遵循相同规则。inspect 的 `fontFacts[].font.spacingPt`
（及继承后的 `effectiveSpacingPt`）用于回读，比较量化后的值，不要求原字符串一致。

需要调整 kerning 时，先查询当前运行时的 `set-run.font` 完整定义，确认披露
`kern` / `fontKernThreshold`。按该定义读取允许的单位、范围和精度，再使用
`"12pt"`、`"12.5pt"` 等阈值字符串；省略保留本层值，`null` 清除本层值并恢复继承。
`"0pt"` 写入显式零值，不能当作跨渲染器的开启开关：macOS PowerPoint 16.112.3 实测中零值会
呈现未启用字偶距调整的效果。需要恢复模板继承时使用 `null`；不要传布尔值、裸数字、
百分比或其他单位。
`kern` 与统一增减字符间距的 `letterSpacing` 独立，不要互相替代，也不要为了统一
字体族顺便重置 kern。

按 inspect/select → dry-run → apply → reopen inspect 验证，回读目标
`fontFacts[].font.kernPt` 和 `effectiveKernPt`：清除后前者应缺失，后者可能仍有继承值。
普通 run 解析所支持的段落、列表、layout、master 与演示文稿默认样式链；表格和图表
字体表面只披露直接值，不据此推断其样式继承。缺失字段也不表示关闭 kerning。
遇到畸形的本地或继承阈值，inspect 会保留其他可读字体事实，但阈值保持未知，且不会继续
搜索更后面的继承层；渲染则跳过畸形阈值继续继承，所以二者可能不同。不要把未知值改写成
`"0pt"`，也不要仅因 inspect 缺值就断言 PNG/PDF 没有字偶距调整。
这组事实说明保存的阈值，不提供完整字体来源追踪或实际字形间距测量；对布局敏感的
修改仍须查看渲染结果，需要 PowerPoint 保真证据时使用对应 PowerPoint 检查流程。

DrawingML 未显式声明 kern 时，当前原生文本测量/绘制采用隐式 12pt 阈值；显式
`0pt` 仍与省略不同。这个渲染默认值不要求写回源文件，也不保证 inspect 会显示本地值。
字体解析和度量变化会影响空白、换行、gradient 文本边界及 shape autofit；升级后先用
同一源文件重新渲染，按 `../review/fidelity-diagnosis.md` 排除环境变化再修改 deck。

本机字体可来自 TTF/TTC；TTC 的具体 face、legacy/typographic alias 及对应 style
共同决定解析，不能把一个集合路径当成唯一字体族或把所有 alias 合并成 regular。
保持 authored family 与 bold/italic，检查实际 PDF 字体证据。字体来自本机不表示已嵌入
PPTX，也不证明接收方安装了同一 face；`xdoc check --checks fonts` 与
`xdoc pdf inspect` 分别回答声明/风险和已导出 PDF 的字体情况。

### Theme 字体（影响继承该主题的文字）

```json
{
  "op": "set-theme",
  "fonts": {
    "major": { "typeface": "Inter" },
    "minor": { "typeface": "Source Han Sans SC", "eastAsian": "Source Han Sans SC" }
  }
}
```

- `fonts.major` = 主题大标题字体（默认绑定到 placeholder type=title）
- `fonts.minor` = 主题正文字体（默认绑定到所有 body / content）
- `typeface` 指定拉丁字符字体，`eastAsian` / `complexScript` 分别指定东亚 / 复杂书写系统字符的字体（让中文/英文分别用不同字体）

`set-theme` 按 OPC Content Type 更新包内**全部普通 Theme part**，包括未被引用但保留的主题，
不限定 `ppt/theme/theme1.xml` 或当前 master。ThemeOverride 与对象上的显式格式保持原样；
它们可能遮蔽更新后的主题槽位。无效 theme 内容或关系会使操作失败，不产生输出包。
先看 `inspect.presentation.themes` 与关联 master，再用 dry-run 的 changed parts 和最终
渲染确认实际范围。只授权某页或某对象时，不使用全包 `set-theme`。

### CJK 字体注意

PowerPoint 在中英混排时会根据字符类型选择拉丁（`typeface`）或东亚（`eastAsian`）字体。若你想为中英分别指定字体：

```json
{
  "op": "set-theme",
  "fonts": {
    "minor": { "typeface": "Inter", "eastAsian": "Source Han Sans SC" }
  }
}
```

某些字体（如 `Inter`）不覆盖中文，缺失字形会触发 fallback。显式设 `eastAsian` 声明东亚字体意图，
但实际显示仍取决于字体安装、字形覆盖、语言和对象上的显式格式；须检查最终渲染。

### 字体栈质量策略

字体策略要同时服务设计气质和交付稳定性。不要只写一个看起来高级但用户机器上可能没有的字体名；
`deck_lock.typography` 中的标题、正文、代码等栈应包含可用 fallback，正式交付时再用
`check-lock --strict-fonts` 防止 patch 引入锁外字体。

实用规则：

- 每个主要字体栈至少包含一个常见 PowerPoint 可用字体。CJK 常用 `Microsoft YaHei` /
  `SimHei` / `SimSun` / `KaiTi`；Latin 常用 `Arial` / `Calibri` / `Segoe UI` /
  `Georgia` / `Times New Roman`；代码用 `Consolas` / `Courier New`。
- 标题和正文可以形成“同族不同权重”或“明确对比”（serif × sans、display × neutral）。
  避免标题用 `Microsoft YaHei`、正文用 `PingFang SC` 这类相似但不相同的组合；它们更适合
  出现在同一个 fallback 栈中，而不是分任两个视觉角色。
- 品牌字体、Google Fonts 或本机未必安装的字体可以放在栈首，但必须写 fallback；如果客户要求
  严格品牌字体，最终摘要要说明字体安装/嵌入风险。
- 不要把字体选择藏在零散 `set-run` 里。优先用 `set-theme`、master placeholder style 或
  DeckKit token 统一角色字体；单个 run 只处理局部强调。

### 权重后缀字体名（`Inter Black` / `Barlow Light` / `Roboto Medium`...）

OOXML 允许在 `typeface` 里直接写带权重后缀的字体名（设计师常这么用）。xdoc 现在
会识别这种命名，把它拆成 **base family + weight**，并在 PDF 导出时拉对应的 Google
Fonts 权重子集:

| 后缀                 | weight |
| -------------------- | ------ |
| `Thin`               | 100    |
| `ExtraLight`         | 200    |
| `Light`              | 300    |
| (无后缀) / `Regular` | 400    |
| `Medium`             | 500    |
| `SemiBold`           | 600    |
| `Bold`               | 700    |
| `ExtraBold`          | 800    |
| `Black`              | 900    |

```json
{
  "op": "set-run",
  "slide": 0,
  "shape": { "id": 2 },
  "paragraph": 0,
  "run": 0,
  "font": { "name": "Barlow Black", "size": "54pt" }
}
```

PDF 导出会自动拉 `Barlow` 的 `wght=900` 子集；浏览器 viewer 也会把 `Barlow Black`
当成 `Barlow` family + `font-weight: 900`。

是否取得所需字重取决于实际字体来源与渲染环境。用户报告 PDF 字重不对时，复核当前
导出的字体证据和 PNG，不用版本号或字体名后缀代替实际 face 验证。

### PDF 导出的 bold / italic 现在正确解析

`pdfFontResolver` 会扫描所有 run / shape / table cell / math element,为每个 family
建一个 `Set<style>`(regular / bold / italic / boldItalic),然后**逐 style** 拉
Google Fonts 子集(`ital,wght@1,400` 等坐标),写入 PDF。

```json
{
  "op": "set-run",
  "slide": 0,
  "shape": { "id": 2 },
  "paragraph": 0,
  "run": 0,
  "font": { "name": "Inter", "bold": true, "italic": true }
}
```

上面这种 boldItalic 组合在旧版 PDF 里会回退到 regular(无粗体也无斜体)。现在
正确显示。**注意**: 浏览器 viewer 一直支持,这条修复只针对 PDF 导出路径。

如果用了**离线字体缓存**(`cache/<family>/<style>.ttf`),xdoc 会按 style 拼文件
名:`bold.ttf` / `italic.ttf` / `bold_italic.ttf`。缺哪种 style 哪种 style 回退
到 regular。

缓存文件必须含真实的 family/style 元数据与字形；把同一份 Regular 或可变字体复制并
重命名为 `bold.ttf` 不会生成 Bold。需要可变字体时使用已正确实例化的静态 face，或用户
提供的匹配静态字体。当前 native 精确匹配同时核对 family 和 style，本机 Regular 不应
遮蔽缓存中的 Bold/Italic；缺样式时仍可能回退。用 `visual-audit` 的实际字体解析证据与
PNG 核对目标对象，不能只凭 `check fonts` 找到字体族就宣布字重正确。

## Theme color（主题色一键改）

```json
{ "op": "set-theme", "colors": { "accent1": "1A73E8" } }
```

继承普通主题 `accent1` 且没有局部覆盖的对象会随之变化。ThemeOverride、显式对象颜色
及其他本地覆盖可能维持原样；主题范围与验证见上文「Theme 字体」。

如果只想改某些 shape 不动 theme：

```json
{ "op": "set-shape", "slide": 0, "shape": {...}, "fill": { "type": "solid", "color": "1A73E8" } }
```

## 整 deck 换肤：remap-theme

已有 deck 翻新优先用 `remap-theme` 做批量换肤，再用单对象 patch 补漏。它会编译为
`remap-theme` patch op，当前可覆盖 text、普通 shape、table 和 chart 的基础颜色/字体 remap。
翻新时必须显式传全 scope，避免 table/chart 保留旧样式：

```bash
xdoc pptx remap-theme clean.pptx \
  --theme corporate-blue \
  --scope text,shapes,tables,charts \
  --output remapped.pptx \
  --dry-run \
  --json
```

查看 dry-run 的 `opResults[].analysis`：`changed` 是已换肤对象，`preserved` 可能是语义色、
亮度变换或截图真实像素，`skipped` / `unsupported` 需要判断是合理保留还是旧风格残留。不要为了
统一视觉覆盖 chart 数据、table 数据、category label、notes 或截图真实像素；需要保留的语义色要写入
`content-audit.json` 或 `deck_lock.assumptions[]`。

## Background（背景）

### Slide-level（单页）

```json
{
  "op": "set-slide-background",
  "slide": 0,
  "fill": { "type": "solid", "color": "F5F7FA" },
  "followMaster": false
}
```

`followMaster: true` 表示用 master 背景（即使 slide 自己有 `<p:bg>` 也忽略）。

### Master-level（整个 deck）

```json
{
  "op": "set-master",
  "background": { "type": "gradient", "preset": "daybreak" }
}
```

可选 `master: <index>` 指定哪个 master（不指定 = 第一个）。

## Master placeholder style（整个 deck 的标题/正文默认）

```json
{
  "op": "set-master",
  "placeholders": [
    {
      "type": "title",
      "font": { "name": "Inter", "size": "32pt", "bold": true },
      "color": "1F1F1F",
      "spacing": 1.15,
      "alignment": "left"
    }
  ]
}
```

`type` 取值与 placeholder 的 type 一致（`title` / `body` / `ctrTitle` / `subTitle` /
`obj` / `chart` / `pic` / `tbl` / ...；写 `object` 会报 invalid enum value）。

## Shape effect（阴影、发光、反射、柔化）

```json
{
  "op": "set-shape",
  "slide": 0,
  "shape": { "id": 2 },
  "effect": {
    "shadow": {
      "blur": "6pt",
      "distance": "4pt",
      "angle": 45,
      "color": "000000",
      "alpha": 0.25
    }
  }
}
```

在 `effect` 中使用 `shadow` / `glow` / `reflection` / `softEdge` 子对象。
每种 effect 有自己的参数：

| effect     | 关键参数                                               |
| ---------- | ------------------------------------------------------ |
| shadow     | `blur`, `distance`, `angle`, `color`, `alpha`, `inner` |
| glow       | `radius`, `color`, `alpha`                             |
| reflection | `blur`, `distance`, `alpha`, `size`                    |
| softEdge   | `radius`                                               |

颜色使用 6 位 hex；透明度单独用 `alpha` 的 0-1 数值。

## Effect 继承开关

shape 可以选择继承 master/layout effect：

```json
{ "op": "set-shape", "slide": 0, "shape": {...}, "effect": { "inherit": true } }
```

`inherit: true` 让 shape 走 master/layout `<a:effectLst>` 继承链；不写或 `inherit: false`
就用 shape 自己的 effect。

## 一键品牌改装（推荐组合）

主题色与字体使用 canonical `set-theme`；需要按 theme pack 重映射现有对象时使用
`remap-theme`：

```json
{
  "op": "set-theme",
  "colors": {
    "accent1": "1A73E8",
    "accent2": "34A853",
    "accent3": "FBBC04",
    "accent4": "EA4335",
    "dk1": "1F1F1F",
    "lt1": "FFFFFF"
  },
  "fonts": {
    "major": { "typeface": "Inter" },
    "minor": { "typeface": "Inter" }
  }
}
```

背景、母版 placeholder 与 presentation 默认文本样式继续使用当前 schema 披露的
`set-master` / `set-slide-background` / 文本样式 op；不要再生成已删除的 rebrand alias。

## 检查改对了

写完样式 patch 一定要：

1. `--dry-run --json` 看 `semanticChanges[]` 是不是覆盖了所有目标 slide
2. apply 后 `xdoc convert out.pptx --to png -o previews --overwrite` 转 PNG，肉眼确认
3. 重要场合用 `xdoc pptx check-brand` 校验品牌合规（见 `data-driven.md`）

## 不要做的事

- ❌ 不要在 `set-theme` 的 `colors` 上加 `slide` 字段（主题色是 deck 级，不属于某页）
- ❌ 不要拆成多个 op 改同一个 shape 的 fill/line/effect — 一个 `set-shape` 里可同时设置且原子生效
- ❌ 不要假定 deck 的 master 名是固定的 — 用 `inspect` 查一下
- ❌ 不要用 `set-theme` 的 `fonts` 改单个 run 字体 — 那是 `set-run.font.name`
