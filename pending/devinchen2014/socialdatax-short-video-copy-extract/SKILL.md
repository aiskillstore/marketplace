---
name: "socialdatax-short-video-copy-extract"
description: "面向短视频文案提取、短视频文案一键提取、视频文案提取、视频链接转文案、短视频转文字、视频转文字、口播转文字、视频逐字稿和逐字稿整理。当前 direct CLI 入口支持小红书、抖音、快手、微博和视频号公开视频链接、分享文案、内容 ID 或已有 job_id，获取视频基础信息、原视频简介、口播逐字稿、可复制文案和精简版；其他平台不在本 Skill 范围内，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "socialdatax-short-video-copy-extract"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🎙️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 短视频文案一键提取

## 适用场景

面向短视频文案提取、短视频文案一键提取、视频文案提取、视频链接转文案、短视频转文字、视频转文字、口播转文字、视频逐字稿和逐字稿整理。当前 direct CLI 入口支持小红书、抖音、快手、微博和视频号公开视频链接、分享文案、内容 ID 或已有 job_id，获取视频基础信息、原视频简介、口播逐字稿、可复制文案和精简版；其他平台不在本 Skill 范围内，来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：视频链接、分享文案、内容 ID 或已有 job_id。
- 平台边界：当前 direct CLI 入口只支持小红书、抖音、快手、微博和视频号；其他平台不在本 Skill 范围内，请先确认是否存在对应口播转文字入口。
- 你通常会得到：视频基础信息、原视频简介、口播逐字稿、可复制文案和精简版；适合短视频文案提取、视频转文字、口播转文字和逐字稿整理；未完成时先继续查询任务状态。

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
npx -y socialdatax-skills@latest xhs transcript \
  --url "<note_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest xhs transcript \
  --note-id "<note_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest xhs transcript \
  --job-id "<job_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest douyin transcript \
  --url "<douyin_content_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest douyin transcript \
  --aweme-id "<aweme_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest douyin transcript \
  --job-id "<job_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest kuaishou transcript \
  --url "<kuaishou_content_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest kuaishou transcript \
  --photo-id "<photo_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest kuaishou transcript \
  --job-id "<job_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest weibo transcript \
  --post-url "<weibo_post_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest weibo transcript \
  --post-id "<post_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest weibo transcript \
  --job-id "<job_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest wechat transcript \
  --url "<wechat_video_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest wechat transcript \
  --encrypted-object-id "<encrypted_object_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill socialdatax-short-video-copy-extract

npx -y socialdatax-skills@latest wechat transcript \
  --job-id "<job_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-short-video-copy-extract
```

### 导出 SRT 字幕（direct CLI）
- 用户需要字幕文件时，使用 CLI 0.2.64 或更新版本，在上方对应平台的 `transcript` 命令末尾追加 `--srt-output ./video.srt`；保留原有来源归因参数。该选项也适用于本 Skill 已列出的 URL、内容 ID 和任务查询入口，不扩展平台范围。
- 先确认保存路径：父目录必须已存在且可写，目标文件不能已存在；CLI 不会覆盖已有文件。任务成功且返回有效时间分段时，CLI 写入 UTF-8 SRT，标准输出仍保留原始 JSON；以实际文件和保存成功提示确认导出完成。
- 任务尚未完成时，沿用对应平台的 `transcript --job-id <job_id>` 示例并追加相同的 `--srt-output ./video.srt`，不要重新提交视频。
- 路径预检失败且尚无 job_id 时，还没有提交转写任务；修正路径后继续原命令。已有 job_id 时，路径或文件写入错误不代表转写失败：保留已返回的 JSON，解决本地保存问题后用同一 job_id 重试。
- 若返回的时间分段缺失或无效，保留 JSON 并说明无法生成 SRT，停止重复查询，不补造时间戳，也不重新提交视频。
- `--srt-output` 只在 direct CLI 中执行本地保存，不是 hosted MCP 工具参数。若 MCP 已提交任务，需要导出时可在 CLI 中查询对应平台的同一 job_id；不能执行 CLI 时说明尚未生成本地 SRT 文件，不要重复提交任务。

## 参数说明

文案提取 / 转写：
- 输入：`--url <video_url_or_share_text>` / 微博 `--post-url <weibo_post_url_or_share_text>`：视频链接或分享文案入口；小红书 / 抖音 / 快手 / 视频号使用 `--url`，微博使用 `--post-url`；当用户想做文案提取 / 口播转文字时，按平台选择对应 transcript 命令。
- 说明：已知内容 ID 且想做文案提取 / 口播转文字时，按平台使用对应 ID 入口：XHS `--note-id`、抖音 `--aweme-id`、快手 `--photo-id`、微博 `--post-id`、视频号 `--encrypted-object-id`。
- 输入：`--job-id <job_id>`：继续查询已有文案提取 / 转写任务；使用产生该 job_id 的同一平台 transcript 命令，不要重复提交视频。
- 说明：单次文案提取 / 转写调用只能使用 URL/share text、平台内容 ID 或 `--job-id` 其中一种入口。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-short-video-copy-extract`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

