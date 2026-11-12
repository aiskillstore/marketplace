---
name: "hongguo-drama-review"
description: "当用户提供红果剧名、剧集链接或 series_id，需要短剧口碑复盘、剧情争议分析、角色反馈整理或多部剧观众评价对比时使用。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "hongguo-drama-review"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🎬","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 红果短剧口碑复盘

## 适用场景

当用户提供红果剧名、剧集链接或 series_id，需要短剧口碑复盘、剧情争议分析、角色反馈整理或多部剧观众评价对比时使用。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供红果剧名、剧集分享链接/文案或series_id；默认复盘指定的1–3部剧。
- 每部默认最多2页、20条主剧评；默认不读回复，必要时只补1条核心争议的一页回复。
- 交付剧评样本说明、口碑主题、评论证据与最多3项复核建议。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。
- 先确认调用方式和命令实际运行位置：已认证的 hosted MCP 不要求本地 CLI 变量或 Node/npm；需要 Key 的直接 CLI 则在同一执行环境用下方命令检查。已能读取就继续原任务，不覆盖已有配置。不能运行命令或缺少 Node.js 属于执行环境问题，不能当成 Key 缺失；仅在确认用户没有 Key 时，才引导从上述官网获取。
- 本地 Agent：优先用客户端官方支持的持久化 Secret / env，并确认它注入 Agent 命令进程。WorkBuddy 可在当前可信工作空间的 `.codebuddy/settings.local.json` 中合并 `{"env":{"SOCIALDATAX_API_KEY":"<YOUR_API_KEY>"}}`，保留其他设置和 env；此路径只适用于 WorkBuddy，作用域只限该工作空间。真实 Key 由用户本地填写，文件不提交版本库。
- 远程 Agent：在实际运行命令的远程主机或服务配置客户端持久化 Secret / env，按该客户端的官方方式重新加载执行进程，并在同一远程会话检查；本机系统变量不会自动传到远程。不要因本机检查成功就认定远程也可用。
- 容器或云端沙箱 Agent：优先用平台支持的持久化 Secret / 环境变量注入功能，让它进入执行 CLI 的容器或沙箱；配置后按平台说明重建或重新加载，再在其中检查。不要改宿主机变量来代替沙箱注入；若平台无法持久保存或注入，说明限制并引导用户使用平台支持的鉴权方式，不绕过隔离。
- 检查为 false 时，先逐项排查：配置文件或 Secret 是否位于正确主机、工作空间和作用域，工作空间是否可信，字段是否正确且保留了已有设置，变量是否注入命令进程（仅 MCP server 的 env 不算），以及是否按官方说明重新加载或完全重启。修正后在原执行环境复查；只有明确不支持客户端持久化，或完成上述排查仍不可用，才用该环境官方支持的用户级/服务级环境变量兜底。不能仅因一次检查或重新加载失败就跳到系统配置。
- 系统兜底按实际执行主机处理：Windows 可用用户环境变量；macOS 可由用户在本机终端隐藏输入（如 Bash `read -s`）后传给 `launchctl setenv`，仅对当前登录会话有效，重登或重启电脑后需重新加载。输入失败、空输入或设置失败时明确报错并停止，返回非零退出码；清理临时变量不能覆盖原错误状态。配置后完全退出对应客户端及后台进程再打开；远程服务按其运行方式重载，沙箱仍通过平台注入。单独终端临时 `export`、只写 shell 启动文件或只关窗口都不能证明 Agent 已继承。真实 Key 不出现在聊天、日志、截图、命令历史或 Skill 文件里。
- 在实际执行 CLI 的同一环境运行 `node -e "console.log(JSON.stringify({apiKeyReadable:Boolean(['SOCIALDATAX_API_KEY','SOCIAL_MEDIA_MCP_API_KEY'].map(name=>process.env[name]?.trim()).find(Boolean))}))"`，只报告布尔结果，不打印 Key 或全部环境变量。检查遵循 CLI 的顺序：先读取去除首尾空白后的主变量，再兼容既有旧变量；新增配置仍统一用 `SOCIALDATAX_API_KEY`。`apiKeyReadable: false` 时停止业务调用并按上面的顺序排查；`true` 只证明存在可读取的非空值，继续原业务请求验证鉴权，不代表 Key 有效或余额充足。不要在检查命令里临时注入变量制造成功。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest hongguo series-detail \
  --url "<series_share_url_or_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill hongguo-drama-review

npx -y socialdatax-skills@latest hongguo comments \
  --url "<series_share_url_or_text>" --pages 2 --max-items 20 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill hongguo-drama-review
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest hongguo search \
  --keyword "<keyword>" --pages 1 --max-items 10 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill hongguo-drama-review

npx -y socialdatax-skills@latest hongguo series-detail \
  --series-id "<series_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill hongguo-drama-review

npx -y socialdatax-skills@latest hongguo comments \
  --series-id "<series_id>" --pages 2 --max-items 20 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill hongguo-drama-review

npx -y socialdatax-skills@latest hongguo replies \
  --series-id "<series_id>" --comment-id "<comment_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill hongguo-drama-review
