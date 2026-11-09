# Skillstore：源码 URL 投稿

核验：2026-11-07，一手仓库说明和当前提交网页。

## 输入与提交

[提交页](https://skillstore.io/submit) 当前接受 GitHub 仓库或特定目录的直接链接。使用经过验证的公开来源；固定 ref 的 tree URL 便于追溯，但仍须核对平台发现的是一个 skill、目录还是整仓。

网页说明可以匿名提交；GitHub 授权是接收审核/发布通知的推荐选项，不是基本表单必需条件。只要求准备时，先给出 URL、简介、范围与版本；不要为此提前要求登录。

有效 SKILL.md 是基本要求；LICENSE 推荐，平台建议 MIT、Apache 2.0 等许可。保留实际权利和作者选择，不把建议当成必须改许可。本次来源未建立统一 SemVer 必须字段，也未确认 raw 单文件 URL 或 ZIP 是发布输入。

**不要向 `aiskillstore/marketplace` 手工开一个“添加 skill”的 PR。** 官方 README 明确该仓库是平台的配套内容库，发布入口在网站；处理管线会生成自己的审核 PR。安装命令 `npx skillstore add ...` 也不是作者上传命令。

## 回执与审核

记录提交 ID/进度链接、解析到的来源 ref/路径/skill 数量、自动处理结果和审核 PR。处理完成或 `Ready` 可能仍在等待人工审核；`pending/` 内容不能当作已批准的 `skills/` 内容。

更新时标明既有条目和目标作者版本；如果解析成新增或整仓导入，先解决身份/范围问题。请求超时或重复回执先查询，不重建另一个条目试错。

## 公开核验

核对批准后的平台页面、内容仓库或公开 manifest/下载入口。PR 创建不表示通过，PR 合并也应与公开内容对应。

在平台暴露 manifest 时区分字段语义：顶层 `version` 可能是协议版本；作者版本可能位于 `skill.authorVersion` / `skill.version`，平台另有 `skillstoreRevision`。按实际 schema 读取，不把 `r2` 或顶层 `1.0` 当作作者版本。比较公开来源提交/路径、归档哈希与本次产物。

来源：[官方仓库说明](https://github.com/aiskillstore/marketplace#readme)、[提交页](https://skillstore.io/submit)。manifest 字段区别来自已公开条目的接口观察，使用时仍须核对当前 schema。
