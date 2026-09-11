# External Reviews 5–7 — Verification Verdict / 三份外部全面复查的核验结论

- Date: 2026-09-10
- Provenance: three independent full-project audits of this skill, produced by
  external AIs and relayed by the maintainer (方法二). Model identities were not
  disclosed by the relays. One of them wrote its own report file
  (`2026-09-10-deep-audit.md`, same directory); the other two exist as relayed
  text only — their claims are archived here as verified by us, not verbatim.
- Verification method: every load-bearing claim was re-checked on disk or
  against the GitHub API before being believed. Claims we could not check are
  listed as UNVERIFIED, not silently accepted.

## P0 — all three CONFIRMED, all three fixed (batch 22)

| # | Claim | Verdict | Evidence | Fix |
| --- | --- | --- | --- | --- |
| P0-1 | CI has never been green; the skilllint step fails and the three validation steps after it are always skipped | **CONFIRMED** | GitHub API: 7/7 runs `failure`; step-level for run 34459210405 → step 6 `Official skilllint` = failure, steps 7 (openai.yaml parses) / 8 (Probe scenarios parse) / 9 (Self-test sheet parses) = **skipped**. Two root causes verified by inspection: the workflow has no `setup-uv` step, and `check gpt-series-reasoning-style` is a path that does not exist relative to the CI checkout (repo root = working dir); locally it only works because we run it from the parent directory | `.github/workflows/selfcheck.yml`: added `astral-sh/setup-uv@20cfd1bf…` (SHA-pinned v10.0.1) and changed the lint step to `cd .. && uvx skilllint@1.19.2 check gpt-series-reasoning-style`. Locally reproduced both forms: parent-dir form passes clean; `check .` reproduces the FM010 false positive named in the pin comment |
| P0-2 | Resume Check is 7 items in the authority file but only 3–4 on the must-load and acceptance surfaces | **CONFIRMED** | `series-reasoning-workflow.md` Resume Check = 7 items; `SKILL.md` workflow item 1 = 4; `README.md` EN line 100 and CN line 106 = 3; `self-test.md` Test 55 = 4. The two missing items (re-anchor the original instruction; project-root hard check) are exactly the fixes for the two most expensive defects the A/B rounds caught | `SKILL.md` now enumerates ①–⑦; both README lines carry all 7; Test 55 gained two expectations (re-anchor; project-root hard check) |
| P0-3 | The load-proof template in examples.md contradicts itself within four lines | **CONFIRMED** | `series-reasoning-examples.md` ~L470: announces 「一条主干 + 两个按需扩展」 then enumerates `1. 单 Agent 模式 / 2. 子 Agent 模式 / 3. 指挥官多 Agent 模式` and refers to 模式一/二/三 — the retired three-mode vocabulary, inside a template hosts are told to reproduce | Template rewritten as 主干 / 扩展 A / 扩展 B with the current vocabulary |

## P1 — CONFIRMED and fixed in the same batch

| Claim | Verdict | Evidence | Fix |
| --- | --- | --- | --- |
| README Maintainer Notes still says 22 identity files; SB19 cannot catch that form | **CONFIRMED — and it is a blind spot in our own SB19** | `README.md:465`: 「内置身份 **22** 个文件（21 类角色）」 while SB4 counts 21 files. Our SB19 regex only matches 个/类 followed by 身份/角色/契约, so `22 个**文件**` (bold breaks the phrase) and the EN number-after-noun form (`identity files **22**`) both slip through | README 22→21 (both languages); SB19 gained file-count forms for CN and EN with the count allowed on either side of the noun, gated on the line mentioning identity + files. RED proof executed against the pre-fix README: both drift forms caught |

## Verified FALSE / stale

| Claim | Verdict | Evidence |
| --- | --- | --- |
| 「docs/selftest-run 应入 .gitignore」(deep-audit C6) | **FALSE** — already ignored since batch 12 | `.gitignore` line 8: `docs/selftest-run/` |

## Verified TRUE but not yet fixed (queued, maintainer's call)

- `claim-check.py` runs untrusted commands with `shell=True`; the destructive-command
  blacklist does not cover interpreter-indirect execution (`python -c "import os;…"`,
  `python malicious.py`), so a hostile claims file still reaches local RCE. Confirmed by
  reading `DANGEROUS_RES` (19 patterns, no python form). The tool documents that it is not
  a sandbox and has `--allow-dangerous`; the gap is real nevertheless. Candidate fix:
  default to `shell=False` with an argv parser, or require `--allow-dangerous` for any
  command that is not a small allowlist.
- `README.md:395` states 「实测中文字符占比 1.5–1.8×英文词」 — the wording claims a
  measurement, but no archived measurement artifact was found. Either archive the
  measurement or soften the wording to an estimate.
- Test 37's self-contradiction (previously archived as C2, "待裁决") remains open.
- deputy-commander placement (README Core vs Optional vs commander-roles) needs a
  three-way re-read before touching.

## NOT YET VERIFIED (listed for the next pass — no verdict, no fix)

