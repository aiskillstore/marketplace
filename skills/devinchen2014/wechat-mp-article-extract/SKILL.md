---
name: "wechat-mp-article-extract"
description: "当用户提供 mp.weixin.qq.com 文章链接或分享文本，需要提取公众号文章标题、账号、发布时间、正文、图片和关联内容并整理成结构化结果时使用。来自 SocialDataX 社媒数据助手。"
source_client: "socialdatax-skills"
source_platform: "modelscope"
source_skill: "wechat-mp-article-extract"
metadata: {"openclaw":{"requires":{"env":["SOCIALDATAX_API_KEY"],"bins":["node","npm"]},"primaryEnv":"SOCIALDATAX_API_KEY","install":[{"kind":"node","package":"socialdatax-skills","bins":[]}],"emoji":"📰","homepage":"https://socialdatax.com/ai?from=modelscope"}}
---
<!-- AUTO-GENERATED from socialdatax-skill-source. Do not edit directly; run `node scripts/generate_socialdatax_skills.mjs`. -->

# 公众号文章提取

## 适用场景

当用户提供 mp.weixin.qq.com 文章链接或分享文本，需要提取公众号文章标题、账号、发布时间、正文、图片和关联内容并整理成结构化结果时使用。来自 SocialDataX 社媒数据助手。

## 快速开始

- 先给出当前 skill 支持的输入：mp.weixin.qq.com 文章链接或包含该链接的分享文本。
- 支持输入：mp.weixin.qq.com 文章链接或包含该链接的分享文本。
- 你通常会得到：文章标题、公众号、发布时间、正文、图片链接、关联文章和内嵌视频卡片；只输出实际返回内容。

## API Key 获取

获取或管理 API Key：访问 <https://socialdatax.com/ai?from=modelscope>，按官网的 API Key 申请/管理入口操作。环境变量名固定使用 `SOCIALDATAX_API_KEY`；不要引导用户使用其他域名。

## 直接调用命令

优先使用 direct CLI；能运行 shell 命令的 Agent 不需要额外配置 MCP server：

```bash
npx -y socialdatax-skills@latest wechat article \
  --url "<mp_article_url_or_share_text>" --pretty --source-client socialdatax-skills \
  --source-platform modelscope --source-skill wechat-mp-article-extract
```

执行 direct CLI 示例时，`<mp_article_url_or_share_text>` 是占位符；不要把原始用户输入拼成整段 shell 字符串。能直接调用子进程时使用参数数组；必须走 shell 时先做 shell 转义。

## 参数说明

通用：
- 必填：`--url <mp_article_url_or_share_text>`：必填；只接受 mp.weixin.qq.com 文章链接或包含该链接的分享文本。
- 可选：`--pretty`：只影响输出格式，不改变实际请求结果。
- 可选：`--source-client socialdatax-skills --source-platform modelscope --source-skill wechat-mp-article-extract`：这是当前 Agent Skill 的来源标记；按本 Skill 示例执行时保持这些值不变。

把用户提供的公众号文章链接或分享文本交给文章详情命令；不要把视频号视频路由到本 skill。
结果缺少正文、图片或关联内容时，按实际返回说明，不补造，也不改用其它平台能力。

## 输出建议

优先输出便于阅读、引用和后续整理的公众号文章结构化结果。

输出时使用固定结构，字段只使用返回中可见内容。

1. 文章信息：标题、公众号、发布时间和原始文章链接。
2. 正文：按返回顺序整理正文段落，保留原意，不添加原文没有的信息。
3. 图片和媒体：列出返回中的图片链接与内嵌视频卡片；缺失时说明未返回。
4. 关联内容：列出返回中的关联文章及链接，并与正文引用分开。

只处理用户提供的公众号文章链接或分享文本，不承诺发现其它文章、账号内容列表、评论、热榜或互动指标。

## MCP 工具

与上面 direct CLI 命令对应的 MCP 工具：

- `wechat_get_mp_article_detail_by_url`

如果当前 Agent 已接入 MCP，只使用 `wechat_get_mp_article_detail_by_url` 处理公众号文章链接或分享文本。

## 安全边界

这是只读 skill。运行时使用用户环境变量中的 `SOCIALDATAX_API_KEY`；生成的 Skill 文件不包含 API Key。不会读取本地浏览器数据，也不会执行登录、发帖、点赞、评论或账号修改。

## 示例结果

- 示例展示格式：文章=标题/公众号/发布时间；正文=分段文本；媒体=图片链接/内嵌视频卡片；关联=关联文章链接。字段缺失时明确标注，不补造。

## 异常处理

- 如果出现 SDK/依赖缺失、npm 网络、Node.js/npm/npx 不可用或执行权限错误：这是本地运行环境、依赖安装、网络或 AI 平台授权问题，不是 SocialDataX API Key 或业务数据返回错误。仅在用户已授权的范围内安装或修复本任务所需依赖，优先使用项目目录或临时环境。环境执行权限不等于用户授权；超出授权范围时，先说明具体改动并征得同意，包括全局安装、运行时升级或系统配置变更。需要网络或执行授权时提醒用户同意或完成授权；处理后继续原命令；不要改用公开网页搜索替代 SocialDataX 数据。
- 非余额不足的网络或 API 异常：保留错误信息，检查 `SOCIALDATAX_API_KEY`、参数和链接格式后原样重试一次。
- 如果返回 `insufficient_balance` 或“积分不足”：不要重复重试；展示错误中的官方充值链接（https://socialdatax.com/dashboard/billing，可带渠道参数）；若没有该链接，使用 https://socialdatax.com/dashboard/billing。充值后继续刚才失败的调用；已有任务或部分结果时，按对应任务查询、分页续查规则恢复。
- 如果用户已经充值但仍提示余额不足：确认当前环境变量 `SOCIALDATAX_API_KEY` 是否来自刚充值的同一个账号；必要时重新复制官网后台的 API Key。
- 重试仍失败：说明当前调用不可用，请用户确认或更换 mp.weixin.qq.com 文章链接或分享文本后再试。

## 常见问题

- 没结果：确认 mp.weixin.qq.com 文章链接或分享文本完整。
- 调用失败：先确认 `SOCIALDATAX_API_KEY` 已配置；如果是 `insufficient_balance` 或“积分不足”，按上述官方充值链接说明完成充值后，按上述恢复规则继续，不要反复重试。
- 担心账号安全：这是只读能力，不登录、不发帖、不点赞、不评论。
- 想继续分析：把最相关的 1-3 条结果发回来，继续缩小范围。
