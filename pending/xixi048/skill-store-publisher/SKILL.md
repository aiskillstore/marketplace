---
name: skill-store-publisher
description: "Push an existing SKILL.md skill (or a whole skill repo) to agent-skill marketplaces at home and abroad, free and paid. Use it when the user asks to publish / upload / list / 上架 / 推送 a skill to skill stores, skill marketplaces, 技能商店, 技能市场, plugin marketplaces, or asks why a published skill is not being discovered. Covers repo layout for auto-indexers, public submit APIs, GitHub-PR registries, login-gated CLIs, platform-hosted stores that need porting, and how to price a paid listing. 关键词：上架技能、推送技能、技能商店、技能市场、skill store、marketplace、publish skill、被收录、署名。"
license: MIT
metadata:
  author: xixi048
  version: "1.0.0"
  language: zh-CN
---

# 技能商店全量推送

把一个已经能跑的技能推到尽可能多的分发渠道，并且**分清哪些能脚本化完成、哪些必须用户本人动手**。

## 先建立最关键的一条认知

「技能商店」不是一个东西，按**提交动作**分成五类；混淆它们会在一半渠道上白费时间：

| 形态 | 提交动作 | 代表 | 能否自动化 |
|---|---|---|---|
| 仓库自动索引 | 改仓库本身（路径 + topics + README） | skills.sh、SkillsMP、claude-plugins.dev | ✅ 完全 |
| 公开提交接口 | 一条 HTTP POST | skillstore.io、skillsmd.dev、skillbay.sh | ✅ 完全 |
| GitHub PR | fork → 加文件 → PR | buildwithclaude、awesome 列表、社区 registry | ✅ 完全（需 GitHub 写权限） |
| 登录式 CLI / OAuth 表单 | 先登录再发 | ClawHub、Tank、Cow Skill Hub、agentskill.sh | ⚠️ 缺凭据就停 |
| 平台托管 | **把技能用平台方言重写** | 扣子 Coze、智谱 AgentMore、GPT Store | ❌ 是另一个开发项目 |

只有前四类是「推送」，第五类是「移植」。不要在第五类上假装能"一键推送"。

完整渠道表（24 个，含国内外、免费与付费、验证等级）见
[references/store-registry.md](references/store-registry.md)。

## 推送顺序（照这个顺序做，返工最少）

1. **先修仓库，再谈提交**（顺序错了全白干）
   - 技能必须放在 `skills/<name>/SKILL.md`
   - 加 `.claude-plugin/marketplace.json`（顺带成为 Claude Code 插件市场）
   - 设 GitHub topics（`agent-skills` `claude-skills` `skill-md` …）+ 仓库 description
   - 布局与清单**两者都要**，它们分别喂给不同的爬虫
2. **自动索引型**：布局改完就等爬虫；用 `npx skills add <owner>/<repo>` 触发首次安装来播种 telemetry
3. **公开 API 型**：`python scripts/submit_all.py --all --repo <url>`
4. **PR 型**：按各仓库 CONTRIBUTING 的位置加一个 `<name>/SKILL.md`
5. **登录型**：先把物料备好，缺凭据就明确告诉用户"这一步需要你登录"
6. **平台托管型**：单独评估工作量，不要混进"推送"的进度里

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

**能 GitHub 导入就绝不本地上传。** 很多渠道的发布页同时提供「上传 zip」和「从 GitHub 导入」。
一律选 GitHub 导入：仓库是唯一真源，push 就能更新版本，不会出现商店版本与仓库不一致；
而且导入器通常能直接识别 `skills/<name>/` 布局。只有平台不支持导入或包需要在仓库外裁剪时才用 zip。

**定价。** 能收费的渠道就收费，同一个技能在不同渠道可以是不同形态、不同价：
免费渠道保留引流版，付费渠道挂完整版或 Pro 版。具体价位与各平台分成见
[references/paid-channels.md](references/paid-channels.md)。

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
