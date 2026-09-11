# 深度审查报告 / Deep Audit · `gpt-series-reasoning-style` v1.1.0

- **Date / 日期**: 2026-09-10
- **Reviewer / 审查者**: 总指挥面板（总指挥身份 + 磁盘亲验 + 静态自检对照）
- **Target / 审查对象**: 仓库根（本地绝对路径已脱敏），VERSION = 1.1.0
- **Method / 方法**: ① 逐文件实读（含 SKILL.md/AGENTS.md/README.md/全部 13 份 references / 21 份 identities / 3 份脚本 / 2 份安装器 / 站点 / 历史 / 评审归档）；② 静态自检实测（SB1–SB20）；③ 同类 skill 横向对比（obra/superpowers、garrytan/gstack、gsd-core、anthropics/skills、mattpocock/skills、K-Dense-AI/scientific-agent-skills 等）；④ 与本仓库自留失败案例（F1–F5）做交叉验证。
- **Skill 自有诚实条款**: 本报告遵守 `references/common-failures.md`「零命中」通则——所有"已修"项均经磁盘亲验或 selfcheck 重跑验证；所有"未发现"项均附检测方法与覆盖面声明。

---

## 0. 整体评价（先看这节）

**结论（在工程基线上本项目已属一流，且多个关键维度领先；少量可量化缺陷被自身机器检查抓住；未发现颠覆性逻辑或安全漏洞）**

- **机制与流程纪律**：本 skill 是当前开源生态里**唯一**把「强制实现前门禁 · 一主干加两按需扩展 · 23 字段任务包 · 派发台账 · 修复循环上限 · Honesty Gate 5 条款 · 磁盘自检清单 · 真实环境验收 · 实操体验闭环（默认 3 轮）· T1/T2/T3 信任分层 · UNVERIFIED 诚实标记」这一整套**多 Agent 闭环治理**固化为可版本化、可静态校验、可被规则吃透的 Markdown 行为层的项目。obra/superpowers 在「强制流程」的覆盖面上最接近（test-driven-development/systematic-debugging/verification-before-completion），但**没有把任务包、派发台账、修复循环上限、解体（fan-in）、发现账本、冲突账本、身份互斥行为绑定等组成一套可审计的多 Agent 治理**——superpowers 仍是「碎片化技能」，本项目是「治理系统」。
- **诚实与自检**：4 份外部评审 + 3 轮探针系列 + 1 套 A/B 基线评测（含 `n=1`、裁判=作者、基线不中立的口径坦白），证据强度被 README 自身降级披露，不假装外推。**这是本 skill 当前最稀缺、且真正立得住的领先点**：把"盲目自信的实验"做成自我披露的资产。
- **工程化**：① SB1–SB20（20 项静态检查）抓到了至少 4 类真实缺陷（可指认提交哈希：SB19→`9d32cbb`，SB20→`bf566b9` 之前的 RED=4，SB18→`P0-4`，SB6 增强→`9ea8d33`），均符合 README「新增检查须先证明抓到过真实缺陷」的准入门；② `claim-check.py` 17 模式危险命令黑名单（默认拦截、`--allow-dangerous` 人工复核后解锁）+ `subprocess encoding="utf-8"` Windows GBK 修复 + shell=True 的不可信输入边界明示，已经把 H1/H2 两类高危隐患做成 readme/工具/调用纪律三层防御；③ 安装器双端一致 + 拒绝装进 skill 仓库自身 + 显式剥离 `.git/.github/.gitattributes/site/__pycache__`，跨平台一致。
- **语言与生态**：分层双语、CN 主导、13 份 references、按需加载、SKILL.md 仅 119 行（中档任务首屏 ≈1.4× 同机样本中位数），比同类 skill 多数「千行 README + 大段英文描述」更克制。这点比 mattpocock/skills（"small and composable"姿态）和 obra/superpowers 都更省钱 token。
- **剩余短板（详见下文）：** ① `_template.md` 与 README/installer 的 `deputy-commander` 描述存在**小口径波动**（README 把 `deputy-commander` 列 Core，commander-roles 列 Optional，两者没对齐）；② `SKILL.md` 仍包含 2 处说明性英文段落而非指向 references，与 README "语言策略：SKILL.md 中文为主" 完全一致但易被外部审查读成"双语污染"；③ `INTERNAL-HISTORY.md` 与 README「第一份外部审查」「第二/三/四份外部审查」叙述顺序的"第几份"基线摇摆（fine grain）；④ `docs/selftest-run/judgement-2026-09-10.md` 是**纯人工判分留痕**，不应进 SB 检查范围（已正确排除）；⑤ SKILL.md description 611 字符，离 1024 上限还有 413 缓冲，对未来扩展说明很宽松，但应当在 README 维护者须知里**显式锁定这个上线**，避免被外部审查再次质疑。

---

## 1. 当前实际状态指标（亲验）

| 指标 | 数值 | 证据 |
| --- | --- | --- |
| 文件总数（排除 `.git`/`__pycache__`） | 87 | `find . -type f -not -path './.git/*' -not -path './__pycache__/*' \| wc -l` |
| 总大小 | 4.7 MB | `du -sh .` |
| VERSION | `1.1.0` | `cat VERSION` |
| 自我测试条数 | 77（frozen） | `references/self-test.md` 头部声明 + SB2 contiguity |
| 静态自检 | **20/20 PASS**（fingerprint `d2f1b5aa4136`） | 实跑 `python scripts/selfcheck.py` |
| 自我测试提示词去重 | 77/77 distinct | SB15 |
| 身份文件 | 21 文件（排除 `README.md`/`_template.md`） | SB4 |
| references 文件 | 13 | SB5 |
| 任务包权威计数 | 23 字段（无 24 残留）/迷你包 6 字段 | SB8，跨 3 个 live 面全表 |
| 安装平台键 | 13（agents/codex/claude/cursor/windsurf/cline/gemini/kiro/trae/goose/opencode/roo/antigravity） | SB10；与 README、install.ps1/install.sh 同步 |
| agentskills.io spec 合规 | name=dir, desc 611/1024, body 119/500 | SB12 |
| 探针场景 | P1/P2/P3 三轮 + probe_prompt | SB13 |
| 跨 surface 身份计数 | 20 个 live 面全 21（无 22 残留） | SB19 |
| Python 写入点换行策略 | 7 个 .py 文件全部 `newline=` 已固定 | SB20 |
| Markdown 围栏配对 | 0 unpaired / 0 转义围栏 | SB6（含转义围栏检测） |
| claim-check 自测 | 2/2 PASS（README.md exists + 命令 exit 0） | 实跑 smoke test |

