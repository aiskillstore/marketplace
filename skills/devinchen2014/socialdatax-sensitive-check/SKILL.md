---
name: "socialdatax-sensitive-check"
description: "用于敏感词检测、违禁词检测、文案发布前检查、内容安全检查、文案合规审核、能不能发判断、平台风险提示和改写建议。支持小红书、抖音、快手和通用文本场景，来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "socialdatax-sensitive-check"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"🛡️","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 敏感词检测与违禁词检查

## 适用场景

用于敏感词检测、违禁词检测、文案发布前检查、内容安全检查、文案合规审核、能不能发判断、平台风险提示和改写建议。支持小红书、抖音、快手和通用文本场景，来自 SocialDataX 社媒数据助手。

## 快速开始

- 粘贴要检测的文案，并按需要指定平台：`generic`、`xhs`、`douyin` 或 `kuaishou`。
- 你通常会得到：是否违规、风险等级、命中类型、风险片段和改写建议。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest sensitive-check text \
  --text "<content>" --platform xhs --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill socialdatax-sensitive-check
```

## 参数说明

通用：
- 必填：`sensitive-check text --text <content>`：必填文本；使用用户要检查的文案进行分析，但不要把原文保存在 skill 文案里。
- 可选：`--platform <generic|xhs|douyin|kuaishou>`：平台上下文，可选；默认是 `generic`。
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill socialdatax-sensitive-check`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

适用于敏感词检测、违禁词检查、文案发布前检查、content safety review、文案合规审核、能不能发判断和 safer rewrite suggestions for draft text.
命令返回 JSON，包含 `platform`、`tool` 和 `data`，不会在 CLI 参数区回显原文。服务会在可用时返回 `violation`、`risk_level`、`types`、`highlights`、`summary`、`platform` 和 `suggestions`。
服务端会保存提交文本和结构化检测结果，用于历史记录、计费和问题排查；本地 CLI 不会把 API Key 写入本地文件，也不会写本地文本副本。
当前 v1 只支持文本敏感检测；图片敏感检测要等单独的图片能力发布后再支持。

## 输出建议

优先输出是否违规、风险等级、命中类型、关键提示和可执行改写建议。

输出时说明是否违规、风险等级、命中的类型、关键提示，以及可执行的改写建议。
除非用户明确要求，否则不要回显完整原文；优先给出简短提示和更安全的改写建议。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `check_sensitive_text`

如果当前 Agent 已可直接调用 MCP 工具，使用 `check_sensitive_text`，传入 `text`，并可选传 `platform`：`generic`、`xhs`、`douyin` 或 `kuaishou`。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式，不代表固定字段：风险=是否违规/风险等级/命中类型；建议=可替换表达和发布前注意点。

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
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
