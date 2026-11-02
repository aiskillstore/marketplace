---
name: "tieba-demand-insights"
description: "当用户需要做百度贴吧用户需求研究、产品痛点归纳、购买顾虑整理或常见问题分析时使用。输入产品关键词、吧名或帖子链接，基于帖子与楼层讨论输出带原话依据的需求报告。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "tieba-demand-insights"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"💬","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 贴吧用户需求洞察

## 适用场景

当用户需要做百度贴吧用户需求研究、产品痛点归纳、购买顾虑整理或常见问题分析时使用。输入产品关键词、吧名或帖子链接，基于帖子与楼层讨论输出带原话依据的需求报告。来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向、吧名、帖子链接或帖子 ID。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 输出带帖子和楼层依据的痛点、购买顾虑、FAQ 与可尝试行动。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest tieba search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba forum-search \
  --forum-name "<forum_name>" --keyword "<keyword>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba forum-posts \
  --forum-name "<forum_name>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba detail \
  --thread-id "<thread_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba comments \
  --thread-id "<thread_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba comments \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill tieba-demand-insights

npx -y socialdatax-skills@latest tieba replies \
  --thread-id "<thread_id>" --comment-id "<comment_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill tieba-demand-insights
```

## 参数说明

搜索：
- 说明：帖子搜索先取 1 页；`tieba search` 可使用 `--pages <n>` 做有界翻页，不支持 `--all`。

详情 / 评论：
- 说明：详情/评论选择 `--thread-id` 或 `--url`；楼中楼回复同时需要 `--thread-id` 和 `--comment-id`。
- 说明：其他列表继续取样时使用返回的完整 `--page-token <next_page_token>`；保持吧名、关键词、帖子 ID 和父评论 ID 与当前链路一致。

通用：
- 必填：`tieba search --keyword <text>`：按产品或主题定位帖子。
- 必填：`tieba forum-posts --forum-name <name>`；吧内研究使用 `tieba forum-search --forum-name <name> --keyword <text>`。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill tieba-demand-insights`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先确认产品/主题和吧范围，从 1 页帖子选择 1–3 个相关讨论；用户提供帖子链接时直接读取详情和评论。按具体问题需要补充楼中楼，不自动遍历整个贴吧。
同一用户重复表达和同帖引用不要作为独立需求计数。把亲身经历、提问、转述和分析判断区分开；没有评论证据时只报告帖子线索。

## 输出建议

优先输出可直接复盘的结果：相关样本和主要角度、单条内容事实、评论主题和反馈线索，并标出下一步可继续追问的问题。

输出需求主题、使用场景、痛点、购买顾虑、FAQ、可尝试的产品或内容行动。每项附短原话、帖子链接或 ID、楼层/评论 ID（有则保留）和证据强弱。
写明帖子及评论样本量、观察范围与缺失信息；样本中的提及次数不等于全体用户占比，不推测用户敏感身份。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `baidu_tieba_search_posts`
- `baidu_tieba_search_posts_in_forum`
- `baidu_tieba_get_forum_posts`
- `baidu_tieba_get_post_detail_by_thread_id`
- `baidu_tieba_get_post_detail_by_url`
- `baidu_tieba_get_post_comments_by_thread_id`
- `baidu_tieba_get_post_comments_by_url`
- `baidu_tieba_get_post_comment_replies`

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：内容样本=标题/作者/链接或 ID、详情=正文/作者/发布时间/互动指标、评论=内容/用户/时间/回复线索；判断=相关原因和下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。

## 常见问题

- 没结果：放宽关键词、减少限定，或换成更贴近用户表达的词。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
