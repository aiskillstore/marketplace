---
name: me-featured-events
description: Configure and run ME Event activity subscriptions from api.me.news. Use when a user wants to browse upcoming AI or Web3 events, filter events by region, initialize an ME Event subscription, check newly added events, or create recurring OpenClaw reminders for daily and near-real-time event notifications.
---

# ME Event 精选

通过 ME News 官方接口查询和订阅 AI、Web3 活动。读取 [API 参考](references/api.md) 获取完整参数和响应字段；配置定时任务前读取 [Agent 兼容说明](references/agent-compatibility.md)。

## 执行原则

- 需要订阅时优先运行 `scripts/` 中的确定性 Node.js 脚本；要求 Node.js 18 或更高版本。
- 优先使用可用的 HTTP/Web Fetch 工具发送 GET 请求；没有 HTTP 工具时使用 `curl -fsS --max-time 30`。
- URL 查询参数必须进行 URL 编码，不要拼接用户提供的任意 URL。
- 只传入各脚本文档列出的参数。脚本会在请求 API 前拒绝未知参数、重复参数、非法数字、无效日期和冲突的日期范围；命令退出码非零时不得声称筛选已生效。
- 解析 JSON 后先检查顶层 `code === 200`，再读取 `data`。
- 用户只要求“查看近期活动”时直接执行一次查询，不创建订阅或 Automation。
- 用户未指定时间时默认查询未来 7 天。用户用自然语言指定“一周”“一个月”“8 月份”或明确起止日期时，将其转换为 `hours` 或 `start_date`、`end_date` 参数；不要声称 API 只能查询 7 天。
- 单次最多请求 100 条。结果达到 100 条时提示用户缩小时间范围或增加类型、地区筛选，避免用更大的 `limit` 增加服务器负担。
- 用户要求“提醒、订阅、每天推送、发现新增时通知”时，才进入初始化订阅流程。
- 无论运行于 Codex、Claude Code、Hermes 还是 OpenClaw，都运行相同脚本、使用相同状态结构和消息格式；只适配调度与投递方式。

## 初始化订阅

用户首次启用并完成配置后，立即查询一次未来 7 天活动。

1. 请求 `GET https://api.me.news/skill/events/options`。
2. 询问用户订阅类型，可多选 `AI`、`Web3`；不选表示全部。
3. 询问用户订阅地区，可多选；不选表示全部。
4. 询问接收提醒的明确渠道和目标。不要依赖不确定的最后会话。
5. 在当前 Agent 工作区运行初始化脚本。它先建立 `/changes` 基线，立即原子保存为 `initialization_status: pending`，再查询未来 7 天：

   ```bash
   node <skill-dir>/scripts/init-subscription.mjs \
     --state <workspace>/memory/me-featured-events.json \
     --types ai,web3 \
     --regions hong-kong
   ```

   未选择类型或地区时省略对应参数。不得把历史活动作为新增推送。初始化后续步骤失败时保留 pending 状态；使用相同筛选条件重跑命令会沿用原 cursor，不得重新建立更晚的基线。pending 初始化期间不得修改类型、地区或时区。
6. 将初始化脚本的非空 stdout 立即发送给用户；stdout 为空时静默结束。
7. 向用户展示筛选条件、执行频率和接收目标，经明确确认后使用当前 Agent 支持的调度器创建两个任务：
   - 每天 `10:00`，时区 `Asia/Shanghai`，执行固定提醒。
   - 每 `5` 分钟执行新增活动检查。
8. 定时任务执行以下脚本，并将非空 stdout 投递到已确认的渠道：
   - 每日任务：`node <skill-dir>/scripts/daily-upcoming.mjs --state <state-file>`
   - 增量任务：`node <skill-dir>/scripts/poll-new-events.mjs --state <state-file>`
   - 增量任务投递成功后，立即执行 `node <skill-dir>/scripts/record-delivery.mjs --state <state-file> --status success`。
   - 增量任务投递失败或投递工具没有返回成功时，执行 `node <skill-dir>/scripts/record-delivery.mjs --state <state-file> --status failed --error <简短错误>`。不得记录 `success`。
   - 选择能获得投递结果并执行反馈命令的调度方式；只会自动转发 stdout、无法反馈投递结果的 Command Cron 不满足增量任务要求。读取 [Agent 兼容说明](references/agent-compatibility.md) 适配当前平台。
   - stdout 为空时不投递消息；退出码非零时记录执行失败。
