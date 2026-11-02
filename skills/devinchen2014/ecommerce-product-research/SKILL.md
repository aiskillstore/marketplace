---
name: "ecommerce-product-research"
description: "提供商品类目或已有商品资料，整理电商选品候选清单，列出可见价格、匹配条件、入选理由和待核实事项。预算与受众有则提供；已有资料可直接分析，无需 API Key。在线商品查询支持抖音与小红书。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "ecommerce-product-research"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[],"emoji":"🛍️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 电商选品研究

## 适用场景

提供商品类目或已有商品资料，整理电商选品候选清单，列出可见价格、匹配条件、入选理由和待核实事项。预算与受众有则提供；已有资料可直接分析，无需 API Key。在线商品查询支持抖音与小红书。来自 SocialDataX 社媒数据助手。

## 快速开始

- 给出商品类目或粘贴已有商品资料；预算、受众和筛选条件有则提供。例如：“帮我初筛抖音上 100 元以内的通勤保温杯，列出入选理由和待核实事项。”
- 已有商品资料直接分析，无需 API Key；在线查询需配置 SOCIALDATAX_API_KEY，仅支持抖音和小红书。需要在线查询时，先取 1 页候选，最多展示 5 项，并复核最相关的 2–3 个商品。
- 得到候选商品表：可见价格、匹配条件、入选理由、来源与待核实事项，以及优先复核的建议。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest douyin product-search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-product-research

npx -y socialdatax-skills@latest douyin product-detail \
  --product-id "<product_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-product-research

npx -y socialdatax-skills@latest douyin product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-product-research

npx -y socialdatax-skills@latest xhs product-search \
  --keyword "<keyword>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-product-research

npx -y socialdatax-skills@latest xhs product-detail \
  --sku-id "<sku_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-product-research

npx -y socialdatax-skills@latest xhs product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-product-research
```

## 参数说明

搜索：
- 说明：抖音 `--sort-type` 可选 `general`、`sales_descending`、`price_ascending`、`price_descending`；默认 general，不把排序位置解释成全平台销量排名。

详情：
- 说明：抖音商品详情：使用 `douyin product-detail --product-id <product_id>` 或 `--url <url>`，二选一；不要把作品 ID 当作商品 ID。
- 说明：小红书商品详情：`xhs product-detail --sku-id <sku_id>` 或 `--url <url>`；sku_id 与抖音 product_id 不能混用。
- 说明：先取 1 页，展示其中最多 5 个匹配商品，再复核其中 2–3 个详情；扩大范围时使用当前命令返回的完整 `--page-token <next_page_token>`，保持平台、关键词和筛选不变，不默认遍历所有结果。

通用：
- 说明：抖音商品搜索：`douyin product-search --keyword <text>`，使用用户指定的类目或商品关键词。
- 说明：小红书商品搜索：`xhs product-search --keyword <text>`；只使用关键词和续页 `--page-token`，不传抖音的价格、排序、官方店等参数，预算在结果中按可见价格筛选。
- 说明：抖音搜索支持 `--min-price` / `--max-price`，均为大于 0 的整数、单位元，最小值不能大于最大值；用户未指定则省略。
- 说明：抖音可选 `--official-store`、`--dispatch-within-24h`、`--shipping-insurance`、`--seven-day-return`；仅按用户明确条件开启。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill ecommerce-product-research`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先确认目标平台：用户给出平台、可识别的商品链接或明确资料时直接使用；未指定且没有资料时，只询问一次目标平台。在线只支持抖音和小红书。用户给其他平台的商品表格或文字资料时直接基于资料分析；仅给不支持平台的链接时，请其粘贴商品信息，不声称已读取该链接。
纯用户资料分析不需要 API Key；调用在线商品命令前需配置 `SOCIALDATAX_API_KEY`。不要为了分析已提供的资料强制在线补查。
用户给类目即可开始；目标客群、预算、店铺和服务条件已有就使用，不要求用户先填长表。需要在线查询时，先按平台支持的条件取 1 页候选，再读取最相关的 2–3 个商品详情复核，不为凑满清单扩大调用。
入选理由依据用户条件和实际返回的商品信息；不合条件的商品说明原因，数量不足时报告实际数量。样本价格分布只能描述当前候选，不代表全市场价格带或市场规模。
只引用实际返回或用户提供的名称、价格、规格、店铺、描述及其他可见信息；没有的字段标记“未提供/未返回”。保留链接或商品 ID、来源平台和观察时间，将商品宣传语与独立证据分开。
未接入本流程的商品评价不得从作品评论代替；不推断真实销量、增长率、市场占有率或爆款概率。利润测算需用户提供成本与费用，未提供时不估算利润。默认交付 Markdown 表格；用户需要导出报告时再整理，不自动引入图表库或复杂页面。

## 输出建议

优先交付简洁、可追溯的选品初筛清单。

候选清单：商品/平台/ID或来源链接/可见价格及口径/匹配条件/入选理由/待核实事项。
结尾给出优先复核的 2–3 项与具体原因，说明本次条件、观察时间、返回范围和不足；这是选品初筛，不是销量或收益承诺。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_search_products`
- `douyin_get_product_detail_by_product_id`
- `douyin_get_product_detail_by_url`
- `xhs_search_products`
- `xhs_get_product_detail_by_sku_id`
- `xhs_get_product_detail_by_url`

## 安全边界

这是只读 skill。已有商品资料直接分析；只有在线商品查询需要 Node.js/npm 与 SOCIALDATAX_API_KEY，生成文件不含API Key。不登录、不发帖、不联系商家、不修改商品或账号。

## 示例结果

- 格式示例：候选商品 → 匹配条件、可见价格、入选理由、来源、待核实项；不填虚构评分。

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
- 想继续分析：补充商品资料或明确要深入比较的维度。
