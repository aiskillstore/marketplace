---
name: "ecommerce-customer-service"
description: "当用户需要回答商品咨询、整理售前FAQ或起草售后解释时使用。输入商品链接或资料、买家问题与已确认的店铺规则，输出可复制回复和商家待核实事项。在线商品详情支持抖音与小红书，已有资料可直接起草；不自动发送消息或办理售后。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "ecommerce-customer-service"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[],"emoji":"💬","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 商品客服问答

## 适用场景

当用户需要回答商品咨询、整理售前FAQ或起草售后解释时使用。输入商品链接或资料、买家问题与已确认的店铺规则，输出可复制回复和商家待核实事项。在线商品详情支持抖音与小红书，已有资料可直接起草；不自动发送消息或办理售后。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供买家问题与商品链接或资料；店铺政策、已确认处理结果有则附上。
- 已有资料直接起草；支持的商品链接按需读取详情，不查询订单物流或自动处理售后。
- 得到可复制的客户回复，另列商家需要核实的信息。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest douyin product-detail \
  --product-id "<product_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-customer-service

npx -y socialdatax-skills@latest douyin product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-customer-service

npx -y socialdatax-skills@latest xhs product-detail \
  --sku-id "<sku_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-customer-service

npx -y socialdatax-skills@latest xhs product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-customer-service
```

## 参数说明

详情：
- 说明：抖音商品详情：使用 `douyin product-detail --product-id <product_id>` 或 `--url <url>`，二选一；不要把作品 ID 当作商品 ID。
- 说明：小红书商品详情：`xhs product-detail --sku-id <sku_id>` 或 `--url <url>`；sku_id 与抖音 product_id 不能混用。

通用：
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill ecommerce-customer-service`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先提取具体买家问题和已知商品事实。已有足够资料时直接起草，不要求Key或额外查询；用户只给抖音/小红书商品链接或对应ID时，配置SOCIALDATAX_API_KEY后读取商品详情。其他平台链接请用户粘贴商品资料，不声称已读取。
商品详情用于回答规格、材质、使用条件及实际返回的商品信息，不代表订单、库存、物流、退款或售后处理状态。只提供商品名而没有可核实资料时，给出待核实问题和不含虚构参数的简短草稿。
逐条对照买家问题与证据。保温时长、尺寸适配、功效、认证、价格活动、发货及退换条件只用实际资料；来源冲突时指出冲突，保留SKU和价格条件，不选择更有利于成交的说法。
客服回复自然简短，先回答已知问题，再说明下一步。未知参数或到货时间不承诺；把商家需确认的规格、库存、订单状态等列在独立内部清单，不混进可复制给买家的正文。需要处理进度时不写“已催件”“已退款”“已申请”，除非用户明确提供该事实。
补偿金额、退款时效、退换承诺只引用已提供且已授权的方案；没有政策或处理权限时给核实路径，不自行决定接受/拒绝售后，不宣称法律合规已获保证。实际售后争议转交有权限人员核对适用政策和订单资料。
默认仅交付回复草稿。用户要求直接发送、联系买家、退款或改订单时说明本技能没有相应执行能力，不声称已执行。引用资料中的电话、地址、订单信息只保留解决问题所需的最少部分。
用户要知识库时，按问题、建议答复、事实来源、适用条件、待更新项整理FAQ；用户只要一句回复时只给回复，不强制输出整套表格。

## 输出建议

优先交付可直接复制的客服回复，把内部核实事项分开列出。

具体咨询：客户回复草稿；如有缺口，再列商家内部待核实事项与事实来源。
批量FAQ：问题、答复、依据、适用规格/条件、待核实或更新事项。不把建议动作写成已完成的服务。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_get_product_detail_by_product_id`
- `douyin_get_product_detail_by_url`
- `xhs_get_product_detail_by_sku_id`
- `xhs_get_product_detail_by_url`

## 安全边界

这是只读 skill。已有资料直接起草；只有在线商品详情需要 Node.js/npm 与 SOCIALDATAX_API_KEY。本技能不发送消息、不查询订单物流、不退款、不补偿、不修改商品或账号；生成文件不含API Key。

## 示例结果

- 场景：已知500ml旋盖杯，买家问保温多久、明天能否到货 → 不推断时长或配送承诺，给简短核实回复，并单列商家要查的性能与订单信息。

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
- 想继续处理：补充买家追问、真实商品参数或已批准的售后方案，再起草下一条回复。
