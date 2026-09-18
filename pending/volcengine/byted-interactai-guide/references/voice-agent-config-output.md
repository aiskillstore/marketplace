# Voice Agent 配置投影与输出

**Domain**: voice-agent

## Target

先生成并验证同一份 StartVoiceChat 核心 `{AgentConfig,Config}`，再按 target 投影。投影过程无需
读取 AibotCreate/AibotUpdate 文档。

- `start-voice-chat`：输出核心 `{AgentConfig,Config}`；API 版本 `2025-06-01`。运行时 AppId、
  RoomId、TaskId、TargetUserId 不属于核心。
- `aibot-create`：把核心直接映射为 `{Name,AccessType,AgentConfig,Config}`；API 版本
  `2025-08-01`。Name 必须来自用户或明确场景名。
- `aibot-update`：把核心映射到刚读取的完整 Aibot 基线，再输出 RFC 7396 JSON Merge Patch；
  API 版本 `2025-08-01`。没有基线时返回 `BASE_CONFIG_REQUIRED`。

Merge Patch 对象递归保留变化分支，数组整体替换，相同值省略，明确删除使用 `null`。不得写入
Id、时间戳、服务端只读字段、凭据或 `[REDACTED]`。

## Envelope

配置生成、修改或校验返回：

```json
{
  "target": "aibot-update",
  "apiVersion": "2025-08-01",
  "valid": true,
  "preview": {"config": null, "patch": {}},
  "config": null,
  "patch": {},
  "executable": true,
  "changedPaths": [],
  "errors": [],
  "questions": [],
  "sources": [],
  "validationSources": []
}
```

`valid=true` 表示当前证据已验证；`false` 表示结构、安全检查、服务端响应或匹配的官方正文给出
确定错误；`null` 表示需要澄清或动态证据不足。`preview` 可在 `valid=null` 时保留结构正确的候选
结果，此时 `config/patch=null` 且 `executable=false`。可执行 config/patch 要求 `valid=true`。

输出前执行证据门禁：核心 `changedPaths` 必须与证据账本中 StartVoiceChat 当前版本且状态为
`supported-current` 的路径集合完全相等，账本中不能出现 `conflict` 或 `unknown`。Aibot target
增加投影元数据，核心证据 scope 保持不变。任一条件不满足时，固定返回 `valid=null`、
`config/patch=null`、`executable=false`。证据冲突表示当前无法判断，不能据此认定目标值非法。

语义不唯一时返回一个 `AMBIGUOUS_CONFIG_INTENT` 和一个最小问题。敏感值不得进入输出或工具；
配置请求包含敏感值时返回 `SENSITIVE_VALUE_FORBIDDEN`。`sources` 是真实官方正文，
`validationSources` 记录实际采用的本地模型或服务端验证，二者不得相互冒充。
