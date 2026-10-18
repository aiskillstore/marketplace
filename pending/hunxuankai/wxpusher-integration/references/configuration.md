# WxPusher Configuration and Secret Handling

本文件说明如何把 WxPusher 配置接入现有项目，不规定某一种语言或配置框架。
先遵循项目已有命名、密钥存储和部署约定；下面的变量名只是可读占位示例。

## 内容

- 配置契约与环境变量
- 本地、容器、CI/CD 和生产环境
- UID/Topic/SPT 表示方式
- 轮换、日志和提交前检查

## 配置契约

至少区分以下概念，不要把它们互相替代：

| 配置 | 用途 | 机密性 |
| --- | --- | --- |
| `WXPUSHER_APP_TOKEN` | 标准推送应用鉴权 | 高度机密 |
| `WXPUSHER_UIDS` | 标准推送接收 UID 集合 | 可能属于个人数据，按项目政策保护 |
| `WXPUSHER_TOPIC_IDS` | 标准推送 Topic ID 集合 | 通常非密钥，但属于路由配置 |
| `WXPUSHER_SPT` / `WXPUSHER_SPT_LIST` | 极简推送 token | 高度机密 |
| `WXPUSHER_CONTENT_TYPE` | 默认格式（1/2/3） | 非机密 |
| `WXPUSHER_TIMEOUT_SECONDS` | 项目 HTTP 超时 | 非机密，服从项目默认值 |

如果项目已有 `NOTIFIER_*`、Vault key、配置中心或 secret object，优先复用
它们，而不是新增同义变量。不要把具体项目的 token、UID、Topic 或服务器地址
写进本 Skill。

## `.env.example`

只提交空值或明显占位符：

```dotenv
WXPUSHER_APP_TOKEN=
WXPUSHER_UIDS=
WXPUSHER_TOPIC_IDS=
WXPUSHER_SPT=
WXPUSHER_SPT_LIST=
WXPUSHER_CONTENT_TYPE=1
WXPUSHER_TIMEOUT_SECONDS=10
```

约定集合的编码方式并在项目文档中写清楚，例如逗号分隔后逐项 trim，或使用
JSON 数组；解析后仍须去重并检查数量上限。空的 UID/Topic 不应被静默当成
“发给所有人”。

## 本地开发

1. 复制 `.env.example` 为被 `.gitignore` 忽略的本地文件（名称服从项目惯例）。
2. 通过项目现有 loader 加载变量，不在源代码常量、测试快照或命令历史中写入
  真实值。
3. 默认只运行 mock HTTP 测试；没有明确授权时不要用本地变量向真实接收者发送。
4. 如果需要演示配置，使用 `AT_example`、`UID_example`、`SPT_example` 等
  明显占位符，并标明不可用。

## Docker / Compose

使用运行时注入，不把 secret 放入镜像层或 Compose 文件的明文提交中：

```yaml
services:
  worker:
    environment:
      WXPUSHER_APP_TOKEN: ${WXPUSHER_APP_TOKEN}
      WXPUSHER_UIDS: ${WXPUSHER_UIDS:-}
      WXPUSHER_TOPIC_IDS: ${WXPUSHER_TOPIC_IDS:-}
```

生产环境优先使用 Docker/Kubernetes secret、外部 secret store 或平台密钥引用；
不要把 `docker inspect`、启动参数和环境转储输出到日志或工单。

## CI/CD

- 将 appToken/SPT 放在 CI 平台的 encrypted secret 中，按环境和最小权限授权。
- 工作流通过受控方式注入 secret；不要 `echo`、调试打印或上传含密钥的 artifact。
  使用官方 GET/query/path 鉴权接口时，不输出完整请求 URL，确保请求日志脱敏。
- Pull request 来自不可信分支时，避免把生产 secret 暴露给其代码；可只运行
  mock 测试，真实部署阶段再由受保护环境注入。
- 在失败摘要中记录 HTTP 状态、业务 code 和脱敏 request ID，不记录 token、UID
  全量或正文中的个人数据。

## 生产与多环境

为 development/staging/production 分别配置 token 和接收目标；不要跨环境复用
生产接收者。配置加载时：

1. 校验 appToken/SPT 非空（若该模式需要）；
2. 校验内容类型、目标数组和 URL/摘要格式；
3. 在启动检查或首次调用前给出可操作的缺失配置错误；
4. 记录“配置已加载”的布尔状态，而不是记录值本身。

将通知失败是否影响主业务作为显式配置/业务决策，不要由 secret 缺失时的
默认分支偷偷改变订单、部署或任务结果。

## 轮换与撤销

- **appToken：** 官方明确支持在管理后台的 appToken 菜单重置，旧值立即失效。
  预先准备配置更新和调用方切换；重置后把新值写入 secret store 并更新所有
  调用方。重置至切换完成之间旧配置会失效，不承诺双 token 并行或无中断轮换。
- **SPT：** 截至 2026-10-08，[官方 SPT 说明](https://wxpusher.zjiecode.com/docs/#/?id=spt)、
  [SPT 专页](https://wxpusher.zjiecode.com/docs/spt.html)及 OpenAPI 未提供重置、撤销
  或轮换方法。不要指示用户去 appToken 菜单重置 SPT，也不要承诺重新扫码会产生
  新值或令旧值失效。文档未记载不等于断言产品内部绝无此能力。
  泄漏时停止继续使用和传播该值、清理可控副本，并通过
  [官方联系方式](https://wxpusher.zjiecode.com/contact.html)核实可用处置方式；
  未取得明确依据前应视为旧值仍可能被使用。清理本地配置不会使远端 SPT 失效。
- 轮换前后检查日志、缓存、CI artifact、容器层和配置备份，删除不必要副本。
- 发生泄漏时按项目 incident 流程处理，并在最终报告中说明是否做过真实发送。

## 提交前检查

- `git diff --check` 检查空白错误和冲突标记；它不检测 secret，凭据需另行扫描；
- `.gitignore` 覆盖本地 env、凭据文件和临时响应；
- 搜索 `AT_`、`SPT_`、真实 UID 形状、`Authorization` 和 webhook secret，逐项
  人工确认只是占位符或安全说明；
- 日志、异常、追踪、截图和测试快照均已脱敏；
- 文档只写变量名和配置位置，不写某个项目的值。
