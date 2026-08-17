# 下载 ShareOne 链接文件

当用户要求“下载这个 ShareOne 链接的文件”或“取回这个链接的源内容”时读取本文件。普通下载不需要先配置 API Key：脚本会在已有凭据时优先尝试 owner 下载，没有凭据时自动退回公开下载。只有用户明确要求用 owner 身份下载、或公开下载失败后需要 owner 权限时，才回到 `environment-and-credentials.md` 完成凭据配置。

## 1. 获取链接或 ref

用户可以提供完整链接、`share_id`、自定义短链 slug，或 `/s/<share_id>` 这类路径。把用户原始输入直接作为参数传给下载脚本即可，脚本会自行解析；不需要自行判断 slug 和 share_id。

## 2. 下载内容

使用 `--save`，脚本会按服务端返回的文件名自动保存到当前目录；如果同名文件已存在，会自动添加数字后缀避免覆盖。成功后在 stdout 输出 `SAVED:<本地文件名>`：

```bash
node scripts/download_share.js "<LINK_OR_ID>" --save
```

同时 stderr 会输出文件信息：

```text
INFO:FILENAME:<原始文件名>
INFO:CONTENT_TYPE:<mime 类型>
```

脚本会在已配置 ShareOne API Key 时先尝试 owner 下载接口；owner 下载不受访问密码和 `allow_download` 限制。如果当前 API Key 不是 owner 或没有 API Key，脚本会自动退回公开下载。

如果用户提供了访问密码，必须通过 `--password` 传入（脚本用 POST body 发送密码），不要把密码拼进 URL：

```bash
node scripts/download_share.js "<LINK_OR_ID>" --password "<PASSWORD>" --save
```

如需把内容输出到 stdout 自行处理（例如管道），去掉 `--save` 即可，此时 stdout 是原始文件内容（不是 JSON）。

## 3. 错误处理

下载失败时脚本向 stderr 输出 `ERROR:<code>`，按 code 处理：

| 脚本输出 | 含义与应对 |
| --- | --- |
| `ERROR:PASSWORD_REQUIRED` | 该链接需要访问密码才能下载。告诉用户请提供密码后再下载。 |
| `ERROR:PASSWORD_INVALID` | 用户提供的访问密码不正确。告诉用户密码错误，请确认后重新提供。 |
| `ERROR:DOWNLOAD_NOT_ALLOWED` | 链接没有开启允许下载。告诉用户需要链接 owner 在文件管理中开启“允许下载”后才能下载。 |
| `ERROR:SHARE_NOT_FOUND` | 链接不存在或已失效。请用户确认链接是否正确、是否已过期删除。 |
| 其他 `ERROR:<HTTP ...>` | 按 `result-and-errors.md` 的通用错误规则处理。 |

不要在收到错误后重试同一请求；先按上表与用户沟通缺失的信息。

## 4. 后续处理

- 如果用户只是要求下载或查看，展示下载结果摘要，并按 stderr 中 `INFO:FILENAME` / `INFO:CONTENT_TYPE` 说明文件名和内容类型。
- 如果用户要求修改下载到的内容，直接编辑 `SAVED:` 给出的本地文件，再根据文件类型读取 `publish-text-page.md` 或 `publish-binary-file.md` 执行更新。
