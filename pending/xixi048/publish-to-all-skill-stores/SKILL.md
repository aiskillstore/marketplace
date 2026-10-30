---
name: publish-to-all-skill-stores
description: "Publish one skill to every agent-skill store at once — at home and abroad, free and paid. Use it when the user asks to publish / upload / list / 上架 / 推送 a skill to skill stores, skill marketplaces, 技能商店, 技能市场, plugin marketplaces, or asks why a published skill is not being discovered. Covers repo layout for auto-indexers, public submit APIs, GitHub-PR registries, login-gated CLIs, platform-hosted stores that need porting, and how to price a paid listing. 关键词：上架技能、推送技能、技能商店、技能市场、虾评、xiaping、skill store、marketplace、publish skill、被收录、署名、API 目录、MCP 目录、国内渠道。"
license: MIT
metadata:
  author: xixi048
  version: "2.2.0"
  language: zh-CN
---

# 同时上架所有 Skill 商店

把一个已经能跑的技能推到尽可能多的分发渠道，并且**分清哪些能脚本化完成、哪些必须用户本人动手**。

## 先建立最关键的一条认知

「技能商店」不是一个东西，按**提交动作**分成五类；混淆它们会在一半渠道上白费时间：

| 形态 | 提交动作 | 代表 | 能否自动化 |
|---|---|---|---|
| 仓库自动索引 | 改仓库本身（路径 + topics + README） | skills.sh、SkillsMP、claude-plugins.dev | ✅ 完全 |
| 公开提交接口 | 一条 HTTP POST | skillstore.io、skillsmd.dev、skillbay.sh | ✅ 完全 |
| **Agent 自注册 API** | 自己申请一个 Agent 账号拿 Key，再 POST | **虾评 XiaPing** | ✅ 完全（**仅版权承诺要问主人**） |
| GitHub PR | fork → 加文件 → PR | buildwithclaude、awesome 列表、社区 registry | ✅ 完全（需 GitHub 写权限） |
| 登录式 CLI / OAuth 表单 | 先登录再发 | ClawHub、Tank、Cow Skill Hub、agentskill.sh | ⚠️ 缺凭据就停 |
| 平台托管 | **把技能用平台方言重写** | 扣子 Coze 技能商店、智谱 AgentMore、GPT Store | ❌ 是另一个开发项目 |
| MCP 目录 | **先把技能包成 MCP server** | Smithery、Glama、mcp.so、PulseMCP、Cursor Directory | ❌ 是另一个开发项目 |

只有前四类是「推送」，第五类是「移植」。不要在第五类上假装能"一键推送"。

**「平台托管」这类里最容易被搞混的一对：扣子技能商店 ≠ 虾评。** 同属扣子生态，但是两条完全不同的路：

| | 扣子技能商店 | 虾评 XiaPing |
|---|---|---|
| 入口 | `www.coze.cn/skills` | `xiaping.coze.com` |
| 谁能发 | 人类开发者 + **技能上架资质**（专业领域 + 资质证明，10 个工作日） | **只有 Agent**，官方明说「不支持人工注册」 |
| 提交动作 | 扣子编程里自然语言重写 → 部署 → 我的技能 → 上架 | 一条 `POST /api/skills` |
| 适合 | 律所/医院/学校/持证自媒体 | 通用工具、兴趣创作、开源项目 |

用户说「提交到扣子」时，先分清他要的是商店还是虾评。**通用工具与兴趣类技能在扣子是过不了资质关的，
官方文档自己就建议去虾评。** 虾评是这类需求唯一能全自动落地的答案，配方见
[references/xiaping.md](references/xiaping.md)。

完整渠道表（**40+ 个**，含国内外、免费与付费、验证等级；含 MCP 目录群、CLI 注册中心、国内第二批）见
[references/store-registry.md](references/store-registry.md)。

**清单本身是会长大的，别拿上一轮的清单当全集。** 每轮开工前花五分钟重新扫一遍：

```bash
# GitHub：列出仍在活跃维护的技能目录/注册中心
gh search repos --topic claude-skills --topic skill-md --sort updated --limit 40
gh search repos "skill marketplace" --sort stars --limit 40
# 关键词检索（会命中新站）：skill marketplace / skill registry / directory / 上架 / 技能商店
```
扫到新站先确认三件事：**域名能打开**、**有提交动作**（表单/API/PR/CLI）、**不是假表单**
（判据：提交后给回执 id 或开 PR，只弹 toast 说"成功"的一律不算）。

## 推送顺序（照这个顺序做，返工最少）

0. **先上 GitHub，再谈商店。** 仓库是所有下游的根：爬取型目录站靠它、PR 型渠道靠它、
   多数平台直接来 clone。**默认私有**（不开源），但要**先问用户一句要不要开源**，不要自己定。
   并告知这个交换：*私有仓库 = 自动索引型渠道（skills.sh / SkillsMP / claude-plugins.dev）全部失效*，
   只能走 zip 上传与平台托管；公开则反之。用户选私有时，把重心放到需要登录的渠道。
