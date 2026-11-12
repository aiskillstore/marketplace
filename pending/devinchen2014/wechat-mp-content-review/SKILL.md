---
name: "wechat-mp-content-review"
description: "当用户提供公众号文章链接、账号 ID 或明确的文章名单，需要公众号内容复盘、近期推文对比、题材表现分析或读者反馈整理时使用。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "wechat-mp-content-review"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📰","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 公众号内容复盘

## 适用场景

当用户提供公众号文章链接、账号 ID 或明确的文章名单，需要公众号内容复盘、近期推文对比、题材表现分析或读者反馈整理时使用。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供公众号文章链接/分享文案、account_id或至多10篇文章名单；昵称不足以直接定位账号。
- 账号文章列表最多3页、至多10篇；正文默认补2–3篇、评论最多补2篇各1页。
- 交付近期文章对照表、实际可见互动数据、代表文章与读者反馈、下一轮选题建议。

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
npx -y socialdatax-skills@latest wechat article \
  --url "<mp_article_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-mp-content-review

npx -y socialdatax-skills@latest wechat mp-account-articles \
  --account-id "<account_id>" --pages 3 --max-items 10 --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill wechat-mp-content-review

npx -y socialdatax-skills@latest wechat article-stats \
  --url "<mp_article_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-mp-content-review
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest wechat mp-account-info \
  --account-id "<account_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-mp-content-review

npx -y socialdatax-skills@latest wechat article-comments \
  --url "<url>" --pages 1 --max-items 20 --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-mp-content-review

npx -y socialdatax-skills@latest wechat article-replies \
  --url "<url>" --comment-id "<comment_id>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill wechat-mp-content-review
```

## 参数说明

搜索：
- 说明：CLI --pages / --max-items在客户端限量，MCP不接受这两个参数；直接MCP调用时逐页读取并在分析侧执行相同上限。

创作者 / 账号：
- 说明：提供一篇该公众号文章的mp.weixin.qq.com链接/完整分享文案，或account_id；也可直接给出至多10篇文章链接。只有昵称时请补文章链接或账号ID，不把昵称传给account-id。
- 说明：默认观察账号至多10篇文章，列表最多读取3页；用户指定文章名单时只处理该名单。续页原样传回完整next_page_token，空令牌停止。

通用：
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill wechat-mp-content-review`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

## 复盘流程

1. 文章链接先调用wechat article取得account.account_id，再读取账号资料确认身份；已有account_id时直接复用。给定文章名单时核对账号归属，多账号分别呈现，不混作一个账号。
2. 账号模式读取文章列表；第一页不足10篇且有next_page_token时继续，直到取得10篇或达到3页/末页。按返回文章ID或规范链接去重，记录可见发布时间。只有时间和顺序足够确认时才称“最近10篇”，否则称本次取得的至多10篇样本并说明覆盖限制。
3. 逐篇查询article-stats，保留观察时间。失败、null和未返回分别记录，不补零、不反复重试；统计失败不阻止继续复盘其他文章。仅有read_count等正数分母且分子存在时计算点赞数/阅读数等比值，名称写出分子和分母。
列表中断或CLI返回partial时，保留已取得的文章、错误和完整next_page_token，报告覆盖不完整。本规则优先于异常处理中的原样重试建议：解决错误后只用非空令牌续取，并从3页/10篇总上限扣除已用页数和条数，不从第一页重跑；空令牌不能证明已取完。
4. 先用标题与摘要初分题材；默认再读取2–3篇代表文章正文核实角度、结构和读者价值，不为每篇强制补全文。最多选2篇代表文章各取1页、20条评论；整份报告最多为1条关键评论补1页回复，需该评论有回复且确需上下文；将实际返回的comment_id传给article-replies，不省略comment-id自动选取其他评论。
5. 对照题材、发布时间与实际阅读互动；注明统计是查询时累计值，文章发布时长不同。各题材列文章数、有效统计数，区分样本表现与原因假设；内容判断对应正文证据，读者反馈对应评论原话/ID。
6. 给最多3条下一轮选题或表达建议，分别写依据和待验证点。没有正文不评价正文质量，没有评论不推断读者态度，没有有效统计不选“表现最佳题材”。

## 输出建议

交付一份可用于运营复盘的简短报告，数据表只填写本次实际获得的值。

1. 账号与样本说明：账号ID、观察时间、覆盖文章数、分页范围、失败及缺失项。
2. 逐篇对照表：标题、原始文章链接、发布时间、题材（标题初判或正文核实）、实际阅读/点赞/推荐/分享/收藏/评论数据；缺失明确标注。
3. 代表文章的内容角度与读者反馈，引用短句和原始链接/评论ID；题材比较注明组内文章数和有效统计数。
4. 最多3条下一轮选题或表达测试建议，以及数据限制。没有送达/曝光、阅读完成、关注归因和收入数据时，不计算打开率、完读率、涨粉效果、推荐流量占比或收益，不将公开互动推断为后台效果或因果结论。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `wechat_get_mp_article_detail_by_url`
- `wechat_get_mp_account_articles_by_account_id`
- `wechat_get_mp_article_stats_by_url`
- `wechat_get_mp_account_info_by_account_id`
- `wechat_get_mp_article_comments_by_url`
- `wechat_get_mp_article_comment_replies_by_url`

已配置微信内容 MCP 时，使用 wechat_get_mp_article_detail_by_url、wechat_get_mp_account_info_by_account_id、wechat_get_mp_account_articles_by_account_id、wechat_get_mp_article_stats_by_url、wechat_get_mp_article_comments_by_url 和 wechat_get_mp_article_comment_replies_by_url。
本流程面向公众号文章，不将文章链接交给视频号搜索、作品详情或转写工具。

## 安全边界

这是只读 skill。用户提供的文章链接或账号ID由 SocialDataX 服务用于在线查询，使用运行时配置的 SOCIALDATAX_API_KEY；Skill文件不含真实Key。不登录公众号后台、发布文章、回复读者、发送消息或变更账号。

## 示例结果

- 格式示例：文章/发布时间/题材/可见阅读与互动/数据缺失 → 代表证据 → 下一轮验证建议；不是实际账号数据。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中按「API Key 获取」的检查规则排查生效配置（主变量优先，兼容既有旧变量）；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时沿用前面的客户端排查与兜底顺序；不要输出 Key、Authorization header 或秘密配置值。
- 非余额不足且非限流的网络或 API 异常：保留错误信息，按上述实际凭证来源核对配置，并检查参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。
- 批量处理：默认按队列逐条处理；用户明确需要批量效率时，最多同时处理 3 条。每完成 1 条，就继续处理下一条，不要一次性发起大量请求。遇到 `rate_limited` 或“请求过于频繁”时，不要放弃任务；先停止发起新的请求，按返回的等待时间等待，没有等待时间就先等待 2 秒，然后继续处理当前队列。等待期间已完成的结果要保留；恢复后继续从未完成的位置处理。遇到 `insufficient_balance` 或“积分不足”时，立即停止后续请求，输出已获得结果，并提示充值或切换有余额的 API Key 后继续。
- 重试仍失败：说明当前调用不可用，请用户补充或更换关键词、链接、ID 等输入后再重试。

## 常见问题

- 没结果：确认链接或 ID 完整；必要时先用内容研究类 skill 找到目标内容。
- 调用失败：先按「异常处理」核对本次调用实际使用的凭证来源；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 继续复盘：提供希望比较的文章或扩大范围；保留已有成功结果，失败和缺失统计不补零。
