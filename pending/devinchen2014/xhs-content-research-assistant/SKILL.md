---
name: "xhs-content-research-assistant"
description: "面向内容运营、品牌调研和创作者的小红书内容研究助手。适用于内容研究、选题策划、竞品观察、趋势判断、评论洞察和创作者资料整理，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "xhs-content-research-assistant"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🔥","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 小红书内容研究助手

## 适用场景

面向内容运营、品牌调研和创作者的小红书内容研究助手。适用于内容研究、选题策划、竞品观察、趋势判断、评论洞察和创作者资料整理，来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向、要观察的平台热榜、内容链接或内容 ID、账号主页、账号分享文本或平台账号 ID。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 你通常会得到：榜单排名和热度信号、相关标题、作者或账号、链接或内容 ID、单条内容正文、作者、发布时间和互动指标、评论文本、回复线索和用户反馈主题、账号资料、认证、粉丝或互动信号、近期内容列表、发布时间和互动信号，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs hot-search \
  --pretty --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs detail \
  --note-id "<note_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs comments \
  --note-id "<note_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs user-info \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs user-posts \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest xhs detail \
  --url "<note_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs comments \
  --url "<note_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs user-posts \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-content-research-assistant

npx -y socialdatax-skills@latest xhs sub-comments \
  --note-id "<note_id>" --comment-id "<comment_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-content-research-assistant
```

## 参数说明

热榜：
- 说明：用户要看当前小红书热榜时，使用 `xhs hot-search`，这个命令不需要 `--keyword`。

搜索：
- 说明：做关键词研究时，使用 `xhs search --keyword <text>`。
- 说明：关键词研究筛选：XHS 搜索使用文档里的 `--sort-type` 值；`--note-type` 和 `--publish-time-range` 只在支持时使用。

详情 / 评论：
- 说明：详情、评论、回复命令：使用示例里的内容 ID 参数，或者用对应的 URL 入口，两种方式不要混用。
- 说明：XHS 评论 `--sort-type <default|time_descending|like_count_descending>`：可选一级评论排序；不传就使用平台默认排序。
- 条件必填：`--comment-id <comment_id>`：子评论命令必填，需要和对应的笔记 ID 一起使用。

创作者 / 账号：
- 说明：创作者资料和创作者笔记列表命令：使用示例里的账号 ID 参数，或者用对应的 profile-url 入口，两种方式不要混用。

通用：
- 说明：XHS 搜索翻页时，如果返回了 `next_page_token`，再使用 `--page-token <next_page_token>`；对于评论、回复和创作者笔记列表，也只能在同一条笔记、评论或创作者链路里原样使用完整返回 token，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill xhs-content-research-assistant`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

优先使用最贴近用户任务的 XHS direct CLI 命令。命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。

## 输出建议

优先输出可直接复盘的结果：榜单信号、相关样本和主要角度、单条内容事实、评论主题和反馈线索、创作者资料、创作者内容证据，并标出下一步可继续追问的问题。

做内容研究时，先把可见证据和你的判断分开写；建议按话题模式、内容角度、受众反应、创作者定位和有代表性的样本来整理。
对于 XHS 搜索或详情结果里的 `note_url`，无论是在最终回答、展示、引用、存储、输出还是转发时，都要保留完整原始 URL，包括其中的 `xsec_token` 查询参数；不要改写、截断、脱敏、重建，也不要只根据 `note_id` 去拼链接。如果详情里的 `note_url` 为空，就展示 `note_id`，或者明确说明当前没有可直接打开的完整链接。
对于 XHS `note_id`，要原样复制返回的完整 `note_id`；不要只传或只展示前缀。
做评论分析时，先归纳可见主题，再判断情绪、需求或风险点。
做创作者研究时，把账号资料和创作者笔记列表证据分开写。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_get_search_hot_list`
- `xhs_search_notes`
- `xhs_get_note_detail_by_note_id`
- `xhs_get_note_comments_by_note_id`
- `xhs_get_user_info_by_user_id`
- `xhs_get_user_posted_notes_by_user_id`
- `xhs_get_note_detail_by_note_url`
- `xhs_get_note_comments_by_note_url`
- `xhs_get_user_info_by_profile_url`
- `xhs_get_user_posted_notes_by_profile_url`
- `xhs_get_note_sub_comments_by_comment_id`

上面自动列出的 MCP 工具名就是事实源；优先选择最贴近当前 XHS 任务的工具。
调用 `xhs_search_notes` 时，续页要使用完整返回的 `next_page_token` 作为 `page_token`；XHS 评论、回复和创作者笔记列表续页时也遵循同样规则。

小红书搜索参数命名提醒：direct CLI 使用 `--sort-type`、`--publish-time-range`、`--note-type`；MCP 工具 `xhs_search_notes` 使用 `sort_type`、`publish_time_range`、`note_type`。不要传 `sortType`、`publishTimeRange` 或 `noteType`。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：热榜=排名/话题/热度信号、内容样本=标题/作者/链接或 ID、详情=正文/作者/发布时间/互动指标、评论=内容/用户/时间/回复线索、账号=昵称/ID/简介/粉丝信号、账号内容=标题/发布时间/互动信号；判断=相关原因和下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 使用 `--include-replies` 时，`replies_partial` 表示该评论回复不完整，`replies_pending` 表示尚未展开。先用该平台回复命令、对应评论标识及可用的 `replies_next_page_token` 补齐；尚未展开或首个回复请求失败时，修正错误后从该评论的首批回复开始，重复令牌错误则先排查。仅在主评论仍有剩余额度时，才用外层 `data.next_page_token` 继续；补齐已取得评论的回复不增加主评论页数；两类令牌不能混用，不把回复预览当成完整回复。
- 非余额不足且非限流的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 批量处理：默认按队列逐条处理；用户明确需要批量效率时，最多同时处理 3 条。每完成 1 条，就继续处理下一条，不要一次性发起大量请求。遇到 `rate_limited` 或“请求过于频繁”时，不要放弃任务；先停止发起新的请求，按返回的等待时间等待，没有等待时间就先等待 2 秒，然后继续处理当前队列。等待期间已完成的结果要保留；恢复后继续从未完成的位置处理。遇到 `insufficient_balance` 或“积分不足”时，立即停止后续请求，输出已获得结果，并提示充值或切换有余额的 API Key 后继续。

## 常见问题

- 没结果：放宽关键词、减少限定，或换成更贴近用户表达的词。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
