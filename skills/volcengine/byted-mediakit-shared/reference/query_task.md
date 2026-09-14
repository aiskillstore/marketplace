# 异步任务查询

## 能力用途

查询异步任务状态与结果

## 参数填写规则

- task_id 必须来自真实异步任务受理结果；可选轮询参数仅在用户明确指定，或可从用户意图准确确定时填写，不得伪造。
- `max_poll_timeout_seconds` 默认 `0` 表示不限制；仅在用户明确需要限制单次轮询总时长时填写。`poll_interval_seconds × max_poll_attempts` 不得超过该上限。

## Cloud

### 命令与生命周期

- 命令：`mediakit-cli shared query-task`
- 生命周期：同步
- 返回方式：直接返回 Cloud 业务结果。

### 使用指南

- 布尔参数（`--poll-complete`）只能写成 `--poll-complete=true` 或 `--poll-complete=false`，也可用裸 `--poll-complete`（等价 true）；禁止空格传值 `--poll-complete true`，否则该值会被当作位置参数。
- 布尔参数取默认值时直接省略，不要显式重复默认值。

### 调用示例

```bash
mediakit-cli shared query-task \
  --task-id <task_id>
```

仅使用用户真实输入替换占位符；可选 flag 遵守参数填写规则，不得编造 URL、文件、枚举或业务参数。

### 参数

| 参数路径 | CLI flag | 类型 | 必填 | 默认值 | 枚举/范围/结构 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| `max_poll_attempts` | `--max-poll-attempts` | integer | 否 | 0 | 最小值: 0 | 最多轮询次数；0 表示只查询一次。与 `poll_interval_seconds` 的乘积不得超过 `max_poll_timeout_seconds`。 |
| `poll_complete` | `--poll-complete` | boolean | 否 | false | - | 是否持续轮询直到任务进入终态。 |
| `poll_interval_seconds` | `--poll-interval-seconds` | number | 否 | 10 | 大于: 0 | 轮询间隔，单位为秒；必须大于 0，仅在持续轮询时使用。 |
| `max_poll_timeout_seconds` | `--max-poll-timeout-seconds` | number | 否 | 0 | 最小值: 0 | 轮询总时长上限，单位为秒；0 表示不限制。 |
| `task_id` | `--task-id` | string | 是 | - | - | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |

### 返回结果

| 字段路径 | 类型 | 必含 | 模式 | 说明 |
| --- | --- | --- | --- | --- |
| `error` | any | 否 | Cloud | 失败终态的原始错误内容；仅在实际失败且后端返回时出现。 |
| `request_id` | string | 否 | Cloud | 请求标识；仅在后端实际返回非空值时出现。 |
| `status` | string | 否 | Cloud | 任务状态；completed 为成功终态，failed、canceled 或 cancelled 为失败终态。 |
| `success` | boolean | 否 | Cloud | 失败终态返回 false；其他状态仅在后端实际返回时出现。 |
| `task_id` | string | 否 | Cloud | 异步任务的唯一标识，用于查询任务状态并获取最终结果。 |
| `task_type` | string | 否 | Cloud | 任务类型；仅在后端实际返回非空值时出现。 |
| `usage` | object | 否 | Cloud | 可选顶层返回字段。仅对已开放该字段的账号，在 Cloud 同步调用成功，或 query_task 查询到 completed 终态，且服务实际产生并返回正向计费用量时透传；其他状态、异步提交及 Local 调用不返回。 |
| `usage.normalized_usage` | number | 是 | Cloud | 归一化后的计费用量。由服务端按 BillingCount / 固定单位换算值 × list_price 计算，结果保留 6 位小数；客户端只校验并原样透传，不计算、推断或补齐。 |

### 机器合同

以下命令只读取本模式的实时 help/schema，不发起业务调用：

```bash
mediakit-cli shared query-task --help
mediakit-cli shared query-task --schema
```
