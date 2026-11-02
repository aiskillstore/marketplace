---
name: "ecommerce-review-insights"
description: "当用户需要归纳商品评价中的优缺点、购买顾虑和改进建议时使用。支持各平台提供的评价文本或表格，也可通过小红书商品链接或sku_id在线分析评价。输出带原话依据、评价条数与范围说明的主题表；已有资料可直接分析。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "ecommerce-review-insights"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[],"emoji":"📝","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 商品评价分析

## 适用场景

当用户需要归纳商品评价中的优缺点、购买顾虑和改进建议时使用。支持各平台提供的评价文本或表格，也可通过小红书商品链接或sku_id在线分析评价。输出带原话依据、评价条数与范围说明的主题表；已有资料可直接分析。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供评价文本、可读取的表格，或小红书商品链接/sku_id；有商品规格、时间范围或关注问题时一并说明。
- 已有评价资料直接分析；小红书商品链接先读取详情取得sku_id，再读取评价，已有sku_id直接读取评价；默认一页，按需继续。
- 得到评价主题、样本条数、原话依据、改进建议与不足说明。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-review-insights

npx -y socialdatax-skills@latest xhs product-reviews \
  --sku-id "<sku_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-review-insights

npx -y socialdatax-skills@latest xhs product-review-replies \
  --review-id "<review_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-review-insights

npx -y socialdatax-skills@latest xhs product-review-reply-replies \
  --review-id "<review_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-review-insights
```

## 参数说明

搜索：
- 说明：评价排序：`--sort-type general`（默认）或 `--sort-type time_descending`；只看带图评价时用 `--has-image true`，并在结果中说明筛选偏差。

评论 / 回复：
- 说明：一级评价下回复：`xhs product-review-replies --review-id <review_id>`，ID取自评价结果；嵌套回复：`xhs product-review-reply-replies --review-id <review_id>`，ID取自上一步回复结果，不传root_review_id。
- 说明：评价及回复翻页：将实际返回的完整 `next_page_token` 原样传入 `--page-token`，不截断、改写或自行构造；这些命令不使用 `--max-pages` 或 `--include-replies`。

通用：
- 说明：商品链接或完整分享文案：先用 `xhs product-detail --url <url_or_share_text>`；成功后将实际返回的 `sku_id` 传给评价命令。不要把商品链接直接传给product-reviews。
- 说明：在线评价：`xhs product-reviews --sku-id <sku_id>`；只接受商品sku_id，不接受商品链接、spu_id、笔记ID或关键词。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill ecommerce-review-insights`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先按输入选择模式：已有评价文本或可读取表格直接分析，不要求Key或在线查询；文件无法读取时请用户导出CSV或粘贴文本。在线模式需要SOCIALDATAX_API_KEY：已有小红书商品sku_id时直接读评价；只有商品链接或完整分享文案时先调用商品详情URL入口，确认成功并取得实际返回的sku_id，再读评价。详情失败或未返回sku_id时说明原因，请用户补充sku_id或评价资料，不从链接自行猜ID；spu_id、笔记ID和其他平台商品不能替代sku_id。
在线默认只读取一页评价并说明排序、筛选与已读取条数。用户需要更多样本时按返回next_page_token继续；没有令牌、令牌重复或已满足约定范围时停止。部分页失败时保留已取得样本并说明缺口，不宣称全量覆盖；没有返回评价时不编造结论。
仅当用户关注讨论或某条评价需要回复语境时，按真实review_id读取该评价下回复，必要时再读取嵌套回复；不默认展开全部回复。评价正文和回复分开统计，回复不增加购买评价的分母；不把笔记评论当商品评价。
为每条评价保留原始行号或评价ID，区分评价正文、商家回复与追评。缺少ID的文本相同只能标记疑似重复，不能直接删掉或判定刷评；同一ID重复导出可去重并说明原始数、去重规则和分析数。用户明确要求按文本去重时保留去重前后数量。
按质量、使用体验、规格适配、包装配送、服务等实际出现的主题归纳，不为凑类别制造结论。一条评价可以同时包含正负面感受和多个主题；每个主题按涉及的评价记录数计数，同一记录同主题只计一次。
有实际完整计数时给出主题提及条数与分母；多主题占比之和可能超过100%。数据较大无法完整统计时只分析明确标注的子集，不外推全量。不把样本负向提及比例称为投诉率、全店差评率、退货率或真实购买人群比例。
引用简短原话并保留行号/评价ID，隐藏手机号、订单号、地址等与主题无关的个人信息。评价是用户陈述，不直接等于已验证的产品缺陷；矛盾体验分别呈现，缺少星级、日期、规格或购买状态时不补造。
每个优先改进项对应一个实际主题和证据，区分产品核查、描述预期调整与客服说明；次数少但可能严重的问题可单列待核实，不伪造销量、评分或评价，不建议批量刷好评或隐瞒负面反馈。

## 输出建议

交付一份可追溯的评价样本分析，先给结论，再给证据与限制。

样本说明：商品、资料来源、已知时间/筛选范围、原始条数、去重规则、实际分析条数及缺失字段。
评价主题表：主题、正向/负向/混合、涉及评价条数及分母、简短原话与行号/ID、可能需要核实的问题。
最后给出最多3项优先改进或验证建议，并说明样本偏差；没有评价正文时不输出伪造洞察。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_get_product_detail_by_url`
- `xhs_get_product_reviews`
- `xhs_get_product_review_replies`
- `xhs_get_product_review_reply_replies`

## 安全边界

这是只读 skill。已有评价资料直接分析；只有在线商品详情、评价和回复需要 Node.js/npm 与 SOCIALDATAX_API_KEY，生成文件不含API Key。不执行登录、联系买家、发布评价、退款或账号操作。

## 示例结果

- 格式示例：5条评价中2条提及某问题 → 列出对应行号和原话；这是样本提及情况，不称全店投诉率。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- CLI 退出码为 1 且输出 `partial: true` 时，保留 `data.items` 和错误，明确结果不完整。此时按以下续页规则恢复，不适用原命令重跑建议；错误解决后（包括充值后），仅用非空的 `data.next_page_token` 和原查询条件继续。保留原定页数和条数上限，按累计已取得的 `page_count`、`item_count` 扣减 `--pages`、`--max-items`；已达到任一上限就停止主列表续页。空令牌不代表取完，不要从第一页自动重跑；因重复令牌中断时，先排查原因。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 重试仍失败：说明当前调用不可用，请用户补充或更换关键词、链接、ID 等输入后再重试。

## 常见问题

- 没结果：确认输入对象完整，再缩小分析范围。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：补充评价资料，或按完整next_page_token继续读取小红书评价；比较时保持相同排序、筛选和统计口径。
