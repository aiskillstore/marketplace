# fetch 函数

> ⚠️ **重要**：`fetch()` 会根据响应头 `Content-Type` **自动解析**响应体。`resp.body` 已经是 Python 对象（dict/list），**不要**再对 `resp.body` 做字符串解析（如 `.split()`、`.strip()` 等）。
>
> 完整 API 签名请参考 [**builtins**.pyi](./__builtins__.pyi)。

执行 HTTP 请求。

```python
response = fetch(
    url,
    method="GET",
    headers=None,
    body=None,
    timeout=30
)
```

**参数：**

- `url` (str): 请求 URL
- `method` (str): HTTP 方法，默认 `"GET"`，支持 `GET`、`POST`、`PUT`、`DELETE`、`HEAD`
- `headers` (dict): HTTP 请求头，默认 None
- `body` (str/dict): 请求体，默认 None。JSON 对象需要先用 `json.dumps()` 序列化，表单数据直接传字符串
- `timeout` (int): 超时秒数，默认 30

**返回值：** Response 对象，包含以下属性：

- `ok` (bool): 是否成功 (status code 200-299)
- `status` (int): HTTP 状态码
- `status_text` (str): 状态文本
- `headers` (dict): 响应头
- `body` (str/dict/list): 响应体，根据响应的 Content-Type 自动解析
- `proto` (str): HTTP 版本，如 "HTTP/1.1"
- `proto_major` (int): HTTP 主版本号
- `proto_minor` (int): HTTP 次版本号
- `uncompressed` (bool): 是否自动解压

**`response.body` 类型规则：**

| Content-Type                  | `body` 类型 | 说明                          |
| ----------------------------- | ----------- | ----------------------------- |
| `application/json`            | dict / list | 自动解析 JSON 为 dict 或 list |
| `text/csv`                    | list        | 自动解析 CSV 为 list of list  |
| 其他 (包括 XML、纯文本、HTML) | str         | 原始响应体字符串              |
| 空响应体                      | None        | 响应体为空时返回 `None`       |

> **注意**：`body` 的解析完全由响应头 `Content-Type` 决定。即使返回了 JSON 格式的数据，如果 Content-Type 不是 `application/json`，也会以字符串形式返回。

**示例：**

### 协议：先验证，再处理

使用 `fetch()` 时遵循两段式流程：

**第 1 步 — 返回类型和数据：**

```python
resp = fetch("https://api.example.com/data")
return {"type": type(resp.body), "data": resp.body}
```

> `type(resp.body)` 返回类型名称字符串（如 `"dict"`、`"list"`、`"str"`），结合数据一起输出可以一目了然地确认结构。仅返回 `resp.body` 有时无法区分 dict 和 list。

**第 2 步 — 用户确认结构后，再写完整逻辑。**

以下是用户确认后的常见完整示例：

---

### 获取 JSON 数组 → 转为 DataFrame

```python
resp = fetch("https://api.example.com/users")
# resp.body 是 list of dict，直接转为 DataFrame
df = DataFrame(resp.body)
return df
```

### 获取嵌套 JSON 字典 → 提取数据字段

```python
resp = fetch("https://api.example.com/products?page=1")
# resp.body 是 {"data": [...], "total": 100, "page": 1}
products = resp.body["data"]
df = DataFrame(products)
return df
```

### 带认证头的请求

```python
resp = fetch(
    "https://api.example.com/orders",
    headers={
        "Authorization": "Bearer sk-xxx",
        "Accept": "application/json"
    }
)
return resp.body
```

### POST JSON 数据

```python
body = json.dumps({"name": "test", "price": 99.9})
resp = fetch(
    "https://api.example.com/products",
    method="POST",
    headers={"Content-Type": "application/json"},
    body=body
)
return resp.body
```

### POST 表单数据

```python
resp = fetch(
    "https://api.example.com/login",
    method="POST",
    body="username=admin&password=123456",
    headers={
      "Content-Type": "application/x-www-form-urlencoded"
    }
)
return resp.body
```

### 错误处理

```python
resp = fetch("https://api.example.com/data")
if not resp.ok:
    throw("请求失败: " + str(resp.status))
# 状态码正常，继续处理
return resp.body
```

### 获取 CSV 数据

```python
resp = fetch("https://api.example.com/export.csv")
# Content-Type: text/csv → body 为 list of list
header = resp.body[0]       # 第一行是表头
rows = resp.body[1:]        # 后续是数据行
return {"header": header, "rows": rows}
```

### 结合 query() 和 fetch()

```python
# 从数据库查数据，发送到外部 API
users = query("SELECT id, email FROM users WHERE active = true")
body = json.dumps({"users": users.to_dicts()})
resp = fetch(
    "https://api.example.com/sync",
    method="POST",
    headers={"Content-Type": "application/json"},
    body=body
)
return resp.body
```
