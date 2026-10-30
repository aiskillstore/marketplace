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
| **虾评 XiaPing** | 字节/扣子 | ❌ 虚拟币（虾米），无现金 | — | **例外：不用改写**，直接收标准 zip，`POST /api/skills` 一条命令上架；但**只许 Agent 注册**，且版权承诺须用户本人签。详见 [xiaping.md](xiaping.md) |
| **扣子 Coze 技能商店** | 字节 | ✅ 按次 / 月订阅 | 创作者约 **70%** | 国内唯一真支持 Skill 交易；**2026-05 起改申请制**，需专业领域资质（自媒体/金融/法律/电商/科研/教育/健康医疗）+ 资质证明，10 个工作日。通用工具类官方建议改投虾评。付费需入驻 |
| **字节 Find Skill** | 字节/火山 | ✅ | 未公开 | 与扣子并列的另一条线 |
| **扣子插件商店（API 插件）** | 字节 | 插件本身免费，可为站外 API 引流付费 | — | **与技能商店是两条线**：收 OpenAPI 云插件，国内唯一个人可上架自有 HTTP API 的渠道。需全工具调试通过 + 自定义头像 + 每工具运行示例；付费端点（402）过不了调试，须停用或给免费额度。实测全流程通过，详见 [coze-plugin.md](coze-plugin.md) |
| 智谱 AgentMore Skills 广场 | 智谱 | 免费（零 Token 安装） | — | 广场形态，多为官方/合作技能 |
| 阿里 虾小宝（JVS Claw 内置） | 阿里 | 免费但耗算力 | — | 内置市场，需走合作 |
| 阿里云百炼 Agent Store | 阿里 | ✅ 打赏 + API 收费 + 分润 | 未公开 | |
| 腾讯元器 | 腾讯 | ✅ | 未公开 | |
| Dify 市场 | 开源 | ✅（自接支付） | 私有部署 **0%** | |
| GPT Store | OpenAI | ✅ | 抽 **15%** | 需 ChatGPT Plus + Builder Profile |
| Windows Agent Store | 微软 | ✅ | 开发者 **85%** | |

**判断要不要移植**：技能的核心动作是在**用户本机**读写文件的（存档、构建产物、本地仓库），
平台托管型读不到用户磁盘，搬过去就是另一个产品；反过来，纯文本/纯推理类技能移植成本低。

> ⚠️ **扣子这条线上还有一个反例：虾评不用移植。** 它收的就是标准 `SKILL.md` zip，
> 但只对 Agent 开放注册，且卡在「版权承诺要用户本人签」。所以「本机读写类技能在扣子系等于白做」
> 这个结论**不适用于虾评** —— 全 CG 存档这种纯本地技能在虾评是能正常上架的。

## 六、已确认是死路（别再试）

| 目标 | 结论 |
|---|---|
| agentskills.my | `handleSubmit` 里只有 `console.log` + 假成功，**数据直接丢弃** |
| machina.directory | 不是商店，是博客 |
| hermeshub / skilldock.io / agentskills.io | 只在二手聚合文档里出现过，查不到实体 |
| skillsplayground.com | 全站 403 |
| agentskills.my / skillregistry.io | 连不上 |
| **skillsdirectory.com** | `/api/op/op1` 是登录墙，匿名提交无路 |
| **skillmd.com** | 有 `/api/skills/upload` 端点，但**未实测通过**，提交前先小流量试一次 |
| **mcpindex.dev** | `/submit` 返回 **500**，它自己的 Supabase RLS 坏了 —— 别浪费时间（详见 [cn-mcp-platforms.md](cn-mcp-platforms.md) 第二节） |

## 七、第二轮补遗（第一版容易漏掉的一批）

第一版只盯「SKILL.md 原生商店」，漏了三类：MCP 侧目录、IDE 内置目录、国内非大厂玩家。
下面这些都实测过域名可达（2026-10），**验证等级**照旧。

### 7.1 又一个真·技能市场

| 渠道 | 地址 | 形态 | 验证 |
|---|---|---|---|
| **LobeHub Skills** | lobehub.com/skills「Agent Skills Marketplace」 | 无 `/submit` 入口，自动索引 + 账号提交 | ✅ 页面可达 |

### 7.2 CLI / 注册中心

| 渠道 | 地址 | 形态 | 验证 |
|---|---|---|---|
| **agentskills.in** | agentskills.in「Universal Skill Manager」 | CLI 型，无网页提交页 | ✅ |
| **讯飞 Astron SkillHub** | skill.xfyun.cn/publish | **有发布页**，需讯飞账号（中文区） | ✅ |

