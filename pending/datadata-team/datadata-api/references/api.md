# Datadata API 参考

基础 URL：`https://www.datadata.com`（本地开发可通过 `DATADATA_BASE_URL` 覆盖）。

认证：使用 `X-Datadata-Api-key` 头传入 API Key。

---

## 直接 API 与 CLI

本 Skill 提供两种访问方式：

- **CLI** (`datadata_query.py`) — 适合交互式探索和一次性查询。大部分端点可通过 CLI 子命令调用。
- **直接 API 调用** — 适合生成脚本（爬虫、ETL、批处理任务）。使用 `urllib.request`（仅标准库，无额外依赖）直接调用 API，可避免子进程开销，并获得更细粒度的错误处理。

Python 请求模板：

```python
import json, urllib.request

API_KEY = "..."
BASE_URL = "https://www.datadata.com"

def _request(url, method="GET", payload=None):
    headers = {"X-Datadata-Api-key": API_KEY, "Accept": "application/json"}
    data = json.dumps(payload).encode() if payload else None
    if payload:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else None
```

---

## 端点总览

| 类型        | 方法 | 路径                                           | 权限                    | CLI 子命令                    |
| ----------- | ---- | ---------------------------------------------- | ----------------------- | ----------------------------- |
| Datasource  | GET  | `/api/v1/datasources/{id}/info`                | `datasources:read`      | `get-datasource-info`         |
| Datasource  | GET  | `/api/v1/datasources/{id}/list-tables`         | `datasources:read`      | `list-tables`                 |
| Datasource  | GET  | `/api/v1/datasources/{id}/describe-table`      | `datasources:read`      | `describe-table`              |
| Datasource  | POST | `/api/v1/datasources/{id}/scan`                | `datasource:scan`       | `scan-datasource`             |
| Datasource  | GET  | `/api/v1/datasources`                          | `datasources:read`      | `search-datasource` (private) |
| Search      | GET  | `/api/search-engine/indexes/datasource/search` | 无                      | `search-datasource` (public)  |
| Execution   | POST | `/api/v1/queries/execute-adhoc`                | `queries:execute-adhoc` | `execute-adhoc`               |
| Execution   | GET  | `/api/v1/executions/{id}/result`               | `executions:get`        | `get-execution-result`        |
| Data Spaces | POST | `/api/v1/data-spaces/{id}/create-table`        | `data-spaces:write`     | `create-table`                |
| Data Spaces | POST | `/api/v1/data-spaces/{id}/describe-table`      | `data-spaces:write`     | `describe-data-space-table`   |
| Data Spaces | POST | `/api/v1/data-spaces/{id}/drop-table`          | `data-spaces:write`     | `drop-data-space-table`       |
| Device Flow | POST | `/api/v1/api-keys/device-flow/code`            | 无                      | 自动（缺少 API Key 时触发）   |
| Device Flow | POST | `/api/v1/api-keys/device-flow/token`           | 无                      | 自动（后台轮询）              |
| Auth        | GET  | `/api/v1/auth/current`                         | 无（需有效 API Key）    | `whoami`                      |

---

## Datasource API

### 获取 datasource 信息

`GET /datasources/{datasourceId}/info`

返回 datasource 的元信息，如类型、引擎、展示名称等。请始终检查返回中的 `type` 字段 — 只有 `ducklake` 类型 datasource 支持 data-spaces 操作。

CLI：

```bash
python3 scripts/datadata_query.py get-datasource-info --datasource-id "CXNGJifvqE48kdzKVC9o5"
```

直接调用：

```python
data = _request(f"{BASE_URL}/api/v1/datasources/CXNGJifvqE48kdzKVC9o5/info")
print(data["type"])
```

### 列出表

`GET /datasources/{datasourceId}/list-tables?schemaName={schema}`

`schemaName` 为可选参数，省略时返回所有 schema。

CLI：

