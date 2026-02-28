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
```

## 子内容规则（子任务 / 子项 / 子 Grid）
1. `子任务`（Checklist/Todo 列）：适用于**简单描述**的子内容，不需要额外字段。
2. `子项`（Relation 列）：当子内容与父级**字段结构一致**时，通过关联行管理。
3. `子 Grid`：当子内容需要**独立字段结构**时，新建 Grid 并在父级引用或说明。

## Grid 默认空行处理
新建 Grid 时可能自动生成 3 条空行。脚本在写入数据前会清理默认空行，避免空行混入真实计划。

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

## 资源
1. `skills/appflowy-api/scripts/`：Python/Node 脚本与通用库。
2. `skills/appflowy-api/references/`：API 参考与模板文件。
3. `skills/appflowy-api/references/templates/`：UTF-8 模板，避免乱码与字段顺序问题。
4. `skills/appflowy-api/examples/`：示例命令与用法。