常见说法：短视频文案提取、短视频文案一键提取、视频文案提取、视频链接转文案、短视频转文字、视频转文字、口播转文字、视频逐字稿和逐字稿整理，均按当前文案提取 / 转写流程处理。
平台选择：小红书 / XHS / RedNote 视频笔记使用 `xhs transcript`；抖音视频使用 `douyin transcript`；快手视频使用 `kuaishou transcript`；微博视频博文使用 `weibo transcript`；视频号视频使用 `wechat transcript`。当前 direct CLI 入口支持小红书、抖音、快手、微博和视频号。
当前 direct CLI 只覆盖上述五个平台；其他平台不在本 Skill 范围内，先确认是否存在对应口播转文字入口，不要为当前 Skill 拼接不存在的命令。
执行步骤：第一步，用对应平台的 URL/share text 或内容 ID 入口提交短视频文案提取；如果用户已经给了 `job_id`，直接用同平台 `--job-id` 查询。
第二步，先看返回 JSON 里的 `data.is_terminal`：如果不是 `true`，复制同一个 `data.job_id`，运行同平台 `transcript --job-id <job_id>` 命令继续查询。
第三步，只有 `data.is_terminal` 是 `true` 时才交付结果：如果 `data.status` 是 `succeeded`，整理视频信息、简介和逐字稿；否则说明 `data.error.message` 或 `data.message`。
循环规则：每次查询返回后都先判断 `data.is_terminal`。只要 `data.is_terminal` 不是 `true`，就继续查询同一个 `data.job_id`；先等 `data.next_poll_after_seconds`，如果没有这个字段，就短暂等待后再查。
停止条件只有三类：终态、工具无法继续运行、用户要求停止。拿到 `data.job_id` 后，提交动作最多一次；不要重复提交同一个视频，不要把只有 `data.job_id` 的内容当作最终结果。
失败时，只在 `data.error.retryable` 是 `true` 时建议稍后重试；如果是 `false`，不要建议重复提交同一个视频。

## 输出建议

优先输出可直接复制的短视频文案提取、视频转文字、口播转文字或逐字稿整理结果：视频基础信息、原视频简介、口播逐字稿、可复制文案和精简版；未完成时继续查询任务状态。

固定输出结构：任务成功后按以下顺序组织；字段只使用返回中可见内容，缺失时标注未返回，不补造。

1. 视频基础信息：平台、标题、作者、发布时间、时长、内容 ID、原始链接等；只有返回中存在时才输出。
2. 原视频简介：优先使用返回中的简介或描述，保留原意，适合用户直接复制或继续整理。
3. 口播逐字稿：输出转写正文，尽量保持原口播顺序。
4. 可复制文案版：基于原视频简介和口播逐字稿整理为便于复制的正文，不新增未出现的信息。
5. 精简版：用短段落概括视频主要内容，方便用户快速判断是否继续复盘。
6. 任务状态：如果任务未完成或失败，只输出 `job_id`、`status`、`next_action`、错误信息和是否可重试。