```bash
python3 scripts/datadata_query.py list-tables --datasource-id "CXNGJifvqE48kdzKVC9o5" --schema-name "main"
```

直接调用：

```python
data = _request(f"{BASE_URL}/api/v1/datasources/CXNGJifvqE48kdzKVC9o5/list-tables?schemaName=main")
```

### 描述表结构

`GET /datasources/{datasourceId}/describe-table?schemaName={schema}&tableName={table}`

> 这是 datasource 级别的 describe-table 端点。data-spaces 的 describe-table 在后文说明。

CLI：

```bash
python3 scripts/datadata_query.py describe-table \
  --datasource-id "CXNGJifvqE48kdzKVC9o5" \
  --schema-name "main" \
  --table-name "customers"
```

直接调用：

```python
data = _request(f"{BASE_URL}/api/v1/datasources/CXNGJifvqE48kdzKVC9o5/describe-table?schemaName=main&tableName=customers")
```

返回示例：

```json
{
  "columns": [
    {
      "column_name": "id",
      "data_type": "INTEGER",
      "is_nullable": "NO",
      "column_default": null
    }
  ]
}
```

### 扫描 datasource 模式

`POST /datasources/{datasourceId}/scan`

触发 datasource 的异步 schema 扫描。该命令会立即返回任务信息，实际扫描在后台执行。此端点主要用于非 ducklake datasource 的元数据发现。

对于 `ducklake` data-spaces，推荐使用 data-spaces 的 `describe-table` 端点获取实时表结构。

CLI：

```bash
python3 scripts/datadata_query.py scan-datasource --datasource-id "CXNGJifvqE48kdzKVC9o5"
```

直接调用：

```python
data = _request(f"{BASE_URL}/api/v1/datasources/CXNGJifvqE48kdzKVC9o5/scan", method="POST")
print(data["taskId"])
```

返回示例：

```json
{
  "taskId": "string",
  "taskType": "scan",
  "state": "active"
}
```

| 状态码 | 含义              |
| ------ | ----------------- |
| 200    | 已创建扫描任务    |
| 404    | datasource 未找到 |

### 搜索公开数据源（Meilisearch 引擎）

`GET /api/search-engine/indexes/datasource/search?q={query}&filter={filter}`

无需认证。支持通过名称、描述模糊搜索，可通过 `user.username` 过滤。

查询参数：

| 参数     | 必填 | 说明                                   |
| -------- | ---- | -------------------------------------- |
| `q`      | 是   | 搜索关键词                             |
| `filter` | 否   | 过滤条件，如 `user.username = hungtcs` |
| `limit`  | 否   | 返回结果数（默认 20）                  |
| `offset` | 否   | 分页偏移                               |

CLI：

```bash
# 公共搜索
python3 scripts/datadata_query.py search-datasource --query "customers" --scope public

# 按用户过滤
python3 scripts/datadata_query.py search-datasource --query "hungtcs/customers"
```

直接调用：

```python
import urllib.parse

query = urllib.parse.quote("customers")
filter_str = urllib.parse.quote("user.username = hungtcs")
url = f"{BASE_URL}/api/search-engine/indexes/datasource/search?q={query}&filter={filter_str}"
data = _request(url)  # 无需 API Key
for hit in data["hits"]:
    print(hit["id"], hit["name"], hit["user"]["username"])
```

### 搜索当前用户的数据源

`GET /api/v1/datasources?scope=owner&search={keyword}&sort=updated_at:desc&limit=10&offset=0`

需要认证（`X-Datadata-Api-key`）。返回当前用户名下的所有数据源（含公开和私有），支持模糊搜索。

查询参数：

| 参数     | 必填 | 说明                             |
| -------- | ---- | -------------------------------- |
| `scope`  | 是   | 固定为 `owner`                   |
| `search` | 否   | 模糊搜索关键词                   |
| `sort`   | 否   | 排序方式，默认 `updated_at:desc` |
| `limit`  | 否   | 返回结果数（默认 10）            |
| `offset` | 否   | 分页偏移                         |

