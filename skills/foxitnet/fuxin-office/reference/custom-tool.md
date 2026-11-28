# 参考文档：fuxin-custom-tool — 企业自定义文档操作示例

> **收敛说明**：本文档为 `fuxin-office` 唯一入口技能**内部参考文档**，演示如何组合 Word 场景工具
> 封装企业专属流程（如合同评审）。**不作独立技能对外暴露**（无 frontmatter / Trigger / description），
> 也不纳入 `fuxin-office` 默认路由，仅在用户**显式引用**「自定义流程」类需求时，按需读取本文档作为示例参考。
> 企业若需独立技能形式可另行封装。
>
> **定位**: 示例规约。演示如何把多个 Word 场景工具组合成**企业自定义操作流程**，
> 以便企业参照套改为自己公司的专属文档操作。**不新增任何网关工具**，仅做组合编排。
> **产品大类**: `Word`
> **依赖**: FuxinAiService（端口见 `bridge.md`「运行端口」，由 `MCPServerPort.ini` 读取）+ Word 场景工具 + `word.md` / `bridge.md`
> **需要确认**: 是（会修改/生成文档；不写前二次确认，写后提示撤销）

---

## 功能概述

本文档提供**一组演示用的企业自定义批量处理流程**示例（以"合同评审"为例），
展示如何组合 `word.md` 的 4 个场景工具，把一句企业指令展开为一条完整的处理管线。

三种常用管线：

| 管线 | 组合的场景工具 | 效果 |
|------|----------------|------|
| ① 合同评审（示例重点） | unify_terminology → checklist_review | 术语统一 + 清单项逐项加批注/汇总表 |
| ② 生成+自检报告 | write_report → highlight_and_comment | 写报告后再按规则自查并高亮 |
| ③ 全文规范统一 | unify_terminology → highlight_and_comment | 批量替换 + 检查项高亮提醒 |

> 管线内部各步骤统属同一 MCP 会话，逐步骤调用 `word.md` 的场景工具，
> 由网关合并为单事务，用户一次 Ctrl+Z 即可整组撤销（见 `batch-undo.md`）。

---

## 架构

```
用户 → fuxin-custom-tool（本示例：定义"企业自定义操作流程"）
    │ 依次路由到
    ▼
fuxin-word 场景工具（write_report / unify_terminology / highlight_and_comment / checklist_review）
    ▼
FuxinAiService（端口见 `bridge.md`「运行端口」） → FuxinOfficeWord App
```

---

## 前置条件与预检

1. FuxinAiService 已启动（端口由 `MCPServerPort.ini` 读取，见 `bridge.md`「运行端口」）
2. Word 产品已注册，FuxinOfficeWord 已启动、插件已加载
3. 已打开活动文档（write_report 会生成新文档；其余需要目标文档）

预检链路统一走 `bridge.md` 的 5 层预检，通过后再进入管线。

---

## 企业自定义管线编排示例

### 管线 1：一键合同评审

企业指令："评审这份合同，统一术语并逐项检查必填项。"

**步骤编排**（按顺序依次调用 `word.md` 场景工具）：

1. **语义检查**：先跑预检 → 链路就绪
2. **统一术语**：`unify_terminology`
   ```json
   {
     "replacements": [
       {"find": "合约", "replace": "合同"},
       {"find": "价格", "replace": "价款"}
     ]
   }
   ```
3. **清单审查**：`checklist_review`（评审检查表）
   ```json
   {
     "checklist": [
       {"item": "甲方主体名称", "status": "待核对", "note": "须完整填写"},
       {"item": "合同金额", "status": "已填", "note": "核对大小写"},
       {"item": "签署日期", "status": "待补充"}
     ],
     "mode": "both",
     "summaryTitle": "合同评审汇总"
   }
   ```
4. **高亮标记**：（可选）对命中重点项高亮
   ```json
   { "targets": [{"text": "合同金额", "highlightColorIndex": 1}] }
   ```
5. **汇报**：汇总各步结果，说明成功/失败项与如何撤销

### 管线 2：生成报告并自检

1. `write_report` 生成合同摘要报告（含标题、章节、表格）
2. `highlight_and_comment` 对关键结论高亮
3. 汇报生成内容与高亮数

### 管线 3：全文规范统一

1. `unify_terminology` 批量替换（统一术语）
2. `highlight_and_comment` 对检查关键词高亮（对照清单逐项勾核）

---

## 如何扩展为企业自定义工具

企业如需自己的专属操作，把本示例的管线改为自己的规则：

1. **确定指令**：定义一句触发词（如"生成技术验收单"）
2. **选择场景工具**：从 Word/Excel/PPT 的 4/3/3 个场景工具中选出需要的
3. **定义固定参数**：把企业固定规则（术语库、检查表、表头、列）固化为默认参数
4. **编排步骤顺序**：按业务顺序依次调用各场景工具
5. **补充预检与撤销**：入口跑预检，末尾给撤销引导

> 企业自定义操作 = 触发词 + 固定默认参数 + 场景工具序列 + 预检/撤销引导。
> 不修改网关，不新增底层插件，只做组合编排。

---

## 与其它编排规约协同

- **单点场景工具**：`word.md` / `excel.md` / `ppt.md` 的完整参数表
- **预检**：`bridge.md` 5 层链路
- **批次撤销**：管线为一事务，`batch-undo.md` 提供撤销引导
- **路由入口**：`../SKILL.md` 汇总层承载所有路由入口，本示例作为其自定义扩展示例