# 来源、核验边界与本技能维护

当前技能版本：**1.2.3**，提供 8 个渠道的指导。腾讯 skillhub.cn 的介绍机制、官方教程与实际发布/更新/概述编辑器，以及 Agensi 和 SkillHub.club 的正式网页表单于 **2026-11-08** 核对；其他既有官方文档、此前文件过滤、CLI 0.1.9 代码与本地运行保留 **2026-11-07** 的核验日期。历史维护记录用于追溯已发行版本，不代表当前平台路由或真实发布成功。

| 主题 | 一手来源 | 本次证据边界 |
| --- | --- | --- |
| 通用格式 | [Agent Skills specification](https://agentskills.io/specification) | name/description 与目录格式；没有通用 SemVer/统一商店 ZIP 规则 |
| GitHub | [Release CLI](https://cli.github.com/manual/gh_release_create)、[认证](https://cli.github.com/manual/gh_auth_login) | 一手文档，未创建远程 Release |
| skills.sh | [FAQ](https://skills.sh/docs/faq)、[CLI](https://skills.sh/docs/cli)、[命令](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)、[创建/发现](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md) | 一手文档；GitHub 安装遥测收录，其他来源的上榜行为未建立 |
| 腾讯 SkillHub | [官网](https://skillhub.cn/)、[管理页](https://skillhub.cn/dashboard)、[官方教程](https://skillhub.cn/tutorials#publish-via-cli)、[Agent 发布规范](https://skillhub.cn/ai/release.md)、[官网当日客户端](https://cloudcache.tencent-cloud.com/qcloud/tea/app/skillhub/assets/skill-hub.bb2n2rxv.js?max_age=31536000) | 2026-11-08 界面声明默认 SKILL.md、自定义概述编辑与版本更新入口；客户端分别处理简介/概述、正文来源与语言优先级，公开 GET 观察各字段。未保存、上传或提交；独立不升版修改、清空语义、审核生效及翻译/缓存机制待核验；此前文件过滤保留原日期 |
| SkillHub.club | [网页 Skills 管理页](https://www.skillhub.club/app/skills)、[CLI 文档](https://www.skillhub.club/docs/cli)、[官方 CLI 仓库](https://github.com/skillhub-club/cli)、[npm 0.1.9](https://www.npmjs.com/package/@skill-hub/cli/v/0.1.9)、[条款](https://www.skillhub.club/terms-and-conditions) | 2026-11-08 实际表单与 accept/multiple 属性；未创建、导入、上传或公开，网页默认可见性与详情页资源规则仍未确认。CLI 11 项检查及受控扫描沿用 2026-11-07 的实测，1 MiB 参数不代表 Pro 账号实测 |
| Skillstore | [官方内容仓库](https://github.com/aiskillstore/marketplace#readme)、[提交页](https://skillstore.io/submit) | 一手说明/当前 UI；每次仍需验证 URL 实际发现范围 |
| ClawHub | [CLI](https://github.com/openclaw/clawhub/blob/main/docs/cli.md)、[发布](https://github.com/openclaw/clawhub/blob/main/docs/publishing.md) | 一手文档，含 MIT-0 条件与 pending 的公开可见性 |
| VoltAgent | [CONTRIBUTING](https://github.com/VoltAgent/awesome-agent-skills/blob/main/CONTRIBUTING.md) | 一手目录规则，不保证投稿会被接受 |
| Agensi | [正式发布页](https://www.agensi.io/dashboard/submit)、[打包](https://www.agensi.io/docs/packaging)、[网页提交](https://www.agensi.io/docs/submit-on-the-website)、[审核](https://www.agensi.io/docs/review-and-approval)、[条款](https://www.agensi.io/terms) | 2026-11-08 实际表单、文件属性及可选区域的可逆展开/收起；未填字段、上传或提交。打包/审核/条款与 MCP 流程沿用 2026-11-07 官方文档证据，未运行代理提交 |

## 资料怎样使用

实际任务只重查所选平台及影响当前步骤的事实。官方维护文档与现行界面优先；第三方文章/skill 用于发现线索。遇到冲突时记录来源、日期、具体字段和适用范围，不凭名称相似或一份旧示例决定。

介绍内容也按证据分层：官方说明写明的机制、真实界面/客户端怎样选择内容、公开只读入口实际返回什么，分别记录；没有真实保存/发布不推定服务端更新已验证。腾讯教程对 `summary` 的“简介与概述”称呼不能替代独立概述的界面与正文核验，语言字段也不能证明翻译生成来源或刷新周期。

本技能独立编写，组织方式参考了 `skill-market-publisher` 的平台矩阵/结果验证思路、`skillhub-publish-skill` 的腾讯站审核区分，以及作者既有发布记录。没有复制它们的个人环境、默认全网发布、许可证修改或镜像凭据转发规则。

## 维护本技能

日常使用在被发布项目保存材料与回执。只有用户要求维护指南，或发现可复现且影响正确性的规则变化时，才在本技能源码项目修改；不因一次发布失败就静默改用户级安装副本。

复核一手来源后更新相关页及本页日期/边界，检查包内引用和必要行为，再递增版本。PATCH 用于兼容修正，MINOR 用于新增兼容渠道/能力，MAJOR 用于不兼容变化；这些是本指南自身的版本约定。仅外层维护工具或运行记录变化不必升级本体。

源码是唯一维护来源，用户级目录接收验证后的完整副本。已发行的同一版本内容和标签不覆盖；如果新事实改变了指导内容，用新版本记录，而不是修改旧包。

## 历史维护记录

以下说明先前已发行版本；当前渠道以入口路由及上表为准。

### 1.1.0

新增 SkillHub.club 独立路线，保留与腾讯 SkillHub 的平台区分；README 改为逐项列出 9 个渠道、接收方式与证据范围。补充入口恢复、流程核对和真实公开发布的确认方法；SkillsDir.dev 的 404 与 Agensi 的证书过期经本次正常 HTTPS 请求复查，仍保留受限状态。没有以维护验证执行真实远程发布。

### 1.1.1

修正不能由单个客户端 TLS 失败推出 Agensi 整体不可用的证据边界；按当前官方文档与用户截图补齐 ZIP/pack 识别、字段、自动保存、审核和受限交付说明。网页摘要与源 description 分开，网站与代理限制分开，保留未实际上传/审核的状态。SkillHub.club 新增隔离本地 CLI/扫描实测依据，SkillsDir 仍保留三处正式执行入口 404。记录不包含个人账号、截图原图或真实发布回执。

### 1.2.0

新增 SkillHub.club 网页创建/文件导入路线，记录 ZIP、Markdown/文本选择器范围、上传自动创建首版的界面说明，以及尚未核验的默认可见性、归档解析和详情页资源限制。Agensi 从截图核验推进到实际表单及可选区域读取，明确界面星号、HTML 属性、官方文档与服务端验证的区别。SkillsDir 当前部署暂停及原执行入口 404 仍列为受限状态。README、路由表和本页同步新版本与分项核验日期，没有填写字段、上传、创建测试条目、提交审核或执行付费操作。

## 1.2.1 维护记录

按用户要求移除没有已核实可用投稿入口的 SkillsDir.dev：删除当前平台路由、README 渠道行、来源表和社区参考页中的发布说明，保留 VoltAgent。当前渠道数由 9 改为 8。此前的受阻事实仅保留在历史维护及外层发行/验证记录中，旧版标签和包不覆盖；不将暂时不可用写成平台永久禁止用户投稿。

## 1.2.2 维护记录

补齐介绍内容同步：分别识别发布包、SKILL.md description、GitHub README、平台简介、详情页概述、翻译与展示副本；发布前准备新版完整文案，提交时确认实际接收，发布后分别核验版本、下载包、简介和概述。模板新增来源、拟更新全文、实际提交、公开展示比较及未完成项，手动处理需完整文案和明确概述步骤。

腾讯指导依据当日官方教程、实际发布/更新/概述编辑器及官网客户端，说明默认文件与自定义正文、独立简介、语言优先级和保存到表单与最终提交的区别。保留旧页面原因、清空/省略语义、不升版编辑、历史版本绑定、审核生效及翻译/缓存时限待核验。当前 8 个渠道与现有授权/许可范围保留；未执行真实平台保存、上传或发布，未修改其他 skill，旧版包和标签不覆盖。

## 1.2.3 维护记录

补齐作者选择的 MIT 许可：入口声明 license，包内携带完整版权和许可正文。指南能力、平台资料核验日期与 1.2.2 相同；真实发布回执写入外层项目记录，旧版本包和标签保留。
