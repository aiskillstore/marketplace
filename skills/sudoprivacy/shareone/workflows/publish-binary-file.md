# 发布二进制文件

当用户要发布 PDF、PPTX、PPT、Word、图片、zip 或其他二进制文件时读取本文件。发布前必须已经完成 `environment-and-credentials.md`。

适用文件类型包括但不限于：`.pdf`、`.ppt`、`.pptx`、`.doc`、`.docx`、`.png`、`.jpg`、`.jpeg`、`.gif`、`.zip`。

如果用户说“发布这个 pptx / PPT / 演示文稿 / presentation”，必须使用本 workflow。不要读取或执行 `publish-text-page.md`，不要使用 `upload_page.js`。

`/s/<share_id>` 是最终给用户访问的分享链接，不是上传地址。不要向 `/s/<share_id>` 上传 PPTX/PPT/PDF/Word 文件。

## 1. 文件检查

- 使用用户指定的文件。
- 如果用户没有指定文件，根据上下文寻找最近一次生成或编辑的文件。
- 如果文件不存在，停止并告知用户。
- 提取用户可能要求的密码 (`password`)、水印 (`watermark`) 和自定义短链接后缀 (`slug`)。服务端会根据文件名自动生成可读的 slug，客户端无需主动设置。只有用户明确说”链接叫 xxx / 自定义短链接 xxx / URL 后缀 xxx”时才用 `--slug` 覆盖。

## 2. 发布前安全确认

发布前安全提示由入口 `SKILL.md` 统一描述。未展示入口安全提示并获得用户明确回复“同意”或 `agree` 前，不得执行本文件中的发布命令。

## 3. 首次发布二进制文件

为了最大兼容性，推荐使用本 skill 的 Node.js 脚本发起 HTTP 请求。

由于二进制文件可能较大，ShareOne 采用直传云存储方式，支持 S3 或 Azure。脚本会自动根据服务端返回的 `upload_type` 判断走 S3 表单上传还是 Azure PUT 直传。

首次发布 `.pptx`、`.ppt`、`.pdf`、Word、图片、zip 等二进制文件时，一律使用文件上传脚本。该脚本会创建新的 ShareOne 文件分享链接，并在结果中返回 `share_url`。

执行：

```bash
node scripts/shareone_upload.js "<FILE_PATH>" [--password "OPTIONAL_PASSWORD"] [--watermark "OPTIONAL_WATERMARK"] [--slug "OPTIONAL_SLUG"]
```

规则：

- Sudowork 环境不要传 `--api-key`。
- 普通 AI Agent 环境可传 `--api-key`，也可以依赖 `SHAREONE_API_KEY` 或本地凭证。
- 如果服务端返回 `custom_slug_warning`，说明文件链接已生成但自定义短链接未生效。必须把提示展示给用户，并请用户提供新的 slug 或之后到管理页修改。

## 4. 更新已上传二进制链接的密码或水印

对于已经上传的二进制文件，如果用户只要求修改密码或水印，调用通用鉴权请求脚本：

```bash
node scripts/shareone_api_request.js "/api/v1/files/<YOUR_SHARE_ID>" \
  --method PUT \
  --data '{"password": "NEW_PASSWORD", "watermark": "NEW_WATERMARK"}'
```

规则：

- Sudowork 环境不要传 `--api-key`。
- 普通 AI Agent 环境可传 `--api-key`，也可以依赖 `SHAREONE_API_KEY` 或本地凭证。
- 空字符串 `""` 表示取消密码或水印。
- `/api/v1/files/<YOUR_SHARE_ID>` 这里只用于修改已上传二进制链接的密码或水印，不用于上传新的 PPTX/PPT/PDF/Word 文件内容。
- 如果用户要求“发布某个 pptx”或“替换成另一个 pptx”，不要把文件内容 PUT 到 `/s/<share_id>` 或 `/api/v1/files/<share_id>`；应使用上面的 `shareone_upload.js "<FILE_PATH>"` 文件上传流程。

## 5. 下一步

执行完成后读取 `result-and-errors.md`，按返回 JSON 展示结果或错误。
