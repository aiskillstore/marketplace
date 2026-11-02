---
name: "socialdatax-short-video-copy-extract"
description: "面向短视频文案提取、短视频文案一键提取、视频文案提取、视频链接转文案、短视频转文字、视频转文字、口播转文字、视频逐字稿和逐字稿整理。当前 direct CLI 入口支持小红书、抖音、快手、微博和视频号公开视频链接、分享文案、内容 ID 或已有 job_id，获取视频基础信息、原视频简介、口播逐字稿、可复制文案和精简版；其他平台不在本 Skill 范围内，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "socialdatax-short-video-copy-extract"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🎙️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
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

这是只读 skill，可通过 direct CLI 或 hosted MCP 提交有限范围的视频转文字分析任务，也可以查询已有任务状态。 运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。 不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：成功=平台/视频基础信息/原视频简介/逐字稿/可复制文案/精简版；未完成=继续查询同一 job_id；失败=错误原因/是否可重试/下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 提交或查询异常：保留错误信息，先检查 `SOCIALDATAX_API_KEY`、输入链接或 ID、以及 `job_id` 是否完整。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复提交或反复查询；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 如果提交失败且没有返回 `data.job_id`，确认参数和 API Key 后可以重新提交；如果已经拿到 `data.job_id`，后续异常只查询同一个任务，不要重复提交视频。
- 任务失败：优先展示 `data.error.message` 或 `data.message`；只有 `data.error.retryable` 是 `true` 时才建议稍后重试。

## 常见问题

- 没结果：确认视频链接、分享文案、内容 ID 或 `job_id` 完整。
- 调用失败：如果已有 `job_id`，只查询同一个任务；如果没有 `job_id`，先确认 `SOCIALDATAX_API_KEY` 和输入格式；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想整理成文案：先等任务成功，再基于逐字稿和返回上下文整理可复制版本。
