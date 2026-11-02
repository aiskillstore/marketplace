---
name: "haokan-topic-analysis"
description: "当用户需要做好看视频选题、短视频内容方向规划或竞品角度复盘时使用。基于用户提供的主题或视频链接，整理相关作品、标题角度与评论反馈，输出带样本依据的选题清单。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "haokan-topic-analysis"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🧭","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 好看视频选题分析

## 适用场景

当用户需要做好看视频选题、短视频内容方向规划或竞品角度复盘时使用。基于用户提供的主题或视频链接，整理相关作品、标题角度与评论反馈，输出带样本依据的选题清单。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供主题、受众或好看视频链接；已有作品时也可以提供 video_id。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 输出带作品依据的候选选题、内容角度与参考标题。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest haokan hot-search \
  --pretty --source-client socialdatax-skills --source-platform modelscope \
  --source-skill haokan-topic-analysis

npx -y socialdatax-skills@latest haokan search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill haokan-topic-analysis

npx -y socialdatax-skills@latest haokan detail \
  --video-id "<video_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill haokan-topic-analysis

npx -y socialdatax-skills@latest haokan detail \
  --url "<video_url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill haokan-topic-analysis

npx -y socialdatax-skills@latest haokan comments \
  --video-id "<video_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill haokan-topic-analysis

npx -y socialdatax-skills@latest haokan comments \
  --url "<video_url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill haokan-topic-analysis

npx -y socialdatax-skills@latest haokan replies \
  --video-id "<video_id>" --comment-id "<comment_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill haokan-topic-analysis
```

## 参数说明

搜索：
- 说明：搜索先取 1 页，需要扩大时使用 `--pages <n>` 与 `--max-items <n>`，不支持 `--all`。
- 说明：评论/回复可用 `--pages` 与 `--max-items` 限制样本；续页原样传回完整 `--page-token <next_page_token>`，保持视频、父评论和关键词不变。

评论 / 回复：
- 必填：`haokan replies`：同时提供 `--video-id` 和父评论 `--comment-id`。

通用：
- 必填：`haokan search --keyword <text>`：按用户主题取样。
- 必填：`haokan detail` / `comments`：选择 `--video-id` 或 `--url`。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill haokan-topic-analysis`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先明确主题和受众，默认从 1 页相关作品开始；用户已有视频链接时直接读取详情。挑选 1–3 条相关作品复核，再按需要读取评论，不为填满报告批量调用。
`haokan hot-search` 返回热词，只能作为选题线索；不等于视频排行榜，也不能据此推断作品播放量或涨幅。
评论内嵌回复是预览；需要深入讨论时用父评论 ID 调用 replies。好看视频不支持 `--include-replies`、`--since-days` 或逐字稿提取；内容判断只使用已返回的标题、描述和评论。

## 输出建议

按选题清单交付，将热词线索、作品事实和评论反馈分开。

给出候选选题、目标受众、内容角度、参考标题、优先级与理由；每项保留视频链接或 ID 及可见证据。
将作品原文、评论反馈和分析建议分开；交代样本数量、观察时间和缺失信息，不承诺爆款或代表全平台趋势。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `haokan_get_hot_search_list`
- `haokan_search_videos`
- `haokan_get_video_detail_by_video_id`
- `haokan_get_video_detail_by_url`
- `haokan_get_video_comments_by_video_id`
- `haokan_get_video_comments_by_url`
- `haokan_get_comment_replies_by_video_id`

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 格式示例：选题／受众／角度／参考标题／理由／视频链接或 ID；只填实际取得的证据。

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