CLI：

```bash
python3 scripts/datadata_query.py search-datasource --query "customers" --scope private
```

直接调用：

```python
url = f"{BASE_URL}/api/v1/datasources?scope=owner&search=customers&sort=updated_at:desc&limit=10&offset=0"
data = _request(url, API_KEY)
for item in data["data"]:
    print(item["id"], item["name"], item["visibility"])
```

---

## 执行 API

### 创建执行（execute adhoc query）

`POST /queries/execute-adhoc`

请求体：

| 字段          | 类型   | 必填 | 默认值   | 说明                                              |
| ------------- | ------ | ---- | -------- | ------------------------------------------------- |
| `script`      | string | 是   | —        | SQL 或脚本内容                                    |
| `scriptType`  | string | 否   | `sql`    | 脚本类型                                          |
| `queryEngine` | string | 否   | `duckdb` | `duckdb` 或 `clickhouse`                          |
| `datasources` | array  | 否   | `[]`     | `[{datasourceId, attachAlias}]`，用于跨数据源关联 |

CLI：

```bash
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "CXNGJifvqE48kdzKVC9o5:orders" \
  --script "SELECT * FROM orders.public.customers LIMIT 10"
```

直接调用：

```python
payload = {
    "script": "SELECT * FROM orders.public.customers LIMIT 10",
    "scriptType": "sql",
    "queryEngine": "duckdb",
    "datasources": [{"datasourceId": "CXNGJifvqE48kdzKVC9o5", "attachAlias": "orders"}],
}
response = _request(f"{BASE_URL}/api/v1/queries/execute-adhoc", method="POST", payload=payload)
execution_id = response.get("id") or response.get("executionId")
```

返回结果中包含 execution `id`，查询会异步执行。可以使用递归查找方式从嵌套响应中提取 `executionId`。

### 获取执行结果

`GET /executions/{executionId}/result?format={fmt}&timeout={sec}`

| 查询参数  | 必填 | 默认值   | 说明                       |
| --------- | ---- | -------- | -------------------------- |
| `format`  | 否   | `ndjson` | 支持 `ndjson` 或 `csv`     |
| `timeout` | 否   | —        | 后端等待执行完成的最大秒数 |

CLI：

```bash
python3 scripts/datadata_query.py get-execution-result \
  --execution-id "CaU6DR..." \
  --format ndjson \
  --timeout 30
```

直接调用：

```python
url = f"{BASE_URL}/api/v1/executions/CaU6DR.../result?format=ndjson&timeout=30"
req = urllib.request.Request(url, headers={"X-Datadata-Api-key": API_KEY})
with urllib.request.urlopen(req) as resp:
    raw = resp.read().decode()
    rows = [json.loads(line) for line in raw.strip().splitlines() if line.strip()]
    print(f"Got {len(rows)} rows")
```

CSV 格式返回纯文本：

```python
url = f"{BASE_URL}/api/v1/executions/CaU6DR.../result?format=csv"
```

如果查询在 `timeout` 内未完成，API 会返回超时错误。请延长 `timeout` 或保存 `executionId` 后续查询。

---

## Data Spaces API

> **注意：** 只有 `ducklake` 类型的 datasource 支持 data-spaces 操作。请先通过 `get-datasource-info` 确认类型。

### 创建表

`POST /data-spaces/{datasourceId}/create-table`

请求体：

| 字段        | 类型   | 必填 | 说明                                           |
| ----------- | ------ | ---- | ---------------------------------------------- |
| `tableName` | string | 是   | 表名                                           |
| `columns`   | array  | 是   | `[{"columnName": "...", "columnType": "..."}]` |

有效的 `columnType` 包括 `INTEGER`、`VARCHAR`、`DOUBLE`、`BOOLEAN`、`TIMESTAMP`、`BIGINT`、`FLOAT` 等。

CLI：

