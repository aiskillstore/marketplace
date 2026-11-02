---
name: "instagram-comment-insights"
description: "当用户需要做 Instagram 评论分析、Instagram 评论洞察、Instagram 用户反馈分析、需求挖掘、痛点总结、购买顾虑整理、FAQ 提炼、口碑分析、评论回复观察或内容讨论复盘时使用。基于用户提供的 Instagram 帖子链接下的评论结果，面向内容运营、产品调研、品牌调研和创作者。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "instagram-comment-insights"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"💬","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# Instagram评论分析与需求挖掘

## 适用场景

当用户需要做 Instagram 评论分析、Instagram 评论洞察、Instagram 用户反馈分析、需求挖掘、痛点总结、购买顾虑整理、FAQ 提炼、口碑分析、评论回复观察或内容讨论复盘时使用。基于用户提供的 Instagram 帖子链接下的评论结果，面向内容运营、产品调研、品牌调研和创作者。

## 快速开始

- 先给出当前 skill 支持的输入：帖子链接。
- 如果结果有分页，先取第一页；要继续扩大，再按返回的下一页标记继续。
- 你通常会得到：评论文本、回复线索和用户反馈主题。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest instagram comments \
  --post-url "<instagram_post_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill instagram-comment-insights

npx -y socialdatax-skills@latest instagram replies \
  --post-id "<post_id>" --comment-id "<comment_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill instagram-comment-insights
```

## 参数说明

评论 / 回复：
- 说明：使用 CLI 示例里的 URL 入口传内容页链接、短链或分享文本来获取一级评论。
- 可选：`--page-token <next_page_token>`：这是不透明的分页 token；在同一条内容或评论链路下，必须把完整返回的 `next_page_token` 原样传回，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
- 可选：`--pages <n>`：获取并合并 N 页一级评论或回复。
- 可选：`--all`：持续获取一级评论或回复，直到 `next_page_token` 为空；默认没有条数或页数上限。
- 可选：`--max-items <n>`：收集到 N 条一级评论或回复后停止。
- 说明：Instagram `--post-url <instagram_post_url_or_share_text>`：用于一级评论；继续取回复时需要 `--post-id <post_id>` 和 `--comment-id <comment_id>`。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill instagram-comment-insights`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

一级评论命令一次只使用 CLI 示例里的一个入口；不要在同一条命令里混用多个内容定位参数。回复命令使用 CLI 示例中对应平台需要的回复定位参数。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。多页结果会把一级评论合并到 `data.items`，并补充 `page_count`、`item_count` 和下一页标记；在支持 `--include-replies` 的平台上，每条一级评论还会带上 `replies`、`replies_page_count` 和 `replies_next_page_token`。

## 输出建议

优先输出可直接用于复盘和决策的结果：评论主题、用户反馈、痛点、需求和可行动建议。

默认按这个结构输出：评论主题、用户痛点、购买顾虑、未满足需求、FAQ、高频原话、可行动建议。
先说明输入范围：结论基于用户提供的目标内容下已返回的评论和回复，不代表全平台完整覆盖。
把评论原文证据和你的判断分开写；引用高频原话时只使用返回中可见的评论文本，不编造不存在的反馈。
如果使用了多页结果或继续拉取回复，说明评论和回复的覆盖范围；如果只取第一页，也要明确这是局部样本。
面向内容运营、产品调研或品牌调研时，把评论反馈转成可执行的问题清单、选题角度、产品改进线索或客服 FAQ。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `instagram_get_post_comments_by_post_url`
- `instagram_get_post_comment_replies_by_comment_id`

如果当前 Agent 已可直接调用 MCP 工具，可按入口选择以下工具：

- `instagram_get_post_comments_by_post_url`：用于 Instagram 帖子 URL。
- `instagram_get_post_comment_replies_by_comment_id`：已知 Instagram `post_id` 和一级评论 ID 时使用。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：评论=内容/用户/时间/回复线索；判断=主题/痛点/需求/建议。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。

## 常见问题

- 没结果：确认链接或 ID 完整；必要时先用内容研究类 skill 找到目标内容。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续做需求挖掘：增加评论页数，必要时继续拉取回复，再结合业务场景整理成问题清单、FAQ 和行动建议。
