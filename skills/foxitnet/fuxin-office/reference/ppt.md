# 参考文档：fuxin-ppt — PowerPoint 演示编排规约

> **收敛说明**：本文档为 `fuxin-office` 唯一入口技能**内部参考文档**，承载「PowerPoint 演示编排」规约，
> **不作独立技能对外暴露**（无 frontmatter / Trigger / description）。由 `fuxin-office` 按需读取，
> 企业若需独立技能形式可另行封装。
>
> **产品分类**: `PowerPoint`
> **依赖**: FuxinAiService（端口见 `bridge.md`「运行端口」，由 `MCPServerPort.ini` 读取）+ PowerPoint 产品场景工具
> **需要确认**: 是（写操作；不写前二次确认，写后提示撤销；保存操作 `save_document` 例外，需提前确认（另存为同此，用 `save_document` 传 `path`））

---

## 功能概述

本规约通过 MCP 网关**直接调用 PowerPoint 产品的场景工具**（场景工具已在网关内部实现，
agent 只需传参直接调用，无需手动编排原子技能、管理会话或处理批次事务）。
覆盖 3 类演示文稿编排任务：

1. **生成汇报 Deck** — 自动生成含多页幻灯片的汇报演示文稿，每页配有标题/正文、格式美化及演讲者备注（≥3 页，每页有备注）
2. **整理已有演示稿** — 删除冗余页、复制模板页、应用布局模板、插入空白页（经 `generate_deck` + `layout=Blank` 实现）
3. **选区编辑助手** — 对选中的形状或文本按指令进行修改

所有写操作由网关内部合并为事务，用户可**一次 Ctrl+Z 整组撤销**；
若需显式管理批次，见 `batch-undo.md`。

---

## 架构

```
用户 (VS Code Copilot)
    │ MCP 协议 (tools/call)
    ▼
FuxinAiService（端口见 `bridge.md`「运行端口」）
    │ 转发到 PowerPoint 产品
    ▼
fuxin-ppt 场景工具（网关内部实现）
    │
    ▼
FuxinOfficePPT App (Office 进程)
```

---

## 前置条件

1. **FuxinAiService 已启动**（端口由 `MCPServerPort.ini` 读取，见 `bridge.md`「运行端口」）
2. **PowerPoint 产品已注册**（产品名 `PowerPoint`），FuxinOfficePPT 应用已启动、插件已加载
3. **已打开一个演示文稿**（所有工具都会修改演示稿内容）

### 预检

执行任何写操作前必须预检，完整预检流程见 `bridge.md`。本规约快速探活：

- 调用 `PowerPoint__get_document_info` / `PowerPoint__get_path` 探活：成功且有活动演示 → 就绪
- 未安装 / 未就绪 / 半就绪（无活动文档）统一按 `bridge.md` 文案输出，
  禁止自行发挥或改写文案
- **空演示文稿（0 页）也是活动文档**，不误判为无活动文档；判定以 `get_document_info` 的
  `docId`/`GetId` 是否非空为准

> 📊 **探活调用也要带埋点**：上面 `PowerPoint__get_document_info` / `PowerPoint__get_path`
> 每一次调用，都须在 `params._meta["com.foxit.office/telemetry"]` 携带 `skill_id` / `scenario_id` / `agent_product`。
> 已确定 PPT 业务场景（如 `generate_deck`）→ 用该场景值（`fuxin-ppt` / `UC-PPT-S1`）；
> 仅独立「检查 Office 状态」→ `fuxin-office-bridge` / `preflight-ppt`；
> 属于 `UC-E2E-01` → `fuxin-office` / `UC-E2E-01`。见 `../SKILL.md`「一·只读工具埋点映射」。
> `agent_product` 填当前真实平台（如 `workbuddy`），无法确证填 `unknown`，会话内恒定。

> 预检全程只读，禁止任何写入操作。预检失败时按 `bridge.md` 文案提示，禁止执行写操作。

### 场景收尾

> **三档区分**：按操作粒度分选，不可互相替代：
> - **单次操作成功** → `已在文档中完成「{操作名}」。请在福昕Office中查看效果。`
> - **一组操作完成**（同一场景内多步/批量成组） → `本组修改已完成。如需撤销，请在福昕Office中按一次「撤销」即可恢复整组操作。`
> - **场景任务完成**（整个场景完全收尾） → 输出下方定稿收尾。

每个场景完全执行完毕后，按 `../SKILL.md` 汇总层「五、用户提示文案总则」输出固定收尾，**单次/一组操作不提前套用场景完成文案**：

