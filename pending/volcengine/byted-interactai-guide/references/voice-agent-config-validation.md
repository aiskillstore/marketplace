# Voice Agent 配置验证

**Domain**: voice-agent

## 本地结构检查

本地可以确定：JSON 是否可解析、target 是否有效、核心是否包含对象形式的
`AgentConfig/Config`、update 是否有基线、merge patch 是否可生成，以及敏感值是否被写入配置。
这些失败不需要查询文档。

字段是否新增、数值范围、枚举、ProviderParams、模型、资源和音色兼容性都可能随产品演进。
本地模板可提示需要验证，不能作为 `INVALID_RANGE`、`INVALID_ENUM` 或“不支持”的判定依据。

## 官方证据流程

CLI 只提供基础原语：

```bash
vertc docs list --query "StartVoiceChat" --limit 10 --format json
vertc docs fetch <唯一精确documents[].id> \
  --match "StartVoiceChat" --match "2025-06-01" --match "<字段>" --format json
```

配置核心使用当前 StartVoiceChat 文档。AibotCreate/AibotUpdate 是输出投影目标，无需搜索或读取
它们的文档。StartVoiceChat 标题没有唯一匹配时，执行一次 fallback：

```bash
vertc docs search "StartVoiceChat 2025-06-01 <字段 目标值>" --limit 2 --format json
vertc docs fetch <明确的results[].id> \
  --match "StartVoiceChat" --match "2025-06-01" --match "<字段>" --format json
```

`search` 的 query 是一个带引号的位置参数，不使用 `--query` 或 `-q`；只有 `list` 使用
`--query`。`fetch` 的 doc ID 是位置参数，必须原样取自 `documents[].id` 或 `results[].id`，不使用
`--url`、网页数字 ID 或猜测路径。

每个已规划配置分区执行一次 list；需要 fallback 时再执行一次 search，并对前两条结果各执行
一次 matched fetch。当前证据请求到此停止，不补 search、不改写 query，也不读取
`documentation-retrieval.md` 或抓取网页。用户下一轮明确要求扩大文档研究时，可以启动新的证据
请求。搜索摘要用于选择文档；采用的 fetch 正文必须满足 `complete=true`，其 `matched_terms`
并集需覆盖 StartVoiceChat、`2025-06-01` 和目标字段。
每条核心变更证据都必须与当前 StartVoiceChat scope 一致；Aibot target 不改变该 scope。

接口契约较长时仍应保留候选资格。用精确标题与 `--match` 控制返回内容；matched excerpt 无法
覆盖已规划字段时返回 `unknown`，无需默认读取全文。

遇到 `vertc.docs.invalid_argument` 或 `vertc.cli.invalid_flag` 时，只按
`error.details.usage/example` 纠正一次语法，query、limit、doc ID 和 match terms 保持不变；旧版 CLI
没有这些字段时只运行一次对应子命令的 `--help`。语法纠正后仍失败就返回 `valid=null`，不再猜测。
`docs` 命令只读，`--dry-run` 不提供参数校验。

采用正文前确认产品、StartVoiceChat 和 API 版本为当前目标 scope。AibotCreate/AibotUpdate 的
target API 版本只属于输出 envelope，不能作为核心配置证据 scope。搜索摘要、示例列表和错版本
正文不能作否定证据。
正文明示目标值违反约束或服务端返回确定错误时，可令 `valid=false`；所有变更路径均有同 scope
正文支持且结构完整时才可令 `valid=true`；工具不可用、正文截断、同轮证据冲突、scope 不匹配
或未提及时令 `valid=null`。

正文未提及的字段保持 `unknown`。证据不足时立即返回 `valid=null`；失败后不猜测参数，也不沿用
另一个 Provider 的 ProviderParams。`sources` 记录实际 fetch 且支撑结论的正文。

服务端执行响应是最终事实来源；当它与本地模板冲突时，以服务端和当前官方文档为准，并把模板
视为需要更新。
