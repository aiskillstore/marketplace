---
name: "socialdatax-creator-research"
description: "当用户需要做社媒创作者研究、小红书博主画像、抖音达人画像、快手达人画像、账号资料、近期内容复盘、合作对象初筛或对标账号观察时使用。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "socialdatax-creator-research"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"👤","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# SocialDataX 创作者研究

## 适用场景

当用户需要做社媒创作者研究、小红书博主画像、抖音达人画像、快手达人画像、账号资料、近期内容复盘、合作对象初筛或对标账号观察时使用。来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：账号关键词、达人名称或赛道方向、账号主页、账号分享文本或平台账号 ID。
- 账号搜索默认取一页；作品示例使用 `--since-days 30` 自动翻页至日期截止或列表结束，可加 `--pages <n>` 限制请求页数。
- 你通常会得到：候选账号、昵称、平台账号 ID 和粉丝信号、账号资料、认证、粉丝或互动信号、近期内容列表、发布时间和互动信号，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs user-search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest xhs user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest xhs user-posts \
  --profile-url "<profile_url_or_share_text>" --since-days 30 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-posts \
  --profile-url "<profile_url_or_share_text>" --since-days 30 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-series \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest kuaishou user-search \
  --keyword "<creator_keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest kuaishou user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest kuaishou user-posts \
  --profile-url "<profile_url_or_share_text>" --since-days 30 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest xhs user-info \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest xhs user-posts \
  --user-id "<user_id>" --since-days 30 --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-info \
  --sec-user-id "<sec_user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-posts \
  --sec-user-id "<sec_user_id>" --since-days 30 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest douyin user-series \
  --sec-user-id "<sec_user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest kuaishou user-search \
  --keyword "<creator_keyword>" --pages 3 --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest kuaishou user-info \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research

npx -y socialdatax-skills@latest kuaishou user-posts \
  --user-id "<user_id>" --since-days 30 --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-creator-research
```

## 参数说明

创作者 / 账号：
- 说明：用户只提供账号名称或赛道时，先用对应平台的 `xhs user-search`、`douyin user-search` 或 `kuaishou user-search`，通过 `--keyword` 找候选账号；用返回的小红书/快手 `user_id`（`--user-id`）或抖音 `sec_user_id`（`--sec-user-id`）继续查资料或作品。候选不唯一时先确认目标；已提供主页或 ID 时直接查询。
- 可选：`--page-token <next_page_token>`：创作者内容列表或合集续页时，只能原样使用完整返回 token；不能截断、改写、脱敏、重建，或用省略号替换中间内容。

通用：
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-creator-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

只有在用户同时需要账号资料和近期内容证据时，才同时使用资料命令和内容列表命令。命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。

## 输出建议

优先输出可直接复盘的结果：候选账号、创作者资料、创作者内容证据，并标出下一步可继续追问的问题。

输出创作者资料时，优先写昵称、平台 ID、简介、认证、粉丝数、关注数、获赞数、IP 属地、性别等可见事实；把事实和策略判断分开写。
整理内容列表时，优先保留标题或描述、摘要、发布时间、互动数据、媒体链接和内容类型等证据。
如果用了抖音短剧合集命令，优先输出合集 ID、标题、描述、封面、价格和作者信息；快手当前提供的是创作者作品列表，不是合集列表。
需要继续下钻时，优先复用返回里的内容 ID 去查详情或评论。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_search_users`
- `xhs_get_user_info_by_profile_url`
- `xhs_get_user_posted_notes_by_profile_url`
- `douyin_search_users`
- `douyin_get_user_info_by_profile_url`
- `douyin_get_user_posted_videos_by_profile_url`
- `douyin_get_user_series_by_profile_url`
- `kuaishou_search_users`
- `kuaishou_get_user_info_by_profile_url`
- `kuaishou_get_user_posted_videos_by_profile_url`
- `xhs_get_user_info_by_user_id`
- `xhs_get_user_posted_notes_by_user_id`
- `douyin_get_user_info_by_sec_user_id`
- `douyin_get_user_posted_videos_by_sec_user_id`
- `douyin_get_user_series_by_sec_user_id`
- `kuaishou_get_user_info_by_user_id`
- `kuaishou_get_user_posted_videos_by_user_id`

如果用户给的是公开抖音号 douyin_id，使用 `douyin_get_user_info_by_douyin_id`；不要把它当作昵称/搜索关键词、`sec_user_id` 或 `profile_url`。
MCP 账号发现使用对应平台的 `xhs_search_users`、`douyin_search_users` 或 `kuaishou_search_users`，传入 `keyword`；续页使用返回的完整 `next_page_token`，不要传 `page`。
创作者内容列表和合集翻页使用不透明的 `page_token`；在同一用户链路下，必须把完整返回的 `next_page_token` 原样传回，不能截断、改写、脱敏、重建，或用省略号替换中间内容。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：候选账号=昵称/ID/粉丝信号、账号=昵称/ID/简介/粉丝信号、账号内容=标题/发布时间/互动信号；判断=相关原因和下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。

## 常见问题

- 没结果：确认账号主页、分享文本、平台账号 ID 或账号关键词完整；必要时放宽达人名称或赛道方向。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
