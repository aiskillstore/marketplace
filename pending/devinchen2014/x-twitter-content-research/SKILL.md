---
name: "x-twitter-content-research"
description: "当用户需要做 X / Twitter 内容研究、账号作品观察、账号发出的回复分析、竞品内容对比或趋势判断时使用。区分账号主动参与的讨论与帖子收到的评论，保留可追溯的内容证据。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "x-twitter-content-research"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🔍","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# X / Twitter内容研究

## 适用场景

当用户需要做 X / Twitter 内容研究、账号作品观察、账号发出的回复分析、竞品内容对比或趋势判断时使用。区分账号主动参与的讨论与帖子收到的评论，保留可追溯的内容证据。

## 快速开始

提供选题关键词，或 X 用户名、用户 ID、主页链接，并说明要看账号作品还是该账号发出的回复。
关键词用 `x search`；账号作品用 `x user-posts`；账号发出的回复用 `x user-replies`。
交付样本范围、账号参与的话题、代表内容链接和观察结论。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest x search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-info \
  --username "<username>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-info \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-posts \
  --username "<username>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-posts \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-posts \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-replies \
  --username "<username>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-replies \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research

npx -y socialdatax-skills@latest x user-replies \
  --profile-url "<profile_url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill x-twitter-content-research
```

## 参数说明

创作者 / 账号：
- 说明：账号查询从 `--username`、`--user-id`、`--profile-url` 选择一种输入。列表续页使用同一账号、同一命令返回的完整 `next_page_token`。

通用：
- 说明：列表先取一页，用户需要更多时按约定页数或条数继续；不使用其他列表的分页令牌。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill x-twitter-content-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

给定账号并询问其参与哪些讨论时，直接使用 `x user-replies`；不要把该需求改成关键词搜索或某一条帖子的评论。
`x user-posts` 是账号作品列表；`x user-replies` 是账号发出的回复；`x comments` 是某条原帖收到的评论。只选择用户需要的入口。
先处理明确给定的账号和一页结果；需要更多样本时按用户指定的上限续页。结果较少或失败时说明已取得的范围，不推断没有互动。

## 输出建议

优先输出可直接复盘的结果：相关样本和主要角度、创作者资料、创作者内容证据，并标出下一步可继续追问的问题。

分别列出账号作品和账号发出的回复；保留原始内容链接、时间及可见上下文，缺失字段注明未返回。
按话题归纳回复样本，区分账号原话和分析判断；不从少量回复推断完整社交关系或私下立场。
X / Twitter 搜索结果中，如果返回了 `media_items[].cover_image_url` 或 `media_items[].video_url`，要原样保留。用户要保存 X 媒体时，每次把一个返回的媒体 URL 传给 `npx -y socialdatax-skills@latest x download-media --url "<media_url>" --output-dir <directory> --pretty`；这个本地保存命令不需要 `SOCIALDATAX_API_KEY`。如果 CLI 进程没有继承用户本地代理，就加 `--proxy "http://127.0.0.1:7890"`，或设置 `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`。如果搜索结果没有媒体字段，先用 X 详情作为下载前的兜底。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `x_search_posts`
- `x_get_user_info_by_username`
- `x_get_user_info_by_user_id`
- `x_get_user_info_by_profile_url`
- `x_get_user_posts_by_username`
- `x_get_user_posts_by_user_id`
- `x_get_user_posts_by_profile_url`
- `x_get_user_replies_by_username`
- `x_get_user_replies_by_user_id`
- `x_get_user_replies_by_profile_url`

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：内容样本=标题/作者/链接或 ID、账号=昵称/ID/简介/粉丝信号、账号内容=标题/发布时间/互动信号；判断=相关原因和下一步。

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