> `「{场景名}」已执行完毕。请检查文档是否符合预期。`

`{场景名}` 取对应场景中文名（生成汇报 / 整理演示 / 选区编辑）。

---

## 工具列表

### 只读工具

> 以下为工具短名，实际调用名 = `PowerPoint__{短名}`（**双下划线**，如 `PowerPoint__get_document_info`）。
> 单下划线（`PowerPoint_get_document_info`）会返回 `tool not found`。另注意本产品用
> `get_document_info`，**不是** Word 的 `get_doc_info`。

`get_document_info`（文档信息）/ `get_path` / `get_ppt_outline`（大纲，**同时是取页数的唯一手段**）/
`get_slide_text`（指定页文本+备注，slideIndex 0基）/ `get_selected_text_range`（文本选区）

> **取页数只用 `get_ppt_outline`**：`get_ppt_outline` 返回逐页层级列表，**条目数 = 当前总页数**，
> 末条 `slideNumber` 即总页数。Level 1 白名单内**没有** `get_slide_count` / `get_slide_layouts`
> （属 Level 2，见 `../SKILL.md`「三·通用约定」第 11 条），因此**不要假设这两个工具可直接调用**：
> 判定空演示稿、核对页数、发现布局索引，一律用 `get_ppt_outline`（大纲里每页的标题/正文可直接看出
> 是否只有「单击此处添加标题」这类占位文字）。
> - `get_ppt_outline` 默认 `maxSlides=0`（全量）；**不要传 `maxSlides` 限制**，否则条目数只是扫描上限，不是总页数。
> - 若确实需要逐页形状/母版级信息，应先按 Level 2 流程检索可用工具，而不是硬编码工具名。

> **页码两套口径（必须区分，误用即错页/错话术）**：
> - `slideIndex`：**0 基**（第 1 页 = 0），所有工具的入参一律用它；
> - `slideNumber`：**1 基**（第 1 页 = 1），由 `get_ppt_outline` / `get_slide_text` 返回，
>   **向用户报告「第几页」时必须用 slideNumber**，不得把 slideIndex 当页码念给用户（会把第 N 页说成第 N-1 页，问题单 #22382）；
>   反过来也不得把 slideNumber 传给 slideIndex 入参（会改错页）。

### 1. generate_deck（生成汇报 Deck）

| 参数 | 必填 | 说明 |
|------|------|------|
| `slides` | ✅ | 每页：`title`、`body`（`\n` 分行）、`notes`、`layout`(Blank/Title/Text/TitleOnly/TwoColumnText/SectionHeader/Table/Chart)、逐页样式覆盖（title*/body* 的 FontSize/Color/FontFace/X/Y/W/H） |
| `slides[].blocks` | ❌ | 灵活内容块数组：任意数量的 `text`（文本框）/`shape`（形状），支持精确坐标或 `edge` 锚定定位，用于复杂版式 |
| `startPosition` | ❌ | 插入起始位置（0基，`-1`=末尾追加，也是默认值）。合法范围 `[0, 当前页数]`；负值一律按末尾追加处理；大于「当前页数」自动 clamp 回末尾追加 |
| 全局默认 | ❌ | titleFontSize=40、bodyFontSize=18、字体 Pretendard、标题色 1F1F1F、正文色 333333 等 |

> 建议 ≥3 页，每页配 `notes` 演讲者备注。

