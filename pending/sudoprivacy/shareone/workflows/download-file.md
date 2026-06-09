# 下载 ShareOne 链接文件

当用户要求“下载这个 ShareOne 链接的文件”或“取回这个链接的源内容”时读取本文件。执行前必须已经完成 `environment-and-credentials.md`。

## 1. 获取链接或 share_id

用户可以提供完整链接、`share_id`、自定义短链 slug，或 `/s/<share_id>` 这类路径。优先把用户原始输入作为 `ref` 传给公开下载接口；不需要自行判断 slug 和 share_id。

## 2. 下载内容

优先使用下载脚本。脚本会在已配置 ShareOne API Key 时先尝试 owner 下载接口：

```bash
node scripts/download_share.js "<LINK_OR_ID>" > downloaded-file
```

owner 下载接口不受访问密码和 `allow_download` 限制；如果当前 API Key 不是 owner 或没有 API Key，脚本会自动退回公开下载。

如果用户提供了访问密码，必须通过 `--password` 传入，脚本会用 POST body 发送密码，不要把密码拼进 URL：

```bash
node scripts/download_share.js "<LINK_OR_ID>" --password "<PASSWORD>" > downloaded-file
```

返回是原文件内容，不是 JSON。根据响应头里的文件名保存到本地文件，再按用户要求查看、总结或处理。

如果接口返回：

```json
{
  "detail": {
    "code": "PASSWORD_REQUIRED",
    "message": "This link requires a password before downloading."
  }
}
```

必须明确告诉用户：该 ShareOne 链接需要访问密码，请提供密码后再下载。

如果接口返回结构化错误：

```json
{
  "detail": {
    "code": "DOWNLOAD_NOT_ALLOWED",
    "message": "Downloads are not enabled for this link. Ask the owner to enable allow_download first."
  }
}
```

必须明确告诉用户：这个 ShareOne 链接没有开启允许下载，需要链接 owner 在文件管理中开启“允许下载”后才能让 agent 下载。

## 3. 后续处理

- 如果用户只是要求下载或查看，展示下载结果摘要，并按返回的文件名和 `content_type` 说明内容类型。
- 如果用户要求修改下载到的内容，先保存源内容到本地文件，再根据文件类型读取 `publish-text-page.md` 或 `publish-binary-file.md` 执行更新。
- 已配置 API Key 时，脚本会优先尝试 `/api/v1/shares/<SHARE_ID>/download` owner 下载；没有 API Key 或非 owner 时，必须要求链接开启 `allow_download`，密码链接还必须要求用户提供访问密码。