```bash
python3 scripts/datadata_query.py create-table \
  --datasource-id "123" \
  --table-name "products" \
  --columns '[{"columnName": "id", "columnType": "INTEGER"}, {"columnName": "name", "columnType": "VARCHAR"}]'
```

直接调用：

```python
payload = {
    "tableName": "products",
    "columns": [
        {"columnName": "id", "columnType": "INTEGER"},
        {"columnName": "name", "columnType": "VARCHAR"},
    ],
}
_request(f"{BASE_URL}/api/v1/data-spaces/123/create-table", method="POST", payload=payload)
```

| 状态码 | 含义              |
| ------ | ----------------- |
| 204    | 已创建            |
| 404    | data space 未找到 |
| 409    | 表已存在          |

### data-spaces 描述表

`POST /data-spaces/{datasourceId}/describe-table`

请求体：

| 字段        | 类型   | 必填 | 说明 |
| ----------- | ------ | ---- | ---- |
| `tableName` | string | 是   | 表名 |

CLI：

```bash
python3 scripts/datadata_query.py describe-data-space-table \
  --datasource-id "123" \
  --table-name "products"
```

直接调用：

```python
payload = {"tableName": "products"}
data = _request(f"{BASE_URL}/api/v1/data-spaces/123/describe-table", method="POST", payload=payload)
for col in data["columns"]:
    print(col["column_name"], col["data_type"])
```

### 删除表

`POST /data-spaces/{datasourceId}/drop-table`

请求体：

| 字段        | 类型   | 必填 | 说明 |
| ----------- | ------ | ---- | ---- |
| `tableName` | string | 是   | 表名 |

CLI：

```bash
python3 scripts/datadata_query.py drop-data-space-table \
  --datasource-id "123" \
  --table-name "products"
```

直接调用：

```python
payload = {"tableName": "products"}
_request(f"{BASE_URL}/api/v1/data-spaces/123/drop-table", method="POST", payload=payload)
```

| 状态码 | 含义              |
| ------ | ----------------- |
| 200    | 已删除            |
| 404    | data space 未找到 |

### 插入行

`POST /data-spaces/{datasourceId}/insert-rows`

请求体：

| 字段        | 类型          | 必填 | 说明                              |
| ----------- | ------------- | ---- | --------------------------------- |
| `tableName` | string        | 是   | 表名                              |
| `columns`   | array[string] | 是   | 与目标表列名一致的列名列表        |
| `rows`      | array[array]  | 是   | 每一行数据，按 `columns` 顺序排列 |

插入操作为事务性：全部成功或全部回滚。`map[string]any` 值会自动序列化为 JSON 字符串。

CLI：

```bash
python3 scripts/datadata_query.py insert-rows \
  --datasource-id "123" \
  --table-name "products" \
  --columns '["id", "name", "price"]' \
  --rows '[[1, "Widget", 9.99], [2, "Gadget", 24.99]]'
```

直接调用：

```python
payload = {
    "tableName": "products",
    "columns": ["id", "name", "price"],
    "rows": [
        [1, "Widget", 9.99],
        [2, "Gadget", 24.99],
    ],
}
_request(f"{BASE_URL}/api/v1/data-spaces/123/insert-rows", method="POST", payload=payload)
```

| 状态码 | 含义              |
| ------ | ----------------- |
| 200    | 已插入            |
| 400    | 表未找到          |
| 404    | data space 未找到 |

---

## Device Flow API（设备授权）

类似 OAuth 2.0 Device Authorization Grant（RFC 8628），用于 CLI/Agent 等输入受限设备自动签发 API Key。

### 端点总览

| 方法   | 路径                              | 认证     | 说明                                        |
| ------ | --------------------------------- | -------- | ------------------------------------------- |
| `POST` | `/api-keys/device-flow/code`      | 无       | 发起授权流程，获取 user code 和 device code |
| `GET`  | `/api-keys/device-flow/authorize` | 需要登录 | 查询授权详情（前端展示用）                  |
| `POST` | `/api-keys/device-flow/authorize` | 需要登录 | 用户确认授权                                |
| `POST` | `/api-keys/device-flow/token`     | 无       | 设备端轮询换取 API Key                      |

