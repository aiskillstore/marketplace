---
name: shareone
version: 1.1.8
description: 发布本地生成的 HTML、Markdown、TXT、PDF、Word 或 PPTX 到 ShareOne 平台，生成公网分享短链接；或者当用户提供 ShareOne 链接并要求下载文件、修改文件、拉取/处理评论时使用此技能。当用户要求“发布”、“分享”、“生成链接”、“上线”，或者“下载这个链接的文件”、“修改这个 ShareOne 链接的内容”、“拉取这个链接的评论”时，必须使用此技能。
---

# AI Agent 技能：发布到 ShareOne (shareone)

这个 Skill 允许 AI Agent（如 Openclaw 等）将当前生成的历史会话以及 HTML/Markdown/TXT/PDF/PPT 等文件发布到 ShareOne 线上托管服务，并为用户生成一个持久化的公网分享链接。

## 入口隔离规则

本 skill 和用户本机可能安装的 `shareone` CLI 是两个独立入口。除非用户明确要求“使用 CLI”或指定执行 `shareone ...` 命令，否则不要调用系统 PATH 中的 `shareone` 命令。

使用本 skill 时，所有 ShareOne 操作都必须调用本 skill 目录内的脚本，例如：

```bash
node scripts/check_api_key.js
node scripts/upload_page.js <file>
node scripts/shareone_upload.js <file>
node scripts/update_share_settings.js <share_link_or_id>
node scripts/shareone_api_request.js <api_path>
```

即使 `which shareone` 能找到 CLI，也不要把自然语言的发布、下载、评论处理任务改走 CLI。

## 使用说明与触发条件

当用户表达出以下意图时，应主动使用此技能：

- "帮我把 `index.html` 发布到 ShareOne"
- "把我刚才生成的网页发布，给我个链接"
- "生成一个可分享的链接给我的团队看"
- "Upload this presentation to ShareOne and protect it with password 'secret'"
- "发布这个 PDF 到 ShareOne，并加上密码 1234"
- "把这个网页发布到 ShareOne，加上水印 '内部绝密'"
- "把这个网页发布到 ShareOne，链接叫 product-demo"
- "发布这份设计稿并开启协同评论模式"
- "用 shareone 分享上一轮对话"
- "把我刚才写的代码/大段文字分享出去"
- "Share your last response as a note"
- "帮我下载这个 ShareOne 链接的文件：https://shareone.app/s/xxx"
- "拉取一下这个链接的评论：https://shareone.app/s/xxx"
- "给这个 ShareOne 链接加水印：https://shareone.app/s/xxx"
- "根据这个链接的评论修改页面：https://shareone.app/s/xxx"
- "修改这个 ShareOne 链接的内容：https://shareone.app/s/xxx"

## 总规则：先路由，再读取子流程

入口文件只负责判断用户意图、判断环境、选择需要阅读的 workflow。不要一次性读取所有 `workflows/*.md` 文件；只读取当前任务需要的子文件。

所有需要 ShareOne API 的操作，都先运行：

```bash
node scripts/check_api_key.js
```

用输出判断环境与凭据状态：

- `SUDOWORK_KEY_FOUND`：当前在 Sudowork 中，且 Sudowork 已配置 ShareOne API Key。
- `SUDOWORK_KEY_NOT_FOUND`：当前在 Sudowork 中，但还没有设置 ShareOne API Key。
- `KEY_FOUND:<api_key>`：当前是普通 AI Agent 环境，且已找到 API Key。
- `KEY_NOT_FOUND`：当前是普通 AI Agent 环境，且没有找到 API Key。

术语固定：

- Sudowork：发布、评论、通用请求命令不要传 `--api-key`，凭证由 Auth Proxy secrets 注入。
- 普通 AI Agent：可以使用 `--api-key`、环境变量 `SHAREONE_API_KEY` 或本地凭证文件。

## 操作路由表

根据用户意图读取对应 workflow：

如果用户提供已有 ShareOne 链接、`share_id` 或自定义短链 slug，并且只要求修改水印、访问密码、自定义短链接或评论开关，必须优先读取 `workflows/update-share-settings.md`。这是元数据更新，不要按文件类型路由，不要下载源文件，不要使用 `upload_page.js`，不要重新上传内容。

其他发布任务先按目标文件类型路由，再按用户动作路由。文件类型优先级最高。

| 目标文件/内容类型 | 必须读取的 workflow |
| --- | --- |
| `.ppt`、`.pptx`、`.pdf`、`.doc`、`.docx`、`.png`、`.jpg`、`.jpeg`、`.gif`、`.zip` 或其他二进制文件 | `workflows/publish-binary-file.md` |
| `.html`、`.md`、`.txt`、对话内容、大段文本、代码块，或已经包装成 HTML 的内容 | `workflows/publish-text-page.md` |
| 包含图表、流程图、思维导图、时序图、甘特图等可视化内容的 HTML 页面 | `workflows/publish-text-page.md`（参考其中的 Mermaid.js 章节） |

