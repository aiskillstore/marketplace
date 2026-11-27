# 福昕Office全家桶技能套件（fuxin-office-suite）

本套件是福昕Office的对外发布包。**对外仅暴露 1 个技能 `fuxin-office`**（唯一入口 / 汇总层），面向福昕Office（Word / Excel / PowerPoint）提供从连接预检、文档编排、只读问答到批次撤销、企业自定义流程的一站式能力。

产品级编排规约（bridge / word / excel / ppt / doc-qa / batch-undo / custom-tool）**不作为独立技能对外暴露**，全部収敛为 `reference/*.md` **内部参考文档**（与入口 `SKILL.md` 同级、位于套件根目录），由入口技能按需读取。

> 版本：1.0.3 (build 1.00.03.242) ｜ 默认语言：简体中文（跟随用户语言） ｜ 运行环境：FuxinAiService（端口由 `MCPServerPort.ini` 动态读取）

---

## 一、套件组成（1 个对外技能 + 7 个内部参考文档）

| 对外技能 | 角色 | 能力 |
|----------|------|------|
| `fuxin-office` | 唯一入口 / 汇总层 | 意图路由 + 跨产品 E2E 分步编排 + 交互/文案总则 |

| 内部参考文档（`reference/`） | 原能力域 | 能力 |
|------|------|------|
| `bridge.md` | 基础设施 | 5 层预检链路 + 统一用户提示出口 |
| `word.md` | Word 编排 | 写报告 / 术语统一排版 / 高亮批注 / 清单审查 |
| `excel.md` | Excel 编排 | 抽取数据建表 / 条件高亮 / 批量建图 |
| `ppt.md` | PowerPoint 编排 | 生成汇报 Deck / 整理演示 / 选区编辑 |
| `doc-qa.md` | 只读问答 | Word/Excel/PPT 内容问答、摘要、定位、数据核对 |
| `batch-undo.md` | 批次管理 | 批次事务边界 + 一次 Ctrl+Z 整组撤销 |
| `custom-tool.md` | 示例 | 组合 Word 场景工具封装企业自定义流程（如合同评审） |

### 技能体系结构

```
fuxin-office（唯一入口：路由 + E2E 分步 + 交互/文案总则）
├── SKILL.md                              （入口 Skill，本技能，与 reference 同级在套件根目录）
└── reference/                            （内部参考文档，不作为独立技能对外暴露）
    ├── bridge.md        连接与预检（5层链路 + 用户提示文案统一出口）
    ├── word.md          Word 文档编排（write_report / unify_terminology / highlight_and_comment / checklist_review）
    ├── excel.md         Excel 表格编排（extract_data_to_new_sheet / highlight_by_condition / batch_create_charts）
    ├── ppt.md           PowerPoint 演示编排（generate_deck / organize_deck / edit_selection）
    ├── doc-qa.md        文档只读问答（Word/Excel/PPT 内容问答、摘要、核对）
    ├── batch-undo.md    批次撤销（批次事务边界 + 一次性撤销引导）
    └── custom-tool.md   企业自定义操作流程示例（合同评审等）
```

---

## 二、能力介绍

以下能力均由 `fuxin-office` 按需读取内部参考文档后提供，**不作为独立技能暴露**。

### 1. 连接与预检（`reference/bridge.md`）
- 5 层预检：网关 → 产品注册 → 技能注册 → 后端可达性 → 活动文档
- 预检结果收敛为四档状态（未安装 / 未就绪 / 半就绪 / 就绪），未就绪时返回结构化诊断与明确操作指引，就绪时附活动文档清单（路径/只读/页数等）

### 2. Word 文档编排（`reference/word.md`）
- **write_report**：自动生成含标题、多级章节、表格、图片的文档，可选目录
- **unify_terminology**：批量查找替换 + 全文格式统一
- **highlight_and_comment**：查找定位 → 高亮 → 批注
- **checklist_review**：批注模式 / 汇总表模式 / 双模式

### 3. Excel 表格编排（`reference/excel.md`）
- **extract_data_to_new_sheet**：按列/范围抽取数据建新表，支持按行条件筛选（`filter`）
- **highlight_by_condition**：数值/文本/日期/重复值/排名条件高亮
- **batch_create_charts**：批量建图（柱状/折线/饼图/面积）

### 4. PowerPoint 演示编排（`reference/ppt.md`）
- **generate_deck**：生成汇报 Deck + 演讲者备注（≥3 页）
- **organize_deck**：删页 / 复制页 / 应用布局模板
- **edit_selection**：选区编辑助手

### 5. 文档只读问答（`reference/doc-qa.md`）
- 全文问答 / 摘要要点 / 内容定位 / 数据核对，**绝不修改文档**

### 6. 批次撤销（`reference/batch-undo.md`）
- 显式批次管理（begin → 操作 → end），一次撤销整组改动
- 网关默认将一次调用内的多步骤合并为单事务

### 7. 企业自定义流程示例（`reference/custom-tool.md`）
- 组合 Word 场景工具封装企业专属操作管线（如"合同评审"：术语统一 + 清单审查）

