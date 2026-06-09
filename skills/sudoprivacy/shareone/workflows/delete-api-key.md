# 删除 ShareOne API Key

当用户明确要求删除、清除、移除或重置 ShareOne API Key 时读取本文件。

## 1. 执行删除

执行：

```bash
node scripts/delete_api_key.js
```

## 2. 根据输出回复

- `SUDOWORK_KEY_DELETED`：告诉用户 Sudowork 中保存的 ShareOne API Key 已删除。
- `KEY_DELETED`：告诉用户本地保存的 ShareOne API Key 已删除。
- `KEY_NOT_FOUND`：告诉用户当前没有找到本地保存的 ShareOne API Key。

## 3. 删除后的规则

删除后，如果用户再次要求发布、查看评论、处理评论或执行任何 ShareOne API 操作，必须重新读取 `environment-and-credentials.md` 并完成凭据检查和配置。
