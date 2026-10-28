# 飞书接入

配套命令以已核对的 `lark-cli` 方言为基础。每台机器先看 help；仅有 `feishu-cli` 时先核对兼容性。读取和写入都要核实身份、scope 与目标资源权限；不要输出 appSecret 或 access token。

## 已安装的能力

有相应 Skill 时按需读 `lark-shared`、`lark-task`、`lark-doc`、`lark-event`、`lark-im`；未知原生接口用 `lark-openapi-explorer` 核实。当前 Skill 自身包含基础接入说明，可在缺少上述 Skill 时工作。

```bash
lark-cli --help
lark-cli auth status --help
lark-cli task +create --help
lark-cli docs +fetch --api-version v2 --help
lark-cli event +subscribe --help
```

user 与 bot 的可见资源不同。bot 权限错误去后台配置，不能用用户登录替代；用户授权按缺少的 scope 增量申请。安装／认证需要用户参与时保留文字版交付。

## 派单、读取与回复

创建任务使用 `task +create`，指定 summary、description、assignee、due 与 idempotency-key。完整命令从 help 构造，使用参数数组或数据文件，禁止把任务正文拼接成 shell 代码。

文档读取：`lark-cli docs +fetch --api-version v2 --doc DOCUMENT_URL --doc-format markdown`。旧版 CLI 不支持 v2 时查看该版本 help；处理分页／截断，正文不完整不能验收。Wiki URL 由文档接口解析或先查节点的 obj_token，不能直接将 wiki token 当文档 token。

文档回复优先 `docs +update` 的 append 模式，参数按当前 help 核实。也可以授权后用 `im +messages-reply`／`+messages-send` 回复指定会话；文档追加不保证员工收到通知，需核实约定通知渠道。若读取的是任务评论，先核实该版本实际读取接口，禁止借用云文档评论接口。

## 文档编辑事件

事件类型为 `drive.file.edit_v1`。先在飞书开发者后台配置事件和接收方式，再针对目标文档订阅。应用或用户需符合该资源的订阅权限要求；可阅读并不保证可订阅。

官方订阅接口：`POST /open-apis/drive/v1/files/{file_token}/subscribe`，新版文档 query 参数 `file_type=docx`。当前 CLI 专用子命令缺失时使用通用 `api`。正文编辑订阅与 `drive user subscription` 评论通知订阅分开。

配套脚本 `subscribe` 默认只输出 dry-run。确认授权后加 `--execute`；只有 API 返回成功才记订阅成功。多种文档类型、权限和旧版 CLI 均需实际核实，脚本仅支持登记的 docx。

接收：`lark-cli event +subscribe --event-types drive.file.edit_v1`。长连接是 bot 身份的传输进程；目标资源订阅可选择符合权限条件的 user 或 bot 身份。必须使用同一个应用配置。不要启用 `--force` 多连接抢事件。

事件提供文档 token、操作人和事件 ID；收到后另读正文。只关注已登记文档。多人共同编辑时不能仅凭事件把全部改动归给一个人；核实回填署名与内容。

## 来源与核实范围

- [官方 CLI](https://github.com/larksuite/cli)
- [官方 SDK 文档订阅实现](https://github.com/larksuite/oapi-sdk-go/blob/v3_main/service/drive/v1/resource.go)
- [官方 SDK 事件字段和订阅参数](https://github.com/larksuite/oapi-sdk-go/blob/v3_main/service/drive/v1/model.go)

接口和本机命令已核对。安装 Skill 不等于完成真实账号的权限、订阅或长连接测试。
