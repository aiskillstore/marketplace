---
name: "douyin-account-analysis-report"
description: "当用户需要做抖音账号诊断、抖音账号分析、抖音账号复盘、账号体检、播放低或不推流排查、近期作品表现整理和内容优化方向判断时使用。基于用户提供的抖音主页链接、分享文案或 sec_user_id，整理账号资料和近 30 天作品结果，输出可执行的账号分析报告。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "douyin-account-analysis-report"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🩺","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 抖音账号诊断

## 适用场景

当用户需要做抖音账号诊断、抖音账号分析、抖音账号复盘、账号体检、播放低或不推流排查、近期作品表现整理和内容优化方向判断时使用。基于用户提供的抖音主页链接、分享文案或 sec_user_id，整理账号资料和近 30 天作品结果，输出可执行的账号分析报告。

## 快速开始

- 先给出当前 skill 支持的输入：账号主页、账号分享文本或平台账号 ID。
- 推荐先取账号资料，再取近 30 天最多 50 条作品；如果用户只想试跑，可以把 `--max-items` 降低到 10。
- 你通常会得到：账号基础信息、近期作品样本、互动指标、内容栏目、更新节奏、问题判断和 30 天测试计划。

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
npx -y socialdatax-skills@latest douyin user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill douyin-account-analysis-report

npx -y socialdatax-skills@latest douyin user-posts \
  --profile-url "<profile_url_or_share_text>" --since-days 30 --max-items 50 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill douyin-account-analysis-report
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest douyin user-info \
  --sec-user-id "<sec_user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill douyin-account-analysis-report

npx -y socialdatax-skills@latest douyin user-posts \
  --sec-user-id "<sec_user_id>" --since-days 30 --max-items 50 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill douyin-account-analysis-report
```

## 参数说明

创作者 / 账号：
- 说明：二选一入口：`--profile-url <profile_url_or_share_text>`，当用户粘贴抖音主页链接、短链或分享文案，想做账号诊断 / 账号分析时使用。
- 说明：二选一入口：`--sec-user-id <sec_user_id>`，当已经知道抖音账号 sec_user_id，想查询账号资料或近期作品列表时使用。
- 说明：账号资料和作品列表可以分两步运行：先取账号资料，再取近 30 天作品样本；不要把主页链接和 sec_user_id 混在同一个命令里。
- 说明：创作者内容列表最近 30 天样本：默认用 `--since-days 30 --max-items 50`；如果用户指定更短或更长窗口，按用户要求调整。
- 可选：`--page-token <next_page_token>`：继续同一账号作品列表分页时，只能原样传回完整返回的 `next_page_token`，不能截断、改写、脱敏、重建，或用省略号替换中间内容。
- 说明：创作者内容列表 `--pages <n>`：从当前起点继续获取并合并 N 页作品结果；账号诊断一般先看近期样本，不需要默认全量翻页。
- 说明：创作者内容列表 `--max-items <n>`：收集到 N 条作品后停止；和 `--since-days` 同时存在时，先按时间过滤，再按数量截断。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill douyin-account-analysis-report`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

推荐流程：第一步运行账号资料命令，确认账号昵称、简介、认证、粉丝和主页基础信息；第二步运行作品列表命令，优先看近 30 天最多 50 条作品样本。
如果用户只给了主页链接或分享文案，用 profile-url 入口即可；如果已经拿到 sec_user_id，后续分页和复查优先使用 sec_user_id。

## 输出建议

优先输出可直接用于复盘会或运营调整的抖音账号诊断报告。

输出时使用固定结构的账号诊断报告，并按以下顺序组织；字段只使用返回中可见内容，缺失时说明缺失，不补造。

1. 账号画像：整理昵称、简介、认证、粉丝数、获赞数、IP 属地等账号基础事实，并把事实和判断分开写。
2. 近 30 天作品样本表：列出作品标题或简介、发布时间、互动指标、aweme_id、是否视频 / 图文，以及可继续追查的作品 ID。
3. Top / Bottom 作品对比：基于已返回样本找互动较高和较低的作品，说明差异来自选题、标题、发布时间、内容形式或互动引导等可见线索。
4. 互动结构：只使用返回里的点赞、评论、收藏、分享等公开指标；缺少某项时标注未返回，不硬算。
5. 内容栏目和更新节奏：把近期作品按主题、场景、人群或产品线分组，观察发布时间和连续性。
6. 问题判断：围绕播放低、不推流、定位不清、选题分散、互动弱等用户问题给出证据化判断；每条判断都要对应已返回的账号或作品证据。
7. 30 天测试计划：给 3-5 个低风险测试动作，例如固定栏目、标题钩子、发布时间、样本量、评论互动复盘和下一次复查指标。

如果返回中没有播放量、曝光、完播等指标，不直接判断真实播放量或平台是否不推流，只基于公开互动和作品表现提出可能方向。
只基于用户提供的抖音账号和当前返回页范围内的公开结果做判断；不承诺全平台完整覆盖，也不把样本结论说成平台推荐机制结论。
不承诺完播率、推荐页占比、粉丝画像、账号权重、保证涨粉、自动发布、账号登录、私信或账号操作。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_get_user_info_by_profile_url`
- `douyin_get_user_posted_videos_by_profile_url`
- `douyin_get_user_info_by_sec_user_id`
- `douyin_get_user_posted_videos_by_sec_user_id`

如果当前 Agent 已可直接调用 MCP 工具，优先使用上面的抖音账号资料和作品列表工具；只有用户给的是公开抖音号 douyin_id 时，才使用 `douyin_get_user_info_by_douyin_id`。
`douyin_get_user_info_by_douyin_id`：用于公开抖音号 douyin_id，不要传昵称、搜索关键词、sec_user_id、主页链接或作品链接。
`douyin_get_user_info_by_profile_url` / `douyin_get_user_posted_videos_by_profile_url`：用于主页链接、短链或主页分享文本。
`douyin_get_user_info_by_sec_user_id` / `douyin_get_user_posted_videos_by_sec_user_id`：用于已知 `sec_user_id` 的账号。
账号作品列表翻页使用不透明的 `page_token`。同一账号、同一命令下，必须把完整返回的 `next_page_token` 原样传回，不能改写、截断、脱敏、重建，或用省略号替换中间部分。
`--since-days` 只在 CLI 侧做过滤，不是 MCP 工具参数；如果只能直接调用 MCP，请按需要续页，再在分析阶段根据返回的 `publish_time` 做筛选。

## 安全边界

这是只读 skill。CLI 使用已有环境凭证或用户本地保存的私有凭证文件；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：账号=昵称/简介/认证/粉丝/获赞；作品=标题或简介/发布时间/互动指标/视频 ID；诊断=问题判断/证据/优化建议/30 天测试计划。字段缺失时明确标注，不补造。

## 异常处理

- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中用 `auth status` 确认环境或本地文件来源；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时按「API Key 获取」由用户本地隐藏录入；不要输出 Key、Authorization header 或秘密配置值。

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，按上述实际凭证来源核对配置，并检查参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。

## 常见问题

- 没结果：确认账号主页、分享文本或平台账号 ID 完整。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先按上述实际凭证来源核对 CLI 或 MCP 的生效配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
