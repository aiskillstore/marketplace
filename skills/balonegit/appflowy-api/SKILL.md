---
name: appflowy-api
description: "AppFlowy Cloud/GoTrue API 的认证与调用流程（获取 token、workspace/文档/数据库/搜索等）。在本仓库用 Python 编写或调试 AppFlowy API 客户端、脚本、自动化或排查接口问题时使用。"
---

# AppFlowy API

## 概述
本 skill 用于自托管 AppFlowy 环境的 API 调用与自动化，覆盖登录鉴权、文档/视图/数据库操作、搜索、协作数据（collab）等常见场景。默认**不读取 `.env`**，仅在显式传入 `--env <path>` 时读取。

本 skill 当前适配 AppFlowy Cloud `0.12.3`。`doctor.py` 会通过 `/api/health` 检测版本并在不匹配时给出警告。

## 快速开始
1. 准备 base URL 与 GoTrue URL（可选 `--env <path>` 读取 `.env`）。
2. 使用账号密码获取 `access_token`。
3. 携带必要请求头调用 AppFlowy API。

```bash
# 获取 token
curl -sS -X POST "http://10.60.0.189/gotrue/token?grant_type=password" \
  -H "Content-Type: application/json" \
  -d '{"email":"<email>","password":"<password>"}'
```

```bash
# 调用 API（示例：搜索）
curl -sS "http://10.60.0.189/api/search/<workspace_id>?query=test" \
  -H "Authorization: Bearer <access_token>" \
  -H "client-version: 0.12.3" \
  -H "client-timestamp: 1700000000000" \
  -H "device-id: <uuid>"
```

## 统一入口（推荐）
统一入口脚本用于封装命令风格，适合自动化与外部集成：

```bash
python skills/appflowy-api/scripts/appflowy_skill.py list
python skills/appflowy-api/scripts/appflowy_skill.py help apply-grid
python skills/appflowy-api/scripts/appflowy_skill.py help database-query
python skills/appflowy-api/scripts/appflowy_skill.py help page-get-tree
python skills/appflowy-api/scripts/appflowy_skill.py help page-get-blocks
python skills/appflowy-api/scripts/appflowy_skill.py help page-delete-blocks
python skills/appflowy-api/scripts/appflowy_skill.py help rename-db-field
python skills/appflowy-api/scripts/appflowy_skill.py help delete-db-field
python skills/appflowy-api/scripts/appflowy_skill.py help bulk-upsert-rows
python skills/appflowy-api/scripts/appflowy_skill.py help schema-diff
python skills/appflowy-api/scripts/appflowy_skill.py help schema-migration-plan
python skills/appflowy-api/scripts/appflowy_skill.py help apply-schema-migration
python skills/appflowy-api/scripts/appflowy_skill.py help render-template
python skills/appflowy-api/scripts/appflowy_skill.py help repair-runner
python skills/appflowy-api/scripts/appflowy_skill.py help snapshot-collab
python skills/appflowy-api/scripts/appflowy_skill.py help rollback-collab
```

## 配置优先级
解析优先级（从高到低）：
1. 命令行参数：`--base-url`、`--gotrue-url`、`--client-version`、`--device-id`
2. 配置文件：`--config <path>`（JSON，示例见 `skills/appflowy-api/references/config.example.json`）
3. 环境变量：`APPFLOWY_BASE_URL`、`API_EXTERNAL_URL`、`APPFLOWY_GOTRUE_BASE_URL`
4. `.env` 文件：仅在传入 `--env <path>` 时读取

## 常用脚本
```bash
# 获取 token
python skills/appflowy-api/scripts/get_token.py --email <email> --password <password>
```

```bash
# 自检（不会自动读取 .env）
python skills/appflowy-api/scripts/doctor.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password>
```

```bash
# 生成“用户管理系统”文档（UTF-8 模板，表格顺序为正序）
python skills/appflowy-api/scripts/create_user_management_doc.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password>
```

```bash
# 就地修正文档（通用模板脚本）
python skills/appflowy-api/scripts/update_user_management_doc.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id>
```

```bash
# 通用模板：按模板更新 Grid（默认就地修改）
python skills/appflowy-api/scripts/apply_grid_template.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --template-file <template.json>
python skills/appflowy-api/scripts/apply_grid_template.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --template-file skills/appflowy-api/references/templates/grid_plan.with_vars.example.json --vars-file skills/appflowy-api/references/templates/grid_plan.vars.example.json
```

```bash
# 删除行（通过 collab 从 row_orders 移除，支持多个 row_id）
python skills/appflowy-api/scripts/delete_rows.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --row-ids <row_id_1,row_id_2>
```