### 7.3 MCP 侧目录（相邻赛道，需交付可跑的 MCP 服务）

Official MCP Registry ／ **Smithery**（smithery.ai）／ **Glama**（glama.ai）／
**mcp.so** ／ **PulseMCP**（pulsemcp.com）／ **mcpservers.org** ／ **MCP Market**（mcpmarket.com）／
**MCP.Directory**（mcp.directory）／ **Stork.AI**（stork.ai）／ mcp.run ／ mcphub.io ／
**Cursor Directory**（cursor.directory，有 Vercel 人机校验）

为什么单列：这些只收「跑着的 MCP server（STDIO / SSE / StreamableHTTP）」。本地脚本型技能要上，得先包成 MCP ——
那是另一个项目。但如果技能本来就是服务，这里是流量最集中的地方。

**同一份仓库可以两边都发。** 这次的实测结果值得记下来：

| 渠道 | 一份仓库能发几种 | 备注 |
|---|---|---|
| **MCP.Directory** | MCP **+ Skill 各一单** | 两个表单独立、都免登录、约 24h 审核；`/submit` 下另有技能入口 |
| **LobeHub** | MCP + Skills 分开两套 | 同一个站的 `/mcp` 与 `/skills` 互不相通 |

**`pull_request_creation_policy` 之外还要看一条**：`punkpeye/awesome-mcp-servers`（8K+ star）
的 bot 只认 **Glama 质量分 + badge**，没有分 PR 会被直接打回 —— 所以顺序是
**Glama（要 Dockerfile + glama.json）→ 拿到分 → 才去开那个 PR**。

完整的 `server.json` 约束、命名空间验证、目录自检三件套与静默错误清单，
见 [mcp-registries.md](mcp-registries.md)。

**国内 MCP 平台是另一套玩法**（多数要求把代码托管给平台重新部署，不是填个 URL 就完事）：
魔搭 / 阿里云百炼 / 百度 MCP World / AIBase / 讯飞 MCP / 火山 ATS / 华为云 ModelArts，
逐站实测与魔搭表单三坑见 [cn-mcp-platforms.md](cn-mcp-platforms.md)。

### 7.4 官方与社区列表（PR 型）——已逐个查过 pull_request_creation_policy

| 仓库 | 外部能否开 PR | 结论 |
|---|---|---|
| **VoltAgent/awesome-agent-skills**（36k★） | ✅ `all` | **已开 PR #1269**，加在 Development and Testing 分类 |
| trailofbits/skills-curated | ✅ `all` | 可开，但它是安全团队的 vetted 目录，非安全类技能放进去不合适 |
| **ComposioHQ/awesome-claude-skills**（78k★） | ❌ `collaborators_only` | **外部根本开不了 PR**，1856 个 open issue —— 别浪费时间 |
| anthropics/skills | —— | 官方示例仓库，社区技能不进 |
| vivy-yi/awesome-skills | —— | 抓取型清单，等它自己抓 |

> 教训：awesome 列表的 CONTRIBUTING 写得再热情，也要先看 `pull_request_creation_policy`。
> 一个 `gh api repos/<owner>/<repo>` 就能省掉一次白干。

### 7.4b 官方与社区列表（说明）

| 渠道 | 说明 |
|---|---|
| **anthropics/skills** | 官方示例仓库，PR 新增 `skills/<name>/`；进了这里等于拿到事实标准背书 |
| **Claude Connectors Directory** | 官方连接器目录，需审核 |
| ComposioHQ/awesome-claude-skills · VoltAgent/awesome-agent-skills · hesreallyhim/awesome-claude-code · trailofbits/skills-curated · vivy-yi/awesome-skills | Awesome 列表群，PR 加一行/一个目录；单条 PR 价值低，但被抓取概率高 |

### 7.5 国内第二批（媒体口径，多为 △）

| 渠道 | 归属 | 形态 | 验证 |
|---|---|---|---|
| **月之暗面 Kimi Claw** | 月之暗面 | 平台型 | △ |
| **小红书 Red Skill** | 小红书 | 仅支持 Markdown 等有限格式 | △ |
| **美团 虾345（xia345）** | 美团 | Skill Hunter 跨平台聚合 SkillHub / ClawHub；"入驻即入全生态" | △ 域名未核实（xia345.com 实为 AI345 资讯站） |
| **WorkBuddy 开放平台** | open.workbuddy.cn | 技能 / 专家 / 连接器；本地 `.workbuddy/skills/` 是另一回事 | 上传 zip（≤3MB、两层、8 必填字段）→ 审核 → 开收款 → 定价 | ✅ 付费，内测抽 1% |