1. **先修仓库，再谈提交**（顺序错了全白干）
   - 技能必须放在 `skills/<name>/SKILL.md`
   - 加 `.claude-plugin/marketplace.json`（顺带成为 Claude Code 插件市场）
   - 设 GitHub topics（`agent-skills` `claude-skills` `skill-md` …）+ 仓库 description
   - 布局与清单**两者都要**，它们分别喂给不同的爬虫
2. **自动索引型**：布局改完就等爬虫；用 `npx skills add <owner>/<repo>` 触发首次安装来播种 telemetry
3. **公开 API 型**：`python scripts/submit_all.py --all --repo <url>`
3.5. **虾评**：注册 → 拿 Key → 逐个 `POST /api/skills`。这一步**只有一个卡点**：版权承诺必须
   由用户本人确认（把平台原文照抄给他，别总结），拿到"同意"后追加 `pledge={"agreed":true}`。
   上传配额由等级压制（注册送 30 虾米 = A2 = **只有 3 个名额**），先把最想曝光的三个排好序。
   发布后默认**试用版**，转正要 20 篇评测 + 加权 ≥ 4，别指望发完就有流量。
4. **PR 型**：按各仓库 CONTRIBUTING 的位置加一个 `<name>/SKILL.md`
5. **登录型**：先把物料备好，缺凭据就明确告诉用户"这一步需要你登录"
6. **社区列表 / PR 型长尾**：awesome 列表与官方示例仓库，一次一条 PR，别刷
7. **平台托管型 / MCP 目录**：单独评估工作量，不要混进"推送"的进度里

判断某一步能不能自己做，只看**目标渠道要的是什么**：要 URL / 要 zip / 要 PR / 要登录态。
别用"能不能用浏览器"当作标准——绝大多数渠道根本不看浏览器，看的是仓库状态。

## 硬性要求（踩过坑的部分）

**布局。** `{name}/SKILL.md` 在仓库根目录**不够**。`skills/<name>/SKILL.md` 才是被广泛索引的路径
（anthropics/skills 与 skills.sh 文档都是这个形状）。仓库根目录的技能永远不会被发现，
而且不报错——它只是安静地不存在。迁移后记得改 README 里所有相对路径。

**套餐。** 目录站普遍要求宽松协议（MIT / Apache-2.0 / MPL-2.0）与 `LICENSE` 里的真实版权人。
含脚本的技能在 skillstore.io 会**追加一轮安全审计**，所以提前把"零依赖 / 无网络 / 无 eval /
写入目标由用户显式给出 / 每次写入前备份"写进提交备注，比修改代码更有效。

**打包。** 要求"zip 且 SKILL.md 在包根"的渠道（Cow Skill Hub 一类）和仓库布局天然冲突，
必须单独打 `skillroot` 包：`python scripts/build_package.py <repo> skills/<name> --out dist`。
打包前删掉 `__pycache__`（`.pyc` 会被原样打进 zip）。

**英文区用英文，中文区用中文。** 同一条 listing 在 ClawHub / skillstore / SkillsMP / skillbay 上写英文
（标题、摘要、审核说明、before-after 证据全英文）；在腾讯 SkillHub / Cow Skill Hub / 扣子 / AgentMore 上写中文
（显示名、简介、分类直接用中文，别把英文 description 粘过去）。混用会显得像机翻，直接影响审核印象。
SKILL.md 的 frontmatter 本身保持英文（它是给模型读的），本地化只发生在**商店的展示字段**上。

**能 GitHub 导入就绝不本地上传。** 很多渠道的发布页同时提供「上传 zip」和「从 GitHub 导入」。
一律选 GitHub 导入：仓库是唯一真源，push 就能更新版本，不会出现商店版本与仓库不一致；
而且导入器通常能直接识别 `skills/<name>/` 布局。只有平台不支持导入或包需要在仓库外裁剪时才用 zip。

**定价。** 能收费的渠道就收费，同一个技能在不同渠道可以是不同形态、不同价：
免费渠道保留引流版，付费渠道挂完整版或 Pro 版。具体价位与各平台分成见
[references/paid-channels.md](references/paid-channels.md)。

## MCP 侧分发（相邻赛道，别和商店混着做）

同一个产品往两边发很常见：**技能是一份方法论（Markdown），MCP 是一个可调用的服务**。
交付物完全不同，配方不能互相套。判断标准只有一条——**用户是要「AI 知道怎么做」，还是要「AI 能调用」**。

三条容易踩错的：

**一、有三种上架形态，只有前两种是「推送」。**

| 形态 | 你要交什么 | 代表 |
|---|---|---|
| 元数据登记 | 一个 URL 或一份 `server.json`，服务还在你自己服务器 | 官方 Registry、mcp.so、Smithery、MCP.Directory |
| 目录自检型 | 仓库 + `Dockerfile` + 声明文件，平台真的跑起来打分 | Glama |
| 平台托管 | 可容器化的完整代码，**平台接管部署** | 魔搭、百炼、火山 |

第三类会生成平台自己的地址，从此有两套端点要同步维护。开工前先问用户**愿不愿意把服务托管给平台**。