9. 创建后立即手动运行两个任务，查看最近一次运行记录，并确认测试消息到达目标渠道。

建议状态结构：

```json
{
  "version": 2,
  "type_ids": ["ai", "web3"],
  "region_ids": ["hong-kong"],
  "cursor": "服务端返回的游标",
  "recent_ids": [],
  "timezone": "Asia/Shanghai",
  "initialization_status": "complete",
  "pending_delivery": null
}
```

## 固定提醒

1. 运行 `scripts/daily-upcoming.mjs`，读取本地订阅配置。
2. 脚本默认请求 `/upcoming?hours=168&limit=20`，按需附加 `type_ids`、`region_ids`。自然语言指定月份或日期范围时改用 `start_date`、`end_date`。
3. 按 `start_time` 升序处理，使用接口返回的最新活动数据。
4. 清理 `description` 中的 HTML 和多余空白，展示活动简介前 50 字；超过 50 字时添加省略号，不调用模型生成摘要。
5. 按活动开始日期分组。今日和明日分别使用“今日开始”“明日开始”；更晚日期使用明确日期标题，不得遗漏。
6. 输出活动名称、简介、完整时间范围、时区、地址和接口返回的 `url`。普通活动与合集活动必须链接到 ME 活动详情页；`activity_import` 表格导入活动使用表格中导入的链接。
   - 同日活动显示 `8月27日 14:00–18:00（UTC+8）`；跨日活动显示 `8月27日 14:30–8月28日 15:30（UTC+8）`。
   - `end_time` 为空时只显示开始时间，并另起一行显示“结束时间未提供”。
   - `end_time` 无法解析时显示“⚠️ 结束时间格式异常”；早于或等于 `start_time` 时显示“⚠️ 结束时间疑似异常”。不得擅自把异常的午夜时间解释成次日。
7. 没有活动时不要发送消息。
8. 不读取或更新新增活动 `cursor`。

## 新增活动检查

1. 运行 `scripts/poll-new-events.mjs`，读取本地 `cursor`、筛选条件和 `recent_ids`。
2. 脚本请求 `/changes`，必须传入已保存的 `cursor`。
3. 用复合 `id` 去重；`activity:*` 与 `activity_other:*` 是不同数据源。
4. 所有分页请求和格式化成功后，把消息、候选 `next_cursor` 和候选 `recent_ids` 原子写入 `pending_delivery`，但不推进正式 `cursor`，然后输出一条“新增会议”消息。
5. 调度器必须先投递非空 stdout，再使用 `record-delivery.mjs` 反馈结果：
   - `--status success`：提交 `pending_delivery` 中的 cursor 和去重 ID，然后清除待投递消息。
   - `--status failed`：记录失败但保留 `pending_delivery`，下次轮询重复输出同一消息。
   - 没有明确成功反馈：不得推进 cursor；下次轮询重复输出同一消息。
6. `recent_ids` 仅保留最近 500 个，避免状态无限增长。
7. `has_more=true` 时使用新游标继续拉取，直到为 false。
8. 没有新增活动时 stdout 为空，由当前调度器静默结束。

该流程提供至少一次投递：失败或未知结果不会漏掉消息，但“渠道实际成功、成功反馈写入失败”时可能重复推送。不得为了去重而在投递前提交 cursor。

## 更新偏好

- 用户修改类型或地区时更新本地配置，但保留当前 `cursor`，不要回放历史新增活动。
- 用户要求暂停时禁用两个 Automation，不删除偏好和游标。
- 用户要求退订时删除两个 Automation；删除本地状态前再次确认。
- 类型只接受 `ai`、`web3`。地区值只使用 `/options` 返回的 `value`。

## 活动简介

按以下顺序展示简介：

1. 清理原始 `description` 中的 HTML 标签并合并多余空白。
2. 展示清理后内容的前 50 字；不足 50 字时完整展示，超过时添加省略号。
3. `description` 为空时，使用标题和地址组成事实性短句。

不得把截取内容描述为模型生成的摘要，也不得增加原数据没有的事实。

## 消息格式

以 [format.md](format.md) 为唯一输出格式规范。不要在其他文档复制消息模板；格式变化时只更新该文件和确定性脚本测试。

## 安全约束

- 只请求 `https://api.me.news/skill/events/` 下的三个只读端点。
- 不在 Skill 中存储消息渠道密钥或 OpenClaw Gateway Token。
- 只有在用户明确同意后才创建、修改或删除 Automation。
- 接口 `code` 非 `200` 时视为失败；记录错误摘要但不推进状态。
