---
name: "wechat-channels-viral-video-breakdown"
description: "当用户提供视频号视频链接或分享文本，希望拆解爆款短视频的内容结构、开头钩子、口播节奏、互动表现、评论反馈和可复用创作角度时使用。基于当前视频公开详情、口播文稿和评论结果，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "wechat-channels-viral-video-breakdown"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🎬","homepage":"https://socialdatax.com/ai?from=modelscope"}}
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
- 先确认调用方式和命令实际运行位置：已认证的 hosted MCP 不要求本地 CLI 变量或 Node/npm；需要 Key 的直接 CLI 则在同一执行环境用下方命令检查。已能读取就继续原任务，不覆盖已有配置。不能运行命令或缺少 Node.js 属于执行环境问题，不能当成 Key 缺失；仅在确认用户没有 Key 时，才引导从上述官网获取。
- 本地 Agent：优先用客户端官方支持的持久化 Secret / env，并确认它注入 Agent 命令进程。WorkBuddy 可在当前可信工作空间的 `.codebuddy/settings.local.json` 中合并 `{"env":{"SOCIALDATAX_API_KEY":"<YOUR_API_KEY>"}}`，保留其他设置和 env；此路径只适用于 WorkBuddy，作用域只限该工作空间。真实 Key 由用户本地填写，文件不提交版本库。
- 远程 Agent：在实际运行命令的远程主机或服务配置客户端持久化 Secret / env，按该客户端的官方方式重新加载执行进程，并在同一远程会话检查；本机系统变量不会自动传到远程。不要因本机检查成功就认定远程也可用。
- 容器或云端沙箱 Agent：优先用平台支持的持久化 Secret / 环境变量注入功能，让它进入执行 CLI 的容器或沙箱；配置后按平台说明重建或重新加载，再在其中检查。不要改宿主机变量来代替沙箱注入；若平台无法持久保存或注入，说明限制并引导用户使用平台支持的鉴权方式，不绕过隔离。
- 检查为 false 时，先逐项排查：配置文件或 Secret 是否位于正确主机、工作空间和作用域，工作空间是否可信，字段是否正确且保留了已有设置，变量是否注入命令进程（仅 MCP server 的 env 不算），以及是否按官方说明重新加载或完全重启。修正后在原执行环境复查；只有明确不支持客户端持久化，或完成上述排查仍不可用，才用该环境官方支持的用户级/服务级环境变量兜底。不能仅因一次检查或重新加载失败就跳到系统配置。
- 系统兜底按实际执行主机处理：Windows 可用用户环境变量；macOS 可由用户在本机终端隐藏输入（如 Bash `read -s`）后传给 `launchctl setenv`，仅对当前登录会话有效，重登或重启电脑后需重新加载。输入失败、空输入或设置失败时明确报错并停止，返回非零退出码；清理临时变量不能覆盖原错误状态。配置后完全退出对应客户端及后台进程再打开；远程服务按其运行方式重载，沙箱仍通过平台注入。单独终端临时 `export`、只写 shell 启动文件或只关窗口都不能证明 Agent 已继承。真实 Key 不出现在聊天、日志、截图、命令历史或 Skill 文件里。
- 在实际执行 CLI 的同一环境运行 `node -e "console.log(JSON.stringify({apiKeyReadable:Boolean(['SOCIALDATAX_API_KEY','SOCIAL_MEDIA_MCP_API_KEY'].map(name=>process.env[name]?.trim()).find(Boolean))}))"`，只报告布尔结果，不打印 Key 或全部环境变量。检查遵循 CLI 的顺序：先读取去除首尾空白后的主变量，再兼容既有旧变量；新增配置仍统一用 `SOCIALDATAX_API_KEY`。`apiKeyReadable: false` 时停止业务调用并按上面的顺序排查；`true` 只证明存在可读取的非空值，继续原业务请求验证鉴权，不代表 Key 有效或余额充足。不要在检查命令里临时注入变量制造成功。

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

### 导出 SRT 字幕（direct CLI）
- 用户需要字幕文件时，使用 CLI 0.2.64 或更新版本，在上方对应平台的 `transcript` 命令末尾追加 `--srt-output ./video.srt`；保留原有来源归因参数。该选项也适用于本 Skill 已列出的 URL、内容 ID 和任务查询入口，不扩展平台范围。
- 先确认保存路径：父目录必须已存在且可写，目标文件不能已存在；CLI 不会覆盖已有文件。任务成功且返回有效时间分段时，CLI 写入 UTF-8 SRT，标准输出仍保留原始 JSON；以实际文件和保存成功提示确认导出完成。
- 任务尚未完成时，沿用对应平台的 `transcript --job-id <job_id>` 示例并追加相同的 `--srt-output ./video.srt`，不要重新提交视频。
- 路径预检失败且尚无 job_id 时，还没有提交转写任务；修正路径后继续原命令。已有 job_id 时，路径或文件写入错误不代表转写失败：保留已返回的 JSON，解决本地保存问题后用同一 job_id 重试。
- 若返回的时间分段缺失或无效，保留 JSON 并说明无法生成 SRT，停止重复查询，不补造时间戳，也不重新提交视频。
- `--srt-output` 只在 direct CLI 中执行本地保存，不是 hosted MCP 工具参数。若 MCP 已提交任务，需要导出时可在 CLI 中查询对应平台的同一 job_id；不能执行 CLI 时说明尚未生成本地 SRT 文件，不要重复提交任务。

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

这是只读 skill，可通过 direct CLI 或 hosted MCP 提交有限范围的视频转文字分析任务，也可以查询已有任务状态。 仅在用户要求导出 SRT 时，direct CLI 会向用户指定的新文件写入字幕，不覆盖已有文件。 运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。 不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式：事实=作者/发布时间/时长/互动指标；拆解=钩子/结构/节奏/互动引导；反馈=评论主题/高频原话；复用=可迁移角度/适用边界。字段缺失时明确标注，不补造。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中按「API Key 获取」的检查规则排查生效配置（主变量优先，兼容既有旧变量）；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时沿用前面的客户端排查与兜底顺序；不要输出 Key、Authorization header 或秘密配置值。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 使用 `--include-replies` 时，`replies_partial` 表示该评论回复不完整，`replies_pending` 表示尚未展开。先用该平台回复命令、对应评论标识及可用的 `replies_next_page_token` 补齐；尚未展开或首个回复请求失败时，修正错误后从该评论的首批回复开始，重复令牌错误则先排查。仅在主评论仍有剩余额度时，才用外层 `data.next_page_token` 继续；补齐已取得评论的回复不增加主评论页数；两类令牌不能混用，不把回复预览当成完整回复。
- 提交或查询异常：保留错误信息，按上述实际凭证来源核对配置，并检查输入链接或 ID、以及 `job_id` 是否完整。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复提交或反复查询；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。
- 如果提交失败且没有返回 `data.job_id`，确认参数和 API Key 后可以重新提交；如果已经拿到 `data.job_id`，后续异常只查询同一个任务，不要重复提交视频。
- 任务失败：优先展示 `data.error.message` 或 `data.message`；只有 `data.error.retryable` 是 `true` 时才建议稍后重试。

## 常见问题

- 没结果：确认视频号视频链接、分享文本或 job_id 完整。
- 结果太多：先基于当前视频详情、口播文稿和必要评论样本拆解；不需要回复证据时不要扩大调用范围。
- 调用失败：按「异常处理」核对本次调用实际使用的凭证来源；如果已有 `job_id`，只查询同一个任务；如果没有 `job_id`，再检查输入格式；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
