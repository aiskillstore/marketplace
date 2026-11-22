---
name: "youtube-content-research"
description: "当用户需要做 YouTube 内容研究、频道内容观察、竞品内容对比、趋势判断或素材整理时使用。面向内容运营、品牌调研和创作者。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "youtube-content-research"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🔍","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# YouTube内容研究

## 适用场景

当用户需要做 YouTube 内容研究、频道内容观察、竞品内容对比、趋势判断或素材整理时使用。面向内容运营、品牌调研和创作者。

## 快速开始

- 先给出当前 skill 支持的输入：关键词或选题方向。
- 如果你只想先看样本，先取 1 页；要继续扩大，再按参数说明使用分页或 `--max-items`。
- 你通常会得到：相关标题、作者或账号、链接或内容 ID，以及可继续追问的角度。

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
npx -y socialdatax-skills@latest youtube search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill youtube-content-research
```

## 参数说明

搜索：
- 说明：YouTube `search --keyword <text>`：使用 `youtube search` 时必填；使用用户真实意图，去掉多余空格，并保持关键词聚焦。
- 可选：`--max-items <n>`：收集到 N 条搜索结果后停止。
- 说明：YouTube `--sort-type <general|time_descending|view_count_descending|rating>`：可选排序参数；不传就使用默认排序。
- 说明：YouTube `--publish-time-range <all|last_hour|today|this_week|this_month|this_year>`：可选发布时间筛选；不传表示不限制发布时间。
- 说明：YouTube `--duration-range <all|under_4_min|between_4_and_20_min|over_20_min>`：可选时长筛选；不传表示不限制时长。
- 说明：YouTube `--pages <n>`：从当前起点继续获取并合并 N 页搜索结果；如果返回了 `next_page_token`，可继续续页。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 说明：YouTube `--page-token <next_page_token>`：这是不透明的分页 token；第一页不要传。继续同一条搜索链路时，只能原样传回完整返回的 `next_page_token`。
- 说明：YouTube `--video-type <all|video|movie>`：可选视频类型筛选；不传表示包含全部视频类型。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill youtube-content-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。搜索支持 `--pages` 和 `--max-items`，但不支持 `--all`，因为搜索没有稳定的完整结果边界。多页结果会把结果合并到 `data.items`，并补充 `page_count`、`item_count` 和下一页标记。

## 输出建议

优先输出可直接复盘的结果：相关样本和主要角度，并标出下一步可继续追问的问题。

先把可见证据和你的判断分开写；当用户需要可追溯结论时，保留有用的内容 ID、链接、标题或描述、作者、数据指标和发布时间。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `youtube_search_videos`

不要只因为某一页 `items` 为空就判断没有更多结果。

## 安全边界

这是只读 skill。CLI 使用已有环境凭证或用户本地保存的私有凭证文件；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：内容样本=标题/作者/链接或 ID；判断=相关原因和下一步。

## 异常处理

- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中用 `auth status` 确认环境或本地文件来源；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时按「API Key 获取」由用户本地隐藏录入；不要输出 Key、Authorization header 或秘密配置值。

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，按上述实际凭证来源核对配置，并检查参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。

## 常见问题

- 没结果：放宽关键词、减少限定，或换成更贴近用户表达的词。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先按上述实际凭证来源核对 CLI 或 MCP 的生效配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