**二、先跑通端点，再谈提交。** 目录站会真的连一次：HTTPS + `initialize` + `tools/list` + 一次真实调用。
仓库里放一个能跑的 `verify.js` / `smoke.mjs`，比任何文案都有说服力。

**三、官方 Registry 是下游的上游，值得先做。** 它只存元数据，但 PulseMCP 一类站会从它自动同步。
`description` 硬限 100 字符；包内必须声明 `mcpName` 且与 `server.json` 一致；
命名空间要么 `login github`（`io.github.<user>/*`），要么域名验证（`cloud.<domain>/*`）。

**四、文案在第一次提交前定死，尤其别写会过期的数量。** `762 words / 598 styles` 这种是当前快照，
词库一扩就失真，而它同时躺在 README、包描述、`server.json` 和几个目录站后台里。
写能力不写数量。目录站大多没有自助编辑入口，改一次要重发版本再排一次队。

**五、国内平台是第三种形态，别拿海外的经验套。** 魔搭 / 百炼 / MCP World / AIBase / 讯飞 MCP
多数是**平台托管**：不是填 URL，而是把代码交出去让平台重新部署，之后两套端点要同步维护。
魔搭的「GitHub 快速创建」在境内读不到 GitHub（会谎报 README 缺失），只能走自定义创建，
且表单有三个坑（托管类型漏选静默失败 / Monaco 编辑器只能剪贴板粘贴 / antd 按钮文本中间带空格）。
逐站实测见 [references/cn-mcp-platforms.md](references/cn-mcp-platforms.md)。

## API 目录（第四条线，别漏了）

同一个产品最多可以走四条线，**每条收的东西都不一样**：

| 线 | 交付物 | 全自动? |
|---|---|---|
| 技能商店 | `SKILL.md` | 部分（公开 API 型可以） |
| MCP 目录 | 跑着的 MCP server | 部分 |
| **API 目录** | **HTTP 端点 + OpenAPI / llms.txt** | **✅ 最高，一条 POST 或一条 PR** |
| 平台托管 | 用平台方言重写 | ❌ 是另一个项目 |

**只要手上有公开 HTTP 端点，这条线就一定要走**——它是唯一不用登录、不用移植、
还能一条命令拿到回执的一条。最低限度三条：

```bash
# 1. x402 / 付费 API 索引：一条 POST，返回里盯 toolCount 与 health
curl -X POST https://agent402.tools/api/index/register \
     -H "Content-Type: application/json" -d '{"origin":"https://<domain>"}'

# 2. public-apis（49 万★）：fork → 在 Art & Design 按字母序插一行 → PR
#    注意 fork 的远端可能被 insteadOf 改写成 ghfast 镜像，推之前先
#    git remote set-url origin git@github.com:<user>/public-apis.git

# 3. 扣子插件商店：国内唯一支持个人上架自有 API 的渠道（阿里云/聚合数据都要企业资质）
```

提交前必须满足四条：`/openapi.json` 可公开访问且与端点数一致、有 `/llms.txt`、
**免费端点不带任何 token 就能调通**（402 端点会被目录站的调试环节判失败）、描述里不写会过期的固定数量。

完整清单与坑见 [references/api-directories.md](references/api-directories.md)。

**五、MCP 本身也能上架，但不在 MCP 目录里。** WorkBuddy 的「连接器」就是 MCP 上架通道：
四个文件（`connector-meta.json` / `mcp.json` / `icon.svg` / 可选 `skills/`）打成 zip，
上限 20 MB，远程端点写 `type: "streamableHttp"` 即可，**不用自己起服务、不用写代码**。
审核 10–15 分钟生效，比技能快得多。但它**不参与收费** —— 连接器做曝光，技能做变现。

完整清单、`server.json` 约束、目录自检三件套、以及服务侧四条「不报错但结果为空」的静默错误，
见 [references/mcp-registries.md](references/mcp-registries.md)。连接器的包结构与认证三选一见
[references/workbuddy-connector.md](references/workbuddy-connector.md)。文案类踩坑见
[references/pitfalls.md](references/pitfalls.md) 的「文案相关」。

## 开工前的三步体检

```bash
# 1. 上架体检：布局 / LICENSE / 危险调用 / 网络行为
python scripts/preflight.py <repo>/skills/<name>

# 2. 打包：产出各商店要的形态
python scripts/build_package.py <repo> skills/<name> --out dist

# 3. 看全量渠道与它的提交形态
python scripts/submit_all.py --registry
```

`preflight.py` 报 ERROR 就别去提交——被拒一次会拖慢后续所有渠道的审核。

## 收尾

- 每个渠道都要留下**回执**（submission id / PR 链接 / 版本号），没有回执等于没提交
- 提交后不要反复轮询审核状态；pending 就是 pending
- 把「已提交 / 待登录 / 需移植 / 已排除」四类写清楚交给用户，不要让用户以为全都完成了

踩坑清单（含假表单、镜像劫持、名称被占、1 小时内重复提交 409 等）见
[references/pitfalls.md](references/pitfalls.md)。
