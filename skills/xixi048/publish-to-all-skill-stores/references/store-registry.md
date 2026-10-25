# 渠道路径 × 提交形态

验证等级：✅ 本次或上轮实际访问/读到官方文档 ｜ △ 二手信源 ｜ ⚪ 未验证，先别花时间

> 时间基准：2026-10。这个生态每月都在变，**URL 与接口先按本表试，失败就重新逆向一次**
> （方法见 [submission-recipes.md](submission-recipes.md)）。

## 一、仓库自动索引型（改仓库 → 自动被收录）

| 渠道 | 地址 | 收录条件 | 提交动作 | 验证 |
|---|---|---|---|---|
| **skills.sh** | skills.sh | 公开仓库 + `skills/<name>/SKILL.md`；按安装量排行 | 无表单。改布局 + `npx skills add <owner>/<repo>` 播种安装量 | ✅ |
| **SkillsMP** | skillsmp.com | 爬公开仓库，SKILL.md 存在，**需 ≥2 stars** | 无表单（另有账号+人工审核的 listing 表单，3–5 天） | ✅ |
| **claude-plugins.dev** | claude-plugins.dev | 索引公开插件/技能仓库 | 无表单；把仓库做成插件市场更容易被识别 | △ |
| **VoltAgent/awesome-openclaw-skills** | GitHub | 从官方 registry 抓取分类 | 无表单 | △ |
| **anbeime/skill 等中文聚合站** | GitHub | 抓 GitHub 上万个 Skills 项目 | 无表单 | △ |

自动索引型的共同前置，缺一条就永远不出现在结果里：

1. `skills/<name>/SKILL.md`（**不是** `{name}/SKILL.md` 在仓库根）
2. GitHub topics 至少覆盖 `agent-skills` / `claude-skills` / `skill-md` / 具体领域词
3. 仓库 description 一句话说清 "是什么 + 给谁用"
4. 有 LICENSE 与可读 README（很多站直接拿 README 做详情页）

## 二、公开提交接口型（一条 POST，无需登录）

| 渠道 | 接口 | 需要 | 回执 | 验证 |
|---|---|---|---|---|
| **skillstore.io** | `POST https://skillstore.io/api/submit` | `github_url`，可选 `notes` | `submission_id`，随后机器人开 PR（含安全审计） | ✅ 实测 200 |
| **skillsmd.dev** | `POST https://skillsmd.dev/api/submit` | `repo` 传 `owner/repo`（**不吃完整 URL**） | `id` | ✅ 实测 201 |
| **skillbay.sh** | `POST https://skillbay.sh/api/v1/submissions/quick`（multipart，文件字段 `file`） | `contactName` / `contactEmail` | `id` + `status: new` | ✅ 实测 201 |

注意：

- skillstore.io 对同一仓库 **1 小时内重复提交返回 409**；改完布局要等窗口过去再提
- `notify_via_github` 必须 `false`，为 `true` 且未登录会弹登录框，纯脚本就断了
- skillsmd 对新建仓库可能返回 `404 GitHub repo not found`（索引还没跟上），过一阵再试

## 三、GitHub PR 型（fork → 加文件 → PR）

| 渠道 | 加到哪里 | 特殊要求 | 验证 |
|---|---|---|---|
| **buildwithclaude** | `plugins/all-skills/skills/<name>/SKILL.md` | frontmatter 需 `name` / `category` / `description`；一个组件一个用途 | ✅ 实测 PR #561 |
| **ComposioHQ/awesome-claude-skills** | 仓库根加 `<name>/SKILL.md` + README 表格行 | 要求有真实用例、示例、可移植性说明 | ✅ 有 CONTRIBUTING |
| **tech-leads-club/agent-skills** | — | PR 策略 `collaborators_only`，**外部开不了 PR** | ✅ |
| 其他社区 registry（mercury-agent-skills、skill-dock、zeroclaw-skills 等） | 各自 README | 先看 `pull_request_creation_policy`，是 `collaborators_only` 就直接跳过 | △ |

## 四、登录式 CLI / OAuth 表单型（缺凭据就停）

| 渠道 | 形态 | 一条命令能否完成 | 验证 |
|---|---|---|---|
| **ClawHub (openclaw)** | device-code 登录 → `clawhub skill publish ./<dir> --slug <slug> --version <v> --source-repo <url> --source-commit <sha>` | ✅ 实测已发 1.2.0（pending security scans） | ✅ |
| **Tank (tankpkg.dev)** | `tank login` → `tank init` → `tank scan` → `tank publish` | ❌ CLI v0.16.5 认证接口报 Invalid request body | △ 官方文档 + 实测失败 |
| **skilld.dev** | CLI 发布 | 登录后可以 | △ |
| **Cow Skill Hub** | Web + GitHub/Google OAuth，上传 zip（SKILL.md 须在包根） | 匿名 POST 返回 401 | ✅ |
| **agentskill.sh** | `/submit` SPA，贴仓库 URL → Analyze & Import | 未找到公开 POST 端点 | ✅（端点探测失败） |
| **腾讯 SkillHub** | 已改域名 **skillhub.cn**（旧 skillhub.tencent.com 301 跳转），网页提交 | 需登录 | ✅ 页面可达 |

## 五、平台托管型（**必须移植，不属于"推送"**）

| 平台 | 归属 | 收费 | 分成 | 备注 |
|---|---|---|---|---|
| **扣子 Coze 技能商店** | 字节 | ✅ 按次 / 月订阅 | 创作者约 **70%** | 国内实测唯一支持 Skill 交易；付费需入驻 `code.coze.cn/merchant-management` |
| **字节 Find Skill** | 字节/火山 | ✅ | 未公开 | 与扣子并列的另一条线 |
| 智谱 AgentMore Skills 广场 | 智谱 | 免费（零 Token 安装） | — | 广场形态，多为官方/合作技能 |
| 阿里 虾小宝（JVS Claw 内置） | 阿里 | 免费但耗算力 | — | 内置市场，需走合作 |
| 阿里云百炼 Agent Store | 阿里 | ✅ 打赏 + API 收费 + 分润 | 未公开 | |
| 腾讯元器 | 腾讯 | ✅ | 未公开 | |
| Dify 市场 | 开源 | ✅（自接支付） | 私有部署 **0%** | |
| GPT Store | OpenAI | ✅ | 抽 **15%** | 需 ChatGPT Plus + Builder Profile |
| Windows Agent Store | 微软 | ✅ | 开发者 **85%** | |

**判断要不要移植**：技能的核心动作是在**用户本机**读写文件的（存档、构建产物、本地仓库），
平台托管型读不到用户磁盘，搬过去就是另一个产品；反过来，纯文本/纯推理类技能移植成本低。

## 六、已确认是死路（别再试）

| 目标 | 结论 |
|---|---|
| agentskills.my | `handleSubmit` 里只有 `console.log` + 假成功，**数据直接丢弃** |
| machina.directory | 不是商店，是博客 |
| hermeshub / skilldock.io / agentskills.io | 只在二手聚合文档里出现过，查不到实体 |
| skillsplayground.com | 全站 403 |
| agentskills.my / skillregistry.io | 连不上 |