> **全新演示稿的空白页（重要，工单 #23884）**：新建演示文稿**自带 1 页空白占位页**（内容为「单击此处添加标题」），
> 这是产品正常行为，不是异常。而 `generate_deck` 的 `startPosition` 默认 `-1`=**末尾追加**，不会清理已有页，
> 因此「要 5 页」若直接生成会得到 **6 页**（1 页空白占位 + 5 页新页）。
>
> **PowerPoint 强制保留至少 1 页（关键前提，必须记住）**：演示文稿**不允许 0 页**。当文稿只剩 1 页时，
> 删除它虽然返回成功（`deleted:1` / `successCount:1`），**页数不会减少**——产品会自动补一页新的空白页。
> 因此「只剩 1 页时先删空页」这条路**无效**：全新演示稿只有 1 页，删掉后仍是 1 页，
> 再以默认 `startPosition` 生成 5 页，结果依旧是 6 页。
>
> 生成前须先判定当前是否为空演示稿（用 `PowerPoint__get_ppt_outline` 看页数与每页文字，
> 页数为 1 且该页只有「单击此处添加标题」等占位文字即为空演示稿），命中则二选一：
>
> | 方案 | 做法 | 适用 |
> |---|---|---|
> | **B. 原位插入后删尾页**（推荐 · 全新演示稿唯一可行） | `generate_deck` 传 `startPosition:0` 把新页插到最前，原空白页被挤到末尾，再调 `PowerPoint__delete_slides` 传 `slideIndexes:[N]`（N = 生成的页数，0 基末页索引）删掉它 | **当前仅 1 页（含全新演示稿）时只能用它**；也可用于需要保留原有版式/母版顺序的场景 |
> | A. 先删后生成 | 先调 `PowerPoint__organize_deck` 传 `deleteSlides`（或 `PowerPoint__delete_slides` 传 `slideIndexes`）删掉空白页，再以默认 `startPosition` 生成 | **仅适用当前 ≥2 页**（删完仍剩 ≥1 页，页数才会真的减少）；当前只剩 1 页时删除无效（见上文「强制保留至少 1 页」），**不要用** |
>
> 方案 B 实测链路（起点 1 页 → 要 5 页）：`generate_deck` 传 `startPosition:0` → 6 页；
> 再 `delete_slides` 传 `slideIndexes:[5]` → **5 页**，结果正确。
> 反例（方案 A 用在 1 页文稿上，实测无效）：`organize_deck` 传 `deleteSlides:[0]` → 返回 `deleted:1`
> 但页数**仍为 1**；再生成 5 页 → 6 页。**不要因为看到 `deleted:1` 就认为删成功了，必须用
> `get_ppt_outline` 复核页数是否真的变化。**
>
> - **不要把 `startPosition` 当「总页数控制」**：它只控制插入起点，不会删除任何既有页。
> - **向用户报页数必须用实际总页数**（`get_ppt_outline` 的条目数 / 末条 `slideNumber`），
>   不得直接报 `created` 数——`created:5` 与 `totalSlides:6` 同时出现正是本工单的现象。
> - 若用户明确要「在现有演示稿后面追加 N 页」，则保留默认 `-1`，此时总页数 = 原页数 + N，属预期，无需删除。

> **edge 与坐标优先级**：显式 `x`/`y` 优先于 `edge` 锚定；`edge` 按页尺寸推算（16:9 = 13.333"×7.5"）。`startPosition` 支持插入到开头（0）或中间指定页（0基），负值/超范围自动收敛到末尾追加，不会污染其他页。

> **能力边界（重要）**：`generate_deck` 场景本身仍不接受 `tableRows`/`tableData`/`table`/`chartData`/`chart`/`imagePath`/`image`（顶层或每页），命中会返回失败；这不代表 SDK 无插入能力。需要真实图片、表格或图表时，使用下方 `insert_slide_image`、`insert_slide_table`、`insert_slide_chart` 原子工具。

**`blocks` 内容块字段**：
| 字段 | 说明 |
|------|------|
| `type` | `text`（默认）/`shape` |
| `text` | 文本内容（type=text） |
| `shapeType` | 形状类型 ShapeType 枚举名：Rectangle/Ellipse/Triangle/RightArrow 等（type=shape） |
| `x`/`y` | 左上角坐标（英寸）；省略时可用 `edge` 锚定 |
| `w`/`h` | 宽度/高度（英寸） |
| `edge` | 锚定边：top/bottom/left/right，可组合（斜杠分隔，如 `bottom/right`） |
| `fontSize`/`fontFace`/`color` | 文字字号/字体/颜色 RRGGBB（type=text） |
| `fillColor`/`noLine` | 填充色 RRGGBB / 是否无边框（type=shape） |

**调用示例**（title/body + 灵活 blocks 混用）：
```json
{
  "slides": [
    {"title": "项目汇报", "body": "本季度进展顺利", "notes": "开场介绍"},
    {
      "title": "封面",
      "layout": "Blank",
      "blocks": [
        {"type": "text", "text": "2025 年度报告", "x": 1, "y": 2, "w": 11, "fontSize": 40, "color": "1F1F1F"},
        {"type": "shape", "shapeType": "Ellipse", "x": 10, "y": 5, "w": 2, "h": 1.5, "fillColor": "4A90D9", "noLine": true},
        {"type": "text", "text": "底部居中备注", "edge": "bottom/left", "w": 8, "fontSize": 14, "color": "999999"}
      ],
      "notes": "封面页用 flexible blocks 排版"
    },
    {"title": "关键成果", "body": "营收 120 万\n用户 1.2 万", "notes": "逐项讲解"}
  ]
}
```

### 2. organize_deck（整理演示稿）

