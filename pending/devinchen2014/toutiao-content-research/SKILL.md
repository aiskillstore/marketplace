---
name: "toutiao-content-research"
description: "当用户需要做今日头条内容研究、文章选题、热点角度整理或同主题内容对比时使用。输入主题或内容链接，基于相关作品和详情输出样本概览、标题模式与可继续验证的内容方向。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "toutiao-content-research"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📰","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 今日头条内容研究

## 适用场景

当用户需要做今日头条内容研究、文章选题、热点角度整理或同主题内容对比时使用。输入主题或内容链接，基于相关作品和详情输出样本概览、标题模式与可继续验证的内容方向。来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向、要观察的平台热榜、内容链接或内容 ID。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 你通常会得到：榜单排名和热度信号、相关标题、作者或账号、链接或内容 ID、单条内容正文、作者、发布时间和互动指标，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest toutiao hot-search \
  --pretty --source-client socialdatax-skills --source-platform modelscope \
  --source-skill toutiao-content-research

npx -y socialdatax-skills@latest toutiao search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill toutiao-content-research

npx -y socialdatax-skills@latest toutiao detail \
  --post-id "<post_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill toutiao-content-research

npx -y socialdatax-skills@latest toutiao detail \
  --url "<toutiao_content_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill toutiao-content-research
```

## 参数说明

热榜：
- 必填：`toutiao hot-search`：无需关键词。

搜索：
- 说明：搜索先取 1 页，需要扩大时使用 `--pages <n>` 与 `--max-items <n>`；不支持搜索 `--all`。

通用：
- 必填：`toutiao search --keyword <text>`：输入聚焦的主题。
- 必填：`toutiao detail`：选择 `--post-id` 或 `--url`；URL 输入也可为分享文案。
- 说明：续页原样传回完整 `--page-token <next_page_token>`，保持关键词和筛选条件一致。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill toutiao-content-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

从用户主题或提供的内容链接开始。主题研究先取 1 页，选择 1–3 条代表作品读取详情；需要当下选题线索时再查看热榜。
热榜和关键词样本分开呈现；以实际返回的内容类型、标题、描述/正文及指标为依据。缺少正文时明确标注，不从标题补写文章内容。

## 输出建议

优先输出可直接复盘的结果：榜单信号、相关样本和主要角度、单条内容事实，并标出下一步可继续追问的问题。

输出样本概览、反复出现的内容角度、标题模式、代表作品与后续选题建议；每个结论保留链接或内容 ID 作为依据。
说明观察时间、样本范围和缺失信息；区分热度信号与分析判断，不根据单次样本声称长期趋势或全平台覆盖。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `toutiao_get_hot_search_list`
- `toutiao_search_posts`
- `toutiao_get_post_detail_by_post_id`
- `toutiao_get_post_detail_by_url`

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：热榜=排名/话题/热度信号、内容样本=标题/作者/链接或 ID、详情=正文/作者/发布时间/互动指标；判断=相关原因和下一步。

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
