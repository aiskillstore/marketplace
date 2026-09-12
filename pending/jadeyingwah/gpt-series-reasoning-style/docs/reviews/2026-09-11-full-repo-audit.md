# 全仓系统审查报告 / Full-Repository Audit Report

- Date / 日期: 2026-09-11
- Scope / 范围: `gpt-series-reasoning-style` 全仓 86 个文件（8 个 Python 脚本 + 2 个安装器 + 1 个 hook + CI 工作流 + 13 份 references + 21 份身份 + README/site/AGENTS/openai.yaml/LICENSE 等）
- Method / 方法: **迭代式**——每轮审查 + 修复后从头再审，直到**连续一整轮零发现**为止（本轮次共 4 轮，第 4 轮零发现终止）。每条发现均**运行时实证**（实测输出 / 变异杀伤）后才判为缺陷；疑似但未获证据者一律标记"撤回"而不计入。
- Result / 结果: 修复 **P1 ×1 / P2 ×6 / P3 ×3**（共 10 项），新增守卫 4 处；静态自检 **22/22**，CI 逐步本地实跑 14/14 通过。

---

## 一、缺陷清单（按严重程度）

### P1 — 阻断级

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 1 | `scripts/claim-check.py:118`（`INTERPRETER_NAMES`） | **解释器默认拒层有族缺口**：`pypy/pypy2/pypy3/ipython/jython/nodejs/osascript/dash/ash/busybox/csh/tcsh/cscript/wscript/mshta` 的 `interpreter_block_reason()` 实测**全部返回 None**，即这些解释器的 `-c/-e/脚本` 载荷会经 `shell=True` 执行。与第 32/35 批（`python3.13`、引号路径）和第 39 批（wrapper 前缀）**同族**，均为"边界形态当时未当变异体"。 | 族扩至上述变体；**白名单同步含 `pypy/jython/ipython` 形态**（`pypy -m pytest` 仍可用，堵洞不误伤）；`_argv0` 增 `pypy3.9`/`ipython3` 归一化；docstring 同步。回归 **17 拦 / 10 放全符合设计** + 端到端实跑（2 拦 2 跑）。 |

### P2 — 主要功能

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 2 | `scripts/selfcheck.py`（SB21 `fam`） | **CI 步数族是空转守卫**：正则 `全绿（(\d+)/(\d+) 步` 在 README 中**零命中**（实际措辞「当前 N/N 步」），"正则找不到即不比较"使该族等于**从未生效**——CI 步数 12→13→**14** 全程绿灯无人察觉（本批加第 14 步时它仍报 22/22 才被撞见）。 | 正则改为锚定实际措辞；并**新增守卫生效性自检**：SB21/SB22 内任一族零命中即 FAIL 并点名（空转守卫比没有守卫更危险，它给出"已检查"的假信号）。RED/GREEN 双证。 |
| 3 | `.github/workflows/selfcheck.yml` | **claim-check 两层安全拦截零行为回归**：CI 只跑 `--help`（仅证明 CLI 可导入）。该层历史被绕过三次，每次都是"代码还在、CLI 能跑、CI 全绿"但拦截没触发。 | 新增入仓夹具 `scripts/examples/claim-check-guard.md` + CI **第 14 步**，四条断言：普通命令仍放行实跑（防"改成全拦"式假绿）、输出含 `interpreter-indirect`、含 `dangerous pattern`、退出码 1。 |
| 4 | `scripts/mutation-kill.py:165` | **退出码与文档不符**：缺字段/坏 JSON manifest 抛 `KeyError` 轨迹并 exit **1**，而 docstring 声明「2 = manifest/环境不合法」；CI 只看 0/1 会把用法错误误读成"有未测成项"。 | 五类结构化失败（文件缺失 / JSON 坏 / 顶层非对象 / 缺 `artifact` 或 `mutants` 非数组 / `budget_ms` 非整数）统一 exit 2；入仓示例回归仍通过（sign 0% / magnitude 100%）。 |
| 5 | `scripts/artifact-check.py:15` | docstring 称「**10** gate-field labels」，而 `GATE_FIELDS` 实为 **11**。 | 改为 11 并注明权威源。 |
| 6 | `README.md:453` | 称「**24 类**破坏性命令黑名单」，`DANGEROUS_RES` 实为 **25**。 | 改 25；并由新增的 SB21 真值族守卫。 |
| 7 | `README.md:289/361/382` + `docs/minimal-discipline.md:3` | **Lite token 三面漂移且 README 自相矛盾**：289 行说整卡 518、382 行说整文件 481；cl100k 称 659 实测 697；三条本体称 154 实测 147。 | 统一重测同步（147 / 518 / 697，标注 2026-09-11 重测）。 |

### P3 — 次要

| # | 位置 | 问题 | 修复 |
|---|---|---|---|
| 8 | `docs/field-tests/selftest-run-2026-09-10/report.md:4` | **断链**：`../../references/self-test.md`（该目录下需上溯**三**级）。 | 改 `../../../`。 |
| 9 | `README.md:454` | 「`docs/gate/*.md` **十字段**标签」应为**十一**字段（与 #5 同族）。 | 改为十一字段；由 SB22 中文数字字面拦截守卫。 |
| 10 | `hooks/README.md:44` | Windows 等效命令的输出文本与 `hooks/session-reminder.sh` **不一致**（只有中文半句、缺英文），同一提醒两平台分叉。 | 对齐为逐字一致，并注明以 `session-reminder.sh` 为唯一权威。 |