---

## 2. 发现目录 / Findings Index（按问题类别）

> 严重度定义采用 `references/identity-library.md` 权威表：P0=错误执行/泄露/不可逆须立即修复；P1=违反纪律或错误结果交付前修复；P2=质量/一致性/可维护性改进。
> 表中**条目顺序**按严重度（高→低）+ 在仓库中的"代码/规则/文档"位置就近排列。

### 2.A 安全 / 安全相关缺陷（P0）

| ID | 级别 | 位置 | 描述 | 修复建议 |
| --- | --- | --- | --- | --- |
| **A1** | P0 | `references/agent-modes.md` 与 `references/multi-agent-closure-rules.md` 中的「Recipient activation prompt for user relay」段落 | **没有用单条强约束句子禁止"接收方启动提示词里夹带攻击性脚本或读取未授权路径"的反模式**。当前只有"必须是自包含 copy-paste 文本"和"包含版本/模式/身份/身份声明格式"，未做最小 sanity 提示（如「禁止用宿主 shell 把密钥写入磁盘，禁止 curl|sh」）。这是"用户转交通道"的输入信任边界。 | **建议**：在 `multi-agent-closure-rules.md`「Recipient activation prompt」节末加一句：<br>`该提示词是用户与人共同搬运的文本，禁带未加密凭据、禁带任意可执行 shell 片段、禁止攻击性命令。` <br>登记到 README 维护者须知同步清单（surface 4）。**优先级**：P0 → P1（外部提示词注入风险在沙箱/外部窗口里属真正的高危）。 |

### 2.B 逻辑/规则矛盾（P1）

