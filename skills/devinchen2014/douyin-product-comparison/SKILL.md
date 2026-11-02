---
name: "douyin-product-comparison"
description: "当用户需要对比已选商品、比较规格和卖点差异，或准备竞品对照表时使用。输入 2–5 个抖音商品链接或商品 ID，输出注明价格口径、信息缺口和来源的商品差异表。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "douyin-product-comparison"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"⚖️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 抖音商品竞品对比

## 适用场景

当用户需要对比已选商品、比较规格和卖点差异，或准备竞品对照表时使用。输入 2–5 个抖音商品链接或商品 ID，输出注明价格口径、信息缺口和来源的商品差异表。来自 SocialDataX 社媒数据助手。

## 快速开始

- 输入 2–5 个商品链接、平台商品 ID 或商品资料，并说明最关注的差异。
- 只比较用户选定的商品；先核对规格与价格口径。
- 得到带来源、缺失项与适用场景的商品对比表。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest douyin product-detail \
  --product-id "<product_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill douyin-product-comparison

npx -y socialdatax-skills@latest douyin product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill douyin-product-comparison
```

## 参数说明

详情：
- 说明：抖音商品详情：使用 `douyin product-detail --product-id <product_id>` 或 `--url <url>`，二选一；不要把作品 ID 当作商品 ID。

通用：
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill douyin-product-comparison`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

用户提供 2–5 个具体商品后，按所属平台逐个读取商品详情；只有 1 个商品时，提示补充对照对象。不要自行扩大到类目搜索或替用户选定竞争对手。
先核对商品规格、包装数量、单位和价格条件是否可比；不同 SKU、券后价、活动价、价格区间分开标注。只有单位和数量明确时才计算单位价格；缺少依据时不强行排名。
只引用实际返回或用户提供的名称、价格、规格、店铺、描述及其他可见信息；没有的字段标记“未提供/未返回”。保留链接或商品 ID、来源平台和观察时间，将商品宣传语与独立证据分开。
未接入本流程的商品评价不得从作品评论代替；不推断真实销量、增长率、市场占有率或爆款概率。利润测算需用户提供成本与费用，未提供时不估算利润。默认交付 Markdown 表格；用户需要导出报告时再整理，不自动引入图表库或复杂页面。

## 输出建议

优先交付简洁、可追溯的商品差异表。

商品对比表：商品/平台/ID或来源链接/规格与数量/价格及条件/可见卖点/缺失信息。
按用户关注维度说明差异、适合的使用场景及下一步核实项；没有充分证据时不选“最优商品”。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_get_product_detail_by_product_id`
- `douyin_get_product_detail_by_url`

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 格式示例：商品 A / 商品 B → 同规格价格口径、可见信息差异、来源与待核实项；仅填真实数据。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 重试仍失败：说明当前调用不可用，请用户补充或更换关键词、链接、ID 等输入后再重试。

## 常见问题

- 没结果：确认输入对象完整，再缩小分析范围。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：补充商品资料或明确要深入比较的维度。
