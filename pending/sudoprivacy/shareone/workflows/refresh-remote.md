# 刷新 remote-url auto-follow 分享

当用户要求刷新/拉取某个绑定了远程源 URL（GitHub 等）的分享的最新内容时读取本文件——典型场景：用户刚 push 到源站，想让 ShareOne 立即同步。

## 背景（为什么需要显式刷新）

remote 页面的刷新是**懒的、且只在渲染路径触发**：只有打开渲染页（`/s/<ref>` 等）才会 refetch，且有节流（60s 硬下限、无 ETag 时 10 分钟 TTL）。`download`/`/file/<id>` 只服务上次缓存的 snapshot，不会 refetch。所以 push 完直接下载常常还是旧内容。本命令绕过节流立即拉取。

## 1. 凭据

刷新是 owner-only。先运行 `node scripts/ensure_credentials.js`（含义见 `workflows/environment-and-credentials.md`）。没有可用凭据时不要继续。

## 2. 执行刷新

```bash
node scripts/refresh_share.js <REF>
```

`<REF>` 可以是完整链接、`/s/<ref>` 等路径、裸 `share_id` 或 slug。

成功时 stdout 输出 JSON `{ share_id, remote_url, remote_cached_at, remote_fetch_failures, remote_last_error }`，stderr 输出 `SHARE_REFRESHED:<ref>`。若 `remote_last_error` 非空，说明源站抓取失败，把原因反馈给用户（源可能不可达或返回非 2xx）。

## 3. 错误处理

- `NOT_REMOTE_BOUND`（400）：该分享不是 remote-url 绑定的（是 static-publish），没有源可刷新。此时若用户想改内容，改走「修改设置」或「重新发布」流程。
- `ERROR:KEY_NOT_FOUND`：先按 `environment-and-credentials.md` 配置凭据。
- `HTTP 404`：链接不存在或不属于当前 API Key。
- 不要用「重新 PUT 同一个 `remote_url`」来强制刷新——那是旧的绕法；直接用本命令。