```bash
# 查询数据库（支持 filter/sort/limit/offset；推荐 query-file）
python skills/appflowy-api/scripts/database_query.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --query-file <query.json>
```

```json
{
  "filter": [
    { "field": "Status", "op": "eq", "value": "To Do" }
  ],
  "sort": [
    { "field": "Last modified", "direction": "desc" }
  ],
  "limit": 20,
  "offset": 0
}
```

```bash
# 读取页面树（支持 root_view_id 与 depth）
python skills/appflowy-api/scripts/page_tree.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --depth 3 --compact
```

```bash
# 读取页面 block 树（默认树形；--flat 扁平输出；--raw 原始 collab）
python skills/appflowy-api/scripts/page_blocks.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --flat
```

```bash
# 删除页面 block（先 dry-run，确认后执行）
python skills/appflowy-api/scripts/delete_page_blocks.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --block-id <block_id> --dry-run
python skills/appflowy-api/scripts/delete_page_blocks.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --view-id <view_id> --block-id <block_id>
```

```bash
# 字段改名（支持按 field_id / field_name）
python skills/appflowy-api/scripts/rename_db_field.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id> --new-name <new_name> --dry-run
python skills/appflowy-api/scripts/rename_db_field.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id> --new-name <new_name>
```

```bash
# 字段删除（默认 dry-run；执行必须 --execute --yes；禁止删除主字段）
python skills/appflowy-api/scripts/delete_db_field.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id>
python skills/appflowy-api/scripts/delete_db_field.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --field-id <field_id> --execute --yes
```

```bash
# 批量 upsert 行（支持 dry-run，输出新增/更新/失败摘要）
python skills/appflowy-api/scripts/bulk_upsert_rows.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --rows-file <rows.json> --pre-hash-prefix <prefix> --dry-run
python skills/appflowy-api/scripts/bulk_upsert_rows.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --rows-file <rows.json> --pre-hash-prefix <prefix>
```

```bash
# v0.3 M1：schema diff（当前库 vs 目标模板/目标库）
python skills/appflowy-api/scripts/schema_diff.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/schema_diff.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-database-id <target_database_id>
```

```bash
# v0.3 M1：migration plan（仅生成计划，不执行）
python skills/appflowy-api/scripts/schema_migration_plan.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/schema_migration_plan.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-database-id <target_database_id> --rename-apply-threshold 0.80
```

```bash
# v0.3 M2：apply schema migration（默认 dry-run）
python skills/appflowy-api/scripts/apply_schema_migration.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --target-template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/apply_schema_migration.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --plan-file <migration_plan.json>
```

```bash
# v0.3 M2：执行 migration（高风险需显式放行）
python skills/appflowy-api/scripts/apply_schema_migration.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --plan-file <migration_plan.json> --execute --yes --allow-high-risk --allow-delete-fields
```

```bash
# v0.3 M3：模板渲染（变量注入）
python skills/appflowy-api/scripts/render_template.py --template-file skills/appflowy-api/references/templates/grid_plan.with_vars.example.json --vars-file skills/appflowy-api/references/templates/grid_plan.vars.example.json --output-file .tmp/grid_plan.rendered.json
```

```bash
# v0.3 M3：修复器框架（默认 dry-run）
python skills/appflowy-api/scripts/repair_runner.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --template-file skills/appflowy-api/references/templates/fitness_plan.example.json
python skills/appflowy-api/scripts/repair_runner.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id> --template-file .tmp/grid_plan.rendered.json --repair ensure-template-fields --repair repair-select-options --execute --yes
```

```bash
# v0.3 M4：collab 快照与回滚
python skills/appflowy-api/scripts/snapshot_collab.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --workspace-id <workspace_id> --database-id <database_id>
python skills/appflowy-api/scripts/rollback_collab.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --snapshot-file <snapshot.json>
python skills/appflowy-api/scripts/rollback_collab.py --config skills/appflowy-api/references/config.example.json --email <email> --password <password> --snapshot-file <snapshot.json> --execute --yes
```

```json
{
  "rows": [
    {
      "key": "task_1",
      "cells": { "Description": "example", "Status": "To Do" }
    },
    {
      "pre_hash": "biz:task_2",
      "cells": { "Description": "example2", "Status": "Doing" }
    }
  ]
}
```

## 子内容规则（子任务 / 子项 / 子 Grid）
1. `子任务`（Checklist/Todo 列）：适用于**简单描述**的子内容，不需要额外字段。
2. `子项`（Relation 列）：当子内容与父级**字段结构一致**时，通过关联行管理。
3. `子 Grid`：当子内容需要**独立字段结构**时，新建 Grid 并在父级引用或说明。

## Grid 默认空行处理
新建 Grid 时可能自动生成 3 条空行。脚本在写入数据前会清理默认空行，避免空行混入真实计划。