---

## 三、使用场景

| 场景 | 入口技能处理方式 |
|------|-----------|
| 写报告 / 季度报告 / 术语统一 / 排版 / 高亮批注 / 清单审查 | `fuxin-office` → 读取 `reference/word.md` |
| 抽列 / 抽取数据 / 条件高亮 / 批量建图 | `fuxin-office` → 读取 `reference/excel.md` |
| 生成汇报 / 做 PPT / 整理演示 / 选区编辑 | `fuxin-office` → 读取 `reference/ppt.md` |
| 问文档 / 总结 / 摘要 / 核对 | `fuxin-office` → 读取 `reference/doc-qa.md` |
| 批次 / 批量撤销 | `fuxin-office` → 读取 `reference/batch-undo.md` |
| 检查 Office / 网关预检 / 网关状态 | `fuxin-office` → 读取 `reference/bridge.md` |
| 一键生成合同评审报告等企业流程 | `fuxin-office` → 读取 `reference/custom-tool.md` |
| 跨产品 / 多步骤 / 未归类 | `fuxin-office`（E2E 分步） |

---

## 四、调用方式

### 1. 部署
- 将本套件解压到技能加载目录，**只需部署入口 `SKILL.md` 及其同级 `reference/` 参考文档**（均位于套件根目录），平台仅发现并暴露 `fuxin-office` 这一个技能。
- 启动 `FuxinAiService`（端口由 `%AppData%\Foxit Software\Fuxin Office\MCP\MCPServerPort.ini` 的 `ListenPort` 读取）。

### 2. 前置条件
- 网关已启动
- 对应产品已注册（产品分类为 `Word` / `Excel` / `PowerPoint`）
- FuxinOfficeWord / FuxinOfficeExcel / FuxinOfficePPT 应用已启动且插件已加载
- 已打开活动文档

### 3. 调用流程
1. **预检**：先按 `reference/bridge.md` 跑 5 层预检
2. **路由 / 编排**：按用户意图读取对应 `reference/*.md`，调用其场景工具
3. **批次**：多步骤写操作如需整体撤销，归入同一批次（`reference/batch-undo.md`）
4. **汇报**：汇总各步骤结果并输出

### 4. 输入输出
- **输入**：自然语言任务描述（由 `fuxin-office` 入口层解析）
- **输出**：执行结果 + 汇总汇报
- 入参校验 schema 见 `schema/input_schema.json`；可运行样例见 `examples/sample_case.json`

---

## 五、注意事项

1. **网关端口非固定**：FuxinAiService 端口由 `%AppData%\Foxit Software\Fuxin Office\MCP\MCPServerPort.ini` 的 `ListenPort` 读取（见 `reference/bridge.md`「运行端口」），非固定 58688；产品分类为 `Word` / `Excel` / `PowerPoint`（不是 FuxinOfficeWord / FuxinOfficeExcel / FuxinOfficePPT）。
2. **写操作不写前二次确认**：用户已下达写指令即视为可写，Skill 直接执行写操作；写成功后提示固定撤销文案（回复「撤销」或在福昕Office按 Ctrl+Z）。危险操作（删除页 / 清空 / 批量覆盖）仍弹确认对话框。**保存操作例外**：`save_document`（保存不可逆、无撤销）在保存前必须弹窗确认，用户确认后才执行，取消则不保存。**另存为**无独立工具，用 `save_document` 传 `path` + 可选 `format` 实现，同样需确认。
3. **预检必须**：写操作前必须按 `reference/bridge.md` 预检。
4. **测试原则**：预检与只读探活使用 REST + 只读工具；**禁止用写操作做探测**。
5. **工具不可用**：提示重启 `FuxinAiService`（网关）后重试。
6. **批量撤销**：写操作默认由网关合并为单事务；显式批次见 `reference/batch-undo.md`。
7. **只读能力**：`reference/doc-qa.md` 只读，绝不调用写工具。
8. **依赖完整性**：`fuxin-office` 依赖其内部 `reference/` 7 份参考文档，需一并部署，缺一将导致对应能力不可用。

---

## 六、目录结构

```
skills/
├── manifest.json              # Skill 套件包清单（包 ID、版本、权限、资源目录；skills 仅列 fuxin-office）
├── README.md                  # 对外使用文档（本文档）
├── CHANGELOG.md               # 版本变更记录
├── LICENSE.md                 # 授权声明
├── SKILL.md                   # 唯一对外技能 fuxin-office（入口/汇总层）
├── schema/
│   └── input_schema.json      # 入参 JSON Schema 校验文件
├── examples/
│   └── sample_case.json       # 输入输出示例用例
└── reference/                 # 内部参考文档（不作为独立技能对外暴露）
    ├── bridge.md
    ├── word.md
    ├── excel.md
    ├── ppt.md
    ├── doc-qa.md
    ├── batch-undo.md
    └── custom-tool.md
```

---

## 七、授权与支持

- 授权声明见 `LICENSE.md`。
- 版本变更记录见 `CHANGELOG.md`。

© 2026 福州福昕网络技术有限责任公司. All rights reserved.