```

## 参数说明

搜索：
- 说明：默认每部最多2页、20条主剧评；用户明确需要时再扩大范围。CLI 使用 --pages / --max-items，MCP 逐页读取并在分析侧执行同样上限，不传这两个 CLI 专用参数。

评论 / 回复：
- 说明：续页原样传回完整 next_page_token；同一剧集和回复层级保持不变，空令牌停止。

通用：
- 说明：提供剧集分享链接、整段分享文案、series_id 或剧名之一。只有剧名时先用综合搜索定位；同名作品不明确时请用户选择，不把搜索结果当榜单。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill hongguo-drama-review`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

## 复盘流程

1. 确认用户指定的1–3部剧集。用链接或series_id读取详情，核对剧名和身份；只给剧名时才先搜索。超过3部先请用户选首批，不自行扩大题材或演员名单。
2. 每部按默认上限读取整剧剧评，以comment_id去重，记录原始条数、去重后条数、观察时间和分页是否结束。正文在data.items，续页令牌在data.next_page_token；列表总计数字不等于已分析样本量。
3. 将实际评论归为剧情节奏、角色/演员、情绪与爽点、结局等出现的主题；每个主题给简短原话和评论ID。评论对剧情的描述标为观众观点，不当作已核实剧情或作者亲自看剧所得。
4. 默认不读回复；某条核心争议确需上下文且主评有回复时，最多补1条主评下的一页二级回复。使用items中的series_id和comment_id，level=2；主评与回复分别计数，不把回复当独立观众。
5. 多剧比较保持相同页数/条数上限，逐剧列明实际覆盖。若评分字段存在，报告其原始值和口径；没有评分量表说明时不自行换算星级或平台总分。
6. 给出最多3项面向编剧、内容运营或发行方的复核建议，每项对应主题与证据。样本有限、失败或无评论时保留已有结果，明确范围；无评论时不生成口碑结论。

## 输出建议

交付一份带评论证据的简短口碑复盘，单剧无需强制输出多剧对照表。

1. 样本范围：剧名、series_id/原始来源链接、观察时间、页数、去重前后主评数、回复数、未完成项。
2. 口碑主题表：主题、正向/负向/混合反馈、简短原话、评论ID；仅在完整统计时列提及条数及样本分母，多主题可重叠。
3. 主要争议、角色反馈与最多3项待核实或改进建议；多剧时补同口径对照。
4. 说明样本偏差与缺失数据。不从评论推断弃剧率、具体集数导致弃剧、完播率或付费转化，不把样本情绪比例称为平台口碑率；不生成官方周榜、历史排名或市场热度趋势。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `hongguo_get_series_detail_by_url`
- `hongguo_get_series_comments_by_url`
- `hongguo_search_general`
- `hongguo_get_series_detail_by_series_id`
- `hongguo_get_series_comments_by_series_id`
- `hongguo_get_series_comment_replies_by_comment_id`

已配置红果 MCP 时，可使用 hongguo_search_general、hongguo_get_series_detail_by_series_id / hongguo_get_series_detail_by_url、hongguo_get_series_comments_by_series_id / hongguo_get_series_comments_by_url 和 hongguo_get_series_comment_replies_by_comment_id。
本流程只复盘整剧剧评，不自动扩展到单集视频评论、下载或转写。

## 安全边界

这是只读 skill。在线详情和剧评查询由 SocialDataX 服务处理用户提供的链接、剧名或ID，使用运行时配置的 SOCIALDATAX_API_KEY；Skill文件不含真实Key。不登录、发评论、联系用户、下载视频或改动账号。

## 示例结果

- 格式示例：节奏争议 → 评论原话/ID → 样本提及条数及分母 → 需要核实的具体问题；不是实际剧评数据。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中按「API Key 获取」的检查规则排查生效配置（主变量优先，兼容既有旧变量）；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时沿用前面的客户端排查与兜底顺序；不要输出 Key、Authorization header 或秘密配置值。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足且非限流的网络或 API 异常：保留错误信息，按上述实际凭证来源核对配置，并检查参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。
- 批量处理：默认按队列逐条处理；用户明确需要批量效率时，最多同时处理 3 条。每完成 1 条，就继续处理下一条，不要一次性发起大量请求。遇到 `rate_limited` 或“请求过于频繁”时，不要放弃任务；先停止发起新的请求，按返回的等待时间等待，没有等待时间就先等待 2 秒，然后继续处理当前队列。等待期间已完成的结果要保留；恢复后继续从未完成的位置处理。遇到 `insufficient_balance` 或“积分不足”时，立即停止后续请求，输出已获得结果，并提示充值或切换有余额的 API Key 后继续。

## 常见问题

- 没结果：放宽关键词、减少限定，或换成更贴近用户表达的词。
- 结果太多：补场景、人群、品牌、时间范围或账号名。
- 调用失败：先按「异常处理」核对本次调用实际使用的凭证来源；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 继续复盘：明确同一剧集需要扩大到多少页或多少条，保留已有样本和完整续页令牌。