| 参数 | 说明 |
|------|------|
| `deleteSlides` | 删除页索引列表（0基，指操作前原始文稿的页索引；内部自动补偿复制/移动产生的位移并从大到小删除）。⚠️ **演示文稿至少保留 1 页**：删到只剩 1 页后再删会返回成功但页数不变（自动补空白页），删除前先确认当前页数 ≥2 |
| `duplicateSlides` | 复制页 `[{slideIndex\|from+to, count=1, insertAfter}]`（索引均 0基；insertAfter=副本插入到指定页之后，支持连续范围） |
| `moveSlides` | 移动页 `[{slideIndex\|from+to, insertAfter}]`（索引均 0基；把页移动到指定页之后） |
| `applyTemplates` | 应用布局模板 `[{slideIndex, masterIndex=0, layoutIndex}]`（slideIndex 0基） |

> `applyTemplates` 的 (masterIndex, layoutIndex) 取值来源：Level 1 白名单内**没有**布局枚举工具
> （`get_slide_layouts` 属 Level 2）。两条可行路径：
> 1. **优先不指定模板**——省略 `applyTemplates`，保持每页原有版式，最稳；
> 2. 用户明确要求换版式时，先按 Level 2 流程检索是否有布局枚举工具，检索到再用其返回值填
>    (masterIndex, layoutIndex)；**禁止凭印象硬编码索引**（索引错会套错母版版式，且不易察觉）。

> **插入空白页并填充内容**：先用 `insert_slides` 按 `layout="Blank"` 创建空白页，再将返回/确认的 0 基 `slideIndex` 传给 `insert_slide_image`、`insert_slide_table`、`insert_slide_chart` 或 `insert_text_boxes` 等内容工具。`generate_deck` 也可用 `layout="Blank"` 插入空页，但该场景仍不接受表格/图表/图片数据字段。

**调用示例**（索引均 0 基：下例=删除第 6、3 页，复制第 2 页 1 份，给第 4 页套模板）：
```json
{
  "deleteSlides": [5, 2],
  "duplicateSlides": [{"slideIndex": 1, "count": 1}],
  "applyTemplates": [{"slideIndex": 3, "masterIndex": 0, "layoutIndex": 1}]
}
```

### 3. edit_selection（选区编辑）

参数 `edits` 数组，每项：`slideIndex`(0基,-1=当前选中页) / `shapeId`(0=自动找第一个文本形状) /
`text` / `append`(默认false) / `fillColor`(RRGGBB) / `x`/`y`/`w`/`h`(英寸) / `noLine` / `notes`(该页备注)

**调用示例**（`slideIndex` 0 基：下例=修改第 2 页）：
```json
{
  "edits": [
    {"slideIndex": 1, "shapeId": 0, "text": "更新后的标题", "append": false, "fillColor": "1F1F1F"}
  ]
}
```

### V4 直接编辑 API

除场景工具外，HShow 还注册以下原子能力：

- `insert_slide_image`：插入图片文件或 Base64 数据；坐标/尺寸单位为英寸。
- `insert_slide_table`：按二维数据或 rows/cols 插入表格。
- `insert_slide_chart`：按二维数据插入图表并设置标题、样式和系列颜色。
- `get_hidden_slides` / `set_hidden_slides`：查询或设置放映时隐藏的页；索引为 0 基。
- `get_slide_transitions` / `set_slide_transition`：读取或设置页面切换效果。
- `get_slide_animations` / `edit_slide_animations`：查看并管理形状动画，effect 使用 SDK 枚举名。
- `arrange_shapes`：对齐、组合或取消组合形状。
- `control_slide_show`：开始/结束放映、查询状态或跳转到放映页。
- `print_presentation`：打开宿主打印对话框；用户取消打印会返回未执行状态。
- `export_to_pdf`：将当前演示文稿导出为 PDF。

新增对象时建议先创建 `Blank` 幻灯片，再调用对应图片/表格/图表工具填充，避免依赖含内容占位符的版式。

移动/复制幻灯片仍使用 `organize_deck`，已按 V4 的 MoveSlide/CopySlides 原生 API 实现。

> 幻灯片标准尺寸 13.333"×7.5"（16:9），坐标单位为英寸，颜色为 "RRGGBB"。

---

## 使用方式

agent 识别到对应 Trigger 关键词（由 `fuxin-office` 路由）后，按以下流程执行：

