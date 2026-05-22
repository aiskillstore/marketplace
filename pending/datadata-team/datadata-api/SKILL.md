---
name: datadata-api
description: "通过 CLI 查询 Datadata — 运行临时 SQL、检查数据源元数据、列表和描述表、下载 NDJSON/CSV 格式结果。当用户提到 Datadata、想查询数据、探索数据源或表 schema、获取查询结果时使用此 skill。触发：Datadata、数据探索、SQL查询、表检查、执行结果。"
---

## 功能概览

本 skill 围绕两大核心功能：

### 查询数据

- **搜索数据源** — 支持社区公开搜索（无需登录）、私有数据源搜索、`username/name` 精确查找
- **元数据查询** — 检查数据源信息、列出表、描述列结构
- **执行 SQL 查询** — 通过 `execute-adhoc` 执行 SELECT 查询，支持 DuckDB 和 ClickHouse 引擎，DuckDB 引擎可跨数据源关联
- **结果下载** — 以 NDJSON 或 CSV 格式下载查询结果
- **Schema 扫描** — 触发异步扫描，刷新数据源的表元数据

### 录入数据

- **Data Spaces 表管理** — 在 ducklake 数据空间中创建表、批量插入数据、删除表
- 录入的数据同样可通过 `execute-adhoc` 查询

### 用户信息

- **当前用户及 API Key 权限** — 通过 `whoami` 获取用户资料、API Key 元数据及权限列表，用于验证可用性

### 生成脚本

- 提供 `urllib.request` 直接调用示例，零额外依赖（详见 [references/api.md](./references/api.md)）

## 使用场景

当用户提出以下需求时，应激活本 skill：

| 场景                        | 示例                                                                             |
| --------------------------- | -------------------------------------------------------------------------------- |
| 查询 Datadata 中的数据      | "帮我查一下销售数据"、"统计上个月的用户增长"                                     |
| 搜索数据源                  | "搜索名叫 customers 的数据源"、"找一下 hungtcs 的公开数据"、"看看我有哪些数据源" |
| 探索数据源结构              | "看看这个 datasource 有哪些表"、"描述一下 customers 表的字段"                    |
| 跨数据源关联分析            | "把 MySQL 的订单表和 CSV 的用户信息 join 一下"                                   |
| 数据写入与持久化            | "把爬虫结果存到 data space 里"、"批量插入这些数据"                               |
| 获取查询结果                | "下载上次查询的 NDJSON 结果"                                                     |
| 以编程方式调用 Datadata API | "帮我写一个 Python 脚本直接调 Datadata API"                                      |
| 验证 API Key                | "检查一下当前 Key 是否有效"                                                      |

## 概念

- **Datasource** — 查询目标的数据源。不同类型的 datasource（ducklake、MySQL、ClickHouse、CSV 等）有不同的表命名约定。
- **Data space** — 录入数据的目标。`ducklake` 类型 datasource 独有的能力，支持创建表、批量插入和删除表。data-space 名称为 datasource 的 `name`（通过 `get-datasource-info` 获取）。录入后可通过 `execute-adhoc` 像查询普通数据源一样查询其中的数据。
- **Query** (`execute-adhoc`) — **只读**抽象，包含 SQL 脚本（SELECT 仅），datasource 绑定和查询引擎类型。查询不会立即执行，直到创建一个 execution。
- **Execution** (`get-execution-result`) — 运行查询的抽象。每次调用 `execute-adhoc` 创建一个 execution 并返回 `executionId`。使用该 ID 异步获取结果。

## 环境变量

| 变量名              | 必填 | 默认值                     | 对应 CLI 标志 | 描述                                                       |
| ------------------- | ---- | -------------------------- | ------------- | ---------------------------------------------------------- |
| `DATADATA_API_KEY`  | 否   | —                          | `--api-key`   | API 认证密钥，始终以 `ak_` 开头                            |
| `DATADATA_BASE_URL` | 否   | `https://www.datadata.com` | `--base-url`  | API 基础地址，仅本地开发或测试时需覆盖（不要询问用户此值） |

> **提示：** CLI 全局标志（`--base-url`、`--api-key`）必须在子命令**之前**出现，否则报"unrecognized arguments"。

### 获取 API Key

