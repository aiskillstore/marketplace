---
tags: [api, {{module}}, {{method}}]
endpoint: {{path}}
method: {{http_method}}
auth: {{auth_required}}
---

# {{api_name}}

> {{description}}

## 基本信息

| 属性 | 值 |
|------|-----|
| 端点 | `{{path}}` |
| 方法 | `{{http_method}}` |
| 认证 | {{auth_required}} |
| 文件 | `{{source_file}}` |

## 请求

```http
{{http_method}} {{full_path}}
{{headers}}
```

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
{{path_params}}

### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
{{query_params}}

### 请求体

```json
{{request_body}}
```

## 响应

### 成功响应 ({{success_code}})

```json
{{success_response}}
```

### 错误响应

| 状态码 | 说明 |
|--------|------|
{{error_codes}}

## 示例

### cURL

```bash
{{curl_example}}
```

### JavaScript

```javascript
{{js_example}}
```

## 相关

- [[{{related_api_1}}]]
- [[{{related_api_2}}]]
- [[{{related_module}}]]

---
*返回 [[_API索引|API 索引]]*
