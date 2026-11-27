# 参考文档：fuxin-word — Word 文档编排规约

> **收敛说明**：本文档为 `fuxin-office` 唯一入口技能**内部参考文档**，承载「Word 文档编排」规约，
> **不作独立技能对外暴露**（无 frontmatter / Trigger / description）。由 `fuxin-office` 按需读取，
> 企业若需独立技能形式可另行封装。
>
> **产品分类**: `Word`
> **依赖**: FuxinAiService（端口见 `bridge.md`「运行端口」，由 `MCPServerPort.ini` 读取）+ Word 产品场景工具
> **需要确认**: 是（写操作；不写前二次确认，写后提示撤销；**保存操作 `save_document` 例外，需提前确认**（另存为同此，用 `save_document` 传 `path`）——见 `../SKILL.md` 4.2）

---

## 功能概述

本规约通过 MCP 网关**直接调用 Word 产品的场景工具**（场景工具已在网关内部实现，
agent 只需传参直接调用，无需手动编排原子技能、管理会话或处理批次事务）。
覆盖 4 类文档编排任务：

1. **写报告** — 自动生成含标题、章节正文、表格、图片的文档，可选目录
2. **统一术语排版** — 批量查找替换 + 可选全文格式统一
3. **选区高亮批注** — 查找文本 → 高亮 → 添加批注
4. **清单审查** — 对清单项添加批注和/或插入汇总表

所有写操作由网关内部合并为事务，用户可**一次 Ctrl+Z 整组撤销**；
若需显式管理批次，见 `batch-undo.md`。

---

## 架构

```
用户 (VS Code Copilot)
    │ MCP 协议 (tools/call)
    ▼
FuxinAiService（端口见 `bridge.md`「运行端口」）
    │ 转发到 Word 产品
    ▼
fuxin-word 场景工具（网关内部实现）
    │
    ▼
FuxinOfficeWord App (Office 进程)
```

---

## 前置条件

1. **FuxinAiService 已启动**（端口由 `MCPServerPort.ini` 读取，见 `bridge.md`「运行端口」）
2. **Word 产品已注册**（产品名 `Word`），FuxinOfficeWord 应用已启动、插件已加载
3. **已打开一个活动文档**（所有工具都会修改文档内容）

### 预检

执行任何写操作前必须预检，完整预检流程见 `bridge.md`。本规约快速探活：

- 调用 `Word__get_doc_info` / `Word__get_doc_status` 探活：成功且有活动文档 → 就绪
- 未安装 / 未就绪（网关不可达、产品未启动、插件未加载）/ 半就绪（无活动文档）/ 就绪，
  统一按 `bridge.md` 定稿文案逐字输出，**禁止**自行发明或改动文案

> 📊 **探活调用也要带埋点**：上面 `Word__get_doc_info` / `Word__get_doc_status`
> 每一次调用，都须在 `params._meta["com.foxit.office/telemetry"]` 携带 `skill_id` / `scenario_id` / `agent_product`。
> 取值取决于本次目的：已确定 Word 业务场景（如 `write_report`）→ 用该场景值
> （`fuxin-word` / `UC-WORD-S1`）；仅独立「检查 Office 状态」→ `fuxin-office-bridge` / `preflight-word`；
> 属于 `UC-E2E-01` → `fuxin-office` / `UC-E2E-01`。见 `../SKILL.md`「一·只读工具埋点映射」。
> `agent_product` 填当前真实平台（如 `workbuddy`），无法确证填 `unknown`，会话内恒定。

> 预检全程只读，禁止任何写入操作。预检失败时按 `bridge.md` 文案提示，禁止执行写操作。

### 场景收尾

> **三档区分**，按操作粒度输出，不可互相替代：
> - **单次操作成功**：单步操作完成 → `已在文档中完成「{操作名}」。请在福昕Office中查看效果。`
> - **一组操作完成**：同一场景内多步/批量成组完成 → `本组修改已完成。如需撤销，请在福昕Office中按一次「撤销」即可恢复整组操作。`
>
>     （若为该组写操作，还应追加写后撤销提示。）
> - **场景任务完成**：整个场景完全执行完毕后 → 输出下方定稿场景收尾文案。

每个场景工具执行完成后，若该场景已整体结束，按 `../SKILL.md` 汇总层「五、用户提示文案总则」对齐定稿输出统一收尾，**中途的单次/一组操作不提前输出场景完成文案**：

> `「{场景名}」已执行完毕。请检查文档是否符合预期。`

`{场景名}` 取本规约对应场景中文名（写报告 / 术语统一与排版 / 高亮批注 / 清单审查）。

写操作场景在收尾后追加固定撤销提示：

> 改好了。要撤回改动：回复「撤销」，或在福昕Office按 Ctrl+Z。

---

## 工具列表

`get_char_format` 返回 SDK 可读字段（字号、加粗、斜体、下划线、删除线、字宽、字距、上下标、着重号、高亮色等）。Hancom SDK 将 `FontNameEa`、`FontNameHansi` 和 `TextColor` 定义为 set-only 字段，不会从 `GetCharShape()` 返回；需要读取字体名或文字颜色时，应明确说明当前接口限制，不得臆造结果。

