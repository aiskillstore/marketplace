---
name: "ecommerce-live-sales-script"
description: "当用户准备直播带货，需要整场流程、商品讲解、互动问答和转场话术时使用。根据排品清单、真实商品资料与已确认活动规则，输出可照读的话术和时间表。已有资料可直接写；抖音、小红书商品详情可按需补充。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "ecommerce-live-sales-script"
metadata: {"openclaw":{"requires":{"env":[],"bins":[]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[],"emoji":"🎙️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 直播带货话术

## 适用场景

当用户准备直播带货，需要整场流程、商品讲解、互动问答和转场话术时使用。根据排品清单、真实商品资料与已确认活动规则，输出可照读的话术和时间表。已有资料可直接写；抖音、小红书商品详情可按需补充。来自 SocialDataX 社媒数据助手。

## 快速开始

- 提供商品清单、商品资料或链接，以及直播时长；已确认的直播价、优惠规则和讲解重点有则附上。
- 资料足够时直接写；需要补充事实时按需读取抖音或小红书商品详情，不自动开播或生成图片、配音。
- 得到整场时间表、逐商品讲解话术、互动问答、转场与收尾话术。

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
npx -y socialdatax-skills@latest douyin product-detail \
  --product-id "<product_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-live-sales-script

npx -y socialdatax-skills@latest douyin product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-live-sales-script

npx -y socialdatax-skills@latest xhs product-detail \
  --sku-id "<sku_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-live-sales-script

npx -y socialdatax-skills@latest xhs product-detail \
  --url "<url>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill ecommerce-live-sales-script
```

## 参数说明

详情：
- 说明：抖音商品详情：使用 `douyin product-detail --product-id <product_id>` 或 `--url <url>`，二选一；不要把作品 ID 当作商品 ID。
- 说明：小红书商品详情：`xhs product-detail --sku-id <sku_id>` 或 `--url <url>`；sku_id 与抖音 product_id 不能混用。

通用：
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill ecommerce-live-sales-script`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

先整理排品顺序、商品资料、直播时长与已确认活动。已有资料直接起草，不要求Key或额外查询；用户只给抖音/小红书商品链接或对应ID时，配置SOCIALDATAX_API_KEY后按需读取商品详情。其他平台链接请用户粘贴资料，不声称已读取。至少有一个可描述商品再写具体讲解；缺商品事实时只给流程骨架和待补项。
用户已给时长、顺序、目标或主播人数时沿用。未给时长可先按30分钟单主播草拟，开头标明假设；未指定顺序可提出建议并标注。按开场、商品讲解、互动、商品转场和收尾分配连续时段，检查无重叠、无空档且合计等于整场时长。用户只要单品话术时只交付该段，不强制整场表。
逐商品保留名称、SKU/规格、事实来源和价格条件，不把其他商品事实写进本商品。页面价格只代表读取时的页面信息，不自动当作直播价；直播优惠、库存、赠品、活动截止、原价比较及配送承诺只用用户已确认的方案。缺项可省略或单列商家待核实项，不阻断已知内容写作。
每件商品按适用人群与场景、真实特点、可现场演示的用法、常见顾虑、适用限制和自然购买引导来写可照读口播。演示动作写成建议，不把未做测试描述成实测结果；不虚构体验、销量、认证、功效或用户好评。缺库存和活动时间时不写“最后几件”“马上结束”，不制造虚假紧迫感。
互动问题围绕规格选择、使用场景与实际疑问，附自然回应和转场。未知性能、到货时间或售后条件用核实回应，不把“已核实”“已催件”等未发生动作写成事实。内部待确认信息与主播可照读稿分开；不要让主播照读占位符或内部批注。
最后检查口播与商品资料、活动条件一致，标出需复核的绝对化表述或证据缺口并给具体改写建议；不把文案检查称为法律或平台合规保证。仅交付文字草稿，不启动直播、不发送消息、不改价格、不生成音视频或图片。

## 输出建议

交付能用于本场直播的文字稿，时间表与逐商品话术对应。

整场流程表：起止时间、商品或环节、讲解目标、对应话术段；注明总时长和所用假设。
逐商品可照读稿：介绍与场景、特点与演示建议、常见疑问、已确认活动和购买引导；保留规格与条件。
互动问答、商品间转场、收尾话术；最后另列商家待核实事项及事实来源。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `douyin_get_product_detail_by_product_id`
- `douyin_get_product_detail_by_url`
- `xhs_get_product_detail_by_sku_id`
- `xhs_get_product_detail_by_url`

## 安全边界

这是只读 skill。已有资料直接写；只有在线商品详情需要 Node.js/npm 与 SOCIALDATAX_API_KEY，生成文件不含API Key。不自动开播、发消息、改商品价格或库存，不生成图片、配音或视频，不保证成交效果。

## 示例结果

- 场景：30分钟、3件商品，未提供库存和活动截止时间 → 给合计30分钟的连续流程和逐品话术，不编造限量或倒计时，待核实项独立列出。

## 异常处理

- 凭证来源排查：先确认本次调用使用 CLI 还是 MCP。CLI 在实际执行环境中用 `auth status` 确认环境或本地文件来源；MCP 检查当前连接实际使用的鉴权配置，不要求另设本地 CLI 变量。配置缺失时按「API Key 获取」由用户本地隐藏录入；不要输出 Key、Authorization header 或秘密配置值。

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 非余额不足的网络或 API 异常：保留错误信息，按上述实际凭证来源核对配置，并检查参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已充值但仍提示余额不足：请用户按上述实际凭证来源，在对应账号后台确认本次请求使用的账号与充值账号一致；如需更新凭证，在实际生效的 CLI 配置或 MCP 连接中由用户更新并按说明重新加载，再继续原命令。不要仅因本地新变量缺失就要求重新配置，也不要展示凭证明文。
- 重试仍失败：说明当前调用不可用，请用户补充或更换关键词、链接、ID 等输入后再重试。

## 常见问题

- 没结果：确认输入对象完整，再缩小分析范围。
- 调用失败：先按上述实际凭证来源核对 CLI 或 MCP 的生效配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续调整：提供真实活动方案、直播时长、商品顺序或主播语气，更新对应段落。