优先交付返回中可见的视频上下文、原视频简介、口播逐字稿、可复制文案和精简版。
输出前先检查 `data.is_terminal`：如果不是 `true`，先用同一个 `data.job_id` 继续查询，不要提前写最终文案。只有工具无法继续运行、会话被中断或用户要求停止时，才输出 `data.job_id`、`data.status` 和 `data.next_action`，提示用户稍后继续查询。
只有 `data.is_terminal` 是 `true` 且 `data.status` 是 `succeeded` 时才输出逐字稿；失败时输出 `data.error.message` 或 `data.message`。
失败时先看 `data.error.retryable`：只有值为 `true` 才建议稍后重试；值为 `false` 时说明当前视频不适合重复提交。
如果结果显示没有可处理的视频资源或任务失败，按当前任务结果说明，不要换平台重试。
除非用户另行要求，当前 skill 只做文案提取和任务状态续查，不扩展到其他创作、账号操作或流量结果判断。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_submit_video_speech_text_by_note_url`
- `xhs_submit_video_speech_text_by_note_id`
- `xhs_get_video_speech_text_job`
- `douyin_submit_video_speech_text_by_video_url`
- `douyin_submit_video_speech_text_by_aweme_id`
- `douyin_get_video_speech_text_job`
- `kuaishou_submit_video_speech_text_by_video_url`
- `kuaishou_submit_video_speech_text_by_photo_id`
- `kuaishou_get_video_speech_text_job`
- `weibo_submit_video_speech_text_by_post_url`
- `weibo_submit_video_speech_text_by_post_id`
- `weibo_get_video_speech_text_job`
- `wechat_submit_video_speech_text_by_video_url`
- `wechat_submit_video_speech_text_by_encrypted_object_id`
- `wechat_get_video_speech_text_job`

如果当前 Agent 已接入 MCP 工具，按平台选择对应的视频文案提取工具：XHS 使用 `xhs_submit_video_speech_text_by_note_url`、`xhs_submit_video_speech_text_by_note_id`、`xhs_get_video_speech_text_job`；抖音使用 `douyin_submit_video_speech_text_by_video_url`、`douyin_submit_video_speech_text_by_aweme_id`、`douyin_get_video_speech_text_job`；快手使用 `kuaishou_submit_video_speech_text_by_video_url`、`kuaishou_submit_video_speech_text_by_photo_id`、`kuaishou_get_video_speech_text_job`；微博使用 `weibo_submit_video_speech_text_by_post_url`、`weibo_submit_video_speech_text_by_post_id`、`weibo_get_video_speech_text_job`；视频号使用 `wechat_submit_video_speech_text_by_video_url`、`wechat_submit_video_speech_text_by_encrypted_object_id`、`wechat_get_video_speech_text_job`。
继续查询已有任务时，只调用同平台 get-job 工具；不要为了轮询状态再次调用 submit 工具。任务未到终态时继续用同一个 `job_id` 查询。

## 安全边界

这是只读 skill，可通过 direct CLI 或 hosted MCP 提交有限范围的视频转文字分析任务，也可以查询已有任务状态。 仅在用户要求导出 SRT 时，direct CLI 会向用户指定的新文件写入字幕，不覆盖已有文件。 运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。 不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：成功=平台/视频基础信息/原视频简介/逐字稿/可复制文案/精简版；未完成=继续查询同一 job_id；失败=错误原因/是否可重试/下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中按「API Key 获取」的检查规则排查生效配置（主变量优先，兼容既有旧变量）；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时沿用前面的客户端排查与兜底顺序；不要输出 Key、Authorization header 或秘密配置值。
- 提交或查询异常：保留错误信息，按上述实际凭证来源核对配置，并检查输入链接或 ID、以及 `job_id` 是否完整。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复提交或反复查询；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。
- 如果提交失败且没有返回 `data.job_id`，确认参数和 API Key 后可以重新提交；如果已经拿到 `data.job_id`，后续异常只查询同一个任务，不要重复提交视频。
- 任务失败：优先展示 `data.error.message` 或 `data.message`；只有 `data.error.retryable` 是 `true` 时才建议稍后重试。

## 常见问题

- 没结果：确认视频链接、分享文案、内容 ID 或 `job_id` 完整。
- 调用失败：按「异常处理」核对本次调用实际使用的凭证来源；如果已有 `job_id`，只查询同一个任务；如果没有 `job_id`，再检查输入格式；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想整理成文案：先等任务成功，再基于逐字稿和返回上下文整理可复制版本。