1. 确定使用的场景工具（三选一）
2. 预检 PowerPoint 链路（调用 `PowerPoint__get_path`；完整预检见 `bridge.md`）；先根据用户目标确定本次 PPT 场景，
   从首次预检 MCP 调用起就使用该场景的埋点字段；例如 `generate_deck` 使用
   `skill_id=fuxin-ppt`、`scenario_id=UC-PPT-S1`，只读预检不得改用 `preflight-ppt`
   （只有独立预检才使用预检编号）；
   预检失败按 `bridge.md` 文案提示，**禁止执行写操作**；若确认 PowerPoint 未启动，且请求及场景必填参数完整，按 `bridge.md`「目标产品未启动时的路由拒绝埋点」仅调用一次目标场景工具，不得携带 `allow_launch=true`
3. **跨产品写前闸门**：若命中 `../SKILL.md`「五·一、跨产品写前闸门」（本产品非当前活跃 / 首次写），先按标准话术提示切换到 PowerPoint 窗口并等待口令，未通过前**不调用写工具**
4. 建立 MCP 会话（initialize → notifications/initialized）
5. 按上方参数表组装业务参数，一次调用场景工具；从预检、只读探测到场景工具和写后验证，**每次 MCP `tools/call` 都须在 `params._meta["com.foxit.office/telemetry"]` 携带同一组埋点字段**：
   - `skill_id`：本技能标识，固定填 `fuxin-ppt`
   - `scenario_id`：本次使用的场景编号，`generate_deck` 填 `UC-PPT-S1`、`organize_deck` 填 `UC-PPT-S2`、`edit_selection` 填 `UC-PPT-S3`
   - `agent_product`：当前真实运行的 Agent 平台（如 `workbuddy` / `vscode` / `cursor`），无法确证填 `unknown`；同一会话恒定，不随工具或场景变化（枚举见 `../SKILL.md`「三·通用约定」第 8 条）
   （网关据此关联到具体 Skill/场景与平台用于调用统计；传入即回显，不传则不回显）
   - ⚠️ **跨产品 E2E 例外**：若本次调用属于 `UC-E2E-01`（Word→Excel→PPT 三件套）中的一步，
     上述 `skill_id` / `scenario_id` **改按** `../SKILL.md`「三·通用约定」第 9 条填写：`skill_id`=`fuxin-office`、
     `scenario_id`=`UC-E2E-01`，原单产品编号降级填入选填的 `base_scenario_id`
     （如 `UC-PPT-S1`）。**未判为 E2E 时才使用上方的单产品编号**；`agent_product` 不受 E2E 影响，始终为当前真实平台
   - **禁止覆盖**：网关须以 Agent 传入值为准回显，工具默认值/按 tool_name 的推断值不得改写
     `scenario_id`；若响应 `_meta["com.foxit.office/telemetry"].scenario_id` 与传入值不一致，保留 `trace_id` 上报
6. 需要验证结果时调用只读工具（`PowerPoint__get_document_info` / `PowerPoint__get_ppt_outline` / `PowerPoint__get_slide_text`）读取内容；**这些校验调用同样携带第 5 步的同一组 `skill_id` / `scenario_id` / `agent_product`**，不得因为是只读校验就省略或改成 `preflight-ppt`；`get_ppt_outline` 与其它只读工具同等对待，不因工具名不同而例外。**核对页数必须用 `PowerPoint__get_ppt_outline` 的实际总页数（条目数 / 末条 `slideNumber`），不得直接采用 `generate_deck` 返回的 `created` 数**（见上文「全新演示稿的空白页」）
7. 向用户报告执行结果（成功数、失败数、生成内容摘要）
8. 不写前二次确认；写成功后按 `../SKILL.md` 汇总层 4.2 输出固定写后撤销提示（危险操作仍弹确认框）；失败/取消按 `bridge.md`「错误 / 异常（统一展示）」文案输出。**保存操作例外**：调用 `PowerPoint__save_document`（保存属不可逆、无撤销）前，先输出 `bridge.md` 「保存确认提示」并等待用户选择，用户确认后才保存调用，取消则中止（取消/超时文案见「错误 / 异常（统一展示）」）。**另存为**没有单独工具（网关不提供 `save_document_as`），用 `PowerPoint__save_document` 传 `path`（绝对路径）+ 可选 `format`（缺省从扩展名推断）实现，同样按保存确认处理

### 与其它编排规约协同

- **预检**：完整五层预检见 `bridge.md`
- **批次撤销**：写操作默认由网关合并为单事务；如需显式批次见 `batch-undo.md`
- **文档问答**：对演示稿内容提问见 `doc-qa.md`
- **跨产品**：Word→Excel→PPT 跨应用分步执行，见 `../SKILL.md`（E2E 分步编排）