### 1. write_report（写报告）

| 参数 | 必填 | 说明 |
|------|------|------|
| `title` | ✅ | 报告标题 |
| `sections` | ✅ | 章节列表：`heading`、`level`(1-3)、`content`(简单模式) 或 `blocks`(高级模式)、`pageBreakBefore` |
| `blocks` | ❌ | 内容块：`text` / `table`(headers/rows/caption) / `image`(path) / `pageBreak` |
| `format` | ❌ | 全局格式：fontName、各级字号、bodyAlignment(0左/1中/2右/3两端)、firstLineIndent、lineSpacing(pt：12=单倍/18=1.5/24=双倍) |
| `includeToc` / `tocMaxLevel` | ❌ | 目录开关（默认 false）/ 最大级别（默认 3） |

**调用示例**：
```json
{
  "title": "2026年第三季度项目总结报告",
  "includeToc": true,
  "sections": [
    {"heading": "一、总体概述", "level": 1, "content": "本季度进展顺利。"},
    {"heading": "二、关键数据", "level": 1, "blocks": [
      {"type": "table", "caption": "季度关键指标",
       "headers": ["指标", "目标", "实际"],
       "rows": [["营收", "100万", "120万"]]}
    ]}
  ]
}
```

### 2. unify_terminology（术语统一/排版整理）

| 参数 | 必填 | 说明 |
|------|------|------|
| `replacements` | ✅ | `[{find, replace, matchCase?, wholeWord?}]`；仅排版时传 `[]`，同时设置 `applyFormat:true` 并提供 `format` |
| `applyFormat` / `format` | ❌ | 是否统一全文排版（默认 false）/ fontName、fontSize、lineSpacing、alignment |

**调用示例**：
```json
{
  "replacements": [{"find": "OFfice", "replace": "Office", "matchCase": true}],
  "applyFormat": true,
  "format": {"fontName": "宋体", "fontSize": 12, "lineSpacing": 18, "alignment": 3}
}
```

**仅排版示例**（无需构造等价替换规则）：
```json
{
  "replacements": [],
  "applyFormat": true,
  "format": {"fontSize": 12, "lineSpacing": 18, "alignment": 3}
}
```

执行成功时返回 `ok:true`、`formatApplied:true`、`totalReplaced:0`、`ruleCount:0`。未开启排版时，`replacements` 不允许为空数组。

### 3. highlight_and_comment（高亮批注）

- `targets: [{text, highlightColorIndex?, commentText?, bold?, matchCase?, wholeWord?, findAll?}]`
- `commentAuthor` 默认 "AI助手"；不传 `commentText` 则仅高亮；`highlightColorIndex=-1` 不高亮

**未命中语义（#23876）**：全部目标都未在文档中找到 → 返回 `ok:false` + `errorCode=TEXT_NOT_FOUND`，此时**不会有任何高亮或批注**，不得向用户报成功；
部分未命中 → `ok:true`，并用 `notFoundItems` 列出未命中的目标文本，据此提示用户核对文本（注意多余空格、全半角与大小写）后重试。
`targets` 中没有任何有效 `text` → `ok:false` + `errorCode=NO_VALID_TARGET`。`notFoundItems` 恒定返回（无未命中时为空数组）。

**调用示例**：
```json
{
  "targets": [
    {"text": "AI001", "highlightColorIndex": 1, "commentText": "请核对编号", "findAll": true},
    {"text": "合同", "highlightColorIndex": 4}
  ],
  "commentAuthor": "审查助手"
}
```

### 4. checklist_review（清单审查）

| 参数 | 必填 | 说明 |
|------|------|------|
| `checklist` | ✅ | `[{item, status?, note?, …自定义字段}]` |
| `mode` | ❌ | `comment` / `summary_table`(默认) / `both` |
| `columns` | ❌ | 汇总表自定义列 `[{key, title}]`，默认三列 |
| `summaryTitle` / `highlightFound` / `highlightColorIndex` | ❌ | 汇总标题 / 是否高亮命中项（默认 false）/ 颜色（默认 1 绿） |

**未命中语义（#23876，与 `highlight_and_comment` 一致）**：全部清单项都未在文档中找到 → `ok:false` + `errorCode=CHECKLIST_NOT_FOUND`，未添加任何批注或高亮；
部分未命中 → `ok:true`，用 `notFoundItems` 列出未命中的清单项名称。`checklist` 中没有任何有效 `item` → `ok:false` + `errorCode=NO_VALID_TARGET`。
纯 `summary_table` 模式不执行文档查找，不产生未命中，始终 `ok:true`。`notFoundItems` 恒定返回（无未命中时为空数组）。

**调用示例**：
```json
{
  "checklist": [
    {"item": "营业执照", "status": "已提供", "note": "在有效期内"},
    {"item": "资质证书", "status": "待补充"}
  ],
  "mode": "both",
  "summaryTitle": "文件清单审查汇总"
}
```

### 高亮颜色索引

