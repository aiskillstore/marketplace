# 结果反馈与错误处理

发布、更新、上传或通用 API 请求完成后读取本文件。判断依据是**脚本的输出**：stdout 输出包含成功 JSON 或成功 token 即成功；stderr 输出 `ERROR:<code>` 即失败。

## 1. 发布成功

如果脚本 stdout 返回的 JSON 表示成功：

- 返回结果中已经包含完整的 `share_url` 字段，例如 `https://s.shareone.vip/s/<share_id>`。
- 必须直接使用返回的 `share_url` 展示给用户；不要展示备用链接。
- 如果返回中包含 `custom_slug_warning`，必须同时展示该提示；这表示内容已发布成功，但用户请求的自定义短链接没有生效。
- 如果返回中包含 `custom_slug_suggestions`，必须把其中的推荐短链接名称一起展示给用户。
- 不要自己拼接分享链接。

如果设置了密码，必须加粗显示密码：

> 发布成功！
> 链接：<返回的 share_url>
> 提取码：**<密码>**

## 2. 功能提示

在本次会话首次向用户展示生成的 `share_url` 时，必须主动但简短地提示所有未使用的高级功能。后续发布不再重复提示。

默认提示：

> 您也可以让我为这个分享链接设置自定义短链接名称、访问密码或水印。

按本次发布已经使用的能力删减提示内容：

- 如果用户已经指定自定义短链接，不再提示“自定义短链接名称”。
- 如果用户已经设置访问密码，不再提示“访问密码”。
- 如果用户已经设置水印，不再提示“水印”。
- 如果自定义短链接、访问密码、水印都已使用，不进行功能提示。

## 3. 自定义短链接冲突的两种行为

slug 冲突在两类发布中的表现**不同**，不要混淆：

- **文本页面（`/api/v1/pages`）**：slug 冲突会导致**发布失败**，返回 HTTP 400 且 `detail.code` 为 `CUSTOM_SLUG_TAKEN`。提示用户短链接名称已被占用；如果 `detail.suggested_slugs` 中包含推荐名称，必须一起展示。不要告诉用户“已发布成功”。
- **二进制文件（`/api/v1/files`）**：slug 冲突时**发布仍然成功**，返回中带 `custom_slug_warning`（和可能的 `custom_slug_suggestions`），只是自定义短链接没有生效。展示链接的同时必须展示该提示。

## 4. 非发布操作成功

对不一定返回 `share_url` 的操作，按脚本输出反馈结果：

- `update_share_settings.js`：stdout 为 JSON 且无 `ERROR:` 即设置更新成功。若 JSON 包含 `share_url`、`custom_slug_warning` 或 `custom_slug_suggestions`，按第 1 节展示；否则简短说明设置已更新。
- `comment_resolve.js`：输出 `REPLY_POSTED:<id>` 后又输出 `COMMENT_RESOLVED:<id>` 表示评论已回复并关闭；输出 `COMMENT_DISMISSED:<id>` 表示评论已忽略并记录原因。
- `shareone_api_request.js`：stdout 为接口返回体；用于查看评论时，摘要或列出评论即可，不要按发布成功话术处理。
- `download_share.js --save`：stdout 输出 `SAVED:<本地文件名>` 表示下载并保存成功；不要提示发布高级功能。

## 5. 常见错误

- 内容违规拦截，HTTP 400：提取 JSON 中的 `detail` 字段展示给用户，例如“发布失败，内容未通过安全审核。原因：<detail>”。
- API Key 无效或权限不足，脚本输出 `ERROR:AUTH_FAILED`：提示“API Key 无效或权限不足”。
- 找不到页面，HTTP 404：若 PUT 更新遇 404，说明原页面已被后台删除，请询问用户是否作为新页面重新 POST。
- 二进制文件被误发到 pages JSON 接口，HTTP 400 且提示检测到二进制内容：使用 `publish.js` 重新发布（它会自动分发到正确通道）；该错误只在绕过 `publish.js` 直接调用底层脚本时才可能出现。
- `ERROR:FILE_PREVIOUSLY_PUBLISHED`：该本地文件之前已发布过，错误提示中带有原 `share_id` 和链接。默认改用 `--share-id <id>` 更新原链接；只有用户明确要求为同一文件再创建一个新链接时，才追加 `--force-new` 重试。
- `ERROR:LOOKS_LIKE_SHARE_LINK`：把 ShareOne 链接当成本地文件传给了发布脚本。要修改已有链接设置用 `update_share_settings.js`，要下载用 `download_share.js`。
- `ERROR:UPDATE_VERIFY_FAILED`：不要按发布成功处理（即使 stdout 中已经输出了包含 `share_url` 的 JSON）。提示用户“ShareOne 接口接受了更新请求，但回读源内容与本地文件不一致，更新可能没有真正生效”，并保留本地文件，等待用户决定是否重试或作为新页面发布。
- `ERROR:ACTIVE_SHARE_TASK`：当前目录存在 `.shareone_active_task`（评论处理任务进行中），但发布命令没有带 `--share-id`。按错误提示中给出的 id 改用 `--share-id <id>` 执行 PUT 更新原链接；只有在确认用户确实要创建全新链接时，才删除该锚点文件或追加 `--force-new` 重试。
- `ERROR:UNKNOWN_ARGUMENT:<arg>` 或 `ERROR:MISSING_VALUE:<flag>`：命令参数写错或缺值。按脚本 Usage 修正命令，不要绕过脚本。
- 下载相关错误码（`PASSWORD_REQUIRED`、`PASSWORD_INVALID`、`DOWNLOAD_NOT_ALLOWED`、`SHARE_NOT_FOUND`）的处理见 `download-file.md`。