## Select 写入规则（重要）
1. `SingleSelect`/`MultiSelect` 行值写入时应使用**选项名称**（例如：`"状态": "进行中"`、`"标签": ["核心", "风险"]`）。
2. 不要把 `selected_option_ids` 直接作为 `SingleSelect`/`MultiSelect` 行值提交给 REST row API，否则容易触发 `HTTP 400`。
3. `selected_option_ids` 仅适用于 `Checklist`（子任务）字段结构。

## 必需请求头
所有 AppFlowy API 请求均需携带：
1. `Authorization: Bearer <access_token>`
2. `client-version: <AppFlowy 版本>`（建议与部署版本一致）
3. `client-timestamp: <Unix 毫秒>`
4. `device-id: <UUID>`

## 错误处理与排障
1. HTTP 200 但响应体包含 `success=false` 或 `error` 视为业务失败。
2. 控制台提示无法连接时，优先检查宿主机 `80/443` 可达性与防火墙规则。
3. 容器间调用优先使用内部地址（如 `http://gotrue:9999`、`http://appflowy_cloud:8000`）。
4. 删除行时，`/database/{database_id}/row` 没有 `DELETE` 路由；应使用 `delete_rows.py` 通过 collab 更新 `row_orders` 完成删除。
5. `database-query` 的 `--query-file` 支持 UTF-8/UTF-8 BOM（Windows PowerShell 导出的 UTF-8 也可读取）。
6. 字段改名/字段删除当前通过 collab 更新实现；其中字段删除默认 dry-run，执行必须显式传入 `--execute --yes`。
7. M3 统一输出协议：高风险/批量命令返回 `change_report`（`before/plan/after/summary` 四段）。
8. v0.3 M1 新增 `schema-diff` 与 `schema-migration-plan`，两者均输出 `change_report`。
9. `schema-diff` 中的 `rename_candidates` 是“建议项”，后续执行仍应优先以 `field_id` 二次确认。
10. v0.3 M2 新增 `apply-schema-migration`，默认 dry-run；执行需要 `--execute --yes`，并对高风险操作要求额外确认参数。
11. `apply-schema-migration` 在执行前后自动输出 before/after diff 摘要；若 plan 文件缺少 target schema，会提示 after diff 不可用。
12. `apply-schema-migration` 的 `--plan-file` 支持 UTF-8 / UTF-8 BOM / UTF-16 编码，兼容 PowerShell 重定向文件。
13. v0.3 M3 新增 `render-template`，支持 `--vars/--vars-file`、默认值与必填校验。
14. v0.3 M3 新增 `repair-runner`，将空行清理 / 字段结构补齐 / select 选项修复抽象为可组合规则。
15. `render-template` 与 `repair-runner` 执行后会生成 `audit_log`，默认输出到 `.tmp/audit_logs/`。
16. v0.3 M4 新增 `snapshot-collab` 与 `rollback-collab`，支持 database/doc 对象快照与回滚。
17. `rollback-collab` 默认 `auto` 策略：database 走 `schema-database`，其余对象走 `state-update`。

## 资源
1. `skills/appflowy-api/scripts/`：Python/Node 脚本与通用库。
2. `skills/appflowy-api/references/`：API 参考与模板文件。
3. `skills/appflowy-api/references/templates/`：UTF-8 模板，避免乱码与字段顺序问题。
4. `skills/appflowy-api/references/v0.2_m1_regression.md`：v0.2 M1 真实联调记录。
5. `skills/appflowy-api/references/v0.2_m2_regression.md`：v0.2 M2 真实联调记录。
6. `skills/appflowy-api/references/v0.2_m3_regression.md`：v0.2 M3 真实联调记录。
7. `skills/appflowy-api/references/v0.2_regression_suite.md`：v0.2 回归脚本清单。
8. `skills/appflowy-api/references/v0.2_m4_regression.md`：v0.2 M4 真实回归记录。
9. `skills/appflowy-api/references/v0.3_m1_regression.md`：v0.3 M1 真实联调记录。
10. `skills/appflowy-api/references/v0.3_m2_regression.md`：v0.3 M2 真实联调记录。
11. `skills/appflowy-api/references/v0.3_m3_regression.md`：v0.3 M3 真实联调记录。
12. `skills/appflowy-api/references/v0.3_m4_regression.md`：v0.3 M4 真实联调记录。
13. `skills/appflowy-api/references/snapshot_rollback_protocol.md`：快照回滚协议。
14. `skills/appflowy-api/references/v0.3_release_notes.md`：v0.3.0 发布说明。
15. `skills/appflowy-api/examples/`：示例命令与用法。
