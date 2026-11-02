---
name: "xhs-viral-copy-breakdown"
description: "当用户给出小红书关键词、赛道、人群、产品方向、笔记链接或 note_id，想拆解爆款文案的标题钩子、开头方式、卖点表达、情绪词、内容结构、互动引导和可复用文案框架时使用。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "xhs-viral-copy-breakdown"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"✍️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 小红书爆款文案拆解

## 适用场景

当用户给出小红书关键词、赛道、人群、产品方向、笔记链接或 note_id，想拆解爆款文案的标题钩子、开头方式、卖点表达、情绪词、内容结构、互动引导和可复用文案框架时使用。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向、内容链接或内容 ID。
- 支持输入：关键词、赛道、产品方向、笔记链接或完整 `note_id`；如果只有关键词，默认取 2 页、最多 20 条高互动样本。
- 你通常会得到：固定结构的文案拆解报告，包含样本表、标题钩子、开头方式、卖点表达、情绪词、内容结构、互动引导、可复用文案框架和下一步建议。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs search \
  --keyword "<keyword>" --sort-type like_count_descending --pages 2 --max-items 20 \
  --pretty --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-viral-copy-breakdown

npx -y socialdatax-skills@latest xhs detail \
  --note-id "<note_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-viral-copy-breakdown
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest xhs detail \
  --url "<note_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-viral-copy-breakdown
```

## 参数说明

搜索：
- 必填：`--keyword <text>`：当用户给关键词、赛道、人群或产品方向时必填；使用用户真实意图，去掉多余空格，并保持关键词聚焦。
- 可选：`--sort-type <general|time_descending|like_count_descending|comment_count_descending|collect_count_descending>`：可选排序参数；本 skill 的样本流程默认偏向 `like_count_descending`，除非用户指定其它排序。
- 可选：`--note-type <all|image|video>`：可选笔记类型筛选；默认是 `all`。
- 可选：`--publish-time-range <all|day|week|half_year>`：可选发布时间筛选；默认是 `all`。
- 可选：`--pages <n>`：从当前起点继续获取并合并 N 页搜索结果；如果返回了 `next_page_token`，可继续续页。
- 可选：`--max-items <n>`：收集到 N 条结果后停止。
- 可选：`--since-days <1-365>`：只保留最近 N 天内公开 `publish_time` 落在范围内的结果；范围仍受 `--pages` 限制，不承诺全平台完整覆盖。

详情：
- 条件必填：`--note-id <note_id>`：详情命令使用 ID 入口时必填；当用户提供完整 `note_id`，或需要打开某条样本详情时使用完整 `note_id`，不要只传前缀。
- 条件必填：`--url <note_url_or_share_text>`：详情命令使用链接入口时必填；用于笔记链接、短链或分享文本。

通用：
- 可选：`--page-token <next_page_token>`：这是不透明的分页 token；第一页不要传。继续同一条搜索链路时，只能原样传回完整返回的 `next_page_token`，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill xhs-viral-copy-breakdown`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

详情命令使用 ID 或 URL 其中一种入口即可，不要同时传两种。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。

## 输出建议

优先输出可直接用于内容复盘和创作参考的文案拆解报告。

输出时使用固定输出结构的文案拆解报告，并按以下顺序组织；字段缺失时说明缺失，不补造。

1. 样本表：保留标题、作者、互动指标、发布时间、完整原始 URL、完整 `note_id`，并用一句话说明为什么值得拆。
2. 标题钩子：拆标题里的利益点、好奇点、冲突点、数字、场景、人群或强情绪表达。
3. 开头方式：拆内容如何进入场景、提出问题、制造代入感或给出明确承诺；如果开头文本不可见，说明不能判断。
4. 卖点表达、情绪词和场景词：整理可见卖点、用户心理、情绪词、场景词和它们对应的表达作用。
5. 内容结构：基于返回的标题、描述、正文或可见文本拆结构顺序；不可见内容不要猜测。
6. 互动引导：分析文案中如何引导评论、收藏、关注等互动动作，只做文案分析，不读取评论数据，也不执行账号操作。
7. 可复用文案框架和下一步建议：给 3-5 个可迁移句式或结构模板，并建议是否继续查看详情、缩小关键词、调整排序或补充样本。

如果用户给出笔记链接或完整 `note_id`，优先围绕该笔记详情做拆解；如果用户给出关键词或赛道，先用高互动样本建立可复用表达模式。
对于 XHS 搜索或详情结果里的 `note_url`，无论是在最终回答、展示、引用、存储、输出还是转发时，都要保留完整原始 URL，包括其中的 `xsec_token` 查询参数；不要改写、截断、脱敏、重建，也不要只根据 `note_id` 去拼链接。如果详情里的 `note_url` 为空，就展示 `note_id`，或者明确说明当前没有可直接打开的完整链接。
对于 XHS `note_id`，要原样复制返回的完整 `note_id`；不要只传或只展示前缀。
只基于用户输入和当前返回样本或详情范围内的公开结果做判断；不承诺全平台完整覆盖，也不把当前样本说成唯一结论。
不承诺产出完整发布稿、设计封面、诊断账号、执行发布或确定性流量结果。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_search_notes`
- `xhs_get_note_detail_by_note_id`
- `xhs_get_note_detail_by_note_url`

在 XHS 搜索场景中，调用 `xhs_search_notes` 时传 `keyword`，可选传 `page_token`、`sort_type`、`note_type` 和 `publish_time_range`。

调用 `xhs_search_notes` 时不要传 `page`；第一页也不要传 `page_token`。
只有在 `next_page_token` 非空时才继续翻页；并且在同一个关键词、排序、内容类型、发布时间范围和调用链路下，把完整返回的 `next_page_token` 原样作为 `page_token` 传回。
如果当前 Agent 已可直接调用 MCP 工具，可按入口选择以下工具：
- `xhs_get_note_detail_by_note_id`：当你已经拿到完整 `note_id` 时使用；不要只传前缀。
- `xhs_get_note_detail_by_note_url`：用于笔记链接、短链或分享文本。

小红书搜索参数命名提醒：direct CLI 使用 `--sort-type`、`--publish-time-range`、`--note-type`；MCP 工具 `xhs_search_notes` 使用 `sort_type`、`publish_time_range`、`note_type`。不要传 `sortType`、`publishTimeRange` 或 `noteType`。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式：样本表=标题/作者/互动信号/完整链接/完整 note_id；拆解=标题钩子/开头方式/卖点表达/情绪词/内容结构/互动引导；复用=可复用文案框架/下一步建议；字段缺失时明确标注，不补造。

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
