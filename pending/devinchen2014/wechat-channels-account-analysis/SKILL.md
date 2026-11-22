---
name: "wechat-channels-account-analysis"
description: "当用户提供视频号作品链接、分享文本或已知 user_id，需要做视频号账号分析、账号复盘、近期内容表现整理、内容栏目归纳或运营方向判断时使用。整理公开账号资料和近 30 天视频结果，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "wechat-channels-account-analysis"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📊","homepage":"https://socialdatax.com/ai?from=modelscope"}}
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
- 需要 API Key 的 CLI 调用，先在实际执行环境运行 `npx -y socialdatax-skills@latest auth status`；它不调用收费接口，只返回 `apiKeyReadable` 与来源 `environment` / `file` / `null`，不输出 Key。已有可用配置时继续原任务；命令、权限或文件格式错误按实际错误处理，不一律判为没配置。已认证的 hosted MCP 沿用当前连接鉴权，不要求另配本地 CLI。
- 缺少 Key 时，请用户从上述官网获取，在自己打开的本地终端运行 `npx -y socialdatax-skills@latest auth login`，按隐藏输入提示填写。Key 保存到该终端当前用户主目录下 `.config/socialdatax/credentials.json`；Unix 文件权限为 600，Windows 使用当前用户私有 ACL，无法限制权限时保存失败。真实 Key 不进入 AI 聊天、模型可见的命令输入、日志、截图、命令历史、Skill 文件或版本库；Agent 不读取或展示凭证文件内容。
- CLI 每次调用都会读取该私有用户文件，不依赖客户端加载 Shell 配置，不需要改客户端或系统设置。非空 `SOCIALDATAX_API_KEY` 优先，既有旧兼容变量其次，最后读取文件；`source=environment` 时保存文件不会覆盖生效的环境凭证。鉴权失败先核对实际来源和账号，再由用户本地修正，保留其它配置。
- 用户完成录入后，在实际业务命令的同一执行环境重新运行 `auth status`。false 时停止业务调用，核对操作系统用户、主目录与文件访问权限；true 只说明凭证可读，鉴权与结果仍以原业务请求返回为准，不为配置检查额外调用收费接口。
- 远程或容器中的 CLI 读取远程或容器用户的配置，本机保存不会自动传入。只有具备可交互终端和持久主目录时，才在该执行环境本地录入；否则使用部署平台已有的 Secret / 环境变量注入方式。无法持久化或被沙箱阻止时说明实际限制，不复制 Key 到聊天、项目或临时命令，不绕过隔离。
- 需要验收长期保存时，完全退出客户端及后台执行进程，重开后再次检查，再继续原请求。日常使用沿用已验证配置，不反复要求重启或重新录入。

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

这是只读 skill。CLI 使用已有环境凭证或用户本地保存的私有凭证文件；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式：账号=昵称/简介/认证/公开规模；视频=描述/发布时间/互动指标/内容 ID；分析=栏目/节奏/表现信号/问题证据/测试建议。字段缺失时明确标注，不补造。

## 异常处理

- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中用 `auth status` 确认环境或本地文件来源；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时按「API Key 获取」由用户本地隐藏录入；不要输出 Key、Authorization header 或秘密配置值。

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，按上述实际凭证来源核对配置，并检查参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。
- 分页中断：保留已取得的结果；重试仍失败时，请用户确认视频号视频链接、分享文本或 user_id 后再试。

## 常见问题

- 没结果：确认视频号视频链接、分享文本或 user_id 完整。
- 结果太多：缩短时间范围或减少 max_items，再基于实际返回样本继续分析。
- 调用失败：先按上述实际凭证来源核对 CLI 或 MCP 的生效配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
