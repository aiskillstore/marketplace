---
name: "wechat-channels-viral-video-breakdown"
description: "当用户提供视频号视频链接或分享文本，希望拆解爆款短视频的内容结构、开头钩子、口播节奏、互动表现、评论反馈和可复用创作角度时使用。基于当前视频公开详情、口播文稿和评论结果，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "wechat-channels-viral-video-breakdown"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🎬","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 视频号爆款短视频拆解

## 适用场景

当用户提供视频号视频链接或分享文本，希望拆解爆款短视频的内容结构、开头钩子、口播节奏、互动表现、评论反馈和可复用创作角度时使用。基于当前视频公开详情、口播文稿和评论结果，来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：视频号视频链接、分享文本或已有 job_id。
- 支持输入：视频号视频链接或分享文本；默认先看详情和口播文稿，评论按用户需要补充。
- 你通常会得到：视频事实、开头钩子、内容结构、口播节奏、互动表现、评论主题、可复用角度和样本局限。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest wechat detail \
  --url "<wechat_work_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-viral-video-breakdown

npx -y socialdatax-skills@latest wechat transcript \
  --url "<wechat_video_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-viral-video-breakdown

npx -y socialdatax-skills@latest wechat transcript \
  --job-id "<job_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-viral-video-breakdown

npx -y socialdatax-skills@latest wechat comments \
  --url "<wechat_video_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-viral-video-breakdown

npx -y socialdatax-skills@latest wechat replies \
  --object-id "<object_id>" --object-nonce-id "<object_nonce_id>" \
  --comment-id "<comment_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-viral-video-breakdown
```

执行 direct CLI 示例时，尖括号内容是占位符；不要把原始用户输入拼成整段 shell 字符串。能直接调用子进程时使用参数数组；必须走 shell 时先做 shell 转义。

## 参数说明

文案提取 / 转写：
- 输入：`--job-id <job_id>`：口播文稿任务未完成时，继续查询同一个任务；不要为了轮询状态重复提交视频。

评论 / 回复：
- 输入：`--url <wechat_video_url_or_share_text>`：用于视频号视频链接或分享文本；详情、口播文稿和一级评论分别调用对应命令，不把同一个输入拼接成其它链接。
- 必填：`--object-id <object_id>`、`--object-nonce-id <object_nonce_id>` 和 `--comment-id <comment_id>`：只在继续查看某条一级评论的回复时使用返回中的完整值。
- 可选：`--page-token <next_page_token>`：继续同一视频的评论或回复分页时，只能原样传回完整 token。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill wechat-channels-viral-video-breakdown`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

推荐流程：先读取视频详情，确认描述、作者、发布时间、时长和公开互动指标；再对同一视频提交口播文稿任务，并在需要用户反馈证据时读取评论。
口播文稿任务返回非终态时，保留同一个 job_id 继续查询；只有终态成功后才基于返回文稿拆解开头钩子、内容结构和节奏。
评论回复只用于补充已返回一级评论的讨论脉络；不需要回复证据时，不扩大调用范围。

## 输出建议

优先输出基于公开详情、口播文稿和评论证据的视频号短视频拆解报告。

输出时使用固定结构，并把公开事实、口播文稿证据、评论证据和分析判断分开写。

1. 视频事实：整理返回中可见的描述、作者、发布时间、时长、公开互动指标和内容 ID。
2. 开头钩子：只基于可见描述或口播文稿判断问题、利益点、冲突、场景或情绪切入；文稿缺失时说明不能判断。
3. 内容结构和口播节奏：按开头、展开、转折、结尾和互动引导拆分；不补写不可见内容。
4. 互动表现：列出返回中的点赞、评论、收藏、转发等公开指标；缺少某项时标注未返回，不硬算。
5. 评论反馈：说明评论样本页数和回复范围，归纳高频主题、疑问、反对意见和用户原话。
6. 可复用角度：给出 3-5 个可迁移的钩子、结构或表达方向，并说明哪些内容依赖当前样本。
7. 样本局限：结论只代表当前视频和实际返回范围，不保证流量结果，不把样本判断说成平台推荐机制。

不承诺发布、账号操作、完整全网覆盖、确定性爆款结果或未返回的用户画像。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `wechat_get_video_detail_by_url`
- `wechat_submit_video_speech_text_by_video_url`
- `wechat_get_video_speech_text_job`
- `wechat_get_video_comments_by_url`
- `wechat_get_video_comment_replies_by_comment_id`

如果当前 Agent 已接入 MCP 工具，只使用上面列出的同一视频详情、口播文稿、评论和回复工具。
口播文稿未到终态时，按返回的 next_action 使用同一个 job_id 继续查询，不重复调用 submit 工具。

## 安全边界

这是只读 skill，可通过 direct CLI 或 hosted MCP 提交有限范围的视频转文字分析任务，也可以查询已有任务状态。 运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。 不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式：事实=作者/发布时间/时长/互动指标；拆解=钩子/结构/节奏/互动引导；反馈=评论主题/高频原话；复用=可迁移角度/适用边界。字段缺失时明确标注，不补造。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 使用 `--include-replies` 时，`replies_partial` 表示该评论回复不完整，`replies_pending` 表示尚未展开。先用该平台回复命令、对应评论标识及可用的 `replies_next_page_token` 补齐；尚未展开或首个回复请求失败时，修正错误后从该评论的首批回复开始，重复令牌错误则先排查。仅在主评论仍有剩余额度时，才用外层 `data.next_page_token` 继续；补齐已取得评论的回复不增加主评论页数；两类令牌不能混用，不把回复预览当成完整回复。
- 提交或查询异常：保留错误信息，先检查 `SOCIALDATAX_API_KEY`、输入链接或 ID、以及 `job_id` 是否完整。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复提交或反复查询；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 如果提交失败且没有返回 `data.job_id`，确认参数和 API Key 后可以重新提交；如果已经拿到 `data.job_id`，后续异常只查询同一个任务，不要重复提交视频。
- 任务失败：优先展示 `data.error.message` 或 `data.message`；只有 `data.error.retryable` 是 `true` 时才建议稍后重试。

## 常见问题

- 没结果：确认视频号视频链接、分享文本或 job_id 完整。
- 结果太多：先基于当前视频详情、口播文稿和必要评论样本拆解；不需要回复证据时不要扩大调用范围。
- 调用失败：如果已有 `job_id`，只查询同一个任务；如果没有 `job_id`，先确认 `SOCIALDATAX_API_KEY` 和输入格式；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
