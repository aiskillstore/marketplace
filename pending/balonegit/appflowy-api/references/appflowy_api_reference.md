# AppFlowy API 参考（自托管）

## 认证与请求头
- 获取 token（password grant）  
  `POST /gotrue/token?grant_type=password`  
  Body: `{"email":"...","password":"..."}`
- AppFlowy API 必需请求头  
  `Authorization: Bearer <access_token>`  
  `client-version: <部署版本>`  
  `client-timestamp: <Unix 毫秒>`  
  `device-id: <UUID>`

## 常用端点
### Workspace
- `GET /api/workspace`

### 文档 / 视图
- `POST /api/workspace/{workspace_id}/page-view`
- `POST /api/workspace/{workspace_id}/page-view/{view_id}/append-block`
- `POST /api/workspace/{workspace_id}/page-view/{view_id}/database-view`

### 数据库
- `GET /api/workspace/{workspace_id}/database`
- `POST /api/workspace/{workspace_id}/database/{database_id}/fields`
- `POST /api/workspace/{workspace_id}/database/{database_id}/row`
- `PUT /api/workspace/{workspace_id}/database/{database_id}/row`
- `GET /api/workspace/{workspace_id}/database/{database_id}/row/detail?ids=...`

### 搜索
- `GET /api/search/{workspace_id}?query=...`

### 协作（Collab）
- `GET /api/workspace/v1/{workspace_id}/collab/{object_id}?collab_type=0`
- `GET /api/workspace/v1/{workspace_id}/collab/{object_id}/json?collab_type=0`
- `POST /api/workspace/v1/{workspace_id}/collab/{object_id}/web-update`

## 请求示例
### 创建页面
```json
{
  "name": "示例文档",
  "view_type": 0,
  "parent_view_id": "<parent_view_id>",
  "parent_view_type": 0
}
```

### 追加块（Quill Delta）
```json
{
  "type": "paragraph",
  "data": {
    "delta": [
      { "insert": "Hello AppFlowy\n" }
    ]
  }
}
```

### 添加字段
```json
{
  "name": "标题",
  "field_type": 0
}
```

### 写入/更新行（cells）
```json
{
  "pre_hash": "example:row-key",
  "cells": {
    "Name": "示例",
    "状态": { "name": "未开始" }
  }
}
```

## 错误处理
- HTTP 200 但响应体包含 `success=false` 或 `error` 视为业务失败。
- 控制台提示无法连接时，优先检查宿主机 `80/443` 端口与防火墙规则。
- 容器间调用优先使用内部地址（如 `http://gotrue:9999`、`http://appflowy_cloud:8000`）。

## 说明
- 模板文件与脚本输出请使用 UTF-8，避免中文乱码。
- Grid 默认可能生成 3 条空行，建议在写入真实数据前清理。
