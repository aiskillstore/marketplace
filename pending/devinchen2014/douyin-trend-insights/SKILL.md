---
name: "douyin-trend-insights"
description: "当用户需要做抖音趋势洞察、抖音趋势分析、热点观察、内容方向判断、趋势线索归纳或营销灵感整理时使用。面向内容运营、品牌调研和创作者。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "douyin-trend-insights"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📈","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 抖音趋势洞察

## 适用场景

当用户需要做抖音趋势洞察、抖音趋势分析、热点观察、内容方向判断、趋势线索归纳或营销灵感整理时使用。面向内容运营、品牌调研和创作者。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向、要观察的平台热榜。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 你通常会得到：榜单排名和热度信号、相关标题、作者或账号、链接或内容 ID，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest douyin hot-search \
  --pretty --source-client socialdatax-skills --source-platform modelscope \
  --source-skill douyin-trend-insights

npx -y socialdatax-skills@latest douyin search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill douyin-trend-insights
```

## 参数说明

热榜：
- 说明：Douyin `hot-search`：无必填参数。

搜索：
- 说明：Douyin `search --keyword <text>`：使用 `douyin search` 时必填；使用用户真实意图，去掉多余空格，并保持关键词聚焦。
- 说明：Douyin `--sort-type <general|time_descending|like_count_descending>`：可选排序参数；不传就使用默认排序。
- 说明：Douyin `--publish-time-range <all|day|week|half_year>`：可选发布时间筛选；不传表示不限制发布时间。
- 说明：Douyin `--duration-range <all|under_1_minute|one_to_five_minutes|over_5_minutes>`：可选时长筛选；不传表示不限制时长。
- 说明：Douyin `--content-type <all|video|image>`：可选内容类型筛选；不传表示包含全部内容类型。
- 说明：Douyin `--pages <n>`：从当前起点继续获取并合并 N 页搜索结果；如果返回了 `next_page_token`，可继续续页。
- 可选：`--max-items <n>`：收集到 N 条搜索结果后停止。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 说明：Douyin `--page-token <next_page_token>`：这是不透明的分页 token；第一页不要传。继续同一条搜索链路时，只能原样传回完整返回的 `next_page_token`，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill douyin-trend-insights`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

如果用户要看当前抖音热榜，使用 `douyin hot-search`；这个命令不需要 `--keyword`。
抖音排序可选值：
- `general`：默认排序。
- `time_descending`：按发布时间从新到旧。
- `like_count_descending`：按点赞数从高到低。

抖音发布时间筛选可选值：
- `all`：不限制发布时间。
- `day`：一天内发布。
- `week`：一周内发布。
- `half_year`：半年内发布。

抖音时长筛选可选值：
- `all`：不限制时长。
- `under_1_minute`：1 分钟以内。
- `one_to_five_minutes`：1 到 5 分钟。
- `over_5_minutes`：5 分钟以上。

抖音内容类型筛选可选值：
- `all`：全部内容类型。
- `video`：视频作品。
- `image`：图文内容。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。搜索支持 `--pages` 和 `--max-items`，但不支持 `--all`，因为搜索没有稳定的完整结果边界。多页结果会把结果合并到 `data.items`，并补充 `page_count`、`item_count` 和下一页标记。

## 输出建议

优先输出可直接复盘的结果：榜单信号、相关样本和主要角度，并标出下一步可继续追问的问题。

输出热榜时，先把它当作当前排名和热度信号来整理；如果同时用了关键词搜索，要把热榜和搜索结果分开写。
先把可见证据和你的判断分开写；当用户需要可追溯结论时，保留有用的内容 ID、链接、标题或描述、作者、数据指标和发布时间。
抖音搜索结果需要可追溯时，保留 `content_type`。
抖音图文搜索结果中，使用返回的 `images`；当 `video.media_type="audio"` 时，把它当作音频播放资源，不要当作视频作品。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_get_hot_search_list`
- `douyin_search_videos`

如果当前 Agent 已可直接调用 MCP 工具，调用 `douyin_get_hot_search_list` 时不要传关键词参数。

抖音 MCP 调用 `douyin_search_videos`：
- `keyword`：必填搜索词或主题；使用用户真实意图，并去掉多余空格。
- `page_token`：可选的不透明分页 token。继续同一条搜索链路时，只能原样传回完整返回的 `next_page_token`，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
调用 `douyin_search_videos` 时不要传 `page`；第一页也不要传 `page_token`。
- `sort_type`：可选排序参数，可选值为 `general`, `time_descending`, `like_count_descending`；不传就使用默认排序。
- `publish_time_range`：可选发布时间筛选，可选值为 `all`、`day`、`week`、`half_year`；不传表示不限制发布时间。
- `duration_range`：可选时长筛选，可选值为 `all`, `under_1_minute`, `one_to_five_minutes`, `over_5_minutes`；不传表示不限制时长。
- `content_type`：可选内容类型筛选，可选值为 `all`, `video`, `image`；不传表示包含全部内容类型。

抖音只有在 `next_page_token` 非空时才继续翻页；同一个关键词和筛选条件链路下，把完整返回的 `next_page_token` 原样作为 `page_token` 传回。
不要只因为某一页 `items` 为空就判断没有更多结果。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：热榜=排名/话题/热度信号、内容样本=标题/作者/链接或 ID；判断=相关原因和下一步。

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
