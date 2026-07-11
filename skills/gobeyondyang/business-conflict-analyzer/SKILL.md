---
name: business-conflict-analyzer
fetch:
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/scripts/diff_analyzer.py
    path: scripts/diff_analyzer.py
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/scripts/impact_mapper.py
    path: scripts/impact_mapper.py
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/scripts/report_generator.py
    path: scripts/report_generator.py
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/scripts/lang.py
    path: scripts/lang.py
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/scripts/commit_guard.py
    path: scripts/commit_guard.py
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/scripts/install_hook.sh
    path: scripts/install_hook.sh
  - url: https://github.com/GoBeyondYang/skills/raw/main/skills/business-conflict-analyzer/references/common_patterns.md
    path: references/common_patterns.md
description: "Analyze API, schema, and contract changes; map affected consumers, assess business risk, generate an impact report, and support commit guarding with compatibility fixes."
---

> ⚠️ **IMPORTANT — Companion files (scripts/, references/) download automatically via `fetch`**
>
> Do NOT manually download, clone, or fetch any companion files from the GitHub repository.
> The `fetch` frontmatter above handles this automatically when the skill is loaded.
> Manually downloading files will override the automatic mechanism and may cause duplicates.
>
> **重要 — `fetch` 前奏会自动下载配套文件（scripts/、references/）**
>
> **不要**手动从 GitHub 下载、克隆或抓取任何配套文件。
> 上述 `fetch` 前奏会在 skill 加载时自动处理。手动下载会干扰自动机制，可能产生重复文件。

# Business Conflict Analyzer / 业务冲突分析 Skill

## Overview / 概述

This Skill is an **inherent instinct** of the AI coding assistant. While generating or modifying code, the AI spontaneously detects changes that affect external contracts (API upgrades, field changes, protocol changes), automatically triggers the analysis pipeline, and outputs a plain-business-language *Impact Analysis Report* for human decision-making.

本 Skill 是 AI 的"内置本能"。AI 在执行代码生成或修改任务时，自发感知到涉及外部依赖变更（API 升级、字段变更、协议变化），自动触发分析流程，输出纯业务语言的《影响分析报告》并推送人类决策。

**Core idea / 核心理念**: No human needs to manually navigate to any system to "start analysis" — the AI notices the change while writing code, analyzes it, pushes the report, and waits for a decision.

---

## Trigger Conditions / 触发条件

The AI should **auto-trigger** this Skill when performing any of the following operations:
AI 在执行以下任一操作时，应**自动触发**本 Skill：

### Auto-Trigger / 自动触发（无需人类指令）

| Scenario / 场景 | Identification / 识别特征 |
|----------------|-------------------------|
| API request/response field change | DTO/VO class add/delete/modify fields, `@RequestBody`/`@ResponseBody` changes |
| Interface method signature change | Interface method parameters, return type, or exception declarations change |
| RPC/Feign interface change | `@FeignClient` definition changes, or downstream service contract changes |
| Database DDL change | `ALTER TABLE`, `DROP COLUMN`, `CREATE TABLE`, etc. |
| Message/event schema change | MQ message body field add/delete/modify |
| Config property change | `application.yml`, config center item add/delete/rename |

### On-Demand / 按需触发（建议分析）

| Scenario / 场景 | Description / 说明 |
|----------------|-------------------|
| Enum value changes | Add/deprecate enum constants |
| Core business logic refactor | Payment, refund, inventory logic changes |
| Annotation/validation rule changes | `@NotNull` → `@Nullable`, `@Validated` scope changes |

---

## Analysis Pipeline / 分析流程

### Step 1: Extract Diff / 提取差异

- Run `scripts/diff_analyzer.py`
- Input: `git diff` (or IDE changes)
- Output: Structured change manifest with file paths, change types (ADD/MODIFY/DELETE), symbols (field/method names), and granularity

### Step 2: Map Impact / 映射影响

- Run `scripts/impact_mapper.py`
- Input: Step 1 structured manifest
- Core logic: Traverse each change, search project references, consult `references/common_patterns.md`
- Output: Impact matrix (consumer impacts, data compatibility, frontend/test impacts)

