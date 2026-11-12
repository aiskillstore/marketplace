# WxPusher API Reference

本文件是项目集成所需的精简事实基线，不是官网镜像。2026-11-12 重新核对官方
正文、SPT 专页、API Reference 和 OpenAPI 中的 SPT 请求、发送响应及旧状态
查询停用说明；其余内容和固定版本 SDK 仍以 2026-10-08 核验为基线。SPT GET
斜杠限制另依据此前实测摘要及用户转述的官方人工答复，公开文档尚未明示该限制。
核验范围和各类证据见 [maintenance.md](maintenance.md)。线上策略可能变化，疑似漂移
时按其中的维护流程复核。

## 内容

- 接收渠道与微信支持
- 标准推送：请求、响应、UID/Topic、旧查询停用和删除
- SPT 极简推送
- 用户、二维码和回调
- 限制、错误和安全边界
- 未确认或易变行为

## 接收渠道与微信支持

截至 2026-10-08，[官方正文](https://wxpusher.zjiecode.com/docs/README.md)的
“介绍”和“微信 ClawBot（iLink）推送渠道”明确说明：当前主推独立全平台客户端，
同时支持通过微信 ClawBot 向已绑定用户发送**文本通知**。

| 接收方式 | 官方说明与接入前提 |
| --- | --- |
| 独立客户端 | Android、iOS、鸿蒙、macOS、Windows、Linux；按客户端要求登录并启用通知。 |
| 微信 ClawBot（iLink） | 在 WxPusher App 的“我的 → 推送渠道 → 绑定微信 ClawBot”完成绑定并启用；还需在微信侧激活该渠道。当前只支持发送通知，暂不支持上行消息。 |

开发者仍使用既有发送接口，appToken、UID、Topic、SPT 的推送模型不变；是否
通过 iLink 接收由用户的绑定和启用状态决定。不要添加未公开的 `channel=wechat`
参数，也不要把 UID 当作微信号、好友 ID 或微信群 ID。官方所列发送接口未提供
向任意微信好友或微信群寻址的能力。标准模式还需要用户关注相应应用或订阅 Topic；
SPT 则使用对应接收人的 SPT，不能与标准身份混用。

微信侧每次激活后，24 小时内通过该渠道最多接收 10 条；用尽后需用户向 ClawBot
回复任意内容再次激活。此限制独立于 API QPS、批量目标数和客户端日用量；
改用 Topic、SPT 或重试不能据此宣称绕过渠道限制。激活回复不代表应用能收到
`send_up_cmd` 回调，不能把标准应用的上行能力套用于 ClawBot。

官方仍保留通过公众号获取 UID、关注和指令回调的说明，但介绍已将公众号称为
早期主要渠道。不能据此承诺“关注公众号就能稳定收到全部通知”，也不能反向
断言公众号相关功能已全部停用；需要判断具体账号可用性时，以当前客户端及官方说明为准。

## 1. 标准推送

### 发送端点

```text
POST https://wxpusher.zjiecode.com/api/send/message
Content-Type: application/json
```

`appToken` 放在 JSON body 中，不使用 `Authorization` 头。请求必须包含
`appToken`、非空 `content`，并至少提供 `uids` 或 `topicIds` 之一。两者可以
同时提供；服务会为每个目标建立发送记录。

示例中的值均为占位符，不能替换真实密钥：

```json
{
  "appToken": "AT_example",
  "content": "任务完成：没有敏感数据",
  "summary": "任务完成",
  "contentType": 1,
  "uids": ["UID_example"],
  "topicIds": [123456],
  "url": "https://example.invalid/result"
}
```

### 字段

| 字段 | 类型/必需性 | 当前官方事实 |
| --- | --- | --- |
| `appToken` | string，必需 | 应用鉴权密钥；官方 OpenAPI 约束前缀 `AT_`。 |
| `content` | string，必需 | 正文；长度 1–40000 字符，且原文及服务端清理、转换后的 HTML 各不超过 65535 个 UTF-8 字节。 |
| `contentType` | integer，可选 | `1` 纯文本（默认）、`2` HTML、`3` Markdown。 |
| `summary` | string，可选 | 摘要，接口上限 100 字符；未传时由服务截取正文，各端可能更短。 |
| `url` | string，可选 | 原文链接，接口上限 1000 字符。 |
| `uids` | string array，条件必需 | UID 单发或批量；单次最多 2000 个，官方 schema 标记唯一。 |
| `topicIds` | integer array，条件必需 | Topic 群发；单次最多 5 个，官方 schema 标记唯一。 |
| `verifyPayType` | integer，可选 | `0` 不验证、`1` 仅付费订阅期内、`2` 仅未订阅或已过期；没有关联消息产品时无效。 |
| `verifyPay` | boolean，旧字段 | 官方正文标为即将废弃；传 `verifyPayType` 时忽略它，新的集成不要使用。 |

字符数和字节数须分别检查：例如 30000 个普通汉字约为 90000 个 UTF-8 字节，
虽未达到字符上限，仍不能发送。原文可用 `new TextEncoder().encode(content).length`
检查；原文合格不保证转换后的 HTML 合格，Markdown、标签、换行和特殊字符
可能扩大体积。服务端超限返回业务码 `1001`，不创建发送任务；应缩短或分段，
保留格式完整性，不对同一超长正文原样重试。此规则同样适用于 SPT。

HTML 正文应提供 body 内片段而不是 `body` 标签本身。官方正文还记录了
`<copy data-clipboard-text="...">...</copy>` 复制标签；只有确实需要且目标
客户端支持时才使用，并对动态值做转义。Markdown 的具体渲染以客户端为准，
不要把 HTML 语法假定为 Markdown 能力。

### 响应与成功判断

典型响应形状如下（示例 ID 是占位符）：

```json
{
  "code": 1000,
  "msg": "处理成功",
  "data": [
    {
      "uid": "UID_example",
      "topicId": null,
      "messageContentId": 123456789,
      "code": 1000,
      "status": "创建发送任务成功"
    }
  ],
  "success": true
}
```

- HTTP 2xx、可解析的 JSON 和顶层业务 `code == 1000` 是成功的必要条件；
  HTTP 200 本身不够，顶层失败时即使有 `success: true` 也不能报告成功。
- `data` 通常按 UID/Topic 返回目标结果；目标结果也有自己的 `code` 和
  `status`；存在目标级失败时不能报告全部成功，应报告失败或部分失败。
- `messageContentId` 是本次发送共享的落地页内容 ID，可用于删除落地页。
- `messageId` 在官方正文中已标记废弃，不要依赖。
- 接口是异步分发；成功只表示任务已创建，不保证用户已经看到通知。
- 客户端应同时处理 HTTP 非成功状态、网络/超时、非 JSON 响应、顶层业务
  失败和目标级失败，并避免把完整响应中的敏感字段写入日志。

### 旧发送状态查询已停用

```text
GET /api/send/query/status
GET /api/send/query/{messageId}
```

2026-11-12 核对的官方正文和 OpenAPI 明确：这两个旧地址仅保留停用响应，
不再查询状态，应停止调用或轮询。`sendRecordId`、`messageId` 参数会被忽略，
返回业务码 `1001` 及停用提示。该提示不表示消息发送失败，不能据此自动重发。
发送是否被接受以发送接口的顶层和逐目标业务码判断；用户实际接收仍需另行确认。

### 删除消息落地页

```text
DELETE https://wxpusher.zjiecode.com/api/send/message
  ?messageContentId=<id>&appToken=<app-token>
```

删除的是用户点击详情时查看的落地页内容，已经到达通知栏/消息列表的记录
不能撤回。多个目标共享一个 `messageContentId`，删除会影响本次发送的所有
目标。DELETE 查询参数中的 token 可能出现在代理日志，能用 POST 的场景不要
把密钥放 URL；若官方接口要求 query 参数，至少确保日志脱敏。

## 2. GET 便捷发送

同一路径也支持：

```text
GET https://wxpusher.zjiecode.com/api/send/message/
  ?appToken=<app-token>&uid=<uid>&content=<url-encoded-text>
```

当前官方 OpenAPI/正文描述它是受限接口：只支持纯文本、一次只能选一个 UID
或一个 Topic，`content`/`url` 必须 URL 编码；可传 `summary`、`url`、
`verifyPayType`。其中 `summary` 由 OpenAPI 列出，README 的 GET 参数列表未列出；
依赖摘要的流程优先 POST。业务集成优先使用 JSON POST，减少 query/path 暴露。

## 3. SPT 极简推送

SPT（Simple Push Token）与标准应用的 appToken/UID/Topic 身份体系不互通，
适合发送者和接收者是同一人或少量已知接收者的简单脚本。SPT 泄漏后，任何
持有者都可能向该 token 的接收者发送消息。

官方说明通过 [SPT 二维码](https://wxpusher.zjiecode.com/docs/#/?id=spt) 获取
SPT，但截至核验日未在公开文档中找到 SPT 重置、撤销或轮换方法。重新扫码是否
返回新值、旧值是否失效也未说明；不能把“重新获取”当作撤销旧值的办法。
appToken 的后台重置仅适用于标准推送，不适用于 SPT。泄漏处置见
[configuration.md](configuration.md#轮换与撤销)。

### POST（SPT 默认方式）

```text
POST https://wxpusher.zjiecode.com/api/send/message/simple-push
Content-Type: application/json
```

单人请求使用已有的 `spt`、原始 `content` 和 `contentType`（纯文本为 `1`），
无需 appToken 或 UID。`content` 保留中文、换行、`/context`、`https://...` 和
百分号等原文，通过 JSON 序列化后以 UTF-8 发送；不做 URL 百分号编码，也不
替换正文字符。JSON 对引号、反斜杠、换行的转义在解析后还原原文，不是 URL 编码。

Body 还可复用 `summary`、`url`，并提供 `spt`（单个）
或 `sptList`（数组，最多 10 个，唯一）。按场景选一个目标字段；官方未说明同时
传入两者时的合并或优先级，不能把此建议称为服务端强制互斥。OpenAPI 因继承
公共模型而包含 `verifyPayType`，但 SPT 正文未说明付费筛选能力，不据此实现或承诺。
示例：

```json
{
  "content": "请执行 /context，查看 https://example.invalid/a/b?next=1#frag，百分号 100%。\n保留原文。",
  "contentType": 1,
  "spt": "SPT_example"
}
```

### GET（受限便捷接口）

```text
GET https://wxpusher.zjiecode.com/api/send/message/<spt>/<url-encoded-content>
```

公开文档仍列出 SPT GET；整个 GET 发送接口没有被宣称停用。但正文含 `/`
（例如 `/context` 或正文中的 `https://...`）、路径段编码后出现 `%2F` 时，
当前应改用上述 SPT JSON POST，保留原始正文和已有 SPT。不要尝试双重编码
（如 `%252F`）、替换斜杠或反复重试来规避限制，也不能据此要求更换 appToken/UID。

**编码规则与服务端支持范围须分开判断：** 路径段的正确编码规则是将 SPT 和
原始正文分别做一次 UTF-8 URL 百分号编码；`/` 的编码确实是 `%2F`，但当前
SPT GET 不接受正文中的这种编码斜杠。编码正确并不保证请求能通过路由或网关。
对不含斜杠、适合 GET 的正文（如 `任务完成 100%`），仍须编码中文、空格、
`?`、`#`、`%`、换行等特殊字符，不编码整条 URL，不重复编码。
需要摘要、独立的 `url` 字段或多个接收者时也使用 POST。凭据和正文均须脱敏。

**限制依据：** 此前使用明确无效的测试 SPT，GET 正文 `a%2Fb` 返回 HTTP 400
HTML，正文 `ab` 返回 HTTP 200、JSON 业务码 `1001`；原正文改用 SPT POST 后
可以进入业务校验。这些结果证明请求处理路径不同，不能证明发送成功。
2026-11-12 用户另转述官方人工答复：SPT GET 暂不支持正文包含编码斜杠的情况，
要求使用 POST。该答复无公开链接或原始客服记录；公开文档仍给出一般 URL
编码要求，尚未描述此限制。证据类型、时间边界见
[核验来源](maintenance.md#核验来源)。本次维护未重放线上发送测试。

## 4. 用户、Topic 和二维码

### Topic 语义

Topic 是应用下的订阅集合，向 Topic 发送是无差别群发；不能用 Topic 做
针对单个订阅者的定制消息，Topic 订阅本身没有用户 UID 回调。标准 POST
请求可以同时含 UID 和 Topic，标准 GET 只能选一个 UID 或一个 Topic。
当前官方公开资料说明 Topic 的创建/订阅通过管理
后台与二维码/链接完成，但本次核验的 OpenAPI 未提供 Topic CRUD 端点；不要
凭经验臆造管理 API。需要管理 Topic 时应使用官方后台或重新核对官方资料。

### 用户列表 V2

官方正文记录：

```text
GET https://wxpusher.zjiecode.com/api/fun/wxuser/v2
```

查询参数为 `appToken`、`page`、`pageSize`（不超过 100），以及可选 `uid`、
`isBlock`、`type`（`0` 应用、`1` Topic）。同一用户若关注应用及其多个 Topic，
会返回多条记录；不要据此假定单个 appToken 可跨应用查询。返回记录包含 `uid`、`appOrTopicId`、`id`、`type`、`reject`
和 `payEndTime` 等字段；新用户的头像/昵称可能为空。

配套用户操作（均以 query 参数鉴权）为：

| 操作 | 方法与端点 | 语义 |
| --- | --- | --- |
| 删除关注 | `DELETE /api/fun/remove` | 删除应用/Topic 关注，用户仍可重新关注。 |
| 拉黑/取消拉黑 | `PUT /api/fun/reject` | `reject=true` 后不能发送或再次关注，直到取消拉黑。 |

这些操作需要用户列表返回的内部 `id`，不要把 UID 当作该参数。

### 参数二维码

创建：

```text
POST https://wxpusher.zjiecode.com/api/fun/create/qrcode
```

Body 需要 `appToken`、`extra`（1–64 字符），可选 `validTime`（秒，最小 1，默认 1800，
最大 2592000，即 30 天）。扫码后可通过回调拿 UID，或查询：

```text
GET https://wxpusher.zjiecode.com/api/fun/scan-qrcode-uid?code=<code>
```

官方 README/OpenAPI 当前列出查询参数 `code`，并要求轮询间隔至少 10 秒、
用户退出后停止轮询。某个官方 Java SDK 版本还在该请求中附加 appToken；这与
当前公开 schema 不一致，属于待复核事项，不要盲目复制 SDK 参数。

## 5. 回调

只有标准推送支持回调；微信 ClawBot 渠道当前不支持上行消息，不能用其激活回复
实现应用指令回调。创建应用时可配置回调地址；不配置则不会收到关注
回调，Topic 订阅也不会给应用用户 UID 回调。官方正文给出三类 action：

| `action` | 用途 | 关键 `data` 字段 |
| --- | --- | --- |
| `app_subscribe` | 用户关注应用 | `appId`、`source`、`uid`、`extra`、`time` |
| `order_pay` | 消息产品付费/退款 | `uid`、`appId`、`prodId`、`type`、`amount`、`addTime`、`tradeNo` |
| `send_up_cmd` | 用户发送上行指令 | `uid`、`appId`、`content`、`time` |

回调处理应：

1. 按 `action` 分派并对未知 action 保持兼容；
2. 使用 HTTPS、公网可达的接收端，校验 JSON 结构并做幂等/去重；
3. 不把回调中的完整请求或个人数据直接转发到通知正文；
4. 官方资料没有为这些回调定义通用签名字段，不能臆造签名校验方式；如需
   来源认证，应在项目边界增加自己的共享密钥、网络限制或其他可验证机制，
   并在维护时复核官方是否新增签名。

这里的 Webhook 回调与“系统对接”的浏览器跳转链接不同：官方已为后者定义
基于可选验证密钥的 HMAC-SHA256 签名，包含 `uid`、`ts`、`nonce`、`sv`、`sign`。
需要实现跳转验签时读取 [系统对接说明](https://wxpusher.zjiecode.com/docs/#/?id=setting-url-sign)，
不要将“未定义通用回调签名”理解为整个平台没有签名功能。

## 6. 限制与错误

### 当前公开限制

以下数值于 2026-10-08 核对官方正文/OpenAPI；带“约”的是运营策略，不应当作
永久 SLA：

| 项目 | 限制/含义 |
| --- | --- |
| `content` | ≤ 40000 字符；原文及服务端转换后的 HTML 各 ≤ 65535 个 UTF-8 字节；超限返回 `1001` |
| `summary` | ≤ 100 字符；客户端展示可能更短 |
| `url` | ≤ 1000 字符 |
| 单次 `uids` | ≤ 2000 |
| 单次 `topicIds` | ≤ 5 |
| 发送频率 | 默认约每 10 秒 20 次（约 2 QPS），部分应用可申请更高配额 |
| 消息数据保留 | 通常 7 天，过期后不保证可用；旧发送状态查询已经停用 |
| 单 UID 客户端日用量 | 约 3000 条后可能不再弹通知栏，约 20000 条后可能停止展示；次日恢复，线上阈值以实际策略为准 |
| 微信 ClawBot 渠道 | 用户激活后 24 小时内该渠道最多 10 条；用尽后向 ClawBot 回复任意内容可再次激活，与 API 级 QPS/批量限制独立 |

请求目标超限时分批；请求频率过高时退避、合并或使用 Topic 群发减少调用数。
客户端日用量和 ClawBot 渠道限制需分别处理，不能通过上述方式保证解除；不要无限重试。
HTTP `429`/`5xx` 的处理属于客户端工程策略；当前文档未承诺所有限流或服务
故障都使用这些 HTTP 状态。收到时按项目策略有限退避，同时检查业务响应，
不能把它们当作业务成功。

### 业务 code

当前官方 OpenAPI 明确：

| code | 当前定义 |
| --- | --- |
| `1000` | 成功 |
| `1001` | 通用业务错误 |
| `1002` | 未登录 |

官方 Java SDK（commit `b98d378e5e6f70d448c8887356165047a0274849`）的客户端枚举
将 `1002` 注释为“未认证”，还定义了
`1003` 签名错误、`1004` 接口不存在、`1005` 服务端内部错误、`1006` 与微信
交互异常、`1007` 网络异常、`1008` 数据异常、`1009` 未知异常。它们没有在
当前 OpenAPI 的 Result 描述中逐项列出，故只能作为兼容性线索；客户端应对
所有非 1000 code 做可诊断的通用失败处理，而不是依赖这份枚举穷举。

## 7. 安全边界

- appToken、SPT、系统对接验证密钥都是秘密；使用环境变量、密钥管理服务、
  CI/CD secret、容器 secret 或项目既有配置中心。
- 只在 `.env.example` 写空值或明显占位符。不要提交真实 token、UID、Topic
  接收人、Cookie、Authorization、回调密钥或业务正文。
- 优先 POST，避免 GET 的 query/path 把正文或 token 写入浏览器、代理和访问
  日志；无论方法如何都要脱敏日志。
- 通知正文只含必要事件、状态、时间、对象、短错误摘要和必要链接；不发送
  密码、token、Cookie、完整请求体或不必要个人数据。
- 创建/开发验证默认只用 mock；真实测试遵循已有明确授权的范围。正式运行
  通知按用户已授权的用途、对象和频率执行，仍适用的长期授权无需重复确认。

## 官方来源

- [官方文档入口](https://wxpusher.zjiecode.com/docs/)
- [官方正文（含微信 ClawBot/iLink 渠道说明）](https://wxpusher.zjiecode.com/docs/README.md)
- [SPT 获取与发送](https://wxpusher.zjiecode.com/docs/#/?id=spt)
- [SPT 专页](https://wxpusher.zjiecode.com/docs/spt.html)
- [正文与字节限制](https://wxpusher.zjiecode.com/docs/#/?id=limit)
- [官方 API Reference](https://wxpusher.zjiecode.com/docs/api-reference.html)
- [官方 OpenAPI](https://wxpusher.zjiecode.com/docs/openapi.yaml)
- [官方文档仓库](https://github.com/wxpusher/wxpusher-docs)
- [官方 Java SDK（错误枚举线索）](https://github.com/wxpusher/wxpusher-sdk-java)
