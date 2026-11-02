---
name: "xhs-creator-profile-insights"
description: "当用户需要做小红书博主画像、小红书博主信息、账号资料、创作者定位、粉丝规模判断或合作对象初筛时使用。面向品牌、MCN、内容运营和创作者。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "xhs-creator-profile-insights"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"👤","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 小红书博主画像

## 适用场景

当用户需要做小红书博主画像、小红书博主信息、账号资料、创作者定位、粉丝规模判断或合作对象初筛时使用。面向品牌、MCN、内容运营和创作者。

## 快速开始

- 先给出当前 skill 支持的输入：账号主页、账号分享文本或平台账号 ID。
- 你通常会得到：账号资料、认证、粉丝或互动信号，以及可继续追问的角度。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest xhs user-info \
  --user-id "<user_id>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill xhs-creator-profile-insights

npx -y socialdatax-skills@latest xhs user-info \
  --profile-url "<profile_url_or_share_text>" --pretty \
  --source-client socialdatax-skills --source-platform modelscope \
  --source-skill xhs-creator-profile-insights
```

## 参数说明

创作者 / 账号：
- 说明：XHS `--user-id <user_id>`：当创作者 ID 已经来自其他结果时优先使用。
- 说明：XHS `--profile-url <profile_url_or_share_text>`：用于主页 URL、短链或主页分享文本。

通用：
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill xhs-creator-profile-insights`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

单次调用只使用一种受支持的标识符或 URL 入口，不要混用多个入口。

命令返回 JSON，包含 `platform`、`tool`、`arguments` 和 `data`。

## 输出建议

优先输出可直接复盘的结果：创作者资料，并标出下一步可继续追问的问题。

输出创作者资料时，优先写昵称、平台 ID、简介、认证、粉丝数、关注数、获赞数、IP 属地、性别等可见事实；把事实和策略判断分开写。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `xhs_get_user_info_by_user_id`
- `xhs_get_user_info_by_profile_url`

如果当前 Agent 已可直接调用 MCP 工具，可按入口选择以下工具：
- `xhs_get_user_info_by_user_id`：当 `user_id` 已经来自搜索、详情、评论或创作者笔记列表结果时优先使用。
- `xhs_get_user_info_by_profile_url`：用于主页链接、短链或主页分享文本。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：账号=昵称/ID/简介/粉丝信号；判断=相关原因和下一步。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 重试仍失败：说明当前调用不可用，请用户补充或更换关键词、链接、ID 等输入后再重试。

## 常见问题

- 没结果：确认账号主页、分享文本或平台账号 ID 完整。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
