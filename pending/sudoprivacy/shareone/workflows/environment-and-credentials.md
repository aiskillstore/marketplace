# 环境判断与 API Key 凭据流程

只在需要 ShareOne API 的操作前读取本文件。凭据状态机（检查 → 保存 → 复查 → 核对）全部由 `ensure_credentials.js` 脚本执行；你只需要按输出 token 行动，并把脚本在分隔线 `--- 请将以下内容原样发给用户 ---` 之后输出的话术**原样转发给用户**。不要凭 `SUDOWORK_AUTH_PROXY_URL` 等环境变量自行推断环境。

## 1. 检查凭据

```bash
node scripts/ensure_credentials.js
```

按输出处理：

- `READY`：凭据就绪，直接继续原操作。同时输出的 `MODE:` 行说明当前环境（见第 3 节后续命令规则）。
- `NEED_USER_INPUT`：凭据缺失。把分隔线之后的提问话术原样转发给用户，**暂停当前操作**，等待用户回复。
- `ERROR:...`：见第 4 节。

## 2. 用户回复后

- 用户提供了 API Key（例如 `sk-xxx`）：

```bash
node scripts/ensure_credentials.js --key <用户提供的KEY>
```

- 用户回复“没有”或“创建”：

```bash
node scripts/ensure_credentials.js --create-guest
```

两个命令都会自动完成保存、复查和核对，按输出处理：

- `READY`：继续原操作。
- `GUEST_KEY_CREATED:<api_key>`：**阻塞性用户通知**。分隔线之后是需要原样转发给用户的完整通知文本（含临时 API Key、绑定账号链接和保存提醒）。必须先把该通知发给用户，才能继续原任务的任何上传、下载、评论处理命令；即使 key 已自动保存也不能省略。
- `NOTE:SUDOWORK_FALLBACK_KEY_SAVED`：附加信息，表示 key 保存到了 skill 安装目录下的本地 fallback 凭证（`.shareone_credentials`），不是 Sudowork Secret Store。脚本输出的说明文字一并转发给用户即可。

## 3. 后续命令规则

- `MODE:sudowork`：后续所有命令**不要传 `--api-key`**，凭证由 Auth Proxy 自动注入。
- `MODE:sudowork_fallback` / `MODE:direct`：脚本会自动读取环境变量 `SHAREONE_API_KEY` 或本地凭证文件，**无需显式传 `--api-key`**；仅当用户临时指定其他 key 时才传。
- 所有非 Sudowork secrets 的本地凭据都只读写 ShareOne skill 安装目录下的 `.shareone_credentials`，不读写用户 home。
- 如果后续操作中服务返回 401（脚本输出 `ERROR:AUTH_FAILED`），提示用户“API Key 无效或权限不足”。

## 4. 错误处理

- `ERROR:RATE_LIMIT_EXCEEDED`：创建临时 API Key 触发频率限制（每小时 20 次、每天 200 次）。把分隔线之后的提示转发给用户，暂停操作。
- `ERROR:SUDOWORK_WRITE_BROKEN`：Sudowork 凭证环境可读但写入失败。**不要循环重试保存**；把分隔线之后的说明转发给用户并停止当前操作。
- 其他 `ERROR:<message>`：把错误信息告知用户，暂停操作。

## 5. 底层脚本（一般不需要直接使用）

`check_api_key.js`、`save_api_key.js`、`create_guest_key.js` 是 `ensure_credentials.js` 的底层组件，仍然可用（输出 `SUDOWORK_ENV_OK_KEY_FOUND` / `KEY_FOUND:<key>` / `SUDOWORK_KEY_SAVED` / `KEY_SAVED` 等细粒度 token），仅用于调试或用户明确指定时；正常流程一律使用 `ensure_credentials.js`。删除凭据见 `delete-api-key.md`。