**设备授权（推荐）**：CLI 缺少 API Key 时，Agent 在同一轮对话中执行三步：`device-flow-start` → 浏览器打开 `verificationUriComplete` → `device-flow-complete`。成功后 Key 自动持久化，有效期 90 天。详见 [references/cli.md](./references/cli.md#认证)。

**手动设置（备选）**：登录 datadata.com → Settings → API Keys → 创建（权限勾选 queries:execute-adhoc, executions:get, datasources:read, datasources:scan, data-spaces:write）。

## 工作流

1. 配置认证（设备授权自动签发，或手动设置 API Key）
2. 搜索数据源（如用户未提供确切数据源 ID）→ 查询元信息 → 执行查询 → 获取结果

详见 [references/cli.md](./references/cli.md#常见工作流)。Data Spaces 表管理见 [references/data-spaces.md](./references/data-spaces.md)。

## 规则

### 🔴 设备授权

当 CLI 返回 exit code 2 且输出含"未找到 API Key"时，立即执行：`device-flow-start` → 浏览器打开 `verificationUriComplete` → `device-flow-complete` → 重跑原命令。**全程在同一轮对话中完成，不要中断询问用户。**

### 🔴 搜索数据源：必须让用户确认，禁止自动选用

`search-datasource` 返回的结果**绝不能**由 Agent 自动选取第一个使用。这是危险操作 — 选错数据源可能导致查询错误数据、写入错误目标等严重后果。

**正确流程：**

1. 执行 `search-datasource` 获取结果列表
2. 将结果以序号 + 关键信息（`name`、`displayName`、`username`、`visibility`）列表形式呈现给用户
3. **等待用户明确选择序号**或确认后再使用对应的 `id` 进行后续操作

即使搜索结果只有 1 条，也应让用户确认后再继续。

### 🔴 最小操作原则：完成一步即停，禁止猜测意图

Agent 只执行用户**明确要求**的操作，完成当前步骤后**立即停止**，等待用户下一个指令。禁止根据上一步的结果自动推断下一步该做什么。

典型违规示例：

- 用户："用 customers 数据源" → Agent 确认数据源后又自动 list-tables、describe-table、查数据
- 用户："看看有哪些表" → Agent list-tables 后又自动 describe-table 所有表

用户说"用 xxx"就是只用 xxx，不是"用 xxx 然后把里面所有东西翻一遍"。每一步之后等用户给明确指令。

### 查询

`execute-adhoc` 的 SQL 编写约定、安全性约束及结果处理方式，详见 [references/query-guide.md](./references/query-guide.md)。

### 错误处理

- **exit code 2 + "未找到 API Key"**：这不是错误，是触发设备授权的信号。立即执行 [获取 API Key](#获取-api-key) 中的四步流程，不要询问用户
- **401**：API Key 无效或过期。若 Key 来自配置文件则自动清除并提示重新授权
- **403**：分两种情况：
  - 响应含 `api key not exists` 等 Key 相关提示 → Key 失效，自动清除配置
  - 响应含 `permission denied` → **正常的权限拒绝**（如操作他人数据源），Key 本身有效，**不清除配置**，向用户说明权限不足即可
- **任何 404**：立即停止。可能是资源不存在（如 datasource ID 无效、execution ID 不存在）或端点路径错误。检查资源 ID 是否正确；若多个端点均 404，可能是 `DATADATA_BASE_URL` 配置有误
- `5xx` 或网络超时：等待 3 秒后重试一次。若仍失败，报告错误并附加 `executionId`
- `--timeout` 超期（后端返回超时，查询仍在运行）：返回 `executionId` — 建议使用更大的 `--timeout` 或稍后检查

### 查询结果处理

`get-execution-result` 下载的 NDJSON/CSV 文件**绝不能直接整个读入上下文**，文件可能非常大（数万行、数百 MB），直接读取会撑爆上下文。

**安全流程：**

1. 报告 `outputPath`、`rowCount`、`format`、`bytes` 等元信息
2. 按需查看：用 `head`/`tail` 看前几行或后几行预览
3. 用户要求时才读取完整内容或做进一步分析
4. 大数据集优先用 `wc -l`、`grep`、`awk` 等命令行工具本地处理，不要加载到上下文

### 输入

- API key 以 `ak_` 开头，datasource ID 为随机字符串（如 `CXNGJifvqE48kdzKVC9o5`）。不要将 datasource ID 误当作 `--api-key`
- `create-table` 和 `insert-rows` 要求 API key 额外拥有 `data-spaces:write` 权限
- 认证和基础地址通过环境变量或 CLI 全局标志配置，详见上方 [环境变量](#环境变量)
- 编写 SQL 前先检查数据源/表/列元信息
- **仅描述需要的表**：用 `list-tables` 找候选项，再对特定表用 `describe-table`。不要导出所有表的所有列

## References

本 skill 由以下文件组成，按用途分类：

| 类型        | 文件                        | 说明                            |
| ----------- | --------------------------- | ------------------------------- |
| 入口脚本    | [scripts/datadata_query.py] | CLI 主入口，stdlib-only Python  |
| CLI 参考    | [references/cli.md]         | 子命令、参数与工作流示例        |
| API 参考    | [references/api.md]         | REST API 端点与 urllib 调用示例 |
| 查询指南    | [references/query-guide.md] | 查询引擎、表命名、标识符引用等  |
| Data Spaces | [references/data-spaces.md] | 数据空间表管理完整说明          |

[scripts/datadata_query.py]: ./scripts/datadata_query.py
[references/cli.md]: ./references/cli.md
[references/api.md]: ./references/api.md
[references/query-guide.md]: ./references/query-guide.md
[references/data-spaces.md]: ./references/data-spaces.md
