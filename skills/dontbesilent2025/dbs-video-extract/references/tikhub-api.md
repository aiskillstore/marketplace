# TikHub API 接口参考

仅在新增平台查询、确认接口参数、处理错误或检查费用时读取。

## 基础配置

- 中国大陆：`https://api.tikhub.dev`
- 中国大陆以外：`https://api.tikhub.io`
- 鉴权请求头：`Authorization: Bearer API_KEY`
- 中文文档：<https://docs.tikhub.io/doc-4579297>
- Swagger：<https://api.tikhub.io>

所有 API 路径和参数在两个域名之间保持一致。

## MCP 配置

- 官方说明：<https://tikhub.io/mcp>
- Streamable HTTP：`https://mcp.tikhub.io/{platform}/mcp`
- 抖音平台：`https://mcp.tikhub.io/douyin/mcp`
- 小红书平台：`https://mcp.tikhub.io/xiaohongshu/mcp`
- 微信平台：`https://mcp.tikhub.io/wechat/mcp`
- 鉴权：`Authorization: Bearer API_KEY`
- 协议版本：`2024-11-05`
- 内容类型：`application/json`
- Accept：`application/json, text/event-stream`

MCP 调用顺序：

1. `initialize`；
2. 保存响应头 `Mcp-Session-Id`；
3. 使用同一鉴权头和 Session ID 调用 `tools/list` 或 `tools/call`。

`https://api.tikhub.dev/mcp` 和 `https://api.tikhub.io/mcp` 不提供 MCP 服务。REST API 返回的 `api_key_scopes` 中可能出现 `/mcp`，它表示权限范围，不能当成 MCP URL。

抖音常用 MCP 工具：

- `douyin_app_v3_handler_user_profile`：用 `sec_user_id` 查询用户资料；
- `douyin_app_v3_fetch_one_video_by_share_url`：用 `share_url` 查询作品；
- `douyin_web_fetch_one_video_by_share_url`：作品 App V3 失败时回退。

小红书视频笔记：

- `xiaohongshu_app_v2_get_video_note_detail`：参数使用 `share_text` 传入完整分享链接或文案；响应 `data.data` 的首条为目标笔记，后续条目可能是推荐内容。

微信视频号作品：

- `wechat_channels_v2_fetch_video_detail`：参数使用 `share_url`，并设置 `raw: false` 获取稳定字段摘要。

抖音分享短链接可能指向用户主页。先跟随公开跳转：

- `/share/user/` 或查询参数含 `sec_uid`：提取用户 ID，调用用户资料工具；
- `/video/`、`/note/` 或 `/slides/`：调用作品工具。

## 内置路由

### 当前账户信息

```text
GET /api/v1/tikhub/user/get_user_info
```

不需要查询参数。返回 `api_key_data` 和 `user_data`。脚本的 `account` 命令会删除邮箱字段后再输出。

### 抖音 App V3 分享链接解析

```text
GET /api/v1/douyin/app/v3/fetch_one_video_by_share_url
query: share_url=<抖音分享链接>
```

返回字段较丰富。内容受版权、删除、隐私或可见范围限制时，可能没有有效作品数据。

### 抖音 Web 分享链接解析

```text
GET /api/v1/douyin/web/fetch_one_video_by_share_url
query: share_url=<抖音分享链接>
```

Web 返回字段较少，视频画质通常更高。App V3 失败或没有作品数据时可回退 1 次。

### 小红书 App V2 视频笔记详情

```text
MCP xiaohongshu_app_v2_get_video_note_detail
arguments: share_text=<小红书分享链接或完整分享文案>
```

摘要保留笔记 ID、作者、标题、发布时间、时长、IP 属地、标签，以及点赞、收藏、评论、分享和播放字段。接口可能同时返回推荐笔记，当前只读取首条目标笔记。

### 微信视频号 Channels V2 作品详情

```text
MCP wechat_channels_v2_fetch_video_detail
arguments: share_url=<视频号分享链接>, raw=false
```

摘要保留作品 ID、作者、标题、发布时间、时长，以及阅读、点赞、收藏、评论和转发字段。

## 字幕与语音转写边界

TikHub 提供部分字幕接口：

- Bilibili Web：获取视频已有字幕信息；
- YouTube Web／Web V2：获取视频已有字幕，可输出 SRT、XML、JSON3 或纯文本。

YouTube Web V2 文档明确说明不会为无字幕视频执行 AI 语音转写。当前文档没有抖音或小红书通用 AI 语音转写端点。

## HTTP 状态码

- `400 Bad Request`：请求格式或参数错误；
- `401 Unauthorized`：Key 缺失、无效、未激活或过期；
- `402 Payment Required`：余额或免费额度不足；
- `403 Forbidden`：账户、邮箱验证、路由或 Key 权限问题；
- `404 Not Found`：路由或数据不存在；
- `429 Too Many Requests`：超过速率限制；
- `500 Internal Server Error`：TikHub 服务端错误。

出现 `401`、`402`、`403`、`429` 时停止自动重试。`500` 可以在用户仍需要该结果时进行 1 次人工确认后的重试。

默认单次数据查询 15 秒超时，不自动重试。TikHub 单侧超时或失败时，整合脚本继续执行轻抖文字稿步骤。

## 新增路由原则

1. 在官方文档中确认路由属于读取公开数据。
2. 记录路径、参数、返回结构、价格和限制。
3. 优先通过通用 `get` 验证一次真实响应。
4. 只有重复使用且字段稳定时，才为该路由增加专用子命令。
5. 不把完整 API Key、Cookie 或其他平台凭证写入参考文件。
