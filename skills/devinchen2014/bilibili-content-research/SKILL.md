---
name: "bilibili-content-research"
description: "当用户需要做 B站视频分析、爆款拆解、选题参考、竞品视频对比、趋势判断或素材整理时使用；需要时也可补充专栏结果。面向内容运营、品牌调研和创作者。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "bilibili-content-research"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🔍","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# B站视频分析

## 适用场景

当用户需要做 B站视频分析、爆款拆解、选题参考、竞品视频对比、趋势判断或素材整理时使用；需要时也可补充专栏结果。面向内容运营、品牌调研和创作者。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 你通常会得到：相关标题、作者或账号、链接或内容 ID，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest bilibili search-videos \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill bilibili-content-research

npx -y socialdatax-skills@latest bilibili search-articles \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill bilibili-content-research
```

## 参数说明

搜索：
- 必填：`--keyword <text>`：必填；使用用户真实意图并保持关键词聚焦。视频样本用 `bilibili search-videos`，专栏样本用 `bilibili search-articles`。
- 可选：`--sort-type <general|view_count_descending|time_descending|danmaku_count_descending|collect_count_descending>`：可选排序参数；视频样本默认偏向 `view_count_descending`。
- 可选：`--sort-type <general|time_descending|view_count_descending|like_count_descending|comment_count_descending>`：可选排序参数；专栏样本默认使用平台默认排序。
- 可选：`--publish-time-range <all|day|week|half_year>`：可选发布时间筛选；仅适用于视频样本。
- 可选：`--duration-range <all|under_10_minutes|between_10_and_30_minutes|between_30_and_60_minutes|over_60_minutes>`：可选时长筛选；仅适用于视频样本。
- 可选：`--pages <n>`：从当前起点继续获取并合并 N 页搜索结果；如果返回了 `next_page_token`，可继续续页。
- 可选：`--max-items <n>`：收集到 N 条结果后停止。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill bilibili-content-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。搜索支持 `--pages` 和 `--max-items`，但不支持 `--all`，因为搜索没有稳定的完整结果边界。多页结果会把结果合并到 `data.items`，并补充 `page_count`、`item_count` 和下一页标记。
B站视频和专栏各有独立入口：视频内容用 `bilibili search-videos`，专栏内容用 `bilibili search-articles`。

## 输出建议

优先输出可直接复盘的结果：相关样本和主要角度，并标出下一步可继续追问的问题。

输出为 B站内容研究报告：结果表、标题钩子、内容角度、互动信号、可复用选题和下一步建议。
先说明输入范围：结论基于当前搜索关键词和当前返回页范围内的公开结果，不代表全站完整覆盖。
样本表保留标题、作者或频道、互动指标、发布时间、完整 URL 和完整内容 ID；如果字段缺失，就明确说明缺失，不补造。
标题钩子和内容角度：拆标题里的利益点、场景词、问题意识和信息密度。
如果用户要继续深入，再建议扩大页数、换关键词，或分开比较视频结果和专栏结果。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `bilibili_search_videos`
- `bilibili_search_articles`

不要只因为某一页 `items` 为空就判断没有更多结果。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：内容样本=标题/作者/链接或 ID；判断=相关原因和下一步。

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
