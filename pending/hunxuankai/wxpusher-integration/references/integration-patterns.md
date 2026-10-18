# WxPusher Integration Patterns

选择与项目现有架构相容的最小模式。不要为一次 HTTP 调用引入新的框架、队列
或数据库；只有实际可靠性、吞吐量或审计需求证明必要时才增加组件。

## 内容

- 模式选择
- 触发点与消息契约
- 失败隔离、重试和幂等
- 测试与交付清单

## 模式选择

| 场景 | 首选形态 | 关键取舍 |
| --- | --- | --- |
| 一次性个人脚本 | SPT POST 或受控的标准 POST | 简单；SPT 必须像密钥一样保护，通常不需要复杂分层。 |
| Web 后端事件 | 现有 NotificationGateway/Service 下的 WxPusher adapter | 复用 HTTP、日志、配置和错误策略；不要把调用散落到控制器。 |
| 定时任务 / cron / Celery / Quartz | 任务完成/失败出口调用 adapter | 为重跑设计幂等键，避免每次重试都重复通知。 |
| 异步队列 | 生产业务事件，消费者发送 | 主业务与推送解耦；记录有限重试和最终失败，不无限堆积。 |
| CI/CD | 工作流末端的独立通知步骤 | Secret 使用受保护环境；通知失败是否阻断流水线要明确。 |
| 监控告警 | 告警聚合器或现有 notifier | 去抖/合并高频事件，遵守 QPS 和单 UID 日用量。 |
| 业务通知 | 领域事件 + 小型通知服务 | 只发送必要字段；订单等主状态通常不因临时推送失败回滚。 |

## 目标与路由

先把通知需求写成可检查的契约：

```text
event:      task.completed | task.failed | order.updated | ...
recipients: UID list, Topic list, or SPT list
format:     text (1), HTML (2), or Markdown (3)
summary:    short, non-sensitive
url:        optional, safe destination
failure:    isolate | fail-primary-action (explicit decision)
retry:      bounded transient-only policy
idempotency: key and deduplication window, if retries/replays are possible
```

UID 表示已知用户的定向/批量发送；Topic 表示订阅者无差别广播；两者可按官方
POST 接口组合；标准 GET 只能选一个 UID 或一个 Topic。不要把 Topic 当作可逐
用户定制的目标，也不要在缺少目标时默认广播。

## 实现边界

1. 在项目已有配置层读取 token 和目标列表，启动时校验必需值与数量。
2. 通过项目已有 HTTP client 发起标准 POST；若确实是简单自推才选 SPT。
3. 将请求构造、响应解析和错误分类封装在一个小 adapter/service 中；业务层
   只调用稳定的项目接口，例如 `notify(event)`。
4. 为每次调用设置明确 timeout。复用现有 retry/backoff；没有现成策略时，
   采用有限次数、指数或固定退避并设置上限，具体数值由项目 SLO 决定。
5. 只有网络错误、429、5xx 等瞬时故障才重试；token/权限/参数/业务校验失败
   应立即报告，不应重试。
6. 记录脱敏的事件、目标类型（不要全量 UID）、HTTP 状态、业务 code、
   sendRecordId（若允许）和最终结果。不要记录 token、SPT 或完整正文。

## 主业务解耦

默认把推送视为旁路副作用：

- 订单已提交、数据已落库、部署已完成后再发送；
- 临时 WxPusher 故障记录并告警，但不回滚已成功的主业务；
- 如果用户明确要求“通知失败即任务失败”，把它写成显式策略并测试；
- 异步队列消费者要有最大重试、死信/人工处理和过期策略。

## 重复与幂等

重试、支付回调、Webhook、MQ 和定时任务都可能重复触发。先判断重复通知的
实际影响，再选择方案：

- 无害低频告警：可接受重复，但在正文中带事件时间/运行 ID；
- 高影响业务：使用现有幂等键、去重缓存或事件状态，不要无条件新增数据库表；
- Topic 群发：确认一次事件不会同时经多个 Topic 重复到达同一用户；
- 发送接口成功是“任务创建”，不是用户阅读确认，状态查询不能替代业务幂等。

## 内容设计

建议正文包含事件、状态、项目/服务、时间、关键对象、短错误摘要和必要链接。
异常内容只保留可行动信息；对堆栈、请求体、环境变量和个人数据做筛选/截断。

```text
【数据同步完成】
项目：<project-name>
状态：成功
新增：<count>
耗时：<seconds> 秒
详情：<safe-url>
```

尖括号字段是模板占位符，发送前必须替换为非敏感值或省略，不要把此示例当作
真实配置。

## 测试策略

至少覆盖：

- 构造正确的 UID/Topic/SPT 请求与 contentType；
- 顶层 `code=1000`、目标级失败和缺失目标；
- HTTP 非 2xx、HTTP 200 但业务失败、非 JSON、连接异常和 timeout；
- 429/5xx 的有限重试与退避，认证/参数错误不重试；
- 配置缺失、数组去重/上限、摘要/URL/正文长度及正文 UTF-8 字节限制；
- 中文未超字符数但超字节数、原文合格但服务端转换后超限并返回 `1001`；
- HTML/Markdown 转义，正文脱敏，日志不泄漏 secret；
- 重复事件/重跑的幂等策略；
- 回调未知 action 和重复回调（如项目启用回调）。

使用 mock HTTP 或本地假服务验证；未经明确授权，不以“测试”名义调用真实
WxPusher。

## 交付清单

- 修改点集中在通知边界，未进行无关重构；
- `.env.example`/部署说明只含空值或占位符；
- 测试命令和结果可复现；
- 报告目标配置、触发点、失败语义、重试上限和是否真实发送；
- 若发现官方行为与 reference 不同，先报告 drift，不在普通项目任务中静默改全局 Skill。
