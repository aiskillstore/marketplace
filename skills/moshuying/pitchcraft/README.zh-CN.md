# pitchcraft （汇报.skill)

**语言：** [English](README.md) · [简体中文](README.zh-CN.md)

![License: Apache License 2.0](https://img.shields.io/badge/License-apache2.0-blue.svg)

**你的价值，值得被看见。**

写好代码是本事，让领导理解你做的事、相信你的判断、把你的建议放进决策里，是更大的本事。

但大多数人只练了前者。

pitchcraft 是一套结构化说服框架，覆盖项目立项、阶段汇报、结项总结、路演、方案推销五个场景。它不是写作模板——它帮你把做的事翻译成对方听得懂、愿意信、会行动的语言。

**影响力不是天生的，是可以被结构化的。**

---

## 为什么会有这个项目

AI 时代，执行力在贬值，说服力在升值。代码 AI 能写，但向决策层说清楚"为什么要做、为什么是我们、为什么是现在"——这件事 AI 做不了，但 AI 可以帮你做得更好。

pitchcraft 就是把这件事从"天赋"变成"流程"：

> 一套通用的说服结构 + 每个场景的实例化模板 + AI 主动追问材料和听众背景 + 提交前检查表。

## 和市面上"AI 写周报"工具的区别

|          | 通用 AI 写周报   | pitchcraft                               |
| -------- | ---------------- | ---------------------------------------- |
| 场景     | 周报、月报流水账 | 立项汇报、阶段复盘、路演、方案推销       |
| 输出目标 | 记录工作         | 说服对方、获得支持                       |
| AI 角色  | 填空机器         | 主动追问：缺什么材料、听众是谁、关注什么 |
| 核心理念 | "做了什么"       | "对方为什么要在意"                       |
| 记忆系统 | 无               | 记住领导背景、业务定位、格式偏好         |

---

## 框架：五段式说服结构

所有说服场景的底层结构相同，区别在于段落侧重：

```
Hook（钩子）→ Context（背景）→ Proposal（方案）→ Evidence（证据）→ Ask（请求）
```

每种汇报类型是这个框架的一个实例：

| 场景        | Hook 主打           | Evidence 主打        | Ask 方向       |
| ----------- | ------------------- | -------------------- | -------------- |
| 立项汇报    | 业务痛点 / 市场机会 | 壁垒（为什么是我们） | 要资源、要批准 |
| 阶段汇报    | 本期最快结论        | 关键数据             | 要决策、要协调 |
| 结项 / 年度 | 目标达成总览        | 量化成果             | 下期或交接     |
| 路演        | 市场空间            | 壁垒 + traction      | 要投资、要合作 |
| 方案推销    | 客户痛点对齐        | 案例 + 数据          | 要订单         |

---

## 安装

### npm / npx

```bash
# 全局（~/.claude/skills/pitchcraft/）
npm install -g pitchcraft
```

或使用 [Vercel skills CLI](https://github.com/vercel-labs/skills)：

```bash
npx skills add moshuying/pitchcraft -a claude-code -a cursor -y
```

发布到 npm：`npm publish`（若包名 `pitchcraft` 已被占用，可改为 `@moshuying/pitchcraft`）。

### Claude Code

```
/plugin marketplace add moshuying/pitchcraft
/plugin install pitchcraft
```

或者直接告诉你的 Agent：

```
Install pitchcraft for me: https://github.com/moshuying/pitchcraft
```

重启后输入触发词即可。需要中文 Skill 时，将 `.claude/skills/pitchcraft/SKILL.zh-CN.md` 复制为 `SKILL.md`（见下方「多语言」）。

### SkillsMP / GitHub 收录

[SkillsMP](https://skillsmp.com) 会自动抓取带根目录 `SKILL.md` 且 frontmatter 含 `name`、`description` 的仓库。本仓库根目录 `SKILL.md` 与 `.claude/skills/pitchcraft/SKILL.md` 保持同步，兼顾收录与插件安装。

在 GitHub：**Settings → General → Topics** → 添加 `claude-skills` 或 `claude-code-skill`（每日同步）。

### Cursor / Codex / 其他 AI

| 工具                    | 方式                                                                          |
| ----------------------- | ----------------------------------------------------------------------------- |
| Cursor                  | 将 `prompts/universal.zh-CN.md` 或 `prompts/universal.md` 粘贴到 Rules for AI |
| Codex CLI               | 同上，设为系统指令                                                            |
| ChatGPT / Claude 网页版 | 直接粘贴对应语言的 prompt 文件                                                |

### 触发词

- **「汇报」或「简报」** — 跨级汇报，15 分钟定印象
- **「立项汇报」** — 说服决策层批准启动
- **「阶段汇报」** — 同步进展，争取继续投入
- **「结项总结」** — 复盘目标达成，沉淀资产
- **「路演」** — 向投资人或合作伙伴展示
- **「方案推销」** — 向客户推荐解决方案

---

## 它怎么帮你

pitchcraft 不是一个丢给 AI 就能自动写好汇报的"魔法棒"。它的工作方式是：

1. **确定场景** — 立项、阶段汇报、结项、路演还是方案推销？
2. **追问材料** — 按场景检查材料完整性，缺什么 AI 主动问你要
3. **了解听众** — 对方是谁、了解多少、关心什么？结构会根据答案调整
4. **按结构写** — 五段式框架生成初稿，不跑偏
5. **检查清单** — 提交前逐项核验：每个数字有出处？每条风险有判断？

这套流程确保：**你花时间在内容本身，结构的事交给 AI，检查的事交给清单。**

---

## 多语言

| 文件                                       | 语言                    |
| ------------------------------------------ | ----------------------- |
| `README.md`                                | English（默认）         |
| `README.zh-CN.md`                          | 简体中文                |
| `prompts/universal.md`                     | English                 |
| `prompts/universal.zh-CN.md`               | 简体中文                |
| `.claude/skills/pitchcraft/SKILL.md`       | English（插件默认安装） |
| `.claude/skills/pitchcraft/SKILL.zh-CN.md` | 简体中文                |

---

## 目录结构

```
pitchcraft/
├── SKILL.md                      # 根目录 skill（SkillsMP 收录）
├── package.json                  # npm 安装入口
├── scripts/install.js
├── .claude/
│   └── skills/pitchcraft/
│       ├── SKILL.md              # English（插件安装源）
│       └── SKILL.zh-CN.md        # 简体中文
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── commands/
│   ├── pitchcraft.md
│   └── pitchcraft.zh-CN.md
├── prompts/
│   ├── universal.md
│   └── universal.zh-CN.md
├── README.md
├── README.zh-CN.md
├── LICENSE
└── .gitignore
```

---

## 阅读参考

这套框架的思想受益于以下著作：

- Malcolm Gladwell — **《Blink》（《眨眼之间》）**：第一印象如何形成，以及如何在有限信息下做判断。汇报的前 10 秒决定一切。
- Malcolm Gladwell — **《The Tipping Point》（《引爆点》）**：观念如何扩散，什么让一个想法被接受。说服的本质是降低对方的接受门槛。
- Chip Heath & Dan Heath — **《Made to Stick》（《让创意更有粘性》）**：SUCCESs 框架（简单、意外、具体、可信、情感、故事），每条都是汇报的血肉。
- Robert Cialdini — **《Influence》（《影响力》）**：互惠、承诺、社会认同、喜好、权威、稀缺——说服的底层原理，五段式结构的设计起点。
- Nancy Duarte — **《Resonate》（《共鸣》）**：好演讲的底层是"现状 vs 未来"的张力，汇报的每个段落都在制造并释放这个张力。
- Barbara Minto — **《金字塔原理》**：结论先行、MECE 原则、纵向分层——结构化表达的基础，是这套框架的底层语法。
- Anne-Laure Le Cunff — **《Tiny Experiments》（《微实验》）**：如何在不确定的环境中做决策和展示进展，对阶段汇报和立项汇报尤其有启发。

---

## 核心理念

### 不是什么

- ❌ 不是"AI 自动写周报"——日常流水账不是它的场景
- ❌ 不是《金字塔原理》的重复——框架是具体的、可执行的，不是原则清单
- ❌ 不是拍马屁和话术——核心是让你做的事被正确理解

### 是什么

- ✅ 一套结构化说服方法论，适用于任何需要"在有限时间内说服特定对象"的场景
- ✅ 每个类型是同一个底层框架的实例，学了立项汇报就自然会路演
- ✅ 带有检查机制，保证不遗漏关键要素
- ✅ 在 AI 时代，让你的执行力被看见、被认可、被放大

---

## 项目状态

当前版本：v1.0 — 核心框架 + 5 种场景模板 + 工作流 + 检查表 + 跨平台安装 + 中英文

规划中：

- 日文 / 韩文翻译
- Web 交互式写作助手
- 更多场景：周报模板、双月汇报、技术评审、事故复盘

---

## 许可证

[Apache 2.0](LICENSE)。

---

## 关于作者

由 [@jiujiangliu](https://github.com/moshuying) 创建。在 real world 的业务汇报中反复打磨出来的框架。