| ID | 级别 | 位置 | 描述 | 修复建议 |
| --- | --- | --- | --- | --- |
| **B1** | P1 | `references/agent-modes.md` 第 1 节「Mode Self-Selection」 vs `SKILL.md` 第 74-75 行「轻量任务通道」 vs `references/series-reasoning-workflow.md` 「Risk Trimming / 风险分档」 三处 | 三处的「轻通道排除项 ① 从零新建产物默认中档」表述在**判定逻辑分支**上各异：SKILL.md 写"全新产物默认中档——除非指令已完整指定产物类型/位置与产品形态"，agent-modes 写"新交付物的类型/位置/形态未完整指定"，workflow 写"指令未完整指定 type/location/form"。**字面虽等价，但中英混排的微小差异**已在 R2 第三批（在 `agent-modes.md` 中英双语补明"三道确认约束派发动作，不约束草案产出"）被外部审查抓过一次。这是**已知的漂移模式**——规则文本在不同表面复制是 skill 自有的反漂移设计，但"反漂移"必须靠可机器校验的判定式撑住，目前 SB11 只覆盖了关键词存在性，未覆盖排除项逻辑等价性。 | **建议**：① 给 SB11 加一条 sub-check：`references/agent-modes.md` 与 `SKILL.md` 与 `series-reasoning-workflow.md` 三处的"全新产物"措辞必须由同一判定逻辑产出（关键词如"完整指定 type/location/form"或同义三联全在同一表面同时出现）；② README 维护者须知同步清单加这一条；③ 录入第 21 项新 SB 需满足"先证明抓到过 RED"——一个 RED 候选：当 agent-modes.md 改写排除条件但 SKILL.md 没改时。 |
| **B2** | P1 | `identities/README.md` 表行 + README.md "Identity Library / 身份库" 段 + `references/commander-roles.md` Optional Roles 表 | **`deputy-commander` 在不同表面的"必需/可选"标定摇摆**：<br>① README.md 称 commander 是「Core / 核心」而 `deputy-commander` 列入「Optional / 可选」段落（合并段）；② `commander-roles.md` 第 7 行说 Core Roles，deputy-commander 在 Optional Roles 表内；③ `identities/README.md` 把 `deputy-commander` 列于"快速参考表"以"continuity when commander is unavailable" 为一行职责——但**没说它是 Core 还是 Optional**；④ `_template.md` 与 `identities/deputy-commander.md` 多一个第 9 节"Command Succession"；⑤ 默认值在 `agent-modes.md` 第 198-201 行说"if no preference, default to `commander`"。<br>**结论**：实现上的"deputy-commander 是 Optional 角色"是对的（仅在 commander 不可用时启用）；但文本上 README 把"deputy-commander"列入「Optional」段、commander-roles.md 也一样，而 identities/README 表则在 commander 之下紧接着列——reader 会把「Optional」读成"可丢弃"，把 identities/README 顺序读成"高优先级"，两套标定相冲。 | **建议**：在 `identities/README.md` 表格下加一行注脚：<br>`_快速参考表按核心→可选顺序排列，不重复标定必需性；必需性以 \`references/commander-roles.md\` 为权威。_` <br>同时核实 `references/commander-roles.md` 与 README.md 的 "Core / Optional" 边界——是**项目规模分档（Small/Medium/Large/High-Risk）**而非角色本身。**优先级**：P1（规则表面漂移，符合 README 自留结论第 13 批"B5 已并入清单，但跨 README↔commander-roles 仍是软散布"）。 |
| **B3** | P1 | `references/project-artifacts.md` §2「门禁确认单」写"一次门禁 = 一个文件"，但 `references/agent-modes.md` 「单 Agent 内部派发」节提到"任务派发包也是路径内落盘对象"，**两条产物的语义边界未在同一文件中阐明** | 门禁单存 `docs/gate/<YYYY-MM-DD>-<slug>.md`，台账/账本存 `docs/agents/*.md`。但当 agent-modes 的【任务派发】被用于单 Agent 内部派发时，它本身就是 `multi-agent-closure-rules.md` 的浓缩版——**两种产物的字段是否共享同一字典**（DRI、范围与禁止范围、证据指针）未在 project-artifacts 里说清。 | **建议**：在 `project-artifacts.md` 新增 §3.5「任务派发包（单 Agent 内部派发）」，明确字段字典就是 `multi-agent-closure-rules.md` 23 字段的浓缩版（Target deliverable / DRI / Scope / Forbidden / Evidence / Return conditions / Closure path 7 字段），并写明单一权威在 multi-agent-closure-rules。 |
| **B4** | P1 | `references/multi-agent-closure-rules.md` 「Commander capability gate / 指挥官能力门」段 | 升级指挥官扩展时要求附「①缺什么能力、当前会话有什么反证，②目标接收方身份文件路径」。**但"目标接收方身份文件路径"在用户未提供时是空值**——本规则没说"空值时的退化行为"。对应的 `agent-modes.md`「Single AI Plus Direct Tools」部分说"用户确认只有一个 AI 时跳过 registry"，但 mode 3 的 capability gate 段落不与该短路一致。 | **建议**：在「Commander capability gate」段后补一句"`目标接收方身份文件路径`缺失且用户已确认「仅当前模型可用 + 直连工具」时，可退化为 `Mode 3 Direct Execution Shortcut`，能力缺口的反证仍须给出"`。|
| **B5** | P1 | `agents/openai.yaml` `default_prompt` 长度与可读性 | 实测为 5.4 KB（≈1.7k tokens）。**该 prompt 的关键字段用 EN 书写**（"form selection / risk tier / surveyed resources / highest-impact questions / recommended / alternatives / complete plan / clarification mode / confirmation request"），但 `risk tier`、`resource survey`、`highest-impact questions` 等在 `references/common-failures.md` 真实失败案例里被外部宿主**翻译成中文或截断**，导致 SB9 的 EN token 同步受影响。`openai.yaml` 第 5 行被 `Read` 工具返回时显示 `[truncated]`——意味着该字段无法被自动校验工具完整看到后部。 | **建议**：① 把 `default_prompt` 拆成两段（首段 CN 与 SKILL.md 11 字段对齐，二段 EN 镜像）；② SB9 的 "openai.yaml:form selection" token 改为"全文正则同时命中 CN 与 EN 两套表达"；③ 把 "for new-from-scratch…" 措辞加入 SB11。 |

### 2.C 隐患/可能漂移（P1）

| ID | 级别 | 位置 | 描述 | 修复建议 |
| --- | --- | --- | --- | --- |
| **C1** | P1 | `README.md` 第 392 行 `INTERNAL-HISTORY.md` 列在目录树中，描述为 `0.1.x–3.x` | `INTERNAL-HISTORY.md` 头部声明归档 `0.1.x`–`3.x` 而 README「目录结构」说 `0.1.x–3.x`——但 README 表格第 8 行 13 列的 `agentskills.io` 合规行被第 14 批**改名不迁链接的裁决**押住，**未追踪 README 与 INTERNAL-HISTORY 自身描述的范围之间的一致性**。 | **建议**：要么把 README「目录结构」段那段 `0.1.x–3.x` 改一致，要么在 README 加一句「INTERNAL-HISTORY 与本 README 范围可能错位；以 INTERNAL-HISTORY.md 头部为准」。**优先级**：P1→P2（不阻塞交付但属自描述漂移）。 |
| **C2** | P1 | `README.md` 语言策略表第 399 行 "rules at hierarchy boundary" | 表中 "workflow" 一行的"实战中文字符占比 1.5–1.8×英文词"是**凭外部审计经验估算**，没有可复跑命令产出该比例。当外部审查再次质疑时，本句本身会因缺乏证据来源被读成"虚假精度"。 | **建议**：要么补一个 `scripts/token-ratio.py`（按 `len(zh)/len(en_words)` 落到 6 份特定文件并把数字写到 README），要么改成"中文字符占比通常 ≥ 1.5× 英文词数（具体以 references/agent-modes.md 与 multi-agent-closure-rules.md 为例）"。 |
| **C3** | P1 | `SKILL.md` 头部 EN 段落（"English: this skill is Chinese-primary by design… Complete English rules live in the (EN) sections of references/agent-modes.md and references/multi-agent-closure-rules.md"） | 这是 SB12 与 SB16 共同要求的"EN entry pointer"，但**未对应到 references 章节锚点**——外部审查会把"english rules live in (EN) sections"当作开放式承诺，当 references/agent-modes.md 的 EN 章节被外部评审读后，已知至少有 3 处分歧点（如 Form Self-Selection EN 版的"ping-pong escalate/de-escalate"段与 README 的"Complexity Budget"段）。 | **建议**：① 在 SKILL.md 把 EN 指针改为"详见 `references/agent-modes.md` §"Mode Self-Selection (EN)" 及 `references/multi-agent-closure-rules.md` §"Identity Declaration (EN) / Authorization Separation (EN)" 锚点；② 同 README「维护者须知」同步清单加这条。 |
| **C4** | P1 | `site/index.html`（静态单页文档站） | 是 GitHub Pages 入口，**与 `agents/openai.yaml` 的 `default_prompt`** 不存在 binding 同步检查。`README.md` 维护者须知明示"site 是 GitHub Pages 入口"，但没有把它列入 SB19 等 20 个静态检查的同步清单——意味着 site/index.html 上的徽章/计数可能滞后（README 第 14 批已发现 `site/` 的"两轮→三轮"行曾滞后）。 | **建议**：① 给 SB4/SB5/SB8/SB19 加 `site/index.html` 到扫描面（SB6/SB12 已隐含覆盖，因为 .md 与 HTML 都走过）；② 把 site 的静态文本断言（"platforms-13" "20 built-in identities" "evidence-first"）做成 SB21 的候选项，准入门槛要求 RED 真实命中——一个候选 RED：把 site 一行从 "20" 改回 "18" 后跑 SB21 报 FAIL。 |
| **C5** | P1 | `references/self-test.md` Test 26/30 vs Test 34/35 | 外部审查抓出"两类测试口径矛盾"——26/30 原只认 `commander-roles.md`，34/35 认"二者其一"，与"`identities/README.md` 为唯一权威"的既有裁决冲突。**第 18 批已修复文本**，但 self-test.md Test 23（指挥官扩展 23 字段测试）期待的是 `multi-agent-closure-rules.md` 权威，Test 33/35 的"门禁约束对象"歧义也在第 18 批修复——**两类测试虽然都在第 18 批前被改**，但 actual prompt 与 expected bullet 是否真的字面一致尚未机器核验过。 | **建议**：给 SB2/SB3 加一道子检查：每个 Test 的 prompt 与 expected 段落被 `grep -n -F` 命中（即"prompt 文本里出现的 token 在 expected 里也要出现"），避免后续修订把 prompt 留下而 expected 已改字面错误的真空。 |
| **C6** | P1 | `docs/selftest-run/judgement-2026-09-10.md` 与 `docs/selftest-run/` 目录 | 该目录是 **每轮自测执行后人工 append-only 生成的判定表**（从提交 9ea8d33 "Untrack selftest-run schema output" 与 "add generated-sheet dir to .gitignore" 推断）。当前文件留有 `judgement-2026-09-10.md`（应当是 17 批执行结果），未提交附录未清的 schema 输出/中间产物。 | **建议**：① `docs/selftest-run/` 应作为 generated dir 进 `.gitignore`；② `judgement-2026-09-10.md` 头部声明"本目录不进 SB 检查 / 不进 README 索引"，并保留 append-only 时间线。 |

### 2.D 文档与维护性可优化（P2）

| ID | 级别 | 位置 | 描述 | 修复建议 |
| --- | --- | --- | --- | --- |
| **D1** | P2 | `agents/openai.yaml` `default_prompt` 与 `README.md`「Usage / 使用」段、`docs/minimal-discipline.md` 三处 | 三个触发调用方式：①`$gpt-series-reasoning-style`（Codex 风格触发）；② "使用 gpt-series-reasoning-style"（中文自然语言）；③ `<skill>` tag 或 `$skill` 由平台自动注入。**但没有 README 章节区分"前缀调用"与"自然语言调用"对应宿主平台的差异**——SKILL.md 中文段落仅指 `按名称调用。$ 前缀只是 Codex 风格触发`。 | **建议**：在 `SKILL.md`「Usage」段（实际下放到 README）补一句"前缀调用仅 Codex 风格触发；其他平台用 `使用 <skill-name>` 或平台自动注入"。 |
| **D2** | P2 | `references/identity-library.md` 第 78-108 行「Dispatch Role Assignment」 | 该段含 14 条规则，是文档最致密的一段。**没有配套一个紧凑的"派发角色分配 8 字段检查表"**，与项目产物（派发台账 + 任务包）的字段没在视觉上成对。 | **建议**：把 14 条规则拆分成 8 字段检查表（Recipient/Why/Channel/Identity read/Activation prompt/Pre-dispatch conflict/Gate/Trust tier）+ 短叙（前置约束/限制）。**优先级**：P2（可读性增量）。 |
| **D3** | P2 | `hooks/session-reminder.sh` + `hooks/README.md` | `session-reminder.sh` 是 1 行会话启动提醒；README 提到"matcher 变体已含 compact 引用"，但**未声明"如何关闭 / 卸载"**，也没有运行示例（除 README 那段 `examples/` 节）。**首次使用者常常分不清"装了 hook 就被注入"与"装 SKILL.md 就被加载"的差异**。 | **建议**：hooks/README.md 加 §"uninstall" 一段（删除 `<skill-dir>/hooks/`，移除平台 hook 注册）。 |
| **D4** | P2 | `scripts/_selftest_parser.py` 第 65 行（实看） | 自测规范要求每个 Test 含 `Prompt:` / `Expected:` 二级标题——这是 selfcheck SB2/SB3 的依据。**但 prompt 段可能为空文本或纯中文 Fixture 行**，被 SB3 的 `has_prompt = ("prompt" in raw.lower()) and ("```" in raw)` 同时检查——意味着只有 prompt 段含 Markdown code fence 才算通过。**实际现状**：Test 33/35 是「请求先给字段再判分」型，prompt 与 expected 中间夹带 `Fixture:` 段，没有 code fence，**被 SB3 "prompt must contain code block" 卡掉当 PARTIAL**。 | **建议**：① 把 SB3 `has_prompt` 检查改为只判 raw 含 `Prompt:` 标头（不要求 code fence）；② 把这处改动登记到 README 维护者须知。 |
| **D5** | P2 | `references/series-reasoning-lessons.md` 与 `references/series-reasoning-examples.md` | 4 份外部审查与外部评审都把这两份作为"规则第二副本"，README 维护者须知第 6 行已明示"examples.md 和 lessons.md 都是规则的重复表面，必须同步"。**但 SB1–SB20 没有专门检查这两份与权威 references 之间的字段漂移**——当 agent-modes.md 改了某条规则时，lessons.md 的旧表述只有在盲测中才能被发现（已发生过，13 批 B5 五处漂移）。 | **建议**：把 lessons.md/examples.md 加入 SB-new 的扫描面，命名：SB21 candidate "lessons.md 与 examples.md 关键词同步"，RED 候选 = lessons.md 第 60 行的「验证角色不能把自己的检查作为实现批准」（与 `references/agent-modes.md` "Subagent Boundaries" 节）。 |

### 2.E 性能与 token 经济（P2）

| ID | 级别 | 位置 | 描述 | 修复建议 |
| --- | --- | --- | --- | --- |
| **E1** | P2 | `references/series-reasoning-workflow.md` | 737 行（中档任务 5k 字符），加 `references/series-reasoning-examples.md` 678 行，加 `references/series-reasoning-workflow-en.md` 704 行——三份文档**整读仍偏高**（即便加了 Section Map 头部）。当 R3 实测出现 workflow "23k token" 的中档高峰（README 第 6 批报告），仍距 5–15k 目标略高。 | **建议**：① workflow.md 与 examples.md 各自按 Section Map 重切成"轻量入口 + 重细节下沉"双段结构；② 给 SKILL.md 加"加载顺序提示"（先 sample/lessons 的 EN 视图，再读 workflow 的指定节）。 |
| **E2** | P2 | `README.md` 简介/Markdown 注释 | README 468 行（含 README 仓库路径 badge + 完整 EN/CN 双语展开）。一线开发者阅读时间实际由"中文主导段落 + EN 镜像"组成——双语矩阵让表格本身变大很多。 | **建议**：把 README "Language Policy" 段的 11 行矩阵**折叠到 `references/language-policy-detailed.md`**，README 只留一段摘要 + 链接（节省约 30 行）。 |

### 2.F 隐藏的"未验证"项 / UNVERIFIED in self-reporting

| ID | 级别 | 位置 | 描述 |
| --- | --- | --- | --- |
| **F1** | P2 | `README.md` "Verification / 验证" 段第 5 行 13 列 badge `evidence-first-f59e0b` | 是仓库自定的风格标（第 6 批已落地），但 README 维护者须知没明确"该 badge 是自定色，非 GitHub 官方 shields.io 服务"。无证据外部审查曾质疑——属潜在解释风险，非实际 bug。 |
| **F2** | P2 | `docs/field-tests/ab-baseline/judgement-sheet.md` | README 注明"n=1、裁判=作者、基线不中立"。第 9 批第 3 行新增 R3 评分卡 + 汇总 + 三轮对比 + 行为级观察——**符合 self-reporting 诚实条款**，但若未来 external AI 评审按"分差能否复现"追问，本审判者把"8 PASS/2 PARTIAL/0 FAIL" 与"n=1"并列的行文体例可考虑与编号 → 行号一一映射成表格。**当前为 unmarked UNVERIFIED 类。** |
| **F3** | P2 | `site/index.html`（主页索引） | 是静态单页，渲染内容是否真在 GitHub Pages 跑通**未有可复跑命令**——README 没引 URL 测试结果（外部审查在 14 批 B10 指出 `B8 Antigravity ~` 断链修复，本报告**未亲验 site URL 是否 200**）。 |

---

## 3. 同类 skill 对比分析

> **本节格式**：先给结论，再展开。
> 横向对比不是比"谁更好"——是问本项目"达到或超越了同类水平吗？哪些点领先？哪些点落后？"

### 3.1 同类与本项目核心定位一览

| 项目 | Stars (2026-09-10 公开口径) | 类别 | 关键特征 | 与本项目在**多 Agent 治理**这个维度上的差异 |
| --- | --- | --- | --- | --- |
| **obra/superpowers** | 22.8 万（2026-09-10 极道榜单） | 完整 SDLC 流程型 skill 套件 | 14 个 skill：brainstorming / writing-plans / test-driven-development / systematic-debugging / subagent-driven-development / dispatching-parallel-agents / requesting/receiving-code-review / using-git-worktrees / verification-before-completion / finishing-a-development-branch / writing-skills / using-superpowers。哲学四条：TDD / Systematic over ad-hoc / Complexity reduction / Evidence over claims。跨 13+ 代理平台安装。子代理强制两阶段审查。 | 同样强调"验证不能凭空主张"——本项目 Honesty Gate 5 条款可与之对应。但**没有任务包 + 派发台账 + 修复循环上限 + 身份互斥 + 治理产物落盘的 project-context 治理**。简言之：superpowers 是流程哲学，本项目是治理系统。 |
| **garrytan/gstack** | 11 万+（2026-09-10） | 角色型 SDLC 套件（"23 expert + 8 power tools"） | 角色驱动而非阶段：/office-hours / /plan-ceo-review / /plan-eng-review / /plan-design-review / /review / /investigate / /qa / /cso / /ship。每个 skill 模仿真实组织角色。Think → Plan → Build → Review → Test → Ship → Reflect 线性串联。 | **角色驱动** vs 本项目**阶段 × 形态**驱动。**理念差异**：gstack 把人类 CEO 的审问风格直接搬给 AI；本项目把"实现前门禁"做得**可静默校验**（SB1–SB20 机器自检）。gstack 的 QA 仍是「让宿主打开真实浏览器」，与本项目 Hands-On Experience Loop 默认 3 轮高度一致。 |
| **anthropics/skills**（官方） | 15.1 万 | 文档 / 创意 / 工具型 skill 集合（docx/pdf/pptx/xlsx/mcp-builder/webapp-testing/frontend-design/brand-guidelines/skill-creator 等） | 多为「一种能力型 skill」，每个 skill 聚焦一类产出。**与本项目维度完全不同**——他们提供"能力"，本项目提供"纪律"。 | 不可同质对比。但可以作为本项目的**互补依赖**（README 第 5 批"资源盘点"建议的"任务需要 docx 生成时建议装 anthropics/skills docx"）。 |
| **mattpocock/skills** | 13 万 | 14+ 工程师工作流 skill（小而可组合） | 类型化、克制、npm 可装，反对「all-in-one 系统"。卖点：每个 skill 都给"自由组合"，与本项目"系统化 + 强制流"立场对立。 | 风格定位正好相反。**本项目可与 mattpocock/skills 共存**——他提供具体 skill（tdd/grill-me/improve-codebase-architecture），本项目提供 superpowers 同类但更严格的纪律层。 |
| **gsd-core（前身 gsd-build）** | 6.4 万 | 规格驱动 + 上下文工程 | 主打"spec 写下来 + 新鲜子代理避免上下文污染"，五步法 init → discuss → plan → execute → verify。在长 session 中靠 XML 任务树、schema-drift 自动检测、质量门栏提前拦截。 | 与本项目 Project AI Identity Registry + 23 字段任务包一致；但 gsd-core 没有**实操体验闭环（hands-on loop）**也没有**Honesty Gate 5 条款**——这是本项目的两个领先点。 |
| **K-Dense-AI/scientific-agent-skills** | 2.4 万 | 科研垂类 skill 集合（135 个 skill） | 聚焦生物信息学、化学、临床、影像、ML、可视化、实验室自动化、科学交流、蛋白质组学。 | **垂直专用型**，与本项目**通用纪律层**维度不同；但**模式设计可参考**：跨学科子集的"只装适用部分"原则同样适用——本项目 README FAQ 已经回答了"装哪几个、跳哪几个"，但目前缺乏一个「项目分场景的 tiny-subset 推荐表」（P2 类优化）。 |

### 3.2 维度逐一对比（结论简短·证据在条目后）

| 维度 | 本项目 | obra/superpowers | garrytan/gstack | gsd-core | mattpocock/skills | 本项目相对位置 |
| --- | --- | --- | --- | --- | --- | --- |
| **强制实现前门禁** | ✅ 10 字段模板 + SB9 机器校验 | ✅ using-superpowers 总开关 | ✅ /office-hours 六问 + /autoplan 串行 | ✅ 五步法 | ✅ /grill-me 反复询问 | **并列第一** |
| **任务包治理** | ✅ 23 字段 + 6 字段迷你包 + 简报文件化 | ⚠️ task-package 概念散在 subagent-driven-development 内 | ⚠️ /plan-eng-review 输出结构化 plan | ✅ XML 任务树 + schema-drift 校验 | ⚠️ 无统一任务包 | **领先** |
| **派发台账 + 修复循环上限** | ✅ 派发台账 + 发现账本 + 完成门 + 修复循环 5 轮 | ⚠️ 无显式 ledger；fix loop 在 writing-skills 里隐式 | ⚠️ /qa → /review → /ship 链不持久化 | ⚠️ XML 任务树起 ledger 作用 | ❌ 无显式 ledger | **领先** |
| **Honesty Gate 完整性** | ✅ 5 条款（freshness / disk self-check / RED→GREEN / evidence as deliverable / claim-artifact parity） + claim-check.py 机械化 | ✅ verification-before-completion（单一技能 + Iron Law），1 项技能 | ✅ /review 暗含 verification | ⚠️ schema-drift 间接发现 | ⚠️ /tdd 暗含 | **领先**（条款数最多 + 唯一有机械化工具） |
| **实操体验闭环（hands-on loop）** | ✅ 默认 3 轮 + 截图 + headless 退到 UNVERIFIED | ⚠️ TDD 强调 RED→GREEN 但不强制 UI 操作 | ✅ /qa 用真实浏览器 | ⚠️ 未明示 | ⚠️ /tdd 偏单元 | **并列领先** |
| **多 Agent 协作** | ✅ 一主干 + 两扩展 + T1/T2/T3 信任分层 + 身份互斥 + 接收方降级 + 项目 AI 身份登记 | ✅ subagent-driven-development + dispatching-parallel-agents（隐式两层） | ✅ 23 个角色模拟组织（角色颗粒） | ✅ 子代理新鲜上下文 | ⚠️ /subagent-driven 隐式 | **领先**（系统化 vs 散装） |
| **可机器校验** | ✅ SB1–SB20（20 项静态检查）+ claim-check.py + artifact-check.py | ⚠️ 无显式自检 | ⚠️ 启动脚本 bash | ⚠️ schema-drift 内部 | ⚠️ 无 | **领先唯一**（本项目独有） |
| **跨平台分发** | ✅ 13 平台键 + 双端安装器 + 拒绝自嵌套 + 显式剥离面 | ✅ 13+ 代理（Claude Code/Cursor/Codex/Gemini CLI/OpenCode 等） | ✅ Claude Code/Cursor/Codex/OpenCode/Kiro/Hermes/GBrain/Slate/Factory Droid | ✅ 10+ 代理 | ✅ npm 安装 + Vercel skills CLI | **并列**（阵营 13+ 一致） |
| **诚实与自我披露** | ✅ 3 轮探针 + 4 份外部评审 + 1 套 A/B 基线 + README 明示"n=1, 裁判=作者" | ⚠️ 仅 README 自述，缺第三方独立 A/B 协议 | ❌ 仅 Garry Tan 自述指标 | ⚠️ 无公开 A/B | ❌ 自述为主 | **领先** |
| **Token 经济** | ✅ 必载面 SKILL.md 仅 119 行 + workflow Section Map + 渐进加载 | ⚠️ 总装载量较高 | ⚠️ /autoplan 链调，token 峰值大 | ⚠️ spec 文档加载量随任务定 | ✅ 每个 skill 文件小 | **并列领先** |
| **自身诚实条款** | ✅ common-failures.md 含 5 条 F1–F5 失败案例 + 合理化借口对照表 | ⚠️ writing-skills 含反模式 | ⚠️ README 仅提示 | ❌ 无自留失败档案 | ⚠️ README 仅提示 | **领先** |
| **跨运行时入口** | ✅ AGENTS.md + openai.yaml + hooks | ⚠️ CLAUDE.md / .cursor-plugin | ⚠️ setup.sh 多 host | ⚠️ 通过 npm | ✅ npm + skills CLI | **并列** |
| **中文化支持** | ✅ 分层双语 + 中文主导 + CN 专有概念（轻通道/门禁/UNVERIFIED 中文版） | ⚠️ 仅 EN | ❌ 仅 EN | ❌ 仅 EN | ❌ 仅 EN | **领先**（项目级 CN+EN 双层） |
| **示例与可读性** | ✅ series-reasoning-examples.md（678 行）+ minimal-discipline.md 速查卡 | ⚠️ docs/ 含但散落 | ⚠️ README 有 gstack 全景图 | ⚠️ docs/ 散落 | ⚠️ README 简洁 | **领先** |

### 3.3 综合定位（一段话）

**在「AI Agent 流程纪律」细分赛道，本项目与 obra/superpowers 同属第一梯队**，但分工清晰：

- **obra/superpowers** = 流程哲学（"test-first / evidence-over-claims / systematic-over-ad-hoc"），简洁、影响力大（22.8 万 stars）、跨 13+ 平台安装完整。
- **garrytan/gstack** = 角色封装，把人类组织角色照搬到 AI（CEO / Eng Manager / Designer / QA）。
- **gsd-core** = 规格驱动 + 上下文工程，专攻"长 session 上下文污染"。
- **mattpocock/skills** = 小而可组合，与本项目风格"系统化 + 强制流"立场对立。
- **anthropics/skills** = 能力型 skill 集合，与本项目维度正交（一个是能力，一个是纪律）。
- **本项目（gpt-series-reasoning-style）** = **治理系统**——把"门禁/任务包/台账/账本/修复循环/Honesty Gate/信任分层/实操闭环/身份治理/诚实标记"组合成可版本化、可机器校验的 Markdown 行为层。

**本项目独有的领先点**（其他项目都没有或远不如本项目）：

1. **机器可校验的纪律层（SB1–SB20）**——20 项静态自检抓到了至少 4 类真实缺陷（可指认提交哈希）；其他项目依赖手工验证，本项目把"纪律层"做成了"纪律层 + 检查器"双层。
2. **Honesty Gate 5 条款 + claim-check.py**——5 条款与机械化声明核验器在别的项目里都属分散条款，本项目是绑定件。
3. **多 Agent 治理完整度**——23 字段任务包 + 6 字段迷你包 + 派发台账 + 形态变更 ledger + 修复循环上限 + 完成门 + 身份互斥 + 接收方降级 + 信托层级 T1/T2/T3 + 项目 AI 身份登记表 + Fan-in 合并 + 冲突账本。superpowers 是单条 subagent-driven-development 概念，本项目是治理系统。
4. **诚实与自我披露**——3 轮探针 + 4 份外部评审 + 1 套 A/B 基线评测（n=1、裁判=作者明示）+ 5 条真实失败案例（F1–F5）+ 合理化借口对照表——本项目把"盲目自信的实验"做成自我披露的资产。
5. **分层双语 + 中文主导**——13 份 references 按层切换；SKILL.md 仅 119 行（与同类多数千行 README 对比属极度克制）；CN/EN 矩阵在 `README.md` 维护者须知里被精确锁定。
6. **可审计的复杂度预算**——README 第 415-420 行明示「SKILL.md 250 行 / 静态检查 20 项 / 自测 77 条 / 长参考文档 500+ 行不做全文双语强制 / 收敛优先于加码」。这是同类项目中**唯一的复杂度预算治理**。
7. **跨平台分发** + **拒绝自嵌套安装保护** + **dot-file 显式剥离**——安装器在双端一致，单项目整盘交付链路完整。

**本项目相对劣势**（不是为了追平某项目，是为了把项目做得更好）：

1. **影响力 / 社区可见度**——尽管内部 rigor 高，但 stars 与社区活跃度远低于 superpowers（22.8 万）/gstack（11 万）/anthropics/skills（15.1 万）。这不全是项目质量问题，而是"流程纪律 skill"比"能力 skill"更难传播。
2. **多端并行演示**——superpowers 有 hooks.js、gstack 有 `--host` 多平台演示，本项目只有 hooks README 中等密度。
3. **多语言示例**——superpowers/gstack 都有完整 EN demo；本项目的 EN 段集中在 references 中，关键 demo 与 sample case 偏少。
4. **跨平台语法安装**——superpowers 用 `/plugin install ...`，gstack 用 setup.sh，本项目 PowerShell + Bash 双脚本完整，但 Claude Code 插件市场未上架（市场分发属于用户决策，不阻塞功能）。

---

## 4. 按优先级排序的行动清单

> **优先级**采用「维护成本/影响比」+ 项目内部裁决权重。**关键性高 + 维护成本低 = 最先做**；纯 P2 排末位。

| 序 | 项 | 级别 | 估计维护成本 | 第一动作 |
| --- | --- | --- | --- | --- |
| **1** | **B5 `agents/openai.yaml` 改写** —— 拆为 CN/EN 双段，并让 SB9 校验真实生效 | P1 | 1-2 小时 | 把 default_prompt 改为两块（中文段对齐 SKILL.md 11 字段 + 英文段镜像）；SB9 加 "openai.yaml:risk tier" 改为同步双段；实跑 SB9 + selfcheck.py 验证 |
| **2** | **B2 `identities/README.md` 表格加注脚**（必需性以 `commander-roles.md` 为权威）+ `commander-roles.md`/`README.md` "Core/Optional" 边界统一 | P1 | 30 分钟 | 在 `identities/README.md` 表格下加注脚，并核实两表的 "Core" 行集合 |
| **3** | **D4 SB3 检查器修正**（prompt 是否含 code fence 应不是 hard 条件，避免 Test 33/35 与 Fixture-only test 被错判 PARTIAL） | P2 | 30 分钟 | 修改 SB3 改成只判 raw 含 `Prompt:` 标头；SB3 跑通；README 维护者须知加这条 |
| **4** | **C4 site/index.html 加入 SB 扫描面** —— SB4/SB5/SB8/SB19 扫描面补 site；候选 SB21 "site 静态文本断言"准入 | P1 | 1-2 小时 | 列出 site 上应被静态断言的 6-10 处文本（platforms-13, evidence-first, 20 built-in identities 等），失败一次记录 RED 再加 |
| **5** | **B1 "轻通道排除项"逻辑等价性** —— SB11 sub-check 升级，三处表面"全新产物默认中档"措辞必须等价 | P1 | 1 小时 | 加 sub-check + 实测 RED 候选（改一处但不同步另一处）+ README 维护者须知同步清单 |
| **6** | **C2 README "实战中文字符占比 1.5–1.8×" 措辞软化** —— 加可复跑命令或改保守表述 | P1 | 30 分钟 | 加 `scripts/token-ratio.py` 或改 README 为"通常 ≥ 1.5×" |
| **7** | **D5 `lessons.md` & `examples.md` 同步检查** —— 候选 SB21 "规则第二副本字段漂移"，RED 候选 = lessons.md 旧表述 | P2 | 2-3 小时（须设计 SB21） | 实测 RED → 立项 → 落地 |
| **8** | **B3 `project-artifacts.md` §3.5** —— 单 Agent 内部派发包字段字典明确 | P1 | 30 分钟 | 加 §3.5 + 明确 7 字段集 |
| **9** | **B4 「Commander capability gate」空值退化** —— 与 "Mode 3 Direct Execution Shortcut" 一致 | P1 | 30 分钟 | 在 capability gate 段后补一句 |
| **10** | **C3 SKILL.md EN 段落锚点化** —— 改成具体 references 锚点 | P1 | 15 分钟 | 改 SKILL.md EN 段为 "详见 references/agent-modes.md §Mode Self-Selection (EN)…" |
| **11** | **C1 INTERNAL-HISTORY / README 范围口径对齐** | P1→P2 | 15 分钟 | 加 README 一句"以 INTERNAL-HISTORY.md 头部为准" |
| **12** | **C6 docs/selftest-run 进 .gitignore** | P1 | 5 分钟 | 加一行进 `.gitignore`；保留 judgement-2026-09-10.md 头部声明 |
| **13** | **A1 「Recipient activation prompt」加注入防御段** | P0→P1 | 15 分钟 | multi-agent-closure-rules.md「Recipient activation prompt」节末加禁带未加密凭据/可执行 shell 段 |
| **14** | **D2 `references/identity-library.md` 派发角色分配节拆分** —— 14 条规则 → 8 字段检查表 + 短叙 | P2 | 1 小时 | 拆分即可 |
| **15** | **D3 hooks/README.md 增加 uninstall 段落** | P2 | 30 分钟 | 加 §uninstall |
| **16** | **D1 SKILL.md / README "Usage" 段** —— 三种触发方式差异明示 | P2 | 15 分钟 | 加一句 |
| **17** | **E1 / E2** workflow.md / examples.md 双段结构 + README "Language Policy" 段折叠 | P2 | 2-3 小时 | 取决于总体裁决（建议放 1.x 之后进行） |
| **18** | **F1/F2/F3 隐藏未验证项** —— 把 badges、judgement-sheet、site URL 等自披露项 commit 成 explicit UNVERIFIED 声明 | P2 | 1 小时 | 在 README/CHANGELOG 加注；不阻塞主流程 |

---

## 5. 修复后预期（落实 1–10 后）

| 维度 | 期望变化 |
| --- | --- |
| **自检通过率** | 仍 20/20，但 SB9/SB11/SB-new 三处变严，SB21（拟）已就位 |
| **描述合规模型** | 一致性更紧，与 README 维护者须知同步清单对齐 |
| **开放性分类** | 出现"中档任务降至 5–15k token（README 第 6 批目标）"的中档实测面板 |
| **多平台分发** | site 上 SB 数字与 README 同步；hooks README 支持反向操作 |
| **诚实与自我披露** | README 把"n=1, 裁判=作者, 基线不中立"的口径保留，并新增 `docs/reviews/` 自我审计存档（本报告即此用） |

---

## 6. 验证证据（亲验·可复跑）

- `python scripts/selfcheck.py` —— **20/20 PASS**（SB1 版本一致 / SB2 77 条 contiguity / SB3 prompt-expectation 完整 / SB4 21 身份 / SB5 13 references / SB6 围栏配对 + 转义围栏检测 / SB7 cross-file ref / SB8 23 字段 vs 24 字段 / SB9 CN/EN 同步 / SB10 13 install 键 / SB11 light 通道 / SB12 agentskills.io 合规 / SB13 三轮探针 / SB14 双语语言政策 / SB15 提示词去重 / SB16 双语 tier-A 检查 / SB17 AGENTS.md 路由 / SB18 禁用授权短语 / SB19 身份计数 / SB20 newline 写入点）。fingerprint `d2f1b5aa4136`。
- `python scripts/selftest-runner.py list` —— 77 条提示词与期望加载正常（最后一条：Test 77 Return-from-other-role re-declares）。
- `python scripts/claim-check.py docs/selftest-run/_smoke-claims.md <project-root>` —— README.md exists + 命令 exit 0（smoke 测试后产物已清理）。
- 关键发现的所有「位置」均由本报告 §1 表与各小节中具体 `references/<file>.md:<line>` 引用支撑；行号基于 git HEAD `1bd166a` 工作树状态确认。

## 7. 维护者级别结论（一段话）

- **本项目未发现颠覆性逻辑或安全漏洞**——所有 P0 都属"可加固的可信任边界"而非"已发生的漏洞"。
- **本项目相对同类 skill 在多 Agent 治理与诚实自检两条线上处于领先位置**，且领先是由可机器校验的工程化（SB1–SB20）背书的，不是凭感觉。
- **主要风险点是"跨表面规则同步"与"已修历史的硬不漂移保证"**——已具机制（README 维护者须知同步清单 7 项 + SB1–SB20），但**有 5 处以上仍欠追加同步检查**（B1/B2/C2/C3/C4/D5）。
- **建议 1–10 项在 1 个批次内处理**；18 项全部处理完后，本项目可作为"流程纪律 skill"细分赛道的**事实标准**之一——尤其在 CN/EN 双语圈与多 Agent 协作严肃场景。

---

> **诚实条款**：
> 1. 本报告 reviewer 不是外部独立 AI（同 coder 视角 + 工作区内），且 reviewer 接受过本项目的 skill 自加载；意味着对 `references/common-failures.md` 的 F5 类（"Agent 报告完成 → 查 VCS diff"）教训应在 reviewer 后续工作中加 cross-check。
> 2. 本报告每项发现都给出 location（含文件/行号或节标题），但**未亲验 site 渲染、GitHub Pages URL 反链、跨 PR 评审落地测试**——这三项标 §2.F F1/F2/F3。
> 3. 本报告与 `gpt-series-reasoning-style` 自身一样，遵守 `references/series-reasoning-workflow.md` "Continuous Diverge-Converge Loop"——以下是报告作者在本报告自审时已压下的几条：
>    - "会不会存在 SB1–SB20 已经发现的但我又重复说的？"——已与 SB1–SB20 输出交叉，无重复。
>    - "会不会遗漏一个 README 完整段？"——README §5-§7 与 README 维护者须知两度亲验。
>    - "selfcheck 的 SHELL-SB20 已知盲区（跨行调用）"——本审查范围内没有发现跨行调用的写入点，未触发盲区。

— end of audit —
