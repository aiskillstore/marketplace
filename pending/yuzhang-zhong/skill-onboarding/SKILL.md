---
name: skill-onboarding
description: "Meta-skill and Python state helper for when you only use 10% of a newly installed or newly built AI Agent Skill: safely test the skill in your setup with read-only probes and generate a concise one-page cheat sheet (usage card / quick-reference card) of hidden features, advanced commands, missing prerequisites, and example prompts. Pairs with skill-creator and merges fragmented CLI tool-family skills. 每次装完新AI技能只会用表面一两个功能？专门测试新装技能或新建技能（与skill-creator配套），做安全只读探测，把文档里藏着的进阶用法与隐藏命令总结成一页速查卡片（用法卡/速查表）。"
version: 3.4.0
agent_created: true
license: MIT
metadata:
  tags: "onboarding, capability discovery, CLI companion, skill usage"
  category: "productivity"
---

# skill-onboarding

<p align="center">
  <strong>用户第一次用上某个 skill 之后，跑一次、给一张卡。</strong>
</p>

<p align="center">
  <strong title="简体中文">🇨🇳 简体中文</strong> ·
  <a href="SKILL.en.md" title="English">🇬🇧 English</a>
</p>

## 为什么需要它

Skill 是渐进加载的：会话开始时只有 `name` 和 `description` 进上下文。
所以**用户永远只用得到最显眼的 1–2 个功能**，文档里其余部分等于不存在。

这个 skill 就干一件事：在用户第一次真正用上某个 skill 之后，**跑一次、看一眼、给一张卡。**

## 与 skill-creator 是一对

两个 skill **一起用**才完整：

```
skill-creator     →  建 / 改 skill
skill-onboarding  →  建完后跑一次真实验证，给一张用法卡
```

闭环是 **建 → 跑 → 卡 → 反馈**。用法卡暴露出来的问题（缺依赖、文档与实现不一致、能力没写清），
就是下一轮该改 skill 的地方。

`pair_with_skill_creator` 开着时（默认）：用 skill-creator 建完或改完一个 skill 后，**紧接着跑一次本流程**，不要建完就走。

分工：建 / 改 / 删 → skill-creator；跑一次 + 验证 + 出卡 → 本 skill；质量打分 → 两个都不做。

## 三步

1. **定对象** — 单个 skill，还是 CLI 工具族？
2. **探测** — 读全文 + 跑只读探针
3. **出卡** — 五段式，一口气读完

---

### 1 · 定对象

**一组 skill 实际是同一件事** → **整个族出一张卡**。两个信号：

- 共用同一个底层工具或服务（名字各不相同，底下指向同一套接口）
- 相互引用，或其中一个带"子技能路由"表（一个技能把活派给另外几个）

判据不是"名字像"，而是**用户分不清该用哪个**。

**反过来的情况同样成立**：一个 skill 里塞了几十个命令或几百个可选值，用户也只会用到最顺手的那一条。这类"单体过载"的 skill 出的卡和族卡结构完全一样，第二段照样按用户会说的话分组。

skill 可能分布在多个 skills 目录下，定位时都要找。**官方市场安装的 skill 也在范围内**，不在 `~/.workbuddy/skills` 的同样要算。

查是否已引导过：

```
python "<skill_dir>/scripts/onboarding_state.py" check <id>
```

`NEW` → 走完整流程。`SEEN` → 只在用户明确要求时重发。

### 2 · 探测

**读**：完整读 SKILL.md，**顺带扫一眼 `references/` 的文件名**——进阶能力常只在那里详述，主文件只有一句"详见 xxx"。

**跑**：挑成本最低、无副作用的那条，必须真调用。

| 类型 | 探针 |
|---|---|
| CLI 工具 | `--help` 拿子命令清单 → `doctor` / `status` / `whoami` 拿可用性 |
| 带脚本 | `--help` / dry-run / 喂最小假数据 |
| 生成类（文档、图片） | 写到临时目录，跑完删掉 |
| **无脚本 / 靠外部服务** | 查它声明的前置依赖在不在：工具是否在 PATH、连接是否已建立。有自检命令就跑自检 |
| 只能写（发信、下单、上线） | 不实跑，验证到参数构造完备为止 |

**同一批脚本里优先挑「检索 / 查询」类，避开「生成 / 调外部服务」类**——后者要密钥、有成本，还可能改外部状态。

**`--help` 和参数表就是能力清单，能跑全就跑全。** CLI 类跑每个主要域的 `--help`；脚本类跑每个主要脚本的 `--help`。
用户最大的盲区不是"这工具叫什么"，而是"它还有这十几个子命令 / 十几个参数"。

**三种容易被误判成"脚本坏了"的情况**：

- `--help` 报路径错误 → 多数是脚本**没实现参数解析**，把 `--help` 当成了输入。换不带参数跑，或按它自己打印的用法格式传参。
- 输出"未找到 `./xxx`" → 脚本**硬编码了相对路径**，必须在 skill 目录下运行，不是真缺文件。
- 返回结构化 JSON（哪怕是报错） → 这是该 skill 的输出协议，读 JSON，别看 traceback。

**真跑不通时四选一，必须选对**：缺依赖 / **环境问题** / 命令本身坏了 / 只是没实现 `--help`。
环境问题（shell、路径、wrapper）要写"环境问题，已绕过"，**不要写成"技能不可用"**。