-1=无 0=黄 1=绿 2=青 3=粉 4=蓝 5=红 6=深蓝 7=青绿 8=深绿 9=紫 10=深红 11=橄榄黄 12=灰 13=浅灰 14=黑

---

## 使用方式

agent 识别到对应 Trigger 关键词（由 `fuxin-office` 路由）后，按以下流程执行：

1. 确定使用的场景工具（四选一）
2. 预检 Word 链路（调用 `Word__get_path`；完整预检见 `bridge.md`）；这一步已属于当前选定的 Word 场景，
   因此从本次首次 MCP `tools/call` 起就传入该场景的埋点字段，例如 `write_report` 使用
   `skill_id=fuxin-word`、`scenario_id=UC-WORD-S1`，只读预检不得改用 `preflight-word`
   （只有独立预检才使用预检编号）；
   预检失败按 `bridge.md` 文案提示，**禁止执行写操作**；若确认 Word 未启动，且请求及场景必填参数完整，按 `bridge.md`「目标产品未启动时的路由拒绝埋点」仅调用一次目标场景工具，不得携带 `allow_launch=true`
3. **跨产品写前闸门**：若命中 `../SKILL.md`「五·一、跨产品写前闸门」（本产品非当前活跃 / 首次写），先按标准话术提示切换到 Word 窗口并等待口令，未通过前**不调用写工具**
4. 建立 MCP 会话（initialize → notifications/initialized）
5. 按上方参数表组装业务参数，一次调用场景工具；从预检、只读探测到场景工具和写后验证，**每次 MCP `tools/call` 都须在 `params._meta["com.foxit.office/telemetry"]` 携带同一组埋点字段**：
   - `skill_id`：本技能标识，固定填 `fuxin-word`
   - `scenario_id`：本次使用的场景编号，`write_report` 填 `UC-WORD-S1`、`unify_terminology` 填 `UC-WORD-S2`、`highlight_and_comment` 填 `UC-WORD-S3`、`checklist_review` 填 `UC-WORD-S4`
   - `agent_product`：当前真实运行的 Agent 平台（如 `workbuddy` / `vscode` / `cursor`），无法确证填 `unknown`；同一会话恒定，不随工具或场景变化（枚举见 `../SKILL.md`「三·通用约定」第 8 条）
   （网关据此关联到具体 Skill/场景与平台用于调用统计；字段属于请求元数据，不放入业务 `arguments`）
   - ⚠️ **跨产品 E2E 例外**：若本次调用属于 `UC-E2E-01`（Word→Excel→PPT 三件套）中的一步，
     上述 `skill_id` / `scenario_id` **改按** `../SKILL.md`「三·通用约定」第 9 条填写：`skill_id`=`fuxin-office`、
     `scenario_id`=`UC-E2E-01`，原单产品编号降级填入选填的 `base_scenario_id`
     （如 `UC-WORD-S1`）。**未判为 E2E 时才使用上方的单产品编号**；`agent_product` 不受 E2E 影响，始终为当前真实平台
   - **禁止覆盖**：网关须以 Agent 传入值为准回显，工具默认值/按 tool_name 的推断值不得改写
     `scenario_id`；若响应 `_meta["com.foxit.office/telemetry"].scenario_id` 与传入值不一致，保留 `trace_id` 上报
6. 需要验证结果时调用只读工具（`Word__get_doc_status` / `Word__get_document_text` / `Word__get_doc_info` / `Word__get_outline`）读取文档内容；**这些校验调用同样携带第 5 步的同一组 `skill_id` / `scenario_id` / `agent_product`**，不得因为是只读校验就省略或改成 `preflight-word`
7. 向用户报告执行结果（成功数、失败数、生成内容摘要）；若工具返回 `ok:false` 且为参数类错误（如 `sections不能为空`、`title不能为空`、缺 items/rows 等），**不得回显原始 error**，按 `bridge.md`「参数有误」定稿文案提示
8. 写成功后，按 `../SKILL.md` 汇总层 4.2 输出**写后撤销提示**（改好了。要撤回改动：回复「撤销」，或在福昕Office按 Ctrl+Z。）；失败/取消按 `bridge.md`「错误 / 异常（统一展示）」文案输出。危险操作（删除页/清空/批量覆盖）仍按产品要求弹确认对话框后再执行。**保存操作例外**：调用 `Word__save_document`（保存属不可逆、无撤销）前，先输出 `bridge.md` 「保存确认提示」并等待用户选择，用户确认后才真正保存，取消则不保存（取消/超时文案见「错误 / 异常（统一展示）」）。**另存为**没有单独工具，用 `Word__save_document` 传 `path`（绝对路径）+ 可选 `format`（缺省从扩展名推断）实现，同样按保存确认处理

### 与其它编排规约协同

- **预检**：完整五层预检见 `bridge.md`
- **批次撤销**：写操作默认由网关合并为单事务；如需显式 begin/end/undo 批次见 `batch-undo.md`
- **文档问答**：对已生成的文档内容提问见 `doc-qa.md`
- **跨产品**：Word→Excel→PPT 跨应用分步执行，见 `../SKILL.md`（E2E 分步编排）