| 用户意图 | 需要读取的 workflow |
| --- | --- |
| 已有 ShareOne 链接只修改水印、访问密码、自定义短链接或评论开关 | 先读 `workflows/environment-and-credentials.md`，再读 `workflows/update-share-settings.md`，最后读 `workflows/result-and-errors.md` |
| 发布、分享、生成链接、上线、分享上一轮对话、大段文本或代码 | 先读 `workflows/environment-and-credentials.md`，再按文件类型读 `workflows/publish-text-page.md` 或 `workflows/publish-binary-file.md`，最后读 `workflows/result-and-errors.md` |
| 删除、清除、移除、重置 ShareOne API Key | 读 `workflows/delete-api-key.md` |
| 下载 ShareOne 链接的文件或源内容 | 先读 `workflows/environment-and-credentials.md`，再读 `workflows/download-file.md` |
| 查看、拉取、总结 ShareOne 链接评论，但用户没有要求修改 | 先读 `workflows/environment-and-credentials.md`，再读 `workflows/comments-view.md` |
| 处理评论、根据评论修改页面、修复 ShareOne 链接内容 | 先读 `workflows/environment-and-credentials.md`，再读 `workflows/comments-process.md`，必要时读 `workflows/publish-text-page.md`，最后读 `workflows/result-and-errors.md` |
| 发布二进制文件，或更新已上传二进制文件的密码/水印 | 先读 `workflows/environment-and-credentials.md`，再读 `workflows/publish-binary-file.md`，最后读 `workflows/result-and-errors.md` |

## ShareOne 链接与 share_id

当用户提供 ShareOne 链接时，可以从完整链接、`/s/<share_id>` 路径、`share_id` 或自定义短链 slug 中解析目标。下载任意用户允许下载的链接时，优先使用公开下载接口并把原始输入作为 `ref`。

`/s/<share_id>` 是最终给用户访问的分享链接，不是上传 API endpoint。不要把 `/s/<share_id>` 当作发布地址，也不要直接向 `/s/<share_id>` PUT/POST 文件。

`share_id` 可用于查看评论、处理评论、owner 下载源文件、文本页面内容 PUT 更新，以及已有链接的密码/水印/短链/评论开关元数据更新。非 owner 下载必须要求链接已开启允许下载；若接口返回 `DOWNLOAD_NOT_ALLOWED`，直接提示用户让链接 owner 先开启允许下载。

对已有链接只改水印、密码、自定义短链接或评论开关时，使用 `update_share_settings.js`。`/s/<share_id>` 和 `/md/<share_id>` 走页面设置更新；`/pdf/<share_id>`、`/ppt/<share_id>` 和 `/word/<share_id>` 走文件设置更新。裸 `share_id` 或 slug 由脚本先尝试页面 endpoint，必要时回退文件 endpoint。整个过程不要下载源文件。

如果目标是 `.pptx`、`.ppt`、`.pdf`、Word、图片、zip 等二进制文件，“发布这个文件”默认必须走文件上传 workflow 和 `shareone_upload.js`。不要因为会话里存在旧的 `/s/<share_id>` 就改走文本页面 PUT；二进制文件内容上传不能使用 `upload_page.js`。

如果你在当前会话中已经为同一个文本/HTML 文件生成过 ShareOne 链接，可复用之前的 `share_id` 执行文本页面 PUT 更新；否则执行首次创建。

## 不可跳过的阻塞步骤

以下步骤是阻塞性用户通知，不是可选说明。触发后必须先发给用户，再继续后续发布、下载、评论处理或最终回复。

- 如果 `create_guest_key.js` 输出 `GUEST_KEY_CREATED:<api_key>`，必须立即向用户发送临时 API Key、绑定账号链接和保存提醒。即使 key 已经自动保存到 Sudowork/Auth Proxy 或本地凭证文件，也不能省略该通知。
- 发送临时 API Key 通知前，不得继续执行原任务的上传、下载、评论处理命令。
- 本会话首次向用户展示生成的 `share_url` 时，必须按 `workflows/result-and-errors.md` 提示所有未使用的高级功能：自定义短链接名称、访问密码、水印。
- 如果用户已经使用了自定义短链接、访问密码、水印中的某些能力，只提示剩余未使用的能力；如果三项都已使用，则不提示。

## 不要遗漏的全局约束

- 发布前必须完成凭据检查和必要的凭据配置。
- 每次发布前都必须展示以下安全提示，并等待用户明确回复“同意”或 `agree` 后才能继续：
  > 发布前安全提示：在将页面发布到公网前，请您确认该页面内容符合相关法律法规要求。禁止发布反动、涉政、暴力、色情、侵权或恶意代码。上传的内容将免费托管保留 90 天。
  > 如果您的内容符合要求，请回复“同意”，我将为您发布。
- 发布成功后必须直接使用接口或脚本返回的 `share_url`，不要自行拼接分享链接；如果返回中包含 `backend_url`，必须同时作为“备用链接”展示给用户。
- 如果用户要求开启评论、允许讨论或协同模式，才添加 `--allow-comments true`。默认不开启评论。
- 自定义短链接（slug）：服务端会根据文件名自动生成可读的 slug（如 `quarterly-report`），客户端无需额外操作。如果用户明确要求”链接叫 xxx”、”自定义短链接 xxx”、”URL 后缀 xxx”，发布命令添加 `--slug xxx` 覆盖自动生成；slug 冲突时把服务端提示反馈给用户，不要静默改名。
- 评论处理必须形成闭环：认领、修改、重新发布、回复、关闭或 dismiss。

## 最终回复前检查清单

在回复用户前，逐项检查：

- 如果本轮创建了临时 API Key，是否已经把 API Key、绑定账号链接和保存提醒发给用户。
- 如果本轮发布内容，是否已经完成凭据检查，并在执行发布命令前获得用户明确回复“同意”或 `agree`。
- 如果发布成功，是否直接展示返回的 `share_url`，没有自行拼接链接。
- 如果返回中包含 `backend_url`，是否作为备用链接展示给用户。
- 如果返回中包含 `custom_slug_warning` 或 `custom_slug_suggestions`，是否展示给用户。
- 如果这是本会话首次展示生成的 `share_url`，是否提示所有未使用的高级功能。
