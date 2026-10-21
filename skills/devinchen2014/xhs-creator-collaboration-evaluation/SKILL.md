---
name: "xhs-creator-collaboration-evaluation"
description: "用户提供品牌或产品、目标受众、候选小红书达人和预算时，使用蒲公英报价、粉丝画像和内容表现比较合作适配度，交付候选对照表与待确认事项。SocialDataX 支持命令查询；不预测实际成交或投放回报。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "xhs-creator-collaboration-evaluation"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"👤","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 小红书达人合作评估

## 适用场景

用户提供品牌或产品、目标受众、候选小红书达人和预算时，使用蒲公英报价、粉丝画像和内容表现比较合作适配度，交付候选对照表与待确认事项。SocialDataX 支持命令查询；不预测实际成交或投放回报。

## 快速开始

提供品牌或产品、目标受众、预算及候选小红书达人 ID 或主页。
只评估给定候选；按需要选择报价、粉丝画像与内容表现端点，成功调用每次 20 积分。
交付候选达人合作对照表，标明费用、样本范围、依据和待确认事项。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs pgy-creator-profile \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation

npx -y socialdatax-skills@latest xhs pgy-creator-fans-profile \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation

npx -y socialdatax-skills@latest xhs pgy-creator-notes-performance \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation
```

更多 direct CLI 入口：

```bash
npx -y socialdatax-skills@latest xhs user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-creator-collaboration-evaluation

npx -y socialdatax-skills@latest xhs pgy-creator-fans-summary \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation

npx -y socialdatax-skills@latest xhs pgy-creator-commercial-overview \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation

npx -y socialdatax-skills@latest xhs pgy-creator-metrics-trend \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation
```

## 参数说明

创作者 / 账号：
- 说明：候选达人的完整 `--user-id`；只有主页时先用 `xhs user-info --profile-url` 取得返回的用户 ID，不猜测 ID。

通用：
- 说明：部分表现、概览和趋势命令支持 `--note-scope daily|cooperation`；需要合作笔记对照时显式选择 `cooperation`，比较时保持相同范围。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill xhs-creator-collaboration-evaluation`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

## 合作评估流程

确认品牌/产品、目标受众、预算和候选名单；仅缺会影响评估的信息时询问。默认评估用户给定的候选，不自动扩充名单。

每个蒲公英端点每次成功查询收费 20 积分，失败不收费。先说明所选端点及预计成功调用积分；商业查询与费用已经确认时不重复询问。默认按需用报价资料、粉丝画像和内容表现，不把六个端点自动全部调用。

三名候选各查询上述三个商业端点，全部成功时共 9 次、180 积分；需要普通主页解析时另按该命令费用计算。仅做预算初筛时先查询报价资料。

只有提供完整用户 ID 才调用 `pgy-creator-*`；这些命令不接受主页 URL。只有主页时使用已列出的普通资料入口取得 ID。

内容表现与趋势采用服务固定窗口，不能指定任意起止日期。使用返回的数据日期和范围；增长指标没有明确周期时不自行补写周期。

画像分布未必完整，报价为 0 不等于免费；中位数不能相加，缺失日期不补 0。估算成本不等于实际成交成本，不能据此计算真实 ROI 或承诺销量。

遇到 `pgy_commercial_data_unavailable` 或公开错误码 `1009`，保留已取得结果，记录该候选商业数据不可用，不用其他输入重试或将普通资料当作商业结果。

## 输出建议

先列候选对照表，再解释预算与受众适配依据，区分接口事实和评估意见。

交付候选对照表：达人 ID/主页、报价及形式、目标受众匹配证据、内容表现、数据范围、预算适配判断、缺失数据。
将接口返回事实与合作建议分开；结论用优先沟通、需补资料或预算不匹配，并写明理由，不生成无依据的精确评分。
保留已取得的完整笔记链接和证据；仅对实际返回的数据作比较，报价以实际沟通确认为准。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_pgy_get_creator_profile`
- `xhs_pgy_get_creator_fans_profile`
- `xhs_pgy_get_creator_notes_performance`
- `xhs_get_user_info_by_profile_url`
- `xhs_pgy_get_creator_fans_summary`
- `xhs_pgy_get_creator_commercial_overview`
- `xhs_pgy_get_creator_metrics_trend`

## 安全边界

这是只读 skill，用于达人商业数据评估。仅进行已确认范围内的达人资料和商业数据查询，使用用户配置的 SOCIALDATAX_API_KEY；不联系达人、不发私信、不下单或签约，生成文件不含 API Key。

## 示例结果

示例：候选=<用户给定达人>；报价=<返回报价或缺失>；受众证据=<返回画像>；判断=<优先沟通或需补资料>；预算适配=<附依据>。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。 `pgy_commercial_data_unavailable` / 公开错误码 `1009` 表示商业数据不可用，应停止；不适用本节的重试和更换输入建议。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；把错误里的充值链接原样展示给用户，并提醒用户充值后继续执行刚才同一条命令。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 重试仍失败：说明当前调用不可用，请用户补充或更换关键词、链接、ID 等输入后再重试。

## 常见问题

- 没结果：确认账号主页、分享文本或平台账号 ID 完整。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按错误里的充值链接充值后继续原命令，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