The deep-audit report's remaining items (B1–B5, C1–C5, D1–D5, E1–E2, F1–F3) and the
second report's P2 list (23-field token-vs-field-set checking, SemVer communication,
probe fail_patterns being dead data, installer `--dry-run`) have **not** been verified
by us yet. They are neither accepted nor rejected; the next verification pass should
take them one by one, and anything confirmed lands with the same
real-defect-evidence bar the SB checks require.

## VERIFIED (2026-09-11,逐条对盘核验 · 第三十二批收尾后执行)

deep-audit B1–B5/C1–C5/D1–D5/E1–E2/F1–F3 与第二报告 P2 四项全部核验完毕。**核验纪律：逐条对盘,证伪也记录。**

### 已过时 / 已被后续批次顺带解决（7 项）

| 项 | 核验结论 |
| --- | --- |
| B5 | **大部分过时**:`default_prompt` 已从 5.4KB 瘦身至约 2.3KB(整文件 2791B),截断风险大减;EN-only 与 CN/EN 双表达的同步顾虑仍在(低危)。 |
| C1 | **已一致**:README:535/:544 与 INTERNAL-HISTORY.md 头部现均为 `0.1.x–3.3.x`。 |
| C2 | **证伪(现状)**:「1.5–1.8×」句已不存在于当前 README(唯一残留「1.5」是 token 区间,无关)。 |
| C4 | **大部分已解决**:SB19 扫描面含 `site/index.html`;SB21 把 site 登记进 selfcheck 表/冻结计数/循环比对 3 处。徽章口号类文本仍无专守(低危)。 |
| D1 | **前提消失**:原引用的「$ 前缀只是 Codex 风格触发」表述已不在 SKILL.md/README(第 25 批重写),无活体问题。 |
| D3 | **已解决**:`hooks/README.md:77` 已有「卸载 / Remove」节。 |
| P2-3 (fail_patterns 死数据) | **已解决**:第十六批 `verify` 子命令已消费 fail_patterns(probe-runner.py:105 硬失败、exit 1)。 |

### 证伪——建议所依据的前提在当前树不成立（1 项）

| 项 | 核验结论 |
| --- | --- |
| D4 | **证伪**:SB3 的 `has_prompt` 判据(`"prompt" in raw and "\x60\x60\x60" in raw`)未变,但当前 77 条全部带 fence、selfcheck 21/21 全绿——「Test 33/35 被卡」无活体失败。放宽 fence 要求反而降低结构判据强度,**不建议采纳**。 |

### 成立——建议仍有效、尚未处置（12 项,按优先级）

| 项 | 现状核验 | 处置建议 |
| --- | --- | --- |
| B1 | 三面排除项仍有软漂移:SKILL.md:76「产品形态」vs workflow:242「形态」vs agent-modes:23/50「形态/type/location/form」;SB11 只查关键词存在性 | 维护时同步;若再抓到真实 RED 可按准入规则立项 SB |
| B2 | identities/README.md 速查表仍无必需性标定、无权威脚注 | 加脚注「必需性以 commander-roles.md 为权威」 |
| B3 | project-artifacts.md 无「任务派发包」节 | 补 §3.5(7 字段浓缩 + 单一权威指向) |
| B4 | capability gate(:139)无「接收方路径空值」退化行为 | 补一句 Mode 3 直连退化 |
| C3 | SKILL.md:9 EN 指针仍无章节锚点 | 指到具体 (EN) 节名 |
| C5 | 26/30 vs 34/35 矛盾已在第 18/21 批修;建议的 prompt/expected 字面子检查未落地 | 无活体 RED,暂不满足 SB 准入;留作候选 |
| D2 | identity-library.md:77 派发角色分配段无 8 字段检查表 | 可读性增量,随下次触及该文件时一并做 |
| D5 | lessons/examples 关键词同步检查未落地(examples 有 SB14 层覆盖,lessons 无);**其引用的 RED 例句已不在 lessons.md——立项须重新举证** | 重新找 RED 或放弃 |
| F1 | evidence-first 徽章(自定义色)仍无「非官方 shields 配色」说明 | README 加半句 |
| F3 | README:437 仍称 site「GitHub Pages 可直接指向」,但仓内无 Pages 部署配置/URL,200 无从验证 | 部署时补可复跑 URL 检查,或改措辞 |
| P2-1 (23 字段 token-字段集核对) | 三层口径已在第十六批④明文收敛(11 内部/6 子/23 跨模型各归权威);机器核对未落地 | 同 C5:无 RED 不准入 |
| P2-4 (installer --dry-run) | install.ps1/install.sh 均无 dry-run | 建议类,随下次改安装器时加 |

### 纯建议类、无缺陷（3 项）

- **E1**(三份大文档切双段结构)、**E2**(README 语言矩阵折叠)、**F2**(judgement-sheet 行文体例)——均为可读性/体例增量,无正确性问题,留档待裁。

### 核验过程新抓的活体漂移（已当场修复）

- **README:540「截至目前 24 批」**——实际已到第 32 批(第 25 批写入后未随批次递增)。这正是 SB21 守的那类「手抄派生数字」,但不在其四族内。修法与 SB21 同理:**删手抄件、改为指向权威源(CHANGELOG Unreleased 最新条目)**,杜绝复发,而非把 24 改成 32 等下次再漂。