**附带修正**：`README.md:288` references 单份上限 13,424 → 实测 13,420；`README.md:458` CI 步数 13/13 → 14/14 并补新步骤；`generate-banner.py` docstring 关于 SVG 同步的**不可维持声明**（见下"残余风险"）。

---

## 二、新增/加固的守卫（刻意不增加检查项数，仍为 22 项）

| 守卫 | 作用 | 鉴别力证据 |
|---|---|---|
| SB21 增「黑名单类数」真值族 | README 的"N 类黑名单"必须等于 `DANGEROUS_RES` 解析值（解析非导入） | 变异 25→24 → 当场 FAIL 并点名 |
| SB21 增「守卫生效性自检」 | 任一族正则零命中即 FAIL（防空转） | 某族正则改坏 → FAIL 报 `guard is a no-op` |
| SB22 增中文数字拦截 | 门禁字段数为 11 时禁止"十字段"字面 | 变异 十一→十 → 当场 FAIL |
| SB20 写模式匹配收紧 | 只扫 `open(` **之后**的片段（原全行搜索会被同行 `d["a"]`、`"x" in s` 误触发） | 全仓 8 个 .py 扫描仍绿 |

---

## 三、核验为净（经查一致、确认无缺陷的项）

- **字段清单实测**：23 字段完整任务包 **恰 23 项**（逐条点名）；六字段迷你包中英两版 **各恰 6 项**；五字段降级包 5 项；内部派发包 **恰 11 项**；门禁 11 字段在 SKILL/workflow CN/EN 三面齐全。
- **身份层**：21 份身份文件小节与 `_template.md` **完全一致**（`deputy-commander` 多出的「指挥权接管」是第 11 批刻意新增）；目录表 22 行 = 21 身份 + `_template`。
- **文档面**：README TOC **25 条锚点零悬空**（第 11 批遗留的 L4 悬案了结）；硬规则首条引文 `宣布阶段序列不是确认。` 在 SKILL/AGENTS/workflow/self-test/README **五面逐字在位**；`docs/field-tests/` **10 份报告全部入索引**；全仓断链仅 #8 一处；缩进围栏 0 处；`platform-installation.md` 安装表 14 行与 README「13 参数 / 14 行」一致。
- **自测面**：77 条用例 0 畸形头、0 空提示词、0 无期望项、0 重复标题、期望项均 ≥2 条。
- **运行时边界 22 项全通过**：`selfcheck --out` 越界拒绝 / 仓库内写入正常；`claim-check` 空清单 exit 2、`# expect exit N` 生效、非法 hash 报 malformed；`artifact-check` 五种情形（含**逐轮**抓出第 2 轮缺字段）判定全对；`selftest-runner` schema→archive 往返；`probe-runner` archive→report→verify 双向；`install.sh` `bash -n`；全脚本 `py_compile`。
- **术语面**：「模式三」是指挥官协议正式名，非废弃的"模式一/二/三"模式命名；`project-artifacts.md` 只引用不罗列门禁字段属设计使然。

**审查中被自己推翻的误报（如实记录）**：`project-artifacts.md` 门禁字段只命中 1/11（实为"逐字拷贝"引用，设计使然）、`platform-installation.md` 缺 `antigravity`（实为首字母大写的 `Antigravity`）、身份目录表 22 行（含 `_template` 行）——三项均已撤回，未改。

---

## 四、残余风险（诚实记档，不假装已覆盖）

1. **Lite token 与 references 单份上限无法自守**：需 tiktoken 测量，而 `selfcheck.py` 刻意只用标准库；这两类数字只能人工重测（已在文档标注测量日期）。
2. **`social-preview.svg` 无法与生成器保持可验证同步**：该 SVG 把全部文字转为路径轮廓（14 个 `<path>`、零 `<text>` 节点），任何机器比对都做不到；`generate-banner.py` docstring 已如实改为"本文件是文案权威源，SVG 是需人工重新导出的冻结产物"。
3. **claim-check 两层拦截不是沙箱**：白名单放行的 `-m pytest/unittest` 仍会执行项目代码（conftest 可藏载荷）；家族外的 exec 型工具（`go run`/`cargo run`/`make`/`uv`/`npm`）不覆盖。真实信任边界仍是可信声明源 + 人工逐条复核。
4. **CI 第 14 步依赖宿主存在 `git`**（用于断言"普通命令仍放行"）：GitHub ubuntu-latest 恒有；本地 Windows 亦已实测通过。

---

## 五、过程纪律事故

- 第 3 轮边界测试向**被跟踪文件** `probes/last-run.md` 追加了一条夹具记录，已当场 `git checkout` 还原。**教训：测试床一律用临时目录，不得污染工作树**——这正是本仓库自己反复强调的纪律，复发即记档。

---

## 六、提交

- `d45d233` 第四十四批（第一轮）：P1 解释器族缺口 + P2×4 + P3×2 + 3 处守卫扩展
- `9083c79` 第四十五批（第二轮）：空转守卫修复与自检 + CI 第 14 步 + hook 文案对齐
- `9510594` 第四十六批（第三轮）：22 项边界测试通过 + SVG 同步声明更正

**待 push 累计 25 个提交**（`74cbb76`…`9510594`），按铁律 1 由总指挥在 cmd 手动推送。
