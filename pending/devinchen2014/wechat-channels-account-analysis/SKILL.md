---
name: "wechat-channels-account-analysis"
description: "当用户提供视频号作品链接、分享文本或已知 user_id，需要做视频号账号分析、账号复盘、近期内容表现整理、内容栏目归纳或运营方向判断时使用。整理公开账号资料和近 30 天视频结果，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "wechat-channels-account-analysis"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📊","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 视频号账号分析

## 适用场景

当用户提供视频号作品链接、分享文本或已知 user_id，需要做视频号账号分析、账号复盘、近期内容表现整理、内容栏目归纳或运营方向判断时使用。整理公开账号资料和近 30 天视频结果，来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：视频号视频链接、分享文本或已知 user_id。
- 支持输入：该账号的视频链接、分享文本或已知 user_id；默认看近 30 天最多 50 条视频。
- 你通常会得到：账号资料、近期视频样本、内容栏目、更新节奏、表现信号、问题判断和下一轮测试建议。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest wechat user-info \
  --user-id "<v2_finder_user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-account-analysis

npx -y socialdatax-skills@latest wechat user-info \
  --url "<wechat_work_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-channels-account-analysis

npx -y socialdatax-skills@latest wechat user-posts \
  --url "<wechat_work_url_or_share_text>" --since-days 30 --max-items 50 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill wechat-channels-account-analysis
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest wechat user-posts \
  --user-id "<v2_finder_user_id>" --since-days 30 --max-items 50 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill wechat-channels-account-analysis
```

执行 direct CLI 示例时，尖括号内容是占位符；不要把原始用户输入拼成整段 shell 字符串。能直接调用子进程时使用参数数组；必须走 shell 时先做 shell 转义。

## 参数说明

创作者 / 账号：
- 说明：二选一入口：`--url <wechat_work_url_or_share_text>`，当用户提供该账号的视频或图文作品链接或分享文本时，用它解析作者并读取账号视频列表。
- 说明：二选一入口：`--user-id <v2_finder_user_id>`，当已经知道视频号 user_id 时，用它读取账号资料和近期视频。
- 说明：不支持只凭账号名称完成本流程；缺少视频链接、分享文本和 user_id 时，先请用户补充其中一种。
- 说明：账号视频列表默认观察近 30 天、最多 50 条样本；用户指定其它时间范围或数量时按用户要求调整。
- 可选：`--page-token <next_page_token>`：继续同一账号的视频列表时，只能原样传回完整返回 token。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill wechat-channels-account-analysis`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

推荐流程：先确认账号资料，再查看近 30 天最多 50 条视频样本；如果只有视频或图文作品链接或分享文本，先通过链接解析作者和视频列表。
只有作品链接或分享文本时，direct CLI 使用 `wechat user-info --url` 获取作者资料；已知 user_id 时使用 `wechat user-info --user-id`。

## 输出建议

优先输出可直接用于账号复盘和内容调整的视频号账号分析报告。

输出时使用固定结构，并把账号事实、视频样本和分析判断分开写。

1. 账号资料：整理返回中可见的昵称、简介、认证、公开规模和账号标识。
2. 近期视频样本：列出描述、发布时间、公开互动指标、内容 ID 和可见内容形式。
3. 内容栏目和形式：按主题、场景、人群或产品线分组，说明各组样本数量和代表内容。
4. 更新节奏：基于实际返回的发布时间观察频率和连续性；时间字段不足时不推断。
5. 表现信号：比较当前样本中公开互动较高和较低的视频，只说明可见差异。
6. 问题判断和建议：每条判断对应账号或视频证据，并给出 3-5 个可验证的下一轮内容测试。

只基于用户提供的账号和当前返回范围判断，不承诺按账号名称查找、全量历史、平台推荐机制或确定性增长结果。
不使用未返回的粉丝画像、完播率、推荐页占比、账号权重或私域数据，不执行登录、发布、私信和账号操作。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `wechat_get_user_info_by_user_id`
- `wechat_get_user_info_by_url`
- `wechat_get_user_posted_videos_by_url`
- `wechat_get_user_posted_videos_by_user_id`

如果当前 Agent 已接入 MCP，视频或图文作品链接或分享文本使用 `wechat_get_user_info_by_url` 和 `wechat_get_user_posted_videos_by_url`；已知 user_id 使用对应 ID 工具。
创作者视频列表的 page_token 是不透明值；同一账号续页时原样传回完整 next_page_token。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式：账号=昵称/简介/认证/公开规模；视频=描述/发布时间/互动指标/内容 ID；分析=栏目/节奏/表现信号/问题证据/测试建议。字段缺失时明确标注，不补造。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 分页中断：保留已取得的结果；重试仍失败时，请用户确认视频号视频链接、分享文本或 user_id 后再试。

## 常见问题

- 没结果：确认视频号视频链接、分享文本或 user_id 完整。
- 结果太多：缩短时间范围或减少 max_items，再基于实际返回样本继续分析。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
