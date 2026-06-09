# 更新已有 ShareOne 链接设置

当用户提供已有 ShareOne 链接、`share_id` 或自定义短链 slug，并且只要求修改水印、访问密码、自定义短链接或评论开关时读取本文件。执行前必须已经完成 `environment-and-credentials.md`。

本 workflow 只更新元数据，不发布新内容，不替换源文件。

## 1. 判断是否适用

适用示例：

- “给 http://localhost:8000/s/test-page 加水印”
- “把这个 ShareOne 链接的水印改成内部资料”
- “清除 /s/demo 的访问密码”
- “给这个已有链接开启评论”
- “把这个链接的短链改成 product-demo”

如果用户没有提供要设置的具体值，例如只说“加水印”但没有水印文字，先询问水印内容。不要自动生成默认水印。

## 2. 不要做的事

- 不要下载源文件来判断类型。
- 不要使用 `upload_page.js`。
- 不要重新上传页面内容、二进制文件或 `html_content`。
- 不要为了 `/s/<ref>` 判断是否是二进制文件；`/s/<ref>` 按 HTML/Markdown 页面设置更新处理。

## 3. 更新命令

推荐使用专用脚本。脚本会解析完整 URL、`/s/<ref>` 路径、裸 `share_id` 或 slug；如果传入完整 URL，例如 `http://localhost:8000/s/test-page`，会自动使用该 URL 的 origin 作为 API base URL。

```bash
node scripts/update_share_settings.js "<SHARE_LINK_OR_ID>" [--watermark "OPTIONAL_WATERMARK"] [--password "OPTIONAL_PASSWORD"] [--slug "OPTIONAL_SLUG"] [--allow-comments true/false]
```

规则：

- Sudowork 环境不要传 `--api-key`。
- 普通 AI Agent 环境可传 `--api-key`，也可以依赖 `SHAREONE_API_KEY` 或本地凭证。
- 空字符串 `""` 表示清除对应设置，例如 `--watermark ""` 或 `--password ""`。
- 只传用户明确要求修改的字段；不要把未知的现有设置补进请求体。

## 4. Endpoint 映射

脚本内部按以下规则选择接口：

- `/s/<ref>` 和 `/md/<ref>`：`PUT /api/v1/pages/<ref>`。
- `/pdf/<ref>`、`/ppt/<ref>` 和 `/word/<ref>`：`PUT /api/v1/files/<ref>`。
- 裸 `share_id` 或 slug：先尝试 `PUT /api/v1/pages/<ref>`；如果服务端明确提示该 endpoint 只适用于 HTML/Markdown 或要求使用 `/api/v1/files`，再尝试 `PUT /api/v1/files/<ref>`。

裸 `share_id` 或 slug 的回退过程仍然不下载源文件。

## 5. 下一步

执行完成后读取 `result-and-errors.md`，按返回 JSON 展示结果或错误。
