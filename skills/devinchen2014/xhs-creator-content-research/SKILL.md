---
name: "xhs-creator-content-research"
description: "当用户需要做小红书博主内容研究、账号内容列表、近期发布复盘、内容风格分析、创作者对标或账号追踪时使用。面向品牌、MCN、内容运营和创作者。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "xhs-creator-content-research"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🗂️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 小红书博主内容研究

## 适用场景

当用户需要做小红书博主内容研究、账号内容列表、近期发布复盘、内容风格分析、创作者对标或账号追踪时使用。面向品牌、MCN、内容运营和创作者。

## 快速开始

- 先给出当前 skill 支持的输入：账号主页、账号分享文本或平台账号 ID。
- 如果结果有分页，先取第一页；要继续扩大，再按返回的下一页标记继续。
- 你通常会得到：近期内容列表、发布时间和互动信号，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs user-posts \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-content-research

npx -y socialdatax-skills@latest xhs user-posts \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-creator-content-research
```

## 参数说明

创作者 / 账号：
- 说明：XHS `--user-id <user_id>`：当创作者 ID 已经明确时优先使用。
- 说明：XHS `--profile-url <profile_url_or_share_text>`：用于主页 URL、短链或主页分享文本。
- 可选：`--page-token <next_page_token>`：这是不透明的分页 token；在同一条创作者内容列表或合集链路下，必须把完整返回的 `next_page_token` 原样传回，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
- 可选：`--pages <n>`：获取并合并 N 页创作者内容或合集条目。
- 可选：`--max-items <n>`：收集到 N 条创作者内容或合集条目后停止。

通用：
- 可选：`--all`：持续获取直到 `next_page_token` 为空；默认没有条数或页数上限。
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill xhs-creator-content-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

单次调用使用 ID 或主页 URL 其中一种入口即可，不要同时传两种。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。多页结果会把创作者内容或合集条目合并到 `data.items`，并补充 `page_count`、`item_count` 和 `next_page_token`。

## 输出建议

优先输出可直接复盘的结果：创作者内容证据，并标出下一步可继续追问的问题。

整理内容列表时，优先保留标题或描述、摘要、发布时间、互动数据、媒体链接和内容类型等证据。
对于 XHS 创作者笔记列表结果，要把每个返回的完整 `note_id` 都原样使用；不要只传或只展示前缀。
需要继续下钻时，优先复用返回里的内容 ID 去查详情或评论。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_get_user_posted_notes_by_user_id`
- `xhs_get_user_posted_notes_by_profile_url`

如果当前 Agent 已可直接调用 MCP 工具，可按入口选择以下工具：
- `xhs_get_user_posted_notes_by_user_id`：当 `user_id` 已经明确时优先使用。
- `xhs_get_user_posted_notes_by_profile_url`：用于主页链接、短链或主页分享文本。

创作者内容列表和合集翻页使用不透明的 `page_token`。同一用户、同一类命令下，必须把完整返回的 `next_page_token` 原样传回，不能改写、截断、脱敏、重建，或用省略号替换中间部分。用户需要多页或全部创作者内容时，优先使用 CLI 的 `--pages`、`--all` 和 `--max-items`。
`--since-days` 只在 CLI 侧做过滤，不是 MCP 工具参数；如果只能直接调用 MCP，请按需要续页，再在分析阶段根据返回的 `publish_time` 做筛选。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：账号内容=标题/发布时间/互动信号；判断=相关原因和下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。

## 常见问题

- 没结果：确认账号主页、分享文本或平台账号 ID 完整。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