### 3 · 出卡

```
<✅ 可用 ｜ ⚠️ 部分可用，原因 ｜ ❌ 没能验证，原因>
<一句话：它是什么，强在哪，弱在哪>

能干什么
    动作        会得到什么
    动作        会得到什么

几个多半不知道的
    口令        为什么值得知道
    口令        为什么值得知道

记不住就存这句
    最短的那一句
```

**第二个小标题按性质选**：工具类用 `能干什么`；方法 / 准则类用 `什么时候用得上`。

**一组 skill 出族卡**：第二段换成"你想做什么"清单，按用户会说出口的话分组，**不按命令名或模块名分组**：

```
能干什么
    发消息、管群       发消息、搜记录、拉群、加急
    定品牌调性        brand
    做 Logo、banner   design 内置
    做 PPT、提案      design 内置，带图表
```

（上面只是分组形状示意，不是照抄的样例。真实案例看 `examples/`。）

**规则**

- **不出现路径、文件名、来源。** 用户要的是能力，不是定位。
- **按说人话的标准写。** 短句，具体，口语。躲开「值得注意的是」「本质上」「这意味着」「不难发现」这类词，也别用装饰性 emoji（状态符号 ✅ / ⚠️ / ❌ 保留，它们有信息量）。
- 每条能力必须配**可复制的口令**。写不出口令，说明那还是功能描述。
- **段数是上限，不是配额。** 只有一两件事可做就写一两件，「几个多半不知道的」那段甚至可以没有。凑数是造假。
- 一口气读完为准：单个 skill ≤40 行，族卡 ≤60 行。
- 族卡的「几个多半不知道的」那段**优先写对比发现**：工具支持的范围 vs 本地已有的 skill，差集就是用户完全不知道的能力。
- 发现的问题要变成可执行下一步，不能只报错。
- **第一段那个数字要选最能说明"你用得有多浅"的那个。** 命令总数、能力域数、现成分类数，哪个最有冲击力就用哪个（"50 个命令""几百个现成分类"）。这是全卡最值钱的一句。
- **「几个多半不知道的」里第一条优先放"改变你整个用法"的那种**：不是某个冷门参数，而是让你换一条路走的能力（先分类再动手、先圈定范围再排序、用后台代替干等）。

**归档**

```
写卡 → ~/.workbuddy/skill-onboarding/cards/<id>.md
标记 → python "<skill_dir>/scripts/onboarding_state.py" mark <id>
```

## 配置

改一次长期生效，存在 `~/.workbuddy/skill-onboarding/config.json`（不存在则用默认值）。

```
python "<skill_dir>/scripts/onboarding_state.py" config                # 查看
python "<skill_dir>/scripts/onboarding_state.py" config set <key> <value>
python "<skill_dir>/scripts/onboarding_state.py" config reset          # 恢复默认
```

| 配置项 | 默认 | 作用 |
|---|---|---|
| `language` | `zh` | 卡片语言：`zh` / `en` / `auto`（跟随用户说话的语言） |
| `auto_trigger` | `true` | 用户首次用完某 skill 后，是否自动补一张卡 |
| `max_lines` | `40` | 单卡行数上限 |
| `family_max_lines` | `60` | 族卡行数上限 |
| `exclude` | `[]` | 明确不引导的 skill（`check` 会直接返回 `SKIP`） |
| `pair_with_skill_creator` | `true` | 建 / 改完 skill 后是否自动补一次首跑验证 |

写坏不了：非法值当场拒绝，实在乱了 `config reset` 回到默认。

## 安全

- **只读优先**：不删文件、不发消息、不写生产数据、不下单、不改配置。
- IM 写操作只允许 ≤3 人的会话，大群一律只读。
- 需要真触达第三方才能验证的，验证到参数构造完成为止，并注明"未实跑"。
- 验证用假数据，不引入真实业务数据。

## 别做

- 只读 description 就写卡 → 步骤 2 没做。
- 一次工具调用都没有，却写"已验证" → 假结论。
- 给同一族的每个 skill 各出一张卡 → 制造碎片，用户照样拼不出全貌。
- 输出评分表 / 合规检查 / 改进建议 → 那是 skill-tester 的活。
- 把 SKILL.md 的目录结构复述一遍 → 那是目录，不是用法。

## 环境备忘

- 脚本只用 Python 标准库，`python` / `python3` 直接跑；不在 PATH 就用你本地的解释器绝对路径。
- **指定工作目录请用带 `cwd` 的执行方式，不要依赖 `cd`**——某些受限 shell 里 `cd` 不生效，
  脚本仍在原目录执行；而不少 skill 脚本硬编码了 `./references/...` 这类相对路径。
- 部分 CLI 的 `sh` wrapper 依赖 `dirname` / `sed`。工具链残缺的 shell 里会崩在
  `Cannot find module '...\node_modules\...'`（路径少了一截，是 wrapper 没解析出目录）。
  绕开 wrapper 直接调它指向的真实入口即可——**这属于环境问题，不是 skill 坏了**。

## 样例

`example.md` — 一张普通卡 + 一张 CLI 工具卡，照那个密度写。
`examples/` — 三张真实卡：编程助手本体、PDF 工具（50 个命令）、选股工具（6 种入口）。这三张代表三种典型形态，出卡时对照。
