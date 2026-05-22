# Data Spaces（数据空间）

Data Spaces 是 Datadata 中 `ducklake` 类型 datasource 独有的表管理能力，支持用户创建、写入和删除表。

## 概述

- **Data space** — 特殊的 `ducklake` 类型数据源，支持用户创建表和插入数据
- data-space 名称为 datasource 的 `name`（通过 `get-datasource-info` 获取）
- 适合 AI 生成爬虫/抓取脚本来存储结果
- 录入后的数据可通过标准查询流程（`execute-adhoc`）读取，命名约定见 [query-guide.md](./query-guide.md#ducklake-数据源类型-ducklake)

## 限制

- **仅 `ducklake`** 类型的 datasource 支持 data-spaces 操作
- 执行创建表或插入数据前，先通过 `get-datasource-info` 确认类型
- `create-table` 和 `insert-rows` 要求 API key 额外拥有 `data-spaces:write` 权限

## 操作

| 操作     | CLI 命令                    | API 端点                                |
| -------- | --------------------------- | --------------------------------------- |
| 创建表   | `create-table`              | `POST /data-spaces/{id}/create-table`   |
| 描述表   | `describe-data-space-table` | `POST /data-spaces/{id}/describe-table` |
| 插入数据 | `insert-rows`               | `POST /data-spaces/{id}/insert-rows`    |
| 删除表   | `drop-data-space-table`     | `POST /data-spaces/{id}/drop-table`     |

> 创建表和删除表后会自动触发 schema 扫描，无需手动操作。如需手动触发，使用 `scan-datasource`（详见 [cli.md](./cli.md#scan-datasource)）。

### 工作流

完整的 CLI 命令示例见 [references/cli.md](./cli.md#data-spaces-工作流创建和管理表)。

## 查询录入的数据

录入 data-space 的表后，通过 `execute-adhoc` 查询。表命名约定（`ducklake.{datasourceName}.{tableName}`）详见 [query-guide.md](./query-guide.md)。

## 获取表结构

使用 `describe-data-space-table` 即时获取 data-space 中已创建表的结构。

> `scan-datasource` 是查询功能中的异步 schema 扫描，主要用于非 ducklake 数据源。对于 data-spaces，始终使用 `describe-data-space-table`。

## 生成脚本

对于生成脚本，优先使用直接 API 调用而不是 CLI — 直接调用使用 `urllib.request`（仅标准库，无额外依赖），避免子进程开销，错误处理更细粒度。详见 [references/api.md](./api.md#data-spaces-api)。

## 参考

- CLI 命令详情：[references/cli.md](./cli.md)
- REST API 详情：[references/api.md](./api.md#data-spaces-api)
