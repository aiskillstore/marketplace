# Security Model / 安全模型

> 本文档描述**当前形态（v1.4.x 极简线）**的安全模型。v1.2.x 时代围绕 `scripts/claim-check.py`
> 的完整威胁模型已随该工具下线而移除，原文见 git 历史（batch 32, 2026-09-11 前后）。
> The document below covers the **current form (v1.4.x minimal line)**. The full threat model for the
> v1.2.x-era `claim-check.py` tool was removed along with the tool; see git history.

## Runtime surface / 运行时面

The skill's runtime surface is **text only**:

- Loading reads exactly two files: `SKILL.md` and `VERSION`. Both are plain Markdown/text.
- `references/multi-agent.md` and `templates/*.md` are on-demand **text** instructions — no code executes.
- The skill contains **no command-execution tool, no network calls, no telemetry, no auto-triggered scripts**.
  加载与执行全程不运行任何代码、不发起网络请求、不上报任何数据。

## scripts/ — what runs and what it touches / 脚本目录

The only script in this repository is `scripts/selfcheck.py`, a **repository consistency self-check**
— it is a development utility, **not** part of the skill's load path:

- Reads only files inside this repository (SKILL.md, VERSION, references/, templates/).
- No network access, no `shell=True`, no arbitrary-command execution, no writes outside stdout.
- 仓库自检脚本：只读仓库内文件做一致性核对，无网络、无 shell 拼接、无任意命令执行、不写文件。

## Historical note / 历史说明

`scripts/claim-check.py` (v1.2.x) mechanically re-ran commands from an agent-authored claims file and
therefore required `shell=True` arbitrary-command execution, with a three-layer mitigation pipeline
(destructive-pattern blacklist / interpreter default-deny / wrapper unwrap). That tool was **not carried
forward** into the 1.4.x minimal line. Should a claim-verification tool return, this file must regain a
full threat-model section **before** the tool ships — not after.

历史工具 `claim-check.py`（v1.2.x）因需 `shell=True` 执行任意命令而带完整三层防御；该工具未随 1.4.x
极简线保留。未来若恢复此类工具，必须**先**在本文档重建完整威胁模型，再发布工具本身。

## Reporting / 报告

Open a GitHub issue in this repository. MIT licensed — no security SLA, best-effort maintenance.
漏洞请开 GitHub issue。本项目为 MIT 许可的尽力维护项目，无安全响应 SLA。