### 发起授权

`POST /api-keys/device-flow/code`

请求体：

| 字段          | 类型     | 必填 | 说明                                 |
| ------------- | -------- | ---- | ------------------------------------ |
| `name`        | string   | 是   | API Key 名称                         |
| `permissions` | string[] | 是   | 权限列表，至少 1 个                  |
| `description` | string?  | 否   | API Key 描述                         |
| `expiresAt`   | string?  | 否   | 过期时间（ISO 8601），为空表示不过期 |

直接调用：

```python
payload = {
    "name": "my-agent-skill",
    "permissions": ["datasources:read", "queries:execute-adhoc", "executions:get"],
    "description": "Auto-generated API key for Datadata CLI",
}
data = _request(f"{BASE_URL}/api/v1/api-keys/device-flow/code", method="POST", payload=payload)
print(f"请在浏览器中打开: {data['verificationUriComplete']}")
# 保存 deviceCode 用于后续轮询
device_code = data["deviceCode"]
```

### 轮询换取 API Key

`POST /api-keys/device-flow/token`

请求体：

| 字段         | 类型   | 必填 | 说明                     |
| ------------ | ------ | ---- | ------------------------ |
| `deviceCode` | string | 是   | 上一步返回的 device code |

直接调用（轮询直到成功或过期）：

```python
import time

deadline = time.time() + data["expiresIn"]
interval = data["interval"]

while time.time() < deadline:
    try:
        result = _request(f"{BASE_URL}/api/v1/api-keys/device-flow/token", method="POST",
                          payload={"deviceCode": device_code})
        api_key = result["key"]
        print(f"获取到 API Key: {api_key}")
        break
    except urllib.error.HTTPError as exc:
        body = json.loads(exc.read())
        if body.get("code") == "authorization_pending":
            time.sleep(interval)  # 用户尚未授权，继续等待
            continue
        raise
```

| 状态码 | code                    | 说明                     |
| ------ | ----------------------- | ------------------------ |
| 200    | —                       | 授权成功，返回 API Key   |
| 400    | `authorization_pending` | 用户尚未确认，应继续轮询 |
| 400    | `invalid_device_code`   | deviceCode 过期或不存在  |

> **注意：** `/token` 为一次性消费接口 — 调用成功后缓存即被删除，API Key 仅返回一次。

---

## 当前用户信息

`GET /auth/current`

返回当前认证用户的资料及 API Key 的元数据、权限列表。可用于验证 API Key 有效性、检查权限、获取用户信息。

CLI：

```bash
python3 scripts/datadata_query.py whoami
```

直接调用：

```python
data = _request(f"{BASE_URL}/api/v1/auth/current")
print(f"User: {data['user']['displayName']}")
print(f"Permissions: {data['permissions']}")
```

返回结构：

| 字段          | 类型     | 说明                                                      |
| ------------- | -------- | --------------------------------------------------------- |
| `user`        | object   | 用户资料（id、username、displayName 等）                  |
| `apiKey`      | object   | API Key 元数据（id、name、keyPrefix、权限）               |
| `permissions` | string[] | 当前会话的有效权限列表（衍生并精简自 apiKey.permissions） |

---

## 常见错误

| 状态码 | 含义                                                                                                               |
| ------ | ------------------------------------------------------------------------------------------------------------------ |
| 401    | 未认证 — API key 缺失或无效                                                                                        |
| 403    | 禁止访问 — API key 缺少所需权限                                                                                    |
| 404    | 资源不存在（如 datasource ID 无效、execution ID 不存在）或端点路径错误。若多个端点均 404，检查 `DATADATA_BASE_URL` |
| 5xx    | 服务器错误 — 等待 3 秒后重试一次；若仍失败，请报告 `executionId`（如适用）                                         |
