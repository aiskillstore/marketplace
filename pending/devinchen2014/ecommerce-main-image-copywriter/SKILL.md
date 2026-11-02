---
name: "ecommerce-main-image-copywriter"
description: "当用户需要提炼商品主图卖点、主副标题或安排商品图片信息层次时使用。提供商品链接或商品资料，输出主图标题、副标题、卖点短句与配图建议；可按需参考同类商品。在线商品能力支持抖音与小红书，已有资料可直接写作。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "ecommerce-main-image-copywriter"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[],"emoji":"✍️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 商品主图卖点文案

## 适用场景

当用户需要提炼商品主图卖点、主副标题或安排商品图片信息层次时使用。提供商品链接或商品资料，输出主图标题、副标题、卖点短句与配图建议；可按需参考同类商品。在线商品能力支持抖音与小红书，已有资料可直接写作。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供目标商品链接或商品资料；受众、平台、语气和篇幅有要求时一并说明。
- 已有资料直接写作；支持的商品链接先读详情，仅按明确需求参考少量同类商品。
- 得到主图标题、副标题、卖点短句与配图建议，并标明来源与待补信息。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest douyin product-detail \
  --product-id "<product_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-main-image-copywriter

npx -y socialdatax-skills@latest douyin product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-main-image-copywriter

npx -y socialdatax-skills@latest xhs product-detail \
  --sku-id "<sku_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-main-image-copywriter

npx -y socialdatax-skills@latest xhs product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-main-image-copywriter

npx -y socialdatax-skills@latest douyin product-search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-main-image-copywriter

npx -y socialdatax-skills@latest xhs product-search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-main-image-copywriter
```

## 参数说明

详情：
- 说明：抖音商品详情：使用 `douyin product-detail --product-id <product_id>` 或 `--url <url>`，二选一；不要把作品 ID 当作商品 ID。
- 说明：小红书商品详情：`xhs product-detail --sku-id <sku_id>` 或 `--url <url>`；sku_id 与抖音 product_id 不能混用。

通用：
- 说明：商品搜索仅用于用户要求的同类参考：`douyin product-search --keyword <text>` 或 `xhs product-search --keyword <text>`，使用目标平台与实际商品类目；默认1页，不自动续页。
- 说明：小红书商品搜索不使用抖音价格、排序或店铺筛选参数。未指定预算与排序时不自行添加条件。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill ecommerce-main-image-copywriter`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先判断输入：已有足够商品资料时直接写作，不强制配置 API Key 或额外调用；用户给抖音/小红书商品链接或对应商品 ID 时，配置 `SOCIALDATAX_API_KEY` 后读取目标商品详情。现有资料有明确缺口且用户要求在线补充时才补查。
在线只支持抖音和小红书商品。其他平台的商品链接不自动读取，请用户粘贴名称、规格、特点及需要保留的价格条件；不声称已打开不支持的链接。只有类目而无具体商品时先请用户给目标商品或资料，不将候选商品当成用户自有商品。
仅在用户明确需要参考同类商品时，使用目标平台的商品搜索，先取1页、最多参考3个相关商品，必要时复核其中最多2个详情；不默认翻页或扫描全市场。只参考表达角度和信息结构，改写为本商品可证实的内容，不复制竞品文案，不把竞品参数、认证或卖点移到本商品。
事实只来自目标商品实际返回或用户提供的资料，保留商品链接/ID、平台及查询时间；纯资料模式注明用户提供。缺失的材质等级、性能时长、认证、销量、评价、优惠与售后不推断。来源冲突时标记并请用户核实，不选更有利于营销的数值。
把事实与建议表达区分开：宣传语不等于独立验证；不写无依据的第一、最好、疗效或收益保证。价格、券后价、规格和活动有效条件保持完整，正式使用前提醒核对变动项。缺少关键事实时列出待补项，仍可基于已知事实交付有用草稿。
默认给出3套不同角度的主图文案，每套聚焦一个有依据的核心价值，包含主标题、副标题、最多3条卖点短句和配图建议；用户指定数量、字数或图位时以其要求为准。
主标题便于快速阅读，副标题解释利益点，卖点短句用实际规格或特点支撑；配图建议说明展示哪个部位或使用场景，不声称已生成、编辑或验证图片。

## 输出建议

优先交付可复制的主图卖点文案，将核实事项放在正文之后。

主图文案表：角度、主标题、副标题、卖点短句、建议画面。
附每套主张的事实依据与缺失信息；不生成图片文件，也不承诺点击率提升。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_get_product_detail_by_product_id`
- `douyin_get_product_detail_by_url`
- `xhs_get_product_detail_by_sku_id`
- `xhs_get_product_detail_by_url`
- `douyin_search_products`
- `xhs_search_products`

## 安全边界

这是只读 skill。已有商品资料时直接写作；仅在线商品调用需要 Node.js/npm 和 `SOCIALDATAX_API_KEY`。命令只读取商品信息，不发布商品、图片或视频，不执行账号修改。生成文件不包含 API Key。

## 示例结果

- 示例请求：根据这份保温杯资料给我3套主图文案，主标题不超过8个字，只要文案和画面建议。

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
- 想继续优化：补充目标受众、平台、真实商品特点或需要修改的段落。
