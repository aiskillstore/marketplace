---
name: skill-publishing-guide
description: Use when preparing, publishing, updating, or verifying an Agent Skill on GitHub, skills.sh, Tencent SkillHub (skillhub.cn), SkillHub (skillhub.club), Skillstore, ClawHub, or community directories, especially when repo URLs, ZIP layouts, review states, or release versions differ. 适用于 Skill 上架、分发、版本更新和发布结果核验。
license: MIT
metadata:
  version: "1.2.3"
---

# Skill 发布指南

把用户指定的一个 skill，按目标平台实际接收的形式发布，并保留可核对的版本与结果。发布包与介绍内容分别准备、提交和验收。发布单元、目标渠道和成功证据先确定，再选工具。沿用用户的语言、许可、仓库及现有授权。

本技能按 [MIT 许可](references/license.md) 分发。

## 先确定本次范围

从任务与项目记录提取：skill 路径、版本/来源提交、目标平台和账号/namespace、任务是咨询、准备、发布、更新还是核验。已有信息直接复用；只有真正缺失且影响下一步时才询问。

只要求方法时给出方案；只要求本地准备时生成材料和检查结果。创建远程仓库、草稿 Release/PR、上传和提交都会写外部状态，须在相应授权范围内。已明确且仍适用的授权不用重问。缺少登录时先完成独立准备，真正执行到登录、扫码、验证码或新的许可/可见性选择时，沿用会话通知约定提出具体请求。

## 按确切平台选择路线

| 目标 | 主要接收方式 | 按需阅读 |
| --- | --- | --- |
| GitHub | 仓库/提交、版本标签、Release 附件 | [GitHub](references/github.md) |
| skills.sh | 安装来源与安装遥测触发收录 | [skills.sh](references/skills-sh.md) |
| 腾讯 SkillHub：skillhub.cn | 登录后的本地文件/ZIP，或绑定 GitHub 后选择导入 | [腾讯 SkillHub](references/skillhub-cn.md) |
| SkillHub：skillhub.club | 网页导入 ZIP/Markdown/文本，或官方 CLI 上传并公开；已有 GitHub 来源的索引单独核对 | [SkillHub.club](references/skillhub-club.md) |
| Skillstore：skillstore.io | 网站提交 GitHub 仓库或目录 URL | [Skillstore](references/skillstore.md) |
| ClawHub：clawhub.ai | 官方 CLI 提交本地 skill 文件夹 | [ClawHub](references/clawhub.md) |
| VoltAgent | 满足社区使用门槛后向 awesome-agent-skills 提交目录 PR | [VoltAgent](references/community-directories.md) |
| Agensi | 正式网页 ZIP 提交；代理提交的文件限制和预览确认单独处理 | [Agensi](references/agensi.md) |

`skills.sh` 与 `agentskill.sh` 是不同网站；腾讯 `skillhub.cn`、独立平台 `skillhub.club` 和字节/企业 SkillHub 的账号与流程分别核对。其他平台先定位其正式发布文档，确认接收物、授权/许可条件及公开验证入口，再决定是否可执行。入口受阻时按 [核验说明](references/verification-and-recovery.md)区分入口恢复、流程核对和真实发布。个人/团队安装 ZIP 和插件市场上架分别记录，不能混成普通 skill 的公开发布。

## 准备并执行

1. 按 [准备与打包](references/prepare-and-package.md) 确认唯一发布单元，核对必要文件、来源、版本和许可。多个 skill 的仓库不能默认整仓导入；repo、tree 子目录和 raw 文件 URL 分别处理。
2. 读取所选平台页，重新核对影响本次发布的入口、字段、文件限制和条款。区分一手文档、客户端观察与历史记录；证据不足的项目保留未核验状态。
3. 生成具体材料：所用 URL 或 ZIP、范围/根层级、版本、分类，以及 [与新版一致的简介和概述全文](references/introduction-content.md)。文案覆盖功能变化、系统支持、依赖和真实验证范围，保留未实测部分；记录各层介绍的来源和实际更新入口。平台没有要求的信息不臆造；不为了通过过滤静默删掉运行依赖。
4. 在既有授权内核对实际接收的文件、简介及概述，再提交选定渠道。表单建议、编辑器保存或 ZIP 上传不能代替介绍内容的提交记录。写请求超时或响应含糊时先记录并查询，不能通过重新上传、改名、升版或重建条目猜测恢复。
5. 按 [结果核验与恢复](references/verification-and-recovery.md) 分别核验公开版本、下载包、简介和概述。接收、待审核、版本公开、网页介绍更新及安装成功分别记录，不能由一项推定其余项。

凭据通过平台正式客户端或已配置的安全方式使用，不打印或写入发布包。不要把 GitHub Authorization 头发送给第三方镜像。源许可和平台分发条款分别核对，尤其 ClawHub 的 MIT-0 条件；不自动改许可证或默认新建公开仓库。

## 交付结果

使用 [发布记录模板](references/submission-record.md)，保存来源提交/路径、作者版本、包结构与哈希、平台及 namespace、介绍来源与拟更新全文、实际提交状态、公开核验和待办。需用户手动处理时，交付完整可复制文案及已核实的操作步骤。记录放到被发布项目的维护目录，不写回本技能。

报告只覆盖实际执行范围；无法确认的结果标为未知或待核验。各平台的依据及本技能维护方式见 [来源与维护](references/sources-and-maintenance.md)。