### 7.6 API 目录（第四条线，旧版整条缺失）

技能商店收 `SKILL.md`，MCP 目录收跑着的 server，**API 目录收的是「HTTP 端点 + OpenAPI」**。
只要有公开端点，这条线是唯一能全自动的一条（一条 POST 或一条 PR，不用登录、不用移植）。

| 渠道 | 提交动作 | 验证 |
|---|---|---|
| **Agent402** | `POST https://agent402.tools/api/index/register` body `{"origin":"https://<domain>"}` | ✅ 实测 |
| **public-apis**（49 万★） | GitHub PR，`Art & Design` 分类按字母序插一行 | ✅ 实测 PR #8482 |
| **public-api-lists / APIs.guru / langchain** | GitHub PR | △（APIs.guru 的 CI 校验极严） |
| **apis.io** | `POST` 一份 `apis.json`，人工审核 | △ |
| **x402.new / x402-trust** | 自动抓 / 放 `.well-known` 声明 | △ |
| **x402scan** | 需**收款钱包**签 SIWx | ⏸ 链上身份 |
| **CDP Bazaar / agentic.market** | **被真实支付过一次才进索引**（自付约 $0.10） | ⏸ 链上身份 |
| **RapidAPI / Postman API Network / publicapis.io / apilist.fun / publicapis.dev** | 需商家账号 | ⏸ 需登录 |
| **国内（阿里云云市场 / A集市 / 聚合数据）** | **全部要企业资质**（正规公司 + 10 人团队 + 1 年经验） | ❌ 个人死路 |
| **扣子插件商店** | 国内唯一支持个人上架自有 API 的渠道，收 OpenAPI | ✅ 详见 [coze-plugin.md](coze-plugin.md) |

完整配方、Agent402 返回值怎么读、public-apis 的 fork 镜像坑、以及提交前必须满足的四条，
见 [api-directories.md](api-directories.md)。

### 7.6 自建发现端点 —— 已实测跑通（两个技能都进去）

做法：仓库开 GitHub Pages，把索引放在 `docs/.well-known/agent-skills/index.json`。实测地址：

```text
https://xixi048.github.io/publish-to-all-skill-stores/.well-known/agent-skills/index.json   # HTTP 200
```

**坑（一定会踩）**：GitHub Pages 默认跑 Jekyll，而 **Jekyll 会跳过以点开头的目录**，
`.well-known` 直接 404。必须加一个空的 `docs/.nojekyll`。不加的话你会以为"文件推上去了但打不开"。

索引内容就是一组 `{name, description, version, source, path, install}`，
`install` 同时给 `npx skills add` 与 `/plugin marketplace add` 两条命令。

### 7.7 MCP 侧：已经从"清单"变成"能跑的东西"

`publish-to-all-skill-stores` 仓库里现在有 `mcp/server.py`（stdio、零依赖、JSON-RPC 2.0），
把三个工具暴露给任何 MCP 客户端：`skill_store_registry` / `skill_preflight` / `skill_build_package`。

客户端配置：

```json
{ "mcpServers": { "publish-to-all-skill-stores": {
    "command": "python", "args": ["<repo>/mcp/server.py"] } } }
```

**但 Official MCP Registry 仍然上不了**：它的 `server.json` 要求 `packages[]`，而 `packages` 的必填字段是
`registry_type / identifier / version / transport` —— 也就是必须先发一个 npm / PyPI / OCI 包。
没有 npm/PyPI 账号就拿不到 `identifier`。Glama / mcp.so / PulseMCP / Cursor Directory 相对宽松，
可以直接提交 GitHub 仓库地址，属于"下一步"。

### 7.8 一个被忽略的免费渠道：自建发现端点

在自己的站点或仓库放 `/.well-known/agent-skills/index.json`，任何支持该约定的 agent 都能直接发现你的技能源。
不依赖任何商店审核，适合自持分发的团队。

> 教训：**"商店清单"本身是会长大的。** 每轮推送前重新扫一遍（GitHub topic 搜索 + 关键词检索
> "skill marketplace / registry / directory"），别拿上一轮的清单当全集。