### Step 3: Generate Report / 生成报告

- Run `scripts/report_generator.py`
- Input: Step 2 impact matrix
- Core logic: Translate technical language → business language
- Output: Plain-business-language *Business Impact Analysis Report*

### Step 4: Push for Decision / 推送决策

- Report pushed directly to human (code review comment / IM / inline display)
- Wait for human feedback:
  - **[1] Accept / 采纳** → AI proceeds with changes (see [Post-Guard Follow-up Protocol](#post-guard-follow-up-protocol--拦截后闭环追问) and [Auto-Fix](#auto-fix-impacted-consumers--引用方批量修复) below)
  - **[2] Reject / 拒绝** → AI rolls back, records reason
  - **[3] Revise / 修改建议** → AI adjusts approach based on feedback and re-analyzes

> **i18n**: All three options support auto-detection via `scripts/lang.py` `Translator._detect_lang()` which checks system locale or `LANG` env var. Present options in the detected language ONLY — never show both languages. No extra user action needed.

---

## Output Specification / 输出规范

### Report Structure / 报告结构

```markdown
## ⚠️ Business Impact Analysis Report / 业务影响分析报告

### Change Summary / 变更摘要
[One sentence: what changed]

### Change Details / 变更明细
[Per-file: tech change → business language translation]

### Impact Scope / 影响范围
[Affected features / services / data compatibility]

### Risk Assessment & Recommendation / 风险等级与建议
Risk level: High / Medium / Low

### Decision / 决策
_Options auto-translated — shown in detected language only (system locale or LANG env var). Example below is English; the actual output matches the user's system language._

> Reply with number:

- **[1] Accept** — proceed, auto-fix all impacted consumers
- **[2] Reject** — rollback change
- **[3] Revise** — adjust approach
```

### Risk Levels / 风险等级

| Level / 等级 | Meaning / 含义 | Action / 处理方式 |
|-------------|---------------|-----------------|
| **High** 🔴 **高** | Downstream compile failure / runtime exception / data loss | Must be confirmed by business owner, version upgrade required |
| **Medium** 🟡 **中** | Behavior change with backward compatibility | Notify stakeholders, include in iteration plan |
| **Low** 🟢 **低** | New capability / internal refactor | Auto-handle, documentation notice suffices |

### Translation Rules / 翻译规则

| Technical / 技术语言 | → | Business / 业务语言 |
|---------------------|:-:|--------------------|
| "Delete UserDTO.mobile field" | → | "User API will no longer return the mobile phone number field" |
| "ALTER TABLE user DROP COLUMN mobile" | → | "User table will drop the mobile column; existing data must be migrated" |
| "Signature getUser(Long) → getUser(String)" | → | "User lookup method changed — input from numeric ID to string UID" |
| "Enum new constant REFUNDING" | → | "Order lifecycle gains a new 'Refunding' state" |

---

## Resources / 配套资源

- `scripts/diff_analyzer.py` — Diff extraction / 差异提取
- `scripts/impact_mapper.py` — Impact mapping / 影响映射
- `scripts/report_generator.py` — Report generation / 报告生成
- `references/common_patterns.md` — Conflict pattern library / 常见冲突模式库

---

## Guard Installation / Guard 安装

When the user says "帮我安装 commit guard" or similar, the AI should:

1. Locate `install_hook.sh` at `.claude/skills/business-conflict-analyzer/scripts/install_hook.sh` (relative to project root)
2. Run it directly:

```bash
bash .claude/skills/business-conflict-analyzer/scripts/install_hook.sh
```

This registers a `PreToolUse` hook (via `.claude/settings.local.json`) that intercepts `git commit` and runs conflict analysis.

When the user says "卸载 commit guard" or "uninstall the guard", delete the `PreToolUse` entry from `.claude/settings.local.json`:

```bash
# Remove the PreToolUse hook entry from settings.local.json
```

> **Note**: `commit_guard.py` must exist at `.claude/skills/business-conflict-analyzer/scripts/commit_guard.py` for the hook to work. The `fetch` frontmatter in this SKILL.md ensures it's auto-downloaded when the skill loads.

---

## Prerequisites / 前置依赖

| Dependency / 依赖 | Purpose / 用途 | Check / 检查方式 |
|------------------|---------------|------------------|
| **Python 3.8+** | All analysis scripts | `python --version` |
| **Git** | Diff data retrieval | `git status` |
| **No third-party libs** | Standard library only | — |

AI should verify before calling scripts / AI 在调用脚本前应确认：
1. Current directory is a git repo root (`git rev-parse --show-toplevel`)
2. There are uncommitted or staged changes (`git diff --stat`)
3. Network is available (if using MCP extensions)

---

## Error Handling / 错误处理

If any script fails, AI should / 如果任何脚本执行失败，AI 应：

1. **Check environment** / 检查环境: Verify Python + Git, current directory is git repo
2. **Check changes** / 检查变更: Verify `git diff --stat` has output
3. **Fallback** / 回退策略: If scripts error, AI can manually analyze `git diff` following this SKILL.md
4. **Notify human** / 反馈人类: Report error and ask whether to continue

Common errors / 常见错误：

| Error / 错误 | Cause / 原因 | Resolution / 处理 |
|-------------|-------------|------------------|
| `Not a git repository` | Not in a git repo | Init git or switch to a repo directory |
| `json.decoder.JSONDecodeError` | Broken pipe between scripts | Re-run the full pipeline command |
| `ModuleNotFoundError` | Python environment issue | Check `python --version`, ensure >= 3.8 |

---

## Post-Guard Follow-up Protocol / 拦截后闭环追问

When `commit_guard.py` blocks a commit (P0 detected), the AI MUST automatically engage the user in a closed-loop decision. **Do not just report the block and stop** — proactively ask for a decision.

当 `commit_guard.py` 拦截了 commit（检测到 P0 破坏性变更），AI **必须**自动发起闭环追问决策。不要只报告拦截结果就结束——要主动问用户怎么处理。

### Protocol Steps / 协议步骤

```
commit_guard.py blocks commit
    ↓
AI reads conflict-report.md
    ↓
AI summarizes P0 findings in 1-2 sentences
    ↓
AI asks user: Accept / Reject / Revise?
    ↓
User decides → AI executes → AI verifies
```

#### Step 1: Acknowledge & Summarize / 告知与摘要

- Tell the user the commit was blocked by Business Conflict Analyzer
- Read `conflict-report.md` and give a **1-2 sentence summary** of the P0 risk in business language
- Do **not** dump the full report — just the key finding

Example:
> "Commit was blocked by Business Conflict Analyzer. The change removes `UserDTO.mobile` field which is consumed by Profile Service and Order Service — this will break their field mappings."

#### Step 2: Ask for Decision / 追问决策

Present three options clearly. Use the detected language (check `LANG` env var or conversation language). Show ONLY one language:

```
How would you like to proceed?

[1] **Accept** — proceed, I'll auto-apply compatibility mitigations
    (@Deprecated, route retention, fallback, calling-site updates)
[2] **Reject** — roll back the change, no action taken
[3] **Revise** — adjust approach (tell me what to change)
```

If the conversation is in Chinese, present in Chinese:

```
请选择处理方式：

[1] **采纳** — 继续执行，自动修复所有受影响引用方
[2] **拒绝** — 回滚变更，不做任何修改
[3] **修改建议** — 调整方案（告诉我怎么改）
```

Wait for user input — do **not** proceed without a decision.

#### Step 3: Execute / 执行决策

Based on user's choice:

| Decision / 决策 | AI Action / AI 操作 |
|----------------|-------------------|
| **→ 1** ✅ | 1. Apply compatibility mitigations (auto-add `@Deprecated`, retain old routes/methods with @Deprecated + delegate, add fallback logic for removed fields). 2. Re-run analysis pipeline to verify no P0 remains. 3. If clean → user can commit again. |
| **→ 2** ❌ | 1. `git checkout -- .` to discard changes. 2. Confirm rollback complete. |
| **→ 3** ✏️ | 1. Listen to user's revision guidance. 2. Adjust code accordingly. 3. Re-run analysis pipeline. 4. Present updated report. |

**Important**: The AI should autonomously execute these actions — no additional user instruction needed. If the user says "1" or "Accept", the AI should immediately start applying mitigations.

#### Step 4: Verify / 验证

After any modification (mitigations applied or revision made):

1. Re-run the analysis pipeline (run `diff_analyzer.py` + `impact_mapper.py` + `report_generator.py` on current changes)
2. If clean → tell user "No P0 risks remain, you can commit now"
3. If still blocked → loop back to Step 2 with updated findings

### Implementation Note / 实现说明

This protocol does not require changes to `commit_guard.py`. The hook already:
- Prints the report to stderr ✅
- Saves `conflict-report.md` to project root ✅
- Outputs JSON stop signal ✅

The AI reads `conflict-report.md` to re-engage the conversation. No additional Python code needed.

---

## Auto-Fix Impacted Consumers / 引用方批量修复

After the user accepts a change (whether via the Post-Guard protocol or in normal conversation), the AI MUST automatically fix **all impacted consumer sites** identified by `impact_mapper.py`, not just the original code being changed.

用户确认采纳变更后（无论是通过拦截后闭环追问还是在正常对话中），AI **必须**自动修复 `impact_mapper.py` 识别的**所有受影响引用方**，而不仅仅是原改动代码。

### Why This Is Explicitly Enforced / 为什么显式要求

| Issue / 问题 | Without instruction / 无指令时 | With instruction / 有指令后 |
|-------------|------------------------------|---------------------------|
| **Determinism** | 60-80% chance AI auto-fixes all | **100%** guaranteed |
| **Scope authorization** | AI may hesitate: "Did user really want me to touch OrderService?" | AI knows it's **authorized to fix all consumers** |
| **Complex multi-hop chains** | AI may fix obvious ones but miss indirect chains | AI **must** trace and fix the full chain |

### Protocol / 协议

#### Step 1: Collect Consumer Sites / 收集引用点

After user says "1" / "Accept" / "采纳" — or after the user chooses the Accept option in any language:

1. Read the impact analysis report or re-run `impact_mapper.py`
2. Extract the complete list of impacted consumer sites (file + line + symbol)
3. Build a fix plan: for each site, determine the corresponding change needed

#### Step 2: Auto-Fix All Sites / 批量自动修复

For each impacted consumer site, apply the matching fix automatically:

| Change Type / 变更类型 | Fix Action / 修复动作 |
|----------------------|---------------------|
| **Field renamed** | Update all references: `getOldName()` → `getNewName()`, `.oldField` → `.newField` |
| **Field removed (with compat)** | Leave calls as-is (compat getter exists), add `// TODO: migrate to newField` |
| **Field removed (no compat)** | Update to new field path, or remove the call and add warning comment |
| **Method signature changed** | Update all call sites with new params/return type |
| **Enum value removed** | Replace usage with equivalent, or add `@SuppressWarnings` + migration comment |
| **Route/path changed** | Add redirect or update all client API call paths |

**Important**: Do not ask the user per-consumer. Fix all sites autonomously, then report the summary.

#### Step 3: Report Summary / 汇报结果

After all fixes are applied, report:

```markdown
Auto-fix completed:
- 9 impacted consumers found
- 9 auto-fixed (getMobile() → getPhone()) ✅
- 0 skipped
- Compilation: verified clean
```

If some sites could not be auto-fixed (ambiguous change, or file outside project scope), list them explicitly as manual action items.

---

## Performance / 性能说明

- `impact_mapper.py` uses `grep` for project reference search; large projects (>100K files) may take 5-10s
- `grep` automatically skips `.git`, `node_modules`, `target`, `build` directories
- For performance issues, restrict scope or use `--since HEAD~1`

---

## Boundary Principles / 边界原则

1. **Not a replacement for Rules** / 不替代 Rule: Technical red lines (SQL injection prevention, security policies) are defined in `CLAUDE.md`
2. **Not a replacement for Tests** / 不替代测试: This Skill generates *business conflict analysis*, not test reports
3. **Blocks only P0 / 仅拦截 P0**: `commit_guard.py` blocks P0 (compile-breaking) changes only — lower-risk changes pass through and are reported without blocking. The human always has final say via the Accept/Reject/Revise loop.
